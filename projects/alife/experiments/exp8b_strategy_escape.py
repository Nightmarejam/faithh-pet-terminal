"""
ALIFE Experiment 8b: Strategy Escape Isolation — Seeded Diversity vs Stochastic Emergence
Track A (pure emergence science)

Pre-registered hypothesis (written before running, 2026-03-29):
  Condition 3 (50/50 DEFENDER/NAKED seed) will survive past Exp 5's collapse
  tick of 10,039. The surviving lineage will trace predominantly to the seeded
  NAKED population, confirming that pre-seeded diversity enables intentional
  escape rather than requiring stochastic emergence.

  If survivors instead trace to late DEFENDER->NAKED mutations, the escape
  mechanism is robust and finds itself regardless of initial conditions.
  That result changes the Constella implication: the design job becomes
  ensuring enough population survives long enough for mutation to find the exit,
  not pre-seeding the exit strategy.

Conditions (run sequentially, identical stressors):
  Condition 1: 200 agents, 100% DEFENDER seed — Exp 5 replication
  Condition 3: 200 agents, 50% DEFENDER / 50% NAKED seed

Lineage logging:
  Every reproduction event writes one line to /tmp/exp8b_<condition>_lineage.tsv:
    tick  child_id  parent_id  parent_genome_hex  parent_strategy  parent_energy

Baselines:
  Exp 5 (100% DEFENDER, no floor): collapsed tick 10,039
  Exp 7 (100% DEFENDER, gated floor, escape emerged): survived 50,000 ticks
"""

import sys
import os
import csv
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

# Stressor parameters — identical to Exp 5/6/7
PARASITE_DRAIN_RATE = 1.5
PARASITE_REDIRECT_FRACTION = 0.3
PARASITE_REDIRECT_TICK = 5000
TOXIN_UNLOCK_TICK = 15000

# Seeded genomes
DEFENDER_GENOME = bytes([
    SENSE_LIGHT, SENSE_THREAT, PROC_THRESHOLD, PROC_PREDICT,
    MEM_PATTERN, ACT_REPRODUCE, ACT_SHIELD, REG_NONE
])

# NAKED: same structure as DEFENDER but slot 6 = ACT_REPRODUCE instead of ACT_SHIELD
# No active-cost gene in positions 5-6 — reproduction-maximizing, zero overhead
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


