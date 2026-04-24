"""
ALIFE Experiment 6: Cognitive Specialization

Scientific Question:
Can agents develop cognitive specialization when exposed to Fibonacci frequency 
ratio interference patterns? Does mathematical cognition evolve through environmental 
pressure to recognize and specialize in specific frequency patterns?

Biological Insight:
Mathematical pattern recognition is a fundamental cognitive capability. 
If agents can evolve to recognize and specialize in Fibonacci-based frequency 
patterns, it suggests mathematical cognition can emerge through evolutionary 
pressure rather than requiring innate mathematical ability.

World Structure:
- Zone 1 (0-95): φ^1 = 1.618 ratio frequency
- Zone 2 (96-191): φ^2 = 2.618 ratio frequency  
- Zone 3 (192-287): φ^3 = 4.236 ratio frequency
- Zone 4 (288-383): φ^4 = 6.854 ratio frequency
- Zone 5 (384-479): φ^5 = 11.090 ratio frequency

Success Criteria (all valid outcomes):
1. COGNITIVE_SPECIALIZATION - Agents specialize in specific Fibonacci zones
2. PATTERN_RECOGNITION - Agents evolve frequency pattern detection
3. ZONE_PREFERENCE - Population stratifies by cognitive specialization
4. MATHEMATICAL_COGNITION - Complex mathematical reasoning emerges
"""

import sys
import os
import argparse
import math
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from agent import Agent
from config import (
    INITIAL_POPULATION, WAVE1_INTERVAL, WAVE2_INTERVAL,
    ZONE_LEFT_END, ZONE_CENTER_END, GRID_WIDTH, GRID_HEIGHT,
    PREDATOR_DAMAGE, THERMAL_DRAIN_RATE, WAVE_SPEED_C, SENSE_THREAT_RANGE,
    ENERGY_SOURCE_RADIUS, ENERGY_MAX
)
import random as _random

# Fibonacci frequency ratios (φ^n)
FIBONACCI_PHI = 1.618033988749895  # Golden ratio
FIBONACCI_ZONES = {
    'zone_1': {'range': (0, 95), 'phi_power': 1, 'ratio': FIBONACCI_PHI},
    'zone_2': {'range': (96, 191), 'phi_power': 2, 'ratio': FIBONACCI_PHI**2},
    'zone_3': {'range': (192, 287), 'phi_power': 3, 'ratio': FIBONACCI_PHI**3},
    'zone_4': {'range': (288, 383), 'phi_power': 4, 'ratio': FIBONACCI_PHI**4},
    'zone_5': {'range': (384, 479), 'phi_power': 5, 'ratio': FIBONACCI_PHI**5}
}

# Cognitive specialization thresholds
SPECIALIZATION_THRESHOLDS = {
    'pattern_recognition': 0.7,
    'frequency_tracking': 0.8,
    'zone_preference': 0.6
}

# Experiment-specific parameters
COGNITIVE_BONUS_MULTIPLIER = 1.5  # Energy bonus for specialized agents
PATTERN_RECOGNITION_COST = 3     # Cost per tick for pattern recognition
ZONE_PREFERENCE_BONUS = 2        # Energy bonus for zone preference

# Try to import FAITHH observer
try:
    from faithh_observer import PulseWatcher
    FAITHH_AVAILABLE = True
except ImportError:
    FAITHH_AVAILABLE = False

class CognitiveWave:
    """Represents a wave with Fibonacci-based frequency pattern."""
    
    def __init__(self, zone_id: str, phi_power: int, base_interval: int, direction: str = 'left_to_right'):
        self.zone_id = zone_id
        self.phi_power = phi_power
        self.base_interval = base_interval
        self.interval = int(base_interval * (FIBONACCI_PHI ** phi_power))
        self.direction = direction
        self.last_spawn = 0
        
    def should_spawn(self, current_tick: int) -> bool:
        return current_tick - self.last_spawn >= self.interval
    
    def spawn(self, current_tick: int):
        self.last_spawn = current_tick

