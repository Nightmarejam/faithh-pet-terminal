"""
ALIFE Experiment 5: The Parasitic Emergence

Scientific Question:
Does offensive capability emerge incrementally — parasitism before
chemical warfare — when agents face adaptive predator pressure?

Biological Insight:
Real offensive behavior doesn't start with venom. It starts with
resource theft. The progression is:
  Level 1: Energy parasitism (drain neighbors — cheap, immediate benefit)
  Level 2: Threat redirection (use neighbors as shields — system hijacking)
  Level 3: Toxin production (chemical warfare — expensive, comes last)

Mechanic — ACT_SIGNAL as Parasitic Drain:
  ACT_SIGNAL (0x05, cost 2/tick) is repurposed: when active, the agent
  drains PARASITE_DRAIN_RATE energy/tick from each adjacent agent.
  This is the cheapest offensive behavior — immediate fitness advantage
  without needing to interact with the predator at all.

Mechanic — Adaptive Predator (same as original Poison Test):
  Predator tracks Shield dominance, gains effectiveness over time.
  Shield becomes progressively useless, creating pressure for alternatives.

Mechanic — Threat Redirection (Phase B):
  After PARASITE_REDIRECT_TICK, parasitic agents can redirect a portion
  of incoming wave damage to adjacent non-signaling agents. This is
  system hijacking — using neighbors as meat shields.

Mechanic — ACT_TOXIN (Phase C):
  ACT_TOXIN (0x06, cost 5/tick) activates after TOXIN_UNLOCK_TICK.
  Provides damage reduction immune to predator adaptation.
  Only viable after parasites accumulate energy surplus.

Success Criteria:
  1. PARASITISM_EMERGES — ACT_SIGNAL agents spread (energy theft works)
  2. ARMS_RACE — Victims evolve counter-strategies (flee, counter-signal)
  3. HIJACKING_EMERGES — Parasites redirect wave damage to neighbors
  4. TOXIN_EMERGES — Full offensive stack (parasitism + toxin)
  5. ECOSYSTEM — Multiple strategies coexist (parasites, defenders, toxin)
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from agent import Agent
from config import (
    PREDATOR_DAMAGE, THERMAL_DRAIN_RATE,
    WAVE_SPEED_C, SENSE_THREAT_RANGE,
    ADAPTATION_CHECK_INTERVAL, ADAPTATION_RATE,
    ADAPTATION_DECAY_RATE, SHIELD_DOMINANCE_THRESHOLD,
    TOXIN_DAMAGE_REDUCTION, TOXIN_COUNTER_RATE,
    STEALTH_WAVE_DAMAGE, EXP5_WAVE_INTERVAL
)

# Op codes
SENSE_LIGHT = 0x02
SENSE_THREAT = 0x01
SENSE_SELF = 0x05
SENSE_NEIGHBOR = 0x03
SENSE_DENSITY = 0x04
PROC_THRESHOLD = 0x00
PROC_PREDICT = 0x04
MEM_NONE = 0x00
MEM_PATTERN = 0x06
ACT_REPRODUCE = 0x04
ACT_SHIELD = 0x03
ACT_SIGNAL = 0x05  # Repurposed as parasitic drain
ACT_TOXIN = 0x06
ACT_FLEE = 0x07
REG_NONE = 0x00

# Experiment 5 specific parameters
PARASITE_DRAIN_RATE = 1.5        # Energy stolen per adjacent victim per tick (tuned for stability)
PARASITE_REDIRECT_FRACTION = 0.3 # Fraction of wave damage redirected to neighbors
PARASITE_REDIRECT_TICK = 5000    # Tick when threat redirection activates
TOXIN_UNLOCK_TICK = 15000        # Tick when ACT_TOXIN becomes available

# Seeded genome — successful Exp 3 defender (Shield + Reproduce + Memory)
DEFENDER_GENOME = bytes([
    SENSE_LIGHT,     # S0
    SENSE_THREAT,    # S1
    PROC_THRESHOLD,  # P0 — reproduce when energy sufficient
    PROC_PREDICT,    # P1 — shield via prediction
    MEM_PATTERN,     # M0 — threat timing memory
    ACT_REPRODUCE,   # A0
    ACT_SHIELD,      # A1
    REG_NONE         # R0
])


def has_shield(agent) -> bool:
    return agent.genome[5] == ACT_SHIELD or agent.genome[6] == ACT_SHIELD

def has_signal(agent) -> bool:
    """Check if agent has parasitic signal (ACT_SIGNAL) in A0 or A1."""
    return agent.genome[5] == ACT_SIGNAL or agent.genome[6] == ACT_SIGNAL

def has_toxin(agent) -> bool:
    return agent.genome[5] == ACT_TOXIN or agent.genome[6] == ACT_TOXIN

def get_strategy(agent) -> str:
    sig = has_signal(agent)
    shd = has_shield(agent)
    tox = has_toxin(agent)
    if tox and sig:
        return "APEX"       # Full offensive stack
    elif tox:
        return "TOXIN"
    elif sig and shd:
        return "PARASITE+"  # Parasite with defense
    elif sig:
        return "PARASITE"   # Pure parasite
    elif shd:
        return "DEFENDER"
    else:
        return "NAKED"


def apply_parasitic_drain(world, current_tick):
    """
    Parasites (agents with active signaling) drain energy from adjacent agents.
    Returns: (total_drained, parasite_count, victim_count)
    """
    total_drained = 0
    parasite_count = 0
    victim_count = 0
    
    for agent in list(world.agents.values()):
        if not agent.alive or not agent.signaling:
            continue
        
        parasite_count += 1
        neighbors = world.get_adjacent_agents(agent.x, agent.y, radius=1)
        
        for victim in neighbors:
            if not victim.alive or victim.signaling:
                continue  # Don't drain other parasites
            
            drain = min(PARASITE_DRAIN_RATE, victim.energy)
            if drain > 0:
                victim.energy -= drain
                agent.energy = min(agent.energy + drain, 255)
                total_drained += drain
                victim_count += 1
                
                if victim.energy <= 0:
                    victim.energy = 0
                    victim.alive = False
    
    return total_drained, parasite_count, victim_count


def apply_adaptive_wave_damage(world, wave, current_tick, shield_adaptation,
                                redirect_active=False):
    """
    Wave damage with adaptive predator + parasitic threat redirection.
    
    When redirect_active: parasitic agents redirect PARASITE_REDIRECT_FRACTION
    of their incoming damage to adjacent non-signaling agents.
    """
    contacts = []
    toxin_contacts = 0
    redirect_events = 0
    front = wave.front_position(current_tick)
    
    for agent_id, agent in list(world.agents.items()):
        if not agent.alive:
            continue
        if abs(agent.x - front) < 1.0:
            # Record wave arrival (dedup)
            MIN_ARRIVAL_GAP = 50
            if not agent.wave_arrival_times or (current_tick - agent.wave_arrival_times[-1]) > MIN_ARRIVAL_GAP:
                agent.wave_arrival_times.append(current_tick)
                agent.wave_arrival_times = agent.wave_arrival_times[-8:]
            
            # Stealth = instant kill
            if wave.stealth:
                agent.energy -= STEALTH_WAVE_DAMAGE
                if agent.energy <= 0:
                    agent.energy = 0
                    agent.alive = False
                contacts.append((agent_id, 'stealth_kill'))
                continue
            
            # Check defenses
            agent_has_toxin = has_toxin(agent) and agent.toxin_active
            agent_has_shield = has_shield(agent) and agent.shield_active
            agent_is_parasite = has_signal(agent) and agent.signaling
            
            if agent_has_toxin:
                # Toxin: fixed damage reduction, immune to adaptation
                damage = PREDATOR_DAMAGE * (1.0 - TOXIN_DAMAGE_REDUCTION)
                agent.energy -= damage
                toxin_contacts += 1
                outcome = 'toxin_defend'
            elif agent_has_shield:
                # Shield: degraded by adaptation
                shield_eff = max(0.0, 1.0 - shield_adaptation)
                damage = PREDATOR_DAMAGE * (1.0 - shield_eff)
                agent.energy -= damage
                outcome = 'shield_defend'
            elif agent_is_parasite and redirect_active:
                # Parasite with redirect: push damage to neighbors
                own_damage = PREDATOR_DAMAGE * (1.0 - PARASITE_REDIRECT_FRACTION)
                redirect_damage = PREDATOR_DAMAGE * PARASITE_REDIRECT_FRACTION
                agent.energy -= own_damage
                
                # Find adjacent non-parasites to dump damage on
                neighbors = world.get_adjacent_agents(agent.x, agent.y, radius=1)
                victims = [n for n in neighbors if n.alive and not n.signaling]
                if victims:
                    per_victim = redirect_damage / len(victims)
                    for v in victims:
                        v.energy -= per_victim
                        if v.energy <= 0:
                            v.energy = 0
                            v.alive = False
                    redirect_events += 1
                else:
                    # No victims nearby — take full damage
                    agent.energy -= redirect_damage
                outcome = 'parasite_redirect'
            else:
                # No defense
                agent.energy -= PREDATOR_DAMAGE
                outcome = 'unshielded'
            
            if agent.energy <= 0:
                agent.energy = 0
                agent.alive = False
            contacts.append((agent_id, outcome))
    
    return contacts, toxin_contacts, redirect_events


def run_experiment_5(ticks: int = 50000, log_interval: int = 1000):
    """Run Experiment 5: The Parasitic Emergence."""
    import config
    config.SIGNAL_ACTIVE = True   # Enable parasitic drain via ACT_SIGNAL
    config.TOXIN_ACTIVE = False   # Toxin starts disabled, unlocks at TOXIN_UNLOCK_TICK
    
    sim = Simulation(experiment=5)
    sim.world.initialize_light_gradient()
    sim.world.current_wave = None
    
    # Seed population: all Defenders (Shield + Reproduce)
    sim.initialize_population(200)
    agents = list(sim.world.agents.values())
    for agent in agents:
        agent.genome = bytearray(DEFENDER_GENOME)
    
    print(f"Seeded {len(agents)} agents with DEFENDER genome")
    
    # FAITHH observer
    observer = None
    try:
        from faithh_observer import PulseWatcher
        observer = PulseWatcher()
    except Exception as e:
        print(f"[PULSE] Observer init failed (non-fatal): {e}")
    
    # Adaptive predator state
    shield_adaptation = 0.0
    
    # Tracking
    results = {
        'wave_count': 0, 'predator_kills': 0, 'thermal_deaths': 0,
        'parasitic_kills': 0, 'redirect_events': 0,
        'first_parasite_tick': None, 'first_parasite_agent': None,
        'first_toxin_tick': None,
        'adaptation_at_parasite': None,
    }
    
    first_parasite = None
    first_toxin = None
    redirect_active = False
    
    print()
    print("=" * 75)
    print("EXPERIMENT 5: THE PARASITIC EMERGENCE")
    print("=" * 75)
    print(f"Wave interval: {EXP5_WAVE_INTERVAL} ticks (L→R)")
    print(f"Parasitic drain: {PARASITE_DRAIN_RATE} energy/tick per adjacent victim")
    print(f"Threat redirect: {PARASITE_REDIRECT_FRACTION*100:.0f}% at tick {PARASITE_REDIRECT_TICK}")
    print(f"Toxin unlock: tick {TOXIN_UNLOCK_TICK}")
    print(f"Adaptation: +{ADAPTATION_RATE*100:.0f}% per {ADAPTATION_CHECK_INTERVAL} ticks")
    print(f"Running for {ticks} ticks")
    print("=" * 75)
    print()
    
    for t in range(ticks):
        # === PHASE UNLOCKS ===
        if t == PARASITE_REDIRECT_TICK and not redirect_active:
            redirect_active = True
            print(f"\n*** PHASE B UNLOCKED: Threat redirection active at tick {t} ***\n")
        
        if t == TOXIN_UNLOCK_TICK and not config.TOXIN_ACTIVE:
            config.TOXIN_ACTIVE = True
            print(f"\n*** PHASE C UNLOCKED: ACT_TOXIN available at tick {t} ***\n")
        
        # === SPAWN WAVE ===
        if t > 0 and t % EXP5_WAVE_INTERVAL == 0:
            wave = sim.world.spawn_wave(t)
            wave.stealth = False
            sim.world.active_waves.append(wave)
            sim.world.current_wave = wave
            results['wave_count'] += 1
        
        # === PROCESS ALL ACTIVE WAVES ===
        for wave in list(sim.world.active_waves):
            if not wave.active:
                sim.world.active_waves.remove(wave)
                continue
            
            negative_gaps = sim.check_wave_detection(wave, t, observer)
            
            contacts, toxin_contacts, redirects = apply_adaptive_wave_damage(
                sim.world, wave, t, shield_adaptation, redirect_active
            )
            results['redirect_events'] += redirects
            
            if toxin_contacts > 0:
                shield_adaptation = max(0.0, shield_adaptation - toxin_contacts * TOXIN_COUNTER_RATE)
            
            for agent_id, outcome in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent and not agent.alive:
                    results['predator_kills'] += 1
                    sim.world.remove_agent(agent)
                    sim.total_deaths += 1
            
            if wave.is_complete(t):
                wave.active = False
        
        # === PARASITIC DRAIN ===
        drained, p_count, v_count = apply_parasitic_drain(sim.world, t)
        # Remove parasitic kills
        for agent in list(sim.world.agents.values()):
            if not agent.alive:
                results['parasitic_kills'] += 1
                sim.world.remove_agent(agent)
                sim.total_deaths += 1
        
        # === ADAPTIVE PREDATOR UPDATE ===
        if t > 0 and t % ADAPTATION_CHECK_INTERVAL == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total > 0:
                shield_count = sum(1 for a in pop if has_shield(a))
                shield_pct = shield_count / total
                if shield_pct > SHIELD_DOMINANCE_THRESHOLD:
                    shield_adaptation = min(1.5, shield_adaptation + ADAPTATION_RATE)
                else:
                    shield_adaptation = max(0.0, shield_adaptation - ADAPTATION_DECAY_RATE)
        
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
        
        # === EMERGENCE DETECTION ===
        for agent in sim.world.agents.values():
            # Parasite emergence (gen > 1 = survived + reproduced from)
            if has_signal(agent) and agent.generation > 1 and not hasattr(agent, '_parasite_logged'):
                agent._parasite_logged = True
                if first_parasite is None:
                    first_parasite = (t, agent.id, agent.generation)
                    results['first_parasite_tick'] = t
                    results['first_parasite_agent'] = agent.id
                    results['adaptation_at_parasite'] = shield_adaptation
                    print(f"\n*** FIRST PARASITE LINEAGE: {agent.id} at tick {t} gen={agent.generation:.0f} ***")
                    print(f"*** Adaptation level: {shield_adaptation:.2f} ***\n")
            
            # Toxin emergence
            if has_toxin(agent) and agent.generation > 1 and not hasattr(agent, '_toxin_logged'):
                agent._toxin_logged = True
                if first_toxin is None:
                    first_toxin = (t, agent.id, agent.generation)
                    results['first_toxin_tick'] = t
                    print(f"\n*** FIRST TOXIN LINEAGE: {agent.id} at tick {t} gen={agent.generation:.0f} ***")
                    print(f"*** Parasites present: {sum(1 for a in sim.world.agents.values() if has_signal(a))} ***\n")
        
        # === SIMULATION TICK ===
        sim.tick()
        
        # === COLLAPSE CHECK ===
        if sim.world.get_population() == 0:
            print(f"\n*** POPULATION COLLAPSED at tick {t} ***\n")
            break
        
        # === LOGGING ===
        if t % log_interval == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total == 0:
                continue
            
            defenders = sum(1 for a in pop if get_strategy(a) == "DEFENDER")
            parasites = sum(1 for a in pop if "PARASITE" in get_strategy(a))
            toxins = sum(1 for a in pop if "TOXIN" in get_strategy(a) or get_strategy(a) == "APEX")
            naked = sum(1 for a in pop if get_strategy(a) == "NAKED")
            
            avg_energy = sum(a.energy for a in pop) / total
            avg_gen = sum(a.generation for a in pop) / total
            shield_eff = max(0, (1.0 - shield_adaptation) * 100)
            
            phase = "A"
            if t >= TOXIN_UNLOCK_TICK:
                phase = "C"
            elif t >= PARASITE_REDIRECT_TICK:
                phase = "B"
            
            markers = []
            if parasites > 0:
                markers.append("PARASITES")
            if toxins > 0:
                markers.append("TOXIN")
            marker_str = f" [{'+'.join(markers)}]" if markers else ""
            
            print(f"Tick {t:6d} [{phase}]: pop={total:4d} | def={defenders:3d} "
                  f"para={parasites:3d} tox={toxins:3d} naked={naked:3d} | "
                  f"adapt={shield_adaptation:.2f} shld_eff={shield_eff:3.0f}% | "
                  f"E={avg_energy:.0f} gen={avg_gen:.0f}{marker_str}")
    
    # === FINAL RESULTS ===
    pop = list(sim.world.agents.values())
    total = len(pop)
    
    print()
    print("=" * 75)
    print("EXPERIMENT 5 RESULTS: THE PARASITIC EMERGENCE")
    print("=" * 75)
    print(f"Final population:       {total}")
    print(f"Wave count:             {results['wave_count']}")
    print(f"Predator kills:         {results['predator_kills']}")
    print(f"Parasitic kills:        {results['parasitic_kills']}")
    print(f"Redirect events:        {results['redirect_events']}")
    print(f"Thermal deaths:         {results['thermal_deaths']}")
    print(f"Total reproductions:    {sim.total_reproductions}")
    print(f"Total deaths:           {sim.total_deaths}")
    print()
    print(f"Final adaptation:       {shield_adaptation:.2f}")
    print(f"Shield effectiveness:   {max(0, (1.0-shield_adaptation)*100):.0f}%")
    
    if total > 0:
        for strat in ["DEFENDER", "PARASITE", "PARASITE+", "TOXIN", "APEX", "NAKED"]:
            count = sum(1 for a in pop if get_strategy(a) == strat)
            if count > 0:
                print(f"  {strat:12s}: {count:4d} ({count/total*100:.1f}%)")
    
    print()
    if first_parasite:
        pt, pid, pgen = first_parasite
        print(f"First parasite lineage: tick {pt}, {pid}, gen {pgen:.0f}")
        print(f"  Adaptation at emergence: {results['adaptation_at_parasite']:.2f}")
    else:
        print("First parasite lineage: NONE")
    
    if first_toxin:
        tt, tid, tgen = first_toxin
        print(f"First toxin lineage:    tick {tt}, {tid}, gen {tgen:.0f}")
    else:
        print("First toxin lineage:    NONE")
    
    # Determine outcome
    has_parasites = first_parasite is not None
    has_toxins_result = first_toxin is not None
    has_multiple = (sum(1 for s in ["DEFENDER", "PARASITE", "TOXIN", "APEX"]
                       if any(get_strategy(a) == s for a in pop)) >= 2) if total > 0 else False
    
    if has_toxins_result and has_parasites:
        outcome = "FULL_OFFENSIVE_STACK"
    elif has_parasites and has_multiple:
        outcome = "ARMS_RACE"
    elif has_parasites:
        outcome = "PARASITISM_EMERGES"
    elif total == 0:
        outcome = "COLLAPSE"
    else:
        outcome = "NO_OFFENSIVE_EMERGENCE"
    
    print(f"\nOutcome:                {outcome}")
    print("=" * 75)
    
    if observer:
        observer.close()
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ALIFE Experiment 5: The Parasitic Emergence")
    parser.add_argument("--ticks", type=int, default=50000)
    parser.add_argument("--log-interval", type=int, default=1000)
    args = parser.parse_args()
    
    run_experiment_5(ticks=args.ticks, log_interval=args.log_interval)
