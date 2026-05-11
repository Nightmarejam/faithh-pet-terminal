# ALife Experiment Findings — Living Document

<!-- 
  Status: Living document — updated after each experiment completes.
  Purpose: Synthesize what the ALife experiments actually discovered,
           distinguish earned findings from interpreted mappings,
           and track how findings evolve the Constella design.
  
  Rule: A finding is only added here when it was NOT predicted before the run.
        Confirmations of prior assumptions are noted but not treated as findings.
        Constella implications are labeled [EARNED] or [INTERPRETED] to be honest
        about epistemic status.
  
  Last updated: 2026-03-30 (after Exp 9 diversity floor)
-->

---

## What This Document Is

The ALife experiments produce emergent behavior from simple rules. This document
records what was actually discovered — including surprises and failures — and
maps those discoveries to Constella design where the connection is honest.

**Earned finding:** The experiment produced a result that was not predicted. The
mapping to Constella is grounded in the structural similarity of the dynamics.

**Interpreted mapping:** The connection to Constella was asserted before the
experiment ran. The result confirms a prior assumption. Useful, but weaker.

**Discarded experiments:** The Windsurf-era genomic experiments (exp8_cultural_transmission,
multi_generational_results, environmental_adaptation) produced zero transmission events
and zero survival probability across all organisms. The mechanics were not working.
The ideas were novel but the results were noise. They are archived, not built upon.

---

## Canonical Experiment Series (Exps 0–6)

These experiments ran on the core ALife simulation engine with genuine emergent
population dynamics. Results are real.

---

### Exp 0 — Primordial Soup (Baseline)
**Date:** 2026-03 | **Track:** A | **Outcome:** Stable equilibrium

**What happened:**
200 agents, no external pressure, minimal genome. Population stabilized at ~324
agents. Energy distribution settled to a normal distribution around mean ~210.
No novel strategies emerged.

**Findings:**
- Carrying capacity (~324) emerged from energy source density — it was not set
- Population self-regulated without any imposed limit
- Logistic growth curve: rapid expansion, asymptotic ceiling

**Constella implication:** [INTERPRETED]
Governance systems have a natural carrying capacity determined by resource density
(facilitation bandwidth, decision throughput), not by membership caps. Capping
membership is fighting the dynamics; managing resource density is working with them.

---

### Exp 1 — Pressure Selection
**Date:** 2026-03 | **Track:** A | **Outcome:** Survived, monoculture

**What happened:**
Consistent predator wave pressure eliminated unshielded lineages within a few
thousand ticks. Shield-dominant population stabilized at a lower count (energy
overhead of shielding is a real cost).

**Findings:**
- Directional selection converges to monoculture under simple, consistent pressure
- The new equilibrium is smaller and more robust but less diverse
- Red Queen dynamics: population adapts until the pressure itself is the ceiling

**Constella implication:** [INTERPRETED]
Uniform governance pressure (single compliance requirement applied uniformly)
produces compliant monoculture — everyone doing the same thing. Functional diversity
requires heterogeneous pressure, not uniform enforcement.

---

### Exp 3 — The Anticipation Gap
**Date:** 2026-03 | **Track:** A | **Outcome:** Survived, 89.2% anticipatory

**What happened:**
Agents with 8-byte genomes, pattern memory buffer, and a threshold opcode developed
genuine predictive behavior. 89.2% of shield activations occurred BEFORE the wave
was detectable by sense range. 74 distinct stable rhythmic patterns coexisted across
the population without any inter-agent communication.

**Findings (earned — not predicted):**
- Anticipatory behavior emerged from memory + threshold alone — no explicit
  prediction code required
- 74 stable patterns coexisted — the population did NOT converge to a single
  optimal rhythm. Diversity was stable, not transitional.
- Spatial position determined optimal rhythm — anticipation is location-dependent
- Distributed temporal coordination emerged without signaling

**Constella implication:** [EARNED]
Collective governance anticipation — responding to threats before they arrive —
does not require sophisticated deliberative institutions. It requires:
  1. Memory of past patterns (→ Civic Tome amendment history)
  2. Clear threshold triggers (→ defined decision activation criteria)
  3. Time for rhythms to stabilize (→ not disrupting established community patterns)

