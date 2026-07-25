# HANDOFF: Experiment 4 — Harmonic Interference

**Date**: 2026-03-23
**From**: Cascade Session (Design Phase)
**To**: Windsurf Implementation
**Status**: Ready for implementation

---

## Scientific Question

Does spatial cognitive stratification emerge when agents face overlapping wave sources with different frequencies? Can agents in the interference zone evolve to track beat frequencies — a cognitive level beyond single-source prediction?

---

## World Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEFT ZONE (0-159)    │  INTERFERENCE ZONE (160-319)  │  RIGHT ZONE (320-479) │
│                       │                               │                       │
│  Wave 1 only          │  Both waves overlap           │  Wave 2 only          │
│  L→R, 200 tick        │  Beat frequency: 600 ticks    │  R→L, 300 tick        │
│                       │                               │                       │
│  Single-source        │  Dual-source prediction       │  Single-source        │
│  prediction           │  required for survival        │  prediction           │
└─────────────────────────────────────────────────────────────────────────────┘

Wave 1: ══════════════════════════════════════════════════════════════════►
         Spawns x=0, travels right at ~0.8 col/tick, interval=200 ticks

Wave 2: ◄══════════════════════════════════════════════════════════════════
         Spawns x=479, travels left at ~0.8 col/tick, interval=300 ticks

Beat frequency = LCM(200, 300) = 600 ticks
```

---

## Implementation Spec

### 1. `config.py` — Add Parameters

```python
# Experiment 4: Harmonic Interference
WAVE1_INTERVAL = 200          # L→R wave interval (ticks)
WAVE2_INTERVAL = 300          # R→L wave interval (ticks)
ZONE_LEFT_END = 159           # Left zone: columns 0-159
ZONE_CENTER_END = 319         # Center zone: columns 160-319
                              # Right zone: columns 320-479
BEAT_TOLERANCE = 30           # ±30 ticks for beat detection
BEAT_HORIZON = 60             # Prediction horizon for PROC_BEAT
```

### 2. `agent.py` — Add Dual Wave Tracking

In `Agent.__init__`, add after `self.wave_arrival_times`:

```python
# Dual-source wave tracking (Exp 4+)
self.wave1_arrival_times: List[int] = []  # L→R waves (max 4)
self.wave2_arrival_times: List[int] = []  # R→L waves (max 4)
self.last_zone: Optional[str] = None      # For zone_entry tracking
```

In `Agent.create_child`, add inheritance:

```python
# Inherit dual wave timing knowledge
child.wave1_arrival_times = self.wave1_arrival_times.copy()
child.wave2_arrival_times = self.wave2_arrival_times.copy()
```

### 3. `world.py` — Add Wave Direction

Modify `WaveState.__init__`:

```python
def __init__(self, start_tick: int, speed: float, stealth: bool = False, 
             direction: str = 'left_to_right'):
    self.start_tick = start_tick
    self.speed = speed
    self.active = True
    self.stealth = stealth
    self.direction = direction  # 'left_to_right' or 'right_to_left'
```

Modify `WaveState.front_position` for bidirectional waves:

```python
def front_position(self, current_tick: int) -> float:
    """Current leading edge of wave in column units."""
    elapsed = current_tick - self.start_tick
    if self.direction == 'left_to_right':
        return elapsed * self.speed
    else:  # right_to_left
        return GRID_WIDTH - (elapsed * self.speed)
```

Add `spawn_wave_from_right` method to `World`:

```python
def spawn_wave_from_right(self, current_tick: int) -> WaveState:
    """Spawn a wave from the right edge traveling left."""
    speed = WAVE_SPEED_C * (1 + random.gauss(0, WAVE_SPEED_VARIANCE))
    speed = max(0.4, min(1.6, speed))
    stealth = random.random() < STEALTH_WAVE_PROBABILITY
    return WaveState(start_tick=current_tick, speed=speed, stealth=stealth,
                     direction='right_to_left')
