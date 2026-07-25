#!/usr/bin/env python3
"""
Export project_status.json and component_map.json to CSV files for Power BI.

Outputs:
    projects/status/tracks.csv   — one row per track
    projects/status/gates.csv    — one row per gate
    projects/status/components.csv — one row per component

Usage:
    python3 scripts/export_status_csv.py
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STATUS_FILE = BASE / "projects/status/project_status.json"
COMP_FILE = BASE / "projects/status/component_map.json"
OUT_DIR = BASE / "projects/status"


def main() -> None:
    now = datetime.now().strftime("%Y-%m-%d")
    ps = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    cm = (
        json.loads(COMP_FILE.read_text(encoding="utf-8"))
        if COMP_FILE.exists()
        else {"components": []}
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_DIR / "tracks.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "track_id",
                "name",
                "status",
                "current_gate",
                "last_activity",
                "total_gates",
                "completed_gates",
                "pending_gates",
                "notes",
                "export_date",
            ],
        )
        w.writeheader()
        for t in ps["tracks"]:
            gates = t.get("gates") or []
            w.writerow(
                {
                    "track_id": t["id"],
                    "name": t["name"],
                    "status": t["status"],
                    "current_gate": t.get("current_gate") or "",
                    "last_activity": t.get("last_activity") or "",
                    "total_gates": len(gates),
                    "completed_gates": sum(1 for g in gates if g.get("status") == "completed"),
                    "pending_gates": sum(1 for g in gates if g.get("status") == "pending"),
                    "notes": (t.get("notes") or "")[:200],
                    "export_date": now,
                }
            )

    with open(OUT_DIR / "gates.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "track_id",
                "track_name",
                "gate_id",
                "title",
                "status",
                "blocker",
                "export_date",
            ],
        )
        w.writeheader()
        for t in ps["tracks"]:
            for g in t.get("gates") or []:
                w.writerow(
                    {
                        "track_id": t["id"],
                        "track_name": t["name"],
                        "gate_id": g["id"],
                        "title": g.get("title") or "",
                        "status": g.get("status") or "",
                        "blocker": g.get("blocker") or "",
                        "export_date": now,
                    }
                )

    with open(OUT_DIR / "components.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "component_id",
                "name",
                "type",
                "file",
                "last_changed",
                "change_summary",
                "dep_count",
                "consumer_count",
                "export_date",
            ],
        )
        w.writeheader()
        for c in cm.get("components", []):
            w.writerow(
                {
                    "component_id": c["id"],
                    "name": c.get("name") or "",
                    "type": c.get("type") or "",
                    "file": c.get("file") or "",
                    "last_changed": c.get("last_changed") or "",
                    "change_summary": (c.get("change_summary") or "")[:200],
                    "dep_count": len(c.get("depends_on") or []),
                    "consumer_count": len(c.get("consumed_by") or []),
                    "export_date": now,
                }
            )

    print(f"Exported to {OUT_DIR}")
    print(f"  tracks.csv:     {len(ps['tracks'])} rows")
    print(f"  gates.csv:      {sum(len(t.get('gates') or []) for t in ps['tracks'])} rows")
    print(f"  components.csv: {len(cm.get('components', []))} rows")


if __name__ == "__main__":
    main()
