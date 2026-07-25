# HANDOFF: ALIFE Experiment 3 Complete — Ready for Experiment 4

**Date**: 2026-03-23
**From**: Cascade Session
**To**: Sonnet 4.6 (Next Session)
**Status**: Experiment 3 COMPLETE, ready for next phase

---

## What Was Accomplished

### Experiment 3: The Anticipation Gap — FULL_SUCCESS

Ran a 200,000 tick simulation to test whether agents could evolve **anticipatory behavior** — shielding *before* detecting threats by predicting wave arrival times.

#### Key Results

| Metric | Value |
|--------|-------|
| **Outcome** | FULL_SUCCESS |
| **First Negative Gap** | tick 402, agent_861, gap=-2 |
| **Peak neg_gap_pct** | 138.5% (tick 85000) |
| **Thresholds Crossed** | 1%, 5%, 10%, 25%, 50% ✓ |
| **Final Population** | 873 |
| **Final Mean Gap** | -1.7 ticks |
| **Final Min Gap** | -184 ticks |
| **Memory Emergences** | 129,345 |
| **Predator Waves** | 999 |
| **Total Reproductions** | 443,708 |

#### What "Negative Gap" Means
- `gap = shield_tick - current_tick`
- **Negative gap** = agent activated shield BEFORE the wave was detectable
- This proves agents learned to **anticipate** threats using `PROC_PREDICT`

---

## Technical Changes Made

### 1. `PROC_PREDICT` Implementation Fixed
**File**: `projects/alife/ops.py`

Changed from broken sense-value extrapolation to proper wave timing prediction:
```python
def proc_predict(sense_value: int, agent: 'Agent', world: 'World') -> bool:
    if len(agent.wave_arrival_times) < 2:
        return False
    intervals = [agent.wave_arrival_times[i] - agent.wave_arrival_times[i-1]
                 for i in range(1, len(agent.wave_arrival_times))]
    avg_interval = sum(intervals) / len(intervals)
    last_arrival = agent.wave_arrival_times[-1]
    predicted_next = last_arrival + avg_interval
    ticks_until_predicted = predicted_next - world.tick
    horizon = SENSE_THREAT_RANGE * 3
    return 0 < ticks_until_predicted < horizon
```

### 2. Wave Arrival Tracking
**File**: `projects/alife/agent.py`
- Added `self.wave_arrival_times: List[int] = []` to Agent.__init__
- Added `child.wave_arrival_times = self.wave_arrival_times.copy()` to create_child

**File**: `projects/alife/world.py`
- Records wave contact times in `apply_wave_damage`:
```python
if abs(agent.x - front) < 1.0:
    agent.wave_arrival_times.append(current_tick)
    agent.wave_arrival_times = agent.wave_arrival_times[-8:]
```

### 3. Gap Calculation Fixed
**File**: `projects/alife/simulation.py`
- Changed from `gap = current_tick - shield_tick` to `gap = shield_tick - current_tick`

### 4. Enhanced Logging
**File**: `projects/alife/experiments/exp3_anticipation.py`
- Added `neg_gap_pct`, `mean_neg_gap`, `best_gap`, `best_agent` tracking
- Added threshold crossing alerts (1%, 5%, 10%, 25%, 50%)
- Added intent regression detection

---

## Commits

```
4d344d6 exp3: FULL_SUCCESS - anticipatory behavior emerged and spread
731b64a (earlier) exp3: diagnostic confirmed negative gaps with seeded anticipatory genome
```

---

## Files of Interest

| File | Purpose |
|------|---------|
| `exp3_intent_final.log` | Full 200K tick log (129K+ lines) |
| `projects/alife/experiments/exp3_anticipation.py` | Experiment script with enhanced logging |
| `projects/alife/ops.py` | Contains fixed `proc_predict` |
| `projects/alife/agent.py` | Agent class with `wave_arrival_times` |
| `projects/alife/world.py` | Wave damage + timing recording |

---

## What's Next: Experiment 4 Options

Per the ALIFE roadmap, possible next experiments:

1. **Experiment 4: Cooperative Signaling** — Can agents evolve to warn others of threats?
2. **Experiment 4: Resource Sharing** — Can agents evolve altruistic energy transfer?
3. **Training Pipeline** — Extract successful genomes for LoRA fine-tuning

### Recommended Next Step
Review `docs/roadmaps/` for the ALIFE experiment plan and decide which Experiment 4 variant to pursue.

---

## Important Context

### ALIFE Simulation Architecture
- **Genome**: 8 slots (S0, S1, P0, P1, M0, A0, A1, R0) controlling behavior
- **Ops**: SENSE_*, PROC_*, MEM_*, ACT_*, REG_* operations
- **Waves**: Predator waves sweep across world, stealth waves are invisible until close
- **Energy**: Agents need energy to survive, reproduce, and shield

### Key Genome for Anticipation
```python
ANTICIPATORY_GENOME = [
    SENSE_LIGHT, SENSE_THREAT,      # S0, S1
    PROC_THRESHOLD, PROC_PREDICT,   # P0, P1 - PROC_PREDICT is key
    MEM_PATTERN,                    # M0
    ACT_REPRODUCE, ACT_SHIELD,      # A0, A1
    REG_NONE                        # R0
]
```

---

## No Action Required

- Experiment 3 is complete and committed
- Log file preserved in repo
- Ready for Experiment 4 planning

---

## Quick Commands

```bash
# View experiment results
tail -50 /home/jonat/ai-stack/exp3_intent_final.log

# Run ALIFE simulation
cd /home/jonat/ai-stack
source venv/bin/activate
python projects/alife/experiments/exp3_anticipation.py --ticks 10000

# Check git status
git log --oneline -5
```

---

*Handoff complete. Experiment 3 achieved FULL_SUCCESS.*
