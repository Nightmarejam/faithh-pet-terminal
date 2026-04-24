"""
ALIFE Instruction Set — All 40 op implementations
5 categories x 8 ops each = 40 total ops
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent import Agent
    from world import World

# =============================================================================
# SENSE OPS (slots S0, S1) — All cost 0 energy, return 0-255
# =============================================================================

def sense_energy(agent: 'Agent', world: 'World') -> int:
    """Read energy level of current cell."""
    return world.get_cell_energy(agent.x, agent.y)

def sense_threat(agent: 'Agent', world: 'World') -> int:
    """Read threat proximity based on wave front distance (0=far, 255=contact).
    
    For Experiment 3+: Returns proximity value based on wave front distance.
    Returns 0 when wave is far away, rising linearly to 255 as wave enters
    SENSE_THREAT_RANGE. This enables PROC_THRESHOLD to fire before wave contact.
    
    For Experiment 4+: Checks BOTH wave sources and returns the maximum threat
    (closest approaching wave). Handles both L→R and R→L wave directions.
    
    Stealth waves return 0 — they are undetectable until contact.
    Agents must predict wave timing to survive stealth waves.
    """
    from config import SENSE_THREAT_RANGE
    
    max_threat = 0
    
    # Collect all active waves to check
    waves = []
    # Multi-wave list (Exp 4+)
    if hasattr(world, 'active_waves') and world.active_waves:
        waves.extend(world.active_waves)
    # Single-wave fallback (Exp 3)
    elif hasattr(world, 'current_wave') and world.current_wave is not None:
        waves.append(world.current_wave)
    
    for wave in waves:
        if not wave.active or wave.stealth:
            continue
        
        current_tick = world.tick
        front = wave.front_position(current_tick)
        direction = getattr(wave, 'direction', 'left_to_right')
        
        if direction == 'left_to_right':
            distance = front - agent.x  # negative = wave hasn't reached agent yet
        else:  # right_to_left
            distance = agent.x - front  # negative = wave hasn't reached agent yet
        
        if distance >= 0:
            max_threat = 255  # Wave at or past agent
            break
        
        # Calculate proximity: 0 when far, rising to 255 as wave approaches
        proximity = SENSE_THREAT_RANGE + distance  # distance is negative
        if proximity > 0:
            threat = int((proximity / SENSE_THREAT_RANGE) * 255)
            max_threat = max(max_threat, threat)
    
    if max_threat > 0:
        return max_threat
    
    # Fallback to cell threat for non-wave experiments
    return world.get_cell_threat(agent.x, agent.y)

def sense_light(agent: 'Agent', world: 'World') -> int:
    """Read light/thermal level of current cell."""
    return world.get_cell_light(agent.x, agent.y)

def sense_neighbor(agent: 'Agent', world: 'World') -> int:
    """Read average energy of adjacent cells."""
    total = 0
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = agent.x + dx, agent.y + dy
            if world.in_bounds(nx, ny):
                total += world.get_cell_energy(nx, ny)
                count += 1
    return total // count if count > 0 else 0

def sense_density(agent: 'Agent', world: 'World') -> int:
    """Read agent density in local radius (3x3 area)."""
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = agent.x + dx, agent.y + dy
            if world.in_bounds(nx, ny) and world.get_occupant(nx, ny) is not None:
                count += 1
    return min(255, count * 28)  # Scale to 0-255 range

def sense_self(agent: 'Agent', world: 'World') -> int:
    """Read own current energy level."""
    return min(255, agent.energy)

def sense_gradient(agent: 'Agent', world: 'World') -> int:
    """Read direction of highest energy gradient (0-7 for 8 directions, 255 if flat)."""
    best_dir = 255
    best_energy = world.get_cell_energy(agent.x, agent.y)
    directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for i, (dx, dy) in enumerate(directions):
        nx, ny = agent.x + dx, agent.y + dy
        if world.in_bounds(nx, ny):
            e = world.get_cell_energy(nx, ny)
            if e > best_energy:
                best_energy = e
                best_dir = i * 32  # Scale to 0-255
    return best_dir

def sense_age(agent: 'Agent', world: 'World') -> int:
    """Read own age in ticks (capped at 255)."""
    return min(255, agent.age)

SENSE_OPS = [
    sense_energy,    # 0x00
    sense_threat,    # 0x01
    sense_light,     # 0x02
    sense_neighbor,  # 0x03
    sense_density,   # 0x04
    sense_self,      # 0x05
    sense_gradient,  # 0x06
    sense_age,       # 0x07
]

# =============================================================================
# PROCESS OPS (slots P0, P1) — Evaluate sense values, return True/False
# =============================================================================

def proc_threshold(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Fire if sense value exceeds fixed threshold (128)."""
    return sense_value > 128

