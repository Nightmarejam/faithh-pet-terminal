"""
ALIFE Experiment 9: Diversity Floor — Sustaining Oscillating Equilibrium
Track A (pure emergence science)

Pre-registered hypothesis (written before running, 2026-03-29):
  The oscillating equilibrium from Exp 8b (ticks 0–28,000) will be maintained past 
  tick 28,000. Floor will activate intermittently (predicted 3–8 events). Adapt 
  will not exceed 0.60 sustained. System survives 50,000 ticks. Gaming behavior 
  may emerge as a structural maintenance mechanism, not an adversarial one.

Condition:
  200 agents, 50% DEFENDER / 50% NAKED seed, drain=1.5, adaptive predator, 50,000 ticks
  NAKED fraction floor: if NAKED fraction < 15%, give each NAKED agent +3 energy/tick
  Floor deactivates automatically when fraction recovers above 15%

Lineage logging:
  Every reproduction event writes one line to /tmp/exp9_lineage.tsv:
    tick  child_id  parent_id  parent_genome_hex  parent_strategy

Baselines:
  Exp 8b cond 3 (50/50, no floor): survived 50K (oscillation broke tick 28K)
"""

import sys
import os
import csv
import json
from collections import defaultdict

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
PROC_THRESHOLD = 0x00
PROC_PREDICT = 0x04
MEM_NONE = 0x00
MEM_PATTERN = 0x06
ACT_REPRODUCE = 0x04
ACT_SHIELD = 0x03
ACT_SIGNAL = 0x05
ACT_TOXIN = 0x06
ACT_FLEE = 0x07
REG_NONE = 0x00

# Stressor parameters — identical to Exp 8b
PARASITE_DRAIN_RATE = 1.5
PARASITE_REDIRECT_FRACTION = 0.3
PARASITE_REDIRECT_TICK = 5000
TOXIN_UNLOCK_TICK = 15000

# Floor parameters
NAKED_FLOOR_THRESHOLD = 0.15  # 15%
NAKED_FLOOR_BONUS = 3
GAMER_WINDOW = 200  # ticks

# Seeded genomes
DEFENDER_GENOME = bytes([
    SENSE_LIGHT, SENSE_THREAT, PROC_THRESHOLD, PROC_PREDICT,
    MEM_PATTERN, ACT_REPRODUCE, ACT_SHIELD, REG_NONE
])

NAKED_GENOME = bytes([
    SENSE_LIGHT, SENSE_THREAT, PROC_THRESHOLD, PROC_PREDICT,
    MEM_PATTERN, ACT_REPRODUCE, ACT_REPRODUCE, REG_NONE
])


def has_shield(agent) -> bool:
    return agent.genome[5] == ACT_SHIELD or agent.genome[6] == ACT_SHIELD

def has_signal(agent) -> bool:
    return agent.genome[5] == ACT_SIGNAL or agent.genome[6] == ACT_SIGNAL

def has_toxin(agent) -> bool:
    return agent.genome[5] == ACT_TOXIN or agent.genome[6] == ACT_TOXIN

def get_strategy(agent) -> str:
    sig = has_signal(agent)
    shd = has_shield(agent)
    tox = has_toxin(agent)
    if tox and sig:   return "APEX"
    elif tox:         return "TOXIN"
    elif sig and shd: return "PARASITE+"
    elif sig:         return "PARASITE"
    elif shd:         return "DEFENDER"
    else:             return "NAKED"


def apply_parasitic_drain(world):
    for agent in list(world.agents.values()):
        if not agent.alive or not agent.signaling:
            continue
        neighbors = world.get_adjacent_agents(agent.x, agent.y, radius=1)
        for victim in neighbors:
            if not victim.alive or victim.signaling:
                continue
            drain = min(PARASITE_DRAIN_RATE, victim.energy)
            if drain > 0:
                victim.energy -= drain
                agent.energy = min(agent.energy + drain, 255)
                if victim.energy <= 0:
                    victim.energy = 0
                    victim.alive = False


