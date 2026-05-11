#!/usr/bin/env python3
"""
Export stable-sign Generation 5 causal examples to training JSONL.

Workflow:
1) Run paired-shock seed sweep (no Chroma writes).
2) Detect dominant effect direction across seeds.
3) Keep only runs whose effects match dominant direction.
4) Export instruction-style JSONL for specialist fine-tuning.
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


def sgn(value: float, eps: float = 1e-9) -> int:
    if value > eps:
        return 1
    if value < -eps:
        return -1
    return 0


def match_sign(value: float, target_sign: int) -> bool:
    current = sgn(value)
    return current == target_sign or current == 0


def run_one_seed(seed: int) -> dict:
    shocks = gen5.build_paired_shocks(seed)
    pop_a = _simulate_population(shocks=shocks, informed_fraction=1.0, asymmetric_noise=False)
    pop_b = _simulate_population(shocks=shocks, informed_fraction=gen5.INFORMED_FRACTION, asymmetric_noise=True)

    uninformed_disadvantaged = False
    if pop_b["uninformed_mean_fitness"] is not None and pop_b["informed_mean_fitness"] is not None:
        uninformed_disadvantaged = pop_b["uninformed_mean_fitness"] < pop_b["informed_mean_fitness"]

    effects = {
        "delta_mean_fitness_b_minus_a": pop_b["fitness_mean"] - pop_a["fitness_mean"],
        "delta_band2_b_minus_a": pop_b["band2_candidates"] - pop_a["band2_candidates"],
        "delta_dep_events_b_minus_a": pop_b["total_depletion_events"] - pop_a["total_depletion_events"],
        "pop_a_better_survival": pop_a["band2_candidates"] >= pop_b["band2_candidates"],
        "pop_a_lower_depletion": pop_a["total_depletion_events"] <= pop_b["total_depletion_events"],
        "uninformed_disadvantaged": uninformed_disadvantaged,
    }
    return {"seed": seed, "pop_a": pop_a, "pop_b": pop_b, "effects": effects}


def _simulate_population(*, shocks: list[list[dict[str, float]]], informed_fraction: float, asymmetric_noise: bool) -> dict:
    agents: list[dict] = []
    n_informed = int(gen5.NUM_AGENTS * informed_fraction)
    for i in range(gen5.NUM_AGENTS):
        agents.append(
            {
                "resources": gen5.STARTING_RESOURCES,
                "survival_ticks": 0,
                "depleted_ticks": 0,
                "resource_history": [gen5.STARTING_RESOURCES],
                "fitness": 0.0,
                "informed": i < n_informed,
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
    informed_agents = [a for a in agents if a["informed"]]
    uninformed_agents = [a for a in agents if not a["informed"]]

    def _mean(group: list[dict]) -> float | None:
        if not group:
            return None
        return float(statistics.mean(a["fitness"] for a in group))

    return {
        "fitness_mean": float(statistics.mean(fitnesses)),
        "band2_candidates": len([a for a in agents if a["survival_ticks"] >= gen5.BAND2_THRESHOLD]),
        "total_depletion_events": sum(depletions),
        "informed_mean_fitness": _mean(informed_agents),
        "uninformed_mean_fitness": _mean(uninformed_agents),
    }


def build_training_example(run: dict) -> dict:
    fx = run["effects"]
    seed = run["seed"]
    pa = run["pop_a"]
    pb = run["pop_b"]

    if fx["delta_band2_b_minus_a"] < 0:
        survival_line = "Population A has stronger survival (more Band 2 candidates)."
    elif fx["delta_band2_b_minus_a"] > 0:
        survival_line = "Population B has stronger survival (more Band 2 candidates)."
    else:
        survival_line = "Population A and B are tied on Band 2 candidates."

    if fx["delta_dep_events_b_minus_a"] < 0:
        depletion_line = "Population B has fewer depletion events."
    elif fx["delta_dep_events_b_minus_a"] > 0:
        depletion_line = "Population A has fewer depletion events."
    else:
        depletion_line = "Population A and B are tied on depletion events."

    supports_hypothesis = fx["pop_a_better_survival"] and fx["pop_a_lower_depletion"]
    hypothesis_line = (
        "This seed supports the symmetry-advantage hypothesis for Band 1."
        if supports_hypothesis
        else "This seed does not support a clear symmetry-advantage in Band 1."
    )

    return {
        "instruction": "Compare Population A vs Population B in a paired-shock ALife causal run and assess symmetry advantage.",
        "input": {
            "seed": seed,
            "population_a": {
                "fitness_mean": round(pa["fitness_mean"], 6),
                "band2_candidates": pa["band2_candidates"],
                "total_depletion_events": pa["total_depletion_events"],
            },
            "population_b": {
                "fitness_mean": round(pb["fitness_mean"], 6),
                "band2_candidates": pb["band2_candidates"],
                "total_depletion_events": pb["total_depletion_events"],
                "informed_mean_fitness": None if pb["informed_mean_fitness"] is None else round(pb["informed_mean_fitness"], 6),
                "uninformed_mean_fitness": None if pb["uninformed_mean_fitness"] is None else round(pb["uninformed_mean_fitness"], 6),
            },
        },
        "output": (
            f"Seed {seed}: mean fitness delta (B-A) is {fx['delta_mean_fitness_b_minus_a']:+.4f}, "
            f"Band2 delta (B-A) is {fx['delta_band2_b_minus_a']:+d}, "
            f"depletion-event delta (B-A) is {fx['delta_dep_events_b_minus_a']:+d}. "
            f"{survival_line} {depletion_line} {hypothesis_line}"
        ),
        "metadata": {
            "source": "gen5_causal_seed_sweep",
            "seed": seed,
            "labels": {
                "pop_a_better_survival": fx["pop_a_better_survival"],
                "pop_a_lower_depletion": fx["pop_a_lower_depletion"],
                "uninformed_disadvantaged": fx["uninformed_disadvantaged"],
            },
        },
    }


def build_consensus_example(summary: dict, stable_count: int, total_count: int) -> dict:
    return {
        "instruction": "Summarize whether ALife causal A/B effects are stable enough for training use.",
        "input": {
            "runs_total": total_count,
            "runs_stable": stable_count,
            "effect_means": summary["effect_means"],
            "sign_lock": summary["sign_lock"],
            "consistency_threshold": summary["consistency_threshold"],
            "causal_contrast_lock_pass": summary["causal_contrast_lock_pass"],
        },
        "output": (
            f"Across {total_count} seeds, {stable_count} matched dominant effect direction. "
            f"Sign-lock rates: A better survival={summary['sign_lock']['pop_a_better_survival_rate']:.3f}, "
            f"A lower depletion={summary['sign_lock']['pop_a_lower_depletion_rate']:.3f}, "
            f"uninformed disadvantaged={summary['sign_lock']['uninformed_disadvantaged_rate']:.3f}. "
            f"Causal contrast lock pass={summary['causal_contrast_lock_pass']}."
        ),
        "metadata": {"source": "gen5_causal_seed_sweep_summary"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export stable-sign gen5 causal examples to JSONL")
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--seed-start", type=int, default=505001)
    parser.add_argument("--consistency-threshold", type=float, default=0.70)
    parser.add_argument("--output-jsonl", default="")
    parser.add_argument("--output-report", default="")
    args = parser.parse_args()

    runs = [run_one_seed(args.seed_start + i) for i in range(args.seeds)]

    delta_fit = [r["effects"]["delta_mean_fitness_b_minus_a"] for r in runs]
    delta_band2 = [r["effects"]["delta_band2_b_minus_a"] for r in runs]
    delta_dep = [r["effects"]["delta_dep_events_b_minus_a"] for r in runs]

    dominant = {
        "delta_mean_fitness_b_minus_a_sign": sgn(statistics.mean(delta_fit)),
        "delta_band2_b_minus_a_sign": sgn(statistics.mean(delta_band2)),
        "delta_dep_events_b_minus_a_sign": sgn(statistics.mean(delta_dep)),
    }

    stable_runs = []
    for r in runs:
        fx = r["effects"]
        if (
            match_sign(fx["delta_mean_fitness_b_minus_a"], dominant["delta_mean_fitness_b_minus_a_sign"])
            and match_sign(float(fx["delta_band2_b_minus_a"]), dominant["delta_band2_b_minus_a_sign"])
            and match_sign(float(fx["delta_dep_events_b_minus_a"]), dominant["delta_dep_events_b_minus_a_sign"])
        ):
            stable_runs.append(r)

    summary = {
        "runs": len(runs),
        "sign_lock": {
            "pop_a_better_survival_rate": sum(1 for r in runs if r["effects"]["pop_a_better_survival"]) / len(runs),
            "pop_a_lower_depletion_rate": sum(1 for r in runs if r["effects"]["pop_a_lower_depletion"]) / len(runs),
            "uninformed_disadvantaged_rate": sum(1 for r in runs if r["effects"]["uninformed_disadvantaged"]) / len(runs),
        },
        "effect_means": {
            "delta_mean_fitness_b_minus_a": statistics.mean(delta_fit),
            "delta_band2_b_minus_a": statistics.mean(delta_band2),
            "delta_dep_events_b_minus_a": statistics.mean(delta_dep),
        },
        "dominant_effect_signs": dominant,
        "consistency_threshold": args.consistency_threshold,
    }
    summary["causal_contrast_lock_pass"] = (
        summary["sign_lock"]["pop_a_better_survival_rate"] >= args.consistency_threshold
        and summary["sign_lock"]["pop_a_lower_depletion_rate"] >= args.consistency_threshold
    )

    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_jsonl = (
        Path(args.output_jsonl)
        if args.output_jsonl
        else REPO_ROOT / f"ml/training_data/seeded_batches/gen5_stable_training_{stamp}.jsonl"
    )
    out_report = (
        Path(args.output_report)
        if args.output_report
        else REPO_ROOT / f"reports/index_runs/gen5_stable_training_report_{stamp}.json"
    )
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    out_report.parent.mkdir(parents=True, exist_ok=True)

    examples = [build_training_example(r) for r in stable_runs]
    examples.append(build_consensus_example(summary, len(stable_runs), len(runs)))

    with out_jsonl.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=True) + "\n")

    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "experiment": "gen5_stable_training_export",
        "seed_start": args.seed_start,
        "seed_count": args.seeds,
        "summary": summary,
        "stable_seed_count": len(stable_runs),
        "stable_seed_fraction": len(stable_runs) / len(runs),
        "stable_seeds": [r["seed"] for r in stable_runs],
        "output_jsonl": str(out_jsonl),
        "examples_written": len(examples),
    }
    out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Training JSONL: {out_jsonl}")
    print(f"Export report:  {out_report}")
    print(
        "Summary: "
        f"stable={len(stable_runs)}/{len(runs)} "
        f"pass={summary['causal_contrast_lock_pass']} "
        f"A_better_survival_rate={summary['sign_lock']['pop_a_better_survival_rate']:.3f} "
        f"A_lower_depletion_rate={summary['sign_lock']['pop_a_lower_depletion_rate']:.3f}"
    )


if __name__ == "__main__":
    main()
