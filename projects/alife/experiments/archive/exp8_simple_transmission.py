"""
ALIFE Experiment 8.2: Simple Protocol Transmission

Scientific Question:
Can agents directly share communication protocols with each other to achieve
basic cultural transmission? Will simplified interaction rules enable
protocol spread between agents?

Biological Insight:
Cultural transmission begins with simple sharing behaviors. When agents
can directly share knowledge, it creates the foundation for more complex
cultural evolution.

World Structure:
- Single zone with all agents able to interact
- Simplified protocol creation and sharing rules
- Focus on basic transmission mechanics

Success Criteria (all valid outcomes):
1. PROTOCOL_CREATION - Agents create communication protocols
2. BASIC_TRANSMISSION - Protocols spread between agents
3. KNOWLEDGE_SHARING - Mathematical insights transmitted
4. CULTURAL_SPREAD - Protocols reach multiple agents
"""

import sys
import os
import argparse
import math
import json
from typing import Optional, Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime

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

# Simple transmission parameters
PROTOCOL_MEMORY_SIZE = 5  # Smaller memory for simplicity
PROTOCOL_TRANSMISSION_RANGE = 100  # Larger range for more interactions
PROTOCOL_LEARNING_RATE = 0.6  # Moderate learning probability
PROTOCOL_CREATION_RATE = 0.02  # Lower creation rate
SHARING_PROBABILITY = 0.1  # Probability of sharing protocols

@dataclass
class SimpleProtocol:
    """A simple communication protocol"""
    protocol_id: str
    creator_id: str
    creation_tick: int
    insight: str  # Single mathematical insight
    transmission_count: int
    carriers: Set[str]  # Set of agent IDs carrying this protocol
    
    def __post_init__(self):
        if isinstance(self.carriers, list):
            self.carriers = set(self.carriers)
        self.carriers.add(self.creator_id)

