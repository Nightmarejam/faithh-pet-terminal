#!/usr/bin/env python3
"""
Promote top non-personal NAS classification rows from pending -> approved.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve top NAS ingest candidates")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/nas_classification_queue.csv",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/nas_classification_queue.csv",
    )
    parser.add_argument("--max-approve", type=int, default=150)
    parser.add_argument("--min-score", type=float, default=1.5)
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    if not inp.exists():
        raise FileNotFoundError(inp)

    rows = list(csv.DictReader(inp.open("r", encoding="utf-8")))
    pending = []
    for i, row in enumerate(rows):
        if row.get("review_status") != "pending":
            continue
        if row.get("domain_group") == "personal":
            continue
        if row.get("ingestion_scope") not in {"governance", "alife", "constella"}:
            continue
        if row.get("sensitivity") == "private":
            continue
        score = float(row.get("score") or 0)
        if score < args.min_score:
            continue
        pending.append((score, i))

    pending.sort(reverse=True, key=lambda x: x[0])
    selected = pending[: args.max_approve]
    for _, idx in selected:
        rows[idx]["review_status"] = "approved"

    fields = list(rows[0].keys()) if rows else []
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Approved additional: {len(selected)}")
    print(f"Output queue: {out}")


if __name__ == "__main__":
    main()
