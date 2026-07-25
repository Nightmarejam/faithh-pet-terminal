# Constella–ALife Constitutional Mapping
<!-- 
  Created: 2026-03-29
  Purpose: Map Constella governance principles to ALife mechanical analogs.
  Source: SYSTEMS_MAP.md, ALife experiments 0-5 (verified results in ChromaDB),
          Constella Framework v1.5.x documentation.
  Status: DRAFT — Constella principle definitions from memory/SYSTEMS_MAP.
          Needs enrichment from ChromaDB Constella doc retrieval once metadata is fixed.
  Next: Re-query FAITHH with metadata filter domain=constella after retagging.
-->

---

## Method: Rational Baseline → Drift Envelope → Mean-Calibrated Law → Penumbra Tail

Constella governance rules are not calibrated to ideal behavior. They are calibrated
to the **mean of the predictable drift** from ideal behavior under structural pressure.

The method has four steps:

1. **Establish the rational baseline** — ALife agents behave optimally within their
   genome. No irrationality, no spite, no trust breakdown. This is the structural
   skeleton: what the system looks like when everyone does what they're supposed to.

2. **Measure predictable drift** — Introduce stressors (resource scarcity, parasitism,
   predator adaptation, drain rate increases). Observe where and at what threshold the
   system diverges from the rational baseline.

3. **Laws live at the mean of the drift** — A governance rule designed for optimal
   behavior fails immediately against real participants. A rule designed for the mean
   observed drift survives the majority of cases with minimal enforcement overhead.

4. **Penumbra Accord handles the tail** — Any rule calibrated to the mean will fail
   at the edges. Edge cases are precisely where human situations are most complex and
   context-dependent. The Penumbra Accord is **structurally required** by this method,
   not optional. Without it, mean-calibrated rules become brittle at the boundary.

```
Rational Baseline (ALife Track A) ──────────────────────► Pure emergence science
         │
         │  Apply structural stressors (Track B)
         ▼
   Drift envelope observed
         │
         │  Center of distribution
         ▼
   Mean of drift ──────────────────────────────────────► Where Constella laws live
         │
         │  Tail / edge cases
         ▼
   Penumbra Accord ────────────────────────────────────► Contextual, restorative, nuanced
```

**What ALife validates:** structural skeleton — collapse thresholds, equilibrium
existence, floor necessity, concentration dynamics, reintegration feasibility.

**What ALife cannot validate:** social tissue — trust breakdown, motivated reasoning,
coalition capture, legitimacy crises. Those require real humans in tabletop governance
exercises with actual Constella draft documents.

---

## Purpose

This document maps each core Constella Framework governance principle to:
1. Its precise definition within Constella
2. The ALife mechanical analog (parameter, behavior, or emergent phenomenon)
3. The stress-testing experiment from the ALife Track B series
4. The design decision that would change if the hypothesis fails
5. What data is still needed

---

## Core Principle Mappings

### 1. Astris Token
**Constella Definition:**
Soul-bound merit token. Earned through civic contribution, cannot be transferred. Decays at 2% weekly — designed to prevent accumulation by inactive members and keep civic power tied to ongoing participation.

**ALife Mechanical Analog:**
Agent energy with natural drain. In Experiment 3 (PROC_BEAT), agents maintain oscillating energy states with a natural decay rate. The "2% weekly" maps directly to the `drain` parameter. Experiment 5 tested `drain=1.0` (stable oscillation confirmed). The planned `drain=1.5` run tests whether faster decay still allows viable civic participation — the question of whether high-contribution agents can sustain themselves under heavier decay pressure.

**Validating Experiment:**
- Experiment 3: PROC_BEAT — base oscillation confirmed (74 unique rhythmic patterns, 89.2% stability)
- Experiment 5: Parasitic emergence at `drain=1.0` — shows what happens when energy extraction exceeds contribution rate
- **Pending**: Experiment 5 `drain=1.5` — tests Astris decay rate stress scenario

**Data Still Needed:**
- What decay rate causes civic participation collapse? (the Astris "death spiral" threshold)
- Does faster decay improve diversity of active contributors or reduce it?
- Longitudinal: does the system reach a new equilibrium or spiral?

**External Sources:**
- Token decay economics literature (time-preference decay models)
- Historical data on participatory budgeting participation rates over time
- Academic: "Decay functions in reputation systems" — searches in Google Scholar

---

### 2. Auctor Token
**Constella Definition:**
Fixed-pool civic voice token. Unlike Astris, Auctor represents positional civic authority — it exists in a fixed supply per governance domain and cannot be created, only transferred or rebalanced. Decays at 5% quarterly. Designed to ensure no single voice monopolizes civic space even if highly active.

