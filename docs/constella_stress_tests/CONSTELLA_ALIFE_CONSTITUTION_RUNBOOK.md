# Constella–ALife Constitution Runbook
**Last Updated**: 2026-05-18
**Owner**: Jonathan Morales
**Status**: Draft — 2 of 5 core principles have experimental data

---

## What This Is

A mapping of Constella governance principles to ALife mechanical analogs. The goal is
to use ALife simulation results as empirical grounding for governance rules — not to
derive Constella from ALife, but to stress-test Constella's structural assumptions
against emergence data before the framework is used in real civic contexts.

The method is documented in `docs/constella_alife_constitution.md`. The short version:

```
Rational Baseline → Measure Drift Under Pressure → Laws Live at Mean of Drift → Penumbra Handles the Tail
```

ALife validates structural skeleton (collapse thresholds, equilibrium existence, floor
necessity, concentration dynamics). It cannot validate social tissue (trust breakdown,
coalition capture, legitimacy). Social tissue requires tabletop exercises with real humans.

---

## Constella Framework Summary

Constella is a civic governance framework built on the **Celestial Equilibrium** doctrine.
Core reference: `docs/reference/CONSTELLA.md` and `docs/constella_alife_constitution.md`.

Key principle: judge systems by how they treat those with the weakest resonance.

Components with ALife analogs:

| Component | ALife Analog | Experiment | Status |
|-----------|-------------|------------|--------|
| Astris Token (soul-bound merit, 2% weekly decay) | Agent energy with natural drain | Exp 5 (drain=1.0) | ✅ Partial data |
| Auctor Token (fixed-pool civic voice, 5% quarterly decay) | Fixed resource scarcity with competition | Exp 4 Wave dedup | ✅ Partial data |
| UCF (Universal Civic Floor) | Minimum energy floor with injection | Exp 6 (failed), Exp 7 (in progress) | ⚠️ Design change required |
| Penumbra Accord (restorative justice, mediation→repair→reintegration) | Agent recovery after low-energy/parasitic state | Not yet designed | ❌ No data yet |
| Civic Tome (living constitution, evolves through amendment) | Emergent rule evolution (parameter space itself) | Not yet designed | ❌ No data yet |

---

## Principle Mapping Details

### 1. Astris Token

**Constella**: Soul-bound merit token. Earned through civic contribution, cannot be
transferred. Decays at 2% weekly — prevents accumulation by inactive members.

**ALife analog**: Agent energy with natural drain (`THERMAL_DRAIN_RATE`).
The Exp 5 drain=1.0 run is the validated baseline. The planned drain=1.5 run (Astris
decay stress scenario) has not been run.

**What we know from data**:
- At drain=1.0: parasitic emergence occurs (tick 2812), population survives to tick 10,039
- At drain=1.5 + unconditional floor (Exp 6): collapse at tick 7,410

**Still needed**:
- drain=1.5 WITHOUT floor — what is the true no-floor baseline at higher decay?
- What decay rate causes civic participation collapse? (the Astris "death spiral" threshold)
- Does faster decay improve contributor diversity or reduce it?

**Constella design implication**: The 2% weekly decay rate is not yet validated.
Exp 7 results will constrain the viable decay range.

---

### 2. Auctor Token

**Constella**: Fixed-pool civic voice token. Fixed supply per governance domain, cannot
be created. Decays at 5% quarterly. Prevents any single voice monopolizing civic space.

**ALife analog**: Fixed-resource scarcity with competition — total energy budget in
the world is conserved, agents compete for share. The MIN_ARRIVAL_GAP fix in Exp 4
(preventing monopolistic wave arrival patterns) is structurally equivalent to Auctor's
fixed-pool constraint.

**What we know from data**:
- Exp 4 Wave 2 dedup fix prevents resource monopolization — validates the concept
- Exp 5 parasitic emergence models what Auctor is designed to prevent

**Still needed**:
- At what extraction rate does the fixed Auctor pool destabilize?
- ALife analog for cross-vault rebalancing (inter-population energy transfer)?
- Mapping of Auctor transfer mechanics to agent energy transfer dynamics

**Open question from SYSTEMS_MAP**: Cross-vault rebalancing guardrails — ALife analog
is inter-population energy transfer limits. Not yet designed.

---

### 3. UCF (Universal Civic Floor)

**Constella**: Baseline resource allocation guaranteed to all members regardless of
contribution history. Ensures minimum viable participation is always possible.
Funded by the commons pool.

**ALife analog**: `min_energy` parameter that triggers small energy top-up when crossed.

**What we know from data** (Exp 6 — design change required):
- Unconditional UCF floor collapsed the system at tick 7,410 — 2,629 ticks EARLIER
  than the no-floor baseline
- Root cause: floor kept all struggling agents alive long enough to reproduce
  → population inflated to 848 → predator scaled to inflated population
  → shield efficiency hit 0% → accelerated cascade collapse
- Floor rider peak: 833 of 848 agents (98%) simultaneously on the floor

**Constella design change required**: UCF CANNOT be unconditional. Existence-based
floors cause population overshoot and accelerate systemic collapse.

**Required design**: UCF eligibility must require a minimum participation threshold.
Participants who drop below engagement minimum enter the Penumbra zone before losing
floor access entirely. This makes the Penumbra Accord structurally load-bearing for UCF.

