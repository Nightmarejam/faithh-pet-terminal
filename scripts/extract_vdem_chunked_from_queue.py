#!/usr/bin/env python3
"""
Chunked V-Dem ingest extractor from X:\\staging ZIP sources.

This extracts large CSV members from V-Dem ZIPs in bounded row chunks
to keep indexing scalable and auditable.
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


def pick_csv_member(zf: zipfile.ZipFile) -> zipfile.ZipInfo:
    csv_members = [i for i in zf.infolist() if (not i.is_dir()) and i.filename.lower().endswith(".csv")]
    if not csv_members:
        raise ValueError("No CSV members in ZIP")
    csv_members.sort(key=lambda x: x.file_size, reverse=True)
    return csv_members[0]


def extract_chunked_csv(
    zip_path: Path,
    output_root: Path,
    rows_per_chunk: int,
    max_rows_per_file: int,
) -> dict:
    out_dir = output_root / sanitize_name(zip_path.stem)
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path) as zf:
        member = pick_csv_member(zf)
        with zf.open(member.filename, "r") as fh:
            text_stream = io.TextIOWrapper(fh, encoding="utf-8", errors="ignore", newline="")
            reader = csv.reader(text_stream)
            header = next(reader, None)
            if header is None:
                raise ValueError("CSV member has no rows")

            chunk_idx = 0
            current_rows: list[list[str]] = []
            data_rows_written = 0
            chunk_files = []

            for row in reader:
                if data_rows_written >= max_rows_per_file:
                    break
                current_rows.append(row)
                data_rows_written += 1
                if len(current_rows) >= rows_per_chunk:
                    chunk_idx += 1
                    out_csv = out_dir / f"{sanitize_name(Path(member.filename).stem)}__chunk_{chunk_idx:03d}.csv"
                    with out_csv.open("w", newline="", encoding="utf-8") as out:
                        writer = csv.writer(out)
                        writer.writerow(header)
                        writer.writerows(current_rows)
                    chunk_files.append(str(out_csv))
                    current_rows = []

            if current_rows:
                chunk_idx += 1
                out_csv = out_dir / f"{sanitize_name(Path(member.filename).stem)}__chunk_{chunk_idx:03d}.csv"
                with out_csv.open("w", newline="", encoding="utf-8") as out:
                    writer = csv.writer(out)
                    writer.writerow(header)
                    writer.writerows(current_rows)
                chunk_files.append(str(out_csv))

    schema_md = out_dir / "_vdem_chunk_schema.md"
    schema_md.write_text(
        "\n".join(
            [
                f"# V-Dem Chunk Extraction: {zip_path.name}",
                "",
                f"- csv_member: {member.filename}",
                f"- csv_member_size_bytes: {member.file_size}",
                f"- rows_per_chunk: {rows_per_chunk}",
                f"- max_rows_per_file: {max_rows_per_file}",
                f"- data_rows_written: {data_rows_written}",
                f"- chunk_files_created: {len(chunk_files)}",
                "",
                "## Columns",
                "",
                *[f"- {c}" for c in header],
            ]
        ),
        encoding="utf-8",
    )

    return {
        "zip_path": str(zip_path),
        "csv_member": member.filename,
        "csv_member_size_bytes": member.file_size,
        "rows_per_chunk": rows_per_chunk,
        "max_rows_per_file": max_rows_per_file,
        "data_rows_written": data_rows_written,
        "chunk_files_created": len(chunk_files),
        "schema_md": str(schema_md),
        "chunk_files": chunk_files,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract V-Dem ZIP CSVs in row chunks")
    parser.add_argument(
        "--queue",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_conversion_queue.csv",
    )
    parser.add_argument("--cache-win-dir", default=r"C:\Users\jonat\x_staging_cache")
    parser.add_argument(
        "--output-root",
        default="/home/jonat/ai-stack/docs/data/governance_sources/windows_staging_import/converted/vdem_chunked",
    )
    parser.add_argument("--rows-per-chunk", type=int, default=25000)
    parser.add_argument("--max-rows-per-file", type=int, default=150000)
    args = parser.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        raise FileNotFoundError(queue_path)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(queue_path.open("r", encoding="utf-8")))
    vdem_rows = [r for r in rows if "v-dem" in (r.get("filename", "").lower()) and r.get("extension", "").lower() == ".zip"]

    extracted = []
    failures = []
    for r in vdem_rows:
        src = r.get("source_path", "")
        try:
            local_zip = copy_from_x_to_cache(src, args.cache_win_dir)
            if not local_zip.exists():
                raise FileNotFoundError(local_zip)
            result = extract_chunked_csv(
                local_zip,
                output_root,
                rows_per_chunk=args.rows_per_chunk,
                max_rows_per_file=args.max_rows_per_file,
            )
            extracted.append(result)
        except Exception as exc:
            failures.append({"source_path": src, "error": str(exc)})

    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "queue_path": str(queue_path),
        "vdem_zip_rows_seen": len(vdem_rows),
        "successful_extractions": len(extracted),
        "failures": failures,
        "extractions": extracted,
    }
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"/home/jonat/ai-stack/reports/index_runs/x_staging_vdem_chunked_{stamp}.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"V-Dem chunked report: {report_path}")
    print(f"Successful extractions: {len(extracted)}")
    print(f"Failures: {len(failures)}")


if __name__ == "__main__":
    main()
