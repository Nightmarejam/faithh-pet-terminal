#!/usr/bin/env python3
"""
Build auditable Constella synthesis set from governance-ALife links.

Produces records with explicit epistemic labels:
- externally_sourced
- simulation_derived
- synthesis_inference
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Constella synthesis set")
    parser.add_argument(
        "--links",
        default="/home/jonat/ai-stack/reports/inventory/governance_alife_links.jsonl",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/constella_synthesis_set.jsonl",
    )
    args = parser.parse_args()

    links_path = Path(args.links)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not links_path.exists():
        raise FileNotFoundError(links_path)

    links = [
        json.loads(line)
        for line in links_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    now = datetime.now(UTC).isoformat()
    out_records = []
    for link in links:
        link_id = link["link_id"]
        concept = link["governance_concept"]
        scenario = link["alife_scenario_id"]
        principle = link["constella_principle_id"]
        mechanism = link["constella_mechanism"]
        evidence = ", ".join(link.get("alife_evidence", []))

        out_records.append(
            {
                "synthesis_id": f"{link_id}_ext",
                "epistemic_label": "externally_sourced",
                "governance_concept": concept,
                "statement": f"Governance source concept identified: {concept}.",
                "alife_scenario_id": scenario,
                "constella_principle_id": principle,
                "constella_mechanism": mechanism,
                "created_at": now,
            }
        )
        out_records.append(
            {
                "synthesis_id": f"{link_id}_sim",
                "epistemic_label": "simulation_derived",
                "governance_concept": concept,
                "statement": f"ALife evidence for scenario {scenario}: {evidence}.",
                "alife_scenario_id": scenario,
                "constella_principle_id": principle,
                "constella_mechanism": mechanism,
                "created_at": now,
            }
        )
        out_records.append(
            {
                "synthesis_id": f"{link_id}_syn",
                "epistemic_label": "synthesis_inference",
                "governance_concept": concept,
                "statement": (
                    f"Synthesis update: apply {concept} through {mechanism} "
                    f"using scenario {scenario} to support principle {principle}."
                ),
                "alife_scenario_id": scenario,
                "constella_principle_id": principle,
                "constella_mechanism": mechanism,
                "created_at": now,
            }
        )

    with output_path.open("w", encoding="utf-8") as fh:
        for rec in out_records:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")

    print(f"Output: {output_path}")
    print(f"Records: {len(out_records)}")


if __name__ == "__main__":
    main()
