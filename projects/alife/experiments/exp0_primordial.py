"""
Experiment 0 — Primordial Soup
Question: Does life sustain itself? Are energy economics correct?

Success criteria:
- Population stabilizes between 20-200 agents over 10,000 ticks
- No collapse to 0
- No explosion above 500

MEM_NONE enforced — purely reactive baseline.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from config import INITIAL_POPULATION, LOG_INTERVAL
from faithh_observer import PulseWatcher


def run_experiment_0(ticks: int = 10000, log_interval: int = 100) -> dict:
    """
    Run Experiment 0: Primordial Soup
    
    Returns dict with:
        - population_curve: list of (tick, population) tuples
        - first_reproduction: tick number of first reproduction
        - final_population: population at end
        - min_population: minimum population observed
        - max_population: maximum population observed
        - success: True if population stayed in 20-200 range
    """
    sim = Simulation(experiment=0)
    sim.initialize_population(INITIAL_POPULATION)
    
    # Initialize FAITHH PULSE observer
    observer = None
    try:
        observer = PulseWatcher()
    except Exception as e:
        print(f"[PULSE] Observer init failed (non-fatal): {e}")
    
    results = {
        'population_curve': [],
        'first_reproduction': None,
        'final_population': 0,
        'min_population': INITIAL_POPULATION,
        'max_population': INITIAL_POPULATION,
        'success': False,
        'energy_distribution': [],
    }
    
    prev_reproductions = 0
    
    print(f"{'='*60}")
    print(f"EXPERIMENT 0: PRIMORDIAL SOUP")
    print(f"{'='*60}")
    print(f"Initial population: {INITIAL_POPULATION}")
    print(f"Running for {ticks} ticks, logging every {log_interval} ticks")
    print(f"{'='*60}\n")
    
    for t in range(ticks):
        sim.tick()
        
        pop = sim.world.get_population()
        
        # Track first reproduction and log to observer
        if sim.total_reproductions > prev_reproductions:
            if results['first_reproduction'] is None:
                results['first_reproduction'] = t + 1
                print(f"*** FIRST REPRODUCTION at tick {t + 1} ***")
            
            # Log reproduction events to observer
            if observer:
                # Find agents that just reproduced (those in reproduction queue were processed)
                # We log the parent agents that successfully reproduced
                for agent in sim.world.get_alive_agents():
                    if agent.energy < 200 and agent.generation > 0:  # Recently reproduced parents lose energy
                        try:
                            observer.log_event("reproduction", agent, sim.world, t + 1)
                        except Exception as e:
                            print(f"[PULSE] Observer error (non-fatal): {e}")
                        break  # Log one per tick to avoid duplicates
        prev_reproductions = sim.total_reproductions
        
        # Log deaths to observer
        if observer and sim.total_deaths > 0:
            for agent in list(sim.world.agents.values()):
                if not agent.alive and not hasattr(agent, '_death_logged'):
                    try:
                        observer.log_event("death_starvation", agent, sim.world, t + 1)
                        agent._death_logged = True
                    except Exception as e:
                        print(f"[PULSE] Observer error (non-fatal): {e}")
        
        # Track min/max
        results['min_population'] = min(results['min_population'], pop)
        results['max_population'] = max(results['max_population'], pop)
        
        # Log at interval
        if (t + 1) % log_interval == 0:
            results['population_curve'].append((t + 1, pop))
            
            # Calculate average energy of living agents
            agents = sim.world.get_alive_agents()
            avg_energy = sum(a.energy for a in agents) / len(agents) if agents else 0
            
            print(f"Tick {t + 1:>6}: pop={pop:>4}, births={sim.total_reproductions:>4}, "
                  f"deaths={sim.total_deaths:>4}, avg_energy={avg_energy:.1f}")
            
            # Log population snapshot to observer
            if observer:
                try:
                    observer.snapshot_population(sim.world.agents, sim.world, t + 1)
                except Exception as e:
                    print(f"[PULSE] Observer error (non-fatal): {e}")
            
            # Early termination on collapse
            if pop == 0:
                print(f"\n*** POPULATION COLLAPSED at tick {t + 1} ***")
                break
    
    results['final_population'] = sim.world.get_population()
    
    # Determine success
    min_ok = results['min_population'] >= 20
    max_ok = results['max_population'] <= 500
    final_ok = 20 <= results['final_population'] <= 200
    results['success'] = min_ok and max_ok and final_ok
    
    print(f"\n{'='*60}")
    print(f"EXPERIMENT 0 RESULTS")
    print(f"{'='*60}")
    print(f"Final population:    {results['final_population']}")
    print(f"Min population:      {results['min_population']}")
    print(f"Max population:      {results['max_population']}")
    print(f"Total reproductions: {sim.total_reproductions}")
    print(f"Total deaths:        {sim.total_deaths}")
    print(f"First reproduction:  tick {results['first_reproduction']}")
    print(f"Success:             {'YES' if results['success'] else 'NO'}")
    
    if not results['success']:
        print(f"\nTuning recommendations:")
        if results['min_population'] < 20:
            print(f"  - Population dropped to {results['min_population']} — increase ENERGY_REGEN_RATE")
        if results['max_population'] > 500:
            print(f"  - Population peaked at {results['max_population']} — increase REPRODUCTION_THRESHOLD")
        if results['final_population'] < 20:
            print(f"  - Final population too low — increase INITIAL_ENERGY or reduce BASELINE_DRAIN")
        if results['final_population'] > 200:
            print(f"  - Final population too high — increase REPRODUCTION_THRESHOLD")
    
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
    
    parser = argparse.ArgumentParser(description='Experiment 0: Primordial Soup')
    parser.add_argument('--ticks', type=int, default=10000, help='Number of ticks to run')
    parser.add_argument('--log-interval', type=int, default=100, help='Ticks between log entries')
    
    args = parser.parse_args()
    
    results = run_experiment_0(ticks=args.ticks, log_interval=args.log_interval)
