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
    ZONE_LEFT_END, ZONE_CENTER_END, GRID_WIDTH, GRID_HEIGHT,
    PREDATOR_DAMAGE, THERMAL_DRAIN_RATE, WAVE_SPEED_C, SENSE_THREAT_RANGE,
    EXP4_WAVE_SPEED, ENERGY_SOURCE_RADIUS
)
import random as _random

# FAITHH-designed environmental parameters
CENTER_BONUS_SOURCES = 10        # Extra energy hotspots in center zone
SIDE_PRESSURE_START = 2000       # Tick when side-zone thermal drain begins ramping
SIDE_PRESSURE_FULL = 10000       # Tick when side-zone drain reaches max multiplier
SIDE_DRAIN_MAX_MULTIPLIER = 3.0  # Max thermal drain multiplier for side zones

# Try to import FAITHH observer
try:
    from faithh_observer import PulseWatcher
    FAITHH_AVAILABLE = True
except ImportError:
    FAITHH_AVAILABLE = False

# Op codes
SENSE_LIGHT = 0x02
SENSE_THREAT = 0x01
PROC_THRESHOLD = 0x00
PROC_BEAT = 0x05
PROC_PREDICT = 0x04
MEM_DUAL = 0x07
MEM_PATTERN = 0x06
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

# Strategy C genome (from Exp 3) — single-source prediction
STRATEGY_C_GENOME = bytes([
    SENSE_LIGHT,     # S0
    SENSE_THREAT,    # S1
    PROC_THRESHOLD,  # P0
    PROC_PREDICT,    # P1 — single-source prediction
    MEM_PATTERN,     # M0
    ACT_REPRODUCE,   # A0
    ACT_SHIELD,      # A1
    REG_NONE         # R0
])


def gcd(a: int, b: int) -> int:
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


def get_zone(x: int) -> str:
    """Return which zone a column is in."""
    if x <= ZONE_LEFT_END:
        return 'left'
    elif x <= ZONE_CENTER_END:
        return 'center'
    else:
        return 'right'


def has_beat_genome(agent) -> bool:
    """Check if agent has PROC_BEAT + MEM_DUAL."""
    return agent.genome[3] == PROC_BEAT and agent.genome[4] == MEM_DUAL


def has_shield(agent) -> bool:
    """Check if agent has Shield trait."""
    return agent.genome[5] == ACT_SHIELD or agent.genome[6] == ACT_SHIELD


def log_spatial_snapshot(agents, tick: int) -> dict:
    """Log population and intent by zone."""
    zones = {'left': [], 'center': [], 'right': []}
    
    for agent in agents:
        zone = get_zone(agent.x)
        neg_gaps = [g for g in agent.anticipation_gaps if g < 0]
        zones[zone].append({
            'id': agent.id,
            'neg_gap_count': len(neg_gaps),
            'has_beat': has_beat_genome(agent),
            'has_shield': has_shield(agent)
        })
    
    summary = {}
    for zone, data in zones.items():
        pop = len(data)
        beat_count = sum(1 for d in data if d['has_beat'])
        shield_count = sum(1 for d in data if d['has_shield'])
        neg_gap_total = sum(d['neg_gap_count'] for d in data)
        summary[zone] = {
            'population': pop,
            'beat_genome_pct': (beat_count / pop * 100) if pop > 0 else 0,
            'shield_pct': (shield_count / pop * 100) if pop > 0 else 0,
            'neg_gaps': neg_gap_total
        }
    
    print(f"\n{'='*60}")
    print(f"SPATIAL SNAPSHOT @ tick {tick}")
    print(f"{'='*60}")
    for zone in ['left', 'center', 'right']:
        s = summary[zone]
        print(f"  {zone:8s}: pop={s['population']:4d} | "
              f"beat={s['beat_genome_pct']:5.1f}% shield={s['shield_pct']:5.1f}% | "
              f"neg_gaps={s['neg_gaps']}")
    print()
    
    return summary