def apply_adaptive_wave_damage(world, wave, current_tick, shield_adaptation,
                                redirect_active=False):
    contacts = []
    toxin_contacts = 0
    redirect_events = 0
    front = wave.front_position(current_tick)
    for agent_id, agent in list(world.agents.items()):
        if not agent.alive:
            continue
        if abs(agent.x - front) < 1.0:
            MIN_ARRIVAL_GAP = 50
            if not agent.wave_arrival_times or \
               (current_tick - agent.wave_arrival_times[-1]) > MIN_ARRIVAL_GAP:
                agent.wave_arrival_times.append(current_tick)
                agent.wave_arrival_times = agent.wave_arrival_times[-8:]
            if wave.stealth:
                agent.energy -= STEALTH_WAVE_DAMAGE
                if agent.energy <= 0:
                    agent.energy = 0
                    agent.alive = False
                contacts.append((agent_id, 'stealth_kill'))
                continue
            agent_has_toxin = has_toxin(agent) and agent.toxin_active
            agent_has_shield = has_shield(agent) and agent.shield_active
            agent_is_parasite = has_signal(agent) and agent.signaling
            if agent_has_toxin:
                damage = PREDATOR_DAMAGE * (1.0 - TOXIN_DAMAGE_REDUCTION)
                agent.energy -= damage
                toxin_contacts += 1
                outcome = 'toxin_defend'
            elif agent_has_shield:
                shield_eff = max(0.0, 1.0 - shield_adaptation)
                damage = PREDATOR_DAMAGE * (1.0 - shield_eff)
                agent.energy -= damage
                outcome = 'shield_defend'
            elif agent_is_parasite and redirect_active:
                own_damage = PREDATOR_DAMAGE * (1.0 - PARASITE_REDIRECT_FRACTION)
                agent.energy -= own_damage
                neighbors = world.get_adjacent_agents(agent.x, agent.y, radius=1)
                victims = [n for n in neighbors if n.alive and not n.signaling]
                if victims:
                    per_victim = PREDATOR_DAMAGE * PARASITE_REDIRECT_FRACTION / len(victims)
                    for v in victims:
                        v.energy -= per_victim
                        if v.energy <= 0:
                            v.energy = 0
                            v.alive = False
                    redirect_events += 1
                else:
                    agent.energy -= PREDATOR_DAMAGE * PARASITE_REDIRECT_FRACTION
                outcome = 'parasite_redirect'
            else:
                agent.energy -= PREDATOR_DAMAGE
                outcome = 'unshielded'
            if agent.energy <= 0:
                agent.energy = 0
                agent.alive = False
            contacts.append((agent_id, outcome))
    return contacts, toxin_contacts, redirect_events


