"""
ALIFE Experiment 3: The Anticipation Gap

Scientific Question:
Do agents develop genuine predictive behavior — modeling future threat states 
rather than reacting to current ones — when their survival depends on 
anticipating a wave they cannot yet sense?

The measurement instrument is the anticipation gap — the temporal distance 
between when a threat appears in an agent's SENSE range and when that agent 
activates its Shield.

  Positive gap = reactive    (Shield fires AFTER detection)
  Zero gap     = simultaneous
  Negative gap = ANTICIPATORY (Shield fires BEFORE detection)

A negative gap means the agent activated Shield before it could sense the 
threat. It modeled the future. That is the result this experiment is designed 
to detect.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from agent import Agent
from config import (
    INITIAL_POPULATION, PREDATOR_WAVE_INTERVAL, PREDATOR_DAMAGE,
    THERMAL_DRAIN_RATE, WAVE_SPEED_C, SENSE_THREAT_RANGE
)
from faithh_observer import PulseWatcher

# Op codes for genome construction
SENSE_ENERGY = 0x00
SENSE_THREAT = 0x01
SENSE_LIGHT = 0x02
SENSE_SELF = 0x05
PROC_THRESHOLD = 0x00
PROC_COMPARE = 0x01
PROC_PREDICT = 0x04
MEM_NONE = 0x00
MEM_PATTERN = 0x07
ACT_REPRODUCE = 0x04
ACT_SHIELD = 0x03
REG_NONE = 0x00

# Fixed genome for Experiment 3 (Strategy C — reactive)
# With process-action coupling: P0→A0, P1→A1
# P0 fires when own energy > 128 → reproduce when healthy
# P1 fires when threat > 128 → shield when wave approaches
# No continuous process firing when nothing is happening
SEEDED_GENOME = bytes([
    SENSE_SELF,      # S0 — own energy level → P0
    SENSE_THREAT,    # S1 — approaching wave (proximity) → P1
    PROC_THRESHOLD,  # P0 — fires when energy > 128 → A0
    PROC_THRESHOLD,  # P1 — fires when threat > 128 → A1
    MEM_NONE,        # M0 — starts here, can mutate
    ACT_REPRODUCE,   # A0 — reproduce when energy sufficient
    ACT_SHIELD,      # A1 — shield when wave detected
    REG_NONE         # R0 — no regulation
])

# Anticipatory genome for diagnostic seeding
# Uses PROC_PREDICT + MEM_PATTERN for predictive Shield activation
ANTICIPATORY_GENOME = bytes([
    SENSE_LIGHT,     # S0 — light gradient for positioning
    SENSE_THREAT,    # S1 — approaching wave → P1
    PROC_THRESHOLD,  # P0 — fires on light for reproduction
    PROC_PREDICT,    # P1 — prediction for shield (uses memory)
    MEM_PATTERN,     # M0 — stores threat timing patterns
    ACT_REPRODUCE,   # A0 — reproduce
    ACT_SHIELD,      # A1 — shield when prediction fires
    REG_NONE         # R0 — no regulation
])

# Memory op names for logging
MEM_OPS = ["MEM_NONE", "MEM_LAST1", "MEM_LAST4", "MEM_AVG", 
           "MEM_DELTA", "MEM_PEAK", "MEM_TREND", "MEM_PATTERN"]


def has_shield(agent) -> bool:
    """Check if agent has Shield trait in A0 or A1."""
    return agent.genome[5] == ACT_SHIELD or agent.genome[6] == ACT_SHIELD


def has_memory(agent) -> bool:
    """Check if agent has any memory op (M0 != MEM_NONE)."""
    return agent.genome[4] != MEM_NONE


def get_memory_op_name(agent) -> str:
    """Get the name of the agent's memory op."""
    return MEM_OPS[agent.genome[4]] if agent.genome[4] < len(MEM_OPS) else "UNKNOWN"


def is_constitutive_defender(agent) -> bool:
    """Check if agent has constitutive defense (PROC_INVERT on P1 with ACT_SHIELD on A1)."""
    PROC_INVERT = 0x07
    ACT_SHIELD = 0x03
    return agent.genome[3] == PROC_INVERT and agent.genome[6] == ACT_SHIELD