The 74-pattern coexistence result is particularly useful: diverse participation
rhythms are stable, not a problem to be solved toward uniformity.

---

### Exp 4 — Harmonic Interference
**Date:** 2026-03 | **Track:** A | **Outcome:** Survived, spatial differentiation

**What happened:**
Two wave sources with different frequencies created three spatial zones. Agents in
the center interference zone developed distinct strategies from single-wave zones.
Beat frequency tracking emerged in the center. Zone boundaries showed mixed strategies.

**Findings (earned — outcome 3 of 4 predicted, but the mechanism was not):**
- Cognitive specialization emerged from environmental structure, not from agent design
- Three distinct stable niches formed without any niche assignment
- The interference zone (highest complexity) produced the most sophisticated agents,
  not the fewest — complexity selected for capability, not avoidance

**Constella implication:** [EARNED]
Governance participation diversity — different communities using different modes —
should not be designed top-down. It emerges naturally from different local conditions.
Constella's role is to allow environmental heterogeneity, not specify participation
modes per community type. Designing for uniformity fights the dynamics.

The interference zone finding is counterintuitive: governance complexity zones
(multi-jurisdictional, multi-stakeholder) will produce more capable participants,
not less. Don't simplify complex zones — support them.

---

### Exp 5 — Parasitic Emergence (drain=1.5)
**Date:** 2026-03-28 | **Track:** A+B | **Outcome:** Collapsed tick 10,039

**Parameters:** drain=1.5, adaptive predator, 3 phases (waves, redirect, toxin)

**What happened:**
Parasitic strategy emerged at tick 57 (generation 2 — extremely fast). Toxin at
tick 1,840 (generation 20). Neither strategy reached critical mass. Predator
adaptation maxed (shield effectiveness 0%) by tick ~8,000. Collapse at tick 10,039.

**Population timeline highlights:**
- Tick 1000: pop=860, parasites=1, adapt=0.20
- Tick 3000: pop=909, parasites=15 (peak), toxin=4, adapt=0.60
- Tick 5000: pop=884, adapt=1.00 (shields 0%)
- Tick 10039: COLLAPSE

**Findings (earned):**
- **Parasitism is always first-order under resource stress.** Extraction behavior
  appears before any other novel strategy. At tick 57, generation 2, before the
  predator had adapted at all.
- **Toxin is second-order** — it appeared at tick 1,840 only after parasitism was
  established. Chemical defense emerges in response to established extraction.
- **The collapse threshold is not the drain rate — it's the ratio** between predator
  adaptation speed and counter-strategy establishment time. drain=1.5 didn't
  directly cause collapse; it removed the time buffer for counter-strategies to scale.
- **Adaptive adversaries create positive feedback:** declining population → weaker
  collective defense → faster decline. Not a linear degradation.

**Constella implication:** [EARNED]
In any resource-stressed governance system, the first emergent dysfunction will be
extraction behavior (free-riding, attention harvesting, voice monopolization) — not
outright destruction. Destruction comes later and only if extraction normalizes.

**Early warning signal = extraction metrics, not crisis metrics.**

The adaptation speed ratio finding: governance complexity must scale at most as fast
as participant capability development. When complexity outruns capability, collapse
follows regardless of participant intent.

---

### Exp 6 — UCF Floor (Unconditional, drain=1.5)
**Date:** 2026-03-29 | **Track:** B | **Outcome:** Collapsed tick 7,410 (WORSE than baseline)

**Parameters:** Identical to Exp 5 + UCF floor (threshold=40, injection=5/tick,
commons pool=500,000, regen=150/tick)

**Baseline:** Exp 5 without floor collapsed at tick 10,039.
**Result:** Collapsed at tick 7,410 — **2,629 ticks earlier** than without any floor.

**What happened:**
Floor kept all struggling agents alive long enough to reproduce. Population inflated
to 848 by tick 3,000 (from ~340 baseline). Floor rider peak: 833 of 848 agents (98%)
simultaneously on floor. Commons pool was NOT depleted (298,137 of 500,000 remaining).
When predator adaptation maxed at tick 5,000, the inflated population collapsed faster.

**Findings (earned — this result was not expected):**
- **Unconditional support removes selection pressure entirely when applied at scale.**
  98% floor dependency is not marginal — it becomes the dominant system state.