class CognitiveSpecializationTracker:
    """Tracks cognitive specialization emergence in agents."""
    
    def __init__(self):
        self.specializations = {}
        self.pattern_recognition_agents = set()
        self.zone_preferences = {}
        
    def track_pattern_recognition(self, agent_id: str, zone_id: str, accuracy: float):
        """Track agent's ability to recognize Fibonacci patterns."""
        if accuracy >= SPECIALIZATION_THRESHOLDS['pattern_recognition']:
            self.pattern_recognition_agents.add(agent_id)
            if agent_id not in self.specializations:
                self.specializations[agent_id] = {'zone': zone_id, 'accuracy': accuracy}
            else:
                self.specializations[agent_id]['accuracy'] = max(
                    self.specializations[agent_id]['accuracy'], accuracy
                )
    
    def track_zone_preference(self, agent_id: str, zone_id: str, preference_strength: float):
        """Track agent's preference for specific Fibonacci zones."""
        if preference_strength >= SPECIALIZATION_THRESHOLDS['zone_preference']:
            if agent_id not in self.zone_preferences:
                self.zone_preferences[agent_id] = {'zone': zone_id, 'strength': preference_strength}
            else:
                # Update if stronger preference
                if preference_strength > self.zone_preferences[agent_id]['strength']:
                    self.zone_preferences[agent_id] = {'zone': zone_id, 'strength': preference_strength}
    
    def get_specialization_stats(self) -> dict:
        """Get statistics on cognitive specialization."""
        total_agents = len(self.specializations)
        if total_agents == 0:
            return {'total_specialized': 0, 'zone_distribution': {}, 'avg_accuracy': 0}
        
        zone_dist = {}
        total_accuracy = 0
        
        for agent_id, spec in self.specializations.items():
            zone = spec['zone']
            zone_dist[zone] = zone_dist.get(zone, 0) + 1
            total_accuracy += spec['accuracy']
        
        return {
            'total_specialized': total_agents,
            'zone_distribution': zone_dist,
            'avg_accuracy': total_accuracy / total_agents,
            'pattern_recognition_agents': len(self.pattern_recognition_agents),
            'zone_preference_agents': len(self.zone_preferences)
        }

