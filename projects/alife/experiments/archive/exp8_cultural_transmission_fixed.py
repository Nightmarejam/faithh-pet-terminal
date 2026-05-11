"""
ALIFE Experiment 8.1: Cultural Transmission - Fixed Version

Scientific Question:
Building on the protocol creation success from Experiment 8, can agents 
transmit and share communication protocols between zones to achieve 
cultural transmission? Will hybrid zone interactions enable protocol 
spread and persistence across generations?

Biological Insight:
Cultural transmission requires interaction between different social groups.
When zones are completely isolated, culture cannot spread. Creating 
hybrid interaction zones allows for cultural exchange while maintaining
specialization benefits.

World Structure:
- Zone 1 (0-199): Protocol innovators (experiment with communication)
- Zone 2 (200-399): Protocol transmitters (teach and spread protocols)
- Zone 3 (400-599): Protocol receivers (learn and adapt protocols)
- Zone 4 (600-799): Cultural archives (preserve successful protocols)
- Zone 5 (800-999): Cross-generational bridges (connect generations)
- HYBRID ZONES: Overlapping areas between zones for cultural exchange

Success Criteria (all valid outcomes):
1. PROTOCOL_EVOLUTION - Communication protocols become more sophisticated over time
2. CULTURAL_TRANSMISSION - Protocols spread between agents and groups
3. KNOWLEDGE_ENCODING - Mathematical insights encoded in stable protocols
4. GENERATIONAL_PERSISTENCE - Protocols survive agent turnover and generations
"""

import sys
import os
import argparse
import math
import json
from typing import Optional, Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, deque
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

# Fixed protocol evolution parameters
PROTOCOL_MEMORY_SIZE = 10  # Number of protocols an agent can remember
PROTOCOL_TRANSMISSION_RANGE = 80  # Increased range for protocol teaching
PROTOCOL_LEARNING_RATE = 0.8  # Increased probability of learning transmitted protocol
PROTOCOL_MUTATION_RATE = 0.1  # Probability of protocol mutation
GENERATION_INTERVAL = 10000  # Ticks between generational turnover
CULTURAL_ARCHIVE_SIZE = 20  # Maximum protocols preserved in cultural archives

# NEW: Hybrid zone parameters
HYBRID_ZONE_WIDTH = 50  # Width of overlapping zones
CULTURAL_EXCHANGE_PROBABILITY = 0.3  # Probability of cultural exchange in hybrid zones
ZONE_INTERACTION_STRENGTH = 0.5  # Strength of interaction between zones

@dataclass
class CommunicationProtocol:
    """A communication protocol with encoded knowledge"""
    protocol_id: str
    creator_id: str
    creation_tick: int
    encoded_insights: List[str]  # Mathematical insights encoded
    transmission_count: int
    success_rate: float
    complexity: int  # 1-5 scale of protocol complexity
    zone_origin: int  # Zone where protocol was created
    
    def mutate(self) -> 'CommunicationProtocol':
        """Create a mutated version of the protocol"""
        if _random.random() < PROTOCOL_MUTATION_RATE:
            # Mutate complexity or add/remove insights
            new_complexity = max(1, min(5, self.complexity + _random.choice([-1, 0, 1])))
            new_insights = self.encoded_insights.copy()
            
            if _random.random() < 0.3 and len(new_insights) > 0:
                # Remove an insight
                new_insights.pop(_random.randint(0, len(new_insights) - 1))
            elif _random.random() < 0.3:
                # Add a new insight (simplified mathematical pattern)
                new_insights.append(f"pattern_{_random.randint(100, 999)}")
            
            return CommunicationProtocol(
                protocol_id=f"{self.protocol_id}_mut_{_random.randint(1000, 9999)}",
                creator_id=self.creator_id,
                creation_tick=self.creation_tick,
                encoded_insights=new_insights,
                transmission_count=0,
                success_rate=self.success_rate * _random.uniform(0.8, 1.2),
                complexity=new_complexity,
                zone_origin=self.zone_origin
            )
        return self

