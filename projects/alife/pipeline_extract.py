#!/usr/bin/env python3
"""
Nomenclature extraction — the pipeline stage that turns seeded fossils into a tiered
dataset. Reads exp5 fossils across seeds, and for each phenomenon asks: does it happen
reproducibly (confirmed pattern) or does it vary (stochastic / emergent variation)?
This is confirmability applied to emergence: a phenomenon earns 'confirmed' by recurring.
"""
import json, glob, statistics
from collections import defaultdict

# group fossils by tick count (only same-scale runs are comparable)
groups = defaultdict(list)
for f in glob.glob("fossils/exp5_seed*.json"):
    d = json.load(open(f))
    groups[d.get("ticks")].append((d.get("seed"), d.get("results", {})))

# use the largest comparable group
ticks, runs = max(groups.items(), key=lambda kv: len(kv[1]))
print(f"=== exp5 nomenclature extraction: {len(runs)} seeds @ {ticks} ticks "
      f"(seeds {sorted(s for s,_ in runs)}) ===\n")

# collect every phenomenon across the runs
fields = defaultdict(list)
for _seed, res in runs:
    for k, v in res.items():
        fields[k].append(v)

print(f"{'phenomenon':22} {'tier':11} {'evidence'}")
print("-" * 70)
for k, vals in sorted(fields.items()):
    nums = [v for v in vals if isinstance(v, (int, float))]
    non_null = [v for v in vals if v not in (None, 0, 0.0)]
    present = len(non_null)
    n = len(vals)
    if present == n and present > 0:            # happens every seed
        if nums and len(set(nums)) == 1:
            tier, ev = "CONFIRMED", f"identical every seed: {nums[0]}"
        elif nums:
            cv = (statistics.pstdev(nums) / statistics.mean(nums)) if statistics.mean(nums) else 0
            tier = "CONFIRMED" if cv < 0.5 else "CONFIRMED*"
            ev = f"always occurs; value varies {min(nums)}–{max(nums)} (mean {statistics.mean(nums):.0f}, CV {cv:.2f})"
        else:
            tier, ev = "CONFIRMED", "present every seed"
    elif present == 0:
        tier, ev = "ABSENT", f"never occurred in {n} seeds (at this scale)"
    else:
        tier, ev = "SPECULATIVE", f"occurred in {present}/{n} seeds only — stochastic"
    print(f"{k:22} {tier:11} {ev}")

print("\nReading: CONFIRMED = a reproducible emergent fact (earns a name in the vocabulary).")
print("CONFIRMED* = reliably happens but magnitude is stochastic (that's the *emergent")
print("variation* — the interesting part). ABSENT/SPECULATIVE = not established at this scale.")
