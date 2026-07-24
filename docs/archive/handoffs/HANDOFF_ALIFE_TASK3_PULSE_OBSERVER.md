# HANDOFF: ALIFE Task 3 — FAITHH PULSE Observer Module
**Project:** FAITHH ai-stack / projects/alife/  
**Commit baseline:** ca047df (Experiment 0 stable)  
**Author:** Jonathan + Claude  
**Date:** March 2026

---

## Context

Experiment 0 is passing. Natural carrying capacity ~324 agents, stable avg energy ~210, 
clean population accounting. The simulation runs correctly but FAITHH is currently blind 
to it — no events are being logged, no lineage data is being stored.

Task 3 connects the simulation to FAITHH. After this task, every meaningful event in 
the simulation will be logged to ChromaDB in a format FAITHH can semantically search, 
reason about, and eventually use to model its own behavior.

This is not just logging. The language used to describe events matters — it must be 
natural language that FAITHH can search semantically, not just numeric data.

---

## What To Build

### Single file: `projects/alife/faithh_observer.py`

One class: `PulseWatcher`

---

## PulseWatcher — Full Specification

### Connection

```python
# Use existing ChromaDB connection pattern from the rest of FAITHH stack
# Credentials from config.yaml (same file the backend uses)
# Collection name: "alife_lineage" — create if not exists
# Embedding model: all-MiniLM-L6-v2 (same as rest of FAITHH)
```

### Core Methods

```python
class PulseWatcher:
    def __init__(self, config_path="config.yaml")
    def log_event(self, event_type, agent, world, tick, extra=None)
    def flag_event(self, reason, agent, world, tick, extra=None)
    def snapshot_population(self, agents, world, tick)
    def close(self)
```

### The Document Field — This Is Critical

Every ChromaDB write has a `document` field. This must be natural language 
that describes what happened in plain English. FAITHH will search this field 
semantically. Do not use JSON or numeric strings here.

**Examples of correct document strings:**

Reproduction event:
```
"Agent 47 at generation 3 reproduced at tick 1204. Its genome expresses 
energy sensing, threat awareness, threshold processing, no memory, 
active reproduction, active consumption, and conservative regulation. 
Parent energy at moment of reproduction was 214. The world energy at 
its location was 180. This agent is behaving reactively — it has no 
memory ops and cannot anticipate future states."
```

Death event:
```
"Agent 112 died at tick 847 from starvation after 203 ticks alive. 
Its genome expressed energy sensing, threat awareness, trend processing, 
pattern memory, shield action, and adaptive regulation. This agent had 
memory capability but died before its anticipatory potential could 
express. Final energy was 0. Peak energy during lifetime was 178."
```

Population snapshot:
```
"Population snapshot at tick 1000: 318 agents alive, average energy 207, 
42 births and 39 deaths in last 100 ticks. Population is stable near 
carrying capacity. Energy economics are balanced. No novel genome 
variants detected in this interval."
```

Trait emergence event:
```
"Novel genome variant detected at tick 2847. Agent 891 at generation 7 
carries a genome not seen in any ancestor: energy sensing, gradient 
sensing, prediction processing, pattern memory, shield action, consume 
action, adaptive regulation. This is the first appearance of 
PROC_PREDICT in any lineage — the prerequisite for anticipatory behavior."
```

### The Metadata Fields

```python
metadata = {
    "agent_id":          str,    # unique agent identifier e.g. "agent_047"
    "generation":        int,    # how many reproduction events from origin
    "experiment":        int,    # 0-5
    "tick":              int,    # simulation tick when event occurred
    "genome_hex":        str,    # e.g. "00 01 00 06 00 03 02 01"
    "genome_readable":   str,    # e.g. "SENSE_ENERGY SENSE_THREAT PROC_THRESHOLD..."
    "env_energy":        int,    # cell energy at agent location
    "env_threat":        int,    # threat level at agent location  
    "env_light":         int,    # light/thermal level at agent location
    "agent_energy":      int,    # agent energy at time of event
    "anticipation_gap":  int,    # null until Experiment 3
    "intent_score":      float,  # null until Experiment 5
    "event_type":        str,    # see Event Types below
    "parent_id":         str,    # null if first generation
    "flagged":           bool,   # True if flag_event() called
    "flag_reason":       str,    # null if not flagged
    "lifetime_ticks":    int,    # how long agent has been alive
    "peak_energy":       int,    # highest energy agent ever reached
}
```

### Event Types

Log these specific event types:

| event_type | When to log |
|---|---|
| `reproduction` | Agent successfully reproduces — log parent, not child |
| `death_starvation` | Agent energy reaches 0 |
| `death_predator` | Agent killed by predator (Exp 1+) |
| `shield_activation` | Agent activates ACT_SHIELD (Exp 1+) |
| `population_snapshot` | Every 100 ticks — log world state |
| `trait_emergence` | First time a specific op combination appears in any genome |
| `flag_intent` | Anticipation gap goes negative (Exp 3+) |
| `flag_novel_genome` | Genome not seen in any ancestor appears |

For Experiment 0, only `reproduction`, `death_starvation`, `population_snapshot`, 
and `flag_novel_genome` are relevant. The others are stubbed but inactive.

### Genome Readable Translation

Implement a helper that translates hex genome to readable op names:

