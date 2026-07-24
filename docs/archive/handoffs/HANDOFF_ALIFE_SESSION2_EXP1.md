# HANDOFF: ALIFE Session 2 — Experiment 1 Pressure Test
**Project:** FAITHH ai-stack / projects/alife/  
**Last commit:** d4a651b (Task 3 — FAITHH PULSE observer connected)  
**Date:** March 2026  
**Status:** Ready for Experiment 1

---

## Where We Left Off

Two experiments complete and committed:

| Commit | What | Status |
|---|---|---|
| ca047df | Experiment 0 — stable population economics | ✅ Passing |
| d4a651b | Task 3 — FAITHH PULSE observer + ChromaDB | ✅ Passing |

### Current Simulation State
- Natural carrying capacity: ~55 agents (1000 tick run) to ~324 (10,000 tick run)
- Stable avg energy: ~180-210
- FAITHH observer logging 37 events per 1000 ticks to `alife_lineage` collection
- ChromaDB at servicebox.taileb8c60.ts.net:8000 confirmed live with natural language docs
- All 50 initial agents seeded with ACT_REPRODUCE (A0) and ACT_CONSUME (A1)

### One Thing To Watch
In the Task 3 verification run, agent_51 reproduced with world energy = 0 at its 
location. It ate its cell completely empty before reproducing. Watch whether this 
"scorched earth reproduction" pattern persists or gets selected against in Experiment 1 
— agents that deplete their local environment may struggle when predators arrive.

---

## Today's Task: Experiment 1 — The Pressure Test

### Scientific Question
Does selection pressure produce heritable trait differentiation?  
Specifically: does the Shield trait (ACT_SHIELD) spread through the population 
when predator waves create survival pressure?

### What Gets Added
A predator wave mechanic — a threat that sweeps the world from left to right 
every 500 ticks. Agents without ACT_SHIELD in their genome lose 150 energy on 
contact, which is usually fatal. Agents with ACT_SHIELD active block the predator 
but pay 1 energy/tick while shielded.

### Success Criteria
- Shield trait frequency rises above 50% within 20 generations under pressure
- Shield trait frequency drops below 20% within 10 generations after predator removed
- If reversion does NOT occur after predator removed, that's a finding worth 
  reporting — it may mean the Shield trait became fixed regardless of pressure

---

## Task 4 Build Spec for Windsurf

### Step 1 — Add predator wave to world.py

Add a method `trigger_predator_wave(tick)` to the World class:

```python
def trigger_predator_wave(self, tick):
    """
    Sweeps a predator wave from left to right across the world.
    Called every PREDATOR_WAVE_INTERVAL ticks.
    Returns list of agent_ids contacted by the wave.
    """
    # Wave column = (tick // PREDATOR_WAVE_INTERVAL) % WORLD_W
    # All agents in that column are contacted
    # If agent has ACT_SHIELD active: no damage
    # If agent does not have ACT_SHIELD active: -150 energy
    # Return list of (agent_id, shielded: bool) tuples
```

Add to config.py:
```python
PREDATOR_WAVE_INTERVAL = 500    # ticks between waves
PREDATOR_DAMAGE = 150           # energy loss on unshielded contact
PREDATOR_REMOVAL_TICK = 25000   # tick when predator is removed mid-experiment
```

### Step 2 — Add Shield tracking to agent.py

Add `shield_active` boolean property to Agent class.
Shield activates when ACT_SHIELD is in A0 or A1 AND the process condition fires.
Track `shield_activations` counter on agent for FAITHH logging.

### Step 3 — Create experiments/exp1_pressure.py

Structure mirrors exp0_primordial.py with additions:

```python
# Initialize from stable Exp 0 state (copy population mechanics)
# Run predator wave every PREDATOR_WAVE_INTERVAL ticks
# Track Shield trait frequency per generation
# At tick PREDATOR_REMOVAL_TICK: stop triggering waves
# Continue 10 more generations after removal to observe reversion
# Log Shield frequency to FAITHH observer every 100 ticks
```

Run length: 50,000 ticks minimum (covers ~100 generations at current reproduction rate)

### Step 4 — Add new event types to faithh_observer.py

Add handling for these event types (already stubbed, need implementation):

