#!/usr/bin/env python3
"""
Build seeded ALife experiment action items from staged governance intake.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build seeded ALife action items")
    parser.add_argument(
        "--manifest",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_manifest.csv",
    )
    parser.add_argument(
        "--queue",
        default="/home/jonat/ai-stack/reports/inventory/x_staging_conversion_queue.csv",
    )
    parser.add_argument(
        "--output-json",
        default="/home/jonat/ai-stack/reports/index_runs/alife_seeded_action_items.json",
    )
    parser.add_argument(
        "--output-jsonl",
        default="/home/jonat/ai-stack/reports/inventory/alife_seeded_action_items.jsonl",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    queue_path = Path(args.queue)
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    if not queue_path.exists():
        raise FileNotFoundError(queue_path)

    manifest = list(csv.DictReader(manifest_path.open("r", encoding="utf-8")))
    queue = list(csv.DictReader(queue_path.open("r", encoding="utf-8")))
    now = datetime.now(UTC).isoformat()

    staged_direct = [r for r in manifest if r.get("ingestion_action") == "stage_direct"]
    convert_required = [r for r in manifest if r.get("ingestion_action") == "convert_required"]

    action_items = [
        {
            "action_id": "alife_seed_001",
            "title": "UCF threshold stress sweep from constitutional source set",
            "priority": "high",
            "alife_target_experiment": "exp9_diversity_floor",
            "input_sources": [
                "United Nations Charter.md",
                "Universal Declaration of Human Rights.md",
                "The Constitution of the United States_ A Transcription _ National Archives.pdf",
            ],
            "task": (
                "Run parameter sweep for floor trigger thresholds (0.10 to 0.20) and compare "
                "survival, activation cadence, and commons burden."
            ),
            "acceptance": "Report includes activation intervals, intervention duration distribution, and fail/survive labels.",
            "status": "pending",
        },
        {
            "action_id": "alife_seed_002",
            "title": "Governance dataset-to-scenario mapping batch",
            "priority": "high",
            "alife_target_experiment": "exp8b_founding_window",
            "input_sources": [
                "wgidataset_with_sourcedata-2025.xlsx",
                "Raw Data from Underlying Data Sources (1996-2024).xlsx",
                "V-Dem-CD-v16_csv.zip",
            ],
            "task": (
                "Extract governance indicators, normalize as scenario seed vectors, and test founding-window "
                "sensitivity under diverse initial compositions."
            ),
            "acceptance": "Scenario seed file produced with source provenance and top indicator weights.",
            "status": "pending",
        },
        {
            "action_id": "alife_seed_003",
            "title": "Adversarial adaptation replay from legal corpus",
            "priority": "medium",
            "alife_target_experiment": "exp7_strategy_escape",
            "input_sources": [
                "xml_uscAll@119-73.zip",
                "Federal Register __ API Documentation.pdf",
                "UNdata _ api manual.pdf",
            ],
            "task": (
                "Build strategy-shift perturbation scenarios using legal/policy language motifs and "
                "measure retreat/dissolution under specialization pressure."
            ),
            "acceptance": "Comparative run log with baseline vs seeded perturbation outcomes.",
            "status": "pending",
        },
    ]

    summary = {
        "generated_at_utc": now,
        "manifest_path": str(manifest_path),
        "queue_path": str(queue_path),
        "manifest_rows": len(manifest),
        "stage_direct_rows": len(staged_direct),
        "convert_required_rows": len(convert_required),
        "conversion_queue_rows": len(queue),
        "seeded_action_items_count": len(action_items),
        "seeded_action_items": action_items,
    }

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    out_jsonl = Path(args.output_jsonl)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as fh:
        for item in action_items:
            rec = {
                "doc_id": f"alife_seed_action_{item['action_id']}",
                "created_at": now,
                **item,
            }
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")

    print(f"Action items report: {out_json}")
    print(f"Action items JSONL: {out_jsonl}")
    print(f"Seeded action items: {len(action_items)}")


if __name__ == "__main__":
    main()
