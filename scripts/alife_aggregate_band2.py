#!/usr/bin/env python3
"""Aggregate Band 2 generation reports across multiple runs."""

from __future__ import annotations

import argparse
import glob
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    var = sum((x - mu) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(var)


def safe_get(d: dict[str, Any], key: str, default: float = 0.0) -> float:
    val = d.get(key, default)
    if isinstance(val, (int, float)):
        return float(val)
    return default


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": mean(values),
        "stdev": stdev(values),
        "min": min(values),
        "max": max(values),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate Band 2 generation runs.")
    parser.add_argument("--generation", type=int, default=4, help="Band 2 generation number")
    parser.add_argument(
        "--reports-dir",
        default="reports/alife",
        help="Directory containing band2_generation*.json files",
    )
    parser.add_argument(
        "--pattern",
        default="",
        help="Glob pattern relative to repo root (e.g. reports/alife/band2_generation5_*.json). Overrides default.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output path. Default: reports/alife/band2_generationN_aggregate_<timestamp>.json",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    reports_dir = (repo_root / args.reports_dir).resolve()
    if args.pattern:
        pattern = str((repo_root / args.pattern).resolve())
    else:
        pattern = str(reports_dir / f"band2_generation{args.generation}_*.json")
    paths = sorted(glob.glob(pattern))
    paths = [p for p in paths if "aggregate" not in Path(p).name.lower()]

    if not paths:
        raise SystemExit(f"No reports found for pattern: {pattern}")

    a_mutual: list[float] = []
    b_mutual: list[float] = []
    a_false: list[float] = []
    b_false: list[float] = []
    a_net: list[float] = []
    b_net: list[float] = []
    a_stability: list[float] = []
    b_stability: list[float] = []
    a_band3_count: list[float] = []
    b_band3_count: list[float] = []
    a_band3_score: list[float] = []
    b_band3_score: list[float] = []
    score_gap: list[float] = []
    hypothesis_supported_count = 0

    lineage_before_first = None
    lineage_after_last = None

    for p in paths:
        with open(p, encoding="utf-8") as f:
            run = json.load(f)

        pop_a = run.get("population_A", {})
        pop_b = run.get("population_B", {})
        hyp = run.get("hypothesis_check", {})

        a_mutual.append(safe_get(pop_a, "mutual_benefit_rate"))
        b_mutual.append(safe_get(pop_b, "mutual_benefit_rate"))
        a_false.append(safe_get(pop_a, "false_cooperation_rate"))
        b_false.append(safe_get(pop_b, "false_cooperation_rate"))
        a_net.append(safe_get(pop_a, "mean_net_resource_from_cooperation"))
        b_net.append(safe_get(pop_b, "mean_net_resource_from_cooperation"))
        a_stability.append(safe_get(pop_a, "trust_network_stability"))
        b_stability.append(safe_get(pop_b, "trust_network_stability"))
        a_band3_count.append(float(len(pop_a.get("band3_candidates", []))))
        b_band3_count.append(float(len(pop_b.get("band3_candidates", []))))
        a_band3_score.append(safe_get(pop_a, "mean_band3_score"))
        b_band3_score.append(safe_get(pop_b, "mean_band3_score"))

        gap_val = run.get("band3_score_gap")
        if isinstance(gap_val, (int, float)):
            score_gap.append(float(gap_val))
        else:
            score_gap.append(a_band3_score[-1] - b_band3_score[-1])

        if hyp.get("hypothesis_supported") is True:
            hypothesis_supported_count += 1

        if lineage_before_first is None:
            lineage_before_first = run.get("alife_lineage_before")
        lineage_after_last = run.get("alife_lineage_after")

    n = len(paths)
    trust_a_higher_runs = sum(
        1 for i in range(n) if a_stability[i] > b_stability[i]
    )
    trust_equal_runs = sum(1 for i in range(n) if a_stability[i] == b_stability[i])

    support_rate = hypothesis_supported_count / n if n else 0.0
    trust_gap = mean(a_stability) - mean(b_stability)

    aggregate = {
        "experiment": "band2_cooperation",
        "generation": args.generation,
        "run_count": n,
        "source_reports": [str(Path(p).relative_to(repo_root)) for p in paths],
        "hypothesis_support_rate": support_rate,
        "trust_stability_gap": trust_gap,
        "trust_stability_A_higher_runs": trust_a_higher_runs,
        "trust_stability_equal_runs": trust_equal_runs,
        "trust_stability_A_higher_fraction": trust_a_higher_runs / n if n else 0.0,
        "band3_candidates_A_mean": mean(a_band3_count),
        "band3_candidates_B_mean": mean(b_band3_count),
        "population_A": {
            "mutual_benefit_rate": summarize(a_mutual),
            "false_cooperation_rate": summarize(a_false),
            "mean_net_resource_from_cooperation": summarize(a_net),
            "trust_network_stability": summarize(a_stability),
            "band3_candidate_count": summarize(a_band3_count),
            "band3_candidates": summarize(a_band3_count),
            "mean_band3_score": summarize(a_band3_score),
        },
        "population_B": {
            "mutual_benefit_rate": summarize(b_mutual),
            "false_cooperation_rate": summarize(b_false),
            "mean_net_resource_from_cooperation": summarize(b_net),
            "trust_network_stability": summarize(b_stability),
            "band3_candidate_count": summarize(b_band3_count),
            "band3_candidates": summarize(b_band3_count),
            "mean_band3_score": summarize(b_band3_score),
        },
        "deltas_A_minus_B": {
            "mutual_benefit_rate_mean_gap": mean(a_mutual) - mean(b_mutual),
            "false_cooperation_rate_mean_gap": mean(a_false) - mean(b_false),
            "mean_net_resource_mean_gap": mean(a_net) - mean(b_net),
            "trust_stability_mean_gap": trust_gap,
            "band3_candidate_count_mean_gap": mean(a_band3_count) - mean(b_band3_count),
            "mean_band3_score_mean_gap": mean(a_band3_score) - mean(b_band3_score),
            "band3_score_gap_reported": summarize(score_gap),
        },
        "hypothesis_support": {
            "supported_runs": hypothesis_supported_count,
            "support_rate": support_rate,
        },
        "alife_lineage_window": {
            "before_first_run": lineage_before_first,
            "after_last_run": lineage_after_last,
            "delta": (
                (int(lineage_after_last) - int(lineage_before_first))
                if lineage_before_first is not None and lineage_after_last is not None
                else None
            ),
        },
        "generated_at": datetime.now().isoformat(),
    }

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        out_path = (repo_root / args.output).resolve()
    else:
        out_path = reports_dir / f"band2_generation{args.generation}_aggregate_{stamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")

    print(f"Runs aggregated: {n}")
    print(f"Output: {out_path}")
    print(f"Hypothesis support rate: {aggregate['hypothesis_support']['support_rate']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
