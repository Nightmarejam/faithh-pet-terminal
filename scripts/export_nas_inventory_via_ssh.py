#!/usr/bin/env python3
"""
Export NAS inventory over SSH into a local CSV.

This script scans NAS roots remotely and writes a local inventory file
with file metadata only (no content transfer).
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path


REMOTE_SCAN_CODE = r"""
import json
from datetime import datetime, timezone
from pathlib import Path

cfg = json.loads({roots_json})
roots = [Path(p) for p in cfg["roots"]]
max_files = int(cfg.get("max_files", 0))
allowed_exts = set(cfg.get("allowed_exts", []))

rows = []
scanned = 0

for root in roots:
    if not root.exists():
        continue
    stack = [root]
    while stack:
        cur = stack.pop()
        try:
            entries = list(cur.iterdir())
        except OSError:
            continue
        for path in entries:
            try:
                if path.is_dir():
                    stack.append(path)
                    continue
                if not path.is_file():
                    continue
            except OSError:
                continue
            scanned += 1
            if allowed_exts and path.suffix.lower() not in allowed_exts:
                continue
            try:
                st = path.stat()
            except OSError:
                continue
            rows.append(
                {
                    "path": str(path),
                    "size_bytes": st.st_size,
                    "modified_at_utc": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                    "extension": path.suffix.lower(),
                    "source_host": "nas",
                }
            )
            if max_files and len(rows) >= max_files:
                break
        if max_files and len(rows) >= max_files:
            break
    if max_files and len(rows) >= max_files:
        break

print(json.dumps({"rows": rows, "scanned": scanned, "exported": len(rows)}))
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Export NAS inventory via SSH")
    parser.add_argument(
        "--roots",
        nargs="+",
        default=[
            "/volume1/AI",
            "/volume1/projects",
            "/volume1/raw_ingest",
            "/volume1/archive",
            "/volume1/Personal",
        ],
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/nas_full_inventory.csv",
    )
    parser.add_argument("--max-files", type=int, default=0, help="0 means no explicit cap")
    parser.add_argument(
        "--allowed-exts",
        nargs="*",
        default=[".md", ".txt", ".json", ".csv", ".yaml", ".yml", ".pdf"],
    )
    parser.add_argument("--ssh-host", default="nas")
    args = parser.parse_args()

    payload_obj = {
        "roots": args.roots,
        "max_files": args.max_files,
        "allowed_exts": [e.lower() for e in args.allowed_exts],
    }
    payload = json.dumps(payload_obj)
    remote_code = REMOTE_SCAN_CODE.replace("{roots_json}", repr(payload))
    proc = subprocess.run(
        ["ssh", args.ssh_host, "python3", "-"],
        input=remote_code,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"NAS export failed (code={proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
        )
    result = json.loads(proc.stdout.strip())

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["path", "size_bytes", "modified_at_utc", "extension", "source_host"],
        )
        writer.writeheader()
        writer.writerows(result["rows"])

    print(f"Output: {output}")
    print(f"Scanned files: {result['scanned']}")
    print(f"Exported rows: {result['exported']}")
    print(f"Generated at: {datetime.now(UTC).isoformat()}")


if __name__ == "__main__":
    main()
