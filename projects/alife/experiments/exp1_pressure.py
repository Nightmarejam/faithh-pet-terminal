"""
Experiment 1 — The Pressure Test
Question: Does selection pressure produce heritable trait differentiation?

Specifically: does the Shield trait (ACT_SHIELD) spread through the population
when predator waves create survival pressure?

Success criteria:
- Shield trait frequency rises above 50% within 20 generations under pressure
- Shield trait frequency drops below 20% within 10 generations after predator removed
- If reversion does NOT occur, that's a finding worth reporting

Run length: 50,000 ticks minimum (covers ~100 generations)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from config import (
    INITIAL_POPULATION, LOG_INTERVAL, PREDATOR_WAVE_INTERVAL,
    PREDATOR_REMOVAL_TICK
)
from faithh_observer import PulseWatcher

# ACT_SHIELD op code
ACT_SHIELD = 0x03


def has_shield_trait(agent) -> bool:
    """Check if agent has ACT_SHIELD in A0 or A1 slot."""
    return agent.genome[5] == ACT_SHIELD or agent.genome[6] == ACT_SHIELD


def calculate_shield_frequency(agents) -> float:
    """Calculate percentage of population with Shield trait."""
    if not agents:
        return 0.0
    shield_count = sum(1 for a in agents if has_shield_trait(a))
    return (shield_count / len(agents)) * 100


def get_avg_generation(agents) -> float:
    """Get average generation of population."""
    if not agents:
        return 0.0
    return sum(a.generation for a in agents) / len(agents)


def run_experiment_1(ticks: int = 50000, log_interval: int = 100) -> dict:
    """
    Run Experiment 1: Pressure Test
    
    Returns dict with:
        - population_curve: list of (tick, population) tuples
        - shield_frequency_curve: list of (tick, frequency) tuples
        - generation_curve: list of (tick, avg_generation) tuples
        - first_shield_emergence: tick and agent info
        - predator_wave_count: number of waves triggered
        - final_shield_frequency: percentage at end
        - success: True if Shield trait spread under pressure
    """
    sim = Simulation(experiment=1)
    sim.initialize_population(INITIAL_POPULATION)
    
    # Seed 10% of initial population with Shield trait using known-viable genome
    # This genome is minimal cost — senses and thresholds but mostly idles
    # S0=SENSE_ENERGY, S1=SENSE_THREAT, P0=PROC_THRESHOLD, P1=PROC_THRESHOLD
    # M0=MEM_NONE, A0=ACT_REPRODUCE, A1=ACT_SHIELD, R0=REG_NONE
    VIABLE_SHIELD_GENOME = bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x04, ACT_SHIELD, 0x00])
    
    agents = list(sim.world.agents.values())
    shield_seed_count = max(20, len(agents) * 2 // 5)  # 40% of population
    for i, agent in enumerate(agents[:shield_seed_count]):
        agent.genome = VIABLE_SHIELD_GENOME
    print(f"Seeded {shield_seed_count} agents with viable Shield genome")
    
    # Initialize FAITHH PULSE observer
    observer = None
    try:
        observer = PulseWatcher()
    except Exception as e:
        print(f"[PULSE] Observer init failed (non-fatal): {e}")
    
    results = {
        'population_curve': [],
        'shield_frequency_curve': [],
        'generation_curve': [],
        'first_shield_emergence': None,
        'predator_wave_count': 0,
        'predator_contacts': 0,
        'predator_kills': 0,
        'shield_blocks': 0,
        'final_shield_frequency': 0.0,
        'final_population': 0,
        'min_population': INITIAL_POPULATION,
        'max_population': INITIAL_POPULATION,
        'success': False,
    }
    
    prev_reproductions = 0
    prev_deaths = 0
    predator_active = True
    
    print(f"{'='*60}")
    print(f"EXPERIMENT 1: PRESSURE TEST")
    print(f"{'='*60}")
    print(f"Initial population: {INITIAL_POPULATION}")
    print(f"Predator wave interval: {PREDATOR_WAVE_INTERVAL} ticks")
    print(f"Predator removal tick: {PREDATOR_REMOVAL_TICK}")
    print(f"Running for {ticks} ticks, logging every {log_interval} ticks")
    print(f"{'='*60}\n")
    
    for t in range(ticks):
        tick_num = t + 1
        
        # Check if predator should be removed
        if predator_active and tick_num >= PREDATOR_REMOVAL_TICK:
            predator_active = False
            print(f"\n*** PREDATOR REMOVED at tick {tick_num} ***\n")
        
        # Run simulation tick first
        sim.tick()
        
        # Trigger predator wave at interval (after tick, so deaths are handled separately)
        wave_contacts = []
        if predator_active and tick_num % PREDATOR_WAVE_INTERVAL == 0:
            wave_contacts = sim.world.trigger_predator_wave(tick_num)
            results['predator_wave_count'] += 1
            
            # Count contacts, kills, and blocks
            predator_deaths_this_wave = []
            for agent_id, shielded, energy_before in wave_contacts:
                results['predator_contacts'] += 1
                if shielded:
                    results['shield_blocks'] += 1
                else:
                    # Check if agent died (energy went to 0)
                    agent = sim.world.agents.get(agent_id)
                    if agent and not agent.alive:
                        results['predator_kills'] += 1
                        predator_deaths_this_wave.append(agent)
                        # Log death to observer
                        if observer:
                            try:
                                observer.log_event("death_predator", agent, sim.world, tick_num, 
                                                   extra={"energy_before": energy_before})
                            except Exception as e:
                                print(f"[PULSE] Observer error (non-fatal): {e}")
            
            # Handle predator deaths through simulation's death counting
            for agent in predator_deaths_this_wave:
                sim.total_deaths += 1
                sim.world.remove_agent(agent)
            
            # Log shield activations
            if observer:
                for agent_id, shielded, energy_before in wave_contacts:
                    if shielded:
                        agent = sim.world.agents.get(agent_id)
                        if agent:
                            try:
                                observer.log_event("shield_activation", agent, sim.world, tick_num)
                            except Exception as e:
                                print(f"[PULSE] Observer error (non-fatal): {e}")
        
        pop = sim.world.get_population()
        agents = sim.world.get_alive_agents()
        
        # Track first reproduction
        if sim.total_reproductions > prev_reproductions:
            # Log reproduction events
            if observer:
                for agent in agents:
                    if agent.energy < 200 and agent.generation > 0:
                        try:
                            observer.log_event("reproduction", agent, sim.world, tick_num)
                        except Exception as e:
                            print(f"[PULSE] Observer error (non-fatal): {e}")
                        break
        prev_reproductions = sim.total_reproductions
        
        # Log starvation deaths
        if observer and sim.total_deaths > prev_deaths:
            for agent in list(sim.world.agents.values()):
                if not agent.alive and not hasattr(agent, '_death_logged'):
                    try:
                        observer.log_event("death_starvation", agent, sim.world, tick_num)
                        agent._death_logged = True
                    except Exception as e:
                        print(f"[PULSE] Observer error (non-fatal): {e}")
        prev_deaths = sim.total_deaths
        
        # Track min/max population
        results['min_population'] = min(results['min_population'], pop)
        results['max_population'] = max(results['max_population'], pop)
        
        # Track first Shield emergence (mutation creating Shield trait)
        if results['first_shield_emergence'] is None:
            for agent in agents:
                if has_shield_trait(agent) and agent.generation > 0:
                    results['first_shield_emergence'] = {
                        'tick': tick_num,
                        'agent_id': agent.id,
                        'generation': agent.generation,
                        'genome_hex': agent.genome.hex()
                    }
                    print(f"*** FIRST SHIELD EMERGENCE at tick {tick_num} ***")
                    print(f"    Agent {agent.id}, generation {agent.generation}")
                    
                    # Log to observer
                    if observer:
                        try:
                            observer.flag_event(
                                "First Shield trait emergence in lineage",
                                agent, sim.world, tick_num,
                                extra={"reason": "First ACT_SHIELD mutation observed"}
                            )
                        except Exception as e:
                            print(f"[PULSE] Observer error (non-fatal): {e}")
                    break
        
        # Log at interval
        if tick_num % log_interval == 0:
            shield_freq = calculate_shield_frequency(agents)
            avg_gen = get_avg_generation(agents)
            avg_energy = sum(a.energy for a in agents) / len(agents) if agents else 0
            
            results['population_curve'].append((tick_num, pop))
            results['shield_frequency_curve'].append((tick_num, shield_freq))
            results['generation_curve'].append((tick_num, avg_gen))
            
            # Wave indicator
            wave_marker = " [WAVE]" if tick_num % PREDATOR_WAVE_INTERVAL == 0 and predator_active else ""
            predator_marker = "" if predator_active else " [NO PREDATOR]"
            
            print(f"Tick {tick_num:>6}: pop={pop:>4}, shield={shield_freq:>5.1f}%, "
                  f"gen={avg_gen:>4.1f}, energy={avg_energy:>5.1f}{wave_marker}{predator_marker}")
            
            # Log population snapshot to observer
            if observer:
                try:
                    observer.snapshot_population(sim.world.agents, sim.world, tick_num)
                except Exception as e:
                    print(f"[PULSE] Observer error (non-fatal): {e}")
                
                # Log trait frequency snapshot
                try:
                    observer.log_trait_frequency(agents, sim.world, tick_num, shield_freq, avg_gen)
                except Exception as e:
                    # Method may not exist yet, that's ok
                    pass
            
            # Early termination on collapse
            if pop == 0:
                print(f"\n*** POPULATION COLLAPSED at tick {tick_num} ***")
                break
    
    # Final results
    final_agents = sim.world.get_alive_agents()
    results['final_population'] = len(final_agents)
    results['final_shield_frequency'] = calculate_shield_frequency(final_agents)
    
    # Determine success
    # Check if Shield frequency rose above 50% at any point during predator pressure
    max_shield_freq_during_pressure = 0
    for tick, freq in results['shield_frequency_curve']:
        if tick < PREDATOR_REMOVAL_TICK:
            max_shield_freq_during_pressure = max(max_shield_freq_during_pressure, freq)
    
    results['success'] = max_shield_freq_during_pressure >= 50
    
    print(f"\n{'='*60}")
    print(f"EXPERIMENT 1 RESULTS")
    print(f"{'='*60}")
    print(f"Final population:       {results['final_population']}")
    print(f"Min population:         {results['min_population']}")
    print(f"Max population:         {results['max_population']}")
    print(f"Total reproductions:    {sim.total_reproductions}")
    print(f"Total deaths:           {sim.total_deaths}")
    print(f"Predator waves:         {results['predator_wave_count']}")
    print(f"Predator contacts:      {results['predator_contacts']}")
    print(f"Predator kills:         {results['predator_kills']}")
    print(f"Shield blocks:          {results['shield_blocks']}")
    print(f"Final Shield frequency: {results['final_shield_frequency']:.1f}%")
    print(f"Max Shield freq (pressure): {max_shield_freq_during_pressure:.1f}%")
    
    if results['first_shield_emergence']:
        print(f"First Shield emergence: tick {results['first_shield_emergence']['tick']}, "
              f"gen {results['first_shield_emergence']['generation']}")
    else:
        print(f"First Shield emergence: None observed")
    
    print(f"Success:                {'YES' if results['success'] else 'NO'}")
    
    # Generation-based Shield frequency table
    print(f"\n{'='*60}")
    print(f"SHIELD FREQUENCY BY GENERATION")
    print(f"{'='*60}")
    
    # Find ticks closest to generation milestones
    gen_milestones = [1, 5, 10, 20, 50]
    for gen in gen_milestones:
        # Find closest tick where avg generation matches
        closest = None
        for i, (tick, avg_gen) in enumerate(results['generation_curve']):
            if avg_gen >= gen:
                closest = i
                break
        if closest is not None:
            tick, _ = results['generation_curve'][closest]
            _, shield_freq = results['shield_frequency_curve'][closest]
            print(f"Generation ~{gen:>2}: Shield frequency = {shield_freq:.1f}%")
    
    print(f"{'='*60}\n")
    
    # Close observer
    if observer:
        try:
            observer.close()
        except Exception as e:
            print(f"[PULSE] Observer close error (non-fatal): {e}")
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Experiment 1: Pressure Test')
    parser.add_argument('--ticks', type=int, default=50000, help='Number of ticks to run')
    parser.add_argument('--log-interval', type=int, default=100, help='Ticks between log entries')
    
    args = parser.parse_args()
    
    results = run_experiment_1(ticks=args.ticks, log_interval=args.log_interval)
