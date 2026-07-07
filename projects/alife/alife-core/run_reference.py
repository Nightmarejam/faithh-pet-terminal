#!/usr/bin/env python3
import sys
sys.path.insert(0, '..')
from simulation import Simulation
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 1
sim = Simulation(experiment=0, seed=seed)
sim.initialize_population()
for _ in range(ticks): sim.tick()

def feed(v, h):
    for b in v.to_bytes(4, 'little', signed=True):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h
h = 0xcbf29ce484222325
for a in sim.world.agents.values():
    h = feed(a.x, h); h = feed(a.y, h)
    for g in a.genome: h = feed(g, h)
    h = feed(a.energy, h); h = feed(a.generation, h); h = feed(a.age, h)
for row in sim.world.grid:
    for c in row: h = feed(c.energy, h)
print(f"seed {seed} after {ticks} ticks: pop={len(sim.world.agents)} births={sim.total_reproductions} deaths={sim.total_deaths}")
print(f"state_hash: {h:016x}")
