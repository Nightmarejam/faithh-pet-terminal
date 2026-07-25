# ALife Project Roadmap — Full Vision

**Created**: 2026-03-25
**Status**: Phase 1 active, Experiments 0–4 complete
**Source**: Consolidated from Claude design sessions + FAITHH analysis

---

## 1. Project Purpose

Build an artificial life simulation that explores emergent intent — specifically:
**"When does evolved agent behavior transition from reactive to anticipatory?"**

The simulation generates structured behavioral data that FAITHH observes, characterizes, and eventually applies to her own self-model. The ALife system is both a research project and a training data generator for FAITHH's cognitive development.

---

## 2. Architecture

### Hardware Division of Labor

| Machine | Role | Specs |
|---------|------|-------|
| **Gen8 MicroServer** | Simulation engine (24/7) | Xeon E3-1265L v2, 15GB ECC, OS SSD only |
| **DS220j NAS** | File serving, lightweight PULSE watcher | ARM RTD1296, 512MB |
| **Windows Desktop** | FAITHH deep analysis (when on) | Ryzen 9 3900X, 64GB, RTX 3090 24GB, GTX 1080 Ti |

### Data Flow

```
Gen8 (always on)
  └── Python simulation (Phase 1) / QEMU+TempleOS (Phase 2)
        └── State files + ChromaDB writes

DS220j (always on)
  └── Lightweight PULSE watcher (reads Gen8 state via NFS)

Windows Desktop (when on)
  └── RTX 3090 → Heavy FAITHH analysis, embedding generation
        └── Intent scoring on accumulated lineage data
        └── Fine-tuning on emergence events
```

### Phase Plan

| Phase | Description | Substrate |
|-------|-------------|-----------|
| **Phase 1** | Python simulation, prove the science | Gen8 Linux |
| **Phase 2** | Port core loop to HolyC in QEMU, serial bridge to FAITHH | Gen8 QEMU + TempleOS |
| **Phase 3** | Native TempleOS on dedicated hardware (sacred sandbox) | Physical machine |

### TempleOS Value Function and Readiness Gate

TempleOS is not a goal by itself. It is a **validation substrate**.

Highest-value function:
- **Deterministic minimalism test**: verify that key ALife findings still emerge in a tightly constrained HolyC environment.
- **Reproducibility hardening**: run fixed-seed, low-abstraction replays to reduce hidden framework effects from Python tooling.
- **Isolation sandbox**: evaluate evolved strategies in a deliberately austere compute context before claiming generality.

Lower-value function (non-blocking):
- Aesthetic/symbolic alignment with the project's minimalism ethos.

Readiness gate for Phase 2 (TempleOS/QEMU):
1. **Science signal lock (Python)**: at least 3 consecutive experiment runs show stable, interpretable selection metrics (not one-off RNG artifacts).
2. **Causal contrast lock**: symmetric vs asymmetric information experiments use paired shocks and behavior-dependent perception, with effect direction reproducible across seeds.
3. **Observer lock**: `alife_lineage` schema + report pipeline stable across reruns (no ID collisions, no data loss).
4. **Portability slice defined**: one minimal HolyC target loop specified (tick/update only), with explicit "what is deferred" list.

Go/No-Go rule:
- **Go Phase 2** when all four gates are true.
- **Stay Phase 1** when any gate remains open.

Current assessment (2026-04-01):
- Causal infrastructure is now present (generation five), but effect direction is not yet locked across seeds.
- Recommendation: continue Phase 1 replication/tuning before TempleOS porting.

---

## 3. Genome Architecture

### Fixed-Length (Exp 0–4)

```
[S0][S1][P0][P1][M0][A0][A1][R0]
 8 slots × 1 byte each = 8 bytes total
```

**Process-Action Coupling** (implemented in Exp 3):
- P0 fires → drives A0
- P1 fires → drives A1
- Creates two independent sense-process-act channels

### Variable-Length (Exp 5+)

Slot duplication (0.05%), deletion (0.05%), category crossing (0.01%).
Genomes can grow — mimics how biological genomes expand.

### Op Table Summary (40 ops, 8 per category)

| Category | Key Ops | Cost Model |
|----------|---------|------------|
| **SENSE** (S0,S1) | ENERGY, THREAT, LIGHT, NEIGHBOR, DENSITY, SELF, GRADIENT, AGE | Free (passive) |
| **PROCESS** (P0,P1) | THRESHOLD, COMPARE, MEMORY_CMP, TREND, PREDICT, WEIGHT, AVG, INVERT | 0–4 energy |
| **MEMORY** (M0) | NONE, LAST1, LAST4, LAST8, BEST, WORST, PATTERN, HYBRID | 0–4 energy |
| **ACT** (A0,A1) | IDLE, MOVE, CONSUME, SHIELD, REPRODUCE, SIGNAL, TOXIN, FLEE | 0–5 energy |
| **REGULATE** (R0) | NONE, CONSERVE, BURST, CYCLE, LEARN, SUPPRESS, PRIORITIZE, ADAPTIVE | 0–4 energy |