def proc_compare(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Compare two sense values, fire on larger. Uses sense_value vs agent energy."""
    return sense_value > agent.energy

def proc_memory_cmp(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Compare current sense to stored memory value."""
    if not agent.memory:
        return False
    return sense_value > agent.memory[-1]

def proc_trend(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Detect rising trend in memory buffer."""
    if len(agent.memory) < 2:
        return False
    return agent.memory[-1] > agent.memory[-2]

def proc_predict(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Predict next wave arrival from timing history. KEY OP for anticipation.
    
    Uses wave_arrival_times to calculate average interval between waves,
    then fires when predicted next arrival is approaching. This enables
    Shield activation BEFORE the wave is detectable — true anticipation.
    """
    from config import SENSE_THREAT_RANGE
    
    if len(agent.wave_arrival_times) < 2:
        return False
    
    # Calculate average interval from wave history
    intervals = [agent.wave_arrival_times[i] - agent.wave_arrival_times[i-1]
                 for i in range(1, len(agent.wave_arrival_times))]
    avg_interval = sum(intervals) / len(intervals)
    
    # Predict next arrival
    last_arrival = agent.wave_arrival_times[-1]
    predicted_next = last_arrival + avg_interval
    current_tick = world.tick
    ticks_until_predicted = predicted_next - current_tick
    
    # Fire when predicted arrival is approaching
    # Prediction horizon = 3x detection range (anticipate before detectable)
    horizon = SENSE_THREAT_RANGE * 3
    return 0 < ticks_until_predicted < horizon

def proc_beat(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Predict beat frequency from dual wave sources (Exp 4+).
    
    Computes the beat interval (difference frequency) from Wave 1 and Wave 2
    arrival times. Fires when predicted beat arrival is approaching.
    
    This is the KEY OP for interference zone survival in Experiment 4.
    """
    from config import SENSE_THREAT_RANGE
    
    # Try to import Exp 4 config, fall back to defaults
    try:
        from config import BEAT_HORIZON
    except ImportError:
        BEAT_HORIZON = 60
    
    # Need at least 2 arrivals from each source for beat detection
    if len(agent.wave1_arrival_times) < 2 or len(agent.wave2_arrival_times) < 2:
        # Fall back to single-source prediction if only one source available
        if len(agent.wave_arrival_times) >= 2:
            intervals = [agent.wave_arrival_times[i] - agent.wave_arrival_times[i-1]
                         for i in range(1, len(agent.wave_arrival_times))]
            avg_interval = sum(intervals) / len(intervals)
            last_arrival = agent.wave_arrival_times[-1]
            predicted_next = last_arrival + avg_interval
            ticks_until = predicted_next - world.tick
            return 0 < ticks_until < SENSE_THREAT_RANGE * 3
        # Ultimate fallback: reactive shielding from sense data (same as proc_predict)
        return sense_value > 128
    
    # Calculate intervals for each source
    intervals1 = [agent.wave1_arrival_times[i] - agent.wave1_arrival_times[i-1]
                  for i in range(1, len(agent.wave1_arrival_times))]
    intervals2 = [agent.wave2_arrival_times[i] - agent.wave2_arrival_times[i-1]
                  for i in range(1, len(agent.wave2_arrival_times))]
    
    avg_interval1 = sum(intervals1) / len(intervals1)
    avg_interval2 = sum(intervals2) / len(intervals2)
    
    # Predict next arrival from each source
    last1 = agent.wave1_arrival_times[-1]
    last2 = agent.wave2_arrival_times[-1]
    predicted1 = last1 + avg_interval1
    predicted2 = last2 + avg_interval2
    
    current_tick = world.tick
    ticks_until1 = predicted1 - current_tick
    ticks_until2 = predicted2 - current_tick
    
    # Fire if EITHER source is approaching within horizon
    # This is the beat detection — agent shields for whichever wave comes next
    horizon = BEAT_HORIZON if BEAT_HORIZON else SENSE_THREAT_RANGE * 3
    
    return (0 < ticks_until1 < horizon) or (0 < ticks_until2 < horizon)

def proc_average(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Average last N memory values, fire if above threshold."""
    if not agent.memory:
        return sense_value > 128
    avg = sum(agent.memory) / len(agent.memory)
    return avg > 128

def proc_invert(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    """Fire when sense value is LOW (inversion)."""
    return sense_value < 64

PROCESS_OPS = [
    proc_threshold,   # 0x00
    proc_compare,     # 0x01
    proc_memory_cmp,  # 0x02
    proc_trend,       # 0x03
    proc_predict,     # 0x04
    proc_beat,        # 0x05 — was proc_weight, now beat detection for Exp 4
    proc_average,     # 0x06
    proc_invert,      # 0x07
]

# =============================================================================
# MEMORY OPS (slot M0) — Define how agent stores past experience
# =============================================================================

def mem_none(agent: 'Agent', sense_value: int) -> None:
    """No memory — purely reactive agent."""
    agent.memory = []

def mem_last1(agent: 'Agent', sense_value: int) -> None:
    """Store last 1 sense reading."""
    agent.memory = [sense_value]

def mem_last4(agent: 'Agent', sense_value: int) -> None:
    """Store last 4 sense readings (rolling buffer)."""
    agent.memory.append(sense_value)
    if len(agent.memory) > 4:
        agent.memory.pop(0)

def mem_last8(agent: 'Agent', sense_value: int) -> None:
    """Store last 8 sense readings."""
    agent.memory.append(sense_value)
    if len(agent.memory) > 8:
        agent.memory.pop(0)

def mem_best(agent: 'Agent', sense_value: int) -> None:
    """Store reading from highest-energy tick seen."""
    if not agent.memory or sense_value > agent.memory[0]:
        agent.memory = [sense_value]

def mem_worst(agent: 'Agent', sense_value: int) -> None:
    """Store reading from lowest-energy tick seen."""
    if not agent.memory or sense_value < agent.memory[0]:
        agent.memory = [sense_value]

def mem_pattern(agent: 'Agent', sense_value: int) -> None:
    """Store last threat encounter pattern (timing + intensity)."""
    # Store as (tick, intensity) pairs, keep last 4 encounters
    if sense_value > 128:  # Threat detected
        agent.pattern_memory.append((agent.age, sense_value))
        if len(agent.pattern_memory) > 4:
            agent.pattern_memory.pop(0)

def mem_dual(agent: 'Agent', sense_value: int) -> None:
    """Dual-source memory for Experiment 4.
    
    Stores separate arrival time buffers for Wave 1 (L→R) and Wave 2 (R→L).
    Actual storage happens in world.apply_wave_damage — this op enables
    the agent to USE the dual buffers via PROC_BEAT.
    
    Also stores sense values in pattern memory for compatibility.
    """
    if sense_value > 128:
        agent.pattern_memory.append((agent.age, sense_value))
        if len(agent.pattern_memory) > 4:
            agent.pattern_memory.pop(0)

MEMORY_OPS = [
    mem_none,     # 0x00
    mem_last1,    # 0x01
    mem_last4,    # 0x02
    mem_last8,    # 0x03
    mem_best,     # 0x04
    mem_worst,    # 0x05
    mem_pattern,  # 0x06
    mem_dual,     # 0x07 — was mem_hybrid, now dual-source for Exp 4
]

# =============================================================================
# ACT OPS (slots A0, A1) — Actions the agent can take
# =============================================================================

def act_idle(agent: 'Agent', world: 'World') -> None:
    """Do nothing this tick."""
    pass

def act_move(agent: 'Agent', world: 'World') -> None:
    """Move toward energy gradient."""
    best_x, best_y = agent.x, agent.y
    best_energy = world.get_cell_energy(agent.x, agent.y)
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = agent.x + dx, agent.y + dy
            if world.in_bounds(nx, ny) and world.get_occupant(nx, ny) is None:
                e = world.get_cell_energy(nx, ny)
                if e > best_energy:
                    best_energy = e
                    best_x, best_y = nx, ny
    
    if (best_x, best_y) != (agent.x, agent.y):
        world.move_agent(agent, best_x, best_y)

def act_consume(agent: 'Agent', world: 'World') -> None:
    """Consume energy from current cell. Transfers cell energy to agent (capped at 255)."""
    from config import CONSUME_AMOUNT
    available = world.get_cell_energy(agent.x, agent.y)
    consume_amount = min(available, CONSUME_AMOUNT)  # Max from config
    agent.add_energy(consume_amount)  # Uses capped add_energy method
    world.reduce_cell_energy(agent.x, agent.y, consume_amount)

def act_shield(agent: 'Agent', world: 'World') -> None:
    """Activate disruption trait — blocks predator, reduces thermal."""
    agent.shield_active = True

def act_reproduce(agent: 'Agent', world: 'World') -> None:
    """Spawn child if energy above threshold and cooldown expired."""
    from config import REPRODUCTION_THRESHOLD, REPRODUCTION_COST
    if agent.reproduction_cooldown == 0 and agent.energy >= REPRODUCTION_THRESHOLD:
        world.request_reproduction(agent)

def act_signal(agent: 'Agent', world: 'World') -> None:
    """Emit chemical signal to adjacent agents (active Exp 4+)."""
    from config import SIGNAL_ACTIVE
    if SIGNAL_ACTIVE:
        agent.signaling = True

def act_toxin(agent: 'Agent', world: 'World') -> None:
    """Deploy toxin — damages predator on contact (active Exp 4+)."""
    from config import TOXIN_ACTIVE
    if TOXIN_ACTIVE:
        agent.toxin_active = True

def act_flee(agent: 'Agent', world: 'World') -> None:
    """Move away from threat gradient."""
    threat_x, threat_y = world.get_threat_direction(agent.x, agent.y)
    if threat_x is not None:
        # Move opposite to threat
        flee_x = agent.x - (threat_x - agent.x)
        flee_y = agent.y - (threat_y - agent.y)
        flee_x = max(0, min(world.width - 1, flee_x))
        flee_y = max(0, min(world.height - 1, flee_y))
        if world.get_occupant(flee_x, flee_y) is None:
            world.move_agent(agent, flee_x, flee_y)

ACT_OPS = [
    act_idle,      # 0x00
    act_move,      # 0x01
    act_consume,   # 0x02
    act_shield,    # 0x03
    act_reproduce, # 0x04
    act_signal,    # 0x05
    act_toxin,     # 0x06
    act_flee,      # 0x07
]

# =============================================================================
# REGULATE OPS (slot R0) — Metabolic optimization
# =============================================================================

def reg_none(agent: 'Agent', world: 'World') -> dict:
    """No regulation — all costs fixed."""
    return {}

def reg_conserve(agent: 'Agent', world: 'World') -> dict:
    """Reduce all op costs by 1 when own energy < 50."""
    from config import CRITICAL_LOW_ENERGY
    if agent.energy < CRITICAL_LOW_ENERGY:
        return {'cost_modifier': -1}
    return {}

def reg_burst(agent: 'Agent', world: 'World') -> dict:
    """Double act effectiveness when own energy > 150."""
    from config import BURST_THRESHOLD
    if agent.energy > BURST_THRESHOLD:
        return {'effectiveness_multiplier': 2}
    return {}

def reg_cycle(agent: 'Agent', world: 'World') -> dict:
    """Alternate between two behavioral modes every N ticks."""
    cycle_period = 50
    mode = (agent.age // cycle_period) % 2
    return {'behavior_mode': mode}

def reg_learn(agent: 'Agent', world: 'World') -> dict:
    """Reduce cost of frequently-used ops by 1 after 100 uses."""
    discounts = {}
    for op_code, count in agent.op_usage.items():
        if count >= 100:
            discounts[op_code] = -1
    return {'op_discounts': discounts}

def reg_suppress(agent: 'Agent', world: 'World') -> dict:
    """Disable most expensive op when energy critical."""
    from config import CRITICAL_LOW_ENERGY
    if agent.energy < CRITICAL_LOW_ENERGY // 2:
        return {'suppress_expensive': True}
    return {}

def reg_prioritize(agent: 'Agent', world: 'World') -> dict:
    """Always execute highest-survival op first regardless of genome order."""
    return {'prioritize_survival': True}

def reg_adaptive(agent: 'Agent', world: 'World') -> dict:
    """Combine REG_CONSERVE and REG_LEARN."""
    result = reg_conserve(agent, world)
    learn_result = reg_learn(agent, world)
    result.update(learn_result)
    return result

REGULATE_OPS = [
    reg_none,       # 0x00
    reg_conserve,   # 0x01
    reg_burst,      # 0x02
    reg_cycle,      # 0x03
    reg_learn,      # 0x04
    reg_suppress,   # 0x05
    reg_prioritize, # 0x06
    reg_adaptive,   # 0x07
]

# =============================================================================
# Op lookup by category
# =============================================================================

def get_sense_op(code: int):
    """Get sense op function by code (0-7)."""
    return SENSE_OPS[code & 0x07]

def get_process_op(code: int):
    """Get process op function by code (0-7)."""
    return PROCESS_OPS[code & 0x07]

def get_memory_op(code: int):
    """Get memory op function by code (0-7)."""
    return MEMORY_OPS[code & 0x07]

def get_act_op(code: int):
    """Get act op function by code (0-7)."""
    return ACT_OPS[code & 0x07]

def get_regulate_op(code: int):
    """Get regulate op function by code (0-7)."""
    return REGULATE_OPS[code & 0x07]

def get_op_cost(category: str, code: int) -> int:
    """Get energy cost for an op."""
    from config import SENSE_COSTS, PROCESS_COSTS, MEMORY_COSTS, ACT_COSTS, REGULATE_COSTS
    costs = {
        'sense': SENSE_COSTS,
        'process': PROCESS_COSTS,
        'memory': MEMORY_COSTS,
        'act': ACT_COSTS,
        'regulate': REGULATE_COSTS,
    }
    return costs[category][code & 0x07]
