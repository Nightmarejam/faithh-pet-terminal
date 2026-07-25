#!/usr/bin/env python3
"""CLI for doc_update_queue in project_states.json (single source of truth)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PROJECT_STATES_PATH = REPO_ROOT / "project_states.json"

TIER_ORDER = {"critical": 0, "reference": 1, "archive": 2}
VALID_TIERS = frozenset(TIER_ORDER)
VALID_STATUS = frozenset({"pending", "in_progress", "done"})


def normalize_path(p: str) -> str:
    return p.replace("\\", "/").strip()


def today_iso_date() -> str:
    return date.today().isoformat()


def load_states() -> dict:
    if not PROJECT_STATES_PATH.is_file():
        print(f"error: missing {PROJECT_STATES_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(PROJECT_STATES_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_states(data: dict) -> None:
    with open(PROJECT_STATES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def ensure_queue(data: dict) -> list:
    q = data.get("doc_update_queue")
    if q is None:
        q = []
        data["doc_update_queue"] = q
    elif not isinstance(q, list):
        print("error: doc_update_queue must be a list", file=sys.stderr)
        sys.exit(1)
    return q


def has_active_entry(queue: list, path_norm: str) -> bool:
    for e in queue:
        if not isinstance(e, dict):
            continue
        if normalize_path(str(e.get("path", ""))) != path_norm:
            continue
        st = e.get("status")
        if st in ("pending", "in_progress"):
            return True
    return False


def cmd_add(args: argparse.Namespace) -> int:
    path_norm = normalize_path(args.path)
    tier = args.tier
    if tier not in VALID_TIERS:
        print(f"error: tier must be one of {sorted(VALID_TIERS)}", file=sys.stderr)
        return 1

    data = load_states()
    queue = ensure_queue(data)
    if has_active_entry(queue, path_norm):
        print(f"skip: already queued (pending/in_progress): {path_norm}")
        return 0

    entry = {
        "path": path_norm,
        "tier": tier,
        "reason": args.reason,
        "triggered_by": args.triggered_by,
        "added": today_iso_date(),
        "status": "pending",
        "completed": None,
    }
    queue.append(entry)
    save_states(data)
    print(f"queued: {path_norm} ({tier})")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    data = load_states()
    queue = ensure_queue(data)
    pending = [e for e in queue if isinstance(e, dict) and e.get("status") == "pending"]
    pending.sort(
        key=lambda e: (
            TIER_ORDER.get(e.get("tier"), 99),
            str(e.get("path", "")),
        )
    )
    if not pending:
        print("No pending doc updates.")
        return 0
    tier_labels = {"critical": "CRITICAL", "reference": "REFERENCE", "archive": "ARCHIVE"}
    print(f"Pending doc updates ({len(pending)}):\n")
    for e in pending:
        tier = e.get("tier", "?")
        label = tier_labels.get(tier, tier.upper())
        path = e.get("path", "")
        reason = e.get("reason", "")
        trig = e.get("triggered_by", "")
        added = e.get("added", "")
        print(f"  [{label}] {path}")
        print(f"      added: {added}  triggered_by: {trig}")
        print(f"      reason: {reason}")
        print()
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    path_norm = normalize_path(args.path)
    data = load_states()
    queue = ensure_queue(data)
    updated = False
    today = today_iso_date()
    for e in queue:
        if not isinstance(e, dict):
            continue
        if normalize_path(str(e.get("path", ""))) != path_norm:
            continue
        if e.get("status") not in ("pending", "in_progress"):
            continue
        e["status"] = "done"
        e["completed"] = today
        updated = True
        break
    if not updated:
        print(f"error: no pending/in_progress entry for path: {path_norm}", file=sys.stderr)
        return 1
    save_states(data)
    print(f"marked done: {path_norm} (completed {today})")
    return 0


def parse_completed_date(completed: str | None) -> date | None:
    if completed is None or completed == "":
        return None
    s = str(completed).strip()
    if "T" in s:
        s = s.split("T", 1)[0]
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def cmd_purge(_args: argparse.Namespace) -> int:
    data = load_states()
    queue = ensure_queue(data)
    cutoff = date.today() - timedelta(days=30)
    new_queue: list = []
    removed = 0
    for e in queue:
        if not isinstance(e, dict):
            new_queue.append(e)
            continue
        if e.get("status") != "done":
            new_queue.append(e)
            continue
        cd = parse_completed_date(e.get("completed"))
        if cd is not None and cd < cutoff:
            removed += 1
            continue
        new_queue.append(e)
    data["doc_update_queue"] = new_queue
    save_states(data)
    print(f"purge: removed {removed} done entr(y/ies) completed before {cutoff.isoformat()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage doc_update_queue in project_states.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a queue entry (no-op if path already pending/in_progress)")
    p_add.add_argument("--path", required=True)
    p_add.add_argument("--tier", required=True, choices=sorted(VALID_TIERS))
    p_add.add_argument("--reason", required=True)
    p_add.add_argument("--triggered-by", dest="triggered_by", required=True)
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List pending entries (critical → reference → archive)")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="Mark pending/in_progress entry done for path")
    p_done.add_argument("--path", required=True)
    p_done.set_defaults(func=cmd_done)

    p_purge = sub.add_parser("purge", help="Remove done entries completed >30 days ago")
    p_purge.set_defaults(func=cmd_purge)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
