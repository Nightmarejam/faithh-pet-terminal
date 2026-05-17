#!/usr/bin/env python3
"""Index Exp 8b strategy escape isolation results into ChromaDB."""
import chromadb

client = chromadb.HttpClient(host="192.158.1.10", port=8000)
col = client.get_collection("faithh_knowledge_base")

doc = """ALife Experiment 8b: Strategy Escape Isolation — Founding Population Effect

Two conditions run sequentially (identical stressors: drain=1.5, adaptive predator, no floor):
  Condition 1: 100% DEFENDER seed (200 agents) — Exp 5 replication
  Condition 3: 50% DEFENDER / 50% NAKED seed (100 each) — founding diversity test

Pre-registered hypothesis: Condition 3 survives past tick 10,039. Survivors trace to seeded NAKED lineage.

Results:
  Condition 1: COLLAPSED tick 8,743 (confirms Exp 5 baseline ~10,039)
  Condition 3: SURVIVED full 50,000 ticks (final pop 474, 100% DEFENDER)

Condition 3 three-phase outcome:

Phase 1 (ticks 0-2000): Founding.
Seeded NAKED agents (100 of 200) personally died by tick 2000.
But before predator adaptation formed (adapt=0.00), they reproduced 858 NAKED
descendants by tick 1000. Strategy established as default before any specialization formed.

Phase 2 (ticks 2000-28000): Oscillating equilibrium.
NAKED/DEFENDER mix held predator adaptation between 0.00-0.40 for 26,000 ticks.
Neither strategy dominated long enough for the predator to specialize.
This is a distinct stable attractor not seen in any prior experiment.

Phase 3 (ticks 28000-50000): Defender drift -> arms-race re-entry.
Stochastic drift eliminated NAKED agents. By tick 36,000 all agents were DEFENDERS,
adapt climbed to 1.50. Late NAKED mutations at ticks 40K-49K died every time —
arriving into adapt=1.50 hostile environment, unable to establish.
Population survived to 50K but in degraded state identical to pre-collapse Exp 5.

Key evidence for founding window (condition 3):
  Tick 0:     NAKED=169, seeded_nak_alive=100, adapt=0.00
  Tick 1000:  NAKED=858, seeded_nak_alive=1,   adapt=0.00  (explosion before adapt)
  Tick 2000:  NAKED=616, seeded_nak_alive=0,   adapt=0.00  (founders gone, lineage established)
  Tick 10000: NAKED=454, seeded_nak_alive=0,   adapt=0.20  (past Exp5 collapse tick)
  Tick 28000: NAKED=2,   seeded_nak_alive=0,   adapt=0.40  (drift beginning)
  Tick 36000: NAKED=0,   seeded_nak_alive=0,   adapt=1.50  (arms-race re-entry)
  Tick 48000: NAKED=1,   seeded_nak_alive=0,   adapt=1.50  (late mutation, died)

Cross-experiment comparison:
  Exp 5 (100% DEFENDER, no floor):           collapsed tick 10,039
  Exp 6 (100% DEFENDER, unconditional floor): collapsed tick 7,410
  Exp 7 (100% DEFENDER, gated floor):         survived 50K via strategy escape tick 7500
  Exp 8b Cond 1 (100% DEFENDER, no floor):   collapsed tick 8,743
  Exp 8b Cond 3 (50/50, no floor):            survived 50K via founding effect

Pattern 7: Early diversity is founding, late diversity is fragile.
The founding window is the pre-adaptation period (adapt=0.00). Diversity seeded
before adversarial specialization forms becomes structurally load-bearing.
Diversity seeded after specialization peaks fails to establish every time.
Personal survival of founders is irrelevant — founding-window reproduction is the mechanism.

Secondary finding: founding alone is not sufficient. Oscillating equilibrium held
28,000 ticks then broke to defender drift without a sustained protective floor.
Next design question: can a targeted floor sustain the oscillating equilibrium against drift?

Constella implication (earned):
The Penumbra Accord and UCF floor must be constitutionally established before
a governance crisis, not in response to one. At maximum stress they arrive too late.
Before pressure forms they become default. Founding + sustained floor = permanent resilience."""

