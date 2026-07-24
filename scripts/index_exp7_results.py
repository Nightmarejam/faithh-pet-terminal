#!/usr/bin/env python3
"""Index Exp 7 UCF gated results into ChromaDB."""
import chromadb

client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
col = client.get_collection("faithh_knowledge_base")

doc = """ALife Experiment 7: UCF Gated Floor (gate=500) — Strategy Escape

Observed system: Identical to Exp 5/6 (drain=1.5, adaptive predator) plus gated UCF floor.
Gate window: 500 ticks — agent must have reproduced within 500 ticks to qualify for support.
Grace period (Penumbra state): 300 ticks at 50% injection after gate expires.
Commons pool: 500,000 initial, regen 150/tick.
Run duration: 50,000 ticks — SURVIVED, no collapse.

What happened:
Gate=500 excluded 100% of population from floor support by tick 1000. Reproduction
frequency under drain=1.5 is too slow for a 500-tick gate window. UCF played no
material role in survival. Commons pool grew to 7,958,473 (unused regen).

Survival was driven by an unexpected mechanism: strategy escape.
Tick ~7500: defender population collapsed (180 -> 18 defenders in 1000 ticks).
Instead of system collapse (Exp 5 outcome), NAKED strategy swept the population.
Population surged: 243 (tick 7000) -> 1160 (tick 10000).
With no shields in population, adaptive predator had nothing to adapt against.
Predator de-adapted from max (1.5) to 0.00 by tick 20000.
Shields restored to 100% effectiveness. New stable equilibrium held for 30000 ticks.
Final population: 1330. Strategy: 94.4% NAKED, 5.6% DEFENDER.

Comparison:
  Exp 5 (no floor): collapsed tick 10039
  Exp 6 (unconditional floor): collapsed tick 7410
  Exp 7 (gated floor): SURVIVED 50000 ticks

Key dynamics:
- Strategy escape: abandoning contested mechanism causes adversary specialization to decay
- Predator de-adaptation: 1.5 -> 0.00 over 12000 ticks with no shield targets
- Population overshoot pulses at ticks 10000 (1160) and 32000 (1441) but self-correcting
- Gaming behavior: NOT OBSERVED (gate too tight to make minimum-compliance viable)
- Penumbra interventions: 49182 in early phase only (birth state), not ongoing

Biological vocabulary:
  dynamics_type: strategy_escape_arms_race
  population_outcome: survived
  survival_mechanism: strategy_escape_plus_predator_deadaptation
  floor_type: gated, gate_window: 500
  gate_effect: excluded_100pct_of_population
  predator_deadapt_tick: 20000, final_adapt: 0.0
  gaming_observed: false, stability_index: 1.0

Broader significance:
A population under arms-race pressure can escape by abandoning the contested strategy.
Adversary specialization then decays through disuse. Abandoned mechanism later restores
effectiveness. Persistence in a losing strategy accelerates collapse; dissolution
preserves future viability. Gate calibration must match actual participation frequency
in the target environment — a gate that excludes everyone is functionally no gate."""

meta = {
    "domain": "alife",
    "source_type": "alife_experiment",
    "experiment": "exp7_ucf_gated",
    "track": "B",
    "population_outcome": "survived",
    "dynamics_type": "strategy_escape_arms_race",
    "pressure_type": "high_drain_adaptive_predator_plus_gated_floor",
    "emergence_events": "strategy_escape,predator_deadaptation",
    "collapse_mechanism": "none",
    "collapse_tick": 0,
    "floor_type": "gated",
    "gate_window": 500,
    "gate_effect": "excluded_entire_population",
    "survival_mechanism": "strategy_escape",
    "predator_deadapt_complete_tick": 20000,
    "gaming_observed": False,
    "stability_index": 1.0,
    "drain_rate": 1.5,
    "date": "2026-03-29",
    "quality_score": 0.97
}

col.upsert(ids=["alife_exp7_ucf_gated_bottomup"], documents=[doc], metadatas=[meta])
print("Indexed Exp 7 to ChromaDB")
