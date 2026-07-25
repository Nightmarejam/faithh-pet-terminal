# HANDOFF: ALIFE Experiment 2 — The Stripe Test
**Project:** FAITHH ai-stack / projects/alife/  
**Prerequisite commit:** Experiment 1 complete (Shield fixation confirmed)  
**Author:** Jonathan + Claude  
**Date:** March 2026

---

## Context & Lessons From Experiment 1

Experiment 1 confirmed selection pressure works. Key lessons that 
directly shape Experiment 2 design:

1. **Severe bottlenecks cause fixation** — waves killing 97% of 
   population eliminate variation and lock in whatever trait survives. 
   Experiment 2 waves must be selective not catastrophic. Target: 
   kill 8-12% of total population per wave, not 50%+.

2. **PREDATOR_DAMAGE=255 is too lethal** — use 120 for gradient kills.

3. **PREDATOR_WAVE_INTERVAL=2000** works well — keep this.

4. **Genome-based shield check is correct** — world.py already checks 
   genome directly, not shield_active flag. Keep this.

5. **Seeding strategies explicitly** works better than waiting for 
   mutation to produce them — mutation rates are too low for rare 
   trait emergence within experiment timeframes.

---

## Scientific Question

> When two simultaneous environmental pressures exist, does a 
> dual-purpose trait emerge that addresses both — or do two 
> single-purpose traits dominate?

**Real-world analog:** Zebra stripes address both predator motion 
tracking AND thermal regulation simultaneously. One trait, two 
survival functions.

---

## The Three Competing Strategies

| Strategy | Description | Genome Signature | Cost |
|---|---|---|---|
| A — Shield only | Blocks predator waves, no thermal protection | ACT_SHIELD in A1 | Low |
| B — Thermal avoidance | Moves to low-light cells, no predator protection | SENSE_LIGHT in S0, ACT_FLEE in A1 | Medium (movement) |
| C — Disruption (Stripe analog) | Addresses both pressures simultaneously | SENSE_LIGHT in S0, ACT_SHIELD in A1 | Medium (trait) |

**The hypothesis:** Under balanced dual pressure, Strategy C should 
reach higher frequency than either A or B alone.

---

## World Changes Required

### 1. Light Level Distribution (world.py)

Initialize cell light levels as a gradient — high in center, 
low at edges:

```python
def initialize_light_gradient(self):
    """
    Center cells have high light (thermal pressure).
    Edge cells have low light (thermal safety).
    Creates spatial pressure that rewards edge-seeking or 
    Disruption trait.
    """
    for x in range(self.width):
        for y in range(self.height):
            # Distance from center, normalized 0-1
            cx = abs(x - self.width // 2) / (self.width // 2)
            cy = abs(y - self.height // 2) / (self.height // 2)
            distance_from_center = min(1.0, (cx + cy) / 2)
            # Center = high light (255), edges = low light (50)
            self.cells[x][y].light = int(50 + (205 * (1 - distance_from_center)))
```

### 2. Thermal Drain (world.py or simulation.py)

Apply every tick, before genome execution:

```python
def apply_thermal_drain(self, agent):
    """
    Agents absorb heat from their current cell each tick.
    Disruption phenotype reduces absorption by 70%.
    """
    cell_light = self.get_cell_light(agent.x, agent.y)
    has_disruption = self.agent_has_disruption_phenotype(agent)
    
    base_drain = (cell_light / 255) * THERMAL_DRAIN_RATE
    
    if has_disruption:
        drain = base_drain * 0.3  # 70% reduction
    else:
        drain = base_drain
    
    return drain  # caller applies to agent.energy

def agent_has_disruption_phenotype(self, agent):
    """
    Disruption phenotype = SENSE_LIGHT in S0 or S1 
    AND ACT_SHIELD in A0 or A1.
    This is the dual-purpose strategy — thermal awareness 
    combined with predator defense.
    """
    has_light_sense = (agent.genome[0] == SENSE_LIGHT or 
                       agent.genome[1] == SENSE_LIGHT)
    has_shield = (agent.genome[5] == ACT_SHIELD or 
                  agent.genome[6] == ACT_SHIELD)
    return has_light_sense and has_shield
```

### 3. Predator Wave Calibration (config.py)

```python
PREDATOR_DAMAGE = 120          # survivable for high-energy agents
PREDATOR_WAVE_INTERVAL = 2000  # keep from Experiment 1
THERMAL_DRAIN_RATE = 3         # max drain per tick in high-light cell
```

**Expected behavior:**
- Agents with energy > 120 survive waves unshielded
- Agents with energy < 120 die on wave contact
- Shielded agents always survive waves
- Center-dwelling agents lose 2-3 extra energy/tick from thermal
- Disruption agents in center lose 0.6-0.9 extra energy/tick (70% reduction)