- **Overshoot, not depletion, caused the failure.** The commons pool had 60% left.
  Carrying capacity was the binding constraint, not resource availability.
- **The intervention accelerated the outcome it was designed to prevent.** This is
  a perverse intervention effect — a real and documented phenomenon in ecology and
  economics that appeared cleanly in the simulation.
- **Scale matters more than amount.** 98% floor utilization with modest injection
  caused more harm than no floor at all.

**Constella design decision (REQUIRED — not optional):**
UCF cannot be unconditional. Existence-based floors cause population overshoot and
accelerate systemic collapse by removing natural selection pressure from the entire
participant base simultaneously.

UCF eligibility must require minimum participation. Participants below the engagement
threshold enter a mediation/liminal state (→ Penumbra zone) before losing floor
access. This makes Penumbra Accord structurally load-bearing for UCF to function.
**They are not independent mechanisms — UCF without Penumbra causes overshoot.**

---

## Cross-Experiment Patterns (as of Exp 9)

These patterns appeared consistently across multiple experiments without being
designed for. They are the most reliable findings.

### Pattern 1: Collapse thresholds are ratios, not parameters
No single parameter value caused collapse. Collapse occurred when the ratio between
two competing rates crossed a threshold: adaptation speed vs. counter-strategy
establishment time (Exp 5), overshoot rate vs. carrying capacity (Exp 6).
Design implication: governance failure parameters are always relational, not absolute.

### Pattern 2: Novel strategies emerge in order — extraction before destruction
Parasitism appeared at tick 57. Toxin at tick 1,840. The sequence was consistent.
Low-cost extraction is always the first-order dysfunction. High-cost destruction is
second-order and only emerges once extraction is normalized.
Design implication: monitor extraction metrics as early warning, not crisis metrics.

### Pattern 3: Unconditional support at scale removes selection pressure
Exp 6 showed this definitively. 98% floor utilization means the floor is not a
safety net — it is the system floor for everyone. This is not a moral failing;
it is structural. Any sufficiently accessible resource will reach full utilization.
Design implication: accessibility thresholds must exist. The threshold IS the filter.

### Pattern 4: Anticipation emerges from memory + threshold, not intelligence
Eight bytes. One pattern buffer. One threshold opcode. 89.2% anticipatory behavior.
74 stable coexisting rhythms. No communication required.
Design implication: anticipatory governance capacity comes from recorded history
plus clear thresholds, not from elaborate predictive institutions.

### Pattern 5: Environmental heterogeneity produces functional diversity without design
Three spatial zones produced three distinct stable strategy distributions. No niche
was assigned. The physical structure of the environment drove specialization.
Design implication: allow heterogeneity, don't enforce uniformity. Diversity is
an outcome of different conditions, not a design target.

### Pattern 6: Strategy escape breaks arms-race lock-in (from Exp 7)
When a population abandons the mechanism an adversary has specialized against,
the adversary's specialization becomes useless. It de-adapts through disuse. The
abandoned mechanism later restores full effectiveness at no cost. The escape was
not designed — it emerged from selection pressure when the defender strategy became
untenable. Persistence in a losing strategy accelerates collapse; dissolution
preserves future viability.
Design implication: governance mechanisms that are fully adapted against may recover
effectiveness if temporarily dissolved rather than reinforced. The instinct to
double down on a failing defense is itself a collapse accelerant. Tactical retreat
is a legitimate systemic survival strategy, not a failure.

### Pattern 7: Early diversity is founding — late diversity is fragile (from Exp 8b)
Diversity seeded before adversarial specialization forms becomes structurally
load-bearing. Diversity introduced after specialization peaks fails to establish.
The founding window is not chronological — it is defined by the predator's
adaptation level. At adapt=0.00, seeded NAKED agents reproduced to 858 descendants
by tick 1000, establishing the NAKED strategy as default before any selection
pressure formed against it. Their personal survival didn't matter — their
reproductive output in the pre-adaptation window did. Late NAKED mutations
appearing at adapt=1.50 (ticks 40K-49K) died every time, unable to establish
against a fully specialized adversary.
A secondary finding: even successfully-founded diversity is fragile to long-run
drift. The oscillating equilibrium held for 28,000 ticks, then defender drift
slowly eliminated NAKED agents, returning the system to the arms-race attractor.
Without a floor mechanism to protect low-cost diversity strategies during drift
periods, founding is temporary.
Design implication: structural protections for diversity (floor mechanisms,
Penumbra Accord equivalents) must be designed before the governance crisis they
are meant to address, not in response to one. Introduced at maximum stress,
they arrive too late to establish. Introduced before pressure forms, they become
default. The second implication is that founding alone is insufficient — sustained
structural support is required to prevent drift back to monoculture.

