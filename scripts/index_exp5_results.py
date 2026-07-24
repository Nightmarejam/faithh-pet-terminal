#!/usr/bin/env python3
"""Index Experiment 5 drain=1.5 results into ChromaDB faithh_knowledge_base."""
import chromadb
import json

client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
collection = client.get_collection("faithh_knowledge_base")

documents = [
    {
        "id": "exp5_drain15_summary",
        "text": """Experiment 5 drain=1.5 — The Parasitic Emergence (COLLAPSE outcome)
Run date: 2026-03-29. Parameters: parasite_drain_rate=1.5, thermal_drain_rate=0.2,
parasite_redirect_tick=5000, toxin_unlock_tick=15000, wave_interval=500, adaptation_rate=0.20.
Outcome: COLLAPSE at tick 10039. Final population: 0.
First parasite lineage: tick 57, agent_812, generation 2. Adaptation at emergence: 0.0.
First toxin lineage: tick 1840, agent_7228, generation 20.
Wave count: 20. Predator kills: 28636. Parasitic kills: 23. Redirect events: 4. Thermal deaths: 296.
Total reproductions: 37585. Total deaths: 37785. Final adaptation: 1.50. Shield effectiveness: 0%.
Population peak: 1112 at tick 4000. Collapse triggered by full shield adaptation by tick 8000.
Parasites peaked at 15 agents (tick 3000) then collapsed. Toxin remained marginal throughout.
Neither counter-strategy reached critical mass before predator fully adapted.""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp5_parasitic_drain15",
            "outcome": "COLLAPSE",
            "collapse_tick": 10039,
            "parasite_drain_rate": 1.5,
            "quality_score": 1.0,
            "is_verified": True,
            "run_date": "2026-03-29"
        }
    },
    {
        "id": "exp5_drain15_constella_mapping",
        "text": """Experiment 5 drain=1.5 — Constella Astris Mapping Analysis
The drain=1.5 run collapses at tick 10039 vs stable oscillation at drain=1.0 (previous run).
This directly maps to Constella's Astris token decay design: if decay rate exceeds the system's
recovery capacity when combined with external pressure (predator = governance complexity), civic
participation collapses entirely rather than reaching a new equilibrium.
The 2% weekly Astris decay rate must be calibrated against governance participation demands to
stay below the collapse threshold. The ALife result shows: high drain alone (1.5) did not
directly cause collapse — parasites and toxin still emerged (tick 57 and 1840 respectively).
Collapse was caused by the combination of high drain + full predator adaptation (shields at 0%
effectiveness by tick 8000) + insufficient counter-strategy scaling before system-wide vulnerability.
Constella implication: Astris decay needs a UCF floor (Universal Civic Floor) to prevent
participants from dropping out entirely when governance pressure peaks. Without a floor,
the entire civic ecosystem collapses rather than finding a new lower equilibrium.""",
        "metadata": {
            "domain": "constella",
            "source_type": "alife_experiment",
            "experiment": "exp5_parasitic_drain15",
            "constella_principle": "Astris_decay",
            "quality_score": 1.0,
            "is_verified": True,
            "run_date": "2026-03-29"
        }
    },
    {
        "id": "exp5_drain15_timeline",
        "text": """Experiment 5 drain=1.5 — Population Timeline
Tick 0 [Phase A]: pop=345, defenders=345, adapt=0.0, shield=100%, energy=118
Tick 57: FIRST PARASITE LINEAGE — agent_812, generation 2, adaptation=0.0
Tick 1000 [A]: pop=860, defenders=859, parasites=1, adapt=0.20, shield=80%, energy=224
Tick 1840: FIRST TOXIN LINEAGE — agent_7228, generation 20, parasites present=4
Tick 2000 [A]: pop=914, defenders=906, parasites=4, toxin=1, adapt=0.40, shield=60%, energy=227
Tick 3000 [A]: pop=909, defenders=889, parasites=15 (PEAK), toxin=4, adapt=0.60, shield=40%, energy=224
Tick 4000 [A]: pop=1112 (PEAK), defenders=1111, parasites=0, toxin=1, adapt=0.80, shield=20%, energy=179
Tick 5000 [Phase B]: THREAT REDIRECTION ACTIVE. pop=884, adapt=1.00, shield=0%
Tick 6000 [B]: pop=799, parasites=1 (resurge), adapt=1.20, shield=0%, energy=161
Tick 7000 [B]: pop=800, toxin=1, adapt=1.40, shield=0%, energy=164
Tick 8000 [B]: pop=836, ADAPT MAX=1.50, shield=0%. Clean defenders only.
Tick 9000 [B]: pop=797, parasites=1 (final), adapt=1.50, energy=164
Tick 10000 [B]: pop=749, defenders=749, adapt=1.50, energy=161
Tick 10039: POPULATION COLLAPSED — predator kills overwhelm reproductions""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp5_parasitic_drain15",
            "quality_score": 1.0,
            "is_verified": True,
            "run_date": "2026-03-29"
        }
    }
]

print(f"Indexing {len(documents)} Exp5 drain=1.5 documents...")
for doc in documents:
    collection.upsert(
        ids=[doc["id"]],
        documents=[doc["text"]],
        metadatas=[doc["metadata"]]
    )
    print(f"  Indexed: {doc['id']}")

print(f"\nDone. Collection total: {collection.count()} documents")

# Quick verification
r = collection.query(
    query_texts=["experiment 5 parasitic collapse drain 1.5"],
    n_results=2,
    where={"domain": "alife"},
    include=["documents", "metadatas"]
)
print("\nVerification query:")
for meta, doc in zip(r["metadatas"][0], r["documents"][0]):
    print(f"  [{meta.get('experiment','?')}] {doc[:80]}...")
