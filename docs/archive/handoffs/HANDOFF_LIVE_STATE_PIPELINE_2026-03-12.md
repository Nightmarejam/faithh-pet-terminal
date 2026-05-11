# HANDOFF: Live State Collector + Imprint Pipeline
<!--
  For: Windsurf AI
  From: Claude + Jonathan
  Date: 2026-03-12
  Archive: docs/archive/ after complete
-->

## What This Builds

Two scripts that eliminate manual chunk count updates forever:

1. **`scripts/live_state_collector.py`** — polls ChromaDB and backend every 15 min, writes `faithh_live_state.json`
2. **`scripts/imprint.py`** — when live state is stable for 6+ consecutive checks, propagates values to state files automatically
3. **Cron wiring** — runs collector every 15 min, imprint every hour

After this is done, chunk counts and backend status self-update. The consistency checker reads `faithh_live_state.json` as authoritative source for live metrics.

---

## Task 1: Create scripts/live_state_collector.py

Create this file at `scripts/live_state_collector.py`:

```python
#!/usr/bin/env python3
"""
FAITHH Live State Collector
============================
Polls live services and writes faithh_live_state.json.
Run every 15 minutes via cron.

Usage:
    python scripts/live_state_collector.py
    python scripts/live_state_collector.py --verbose
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent

CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000
CHROMA_COLLECTION = "faithh_knowledge_base"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5557
STABILITY_THRESHOLD = 6  # checks before imprint is allowed
OUTPUT_FILE = BASE_DIR / "faithh_live_state.json"


def check_chromadb(verbose=False):
    """Query ChromaDB for live chunk count."""
    result = {"reachable": False, "chunk_count": None, "collection": None, "error": None}
    try:
        import chromadb
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        col = client.get_collection(CHROMA_COLLECTION)
        count = col.count()
        result.update({
            "reachable": True,
            "chunk_count": count,
            "collection": col.name,
        })
        if verbose:
            print(f"  ChromaDB: {count} chunks in {col.name}")
    except Exception as e:
        result["error"] = str(e)
        if verbose:
            print(f"  ChromaDB: unreachable ({e})")
    return result


def check_backend(verbose=False):
    """Check FAITHH backend health."""
    result = {"reachable": False, "version": None, "error": None}
    try:
        import urllib.request
        url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/health"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
            result.update({
                "reachable": True,
                "version": data.get("version") or data.get("status"),
            })
            if verbose:
                print(f"  Backend: reachable, version={result['version']}")
    except Exception as e:
        result["error"] = str(e)
        if verbose:
            print(f"  Backend: unreachable ({e})")
    return result


def compute_stability(current_count, previous_state):
    """
    Track how many consecutive checks have seen the same chunk count.
    Stability gate prevents mid-reindex values from being imprinted.
    """
    prev_count = previous_state.get("chroma", {}).get("chunk_count")
    prev_stable = previous_state.get("stability", {}).get("chunk_count_stable_for_checks", 0)

    if prev_count is not None and current_count == prev_count:
        return prev_stable + 1
    else:
        return 1  # reset — count changed


def load_previous_state():
    if OUTPUT_FILE.exists():
        try:
            return json.loads(OUTPUT_FILE.read_text())
        except Exception:
            pass
    return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print(f"\nFAITHH Live State Collector — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    previous = load_previous_state()
    chroma = check_chromadb(args.verbose)
    backend = check_backend(args.verbose)

    stable_checks = compute_stability(chroma.get("chunk_count"), previous)
    ready_to_imprint = (
        chroma["reachable"]
        and stable_checks >= STABILITY_THRESHOLD
    )

    last_imprint = previous.get("stability", {}).get("last_imprint", "never")

    state = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "chroma": chroma,
        "backend": backend,
        "stability": {
            "chunk_count_stable_for_checks": stable_checks,
            "stability_threshold": STABILITY_THRESHOLD,
            "ready_to_imprint": ready_to_imprint,
            "last_imprint": last_imprint,
        }
    }

    OUTPUT_FILE.write_text(json.dumps(state, indent=2))

    if args.verbose:
        print(f"  Stability: {stable_checks}/{STABILITY_THRESHOLD} checks")
        print(f"  Ready to imprint: {ready_to_imprint}")
        print(f"  Written: {OUTPUT_FILE}")

    # Exit code 0 = healthy, 1 = ChromaDB unreachable (useful for cron alerts)
    sys.exit(0 if chroma["reachable"] else 1)


if __name__ == "__main__":
    main()
```

