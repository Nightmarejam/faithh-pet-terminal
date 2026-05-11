"""
ALIFE Experiment 7: UCF Gated Floor — Participation Gate + Penumbra Zone
Track B — Constella Constitutional Stress Test

Pre-registered hypothesis (written before running):
  Gate window of 500 ticks is aggressive enough to exclude most passive floor
  riders, but reproduction under high drain pressure is hard enough that we'll
  see a genuine Penumbra population — agents caught between participation and
  exclusion. Prediction: 10-25% of population in Penumbra state at peak stress.
  Collapse delayed vs Exp 6 (>7,410 ticks). Whether it beats Exp 5 baseline
  (10,039) is the real question.
  
  Gaming behavior (reproduce-at-minimum-frequency) may emerge as a distinct
  Penumbra-adjacent strategy: agents reproduce just often enough to qualify,
  never often enough to contribute meaningfully to population health.

Baseline comparisons:
  Exp 5 (no floor, drain=1.5):         collapsed tick 10,039
  Exp 6 (unconditional floor, drain=1.5): collapsed tick 7,410 (WORSE)

Parameters changed from Exp 6:
  UCF_GATE_WINDOW = 500       # Must have reproduced within last 500 ticks to qualify
  UCF_GRACE_PERIOD = 300      # After gate expires: 300 ticks of 50% support (Penumbra)
  UCF_GRACE_INJECTION = 2     # Half of full injection during grace period

Agent states tracked this experiment:
  ACTIVE    — reproduced within UCF_GATE_WINDOW ticks, full floor support if needed
  PENUMBRA  — gate expired, within grace period, 50% floor support
  EXCLUDED  — grace period expired, no floor support
  (plus existing: DEFENDER, PARASITE, TOXIN, APEX, NAKED by genome strategy)

Gaming behavior detection:
  An agent is flagged as a GAMER if:
    - It is consistently in ACTIVE state (reproduced recently)
    - BUT its reproduction intervals cluster tightly around UCF_GATE_WINDOW
    - Meaning it reproduces exactly often enough to stay qualified, no more
  This requires tracking reproduction interval variance per agent lineage.
"""

import sys
import os
import argparse
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

# Op codes (same as Exp 5/6)
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

# Exp 5/6 stressor parameters (unchanged)
PARASITE_DRAIN_RATE = 1.5
PARASITE_REDIRECT_FRACTION = 0.3
PARASITE_REDIRECT_TICK = 5000
TOXIN_UNLOCK_TICK = 15000

# === UCF Gated Floor Parameters ===
UCF_FLOOR_THRESHOLD = 40        # Energy below which floor support activates
UCF_INJECTION_AMOUNT = 5        # Full injection per tick (ACTIVE agents)
UCF_GATE_WINDOW = 500           # Must have reproduced within this many ticks to be ACTIVE
UCF_GRACE_PERIOD = 300          # Ticks of partial support after gate expires (PENUMBRA)
UCF_GRACE_INJECTION = 2         # Partial injection during PENUMBRA state
UCF_COMMONS_INITIAL = 500000    # Starting commons pool
UCF_COMMONS_REGEN_RATE = 150    # Commons regen per tick

# Gaming detection: if agent's last 5 reproduction intervals all within this
# range of UCF_GATE_WINDOW, flag as potential gamer
GAMING_INTERVAL_TOLERANCE = 100   # intervals within [GATE_WINDOW ± TOLERANCE]
GAMING_MIN_SAMPLES = 5            # Need at least 5 intervals to flag

# Seeded genome — same as Exp 5/6
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


