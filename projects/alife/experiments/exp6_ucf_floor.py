"""
ALIFE Experiment 6: The UCF Floor
Track B — Constella Constitutional Stress Test

Scientific Question:
Does a minimum energy floor (Universal Civic Floor analog) prevent the
population collapse observed in Experiment 5 (drain=1.5)?

Constella Principle Tested:
  Universal Civic Floor (UCF) — baseline resource allocation guaranteed
  to all members regardless of contribution history. Ensures minimum
  viable participation is always possible.

Rational Baseline (from Exp 5 drain=1.5):
  Without UCF: COLLAPSE at tick 10039.
  Parasites emerged tick 57. Toxin tick 1840.
  Neither counter-strategy reached critical mass.
  Full predator adaptation (shields 0%) by tick 8000.

Hypothesis:
  A UCF floor at MIN_ENERGY_FLOOR energy units prevents collapse by
  ensuring agents never drop below viable participation threshold,
  buying time for counter-strategies (toxin, parasitic response) to scale.

Null Hypothesis (what failure looks like):
  UCF floor merely delays collapse by a few thousand ticks, does not
  prevent it. Or worse: floor enables free-riding — agents stop contributing
  and coast on the floor indefinitely, causing a different kind of collapse
  (population bloat, no evolution pressure).

Design Decision This Experiment Determines:
  IF hypothesis confirmed (UCF prevents collapse):
    → UCF is load-bearing in Constella, not aspirational.
    → Floor level becomes a critical calibration parameter.
    → The commons pool funding mechanism must be robust.
  IF null hypothesis confirmed (UCF only delays):
    → UCF needs a contribution requirement to prevent free-riding.
    → Floor alone is insufficient — Astris decay must also be reduced,
      OR the predator pressure analog (governance complexity) must be capped.
  IF free-riding failure mode observed:
    → UCF requires minimum participation threshold to receive floor support.
    → This directly maps to "minimum engagement to receive civic floor benefits."

UCF Mechanic:
  When an agent's energy drops below UCF_FLOOR_THRESHOLD, inject
  UCF_INJECTION_AMOUNT energy from a shared commons pool each tick.
  Commons pool regenerates at UCF_COMMONS_REGEN_RATE per tick.
  If commons pool is depleted, UCF floor fails (tests commons funding).

Free-Riding Detection:
  An agent is a "floor rider" if energy == UCF_FLOOR_THRESHOLD for >
  UCF_FLOOR_RIDER_TICKS consecutive ticks without contributing (reproducing).
  Track floor rider count over time.

Penumbra Connection:
  Agents in the floor-supported state are in the "penumbra zone" —
  not fully excluded (energy > 0), not fully participating (energy < threshold).
  The Penumbra Accord in Constella is the governance analog of this state:
  structured support + path back to full participation, not exclusion.
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

# Reuse Exp 5 op codes and mechanics
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
ACT_SIGNAL = 0x05
ACT_TOXIN = 0x06
ACT_FLEE = 0x07
REG_NONE = 0x00

# Exp 5 parameters (unchanged — same pressure environment)
PARASITE_DRAIN_RATE = 1.5
PARASITE_REDIRECT_FRACTION = 0.3
PARASITE_REDIRECT_TICK = 5000
TOXIN_UNLOCK_TICK = 15000

# === UCF Floor Parameters (the new mechanic) ===
UCF_FLOOR_THRESHOLD = 40       # Energy below which UCF support activates
UCF_INJECTION_AMOUNT = 5       # Energy injected per tick when below floor
UCF_COMMONS_INITIAL = 500000   # Starting commons pool (sized for 50K tick run)
UCF_COMMONS_REGEN_RATE = 150   # Regen ~150/tick = sustainable for ~30 agents on floor
UCF_FLOOR_RIDER_TICKS = 500    # Ticks at floor without reproducing = floor rider

# Seeded genome — same as Exp 5 (Defender)
DEFENDER_GENOME = bytes([
    SENSE_LIGHT, SENSE_THREAT, PROC_THRESHOLD, PROC_PREDICT,
    MEM_PATTERN, ACT_REPRODUCE, ACT_SHIELD, REG_NONE
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


def apply_ucf_floor(world, commons_pool: float) -> tuple:
    """
    Apply UCF floor injection to agents below threshold.
    Draws from commons pool. Returns (new_commons_pool, floor_supported_count).
    """
    floor_supported = 0
    for agent in world.agents.values():
        if not agent.alive:
            continue
        if agent.energy < UCF_FLOOR_THRESHOLD and commons_pool > 0:
            inject = min(UCF_INJECTION_AMOUNT, commons_pool,
                         UCF_FLOOR_THRESHOLD - agent.energy)
            agent.energy += inject
            commons_pool -= inject
            floor_supported += 1
            # Track floor riding
            if not hasattr(agent, '_floor_ticks'):
                agent._floor_ticks = 0
            agent._floor_ticks += 1
        else:
            if hasattr(agent, '_floor_ticks'):
                agent._floor_ticks = 0
    return commons_pool, floor_supported


def apply_parasitic_drain(world):
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
                continue
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
    contacts = []
    toxin_contacts = 0
    redirect_events = 0
    front = wave.front_position(current_tick)
    for agent_id, agent in list(world.agents.items()):
        if not agent.alive:
            continue
        if abs(agent.x - front) < 1.0:
            MIN_ARRIVAL_GAP = 50
            if not agent.wave_arrival_times or (current_tick - agent.wave_arrival_times[-1]) > MIN_ARRIVAL_GAP:
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
                redirect_damage = PREDATOR_DAMAGE * PARASITE_REDIRECT_FRACTION
                agent.energy -= own_damage
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
                    agent.energy -= redirect_damage
                outcome = 'parasite_redirect'
            else:
                agent.energy -= PREDATOR_DAMAGE
                outcome = 'unshielded'
            if agent.energy <= 0:
                agent.energy = 0
                agent.alive = False
            contacts.append((agent_id, outcome))
    return contacts, toxin_contacts, redirect_events


def run_experiment_6(ticks: int = 50000, log_interval: int = 1000):
    """Run Experiment 6: UCF Floor — Constitutional Stress Test."""
    import config
    config.SIGNAL_ACTIVE = True
    config.TOXIN_ACTIVE = False

    sim = Simulation(experiment=6)
    sim.world.initialize_light_gradient()
    sim.world.current_wave = None

    sim.initialize_population(200)
    for agent in sim.world.agents.values():
        agent.genome = bytearray(DEFENDER_GENOME)

    print(f"Seeded {sim.world.get_population()} agents with DEFENDER genome")

    observer = None
    try:
        from faithh_observer import PulseWatcher
        observer = PulseWatcher()
    except Exception as e:
        print(f"[PULSE] Observer init failed (non-fatal): {e}")

    shield_adaptation = 0.0
    commons_pool = float(UCF_COMMONS_INITIAL)
    redirect_active = False

    results = {
        'wave_count': 0, 'predator_kills': 0, 'thermal_deaths': 0,
        'parasitic_kills': 0, 'redirect_events': 0,
        'first_parasite_tick': None, 'first_toxin_tick': None,
        'ucf_interventions': 0, 'floor_rider_peak': 0,
        'commons_depleted_tick': None,
        'collapsed': False, 'collapse_tick': None,
    }

    first_parasite = None
    first_toxin = None

    print()
    print("=" * 75)
    print("EXPERIMENT 6: THE UCF FLOOR (Track B — Constella Stress Test)")
    print("=" * 75)
    print(f"Identical to Exp 5 drain=1.5 EXCEPT: UCF floor active")
    print(f"UCF floor threshold:  {UCF_FLOOR_THRESHOLD} energy")
    print(f"UCF injection/tick:   {UCF_INJECTION_AMOUNT} energy when below floor")
    print(f"Commons pool:         {UCF_COMMONS_INITIAL:,} (regen {UCF_COMMONS_REGEN_RATE}/tick)")
    print(f"Parasitic drain:      {PARASITE_DRAIN_RATE} energy/tick (same as Exp 5)")
    print(f"Exp 5 collapsed at:   tick 10039 (baseline)")
    print(f"Hypothesis:           UCF prevents or significantly delays collapse")
    print(f"Null hypothesis:      UCF merely delays or causes free-riding collapse")
    print("=" * 75)
    print()

    for t in range(ticks):
        # Phase unlocks (same as Exp 5)
        if t == PARASITE_REDIRECT_TICK and not redirect_active:
            redirect_active = True
            print(f"\n*** PHASE B: Threat redirection active at tick {t} ***\n")
        if t == TOXIN_UNLOCK_TICK and not config.TOXIN_ACTIVE:
            config.TOXIN_ACTIVE = True
            print(f"\n*** PHASE C: ACT_TOXIN available at tick {t} ***\n")

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
            sim.check_wave_detection(wave, t, observer)
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

        # Parasitic drain
        apply_parasitic_drain(sim.world)
        for agent in list(sim.world.agents.values()):
            if not agent.alive:
                results['parasitic_kills'] += 1
                sim.world.remove_agent(agent)
                sim.total_deaths += 1

        # === UCF FLOOR — the new mechanic ===
        if commons_pool > 0:
            commons_pool += UCF_COMMONS_REGEN_RATE
            commons_pool, floor_supported = apply_ucf_floor(sim.world, commons_pool)
            results['ucf_interventions'] += floor_supported
            if floor_supported > results['floor_rider_peak']:
                results['floor_rider_peak'] = floor_supported
        elif results['commons_depleted_tick'] is None:
            results['commons_depleted_tick'] = t
            print(f"\n*** COMMONS POOL DEPLETED at tick {t} — UCF floor offline ***\n")

        # Adaptive predator
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
            if has_signal(agent) and agent.generation > 1 and not hasattr(agent, '_parasite_logged'):
                agent._parasite_logged = True
                if first_parasite is None:
                    first_parasite = (t, agent.id, agent.generation)
                    results['first_parasite_tick'] = t
                    print(f"\n*** FIRST PARASITE LINEAGE: {agent.id} tick {t} gen={agent.generation:.0f} ***\n")
            if has_toxin(agent) and agent.generation > 1 and not hasattr(agent, '_toxin_logged'):
                agent._toxin_logged = True
                if first_toxin is None:
                    first_toxin = (t, agent.id, agent.generation)
                    results['first_toxin_tick'] = t
                    print(f"\n*** FIRST TOXIN LINEAGE: {agent.id} tick {t} gen={agent.generation:.0f} ***\n")

        sim.tick()

        if sim.world.get_population() == 0:
            results['collapsed'] = True
            results['collapse_tick'] = t
            print(f"\n*** POPULATION COLLAPSED at tick {t} ***\n")
            break

        # Logging
        if t % log_interval == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total == 0:
                continue
            defenders = sum(1 for a in pop if get_strategy(a) == "DEFENDER")
            parasites = sum(1 for a in pop if "PARASITE" in get_strategy(a))
            toxins = sum(1 for a in pop if "TOXIN" in get_strategy(a) or get_strategy(a) == "APEX")
            floor_now = sum(1 for a in pop if a.energy <= UCF_FLOOR_THRESHOLD)
            avg_energy = sum(a.energy for a in pop) / total
            shield_eff = max(0, (1.0 - shield_adaptation) * 100)
            phase = "C" if t >= TOXIN_UNLOCK_TICK else "B" if t >= PARASITE_REDIRECT_TICK else "A"
            commons_pct = commons_pool / UCF_COMMONS_INITIAL * 100

            print(f"Tick {t:6d} [{phase}]: pop={total:4d} | def={defenders:3d} "
                  f"para={parasites:3d} tox={toxins:3d} | "
                  f"adapt={shield_adaptation:.2f} shld={shield_eff:3.0f}% | "
                  f"E={avg_energy:.0f} floor={floor_now:3d} commons={commons_pct:.0f}%")

    # Final results
    pop = list(sim.world.agents.values())
    total = len(pop)

    print()
    print("=" * 75)
    print("EXPERIMENT 6 RESULTS: THE UCF FLOOR")
    print("=" * 75)
    print(f"Final population:       {total}")
    print(f"Collapsed:              {'YES at tick ' + str(results['collapse_tick']) if results['collapsed'] else 'NO — survived full run'}")
    print(f"Exp 5 collapsed at:     tick 10039 (baseline without UCF)")
    print()
    print(f"Wave count:             {results['wave_count']}")
    print(f"Predator kills:         {results['predator_kills']}")
    print(f"Parasitic kills:        {results['parasitic_kills']}")
    print(f"Thermal deaths:         {results['thermal_deaths']}")
    print(f"Total reproductions:    {sim.total_reproductions}")
    print()
    print(f"UCF interventions:      {results['ucf_interventions']:,} (total floor injections)")
    print(f"Floor rider peak:       {results['floor_rider_peak']} agents simultaneously on floor")
    print(f"Commons depleted tick:  {results['commons_depleted_tick'] or 'Never'}")
    print(f"Final commons pool:     {commons_pool:.0f} / {UCF_COMMONS_INITIAL:,}")
    print()
    para_tick = results['first_parasite_tick']
    toxin_tick = results['first_toxin_tick']
    print(f"First parasite:         {'tick ' + str(para_tick) if para_tick else 'NONE'}")
    print(f"First toxin:            {'tick ' + str(toxin_tick) if toxin_tick else 'NONE'}")

    if total > 0:
        print()
        for strat in ["DEFENDER", "PARASITE", "PARASITE+", "TOXIN", "APEX", "NAKED"]:
            count = sum(1 for a in pop if get_strategy(a) == strat)
            if count > 0:
                print(f"  {strat:12s}: {count:4d} ({count/total*100:.1f}%)")

    # Determine outcome and Constella design decision
    print()
    if not results['collapsed']:
        if results['floor_rider_peak'] > total * 0.3:
            outcome = "UCF_PREVENTS_COLLAPSE_BUT_FREE_RIDING"
            decision = "UCF needs minimum participation requirement to receive floor support"
        else:
            outcome = "UCF_PREVENTS_COLLAPSE"
            decision = "UCF is load-bearing. Floor level and commons regen rate are critical parameters."
    elif results['collapse_tick'] > 10039:
        delay = results['collapse_tick'] - 10039
        outcome = f"UCF_DELAYS_COLLAPSE_BY_{delay}_TICKS"
        decision = "UCF alone insufficient. Must reduce Astris decay rate OR cap governance pressure."
    else:
        outcome = "UCF_NO_EFFECT"
        decision = "Floor threshold or injection rate too low. Recalibrate UCF parameters."

    print(f"Outcome:                {outcome}")
    print(f"Constella decision:     {decision}")
    print("=" * 75)

    if observer:
        observer.close()

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ALIFE Experiment 6: UCF Floor")
    parser.add_argument("--ticks", type=int, default=50000)
    parser.add_argument("--log-interval", type=int, default=1000)
    args = parser.parse_args()
    run_experiment_6(ticks=args.ticks, log_interval=args.log_interval)