**ALife Mechanical Analog:**
Fixed-resource scarcity with competition. This maps to the resource field in Experiments 3-5 where total energy in the system is conserved and agents compete for share. The "fixed pool" constraint is the total energy budget. The 5% quarterly decay maps to a slower background drain on positional resources — distinct from the faster Astris-equivalent individual drain.

The parasitic agents in Experiment 5 function as an Auctor stress test: what happens when some agents extract disproportionate civic voice? The `MIN_ARRIVAL_GAP` fix in Experiment 4 Wave 2 is relevant here — preventing monopolistic arrival patterns is structurally equivalent to Auctor's fixed-pool constraint.

**Validating Experiment:**
- Experiment 4 Wave 2: MIN_ARRIVAL_GAP fix — prevents resource monopolization
- Experiment 5: Parasitic emergence — models what Auctor is designed to prevent

**Data Still Needed:**
- At what pool-extraction rate does the fixed Auctor pool destabilize?
- Is there an ALife analog to cross-vault rebalancing (the open question in SYSTEMS_MAP)?
- Mapping of Auctor transfer mechanics to agent energy transfer

**External Sources:**
- Fixed-supply token economics (Bitcoin supply mechanics as contrast case)
- Participatory budgeting pool allocation studies
- Oregon municipal governance bylaws (Oregon SOS API)

---

### 3. Penumbra Accord
**Constella Definition:**
Restorative justice framework: mediation → repair → reintegration. When an agent (citizen/member) violates community norms, the response is not exclusion but a structured path back — accountability without permanent exile. The "penumbra" is the liminal state between full participation and exclusion.

**ALife Mechanical Analog:**
Agent recovery and reintegration after low-energy/parasitic states. In Experiment 5, parasitic agents extract energy from the system. The question the Penumbra Accord poses in ALife terms: can a formerly parasitic agent, if its drain behavior is corrected, reintegrate into the stable oscillating population? This has not been tested yet — it would require a parameter change mid-simulation (the "repair" phase).

The "mediation" phase maps to the period when an agent's energy drops below threshold but hasn't been excluded — it's in a degraded state but still participating.

**Validating Experiment:**
- **Not yet designed.** Experiment 6 (Lagrange point / standing wave) is the candidate.
- The Penumbra test would require: agent drops below threshold → enters mediation state → receives energy assistance from stable agents → attempts reintegration → measure success rate.

**Data Still Needed:**
- Design Experiment 6 to include a "repair" phase for low-energy agents
- What reintegration success rate validates the Penumbra model?
- Historical restorative justice outcome data (recidivism rates, community reintegration studies)

**External Sources:**
- Oregon restorative justice program outcome data (Oregon DOJ)
- Academic: "Reintegration in agent-based social simulations"
- UN restorative justice framework documentation

---

### 4. Universal Civic Floor (UCF)
**Constella Definition:**
Baseline resource allocation guaranteed to all members regardless of contribution history. The UCF ensures that minimum viable participation is always possible — no member can fall so low that civic engagement becomes impossible. Funded by the commons pool.

**ALife Mechanical Analog:**
Minimum energy floor per agent — the floor below which an agent cannot fall, maintained by a background energy injection. This is the direct inverse of the Astris decay: decay pulls down, UCF holds the floor. In ALife terms, it is a `min_energy` parameter that triggers a small energy top-up when crossed.

This has strong implications for Experiment 5: the parasitic emergence may not occur if agents have a UCF floor, because parasitic behavior becomes less necessary for survival. Testing UCF as a system stabilizer is a natural Experiment 6 design goal.

**Validating Experiment:**
- **Experiment 6 (UCF Floor) — COMPLETED 2026-03-29. Result: DESIGN CHANGE REQUIRED.**
- Ran identical conditions to Exp 5 (drain=1.5, collapsed tick 10039) with UCF floor added.
- **Collapsed at tick 7410 — 2629 ticks EARLIER than without UCF.**
- Root cause: unconditional floor kept all struggling agents alive long enough to reproduce.
  Population inflated to 848 (from ~340 baseline). Floor rider peak: 833 of 848 agents (98%)
  simultaneously on the floor. Predator adaptation scaled to the inflated population.
  When shield efficiency hit 0%, the oversized population collapsed faster than without UCF.

**Constella Design Decision (from Exp 6):**
UCF **cannot be unconditional**. Existence-based floors cause population overshoot and
accelerate systemic collapse by inflating participant counts beyond sustainable capacity.

**Required design change:** UCF eligibility must require a minimum participation threshold.
Participants who drop below engagement minimum enter the **Penumbra zone** (mediation state)
before losing floor access entirely. This makes the Penumbra Accord structurally load-bearing
for UCF to function — they are not independent mechanisms.

