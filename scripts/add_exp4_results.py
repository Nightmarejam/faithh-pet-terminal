#!/usr/bin/env python3
"""Index Experiment 4: Harmonic Interference results into ChromaDB.

Uses the proven add_*.py pattern — NO sentence_transformers import.
ChromaDB handles embeddings server-side.
"""
import chromadb
from datetime import datetime

client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")

timestamp = datetime.now().isoformat()

docs = [
    {
        "id": "alife_exp4_results_summary",
        "source": "docs/research/EXP4_HARMONIC_INTERFERENCE_RESULTS.md",
        "content": """
Experiment 4: Harmonic Interference — Results Summary

Scientific question: Does spatial cognitive stratification emerge when agents face
overlapping wave sources with different frequencies? Can agents evolve to track
beat frequencies in the interference zone?

World structure: Left zone (Wave 1 only, L→R, 600-tick), Center zone (both waves,
beat frequency 1800 ticks), Right zone (Wave 2 only, R→L, 900-tick).

Outcome: RED_QUEEN_CONTINUES (Outcome #4 of 4 valid outcomes).

Key finding: Beat-genome agents (PROC_BEAT + MEM_DUAL) dominated at tick 1000
(170 vs 90 predict agents) but PROC_PREDICT caught up by tick 2000. Neither
strategy achieves permanent dominance — continuous competitive adaptation.

Final population: 852 agents, 830 in center zone. 100% negative gap rate by tick 3000.
Intent emergence confirmed at tick 918 (gap=-27, gen=5, center zone).
        """
    },
    {
        "id": "alife_exp4_bugs_fixed",
        "source": "docs/research/EXP4_HARMONIC_INTERFERENCE_RESULTS.md",
        "content": """
Experiment 4: Critical Bug Fixes

Five bugs were fixed in Experiment 4, with bug #5 being the root cause of all
previous incorrect results:

Bug 5 (ROOT CAUSE): Duplicate wave arrival recording in world.py. The wave front
crosses an agent over 2-3 consecutive ticks (speed 0.8, check abs(x-front) < 1.0).
Each tick recorded a separate arrival, corrupting interval calculations. Example:
arrival_times = [2120, 2121, 2701, 2702] gave avg interval 194 instead of ~600.

Fix: Added MIN_ARRIVAL_GAP = 50 deduplication in world.py:apply_wave_damage().
This fix benefits ALL experiments (Exp 3 PROC_PREDICT data was also corrupted).

Other bugs: debug spam removal, pre-seed timing alignment, debug check timing.
        """
    },
    {
        "id": "alife_exp4_faithh_design",
        "source": "docs/research/EXP4_HARMONIC_INTERFERENCE_RESULTS.md",
        "content": """
Experiment 4: FAITHH-Designed Environmental Modifications

FAITHH participated in experimental design for the first time. She recommended
two environmental changes to give PROC_BEAT agents a selective advantage:

1. Center zone energy bonus: 10 extra energy sources placed in the interference
   zone (columns 160-319), making it ecologically richer. Metaphor: "like a
   fertile river delta" — worth the risk of dual-wave exposure.

2. Gradual side-zone pressure: After tick 2000, thermal drain in side zones
   ramps linearly to 3x by tick 10000. Creates natural incentive to occupy
   the center where PROC_BEAT's dual-wave prediction helps.

Result: Center zone held 830 agents (vs 25 in pre-design runs). The environmental
design successfully concentrated population in the interference zone.

FAITHH recommended accepting the Red Queen outcome as scientifically valid,
emphasizing adaptability over fixed dominance.
        """
    },
    {
        "id": "alife_exp4_red_queen_dynamics",
        "source": "docs/research/EXP4_HARMONIC_INTERFERENCE_RESULTS.md",
        "content": """
Red Queen Dynamics in Experiment 4

The Red Queen hypothesis describes competitive co-evolution where organisms must
constantly adapt just to maintain their fitness relative to competitors.

In Experiment 4, PROC_BEAT and PROC_PREDICT demonstrated Red Queen dynamics:
- PROC_BEAT dominated early (170 vs 90 at tick 1000) due to accurate per-source
  wave predictions from separate wave1/wave2 arrival time buffers.
- PROC_PREDICT caught up (827 vs 19 at tick 2000) as it accumulated clean
  timing data from both wave sources in its combined buffer.
- Neither strategy achieved permanent dominance.

Implications for FAITHH's architecture:
- No single prediction strategy dominates in multi-source environments
- Data integrity is foundational — corrupted data made all strategies fail
- Adaptability matters more than fixed algorithmic superiority
- Systems handling competing information sources should evolve dynamically

This result validates Outcome #4 from the experiment design: "Red Queen continues
— interference prevents fixation."
        """
    },
    {
        "id": "alife_experiment_progression",
        "source": "projects/alife/experiments/",
        "content": """
ALife Experiment Progression (Phase 1)

Completed experiments:
- Exp 0: Primordial Soup — baseline population dynamics, energy economics validation
- Exp 1: Pressure Test — selection pressure produces heritable Shield trait
- Exp 2: Stripe Test — dual-purpose traits outcompete single-purpose under dual pressure
- Exp 3: Anticipation Gap — agents develop genuine predictive behavior (negative gaps)
- Exp 4: Harmonic Interference — Red Queen dynamics between PROC_BEAT and PROC_PREDICT

Original Phase 1 roadmap (from HANDOFF_ALIFE_PHASE1.md):
- Original Exp 4 was "The Poison Test" (adaptive predator + ACT_TOXIN + variable-length genomes)
- Exp 4 was reimplemented as Harmonic Interference (dual-wave beat frequency detection)
- Original Exp 5: "The Intent Gradient" — continuous intent scoring across full population

Key ops not yet activated: ACT_SIGNAL (0x05), ACT_TOXIN (0x06), variable-length genomes.
These were designed for Experiments 4+ but Harmonic Interference did not require them.
        """
    }
]

for doc in docs:
    collection.upsert(
        ids=[doc["id"]],
        documents=[doc["content"].strip()],
        metadatas=[{
            "source": doc["source"],
            "indexed_at": timestamp,
            "category": "alife_results",
            "experiment": "exp4_harmonic_interference"
        }]
    )
    print(f"  Indexed: {doc['id']}")

print(f"\nDone. Indexed {len(docs)} documents into faithh_knowledge_base.")