---

## Initial Population Seeding

Seed all three strategies explicitly. Do NOT use random genomes for 
all 50 agents — mutation rates are too low for strategy emergence 
within experiment timeframes.

```python
# Strategy A — Shield only (20 agents)
STRATEGY_A_GENOME = bytes([
    SENSE_ENERGY,    # S0 — sense energy
    SENSE_THREAT,    # S1 — sense threat
    PROC_THRESHOLD,  # P0 — threshold processing
    PROC_THRESHOLD,  # P1 — threshold processing
    MEM_NONE,        # M0 — no memory
    ACT_REPRODUCE,   # A0 — reproduce (always)
    ACT_SHIELD,      # A1 — shield only
    REG_NONE         # R0 — no regulation
])

# Strategy B — Thermal avoidance (15 agents)
STRATEGY_B_GENOME = bytes([
    SENSE_LIGHT,     # S0 — sense light/thermal
    SENSE_ENERGY,    # S1 — sense energy
    PROC_THRESHOLD,  # P0 — threshold processing
    PROC_COMPARE,    # P1 — compare values
    MEM_NONE,        # M0 — no memory
    ACT_REPRODUCE,   # A0 — reproduce (always)
    ACT_FLEE,        # A1 — flee from threat/heat
    REG_NONE         # R0 — no regulation
])

# Strategy C — Disruption/Stripe analog (15 agents)
STRATEGY_C_GENOME = bytes([
    SENSE_LIGHT,     # S0 — sense light/thermal (KEY DIFFERENCE)
    SENSE_THREAT,    # S1 — sense threat
    PROC_THRESHOLD,  # P0 — threshold processing
    PROC_COMPARE,    # P1 — compare values
    MEM_NONE,        # M0 — no memory
    ACT_REPRODUCE,   # A0 — reproduce (always)
    ACT_SHIELD,      # A1 — shield (addresses BOTH pressures)
    REG_NONE         # R0 — no regulation
])
```

---

## Experiment Runner: exp2_stripe.py

Structure mirrors exp1_pressure.py with additions:

```python
def run_experiment_2(ticks, log_interval):
    sim = Simulation(experiment=2)
    sim.world.initialize_light_gradient()
    
    # Seed all three strategies
    sim.seed_strategy(STRATEGY_A_GENOME, count=20)
    sim.seed_strategy(STRATEGY_B_GENOME, count=15)
    sim.seed_strategy(STRATEGY_C_GENOME, count=15)
    
    observer = PulseWatcher()
    
    for tick in range(ticks):
        # Apply thermal drain before genome execution
        for agent in sim.world.agents.values():
            drain = sim.world.apply_thermal_drain(agent)
            agent.energy -= drain
            if agent.energy <= 0:
                # Thermal death
                observer.log_event("thermal_death", agent, 
                                   sim.world, tick)
                sim.handle_agent_death(agent.id)
        
        # Apply predator wave
        if tick % PREDATOR_WAVE_INTERVAL == 0 and tick > 0:
            contacts = sim.world.trigger_predator_wave(tick)
            for agent_id, shielded in contacts:
                if not shielded:
                    agent = sim.world.agents.get(agent_id)
                    if agent:
                        agent.energy -= PREDATOR_DAMAGE
                        if agent.energy <= 0:
                            observer.log_event("death_predator", 
                                              agent, sim.world, tick)
                            sim.handle_agent_death(agent_id)
        
        # Normal tick
        sim.tick()
        
        # Log strategy distribution every log_interval
        if tick % log_interval == 0:
            log_strategy_distribution(sim, observer, tick)
    
    observer.close()
```

### Strategy Distribution Logging

Track all three strategies every log_interval ticks:

```python
def log_strategy_distribution(sim, observer, tick):
    total = len(sim.world.agents)
    if total == 0:
        return
    
    strategy_a = sum(1 for a in sim.world.agents.values() 
                     if has_shield(a) and not has_light_sense(a))
    strategy_b = sum(1 for a in sim.world.agents.values() 
                     if has_light_sense(a) and not has_shield(a))
    strategy_c = sum(1 for a in sim.world.agents.values() 
                     if has_shield(a) and has_light_sense(a))
    unspecialized = total - strategy_a - strategy_b - strategy_c
    
    pct_a = (strategy_a / total) * 100
    pct_b = (strategy_b / total) * 100
    pct_c = (strategy_c / total) * 100
    
    print(f"Tick {tick:6d}: pop={total:4d} | "
          f"A(Shield)={pct_a:.1f}% | "
          f"B(Thermal)={pct_b:.1f}% | "
          f"C(Disruption)={pct_c:.1f}%")
    
    # Log to FAITHH observer
    observer.log_strategy_snapshot(tick, pct_a, pct_b, pct_c, 
                                   total, sim.world)
```