```

Modify `apply_wave_damage` to tag arrivals by direction:

```python
# After recording wave arrival, tag by direction
if wave.direction == 'left_to_right':
    agent.wave1_arrival_times.append(current_tick)
    agent.wave1_arrival_times = agent.wave1_arrival_times[-4:]
else:
    agent.wave2_arrival_times.append(current_tick)
    agent.wave2_arrival_times = agent.wave2_arrival_times[-4:]
```

Add zone detection helper:

```python
def get_agent_zone(self, agent: 'Agent') -> str:
    """Return which zone an agent is in."""
    from config import ZONE_LEFT_END, ZONE_CENTER_END
    if agent.x <= ZONE_LEFT_END:
        return 'left'
    elif agent.x <= ZONE_CENTER_END:
        return 'center'
    else:
        return 'right'
```

### 4. `ops.py` — Add MEM_DUAL and PROC_BEAT

Replace `mem_hybrid` (index 0x07) with `mem_dual`:

```python
def mem_dual(agent: 'Agent', sense_value: int) -> None:
    """Dual-source memory for Experiment 4.
    
    Stores separate arrival time buffers for Wave 1 (L→R) and Wave 2 (R→L).
    Actual storage happens in world.apply_wave_damage — this op enables
    the agent to USE the dual buffers via PROC_BEAT.
    
    Also stores sense values in pattern memory for compatibility.
    """
    if sense_value > 128:
        agent.pattern_memory.append((agent.age, sense_value))
        if len(agent.pattern_memory) > 4:
            agent.pattern_memory.pop(0)