### Pattern 8: Targeted diversity floors behave as threshold control loops, not rare rescues (from Exp 9)
Exp 8b ended with defender drift into the arms-race attractor. Exp 9 added a **NAKED
fraction floor** (activate below 15%, +3 energy/tick to NAKED only; deactivate when
fraction recovers). Over 50,000 ticks the run logged **64** distinct floor activations
— brief on/off cycles as the population grazed the threshold, not the 3–8 intermittent
events hypothesized pre-run. **max_adapt_reached = 0.55** — adaptation never reached
the Exp 8b terminal 1.50 regime; the mixed strategy state was sustained. Final
strategy mix: ~51% NAKED / 49% DEFENDER (plus trace TOXIN), versus Exp 8b Cond 3’s
late drift to all DEFENDER.

**Constella implication:** [EARNED]
A diversity guarantee tied to a hard participation fraction behaves operationally like
a **high-duty-cycle controller**: expect frequent, small corrections, not rare
catastrophe interventions. Threshold and bonus size determine duty cycle; mis-sizing
reads as “broken” or “always on” when it is actually doing threshold-chasing work.
Governance analogues need monitoring and cadence design, not only existence proofs.

---

## Discarded Experiments

**exp8_cultural_transmission (2026-03-26):**
16,499 protocols created. 0 transmissions. 0 archived. 3 generation turnovers.
Cultural transmission mechanic was not working. Ideas were novel (protocol evolution,
cultural archive, hybrid zones) but results were noise. Archived, not built upon.

**multi_generational_results (2026-03-27):**
50 organisms, 4 environments, 5 generations. avg_adaptation_success: 0.032.
avg_survival_probability: 0.029. successful_adaptations: 0. high_survival_organisms: 0.
Statistical significance of environmental effect: false.
Genomic biasing mechanics produced output but no actual adaptation. Noise.

**environmental_adaptation (2026-03-27):**
Similar to above — genomic biasing calculations ran but survival_probability was
effectively 0 across all conditions. The simulation framework was not producing
real selection dynamics.

**Decision:** These three experiments share a common failure mode — the mechanics
produced numerical output without functional dynamics. They are set aside until
the underlying genomic simulation engine is rebuilt on firmer ground.

---

---

### Exp 7 — UCF Gated Floor + Penumbra Zone (gate=500)
**Date:** 2026-03-29 | **Track:** B | **Outcome:** SURVIVED — full 50,000 tick run

**Parameters:** Identical to Exp 5/6 (drain=1.5, adaptive predator) + gated UCF:
gate window=500 ticks, grace period=300 ticks at 50% injection, commons=500,000.

**Pre-registered hypothesis:**
> 10-25% population in Penumbra at peak stress. Collapse delayed past Exp 6 (>7,410).
> Gaming behavior (min-compliance reproduction) may emerge.

**Hypothesis check:**
- Penumbra 10-25%: PARTIAL — gate too tight, full population excluded by tick 1000
- Collapse beyond Exp 6: CONFIRMED — no collapse at all
- Gaming detected: NOT OBSERVED — gate too tight to make gaming viable

**What happened:**
Gate=500 was too tight for reproduction frequency under drain=1.5. The entire
population was EXCLUDED from floor support from tick 1000 onward. UCF played
no material role. Commons pool was never drawn against — final pool: 7,958,473
(regen accumulated, initial was 500,000). 49,182 Penumbra-state interventions
occurred in the early phase (tick 0–1000, birth state) but not thereafter.

Survival was driven by an unexpected mechanism: **strategy escape.**

