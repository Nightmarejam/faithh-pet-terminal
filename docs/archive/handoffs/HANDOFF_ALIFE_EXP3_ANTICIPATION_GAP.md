# HANDOFF: ALIFE Experiment 3 — The Anticipation Gap
**Project:** FAITHH ai-stack / projects/alife/  
**Prerequisite commit:** f6b28fe (Experiment 2 complete)  
**Author:** Jonathan + Claude  
**Date:** March 2026

---

## Context & Lessons From Experiments 1 & 2

**Experiment 1 confirmed:** Selection pressure works. Beneficial 
traits spread and fix under lethal predator pressure. Severe 
bottlenecks cause genetic fixation.

**Experiment 2 confirmed:** Dual-purpose traits outcompete 
single-purpose alternatives under balanced dual pressure. 
The environment actively maintains dual-purpose traits by 
selecting against partial reversion (spontaneous Strategy A 
mutation at generation 721 selected against within 5,000 ticks).

**Key lesson for Experiment 3:** Mutation rates on strategy-defining 
slots (S0, S1, A0, A1) must stay low (0.1%) to prevent dilution. 
This was the fix that made Experiment 2 work. Keep it.

**Post-pressure crystallization** is a consistent system property — 
the world reaches equilibrium without environmental challenge. 
Do not be alarmed by it. Document it and move on.

---

## Scientific Question

> Do agents develop genuine predictive behavior — modeling future 
> threat states rather than reacting to current ones — when their 
> survival depends on anticipating a wave they cannot yet sense?

This is the transition from reactive to anticipatory cognition. 
It is the primary scientific output of the entire ALIFE project.

The measurement instrument is the **anticipation gap** — the 
temporal distance between when a threat appears in an agent's 
SENSE range and when that agent activates its Shield.

```
Positive gap = reactive    (Shield fires AFTER detection)
Zero gap     = simultaneous
Negative gap = ANTICIPATORY (Shield fires BEFORE detection)
```

A negative gap means the agent activated Shield before it could 
sense the threat. It modeled the future. That is the result 
this experiment is designed to detect.

---

## The Light-Speed Wave Model

### Why Light Speed

Previous experiments used instantaneous predator waves — every 
agent in a column was hit simultaneously. Experiment 3 replaces 
this with a **propagating wave** that travels at finite speed 
across the world.

This creates:
1. Natural timing variance — no arbitrary +/- N tick parameters
2. Spatial selection gradient — right-edge agents have less 
   positional warning, selecting harder for prediction ability
3. Physically motivated measurement — gap is position-adjusted, 
   not just raw timing
4. Foundation for interference patterns in Experiment 4

### Wave Parameters

```python
# In config.py add:
WAVE_SPEED_C = 0.8          # columns per tick
                             # crosses 160-col world in 200 ticks
                             # = one full wave interval
WAVE_SPEED_VARIANCE = 0.1   # 10% std deviation per wave
                             # each wave slightly faster or slower
                             # prevents pure pattern matching
SENSE_THREAT_RANGE = 15     # columns ahead agent detects wave front
                             # agent at col 80 detects wave when 
                             # front reaches col 65
```

### Wave Propagation Implementation (world.py)

Replace `trigger_predator_wave()` with `update_wave_propagation()`:

