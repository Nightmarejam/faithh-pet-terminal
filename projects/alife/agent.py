"""
ALIFE Agent — 8-byte genome, energy, age, position
"""

import random
from typing import List, Dict, Optional
from config import GENOME_LENGTH, MEMORY_ENABLED, INITIAL_ENERGY, ENERGY_MAX


class Agent:
    """An agent in the artificial life simulation."""
    
    _next_id = 0
    
    def __init__(self, x: int, y: int, genome: Optional[bytes] = None, parent_id: Optional[str] = None):
        Agent._next_id += 1
        self.id = f"agent_{Agent._next_id}"
        self.parent_id = parent_id
        self.generation = 0
        
        # Position
        self.x = x
        self.y = y
        
        # Genome: 8 bytes [S0][S1][P0][P1][M0][A0][A1][R0]
        if genome is None:
            self.genome = self._random_genome()
        else:
            self.genome = genome
        
        # State
        self.energy = INITIAL_ENERGY
        self.age = 0
        self.alive = True
        
        # Memory (for Exp 3+)
        self.memory: List[int] = []
        self.pattern_memory: List[tuple] = []
        
        # Action state
        self.shield_active = False
        self.signaling = False
        self.toxin_active = False
        
        # Tracking for REG_LEARN
        self.op_usage: Dict[int, int] = {}
        
        # Anticipation tracking
        self.last_shield_tick: Optional[int] = None
        self.last_threat_sense_tick: Optional[int] = None
        
        # Shield tracking for FAITHH logging (Exp 1+)
        self.shield_activations: int = 0
        self.peak_energy: int = INITIAL_ENERGY
        
        # Anticipation gap tracking (Exp 3+)
        self.last_shield_activation: Optional[int] = None  # tick when Shield last activated
        self.wave_detection_tick: Optional[int] = None     # tick when current wave detected
        self.wave_detected: Optional[int] = None           # start_tick of detected wave
        self.anticipation_gaps: List[float] = []           # history of all gap values
        self.position_adjusted_gaps: List[float] = []      # gap normalized by position
        self.wave_arrival_times: List[int] = []            # ticks when waves contacted agent
        
        # Dual-source wave tracking (Exp 4+)
        self.wave1_arrival_times: List[int] = []  # L→R waves (max 4)
        self.wave2_arrival_times: List[int] = []  # R→L waves (max 4)
        self.last_zone: Optional[str] = None      # For zone_entry tracking
        
        # Reproduction cooldown (prevents energy drain cascade)
        self.reproduction_cooldown: int = 0                # ticks until can reproduce again
    
    def _random_genome(self) -> bytes:
        """Generate a random genome with valid ops per slot."""
        # Each byte is 0-7 (valid op range for each category)
        return bytes([random.randint(0, 7) for _ in range(GENOME_LENGTH)])
    
    @property
    def sense_ops(self) -> tuple:
        """Get sense op codes (S0, S1)."""
        return (self.genome[0], self.genome[1])
    
    @property
    def process_ops(self) -> tuple:
        """Get process op codes (P0, P1)."""
        return (self.genome[2], self.genome[3])
    
    @property
    def memory_op(self) -> int:
        """Get memory op code (M0)."""
        if not MEMORY_ENABLED:
            return 0  # MEM_NONE enforced
        return self.genome[4]
    
    @property
    def act_ops(self) -> tuple:
        """Get act op codes (A0, A1)."""
        return (self.genome[5], self.genome[6])
    
    @property
    def regulate_op(self) -> int:
        """Get regulate op code (R0)."""
        return self.genome[7]
    
    def genome_hex(self) -> str:
        """Return genome as hex string."""
        return self.genome.hex()
    
    def tick_age(self) -> None:
        """Increment age by one tick."""
        self.age += 1
    
    def apply_energy_cost(self, cost: int) -> None:
        """Deduct energy cost."""
        self.energy -= cost
        if self.energy <= 0:
            self.energy = 0
            self.alive = False
    
    def add_energy(self, amount: int) -> None:
        """Add energy, capped at ENERGY_MAX (255)."""
        self.energy = min(self.energy + amount, ENERGY_MAX)
    
    def reset_tick_state(self) -> None:
        """Reset per-tick state flags."""
        self.shield_active = False
        self.signaling = False
        self.toxin_active = False
    
    def record_op_usage(self, op_code: int) -> None:
        """Track op usage for REG_LEARN."""
        self.op_usage[op_code] = self.op_usage.get(op_code, 0) + 1
    
    def create_child(self, child_x: int, child_y: int, child_genome: bytes) -> 'Agent':
        """Create a child agent."""
        from config import REPRODUCTION_COST
        
        child = Agent(child_x, child_y, genome=child_genome, parent_id=self.id)
        child.generation = self.generation + 1
        child.energy = REPRODUCTION_COST
        self.energy -= REPRODUCTION_COST
        
        # Inherit wave timing knowledge for PROC_PREDICT
        child.wave_arrival_times = self.wave_arrival_times.copy()
        
        # Inherit dual wave timing knowledge (Exp 4+)
        child.wave1_arrival_times = self.wave1_arrival_times.copy()
        child.wave2_arrival_times = self.wave2_arrival_times.copy()
        
        return child
    
    def __repr__(self) -> str:
        return f"Agent({self.id}, pos=({self.x},{self.y}), energy={self.energy}, gen={self.generation})"
