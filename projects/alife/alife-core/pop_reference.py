#!/usr/bin/env python3
"""Python reference for population init — same FNV-1a as agent.rs."""
import sys
sys.path.insert(0, '..')
from simulation import Simulation
sim = Simulation(experiment=0, seed=42)   # seeds 42, builds World
sim.initialize_population()                # spawns 50 agents

def feed(v, h):
    for b in v.to_bytes(4, 'little', signed=True):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h

h = 0xcbf29ce484222325
agents = list(sim.world.agents.values())
for a in agents:
    h = feed(a.x, h); h = feed(a.y, h)
    for g in a.genome: h = feed(g, h)
    h = feed(a.energy, h); h = feed(a.generation, h)

a0 = agents[0]
print(f"seed 42 population: {len(agents)} agents")
print(f"agent0: pos=({a0.x},{a0.y}) genome={list(a0.genome)} energy={a0.energy}")
print(f"population_hash: {h:016x}")