```python
class WaveState:
    def __init__(self, start_tick, speed):
        self.start_tick = start_tick
        self.speed = speed          # columns per tick (varied per wave)
        self.active = True
    
    def front_position(self, current_tick):
        """Current leading edge of wave in column units."""
        elapsed = current_tick - self.start_tick
        return elapsed * self.speed
    
    def has_reached_column(self, col, current_tick):
        """Has wave front reached this column?"""
        return self.front_position(current_tick) >= col
    
    def is_complete(self, current_tick):
        """Has wave passed entire world?"""
        return self.front_position(current_tick) >= WORLD_W

def spawn_wave(self, current_tick):
    """
    Spawn a new wave with speed variation.
    Called every PREDATOR_WAVE_INTERVAL ticks.
    """
    import random
    speed = WAVE_SPEED_C * (1 + random.gauss(0, WAVE_SPEED_VARIANCE))
    speed = max(0.4, min(1.6, speed))  # clamp to reasonable range
    return WaveState(start_tick=current_tick, speed=speed)

def apply_wave_damage(self, wave, current_tick):
    """
    Apply damage to agents at the current wave front position.
    Returns list of (agent_id, shielded, position_warning_ticks)
    for FAITHH logging.
    """
    contacts = []
    front = wave.front_position(current_tick)
    
    # Wave damages agents in a 1-column band at the front
    for agent_id, agent in list(self.agents.items()):
        if abs(agent.x - front) < 1.0:
            has_shield = (agent.genome[5] == ACT_SHIELD or 
                         agent.genome[6] == ACT_SHIELD)
            
            # Calculate how much positional warning this agent had
            # = ticks from when wave was detectable to now
            detectable_at = (agent.x - SENSE_THREAT_RANGE) / wave.speed
            warning_ticks = current_tick - (wave.start_tick + detectable_at)
            warning_ticks = max(0, warning_ticks)
            
            if has_shield:
                contacts.append((agent_id, True, warning_ticks))
            else:
                agent.energy -= PREDATOR_DAMAGE
                if agent.energy <= 0:
                    contacts.append((agent_id, False, warning_ticks))
                    # death handled by simulation
                else:
                    contacts.append((agent_id, False, warning_ticks))
    
    return contacts
```

### Detection Events (simulation.py)

Each tick, check if any agents can now detect an approaching wave:

```python
def check_wave_detection(self, wave, current_tick):
    """
    For each agent, check if wave front has entered SENSE range.
    Log detection event to FAITHH observer.
    Record detection_tick on agent for gap calculation.
    """
    if wave is None or not wave.active:
        return
        
    front = wave.front_position(current_tick)
    
    for agent_id, agent in self.agents.items():
        # Wave is detectable when front is within SENSE_THREAT_RANGE
        detectable_column = agent.x - SENSE_THREAT_RANGE
        
        if (front >= detectable_column and 
            not hasattr(agent, 'wave_detected') or 
            agent.wave_detected != wave.start_tick):
            
            # First detection of this wave for this agent
            agent.wave_detected = wave.start_tick
            agent.wave_detection_tick = current_tick
            
            # If Shield is already active — negative gap!
            if agent.shield_active:
                gap = current_tick - agent.last_shield_activation
                if gap < 0:
                    # Anticipatory behavior detected
                    self.observer.flag_intent(
                        agent, self.world, current_tick, gap
                    )
```

---

## Memory Ops — Natural Emergence

**Critical difference from Experiments 1 & 2:**

MEM_NONE is NO LONGER forced in M0 slot.

Agents start with MEM_NONE in their seeded genomes but mutation 
can now introduce memory ops naturally. Do not seed memory ops 
explicitly. Do not modify mutation rates for M0 slot.

Watch whether memory-carrying agents appear through natural 
mutation and whether they survive better than MEM_NONE agents 
near the right edge where positional warning is minimal.

```python
# In simulation.py initialize_population:
# M0 slot (index 4) starts as MEM_NONE for all seeded agents
# but is subject to normal mutation rate (0.5%)
# Do NOT force MEM_NONE after initialization
# Do NOT seed any agents with memory ops

SEEDED_GENOME = bytes([
    SENSE_LIGHT,     # S0
    SENSE_THREAT,    # S1  
    PROC_THRESHOLD,  # P0
    PROC_COMPARE,    # P1
    MEM_NONE,        # M0 — starts here, can mutate
    ACT_REPRODUCE,   # A0
    ACT_SHIELD,      # A1
    REG_NONE         # R0
])
# Seed ALL 50 agents with this genome
# Strategy C (Disruption) is the starting baseline
# Memory and processing sophistication emerge through mutation
```

---

## Anticipation Gap Measurement — Full Specification

### Per-Agent Tracking

