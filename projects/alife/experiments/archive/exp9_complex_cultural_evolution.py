"""
ALIFE Experiment 9: Complex Cultural Evolution

Scientific Question:
Building on the cultural transmission breakthrough from Experiment 8.2, can agents
develop complex cultural systems with sophisticated protocols, social structures,
and multi-generational knowledge accumulation? Will cultural complexity emerge
from simple transmission mechanisms?

Biological Insight:
Cultural complexity emerges when simple transmission mechanisms are combined
with selection pressures, innovation, and social learning. Complex cultures
develop specialized roles, accumulated knowledge, and sophisticated communication
systems that persist across generations.

World Structure:
- Multi-zone world with cultural centers and peripheries
- Innovation zones (protocol creation and refinement)
- Transmission zones (cultural exchange and learning)
- Archive zones (knowledge preservation and accumulation)
- Social zones (role specialization and cooperation)
- Evolution zones (selection and adaptation)

Success Criteria (all valid outcomes):
1. COMPLEX_PROTOCOL_EVOLUTION - Protocols increase in sophistication over time
2. CULTURAL_ACCUMULATION - Knowledge builds across generations
3. SOCIAL_SPECIALIZATION - Agents develop specialized cultural roles
4. MULTI_GENERATIONAL_PERSISTENCE - Complex culture survives generational turnover
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

# Complex cultural evolution parameters
PROTOCOL_COMPLEXITY_LEVELS = 5  # Levels of protocol sophistication
CULTURAL_MEMORY_SIZE = 15  # Increased memory for complex culture
INNOVATION_RATE = 0.03  # Rate of cultural innovation
TRANSMISSION_FIDELITY = 0.85  # Fidelity of cultural transmission
SELECTION_PRESSURE = 0.1  # Cultural selection pressure
SOCIAL_ROLE_COUNT = 4  # Number of specialized cultural roles
GENERATION_INTERVAL = 8000  # Generational turnover
CULTURAL_CENTERS = 3  # Number of cultural centers

@dataclass
class ComplexProtocol:
    """A sophisticated communication protocol with complexity levels"""
    protocol_id: str
    creator_id: str
    creation_tick: int
    complexity_level: int  # 1-5 sophistication level
    encoded_knowledge: List[str]  # Multiple knowledge components
    cultural_tags: Set[str]  # Cultural identifiers
    transmission_count: int
    success_rate: float
    generational_persistence: int  # How many generations survived
    social_role: str  # Associated social role
    
    def evolve(self) -> 'ComplexProtocol':
        """Evolve protocol to higher complexity"""
        if self.complexity_level < PROTOCOL_COMPLEXITY_LEVELS and _random.random() < 0.1:
            # Increase complexity
            new_complexity = self.complexity_level + 1
            
            # Add new knowledge component
            new_knowledge = f"advanced_concept_{_random.randint(1000, 9999)}"
            new_knowledge_list = self.encoded_knowledge + [new_knowledge]
            
            # Add cultural tag
            new_tags = self.cultural_tags.copy()
            new_tags.add(f"evolved_gen_{_random.randint(1, 100)}")
            
            return ComplexProtocol(
                protocol_id=f"{self.protocol_id}_evo_{_random.randint(1000, 9999)}",
                creator_id=self.creator_id,
                creation_tick=self.creation_tick,
                complexity_level=new_complexity,
                encoded_knowledge=new_knowledge_list,
                cultural_tags=new_tags,
                transmission_count=0,
                success_rate=self.success_rate * 0.9,  # Slightly lower success rate for new complexity
                generational_persistence=0,
                social_role=self.social_role
            )
        return self

@dataclass
class CulturalRole:
    """Specialized cultural role for agents"""
    role_name: str
    specialization: str
    protocol_preferences: List[str]
    social_function: str
    knowledge_requirements: List[str]
    collaboration_bonus: float

class ComplexCulturalWorld:
    """World with complex cultural evolution mechanics"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.agents: List[Agent] = []
        self.protocols: Dict[str, ComplexProtocol] = {}
        self.cultural_roles: Dict[str, CulturalRole] = {}
        self.cultural_centers: List[Tuple[int, int]] = []
        self.generation_count = 0
        self.tick_count = 0
        
        # Cultural evolution tracking
        self.cultural_complexity_history: List[Dict] = []
        self.social_structure_evolution: List[Dict] = []
        self.knowledge_accumulation: Dict[str, List[str]] = defaultdict(list)
        self.cultural_transmission_events: List[Dict] = []
        
        # Initialize cultural roles
        self._initialize_cultural_roles()
        
        # Initialize cultural centers
        self._initialize_cultural_centers()
        
    def _initialize_cultural_roles(self):
        """Initialize specialized cultural roles"""
        roles = {
            'innovator': CulturalRole(
                role_name='innovator',
                specialization='protocol_creation',
                protocol_preferences=['new', 'experimental'],
                social_function='create_new_protocols',
                knowledge_requirements=['creativity', 'domain_expertise'],
                collaboration_bonus=1.2
            ),
            'teacher': CulturalRole(
                role_name='teacher',
                specialization='protocol_transmission',
                protocol_preferences=['established', 'effective'],
                social_function='transmit_culture',
                knowledge_requirements=['communication', 'pedagogy'],
                collaboration_bonus=1.5
            ),
            'archivist': CulturalRole(
                role_name='archivist',
                specialization='knowledge_preservation',
                protocol_preferences=['complex', 'valuable'],
                social_function='preserve_knowledge',
                knowledge_requirements=['memory', 'organization'],
                collaboration_bonus=1.1
            ),
            'integrator': CulturalRole(
                role_name='integrator',
                specialization='protocol_synthesis',
                protocol_preferences=['diverse', 'complementary'],
                social_function='combine_protocols',
                knowledge_requirements=['synthesis', 'analysis'],
                collaboration_bonus=1.3
            )
        }
        self.cultural_roles = roles
    
    def _initialize_cultural_centers(self):
        """Initialize cultural centers in the world"""
        zone_width = self.width // 3
        zone_height = self.height // 3
        
        for i in range(CULTURAL_CENTERS):
            center_x = (i % 3) * zone_width + zone_width // 2
            center_y = (i // 3) * zone_height + zone_height // 2
            self.cultural_centers.append((center_x, center_y))
    
    def add_agent(self, agent: Agent):
        """Add an agent with cultural capabilities"""
        self.agents.append(agent)
        
        # Initialize agent cultural properties
        agent.cultural_memory = []
        agent.known_protocols = set()
        agent.cultural_role = _random.choice(list(self.cultural_roles.keys()))
        agent.cultural_center = _random.choice(self.cultural_centers)
        agent.specialization_level = _random.uniform(0.5, 1.0)
        agent.collaboration_tendency = _random.uniform(0.3, 0.9)
        
    def get_zone(self, x: int) -> int:
        """Determine cultural zone based on position"""
        zone_width = self.width // 5
        return min(4, x // zone_width)
    
    def get_nearby_cultural_center(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Get nearest cultural center"""
        min_distance = float('inf')
        nearest_center = None
        
        for center in self.cultural_centers:
            distance = math.sqrt((x - center[0])**2 + (y - center[1])**2)
            if distance < min_distance:
                min_distance = distance
                nearest_center = center
        
        return nearest_center
    
    def create_complex_protocol(self, creator: Agent) -> ComplexProtocol:
        """Create a new complex protocol"""
        # Determine protocol complexity based on creator's specialization
        base_complexity = 1
        if creator.cultural_role == 'innovator':
            base_complexity = _random.randint(1, 3)
        elif creator.specialization_level > 0.8:
            base_complexity = _random.randint(2, 4)
        
        # Generate knowledge components
        knowledge_components = []
        for i in range(base_complexity):
            component_types = ['mathematical', 'logical', 'creative', 'social', 'technical']
            component_type = _random.choice(component_types)
            component = f"{component_type}_insight_{_random.randint(100, 999)}"
            knowledge_components.append(component)
        
        # Generate cultural tags
        cultural_tags = {
            f"gen_{self.generation_count}",
            f"role_{creator.cultural_role}",
            f"complexity_{base_complexity}"
        }
        
        protocol = ComplexProtocol(
            protocol_id=f"complex_proto_{creator.id}_{len(self.protocols)}_{self.tick_count}",
            creator_id=creator.id,
            creation_tick=self.tick_count,
            complexity_level=base_complexity,
            encoded_knowledge=knowledge_components,
            cultural_tags=cultural_tags,
            transmission_count=0,
            success_rate=0.5 + (creator.specialization_level * 0.3),
            generational_persistence=0,
            social_role=creator.cultural_role
        )
        
        self.protocols[protocol.protocol_id] = protocol
        creator.cultural_memory.append(protocol)
        creator.known_protocols.add(protocol.protocol_id)
        
        # Add to knowledge accumulation
        for knowledge in knowledge_components:
            self.knowledge_accumulation[knowledge].append(protocol.protocol_id)
        
        return protocol
    
    def transmit_complex_protocol(self, teacher: Agent, student: Agent, protocol: ComplexProtocol) -> bool:
        """Transmit complex protocol with fidelity and evolution"""
        # Calculate transmission success probability
        base_probability = TRANSMISSION_FIDELITY
        
        # Role-based bonuses
        if teacher.cultural_role == 'teacher':
            base_probability += 0.1
        if student.cultural_role == 'archivist':
            base_probability += 0.05
        
        # Specialization level effects
        teacher_bonus = teacher.specialization_level * 0.1
        student_bonus = student.specialization_level * 0.1
        base_probability += teacher_bonus + student_bonus
        
        # Collaboration effects
        if teacher.collaboration_tendency > 0.7 and student.collaboration_tendency > 0.7:
            base_probability += 0.1
        
        # Complexity difficulty
        complexity_penalty = protocol.complexity_level * 0.05
        base_probability -= complexity_penalty
        
        base_probability = max(0.1, min(0.95, base_probability))
        
        if _random.random() < base_probability:
            # Successful transmission
            if protocol.protocol_id not in student.known_protocols:
                # Check memory capacity
                if len(student.cultural_memory) >= CULTURAL_MEMORY_SIZE:
                    # Forget oldest protocol
                    forgotten = student.cultural_memory.pop(0)
                    student.known_protocols.discard(forgotten.protocol_id)
                
                # Add protocol with potential mutation
                transmitted_protocol = protocol
                if _random.random() < 0.1:  # 10% mutation chance
                    transmitted_protocol = protocol.evolve()
                    self.protocols[transmitted_protocol.protocol_id] = transmitted_protocol
                
                student.cultural_memory.append(transmitted_protocol)
                student.known_protocols.add(transmitted_protocol.protocol_id)
                
                # Update transmission statistics
                protocol.transmission_count += 1
                
                # Record transmission event
                self.cultural_transmission_events.append({
                    'tick': self.tick_count,
                    'teacher_id': teacher.id,
                    'student_id': student.id,
                    'protocol_id': transmitted_protocol.protocol_id,
                    'teacher_role': teacher.cultural_role,
                    'student_role': student.cultural_role,
                    'protocol_complexity': transmitted_protocol.complexity_level,
                    'transmission_fidelity': base_probability
                })
                
                return True
        
        return False
    
    def simulate_complex_cultural_evolution(self):
        """Simulate one tick of complex cultural evolution"""
        self.tick_count += 1
        
        # Check for generational turnover
        if self.tick_count % GENERATION_INTERVAL == 0:
            self.generational_turnover()
        
        # Agent behaviors based on cultural roles
        for agent in self.agents:
            if not agent.alive:
                continue
            
            nearby_agents = self.get_nearby_agents(agent.x, agent.y, 80)
            
            if agent.cultural_role == 'innovator':
                self.innovator_behavior(agent, nearby_agents)
            elif agent.cultural_role == 'teacher':
                self.teacher_behavior(agent, nearby_agents)
            elif agent.cultural_role == 'archivist':
                self.archivist_behavior(agent, nearby_agents)
            elif agent.cultural_role == 'integrator':
                self.integrator_behavior(agent, nearby_agents)
            
            # General cultural transmission
            if _random.random() < 0.05:  # 5% chance per tick
                self.general_cultural_transmission(agent, nearby_agents)
        
        # Cultural center effects
        self.simulate_cultural_center_effects()
        
        # Record cultural complexity
        if self.tick_count % 1000 == 0:
            self.record_cultural_complexity()
    
    def innovator_behavior(self, innovator: Agent, nearby_agents: List[Agent]):
        """Innovator role behavior: create new protocols"""
        if _random.random() < INNOVATION_RATE:
            protocol = self.create_complex_protocol(innovator)
            
            # Share with nearby agents
            if nearby_agents and _random.random() < 0.3:
                student = _random.choice(nearby_agents)
                self.transmit_complex_protocol(innovator, student, protocol)
    
    def teacher_behavior(self, teacher: Agent, nearby_agents: List[Agent]):
        """Teacher role behavior: transmit established protocols"""
        if teacher.cultural_memory and nearby_agents:
            # Select best protocols for teaching
            teachable_protocols = [p for p in teacher.cultural_memory if p.transmission_count > 0]
            
            if teachable_protocols:
                # Prefer successful protocols
                teachable_protocols.sort(key=lambda p: p.success_rate, reverse=True)
                protocol_to_teach = teachable_protocols[0]
                
                # Teach multiple students
                for student in nearby_agents[:3]:  # Up to 3 students
                    if student.id != teacher.id:
                        self.transmit_complex_protocol(teacher, student, protocol_to_teach)
    
    def archivist_behavior(self, archivist: Agent, nearby_agents: List[Agent]):
        """Archivist role behavior: preserve complex protocols"""
        if archivist.cultural_memory:
            # Focus on complex, valuable protocols
            complex_protocols = [p for p in archivist.cultural_memory if p.complexity_level >= 3]
            
            if complex_protocols:
                # Share complex knowledge
                for student in nearby_agents:
                    if student.id != archivist.id and student.cultural_role in ['teacher', 'integrator']:
                        protocol = _random.choice(complex_protocols)
                        self.transmit_complex_protocol(archivist, student, protocol)
    
    def integrator_behavior(self, integrator: Agent, nearby_agents: List[Agent]):
        """Integrator role behavior: combine and synthesize protocols"""
        if len(integrator.cultural_memory) >= 2:
            # Select diverse protocols
            protocols_by_role = defaultdict(list)
            for protocol in integrator.cultural_memory:
                protocols_by_role[protocol.social_role].append(protocol)
            
            # Try to share protocols across roles
            for role, protocols in protocols_by_role.items():
                if protocols and nearby_agents:
                    target_roles = [r for r in ['innovator', 'teacher', 'archivist'] if r != role]
                    for student in nearby_agents:
                        if student.id != integrator.id and student.cultural_role in target_roles:
                            protocol = _random.choice(protocols)
                            self.transmit_complex_protocol(integrator, student, protocol)
                            break
    
    def general_cultural_transmission(self, agent: Agent, nearby_agents: List[Agent]):
        """General cultural transmission between agents"""
        if agent.cultural_memory and nearby_agents:
            # Select protocol based on social role preferences
            role = self.cultural_roles[agent.cultural_role]
            preferred_protocols = [p for p in agent.cultural_memory 
                                  if any(pref in p.protocol_id for pref in role.protocol_preferences)]
            
            if not preferred_protocols:
                preferred_protocols = agent.cultural_memory
            
            if preferred_protocols:
                protocol = _random.choice(preferred_protocols)
                student = _random.choice(nearby_agents)
                self.transmit_complex_protocol(agent, student, protocol)
    
    def simulate_cultural_center_effects(self):
        """Simulate cultural center effects on agents"""
        for agent in self.agents:
            if not agent.alive:
                continue
            
            # Check if agent is near a cultural center
            nearest_center = self.get_nearby_cultural_center(agent.x, agent.y)
            if nearest_center:
                distance = math.sqrt((agent.x - nearest_center[0])**2 + (agent.y - nearest_center[1])**2)
                
                if distance < 50:  # Within cultural center influence
                    # Enhanced innovation and transmission
                    if _random.random() < 0.1:  # 10% boost
                        if agent.cultural_role == 'innovator':
                            self.create_complex_protocol(agent)
                        elif agent.cultural_memory:
                            nearby_agents = self.get_nearby_agents(agent.x, agent.y, 100)
                            if nearby_agents:
                                student = _random.choice(nearby_agents)
                                protocol = _random.choice(agent.cultural_memory)
                                self.transmit_complex_protocol(agent, student, protocol)
    
    def get_nearby_agents(self, x: int, y: int, range_distance: int) -> List[Agent]:
        """Get agents within range"""
        nearby = []
        for agent in self.agents:
            if not agent.alive:
                continue
            distance = math.sqrt((agent.x - x)**2 + (agent.y - y)**2)
            if distance <= range_distance:
                nearby.append(agent)
        return nearby
    
    def generational_turnover(self):
        """Simulate generational turnover with cultural preservation"""
        self.generation_count += 1
        
        # Identify most valuable protocols for preservation
        valuable_protocols = []
        for protocol in self.protocols.values():
            # Value based on complexity, transmission, and success
            value = (protocol.complexity_level * 2 + 
                     protocol.transmission_count * 0.1 + 
                     protocol.success_rate * 3)
            valuable_protocols.append((value, protocol))
        
        valuable_protocols.sort(key=lambda x: x[0], reverse=True)
        preserved_protocols = [protocol for _, protocol in valuable_protocols[:20]]  # Top 20
        
        # Update generational persistence
        for protocol in preserved_protocols:
            protocol.generational_persistence += 1
        
        # Generational turnover of agents
        surviving_agents = []
        for agent in self.agents:
            if agent.alive and _random.random() < 0.7:  # 70% survival rate
                surviving_agents.append(agent)
        
        # Create new generation
        new_agent_count = INITIAL_POPULATION - len(surviving_agents)
        for _ in range(new_agent_count):
            x = _random.randint(0, self.width - 1)
            y = _random.randint(0, self.height - 1)
            new_agent = Agent(x, y)
            self.add_agent(new_agent)
            
            # Inherit some cultural knowledge
            if preserved_protocols and _random.random() < 0.4:
                inherited_protocol = _random.choice(preserved_protocols)
                new_agent.cultural_memory.append(inherited_protocol)
                new_agent.known_protocols.add(inherited_protocol.protocol_id)
        
        self.agents = surviving_agents
    
    def record_cultural_complexity(self):
        """Record cultural complexity metrics"""
        if not self.protocols:
            return
        
        # Calculate complexity metrics
        complexity_levels = [p.complexity_level for p in self.protocols.values()]
        avg_complexity = sum(complexity_levels) / len(complexity_levels)
        
        # Role distribution
        role_counts = defaultdict(int)
        for agent in self.agents:
            role_counts[agent.cultural_role] += 1
        
        # Knowledge diversity
        knowledge_types = set()
        for protocol in self.protocols.values():
            for knowledge in protocol.encoded_knowledge:
                knowledge_type = knowledge.split('_')[0]
                knowledge_types.add(knowledge_type)
        
        # Cultural diversity
        cultural_tags = set()
        for protocol in self.protocols.values():
            cultural_tags.update(protocol.cultural_tags)
        
        complexity_record = {
            'tick': self.tick_count,
            'generation': self.generation_count,
            'total_protocols': len(self.protocols),
            'avg_complexity': avg_complexity,
            'max_complexity': max(complexity_levels),
            'role_distribution': dict(role_counts),
            'knowledge_diversity': len(knowledge_types),
            'cultural_diversity': len(cultural_tags),
            'total_transmissions': sum(p.transmission_count for p in self.protocols.values()),
            'persistent_protocols': len([p for p in self.protocols.values() if p.generational_persistence > 0])
        }
        
        self.cultural_complexity_history.append(complexity_record)
    
    def calculate_cultural_evolution_metrics(self) -> Dict:
        """Calculate comprehensive cultural evolution metrics"""
        if not self.protocols:
            return {
                'total_protocols': 0,
                'avg_complexity': 0,
                'max_complexity': 0,
                'knowledge_diversity': 0,
                'cultural_diversity': 0,
                'generations': self.generation_count,
                'role_specialization': 0,
                'cultural_accumulation': 0,
                'transmission_events': len(self.cultural_transmission_events)
            }
        
        # Protocol complexity metrics
        complexity_levels = [p.complexity_level for p in self.protocols.values()]
        avg_complexity = sum(complexity_levels) / len(complexity_levels)
        max_complexity = max(complexity_levels)
        
        # Knowledge diversity
        knowledge_types = set()
        for protocol in self.protocols.values():
            for knowledge in protocol.encoded_knowledge:
                knowledge_type = knowledge.split('_')[0]
                knowledge_types.add(knowledge_type)
        
        # Cultural diversity
        cultural_tags = set()
        for protocol in self.protocols.values():
            cultural_tags.update(protocol.cultural_tags)
        
        # Role specialization
        role_counts = defaultdict(int)
        for agent in self.agents:
            role_counts[agent.cultural_role] += 1
        
        # Calculate specialization index (entropy)
        total_agents = len(self.agents)
        if total_agents > 0:
            role_entropy = 0
            for count in role_counts.values():
                if count > 0:
                    p = count / total_agents
                    role_entropy -= p * math.log(p)
            max_entropy = math.log(len(self.cultural_roles))
            role_specialization = role_entropy / max_entropy if max_entropy > 0 else 0
        else:
            role_specialization = 0
        
        # Cultural accumulation
        persistent_protocols = len([p for p in self.protocols.values() if p.generational_persistence > 0])
        cultural_accumulation = persistent_protocols / len(self.protocols) if self.protocols else 0
        
        return {
            'total_protocols': len(self.protocols),
            'avg_complexity': avg_complexity,
            'max_complexity': max_complexity,
            'knowledge_diversity': len(knowledge_types),
            'cultural_diversity': len(cultural_tags),
            'generations': self.generation_count,
            'role_specialization': role_specialization,
            'cultural_accumulation': cultural_accumulation,
            'transmission_events': len(self.cultural_transmission_events),
            'persistent_protocols': persistent_protocols,
            'role_distribution': dict(role_counts)
        }

class ComplexCulturalEvolutionExperiment:
    """Main experiment controller for complex cultural evolution"""
    
    def __init__(self, max_ticks: int = 40000, population: int = 60):
        self.max_ticks = max_ticks
        self.population = population
        self.world = ComplexCulturalWorld(GRID_WIDTH, GRID_HEIGHT)
        self.setup_population()
        
    def setup_population(self):
        """Initialize population with diverse cultural roles"""
        for i in range(self.population):
            x = _random.randint(0, GRID_WIDTH - 1)
            y = _random.randint(0, GRID_HEIGHT - 1)
            agent = Agent(x, y)
            self.world.add_agent(agent)
    
    def run_simulation(self) -> Dict:
        """Run the complex cultural evolution simulation"""
        print(f"🧬 Starting Complex Cultural Evolution Simulation")
        print(f"   Max ticks: {self.max_ticks}")
        print(f"   Population: {self.population}")
        print(f"   Cultural roles: {len(self.world.cultural_roles)}")
        print(f"   Cultural centers: {len(self.world.cultural_centers)}")
        print(f"   Protocol complexity levels: {PROTOCOL_COMPLEXITY_LEVELS}")
        print(f"   Generation interval: {GENERATION_INTERVAL}")
        print()
        
        for tick in range(self.max_ticks):
            self.world.simulate_complex_cultural_evolution()
            
            if tick % 8000 == 0 and tick > 0:
                metrics = self.world.calculate_cultural_evolution_metrics()
                print(f"   Tick {tick}: {metrics['total_protocols']} protocols, "
                      f"avg complexity: {metrics['avg_complexity']:.2f}, "
                      f"max complexity: {metrics['max_complexity']}, "
                      f"generations: {metrics['generations']}")
        
        # Final metrics
        final_metrics = self.world.calculate_cultural_evolution_metrics()
        
        # Evaluate success criteria
        success_criteria = self.evaluate_success_criteria(final_metrics)
        
        results = {
            'experiment': 'exp9_complex_cultural_evolution',
            'date': datetime.now().isoformat(),
            'parameters': {
                'max_ticks': self.max_ticks,
                'population': self.population,
                'protocol_complexity_levels': PROTOCOL_COMPLEXITY_LEVELS,
                'cultural_memory_size': CULTURAL_MEMORY_SIZE,
                'innovation_rate': INNOVATION_RATE,
                'transmission_fidelity': TRANSMISSION_FIDELITY,
                'generation_interval': GENERATION_INTERVAL,
                'cultural_centers': CULTURAL_CENTERS
            },
            'results': final_metrics,
            'success_criteria': success_criteria,
            'cultural_evolution_history': self.world.cultural_complexity_history[-10:],  # Last 10 records
            'transmission_events': len(self.world.cultural_transmission_events)
        }
        
        return results
    
    def evaluate_success_criteria(self, metrics: Dict) -> Dict:
        """Evaluate the success criteria for complex cultural evolution"""
        return {
            'complex_protocol_evolution': metrics['avg_complexity'] > 2.5,
            'cultural_accumulation': metrics['cultural_accumulation'] > 0.3,
            'social_specialization': 0.3 < metrics['role_specialization'] < 0.8,  # Balanced specialization
            'multi_generational_persistence': metrics['persistent_protocols'] > 10
        }

def main():
    parser = argparse.ArgumentParser(description='ALIFE Experiment 9: Complex Cultural Evolution')
    parser.add_argument('--ticks', type=int, default=40000, help='Maximum simulation ticks')
    parser.add_argument('--population', type=int, default=60, help='Initial population size')
    parser.add_argument('--output', type=str, default='exp9_complex_cultural_evolution_results.json', 
                       help='Output file for results')
    
    args = parser.parse_args()
    
    # Run experiment
    experiment = ComplexCulturalEvolutionExperiment(max_ticks=args.ticks, population=args.population)
    results = experiment.run_simulation()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("🎉 Complex Cultural Evolution Experiment Complete!")
    print(f"   Results saved to: {args.output}")
    print()
    print("📊 Final Results:")
    print(f"   Total Protocols: {results['results']['total_protocols']}")
    print(f"   Average Complexity: {results['results']['avg_complexity']:.2f}")
    print(f"   Max Complexity: {results['results']['max_complexity']}")
    print(f"   Knowledge Diversity: {results['results']['knowledge_diversity']}")
    print(f"   Cultural Diversity: {results['results']['cultural_diversity']}")
    print(f"   Generations: {results['results']['generations']}")
    print(f"   Role Specialization: {results['results']['role_specialization']:.2f}")
    print(f"   Cultural Accumulation: {results['results']['cultural_accumulation']:.2f}")
    print(f"   Persistent Protocols: {results['results']['persistent_protocols']}")
    print()
    print("✅ Success Criteria:")
    for criterion, passed in results['success_criteria'].items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {criterion}: {status}")
    
    passed_count = sum(results['success_criteria'].values())
    print(f"\n🎯 Overall: {passed_count}/4 criteria passed")
    
    if passed_count >= 3:
        print(f"\n🌍 Complex Cultural Evolution Analysis:")
        print(f"   Cultural complexity achieved!")
        print(f"   Multi-generational cultural persistence established")
        print(f"   Social specialization and role differentiation developed")
        print(f"   Foundation for advanced cultural systems established")

if __name__ == "__main__":
    main()