def log_experiment_3_state(sim, tick: int, first_negative_gap: tuple, 
                           current_wave, verify_waves: bool = False):
    """Log experiment state to console."""
    agents = list(sim.world.agents.values())
    total = len(agents)
    
    if total == 0:
        print(f"Tick {tick:6d}: POPULATION COLLAPSED")
        return None
    
    # Calculate statistics
    shield_count = sum(1 for a in agents if has_shield(a))
    mem_count = sum(1 for a in agents if has_memory(a))
    constitutive_count = sum(1 for a in agents if is_constitutive_defender(a))
    shield_pct = (shield_count / total) * 100
    mem_pct = (mem_count / total) * 100
    constitutive_pct = (constitutive_count / total) * 100
    
    # Calculate gap statistics (only wave-period activations)
    all_gaps = []
    neg_gaps_list = []
    best_gap = 0
    best_agent = None
    for agent in agents:
        if agent.anticipation_gaps:
            all_gaps.extend(agent.anticipation_gaps)
            for g in agent.anticipation_gaps:
                if g < 0:
                    neg_gaps_list.append(g)
                    if g < best_gap:
                        best_gap = g
                        best_agent = agent.id
    
    mean_gap = sum(all_gaps) / len(all_gaps) if all_gaps else 0
    min_gap = min(all_gaps) if all_gaps else 0
    neg_count = len(neg_gaps_list)
    neg_gap_pct = (neg_count / total) * 100 if total > 0 else 0
    mean_neg_gap = sum(neg_gaps_list) / len(neg_gaps_list) if neg_gaps_list else 0
    
    avg_energy = sum(a.energy for a in agents) / total
    avg_gen = sum(a.generation for a in agents) / total
    
    # Wave info for verification mode
    wave_info = ""
    if verify_waves and current_wave and current_wave.active:
        front = current_wave.front_position(tick)
        wave_info = f" | wave_front={front:.1f}"
    
    # Intent status
    intent_status = ""
    if first_negative_gap:
        intent_status = " [INTENT]"
    
    print(f"Tick {tick:6d}: pop={total:4d} | C={shield_pct:5.1f}% mem={mem_pct:5.1f}% const={constitutive_pct:4.1f}% | "
          f"mean_gap={mean_gap:+6.1f} min_gap={min_gap:+4.0f} neg_gaps={neg_count} ({neg_gap_pct:.1f}%)"
          f"{wave_info}{intent_status}")
    
    return {
        "total": total,
        "shield_pct": shield_pct,
        "mem_pct": mem_pct,
        "constitutive_pct": constitutive_pct,
        "mean_gap": mean_gap,
        "min_gap": min_gap,
        "neg_count": neg_count,
        "neg_gap_pct": neg_gap_pct,
        "mean_neg_gap": mean_neg_gap,
        "best_gap": best_gap,
        "best_agent": best_agent
    }