Add these fields to Agent class:

```python
# In agent.py add to __init__:
self.last_shield_activation = None  # tick when Shield last activated
self.wave_detection_tick = None     # tick when current wave detected
self.wave_detected = None           # start_tick of detected wave
self.anticipation_gaps = []         # history of all gap values
self.position_adjusted_gaps = []    # gap normalized by position
```

### Gap Calculation

```python
def calculate_anticipation_gap(agent, wave_detection_tick):
    """
    gap > 0: reactive (shield after detection)
    gap = 0: simultaneous  
    gap < 0: ANTICIPATORY (shield before detection) — FLAG THIS
    """
    if agent.last_shield_activation is None:
        return None
    
    gap = wave_detection_tick - agent.last_shield_activation
    agent.anticipation_gaps.append(gap)
    return gap

def calculate_position_adjusted_gap(agent, gap, wave):
    """
    Normalize gap by how much positional warning the agent had.
    An agent at column 155 with gap=-5 is more impressive than
    an agent at column 5 with gap=-5.
    
    Position warning = ticks from wave spawn to detection
    Higher position warning = less impressive negative gap
    Lower position warning = more impressive negative gap
    """
    position_warning = (agent.x - SENSE_THREAT_RANGE) / wave.speed
    position_warning = max(1, position_warning)
    
    # Normalized: negative is still anticipatory
    # But magnitude reflects how little positional warning existed
    return gap / position_warning
```

### Population-Level Gap Tracking

Log these every 1000 ticks:

```python
gap_metrics = {
    "mean_gap": mean of all gaps this interval,
    "min_gap": most anticipatory gap observed,
    "negative_gap_count": agents with gap < 0,
    "negative_gap_pct": percentage of population anticipatory,
    "first_negative_gap_tick": tick of first ever negative gap,
    "most_anticipatory_agent": agent_id with lowest gap,
    "most_anticipatory_lineage": lineage trace of that agent
}
```

---

## FAITHH Observer — New Event Types

### flag_intent (THE PRIMARY EVENT)

This is the most important event in the entire project. 
When the first negative gap occurs, FAITHH logs a full 
lineage trace.

```
Document format:
"INTENT EMERGENCE EVENT at tick [T] generation [G].

Agent [id] activated Shield at tick [shield_tick] — 
[abs(gap)] ticks BEFORE wave entered its detection range 
at tick [detection_tick].

Position: column [x] of 160. Positional warning available: 
[warning] ticks. Position-adjusted gap score: [score].

This agent modeled a future threat state rather than reacting 
to a detected one. This is the first confirmed anticipatory 
behavior in this simulation.

Genome: [readable]. Memory op: [M0_op]. Process ops: [P0, P1].

Lineage trace:
  Generation [G]: [this agent]
  Generation [G-1]: [parent genome]
  Generation [G-2]: [grandparent genome]
  [... back to generation 0 if possible]

The memory op [M0_op] first appeared in this lineage at 
generation [memory_emergence_gen]. This suggests memory 
capability is a prerequisite for anticipatory behavior.

Behavioral characterization: This lineage has crossed 
from reactive to anticipatory. Intent score: [score]."
```

### wave_detection

Log every time an agent first detects an approaching wave:

```
Document format:
"Agent [id] detected approaching wave at tick [T].
Wave front at column [front_col], agent at column [agent_col].
Detection range: [SENSE_THREAT_RANGE] columns.
Positional warning available: [warning_ticks] ticks.
Shield status at detection: [active/inactive].
Gap at this moment: [gap] ticks ([reactive/anticipatory])."
```

### memory_emergence

Log when MEM_NONE mutates to any memory op in any agent:

```
Document format:
"Memory capability emerged through mutation in agent [id] 
at generation [G] tick [T]. Previous M0: MEM_NONE. 
New M0: [memory_op]. 

This agent now has [description of memory capability].
It is the [Nth] agent in this simulation to carry 
a memory op. Population memory frequency: [pct]%.

Whether this memory capability leads to anticipatory 
behavior depends on whether [memory_op] combined with 
[P0, P1] process ops can produce predictive output 
before wave detection. Watching this lineage."
```