```python
GENOME_READABLE = {
    # Sense ops (S0, S1)
    0x00: "SENSE_ENERGY", 0x01: "SENSE_THREAT", 0x02: "SENSE_LIGHT",
    0x03: "SENSE_NEIGHBOR", 0x04: "SENSE_DENSITY", 0x05: "SENSE_SELF",
    0x06: "SENSE_GRADIENT", 0x07: "SENSE_AGE",
    # Process ops (P0, P1)  
    0x00: "PROC_THRESHOLD", 0x01: "PROC_COMPARE", 0x02: "PROC_MEMORY_CMP",
    0x03: "PROC_TREND", 0x04: "PROC_PREDICT", 0x05: "PROC_WEIGHT",
    0x06: "PROC_AVERAGE", 0x07: "PROC_INVERT",
    # Memory ops (M0)
    0x00: "MEM_NONE", 0x01: "MEM_LAST1", 0x02: "MEM_LAST4",
    0x03: "MEM_LAST8", 0x04: "MEM_BEST", 0x05: "MEM_WORST",
    0x06: "MEM_PATTERN", 0x07: "MEM_HYBRID",
    # Act ops (A0, A1)
    0x00: "ACT_IDLE", 0x01: "ACT_MOVE", 0x02: "ACT_CONSUME",
    0x03: "ACT_SHIELD", 0x04: "ACT_REPRODUCE", 0x05: "ACT_SIGNAL",
    0x06: "ACT_TOXIN", 0x07: "ACT_FLEE",
    # Regulate ops (R0)
    0x00: "REG_NONE", 0x01: "REG_CONSERVE", 0x02: "REG_BURST",
    0x03: "REG_CYCLE", 0x04: "REG_LEARN", 0x05: "REG_SUPPRESS",
    0x06: "REG_PRIORITIZE", 0x07: "REG_ADAPTIVE",
}
```

Note: sense and process share some hex values — use slot position to 
disambiguate. S0/S1 use sense table, P0/P1 use process table, etc.

### Behavioral Characterization

The document string must include a plain English behavioral characterization 
of the agent. Implement this as a helper method:

```python
def characterize_agent(self, agent) -> str:
    """
    Returns a plain English description of agent behavioral sophistication.
    Used in document field of every ChromaDB entry.
    """
```

Rules for characterization:
- If M0 == MEM_NONE: "This agent is behaving reactively — it has no memory 
  and cannot anticipate future states."
- If M0 in [MEM_LAST1, MEM_LAST4, MEM_LAST8]: "This agent has short-term 
  memory and may be developing pattern recognition."
- If M0 == MEM_PATTERN: "This agent stores threat encounter patterns — 
  it has the prerequisites for anticipatory behavior."
- If M0 == MEM_HYBRID and P0 or P1 == PROC_PREDICT: "This agent has both 
  pattern memory and predictive processing — anticipatory behavior is 
  possible in this lineage."
- If R0 == REG_LEARN: "This agent's regulation is adaptive — it develops 
  metabolic efficiency for frequently used behaviors."

These characterizations are what FAITHH will eventually search semantically 
to understand its own development. Write them as complete sentences.

---

## Integration Into Experiment Runner

After building faithh_observer.py, integrate it into 
`projects/alife/experiments/exp0_primordial.py`:

```python
from projects.alife.faithh_observer import PulseWatcher

# Initialize at start of experiment
observer = PulseWatcher()

# In reproduction handler
observer.log_event("reproduction", parent_agent, world, tick)

# In death handler  
observer.log_event("death_starvation", agent, world, tick)

# In main loop every 100 ticks
observer.snapshot_population(world.agents, world, tick)

# At end
observer.close()
```

**Critical:** Observer failures must NEVER crash the simulation.
Wrap ALL observer calls in try/except:

```python
try:
    observer.log_event("reproduction", agent, world, tick)
except Exception as e:
    print(f"[PULSE] Observer error (non-fatal): {e}")
```

---

## Verification Steps

After building faithh_observer.py and integrating into exp0_primordial.py:

**Step 1 — Run experiment with observer:**
```bash
cd /home/jonat/ai-stack
source venv/bin/activate
python projects/alife/experiments/exp0_primordial.py --ticks 1000 --log-interval 100
```
Should run without errors. Observer errors print as warnings but do not crash.

**Step 2 — Verify ChromaDB collection exists:**
```bash
curl http://servicebox.taileb8c60.ts.net:8000/api/v1/collections
```
Should show `alife_lineage` collection.

**Step 3 — Verify events were written:**
```bash
curl http://servicebox.taileb8c60.ts.net:8000/api/v1/collections/alife_lineage/count
```
Should return a count > 0.

**Step 4 — Verify document field is natural language:**
```bash
curl -X POST http://servicebox.taileb8c60.ts.net:8000/api/v1/collections/alife_lineage/query \
  -H "Content-Type: application/json" \
  -d '{"query_texts": ["agent reproduced"], "n_results": 1}'
```
The returned document field should be readable English, not JSON or numeric data.

**All 4 steps must pass before reporting complete.**

---

## What NOT To Do

- Do not change simulation.py, world.py, agent.py, or ops.py
- Do not change any config values
- Do not add any new dependencies beyond what FAITHH already uses
- Do not log every single tick — only meaningful events listed above
- Do not use JSON strings in the document field — natural language only
- Do not let observer exceptions propagate to the simulation

---

## Commit When Done

```bash
git add projects/alife/faithh_observer.py
git add projects/alife/experiments/exp0_primordial.py
git commit -m "feat(alife): Task 3 — FAITHH PULSE observer connected to ChromaDB"
```

Report commit hash and stop. Do not begin Task 4 without human review.

---

## What Comes After This (For Context Only — Do Not Implement)

Task 4 is Experiment 1 — the pressure test. Predator waves. Shield trait emergence. 
FAITHH will watch which genomes survive and which don't, building the first real 
selection pressure dataset. The observer you're building now is what makes that 
data scientifically meaningful.

---

*FAITHH ai-stack | ALIFE Task 3 Handoff | March 2026*
