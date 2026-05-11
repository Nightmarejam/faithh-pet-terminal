#!/usr/bin/env python3
"""
Build NAS ingest allowlist from approved, non-personal classification rows.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build NAS ingest allowlist")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/nas_classification_queue.csv",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/nas_ingest_allowlist.csv",
    )
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not inp.exists():
        raise FileNotFoundError(inp)

    rows = list(csv.DictReader(inp.open("r", encoding="utf-8")))
    allowed = []
    for row in rows:
        if row.get("domain_group") == "personal":
            continue
        if row.get("review_status") != "approved":
            continue
        if row.get("ingestion_scope") not in {"governance", "alife", "constella"}:
            continue
        if row.get("sensitivity") == "private":
            continue
        allowed.append(row)

    fields = [
        "path",
        "size_bytes",
        "modified_at_utc",
        "extension",
        "source_host",
        "domain_group",
        "ingestion_scope",
        "sensitivity",
        "move_target",
        "review_status",
        "score",
    ]
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(allowed)

    print(f"Output: {out}")
    print(f"Allowlist rows: {len(allowed)}")


if __name__ == "__main__":
    main()
