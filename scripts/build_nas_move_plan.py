#!/usr/bin/env python3
"""
Generate non-destructive NAS move/copy plan from classification queue.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build NAS move plan CSV")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/nas_classification_queue.csv",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/nas_move_plan.csv",
    )
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not inp.exists():
        raise FileNotFoundError(inp)

    rows = list(csv.DictReader(inp.open("r", encoding="utf-8")))
    plan = []
    for row in rows:
        status = row.get("review_status", "pending")
        if status != "approved":
            continue
        if row.get("domain_group", "") == "personal":
            continue
        if row.get("ingestion_scope", "") not in {"governance", "alife", "constella"}:
            continue
        if row.get("sensitivity", "") == "private":
            continue
        src = row.get("path", "")
        dst = row.get("move_target", "")
        plan.append(
            {
                "source_path": src,
                "target_path": dst,
                "domain_group": row.get("domain_group", ""),
                "ingestion_scope": row.get("ingestion_scope", ""),
                "review_status": status,
                "copy_then_verify": "yes",
                "checksum_required": "yes",
                "delete_source_after_verify": "no",
                "execution_state": "planned",
            }
        )

    fields = list(plan[0].keys()) if plan else [
        "source_path",
        "target_path",
        "domain_group",
        "ingestion_scope",
        "review_status",
        "copy_then_verify",
        "checksum_required",
        "delete_source_after_verify",
        "execution_state",
    ]
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(plan)

    print(f"Output: {out}")
    print(f"Planned rows: {len(plan)}")


if __name__ == "__main__":
    main()
