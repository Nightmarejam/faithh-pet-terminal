#!/usr/bin/env python3
"""
Chroma collection composition census (DB census handoff).

Delegates to scripts/generate_db_map.py with a dated default output path.
Use --dry-run for a fast first-batch connectivity check.

Examples:
  python scripts/analyze_chroma_composition.py --dry-run
  python scripts/analyze_chroma_composition.py
  python scripts/analyze_chroma_composition.py --output docs/DATABASE_MAP_2026-04-10.md
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "generate_db_map.py"


def main() -> int:
    ap = argparse.ArgumentParser(description="Chroma DB census → DATABASE_MAP markdown.")
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Markdown path (default: docs/DATABASE_MAP_YYYY-MM-DD.md UTC date)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="First batch only; no report file (passed through to generate_db_map).",
    )
    ap.add_argument(
        "--collection",
        default=None,
        help="Override CHROMA_COLLECTION for this run.",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override CHROMA_MAINT_BATCH_SIZE / default batch for paging.",
    )
    args = ap.parse_args()

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = args.output if args.output is not None else REPO_ROOT / "docs" / f"DATABASE_MAP_{day}.md"

    cmd = [sys.executable, str(SCRIPT), "--output", str(out.resolve())]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.collection:
        cmd.extend(["--collection", args.collection])
    if args.batch_size is not None:
        cmd.extend(["--batch-size", str(args.batch_size)])

    print("Running:", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=str(REPO_ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