def run_experiment_3(ticks: int = 200000, log_interval: int = 5000, 
                     verify_waves: bool = False):
    """
    Run Experiment 3: The Anticipation Gap.
    
    Tests whether agents develop genuine predictive behavior under
    propagating wave pressure.
    
    Args:
        ticks: Number of ticks to run
        log_interval: How often to log state
        verify_waves: If True, log wave propagation details for verification
    
    Returns:
        dict with experiment results
    """
    sim = Simulation(experiment=3)
    
    # Initialize light gradient (keep from Exp 2)
    sim.world.initialize_light_gradient()
    sim.world.current_wave = None  # Initialize wave state for SENSE_THREAT
    
    # Seed 100 agents: 10 anticipatory + 90 Strategy C
    # Diagnostic: test if anticipatory genome produces negative gaps
    sim.initialize_population(100)
    agents = list(sim.world.agents.values())
    anticipatory_count = 10
    for i, agent in enumerate(agents):
        if i < anticipatory_count:
            agent.genome = ANTICIPATORY_GENOME
        else:
            agent.genome = SEEDED_GENOME
    
    print(f"Seeded {anticipatory_count} agents with ANTICIPATORY genome (PROC_PREDICT + MEM_PATTERN)")
    print(f"Seeded {len(agents) - anticipatory_count} agents with Strategy C genome (MEM_NONE)")
    
    # Initialize FAITHH PULSE observer
    observer = None
    try:
        observer = PulseWatcher()
    except Exception as e:
        print(f"[PULSE] Observer init failed (non-fatal): {e}")
    
    results = {
        'gap_curve': [],
        'population_curve': [],
        'memory_emergence_ticks': [],
        'first_negative_gap': None,
        'predator_wave_count': 0,
        'predator_kills': 0,
        'thermal_deaths': 0,
        'final_population': 0,
        'final_mean_gap': 0,
        'final_min_gap': 0,
        'final_memory_pct': 0,
        'success': False,
    }
    
    # Wave state
    current_wave = None
    first_negative_gap = None
    memory_emergence_count = 0
    
    # Intent threshold tracking
    intent_thresholds_crossed = {1: False, 5: False, 10: False, 25: False, 50: False}
    peak_neg_gap_pct = 0.0
    last_neg_gap_pct = 0.0
    
    print("=" * 70)
    print("EXPERIMENT 3: THE ANTICIPATION GAP")
    print("=" * 70)
    print(f"Initial population: {INITIAL_POPULATION}")
    print(f"Wave speed: {WAVE_SPEED_C} columns/tick")
    print(f"Sense threat range: {SENSE_THREAT_RANGE} columns")
    print(f"Predator wave interval: {PREDATOR_WAVE_INTERVAL} ticks")
    print(f"Predator damage: {PREDATOR_DAMAGE}")
    print(f"Thermal drain rate: {THERMAL_DRAIN_RATE}")
    print(f"Running for {ticks} ticks, logging every {log_interval} ticks")
    if verify_waves:
        print("*** WAVE VERIFICATION MODE ***")
    print("=" * 70)
    print()
    
    for t in range(ticks):
        # Spawn new wave on interval
        if t > 0 and t % PREDATOR_WAVE_INTERVAL == 0:
            current_wave = sim.world.spawn_wave(t)
            sim.world.current_wave = current_wave  # Make wave accessible to sense ops
            results['predator_wave_count'] += 1
            if verify_waves:
                stealth_tag = " [STEALTH]" if current_wave.stealth else ""
                print(f"  [WAVE] Spawned at tick {t}, speed={current_wave.speed:.3f}{stealth_tag}")
        
        # Process wave if active
        if current_wave and current_wave.active:
            # Check wave detection for all agents
            negative_gaps = sim.check_wave_detection(current_wave, t, observer)
            
            # Flag first negative gap
            for agent, gap in negative_gaps:
                if first_negative_gap is None:
                    first_negative_gap = (t, agent.id, gap)
                    results['first_negative_gap'] = first_negative_gap
                    print()
                    print(f"*** FIRST NEGATIVE GAP: {agent.id} gap={gap} at tick {t} gen={agent.generation:.0f} ***")
                    print(f"*** INTENT EMERGENCE CONFIRMED ***")
                    print()
                    
                    # Log to FAITHH
                    if observer:
                        try:
                            observer.flag_intent(agent, sim.world, t, gap, current_wave.speed)
                        except Exception:
                            pass
            
            # Apply wave damage at front position
            contacts = sim.world.apply_wave_damage(current_wave, t)
            
            # Process deaths
            for agent_id, shielded, warning_ticks in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent and not agent.alive:
                    results['predator_kills'] += 1
                    sim.world.remove_agent(agent)
                    sim.total_deaths += 1
            
            # Check if wave is complete
            if current_wave.is_complete(t):
                current_wave.active = False
                sim.world.current_wave = None  # Clear wave from world
                if verify_waves:
                    print(f"  [WAVE] Completed at tick {t}")
        
        # Apply thermal drain (keep from Exp 2)
        for agent in list(sim.world.agents.values()):
            if not agent.alive:
                continue
            drain = sim.world.apply_thermal_drain(agent)
            agent.energy -= drain
            if agent.energy <= 0:
                agent.energy = 0
                agent.alive = False
                results['thermal_deaths'] += 1
                sim.world.remove_agent(agent)
                sim.total_deaths += 1
        
        # Check for memory emergence through mutation
        for agent in sim.world.agents.values():
            if has_memory(agent) and not hasattr(agent, '_memory_logged'):
                agent._memory_logged = True
                memory_emergence_count += 1
                results['memory_emergence_ticks'].append(t)
                mem_op = get_memory_op_name(agent)
                print(f"*** MEMORY EMERGENCE: {agent.id} MEM_NONE→{mem_op} at tick {t} ***")
        
        # Normal simulation tick
        sim.tick()
        
        # Check for population collapse
        if sim.world.get_population() == 0:
            print(f"\n*** POPULATION COLLAPSED at tick {t} ***\n")
            break
        
        # Log gap snapshot every 1000 ticks
        if t % 1000 == 0 and observer:
            try:
                observer.log_gap_snapshot(sim.world.agents, sim.world, t, first_negative_gap)
            except Exception:
                pass
        
        # Log at interval
        if t % log_interval == 0:
            stats = log_experiment_3_state(sim, t, first_negative_gap, 
                                           current_wave, verify_waves)
            if stats:
                results['gap_curve'].append((t, stats['mean_gap'], stats['min_gap']))
                results['population_curve'].append((t, stats['total']))
                
                # Check intent threshold crossings
                current_neg_pct = stats['neg_gap_pct']
                if current_neg_pct > peak_neg_gap_pct:
                    peak_neg_gap_pct = current_neg_pct
                
                # Check for threshold crossings
                for threshold in [1, 5, 10, 25, 50]:
                    if current_neg_pct >= threshold and not intent_thresholds_crossed[threshold]:
                        intent_thresholds_crossed[threshold] = True
                        avg_gen = sum(a.generation for a in sim.world.agents.values()) / stats['total']
                        print(f"\n*** INTENT THRESHOLD: neg_gaps crossed {threshold}% at tick {t} gen {avg_gen:.1f} ***")
                        print(f"    Population: {stats['total']}")
                        print(f"    Mean gap (all agents): {stats['mean_gap']:+.1f}")
                        print(f"    Mean gap (anticipatory only): {stats['mean_neg_gap']:+.1f}")
                        print(f"    Best gap: {stats['best_gap']} ({stats['best_agent']})\n")
                
                # Check for intent regression
                if current_neg_pct < last_neg_gap_pct - 2.0 and last_neg_gap_pct > 5.0:
                    print(f"\n*** INTENT REGRESSION: neg_gaps dropped from {last_neg_gap_pct:.1f}% to {current_neg_pct:.1f}% at tick {t} ***")
                    print(f"    Possible causes: bottleneck, mutation drift, selection reversal\n")
                
                last_neg_gap_pct = current_neg_pct
    
    # Final results
    agents = list(sim.world.agents.values())
    results['final_population'] = len(agents)
    
    if len(agents) > 0:
        all_gaps = []
        for agent in agents:
            if agent.anticipation_gaps:
                all_gaps.extend(agent.anticipation_gaps)
        
        results['final_mean_gap'] = sum(all_gaps) / len(all_gaps) if all_gaps else 0
        results['final_min_gap'] = min(all_gaps) if all_gaps else 0
        results['final_memory_pct'] = sum(1 for a in agents if has_memory(a)) / len(agents) * 100
    
    # Determine success based on criteria from handoff
    if results['final_mean_gap'] < 0:
        results['success'] = True
        results['outcome'] = "FULL_SUCCESS"
    elif first_negative_gap:
        results['success'] = True
        results['outcome'] = "PARTIAL_SUCCESS"
    elif memory_emergence_count > 0:
        results['success'] = True
        results['outcome'] = "MEMORY_EMERGENCE_ONLY"
    elif results['final_population'] > 0:
        results['success'] = False
        results['outcome'] = "NO_MEMORY_EMERGENCE"
    else:
        results['success'] = False
        results['outcome'] = "POPULATION_COLLAPSED"
    
    # Print final results
    print()
    print("=" * 70)
    print("EXPERIMENT 3 RESULTS")
    print("=" * 70)
    print(f"Final population:       {results['final_population']}")
    print(f"Predator waves:         {results['predator_wave_count']}")
    print(f"Predator kills:         {results['predator_kills']}")
    print(f"Thermal deaths:         {results['thermal_deaths']}")
    print(f"Total reproductions:    {sim.total_reproductions}")
    print(f"Total deaths:           {sim.total_deaths}")
    print()
    print(f"Final mean gap:         {results['final_mean_gap']:+.1f} ticks")
    print(f"Final min gap:          {results['final_min_gap']:+.1f} ticks")
    print(f"Final memory %:         {results['final_memory_pct']:.1f}%")
    print(f"Memory emergences:      {memory_emergence_count}")
    print()
    if first_negative_gap:
        print(f"FIRST NEGATIVE GAP:     tick {first_negative_gap[0]}, "
              f"agent {first_negative_gap[1]}, gap={first_negative_gap[2]}")
    else:
        print(f"FIRST NEGATIVE GAP:     None observed")
    print()
    print(f"Peak neg_gap_pct:       {peak_neg_gap_pct:.1f}%")
    print(f"Thresholds crossed:     {[k for k, v in intent_thresholds_crossed.items() if v]}%")
    print()
    print(f"Outcome:                {results['outcome']}")
    print(f"Success:                {'YES' if results['success'] else 'NO'}")
    print("=" * 70)
    
    # Close observer
    if observer:
        observer.close()
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ALIFE Experiment 3: The Anticipation Gap")
    parser.add_argument("--ticks", type=int, default=200000, help="Number of ticks to run")
    parser.add_argument("--log-interval", type=int, default=5000, help="Logging interval")
    parser.add_argument("--verify-waves", action="store_true", help="Enable wave verification mode")
    args = parser.parse_args()
    
    run_experiment_3(ticks=args.ticks, log_interval=args.log_interval, 
                     verify_waves=args.verify_waves)
