#!/usr/bin/env python3
"""
Generation four — First real experiment: Population A vs Population B.

Population A: Symmetric information — all agents see exact resource levels.
Population B: Asymmetric information — 80% see noisy resource data (±40% noise),
              20% (informed class) see exact values.

Tests the Constella founding hypothesis:
"If everyone knew exactly what worth was, there wouldn't be too many
people trying to take advantage of each other."

Operationally: does information symmetry produce better survival outcomes,
especially for the weakest agents?
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

CHROMA_HOST = "192.158.1.10"
CHROMA_PORT = 8000
COLLECTION = "alife_lineage"

# Locked Band 1 parameters (confirmed generation three)
NUM_AGENTS = 50
NUM_TICKS = 10
STARTING_RESOURCES = 3.0
ACQUISITION_MIN = 0.3
ACQUISITION_MAX = 1.2
LOSS_MIN = 0.5
LOSS_MAX = 1.5
BAND2_THRESHOLD = 10

GENERATION = 4
NOISE_LEVEL = 0.40  # ±40% noise for uninformed agents (uniform on [-0.4, 0.4] multiplier)
INFORMED_FRACTION = 0.20  # 20% of Population B see exact values


def resource_stability(history: list[float]) -> float:
    if len(history) < 2:
        return 1.0
    std = statistics.stdev(history[-5:]) if len(history) >= 5 else statistics.stdev(history)
    return 1.0 / (1.0 + std)


def run_population(
    population_id: str,
    col,
    informed_fraction: float = 1.0,
    noise_level: float = 0.0,
) -> dict:
    """
    Run one population for NUM_TICKS ticks.
    informed_fraction: fraction of agents with exact resource visibility.
    noise_level: max absolute fractional noise on perceived resources for uninformed agents
                 (perceived = actual * (1 + U[-noise_level, noise_level])).
    """
    random.seed()

    agents = []
    n_informed = int(NUM_AGENTS * informed_fraction)
    for i in range(NUM_AGENTS):
        informed = i < n_informed
        agents.append(
            {
                "id": f"gen4_{population_id}_agent_{i:03d}",
                "lineage_id": f"lineage_{population_id}_{i:03d}",
                "resources": STARTING_RESOURCES,
                "survival_ticks": 0,
                "depleted_ticks": 0,
                "resource_history": [STARTING_RESOURCES],
                "band": 1,
                "fitness": 0.0,
                "informed": informed,
                "population": population_id,
            }
        )

    all_docs, all_meta, all_ids = [], [], []
    tick_summaries = []

    for tick in range(1, NUM_TICKS + 1):
        for agent in agents:
            acquire = random.uniform(ACQUISITION_MIN, ACQUISITION_MAX)
            lose = random.uniform(LOSS_MIN, LOSS_MAX)
            agent["resources"] = max(0.0, agent["resources"] + acquire - lose)
            agent["resource_history"].append(agent["resources"])

            if agent["informed"] or noise_level == 0.0:
                perceived = agent["resources"]
            else:
                noise = random.uniform(-noise_level, noise_level)
                perceived = max(0.0, agent["resources"] * (1.0 + noise))

            if agent["resources"] > 0:
                agent["survival_ticks"] += 1
            else:
                agent["depleted_ticks"] += 1

            stab = resource_stability(agent["resource_history"])
            agent["fitness"] = agent["survival_ticks"] * stab

            doc_text = (
                f"Agent {agent['id']} tick {tick}: "
                f"resources={agent['resources']:.2f} "
                f"perceived={perceived:.2f} "
                f"fitness={agent['fitness']:.3f} "
                f"informed={agent['informed']} "
                f"population={population_id}"
            )
            all_docs.append(doc_text)
            all_meta.append(
                {
                    "experiment": "generation_four",
                    "generation": GENERATION,
                    "population": population_id,
                    "agent_id": agent["id"],
                    "lineage_id": agent["lineage_id"],
                    "tick": tick,
                    "resources": round(agent["resources"], 4),
                    "perceived_resources": round(perceived, 4),
                    "fitness": round(agent["fitness"], 4),
                    "band": agent["band"],
                    "informed": agent["informed"],
                    "survival_ticks": agent["survival_ticks"],
                    "depleted_ticks": agent["depleted_ticks"],
                    "resource_stability": round(stab, 4),
                    "timestamp": datetime.now().isoformat(),
                }
            )
            all_ids.append(f"{agent['id']}_tick{tick:02d}")

        alive = sum(1 for a in agents if a["resources"] > 0)
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

    def _mean_fit(xs: list) -> float | None:
        return round(statistics.mean(x["fitness"] for x in xs), 3) if xs else None

    result = {
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
            "informed_mean_fitness": _mean_fit(informed_agents),
            "uninformed_mean_fitness": _mean_fit(uninformed_agents),
            "informed_band2": len([a for a in informed_agents if a["survival_ticks"] >= BAND2_THRESHOLD]),
            "uninformed_band2": len([a for a in uninformed_agents if a["survival_ticks"] >= BAND2_THRESHOLD]),
        },
        "docs_written": len(all_docs),
    }
    return result


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)
    count_before = col.count()
    print(f"alife_lineage before: {count_before:,}\n")

    print("=== POPULATION A — Symmetric Information ===")
    result_a = run_population("A", col, informed_fraction=1.0, noise_level=0.0)

    print()

    print("=== POPULATION B — Asymmetric Information ===")
    result_b = run_population("B", col, informed_fraction=INFORMED_FRACTION, noise_level=NOISE_LEVEL)

    count_after = col.count()

    print("\n=== GENERATION FOUR COMPARISON ===")
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
        if isinstance(va, float) and isinstance(vb, float):
            diff_str = f"{diff:+.3f}"
        else:
            diff_str = f"{diff:+d}"
        print(f"  {label:<33} {str(va):>10} {str(vb):>10} {diff_str:>12}")

    print("\n  Population B breakdown (informed 20% vs uninformed 80%):")
    ivu = result_b["informed_vs_uninformed"]
    print(f"    Informed   (n={ivu['informed_count']}): mean_fitness={ivu['informed_mean_fitness']} band2={ivu['informed_band2']}")
    print(f"    Uninformed (n={ivu['uninformed_count']}): mean_fitness={ivu['uninformed_mean_fitness']} band2={ivu['uninformed_band2']}")

    mi, mu = ivu["informed_mean_fitness"], ivu["uninformed_mean_fitness"]
    uninformed_disadvantaged = None
    if mi is not None and mu is not None:
        uninformed_disadvantaged = mu < mi

    summary = {
        "experiment": "generation_four",
        "generation": GENERATION,
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "agents_per_population": NUM_AGENTS,
            "ticks": NUM_TICKS,
            "starting_resources": STARTING_RESOURCES,
            "acquisition": f"{ACQUISITION_MIN}-{ACQUISITION_MAX}",
            "loss": f"{LOSS_MIN}-{LOSS_MAX}",
            "noise_level_pop_b": NOISE_LEVEL,
            "informed_fraction_pop_b": INFORMED_FRACTION,
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

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"generation_four_dual_population_{ts}.json"
    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nalife_lineage: {count_before:,} → {count_after:,}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