---

## 4. Experiment Ladder — Completed Results

### Exp 0: Primordial Soup ✅
- **Question**: Does life sustain itself?
- **Result**: Population stabilizes at ~324 agents. Energy economics validated.
- **Commit**: `ca047df`

### Exp 1: Pressure Test ✅
- **Question**: Does selection pressure produce trait differentiation?
- **Result**: Shield trait rose from 10% to 100% in 5 generations under predator wave pressure. Genetic fixation after bottleneck.
- **Commit**: `dc89a49`

### Exp 2: Stripe Test ✅
- **Question**: Does a dual-purpose trait emerge under dual pressure?
- **Result**: Strategy C (Disruption) reached 100%. Spontaneous Strategy A reversion at gen 721 was selected against — environment actively maintains dual-purpose trait.
- **Key finding**: "The environment defended its own complexity."
- **Commit**: `f6b28fe`

### Exp 3: Anticipation Gap ✅
- **Question**: When does behavior become anticipatory rather than reactive?
- **Result**: Intent emergence confirmed. Negative anticipation gaps observed. Process-action coupling (P0→A0, P1→A1) was the architectural key — created a prediction-to-shield pipeline.
- **Key measurement**: `gap = T_sense - T_shield`. Negative = anticipatory.
- **Wave model**: Finite speed propagation at C=0.8 col/tick with 10% variance.

### Exp 4: Harmonic Interference ✅
- **Question**: Does spatial cognitive stratification emerge with dual wave sources?
- **Result**: RED_QUEEN_CONTINUES. PROC_BEAT dominated early (170 vs 90 at tick 1K), PROC_PREDICT caught up by tick 2K. Neither achieves permanent dominance.
- **FAITHH participated in design**: Center zone energy bonus + gradual side-zone pressure.
- **Critical bug fix**: Wave arrival deduplication (benefits ALL experiments).
- **Documented**: `docs/research/EXP4_HARMONIC_INTERFERENCE_RESULTS.md`

---

## 5. Experiment 5: The Parasitic Emergence (REDESIGNED)

### Original Design (Failed)
The original "Poison Test" jumped straight to ACT_TOXIN — chemical warfare against an adaptive predator. **Diagnostic showed this doesn't work**: toxin is too metabolically expensive (5 energy/tick) with no intermediate benefit. The population survived through reproductive throughput even with Shield at 0% effectiveness. Toxin never established a viable lineage.

### Biological Insight (User + FAITHH)
Real offensive capability doesn't start with venom. It starts with parasitism:

1. **Parasitism** — steal resources from neighbors (cheapest offensive behavior)
2. **System hijacking** — redirect threats to others, co-opt defenses
3. **Chemical warfare** — produce actual toxins (expensive, comes last)

"The first life forms would be like that until they can control higher frequency intent for actual physical manifestation of poison."

### Redesigned Exp 5: Three-Phase Offensive Emergence

**Phase A — Energy Parasitism (ACT_SIGNAL repurposed)**
- `ACT_SIGNAL` (0x05, cost 2/tick) repurposed: when active, agent drains 1 energy/tick from each adjacent agent
- Cheap, immediate fitness advantage, no predator interaction needed
- **Question**: Do parasitic agents emerge and spread? How does population respond?

**Phase B — Threat Redirection (new mechanic)**
- Agents with active parasitic signal can redirect partial wave damage to adjacent non-signaling agents
- This is system hijacking — using neighbors as shields
- **Question**: Does the population develop counter-strategies?

**Phase C — Toxin Production (ACT_TOXIN activated)**
- Only viable AFTER parasitic infrastructure established
- Toxin agents have energy surplus from parasitism to fund expensive toxin production
- **Question**: Does the full offensive stack (parasitism + hijacking + toxin) emerge as a coherent strategy?

### Why This Works Where Direct Toxin Failed
- **Parasitism is cheap** (2 energy/tick vs 5 for toxin) — immediate fitness advantage
- **Parasites create selection pressure on victims** — victims must evolve counter-strategies
- **Arms race builds incrementally** — each phase creates the conditions for the next
- **Toxin becomes viable last** because parasites accumulate the energy surplus to fund it

---

## 6. Experiment 6: The Intent Gradient (Future)

