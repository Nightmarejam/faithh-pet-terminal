"""
ALIFE World — 160x120 grid, 4-byte cells, energy regeneration
"""

import random
from typing import Optional, List, Tuple, TYPE_CHECKING
from config import (
    GRID_WIDTH, GRID_HEIGHT, ENERGY_MAX, THREAT_MAX, LIGHT_MAX,
    ENERGY_REGEN_RATE, REGEN_INTERVAL, PREDATOR_DAMAGE, SHIELD_COST,
    THERMAL_DRAIN_RATE, WAVE_SPEED_C, WAVE_SPEED_VARIANCE, SENSE_THREAT_RANGE,
    STEALTH_WAVE_PROBABILITY, STEALTH_WAVE_DAMAGE, NUM_ENERGY_SOURCES,
    ENERGY_SOURCE_RADIUS, ENERGY_SOURCE_STRENGTH
)

if TYPE_CHECKING:
    from agent import Agent


class WaveState:
    """Represents a propagating predator wave with finite speed."""
    
    def __init__(self, start_tick: int, speed: float, stealth: bool = False,
                 direction: str = 'left_to_right'):
        self.start_tick = start_tick
        self.speed = speed  # columns per tick (varied per wave)
        self.active = True
        self.stealth = stealth  # stealth waves are undetectable via SENSE_THREAT
        self.direction = direction  # 'left_to_right' or 'right_to_left' (Exp 4+)
    
    def front_position(self, current_tick: int) -> float:
        """Current leading edge of wave in column units."""
        elapsed = current_tick - self.start_tick
        if self.direction == 'left_to_right':
            return elapsed * self.speed
        else:  # right_to_left
            return GRID_WIDTH - (elapsed * self.speed)
    
    def has_reached_column(self, col: int, current_tick: int) -> bool:
        """Has wave front reached this column?"""
        if self.direction == 'left_to_right':
            return self.front_position(current_tick) >= col
        else:  # right_to_left
            return self.front_position(current_tick) <= col
    
    def is_complete(self, current_tick: int) -> bool:
        """Has wave passed entire world?"""
        if self.direction == 'left_to_right':
            return self.front_position(current_tick) >= GRID_WIDTH
        else:  # right_to_left
            return self.front_position(current_tick) <= 0


class Cell:
    """A single cell in the world grid."""
    __slots__ = ['energy', 'threat', 'light', 'occupant_id']
    
    def __init__(self):
        self.energy: int = random.randint(50, 150)
        self.threat: int = 0
        self.light: int = random.randint(100, 200)
        self.occupant_id: Optional[str] = None