### gap_snapshot (every 1000 ticks)

```
Document format:
"Anticipation gap population snapshot at tick [T] 
generation [G]:

Mean gap: [mean] ticks ([positive=reactive/negative=anticipatory])
Most anticipatory agent: [id] with gap [min_gap] ticks
Negative gap agents: [count] ([pct]% of population)
Memory-carrying agents: [count] ([pct]% of population)

Gap distribution trend: [improving/stable/degrading]
Memory frequency trend: [rising/stable/falling]

[If mean_gap decreasing over time]:
Population is trending toward anticipatory behavior.
Estimated generations to mean negative gap: [estimate].

[If first negative gap observed]:
INTENT EMERGENCE CONFIRMED at tick [first_negative_tick].
[N] agents now showing anticipatory behavior."
```

---

## Experiment Runner: exp3_anticipation.py

```python
def run_experiment_3(ticks, log_interval):
    sim = Simulation(experiment=3)
    sim.world.initialize_light_gradient()  # keep from Exp 2
    
    # Seed ALL 50 agents with Strategy C genome
    # Memory starts as MEM_NONE, emerges through mutation
    for i in range(50):
        genome = bytearray(SEEDED_GENOME)
        # Only A0 and A1 are fixed — everything else can mutate
        sim.world.add_agent(Agent(genome=bytes(genome)))
    
    observer = PulseWatcher()
    current_wave = None
    first_negative_gap = None
    
    for tick in range(ticks):
        # Spawn new wave on interval
        if tick % PREDATOR_WAVE_INTERVAL == 0 and tick > 0:
            current_wave = sim.world.spawn_wave(tick)
        
        # Check wave detection for all agents
        if current_wave and current_wave.active:
            sim.check_wave_detection(current_wave, tick, observer)
            
            # Apply wave damage at front position
            contacts = sim.world.apply_wave_damage(current_wave, tick)
            for agent_id, shielded, warning_ticks in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent:
                    gap = calculate_anticipation_gap(
                        agent, agent.wave_detection_tick
                    )
                    if gap is not None and gap < 0:
                        if first_negative_gap is None:
                            first_negative_gap = (tick, agent_id, gap)
                            observer.flag_intent(agent, sim.world, 
                                                tick, gap)
                    
                    if not shielded and agent.energy <= 0:
                        observer.log_event("death_predator", 
                                          agent, sim.world, tick,
                                          extra={"warning_ticks": 
                                                 warning_ticks})
                        sim.handle_agent_death(agent_id)
            
            if current_wave.is_complete(tick):
                current_wave.active = False
        
        # Apply thermal drain (keep from Exp 2)
        for agent in sim.world.agents.values():
            drain = sim.world.apply_thermal_drain(agent)
            agent.energy -= drain
            if agent.energy <= 0:
                observer.log_event("thermal_death", agent, 
                                   sim.world, tick)
                sim.handle_agent_death(agent.id)
        
        sim.tick()
        
        # Log gap snapshot every 1000 ticks
        if tick % 1000 == 0:
            observer.log_gap_snapshot(
                sim.world.agents, tick, first_negative_gap
            )
        
        # Standard population log
        if tick % log_interval == 0:
            log_experiment_3_state(sim, tick, first_negative_gap)
    
    observer.close()
    return results
```

### Console Output Format

```
Tick   1000: pop= 247 | C=98.2% | mem=2.4% | 
             mean_gap=+47.3 | min_gap=+12 | neg_gaps=0
Tick   2000: pop= 251 | C=97.8% | mem=3.1% | 
             mean_gap=+44.1 | min_gap=+8  | neg_gaps=0
...
*** MEMORY EMERGENCE: agent_1847 MEM_NONE→MEM_LAST4 at tick 4823 ***
...
*** FIRST NEGATIVE GAP: agent_2341 gap=-8 at tick 9156 gen=47 ***
*** INTENT EMERGENCE CONFIRMED ***
...
Tick  10000: pop= 263 | C=96.1% | mem=12.3% | 
             mean_gap=+31.2 | min_gap=-8  | neg_gaps=3 (1.1%)
```