class SimpleTransmissionWorld:
    """World with simple protocol transmission mechanics"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.agents: List[Agent] = []
        self.protocols: Dict[str, SimpleProtocol] = {}
        self.tick_count = 0
        
        # Statistics
        self.creation_events = 0
        self.transmission_events = 0
        self.sharing_events = 0
        
    def add_agent(self, agent: Agent):
        """Add an agent with protocol memory"""
        self.agents.append(agent)
        agent.protocol_memory = []
        agent.known_protocols = set()
        
    def get_nearby_agents(self, x: int, y: int, range_distance: int) -> List[Agent]:
        """Get agents within communication range"""
        nearby = []
        for agent in self.agents:
            if not agent.alive:
                continue
            distance = math.sqrt((agent.x - x)**2 + (agent.y - y)**2)
            if distance <= range_distance:
                nearby.append(agent)
        return nearby
    
    def create_protocol(self, creator: Agent) -> SimpleProtocol:
        """Create a new protocol with mathematical insight"""
        # Generate simple mathematical insight
        insight_types = ["fibonacci", "prime", "geometric", "arithmetic", "pattern"]
        insight_type = _random.choice(insight_types)
        insight_value = _random.randint(1, 100)
        insight = f"{insight_type}_{insight_value}"
        
        protocol = SimpleProtocol(
            protocol_id=f"proto_{creator.id}_{len(self.protocols)}_{self.tick_count}",
            creator_id=creator.id,
            creation_tick=self.tick_count,
            insight=insight,
            transmission_count=0,
            carriers=set([creator.id])
        )
        
        self.protocols[protocol.protocol_id] = protocol
        creator.protocol_memory.append(protocol)
        creator.known_protocols.add(protocol.protocol_id)
        self.creation_events += 1
        
        return protocol
    
    def transmit_protocol(self, sender: Agent, receiver: Agent, protocol: SimpleProtocol) -> bool:
        """Transmit a protocol from sender to receiver"""
        if protocol.protocol_id not in receiver.known_protocols:
            if _random.random() < PROTOCOL_LEARNING_RATE:
                # Receiver learns the protocol
                receiver.protocol_memory.append(protocol)
                receiver.known_protocols.add(protocol.protocol_id)
                protocol.carriers.add(receiver.id)
                protocol.transmission_count += 1
                self.transmission_events += 1
                return True
        return False
    
    def simulate_simple_transmission(self):
        """Simulate one tick of simple protocol transmission"""
        self.tick_count += 1
        
        for agent in self.agents:
            if not agent.alive:
                continue
            
            nearby_agents = self.get_nearby_agents(agent.x, agent.y, PROTOCOL_TRANSMISSION_RANGE)
            
            # Create new protocols occasionally
            if _random.random() < PROTOCOL_CREATION_RATE:
                self.create_protocol(agent)
            
            # Share protocols with nearby agents
            if agent.protocol_memory and nearby_agents:
                if _random.random() < SHARING_PROBABILITY:
                    # Select a protocol to share
                    protocol_to_share = _random.choice(agent.protocol_memory)
                    
                    # Share with random nearby agent
                    other_agents = [a for a in nearby_agents if a.id != agent.id]
                    if other_agents:
                        receiver = _random.choice(other_agents)
                        if self.transmit_protocol(agent, receiver, protocol_to_share):
                            self.sharing_events += 1
    
    def calculate_metrics(self) -> Dict:
        """Calculate transmission metrics"""
        total_protocols = len(self.protocols)
        total_transmissions = sum(p.transmission_count for p in self.protocols.values())
        
        # Calculate spread metrics
        carrier_counts = [len(p.carriers) for p in self.protocols.values()]
        avg_carriers = sum(carrier_counts) / len(carrier_counts) if carrier_counts else 0
        max_carriers = max(carrier_counts) if carrier_counts else 0
        
        # Calculate how many agents have protocols
        agents_with_protocols = len([a for a in self.agents if a.known_protocols])
        
        return {
            'total_protocols': total_protocols,
            'total_transmissions': total_transmissions,
            'creation_events': self.creation_events,
            'transmission_events': self.transmission_events,
            'sharing_events': self.sharing_events,
            'avg_carriers_per_protocol': avg_carriers,
            'max_carriers_per_protocol': max_carriers,
            'agents_with_protocols': agents_with_protocols,
            'protocol_coverage': agents_with_protocols / len(self.agents) if self.agents else 0
        }

class SimpleTransmissionExperiment:
    """Main experiment controller for simple transmission"""
    
    def __init__(self, max_ticks: int = 20000, population: int = 30):
        self.max_ticks = max_ticks
        self.population = population
        self.world = SimpleTransmissionWorld(GRID_WIDTH, GRID_HEIGHT)
        self.setup_population()
        
    def setup_population(self):
        """Initialize the population"""
        for i in range(self.population):
            x = _random.randint(0, GRID_WIDTH - 1)
            y = _random.randint(0, GRID_HEIGHT - 1)
            agent = Agent(x, y)
            self.world.add_agent(agent)
    
    def run_simulation(self) -> Dict:
        """Run the simple transmission simulation"""
        print(f"🧬 Starting Simple Protocol Transmission Simulation")
        print(f"   Max ticks: {self.max_ticks}")
        print(f"   Population: {self.population}")
        print(f"   Transmission range: {PROTOCOL_TRANSMISSION_RANGE}")
        print(f"   Learning rate: {PROTOCOL_LEARNING_RATE}")
        print(f"   Sharing probability: {SHARING_PROBABILITY}")
        print()
        
        for tick in range(self.max_ticks):
            self.world.simulate_simple_transmission()
            
            if tick % 4000 == 0 and tick > 0:
                metrics = self.world.calculate_metrics()
                print(f"   Tick {tick}: {metrics['total_protocols']} protocols, "
                      f"{metrics['total_transmissions']} transmissions, "
                      f"{metrics['agents_with_protocols']} agents with protocols")
        
        # Final metrics
        final_metrics = self.world.calculate_metrics()
        
        # Evaluate success criteria
        success_criteria = self.evaluate_success_criteria(final_metrics)
        
        results = {
            'experiment': 'exp8_simple_transmission',
            'date': datetime.now().isoformat(),
            'parameters': {
                'max_ticks': self.max_ticks,
                'population': self.population,
                'protocol_memory_size': PROTOCOL_MEMORY_SIZE,
                'transmission_range': PROTOCOL_TRANSMISSION_RANGE,
                'learning_rate': PROTOCOL_LEARNING_RATE,
                'creation_rate': PROTOCOL_CREATION_RATE,
                'sharing_probability': SHARING_PROBABILITY
            },
            'results': final_metrics,
            'success_criteria': success_criteria
        }
        
        return results
    
    def evaluate_success_criteria(self, metrics: Dict) -> Dict:
        """Evaluate the success criteria"""
        return {
            'protocol_creation': metrics['total_protocols'] > 10,
            'basic_transmission': metrics['total_transmissions'] > 5,
            'knowledge_sharing': metrics['agents_with_protocols'] > 5,
            'cultural_spread': metrics['protocol_coverage'] > 0.3
        }

def main():
    parser = argparse.ArgumentParser(description='ALIFE Experiment 8.2: Simple Protocol Transmission')
    parser.add_argument('--ticks', type=int, default=20000, help='Maximum simulation ticks')
    parser.add_argument('--population', type=int, default=30, help='Initial population size')
    parser.add_argument('--output', type=str, default='exp8_simple_transmission_results.json', 
                       help='Output file for results')
    
    args = parser.parse_args()
    
    # Run experiment
    experiment = SimpleTransmissionExperiment(max_ticks=args.ticks, population=args.population)
    results = experiment.run_simulation()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("🎉 Simple Transmission Experiment Complete!")
    print(f"   Results saved to: {args.output}")
    print()
    print("📊 Final Results:")
    print(f"   Total Protocols: {results['results']['total_protocols']}")
    print(f"   Total Transmissions: {results['results']['total_transmissions']}")
    print(f"   Agents with Protocols: {results['results']['agents_with_protocols']}")
    print(f"   Protocol Coverage: {results['results']['protocol_coverage']:.2%}")
    print(f"   Avg Carriers per Protocol: {results['results']['avg_carriers_per_protocol']:.2f}")
    print()
    print("✅ Success Criteria:")
    for criterion, passed in results['success_criteria'].items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {criterion}: {status}")
    
    passed_count = sum(results['success_criteria'].values())
    print(f"\n🎯 Overall: {passed_count}/4 criteria passed")
    
    if results['results']['total_transmissions'] > 0:
        print(f"\n🌍 Cultural Transmission Analysis:")
        print(f"   Basic transmission achieved!")
        print(f"   Protocols spread between agents")
        print(f"   Foundation for cultural evolution established")

if __name__ == "__main__":
    main()
