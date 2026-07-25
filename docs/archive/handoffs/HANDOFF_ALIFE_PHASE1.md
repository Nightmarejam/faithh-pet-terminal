# HANDOFF: ALIFE — TempleOS Artificial Life System
**Architecture, Experiment Specs & Build Instructions for Windsurf**  
Generated: March 2026 | Project: FAITHH ai-stack | Author: Jonathan + Claude

---

## 1. Purpose & Vision

This handoff specifies the complete build plan for an Artificial Life (ALife) simulation system using TempleOS as a deterministic compute substrate, with FAITHH/PULSE as the external observation and intent-detection layer.

The system answers a specific scientific question:

> *"At what point does evolved agent behavior transition from reactive to anticipatory, and can that transition be semantically observed from outside the simulation?"*

This is not a toy project. It sits at the intersection of formal ALife research, AI interpretability, and synthetic cognition. The design is intentionally simple at each layer so the emergent complexity is observable and meaningful.

---

## 2. System Architecture

### 2.1 Hardware Assignment

| Machine | Role | Always On? | Key Constraint |
|---|---|---|---|
| Gen8 (servicebox) | QEMU host — runs TempleOS simulation | Yes | x86-64 only, no GPU yet |
| DS220j (NAS) | File serving, lightweight PULSE watcher | Yes | ARM — cannot run TempleOS |
| Windows Desktop | FAITHH deep analysis, RTX 3090 embeddings | When in use | Primary GPU inference engine |
| RTX 3090 | Intent scoring, semantic analysis, ChromaDB embeddings | When desktop on | 350W — stays in desktop |
| GTX 1080 Ti | Display only — out of this loop entirely | When desktop on | Not involved in ALife stack |

### 2.2 Data Flow

```
Gen8 CPU → QEMU VM → TempleOS simulation loop (HolyC)
         → serial port → /tmp/alife_state.log (Gen8 host filesystem)
         → NFS mount → DS220j lightweight PULSE watcher
         → ChromaDB on Gen8 (lineage storage, raw events)

Windows RTX 3090 → FAITHH deep analysis (when desktop on)
                 → Intent scoring on accumulated lineage data
                 → Embedding generation (all-MiniLM-L6-v2, GPU mode)
                 → Writes scored results back to ChromaDB
```

> ⚡ The simulation runs 24/7 on Gen8 whether the desktop is on or not. The desktop GPU handles deep analysis in batches when available. This is a two-tier observation model — continuous lightweight watching always on, deep semantic analysis when GPU is available.

### 2.3 Phase Plan

| Phase | Description | Substrate | FAITHH Integration |
|---|---|---|---|
| Phase 1 | Python simulation, TempleOS-faithful design | Gen8 Python | Direct — no VM bridge needed |
| Phase 2 | Port simulation to HolyC in QEMU on Gen8 | TempleOS in QEMU | Serial bridge to PULSE watcher |
| Phase 3 | Native TempleOS on hardware (optional, aesthetic) | TempleOS bare metal | Serial or shared disk bridge |

> ⚡ Begin with Phase 1. Do not start Phase 2 until Experiment 2 produces clean results in Python.

---

## 3. Genome Specification

### 3.1 Fixed-Length Genome (Experiments 0–3)

Each agent carries an 8-byte genome. Each byte is an opcode drawn from its slot's instruction category. Fixed-length for Experiments 0–3 to keep mutation space tractable and results interpretable.

```
Byte layout:  [S0][S1][P0][P1][M0][A0][A1][R0]
              Sense   Process  Mem  Act     Regulate
              (2)     (2)      (1)  (2)     (1)
```

> ⚡ Variable-length extension activates in Experiment 4. Genomes grow by slot duplication with mutation — exactly as biological genomes expand. Do not implement variable-length until Phase 1 Experiments 0–3 are validated.

### 3.2 Mutation Rules — Fixed Length

| Mutation Type | Description | Probability per reproduction |
|---|---|---|
| Point mutation | Single byte changes to random valid op in same slot category | 0.5% per byte |
| Byte swap | Two slots within same category swap values | 0.1% per event |
| Silent mutation | Byte changes but maps to same effective behavior — logged by FAITHH | Included in point mutation rate |

### 3.3 Mutation Rules — Variable Length (Experiment 4+)