class World:
    """The simulation world grid."""
    
    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height
        self.tick = 0
        
        # Grid of cells
        self.grid: List[List[Cell]] = [
            [Cell() for _ in range(width)]
            for _ in range(height)
        ]
        
        # Energy source nodes (rich ecological niches)
        self.energy_sources: List[Tuple[int, int]] = []
        self._place_energy_sources()
        
        # Agent registry
        self.agents: dict = {}  # id -> Agent
        
        # Reproduction queue (processed at end of tick)
        self.reproduction_queue: List['Agent'] = []
        
        # Threat state
        self.predator_wave_active = False
        self.predator_x = 0  # Current x position of predator wave
        
        # Multi-wave support (Exp 4+)
        self.active_waves: List[WaveState] = []
    
    def _place_energy_sources(self) -> None:
        """Place energy source nodes randomly across the world."""
        for _ in range(NUM_ENERGY_SOURCES):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.energy_sources.append((x, y))
    
    def _get_regen_rate(self, x: int, y: int) -> int:
        """Get regeneration rate for a cell based on proximity to energy sources."""
        for sx, sy in self.energy_sources:
            dist = abs(x - sx) + abs(y - sy)  # Manhattan distance
            if dist <= ENERGY_SOURCE_RADIUS:
                return ENERGY_SOURCE_STRENGTH
        return ENERGY_REGEN_RATE
        
    def in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_cell(self, x: int, y: int) -> Cell:
        """Get cell at position."""
        return self.grid[y][x]
    
    def get_cell_energy(self, x: int, y: int) -> int:
        """Get energy level at position."""
        return self.grid[y][x].energy
    
    def get_cell_threat(self, x: int, y: int) -> int:
        """Get threat level at position."""
        return self.grid[y][x].threat
    
    def get_cell_light(self, x: int, y: int) -> int:
        """Get light level at position."""
        return self.grid[y][x].light
    
    def get_occupant(self, x: int, y: int) -> Optional['Agent']:
        """Get agent at position, if any."""
        occupant_id = self.grid[y][x].occupant_id
        if occupant_id:
            return self.agents.get(occupant_id)
        return None
    
    def reduce_cell_energy(self, x: int, y: int, amount: int) -> None:
        """Reduce energy at position."""
        self.grid[y][x].energy = max(0, self.grid[y][x].energy - amount)
    
    def add_agent(self, agent: 'Agent') -> bool:
        """Add agent to world. Returns False if position occupied."""
        if self.grid[agent.y][agent.x].occupant_id is not None:
            return False
        
        self.agents[agent.id] = agent
        self.grid[agent.y][agent.x].occupant_id = agent.id
        return True
    
    def remove_agent(self, agent: 'Agent') -> None:
        """Remove agent from world."""
        if agent.id in self.agents:
            self.grid[agent.y][agent.x].occupant_id = None
            del self.agents[agent.id]
    
    def move_agent(self, agent: 'Agent', new_x: int, new_y: int) -> bool:
        """Move agent to new position. Returns False if blocked."""
        if not self.in_bounds(new_x, new_y):
            return False
        if self.grid[new_y][new_x].occupant_id is not None:
            return False
        
        # Clear old position
        self.grid[agent.y][agent.x].occupant_id = None
        
        # Set new position
        agent.x = new_x
        agent.y = new_y
        self.grid[new_y][new_x].occupant_id = agent.id
        
        return True
    
    def request_reproduction(self, agent: 'Agent') -> None:
        """Queue agent for reproduction (processed at end of tick)."""
        self.reproduction_queue.append(agent)
    
    def get_threat_direction(self, x: int, y: int) -> Tuple[Optional[int], Optional[int]]:
        """Get direction of highest threat. Returns (threat_x, threat_y) or (None, None)."""
        max_threat = 0
        threat_pos = (None, None)
        
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    t = self.grid[ny][nx].threat
                    if t > max_threat:
                        max_threat = t
                        threat_pos = (nx, ny)
        
        return threat_pos
    
    def regenerate_energy(self) -> None:
        """Regenerate energy across all cells based on proximity to energy sources."""
        if self.tick % REGEN_INTERVAL != 0:
            return
        
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                regen_rate = self._get_regen_rate(x, y)
                cell.energy = min(ENERGY_MAX, cell.energy + regen_rate)
    
    def clear_threats(self) -> None:
        """Clear all threat values."""
        for row in self.grid:
            for cell in row:
                cell.threat = 0
    
    def apply_predator_wave(self) -> None:
        """Apply predator wave damage (sweeps left to right)."""
        if not self.predator_wave_active:
            return
        
        # Set threat level at predator x position
        for y in range(self.height):
            if self.in_bounds(self.predator_x, y):
                self.grid[y][self.predator_x].threat = THREAT_MAX
                
                # Damage agents at this position
                agent = self.get_occupant(self.predator_x, y)
                if agent and agent.alive:
                    if not agent.shield_active:
                        agent.apply_energy_cost(PREDATOR_DAMAGE)
                    agent.last_threat_sense_tick = self.tick
        
        # Advance predator
        self.predator_x += 1
        if self.predator_x >= self.width:
            self.predator_wave_active = False
            self.predator_x = 0
    
    def start_predator_wave(self) -> None:
        """Start a new predator wave."""
        self.predator_wave_active = True
        self.predator_x = 0
        self.clear_threats()
    
    def trigger_predator_wave(self, tick: int) -> List[Tuple[str, bool, int]]:
        """
        Trigger a predator wave sweep across the entire world in one tick.
        Returns list of (agent_id, shielded, energy_before) tuples for logging.
        
        This is a full-world sweep version for Experiment 1+ where we want
        to process the entire wave at once rather than column-by-column.
        
        Shield check: An agent is considered shielded if they have ACT_SHIELD (0x03)
        in either A0 or A1 slot of their genome. This represents the trait being
        present and active — the agent's genome encodes shield behavior.
        """
        contacts = []
        ACT_SHIELD = 0x03
        
        # Sweep all columns
        for x in range(self.width):
            # Set threat level
            for y in range(self.height):
                self.grid[y][x].threat = THREAT_MAX
                
                # Check for agents
                agent = self.get_occupant(x, y)
                if agent and agent.alive:
                    energy_before = agent.energy
                    # Check if agent has Shield trait in genome (A0 or A1 slot)
                    has_shield_trait = (agent.genome[5] == ACT_SHIELD or 
                                        agent.genome[6] == ACT_SHIELD)
                    
                    if not has_shield_trait:
                        agent.apply_energy_cost(PREDATOR_DAMAGE)
                    else:
                        # Shield blocks predator, cost from config (default 0)
                        if SHIELD_COST > 0:
                            agent.apply_energy_cost(SHIELD_COST)
                        agent.shield_activations = getattr(agent, 'shield_activations', 0) + 1
                    
                    agent.last_threat_sense_tick = tick
                    contacts.append((agent.id, has_shield_trait, energy_before))
        
        return contacts
    
    def get_adjacent_agents(self, x: int, y: int, radius: int = 1) -> List['Agent']:
        """Get all living agents within Manhattan distance radius."""
        nearby = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    occupant = self.get_occupant(nx, ny)
                    if occupant and occupant.alive:
                        nearby.append(occupant)
        return nearby
    
    def find_empty_nearby(self, x: int, y: int, max_radius: int = 3) -> Optional[Tuple[int, int]]:
        """Find an empty cell within radius, spiraling outward from position."""
        for radius in range(1, max_radius + 1):
            candidates = []
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx == 0 and dy == 0:
                        continue
                    # Only check cells at current radius (not inner cells already checked)
                    if abs(dx) == radius or abs(dy) == radius:
                        nx, ny = x + dx, y + dy
                        if self.in_bounds(nx, ny) and self.grid[ny][nx].occupant_id is None:
                            candidates.append((nx, ny))
            if candidates:
                return random.choice(candidates)
        return None
    
    def find_empty_adjacent(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Find an empty cell adjacent to position (legacy, uses find_empty_nearby)."""
        return self.find_empty_nearby(x, y, max_radius=3)
    
    def get_population(self) -> int:
        """Get current population count."""
        return len(self.agents)
    
    def get_alive_agents(self) -> List['Agent']:
        """Get list of all alive agents."""
        return [a for a in self.agents.values() if a.alive]
    
    def advance_tick(self) -> None:
        """Advance world tick counter."""
        self.tick += 1
    
    def initialize_light_gradient(self) -> None:
        """
        Initialize cell light levels as a gradient — high in center, low at edges.
        Center cells have high light (thermal pressure) AND high energy (food).
        Edge cells have low light (thermal safety) AND low energy (food-scarce).
        
        This creates resource tension:
        - Center is profitable but thermally expensive
        - Edges are safe but food-scarce
        - Strategy C can thrive in center with both protection AND better food
        """
        for y in range(self.height):
            for x in range(self.width):
                # Distance from center, normalized 0-1
                cx = abs(x - self.width // 2) / (self.width // 2)
                cy = abs(y - self.height // 2) / (self.height // 2)
                distance_from_center = min(1.0, (cx + cy) / 2)
                # Center = high light (255), edges = low light (50)
                self.grid[y][x].light = int(50 + (205 * (1 - distance_from_center)))
                # Energy proportional to light: center ~210+, edges ~90
                self.grid[y][x].energy = 50 + int(self.grid[y][x].light * 0.8)
    
    def apply_thermal_drain(self, agent: 'Agent') -> float:
        """
        Calculate thermal drain for an agent based on their cell's light level.
        Agents absorb heat from their current cell each tick.
        Disruption phenotype reduces absorption by 70%.
        
        Returns the drain amount (caller applies to agent.energy).
        """
        cell_light = self.get_cell_light(agent.x, agent.y)
        has_disruption = self.agent_has_disruption_phenotype(agent)
        
        base_drain = (cell_light / 255) * THERMAL_DRAIN_RATE
        
        if has_disruption:
            drain = base_drain * 0.3  # 70% reduction
        else:
            drain = base_drain
        
        return drain
    
    def agent_has_disruption_phenotype(self, agent: 'Agent') -> bool:
        """
        Check if agent has Disruption phenotype (Strategy C).
        Disruption phenotype = SENSE_LIGHT in S0 or S1 AND ACT_SHIELD in A0 or A1.
        This is the dual-purpose strategy — thermal awareness combined with predator defense.
        """
        SENSE_LIGHT = 0x02
        ACT_SHIELD = 0x03
        
        has_light_sense = (agent.genome[0] == SENSE_LIGHT or 
                          agent.genome[1] == SENSE_LIGHT)
        has_shield = (agent.genome[5] == ACT_SHIELD or 
                     agent.genome[6] == ACT_SHIELD)
        return has_light_sense and has_shield
    
    def spawn_wave(self, current_tick: int) -> WaveState:
        """
        Spawn a new wave with speed variation.
        Called every PREDATOR_WAVE_INTERVAL ticks.
        30% of waves are stealth — undetectable via SENSE_THREAT.
        """
        speed = WAVE_SPEED_C * (1 + random.gauss(0, WAVE_SPEED_VARIANCE))
        speed = max(0.4, min(1.6, speed))  # clamp to reasonable range
        stealth = random.random() < STEALTH_WAVE_PROBABILITY
        return WaveState(start_tick=current_tick, speed=speed, stealth=stealth,
                         direction='left_to_right')
    
    def spawn_wave_from_right(self, current_tick: int) -> WaveState:
        """
        Spawn a wave from the right edge traveling left (Exp 4+).
        Used for the second wave source in harmonic interference.
        """
        speed = WAVE_SPEED_C * (1 + random.gauss(0, WAVE_SPEED_VARIANCE))
        speed = max(0.4, min(1.6, speed))
        stealth = random.random() < STEALTH_WAVE_PROBABILITY
        return WaveState(start_tick=current_tick, speed=speed, stealth=stealth,
                         direction='right_to_left')
    
    def apply_wave_damage(self, wave: WaveState, current_tick: int) -> List[Tuple[str, bool, float]]:
        """
        Apply damage to agents at the current wave front position.
        Returns list of (agent_id, shielded, position_warning_ticks)
        for FAITHH logging.
        """
        contacts = []
        ACT_SHIELD = 0x03
        front = wave.front_position(current_tick)
        
        # Wave damages agents in a 1-column band at the front
        for agent_id, agent in list(self.agents.items()):
            if not agent.alive:
                continue
            if abs(agent.x - front) < 1.0:
                # Record wave arrival for ALL reached agents (before shield check)
                # Dedup: only record if last arrival was >50 ticks ago
                # (wave front crosses agent over 2-3 consecutive ticks at speed 0.8)
                MIN_ARRIVAL_GAP = 10
                if wave.direction == 'left_to_right':
                    if hasattr(agent, 'wave1_arrival_times'):
                        if not agent.wave1_arrival_times or (current_tick - agent.wave1_arrival_times[-1]) > MIN_ARRIVAL_GAP:
                            agent.wave1_arrival_times.append(current_tick)
                            agent.wave1_arrival_times = agent.wave1_arrival_times[-4:]
                else:
                    if hasattr(agent, 'wave2_arrival_times'):
                        if not agent.wave2_arrival_times or (current_tick - agent.wave2_arrival_times[-1]) > MIN_ARRIVAL_GAP:
                            agent.wave2_arrival_times.append(current_tick)
                            agent.wave2_arrival_times = agent.wave2_arrival_times[-4:]
                                            
                # Record general arrival time (existing) — same dedup
                if not agent.wave_arrival_times or (current_tick - agent.wave_arrival_times[-1]) > MIN_ARRIVAL_GAP:
                    agent.wave_arrival_times.append(current_tick)
                    agent.wave_arrival_times = agent.wave_arrival_times[-8:]
                
                # THEN check shield status
                has_shield = (agent.genome[5] == ACT_SHIELD or 
                             agent.genome[6] == ACT_SHIELD)
                
                # Calculate how much positional warning this agent had
                # = ticks from when wave was detectable to now
                if wave.direction == 'left_to_right':
                    detectable_at = (agent.x - SENSE_THREAT_RANGE) / wave.speed
                else:  # right_to_left
                    detectable_at = (GRID_WIDTH - agent.x - SENSE_THREAT_RANGE) / wave.speed
                warning_ticks = current_tick - (wave.start_tick + detectable_at)
                warning_ticks = max(0, warning_ticks)
                
                if has_shield and agent.shield_active:
                    contacts.append((agent_id, True, warning_ticks))
                else:
                    # Stealth waves deal instant death damage
                    damage = STEALTH_WAVE_DAMAGE if wave.stealth else PREDATOR_DAMAGE
                    agent.energy -= damage
                    if agent.energy <= 0:
                        agent.energy = 0
                        agent.alive = False
                    contacts.append((agent_id, False, warning_ticks))
        
        return contacts
    
    def can_agent_detect_wave(self, agent: 'Agent', wave: WaveState, current_tick: int) -> bool:
        """
        Check if wave front has entered agent's SENSE_THREAT_RANGE.
        """
        if wave is None or not wave.active:
            return False
        front = wave.front_position(current_tick)
        if wave.direction == 'left_to_right':
            detectable_column = agent.x - SENSE_THREAT_RANGE
            return front >= detectable_column
        else:  # right_to_left
            detectable_column = agent.x + SENSE_THREAT_RANGE
            return front <= detectable_column
    
    def get_agent_zone(self, agent: 'Agent') -> str:
        """Return which zone an agent is in (Exp 4+)."""
        from config import ZONE_LEFT_END, ZONE_CENTER_END
        if agent.x <= ZONE_LEFT_END:
            return 'left'
        elif agent.x <= ZONE_CENTER_END:
            return 'center'
        else:
            return 'right'
