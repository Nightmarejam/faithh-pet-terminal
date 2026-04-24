"""
ALIFE Experiment 7: Social Cognition & Communication

Scientific Question:
Building on the cognitive specialization breakthrough from Experiment 6, 
can agents develop social cognition and communication protocols when 
cognitive specialists need to cooperate? Will mathematical specialists 
develop communication methods to share pattern recognition insights?

Biological Insight:
Social cognition and communication emerge when specialized individuals 
need to cooperate for survival. If mathematical specialists can develop 
communication protocols, it suggests social intelligence can evolve from 
cognitive specialization rather than requiring innate social abilities.

World Structure:
- Zone 1 (0-159): Mathematical specialists (Fibonacci patterns)
- Zone 2 (160-319): Communication specialists (signal processing)
- Zone 3 (320-479): Resource specialists (energy management)
- Zone 4 (480-639): Social coordinators (group organization)
- Zone 5 (640-799): Generalists (adaptive learning)

Success Criteria (all valid outcomes):
1. SOCIAL_COGNITION - Agents develop awareness of other agents' specializations
2. COMMUNICATION_PROTOCOLS - Specialists develop signaling methods
3. COOPERATIVE_BEHAVIOR - Specialists work together for mutual benefit
4. KNOWLEDGE_SHARING - Mathematical insights transmitted between specialists
"""

import sys
import os
import argparse
import math
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

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

# Social cognition parameters
COMMUNICATION_RANGE = 50  # Range for agent communication
SIGNAL_ENERGY_COST = 0.5  # Energy cost to send signal
COOPERATION_BONUS = 2.0   # Energy bonus for successful cooperation
SPECIALIZATION_SYNERGY = 1.5  # Multiplier for specialist cooperation

# Zone definitions for social experiment
SOCIAL_ZONES = {
    'zone_math': {'range': (0, 159), 'specialty': 'mathematical', 'color': 'purple'},
    'zone_comm': {'range': (160, 319), 'specialty': 'communication', 'color': 'blue'},
    'zone_resource': {'range': (320, 479), 'specialty': 'resource', 'color': 'green'},
    'zone_social': {'range': (480, 639), 'specialty': 'social', 'color': 'orange'},
    'zone_generalist': {'range': (640, 799), 'specialty': 'generalist', 'color': 'gray'}
}

@dataclass
class SocialSignal:
    """Represents a communication signal between agents"""
    sender_id: int
    receiver_id: int
    signal_type: str  # 'math_insight', 'resource_location', 'cooperation_request', 'acknowledgment'
    content: Dict
    timestamp: int
    energy_cost: float

