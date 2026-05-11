#!/usr/bin/env python3
"""
Generation five — dual-population causal test (paired shocks).

Population A (control): symmetric information; all agents perceive exact resources.
Population B (treatment): asymmetric information; 20% informed perceive exact resources,
80% uninformed perceive noisy resources (uniform ±40%).

Causal improvement over generation four:
- Both populations receive identical base environment shocks (paired RNG).
- Agent strategy depends on perceived resources, so information quality affects outcomes.
"""

from __future__ import annotations

import json
import random
import statistics
from datetime import datetime
from pathlib import Path

import chromadb

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = REPO_ROOT / "reports" / "alife"

CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000
COLLECTION = "alife_lineage"

# Locked Band 1 parameters (from generation three)
NUM_AGENTS = 50
NUM_TICKS = 10
STARTING_RESOURCES = 3.0
ACQUISITION_MIN = 0.3
ACQUISITION_MAX = 1.2
LOSS_MIN = 0.5
LOSS_MAX = 1.5
BAND2_THRESHOLD = 10

GENERATION = 5
EXPERIMENT = "generation_five_causal"
NOISE_LEVEL = 0.40
INFORMED_FRACTION = 0.20
PAIRED_SEED = 505001

# Simple policy driven by perceived resources.
# Misperception now causes concrete behavioral consequences.
LOW_RESOURCE_THRESHOLD = 1.0
HIGH_RESOURCE_THRESHOLD = 2.5
DESPERATE_GAIN_MULT = 1.25
DESPERATE_LOSS_MULT = 1.35
CONSERVE_GAIN_MULT = 0.90
CONSERVE_LOSS_MULT = 0.85


def resource_stability(history: list[float]) -> float:
    if len(history) < 2:
        return 1.0
    std = statistics.stdev(history[-5:]) if len(history) >= 5 else statistics.stdev(history)
    return 1.0 / (1.0 + std)


def build_paired_shocks(seed: int) -> list[list[dict[str, float]]]:
    rng = random.Random(seed)
    shocks: list[list[dict[str, float]]] = []
    for _ in range(NUM_TICKS):
        tick_shocks = []
        for _ in range(NUM_AGENTS):
            tick_shocks.append(
                {
                    "acquire": rng.uniform(ACQUISITION_MIN, ACQUISITION_MAX),
                    "lose": rng.uniform(LOSS_MIN, LOSS_MAX),
                    "noise": rng.uniform(-NOISE_LEVEL, NOISE_LEVEL),
                }
            )
        shocks.append(tick_shocks)
    return shocks


def strategy_multipliers(perceived_resources: float) -> tuple[float, float, str]:
    if perceived_resources <= LOW_RESOURCE_THRESHOLD:
        return DESPERATE_GAIN_MULT, DESPERATE_LOSS_MULT, "desperate_foraging"
    if perceived_resources >= HIGH_RESOURCE_THRESHOLD:
        return CONSERVE_GAIN_MULT, CONSERVE_LOSS_MULT, "conserve_mode"
    return 1.0, 1.0, "balanced"