def get_ucf_state(agent, current_tick: int) -> str:
    """Return UCF participation state for this agent."""
    last_repro = getattr(agent, '_last_reproduction_tick', None)
    if last_repro is None:
        # Never reproduced — starts in PENUMBRA from birth
        birth_tick = getattr(agent, '_birth_tick', 0)
        ticks_since_birth = current_tick - birth_tick
        if ticks_since_birth <= UCF_GRACE_PERIOD:
            return "PENUMBRA"
        return "EXCLUDED"
    ticks_since_repro = current_tick - last_repro
    if ticks_since_repro <= UCF_GATE_WINDOW:
        return "ACTIVE"
    elif ticks_since_repro <= UCF_GATE_WINDOW + UCF_GRACE_PERIOD:
        return "PENUMBRA"
    else:
        return "EXCLUDED"


def is_gaming(agent) -> bool:
    """Detect minimum-compliance gaming: reproducing just enough to stay ACTIVE."""
    intervals = getattr(agent, '_repro_intervals', [])
    if len(intervals) < GAMING_MIN_SAMPLES:
        return False
    recent = intervals[-GAMING_MIN_SAMPLES:]
    lo = UCF_GATE_WINDOW - GAMING_INTERVAL_TOLERANCE
    hi = UCF_GATE_WINDOW + GAMING_INTERVAL_TOLERANCE
    # All recent intervals cluster around gate window
    return all(lo <= iv <= hi for iv in recent)


def apply_gated_ucf(world, commons_pool: float, current_tick: int) -> tuple:
    """
    Apply gated UCF floor.
    ACTIVE agents below threshold: full injection
    PENUMBRA agents below threshold: partial injection
    EXCLUDED agents: no support
    Returns (new_commons_pool, active_supported, penumbra_supported, excluded_count)
    """
    active_supported = 0
    penumbra_supported = 0
    excluded_count = 0

    for agent in world.agents.values():
        if not agent.alive:
            continue
        if agent.energy >= UCF_FLOOR_THRESHOLD:
            continue

        state = get_ucf_state(agent, current_tick)

        if state == "ACTIVE" and commons_pool > 0:
            inject = min(UCF_INJECTION_AMOUNT, commons_pool,
                         UCF_FLOOR_THRESHOLD - agent.energy)
            agent.energy += inject
            commons_pool -= inject
            active_supported += 1

        elif state == "PENUMBRA" and commons_pool > 0:
            inject = min(UCF_GRACE_INJECTION, commons_pool,
                         UCF_FLOOR_THRESHOLD - agent.energy)
            agent.energy += inject
            commons_pool -= inject
            penumbra_supported += 1

        else:
            excluded_count += 1

    return commons_pool, active_supported, penumbra_supported, excluded_count


def track_reproduction(agent, current_tick: int):
    """Record reproduction event for gaming detection."""
    if not hasattr(agent, '_last_reproduction_tick'):
        agent._last_reproduction_tick = current_tick
        agent._repro_intervals = []
        return
    interval = current_tick - agent._last_reproduction_tick
    if not hasattr(agent, '_repro_intervals'):
        agent._repro_intervals = []
    agent._repro_intervals.append(interval)
    agent._repro_intervals = agent._repro_intervals[-20:]  # Keep last 20
    agent._last_reproduction_tick = current_tick


def apply_parasitic_drain(world):
    total_drained = 0
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
                total_drained += drain
                if victim.energy <= 0:
                    victim.energy = 0
                    victim.alive = False
    return total_drained


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


