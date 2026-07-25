#!/usr/bin/env python3
"""
Check project_status.json for stale tracks.
A track is stale if last_activity > STALE_DAYS days ago AND status is active.

Usage:
    python3 scripts/check_project_staleness.py
    python3 scripts/check_project_staleness.py --days 14
    python3 scripts/check_project_staleness.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

STATUS_FILE = Path(__file__).resolve().parent.parent / "projects/status/project_status.json"


def _parse_last_activity(track: dict) -> datetime | None:
    raw = track.get("last_activity")
    if not raw:
        return None
    try:
        return datetime.strptime(str(raw)[:10], "%Y-%m-%d")
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    cutoff = datetime.now() - timedelta(days=args.days)
    stale, active = [], []
    now = datetime.now()

    for track in data.get("tracks", []):
        last = _parse_last_activity(track)
        age = (now - last).days if last else None
        entry = {
            "track_id": track["id"],
            "name": track["name"],
            "status": track["status"],
            "last_activity": track.get("last_activity") or "",
            "age_days": age if age is not None else -1,
            "current_gate": track.get("current_gate"),
            "notes": track.get("notes", ""),
        }
        if track.get("status") == "active" and last is not None and last < cutoff:
            stale.append(entry)
        else:
            active.append(entry)

    total_gates = sum(len(t.get("gates") or []) for t in data.get("tracks", []))
    done = sum(
        1
        for t in data.get("tracks", [])
        for g in t.get("gates") or []
        if g.get("status") == "completed"
    )
    summ = data.get("summary") or {}
    next_action = summ.get("next_action") or data.get("next_action") or "not set"

    if args.json:
        print(
            json.dumps(
                {
                    "stale": stale,
                    "active": active,
                    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                },
                indent=2,
            )
        )
        return 1 if stale else 0

    print(f"\n=== Project Staleness Report ({args.days}-day threshold) ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    if stale:
        print(f"STALE ACTIVE TRACKS ({len(stale)}):")
        for t in stale:
            print(f"  [{t['track_id']}] {t['name']}")
            print(f"       Last activity: {t['last_activity']} ({t['age_days']}d ago)")
            print(f"       Current gate:  {t['current_gate']}")
    else:
        print("No stale active tracks.\n")

    print("ALL TRACKS:")
    combined = {t["track_id"]: t for t in active + stale}
    stale_ids = {t["track_id"] for t in stale}
    order = [t["id"] for t in data.get("tracks", [])]
    for tid in order:
        t = combined.get(tid)
        if not t:
            continue
        marker = " *** STALE" if tid in stale_ids else ""
        age_s = f"{t['age_days']:3d}d ago" if t["age_days"] >= 0 else " n/a "
        cg = (t.get("current_gate") or "—")[:6]
        print(
            f"  [{t['track_id']}] {t['status']:10s} gate={cg:6s} "
            f"{age_s}  {t['name']}{marker}"
        )

    print(f"\nGate progress: {done}/{total_gates} complete")
    print(f"Next action:   {next_action}\n")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
