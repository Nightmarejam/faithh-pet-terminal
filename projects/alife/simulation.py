"""
ALIFE Simulation — Main loop, tick(), reproduce(), mutate()
"""

import random
import argparse
from typing import List, Optional

from config import (
    INITIAL_POPULATION, MAX_POPULATION, BASELINE_DRAIN,
    POINT_MUTATION_RATE, BYTE_SWAP_RATE, GENOME_LENGTH,
    REPRODUCTION_THRESHOLD, LOG_INTERVAL, RANDOM_SEED,
    CURRENT_EXPERIMENT, SENSE_THREAT_RANGE
)
from world import World, WaveState
from agent import Agent
from ops import (
    get_sense_op, get_process_op, get_memory_op, get_act_op, get_regulate_op,
    get_op_cost
)


class Simulation:
    """Main simulation controller."""
    
    def __init__(self, experiment: int = 0, seed: Optional[int] = None):
        self.experiment = experiment
        
        # Set random seed for reproducibility
        if seed is not None:
            random.seed(seed)
        elif RANDOM_SEED is not None:
            random.seed(RANDOM_SEED)
        
        self.world = World()
        self.total_ticks = 0
        self.total_reproductions = 0
        self.total_deaths = 0
        
    def initialize_population(self, count: int = INITIAL_POPULATION, seed_reproduce: bool = True) -> None:
        """Spawn initial population with random genomes and positions.
        
        Args:
            count: Total number of agents to spawn
            seed_reproduce: If True, ALL agents get ACT_REPRODUCE in A0 (for Exp 0 energy testing)
        """
        spawned = 0
        attempts = 0
        max_attempts = count * 10
        
        while spawned < count and attempts < max_attempts:
            x = random.randint(0, self.world.width - 1)
            y = random.randint(0, self.world.height - 1)
            
            # Create agent with random genome
            agent = Agent(x, y)
            
            # For Exp 0: ALL agents get ACT_REPRODUCE and ACT_CONSUME
            # This removes genome lottery from energy economics testing
            if seed_reproduce:
                genome_list = list(agent.genome)
                genome_list[5] = 0x04  # A0 slot = ACT_REPRODUCE
                genome_list[6] = 0x02  # A1 slot = ACT_CONSUME
                agent.genome = bytes(genome_list)
            
            if self.world.add_agent(agent):
                spawned += 1
            attempts += 1
        
        reproduce_note = " (all with ACT_REPRODUCE in A0)" if seed_reproduce else ""
        print(f"Initialized {spawned} agents{reproduce_note}")
    
    def tick(self) -> None:
        """Execute one simulation tick."""
        # Track population for assertion
        prev_population = self.world.get_population()
        prev_births = self.total_reproductions
        prev_deaths = self.total_deaths
        
        self.world.advance_tick()
        self.total_ticks += 1
        
        # Regenerate world energy
        self.world.regenerate_energy()
        
        # Process predator wave if active
        self.world.apply_predator_wave()
        
        # Process each agent
        agents = list(self.world.agents.values())
        random.shuffle(agents)  # Randomize execution order
        
        for agent in agents:
            if not agent.alive:
                continue
            
            # Decrement reproduction cooldown
            if agent.reproduction_cooldown > 0:
                agent.reproduction_cooldown -= 1
            
            # Reset per-tick state
            agent.reset_tick_state()
            
            # Apply baseline energy drain
            agent.apply_energy_cost(BASELINE_DRAIN)
            if not agent.alive:
                self._handle_death(agent)
                continue
            
            # Passive consumption — involuntary metabolism
            # Agents absorb small amount from cell automatically each tick
            passive_gain = min(self.world.get_cell_energy(agent.x, agent.y), 5)
            agent.add_energy(passive_gain)
            self.world.reduce_cell_energy(agent.x, agent.y, passive_gain)
            
            # Execute genome
            self._execute_genome(agent)
            
            # Check if agent died during genome execution
            if not agent.alive:
                self._handle_death(agent)
                continue
            
            # Age the agent
            agent.tick_age()
        
        # Process reproduction queue
        self._process_reproductions()
        
        # Remove dead agents
        self._cleanup_dead()
        
        # Population accounting assertion
        new_births = self.total_reproductions - prev_births
        new_deaths = self.total_deaths - prev_deaths
        current_population = self.world.get_population()
        expected_population = prev_population + new_births - new_deaths
        assert current_population == expected_population, \
            f"Population mismatch: expected {expected_population}, got {current_population} " \
            f"(prev={prev_population}, births={new_births}, deaths={new_deaths})"
    
    def _execute_genome(self, agent: Agent) -> None:
        """Execute agent's genome instructions.
        
        Conditional op costs: ops only cost energy when they actually fire.
        - SENSE ops: always free
        - PROCESS ops: cost only when condition is TRUE
        - MEMORY ops: cost only when new data is stored
        - ACT ops: cost only when action actually executes
        - REGULATE ops: cost only when regulation condition is met
        """
        # Get regulation modifiers first (free to check)
        reg_op = get_regulate_op(agent.regulate_op)
        reg_mods = reg_op(agent, self.world)
        cost_modifier = reg_mods.get('cost_modifier', 0)
        
        # REGULATE ops cost only if they produced a modifier
        if reg_mods:
            reg_cost = max(0, get_op_cost('regulate', agent.regulate_op) + cost_modifier)
            agent.apply_energy_cost(reg_cost)
            if not agent.alive:
                return
        
        # Execute sense ops (S0, S1) - always free
        sense_values = []
        for sense_code in agent.sense_ops:
            sense_fn = get_sense_op(sense_code)
            value = sense_fn(agent, self.world)
            sense_values.append(value)
        
        # Execute memory op (M0) - cost only if data changes
        mem_op = get_memory_op(agent.memory_op)
        old_memory_len = len(agent.memory)
        if agent.alive and sense_values:
            mem_op(agent, sense_values[0])
            # Cost only if memory was actually written
            if len(agent.memory) != old_memory_len or (agent.memory and agent.memory[-1] == sense_values[0]):
                mem_cost = max(0, get_op_cost('memory', agent.memory_op) + cost_modifier)
                agent.apply_energy_cost(mem_cost)
                if not agent.alive:
                    return
        
        # Execute process ops (P0, P1) with process-action coupling
        # P0 result drives A0, P1 result drives A1
        # This creates meaningful genome grammar: [P0]→[A0], [P1]→[A1]
        process_fired = [False, False]  # Track which process channels fired
        for i, proc_code in enumerate(agent.process_ops):
            proc_fn = get_process_op(proc_code)
            sense_val = sense_values[i] if i < len(sense_values) else 0
            
            # Check if process condition fires
            if proc_fn(sense_val, agent, self.world):
                process_fired[i] = True
                # Cost only when process actually triggers
                proc_cost = max(0, get_op_cost('process', proc_code) + cost_modifier)
                agent.apply_energy_cost(proc_cost)
                if not agent.alive:
                    return
        
        # Execute act ops with process-action coupling
        # A0 executes only if P0 fired, A1 executes only if P1 fired
        act_ops = agent.act_ops
        for i, act_code in enumerate(act_ops):
            # Only execute if corresponding process channel fired
            if not process_fired[i]:
                continue
            
            act_fn = get_act_op(act_code)
            
            # Track state before action to determine if it actually did something
            old_x, old_y = agent.x, agent.y
            old_shield = agent.shield_active
            old_energy = agent.energy
            
            # Execute the action
            act_fn(agent, self.world)
            agent.record_op_usage(act_code)
            
            # Determine if action actually fired (state changed)
            action_fired = False
            if act_code == 0x00:  # ACT_IDLE - never costs
                action_fired = False
            elif act_code == 0x01:  # ACT_MOVE - cost if moved
                action_fired = (agent.x != old_x or agent.y != old_y)
            elif act_code == 0x02:  # ACT_CONSUME - cost if consumed (energy increased)
                action_fired = (agent.energy > old_energy)
            elif act_code == 0x03:  # ACT_SHIELD - cost if shield activated
                action_fired = agent.shield_active and not old_shield
                if action_fired:
                    agent.last_shield_tick = self.world.tick
                    agent.last_shield_activation = self.world.tick  # For Exp 3 gap tracking
                    # Debug: track which channel triggered Shield
                    agent._shield_triggered_by_channel = i  # 0=P0→A0, 1=P1→A1
            elif act_code == 0x04:  # ACT_REPRODUCE - cost handled in reproduction
                action_fired = False  # Cost is REPRODUCTION_COST, not op cost
            elif act_code == 0x05:  # ACT_SIGNAL - cost if signaling
                action_fired = agent.signaling
            elif act_code == 0x06:  # ACT_TOXIN - cost if toxin active
                action_fired = agent.toxin_active
            elif act_code == 0x07:  # ACT_FLEE - cost if moved
                action_fired = (agent.x != old_x or agent.y != old_y)
            
            # Apply cost only if action actually fired
            if action_fired:
                act_cost = max(0, get_op_cost('act', act_code) + cost_modifier)
                agent.apply_energy_cost(act_cost)
                if not agent.alive:
                    return
    
    def _process_reproductions(self) -> None:
        """Process queued reproduction requests.
        
        Density-dependent reproduction: when population exceeds 500,
        reproduction threshold increases by 1 for every 10 agents above 500.
        MAX_POPULATION=2000 serves as emergency hard cap only.
        """
        current_pop = self.world.get_population()
        
        # Emergency hard cap
        if current_pop >= MAX_POPULATION:
            self.world.reproduction_queue.clear()
            return
        
        # Density-dependent threshold increase (kicks in at 150 agents)
        # Prevents bottleneck while still controlling population explosion
        density_penalty = max(0, (current_pop - 150) // 5)
        effective_threshold = REPRODUCTION_THRESHOLD + density_penalty
        
        for parent in self.world.reproduction_queue:
            if not parent.alive:
                continue
            if parent.energy < effective_threshold:
                continue
            
            # Find empty adjacent cell
            spawn_pos = self.world.find_empty_adjacent(parent.x, parent.y)
            if spawn_pos is None:
                continue
            
            # Create mutated genome
            child_genome = self._mutate_genome(parent.genome)
            
            # Spawn child
            child = parent.create_child(spawn_pos[0], spawn_pos[1], child_genome)
            if self.world.add_agent(child):
                self.total_reproductions += 1
                # Set reproduction cooldown (prevents energy drain cascade)
                parent.reproduction_cooldown = 20
        
        self.world.reproduction_queue.clear()
    
    def _mutate_genome(self, genome: bytes) -> bytes:
        """Apply mutations to genome.
        
        Slot-specific mutation rates (stabilizing selection on adaptive traits):
        - Slots 0,1 (S0,S1): 0.1% — sense slots define strategy
        - Slots 2,3 (P0,P1): 0.5% — processing can vary freely
        - Slot 4 (M0):       0.5% — memory can vary freely
        - Slots 5,6 (A0,A1): 0.1% — action slots define strategy
        - Slot 7 (R0):       0.5% — regulation can vary freely
        """
        genome_list = list(genome)
        
        # Slot-specific mutation rates
        # Strategy-defining slots (sense, act) mutate slowly
        # Process slots mutate faster for prediction co-evolution with memory
        SLOT_MUTATION_RATES = [
            0.001,  # S0 - 0.1%
            0.001,  # S1 - 0.1%
            0.010,  # P0 - 1.0% (increased for Exp 3 prediction co-evolution)
            0.010,  # P1 - 1.0% (increased for Exp 3 prediction co-evolution)
            0.005,  # M0 - 0.5%
            0.001,  # A0 - 0.1%
            0.001,  # A1 - 0.1%
            0.005,  # R0 - 0.5%
        ]
        
        # Point mutations with slot-specific rates
        for i in range(len(genome_list)):
            mutation_rate = SLOT_MUTATION_RATES[i]
            
            if random.random() < mutation_rate:
                genome_list[i] = random.randint(0, 7)
        
        # Byte swap (within same category pairs)
        if random.random() < BYTE_SWAP_RATE:
            # Swap within sense pair (0,1) or process pair (2,3) or act pair (5,6)
            pairs = [(0, 1), (2, 3), (5, 6)]
            pair = random.choice(pairs)
            genome_list[pair[0]], genome_list[pair[1]] = genome_list[pair[1]], genome_list[pair[0]]
        
        return bytes(genome_list)
    
    def _handle_death(self, agent: Agent) -> None:
        """Unified death handler - the ONLY place agents should be counted as dead."""
        # Agent is already marked dead by apply_energy_cost, just count it
        # Use a flag to prevent double-counting
        if not hasattr(agent, '_death_counted') or not agent._death_counted:
            agent._death_counted = True
            self.total_deaths += 1
    
    def _cleanup_dead(self) -> None:
        """Remove dead agents from world."""
        dead_agents = [a for a in self.world.agents.values() if not a.alive]
        for agent in dead_agents:
            self.world.remove_agent(agent)
    
    def check_wave_detection(self, wave: WaveState, current_tick: int, observer=None) -> List[tuple]:
        """
        For each agent, check if wave front has entered SENSE range.
        Record detection_tick on agent for gap calculation.
        
        Handles both L→R and R→L wave directions (Exp 4+).
        
        Only records gap if Shield was activated DURING the wave window:
        - Wave must be active
        - Shield activation must have occurred after wave spawned
        - Wave must not have reached agent yet at activation time
        
        Returns list of (agent, gap) tuples for agents with negative gaps.
        """
        if wave is None or not wave.active:
            return []
        
        negative_gaps = []
        front = wave.front_position(current_tick)
        direction = getattr(wave, 'direction', 'left_to_right')
        
        for agent in self.world.agents.values():
            if not agent.alive:
                continue
            
            # Wave is detectable when front is within SENSE_THREAT_RANGE
            if direction == 'left_to_right':
                detectable_column = agent.x - SENSE_THREAT_RANGE
                wave_detectable = front >= detectable_column
            else:  # right_to_left
                detectable_column = agent.x + SENSE_THREAT_RANGE
                wave_detectable = front <= detectable_column
            
            if wave_detectable:
                # Check if this is first detection of this wave for this agent
                # Use (start_tick, direction) as unique wave key to handle dual waves
                wave_key = (wave.start_tick, direction)
                if agent.wave_detected != wave_key:
                    agent.wave_detected = wave_key
                    agent.wave_detection_tick = current_tick
                    
                    # Calculate anticipation gap if Shield was activated DURING wave window
                    # Shield activation must be after wave spawned to count
                    if agent.last_shield_activation is not None:
                        shield_tick = agent.last_shield_activation
                        
                        # Only count if Shield activated after this wave spawned
                        if shield_tick >= wave.start_tick:
                            # gap = shield_tick - detection_tick
                            # Positive = reactive (shield after detection)
                            # Negative = ANTICIPATORY (shield before detection)
                            gap = shield_tick - current_tick
                            agent.anticipation_gaps.append(gap)
                            
                            # Calculate position-adjusted gap
                            if direction == 'left_to_right':
                                position_warning = (agent.x - SENSE_THREAT_RANGE) / wave.speed
                            else:
                                position_warning = (SENSE_THREAT_RANGE - agent.x + self.world.width) / wave.speed
                            position_warning = max(1, position_warning)
                            adjusted_gap = gap / position_warning
                            agent.position_adjusted_gaps.append(adjusted_gap)
                            
                            # If gap is negative — anticipatory behavior!
                            if gap < 0:
                                negative_gaps.append((agent, gap))
        
        return negative_gaps
    
    def calculate_anticipation_gap(self, agent: Agent, wave_detection_tick: int) -> Optional[float]:
        """
        Calculate anticipation gap for an agent.
        gap > 0: reactive (shield after detection)
        gap = 0: simultaneous  
        gap < 0: ANTICIPATORY (shield before detection) — FLAG THIS
        """
        if agent.last_shield_activation is None:
            return None
        
        gap = wave_detection_tick - agent.last_shield_activation
        return gap
    
    def run(self, ticks: int, log_interval: int = LOG_INTERVAL) -> None:
        """Run simulation for specified number of ticks."""
        print(f"Starting simulation: experiment={self.experiment}, ticks={ticks}")
        
        for t in range(ticks):
            self.tick()
            
            if (t + 1) % log_interval == 0:
                pop = self.world.get_population()
                print(f"Tick {t + 1}: population={pop}, births={self.total_reproductions}, deaths={self.total_deaths}")
        
        print(f"\nSimulation complete.")
        print(f"Final population: {self.world.get_population()}")
        print(f"Total reproductions: {self.total_reproductions}")
        print(f"Total deaths: {self.total_deaths}")


def main():
    parser = argparse.ArgumentParser(description='ALIFE Simulation')
    parser.add_argument('--experiment', type=int, default=0, help='Experiment number (0-5)')
    parser.add_argument('--ticks', type=int, default=100, help='Number of ticks to run')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--population', type=int, default=INITIAL_POPULATION, help='Initial population')
    
    args = parser.parse_args()
    
    sim = Simulation(experiment=args.experiment, seed=args.seed)
    sim.initialize_population(args.population)
    sim.run(args.ticks)


if __name__ == '__main__':
    main()
