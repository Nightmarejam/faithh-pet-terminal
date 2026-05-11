#!/usr/bin/env python3
"""
Extract sampled CSV slices from very large ZIP members in X:\\staging.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import zipfile
from datetime import UTC, datetime
from pathlib import Path

POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"


def run_ps(cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-Command", cmd],
        capture_output=True,
        text=True,
    )


def sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return cleaned or "unnamed"


def copy_from_x_to_cache(source_win_path: str, cache_win_dir: str) -> Path:
    escaped_src = source_win_path.replace("'", "''")
    escaped_dst = cache_win_dir.replace("'", "''")
    ps = (
        "& { "
        f"$dst='{escaped_dst}'; "
        "New-Item -ItemType Directory -Path $dst -Force | Out-Null; "
        f"Copy-Item -LiteralPath '{escaped_src}' -Destination $dst -Force; "
        f"$out = Join-Path $dst (Split-Path -Leaf '{escaped_src}'); "
        "Write-Output $out "
        "}"
    )
    proc = run_ps(ps)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"Copy failed for {source_win_path}")
    win_out = proc.stdout.strip().splitlines()[-1].strip()
    drive = win_out[0].lower()
    rest = win_out[2:].replace("\\", "/")
    return Path(f"/mnt/{drive}/{rest}")


def sample_csv_from_zip(
    zip_path: Path,
    output_root: Path,
    max_rows: int,
    min_member_size_bytes: int,
) -> list[dict]:
    records = []
    zip_stem = sanitize_name(zip_path.stem)
    out_dir = output_root / zip_stem
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            if not info.filename.lower().endswith(".csv"):
                continue
            if info.file_size < min_member_size_bytes:
                continue

            with zf.open(info.filename, "r") as fh:
                text_stream = io.TextIOWrapper(fh, encoding="utf-8", errors="ignore", newline="")
                reader = csv.reader(text_stream)
                rows = []
                header = None
                for i, row in enumerate(reader):
                    if i == 0:
                        header = row
                        rows.append(row)
                        continue
                    if i <= max_rows:
                        rows.append(row)
                    else:
                        break

            member_stem = sanitize_name(Path(info.filename).stem)
            sample_csv = out_dir / f"{member_stem}__sample.csv"
            with sample_csv.open("w", newline="", encoding="utf-8") as out:
                writer = csv.writer(out)
                writer.writerows(rows)

            schema_md = out_dir / f"{member_stem}__schema.md"
            schema_lines = [
                f"# Sample Schema: {info.filename}",
                "",
                f"- source_zip: {zip_path.name}",
                f"- member_size_bytes: {info.file_size}",
                f"- sampled_rows_including_header: {len(rows)}",
                f"- sampled_data_rows: {max(0, len(rows)-1)}",
                "",
                "## Header columns",
                "",
            ]
            if header:
                for col in header:
                    schema_lines.append(f"- {col}")
            schema_md.write_text("\n".join(schema_lines), encoding="utf-8")

            records.append(
                {
                    "zip_path": str(zip_path),
                    "member_name": info.filename,
                    "member_size_bytes": info.file_size,
                    "sample_csv": str(sample_csv),
                    "schema_md": str(schema_md),
                    "sampled_rows_including_header": len(rows),
                }
            )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract sampled CSV slices from large ZIP members")
    parser.add_argument(
        "--queue",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_conversion_queue.csv",
    )
    parser.add_argument("--cache-win-dir", default=r"C:\Users\jonat\x_staging_cache")
    parser.add_argument(
        "--output-root",
        default="/home/jonat/ai-stack/docs/data/governance_sources/windows_staging_import/converted/zip_samples",
    )
    parser.add_argument("--max-rows", type=int, default=5000)
    parser.add_argument("--min-member-size-mb", type=int, default=100)
    args = parser.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        raise FileNotFoundError(queue_path)

    rows = list(csv.DictReader(queue_path.open("r", encoding="utf-8")))
    zips = [r for r in rows if r.get("extension", "").lower() == ".zip"]
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()

    extracted = []
    failures = []
    threshold = args.min_member_size_mb * 1024 * 1024

    for row in zips:
        source_path = row.get("source_path", "")
        try:
            local_zip = copy_from_x_to_cache(source_path, args.cache_win_dir)
            if not local_zip.exists():
                raise FileNotFoundError(local_zip)
            recs = sample_csv_from_zip(local_zip, output_root, args.max_rows, threshold)
            extracted.extend(recs)
        except Exception as exc:
            failures.append({"source_path": source_path, "error": str(exc)})

    report = {
        "timestamp_utc": now,
        "queue_path": str(queue_path),
        "zip_rows_seen": len(zips),
        "samples_created": len(extracted),
        "failures": failures,
        "records": extracted,
    }
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"/home/jonat/ai-stack/reports/index_runs/x_staging_zip_samples_{stamp}.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Zip sample report: {report_path}")
    print(f"Samples created: {len(extracted)}")
    print(f"Failures: {len(failures)}")


if __name__ == "__main__":
    main()