**Next experiment (Exp 7)**: UCF with participation gate. Agents must have reproduced
within 500 ticks to qualify. Tests whether gated floor prevents overshoot while still
providing collapse protection.

---

### 4. Penumbra Accord

**Constella**: Restorative justice framework — mediation → repair → reintegration.
When a member violates norms, the response is a structured path back, not exclusion.
The "penumbra" is the liminal state between full participation and exclusion.

**ALife analog**: Agent recovery and reintegration after low-energy/parasitic states.
A formerly parasitic agent, if its drain behavior is corrected, attempts reintegration
into the stable oscillating population.

**What we know from data**: Nothing yet. Exp 7 introduces Penumbra as a state
(agents in grace period after gate expires get 50% support). But it doesn't test
the reintegration phase — whether Penumbra agents can recover to ACTIVE status.

**Still needed (Exp 8 design)**:
- Agent drops below threshold → enters PENUMBRA (mediation state, 50% support)
- Receives energy assistance from stable neighbors (the "repair" phase)
- Attempts reintegration → measure success rate
- What reintegration success rate validates the Penumbra model?

**Constella design implication**: The Penumbra Accord is not optional — Exp 6 proved
that UCF requires it structurally. The mediation period (grace period with partial
support) is the mechanism that prevents both unconditional floor failure AND
hard exclusion failure.

---

### 5. Civic Tome

**Constella**: The living governance document. Unlike a fixed legal code, the Civic Tome
evolves through structured amendment processes. Records precedents, decisions, amendments,
and reasoning. Institutional memory.

**ALife analog**: Emergent rule evolution — rules that can be modified by the agent
population mid-simulation. The PROC_BEAT rhythm convergence in Exp 3 (population
collectively converges on stable rhythmic patterns) is the closest existing analog —
emergent constitutional order.

**What we know from data**: Nothing directly. The nearest analog (collective rhythm
emergence) is documented but not designed as a governance test.

**Still needed**: An ALife simulation where agents can vote on parameter changes.
This is the most complex mapping and requires significant new mechanics. Not blocking
for current work.

---

## Experiment Roadmap for Constitution Work

```
Exp 7 (UCF Gated)     — validates whether participation-gated floor works
     ↓
Exp 8 (Penumbra)      — validates reintegration mechanics
     ↓
Exp 9 (Astris stress) — drain=1.5 without floor, establishes decay threshold
     ↓
Exp 10 (Civic Tome)   — emergent rule amendment mechanics (complex, future)
```

Note: These experiment numbers are for the validated Track B (Constella stress-testing)
sequence. The archived experiments 6-9 in `experiments/archive/` are unrelated and
should be ignored.

---

## Data Acquisition Pipeline

What external data is still needed to ground the constitutional principles:

| Source | What For | Where It Lives | Status |
|--------|---------|----------------|--------|
| Oregon SOS API | Cooperative/LLC filings, amendment history (UCF and Civic Tome analog) | `/volume1/raw_ingest/gov_api/oregon_sos/` on NAS | Not yet connected |
| Census/ACS data | UCF baseline modeling, Oregon poverty thresholds (12.1% indexed) | `/volume1/raw_ingest/gov_api/census/` on NAS | Partially indexed |
| Academic papers (PDF) | Restorative justice outcomes, token decay economics, deliberative democracy | `/volume1/projects/constella/research/papers/` on NAS | Not yet organized |
| UBI residency/participation research | UCF design validation (conditional vs unconditional) | Same as above | Not yet |

**ChromaDB metadata gap**: Constella docs are indexed in ChromaDB but not filterable
by `domain=constella`. Need to retag with that metadata filter so RAG retrieval can
pull Constella-specific context. Until then, retrieval is by text search only.

---

## Constella Framework Reference

The full Constella framework is documented separately:
- `docs/reference/CONSTELLA.md` — living master reference
- `docs/constella_alife_constitution.md` — the full principle→analog mapping (source of truth)
- `archive/handoffs/OPUS_HANDOFF_CONSTELLA_2025-11-25.md` — original design session

**Confidence levels in the reference doc**:
- ✅ KNOWN: Celestial Equilibrium doctrine, Resonance Gap, Harmonic Alignment
- 🔶 PARTIAL: UCF mechanics, Astris/Auctor token details, Civic Tome structure
- ❓ UNKNOWN: Penumbra Accord details, Map of Intent, component interaction flow

The ❓ UNKNOWN sections should be populated from ChromaDB conversation history
using the discovery queries listed in `CONSTELLA.md`.

---

## Open Questions

1. **Facilitator load caps** — ALife analog: maximum agent interaction rate per tick. Not yet modeled.
2. **Tie-break protocol refinements** — ALife analog: agent voting weight when energy is equal. Exp 7 may surface this.
3. **Cross-vault rebalancing** — ALife analog: inter-population energy transfer. Band 2 cooperation experiments may be relevant.
4. **Astris decay rate validation** — The 2% weekly figure needs an ALife run to bound the viable range. Exp 9 (planned).
5. **Social tissue validation** — Trust breakdown, coalition capture, legitimacy crises cannot be validated by ALife. Needs tabletop governance exercises. Not yet scheduled.
