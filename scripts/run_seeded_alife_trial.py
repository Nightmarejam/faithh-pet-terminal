#!/usr/bin/env python3
"""
Run a short seeded ALife trial using generated action items.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path("/home/jonat/ai-stack")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from projects.alife.experiments import exp9_diversity_floor as exp9


def main() -> None:
    parser = argparse.ArgumentParser(description="Run seeded ALife trial from action items")
    parser.add_argument(
        "--action-items",
        default="/home/jonat/ai-stack/reports/index_runs/alife_seeded_action_items.json",
    )
    parser.add_argument("--ticks", type=int, default=4000)
    parser.add_argument("--log-interval", type=int, default=500)
    parser.add_argument(
        "--output",
        default="",
        help="Optional output JSON path",
    )
    args = parser.parse_args()

    action_items_path = Path(args.action_items)
    if not action_items_path.exists():
        raise FileNotFoundError(action_items_path)

    action_doc = json.loads(action_items_path.read_text(encoding="utf-8"))
    items = action_doc.get("seeded_action_items", [])

    # Seeded trial knobs derived from first action item intent:
    # broaden floor exploration for a quick trail run.
    original_threshold = exp9.NAKED_FLOOR_THRESHOLD
    original_bonus = exp9.NAKED_FLOOR_BONUS
    exp9.NAKED_FLOOR_THRESHOLD = 0.17
    exp9.NAKED_FLOOR_BONUS = 4

    try:
        result = exp9.run_exp9(ticks=args.ticks, log_interval=args.log_interval)
    finally:
        exp9.NAKED_FLOOR_THRESHOLD = original_threshold
        exp9.NAKED_FLOOR_BONUS = original_bonus

    trial = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "trial_type": "seeded_action_item_trail_run",
        "source_action_items_path": str(action_items_path),
        "action_items_count": len(items),
        "seeded_overrides": {
            "NAKED_FLOOR_THRESHOLD": 0.17,
            "NAKED_FLOOR_BONUS": 4,
        },
        "run_args": {"ticks": args.ticks, "log_interval": args.log_interval},
        "result_summary": {
            "collapsed": result.get("collapsed"),
            "collapse_tick": result.get("collapse_tick"),
            "final_population": result.get("final_population"),
            "floor_activations": result.get("floor_activations"),
            "max_adapt_reached": result.get("max_adapt_reached"),
            "strategy_escape_tick": result.get("strategy_escape_tick"),
        },
        "result_path_reference": "genomic_results/exp9_diversity_floor_results.json",
    }

    if args.output:
        out = Path(args.output)
    else:
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        out = Path(f"/home/jonat/ai-stack/reports/index_runs/alife_seeded_trial_{stamp}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(trial, indent=2), encoding="utf-8")

    print(f"Trial report: {out}")
    print(
        "Summary: "
        f"collapsed={trial['result_summary']['collapsed']} "
        f"final_population={trial['result_summary']['final_population']} "
        f"floor_activations={trial['result_summary']['floor_activations']}"
    )


if __name__ == "__main__":
    main()