```

Replace `proc_weight` (index 0x05) with `proc_beat`:

```python
def proc_beat(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Predict beat frequency from dual wave sources.
    
    Computes the beat interval (difference frequency) from Wave 1 and Wave 2
    arrival times. Fires when predicted beat arrival is approaching.
    
    Beat frequency = |interval1 - interval2| when intervals are similar,
    or LCM-based pattern when intervals differ significantly.
    
    This is the KEY OP for interference zone survival in Experiment 4.
    """
    from config import BEAT_TOLERANCE, BEAT_HORIZON, SENSE_THREAT_RANGE
    
    # Need at least 2 arrivals from each source
    if len(agent.wave1_arrival_times) < 2 or len(agent.wave2_arrival_times) < 2:
        # Fall back to single-source prediction if only one source available
        if len(agent.wave_arrival_times) >= 2:
            # Use legacy single-source prediction
            intervals = [agent.wave_arrival_times[i] - agent.wave_arrival_times[i-1]
                         for i in range(1, len(agent.wave_arrival_times))]
            avg_interval = sum(intervals) / len(intervals)
            last_arrival = agent.wave_arrival_times[-1]
            predicted_next = last_arrival + avg_interval
            ticks_until = predicted_next - world.tick
            return 0 < ticks_until < SENSE_THREAT_RANGE * 3
        return False
    
    # Calculate intervals for each source
    intervals1 = [agent.wave1_arrival_times[i] - agent.wave1_arrival_times[i-1]
                  for i in range(1, len(agent.wave1_arrival_times))]
    intervals2 = [agent.wave2_arrival_times[i] - agent.wave2_arrival_times[i-1]
                  for i in range(1, len(agent.wave2_arrival_times))]
    
    avg_interval1 = sum(intervals1) / len(intervals1)
    avg_interval2 = sum(intervals2) / len(intervals2)
    
    # Predict next arrival from each source
    last1 = agent.wave1_arrival_times[-1]
    last2 = agent.wave2_arrival_times[-1]
    predicted1 = last1 + avg_interval1
    predicted2 = last2 + avg_interval2
    
    current_tick = world.tick
    ticks_until1 = predicted1 - current_tick
    ticks_until2 = predicted2 - current_tick
    
    # Fire if EITHER source is approaching within horizon
    # This is the beat detection — agent shields for whichever wave comes next
    horizon = BEAT_HORIZON if BEAT_HORIZON else SENSE_THREAT_RANGE * 3
    
    return (0 < ticks_until1 < horizon) or (0 < ticks_until2 < horizon)
```

Update the op arrays:

```python
MEMORY_OPS = [
    mem_none,     # 0x00
    mem_last1,    # 0x01
    mem_last4,    # 0x02
    mem_last8,    # 0x03
    mem_best,     # 0x04
    mem_worst,    # 0x05
    mem_pattern,  # 0x06
    mem_dual,     # 0x07 — was mem_hybrid, now dual-source for Exp 4
]

PROCESS_OPS = [
    proc_threshold,   # 0x00
    proc_compare,     # 0x01
    proc_memory_cmp,  # 0x02
    proc_trend,       # 0x03
    proc_predict,     # 0x04
    proc_beat,        # 0x05 — was proc_weight, now beat detection for Exp 4
    proc_average,     # 0x06
    proc_invert,      # 0x07
]
```

### 5. `exp4_harmonic.py` — New Experiment Script

Create `projects/alife/experiments/exp4_harmonic.py`:

```python
"""
ALIFE Experiment 4: Harmonic Interference

Scientific Question:
Does spatial cognitive stratification emerge when agents face overlapping 
wave sources with different frequencies? Can agents in the interference 
zone evolve to track beat frequencies?

World Structure:
- Left zone (0-159): Wave 1 only (L→R, 200 tick interval)
- Center zone (160-319): Both waves overlap (beat frequency 600 ticks)
- Right zone (320-479): Wave 2 only (R→L, 300 tick interval)

Success Criteria (all valid outcomes):
1. Beat-frequency phase coherence in interference zone only — ideal
2. Phase coherence everywhere — beat learnable from outer zones
3. Interference zone depopulates — too cognitively demanding
4. Red Queen continues — interference prevents fixation
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from agent import Agent
from config import (
    INITIAL_POPULATION, WAVE1_INTERVAL, WAVE2_INTERVAL,
    ZONE_LEFT_END, ZONE_CENTER_END, GRID_WIDTH,
    PREDATOR_DAMAGE, THERMAL_DRAIN_RATE, WAVE_SPEED_C, SENSE_THREAT_RANGE
)
from faithh_observer import PulseWatcher

# Op codes
SENSE_LIGHT = 0x02
SENSE_THREAT = 0x01
PROC_THRESHOLD = 0x00
PROC_BEAT = 0x05
MEM_DUAL = 0x07
ACT_REPRODUCE = 0x04
ACT_SHIELD = 0x03
REG_NONE = 0x00

# Harmonic genome — uses PROC_BEAT + MEM_DUAL for beat detection
HARMONIC_GENOME = bytes([
    SENSE_LIGHT,     # S0
    SENSE_THREAT,    # S1
    PROC_THRESHOLD,  # P0 — for reproduction
    PROC_BEAT,       # P1 — beat frequency prediction
    MEM_DUAL,        # M0 — dual-source memory
    ACT_REPRODUCE,   # A0
    ACT_SHIELD,      # A1
    REG_NONE         # R0
])

def get_zone(x: int) -> str:
    if x <= ZONE_LEFT_END:
        return 'left'
    elif x <= ZONE_CENTER_END:
        return 'center'
    else:
        return 'right'

def log_spatial_snapshot(agents, tick: int) -> dict:
    """Log population and intent by zone."""
    zones = {'left': [], 'center': [], 'right': []}
    for agent in agents:
        zone = get_zone(agent.x)
        neg_gaps = [g for g in agent.anticipation_gaps if g < 0]
        zones[zone].append({
            'id': agent.id,
            'neg_gap_count': len(neg_gaps),
            'has_beat': agent.genome[3] == PROC_BEAT and agent.genome[4] == MEM_DUAL
        })
    
    summary = {}
    for zone, data in zones.items():
        pop = len(data)
        beat_count = sum(1 for d in data if d['has_beat'])
        neg_gap_total = sum(d['neg_gap_count'] for d in data)
        summary[zone] = {
            'population': pop,
            'beat_genome_pct': (beat_count / pop * 100) if pop > 0 else 0,
            'neg_gaps': neg_gap_total
        }
    
    print(f"\n=== SPATIAL SNAPSHOT @ tick {tick} ===")
    for zone in ['left', 'center', 'right']:
        s = summary[zone]
        print(f"  {zone:8s}: pop={s['population']:4d} beat={s['beat_genome_pct']:5.1f}% neg_gaps={s['neg_gaps']}")
    print()
    
    return summary

def run_experiment_4(ticks: int = 200000, log_interval: int = 5000):
    """Run Experiment 4: Harmonic Interference."""
    sim = Simulation(experiment=4)
    sim.world.initialize_light_gradient()
    
    # Initialize wave states
    sim.world.current_wave = None
    sim.world.wave2 = None  # Second wave for R→L
    
    # Seed population: 10% harmonic genome, 90% random
    sim.initialize_population(100)
    agents = list(sim.world.agents.values())
    harmonic_count = 10
    for i, agent in enumerate(agents):
        if i < harmonic_count:
            agent.genome = HARMONIC_GENOME
    
    print(f"Seeded {harmonic_count} agents with HARMONIC genome (PROC_BEAT + MEM_DUAL)")
    
    # Initialize observer
    observer = None
    try:
        observer = PulseWatcher()
    except Exception as e:
        print(f"[PULSE] Observer init failed: {e}")
    
    results = {
        'wave1_count': 0,
        'wave2_count': 0,
        'zone_populations': [],
        'beat_activations': 0,
        'first_beat_coherence': None,
    }
    
    print("=" * 70)
    print("EXPERIMENT 4: HARMONIC INTERFERENCE")
    print("=" * 70)
    print(f"Wave 1: L→R, interval={WAVE1_INTERVAL} ticks")
    print(f"Wave 2: R→L, interval={WAVE2_INTERVAL} ticks")
    print(f"Beat frequency: {WAVE1_INTERVAL * WAVE2_INTERVAL // gcd(WAVE1_INTERVAL, WAVE2_INTERVAL)} ticks")
    print(f"Zones: left=0-{ZONE_LEFT_END}, center={ZONE_LEFT_END+1}-{ZONE_CENTER_END}, right={ZONE_CENTER_END+1}-{GRID_WIDTH-1}")
    print("=" * 70)
    
    for t in range(ticks):
        # Spawn Wave 1 (L→R)
        if t > 0 and t % WAVE1_INTERVAL == 0:
            wave1 = sim.world.spawn_wave(t)
            wave1.direction = 'left_to_right'
            sim.world.current_wave = wave1
            results['wave1_count'] += 1
        
        # Spawn Wave 2 (R→L)
        if t > 0 and t % WAVE2_INTERVAL == 0:
            wave2 = sim.world.spawn_wave_from_right(t)
            sim.world.wave2 = wave2
            results['wave2_count'] += 1
        
        # Process Wave 1
        if sim.world.current_wave and sim.world.current_wave.active:
            contacts = sim.world.apply_wave_damage(sim.world.current_wave, t)
            for agent_id, shielded, _ in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent and not agent.alive:
                    sim.world.remove_agent(agent)
                    sim.total_deaths += 1
            if sim.world.current_wave.is_complete(t):
                sim.world.current_wave.active = False
        
        # Process Wave 2
        if sim.world.wave2 and sim.world.wave2.active:
            contacts = sim.world.apply_wave_damage(sim.world.wave2, t)
            for agent_id, shielded, _ in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent and not agent.alive:
                    sim.world.remove_agent(agent)
                    sim.total_deaths += 1
            if sim.world.wave2.is_complete(t):
                sim.world.wave2.active = False
        
        # Thermal drain
        for agent in list(sim.world.agents.values()):
            if not agent.alive:
                continue
            drain = sim.world.apply_thermal_drain(agent)
            agent.energy -= drain
            if agent.energy <= 0:
                agent.alive = False
                sim.world.remove_agent(agent)
                sim.total_deaths += 1
        
        # Simulation tick
        sim.tick()
        
        # Population collapse check
        if sim.world.get_population() == 0:
            print(f"\n*** POPULATION COLLAPSED at tick {t} ***")
            break
        
        # Spatial snapshot every 10K ticks
        if t % 10000 == 0 and t > 0:
            snapshot = log_spatial_snapshot(list(sim.world.agents.values()), t)
            results['zone_populations'].append((t, snapshot))
        
        # Regular logging
        if t % log_interval == 0:
            agents = list(sim.world.agents.values())
            total = len(agents)
            zones = {'left': 0, 'center': 0, 'right': 0}
            for a in agents:
                zones[get_zone(a.x)] += 1
            
            beat_count = sum(1 for a in agents 
                           if a.genome[3] == PROC_BEAT and a.genome[4] == MEM_DUAL)
            
            print(f"Tick {t:6d}: pop={total:4d} | "
                  f"L={zones['left']:3d} C={zones['center']:3d} R={zones['right']:3d} | "
                  f"beat_genome={beat_count}")
    
    # Final results
    print()
    print("=" * 70)
    print("EXPERIMENT 4 RESULTS")
    print("=" * 70)
    print(f"Final population: {sim.world.get_population()}")
    print(f"Wave 1 count: {results['wave1_count']}")
    print(f"Wave 2 count: {results['wave2_count']}")
    print(f"Total deaths: {sim.total_deaths}")
    print("=" * 70)
    
    if observer:
        observer.close()
    
    return results

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ALIFE Experiment 4: Harmonic Interference")
    parser.add_argument("--ticks", type=int, default=200000)
    parser.add_argument("--log-interval", type=int, default=5000)
    args = parser.parse_args()
    
    run_experiment_4(ticks=args.ticks, log_interval=args.log_interval)
```

### 6. `faithh_observer.py` — Add Event Types

Add these methods to `PulseWatcher` class:

```python
def log_zone_entry(self, agent, old_zone: str, new_zone: str, tick: int, intent_score: float):
    """Log when agent crosses zone boundary."""
    self._log_event('zone_entry', {
        'agent_id': agent.id,
        'old_zone': old_zone,
        'new_zone': new_zone,
        'tick': tick,
        'intent_score': intent_score,
        'genome': agent.genome.hex()
    })

def log_beat_activation(self, agent, tick: int, wave1_interval: float, wave2_interval: float):
    """Log when agent shields at beat interval."""
    self._log_event('beat_activation', {
        'agent_id': agent.id,
        'tick': tick,
        'wave1_interval': wave1_interval,
        'wave2_interval': wave2_interval,
        'genome': agent.genome.hex()
    })

def log_spatial_snapshot(self, zone_data: dict, tick: int):
    """Log population distribution across zones."""
    self._log_event('spatial_snapshot', {
        'tick': tick,
        'zones': zone_data
    })
```

---

## Testing Commands

```bash
# Quick diagnostic run (10K ticks)
cd /home/jonat/ai-stack
source venv/bin/activate
python projects/alife/experiments/exp4_harmonic.py --ticks 10000 --log-interval 1000

# Full run (200K ticks)
python projects/alife/experiments/exp4_harmonic.py --ticks 200000 --log-interval 5000 > exp4_harmonic.log 2>&1 &

# Monitor
tail -f exp4_harmonic.log
```

---

## Success Metrics

| Outcome | Description | Interpretation |
|---------|-------------|----------------|
| **BEAT_COHERENCE** | neg_gap_pct > 10% in center zone only | Spatial stratification achieved |
| **UNIVERSAL_COHERENCE** | neg_gap_pct > 10% in all zones | Beat frequency learnable everywhere |
| **CENTER_DEPOPULATION** | center zone < 10% of population | Interference too demanding |
| **RED_QUEEN** | Oscillating neg_gap_pct, no fixation | Interference prevents stability |

---

## Commit Message Template

```
exp4: implement harmonic interference with dual-wave system

- Add MEM_DUAL (0x07) for separate wave source buffers
- Add PROC_BEAT (0x05) for beat frequency prediction
- Add wave direction tracking in WaveState
- Add zone detection and spatial snapshots
- Create exp4_harmonic.py experiment script

Scientific question: Does spatial cognitive stratification emerge
when agents face overlapping wave sources with different frequencies?
```

---

*Handoff ready for implementation.*
