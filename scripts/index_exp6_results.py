#!/usr/bin/env python3
"""Index Experiment 6 UCF Floor results into ChromaDB."""
import json, chromadb

CHROMADB_HOST = "192.158.1.243"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"

results_path = "/home/jonat/ai-stack/genomic_results/exp6_ucf_floor_results.json"
with open(results_path) as f:
    data = json.load(f)

client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
collection = client.get_collection(COLLECTION_NAME)

documents = [
    {
        "id": "alife_exp6_ucf_floor_results",
        "text": """ALife Experiment 6: UCF Floor — Track B Constella Stress Test (2026-03-29)

HYPOTHESIS: UCF minimum energy floor prevents population collapse from Exp 5 (drain=1.5).
RESULT: FAILED — collapsed at tick 7410, which is 2629 ticks EARLIER than Exp 5 (no UCF).

Parameters: drain=1.5, UCF floor threshold=40 energy, injection=5/tick, commons pool=500,000.
Baseline (Exp 5 no UCF): collapsed tick 10039.

ROOT CAUSE — Population overshoot from unconditional floor support:
- UCF kept all struggling agents alive long enough to reproduce
- Population inflated to 848 at tick 3000 (above sustainable carrying capacity)
- Floor rider peak: 833 agents simultaneously on floor — 98% of entire population
- Predator adaptation scaled to the inflated population
- When shield efficiency hit 0% at tick 5000, the oversized population collapsed faster
- Collapse tick 7410 — 2629 ticks EARLIER than without UCF

CONSTELLA DESIGN DECISION:
Unconditional UCF floor causes population overshoot and accelerates collapse.
UCF MUST require minimum participation/engagement to receive support.
Cannot be purely existence-based — participants exploit unconditional floors predictably.

PENUMBRA CONNECTION:
The participation gate IS the Penumbra zone. Agents below the engagement threshold
enter mediation state before losing floor access entirely. This makes the Penumbra
Accord structurally load-bearing for UCF to function correctly.

Next experiment: Exp 7 — UCF with minimum participation gate.
Agents must have reproduced within N ticks to qualify for floor support.""",
        "metadata": {
            "domain": "constella",
            "source_type": "alife_experiment",
            "experiment": "exp6_ucf_floor",
            "constella_principle": "UCF",
            "track": "B",
            "result": "DESIGN_CHANGE_REQUIRED",
            "collapse_tick": 7410,
            "baseline_collapse_tick": 10039,
            "date": "2026-03-29",
            "quality_score": 0.95
        }
    }
]

collection.upsert(
    ids=[d["id"] for d in documents],
    documents=[d["text"] for d in documents],
    metadatas=[d["metadata"] for d in documents]
)
print(f"Indexed {len(documents)} Exp 6 result documents to ChromaDB")