class CulturalTransmissionWorld:
    """World with fixed cultural transmission mechanics"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.agents: List[Agent] = []
        self.protocols: Dict[str, CommunicationProtocol] = {}
        self.cultural_archive: List[CommunicationProtocol] = []
        self.protocol_statistics = defaultdict(int)
        self.generation_count = 0
        self.tick_count = 0
        
        # Protocol evolution tracking
        self.protocol_lineage: Dict[str, List[str]] = {}  # parent -> children
        self.knowledge_transmission_events: List[Dict] = []
        self.cultural_persistence_events: List[Dict] = []
        
        # NEW: Cultural exchange tracking
        self.cultural_exchange_events: List[Dict] = []
        self.zone_interaction_events: List[Dict] = []
        
    def add_agent(self, agent: Agent):
        """Add an agent with protocol memory"""
        self.agents.append(agent)
        # Initialize agent's protocol memory
        agent.protocol_memory = []
        agent.learned_protocols = set()
        agent.teaching_protocols = []
        agent.zone_affinity = self.get_zone(agent.x)  # Agent's primary zone
        
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
    
    def get_zone(self, x: int) -> int:
        """Determine zone based on x position"""
        zone_width = self.width // 5
        return min(4, x // zone_width)
    
    def is_in_hybrid_zone(self, x: int) -> bool:
        """Check if position is in a hybrid zone (overlap between zones)"""
        zone_width = self.width // 5
        zone = x // zone_width
        
        # Check if near zone boundary
        zone_start = zone * zone_width
        zone_end = (zone + 1) * zone_width
        
        # Hybrid zones are areas near zone boundaries
        return (x < zone_start + HYBRID_ZONE_WIDTH or 
                x > zone_end - HYBRID_ZONE_WIDTH)
    
    def get_hybrid_zone_interactions(self, agent: Agent) -> List[int]:
        """Get zones that this agent can interact with in hybrid zones"""
        if not self.is_in_hybrid_zone(agent.x):
            return [self.get_zone(agent.x)]
        
        # In hybrid zones, can interact with adjacent zones
        current_zone = self.get_zone(agent.x)
        interactions = [current_zone]
        
        # Add adjacent zones
        if current_zone > 0:
            interactions.append(current_zone - 1)
        if current_zone < 4:
            interactions.append(current_zone + 1)
        
        return list(set(interactions))  # Remove duplicates
    
    def create_protocol(self, creator: Agent, insights: List[str]) -> CommunicationProtocol:
        """Create a new communication protocol"""
        protocol = CommunicationProtocol(
            protocol_id=f"proto_{creator.id}_{len(self.protocols)}_{self.tick_count}",
            creator_id=creator.id,
            creation_tick=self.tick_count,
            encoded_insights=insights,
            transmission_count=0,
            success_rate=0.5,  # Start with neutral success rate
            complexity=min(5, len(insights)),
            zone_origin=self.get_zone(creator.x)
        )
        
        self.protocols[protocol.protocol_id] = protocol
        creator.teaching_protocols.append(protocol)
        self.protocol_statistics['protocols_created'] += 1
        
        return protocol
    
    def transmit_protocol(self, teacher: Agent, student: Agent, protocol: CommunicationProtocol) -> bool:
        """Attempt to transmit a protocol from teacher to student with enhanced success"""
        # Base learning probability
        learning_probability = PROTOCOL_LEARNING_RATE
        
        # Enhanced learning in hybrid zones
        if self.is_in_hybrid_zone(student.x):
            learning_probability += 0.2  # 20% boost in hybrid zones
        
        # Zone affinity bonus
        if self.get_zone(student.x) == protocol.zone_origin:
            learning_probability += 0.1  # 10% boost in same zone
        
        # Cap learning probability
        learning_probability = min(1.0, learning_probability)
        
        if _random.random() < learning_probability:
            # Student learns the protocol
            if protocol.protocol_id not in student.learned_protocols:
                student.learned_protocols.add(protocol.protocol_id)
                student.protocol_memory.append(protocol)
                
                # Limit memory size
                if len(student.protocol_memory) > PROTOCOL_MEMORY_SIZE:
                    forgotten = student.protocol_memory.pop(0)
                    student.learned_protocols.discard(forgotten.protocol_id)
                
                # Update transmission statistics
                protocol.transmission_count += 1
                self.protocol_statistics['transmissions'] += 1
                
                # Record transmission event
                self.knowledge_transmission_events.append({
                    'tick': self.tick_count,
                    'teacher_id': teacher.id,
                    'student_id': student.id,
                    'protocol_id': protocol.protocol_id,
                    'teacher_zone': self.get_zone(teacher.x),
                    'student_zone': self.get_zone(student.x),
                    'in_hybrid_zone': self.is_in_hybrid_zone(student.x)
                })
                
                return True
        return False
    
    def archive_protocol(self, protocol: CommunicationProtocol):
        """Add a protocol to the cultural archive"""
        if len(self.cultural_archive) >= CULTURAL_ARCHIVE_SIZE:
            # Remove least successful protocol
            self.cultural_archive.sort(key=lambda p: p.success_rate)
            removed = self.cultural_archive.pop(0)
            del self.protocols[removed.protocol_id]
        
        self.cultural_archive.append(protocol)
        self.protocol_statistics['archived'] += 1
        
        # Record persistence event
        self.cultural_persistence_events.append({
            'tick': self.tick_count,
            'protocol_id': protocol.protocol_id,
            'success_rate': protocol.success_rate,
            'transmission_count': protocol.transmission_count,
            'complexity': protocol.complexity,
            'zone_origin': protocol.zone_origin
        })
    
    def simulate_cultural_transmission(self):
        """Simulate one tick of cultural transmission with fixed mechanics"""
        self.tick_count += 1
        
        # Check for generational turnover
        if self.tick_count % GENERATION_INTERVAL == 0:
            self.generation_turnover()
        
        # Protocol innovation and transmission with enhanced interactions
        for agent in self.agents:
            if not agent.alive:
                continue
            
            zone = self.get_zone(agent.x)
            nearby_agents = self.get_nearby_agents(agent.x, agent.y, PROTOCOL_TRANSMISSION_RANGE)
            
            # Get available zones for interaction (enhanced in hybrid zones)
            interaction_zones = self.get_hybrid_zone_interactions(agent)
            
            if zone == 0:  # Protocol innovators
                self.innovate_protocols(agent)
            elif zone == 1:  # Protocol transmitters
                self.transmit_protocols(agent, nearby_agents, interaction_zones)
            elif zone == 2:  # Protocol receivers
                self.learn_protocols(agent, nearby_agents, interaction_zones)
            elif zone == 3:  # Cultural archives
                self.archive_successful_protocols(agent)
            elif zone == 4:  # Cross-generational bridges
                self.bridge_generations(agent, nearby_agents)
            
            # NEW: Cultural exchange in hybrid zones
            if self.is_in_hybrid_zone(agent.x):
                self.facilitate_cultural_exchange(agent, nearby_agents, interaction_zones)
    
    def innovate_protocols(self, agent: Agent):
        """Zone 0: Create new protocols based on insights"""
        if _random.random() < 0.05:  # 5% chance per tick
            # Create insights based on agent's genome (simplified)
            insights = [f"insight_{agent.genome[i] % 1000:03d}" for i in range(1, 4)]
            protocol = self.create_protocol(agent, insights)
            self.protocol_statistics['innovations'] += 1
    
    def transmit_protocols(self, teacher: Agent, nearby_agents: List[Agent], interaction_zones: List[int]):
        """Zone 1: Transmit protocols to nearby agents with enhanced zone interactions"""
        if teacher.teaching_protocols and nearby_agents:
            # Select protocol to teach (prefer successful ones)
            teacher.teaching_protocols.sort(key=lambda p: p.success_rate, reverse=True)
            protocol_to_teach = teacher.teaching_protocols[0]
            
            # Enhanced transmission based on zone interactions
            for student in nearby_agents:
                if student.id != teacher.id:
                    student_zone = self.get_zone(student.x)
                    
                    # Transmit if in same zone or interaction zones
                    if student_zone in interaction_zones:
                        if self.transmit_protocol(teacher, student, protocol_to_teach):
                            # Update success rate based on transmission
                            protocol_to_teach.success_rate *= 1.01
                            protocol_to_teach.success_rate = min(1.0, protocol_to_teach.success_rate)
                            
                            # Record zone interaction
                            self.zone_interaction_events.append({
                                'tick': self.tick_count,
                                'teacher_zone': self.get_zone(teacher.x),
                                'student_zone': student_zone,
                                'protocol_id': protocol_to_teach.protocol_id,
                                'interaction_type': 'transmission'
                            })
    
    def learn_protocols(self, student: Agent, nearby_agents: List[Agent], interaction_zones: List[int]):
        """Zone 2: Learn protocols from nearby agents with enhanced zone interactions"""
        potential_teachers = [a for a in nearby_agents if a.teaching_protocols and a.id != student.id]
        
        if potential_teachers:
            # Filter teachers by interaction zones
            available_teachers = []
            for teacher in potential_teachers:
                teacher_zone = self.get_zone(teacher.x)
                if teacher_zone in interaction_zones:
                    available_teachers.append(teacher)
            
            if available_teachers:
                teacher = _random.choice(available_teachers)
                if teacher.teaching_protocols:
                    protocol = _random.choice(teacher.teaching_protocols)
                    self.transmit_protocol(teacher, student, protocol)
    
    def archive_successful_protocols(self, archivist: Agent):
        """Zone 3: Archive successful protocols"""
        successful_protocols = [p for p in self.protocols.values() 
                              if p.transmission_count > 5 and p.success_rate > 0.7]
        
        for protocol in successful_protocols[:2]:  # Archive up to 2 protocols
            if protocol not in self.cultural_archive:
                self.archive_protocol(protocol)
    
    def bridge_generations(self, bridge_agent: Agent, nearby_agents: List[Agent]):
        """Zone 4: Bridge protocols across generations"""
        if self.cultural_archive and nearby_agents:
            # Transmit archived protocols to new generation
            archived_protocol = _random.choice(self.cultural_archive)
            mutated_protocol = archived_protocol.mutate()
            
            # Add mutated protocol to system
            self.protocols[mutated_protocol.protocol_id] = mutated_protocol
            bridge_agent.teaching_protocols.append(mutated_protocol)
            
            # Transmit to nearby agents
            for agent in nearby_agents:
                if agent.id != bridge_agent.id:
                    self.transmit_protocol(bridge_agent, agent, mutated_protocol)
    
    def facilitate_cultural_exchange(self, agent: Agent, nearby_agents: List[Agent], interaction_zones: List[int]):
        """NEW: Facilitate cultural exchange in hybrid zones"""
        if _random.random() < CULTURAL_EXCHANGE_PROBABILITY:
            # Select a random protocol from agent's memory to share
            if agent.protocol_memory:
                shared_protocol = _random.choice(agent.protocol_memory)
                
                # Share with agents in different zones
                for other_agent in nearby_agents:
                    if other_agent.id != agent.id:
                        other_zone = self.get_zone(other_agent.x)
                        
                        # Cultural exchange between different zones
                        if other_zone not in interaction_zones:
                            if self.transmit_protocol(agent, other_agent, shared_protocol):
                                # Record cultural exchange event
                                self.cultural_exchange_events.append({
                                    'tick': self.tick_count,
                                    'exchanger_id': agent.id,
                                    'receiver_id': other_agent.id,
                                    'protocol_id': shared_protocol.protocol_id,
                                    'from_zone': self.get_zone(agent.x),
                                    'to_zone': other_zone,
                                    'exchange_type': 'cross_zone'
                                })
    
    def generation_turnover(self):
        """Simulate generational turnover with cultural preservation"""
        self.generation_count += 1
        
        # Preserve some protocols from cultural archive
        preserved_protocols = self.cultural_archive.copy()
        
        # Remove some agents (death)
        surviving_agents = []
        for agent in self.agents:
            if agent.alive and _random.random() < 0.7:  # 70% survival rate
                surviving_agents.append(agent)
        
        # Add new agents (birth) with inherited cultural knowledge
        new_agent_count = INITIAL_POPULATION - len(surviving_agents)
        for _ in range(new_agent_count):
            x = _random.randint(0, self.width - 1)
            y = _random.randint(0, self.height - 1)
            new_agent = Agent(x, y)
            self.add_agent(new_agent)
            
            # Inherit some cultural knowledge from archive
            if preserved_protocols and _random.random() < 0.3:
                inherited_protocol = _random.choice(preserved_protocols)
                new_agent.learned_protocols.add(inherited_protocol.protocol_id)
                new_agent.protocol_memory.append(inherited_protocol)
        
        self.agents = surviving_agents
        self.protocol_statistics['generation_turnovers'] += 1
    
    def calculate_cultural_transmission_metrics(self) -> Dict:
        """Calculate metrics for cultural transmission"""
        # Protocol complexity over time
        complexities = [p.complexity for p in self.protocols.values()]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        
        # Cultural transmission metrics
        total_transmissions = sum(p.transmission_count for p in self.protocols.values())
        unique_protocols = len(self.protocols)
        
        # Generational persistence
        persistent_protocols = len([p for p in self.cultural_archive if p.success_rate > 0.8])
        
        # Knowledge encoding
        total_insights = sum(len(p.encoded_insights) for p in self.protocols.values())
        
        # NEW: Cultural exchange metrics
        cross_zone_transmissions = len([e for e in self.knowledge_transmission_events 
                                     if e['teacher_zone'] != e['student_zone']])
        
        return {
            'total_protocols': unique_protocols,
            'average_complexity': avg_complexity,
            'total_transmissions': total_transmissions,
            'cultural_archive_size': len(self.cultural_archive),
            'persistent_protocols': persistent_protocols,
            'total_encoded_insights': total_insights,
            'generations': self.generation_count,
            'transmission_events': len(self.knowledge_transmission_events),
            'persistence_events': len(self.cultural_persistence_events),
            'cultural_exchange_events': len(self.cultural_exchange_events),
            'cross_zone_transmissions': cross_zone_transmissions,
            'zone_interaction_events': len(self.zone_interaction_events)
        }

class CulturalTransmissionExperiment:
    """Main experiment controller for fixed cultural transmission"""
    
    def __init__(self, max_ticks: int = 30000, population: int = 50):
        self.max_ticks = max_ticks
        self.population = population
        self.world = CulturalTransmissionWorld(GRID_WIDTH, GRID_HEIGHT)
        self.setup_population()
        
    def setup_population(self):
        """Initialize the population with zone distribution"""
        for i in range(self.population):
            # Distribute agents across zones
            zone = i % 5
            zone_width = GRID_WIDTH // 5
            x = zone * zone_width + _random.randint(0, zone_width - 1)
            y = _random.randint(0, GRID_HEIGHT - 1)
            agent = Agent(x, y)
            self.world.add_agent(agent)
    
    def run_simulation(self) -> Dict:
        """Run the complete simulation with cultural transmission"""
        print(f"🧬 Starting Cultural Transmission Simulation (Fixed)")
        print(f"   Max ticks: {self.max_ticks}")
        print(f"   Population: {self.population}")
        print(f"   Protocol memory size: {PROTOCOL_MEMORY_SIZE}")
        print(f"   Transmission range: {PROTOCOL_TRANSMISSION_RANGE}")
        print(f"   Learning rate: {PROTOCOL_LEARNING_RATE}")
        print(f"   Hybrid zone width: {HYBRID_ZONE_WIDTH}")
        print(f"   Cultural exchange probability: {CULTURAL_EXCHANGE_PROBABILITY}")
        print()
        
        for tick in range(self.max_ticks):
            self.world.simulate_cultural_transmission()
            
            if tick % 5000 == 0 and tick > 0:
                metrics = self.world.calculate_cultural_transmission_metrics()
                print(f"   Tick {tick}: {metrics['total_protocols']} protocols, "
                      f"{metrics['total_transmissions']} transmissions, "
                      f"{metrics['cultural_exchange_events']} cultural exchanges, "
                      f"generations: {metrics['generations']}")
        
        # Final metrics
        final_metrics = self.world.calculate_cultural_transmission_metrics()
        
        # Evaluate success criteria
        success_criteria = self.evaluate_success_criteria(final_metrics)
        
        results = {
            'experiment': 'exp8_cultural_transmission_fixed',
            'date': datetime.now().isoformat(),
            'parameters': {
                'max_ticks': self.max_ticks,
                'population': self.population,
                'protocol_memory_size': PROTOCOL_MEMORY_SIZE,
                'transmission_range': PROTOCOL_TRANSMISSION_RANGE,
                'learning_rate': PROTOCOL_LEARNING_RATE,
                'mutation_rate': PROTOCOL_MUTATION_RATE,
                'generation_interval': GENERATION_INTERVAL,
                'hybrid_zone_width': HYBRID_ZONE_WIDTH,
                'cultural_exchange_probability': CULTURAL_EXCHANGE_PROBABILITY
            },
            'results': final_metrics,
            'success_criteria': success_criteria,
            'protocol_details': {
                'total_created': self.world.protocol_statistics.get('protocols_created', 0),
                'innovations': self.world.protocol_statistics.get('innovations', 0),
                'transmissions': self.world.protocol_statistics.get('transmissions', 0),
                'archived': self.world.protocol_statistics.get('archived', 0),
                'generation_turnovers': self.world.protocol_statistics.get('generation_turnovers', 0)
            },
            'cultural_events': {
                'transmission_events': len(self.world.knowledge_transmission_events),
                'persistence_events': len(self.world.cultural_persistence_events),
                'cultural_exchange_events': len(self.world.cultural_exchange_events),
                'zone_interaction_events': len(self.world.zone_interaction_events)
            }
        }
        
        return results
    
    def evaluate_success_criteria(self, metrics: Dict) -> Dict:
        """Evaluate the success criteria for cultural transmission"""
        return {
            'protocol_evolution': metrics['average_complexity'] > 2.0,
            'cultural_transmission': metrics['total_transmissions'] > 100,
            'knowledge_encoding': metrics['total_encoded_insights'] > 50,
            'generational_persistence': metrics['persistent_protocols'] > 5
        }

def main():
    parser = argparse.ArgumentParser(description='ALIFE Experiment 8.1: Cultural Transmission - Fixed')
    parser.add_argument('--ticks', type=int, default=30000, help='Maximum simulation ticks')
    parser.add_argument('--population', type=int, default=50, help='Initial population size')
    parser.add_argument('--output', type=str, default='exp8_cultural_transmission_fixed_results.json', 
                       help='Output file for results')
    
    args = parser.parse_args()
    
    # Run experiment
    experiment = CulturalTransmissionExperiment(max_ticks=args.ticks, population=args.population)
    results = experiment.run_simulation()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("🎉 Cultural Transmission Experiment (Fixed) Complete!")
    print(f"   Results saved to: {args.output}")
    print()
    print("📊 Final Results:")
    print(f"   Total Protocols: {results['results']['total_protocols']}")
    print(f"   Total Transmissions: {results['results']['total_transmissions']}")
    print(f"   Cultural Exchanges: {results['results']['cultural_exchange_events']}")
    print(f"   Cross-Zone Transmissions: {results['results']['cross_zone_transmissions']}")
    print(f"   Cultural Archive: {results['results']['cultural_archive_size']}")
    print(f"   Generations: {results['results']['generations']}")
    print()
    print("✅ Success Criteria:")
    for criterion, passed in results['success_criteria'].items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {criterion}: {status}")
    
    passed_count = sum(results['success_criteria'].values())
    print(f"\n🎯 Overall: {passed_count}/4 criteria passed")
    
    # Cultural transmission analysis
    if results['results']['cultural_exchange_events'] > 0:
        print(f"\n🌍 Cultural Transmission Analysis:")
        print(f"   Cultural exchanges: {results['results']['cultural_exchange_events']}")
        print(f"   Cross-zone transmissions: {results['results']['cross_zone_transmissions']}")
        print(f"   Zone interactions: {results['results']['zone_interaction_events']}")
        print("   ✅ Cultural transmission achieved!")

if __name__ == "__main__":
    main()
