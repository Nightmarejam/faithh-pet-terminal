#!/usr/bin/env python3
"""
Ecosystem baseline probe: PLC snapshot, /api/health aggregate, and timed /api/chat
(ping fast-path + minimal LLM; optional RAG). Emits JSON for repeatability.

Usage:
  python scripts/ecosystem_baseline_probe.py
  python scripts/ecosystem_baseline_probe.py --base-url http://127.0.0.1:5557 --with-rag
  python scripts/ecosystem_baseline_probe.py --out /tmp/probe.json --quiet
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_llm_latency_ms(chat_body: Dict[str, Any]) -> Optional[float]:
    """routing_debug.llm_routing.latency_ms when present (LLM provider round-trip only)."""
    rd = chat_body.get("routing_debug")
    if not isinstance(rd, dict):
        return None
    lr = rd.get("llm_routing")
    if not isinstance(lr, dict):
        return None
    v = lr.get("latency_ms")
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def summarize_plc_for_probe(plc: Dict[str, Any]) -> Dict[str, Any]:
    """Small PLC slice for reports (avoid huge JSON)."""
    fs = plc.get("faithh_status") or {}
    sv = (fs.get("services") or {}) if isinstance(fs, dict) else {}
    out: Dict[str, Any] = {
        "current_state": plc.get("current_state"),
        "faithh_version": fs.get("version") if isinstance(fs, dict) else None,
        "recent_component_changes_count": len(plc.get("recent_component_changes") or []),
    }
    if isinstance(fs, dict):
        cm = fs.get("current_model")
        if isinstance(cm, dict):
            out["current_model"] = {
                "name": cm.get("name"),
                "provider": cm.get("provider"),
            }
        chroma = sv.get("chromadb") if isinstance(sv, dict) else None
        if isinstance(chroma, dict):
            out["chromadb"] = {
                "reachable": chroma.get("reachable"),
                "documents": chroma.get("documents"),
                "host": chroma.get("host"),
            }
        ollama = sv.get("ollama") if isinstance(sv, dict) else None
        if isinstance(ollama, dict):
            out["ollama"] = {
                "reachable": ollama.get("reachable"),
                "count": ollama.get("count"),
            }
    return out


def summarize_health_for_probe(health: Dict[str, Any]) -> Dict[str, Any]:
    oh = health.get("overall_health") or {}
    cm = health.get("services", {}).get("connection_monitor") or {}
    return {
        "overall_status": oh.get("status"),
        "overall_issues": oh.get("issues") or [],
        "connection_monitor_active": cm.get("monitoring_active"),
        "connection_monitor_overall": cm.get("overall_status"),
        "required_unhealthy_services": cm.get("required_unhealthy_services"),
    }


def _timed_post_json(
    session: requests.Session,
    url: str,
    payload: Dict[str, Any],
    timeout: float,
) -> Tuple[float, int, Dict[str, Any]]:
    t0 = time.perf_counter()
    r = session.post(url, json=payload, timeout=timeout)
    wall_ms = (time.perf_counter() - t0) * 1000.0
    try:
        body = r.json()
    except Exception:
        body = {"_parse_error": True, "text": r.text[:500]}
    return wall_ms, r.status_code, body


def _chat_step_report(
    name: str,
    wall_ms: float,
    status_code: int,
    body: Dict[str, Any],
) -> Dict[str, Any]:
    rep: Dict[str, Any] = {
        "name": name,
        "http_status": status_code,
        "wall_ms": round(wall_ms, 2),
        "success": bool(body.get("success")) if isinstance(body, dict) else False,
    }
    if isinstance(body, dict):
        rep["response_time_server"] = body.get("response_time")
        rep["model_used"] = body.get("model_used")
        rep["provider"] = body.get("provider")
        rep["request_id"] = body.get("request_id")
        llm = extract_llm_latency_ms(body)
        if llm is not None:
            rep["llm_routing_latency_ms"] = llm
        rep["rag_results_count"] = len(body.get("rag_results") or []) if body.get("rag_results") else 0
        if body.get("success") is False:
            rep["error"] = body.get("error")
    return rep


def run_probe(
    base_url: str,
    with_rag: bool,
    skip_llm: bool,
    timeout_plc: float,
    timeout_health: float,
    timeout_chat: float,
    max_wall_ping_ms: float,
    max_wall_llm_ms: float,
    max_wall_rag_ms: float,
    strict_health: bool,
    llm_message: str,
) -> Dict[str, Any]:
    base = base_url.rstrip("/")
    session = requests.Session()
    failures: List[str] = []

    report: Dict[str, Any] = {
        "timestamp": _now_iso(),
        "base_url": base,
        "steps": {},
    }

    # A — PLC
    t0 = time.perf_counter()
    try:
        r = session.get(f"{base}/api/plc/state", timeout=timeout_plc)
        plc_wall_ms = (time.perf_counter() - t0) * 1000.0
        plc = r.json() if r.ok else {}
    except Exception as e:
        failures.append(f"plc: {e}")
        report["steps"]["plc"] = {"ok": False, "error": str(e)}
        report["pass"] = False
        report["failures"] = failures
        return report

    fs = plc.get("faithh_status") if isinstance(plc, dict) else {}
    fs = fs if isinstance(fs, dict) else {}
    plc_ok = r.status_code == 200 and bool(fs.get("version"))
    if r.status_code != 200:
        failures.append(f"plc: HTTP {r.status_code}")
    elif not fs.get("version"):
        failures.append("plc: faithh_status.version missing")

    report["steps"]["plc"] = {
        "ok": plc_ok,
        "http_status": r.status_code,
        "wall_ms": round(plc_wall_ms, 2),
        "summary": summarize_plc_for_probe(plc) if isinstance(plc, dict) else {},
    }

    # B — Health
    t0 = time.perf_counter()
    try:
        r_h = session.get(f"{base}/api/health", timeout=timeout_health)
        health_wall_ms = (time.perf_counter() - t0) * 1000.0
        health = r_h.json() if r_h.ok else {}
    except Exception as e:
        failures.append(f"health: {e}")
        report["steps"]["health"] = {"ok": False, "error": str(e)}
        report["pass"] = False
        report["failures"] = failures
        return report

    if r_h.status_code != 200:
        failures.append(f"health: HTTP {r_h.status_code}")

    hsum = summarize_health_for_probe(health) if isinstance(health, dict) else {}
    report["steps"]["health"] = {
        "ok": r_h.status_code == 200,
        "http_status": r_h.status_code,
        "wall_ms": round(health_wall_ms, 2),
        "summary": hsum,
    }

    if strict_health and isinstance(health, dict):
        oh = health.get("overall_health") or {}
        if oh.get("status") and oh.get("status") != "healthy":
            failures.append(f"health: overall_health.status={oh.get('status')}")
        cm = (health.get("services") or {}).get("connection_monitor") or {}
        ru = cm.get("required_unhealthy_services")
        if ru:
            failures.append(f"health: required_unhealthy_services={ru}")

    # C1 — Ping chat (fast path)
    wall_ms, code, body = _timed_post_json(
        session,
        f"{base}/api/chat",
        {"message": "ping", "model": "auto", "use_rag": False},
        timeout_chat,
    )
    step_ping = _chat_step_report("chat_ping", wall_ms, code, body)
    report["steps"]["chat_ping"] = step_ping
    if code != 200 or not body.get("success"):
        failures.append(f"chat_ping: HTTP {code} or success=false")
    elif (body.get("response") or "").strip().lower() != "pong":
        failures.append("chat_ping: expected response 'pong'")
    if wall_ms > max_wall_ping_ms:
        failures.append(f"chat_ping: wall_ms {wall_ms:.0f} > max {max_wall_ping_ms}")

    # C2 — Minimal LLM (non-ping)
    if not skip_llm:
        wall_ms, code, body = _timed_post_json(
            session,
            f"{base}/api/chat",
            {
                "message": llm_message,
                "model": "auto",
                "use_rag": False,
            },
            timeout_chat,
        )
        step_llm = _chat_step_report("chat_baseline_llm", wall_ms, code, body)
        report["steps"]["chat_baseline_llm"] = step_llm
        if code != 200 or not body.get("success"):
            failures.append(f"chat_baseline_llm: HTTP {code} or success=false")
        if not (body.get("response") or "").strip():
            failures.append("chat_baseline_llm: empty response")
        if wall_ms > max_wall_llm_ms:
            failures.append(f"chat_baseline_llm: wall_ms {wall_ms:.0f} > max {max_wall_llm_ms}")
    else:
        report["steps"]["chat_baseline_llm"] = {"skipped": True}

    # C3 — RAG path
    if with_rag:
        wall_ms, code, body = _timed_post_json(
            session,
            f"{base}/api/chat",
            {
                "message": llm_message,
                "model": "auto",
                "use_rag": True,
            },
            timeout_chat,
        )
        step_rag = _chat_step_report("chat_with_rag", wall_ms, code, body)
        report["steps"]["chat_with_rag"] = step_rag
        if code != 200 or not body.get("success"):
            failures.append(f"chat_with_rag: HTTP {code} or success=false")
        if not (body.get("response") or "").strip():
            failures.append("chat_with_rag: empty response")
        if wall_ms > max_wall_rag_ms:
            failures.append(f"chat_with_rag: wall_ms {wall_ms:.0f} > max {max_wall_rag_ms}")
    else:
        report["steps"]["chat_with_rag"] = {"skipped": True}

    report["pass"] = len(failures) == 0
    report["failures"] = failures
    return report


def _print_summary(report: Dict[str, Any]) -> None:
    print(f"Ecosystem baseline probe — pass={report.get('pass')} base={report.get('base_url')}")
    steps = report.get("steps") or {}
    for key in ("plc", "health", "chat_ping", "chat_baseline_llm", "chat_with_rag"):
        s = steps.get(key)
        if not s:
            continue
        if s.get("skipped"):
            print(f"  {key}: skipped")
            continue
        if key == "plc":
            print(f"  plc: ok={s.get('ok')} wall_ms={s.get('wall_ms')} version={s.get('summary', {}).get('faithh_version')}")
        elif key == "health":
            print(f"  health: status={s.get('summary', {}).get('overall_status')} wall_ms={s.get('wall_ms')}")
        elif key.startswith("chat_"):
            print(
                f"  {key}: wall_ms={s.get('wall_ms')} "
                f"server_rt={s.get('response_time_server')} "
                f"llm_ms={s.get('llm_routing_latency_ms')} "
                f"model={s.get('model_used')} provider={s.get('provider')}"
            )
    if report.get("failures"):
        print("Failures:")
        for f in report["failures"]:
            print(f"  - {f}")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="FAITHH ecosystem baseline probe (PLC, health, chat timing).")
    p.add_argument("--base-url", default="http://127.0.0.1:5557", help="FAITHH backend base URL")
    p.add_argument("--with-rag", action="store_true", help="Run an additional /api/chat with use_rag=true")
    p.add_argument("--skip-llm", action="store_true", help="Skip non-ping LLM baseline (only ping chat)")
    p.add_argument("--llm-message", default="What is 2+2? Reply with one digit only.", help="Prompt for LLM/RAG steps")
    p.add_argument("--timeout-plc", type=float, default=15.0)
    p.add_argument("--timeout-health", type=float, default=15.0)
    p.add_argument("--timeout-chat", type=float, default=180.0)
    p.add_argument("--max-wall-ping-ms", type=float, default=5000.0)
    # Default 180s: first auto-route hit often spends ~60–120s in context/Ollama before LLM;
    # LLM ms in routing_debug stays small (see probe report).
    p.add_argument("--max-wall-llm-ms", type=float, default=180_000.0)
    p.add_argument("--max-wall-rag-ms", type=float, default=180_000.0)
    p.add_argument("--strict-health", action="store_true", help="Fail if overall_health not healthy or required deps down")
    p.add_argument("--out", type=str, default=None, help="Write full JSON report to this path")
    p.add_argument("--quiet", action="store_true", help="JSON only to stdout (no summary lines)")
    args = p.parse_args(argv)

    report = run_probe(
        base_url=args.base_url,
        with_rag=args.with_rag,
        skip_llm=args.skip_llm,
        timeout_plc=args.timeout_plc,
        timeout_health=args.timeout_health,
        timeout_chat=args.timeout_chat,
        max_wall_ping_ms=args.max_wall_ping_ms,
        max_wall_llm_ms=args.max_wall_llm_ms,
        max_wall_rag_ms=args.max_wall_rag_ms,
        strict_health=args.strict_health,
        llm_message=args.llm_message,
    )

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    if args.quiet:
        print(json.dumps(report, indent=2))
    else:
        _print_summary(report)
        if not args.out:
            print(json.dumps(report, indent=2))

    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    sys.exit(main())