meta = {
    "domain": "alife",
    "source_type": "alife_experiment",
    "experiment": "exp8b_strategy_escape",
    "track": "A",
    "population_outcome": "condition1_collapsed_condition3_survived",
    "dynamics_type": "founding_population_effect_oscillating_equilibrium",
    "pressure_type": "high_drain_adaptive_predator_no_floor",
    "emergence_events": "founding_effect,oscillating_equilibrium,defender_drift,arms_race_reentry",
    "collapse_mechanism": "defender_drift_breaks_oscillation",
    "condition1_collapse_tick": 8743,
    "condition3_survived": True,
    "founding_window_tick": 1000,
    "oscillation_stable_ticks": 28000,
    "drift_break_tick": 28000,
    "late_mutation_fate": "failed_to_establish_at_adapt_1.5",
    "pattern": "pattern7_early_diversity_founding",
    "drain_rate": 1.5,
    "date": "2026-03-29",
    "quality_score": 0.99
}

col.upsert(ids=["alife_exp8b_strategy_escape_bottomup"], documents=[doc], metadatas=[meta])
print("Indexed Exp 8b to ChromaDB")

# Also index Pattern 7 as a standalone finding
doc_p7 = """ALife Pattern 7: Early Diversity Is Founding — Late Diversity Is Fragile

Source: Experiment 8b (2026-03-29), confirmed by comparison across Exp 5, 6, 7, 8b.

Core finding:
Diversity seeded before adversarial specialization forms becomes structurally load-bearing.
Diversity introduced after specialization peaks fails to establish.
The founding window is not chronological — it is defined by the predator's adaptation level.

Evidence from Exp 8b:
At adapt=0.00 (tick 0), seeded NAKED agents reproduced 858 descendants by tick 1000.
The predator never adapted because the NAKED-dominant strategy gave it nothing to target.
The oscillating NAKED/DEFENDER equilibrium held predator adaptation at 0.0-0.4 for 28,000 ticks.

At adapt=1.50 (ticks 40K-49K), identical NAKED mutations appeared 4 times and died every time.
Same gene. Same environment. Different adaptation level. Zero survival.
The founding window had closed.

Secondary finding — oscillating equilibrium is fragile to drift:
Even successfully-founded diversity eventually eroded through stochastic defender drift.
Without a sustained floor protecting low-cost strategies, founding is temporary.
Founding is necessary but not sufficient for permanent resilience.

Design principle (earned):
Structural protections (floor mechanisms, Penumbra Accord equivalents) must be
constitutionally established before the governance crisis they are meant to address.
Introduced at maximum stress, they arrive into a hostile environment and fail to establish.
Introduced before pressure forms, they become default and suppress the arms-race attractor.

Distinction from Pattern 6 (strategy escape):
Pattern 6 (Exp 7): What to do when already losing — dissolve the contested form,
  let adversary de-adapt, restore later.
Pattern 7 (Exp 8b): What to do before pressure starts — seed diversity early enough
  that it establishes as default before anything specializes against it.
These are different interventions at different points in the crisis timeline."""

meta_p7 = {
    "domain": "alife",
    "source_type": "alife_cross_experiment_pattern",
    "pattern_number": 7,
    "pattern_name": "early_diversity_founding_late_diversity_fragile",
    "source_experiments": "exp8b,exp7,exp5,exp6",
    "track": "A_and_B",
    "constella_relevance": "penumbra_accord_ucf_floor_founding_timing",
    "date": "2026-03-29",
    "quality_score": 0.99
}

col.upsert(ids=["alife_pattern7_founding_diversity"], documents=[doc_p7], metadatas=[meta_p7])
print("Indexed Pattern 7 to ChromaDB")