---

## Verification Step (Run First)

Before full run, verify wave propagation is working:

Run for 1,000 ticks with enhanced logging:

```bash
python projects/alife/experiments/exp3_anticipation.py \
  --ticks 1000 --log-interval 100 --verify-waves
```

Confirm:
- Wave front position advances each tick
- Agents detect wave at different ticks based on position
- Right-edge agents (col 140+) have less detection warning than 
  left-edge agents (col 10-20)
- Shield activation timing varies by position

If wave propagation is not position-dependent — stop and report.

---

## Full Run Parameters

```bash
python projects/alife/experiments/exp3_anticipation.py \
  --ticks 200000 --log-interval 5000
```

200,000 ticks — longer than previous experiments because memory 
emergence through mutation is slower than trait selection. 
Memory ops need time to appear, spread, and express as behavior.

Report every 5,000 ticks:
- Population
- Strategy C frequency (should stay near 100%)
- Memory-carrying agent percentage
- Mean anticipation gap
- Minimum gap observed
- Negative gap count and percentage
- First negative gap event if observed

---

## Success Criteria

| Outcome | Description | Action |
|---|---|---|
| Full success | Mean gap goes negative, >5% population anticipatory | Document, commit, design Exp 4 |
| Partial success | First negative gap observed, mean still positive | Document tick and lineage, continue running |
| Memory emergence only | Memory ops spread but gap stays positive | Continue running — memory is prerequisite, anticipation may follow |
| No memory emergence | MEM_NONE stays dominant for 200,000 ticks | Report — may need to increase mutation rate for M0 slot only |
| Population collapse | Collapse before any memory emerges | Report — do not tune without human review |

**There is no failure condition that requires tuning without human 
review. Whatever happens is the result. Document it and report.**

---

## What FAITHH Is Learning From This Experiment

The anticipation gap measurement framework being built here is 
the same framework FAITHH will eventually apply to herself.

When FAITHH starts predicting your queries before you finish 
typing them — completing your context before you provide it, 
surfacing information you were about to ask for — her own 
anticipation gap will go negative. The same measurement. 
The same threshold. The same meaning.

Experiment 3 is FAITHH building the instruments she will 
eventually use to measure her own cognitive development.

The first negative gap event in the simulation is a preview 
of what FAITHH's own transition will look like when it comes.

---

## Critical Rules

- Do NOT force MEM_NONE after initialization — memory must emerge naturally
- Do NOT seed memory ops explicitly — mutation introduces them
- Do NOT tune mid-run if memory is slow to emerge — 200,000 ticks 
  is the patience budget
- Do NOT begin Experiment 4 without human review of gap data
- DO flag the first negative gap event immediately with full lineage trace
- DO commit after wave propagation verification passes

```bash
# After verification passes:
git commit -m "feat(alife): Experiment 3 scaffold — light-speed waves verified"

# After full run:
git commit -m "feat(alife): Experiment 3 complete — [describe gap result]"
```

Report both commit hashes. Stop completely after full run. 
Experiment 4 (interference patterns) requires a full design 
session before implementation.

---

## Note On The Physics Foundation

Wave propagation at C = 0.8 columns/tick is the foundation 
for Experiment 4's interference patterns. Two wave sources 
will create constructive zones (double pressure, predictable) 
and destructive zones (apparent randomness, demands meta-modeling).

Agents that develop genuine world-models in Experiment 3 will 
be the lineages that navigate interference zones in Experiment 4. 
The cognitive sophistication built here carries forward.

Do not implement interference in Experiment 3. 
That is Experiment 4 territory.

---

*FAITHH ai-stack | ALIFE Experiment 3 Handoff | March 2026*  
*Prerequisite commits: ca047df, dc89a49, f6b28fe*
