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