**shield_activation:**
```
"Agent agent_89 activated its Shield trait at tick 4823 generation 7. 
Predator wave contact imminent — wave column 47, agent at column 47. 
Shield cost: 1 energy/tick. Agent energy before shield: 198. 
This agent is behaving reactively — shield fires on threat contact, 
not in anticipation of it. Genome: [readable genome string]."
```

**death_predator:**
```
"Agent agent_134 died at tick 5001 from predator contact at generation 9. 
It did not have ACT_SHIELD active. Energy at death: 0 (from 187 before 
predator contact — lethal damage). This lineage ends here. 
Genome lacked shield protection: [readable genome string]."
```

**trait_frequency_snapshot** (new event type — add to observer):
```
"Shield trait frequency snapshot at tick 5000 generation 10: 
34% of population carries ACT_SHIELD in A0 or A1. 
Up from 8% at generation 1. Selection pressure is working — 
shielded lineages surviving predator waves at higher rates."
```

### Step 5 — Verification

Run exp1_pressure.py for 10,000 ticks first as a quick check:
- Predator waves should be visible in the death counts at wave ticks
- Shield trait frequency should be rising
- FAITHH observer should log shield_activation and death_predator events

Then run full 50,000 ticks and report:
- Shield frequency table per generation (gen 1, 5, 10, 20)
- First Shield emergence event (which agent, which generation)
- Population curve showing wave impacts
- FAITHH ChromaDB document count

**Stop and report after 50,000 ticks. Do not begin predator removal phase 
without human review of Shield frequency data.**

---

## What To Watch For — Reading The Output

### Healthy Experiment 1 Output
```
Tick  500: wave hit, deaths spike, pop drops ~20%
Tick 1000: pop recovered, Shield frequency rising
Gen   5:  Shield in 23% of population
Gen  10:  Shield in 47% of population  
Gen  20:  Shield in 71% of population  ← selection working
```

### Interesting Outcomes Worth Flagging
- **Shield frequency plateaus below 50%** — cost of shielding may be too high 
  relative to predator damage. Report plateau level and tick.
- **Population collapses under predator pressure** — waves too frequent or 
  damage too high. Increase PREDATOR_WAVE_INTERVAL to 750 if collapse occurs.
- **Shield frequency rises then falls** — agents evolving ACT_FLEE instead of 
  ACT_SHIELD as a cheaper alternative. Report which act op is spreading instead.
- **Any agent with MEM_PATTERN or MEM_LAST8 activating Shield early** — 
  this would be the first anticipatory signal appearing before Experiment 3. 
  Flag immediately with full lineage trace.

---

## Architecture Reminder

```
Gen8 (servicebox, servicebox.taileb8c60.ts.net)
  └── Python simulation — exp1_pressure.py
  └── ChromaDB — alife_lineage collection

Windows Desktop (when on)
  └── FAITHH analysis of accumulated lineage data
  └── RTX 3090 for embedding if needed

DS220j (NAS)
  └── File storage only at this stage
```

No hardware changes needed. No new dependencies needed.

---

## Agent Behavior Rules

- Read AGENTS.md before starting
- Do not chain tasks — stop and report after each verification
- If predator wave causes immediate population collapse, 
  increase PREDATOR_WAVE_INTERVAL and report — do not retry silently
- All observer calls wrapped in try/except — observer failure non-fatal
- Commit after verification passes with message:
  `feat(alife): Experiment 1 — predator pressure + Shield trait emergence`

---

## Bigger Picture — What Experiment 1 Proves

Experiment 0 proved the world can sustain life.  
Experiment 1 proves selection pressure produces heritable change.  

If Shield trait frequency rises under pressure and falls when pressure 
is removed, you have confirmed that natural selection is working in 
your simulation. That's the foundation everything else builds on.

Experiment 2 (The Stripe Test) and Experiment 3 (The Anticipation Gap) 
both depend on this being solid. Don't rush it.

---

## Questions To Bring To Claude Before Starting Experiment 2

After Experiment 1 completes, bring the Shield frequency data back 
before writing the Experiment 2 spec. Experiment 2 introduces dual 
simultaneous pressures — the thermal drain plus predator waves — and 
the balance between those two pressures determines whether the 
dual-purpose Disruption trait emerges or single-purpose traits dominate.

That balance needs to be calibrated based on what Experiment 1 tells 
us about how strong the predator pressure actually is in practice.

---

*FAITHH ai-stack | ALIFE Session 2 Handoff | March 2026*
*Previous session commits: ca047df, d4a651b*