def run_exp9(ticks: int = 50000, log_interval: int = 1000) -> dict:
    """
    Run Experiment 9: Diversity Floor
    """
    import config
    config.SIGNAL_ACTIVE = True
    config.TOXIN_ACTIVE = False

    # Open log files
    lineage_file = open('/tmp/exp9_lineage.tsv', 'w', newline='')
    lineage_writer = csv.writer(lineage_file, delimiter='\t')
    lineage_writer.writerow(['tick', 'child_id', 'parent_id', 'parent_genome_hex', 'parent_strategy'])

    floor_log_file = open('/tmp/exp9_floor.log', 'w')

    # Initialize simulation
    sim = Simulation(experiment=9)
    sim.world.initialize_light_gradient()
    sim.world.current_wave = None
    sim.initialize_population(200)

    # Seed 50/50 NAKED/DEFENDER population
    seeded_naked_ids = set()
    agents = list(sim.world.agents.values())
    naked_count_seed = int(len(agents) * 0.5)
    for i, agent in enumerate(agents):
        if i < naked_count_seed:
            agent.genome = bytearray(NAKED_GENOME)
            agent._seeded_naked = True
            seeded_naked_ids.add(agent.id)
        else:
            agent.genome = bytearray(DEFENDER_GENOME)
            agent._seeded_naked = False
        agent._birth_tick = 0
        agent._last_reproduction_tick = None

    # Lineage logging callback
    def on_reproduce_log(parent, child):
        lineage_writer.writerow([
            sim.world.current_tick,
            child.id,
            parent.id,
            bytes(parent.genome).hex(),
            get_strategy(parent)
        ])
        child._seeded_naked = getattr(parent, '_seeded_naked', False)
        child._last_reproduction_tick = sim.world.current_tick
        if getattr(parent, '_seeded_naked', False):
            seeded_naked_ids.add(child.id)

    # Patch simulation to use lineage logging
    original_process = sim._process_reproductions
    def patched_process_reproductions():
        from config import REPRODUCTION_THRESHOLD, MAX_POPULATION
        current_pop = sim.world.get_population()
        if current_pop >= MAX_POPULATION:
            sim.world.reproduction_queue.clear()
            return
        density_penalty = max(0, (current_pop - 150) // 5)
        effective_threshold = REPRODUCTION_THRESHOLD + density_penalty
        for parent in sim.world.reproduction_queue:
            if not parent.alive or parent.energy < effective_threshold:
                continue
            spawn_pos = sim.world.find_empty_adjacent(parent.x, parent.y)
            if spawn_pos is None:
                continue
            child_genome = sim._mutate_genome(parent.genome)
            child = parent.create_child(spawn_pos[0], spawn_pos[1], child_genome, on_reproduce=on_reproduce_log)
            if sim.world.add_agent(child):
                sim.total_reproductions += 1
                parent.reproduction_cooldown = 20
        sim.world.reproduction_queue.clear()
    sim._process_reproductions = patched_process_reproductions

    print()
    print("=" * 70)
    print("EXPERIMENT 9 — DIVERSITY FLOOR")
    print("=" * 70)
    print(f"  Seed: {naked_count_seed} NAKED (50%) + {len(agents)-naked_count_seed} DEFENDER (50%)")
    print(f"  Drain: {PARASITE_DRAIN_RATE} | Waves every {EXP5_WAVE_INTERVAL} ticks")
    print(f"  Floor: NAKED fraction < {NAKED_FLOOR_THRESHOLD*100:.0f}% → +{NAKED_FLOOR_BONUS} energy/tick to NAKED")
    print(f"  GAMER tracking: reproduction within {GAMER_WINDOW} ticks of floor activation")
    print("=" * 70)

    # Run state
    shield_adaptation = 0.0
    redirect_active = False
    floor_active = False
    floor_activations = 0
    floor_activation_ticks = []
    last_floor_activation_tick = None

    results = {
        'experiment': 9,
        'condition': 'diversity_floor',
        'collapsed': False,
        'collapse_tick': None,
        'final_population': 0,
        'wave_count': 0,
        'predator_kills': 0,
        'thermal_deaths': 0,
        'first_parasite_tick': None,
        'first_toxin_tick': None,
        'total_reproduction_events': 0,
        'strategy_escape_tick': None,
        'floor_activations': 0,
        'floor_events': [],
        'max_adapt_reached': 0.0,
        'population_timeline': []
    }

    for t in range(ticks):
        sim.world.current_tick = t

        if t == PARASITE_REDIRECT_TICK and not redirect_active:
            redirect_active = True
            print(f"\n  *** PHASE B: redirect active tick {t} ***\n")
        if t == TOXIN_UNLOCK_TICK and not config.TOXIN_ACTIVE:
            config.TOXIN_ACTIVE = True
            print(f"\n  *** PHASE C: toxin available tick {t} ***\n")

        # Spawn wave
        if t > 0 and t % EXP5_WAVE_INTERVAL == 0:
            wave = sim.world.spawn_wave(t)
            wave.stealth = False
            sim.world.active_waves.append(wave)
            sim.world.current_wave = wave
            results['wave_count'] += 1

        # Process waves
        for wave in list(sim.world.active_waves):
            if not wave.active:
                sim.world.active_waves.remove(wave)
                continue
            sim.check_wave_detection(wave, t, None)
            contacts, toxin_contacts, redirects = apply_adaptive_wave_damage(
                sim.world, wave, t, shield_adaptation, redirect_active
            )
            if toxin_contacts > 0:
                shield_adaptation = max(0.0,
                    shield_adaptation - toxin_contacts * TOXIN_COUNTER_RATE)
            for agent_id, outcome in contacts:
                agent = sim.world.agents.get(agent_id)
                if agent and not agent.alive:
                    results['predator_kills'] += 1
                    sim.world.remove_agent(agent)
                    sim.total_deaths += 1
            if wave.is_complete(t):
                wave.active = False

        # Parasitic drain
        apply_parasitic_drain(sim.world)
        for agent in list(sim.world.agents.values()):
            if not agent.alive:
                results['thermal_deaths'] += 1
                sim.world.remove_agent(agent)
                sim.total_deaths += 1

        # Adaptive predator
        if t > 0 and t % ADAPTATION_CHECK_INTERVAL == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total > 0:
                shield_count = sum(1 for a in pop if has_shield(a))
                if shield_count / total > SHIELD_DOMINANCE_THRESHOLD:
                    shield_adaptation = min(1.5, shield_adaptation + ADAPTATION_RATE)
                else:
                    shield_adaptation = max(0.0,
                        shield_adaptation - ADAPTATION_DECAY_RATE)

        if shield_adaptation > results['max_adapt_reached']:
            results['max_adapt_reached'] = shield_adaptation

        # Thermal drain
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

        # NAKED fraction floor
        pop_now = list(sim.world.agents.values())
        total_now = len(pop_now)
        if total_now > 0:
            naked_agents = [a for a in pop_now if get_strategy(a) == 'NAKED']
            naked_frac = len(naked_agents) / total_now
            was_active = floor_active

            if naked_frac < NAKED_FLOOR_THRESHOLD:
                floor_active = True
                for a in naked_agents:
                    a.add_energy(NAKED_FLOOR_BONUS)
            else:
                floor_active = False

            # Log floor events
            if floor_active and not was_active:
                floor_activations += 1
                last_floor_activation_tick = t
                floor_activation_ticks.append(t)
                floor_event = {
                    'event': 'ACTIVATE',
                    'tick': t,
                    'naked_fraction': naked_frac,
                    'naked_count': len(naked_agents),
                    'total_pop': total_now
                }
                results['floor_events'].append(floor_event)
                floor_log_file.write(f"[{t}] FLOOR ACTIVATE: naked_frac={naked_frac:.3f} ({len(naked_agents)}/{total_now})\n")
                floor_log_file.flush()
            elif not floor_active and was_active:
                floor_event = {
                    'event': 'DEACTIVATE',
                    'tick': t,
                    'naked_fraction': naked_frac,
                    'naked_count': len(naked_agents),
                    'total_pop': total_now
                }
                results['floor_events'].append(floor_event)
                floor_log_file.write(f"[{t}] FLOOR DEACTIVATE: naked_frac={naked_frac:.3f} ({len(naked_agents)}/{total_now})\n")
                floor_log_file.flush()

        # Emergence detection
        for agent in sim.world.agents.values():
            if not agent.alive:
                continue
            if (has_signal(agent) and agent.generation > 1
                    and not hasattr(agent, '_parasite_logged')):
                agent._parasite_logged = True
                if results['first_parasite_tick'] is None:
                    results['first_parasite_tick'] = t
                    print(f"\n  *** FIRST PARASITE: {agent.id} tick {t} "
                          f"gen={agent.generation:.0f} ***\n")
            if (has_toxin(agent) and agent.generation > 1
                    and not hasattr(agent, '_toxin_logged')):
                agent._toxin_logged = True
                if results['first_toxin_tick'] is None:
                    results['first_toxin_tick'] = t
                    print(f"\n  *** FIRST TOXIN: {agent.id} tick {t} "
                          f"gen={agent.generation:.0f} ***\n")

        # Strategy escape detection
        if results['strategy_escape_tick'] is None:
            pop = list(sim.world.agents.values())
            if len(pop) > 10:
                shield_count = sum(1 for a in pop if has_shield(a))
                if shield_count / len(pop) < 0.05:
                    results['strategy_escape_tick'] = t
                    print(f"\n  *** STRATEGY ESCAPE: shields < 5% of pop at "
                          f"tick {t} (adapt={shield_adaptation:.2f}) ***\n")

        sim.tick()

        if sim.world.get_population() == 0:
            results['collapsed'] = True
            results['collapse_tick'] = t
            print(f"\n  *** COLLAPSED at tick {t} ***\n")
            break

        # Periodic logging
        if t % log_interval == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total == 0:
                continue
            
            # Count strategies
            defenders = sum(1 for a in pop if get_strategy(a) == 'DEFENDER')
            naked = sum(1 for a in pop if get_strategy(a) == 'NAKED')
            parasites = sum(1 for a in pop if 'PARASITE' in get_strategy(a))
            
            # Count GAMERs
            gamers = 0
            if last_floor_activation_tick is not None:
                for a in pop:
                    if hasattr(a, '_last_reproduction_tick') and a._last_reproduction_tick is not None:
                        if last_floor_activation_tick <= a._last_reproduction_tick <= last_floor_activation_tick + GAMER_WINDOW:
                            gamers += 1
            
            avg_energy = sum(a.energy for a in pop) / total
            shield_eff = max(0, (1.0 - shield_adaptation) * 100)
            phase = ("C" if t >= TOXIN_UNLOCK_TICK
                     else "B" if t >= PARASITE_REDIRECT_TICK else "A")
            floor_status = "ON" if floor_active else "OFF"
            
            print(f"Tick {t:6d} [{phase}]: pop={total:4d} | "
                  f"def={defenders:3d} nak={naked:3d} gam={gamers:3d} | "
                  f"floor={floor_status} frac={naked_frac:.2f} | "
                  f"adapt={shield_adaptation:.2f} shld={shield_eff:3.0f}% | "
                  f"E={avg_energy:.0f}")
            
            results['population_timeline'].append({
                'tick': t, 'phase': phase, 'pop': total,
                'defenders': defenders, 'naked': naked, 'gamers': gamers,
                'floor_active': floor_active, 'naked_fraction': naked_frac,
                'adapt': round(shield_adaptation, 2),
                'shield_eff_pct': round(shield_eff),
                'avg_energy': round(avg_energy),
            })

    # Close log files
    lineage_file.close()
    floor_log_file.close()

    # Final population analysis
    pop = list(sim.world.agents.values())
    total = len(pop)
    results['final_population'] = total
    results['final_strategy'] = {}
    results['floor_activations'] = floor_activations
    
    if total > 0:
        for strat in ["DEFENDER", "NAKED", "PARASITE", "TOXIN", "APEX"]:
            count = sum(1 for a in pop if get_strategy(a) == strat)
            if count > 0:
                results['final_strategy'][strat] = {
                    'count': count, 'pct': round(count/total*100, 1)
                }

    # Save results JSON
    with open('genomic_results/exp9_diversity_floor_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 70)
    print("EXPERIMENT 9 RESULT")
    print("=" * 70)
    print(f"  Collapsed: {'YES tick ' + str(results['collapse_tick']) if results['collapsed'] else 'NO — survived'}")
    print(f"  Final pop: {total}")
    print(f"  Floor activations: {floor_activations}")
    print(f"  Max adapt reached: {results['max_adapt_reached']:.2f}")
    print(f"  Strategy escape: {'tick ' + str(results['strategy_escape_tick']) if results['strategy_escape_tick'] else 'not detected'}")
    for strat, data in results.get('final_strategy', {}).items():
        print(f"  {strat:12s}: {data['count']:4d} ({data['pct']}%)")
    print(f"  Results saved to: genomic_results/exp9_diversity_floor_results.json")

    return results


if __name__ == '__main__':
    import random
    random.seed(42)
    run_exp9()