def run_experiment_4(ticks: int = 200000, log_interval: int = 5000):
    """
    Run Experiment 4: Harmonic Interference.
    
    Tests whether spatial cognitive stratification emerges when agents
    face overlapping wave sources with different frequencies.
    """
    sim = Simulation(experiment=4)
    sim.world.initialize_light_gradient()
    
    # FAITHH design: Center zone ecological richness
    # Add extra energy sources in the center zone (cols 160-319)
    # This makes the interference zone worth the risk — like a fertile river delta
    for _ in range(CENTER_BONUS_SOURCES):
        cx = _random.randint(ZONE_LEFT_END + 1, ZONE_CENTER_END)
        cy = _random.randint(0, GRID_HEIGHT - 1)
        sim.world.energy_sources.append((cx, cy))
    print(f"Added {CENTER_BONUS_SOURCES} bonus energy sources to center zone")
    
    # Initialize wave states
    sim.world.current_wave = None
    sim.world.wave2 = None  # Second wave for R→L
    
    # Seed population: 15% harmonic genome, 85% Strategy C
    # Use 200 agents for better zone coverage
    sim.initialize_population(200)
    agents = list(sim.world.agents.values())
    harmonic_count = 30
    for i, agent in enumerate(agents):
        if i < harmonic_count:
            agent.genome = HARMONIC_GENOME[:]
        else:
            agent.genome = STRATEGY_C_GENOME[:]
    
    # Option B: Pre-seed wave arrival times on harmonic-genome agents
    # Solves cold-start problem — PROC_BEAT needs 2+ arrivals from each source
    # This simulates inherited timing instinct from parent generation
    # Critical: predictions use last_arrival + avg_interval, so seed values
    # must predict the ACTUAL first wave arrivals (tick 600 for W1, tick 900 for W2)
    for i, agent in enumerate(agents):
        if i < harmonic_count:
            agent.wave1_arrival_times = [
                -WAVE1_INTERVAL, 0  # interval=600, predicts next at tick 600
            ]
            agent.wave2_arrival_times = [
                -WAVE2_INTERVAL, 0  # interval=900, predicts next at tick 900
            ]
            agent.wave_arrival_times = [
                -WAVE1_INTERVAL, -WAVE2_INTERVAL, 0
            ]
    
    print(f"Seeded {harmonic_count} agents with HARMONIC genome (PROC_BEAT + MEM_DUAL)")
    print(f"  Pre-seeded with wave timing instinct: W1 interval~{WAVE1_INTERVAL}, W2 interval~{WAVE2_INTERVAL}")
    print(f"Seeded {len(agents) - harmonic_count} agents with Strategy C genome (PROC_PREDICT)")
    
    # Initialize observer
    observer = None
    if FAITHH_AVAILABLE:
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
        'predator_kills': 0,
        'thermal_deaths': 0,
    }
    
    # Tracking variables
    first_negative_gap = None
    
    # Calculate beat frequency
    beat_frequency = (WAVE1_INTERVAL * WAVE2_INTERVAL) // gcd(WAVE1_INTERVAL, WAVE2_INTERVAL)
    
    print()
    print("=" * 70)
    print("EXPERIMENT 4: HARMONIC INTERFERENCE")
    print("=" * 70)
    print(f"Wave 1: L→R, interval={WAVE1_INTERVAL} ticks")
    print(f"Wave 2: R→L, interval={WAVE2_INTERVAL} ticks")
    print(f"Beat frequency: {beat_frequency} ticks (LCM)")
    print(f"Zones: left=0-{ZONE_LEFT_END}, center={ZONE_LEFT_END+1}-{ZONE_CENTER_END}, "
          f"right={ZONE_CENTER_END+1}-{GRID_WIDTH-1}")
    print(f"Running for {ticks} ticks, logging every {log_interval} ticks")
    print("=" * 70)
    print()
    
    for t in range(ticks):
        # Spawn Wave 1 (L→R) — add to active list, don't replace
        if t > 0 and t % WAVE1_INTERVAL == 0:
            wave1 = sim.world.spawn_wave(t)
            wave1.stealth = False  # Exp 4: all waves detectable (agents need timing data)
            if EXP4_WAVE_SPEED is not None:
                wave1.speed = EXP4_WAVE_SPEED
            sim.world.active_waves.append(wave1)
            results['wave1_count'] += 1
        
        # Spawn Wave 2 (R→L) — add to active list, don't replace
        if t > 0 and t % WAVE2_INTERVAL == 0:
            wave2 = sim.world.spawn_wave_from_right(t)
            wave2.stealth = False  # Exp 4: all waves detectable
            if EXP4_WAVE_SPEED is not None:
                wave2.speed = EXP4_WAVE_SPEED
            sim.world.active_waves.append(wave2)
            results['wave2_count'] += 1
            print(f"[WAVE2 SPAWN] tick={t} wave2 spawned")
        
        # Process ALL active waves
        for wave in sim.world.active_waves[:]:  # copy list for safe removal
            if not wave.active:
                sim.world.active_waves.remove(wave)
                continue
            
            # Check wave detection for anticipation gap tracking
            neg_gaps_w = sim.check_wave_detection(wave, t, observer)
            for agent, gap in neg_gaps_w:
                if first_negative_gap is None:
                    first_negative_gap = (t, agent.id, gap)
                    print(f"\n*** FIRST NEGATIVE GAP: {agent.id} gap={gap} at tick {t} "
                          f"gen={agent.generation:.0f} zone={get_zone(agent.x)} ***")
                    print(f"*** INTENT EMERGENCE CONFIRMED ***\n")
            
            contacts = sim.world.apply_wave_damage(wave, t)
            for agent_id, shielded, _ in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent and not agent.alive:
                    results['predator_kills'] += 1
                    sim.world.remove_agent(agent)
                    sim.total_deaths += 1
            if wave.is_complete(t):
                wave.active = False
                sim.world.active_waves.remove(wave)
        
        # Thermal drain with FAITHH-designed gradual side-zone pressure
        # After warm-up period, side zones become progressively harder,
        # creating natural incentive to occupy center (where PROC_BEAT helps)
        if t >= SIDE_PRESSURE_START:
            ramp = min(1.0, (t - SIDE_PRESSURE_START) / (SIDE_PRESSURE_FULL - SIDE_PRESSURE_START))
            side_multiplier = 1.0 + (SIDE_DRAIN_MAX_MULTIPLIER - 1.0) * ramp
        else:
            side_multiplier = 1.0
        
        for agent in list(sim.world.agents.values()):
            if not agent.alive:
                continue
            drain = sim.world.apply_thermal_drain(agent)
            # Apply zone-based multiplier
            zone = get_zone(agent.x)
            if zone != 'center':
                drain = drain * side_multiplier
            agent.energy -= drain
            if agent.energy <= 0:
                agent.alive = False
                results['thermal_deaths'] += 1
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
        
        # Debug output at tick 3000 for beat-genome agent arrival buffers
        if t == 3000:
            beat_agents = [a for a in sim.world.agents.values() if has_beat_genome(a)]
            print(f"\n*** DEBUG: Beat-Genome Agent Wave Arrival Buffers at tick {t} ***")
            for i, agent in enumerate(beat_agents[:3]):  # First 3 beat-genome agents
                print(f"Agent {agent.id}:")
                print(f"  wave1_arrival_times: {agent.wave1_arrival_times}")
                print(f"  wave2_arrival_times: {agent.wave2_arrival_times}")
                print(f"  wave_arrival_times: {agent.wave_arrival_times}")
            print("*** END DEBUG ***\n")
        
        # Regular logging
        if t % log_interval == 0:
            agents = list(sim.world.agents.values())
            total = len(agents)
            zones = {'left': 0, 'center': 0, 'right': 0}
            for a in agents:
                zones[get_zone(a.x)] += 1
            
            beat_agents = [a for a in agents if has_beat_genome(a)]
            predict_agents = [a for a in agents if not has_beat_genome(a)]
            beat_count = len(beat_agents)
            shield_count = sum(1 for a in agents if has_shield(a))
            
            # PRIMARY METRIC: genome fitness comparison (avg energy)
            beat_avg_e = (sum(a.energy for a in beat_agents) / beat_count) if beat_count > 0 else 0
            pred_avg_e = (sum(a.energy for a in predict_agents) / len(predict_agents)) if predict_agents else 0
            
            # Count agents with at least one negative gap (per-agent metric)
            agents_with_neg_gap = sum(1 for a in agents if any(g < 0 for g in a.anticipation_gaps))
            neg_gap_pct = (agents_with_neg_gap / total * 100) if total > 0 else 0
            
            print(f"Tick {t:6d}: pop={total:4d} | "
                  f"L={zones['left']:3d} C={zones['center']:3d} R={zones['right']:3d} | "
                  f"beat={beat_count:3d}(E={beat_avg_e:.0f}) pred={len(predict_agents)}(E={pred_avg_e:.0f}) | "
                  f"neg_gap={neg_gap_pct:.0f}%")
    
    # Final results
    final_agents = list(sim.world.agents.values())
    final_pop = len(final_agents)
    
    # Calculate final zone distribution
    final_zones = {'left': 0, 'center': 0, 'right': 0}
    for a in final_agents:
        final_zones[get_zone(a.x)] += 1
    
    # Calculate final beat genome prevalence by zone
    zone_beat_counts = {'left': 0, 'center': 0, 'right': 0}
    for a in final_agents:
        if has_beat_genome(a):
            zone_beat_counts[get_zone(a.x)] += 1
    
    print()
    print("=" * 70)
    print("EXPERIMENT 4 RESULTS")
    print("=" * 70)
    print(f"Final population:       {final_pop}")
    print(f"Wave 1 count:           {results['wave1_count']}")
    print(f"Wave 2 count:           {results['wave2_count']}")
    print(f"Predator kills:         {results['predator_kills']}")
    print(f"Thermal deaths:         {results['thermal_deaths']}")
    print(f"Total reproductions:    {sim.total_reproductions}")
    print(f"Total deaths:           {sim.total_deaths}")
    print()
    print("Zone Distribution:")
    for zone in ['left', 'center', 'right']:
        pop = final_zones[zone]
        beat = zone_beat_counts[zone]
        beat_pct = (beat / pop * 100) if pop > 0 else 0
        print(f"  {zone:8s}: pop={pop:4d} beat_genome={beat_pct:5.1f}%")
    print()
    
    # Determine outcome
    center_pop = final_zones['center']
    center_beat_pct = (zone_beat_counts['center'] / center_pop * 100) if center_pop > 0 else 0
    total_beat = sum(zone_beat_counts.values())
    total_beat_pct = (total_beat / final_pop * 100) if final_pop > 0 else 0
    
    if center_pop < final_pop * 0.1:
        outcome = "CENTER_DEPOPULATION"
    elif center_beat_pct > 50 and total_beat_pct < 30:
        outcome = "SPATIAL_STRATIFICATION"
    elif total_beat_pct > 30:
        outcome = "UNIVERSAL_BEAT_COHERENCE"
    else:
        outcome = "RED_QUEEN_CONTINUES"
    
    print(f"Outcome:                {outcome}")
    print("=" * 70)
    
    results['final_population'] = final_pop
    results['final_zones'] = final_zones
    results['outcome'] = outcome
    
    if observer:
        observer.close()
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ALIFE Experiment 4: Harmonic Interference")
    parser.add_argument("--ticks", type=int, default=200000, help="Number of ticks to run")
    parser.add_argument("--log-interval", type=int, default=5000, help="Logging interval")
    args = parser.parse_args()
    
    run_experiment_4(ticks=args.ticks, log_interval=args.log_interval)
