#!/usr/bin/env python3
"""
Generation two — Band 1, Option A: negative drift for real selection pressure.

Acquisition: 0.3–1.2 (mean 0.75). Loss: 0.5–1.5 (mean 1.0).
Net per tick (expectation): 0.75 − 1.0 = −0.25 drift.
Over 10 ticks, expected drawdown ~2.5 from starting 10.0 — variance ensures some agents
hit zero while others persist, producing spread in survival_ticks and fitness.
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

# Generation two — Option A (negative drift vs generation one)
NUM_AGENTS = 50
NUM_TICKS = 10
STARTING_RESOURCES = 10.0
ACQUISITION_MIN = 0.3
ACQUISITION_MAX = 1.2
LOSS_MIN = 0.5
LOSS_MAX = 1.5
BAND2_THRESHOLD = 10  # survival_ticks to qualify for Band 2

GENERATION = 2
POPULATION = "A"  # symmetric information

EXPERIMENT = "generation_two"


def resource_stability(history: list[float]) -> float:
    if len(history) < 2:
        return 1.0
    std = statistics.stdev(history[-5:]) if len(history) >= 5 else statistics.stdev(history)
    return 1.0 / (1.0 + std)


def run():
    random.seed()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)
    count_before = col.count()
    print(f"alife_lineage before: {count_before:,}")

    agents = []
    for i in range(NUM_AGENTS):
        agents.append(
            {
                "id": f"gen2_agent_{i:03d}",
                "lineage_id": f"lineage_{i:03d}",
                "resources": STARTING_RESOURCES,
                "survival_ticks": 0,
                "depleted_ticks": 0,
                "resource_history": [STARTING_RESOURCES],
                "band": 1,
                "fitness": 0.0,
            }
        )

    all_docs = []
    all_meta = []
    all_ids = []

    for tick in range(1, NUM_TICKS + 1):
        for agent in agents:
            acquire = random.uniform(ACQUISITION_MIN, ACQUISITION_MAX)
            lose = random.uniform(LOSS_MIN, LOSS_MAX)
            agent["resources"] = max(0.0, agent["resources"] + acquire - lose)
            agent["resource_history"].append(agent["resources"])

            if agent["resources"] > 0:
                agent["survival_ticks"] += 1
            else:
                agent["depleted_ticks"] += 1

            stab = resource_stability(agent["resource_history"])
            agent["fitness"] = agent["survival_ticks"] * stab

            doc_text = (
                f"Agent {agent['id']} tick {tick}: "
                f"resources={agent['resources']:.2f} "
                f"fitness={agent['fitness']:.3f} "
                f"band={agent['band']} "
                f"depleted_ticks={agent['depleted_ticks']}"
            )
            all_docs.append(doc_text)
            all_meta.append(
                {
                    "experiment": EXPERIMENT,
                    "generation": GENERATION,
                    "population": POPULATION,
                    "agent_id": agent["id"],
                    "lineage_id": agent["lineage_id"],
                    "tick": tick,
                    "resources": round(agent["resources"], 4),
                    "fitness": round(agent["fitness"], 4),
                    "band": agent["band"],
                    "survival_ticks": agent["survival_ticks"],
                    "depleted_ticks": agent["depleted_ticks"],
                    "resource_stability": round(resource_stability(agent["resource_history"]), 4),
                    "timestamp": datetime.now().isoformat(),
                }
            )
            all_ids.append(f"gen2_{agent['id']}_tick{tick:02d}")

        alive = sum(1 for a in agents if a["resources"] > 0)
        avg_fit = statistics.mean(a["fitness"] for a in agents)
        print(f"  Tick {tick:2d}: alive={alive}/50 avg_fitness={avg_fit:.3f}")

    batch_size = 100
    for i in range(0, len(all_docs), batch_size):
        col.add(
            documents=all_docs[i : i + batch_size],
            metadatas=all_meta[i : i + batch_size],
            ids=all_ids[i : i + batch_size],
        )

    count_after = col.count()

    fitnesses = [a["fitness"] for a in agents]
    depletions = [a["depleted_ticks"] for a in agents]
    band2_candidates = [a for a in agents if a["survival_ticks"] >= BAND2_THRESHOLD]
    fully_depleted = [a for a in agents if a["depleted_ticks"] > 0]

    sorted_agents = sorted(agents, key=lambda x: x["fitness"], reverse=True)
    top5 = sorted_agents[:5]
    bottom5 = sorted_agents[-5:]

    summary = {
        "experiment": EXPERIMENT,
        "generation": GENERATION,
        "population": POPULATION,
        "parameters": {
            "agents": NUM_AGENTS,
            "ticks": NUM_TICKS,
            "acquisition": f"{ACQUISITION_MIN}-{ACQUISITION_MAX}",
            "loss": f"{LOSS_MIN}-{LOSS_MAX}",
            "option": "A_negative_drift",
        },
        "timestamp": datetime.now().isoformat(),
        "fitness_summary": {
            "mean": round(statistics.mean(fitnesses), 3),
            "max": round(max(fitnesses), 3),
            "min": round(min(fitnesses), 3),
            "stdev": round(statistics.stdev(fitnesses), 3),
            "top_10pct_threshold": round(sorted(fitnesses, reverse=True)[4], 3),
        },
        "survival": {
            "agents_with_any_depletion": len(fully_depleted),
            "agents_fully_survived": len(band2_candidates),
            "total_depletion_events": sum(depletions),
            "avg_depleted_ticks": round(statistics.mean(depletions), 2),
        },
        "band2_candidates": len(band2_candidates),
        "top_5_agents": [
            {
                "id": a["id"],
                "fitness": round(a["fitness"], 3),
                "survival_ticks": a["survival_ticks"],
                "depleted_ticks": a["depleted_ticks"],
            }
            for a in top5
        ],
        "bottom_5_agents": [
            {
                "id": a["id"],
                "fitness": round(a["fitness"], 3),
                "survival_ticks": a["survival_ticks"],
                "depleted_ticks": a["depleted_ticks"],
            }
            for a in bottom5
        ],
        "chroma_documents_written": len(all_docs),
        "alife_lineage_count_before": count_before,
        "alife_lineage_count_after": count_after,
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"generation_two_band1_{ts}.json"
    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== GENERATION TWO RESULTS ===")
    print(f"Mean fitness:        {summary['fitness_summary']['mean']}")
    print(f"Max fitness:         {summary['fitness_summary']['max']}")
    print(f"Min fitness:         {summary['fitness_summary']['min']}")
    print(f"Fitness stdev:       {summary['fitness_summary']['stdev']}")
    print(f"Agents depleted:     {summary['survival']['agents_with_any_depletion']}/50")
    print(f"Band 2 candidates:   {summary['band2_candidates']}/50")
    print(f"Total depletion events: {summary['survival']['total_depletion_events']}")
    print(f"Docs written:        {len(all_docs)}")
    print(f"alife_lineage:       {count_before:,} → {count_after:,}")
    print(f"Report: {report_path}")

    return summary


if __name__ == "__main__":
    run()
