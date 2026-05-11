# ALife Track B — Constella Constitutional Stress Testing

## Core Method

**Step 1: Establish the rational baseline.**
Run ALife with agents that behave optimally within their genome — no irrationality,
no spite, no trust breakdown. This is the structural skeleton: what the system looks
like when everyone does what they're supposed to do.

**Step 2: Measure predictable drift from the baseline.**
Introduce stressors — resource scarcity, parasitic agents, predator adaptation,
drain rate increases. Observe where the system diverges from the rational baseline
and at what threshold it collapses. This is the predictable failure envelope.

**Step 3: Laws live at the mean of the drift, not the ideal.**
Constella governance rules are calibrated not to the rational baseline but to the
*center of the observed drift distribution*. A law designed for optimal behavior
fails immediately against real humans. A law designed for the mean drift survives
most cases.

**Step 4: Penumbra Accord handles the tail.**
Any rule calibrated to the mean will fail at the edges. Edge cases are precisely
where human situations are most complex and context-dependent. The Penumbra Accord
is not a nice-to-have — it is **structurally required** by the mean-calibration
approach. Without it, the system becomes brittle at the boundary cases.

```
Rational Baseline ──────────────────────────────► ALife Track A
         │
         │  Drift envelope
         ▼
   Mean of drift ──► Where laws live (Constella governance rules)
         │
         │  Tail cases
         ▼
   Edge cases ──────► Penumbra Accord (contextual, restorative, nuanced)
```

---

## Success Criteria

A Track B experiment succeeds when it **changes a design decision** in Constella.
Confirmation that a working design continues to work is not a success — that's
just Track A science with extra steps.

Questions a Track B experiment must answer:
- Does this Constella mechanism hold under rational-agent stress?
- If it fails, at what threshold?
- What does that threshold tell us about where to set the governance parameter?
- Does the failure mode require a Penumbra-class response or a rule revision?

---

## What ALife Can and Cannot Validate

### CAN validate (structural skeleton):
- Collapse thresholds — at what drain rate does civic participation fail?
- Equilibrium existence — does a stable governance state exist at all?
- Floor necessity — does UCF prevent collapse or merely delay it?
- Concentration dynamics — does fixed-pool Auctor prevent voice monopolization?
- Reintegration feasibility — can formerly parasitic agents stabilize?

### CANNOT validate (social tissue):
- Trust breakdown (people leave because they feel disrespected, not because energy=0)
- Motivated reasoning (voting against UCF because "I'll never need it")
- Coalition capture (coordinating outside the system to control Auctor allocation)
- Legitimacy crises (systems that work but people stop believing in them)

**The social tissue validation is a separate research track requiring real humans —
likely small tabletop governance exercises with actual Constella draft documents.**

---

## Experiment Roadmap

### Exp 6 — UCF Floor (NEXT)
**Constella principle tested:** Universal Civic Floor
**Question:** Does a minimum energy floor prevent the Exp 5 collapse?
**Null hypothesis:** UCF floor merely delays collapse, does not prevent it.
**Design change from Exp 5:** Add `MIN_ENERGY_FLOOR` parameter. When agent energy
drops below floor, inject small energy top-up from commons pool.
**Success:** Stable population with parasites present AND floor preventing extinction.
**Failure mode to watch:** Floor enables free-riding — agents stop contributing and
just live on the floor. This would mean UCF needs a contribution requirement.

### Exp 7 — Penumbra Reintegration
**Constella principle tested:** Penumbra Accord
**Question:** Can formerly parasitic agents reintegrate into stable population?
**Design:** Phase the experiment — Phase A: parasites establish, Phase B: "repair"
mechanic available (parasitic agents can switch genome mid-sim if energy drops below
threshold), Phase C: measure reintegration success rate.
**Key metric:** What fraction of formerly parasitic lineages successfully reintegrate?

### Exp 8 — Auctor Fixed Pool
**Constella principle tested:** Auctor token fixed-pool constraint
**Question:** Does fixed total Auctor supply prevent voice concentration, or does
concentration just shift to whoever holds the pool?
**Design:** Fixed total energy with transfer mechanics. Some agents can accumulate
positional energy (Auctor analog). Measure Gini coefficient over time.
**Success:** Gini coefficient stays below concentration threshold with fixed pool.
**Failure:** Fixed pool concentrates anyway through positional advantage — means
Auctor needs additional redistribution mechanics beyond fixed supply.

### Exp 9 — Noise Injection (Human Randomness Proxy)
**Constella principle tested:** All of the above under irrational conditions
**Question:** Do the structural findings from Exp 6-8 hold when ~20% of agents
behave randomly (ignoring genome, acting against survival interest)?
**Purpose:** This is the closest ALife can get to modeling human irrationality.
**Note:** Results here are lower confidence — random agents are not a good model
of human motivation, but they do test structural robustness to noise.

---

## Relationship to Government API Data

The external data ingests (Census, USAspending, FEC, Federal Register) ground
Track B findings in real-world calibration:

| API Data | Track B Use |
|---|---|
| Census Oregon poverty rate (12.1%) | UCF floor calibration — what does "minimum civic participation" actually cost? |
| FEC campaign finance concentration | Auctor baseline — what does civic voice concentration look like without fixed-pool constraints? |
| USAspending budget functions | UCF funding model — how do real governments fund civic floors? |
| Federal Register rule amendments | Civic Tome amendment rate — how often do real governance documents change? |

---

*Track B experiments are numbered sequentially with the main ALife series.*
*All Track B experiments must state explicitly: what Constella design decision*
*would change if the hypothesis is confirmed vs. rejected.*