At tick ~7,500 the defender population collapsed (180 → 18 defenders in 1,000 ticks).
Instead of system collapse (Exp 5 outcome), NAKED strategy agents swept the population.
Population surged: tick 7,000: 243 → tick 10,000: 1,160. When shields disappeared,
the adaptive predator had nothing to adapt against. It de-adapted from max (1.5)
all the way to 0.00 by tick 20,000. With predator fully de-adapted, shields restored
to 100% effectiveness. New stable equilibrium held for the remaining 30,000 ticks.
Final population: 1,330. Final strategy: 94.4% NAKED, 5.6% DEFENDER.

**Comparison:**

| Experiment | Floor | Collapse tick |
|---|---|---|
| Exp 5 | None | 10,039 |
| Exp 6 | Unconditional | 7,410 |
| Exp 7 | Gated (500) | **SURVIVED 50K** |

**Findings (earned — not designed for):**

1. **Strategy escape from arms race.** When a population abandons the mechanism
   an adversary has specialized against, the adversary's specialization becomes
   useless. De-adaptation follows. The abandoned mechanism later becomes effective
   again. Persistence in a losing strategy accelerates collapse; tactical dissolution
   preserves future viability. This is a new pattern not observed in any prior experiment.

2. **Gate calibration is environmental.** Gate=500 was appropriate in theory but
   too tight for actual reproduction frequency under drain=1.5 pressure. A gate
   that excludes 100% of agents is functionally equivalent to no floor. Gate must
   be calibrated against observed participation frequency in the target environment,
   not against theoretical ideal frequency.

3. **Commons regen rate matters more than initial size.** With regen=150/tick and
   zero draw, pool grew to 7.9M. The floor infrastructure was sound — the gate
   prevented it from being used at all. This is a calibration failure, not a
   design failure.

**Constella implications (earned):**
- Strategy escape is a real survival mechanism: when a governance mechanism is
  fully adapted against, temporarily dissolving it allows adversarial pressure to
  de-adapt, then the mechanism can be restored with full effectiveness.
  The Penumbra Accord may serve this function at the systemic level — not just
  for individuals, but for strategies and institutions.
- UCF gate must be set against observed engagement frequency, not ideal engagement
  frequency. A gate too tight creates the same outcome as no gate: no floor support.

---

### Exp 8b — Strategy Escape Isolation: Seeded Diversity vs Stochastic Emergence
**Date:** 2026-03-29 | **Track:** A | **Outcome:** Cond 1 collapsed tick 8,743 / Cond 3 survived 50K

**Conditions:**
- Condition 1: 200 agents, 100% DEFENDER seed — Exp 5 replication (no floor)
- Condition 3: 200 agents, 50% DEFENDER / 50% NAKED seed — founding diversity test

**Pre-registered hypothesis:**
> Condition 3 will survive past tick 10,039. Survivors will trace predominantly
> to the seeded NAKED lineage, confirming intentional escape is viable.

**Hypothesis check:**
- Cond 3 survived past tick 10,039: CONFIRMED — survived full 50K (final pop 474)
- Lineage: SEEDED_FOUNDING_EFFECT confirmed via population data (see below)

**What happened:**

Condition 1 collapsed at tick 8,743 — close to Exp 5 baseline (10,039). Confirmed replication.

Condition 3 produced a three-phase result:

**Phase 1 (ticks 0–2000): Founding.** Seeded NAKED agents (100 of 200) personally died
by tick 2000. But before predator adaptation formed at all (adapt=0.00 throughout),
they reproduced 858 NAKED descendants by tick 1000. The seeded agents didn't need to
survive — they needed to reproduce before selection pressure formed.

**Phase 2 (ticks 2000–28000): Oscillating equilibrium.** NAKED/DEFENDER mix held
predator adaptation between 0.00–0.40 for 26,000 ticks. Neither strategy dominated
long enough for the predator to specialize. The founding effect was load-bearing.

**Phase 3 (ticks 28000–50000): Defender drift → arms-race re-entry.** Stochastic
drift slowly pushed NAKED toward zero. By tick 36,000, all agents were DEFENDERS
and adapt climbed to 1.50 — the same arms-race trap as Exp 5. Late NAKED mutations
at ticks 40K–49K failed to establish every time (adapt=1.50, hostile environment).
Population survived to tick 50K but in a degraded state identical to pre-collapse Exp 5.

**Key evidence for founding window:**

