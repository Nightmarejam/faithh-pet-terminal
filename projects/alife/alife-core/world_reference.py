#!/usr/bin/env python3
"""Python reference: build the World and compute the SAME FNV-1a hash as world.rs."""
import sys, random
sys.path.insert(0, '..')
random.seed(42)
from world import World
w = World()

def feed(v, h):
    for b in v.to_bytes(4, 'little', signed=True):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h

h = 0xcbf29ce484222325
for row in w.grid:
    for c in row:
        h = feed(c.energy, h); h = feed(c.light, h)
for (sx, sy) in w.energy_sources:
    h = feed(sx, h); h = feed(sy, h)

print(f"seed 42 World: {w.width}x{w.height}, {len(w.energy_sources)} sources")
print(f"first sources: {w.energy_sources[:3]}")
print(f"state_hash: {h:016x}")