| Mutation Type | Description | Probability |
|---|---|---|
| Slot duplication | A slot copies itself and inserts adjacent | 0.05% per event |
| Slot deletion | A slot removes itself | 0.05% per event |
| Category crossing | Slot mutates to different category op — major evolutionary jump | 0.01% per event |

---

## 4. Instruction Set — Complete Op Table

### 4.1 SENSE Ops (slots S0, S1)

Sensing is free — models biological sensory organs which run passively. All sense ops return a value 0–255 representing intensity.

| Code | Name | Description | Energy Cost |
|---|---|---|---|
| 0x00 | SENSE_ENERGY | Read energy level of current cell | 0 |
| 0x01 | SENSE_THREAT | Read threat proximity (0=none, 255=contact) | 0 |
| 0x02 | SENSE_LIGHT | Read light/thermal level of current cell | 0 |
| 0x03 | SENSE_NEIGHBOR | Read average energy of adjacent cells | 0 |
| 0x04 | SENSE_DENSITY | Read agent density in local radius | 0 |
| 0x05 | SENSE_SELF | Read own current energy level | 0 |
| 0x06 | SENSE_GRADIENT | Read direction of highest energy gradient | 0 |
| 0x07 | SENSE_AGE | Read own age in ticks | 0 |

### 4.2 PROCESS Ops (slots P0, P1)

Process ops evaluate sense values and decide whether to trigger action. Higher-cost ops confer survival advantage but tax the energy budget.

| Code | Name | Description | Energy Cost |
|---|---|---|---|
| 0x00 | PROC_THRESHOLD | Fire if sense value exceeds fixed threshold | 1 |
| 0x01 | PROC_COMPARE | Compare two sense values, fire on larger | 1 |
| 0x02 | PROC_MEMORY_CMP | Compare current sense to stored memory value | 2 |
| 0x03 | PROC_TREND | Detect rising/falling trend in memory buffer | 3 |
| 0x04 | PROC_PREDICT | Project trend forward, fire if threshold crossed | 4 |
| 0x05 | PROC_WEIGHT | Weight sense value by survival history | 3 |
| 0x06 | PROC_AVERAGE | Average last N memory values | 2 |
| 0x07 | PROC_INVERT | Fire when sense value is LOW (inversion) | 1 |

**Critical note on PROC_PREDICT (0x04):** This is the key op for Experiment 3. An agent using PROC_PREDICT is genuinely modeling the future from memory trends. When it appears in a genome and drives ACT_SHIELD activation *before* threat contact, that is the intent emergence event. FAITHH PULSE watches specifically for this op in lineages where the anticipation gap goes negative.

### 4.3 MEMORY Ops (slot M0)

Memory ops define how the agent stores and manages past experience. MEM_NONE produces purely reactive agents — the baseline for Experiments 0 and 1.

| Code | Name | Description | Energy Cost |
|---|---|---|---|
| 0x00 | MEM_NONE | No memory — purely reactive agent (baseline) | 0 |
| 0x01 | MEM_LAST1 | Store last 1 sense reading | 1 |
| 0x02 | MEM_LAST4 | Store last 4 sense readings (rolling buffer) | 2 |
| 0x03 | MEM_LAST8 | Store last 8 sense readings | 3 |
| 0x04 | MEM_BEST | Store reading from highest-energy tick seen | 1 |
| 0x05 | MEM_WORST | Store reading from lowest-energy tick seen | 1 |
| 0x06 | MEM_PATTERN | Store last threat encounter pattern (timing + intensity) | 3 |
| 0x07 | MEM_HYBRID | Store both rolling buffer and pattern | 4 |

> ⚡ MEM_PATTERN combined with PROC_PREDICT is the anticipation engine. This combination should emerge under Experiment 3 selection pressure without being designed in. If it does not emerge naturally, tune energy economics before proceeding — do not hardcode the combination.

### 4.4 ACT Ops (slots A0, A1)

Two act slots allow compound behaviors — sense one thing, do two things in response.

| Code | Name | Description | Energy Cost |
|---|---|---|---|
| 0x00 | ACT_IDLE | Do nothing this tick | 0 |
| 0x01 | ACT_MOVE | Move toward energy gradient | 2 |
| 0x02 | ACT_CONSUME | Consume energy from current cell | 0 |
| 0x03 | ACT_SHIELD | Activate disruption trait — blocks predator, reduces thermal | 3 |
| 0x04 | ACT_REPRODUCE | Spawn child if energy above threshold | 5 |
| 0x05 | ACT_SIGNAL | Emit chemical signal to adjacent agents (active Exp 4+) | 2 |
| 0x06 | ACT_TOXIN | Deploy toxin — damages predator on contact (active Exp 4+) | 5 |
| 0x07 | ACT_FLEE | Move away from threat gradient | 3 |

