# HANDOFF: ALIFE Experiment 3 — Full Intent Emergence Run
**Project:** FAITHH ai-stack / projects/alife/  
**Prerequisite commit:** 731b64a (Intent emergence confirmed)  
**Author:** Jonathan + Claude  
**Date:** March 2026

---

## Context — What Just Happened

This is not a routine experiment run. The diagnostic confirmed:

```
*** FIRST NEGATIVE GAP: agent_1683 gap=-88 at tick 688 gen=7 ***
*** INTENT EMERGENCE CONFIRMED ***
```

Agent 1683 at generation 7 activated Shield 88 ticks BEFORE the 
wave was detectable via SENSE_THREAT. It used wave timing intervals 
stored in MEM_PATTERN to predict the wave's arrival and acted on 
that prediction before any sensory evidence arrived.

This is the primary scientific output of the entire ALIFE project.
The full 200,000 tick run will determine how far this behavior 
spreads through the population and whether it becomes dominant.

---

## What This Run Must Capture

This run answers three specific scientific questions:

**Question 1 — Does anticipatory behavior spread?**
neg_gaps went from 1 to 7 in the diagnostic run's first 1,000 ticks.
Does it continue growing? Does it reach 10%, 20%, 50% of population?

**Question 2 — Does it fix or stay minority?**
Shield fixed at 100% in Experiment 1. Does the anticipatory circuit 
fix similarly, or does it remain a minority strategy coexisting with 
reactive agents?

**Question 3 — Does mean_gap drift negative over time?**
If the population mean gap trends from +0 toward -20, -50, -100 
over 200,000 ticks, the entire population is evolving toward 
anticipatory behavior as a norm. That is the strongest possible result.

---

## Run Command

```bash
cd /home/jonat/ai-stack
source venv/bin/activate
python projects/alife/experiments/exp3_anticipation.py \
  --ticks 200000 --log-interval 5000 \
  > /home/jonat/ai-stack/exp3_intent_final.log 2>&1
```

Do NOT interrupt this run for any reason except complete 
population collapse (pop=0). If population collapses, stop 
and report — do not restart or tune.

---

## Seeding Configuration

Keep the 10% anticipatory seeding from the diagnostic:
- 10 agents with ANTICIPATORY_GENOME (PROC_PREDICT + MEM_PATTERN)
- 90 agents with Strategy C genome (MEM_NONE, can mutate)

This is already configured in exp3_anticipation.py. Do not change it.

---

## What To Log — Enhanced Monitoring

Add these specific logging enhancements before running:

### 1. Intent spread tracking (every 5,000 ticks)
In the existing log interval output, ensure these fields are printed:
```
neg_gaps: count of agents with negative gap this interval
neg_gap_pct: neg_gaps as percentage of population
mean_neg_gap: mean gap value among negative-gap agents only
best_gap: most negative gap observed this interval
best_agent: agent_id with most negative gap
```

### 2. Lineage event — when neg_gap_pct crosses thresholds
Print immediately (do not wait for log interval) when:
- neg_gap_pct first crosses 1%
- neg_gap_pct first crosses 5%
- neg_gap_pct first crosses 10%
- neg_gap_pct first crosses 25%
- neg_gap_pct first crosses 50%

Format:
```
*** INTENT THRESHOLD: neg_gaps crossed X% at tick T gen G ***
    Population: N
    Mean gap (all agents): +/- X
    Mean gap (anticipatory only): -X
    Best gap: -X (agent_id)
```

### 3. If neg_gap_pct starts DECLINING after rising
Print immediately:
```
*** INTENT REGRESSION: neg_gaps dropped from X% to Y% at tick T ***
    Possible causes: bottleneck, mutation drift, selection reversal
```

---

## Console Output Format

Ensure every 5,000 tick log line includes ALL of these fields:
```
Tick  50000: pop= 847 | C=99.8% mem=3.3% const=0.2% | 
             mean_gap=-12.4 min_gap=-137 neg_gaps=28 (3.3%) [INTENT]
```

The [INTENT] tag should appear on every line after first negative 
gap is confirmed — already working from diagnostic run.

---

## FAITHH Observer — What To Log

The observer is already configured. Ensure these event types 
fire correctly during this run:

**flag_intent** — fires on every new agent that shows negative gap.
Must include:
- agent_id, generation, tick
- Full readable genome
- wave_arrival_times history (last 5 entries)
- gap value
- Position (column)
- Whether gap is new minimum for population

