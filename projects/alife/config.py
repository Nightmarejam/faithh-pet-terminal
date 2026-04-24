"""
ALIFE Configuration — All tunable parameters
Never hardcode values in simulation logic — edit here only.

# === EXPERIMENT 0 BASELINE (stable) ===
# Natural carrying capacity: ~324 agents
# Stable avg energy: ~210
# Validated: 2026-03-19
"""

# Grid dimensions (tripled for higher carrying capacity)
GRID_WIDTH = 480
GRID_HEIGHT = 360

# Cell data ranges
ENERGY_MAX = 255
THREAT_MAX = 255
LIGHT_MAX = 255

# Energy economics
ENERGY_REGEN_RATE = 1          # Base energy regen per cell per REGEN_INTERVAL ticks
REGEN_INTERVAL = 5             # Ticks between energy regeneration

# Energy source nodes (rich ecological niches)
NUM_ENERGY_SOURCES = 20        # Number of energy hotspots in world
ENERGY_SOURCE_RADIUS = 15      # Cells within this radius get boosted regen
ENERGY_SOURCE_STRENGTH = 10    # Regen rate within source radius
BASELINE_DRAIN = 1             # Energy cost per tick just to exist
REPRODUCTION_THRESHOLD = 120   # Minimum energy to reproduce (lowered for Exp 1 drift test)
REPRODUCTION_COST = 80         # Energy given to child (parent loses this)
INITIAL_ENERGY = 200           # Starting energy for new agents
CRITICAL_LOW_ENERGY = 50       # REG_CONSERVE activates below this
BURST_THRESHOLD = 150          # REG_BURST activates above this

# Population
INITIAL_POPULATION = 50        # Starting agent count for Exp 0
MAX_POPULATION = 2000          # Emergency hard cap only — density-dependent reproduction handles soft cap

# Mutation rates (per reproduction event)
POINT_MUTATION_RATE = 0.005    # 0.5% per byte
BYTE_SWAP_RATE = 0.001         # 0.1% per event
SLOT_DUPLICATION_RATE = 0.0005 # 0.05% (Exp 4+ only)
SLOT_DELETION_RATE = 0.0005    # 0.05% (Exp 4+ only)
CATEGORY_CROSSING_RATE = 0.0001 # 0.01% (Exp 4+ only)

# Threat parameters
PREDATOR_WAVE_PERIOD = 200     # Ticks between predator waves (Exp 2: fast waves)
PREDATOR_WAVE_INTERVAL = 200   # Alias for PREDATOR_WAVE_PERIOD (Exp 2: fast waves)
PREDATOR_WAVE_VARIANCE = 50    # +/- variance for Exp 3+
PREDATOR_DAMAGE = 200          # Survivable with high energy, lethal to low-energy agents
SHIELD_COST = 0                # Wave-contact cost for shielded agents (per-tick cost is in ACT_COSTS)
PREDATOR_REMOVAL_TICK = 25000  # Tick when predator is removed mid-experiment (Exp 1)
THERMAL_DRAIN_RATE = 0.2       # Tiebreaker pressure, reduced for Exp 3 sustainability

# Wave propagation parameters (Exp 3+)
WAVE_SPEED_C = 0.8             # Columns per tick — crosses 480-col world in 600 ticks
WAVE_SPEED_VARIANCE = 0.05     # 5% std dev — near-deterministic so prediction accuracy matters
SENSE_THREAT_RANGE = 5         # Short detection range — memory confers survival advantage
STEALTH_WAVE_PROBABILITY = 0.3 # 30% of waves are undetectable — requires prediction to survive
STEALTH_WAVE_DAMAGE = 999      # Instant death — stealth waves are lethal regardless of energy

# Op energy costs (indexed by op code) — reduced 50% for Exp 0 tuning
SENSE_COSTS = [0, 0, 0, 0, 0, 0, 0, 0]      # Sensing is always free
PROCESS_COSTS = [0, 0, 1, 1, 2, 1, 1, 0]    # Was [1, 1, 2, 3, 4, 3, 2, 1]
MEMORY_COSTS = [0, 0, 1, 1, 0, 0, 1, 2]     # Was [0, 1, 2, 3, 1, 1, 3, 4]
ACT_COSTS = [0, 1, 0, 1, 2, 1, 2, 1]        # Original costs — selection via prediction accuracy, not cost
REGULATE_COSTS = [0, 0, 1, 1, 1, 0, 1, 2]   # Was [0, 1, 2, 2, 3, 1, 3, 4]

# ACT_CONSUME parameters
CONSUME_AMOUNT = 25                         # Max energy transferred per consume action

# Memory buffer sizes
MEM_LAST1_SIZE = 1
MEM_LAST4_SIZE = 4
MEM_LAST8_SIZE = 8

# Genome structure
GENOME_LENGTH = 8              # Fixed length for Exp 0-3
VARIABLE_LENGTH_ENABLED = False # Enable in Exp 4+

# Experiment flags
CURRENT_EXPERIMENT = 0
MEMORY_ENABLED = False         # MEM_NONE enforced when False
SIGNAL_ACTIVE = False          # ACT_SIGNAL effect enabled (Exp 4+)
TOXIN_ACTIVE = False           # ACT_TOXIN effect enabled (Exp 4+)

# Logging
LOG_INTERVAL = 100             # Ticks between population logging
RANDOM_SEED = None             # Set for deterministic runs, None for random

# Experiment 4: Harmonic Interference
WAVE1_INTERVAL = 600          # L→R wave interval (ticks) — exactly 1 active at speed 0.8
WAVE2_INTERVAL = 900          # R→L wave interval (ticks) — 2:3 ratio, max 1 active
ZONE_LEFT_END = 159           # Left zone: columns 0-159
ZONE_CENTER_END = 319         # Center zone: columns 160-319
                              # Right zone: columns 320-479
EXP4_WAVE_SPEED = None        # None = use default WAVE_SPEED_C (0.8). Intervals set above crossing time.
BEAT_TOLERANCE = 30           # ±30 ticks for beat detection
BEAT_HORIZON = 15             # Same horizon as PROC_PREDICT — advantage is accuracy, not window size

# Experiment 5: The Poison Test
EXP5_WAVE_INTERVAL = 500              # L→R predator wave interval (ticks)
ADAPTATION_CHECK_INTERVAL = 1000      # Ticks between predator adaptation checks
ADAPTATION_RATE = 0.20                # +20% shield ineffectiveness per adaptation step
ADAPTATION_DECAY_RATE = 0.10          # Adaptation decreases when shield is NOT dominant
SHIELD_DOMINANCE_THRESHOLD = 0.50     # Shield must be >50% of pop to trigger adaptation
TOXIN_DAMAGE_REDUCTION = 0.60         # Toxin reduces incoming wave damage by 60%
TOXIN_COUNTER_RATE = 0.05             # Each toxin contact reduces predator adaptation by 5%
