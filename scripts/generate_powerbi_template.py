#!/usr/bin/env python3
"""
Generate Power BI setup artifacts for FGS status CSV dashboards.

Full .pbit / PBIX automation typically needs pbi-tools, Tabular Editor, or the
Power BI REST API. This script writes:
  - FGS_Project_Dashboard_Setup.md — step-by-step Desktop instructions
  - FGS_Dashboard_model_definition.json — documented tabular-style schema (reference)

Outputs (prefer Windows Downloads when mounted from WSL):
  /mnt/c/Users/jonat/Downloads/FGS_Project_Dashboard_Setup.md
  /mnt/c/Users/jonat/Downloads/FGS_Dashboard_model_definition.json

Fallback if Downloads is missing:
  projects/status/FGS_Project_Dashboard_Setup.md
  projects/status/FGS_Dashboard_model_definition.json

Usage:
    python3 scripts/generate_powerbi_template.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_DIR = REPO_ROOT / "projects" / "status"
WIN_STATUS_DIR = r"\\wsl.localhost\Ubuntu\home\jonat\ai-stack\projects\status"

OUT_DOWNLOADS = Path("/mnt/c/Users/jonat/Downloads")


def output_dir() -> Path:
    if OUT_DOWNLOADS.is_dir():
        return OUT_DOWNLOADS
    return STATUS_DIR


def make_project_dashboard_artifacts() -> None:
    model = {
        "name": "FGS Project Dashboard",
        "tables": [
            {
                "name": "tracks",
                "partitions": [
                    {
                        "name": "tracks",
                        "source": {
                            "type": "m",
                            "expression": (
                                "let\n"
                                f'    Source = Csv.Document(File.Contents("{WIN_STATUS_DIR}\\\\tracks.csv"),'
                                "[Delimiter=\",\",Columns=10,Encoding=65001,QuoteStyle=QuoteStyle.None]),\n"
                                '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n'
                                '    in #"Promoted Headers"'
                            ),
                        },
                    }
                ],
                "columns": [
                    {"name": "track_id", "dataType": "string"},
                    {"name": "name", "dataType": "string"},
                    {"name": "status", "dataType": "string"},
                    {"name": "current_gate", "dataType": "string"},
                    {"name": "last_activity", "dataType": "dateTime"},
                    {"name": "total_gates", "dataType": "int64"},
                    {"name": "completed_gates", "dataType": "int64"},
                    {"name": "pending_gates", "dataType": "int64"},
                    {"name": "notes", "dataType": "string"},
                    {"name": "export_date", "dataType": "dateTime"},
                ],
                "measures": [
                    {
                        "name": "Completion %",
                        "expression": "DIVIDE(SUM(tracks[completed_gates]), SUM(tracks[total_gates]), 0)",
                    },
                    {
                        "name": "Active Tracks",
                        "expression": 'COUNTROWS(FILTER(tracks, tracks[status] = "active"))',
                    },
                    {
                        "name": "Days Since Activity",
                        "expression": "DATEDIFF(MAX(tracks[last_activity]), TODAY(), DAY)",
                    },
                ],
            },
            {
                "name": "gates",
                "partitions": [
                    {
                        "name": "gates",
                        "source": {
                            "type": "m",
                            "expression": (
                                "let\n"
                                f'    Source = Csv.Document(File.Contents("{WIN_STATUS_DIR}\\\\gates.csv"),'
                                "[Delimiter=\",\",Columns=7,Encoding=65001,QuoteStyle=QuoteStyle.None]),\n"
                                '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n'
                                '    in #"Promoted Headers"'
                            ),
                        },
                    }
                ],
                "columns": [
                    {"name": "track_id", "dataType": "string"},
                    {"name": "track_name", "dataType": "string"},
                    {"name": "gate_id", "dataType": "string"},
                    {"name": "title", "dataType": "string"},
                    {"name": "status", "dataType": "string"},
                    {"name": "blocker", "dataType": "string"},
                    {"name": "export_date", "dataType": "dateTime"},
                ],
                "measures": [
                    {
                        "name": "Completed Gates",
                        "expression": 'COUNTROWS(FILTER(gates, gates[status] = "completed"))',
                    },
                    {
                        "name": "Blocked Gates",
                        "expression": 'COUNTROWS(FILTER(gates, gates[blocker] <> ""))',
                    },
                ],
            },
            {
                "name": "components",
                "partitions": [
                    {
                        "name": "components",
                        "source": {
                            "type": "m",
                            "expression": (
                                "let\n"
                                f'    Source = Csv.Document(File.Contents("{WIN_STATUS_DIR}\\\\components.csv"),'
                                "[Delimiter=\",\",Columns=9,Encoding=65001,QuoteStyle=QuoteStyle.None]),\n"
                                '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n'
                                '    in #"Promoted Headers"'
                            ),
                        },
                    }
                ],
                "columns": [
                    {"name": "component_id", "dataType": "string"},
                    {"name": "name", "dataType": "string"},
                    {"name": "type", "dataType": "string"},
                    {"name": "file", "dataType": "string"},
                    {"name": "last_changed", "dataType": "dateTime"},
                    {"name": "change_summary", "dataType": "string"},
                    {"name": "dep_count", "dataType": "int64"},
                    {"name": "consumer_count", "dataType": "int64"},
                    {"name": "export_date", "dataType": "dateTime"},
                ],
            },
        ],
        "relationships": [
            {
                "name": "tracks_to_gates",
                "fromTable": "gates",
                "fromColumn": "track_id",
                "toTable": "tracks",
                "toColumn": "track_id",
                "crossFilteringBehavior": "oneDirection",
            }
        ],
    }

    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    instructions = f"""# FGS Project Dashboard — Power BI Setup