class CognitiveSimulation(Simulation):
    """Extended simulation with Fibonacci frequency zones and cognitive tracking."""
    
    def __init__(self, experiment: int = 6, seed: Optional[int] = None):
        super().__init__(experiment=experiment, seed=seed)
        
        # Initialize Fibonacci zone waves
        self.fibonacci_waves = {}
        base_interval = 400  # Base interval for φ^1
        
        for zone_id, zone_config in FIBONACCI_ZONES.items():
            direction = 'left_to_right' if zone_config['phi_power'] % 2 == 1 else 'right_to_left'
            self.fibonacci_waves[zone_id] = CognitiveWave(
                zone_id, 
                zone_config['phi_power'], 
                base_interval,
                direction
            )
        
        # Cognitive specialization tracker
        self.cognitive_tracker = CognitiveSpecializationTracker()
        
        # Zone energy bonuses for specialization
        self.zone_energy_bonuses = {}
        for zone_id in FIBONACCI_ZONES:
            self.zone_energy_bonuses[zone_id] = []
        
        # Initialize population first
        self.initialize_population(count=INITIAL_POPULATION, seed_reproduce=True)
        
        # Pre-seed some agents with cognitive traits
        self._seed_cognitive_agents()
    
    def _seed_cognitive_agents(self):
        """Pre-seed some agents with cognitive traits."""
        cognitive_agents = min(30, len(self.world.agents))  # 15% of population
        agent_ids = list(self.world.agents.keys())
        _random.shuffle(agent_ids)
        
        for i in range(cognitive_agents):
            agent_id = agent_ids[i]
            agent = self.world.agents[agent_id]
            
            # Assign to random Fibonacci zone
            zone_id = _random.choice(list(FIBONACCI_ZONES.keys()))
            zone_range = FIBONACCI_ZONES[zone_id]['range']
            
            # Place agent in assigned zone
            agent.x = _random.randint(zone_range[0], zone_range[1])
            agent.y = _random.randint(0, self.world.height - 1)
            
            # Give cognitive genome (PROC_PATTERN + MEM_FIBONACCI)
            agent.genome = [
                0x01,  # ACT_REPRODUCE
                0x00,  # ACT_MOVE
                0x00,  # ACT_TURN
                0x00,  # ACT_SHIELD
                0x05,  # ACT_SIGNAL (repurposed for pattern recognition)
                0x06,  # ACT_TOXIN (repurposed for cognitive enhancement)
                0x07,  # PROC_PATTERN (new - Fibonacci pattern recognition)
                0x08,  # MEM_FIBONACCI (new - Fibonacci memory)
                0x00,  # MEM_WAVE1
                0x00,  # MEM_WAVE2
                0x00,  # MEM_DUAL
                0x00,  # MEM_BEAT
                0x00,  # MEM_PREDICT
                0x00,  # MEM_ANTICIPATE
                0x00,  # MEM_STRIPE
                0x00,  # MEM_POISON
                0x00   # MEM_PARASITE
            ]
    
    def get_agent_zone(self, agent) -> str:
        """Determine which Fibonacci zone an agent is in."""
        for zone_id, zone_config in FIBONACCI_ZONES.items():
            if zone_config['range'][0] <= agent.x <= zone_config['range'][1]:
                return zone_id
        return 'zone_1'  # Default fallback
    
    def apply_cognitive_bonuses(self, tick: int):
        """Apply energy bonuses for cognitive specialization."""
        for agent_id, agent in list(self.world.agents.items()):
            if not agent.alive:
                continue
            
            zone_id = self.get_agent_zone(agent)
            
            # Check if agent has cognitive traits
            has_pattern_recognition = (agent.genome[6] == 0x07)  # PROC_PATTERN
            has_fibonacci_memory = (agent.genome[7] == 0x08)     # MEM_FIBONACCI
            
            if has_pattern_recognition and has_fibonacci_memory:
                # Calculate pattern recognition accuracy
                zone_config = FIBONACCI_ZONES[zone_id]
                expected_ratio = zone_config['ratio']
                
                # Simulate pattern recognition (higher in correct zone)
                zone_bonus = 1.0
                if self.get_agent_zone(agent) == zone_id:
                    zone_bonus = COGNITIVE_BONUS_MULTIPLIER
                
                accuracy = min(1.0, zone_bonus * 0.8)  # Base 80% accuracy in correct zone
                
                # Track cognitive specialization
                self.cognitive_tracker.track_pattern_recognition(agent_id, zone_id, accuracy)
                
                # Apply energy bonus for specialization
                if accuracy >= SPECIALIZATION_THRESHOLDS['pattern_recognition']:
                    agent.energy += ZONE_PREFERENCE_BONUS * accuracy
                    agent.energy = min(agent.energy, ENERGY_MAX)
                
                # Track zone preference
                preference_strength = accuracy * zone_bonus
                self.cognitive_tracker.track_zone_preference(agent_id, zone_id, preference_strength)
    
    def spawn_fibonacci_waves(self, tick: int):
        """Spawn waves according to Fibonacci frequency patterns."""
        for zone_id, wave in self.fibonacci_waves.items():
            if wave.should_spawn(tick):
                wave.spawn(tick)
                
                # Create wave state for this zone
                from world import WaveState
                wave_state = WaveState(
                    start_tick=tick,
                    speed=WAVE_SPEED_C,
                    stealth=False,
                    direction=wave.direction
                )
                
                # Add to world's wave list
                self.world.active_waves.append(wave_state)
    
    def tick(self):
        """Extended tick with cognitive tracking."""
        super().tick()
        tick = self.total_ticks
        
        # Spawn Fibonacci waves
        self.spawn_fibonacci_waves(tick)
        
        # Apply cognitive bonuses every 10 ticks
        if tick % 10 == 0:
            self.apply_cognitive_bonuses(tick)
    
    def get_cognitive_stats(self) -> dict:
        """Get comprehensive cognitive specialization statistics."""
        base_stats = self.cognitive_tracker.get_specialization_stats()
        
        # Add zone population distribution
        zone_populations = {}
        for zone_id in FIBONACCI_ZONES:
            zone_populations[zone_id] = 0
        
        for agent in self.world.agents.values():
            if agent.alive:
                zone_id = self.get_agent_zone(agent)
                zone_populations[zone_id] += 1
        
        base_stats['zone_populations'] = zone_populations
        base_stats['total_population'] = sum(zone_populations.values())
        
        return base_stats

