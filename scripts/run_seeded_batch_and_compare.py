#!/usr/bin/env python3
"""
Run a seeded ALife batch and emit side-by-side comparison artifacts.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path("/home/jonat/ai-stack")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from projects.alife.experiments import exp9_diversity_floor as exp9


def run_variant(
    *,
    name: str,
    threshold: float,
    bonus: int,
    drain: float,
    seed: int,
    ticks: int,
    log_interval: int,
) -> dict:
    original = {
        "threshold": exp9.NAKED_FLOOR_THRESHOLD,
        "bonus": exp9.NAKED_FLOOR_BONUS,
        "drain": exp9.PARASITE_DRAIN_RATE,
    }
    exp9.NAKED_FLOOR_THRESHOLD = threshold
    exp9.NAKED_FLOOR_BONUS = bonus
    exp9.PARASITE_DRAIN_RATE = drain
    random.seed(seed)

    try:
        result = exp9.run_exp9(ticks=ticks, log_interval=log_interval)
    finally:
        exp9.NAKED_FLOOR_THRESHOLD = original["threshold"]
        exp9.NAKED_FLOOR_BONUS = original["bonus"]
        exp9.PARASITE_DRAIN_RATE = original["drain"]

    return {
        "variant": name,
        "seed": seed,
        "params": {
            "NAKED_FLOOR_THRESHOLD": threshold,
            "NAKED_FLOOR_BONUS": bonus,
            "PARASITE_DRAIN_RATE": drain,
            "ticks": ticks,
        },
        "result_summary": {
            "collapsed": result.get("collapsed"),
            "collapse_tick": result.get("collapse_tick"),
            "final_population": result.get("final_population"),
            "floor_activations": result.get("floor_activations"),
            "max_adapt_reached": result.get("max_adapt_reached"),
            "strategy_escape_tick": result.get("strategy_escape_tick"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run seeded ALife batch and side-by-side comparison")
    parser.add_argument("--ticks", type=int, default=3000)
    parser.add_argument("--log-interval", type=int, default=500)
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional JSON output path",
    )
    parser.add_argument(
        "--output-md",
        default="",
        help="Optional markdown output path",
    )
    args = parser.parse_args()

    variants = [
        {
            "name": "seed_001_ucf_stress_sweep",
            "threshold": 0.17,
            "bonus": 4,
            "drain": 1.5,
            "seed": 101,
        },
        {
            "name": "seed_002_founding_window_map",
            "threshold": 0.15,
            "bonus": 3,
            "drain": 1.3,
            "seed": 202,
        },
        {
            "name": "seed_003_adversarial_replay",
            "threshold": 0.16,
            "bonus": 3,
            "drain": 1.8,
            "seed": 303,
        },
    ]

    runs = []
    for v in variants:
        print(f"Running variant: {v['name']}")
        runs.append(
            run_variant(
                name=v["name"],
                threshold=v["threshold"],
                bonus=v["bonus"],
                drain=v["drain"],
                seed=v["seed"],
                ticks=args.ticks,
                log_interval=args.log_interval,
            )
        )

    out = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "batch_type": "seeded_alife_side_by_side",
        "runs": runs,
    }
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    json_path = Path(args.output_json) if args.output_json else REPO_ROOT / f"reports/index_runs/alife_seeded_batch_{stamp}.json"
    md_path = Path(args.output_md) if args.output_md else REPO_ROOT / f"reports/index_runs/alife_seeded_batch_{stamp}.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# Seeded ALife Batch Side-by-Side",
        "",
        f"- generated_at_utc: {out['timestamp_utc']}",
        f"- ticks_per_run: {args.ticks}",
        "",
        "| variant | seed | threshold | bonus | drain | collapsed | final_pop | floor_activations | max_adapt | strategy_escape_tick |",
        "|---|---:|---:|---:|---:|---|---:|---:|---:|---:|",
    ]
    for r in runs:
        s = r["result_summary"]
        p = r["params"]
        lines.append(
            "| "
            f"{r['variant']} | {r['seed']} | {p['NAKED_FLOOR_THRESHOLD']:.2f} | {p['NAKED_FLOOR_BONUS']} | {p['PARASITE_DRAIN_RATE']:.2f} | "
            f"{s['collapsed']} | {s['final_population']} | {s['floor_activations']} | {s['max_adapt_reached']} | {s['strategy_escape_tick']} |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Batch JSON: {json_path}")
    print(f"Batch table: {md_path}")


if __name__ == "__main__":
    main()