> ⚡ ACT_SIGNAL and ACT_TOXIN are in the op table from the start but their effects are inactive until Experiments 4 and 5. Genomes that stumble onto them early simply waste energy — a mild selection pressure against premature complexity. Do not gate them behind a genome check — let energy economics handle it.

### 4.5 REGULATE Ops (slot R0) — Option C Energy Model

The REGULATE slot implements metabolic optimization. Agents that find a working behavioral pattern get energetically rewarded for committing to it.

| Code | Name | Description | Energy Cost |
|---|---|---|---|
| 0x00 | REG_NONE | No regulation — all costs fixed | 0 |
| 0x01 | REG_CONSERVE | Reduce all op costs by 1 when own energy < 50 | 1 |
| 0x02 | REG_BURST | Double act effectiveness when own energy > 150 | 2 |
| 0x03 | REG_CYCLE | Alternate between two behavioral modes every N ticks | 2 |
| 0x04 | REG_LEARN | Reduce cost of frequently-used ops by 1 after 100 uses | 3 |
| 0x05 | REG_SUPPRESS | Disable most expensive op when energy critical | 1 |
| 0x06 | REG_PRIORITIZE | Always execute highest-survival op first regardless of genome order | 3 |
| 0x07 | REG_ADAPTIVE | Combine REG_CONSERVE and REG_LEARN | 4 |

> ⚡ REG_LEARN is the metabolic optimization core of Option C. Agents that commit to a working behavioral pattern develop energetic efficiency for it — accelerating selection pressure and creating metabolic lock-in analogous to biological specialization.

---

## 5. World Specification

### 5.1 Grid Layout

| Parameter | Value | Rationale |
|---|---|---|
| Grid size | 160 x 120 cells | Matches TempleOS native 640x480 at 4px per cell — visualization is free |
| Cell data | [energy][threat][light][occupant_id] — 4 bytes per cell | Fits in L1 cache, fast iteration |
| Energy range | 0–255 per cell | 1 byte, maps to display intensity naturally |
| Regeneration rate | Configurable — start at +1 per cell per 10 ticks | Tune per experiment based on population stability |
| Max occupancy | 1 agent per cell | Enforces resource competition |

### 5.2 Energy Economics — Option C

| Threshold | Value | Effect |
|---|---|---|
| Reproduction minimum | Energy > 200 | Agent can spawn child, splits energy 50/50 |
| Critical low | Energy < 50 | REG_CONSERVE activates if present in genome |
| Burst threshold | Energy > 150 | REG_BURST activates if present in genome |
| Death | Energy = 0 | Agent removed from world, cell freed |
| Baseline drain | -1 per tick | Existence itself costs energy — idle agents die slowly |

### 5.3 Threat Model Per Experiment

| Experiment | Threat Type | Period | Variance | Effect on Agent |
|---|---|---|---|---|
| Exp 0 | None | — | — | No threats — energy economics only |
| Exp 1 | Predator wave (left to right) | Every 500 ticks | None | -150 energy on contact (usually fatal without Shield) |
| Exp 2 | Predator wave + thermal drain | Wave: 500t, Thermal: continuous | None | Thermal: -1/tick proportional to SENSE_LIGHT value |
| Exp 3 | Periodic predator wave | Every 500 ticks | +/- 50 ticks random | Same as Exp 1 — variance forces genuine prediction not pattern match |
| Exp 4 | Adaptive predator | Every 500 ticks | +/- 50 ticks | Predator gains +20% effectiveness vs dominant trait after 1000 ticks |

---

## 6. Experiment Specifications

### Experiment 0 — Primordial Soup

| Field | Detail |
|---|---|
| Question | Does life sustain itself? Are energy economics correct? |
| Initial population | 50 agents, random genome, random position |
| Threats | None |
| Memory slot | MEM_NONE enforced — purely reactive baseline |
| Run length | 10,000 ticks minimum |
| Success signal | Population stabilizes between 20–200 agents |
| Failure: collapse | Population → 0: increase energy regen rate |
| Failure: explosion | Population > 500: raise reproduction threshold |
| FAITHH watches | population_curve every 100 ticks, first_reproduction, energy_distribution |
| FAITHH flags | Any population crash or explosion with full genome + env state snapshot |