**Stop condition:** File created at `scripts/live_state_collector.py`. Run once to verify:
```bash
cd ~/ai-stack && source venv/bin/activate && python3 scripts/live_state_collector.py --verbose
```
Confirm `faithh_live_state.json` is created in repo root. Move on.

---

## Task 2: Create scripts/imprint.py

Create this file at `scripts/imprint.py`:

```python
#!/usr/bin/env python3
"""
FAITHH Imprint Script
======================
When live state is stable, propagates values to state files.
Run every hour via cron (after collector has run at least 6 times).

Usage:
    python scripts/imprint.py
    python scripts/imprint.py --dry-run   # show what would change, don't write
    python scripts/imprint.py --force     # skip stability gate
"""

import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
LIVE_STATE_FILE = BASE_DIR / "faithh_live_state.json"
PROJECT_STATES  = BASE_DIR / "project_states.json"
FAITHH_MEMORY   = BASE_DIR / "faithh_memory.json"


def load_json(path):
    return json.loads(path.read_text())


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force",   action="store_true")
    args = parser.parse_args()

    if not LIVE_STATE_FILE.exists():
        print("ERROR: faithh_live_state.json not found. Run live_state_collector.py first.")
        return

    live = load_json(LIVE_STATE_FILE)
    stability = live.get("stability", {})
    ready = stability.get("ready_to_imprint", False)
    chunk_count = live.get("chroma", {}).get("chunk_count")
    collected_at = live.get("collected_at", "unknown")

    if not args.force and not ready:
        stable_for = stability.get("chunk_count_stable_for_checks", 0)
        threshold  = stability.get("stability_threshold", 6)
        print(f"Not ready to imprint — stable for {stable_for}/{threshold} checks.")
        print("Run collector more times or use --force to override.")
        return

    if chunk_count is None:
        print("ERROR: No chunk count in live state. ChromaDB may be unreachable.")
        return

    now = datetime.now(timezone.utc).isoformat()
    changes = []

    # ── Update project_states.json ──────────────────────────────────────────
    ps = load_json(PROJECT_STATES)
    old_count = ps["projects"]["FAITHH"]["infrastructure"].get("chunks_indexed")
    if old_count != chunk_count:
        changes.append(f"project_states.json: chunks_indexed {old_count} → {chunk_count}")
        if not args.dry_run:
            ps["projects"]["FAITHH"]["infrastructure"]["chunks_indexed"] = chunk_count
            ps["last_updated"] = now[:10]  # YYYY-MM-DD
            save_json(PROJECT_STATES, ps)

    # ── Update faithh_memory.json ───────────────────────────────────────────
    fm = load_json(FAITHH_MEMORY)
    kb = fm.get("knowledge_base_status", {})
    old_mem_count = kb.get("total_documents")
    if old_mem_count != chunk_count:
        changes.append(f"faithh_memory.json: total_documents {old_mem_count} → {chunk_count}")
        if not args.dry_run:
            fm["knowledge_base_status"]["total_documents"] = chunk_count
            fm["last_updated"] = now[:10]
            save_json(FAITHH_MEMORY, fm)

    # ── Record imprint timestamp in live state ──────────────────────────────
    if not args.dry_run and changes:
        live["stability"]["last_imprint"] = now
        LIVE_STATE_FILE.write_text(json.dumps(live, indent=2))

    # ── Regenerate CONTEXT.md ───────────────────────────────────────────────
    if not args.dry_run and changes:
        context_script = BASE_DIR / "scripts" / "generate_context.py"
        if context_script.exists():
            result = subprocess.run(
                ["python3", str(context_script)],
                cwd=BASE_DIR, capture_output=True, text=True
            )
            if result.returncode == 0:
                changes.append("CONTEXT.md: regenerated")
            else:
                changes.append(f"CONTEXT.md: regeneration failed ({result.stderr.strip()})")

    # ── Report ──────────────────────────────────────────────────────────────
    if changes:
        prefix = "[DRY RUN] Would apply:" if args.dry_run else "Imprinted:"
        print(f"\n{prefix}")
        for c in changes:
            print(f"  ✓ {c}")
        print(f"\nSource: faithh_live_state.json collected at {collected_at}")
    else:
        print(f"Nothing to imprint — all values already match live state ({chunk_count} chunks).")


if __name__ == "__main__":
    main()
```