def run_population(
    population_id: str,
    col,
    shocks: list[list[dict[str, float]]],
    run_id: str,
    informed_fraction: float,
    asymmetric_noise: bool,
) -> dict:
    agents = []
    n_informed = int(NUM_AGENTS * informed_fraction)
    for i in range(NUM_AGENTS):
        informed = i < n_informed
        agents.append(
            {
                "id": f"gen5_{population_id}_agent_{i:03d}",
                "lineage_id": f"lineage_{population_id}_{i:03d}",
                "resources": STARTING_RESOURCES,
                "survival_ticks": 0,
                "depleted_ticks": 0,
                "resource_history": [STARTING_RESOURCES],
                "fitness": 0.0,
                "informed": informed,
            }
        )

    all_docs, all_meta, all_ids = [], [], []
    tick_summaries = []

    for tick_idx in range(NUM_TICKS):
        tick = tick_idx + 1
        for i, agent in enumerate(agents):
            shock = shocks[tick_idx][i]

            if agent["informed"] or not asymmetric_noise:
                perceived = agent["resources"]
            else:
                perceived = max(0.0, agent["resources"] * (1.0 + shock["noise"]))

            gain_mult, loss_mult, strategy = strategy_multipliers(perceived)
            acquire = shock["acquire"] * gain_mult
            lose = shock["lose"] * loss_mult

            agent["resources"] = max(0.0, agent["resources"] + acquire - lose)
            agent["resource_history"].append(agent["resources"])

            if agent["resources"] > 0.0:
                agent["survival_ticks"] += 1
            else:
                agent["depleted_ticks"] += 1

            stab = resource_stability(agent["resource_history"])
            agent["fitness"] = agent["survival_ticks"] * stab

            doc_text = (
                f"Agent {agent['id']} tick {tick}: resources={agent['resources']:.2f} "
                f"perceived={perceived:.2f} strategy={strategy} "
                f"acq={acquire:.2f} loss={lose:.2f} fitness={agent['fitness']:.3f}"
            )
            all_docs.append(doc_text)
            all_meta.append(
                {
                    "experiment": EXPERIMENT,
                    "generation": GENERATION,
                    "run_id": run_id,
                    "population": population_id,
                    "agent_id": agent["id"],
                    "lineage_id": agent["lineage_id"],
                    "tick": tick,
                    "resources": round(agent["resources"], 4),
                    "perceived_resources": round(perceived, 4),
                    "strategy": strategy,
                    "acquire_effective": round(acquire, 4),
                    "loss_effective": round(lose, 4),
                    "fitness": round(agent["fitness"], 4),
                    "informed": agent["informed"],
                    "survival_ticks": agent["survival_ticks"],
                    "depleted_ticks": agent["depleted_ticks"],
                    "resource_stability": round(stab, 4),
                    "timestamp": datetime.now().isoformat(),
                }
            )
            all_ids.append(f"{run_id}_{agent['id']}_tick{tick:02d}")

        alive = sum(1 for a in agents if a["resources"] > 0.0)
        avg_fit = statistics.mean(a["fitness"] for a in agents)
        tick_summaries.append({"tick": tick, "alive": alive, "avg_fitness": round(avg_fit, 3)})
        print(f"  [{population_id}] Tick {tick:2d}: alive={alive}/50 avg_fitness={avg_fit:.3f}")

    batch_size = 100
    for i in range(0, len(all_docs), batch_size):
        col.add(
            documents=all_docs[i : i + batch_size],
            metadatas=all_meta[i : i + batch_size],
            ids=all_ids[i : i + batch_size],
        )

    fitnesses = [a["fitness"] for a in agents]
    depletions = [a["depleted_ticks"] for a in agents]
    band2 = [a for a in agents if a["survival_ticks"] >= BAND2_THRESHOLD]
    informed_agents = [a for a in agents if a["informed"]]
    uninformed_agents = [a for a in agents if not a["informed"]]

    def _mean_fitness(group: list[dict]) -> float | None:
        return round(statistics.mean(a["fitness"] for a in group), 3) if group else None

    return {
        "population": population_id,
        "tick_summaries": tick_summaries,
        "fitness": {
            "mean": round(statistics.mean(fitnesses), 3),
            "max": round(max(fitnesses), 3),
            "min": round(min(fitnesses), 3),
            "stdev": round(statistics.stdev(fitnesses), 3),
        },
        "survival": {
            "band2_candidates": len(band2),
            "agents_depleted": len([a for a in agents if a["depleted_ticks"] > 0]),
            "total_depletion_events": sum(depletions),
            "final_alive": tick_summaries[-1]["alive"],
        },
        "informed_vs_uninformed": {
            "informed_count": len(informed_agents),
            "uninformed_count": len(uninformed_agents),
            "informed_mean_fitness": _mean_fitness(informed_agents),
            "uninformed_mean_fitness": _mean_fitness(uninformed_agents),
            "informed_band2": len([a for a in informed_agents if a["survival_ticks"] >= BAND2_THRESHOLD]),
            "uninformed_band2": len([a for a in uninformed_agents if a["survival_ticks"] >= BAND2_THRESHOLD]),
        },
        "docs_written": len(all_docs),
    }


