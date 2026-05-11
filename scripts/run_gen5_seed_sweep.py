#!/usr/bin/env python3
"""
Run a multi-seed sweep for generation five causal A/B comparison.

This script intentionally does NOT write to ChromaDB. It is a fast,
reproducible gate-check utility for:
- causal contrast direction stability across seeds
- survivor/depletion effect consistency
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path("/home/jonat/ai-stack")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from projects.alife.experiments import generation_five_dual_population_causal as gen5


def run_population_sim(
    *,
    shocks: list[list[dict[str, float]]],
    informed_fraction: float,
    asymmetric_noise: bool,
) -> dict:
    agents: list[dict] = []
    n_informed = int(gen5.NUM_AGENTS * informed_fraction)
    for i in range(gen5.NUM_AGENTS):
        informed = i < n_informed
        agents.append(
            {
                "resources": gen5.STARTING_RESOURCES,
                "survival_ticks": 0,
                "depleted_ticks": 0,
                "resource_history": [gen5.STARTING_RESOURCES],
                "fitness": 0.0,
                "informed": informed,
            }
        )

    for tick_idx in range(gen5.NUM_TICKS):
        for i, agent in enumerate(agents):
            shock = shocks[tick_idx][i]
            if agent["informed"] or not asymmetric_noise:
                perceived = agent["resources"]
            else:
                perceived = max(0.0, agent["resources"] * (1.0 + shock["noise"]))

            gain_mult, loss_mult, _ = gen5.strategy_multipliers(perceived)
            acquire = shock["acquire"] * gain_mult
            lose = shock["lose"] * loss_mult

            agent["resources"] = max(0.0, agent["resources"] + acquire - lose)
            agent["resource_history"].append(agent["resources"])
            if agent["resources"] > 0.0:
                agent["survival_ticks"] += 1
            else:
                agent["depleted_ticks"] += 1
            stab = gen5.resource_stability(agent["resource_history"])
            agent["fitness"] = agent["survival_ticks"] * stab

    fitnesses = [a["fitness"] for a in agents]
    depletions = [a["depleted_ticks"] for a in agents]
    band2 = [a for a in agents if a["survival_ticks"] >= gen5.BAND2_THRESHOLD]
    informed_agents = [a for a in agents if a["informed"]]
    uninformed_agents = [a for a in agents if not a["informed"]]

    def _mean_fit(group: list[dict]) -> float | None:
        if not group:
            return None
        return float(statistics.mean(a["fitness"] for a in group))

    return {
        "fitness_mean": float(statistics.mean(fitnesses)),
        "fitness_stdev": float(statistics.stdev(fitnesses)),
        "band2_candidates": len(band2),
        "agents_depleted": len([a for a in agents if a["depleted_ticks"] > 0]),
        "total_depletion_events": sum(depletions),
        "final_alive": len([a for a in agents if a["resources"] > 0.0]),
        "informed_mean_fitness": _mean_fit(informed_agents),
        "uninformed_mean_fitness": _mean_fit(uninformed_agents),
    }


def summarize_runs(runs: list[dict], min_consistency: float) -> dict:
    n = len(runs)
    if n == 0:
        raise ValueError("No runs to summarize")

    better_survival = sum(1 for r in runs if r["effects"]["pop_a_better_survival"])
    lower_depletion = sum(1 for r in runs if r["effects"]["pop_a_lower_depletion"])
    uninformed_disadv = sum(1 for r in runs if r["effects"]["uninformed_disadvantaged"])

    mean_delta_fit = statistics.mean(r["effects"]["delta_mean_fitness_b_minus_a"] for r in runs)
    mean_delta_band2 = statistics.mean(r["effects"]["delta_band2_b_minus_a"] for r in runs)
    mean_delta_dep_events = statistics.mean(r["effects"]["delta_dep_events_b_minus_a"] for r in runs)

    sign_lock = {
        "pop_a_better_survival_rate": better_survival / n,
        "pop_a_lower_depletion_rate": lower_depletion / n,
        "uninformed_disadvantaged_rate": uninformed_disadv / n,
    }

    gate_pass = (
        sign_lock["pop_a_better_survival_rate"] >= min_consistency
        and sign_lock["pop_a_lower_depletion_rate"] >= min_consistency
    )

    return {
        "runs": n,
        "sign_lock": sign_lock,
        "effect_means": {
            "delta_mean_fitness_b_minus_a": mean_delta_fit,
            "delta_band2_b_minus_a": mean_delta_band2,
            "delta_dep_events_b_minus_a": mean_delta_dep_events,
        },
        "causal_contrast_lock_pass": gate_pass,
        "consistency_threshold": min_consistency,
    }


def to_markdown(report: dict) -> str:
    lines = []
    lines.append("# Generation Five Causal Seed Sweep")
    lines.append("")
    lines.append(f"- generated_at_utc: {report['timestamp_utc']}")
    lines.append(f"- seeds_tested: {report['seed_count']}")
    lines.append(f"- seed_start: {report['seed_start']}")
    lines.append(f"- consistency_threshold: {report['summary']['consistency_threshold']:.2f}")
    lines.append(f"- causal_contrast_lock_pass: {report['summary']['causal_contrast_lock_pass']}")
    lines.append("")
    s = report["summary"]["sign_lock"]
    lines.append("## Sign-Lock Rates")
    lines.append("")
    lines.append(f"- pop_a_better_survival_rate: {s['pop_a_better_survival_rate']:.3f}")
    lines.append(f"- pop_a_lower_depletion_rate: {s['pop_a_lower_depletion_rate']:.3f}")
    lines.append(f"- uninformed_disadvantaged_rate: {s['uninformed_disadvantaged_rate']:.3f}")
    lines.append("")
    e = report["summary"]["effect_means"]
    lines.append("## Mean Effects (B - A)")
    lines.append("")
    lines.append(f"- delta_mean_fitness_b_minus_a: {e['delta_mean_fitness_b_minus_a']:.4f}")
    lines.append(f"- delta_band2_b_minus_a: {e['delta_band2_b_minus_a']:.4f}")
    lines.append(f"- delta_dep_events_b_minus_a: {e['delta_dep_events_b_minus_a']:.4f}")
    lines.append("")
    lines.append("## Per-Seed Results")
    lines.append("")
    lines.append("| seed | d_fit (B-A) | d_band2 (B-A) | d_dep_events (B-A) | A_better_survival | A_lower_depletion | uninformed_disadvantaged |")
    lines.append("|---:|---:|---:|---:|---|---|---|")
    for r in report["runs"]:
        fx = r["effects"]
        lines.append(
            f"| {r['seed']} | {fx['delta_mean_fitness_b_minus_a']:.4f} | {fx['delta_band2_b_minus_a']} | {fx['delta_dep_events_b_minus_a']} | "
            f"{fx['pop_a_better_survival']} | {fx['pop_a_lower_depletion']} | {fx['uninformed_disadvantaged']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run generation five causal seed sweep (no Chroma writes)")
    parser.add_argument("--seeds", type=int, default=20, help="Number of seeds to run")
    parser.add_argument("--seed-start", type=int, default=505001, help="First paired seed")
    parser.add_argument(
        "--consistency-threshold",
        type=float,
        default=0.70,
        help="Minimum sign-lock rate required to declare causal contrast lock",
    )
    parser.add_argument("--output-json", default="", help="Optional JSON output path")
    parser.add_argument("--output-md", default="", help="Optional markdown output path")
    args = parser.parse_args()

    runs: list[dict] = []
    for i in range(args.seeds):
        seed = args.seed_start + i
        shocks = gen5.build_paired_shocks(seed)
        pop_a = run_population_sim(
            shocks=shocks,
            informed_fraction=1.0,
            asymmetric_noise=False,
        )
        pop_b = run_population_sim(
            shocks=shocks,
            informed_fraction=gen5.INFORMED_FRACTION,
            asymmetric_noise=True,
        )

        uninformed_disadvantaged = False
        if pop_b["uninformed_mean_fitness"] is not None and pop_b["informed_mean_fitness"] is not None:
            uninformed_disadvantaged = pop_b["uninformed_mean_fitness"] < pop_b["informed_mean_fitness"]

        effects = {
            "delta_mean_fitness_b_minus_a": round(pop_b["fitness_mean"] - pop_a["fitness_mean"], 6),
            "delta_band2_b_minus_a": pop_b["band2_candidates"] - pop_a["band2_candidates"],
            "delta_dep_events_b_minus_a": pop_b["total_depletion_events"] - pop_a["total_depletion_events"],
            "pop_a_better_survival": pop_a["band2_candidates"] >= pop_b["band2_candidates"],
            "pop_a_lower_depletion": pop_a["total_depletion_events"] <= pop_b["total_depletion_events"],
            "uninformed_disadvantaged": uninformed_disadvantaged,
        }
        runs.append({"seed": seed, "pop_a": pop_a, "pop_b": pop_b, "effects": effects})

    summary = summarize_runs(runs, args.consistency_threshold)
    out = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "experiment": "generation_five_causal_seed_sweep",
        "seed_start": args.seed_start,
        "seed_count": args.seeds,
        "parameters_ref": {
            "agents": gen5.NUM_AGENTS,
            "ticks": gen5.NUM_TICKS,
            "starting_resources": gen5.STARTING_RESOURCES,
            "acquisition": [gen5.ACQUISITION_MIN, gen5.ACQUISITION_MAX],
            "loss": [gen5.LOSS_MIN, gen5.LOSS_MAX],
            "noise_level": gen5.NOISE_LEVEL,
            "informed_fraction": gen5.INFORMED_FRACTION,
        },
        "summary": summary,
        "runs": runs,
    }

    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    json_path = Path(args.output_json) if args.output_json else REPO_ROOT / f"reports/index_runs/gen5_seed_sweep_{stamp}.json"
    md_path = Path(args.output_md) if args.output_md else REPO_ROOT / f"reports/index_runs/gen5_seed_sweep_{stamp}.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(out), encoding="utf-8")

    print(f"Seed sweep JSON: {json_path}")
    print(f"Seed sweep MD:   {md_path}")
    print(
        "Summary: "
        f"pass={summary['causal_contrast_lock_pass']} "
        f"A_better_survival_rate={summary['sign_lock']['pop_a_better_survival_rate']:.3f} "
        f"A_lower_depletion_rate={summary['sign_lock']['pop_a_lower_depletion_rate']:.3f}"
    )


if __name__ == "__main__":
    main()
