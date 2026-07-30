#!/usr/bin/env python3
"""Read-only health observer for the FAITHH stack.

Reports; never writes, never heals, never restarts. That restraint is the point:
the one component that acted autonomously — the conversation auto-indexer — spent
weeks laundering wrong answers into the knowledge base as "decisions", unnoticed,
because nothing was checking it. An observer you trust is worth more than a healer
you have to supervise.

Every check here exists because its absence cost real debugging time:

  dimension     embedder vs collection width. A mismatch does not crash; it returns
                best_distance 1.0 forever and answers ungrounded.
  deploy drift  a file deployed AFTER the service started is not running. This
                silently invalidated two test cycles in one session.
  feedback loop model output indexed as retrievable fact. Canary for the auto-indexer
                relabelling its own answers as decisions.
  doc currency  documents asserting facts since verified false. Retrieval improvements
                raised the cost of these: a confident wrong doc now outranks the one
                that corrects it.
  reachability  vLLM answered on localhost but not from the Gen8 — the link that
                actually matters was the one not being checked.

Exit codes: 0 clean, 1 warnings, 2 critical.

Usage:
    python scripts/ops/observer_report.py
    python scripts/ops/observer_report.py --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request

GEN8 = "servicebox.taileb8c60.ts.net"
BACKEND = f"http://{GEN8}:5557"
CHROMA = f"http://{GEN8}:8000"
VLLM_FROM_GEN8 = "http://desktop-iifeikl.taileb8c60.ts.net:8000"
COLLECTION = "faithh_knowledge_base_v2"

OK, WARN, CRIT = "ok", "warn", "critical"
results: list[dict] = []


def record(name: str, status: str, detail: str) -> None:
    results.append({"check": name, "status": status, "detail": detail})


def http_json(url: str, timeout: int = 15):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def ssh(cmd: str, timeout: int = 25) -> tuple[int, str]:
    p = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", "servicebox", cmd],
        capture_output=True, text=True, timeout=timeout,
    )
    return p.returncode, (p.stdout or p.stderr).strip()


def check_backend_health() -> None:
    try:
        d = http_json(f"{BACKEND}/api/health")
    except Exception as e:
        record("backend", CRIT, f"unreachable: {e}")
        return
    overall = (d.get("overall_health") or {}).get("status", "unknown")
    issues = (d.get("overall_health") or {}).get("issues") or []
    svc = (d.get("services", {}).get("connection_monitor", {}) or {}).get("services", {})
    down = [n for n, s in svc.items() if s.get("status") not in ("healthy",)]
    status = OK if overall == "healthy" else WARN
    record("backend", status, f"overall={overall} issues={issues or 'none'} degraded={down or 'none'}")


def check_reachability() -> None:
    for name, url in (("chroma", f"{CHROMA}/api/v2/heartbeat"),):
        try:
            urllib.request.urlopen(url, timeout=10).read(1)
            record(f"reach:{name}", OK, "200")
        except Exception as e:
            record(f"reach:{name}", CRIT, str(e)[:90])
    # The link that actually matters: the Gen8 consuming inference over the tailnet.
    # Checking it from this workstation would pass while the real path is broken.
    rc, out = ssh(f"curl -s -o /dev/null -w '%{{http_code}}' --max-time 10 {VLLM_FROM_GEN8}/v1/models")
    if rc != 0:
        record("reach:gen8->vllm", CRIT, f"ssh failed: {out[:80]}")
    elif out.strip() == "200":
        record("reach:gen8->vllm", OK, "200")
    else:
        record("reach:gen8->vllm", CRIT, f"HTTP {out.strip() or 'no response'} — inference unavailable")


def check_dimensions() -> None:
    rc, out = ssh(
        "cd ~/ai-stack && ./venv/bin/python -c \""
        "import chromadb;"
        f"c=chromadb.HttpClient(host='localhost',port=8000).get_collection('{COLLECTION}');"
        "pk=c.peek(limit=1);e=pk.get('embeddings');"
        "print(c.count(), len(e[0]) if e is not None and len(e) else 'none')\"",
        timeout=60,
    )
    if rc != 0:
        record("dimension", WARN, f"could not read collection: {out[:80]}")
        return
    parts = out.split()
    if len(parts) != 2:
        record("dimension", WARN, f"unexpected output: {out[:60]}")
        return
    count, dim = parts
    if dim == "768":
        record("dimension", OK, f"{COLLECTION}: {int(count):,} docs @ 768-dim (matches BGE)")
    else:
        record("dimension", CRIT,
               f"{COLLECTION} is {dim}-dim but the query embedder is 768-dim — "
               "every query will report best_distance 1.0")


def check_deploy_drift() -> None:
    rc, out = ssh(
        "stat -c %Y ~/ai-stack/faithh_professional_backend_fixed.py; "
        "date -d \"$(systemctl show faithh-backend -p ActiveEnterTimestamp --value)\" +%s"
    )
    if rc != 0 or len(out.split()) != 2:
        record("deploy-drift", WARN, f"could not compare: {out[:80]}")
        return
    deployed, started = (int(x) for x in out.split())
    if started >= deployed:
        record("deploy-drift", OK, f"service started {started - deployed}s after deploy")
    else:
        record("deploy-drift", CRIT,
               f"deployed file is {deployed - started}s NEWER than the running process — "
               "the running code is not what is on disk; restart faithh-backend")


def check_feedback_loop() -> None:
    """Canary for model output being retrievable as fact."""
    rc, out = ssh(
        "cd ~/ai-stack && ./venv/bin/python -c \""
        "import chromadb;"
        f"c=chromadb.HttpClient(host='localhost',port=8000).get_collection('{COLLECTION}');"
        "print(len(c.get(where={'document_type':'decision'}, limit=5000, include=[])['ids']))\"",
        timeout=60,
    )
    if rc != 0:
        record("feedback-loop", WARN, f"could not query: {out[:70]}")
        return
    try:
        n = int(out.split()[-1])
    except (ValueError, IndexError):
        record("feedback-loop", WARN, f"unexpected output: {out[:60]}")
        return
    if n == 0:
        record("feedback-loop", OK, "no model output labelled as 'decision'")
    else:
        record("feedback-loop", CRIT,
               f"{n} record(s) labelled document_type=decision — the auto-tagger may be "
               "relabelling FAITHH's own answers as curated decisions again")


def check_doc_currency() -> None:
    p = subprocess.run(
        [sys.executable, "scripts/docs/audit_doc_currency.py", "--severity", "high"],
        capture_output=True, text=True,
    )
    line = next((l for l in p.stdout.splitlines() if "documents with stale claims" in l), "")
    n = line.split(":")[-1].strip() if line else "?"
    record("doc-currency", OK if n == "0" else WARN, f"{n} document(s) with high-severity stale claims")


def check_disk() -> None:
    rc, out = ssh("df -h / | tail -1 | awk '{print $3\" used of \"$2\" (\"$5\")\"}'")
    if rc != 0:
        record("disk", WARN, out[:70])
        return
    pct = 0
    for tok in out.split():
        if tok.strip("()%").isdigit() and "%" in tok:
            pct = int(tok.strip("()%"))
    record("disk", CRIT if pct >= 90 else WARN if pct >= 80 else OK, out)


CHECKS = [
    check_backend_health, check_reachability, check_dimensions,
    check_deploy_drift, check_feedback_loop, check_doc_currency, check_disk,
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    for fn in CHECKS:
        try:
            fn()
        except Exception as e:
            record(fn.__name__.replace("check_", ""), WARN, f"check itself failed: {e}")

    if args.json:
        print(json.dumps({"results": results}, indent=2))
    else:
        icon = {OK: "OK  ", WARN: "WARN", CRIT: "CRIT"}
        width = max(len(r["check"]) for r in results)
        print("FAITHH observer — read-only\n")
        for r in results:
            print(f"  [{icon[r['status']]}] {r['check']:<{width}}  {r['detail']}")
        crit = sum(1 for r in results if r["status"] == CRIT)
        warn = sum(1 for r in results if r["status"] == WARN)
        print(f"\n  {len(results)} checks — {crit} critical, {warn} warning")

    if any(r["status"] == CRIT for r in results):
        return 2
    return 1 if any(r["status"] == WARN for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
