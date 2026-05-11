#!/usr/bin/env python3
"""
Build governance -> ALife scenario -> Constella principle linkage set.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path


LINKS = [
    {
        "governance_concept": "targeted participation floor",
        "concept_keywords": ["ucf", "participation", "floor", "minimum compliance"],
        "alife_scenario_id": "exp9_diversity_floor",
        "alife_evidence": ["exp9", "alife_findings_pattern_8"],
        "constella_principle_id": "ucf-targeted-floor",
        "constella_mechanism": "Universal Civic Floor (UCF)",
        "epistemic_label": "synthesis/inference",
    },
    {
        "governance_concept": "founding diversity before crisis",
        "concept_keywords": ["founding diversity", "bootstrap", "pre-stress"],
        "alife_scenario_id": "exp8b_founding_window",
        "alife_evidence": ["exp8b", "alife_findings_pattern_7"],
        "constella_principle_id": "founding-diversity-before-crisis",
        "constella_mechanism": "Core Framework",
        "epistemic_label": "synthesis/inference",
    },
    {
        "governance_concept": "penumbra transitional scaffolding",
        "concept_keywords": ["penumbra", "gamer lifecycle", "transitional"],
        "alife_scenario_id": "exp9_gamer_lifecycle",
        "alife_evidence": ["exp9"],
        "constella_principle_id": "gamer-lifecycle-scaffolding",
        "constella_mechanism": "Penumbra Accord",
        "epistemic_label": "synthesis/inference",
    },
    {
        "governance_concept": "strategic retreat under specialization pressure",
        "concept_keywords": ["strategy escape", "dissolution", "adversarial adaptation"],
        "alife_scenario_id": "exp7_strategy_escape",
        "alife_evidence": ["exp7"],
        "constella_principle_id": "strategic-dissolution-survival",
        "constella_mechanism": "Penumbra Accord",
        "epistemic_label": "synthesis/inference",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build governance-ALife linkage set")
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/governance_alife_links.jsonl",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()

    with output.open("w", encoding="utf-8") as fh:
        for idx, row in enumerate(LINKS, start=1):
            rec = {
                "link_id": f"gov_alife_link_{idx:03d}",
                "created_at": now,
                **row,
            }
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")

    print(f"Output: {output}")
    print(f"Links: {len(LINKS)}")


if __name__ == "__main__":
    main()