| Tick | NAKED | seeded_nak_alive | adapt |
|------|-------|-----------------|-------|
| 0 | 169 | 100 | 0.00 |
| 1000 | **858** | 1 | **0.00** |
| 2000 | 616 | 0 | 0.00 |
| 10000 | 454 | 0 | 0.20 |
| 28000 | 2 | 0 | 0.40 |
| 36000 | 0 | 0 | 1.50 |
| 48000 | 1 | 0 | 1.50 → died |

Original seeded agents gone by tick 2000. Late mutations at adapt=1.50 die on
arrival. The founding window is the pre-adaptation period — before adapt forms —
and it is the only window where new strategies can establish.

**Comparison across the series:**

| Experiment | Seed | Floor | Result |
|---|---|---|---|
| Exp 5 | 100% DEFENDER | None | Collapsed tick 10,039 |
| Exp 6 | 100% DEFENDER | Unconditional | Collapsed tick 7,410 |
| Exp 7 | 100% DEFENDER | Gated | Survived 50K (strategy escape) |
| Exp 8b Cond 1 | 100% DEFENDER | None | Collapsed tick 8,743 |
| **Exp 8b Cond 3** | **50/50** | **None** | **Survived 50K (founding effect)** |

**Findings (earned):**

1. **Founding population effect.** The original seeded agents didn't need to survive.
   They needed to reproduce before adversarial specialization formed. 858 descendants
   by tick 1000 established NAKED as default before the predator had anything to adapt
   against. Personal survival is irrelevant; founding-window reproduction is the mechanism.

2. **Founding window = pre-adaptation period.** At adapt=0.00, new strategies establish
   freely. At adapt=1.50, identical strategies die on arrival. The window is not
   chronological — it closes when the adversary specializes, not when time passes.

3. **Oscillating equilibrium is a distinct stable state — but fragile to drift.**
   Mixed NAKED/DEFENDER held adapt to 0.0–0.4 for 28,000 ticks. Then stochastic
   drift eliminated NAKED, the oscillation broke, and the system returned to the
   arms-race attractor. Founding is necessary but not sufficient — sustained structural
   support is required to prevent drift back to monoculture.

**Constella implications (earned):**
- The Penumbra Accord and UCF floor must be constitutionally established before
  a governance crisis forms, not in response to one. Introduced at maximum stress,
  they arrive too late. Introduced before pressure forms, they become default.
- Finding 3 raises the next design question: what mechanism sustains the
  oscillating equilibrium against defender drift? **Exp 9 (below) tested a targeted
  NAKED fraction floor; results support sustained mixed equilibrium through 50K ticks.**

### Exp 9 — Diversity Floor (NAKED fraction threshold)
**Date:** 2026-03-29 / 2026-03-30 | **Track:** A | **Outcome:** SURVIVED — full 50,000 tick run, no collapse

**Parameters:** Same stressor stack as Exp 8b Cond 3: 200 agents, 50% DEFENDER /
50% NAKED seed, drain=1.5, adaptive predator, parasitic redirect at tick 5,000,
toxin unlock at tick 15,000. **Addition:** if NAKED fraction drops below 15%, each NAKED agent
receives +3 energy/tick until fraction recovers above 15%. Implementation and
pre-registration: `projects/alife/experiments/exp9_diversity_floor.py`. Full metrics:
`genomic_results/exp9_diversity_floor_results.json`.

**Pre-registered hypothesis (from source, before run):**
> Oscillating equilibrium from Exp 8b maintained past tick 28,000. Floor activates
> intermittently (predicted 3–8 events). Adapt does not exceed 0.60 sustained.
> System survives 50,000 ticks. Gaming behavior (reproduction within 200 ticks of
> floor activation) may emerge as structural maintenance, not adversarial exploitation.

**Hypothesis check:**
- Past tick 28,000 with mixed strategies: **CONFIRMED** — e.g. tick 28,000: 699 NAKED /
  173 DEFENDER (873 pop); tick 50,000-equivalent timeline at 49,000: mixed pop 959;
  final_strategy ~50.9% NAKED / 49.1% DEFENDER.
- Floor 3–8 activations: **REJECTED** — **64** separate activations; threshold-chasing
  control-loop dynamics, not rare events.