**Next experiment:** Exp 7 — UCF with minimum participation gate. Agents must have reproduced
within N ticks to qualify. Tests whether gated floor prevents overshoot while still
providing the collapse protection UCF was designed to deliver.

**Data Still Needed:**
- What participation gate interval prevents overshoot without excluding genuinely struggling agents?
- Does gated UCF + Astris decay reach a stable equilibrium?
- Real-world: what is a meaningful participation threshold? (minimum civic engagement definition)

**External Sources:**
- UBI research specifically on participation/residency requirements (not unconditional pilots)
- Census poverty threshold data (Oregon, federal) — now indexed, 12.1% Oregon poverty rate
- Academic: "Conditional vs unconditional transfers in commons governance"

---

### 5. Civic Tome
**Constella Definition:**
The living governance document — the written constitution of a Constella community. Unlike a fixed legal code, the Civic Tome is designed to evolve through structured amendment processes. It records precedents, decisions, amendments, and the reasoning behind them. It is the institutional memory of the community.

**ALife Mechanical Analog:**
Emergent rule evolution. In ALife terms, the Civic Tome maps to the parameter space itself — the ruleset governing agent behavior. The ALife series has been testing static rulesets. A Civic Tome analog would require rules that can be modified by the agent population mid-simulation — a form of collective parameter adjustment.

This is the most complex mapping and requires the most new experimental design. The nearest existing analog is the PROC_BEAT rhythm evolution in Experiment 3, where the population collectively converges on stable rhythmic patterns — a form of emergent constitutional order.

**Validating Experiment:**
- **Not yet designed.** Requires significant new mechanics.
- Experiment 3 PROC_BEAT provides the closest analog (emergent collective rhythm as proto-constitution).

**Data Still Needed:**
- Design an ALife simulation where agents can vote on parameter changes
- Historical: how do constitutional documents evolve in practice?
- Constella: the 88,000+ lines of design reasoning ARE the Civic Tome in draft form

**External Sources:**
- Constitutional amendment history datasets (US, state-level, municipal)
- Oregon SOS: articles of incorporation and amendment history for cooperatives
- Academic: "Evolutionary game theory and rule emergence"

---

## Data Acquisition Pipeline

### What to Collect → Where It Lives → How It Gets Indexed

```
Source                          NAS Location                    ChromaDB Collection
------                          ------------                    -------------------
Oregon SOS API                  /volume1/raw_ingest/gov_api/    faithh_knowledge_base
  (cooperative/LLC filings,     oregon_sos/                     metadata: domain=constella,
   amendment history)                                           source_type=government_api

Census / ACS data               /volume1/raw_ingest/gov_api/    faithh_knowledge_base
  (UCF baseline modeling,       census/                         metadata: domain=constella,
   Oregon poverty thresholds)                                   source_type=demographic

Academic papers (PDF)           /volume1/projects/constella/    faithh_knowledge_base
  (restorative justice,         research/papers/                metadata: domain=constella,
   token decay, deliberative                                    source_type=academic
   democracy)

ALife experiment results        /volume1/projects/alife/        faithh_knowledge_base
  (experiments 3-9)             results/                        metadata: domain=alife,
                                                                source_type=alife_experiment

Constella design docs           /volume1/projects/constella/    faithh_knowledge_base
  (the 88k+ lines already       design_docs/                    metadata: domain=constella,
   partially indexed)                                           source_type=design_doc
```

---

## Immediate Gaps (Priority Order)

1. **ChromaDB metadata fix** — Constella docs need `domain: constella` tags so RAG retrieval can filter by principle. Currently they're indexed but not filterable.

2. **Experiment 5 drain=1.5** — Validates Astris decay stress scenario. One run, 50K ticks.

3. **Experiment 6 design** — Needs to incorporate UCF floor parameter and Penumbra reintegration phase. The Lagrange point / standing wave model already planned is the right vehicle.

4. **NAS folder structure** — Create `raw_ingest/` and `projects/constella/` directories. The `homes/FAITHH/` directory that already exists on the NAS should become the staging area for FAITHH-processed data.

5. **Oregon SOS API connection** — First real external data ingest. Free, well-documented, directly relevant to Constella (cooperative governance filings).

---

## Open Questions (From SYSTEMS_MAP)

- Facilitator load caps → ALife analog: maximum agent interaction rate
- Tie-break protocol refinements → ALife analog: agent voting weight when energy is equal  
- Cross-vault rebalancing guardrails → ALife analog: inter-population energy transfer limits

---

*Document status: Draft v0.1 — constitutional principle definitions from SYSTEMS_MAP context.*
*Next revision: Re-query ChromaDB with domain=constella filter after metadata retagging.*
*Owner: Jonathan Morales + FAITHH*