def run_condition(condition_name: str, naked_fraction: float,
                  ticks: int = 50000, log_interval: int = 1000) -> dict:
    """
    Run one condition of Exp 8b.

    condition_name: label for logs/files
    naked_fraction: 0.0 = all DEFENDER, 0.5 = 50/50, 1.0 = all NAKED
    """
    import config
    config.SIGNAL_ACTIVE = True
    config.TOXIN_ACTIVE = False

    lineage_path = f"/tmp/exp8b_{condition_name}_lineage.tsv"
    lineage_file = open(lineage_path, 'w', newline='')
    lineage_writer = csv.writer(lineage_file, delimiter='\t')
    lineage_writer.writerow([
        'tick', 'child_id', 'parent_id',
        'parent_genome_hex', 'parent_strategy', 'parent_energy',
        'parent_is_seeded_naked'
    ])

    sim = Simulation(experiment=8)
    sim.world.initialize_light_gradient()
    sim.world.current_wave = None
    sim.initialize_population(200)

    # Track which agent IDs were seeded as NAKED
    seeded_naked_ids = set()

    agents = list(sim.world.agents.values())
    naked_count = int(len(agents) * naked_fraction)
    for i, agent in enumerate(agents):
        if i < naked_count:
            agent.genome = bytearray(NAKED_GENOME)
            agent._seeded_naked = True
            seeded_naked_ids.add(agent.id)
        else:
            agent.genome = bytearray(DEFENDER_GENOME)
            agent._seeded_naked = False
        agent._birth_tick = 0

    print()
    print("=" * 70)
    print(f"EXPERIMENT 8b — CONDITION: {condition_name}")
    print("=" * 70)
    print(f"  Seeded: {naked_count} NAKED ({naked_fraction*100:.0f}%) + "
          f"{len(agents)-naked_count} DEFENDER ({(1-naked_fraction)*100:.0f}%)")
    print(f"  Drain: {PARASITE_DRAIN_RATE} | Waves every {EXP5_WAVE_INTERVAL} ticks")
    print(f"  Lineage log: {lineage_path}")
    print()
    print(f"  Pre-registered hypothesis:")
    if naked_fraction == 0.0:
        print(f"  CONDITION 1 (baseline): should collapse ~tick 10,039 (Exp 5 replication)")
    else:
        print(f"  CONDITION 3 (50/50): should survive past tick 10,039")
        print(f"  Lineage question: do survivors trace to seeded NAKED or late mutations?")
    print("=" * 70)

    shield_adaptation = 0.0
    redirect_active = False

    results = {
        'condition': condition_name,
        'naked_fraction': naked_fraction,
        'collapsed': False,
        'collapse_tick': None,
        'final_population': 0,
        'wave_count': 0,
        'predator_kills': 0,
        'thermal_deaths': 0,
        'first_parasite_tick': None,
        'first_toxin_tick': None,
        'lineage_path': lineage_path,
        'total_reproduction_events': 0,
        'strategy_escape_tick': None,
        'population_timeline': []
    }

    for t in range(ticks):
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

        # === LINEAGE LOGGING — hook into generation increment ===
        for agent in sim.world.agents.values():
            if not agent.alive:
                continue
            if not hasattr(agent, '_last_gen_logged'):
                agent._last_gen_logged = agent.generation
            if agent.generation > agent._last_gen_logged:
                # Agent just reproduced — log the event
                is_seeded_naked = getattr(agent, '_seeded_naked', False)
                lineage_writer.writerow([
                    t,
                    f"{agent.id}_g{agent.generation:.0f}",
                    agent.id,
                    agent.genome.hex(),
                    get_strategy(agent),
                    int(agent.energy),
                    1 if is_seeded_naked else 0
                ])
                agent._last_gen_logged = agent.generation
                results['total_reproduction_events'] += 1

                # Pass seeded_naked flag to children via agent attribute
                # (children inherit parent's seeded status for lineage tracing)
                # This is done by tagging newly created agents in world
                for child in list(sim.world.agents.values()):
                    if (not hasattr(child, '_seeded_naked')
                            and child.parent_id == agent.id):
                        child._seeded_naked = is_seeded_naked
                        child._last_gen_logged = child.generation
                        if is_seeded_naked:
                            seeded_naked_ids.add(child.id)

        # Strategy escape detection
        if results['strategy_escape_tick'] is None:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total > 10:
                shield_count = sum(1 for a in pop if has_shield(a))
                if shield_count / total < 0.05:
                    results['strategy_escape_tick'] = t
                    print(f"\n  *** STRATEGY ESCAPE: shields < 5% of pop at "
                          f"tick {t} (adapt={shield_adaptation:.2f}) ***\n")

        sim.tick()

        if sim.world.get_population() == 0:
            results['collapsed'] = True
            results['collapse_tick'] = t
            print(f"\n  *** COLLAPSED at tick {t} ***\n")
            break

        if t % log_interval == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total == 0:
                continue
            defenders = sum(1 for a in pop if get_strategy(a) == 'DEFENDER')
            naked = sum(1 for a in pop if get_strategy(a) == 'NAKED')
            parasites = sum(1 for a in pop if 'PARASITE' in get_strategy(a))
            avg_energy = sum(a.energy for a in pop) / total
            shield_eff = max(0, (1.0 - shield_adaptation) * 100)
            phase = ("C" if t >= TOXIN_UNLOCK_TICK
                     else "B" if t >= PARASITE_REDIRECT_TICK else "A")
            seeded_naked_alive = sum(
                1 for a in pop if getattr(a, '_seeded_naked', False))
            print(f"  Tick {t:6d} [{phase}]: pop={total:4d} | "
                  f"def={defenders:3d} nak={naked:4d} par={parasites:2d} | "
                  f"seeded_nak_alive={seeded_naked_alive:4d} | "
                  f"adapt={shield_adaptation:.2f} shld={shield_eff:3.0f}% | "
                  f"E={avg_energy:.0f}")
            results['population_timeline'].append({
                'tick': t, 'phase': phase, 'pop': total,
                'defenders': defenders, 'naked': naked,
                'seeded_naked_alive': seeded_naked_alive,
                'adapt': round(shield_adaptation, 2),
                'shield_eff_pct': round(shield_eff),
                'avg_energy': round(avg_energy)
            })

    lineage_file.flush()
    lineage_file.close()

    pop = list(sim.world.agents.values())
    total = len(pop)
    results['final_population'] = total
    results['final_strategy'] = {}
    results['final_seeded_naked_alive'] = sum(
        1 for a in pop if getattr(a, '_seeded_naked', False))

    if total > 0:
        for strat in ["DEFENDER", "NAKED", "PARASITE", "TOXIN", "APEX"]:
            count = sum(1 for a in pop if get_strategy(a) == strat)
            if count > 0:
                results['final_strategy'][strat] = {
                    'count': count, 'pct': round(count/total*100, 1)
                }

    print()
    print(f"  --- CONDITION {condition_name} RESULT ---")
    print(f"  Collapsed:       {'YES tick ' + str(results['collapse_tick']) if results['collapsed'] else 'NO — survived'}")
    print(f"  Final pop:       {total}")
    print(f"  Seeded nak alive:{results['final_seeded_naked_alive']}")
    print(f"  Lineage log:     {lineage_path} "
          f"({results['total_reproduction_events']} events)")
    print(f"  Strategy escape: {'tick ' + str(results['strategy_escape_tick']) if results['strategy_escape_tick'] else 'not detected'}")
    for strat, data in results.get('final_strategy', {}).items():
        print(f"  {strat:12s}: {data['count']:4d} ({data['pct']}%)")
    print()

    return results