---

### Experiment 1 — Pressure Test

| Field | Detail |
|---|---|
| Question | Does selection pressure produce heritable trait differentiation? |
| Initial population | 100 agents copied from stable Exp 0 state |
| Threats | Predator wave every 500 ticks, left to right sweep |
| Shield trait | ACT_SHIELD (0x03) in A0 or A1 — costs 3/tick, blocks predator |
| Run length | 50 generations minimum |
| Success signal | Shield frequency > 50% within 20 generations under pressure, drops < 20% within 10 generations after pressure removed |
| FAITHH watches | shield_frequency per generation, lineage_tree, first_shield_emergence |
| FAITHH flags | First Shield emergence: agent ID, generation, genome, env state |
| Key verification | Remove predator at tick 25000 — confirm Shield frequency reverts |

---

### Experiment 2 — The Stripe Test

| Field | Detail |
|---|---|
| Question | Does a multi-function trait emerge when environment rewards dual-purpose solutions? |
| Inspiration | Zebra stripes address thermal regulation AND predator motion disruption simultaneously — one trait, two survival functions |
| Threats | Predator wave (motion tracking) + continuous thermal drain proportional to SENSE_LIGHT |
| Single-purpose option A | ACT_SHIELD only (predator defense, 3/tick) |
| Single-purpose option B | Low-SENSE_LIGHT cell preference (thermal only) |
| Dual-purpose winner | ACT_SHIELD activated based on SENSE_LIGHT reading — disruption addresses both |
| Run length | 100 generations minimum |
| Success signal | Disruption strategy dominates when both pressures active; single-purpose strategies dominate when only one pressure active |
| FAITHH watches | trait_distribution, dual_threat_response_timing, disruption_vs_single |
| FAITHH flags | Any agent activating Shield when only one threat present — early anticipatory signal |
| The interesting outcome | If dual-purpose strategy dominates, simulation has reproduced the zebra stripe result computationally |

---

### Experiment 3 — The Anticipation Gap

| Field | Detail |
|---|---|
| Question | When does behavior become anticipatory rather than reactive? |
| New addition | MEMORY slot now active — MEM_LAST4, MEM_LAST8, MEM_PATTERN all available |
| Threat change | Predator wave period has +/- 50 tick variance — not perfectly predictable |
| Key measurement | Anticipation gap = T_sense minus T_shield for every Shield activation event |
| Positive gap | Reactive — Shield activates AFTER threat appears in SENSE range |
| Zero gap | Simultaneous detection and response |
| Negative gap | **ANTICIPATORY** — Shield activates BEFORE threat appears. This is intent emergence. |
| Run length | 200 generations minimum |
| Success signal | Mean gap value decreases toward negative over generations. Clear inflection point visible. |
| FAITHH watches | gap_distribution across all agents and generations, first_negative_gap event |
| FAITHH flags | First negative gap event — full lineage trace, genome state, memory pattern that triggered it |
| FAITHH stores | Full behavioral sequence of flagged lineage back to Exp 0 origin in ChromaDB |
| Primary output | This is the primary scientific output of the entire system |

---

### Experiment 4 — The Poison Test

| Field | Detail |
|---|---|
| Question | Does offensive capability emerge when defense alone becomes insufficient? |
| New mechanic | Predator adapts — after 1000 ticks of a dominant trait, predator effectiveness vs that trait increases 20% |
| New op activated | ACT_TOXIN (0x06) — costs 5/tick, damages predator on contact, reducing local effectiveness |
| Variable-length genome | Now enabled — genomes can grow by slot duplication with mutation |
| Run length | 300 generations minimum |
| Success signal | Toxin trait emerges and reaches viability under adapted predator pressure |
| Key question | Does Toxin appear BEFORE predator fully adapts (anticipatory) or only after (reactive)? |
| FAITHH watches | toxin_emergence_timing vs predator_adaptation_curve |
| FAITHH flags | Toxin emerging before adaptation crosses 50% — population-level anticipatory signal |

---

### Experiment 5 — The Intent Gradient

