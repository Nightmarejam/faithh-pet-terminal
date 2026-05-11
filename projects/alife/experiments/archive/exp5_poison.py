"""
ALIFE Experiment 5: The Poison Test

Scientific Question:
Does offensive capability emerge when defense alone becomes insufficient?
Can agents evolve ACT_TOXIN when an adaptive predator renders ACT_SHIELD 
progressively useless?

Adaptive Predator Mechanic:
- Single L→R predator wave, interval ~500 ticks
- Predator tracks Shield dominance in population
- When Shield > 50% for 1000 ticks, predator gains +20% effectiveness vs Shield
- Shield effectiveness degrades: 100% → 80% → 60% → ... → 0%
- ACT_TOXIN provides 60% damage reduction IMMUNE to predator adaptation
- Toxin contacts also reduce predator adaptation (counter-evolution)

Success Criteria (all valid outcomes):
1. TOXIN_EMERGENCE_ANTICIPATORY — Toxin appears before adaptation > 0.5 (anticipatory)
2. TOXIN_EMERGENCE_REACTIVE — Toxin appears after adaptation > 0.5 (reactive)
3. SHIELD_COLLAPSE — Shield becomes useless, population collapses (too slow to adapt)
4. ARMS_RACE — Toxin and Shield coexist, adaptation oscillates (Red Queen)

Key Measurement:
- Tick when first ACT_TOXIN agent appears and survives to reproduce
- Predator adaptation level at that tick
- If adaptation < 0.5 at Toxin emergence → anticipatory (population-level intent)
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from agent import Agent
from config import (
    INITIAL_POPULATION, PREDATOR_DAMAGE, THERMAL_DRAIN_RATE,
    WAVE_SPEED_C, SENSE_THREAT_RANGE,
    EXP5_WAVE_INTERVAL, ADAPTATION_CHECK_INTERVAL, ADAPTATION_RATE,
    ADAPTATION_DECAY_RATE, SHIELD_DOMINANCE_THRESHOLD,
    TOXIN_DAMAGE_REDUCTION, TOXIN_COUNTER_RATE,
    STEALTH_WAVE_DAMAGE
)

# Op codes
SENSE_LIGHT = 0x02
SENSE_THREAT = 0x01
SENSE_SELF = 0x05
PROC_THRESHOLD = 0x00
PROC_PREDICT = 0x04
MEM_NONE = 0x00
MEM_PATTERN = 0x06
ACT_REPRODUCE = 0x04
ACT_SHIELD = 0x03
ACT_TOXIN = 0x06
REG_NONE = 0x00

# Seeded genome — successful Exp 3 strategy (Shield + Reproduce)
DEFENDER_GENOME = bytes([
    SENSE_LIGHT,     # S0 — light gradient for positioning
    SENSE_THREAT,    # S1 — approaching wave → P1
    PROC_THRESHOLD,  # P0 — fires on energy for reproduction
    PROC_PREDICT,    # P1 — prediction for shield (uses memory)
    MEM_PATTERN,     # M0 — stores threat timing patterns
    ACT_REPRODUCE,   # A0 — reproduce when P0 fires
    ACT_SHIELD,      # A1 — shield when P1 fires
    REG_NONE         # R0 — no regulation
])

# Toxin genome — what we expect to emerge via mutation
# Replaces ACT_SHIELD with ACT_TOXIN in A1 slot
TOXIN_GENOME = bytes([
    SENSE_LIGHT,     # S0
    SENSE_THREAT,    # S1
    PROC_THRESHOLD,  # P0 — reproduce
    PROC_PREDICT,    # P1 — toxin deployment (prediction-driven)
    MEM_PATTERN,     # M0
    ACT_REPRODUCE,   # A0
    ACT_TOXIN,       # A1 — toxin instead of shield
    REG_NONE         # R0
])


def has_shield(agent) -> bool:
    """Check if agent has Shield in A0 or A1."""
    return agent.genome[5] == ACT_SHIELD or agent.genome[6] == ACT_SHIELD


def has_toxin(agent) -> bool:
    """Check if agent has Toxin in A0 or A1."""
    return agent.genome[5] == ACT_TOXIN or agent.genome[6] == ACT_TOXIN


def get_strategy_name(agent) -> str:
    """Classify agent strategy."""
    s = has_shield(agent)
    t = has_toxin(agent)
    if s and t:
        return "HYBRID"
    elif t:
        return "TOXIN"
    elif s:
        return "SHIELD"
    else:
        return "NAKED"


def apply_adaptive_wave_damage(world, wave, current_tick, shield_adaptation):
    """
    Apply wave damage with adaptive predator mechanics.
    
    Shield effectiveness is reduced by shield_adaptation level.
    Toxin agents take reduced damage immune to adaptation.
    
    Returns: (contacts, toxin_contacts_count)
        contacts: list of (agent_id, outcome, warning_ticks)
        toxin_contacts_count: number of toxin agents that countered the predator
    """
    contacts = []
    toxin_contacts = 0
    front = wave.front_position(current_tick)
    
    for agent_id, agent in list(world.agents.items()):
        if not agent.alive:
            continue
        if abs(agent.x - front) < 1.0:
            # Record wave arrival (with dedup from world.py fix)
            MIN_ARRIVAL_GAP = 50
            if not agent.wave_arrival_times or (current_tick - agent.wave_arrival_times[-1]) > MIN_ARRIVAL_GAP:
                agent.wave_arrival_times.append(current_tick)
                agent.wave_arrival_times = agent.wave_arrival_times[-8:]
            
            # Calculate warning ticks for logging
            detectable_at = (agent.x - SENSE_THREAT_RANGE) / wave.speed
            warning_ticks = current_tick - (wave.start_tick + detectable_at)
            warning_ticks = max(0, warning_ticks)
            
            # Stealth waves are always lethal
            if wave.stealth:
                agent.energy -= STEALTH_WAVE_DAMAGE
                if agent.energy <= 0:
                    agent.energy = 0
                    agent.alive = False
                contacts.append((agent_id, 'stealth_kill', warning_ticks))
                continue
            
            # Check defense type
            agent_has_shield = has_shield(agent) and agent.shield_active
            agent_has_toxin = has_toxin(agent) and agent.toxin_active
            
            if agent_has_toxin:
                # Toxin defense: fixed damage reduction, IMMUNE to predator adaptation
                damage = PREDATOR_DAMAGE * (1.0 - TOXIN_DAMAGE_REDUCTION)
                agent.energy -= damage
                toxin_contacts += 1
                if agent.energy <= 0:
                    agent.energy = 0
                    agent.alive = False
                contacts.append((agent_id, 'toxin_defend', warning_ticks))
            elif agent_has_shield:
                # Shield defense: effectiveness degraded by predator adaptation
                shield_effectiveness = max(0.0, 1.0 - shield_adaptation)
                damage = PREDATOR_DAMAGE * (1.0 - shield_effectiveness)
                agent.energy -= damage
                if agent.energy <= 0:
                    agent.energy = 0
                    agent.alive = False
                contacts.append((agent_id, 'shield_defend', warning_ticks))
            else:
                # No defense: full damage
                agent.energy -= PREDATOR_DAMAGE
                if agent.energy <= 0:
                    agent.energy = 0
                    agent.alive = False
                contacts.append((agent_id, 'unshielded', warning_ticks))
    
    return contacts, toxin_contacts


def run_experiment_5(ticks: int = 50000, log_interval: int = 1000):
    """Run Experiment 5: The Poison Test."""
    # Activate ACT_TOXIN for this experiment (default is False in config.py)
    import config
    config.TOXIN_ACTIVE = True
    
    sim = Simulation(experiment=5)
    sim.world.initialize_light_gradient()
    sim.world.current_wave = None
    
    # Seed population: all start with Defender genome (Shield + Reproduce)
    # Toxin must emerge via mutation — that's the whole point
    sim.initialize_population(200)
    agents = list(sim.world.agents.values())
    for agent in agents:
        agent.genome = DEFENDER_GENOME[:]
    
    # Ensure all have ACT_REPRODUCE in genome
    print(f"Seeded {len(agents)} agents with DEFENDER genome (PROC_PREDICT + ACT_SHIELD + ACT_REPRODUCE)")
    
    # Initialize FAITHH observer
    observer = None
    FAITHH_AVAILABLE = False
    try:
        from faithh_observer import PulseWatcher
        observer = PulseWatcher()
        FAITHH_AVAILABLE = True
    except Exception as e:
        print(f"[PULSE] Observer init failed (non-fatal): {e}")
    
    # Adaptive predator state
    shield_adaptation = 0.0  # 0.0 = Shield fully effective, 1.0 = Shield useless
    
    # Results tracking
    results = {
        'wave_count': 0,
        'predator_kills': 0,
        'thermal_deaths': 0,
        'total_reproductions': 0,
        'first_toxin_tick': None,
        'first_toxin_agent': None,
        'adaptation_at_toxin': None,
        'adaptation_curve': [],
        'shield_pct_curve': [],
        'toxin_pct_curve': [],
    }
    
    # Toxin tracking
    first_toxin_emergence = None
    first_toxin_reproduction = None
    toxin_lineage_started = False
    
    print()
    print("=" * 70)
    print("EXPERIMENT 5: THE POISON TEST")
    print("=" * 70)
    print(f"Wave interval: {EXP5_WAVE_INTERVAL} ticks (L→R)")
    print(f"Adaptation rate: +{ADAPTATION_RATE*100:.0f}% per {ADAPTATION_CHECK_INTERVAL} ticks when Shield > {SHIELD_DOMINANCE_THRESHOLD*100:.0f}%")
    print(f"Toxin damage reduction: {TOXIN_DAMAGE_REDUCTION*100:.0f}% (immune to adaptation)")
    print(f"Toxin counter-rate: -{TOXIN_COUNTER_RATE*100:.0f}% adaptation per contact")
    print(f"Running for {ticks} ticks, logging every {log_interval} ticks")
    print("=" * 70)
    print()
    
    for t in range(ticks):
        # === SPAWN WAVE (added to active list so waves complete full crossing) ===
        if t > 0 and t % EXP5_WAVE_INTERVAL == 0:
            wave = sim.world.spawn_wave(t)
            wave.stealth = False  # All waves detectable in Exp 5 (focus is on adaptation, not stealth)
            sim.world.active_waves.append(wave)
            sim.world.current_wave = wave  # For SENSE_THREAT compatibility
            results['wave_count'] += 1
        
        # === PROCESS ALL ACTIVE WAVES ===
        for wave in list(sim.world.active_waves):
            if not wave.active:
                sim.world.active_waves.remove(wave)
                continue
            
            # Check wave detection for anticipation gap tracking
            negative_gaps = sim.check_wave_detection(wave, t, observer)
            
            # Apply adaptive wave damage
            contacts, toxin_contacts = apply_adaptive_wave_damage(
                sim.world, wave, t, shield_adaptation
            )
            
            # Toxin counter-evolution: reduce predator adaptation
            if toxin_contacts > 0:
                reduction = toxin_contacts * TOXIN_COUNTER_RATE
                shield_adaptation = max(0.0, shield_adaptation - reduction)
            
            # Process deaths
            for agent_id, outcome, warning_ticks in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent and not agent.alive:
                    results['predator_kills'] += 1
                    sim.world.remove_agent(agent)
                    sim.total_deaths += 1
            
            # Check if wave is complete
            if wave.is_complete(t):
                wave.active = False
        
        # === ADAPTIVE PREDATOR UPDATE ===
        if t > 0 and t % ADAPTATION_CHECK_INTERVAL == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total > 0:
                shield_count = sum(1 for a in pop if has_shield(a))
                shield_pct = shield_count / total
                
                if shield_pct > SHIELD_DOMINANCE_THRESHOLD:
                    # Predator adapts to Shield
                    shield_adaptation = min(1.5, shield_adaptation + ADAPTATION_RATE)
                else:
                    # Predator slowly loses adaptation when Shield isn't dominant
                    shield_adaptation = max(0.0, shield_adaptation - ADAPTATION_DECAY_RATE)
                
                results['adaptation_curve'].append((t, shield_adaptation))
        
        # === THERMAL DRAIN ===
        for agent in list(sim.world.agents.values()):
            if not agent.alive:
                continue
            drain = sim.world.apply_thermal_drain(agent)
            agent.energy -= drain
            if agent.energy <= 0:
                agent.energy = 0
                agent.alive = False
                results['thermal_deaths'] += 1
                sim.world.remove_agent(agent)
                sim.total_deaths += 1
        
        # === TOXIN EMERGENCE DETECTION ===
        # Only count as "emergence" if a toxin agent survives to gen > 1
        # (a random mutation at gen 1 that dies immediately isn't meaningful)
        for agent in sim.world.agents.values():
            if has_toxin(agent) and agent.generation > 1 and not hasattr(agent, '_toxin_logged'):
                agent._toxin_logged = True
                if first_toxin_emergence is None:
                    first_toxin_emergence = (t, agent.id, agent.generation)
                    results['first_toxin_tick'] = t
                    results['first_toxin_agent'] = agent.id
                    results['adaptation_at_toxin'] = shield_adaptation
                    
                    anticipatory = shield_adaptation < 0.5
                    label = "ANTICIPATORY" if anticipatory else "REACTIVE"
                    
                    print()
                    print(f"*** FIRST TOXIN EMERGENCE: {agent.id} at tick {t} gen={agent.generation:.0f} ***")
                    print(f"*** Predator adaptation at emergence: {shield_adaptation:.2f} ***")
                    print(f"*** Classification: {label} — Toxin appeared {'before' if anticipatory else 'after'} Shield became < 50% effective ***")
                    print()
        
        # === SIMULATION TICK ===
        sim.tick()
        
        # === POPULATION COLLAPSE CHECK ===
        if sim.world.get_population() == 0:
            print(f"\n*** POPULATION COLLAPSED at tick {t} ***\n")
            break
        
        # === LOGGING ===
        if t % log_interval == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total == 0:
                continue
            
            shield_count = sum(1 for a in pop if has_shield(a))
            toxin_count = sum(1 for a in pop if has_toxin(a))
            hybrid_count = sum(1 for a in pop if has_shield(a) and has_toxin(a))
            naked_count = total - shield_count - toxin_count + hybrid_count
            
            shield_pct = (shield_count / total) * 100
            toxin_pct = (toxin_count / total) * 100
            avg_energy = sum(a.energy for a in pop) / total
            avg_gen = sum(a.generation for a in pop) / total
            
            # Anticipation gap stats
            all_gaps = []
            for a in pop:
                all_gaps.extend(a.anticipation_gaps)
            neg_count = sum(1 for g in all_gaps if g < 0)
            neg_pct = (neg_count / total * 100) if total > 0 else 0
            
            results['shield_pct_curve'].append((t, shield_pct))
            results['toxin_pct_curve'].append((t, toxin_pct))
            
            shield_eff = max(0, (1.0 - shield_adaptation) * 100)
            toxin_marker = " [TOXIN!]" if toxin_count > 0 else ""
            
            print(f"Tick {t:6d}: pop={total:4d} | shield={shield_count:3d}({shield_pct:4.0f}%) "
                  f"toxin={toxin_count:3d}({toxin_pct:4.0f}%) naked={naked_count:3d} | "
                  f"adapt={shield_adaptation:.2f} shield_eff={shield_eff:4.0f}% | "
                  f"E={avg_energy:.0f} gen={avg_gen:.0f} neg_gap={neg_pct:.0f}%{toxin_marker}")
    
    # === FINAL RESULTS ===
    pop = list(sim.world.agents.values())
    total = len(pop)
    
    print()
    print("=" * 70)
    print("EXPERIMENT 5 RESULTS")
    print("=" * 70)
    print(f"Final population:       {total}")
    print(f"Wave count:             {results['wave_count']}")
    print(f"Predator kills:         {results['predator_kills']}")
    print(f"Thermal deaths:         {results['thermal_deaths']}")
    print(f"Total reproductions:    {sim.total_reproductions}")
    print(f"Total deaths:           {sim.total_deaths}")
    print()
    print(f"Final adaptation level: {shield_adaptation:.2f}")
    print(f"Shield effectiveness:   {max(0, (1.0 - shield_adaptation) * 100):.0f}%")
    
    if total > 0:
        shield_count = sum(1 for a in pop if has_shield(a))
        toxin_count = sum(1 for a in pop if has_toxin(a))
        print(f"Shield agents:          {shield_count} ({shield_count/total*100:.1f}%)")
        print(f"Toxin agents:           {toxin_count} ({toxin_count/total*100:.1f}%)")
    
    print()
    if first_toxin_emergence:
        t_tick, t_id, t_gen = first_toxin_emergence
        adapt_at = results['adaptation_at_toxin']
        anticipatory = adapt_at < 0.5
        print(f"First Toxin:            tick {t_tick}, {t_id}, gen {t_gen:.0f}")
        print(f"Adaptation at Toxin:    {adapt_at:.2f}")
        print(f"Classification:         {'ANTICIPATORY' if anticipatory else 'REACTIVE'}")
        
        if anticipatory:
            outcome = "TOXIN_EMERGENCE_ANTICIPATORY"
        else:
            outcome = "TOXIN_EMERGENCE_REACTIVE"
    elif total == 0:
        outcome = "SHIELD_COLLAPSE"
    elif shield_adaptation > 0.8 and total > 0:
        outcome = "ADAPTATION_STALEMATE"
    else:
        outcome = "NO_TOXIN_EMERGED"
    
    print(f"\nOutcome:                {outcome}")
    print("=" * 70)
    
    if observer:
        observer.close()
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ALIFE Experiment 5: The Poison Test")
    parser.add_argument("--ticks", type=int, default=50000)
    parser.add_argument("--log-interval", type=int, default=1000)
    args = parser.parse_args()
    
    run_experiment_5(ticks=args.ticks, log_interval=args.log_interval)