- Adapt ≤ 0.60 sustained: **CONFIRMED** — `max_adapt_reached` **0.55** (vs. Exp 8b
  Cond 3 reaching 1.50 after drift).
- Survive 50K: **CONFIRMED** — `collapsed: false`, `collapse_tick: null`,
  `final_population: 1111`.
- Gaming: **PARTIAL** — `gamers` count in logs spiked mid-run (hundreds at some
  1k-sample rows) then fell; interpret as coupling between floor cadence and
  reproduction timing, not a clean adversarial gaming signature.

**What happened:**
Early dynamics matched Exp 8b-style founding and oscillation. The floor engaged
whenever NAKED share dipped under 15%, repeatedly through the run (first activation
tick 1,569 per `floor_events`). **Strategy escape** was recorded at tick **26,947**
(predator de-specialization pathway analogous to Exp 7). Late phase (e.g. ticks
45k–47k) shows very high NAKED share with **adapt at 0.00** and shields fully
effective again, then renewed DEFENDER rebound by tick 49k — the mix remained
dynamic but **did not collapse** and **did not lock into Exp 8b’s terminal
all-DEFENDER state**. Parasite/toxin first appearances: ticks 852 / 336 in results
file; predator_kills 114,912 over the run.

**Comparison:**

| Run | Floor | Collapse | max adapt (result file) | Final strategy (approx.) |
|-----|-------|----------|-------------------------|---------------------------|
| Exp 8b Cond 3 | None | No (survived) | 1.50 (drift attractor) | All DEFENDER late |
| **Exp 9** | NAKED fraction below 15% | **No** | **0.55** | **~51 / 49 NAKED/DEFENDER** |

**Findings (earned):**

1. **A narrow targeted floor can prevent the defender-drift attractor** without
   unconditional UCF (contrast Exp 6): same seed and stressors as Exp 8b Cond 3,
   but terminal state stays mixed instead of monoculture.
2. **Floor frequency was under-predicted by an order of magnitude** — threshold
   design implies many short activations; “a few rescues” is the wrong mental model.
3. **Strategy escape remains load-bearing** in this family of runs (tick 26,947);
   the floor modulates diversity retention; escape still resets adversarial pressure.
4. **Targeted ≠ unconditional:** only NAKED agents receive the bonus and only when
   under the fraction threshold — avoiding Exp 6-style universal floor dependency.

**Constella implications (earned):**
- Penumbra / participation floors aimed at **preserving minority strategy share**
  should be designed for **continuous boundary-hugging operation**, with metrics and
  governance load expectations set accordingly — not only for crisis moments.
- Combining **founding-time diversity** (Exp 8b) with **ongoing fraction protection**
  (Exp 9) is empirically closer to “durable pluralism” in this simulation than
  founding alone.

## Experiment Queue

### Exp 8 — UCF Gate Calibration (gate=2000–5000)
**Question:** What gate window is meaningful under drain=1.5 pressure? Find the
range where the gate excludes true free-riders but not genuinely stressed agents.
**Pre-registered hypothesis (to be written before running):** TBD

### Exp 8-alt — Strategy Escape Isolation
**Question:** Can strategy escape be deliberately triggered? If a population is
seeded with two strategies (shield + naked) at different ratios, does the escape
mechanism engage before the arms race peaks?

### Exp 8 — Auctor Fixed Pool
**Question:** Does fixed total Auctor supply prevent voice concentration, or does
concentration shift to whoever establishes positional advantage first?

### Queue — Noise injection (future)
**Question:** Do structural findings from Exps 6–9 hold when ~20% of agents
behave randomly (ignoring genome)?

---

## How to Use This Document

When a new experiment completes:
1. Add it to the canonical series section with date, outcome, and what happened
2. Extract any findings that were NOT predicted before the run
3. Label Constella implications as [EARNED] or [INTERPRETED]
4. Update the cross-experiment patterns section if a new pattern emerges
5. Add the next experiment to the queue with a pre-registered hypothesis

The pre-registration rule is the most important discipline: write down what you
expect to happen BEFORE running. If the result matches, it's weak confirmation.
If it contradicts, it's strong signal. Exp 6 was strong signal.

---

*Document owner: Jonathan Morales + FAITHH*
*Updated after each experiment. Never delete entries — mark as superseded if revised.*