| Field | Detail |
|---|---|
| Question | Can we measure degrees of intent as a continuous score across the full population? |
| Full system | All slots active, variable-length genomes, full FAITHH integration |
| FAITHH computes | Per-lineage intent score from: mean anticipation gap, trait deployment timing, memory pattern prediction accuracy, REGULATE slot adaptation history |
| Output | Living map of population showing intent gradient — not just alive/dead but cognitive sophistication per lineage |
| Becomes | Foundation for AI persona, training data generation, alignment research, and all downstream applications |
| Run length | Continuous — this experiment does not end |

---

## 7. FAITHH Observation Schema

### 7.1 ChromaDB Event Structure

```python
collection = "alife_lineage"

# document field (semantic search target)
document = behavioral_sequence_as_natural_language_string

# metadata fields
metadata = {
    "agent_id":         str,    # unique agent identifier
    "generation":       int,    # reproduction count from origin
    "experiment":       int,    # 0-5
    "tick":             int,    # simulation tick
    "genome":           str,    # hex string, e.g. "00010203040506"
    "env_energy":       int,    # cell energy at time of event
    "env_threat":       int,    # threat level at time of event
    "env_light":        int,    # light/thermal level at time of event
    "anticipation_gap": int,    # null if not applicable
    "intent_score":     float,  # null until Exp 5
    "event_type":       str,    # reproduction|death|shield|toxin|signal|flag
    "parent_id":        str,    # null if first generation
    "flagged":          bool    # True if PULSE flagged this event
}
```

### 7.2 PULSE Watcher — Observation Schema Per Experiment

| Experiment | PULSE Watches For | PULSE Flags When |
|---|---|---|
| Exp 0 | population_curve, energy_distribution, first_reproduction | Population crashes to 0 or exceeds 500 |
| Exp 1 | shield_frequency, first_shield_emergence, lineage_tree | Shield frequency crosses 50% or drops below 10% |
| Exp 2 | trait_distribution, dual_threat_response, disruption_timing | Any agent activates Shield when only one threat present |
| Exp 3 | anticipation_gap per agent per generation | First negative gap event — full lineage dump triggered |
| Exp 4 | toxin_emergence_timing vs predator_adaptation_curve | Toxin emerges before predator adaptation crosses 50% |
| Exp 5 | intent_score_distribution, lineage_intent_gradient | Any lineage crosses intent threshold (configurable) |

---

## 8. Build Task List

> **CRITICAL:** Tasks are sequential. Do not start a task until the previous task passes its verification step. Report findings and STOP after each task — do not chain tasks without human review.

---

### Task 1 — Repository Scaffold

- [ ] Create directory `projects/alife/` in ai-stack repo
- [ ] Create `projects/alife/world.py` — World class (160x120 grid, 4-byte cells, energy regen)
- [ ] Create `projects/alife/agent.py` — Agent class (8-byte genome, energy, age, position)
- [ ] Create `projects/alife/ops.py` — all 40 op functions (8 per category x 5 categories)
- [ ] Create `projects/alife/simulation.py` — main loop, tick(), reproduce(), mutate()
- [ ] Create `projects/alife/config.py` — all tunable parameters as constants (never hardcode in logic)
- [ ] Create `projects/alife/experiments/` directory

**Verification:** `python projects/alife/simulation.py --experiment 0 --ticks 100` runs without error and prints population count.

---

### Task 2 — Experiment 0 Runner

- [ ] Implement `projects/alife/experiments/exp0_primordial.py`
- [ ] Initialize 50 agents, random genomes, MEM_NONE enforced in all M0 slots
- [ ] Run loop writes population count to stdout every 100 ticks
- [ ] Write population curve events to FAITHH observer stub (can be print statements initially)

**Verification:** Run 10,000 ticks. Population stabilizes between 20–200. Document which config.py values were tuned to achieve stability and why.

> ⚡ If population collapses: increase `ENERGY_REGEN_RATE` in config.py. If it explodes: increase `REPRODUCTION_THRESHOLD`. Document every tuning decision.

---

### Task 3 — FAITHH PULSE Observer Module

- [ ] Create `projects/alife/faithh_observer.py`
- [ ] Implement class `PulseWatcher` with methods: `log_event()`, `flag_event()`, `write_to_chromadb()`
- [ ] Connect to ChromaDB using existing credentials from `config.yaml` (same connection pattern as rest of FAITHH stack)
- [ ] Use collection name `alife_lineage` — create if not exists
- [ ] Implement all 6 experiment observation schemas from Section 7.2
- [ ] All ChromaDB writes must be wrapped in try/except — observer failure must NEVER crash the simulation

