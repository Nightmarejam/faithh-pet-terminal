#!/usr/bin/env python3
"""
Generation zero — Band 1 pilot: 50 agents, 10 ticks, log to alife_lineage.
Does not modify any other project files.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from statistics import pstdev
from typing import Any

import chromadb

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = REPO_ROOT / "reports" / "alife"

CHROMA_HOST = "192.158.1.10"
CHROMA_PORT = 8000
COLLECTION = "alife_lineage"

N_AGENTS = 50
N_TICKS = 10
POPULATION = "A"
GENERATION = 0
EXPERIMENT = "generation_zero"


@dataclass
class Agent:
    id: str
    resources: float = 10.0
    survival_ticks: int = 0
    resource_history: list[float] = field(default_factory=list)
    resource_stability: float = 1.0
    band: int = 1
    lineage_id: str = ""
    fitness: float = 0.0

    def __post_init__(self) -> None:
        if not self.lineage_id:
            self.lineage_id = self.id

    def _update_stability(self) -> None:
        vals = self.resource_history[-5:]
        if len(vals) < 2:
            std = 0.0
        else:
            std = float(pstdev(vals))
        self.resource_stability = 1.0 / (1.0 + std)

    def step_tick(self) -> bool:
        """Apply one tick. Returns True if depleted (resources < 0) after update."""
        gain = random.uniform(0.5, 2.0)
        loss = random.uniform(0.3, 1.5)
        self.resources = self.resources + gain - loss
        depleted = self.resources < 0
        if not depleted:
            self.survival_ticks += 1

        self.resource_history.append(self.resources)
        if len(self.resource_history) > 5:
            self.resource_history = self.resource_history[-5:]
        self._update_stability()
        self.fitness = float(self.survival_ticks * self.resource_stability)
        return depleted


def main() -> None:
    random.seed()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)
    count_before = col.count()

    agents = [
        Agent(id=f"gen0_{POPULATION}_{i:03d}", lineage_id=f"lineage_gen0_{POPULATION}_{i:03d}")
        for i in range(N_AGENTS)
    ]

    docs_written = 0
    ids_batch: list[str] = []
    docs_batch: list[str] = []
    metas_batch: list[dict[str, Any]] = []

    def flush_batch() -> None:
        nonlocal docs_written, ids_batch, docs_batch, metas_batch
        if not ids_batch:
            return
        col.add(ids=ids_batch, documents=docs_batch, metadatas=metas_batch)
        docs_written += len(ids_batch)
        ids_batch, docs_batch, metas_batch = [], [], []

    for tick in range(N_TICKS):
        for agent in agents:
            agent.step_tick()
            doc_text = (
                f"Agent {agent.id} tick {tick}: resources={agent.resources:.2f} "
                f"fitness={agent.fitness:.3f} band={agent.band}"
            )
            meta = {
                "experiment": EXPERIMENT,
                "generation": GENERATION,
                "population": POPULATION,
                "agent_id": agent.id,
                "tick": tick,
                "resources": float(agent.resources),
                "fitness": float(agent.fitness),
                "band": agent.band,
                "survival_ticks": agent.survival_ticks,
                "resource_stability": float(agent.resource_stability),
                "timestamp": datetime.now().isoformat(),
            }
            doc_id = f"{EXPERIMENT}_g{GENERATION}_pop{POPULATION}_{agent.id}_t{tick}"
            ids_batch.append(doc_id)
            docs_batch.append(doc_text)
            metas_batch.append(meta)
            if len(ids_batch) >= 100:
                flush_batch()
        flush_batch()

    count_after = col.count()

    final_fitness = [a.fitness for a in agents]
    mean_f = sum(final_fitness) / len(final_fitness)
    max_f = max(final_fitness)
    min_f = min(final_fitness)
    sorted_f = sorted(final_fitness)
    idx = max(0, int(round(0.9 * (len(sorted_f) - 1))))
    top_10_threshold = sorted_f[idx]

    band2_candidates = [a.id for a in agents if a.survival_ticks >= 10]

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = REPORT_DIR / f"generation_zero_band1_{stamp}.json"
    summary = {
        "experiment": EXPERIMENT,
        "generation": GENERATION,
        "population": POPULATION,
        "agent_count": N_AGENTS,
        "ticks": N_TICKS,
        "timestamp": datetime.now().isoformat(),
        "fitness_summary": {
            "mean": mean_f,
            "max": max_f,
            "min": min_f,
            "top_10_percent_threshold": top_10_threshold,
        },
        "band_access_candidates": band2_candidates,
        "chroma_documents_written": docs_written,
        "alife_lineage_count_before": count_before,
        "alife_lineage_count_after": count_after,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"alife_lineage count before: {count_before}")
    print(f"alife_lineage count after:  {count_after}")
    print(f"Documents written (batch add): {docs_written}")
    print(f"Band 2 candidates (survival_ticks >= 10): {len(band2_candidates)}")
    print(f"Summary written: {summary_path}")


if __name__ == "__main__":
    main()