def analyze_lineage(condition_name: str, collapse_tick) -> dict:
    """
    Post-run lineage analysis.
    Answers: do survivors trace to seeded NAKED lineage or to independent mutations?
    """
    path = f"/tmp/exp8b_{condition_name}_lineage.tsv"
    try:
        with open(path) as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)
    except FileNotFoundError:
        return {'error': f'No lineage file at {path}'}

    if not rows:
        return {'error': 'Empty lineage file'}

    total_events = len(rows)
    seeded_naked_events = sum(1 for r in rows if r['parent_is_seeded_naked'] == '1')
    defender_events = sum(1 for r in rows if r['parent_strategy'] == 'DEFENDER')
    naked_events = sum(1 for r in rows if r['parent_strategy'] == 'NAKED')

    # Events in the final 10000 ticks (or after escape tick)
    if collapse_tick:
        late_cutoff = max(0, collapse_tick - 5000)
    else:
        late_cutoff = 40000
    late_rows = [r for r in rows if int(r['tick']) >= late_cutoff]
    late_seeded = sum(1 for r in late_rows if r['parent_is_seeded_naked'] == '1')
    late_total = len(late_rows)

    # Dominant genome in final phase
    if late_rows:
        genome_counts = defaultdict(int)
        for r in late_rows:
            genome_counts[r['parent_genome_hex']] += 1
        dominant_genome = max(genome_counts, key=genome_counts.get)
        dominant_count = genome_counts[dominant_genome]
    else:
        dominant_genome = None
        dominant_count = 0

    late_seeded_pct = (late_seeded / late_total * 100) if late_total > 0 else 0

    print(f"\n  === LINEAGE ANALYSIS: {condition_name} ===")
    print(f"  Total reproduction events:    {total_events:,}")
    print(f"  From seeded NAKED lineage:    {seeded_naked_events:,} "
          f"({seeded_naked_events/total_events*100:.1f}% of all events)")
    print(f"  From DEFENDER strategy:       {defender_events:,}")
    print(f"  From NAKED strategy:          {naked_events:,}")
    print(f"  Late-phase events (tick {late_cutoff}+): {late_total:,}")
    print(f"  Late seeded NAKED fraction:   {late_seeded_pct:.1f}%")
    if dominant_genome:
        print(f"  Dominant late genome:         {dominant_genome} "
              f"(x{dominant_count} in late phase)")
    print()

    if late_seeded_pct >= 60:
        verdict = "SEEDED_LINEAGE_DOMINANT"
        interpretation = ("Survivors predominantly descend from seeded NAKED population. "
                          "Pre-seeded diversity enables intentional escape. "
                          "Constella implication: deliberately maintaining multiple "
                          "participation modes is load-bearing for resilience.")
    elif late_seeded_pct <= 20:
        verdict = "INDEPENDENT_MUTATION_DOMINANT"
        interpretation = ("Survivors predominantly descend from DEFENDER->NAKED mutations "
                          "that emerged independently under pressure. Escape is stochastic "
                          "and robust — it finds itself regardless of seeding. "
                          "Constella implication: design job is ensuring population "
                          "survives long enough for mutation to find the exit — exactly "
                          "what a calibrated UCF floor would do.")
    else:
        verdict = "MIXED_LINEAGE"
        interpretation = ("Both seeded NAKED and independent mutations contributed to "
                          "survival. Both mechanisms are active. Further runs needed "
                          "to determine which is dominant.")

    print(f"  Verdict:    {verdict}")
    print(f"  Meaning:    {interpretation}")
    print()

    return {
        'condition': condition_name,
        'total_events': total_events,
        'seeded_naked_events': seeded_naked_events,
        'late_seeded_pct': round(late_seeded_pct, 1),
        'late_cutoff_tick': late_cutoff,
        'dominant_late_genome': dominant_genome,
        'verdict': verdict,
        'interpretation': interpretation
    }