Generated: {generated}

## Data source paths (WSL UNC paths for Power BI on Windows)
tracks.csv:     {WIN_STATUS_DIR}\\tracks.csv
gates.csv:      {WIN_STATUS_DIR}\\gates.csv
components.csv: {WIN_STATUS_DIR}\\components.csv

Adjust the `\\\\wsl.localhost\\...` prefix if your distro name differs from **Ubuntu**.

## Quick setup in Power BI Desktop
1. File → New
2. Home → Get data → Text/CSV → open `tracks.csv` via the path above
3. Repeat for `gates.csv` and `components.csv`
4. Model view → relate `tracks[track_id]` → `gates[track_id]`

## Measures (Modeling → New measure)
Completion % = DIVIDE(SUM(tracks[completed_gates]), SUM(tracks[total_gates]), 0)
Active Tracks = COUNTROWS(FILTER(tracks, tracks[status] = "active"))
Completed Gates = COUNTROWS(FILTER(gates, gates[status] = "completed"))
Blocked Gates = COUNTROWS(FILTER(gates, gates[blocker] <> ""))
Days Since Activity = DATEDIFF(MAX(tracks[last_activity]), TODAY(), DAY)

## Refresh CSVs from WSL
python3 {REPO_ROOT}/scripts/export_status_csv.py

Then Power BI: Home → Refresh

## Full .pbit / CI automation (next step)
Options: **pbi-tools**, **Tabular Editor 3**, or **Power BI REST API** (Microsoft 365 workspace).
Tracked as gate **PBI1** in `project_status.json` (T5).
"""

    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)
    inst_path = out / "FGS_Project_Dashboard_Setup.md"
    model_path = out / "FGS_Dashboard_model_definition.json"
    inst_path.write_text(instructions, encoding="utf-8")
    model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")
    print(f"Written: {inst_path}")
    print(f"Written: {model_path}")
    print(f"CSV UNC base: {WIN_STATUS_DIR}")


if __name__ == "__main__":
    make_project_dashboard_artifacts()
