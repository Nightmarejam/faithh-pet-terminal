#!/usr/bin/env python3
"""
Export filesystem inventory to CSV for transparency/audit workflows.

Examples:
  python3 scripts/export_file_inventory.py \
    --root /mnt/c/Users/jonat \
    --output reports/inventory/windows_inventory.csv \
    --source-host windows --max-files 200000

  python3 scripts/export_file_inventory.py \
    --root /mnt/z \
    --output reports/inventory/nas_inventory.csv \
    --source-host nas --max-files 200000
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, UTC
from pathlib import Path


def domain_guess(path: Path) -> str:
    lower = str(path).lower()
    if any(k in lower for k in ("governance", "constitution", "constella", "civic", "ostrom")):
        return "governance"
    if any(k in lower for k in ("alife", "genomic", "experiment", "lineage")):
        return "alife"
    if "business" in lower or "finance" in lower:
        return "business"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export file inventory to CSV")
    parser.add_argument("--root", required=True, help="Root directory to inventory")
    parser.add_argument("--output", required=True, help="CSV output path")
    parser.add_argument("--source-host", required=True, choices=["windows", "nas", "wsl", "gen8"])
    parser.add_argument("--max-files", type=int, default=0, help="Stop after N files (0 = no limit)")
    parser.add_argument(
        "--exclude-dirs",
        nargs="*",
        default=["$RECYCLE.BIN", "System Volume Information", ".git", "__pycache__"],
        help="Directory names to skip",
    )
    args = parser.parse_args()

    root = Path(args.root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not root.exists():
        raise FileNotFoundError(f"Root does not exist: {root}")

    written = 0
    started = datetime.now(UTC).isoformat()

    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "path",
                "size_bytes",
                "modified_at_utc",
                "extension",
                "source_host",
                "domain_guess",
            ]
        )

        for path in root.rglob("*"):
            if path.is_dir():
                continue

            parts = set(path.parts)
            if any(ex in parts for ex in args.exclude_dirs):
                continue

            try:
                stat = path.stat()
            except OSError:
                continue

            writer.writerow(
                [
                    str(path),
                    stat.st_size,
                    datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
                    path.suffix.lower(),
                    args.source_host,
                    domain_guess(path),
                ]
            )
            written += 1
            if args.max_files and written >= args.max_files:
                break

    finished = datetime.now(UTC).isoformat()
    print(f"Inventory written: {output}")
    print(f"Files: {written}")
    print(f"Started: {started}")
    print(f"Finished: {finished}")


if __name__ == "__main__":
    main()
