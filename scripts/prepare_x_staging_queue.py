#!/usr/bin/env python3
"""
Build manifest + conversion queue from Windows X:\\staging.

Also stages text-native files (.md/.txt/.json/.csv/.yaml/.yml) into
docs/data/governance_sources/windows_staging_import for immediate ingestion.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
DIRECT_EXTS = {".md", ".txt", ".json", ".csv", ".yaml", ".yml"}
CONVERT_EXTS = {".pdf", ".xlsx", ".zip"}


def run_ps(cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-Command", cmd],
        capture_output=True,
        text=True,
    )


def list_windows_files(windows_dir: str) -> list[dict]:
    ps = (
        f"& {{ "
        f"$items = Get-ChildItem -File -LiteralPath '{windows_dir}' | "
        "Select-Object FullName,Name,Length,LastWriteTime,Extension; "
        "$items | ConvertTo-Json -Depth 4 "
        "}"
    )
    proc = run_ps(ps)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to list Windows staging files")
    out = proc.stdout.strip()
    if not out:
        return []
    data = json.loads(out)
    if isinstance(data, dict):
        return [data]
    return data


def classify_converter(ext: str) -> str:
    ext = ext.lower()
    if ext == ".pdf":
        return "pdf_to_markdown"
    if ext == ".xlsx":
        return "xlsx_to_csv_markdown"
    if ext == ".zip":
        return "zip_unpack_then_filter"
    return "none"


def read_windows_text(path: str) -> str:
    escaped = path.replace("'", "''")
    ps = f"& {{ [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Get-Content -Raw -LiteralPath '{escaped}' }}"
    proc = run_ps(ps)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"Failed reading: {path}")
    return proc.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare X:\\staging manifest and conversion queue")
    parser.add_argument("--windows-dir", default=r"X:\staging")
    parser.add_argument(
        "--manifest-csv",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_manifest.csv",
    )
    parser.add_argument(
        "--queue-csv",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_conversion_queue.csv",
    )
    parser.add_argument(
        "--stage-root",
        default="/home/jonat/ai-stack/docs/data/governance_sources/windows_staging_import",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    files = list_windows_files(args.windows_dir)
    now = datetime.now(UTC).isoformat()

    manifest_rows = []
    queue_rows = []
    stage_root = Path(args.stage_root)
    stage_root.mkdir(parents=True, exist_ok=True)

    staged_count = 0
    skipped_existing = 0
    staged_errors = 0

    for f in files:
        ext = (f.get("Extension") or "").lower()
        full = f.get("FullName", "")
        name = f.get("Name", "")
        size = int(f.get("Length") or 0)
        last_write = str(f.get("LastWriteTime") or "")

        if ext in DIRECT_EXTS:
            action = "stage_direct"
        elif ext in CONVERT_EXTS:
            action = "convert_required"
        else:
            action = "exclude"

        row = {
            "source_path": full,
            "filename": name,
            "extension": ext,
            "size_bytes": size,
            "last_write_time": last_write,
            "ingestion_action": action,
            "proposed_lane": "governance",
            "proposed_converter": classify_converter(ext),
            "review_status": "pending",
            "generated_at_utc": now,
        }
        manifest_rows.append(row)

        if action == "convert_required":
            queue_rows.append(
                {
                    "source_path": full,
                    "filename": name,
                    "extension": ext,
                    "size_bytes": size,
                    "proposed_converter": classify_converter(ext),
                    "target_output_dir": str(stage_root),
                    "queue_status": "pending",
                    "priority": "high",
                    "generated_at_utc": now,
                }
            )
        elif action == "stage_direct":
            target = stage_root / name
            if target.exists() and not args.overwrite:
                skipped_existing += 1
                continue
            try:
                text = read_windows_text(full)
                target.write_text(text, encoding="utf-8")
                staged_count += 1
            except Exception:
                staged_errors += 1

    manifest_path = Path(args.manifest_csv)
    queue_path = Path(args.queue_csv)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.parent.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        fields = [
            "source_path",
            "filename",
            "extension",
            "size_bytes",
            "last_write_time",
            "ingestion_action",
            "proposed_lane",
            "proposed_converter",
            "review_status",
            "generated_at_utc",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest_rows)

    with queue_path.open("w", newline="", encoding="utf-8") as f:
        fields = [
            "source_path",
            "filename",
            "extension",
            "size_bytes",
            "proposed_converter",
            "target_output_dir",
            "queue_status",
            "priority",
            "generated_at_utc",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(queue_rows)

    print(f"Manifest: {manifest_path}")
    print(f"Conversion queue: {queue_path}")
    print(f"Rows manifest={len(manifest_rows)} conversion_queue={len(queue_rows)}")
    print(f"Staged direct files: {staged_count}")
    print(f"Skipped existing direct files: {skipped_existing}")
    print(f"Stage errors: {staged_errors}")


if __name__ == "__main__":
    main()
