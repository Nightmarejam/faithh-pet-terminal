#!/usr/bin/env python3
"""
ALife Bottom-Up Indexer
Reindexes all ALife experiment results using raw biological/dynamical vocabulary.
No Constella framing imposed. Tags describe what actually happened in the simulation.

The goal: FAITHH learns what emergent population dynamics look like from observation,
not from pre-labeled governance abstractions. Nomenclature emerges bottom-up.

Metadata schema uses biological/complexity science vocabulary:
  - dynamics_type: what kind of system behavior was observed
  - population_outcome: survived | collapsed | oscillating | overshoot
  - emergence_events: what novel behaviors appeared
  - pressure_type: what stressors were active
  - carrying_capacity_behavior: how the population related to system limits
  - collapse_mechanism: if collapsed, what drove it
  - stability_index: 0.0-1.0 rough measure of system stability
"""
import chromadb

CHROMADB_HOST = "192.158.1.10"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"

client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
collection = client.get_collection(COLLECTION_NAME)

EXPERIMENTS = [
    {
        "id": "alife_exp0_primordial_bottomup",
        "text": """ALife Experiment 0: Primordial Soup — Baseline Population Dynamics

Observed system: 200 agents, minimal genome, energy-based survival, no external stressors.
Run duration: 10,000 ticks.

What happened:
Population stabilized at natural carrying capacity of approximately 324 agents.
Average energy settled at ~210 units. Reproduction and death reached equilibrium.
No novel strategies emerged — genome fixed, no mutation pressure, no external threat.

Key dynamics observed:
- Logistic growth curve: rapid initial expansion, asymptotic approach to carrying capacity
- Carrying capacity emerged from energy source density, not from imposed parameter
- Population self-regulated — overshoot did not occur under zero external pressure
- Energy distribution: roughly normal around mean, no concentration or depletion zones

Biological vocabulary:
  carrying_capacity: ~324 agents (emergent, not set)
  growth_pattern: logistic
  equilibrium_type: stable fixed point
  perturbation_response: not tested (no stressors)
  energy_distribution: normal, balanced
  novel_strategy_emergence: none

System state at end: stable equilibrium, all agents using identical strategy.""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp0_primordial",
            "track": "A",
            "population_outcome": "stable_equilibrium",
            "dynamics_type": "logistic_growth",
            "carrying_capacity": 324,
            "pressure_type": "none",
            "emergence_events": "none",
            "collapse_mechanism": "none",
            "stability_index": 1.0,
            "date": "2026-03",
            "quality_score": 0.9
        }
    },
    {
        "id": "alife_exp1_pressure_bottomup",
        "text": """ALife Experiment 1: Pressure Selection — Adaptive Response to Predation

Observed system: Population under periodic predator wave pressure. Agents with shield
genome survive wave contact; unshielded agents take full damage.
Run duration: 20,000+ ticks.

What happened:
Consistent predator pressure selected for shield-active genomes. Unshielded lineages
were eliminated within a few thousand ticks. Shield-dominant population stabilized.
Red Queen dynamics: population adapts to pressure until pressure is the binding constraint.

Key dynamics observed:
- Directional selection: clear fitness gradient toward shield strategy
- Lineage extinction: non-shield lineages eliminated, not just suppressed
- New equilibrium: population smaller but more robust (shield overhead = energy cost)
- No novel strategies emerged — selection pressure was simple and consistent

Biological vocabulary:
  selection_type: directional (single fitness peak)
  adaptation_mechanism: genome-level selection, not individual learning
  equilibrium_type: new stable point post-selection
  genetic_diversity: collapsed to near-monoculture (shield dominant)
  red_queen_dynamics: true (arms race between shield and wave damage)
  population_bottleneck: yes, during transition to shield dominance
  novel_strategy_emergence: none beyond seeded strategies""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp1_pressure",
            "track": "A",
            "population_outcome": "survived",
            "dynamics_type": "directional_selection",
            "pressure_type": "predator_waves",
            "emergence_events": "shield_monoculture",
            "collapse_mechanism": "none",
            "genetic_diversity_outcome": "collapsed_to_monoculture",
            "red_queen": True,
            "stability_index": 0.75,
            "date": "2026-03",
            "quality_score": 0.85
        }
    },
    {
        "id": "alife_exp3_anticipation_bottomup",
        "text": """ALife Experiment 3: The Anticipation Gap — Predictive Behavior Emergence

Observed system: Agents with memory buffer and predict opcode, periodic wave threats.
Measurement: anticipation gap = time between Shield activation and wave arrival.
Negative gap = agent activated Shield BEFORE it could sense the wave.
Run duration: 50,000 ticks.

What happened:
89.2% of shield activations showed negative anticipation gap — agents fired Shield
before wave was detectable by sense range. 74 unique rhythmic patterns emerged across
the population. Agents converged on stable temporal rhythms synchronized to wave intervals.

Key dynamics observed:
- Genuine anticipatory behavior emerged from memory + threshold processing
- Population did not converge to single rhythm — 74 distinct stable patterns coexisted
- Pattern diversity correlated with spatial position (wave arrives at different times by location)
- Rhythmic convergence is a form of distributed temporal coordination without communication

Biological vocabulary:
  behavior_type: anticipatory (predictive, not reactive)
  anticipation_rate: 89.2% of shield events
  pattern_diversity: 74 unique rhythmic strategies
  coordination_type: distributed temporal synchronization (no signaling)
  memory_utilization: pattern buffer driving predict opcode
  spatial_differentiation: yes (position determines optimal rhythm)
  novel_strategy_emergence: anticipatory shielding (not seeded)
  stability_index: 0.892

Broader significance:
Demonstrates that simple memory + threshold processing produces genuine prediction.
Collective rhythmic diversity without communication is a form of distributed cognition.
74 stable patterns coexisting = high functional diversity despite identical genome structure.""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp3_anticipation",
            "track": "A",
            "population_outcome": "survived",
            "dynamics_type": "anticipatory_behavior_emergence",
            "pressure_type": "periodic_predator_waves",
            "emergence_events": "predictive_shielding,rhythmic_pattern_diversity",
            "anticipation_rate": 0.892,
            "pattern_count": 74,
            "coordination_type": "distributed_temporal",
            "collapse_mechanism": "none",
            "stability_index": 0.892,
            "date": "2026-03",
            "quality_score": 0.95
        }
    },
    {
        "id": "alife_exp4_harmonic_bottomup",
        "text": """ALife Experiment 4: Harmonic Interference — Spatial Cognitive Stratification

Observed system: Two wave sources with different frequencies creating interference zones.
Left zone: wave 1 only. Center: both waves (beat frequency). Right: wave 2 only.
Run duration: 50,000 ticks.

What happened:
Spatial cognitive stratification emerged. Agents in the center interference zone developed
distinct strategies from single-wave zones. Beat frequency tracking appeared in center zone
agents. Side zones selected for single-frequency rhythm. The cognitive demand of tracking
overlapping frequencies created a specialized sub-population in the interference zone.

Key dynamics observed:
- Spatial niche differentiation: three zones produced three distinct strategy distributions
- Cognitive specialization under complexity: interference zone agents more sophisticated
- Beat frequency tracking: agents learned composite rhythm from component frequencies
- Zone boundary effects: agents near boundaries showed mixed strategy profiles

Biological vocabulary:
  dynamics_type: spatial_niche_differentiation
  cognitive_stratification: true (zone-dependent strategy specialization)
  frequency_learning: beat_frequency_tracking in interference zone
  niche_count: 3 (left, center, right)
  spatial_boundary_effects: mixed strategies at zone edges
  complexity_response: specialization (not avoidance of complex zone)
  novel_strategy_emergence: beat_frequency_tracking
  stability_index: 0.78

Broader significance:
Environmental complexity drives cognitive specialization without top-down assignment.
Niches emerge from physical structure of the environment, not from agent design.
Demonstrates how heterogeneous environments produce functional diversity.""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp4_harmonic",
            "track": "A",
            "population_outcome": "survived",
            "dynamics_type": "spatial_niche_differentiation",
            "pressure_type": "overlapping_wave_frequencies",
            "emergence_events": "cognitive_stratification,beat_frequency_tracking",
            "niche_count": 3,
            "collapse_mechanism": "none",
            "stability_index": 0.78,
            "date": "2026-03",
            "quality_score": 0.9
        }
    },
    {
        "id": "alife_exp5_parasitic_drain15_bottomup",
        "text": """ALife Experiment 5: Parasitic Emergence under High Drain (drain=1.5)

Observed system: High energy drain rate (1.5/tick), adaptive predator, three-phase
experiment: Phase A (waves only), Phase B (threat redirection available), Phase C (toxin).
Run duration: 50,000 ticks (collapsed at tick 10,039).

What happened:
Parasitic strategy emerged at tick 57 — far earlier than drain=1.0 baseline.
Toxin strategy emerged at tick 1,840. Neither counter-strategy scaled to critical mass.
Predator adapted fully (shield effectiveness 0%) by tick ~8,000.
Population collapsed at tick 10,039. Final population: 0.

Key dynamics observed:
- Parasitic emergence under resource stress: drain rate drives predatory inter-agent behavior
- Strategy arms race: parasites → toxin counter → predator adaptation outpaces both
- Critical mass failure: counter-strategies emerged but couldn't scale before system collapse
- High drain as collapse accelerant: faster drain = less time for counter-strategies to establish
- Adaptive predator = positive feedback loop: as population shrinks, each death weakens defense

Biological vocabulary:
  dynamics_type: arms_race_collapse
  collapse_mechanism: adaptive_predator_plus_high_drain
  collapse_tick: 10039
  parasitic_emergence_tick: 57
  toxin_emergence_tick: 1840
  counter_strategy_failure: critical_mass_not_reached
  pressure_type: high_drain_plus_adaptive_predator
  drain_rate: 1.5
  population_outcome: collapsed
  stability_index: 0.0
  arms_race_outcome: predator_wins

Broader significance:
High resource drain removes the time buffer needed for adaptive counter-strategies to establish.
Parasitism is the first-order response to resource stress — appears before chemical defense.
Adaptive adversaries create positive feedback: population decline accelerates further decline.
There is a drain rate threshold above which no counter-strategy can establish in time.""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp5_parasitic",
            "track": "A",
            "population_outcome": "collapsed",
            "dynamics_type": "arms_race_collapse",
            "pressure_type": "high_drain_adaptive_predator",
            "emergence_events": "parasitism,toxin_production",
            "collapse_mechanism": "adaptive_predator_plus_resource_exhaustion",
            "collapse_tick": 10039,
            "drain_rate": 1.5,
            "parasitic_emergence_tick": 57,
            "toxin_emergence_tick": 1840,
            "stability_index": 0.0,
            "date": "2026-03-28",
            "quality_score": 0.95
        }
    },
    {
        "id": "alife_exp6_ucf_floor_bottomup",
        "text": """ALife Experiment 6: Unconditional Floor Support under High Drain (drain=1.5)

Observed system: Identical to Exp 5 (drain=1.5, adaptive predator) with one addition:
unconditional energy floor. Any agent below 40 energy receives +5 energy/tick from
a shared commons pool (500,000 initial, regenerates 150/tick).
Run duration: 50,000 ticks (collapsed at tick 7,410 — 2,629 ticks EARLIER than Exp 5).

What happened:
Floor support prevented immediate energy death but kept all struggling agents alive
long enough to reproduce. Population inflated to 848 by tick 3,000 (from ~340 baseline).
Floor rider peak: 833 of 848 agents (98%) simultaneously on the floor.
Commons pool never depleted (298,137 remaining at collapse).
Predator adapted to the inflated population size. When shield effectiveness hit 0%
at tick 5,000, the oversized population collapsed faster than without any floor.
Collapse tick 7,410 — 2,629 ticks earlier than no-floor baseline.

Key dynamics observed:
- Unconditional support causes population overshoot: floor removes natural culling
- Overshoot creates larger collapse: more agents = faster system-wide failure when pressure peaks
- Commons not the bottleneck: pool had 60% remaining at collapse — resource availability
  was not the limiting factor, carrying capacity was
- Free-riding at scale: 98% floor dependency is not marginal — it is the dominant system state
- Perverse outcome: intervention designed to prevent collapse accelerated it

Biological vocabulary:
  dynamics_type: commons_overshoot_collapse
  collapse_mechanism: population_overshoot_plus_adaptive_predator
  collapse_tick: 7410
  baseline_collapse_tick: 10039 (Exp 5, no floor)
  delta_vs_baseline: -2629 ticks (collapsed EARLIER)
  floor_type: unconditional
  overshoot_peak_population: 848
  floor_rider_peak: 833
  floor_rider_fraction: 0.98
  commons_depletion: false (60% remaining)
  population_outcome: collapsed
  stability_index: 0.0
  intervention_effect: negative (accelerated collapse)

Broader significance:
Unconditional resource floors remove selection pressure entirely when applied universally.
Without culling, populations overshoot carrying capacity.
Overshoot + external adaptive pressure = faster collapse than no intervention.
The commons pool is irrelevant if carrying capacity is the binding constraint.
Conditional access (participation gate) is the predicted fix — removes free-riding
while preserving support for genuinely stressed agents.""",
        "metadata": {
            "domain": "alife",
            "source_type": "alife_experiment",
            "experiment": "exp6_ucf_floor",
            "track": "B",
            "population_outcome": "collapsed",
            "dynamics_type": "commons_overshoot_collapse",
            "pressure_type": "high_drain_adaptive_predator_plus_unconditional_floor",
            "emergence_events": "universal_floor_dependency,population_overshoot",
            "collapse_mechanism": "overshoot_plus_adaptive_predator",
            "collapse_tick": 7410,
            "baseline_collapse_tick": 10039,
            "floor_type": "unconditional",
            "floor_rider_fraction": 0.98,
            "overshoot_peak": 848,
            "intervention_effect": "negative",
            "drain_rate": 1.5,
            "stability_index": 0.0,
            "date": "2026-03-29",
            "quality_score": 0.95
        }
    }
]

# Upsert all documents
ids = [d["id"] for d in EXPERIMENTS]
texts = [d["text"] for d in EXPERIMENTS]
metas = [d["metadata"] for d in EXPERIMENTS]

collection.upsert(ids=ids, documents=texts, metadatas=metas)
print(f"Indexed {len(EXPERIMENTS)} ALife experiments with bottom-up biological vocabulary")
print()
for exp in EXPERIMENTS:
    print(f"  {exp['id']}")
    print(f"    outcome: {exp['metadata']['population_outcome']}")
    print(f"    dynamics: {exp['metadata']['dynamics_type']}")
    print()
