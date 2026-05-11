#!/usr/bin/env python3
"""
Process X:\\staging conversion queue into ingestion-ready artifacts.

Workflow:
1) Copy source files from X:\\staging to C:\\Users\\jonat\\x_staging_cache (readable from WSL).
2) Convert by declared converter:
   - pdf_to_markdown
   - xlsx_to_csv_markdown
   - zip_unpack_then_filter
3) Emit updated queue CSV and a run report.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shlex
import subprocess
import zipfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

import pandas as pd
from pypdf import PdfReader


POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
MAX_XLSX_ROWS_PER_SHEET = 1000
MAX_ZIP_EXTRACT_FILES = 30
MAX_ZIP_FILE_BYTES = 15 * 1024 * 1024
TEXT_MEMBER_EXTS = {".csv", ".txt", ".json", ".xml", ".md"}


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
    # Expect C:\... -> /mnt/c/...
    drive = win_out[0].lower()
    rest = win_out[2:].replace("\\", "/")
    return Path(f"/mnt/{drive}/{rest}")


def convert_pdf_to_md(src: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{sanitize_name(src.stem)}.md"
    reader = PdfReader(str(src))
    parts = [f"# {src.name}", ""]
    total_chars = 0
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        total_chars += len(text)
        parts.append(f"## Page {idx}")
        parts.append("")
        parts.append(text.strip())
        parts.append("")
    out_path.write_text("\n".join(parts), encoding="utf-8")
    return {"output": str(out_path), "pages": len(reader.pages), "chars": total_chars}


def convert_xlsx_to_outputs(src: Path, out_dir: Path) -> dict:
    base = out_dir / sanitize_name(src.stem)
    base.mkdir(parents=True, exist_ok=True)
    xls = pd.ExcelFile(src)
    summary = [f"# Workbook: {src.name}", ""]
    created = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(src, sheet_name=sheet)
        row_count = len(df)
        trimmed = df.head(MAX_XLSX_ROWS_PER_SHEET)
        safe_sheet = sanitize_name(sheet)
        csv_path = base / f"{safe_sheet}.csv"
        trimmed.to_csv(csv_path, index=False)
        created.append(str(csv_path))
        summary.append(f"## Sheet: {sheet}")
        summary.append(f"- rows_total: {row_count}")
        summary.append(f"- rows_exported: {len(trimmed)}")
        summary.append(f"- columns: {len(trimmed.columns)}")
        summary.append("")
    md_path = base / "_workbook_summary.md"
    md_path.write_text("\n".join(summary), encoding="utf-8")
    created.append(str(md_path))
    return {"output_dir": str(base), "sheets": len(xls.sheet_names), "files_created": len(created)}


def safe_member_path(root: Path, member_name: str) -> Path:
    parts = []
    for p in PurePosixPath(member_name).parts:
        if p in {"", ".", ".."}:
            continue
        parts.append(sanitize_name(p))
    if not parts:
        parts = ["unnamed"]
    return root.joinpath(*parts)


def convert_zip_to_outputs(src: Path, out_dir: Path) -> dict:
    base = out_dir / sanitize_name(src.stem)
    base.mkdir(parents=True, exist_ok=True)
    manifest_lines = [f"# ZIP Manifest: {src.name}", ""]
    extracted = 0
    scanned = 0
    with zipfile.ZipFile(src) as zf:
        infos = zf.infolist()
        for info in infos:
            scanned += 1
            ext = Path(info.filename).suffix.lower()
            manifest_lines.append(f"- {info.filename} ({info.file_size} bytes)")
            if extracted >= MAX_ZIP_EXTRACT_FILES:
                continue
            if ext not in TEXT_MEMBER_EXTS:
                continue
            if info.file_size > MAX_ZIP_FILE_BYTES:
                continue
            if info.is_dir():
                continue
            member_out = safe_member_path(base, info.filename)
            member_out.parent.mkdir(parents=True, exist_ok=True)
            data = zf.read(info.filename)
            member_out.write_bytes(data)
            extracted += 1

    md_path = base / "_zip_manifest.md"
    md_path.write_text("\n".join(manifest_lines), encoding="utf-8")
    return {"output_dir": str(base), "members_scanned": scanned, "members_extracted": extracted}


def main() -> None:
    parser = argparse.ArgumentParser(description="Process X staging conversion queue")
    parser.add_argument(
        "--queue",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_conversion_queue.csv",
    )
    parser.add_argument(
        "--cache-win-dir",
        default=r"C:\Users\jonat\x_staging_cache",
    )
    parser.add_argument(
        "--converted-root",
        default="/home/jonat/ai-stack/docs/data/governance_sources/windows_staging_import/converted",
    )
    parser.add_argument(
        "--queue-out",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_conversion_queue.csv",
    )
    parser.add_argument(
        "--report-out",
        default="",
        help="Optional explicit report path",
    )
    args = parser.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        raise FileNotFoundError(queue_path)
    converted_root = Path(args.converted_root)
    converted_root.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(queue_path.open("r", encoding="utf-8")))
    now = datetime.now(UTC).isoformat()
    counters = Counter()
    results = []

    for row in rows:
        converter = row.get("proposed_converter", "")
        src_win = row.get("source_path", "")
        record = {
            "source_path": src_win,
            "filename": row.get("filename", ""),
            "converter": converter,
            "status": "pending",
            "detail": "",
            "outputs": {},
        }
        try:
            local_src = copy_from_x_to_cache(src_win, args.cache_win_dir)
            if not local_src.exists():
                raise FileNotFoundError(local_src)

            if converter == "pdf_to_markdown":
                out = convert_pdf_to_md(local_src, converted_root / "pdf")
            elif converter == "xlsx_to_csv_markdown":
                out = convert_xlsx_to_outputs(local_src, converted_root / "xlsx")
            elif converter == "zip_unpack_then_filter":
                out = convert_zip_to_outputs(local_src, converted_root / "zip")
            else:
                raise ValueError(f"Unsupported converter: {converter}")

            record["status"] = "completed"
            record["outputs"] = out
            row["queue_status"] = "completed"
            counters["completed"] += 1
        except Exception as exc:
            record["status"] = "failed"
            record["detail"] = str(exc)
            row["queue_status"] = "failed"
            counters["failed"] += 1
        results.append(record)

    out_queue = Path(args.queue_out)
    out_queue.parent.mkdir(parents=True, exist_ok=True)
    with out_queue.open("w", newline="", encoding="utf-8") as f:
        fields = list(rows[0].keys()) if rows else []
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "timestamp_utc": now,
        "queue_path": str(queue_path),
        "queue_out": str(out_queue),
        "converted_root": str(converted_root),
        "total_rows": len(rows),
        "counts": dict(counters),
        "results": results,
    }

    if args.report_out:
        report_path = Path(args.report_out)
    else:
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        report_path = Path(f"/home/jonat/ai-stack/reports/index_runs/x_staging_conversion_run_{stamp}.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Queue updated: {out_queue}")
    print(f"Conversion report: {report_path}")
    print(f"Completed: {counters['completed']} Failed: {counters['failed']}")


if __name__ == "__main__":
    main()