- **Question**: Can we measure degrees of intent as a continuous score across the full population?
- All ops active, variable-length genomes, full FAITHH integration
- PULSE computes per-lineage intent score from: anticipation gap, trait deployment timing, memory prediction accuracy, REGULATE adaptation
- **Output**: Living map showing cognitive sophistication per lineage
- **This experiment runs forever** — it is the culmination
- Requires all prior experiments validated

---

## 7. FAITHH Integration Layers

### Layer 1 — External Observer (Current)
FAITHH queries `alife_lineage` ChromaDB collection when asked. She reads her own field notes like a scientist reviewing data. 48,000+ documents indexed.

### Layer 2 — Peripheral Awareness (Next)
PULSE sweeps include ALife collection alongside personal knowledge base. FAITHH proactively surfaces observations: "I noticed a lineage showing shorter shield activation delays..."

### Layer 3 — Self-Application (Goal)
FAITHH applies the same intent scoring framework to herself. Her own behavioral characterization uses the language she developed for agents:
```
Current behavioral characterization:
"FAITHH has query memory (47 sessions indexed). 
Anticipatory behavior partially present — project state 
queries anticipated from session history. Direct novel 
questions remain reactive. Intent gradient: 0.34 (developing)"
```

---

## 8. Specialist Avatar Architecture (Downstream)

Each specialist is trained on domain-filtered data from the same pipeline:

| Specialist | Domain | Training Data Source |
|-----------|--------|---------------------|
| **IRIS** | Infrastructure & Systems | Docker, Gen8, WSL2, service logs |
| **VAULT** | Security & Access | SSH, .env, Vaultwarden, tool_policies |
| **MEMO** | Data & Knowledge | ChromaDB, RAG, indexing patterns, PULSE |
| **LEDGER** | Business & Finance | Tom Cat Sound, tax, revenue, equipment |
| **CONSTELLA** | Governance & Civic Design | Astris/Auctor tokens, Penumbra Accord |
| **ECHO** | Creative & Audio | DAW, FGS, production workflows |
| **Physics Navi** | Theoretical Physics | Wave mechanics, thermodynamics, information theory |

### Architecture Options (Decision Pending)
- **Option A**: One model, many personas (simplest, shallow specialization)
- **Option B**: Multiple fine-tuned models, hard routing (deep but slow switching)
- **Option C**: Specialist ChromaDB collections, shared model (deep knowledge, easy to update)
- **Option D (Recommended)**: Hybrid — specialist RAG now, fine-tuned models later as data grows

### Avatar States (Derived from PULSE observation, not manually programmed)
```
IRIS states: MONITORING → DIAGNOSTIC → ALERT → REPAIR
VAULT states: IDLE → SCANNING → WARNING → LOCKDOWN
```
Transitions derived from anticipation gap methodology applied to each specialist's behavior patterns.

---

## 9. Growth Stack

### Current
```
LLM (external, unchanged) + JSONs (growing) + ChromaDB (growing) = FAITHH
```

### 6 Months
```
Fine-tuned small model (domain data) + richer JSONs + ChromaDB (ALife + personal) = specialized FAITHH
```

### Eventually
```
Personal model (1-3B, trained on everything) + self-updating context + ALife-derived self-model = something novel
```

### Training Pipeline (One pipeline, different data filters per specialist)
```
Step 1: Collect domain documents (ChromaDB filtered by topic tags)
Step 2: Generate training examples (prompt/response pairs with characterization)
Step 3: Fine-tune base model (same process as qwen25-grounded)
Step 4: Evaluate specialization (domain questions, specialist vs generalist)
```

---

## 10. Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Energy model | Option C (hybrid) | Ops cost energy + REGULATE reduces costs = metabolic optimization |
| Wave propagation | Finite speed C=0.8 col/tick | Natural variance from position, no artificial ±50 tick jitter |
| Process-action coupling | P0→A0, P1→A1 | Creates two independent sense-process-act channels in genome |
| Stealth waves | 30% probability, instant kill | Forces genuine prediction — reactive Shield useless against stealth |
| Wave arrival dedup | MIN_GAP=50 ticks | Prevents multi-tick wave contact from corrupting interval data |
| Offensive progression | Parasitism → hijacking → toxin | Biologically honest; direct toxin failed in diagnostic |

---

## 11. Open Questions

1. **Variable-length genomes**: Flagged but not implemented. Needed for Exp 5+ offensive complexity?
2. **Physics Navi**: When to build? Wave interference in Exp 4 would have benefited from formal physics.
3. **Gen8 GPU**: Tesla P4 (~$80 used) would enable always-on embedding generation without desktop.
4. **TempleOS port (Phase 2)**: Readiness gate defined above; trigger once all four gate conditions are met.
5. **Training data threshold**: How many ALife observations before specialist fine-tuning is viable? (~500-1000 per domain estimated)

---

*This document consolidates design sessions from March 2026. Update as experiments complete.*