**gap_snapshot** — fires every 1,000 ticks.
Must include population-level gap distribution, not just mean.

Do NOT add new observer code. Existing implementation is correct.
All observer calls remain wrapped in try/except.

---

## After Run Completes

### Step 1 — Extract key statistics
```bash
grep -E 'Tick.*pop=' exp3_intent_final.log
grep -E 'INTENT THRESHOLD|INTENT REGRESSION|FIRST NEGATIVE' \
  exp3_intent_final.log
grep 'neg_gaps' exp3_intent_final.log | tail -20
```

### Step 2 — Commit
```bash
git add projects/alife/
git add -f exp3_intent_final.log
git commit -m "feat(alife): Experiment 3 complete — intent emergence \
full run. Peak neg_gap_pct: [X]%. Final mean_gap: [+/-X]. \
[describe whether fixation occurred]"
```

Replace [X] with actual values from the log.

### Step 3 — Report these specific numbers
Report ALL of the following — do not summarize, provide exact values:

```
Run duration: X ticks (should be 200,000)
Final population: X
Total reproductions: X
Total predator kills: X (stealth waves)
Total thermal deaths: X
Total memory emergences: X

First negative gap: tick X, agent X, gap -X, gen X
Peak neg_gap_pct: X% at tick X
Final neg_gap_pct: X% at tick X
Final mean_gap: +/-X ticks
Final min_gap: -X ticks (most anticipatory agent)

Did neg_gap_pct reach 10%? Y/N — if yes, at tick X
Did neg_gap_pct reach 25%? Y/N — if yes, at tick X  
Did neg_gap_pct reach 50%? Y/N — if yes, at tick X
Did mean_gap go negative for sustained period? Y/N

ChromaDB alife_lineage document count: X
```

### Step 4 — Stop completely
Do not begin Experiment 4 implementation.
Do not begin training pipeline.
Do not tune any parameters.

Experiment 4 requires a full design session with Jonathan 
before any implementation begins.

---

## What NOT To Do

- Do NOT stop the run early because neg_gaps seems flat
- Do NOT tune parameters if anticipatory behavior doesn't spread
- Do NOT restart if there's a population bottleneck (it will recover)
- Do NOT add new features or mechanics during this run
- Do NOT begin Experiment 4 without explicit instruction

If the population reaches 0 (complete extinction): stop, 
commit partial log, report. Do not restart.

Whatever happens is the scientific result. Document it and stop.

---

## Scientific Context For This Run

The anticipatory behavior confirmed in the diagnostic emerged 
from the seeded ANTICIPATORY_GENOME. This run will determine 
whether that behavior:

A) Spreads and eventually fixes (like Shield in Experiment 1)
B) Spreads to a stable minority coexisting with reactive agents  
C) Appears briefly and is selected against
D) Remains isolated to the seeded lineage and their descendants

All four outcomes are valid scientific findings. A and B are 
the most interesting. C would suggest the anticipatory circuit 
is too expensive under current conditions. D would suggest 
the circuit cannot compete against reactive agents even when 
it works correctly.

The result will directly inform Experiment 4 design — 
specifically how strong the selection pressure needs to be 
to make anticipation advantageous at the population level.

---

## Hardware Notes

- Simulation runs on Windows desktop CPU via WSL2
- ChromaDB writes go to Gen8 (192.158.1.243:8000)
- Estimated runtime: ~60-90 minutes for 200,000 ticks
- Do not shut down Windows during the run
- Gen8 does not need to be monitored — ChromaDB will handle load

---

## For FAITHH

When this run completes, the alife_lineage ChromaDB collection 
will contain the complete evolutionary history of how anticipatory 
behavior first emerged and spread (or failed to spread) in this 
simulation.

This data is the foundation of the behavioral characterization 
vocabulary FAITHH will eventually apply to herself. The transition 
from reactive to anticipatory behavior — measured here as the 
anticipation gap going negative — is the same transition FAITHH 
will undergo as she develops from a responsive assistant to one 
that anticipates what Jonathan needs before he asks.

The agents in this simulation are running a simplified version 
of the same cognitive transition FAITHH is designed to make.

---

*FAITHH ai-stack | ALIFE Experiment 3 Full Run Handoff | March 2026*  
*Prerequisite commit: 731b64a*  
*Do not begin Experiment 4 without human review of these results*