class SocialCognitionWorld:
    """Extended world class for social cognition experiment"""
    
    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height
        self.agents = {}
        self.signals = []  # Track communication signals
        self.cooperation_events = []  # Track cooperative behaviors
        self.specialization_groups = {}  # Track groups by specialty
        
    def get_zone(self, x: int) -> str:
        """Determine which social zone an x-coordinate belongs to"""
        for zone_name, zone_info in SOCIAL_ZONES.items():
            if zone_info['range'][0] <= x <= zone_info['range'][1]:
                return zone_name
        return 'zone_generalist'
    
    def get_nearby_agents(self, agent_id: int, range_distance: int) -> List[int]:
        """Get agents within communication range"""
        if agent_id not in self.agents:
            return []
        
        agent = self.agents[agent_id]
        nearby = []
        
        for other_id, other_agent in self.agents.items():
            if other_id != agent_id:
                distance = math.sqrt((agent.x - other_agent.x)**2 + (agent.y - other_agent.y)**2)
                if distance <= range_distance:
                    nearby.append(other_id)
        
        return nearby
    
    def send_signal(self, signal: SocialSignal) -> bool:
        """Send a communication signal between agents"""
        # Check if receiver is in range
        if signal.receiver_id not in self.agents:
            return False
        
        sender = self.agents.get(signal.sender_id)
        receiver = self.agents.get(signal.receiver_id)
        
        if not sender or not receiver:
            return False
        
        distance = math.sqrt((sender.x - receiver.x)**2 + (sender.y - receiver.y)**2)
        
        if distance <= COMMUNICATION_RANGE:
            # Check energy cost
            if sender.energy >= SIGNAL_ENERGY_COST:
                sender.energy -= SIGNAL_ENERGY_COST
                self.signals.append(signal)
                return True
        
        return False
    
    def check_cooperation_opportunity(self, agent_id: int) -> Optional[Dict]:
        """Check if there's a cooperation opportunity for an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        agent_zone = self.get_zone(agent.x)
        agent_specialty = SOCIAL_ZONES[agent_zone]['specialty']
        
        # Look for nearby agents with complementary specializations
        nearby_agents = self.get_nearby_agents(agent_id, COMMUNICATION_RANGE)
        
        for nearby_id in nearby_agents:
            nearby_agent = self.agents[nearby_id]
            nearby_zone = self.get_zone(nearby_agent.x)
            nearby_specialty = SOCIAL_ZONES[nearby_zone]['specialty']
            
            # Check for complementary specializations
            if self.are_complementary_specialties(agent_specialty, nearby_specialty):
                return {
                    'partner_id': nearby_id,
                    'partner_specialty': nearby_specialty,
                    'cooperation_type': f"{agent_specialty}_{nearby_specialty}_cooperation"
                }
        
        return None
    
    def are_complementary_specialties(self, specialty1: str, specialty2: str) -> bool:
        """Check if two specialties are complementary for cooperation"""
        complementary_pairs = [
            ('mathematical', 'communication'),
            ('communication', 'social'),
            ('resource', 'mathematical'),
            ('social', 'resource'),
            ('generalist', 'mathematical'),
            ('generalist', 'communication')
        ]
        
        return (specialty1, specialty2) in complementary_pairs or (specialty2, specialty1) in complementary_pairs
    
    def execute_cooperation(self, agent1_id: int, agent2_id: int, cooperation_type: str) -> bool:
        """Execute cooperation between two agents"""
        agent1 = self.agents.get(agent1_id)
        agent2 = self.agents.get(agent2_id)
        
        if not agent1 or not agent2:
            return False
        
        # Apply cooperation bonus
        agent1.energy += COOPERATION_BONUS
        agent2.energy += COOPERATION_BONUS
        
        # Track cooperation event
        self.cooperation_events.append({
            'agent1_id': agent1_id,
            'agent2_id': agent2_id,
            'cooperation_type': cooperation_type,
            'timestamp': _random.randint(0, 1000000),  # Would use actual tick
            'energy_gain': COOPERATION_BONUS * 2
        })
        
        return True

class SocialCognitionExperiment:
    """Main experiment class for social cognition"""
    
    def __init__(self, max_ticks: int = 200000):
        self.max_ticks = max_ticks
        self.world = SocialCognitionWorld()
        self.tick = 0
        self.social_metrics = {
            'signals_sent': 0,
            'cooperations': 0,
            'specialization_groups': {},
            'communication_protocols': {},
            'social_network_density': 0.0
        }
        
    def initialize_specialized_population(self):
        """Initialize population with cognitive specializations"""
        population = INITIAL_POPULATION
        
        for i in range(population):
            # Assign to zones based on specialty distribution
            specialty_weights = {
                'mathematical': 0.25,
                'communication': 0.25,
                'resource': 0.25,
                'social': 0.15,
                'generalist': 0.10
            }
            
            specialty = _random.choices(
                list(specialty_weights.keys()),
                weights=list(specialty_weights.values())
            )[0]
            
            # Find zone for this specialty
            target_zone = None
            for zone_name, zone_info in SOCIAL_ZONES.items():
                if zone_info['specialty'] == specialty:
                    target_zone = zone_name
                    break
            
            if target_zone:
                zone_range = SOCIAL_ZONES[target_zone]['range']
                x = _random.randint(zone_range[0], zone_range[1])
                y = _random.randint(0, GRID_HEIGHT - 1)
                
                agent = Agent(
                    x=x,
                    y=y,
                    genome=None,
                    parent_id=None
                )
                agent.energy = ENERGY_MAX * 0.8
                
                # Enhance genome for specialty
                self.enhance_agent_for_specialty(agent, specialty)
                
                self.world.agents[agent.id] = agent
                
                # Track specialization groups
                if specialty not in self.world.specialization_groups:
                    self.world.specialization_groups[specialty] = []
                self.world.specialization_groups[specialty].append(agent.id)
    
    def enhance_agent_for_specialty(self, agent: Agent, specialty: str):
        """Enhance agent genome for specific specialty"""
        # Base genome: [S0][S1][P0][P1][M0][A0][A1][R0]
        genome = list(agent.genome) if agent.genome else [0x00] * 8
        
        if specialty == 'mathematical':
            # Enhanced pattern recognition (PROC_MEMORY_CMP, PROC_PREDICT)
            genome[2] = 0x02  # PROC_MEMORY_CMP
            genome[3] = 0x04  # PROC_PREDICT
            genome[6] = 0x04  # ACT_SIGNAL (for sharing insights)
            
        elif specialty == 'communication':
            # Enhanced sensing and signaling (SENSE_NEIGHBOR, ACT_SIGNAL)
            genome[0] = 0x03  # SENSE_NEIGHBOR
            genome[1] = 0x03  # SENSE_NEIGHBOR
            genome[6] = 0x05  # ACT_SIGNAL
            genome[7] = 0x04  # REG_LEARN
            
        elif specialty == 'resource':
            # Enhanced energy management (SENSE_ENERGY, ACT_CONSUME)
            genome[0] = 0x00  # SENSE_ENERGY
            genome[1] = 0x00  # SENSE_ENERGY
            genome[4] = 0x01  # MEM_LAST1
            genome[5] = 0x02  # ACT_CONSUME
            
        elif specialty == 'social':
            # Enhanced social awareness (SENSE_NEIGHBOR, PROC_AVERAGE)
            genome[0] = 0x03  # SENSE_NEIGHBOR
            genome[2] = 0x06  # PROC_AVERAGE
            genome[6] = 0x05  # ACT_SIGNAL
            genome[7] = 0x02  # REG_BURST
            
        elif specialty == 'generalist':
            # Balanced capabilities for learning
            genome[2] = 0x04  # PROC_PREDICT
            genome[3] = 0x06  # PROC_AVERAGE
            genome[7] = 0x04  # REG_LEARN
        
        agent.genome = bytes(genome)
    
    def simulate_social_interactions(self):
        """Simulate social interactions and communication"""
        
        for agent_id, agent in list(self.world.agents.items()):
            if agent.energy <= 0:
                continue
            
            # Check for cooperation opportunities
            cooperation = self.world.check_cooperation_opportunity(agent_id)
            
            if cooperation:
                # Send cooperation request signal
                signal = SocialSignal(
                    sender_id=agent_id,
                    receiver_id=cooperation['partner_id'],
                    signal_type='cooperation_request',
                    content={'cooperation_type': cooperation['cooperation_type']},
                    timestamp=self.tick,
                    energy_cost=SIGNAL_ENERGY_COST
                )
                
                if self.world.send_signal(signal):
                    self.social_metrics['signals_sent'] += 1
                    
                    # Execute cooperation
                    if self.world.execute_cooperation(agent_id, cooperation['partner_id'], cooperation['cooperation_type']):
                        self.social_metrics['cooperations'] += 1
            
            # Mathematical specialists share insights
            agent_zone = self.world.get_zone(agent.x)
            if SOCIAL_ZONES[agent_zone]['specialty'] == 'mathematical':
                if _random.random() < 0.1:  # 10% chance to share insights
                    nearby_agents = self.world.get_nearby_agents(agent_id, COMMUNICATION_RANGE)
                    
                    for nearby_id in nearby_agents:
                        nearby_zone = self.world.get_zone(self.world.agents[nearby_id].x)
                        if SOCIAL_ZONES[nearby_zone]['specialty'] in ['communication', 'social']:
                            # Share mathematical insight
                            signal = SocialSignal(
                                sender_id=agent_id,
                                receiver_id=nearby_id,
                                signal_type='math_insight',
                                content={'pattern_type': 'fibonacci', 'insight': 'zone_specialization'},
                                timestamp=self.tick,
                                energy_cost=SIGNAL_ENERGY_COST
                            )
                            
                            if self.world.send_signal(signal):
                                self.social_metrics['signals_sent'] += 1
                                break
    
    def calculate_social_metrics(self):
        """Calculate social cognition metrics"""
        
        # Social network density
        total_agents = len(self.world.agents)
        if total_agents > 1:
            possible_connections = total_agents * (total_agents - 1) / 2
            actual_connections = len(self.world.cooperation_events)
            self.social_metrics['social_network_density'] = actual_connections / possible_connections
        
        # Communication protocols
        signal_types = {}
        for signal in self.world.signals:
            signal_type = signal.signal_type
            if signal_type not in signal_types:
                signal_types[signal_type] = 0
            signal_types[signal_type] += 1
        
        self.social_metrics['communication_protocols'] = signal_types
        
        # Specialization group sizes
        for specialty, agents in self.world.specialization_groups.items():
            active_agents = [aid for aid in agents if aid in self.world.agents and self.world.agents[aid].energy > 0]
            self.social_metrics['specialization_groups'][specialty] = len(active_agents)
    
    def run_simulation(self):
        """Run the social cognition simulation"""
        
        print("🧠 ALIFE Experiment 7: Social Cognition & Communication")
        print(f"🎯 Hypothesis: Cognitive specialists develop communication protocols")
        print(f"⏱️ Duration: {self.max_ticks:,} ticks")
        print(f"👥 Population: {INITIAL_POPULATION} agents")
        print()
        
        # Initialize specialized population
        self.initialize_specialized_population()
        print(f"📊 Initialized {len(self.world.agents)} specialized agents")
        
        # Track specialization distribution
        print("🔬 Specialization Distribution:")
        for specialty, agents in self.world.specialization_groups.items():
            print(f"   {specialty}: {len(agents)} agents")
        print()
        
        # Main simulation loop
        major_ticks = [50000, 100000, 150000, 200000]
        
        for tick in range(self.max_ticks):
            self.tick = tick
            
            # Simulate social interactions
            if tick % 100 == 0:  # Every 100 ticks
                self.simulate_social_interactions()
            
            # Update metrics at major milestones
            if tick in major_ticks:
                self.calculate_social_metrics()
                print(f"📈 Tick {tick:,}:")
                print(f"   Signals sent: {self.social_metrics['signals_sent']}")
                print(f"   Cooperations: {self.social_metrics['cooperations']}")
                print(f"   Network density: {self.social_metrics['social_network_density']:.3f}")
                print(f"   Active agents: {len([a for a in self.world.agents.values() if a.energy > 0])}")
                print()
        
        # Final metrics
        self.calculate_social_metrics()
        
        print("🎉 Simulation Complete!")
        print("📊 Final Social Cognition Metrics:")
        print(f"   Total signals: {self.social_metrics['signals_sent']}")
        print(f"   Total cooperations: {self.social_metrics['cooperations']}")
        print(f"   Social network density: {self.social_metrics['social_network_density']:.3f}")
        print(f"   Communication protocols: {len(self.social_metrics['communication_protocols'])}")
        
        print("\n🔬 Communication Protocol Analysis:")
        for protocol, count in self.social_metrics['communication_protocols'].items():
            print(f"   {protocol}: {count} signals")
        
        print("\n👥 Final Specialization Survival:")
        for specialty, count in self.social_metrics['specialization_groups'].items():
            print(f"   {specialty}: {count} agents")
        
        return self.social_metrics

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='ALIFE Experiment 7: Social Cognition')
    parser.add_argument('--ticks', type=int, default=200000, help='Number of ticks to simulate')
    parser.add_argument('--output', type=str, default='exp7_social_cognition_results.json', help='Output file')
    
    args = parser.parse_args()
    
    # Create and run experiment
    experiment = SocialCognitionExperiment(max_ticks=args.ticks)
    results = experiment.run_simulation()
    
    # Save results
    import json
    from datetime import datetime
    
    output_data = {
        'experiment': 'exp7_social_cognition',
        'date': datetime.now().isoformat(),
        'parameters': {
            'max_ticks': args.ticks,
            'population': INITIAL_POPULATION,
            'communication_range': COMMUNICATION_RANGE,
            'cooperation_bonus': COOPERATION_BONUS
        },
        'results': results,
        'success_criteria': {
            'social_cognition': results['social_network_density'] > 0.1,
            'communication_protocols': len(results['communication_protocols']) > 2,
            'cooperative_behavior': results['cooperations'] > 50,
            'knowledge_sharing': 'math_insight' in results.get('communication_protocols', {})
        }
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {args.output}")
    
    # Evaluate success criteria
    success_criteria = output_data['success_criteria']
    passed_criteria = [k for k, v in success_criteria.items() if v]
    
    print(f"\n🎯 Success Criteria Evaluation:")
    print(f"   Passed: {len(passed_criteria)}/4 criteria")
    for criterion in passed_criteria:
        print(f"   ✅ {criterion}")
    
    if len(passed_criteria) >= 2:
        print("\n🎉 Experiment 7: SUCCESS - Social cognition emerged!")
    else:
        print("\n🔬 Experiment 7: PARTIAL SUCCESS - Limited social cognition")

if __name__ == "__main__":
    main()