def run_experiment_7(ticks: int = 50000, log_interval: int = 1000):
    """Run Experiment 7: Gated UCF Floor with Penumbra Zone."""
    import config
    config.SIGNAL_ACTIVE = True
    config.TOXIN_ACTIVE = False

    sim = Simulation(experiment=7)
    sim.world.initialize_light_gradient()
    sim.world.current_wave = None

    sim.initialize_population(200)
    for agent in sim.world.agents.values():
        agent.genome = bytearray(DEFENDER_GENOME)
        agent._birth_tick = 0
        agent._last_reproduction_tick = None
        agent._repro_intervals = []

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
        'first_gamer_tick': None, 'gamer_peak': 0,
        'penumbra_peak': 0, 'excluded_peak': 0,
        'active_supported_total': 0, 'penumbra_supported_total': 0,
        'commons_depleted_tick': None,
        'collapsed': False, 'collapse_tick': None,
    }

    # Gaming lineage tracker: agent_id -> first tick flagged
    confirmed_gamers = {}

    print()
    print("=" * 75)
    print("EXPERIMENT 7: UCF GATED FLOOR + PENUMBRA ZONE (Track B)")
    print("=" * 75)
    print(f"Gate window:          {UCF_GATE_WINDOW} ticks (must reproduce to stay ACTIVE)")
    print(f"Grace period:         {UCF_GRACE_PERIOD} ticks at {UCF_GRACE_INJECTION} energy/tick (PENUMBRA)")
    print(f"Full injection:       {UCF_INJECTION_AMOUNT} energy/tick (ACTIVE agents only)")
    print(f"Commons pool:         {UCF_COMMONS_INITIAL:,} (regen {UCF_COMMONS_REGEN_RATE}/tick)")
    print(f"Parasitic drain:      {PARASITE_DRAIN_RATE} (same as Exp 5/6)")
    print()
    print(f"Pre-registered hypothesis:")
    print(f"  10-25% population in PENUMBRA at peak stress")
    print(f"  Collapse delayed past Exp 6 (>7,410 ticks)")
    print(f"  Gaming behavior (min-compliance reproduction) may emerge")
    print()
    print(f"Baselines:")
    print(f"  Exp 5 (no floor):          collapsed tick 10,039")
    print(f"  Exp 6 (unconditional):     collapsed tick  7,410")
    print("=" * 75)
    print()

    for t in range(ticks):
        # Phase unlocks
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
                results['parasitic_kills'] += 1
                sim.world.remove_agent(agent)
                sim.total_deaths += 1

        # === GATED UCF FLOOR ===
        if commons_pool > 0:
            commons_pool += UCF_COMMONS_REGEN_RATE
            commons_pool, act_sup, pen_sup, excl = apply_gated_ucf(
                sim.world, commons_pool, t
            )
            results['active_supported_total'] += act_sup
            results['penumbra_supported_total'] += pen_sup
        elif results['commons_depleted_tick'] is None:
            results['commons_depleted_tick'] = t
            print(f"\n*** COMMONS POOL DEPLETED at tick {t} — UCF floor offline ***\n")

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

        # === EMERGENCE + GAMING DETECTION ===
        for agent in sim.world.agents.values():
            if not agent.alive:
                continue

            # Hook into reproduction events via energy spike detection
            # (actual reproduction tracking is done when energy increases
            # significantly in a single tick — proxy for a child being born)
            # Better: check if agent just reproduced via generation counter
            if hasattr(agent, '_last_gen') and agent.generation > agent._last_gen:
                track_reproduction(agent, t)
            if not hasattr(agent, '_last_gen'):
                agent._last_gen = agent.generation
            agent._last_gen = agent.generation

            # Parasite emergence
            if (has_signal(agent) and agent.generation > 1
                    and not hasattr(agent, '_parasite_logged')):
                agent._parasite_logged = True
                if results['first_parasite_tick'] is None:
                    results['first_parasite_tick'] = t
                    print(f"\n*** FIRST PARASITE: {agent.id} tick {t} "
                          f"gen={agent.generation:.0f} ***\n")

            # Toxin emergence
            if (has_toxin(agent) and agent.generation > 1
                    and not hasattr(agent, '_toxin_logged')):
                agent._toxin_logged = True
                if results['first_toxin_tick'] is None:
                    results['first_toxin_tick'] = t
                    print(f"\n*** FIRST TOXIN: {agent.id} tick {t} "
                          f"gen={agent.generation:.0f} ***\n")

            # Gaming detection
            if agent.id not in confirmed_gamers and is_gaming(agent):
                confirmed_gamers[agent.id] = t
                if results['first_gamer_tick'] is None:
                    results['first_gamer_tick'] = t
                    intervals = agent._repro_intervals[-GAMING_MIN_SAMPLES:]
                    print(f"\n*** GAMING BEHAVIOR DETECTED: {agent.id} tick {t} "
                          f"gen={agent.generation:.0f} ***")
                    print(f"    Reproduction intervals: {intervals}")
                    print(f"    Gate window: {UCF_GATE_WINDOW} — "
                          f"agent reproducing at minimum compliance frequency\n")

        sim.tick()

        if sim.world.get_population() == 0:
            results['collapsed'] = True
            results['collapse_tick'] = t
            print(f"\n*** POPULATION COLLAPSED at tick {t} ***\n")
            break

        # === LOGGING ===
        if t % log_interval == 0:
            pop = list(sim.world.agents.values())
            total = len(pop)
            if total == 0:
                continue

            # UCF state counts
            states = defaultdict(int)
            for a in pop:
                states[get_ucf_state(a, t)] += 1
            active_ct = states['ACTIVE']
            penumbra_ct = states['PENUMBRA']
            excluded_ct = states['EXCLUDED']

            # Update peaks
            if penumbra_ct > results['penumbra_peak']:
                results['penumbra_peak'] = penumbra_ct
            if excluded_ct > results['excluded_peak']:
                results['excluded_peak'] = excluded_ct

            # Strategy counts
            defenders = sum(1 for a in pop if get_strategy(a) == 'DEFENDER')
            parasites = sum(1 for a in pop if 'PARASITE' in get_strategy(a))
            toxins = sum(1 for a in pop
                         if 'TOXIN' in get_strategy(a) or get_strategy(a) == 'APEX')
            gamers_now = sum(1 for a in pop if is_gaming(a))
            if gamers_now > results['gamer_peak']:
                results['gamer_peak'] = gamers_now

            avg_energy = sum(a.energy for a in pop) / total
            shield_eff = max(0, (1.0 - shield_adaptation) * 100)
            phase = ("C" if t >= TOXIN_UNLOCK_TICK
                     else "B" if t >= PARASITE_REDIRECT_TICK else "A")
            commons_pct = commons_pool / UCF_COMMONS_INITIAL * 100

            print(f"Tick {t:6d} [{phase}]: pop={total:4d} | "
                  f"def={defenders:3d} par={parasites:2d} tox={toxins:2d} | "
                  f"ACT={active_ct:3d} PEN={penumbra_ct:3d} EXC={excluded_ct:3d} "
                  f"GAM={gamers_now:3d} | "
                  f"adapt={shield_adaptation:.2f} shld={shield_eff:3.0f}% | "
                  f"E={avg_energy:.0f} cmns={commons_pct:.0f}%")

    # === FINAL RESULTS ===
    pop = list(sim.world.agents.values())
    total = len(pop)

    print()
    print("=" * 75)
    print("EXPERIMENT 7 RESULTS: UCF GATED FLOOR + PENUMBRA")
    print("=" * 75)
    print(f"Final population:         {total}")
    if results['collapsed']:
        print(f"Collapsed:                YES at tick {results['collapse_tick']}")
    else:
        print(f"Collapsed:                NO — survived full {ticks} tick run")
    print()
    print(f"Baselines:")
    print(f"  Exp 5 (no floor):         tick 10,039")
    print(f"  Exp 6 (unconditional):    tick  7,410")
    if results['collapsed']:
        delta5 = results['collapse_tick'] - 10039
        delta6 = results['collapse_tick'] - 7410
        print(f"  Exp 7 (gated):            tick {results['collapse_tick']:,} "
              f"({'+'if delta5>=0 else ''}{delta5} vs Exp5, "
              f"{'+'if delta6>=0 else ''}{delta6} vs Exp6)")
    print()
    print(f"UCF State Peaks:")
    print(f"  PENUMBRA peak:            {results['penumbra_peak']} agents")
    print(f"  EXCLUDED peak:            {results['excluded_peak']} agents")
    print(f"  Active supported total:   {results['active_supported_total']:,}")
    print(f"  Penumbra supported total: {results['penumbra_supported_total']:,}")
    print(f"  Commons depleted:         {results['commons_depleted_tick'] or 'Never'}")
    print(f"  Final commons pool:       {commons_pool:.0f} / {UCF_COMMONS_INITIAL:,}")
    print()
    print(f"Emergence:")
    para_tick = results['first_parasite_tick']
    toxin_tick = results['first_toxin_tick']
    gamer_tick = results['first_gamer_tick']
    print(f"  First parasite:           {'tick ' + str(para_tick) if para_tick else 'NONE'}")
    print(f"  First toxin:              {'tick ' + str(toxin_tick) if toxin_tick else 'NONE'}")
    print(f"  First gamer detected:     {'tick ' + str(gamer_tick) if gamer_tick else 'NONE'}")
    print(f"  Gamer peak count:         {results['gamer_peak']}")
    print(f"  Total confirmed gamers:   {len(confirmed_gamers)}")
    print()
    print(f"Other:")
    print(f"  Wave count:               {results['wave_count']}")
    print(f"  Predator kills:           {results['predator_kills']}")
    print(f"  Total reproductions:      {sim.total_reproductions}")

    if total > 0:
        print()
        for strat in ["DEFENDER", "PARASITE", "PARASITE+", "TOXIN", "APEX", "NAKED"]:
            count = sum(1 for a in pop if get_strategy(a) == strat)
            if count > 0:
                print(f"  {strat:12s}: {count:4d} ({count/total*100:.1f}%)")

    # === OUTCOME ASSESSMENT ===
    print()
    if not results['collapsed']:
        if results['gamer_peak'] > 0:
            outcome = "UCF_GATED_SURVIVED_WITH_GAMING"
            decision = ("Gate prevents overshoot. Gaming emerged — gate interval needs "
                        "a secondary metric beyond reproduction frequency.")
        else:
            outcome = "UCF_GATED_SURVIVED_CLEAN"
            decision = "Gated UCF with Penumbra zone is a viable design. Gate=500 confirmed."
    else:
        ct = results['collapse_tick']
        if ct > 10039:
            outcome = "UCF_GATED_IMPROVED_BEYOND_BASELINE"
            decision = ("Gated UCF outperforms both no-floor and unconditional floor. "
                        "Gate design is directionally correct. Tune gate window.")
        elif ct > 7410:
            outcome = "UCF_GATED_BETTER_THAN_UNCONDITIONAL"
            decision = ("Gated UCF beats unconditional but not no-floor baseline. "
                        "Gate reduces overshoot but insufficient alone.")
        else:
            outcome = "UCF_GATED_NO_IMPROVEMENT"
            decision = "Gate=500 too tight — excludes agents before they can stabilize."

    print(f"Outcome:                  {outcome}")
    print(f"Constella decision:       {decision}")
    print()
    print(f"Pre-registered hypothesis check:")
    if results['penumbra_peak'] > 0:
        total_at_peak = results['penumbra_peak']
        print(f"  Penumbra 10-25% of pop:  "
              f"{'CONFIRMED' if 0.10 <= results['penumbra_peak']/340 <= 0.25 else 'PARTIAL — check raw numbers'} "
              f"(peak={results['penumbra_peak']})")
    print(f"  Collapse > Exp6 (7410):  "
          f"{'CONFIRMED' if not results['collapsed'] or results['collapse_tick'] > 7410 else 'REJECTED'}")
    print(f"  Gaming detected:         "
          f"{'CONFIRMED' if results['first_gamer_tick'] else 'NOT OBSERVED'}")
    print("=" * 75)

    if observer:
        observer.close()

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ALIFE Experiment 7: UCF Gated Floor + Penumbra Zone")
    parser.add_argument("--ticks", type=int, default=50000)
    parser.add_argument("--log-interval", type=int, default=1000)
    args = parser.parse_args()
    run_experiment_7(ticks=args.ticks, log_interval=args.log_interval)