def print_comparison(result_a: dict, result_b: dict) -> None:
    print("\n=== GENERATION FIVE COMPARISON (CAUSAL) ===")
    print(f"{'Metric':<35} {'Pop A':>10} {'Pop B':>10} {'Difference':>12}")
    print("-" * 70)

    metrics = [
        ("Mean fitness", result_a["fitness"]["mean"], result_b["fitness"]["mean"]),
        ("Min fitness", result_a["fitness"]["min"], result_b["fitness"]["min"]),
        ("Fitness stdev", result_a["fitness"]["stdev"], result_b["fitness"]["stdev"]),
        ("Band 2 candidates", result_a["survival"]["band2_candidates"], result_b["survival"]["band2_candidates"]),
        ("Agents depleted", result_a["survival"]["agents_depleted"], result_b["survival"]["agents_depleted"]),
        ("Total depletion events", result_a["survival"]["total_depletion_events"], result_b["survival"]["total_depletion_events"]),
        ("Final alive", result_a["survival"]["final_alive"], result_b["survival"]["final_alive"]),
    ]

    for label, va, vb in metrics:
        diff = vb - va
        diff_str = f"{diff:+.3f}" if isinstance(diff, float) else f"{diff:+d}"
        print(f"  {label:<33} {str(va):>10} {str(vb):>10} {diff_str:>12}")

    ivu = result_b["informed_vs_uninformed"]
    print("\n  Population B breakdown (informed 20% vs uninformed 80%):")
    print(f"    Informed   (n={ivu['informed_count']}): mean_fitness={ivu['informed_mean_fitness']} band2={ivu['informed_band2']}")
    print(f"    Uninformed (n={ivu['uninformed_count']}): mean_fitness={ivu['uninformed_mean_fitness']} band2={ivu['uninformed_band2']}")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("gen5run_%Y%m%d_%H%M%S")

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)
    count_before = col.count()
    print(f"alife_lineage before: {count_before:,}")
    print(f"run_id: {run_id}")
    print(f"paired_seed: {PAIRED_SEED}\n")

    shocks = build_paired_shocks(PAIRED_SEED)

    print("=== POPULATION A — Symmetric Information ===")
    result_a = run_population(
        population_id="A",
        col=col,
        shocks=shocks,
        run_id=run_id,
        informed_fraction=1.0,
        asymmetric_noise=False,
    )

    print("\n=== POPULATION B — Asymmetric Information ===")
    result_b = run_population(
        population_id="B",
        col=col,
        shocks=shocks,
        run_id=run_id,
        informed_fraction=INFORMED_FRACTION,
        asymmetric_noise=True,
    )

    count_after = col.count()
    print_comparison(result_a, result_b)

    ivu = result_b["informed_vs_uninformed"]
    mi, mu = ivu["informed_mean_fitness"], ivu["uninformed_mean_fitness"]
    uninformed_disadvantaged = (mu < mi) if (mi is not None and mu is not None) else None

    summary = {
        "experiment": EXPERIMENT,
        "generation": GENERATION,
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "agents_per_population": NUM_AGENTS,
            "ticks": NUM_TICKS,
            "starting_resources": STARTING_RESOURCES,
            "acquisition": f"{ACQUISITION_MIN}-{ACQUISITION_MAX}",
            "loss": f"{LOSS_MIN}-{LOSS_MAX}",
            "noise_level_pop_b": NOISE_LEVEL,
            "informed_fraction_pop_b": INFORMED_FRACTION,
            "paired_seed": PAIRED_SEED,
            "paired_shocks": True,
            "strategy_model": {
                "low_threshold": LOW_RESOURCE_THRESHOLD,
                "high_threshold": HIGH_RESOURCE_THRESHOLD,
                "desperate_gain_mult": DESPERATE_GAIN_MULT,
                "desperate_loss_mult": DESPERATE_LOSS_MULT,
                "conserve_gain_mult": CONSERVE_GAIN_MULT,
                "conserve_loss_mult": CONSERVE_LOSS_MULT,
            },
        },
        "population_a": result_a,
        "population_b": result_b,
        "hypothesis_check": {
            "pop_a_band2": result_a["survival"]["band2_candidates"],
            "pop_b_band2": result_b["survival"]["band2_candidates"],
            "pop_a_better_survival": result_a["survival"]["band2_candidates"] >= result_b["survival"]["band2_candidates"],
            "pop_a_lower_depletion": result_a["survival"]["total_depletion_events"] <= result_b["survival"]["total_depletion_events"],
            "uninformed_disadvantaged": uninformed_disadvantaged,
        },
        "alife_lineage_count_before": count_before,
        "alife_lineage_count_after": count_after,
        "total_docs_written": result_a["docs_written"] + result_b["docs_written"],
    }

    report_path = REPORT_DIR / f"generation_five_dual_population_causal_{run_id}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nalife_lineage: {count_before:,} → {count_after:,}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