def run_experiment_8b(ticks: int = 50000, log_interval: int = 1000):
    """Run both conditions sequentially, then analyze lineage."""

    print()
    print("=" * 70)
    print("EXPERIMENT 8b: STRATEGY ESCAPE ISOLATION")
    print("Seeded Diversity vs Stochastic Emergence")
    print("=" * 70)
    print()
    print("Pre-registered hypothesis:")
    print("  Condition 3 (50/50) will survive past tick 10,039.")
    print("  If survivors trace to seeded NAKED: intentional escape is viable.")
    print("  If survivors trace to late mutations: escape is stochastic/robust.")
    print()
    print("Running Condition 1 (100% DEFENDER) first...")
    print()

    # === CONDITION 1: 100% DEFENDER ===
    r1 = run_condition("cond1_100pct_defender", naked_fraction=0.0,
                       ticks=ticks, log_interval=log_interval)

    print()
    print("Running Condition 3 (50% DEFENDER / 50% NAKED)...")
    print()

    # === CONDITION 3: 50/50 ===
    r3 = run_condition("cond3_50pct_naked", naked_fraction=0.5,
                       ticks=ticks, log_interval=log_interval)

    # === LINEAGE ANALYSIS ===
    print()
    print("=" * 70)
    print("LINEAGE ANALYSIS")
    print("=" * 70)
    la1 = analyze_lineage("cond1_100pct_defender", r1['collapse_tick'])
    la3 = analyze_lineage("cond3_50pct_naked", r3['collapse_tick'])

    # === FINAL COMPARISON ===
    print()
    print("=" * 70)
    print("EXPERIMENT 8b FINAL COMPARISON")
    print("=" * 70)
    print(f"Condition 1 (100% DEFENDER):")
    c1_result = ('COLLAPSED tick ' + str(r1['collapse_tick'])
                 if r1['collapsed'] else 'SURVIVED 50K')
    print(f"  Result:          {c1_result}")
    print(f"  Strategy escape: {r1['strategy_escape_tick'] or 'not detected'}")
    print()
    print(f"Condition 3 (50/50):")
    c3_result = ('COLLAPSED tick ' + str(r3['collapse_tick'])
                 if r3['collapsed'] else 'SURVIVED 50K')
    print(f"  Result:          {c3_result}")
    print(f"  Strategy escape: {r3['strategy_escape_tick'] or 'not detected'}")
    print(f"  Late seeded fraction: {la3.get('late_seeded_pct', 'N/A')}%")
    print(f"  Lineage verdict: {la3.get('verdict', 'N/A')}")
    print()

    print("Pre-registered hypothesis check:")
    c3_survived_past_baseline = (
        not r3['collapsed'] or (r3['collapse_tick'] and r3['collapse_tick'] > 10039)
    )
    print(f"  Cond 3 survived past tick 10039: "
          f"{'CONFIRMED' if c3_survived_past_baseline else 'REJECTED'}")
    verdict = la3.get('verdict', '')
    if 'SEEDED' in verdict:
        print(f"  Lineage: SEEDED_DOMINANT — intentional escape is viable [hypothesis CONFIRMED]")
    elif 'INDEPENDENT' in verdict:
        print(f"  Lineage: INDEPENDENT_MUTATION — escape is stochastic [hypothesis REJECTED, "
              f"but more interesting result]")
    else:
        print(f"  Lineage: MIXED — inconclusive, more runs needed")

    print()
    print(f"Constella implication:")
    print(la3.get('interpretation', 'See lineage analysis above.'))
    print("=" * 70)

    return r1, r3, la1, la3


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="ALIFE Exp 8b: Strategy Escape Isolation")
    parser.add_argument("--ticks", type=int, default=50000)
    parser.add_argument("--log-interval", type=int, default=1000)
    args = parser.parse_args()
    run_experiment_8b(ticks=args.ticks, log_interval=args.log_interval)