---

## New FAITHH Observer Event Types

Add these three methods to faithh_observer.py:

### thermal_death
```
Document format:
"Agent [id] at generation [g] died at tick [t] from thermal drain. 
Occupied cells averaging light level [avg_light] for [lifetime] ticks 
without Disruption trait protection. Genome: [readable]. 
This agent was pursuing Strategy B (thermal avoidance) but thermal 
pressure exceeded its behavioral avoidance capacity. 
Lineage ends here."
```

### disruption_emergence  
```
Document format:
"Disruption phenotype confirmed in agent [id] at generation [g] 
tick [t]. Genome carries [SENSE_LIGHT] in S0 and ACT_SHIELD in A1 — 
addressing both predator and thermal pressure simultaneously. 
Current thermal drain reduction: 70%. Predator wave protection: full. 
This is Strategy C — the dual-purpose Stripe analog. 
Population Strategy C frequency at emergence: [pct]%."
```

### strategy_snapshot
```
Document format:
"Strategy distribution at tick [t] generation [g]:
Strategy A (Shield only): [pct_a]% — predator defense, 
  thermal vulnerable.
Strategy B (Thermal avoidance): [pct_b]% — thermal adapted, 
  predator vulnerable.  
Strategy C (Disruption): [pct_c]% — dual-purpose protection.
Unspecialized: [pct_u]%.
Total population: [total].
Dominant pressure this interval: [predator/thermal/balanced].
[FAITHH prediction based on current trajectory]"
```

---

## Success Criteria

Experiment 2 passes under ANY of these three outcomes:

| Outcome | Description | Scientific Meaning |
|---|---|---|
| A — C dominates | Strategy C >50% when both pressures active | Dual-purpose advantage confirmed — Stripe result |
| B — Pressure switching | A dominates under high predator, B under high thermal, C under balance | Conditional dual-purpose advantage confirmed |
| C — Stable coexistence | All three strategies maintain stable frequencies | Polymorphic equilibrium — all strategies viable |

**Failure condition (only):** Population collapses before any 
strategy establishes. If this happens increase THERMAL_DRAIN_RATE 
to 1 (less thermal pressure) and report — do not tune further 
without human review.

---

## What NOT To Change Mid-Run

If population is stable but Strategy C isn't winning — that is 
a valid result, not a failure. Do not adjust pressure balance 
mid-experiment to force Strategy C to win. The science is in 
what actually happens, not in confirming the hypothesis.

---

## Verification Steps

**Step 1 — 5,000 tick quick check:**
Run for 5,000 ticks first. Confirm:
- All three strategies present in population
- Thermal drain is occurring (avg_energy lower than Exp 1)
- Predator waves are killing some but not all unshielded agents
- No immediate population collapse

If any of these fail, stop and report before running full experiment.

**Step 2 — Full 100,000 tick run:**
Run for 100,000 ticks (longer than Exp 1 — need time for 
strategy competition to play out).

Report every 5,000 ticks:
- Population
- Strategy A/B/C percentages
- Average energy
- Wave events

**Step 3 — Pressure removal test at tick 50,000:**
At tick 50,000 remove BOTH pressures simultaneously:
- Stop predator waves
- Set THERMAL_DRAIN_RATE = 0

Continue running to tick 100,000. Report whether strategy 
distribution changes after both pressures removed.

---

## Commit Instructions

After Step 1 passes verification, commit scaffold:
```
git commit -m "feat(alife): Experiment 2 scaffold — Stripe Test"
```

After full run completes:
```
git commit -m "feat(alife): Experiment 2 complete — [outcome]"
```

Report both commit hashes. Stop completely after Step 3. 
Do not begin Experiment 3 without human review of strategy data.

---

## What FAITHH Is Learning From This Experiment

By the end of Experiment 2, FAITHH's alife_lineage collection 
will contain semantic records of:
- Which strategies survive under which pressure combinations
- The moment dual-purpose traits emerge or fail to emerge
- The language of adaptive vs maladaptive specialization

This vocabulary — learned from simple agents under simple pressures — 
is what FAITHH will eventually apply to characterize her own 
specialist Navis as they develop. The Stripe Test isn't just 
about zebras. It's FAITHH learning what dual-purpose adaptation 
looks like from the inside.

---

*FAITHH ai-stack | ALIFE Experiment 2 Handoff | March 2026*  
*Prerequisite: Experiment 1 Shield fixation commit*
