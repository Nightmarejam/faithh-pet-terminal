#!/usr/bin/env python3
"""Read ml/output/staleness_report.md and enqueue stale docs via queue_doc_update.py add."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_REPORT = REPO_ROOT / "ml" / "output" / "staleness_report.md"
QUEUE_SCRIPT = SCRIPT_DIR / "queue_doc_update.py"

CRITICAL_MARKERS = (
    "architecture/",
    "INFRASTRUCTURE",
    "SYSTEM_OVERVIEW",
    "scaffolding_state",
    "project_states",
    "CONTEXT.md",
    "component_map",
)
ARCHIVE_MARKERS = (
    "archive/",
    "legacy/",
    "roadmaps/",
    "implementation_summary/",
)


def classify_tier(path: str) -> str:
    p = path.replace("\\", "/")
    for m in CRITICAL_MARKERS:
        if m in p:
            return "critical"
    for m in ARCHIVE_MARKERS:
        if m in p:
            return "archive"
    return "reference"


def parse_stale_table(report_path: Path) -> list[tuple[str, str]]:
    """Return list of (path, issue) from Stale Documents markdown table."""
    text = report_path.read_text(encoding="utf-8")
    start = text.find("## Stale Documents")
    if start == -1:
        return []
    rest = text[start:]
    end_markers = ("\n## ", "\n---\n")
    end = len(rest)
    for em in end_markers:
        idx = rest.find(em, 1)
        if idx != -1:
            end = min(end, idx)
    section = rest[:end]
    rows: list[tuple[str, str]] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("|------") or "File" in line and "Age (days)" in line:
            continue
        m = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
        if not m:
            continue
        path = m.group(1).strip()
        parts = [p.strip() for p in line.split("|")]
        # | `path` | age | rel | sev | issue | (optional trailing empty)
        if len(parts) < 6:
            continue
        issue = parts[5].strip()
        rows.append((path, issue))
    return rows


def load_active_paths(project_states_path: Path) -> set[str]:
    with open(project_states_path, encoding="utf-8") as f:
        data = json.load(f)
    q = data.get("doc_update_queue") or []
    active: set[str] = set()
    for e in q:
        if not isinstance(e, dict):
            continue
        st = e.get("status")
        if st in ("pending", "in_progress"):
            active.add(str(e.get("path", "")).replace("\\", "/").strip())
    return active


def run_add(path: str, tier: str, reason: str) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(QUEUE_SCRIPT),
        "add",
        "--path",
        path,
        "--tier",
        tier,
        "--reason",
        reason,
        "--triggered-by",
        "staleness_report",
    ]
    p = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out.strip()


def main() -> int:
    report = DEFAULT_REPORT
    if len(sys.argv) > 1:
        report = Path(sys.argv[1]).resolve()
    if not report.is_file():
        print(f"error: staleness report not found: {report}", file=sys.stderr)
        return 1
    if not QUEUE_SCRIPT.is_file():
        print(f"error: queue script not found: {QUEUE_SCRIPT}", file=sys.stderr)
        return 1

    project_states = REPO_ROOT / "project_states.json"
    active = load_active_paths(project_states)
    rows = parse_stale_table(report)
    added = 0
    skipped = 0
    for path, issue in rows:
        norm = path.replace("\\", "/").strip()
        if norm in active:
            skipped += 1
            continue
        tier = classify_tier(norm)
        code, msg = run_add(norm, tier, issue)
        if code != 0:
            print(f"error: add failed for {norm}:\n{msg}", file=sys.stderr)
            return code
        if "skip:" in msg.lower():
            skipped += 1
        else:
            added += 1
            active.add(norm)
        if msg:
            print(msg)
    print(f"staleness_to_queue: processed {len(rows)} row(s), added {added}, skipped {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