**Stop condition:** File created. Test dry run:
```bash
python3 scripts/imprint.py --dry-run
```
Should say "Not ready to imprint" (collector hasn't run 6 times yet) or show what would change. Either is correct. Move on.

---

## Task 3: Wire cron in WSL

Add cron jobs for the collector (every 15 min) and imprint (every hour):

```bash
crontab -e
```

Add these lines:
```
# FAITHH live state collector — every 15 minutes
*/15 * * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python3 scripts/live_state_collector.py >> /tmp/faithh_collector.log 2>&1

# FAITHH imprint — every hour
0 * * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python3 scripts/imprint.py >> /tmp/faithh_imprint.log 2>&1
```

Verify cron saved:
```bash
crontab -l | grep faithh
```

**Stop condition:** Both lines appear in crontab output. Move on.

---

## Task 4: Update consistency_checker.py to read live state

Open `scripts/consistency_checker.py`. Find the `COMPARISONS` dict.

Change the `"ChromaDB chunk count"` comparison entry to add `live_state` as a source:

In the `STATE_FILES` dict at the top, add:
```python
"live_state": BASE_DIR / "faithh_live_state.json",
```

Add a new extractor function after the existing extractors:
```python
def extract_live_state(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {"_parse_error": True}
    chroma = data.get("chroma", {})
    return {
        "chroma_chunks":     chroma.get("chunk_count"),
        "chroma_collection": chroma.get("collection"),
        "live_reachable":    chroma.get("reachable"),
        "collected_at":      data.get("collected_at"),
    }
```

Add `live_state` to the `extracted` dict in `main()`:
```python
"live_state": extract_live_state(STATE_FILES["live_state"]),
```

Add `("live_state", "chroma_chunks")` to the `"ChromaDB chunk count"` comparison list.

**Stop condition:** Run checker, confirm `live_state` appears in the chunk count comparison row.

---

## Task 5: Commit everything

```bash
git add scripts/live_state_collector.py scripts/imprint.py scripts/consistency_checker.py faithh_live_state.json
git commit -m "feat: live state collector + imprint pipeline

- live_state_collector.py: polls ChromaDB + backend every 15min
- imprint.py: propagates stable values to state files automatically  
- consistency_checker.py: now reads faithh_live_state.json as live source
- cron: collector every 15min, imprint every hour
- stability gate: 6 consecutive matching checks before imprint fires

Chunk counts will now self-update. No more manual drift."
git push
```

**Stop condition:** Push succeeds. Report commit hash and stop.

---

## What NOT To Do

- Do NOT run a reindex
- Do NOT modify project_states.json or faithh_memory.json manually
- Do NOT run imprint.py without --dry-run until collector has run at least 6 times
- Do NOT add new cron jobs beyond the two specified
- Do NOT modify any other files

## Done When

- [ ] `scripts/live_state_collector.py` created and runs without error
- [ ] `faithh_live_state.json` exists in repo root
- [ ] `scripts/imprint.py` created, dry-run works
- [ ] Cron wired (both jobs in crontab)
- [ ] Consistency checker updated to read live_state
- [ ] Committed and pushed

Report: commit hash + output of `python3 scripts/live_state_collector.py --verbose`