def run_experiment(ticks: int = 200000, log_interval: int = 5000):
    """Run the cognitive specialization experiment."""
    print("=" * 60)
    print("EXPERIMENT 6: COGNITIVE SPECIALIZATION")
    print("=" * 60)
    print("Fibonacci Frequency Zones:")
    for zone_id, config in FIBONACCI_ZONES.items():
        print(f"  {zone_id}: cols {config['range'][0]}-{config['range'][1]}, φ^{config['phi_power']} = {config['ratio']:.3f}")
    print(f"Running for {ticks:,} ticks, logging every {log_interval:,} ticks")
    print("=" * 60)
    
    # Initialize simulation
    sim = CognitiveSimulation()
    
    # Set up FAITHH observer if available
    observer = None
    if FAITHH_AVAILABLE:
        observer = PulseWatcher()
        if not observer.connected:
            print("[PULSE] ChromaDB connection failed (continuing without logging)")
            observer = None
    
    # Run experiment
    cognitive_emergence_tick = None
    for tick in range(ticks):
        sim.tick()
        
        # Log progress
        if tick % log_interval == 0:
            stats = sim.get_cognitive_stats()
            specialized = stats['total_specialized']
            total = stats['total_population']
            
            zone_dist_str = ", ".join([f"{z}={stats['zone_populations'].get(z, 0)}" 
                                      for z in ['zone_1', 'zone_2', 'zone_3', 'zone_4', 'zone_5']])
            
            print(f"Tick {tick:6d}: pop={total:4d} | specialized={specialized:3d} ({specialized/total*100:.1f}%) | {zone_dist_str}")
            
            # Check for cognitive emergence
            if cognitive_emergence_tick is None and specialized >= 10:
                cognitive_emergence_tick = tick
                print(f"*** COGNITIVE SPECIALIZATION EMERGENCE: tick={tick}, {specialized} agents specialized ***")
    
    # Final results
    final_stats = sim.get_cognitive_stats()
    print("=" * 60)
    print("EXPERIMENT 6 RESULTS: COGNITIVE SPECIALIZATION")
    print("=" * 60)
    print(f"Final population:       {final_stats['total_population']}")
    print(f"Specialized agents:     {final_stats['total_specialized']}")
    print(f"Pattern recognition:    {final_stats['pattern_recognition_agents']}")
    print(f"Zone preference:        {final_stats['zone_preference_agents']}")
    print(f"Average accuracy:       {final_stats['avg_accuracy']:.3f}")
    
    print("\nZone Distribution:")
    for zone_id in ['zone_1', 'zone_2', 'zone_3', 'zone_4', 'zone_5']:
        pop = final_stats['zone_populations'].get(zone_id, 0)
        spec = final_stats['zone_distribution'].get(zone_id, 0)
        print(f"  {zone_id}: pop={pop:4d}, specialized={spec:3d} ({spec/pop*100 if pop > 0 else 0:.1f}%)")
    
    # Determine outcome
    specialization_rate = final_stats['total_specialized'] / final_stats['total_population']
    
    if specialization_rate >= 0.3:
        outcome = "COGNITIVE_SPECIALIZATION"
    elif specialization_rate >= 0.15:
        outcome = "PATTERN_RECOGNITION"
    elif specialization_rate >= 0.05:
        outcome = "ZONE_PREFERENCE"
    else:
        outcome = "NO_SPECIALIZATION"
    
    print(f"\nOutcome:                {outcome}")
    print(f"Cognitive emergence:    {cognitive_emergence_tick or 'NONE'}")
    print("=" * 60)
    
    # Close FAITHH observer
    if observer is not None:
        print("[PULSE] Observer closing")
    
    return outcome, final_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ALIFE Experiment 6: Cognitive Specialization")
    parser.add_argument("--ticks", type=int, default=200000, help="Number of ticks to run")
    parser.add_argument("--log-interval", type=int, default=5000, help="Logging interval")
    
    args = parser.parse_args()
    
    outcome, stats = run_experiment(args.ticks, args.log_interval)