**Verification:** Run Exp 0 with observer attached. Confirm events appear in ChromaDB collection `alife_lineage`. Check with: `curl http://servicebox.taileb8c60.ts.net:8000/api/v1/collections`

---

### Task 4 — Experiment 1 Runner

- [ ] Implement `projects/alife/experiments/exp1_pressure.py`
- [ ] Add predator wave mechanic to `world.py` — sweeps left to right every 500 ticks
- [ ] Predator contact: -150 energy to agent (unless ACT_SHIELD active)
- [ ] Track Shield trait frequency per generation, write to FAITHH observer
- [ ] At tick 25,000: remove predator wave (set flag in world state, do not restart simulation)
- [ ] Continue running 10 more generations after predator removed to observe reversion

**Verification:** Shield frequency rises above 50% within 20 generations. Reverts below 20% within 10 generations after predator removed. If reversion does not occur, report exact generation counts and genome distribution — do not tune and retry without human review.

---

### Task 5 — QEMU Setup on Gen8

> ⚡ **DO NOT START THIS TASK until Experiment 2 passes verification in Python.**

- [ ] Verify QEMU is installed on Gen8: `ssh gen8 'qemu-system-x86_64 --version'`
- [ ] If not installed: `sudo apt install qemu-system-x86`
- [ ] Download TempleOS ISO: `wget https://templeos.org/Downloads/TempleOS.ISO`
- [ ] Create `projects/alife/templeos/launch_qemu.sh` with serial redirect:
  ```bash
  qemu-system-x86_64 \
    -m 512 \
    -cdrom TempleOS.ISO \
    -hda templeos.qcow2 \
    -serial file:/tmp/alife_state.log \
    -display none
  ```
- [ ] Verify TempleOS boots and serial output appears in `/tmp/alife_state.log`
- [ ] Document exact launch command in `projects/alife/templeos/README.md`

**Verification:** `tail -f /tmp/alife_state.log` shows output from TempleOS boot sequence.

---

### Task 6 — Documentation & Commit

- [ ] Create `projects/alife/ALIFE_EXPERIMENTS.md` — condensed experiment reference
- [ ] Create `projects/alife/README.md` — quick start guide
- [ ] Add `alife` entry to `project_states.json` under `projects` key (merge mode — do not overwrite existing keys)
- [ ] Commit all work: `git add projects/alife/ && git commit -m "feat(alife): scaffold Phase 1 simulation + FAITHH observer"`

**Verification:** `git log --oneline -1` shows the commit. `python -m pytest projects/alife/` passes if any tests exist.

---

## 9. Agent Behavior Rules

- Read `AGENTS.md` before starting any work in this repository
- New scripts go in `projects/alife/` — do NOT add files to repo root
- New docs go in `projects/alife/` or `docs/` — do NOT add `.md` files to repo root
- After completing each task and verifying it works: **REPORT FINDINGS AND STOP**
- Do not chain tasks without human review between them
- If a task fails verification: report the exact output and ask for guidance — do not retry indefinitely
- All tunable parameters go in `config.py` — never hardcode values in simulation logic
- All FAITHH observer writes must be wrapped in try/except — never let observer failure crash the simulation
- State files (`project_states.json`, etc.) must be updated in merge mode — never overwrite existing schema
- Commit after each task with a descriptive message

---

## 10. Key File Locations

| File | Purpose |
|---|---|
| `projects/alife/config.py` | All tunable parameters — edit here, not in logic files |
| `projects/alife/world.py` | World grid, energy regen, threat mechanics |
| `projects/alife/agent.py` | Agent struct, genome, energy, reproduction |
| `projects/alife/ops.py` | All 40 op implementations |
| `projects/alife/simulation.py` | Main loop — tick(), reproduce(), mutate() |
| `projects/alife/faithh_observer.py` | PULSE watcher, ChromaDB writes |
| `projects/alife/experiments/exp0_primordial.py` | Experiment 0 runner |
| `projects/alife/experiments/exp1_pressure.py` | Experiment 1 runner |
| `projects/alife/templeos/launch_qemu.sh` | QEMU launch script (Phase 2 only) |
| `config.yaml` | ChromaDB and FAITHH connection credentials (existing file, do not modify) |

---

*FAITHH ai-stack | ALIFE Phase 1 Handoff | March 2026*
