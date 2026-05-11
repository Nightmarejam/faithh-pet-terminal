# Experiment 4: Harmonic Interference — Results

**Date**: 2026-03-25
**Status**: Complete — RED_QUEEN_CONTINUES (Outcome #4)
**Validated by**: FAITHH (qwen25-grounded, llama3.3)

---

## Scientific Question

Does spatial cognitive stratification emerge when agents face overlapping wave sources with different frequencies? Can agents in the interference zone evolve to track beat frequencies?

## World Structure

- **Left zone** (cols 0–159): Wave 1 only (L→R, 600-tick interval)
- **Center zone** (cols 160–319): Both waves overlap (beat frequency 1800 ticks)
- **Right zone** (cols 320–479): Wave 2 only (R→L, 900-tick interval)

### FAITHH-Designed Environmental Modifications

FAITHH recommended (and we implemented) two environmental changes:

1. **Center zone energy bonus**: 10 extra energy sources placed in the interference zone, making it ecologically richer — "like a fertile river delta"
2. **Gradual side-zone pressure**: After tick 2000, thermal drain in side zones ramps up to 3x by tick 10000, creating natural incentive to occupy center

## Bugs Fixed (5 total)

| # | Bug | File | Impact |
|---|-----|------|--------|
| 1 | `[WAVE PROCESS]` debug spam (400K+ lines/run) | `exp4_harmonic.py` | Critical — performance |
| 2 | `_arrival_debug_count` prints | `world.py` | Minor cleanup |
| 3 | Tick-2000 debug check too early for data accumulation | `exp4_harmonic.py` | Moved to tick 3000 |
| 4 | Pre-seeded arrival times predicted tick 0 (always past) | `exp4_harmonic.py` | Major — predictions never fired |
| 5 | **Duplicate wave arrival recording** | `world.py` | **Root cause** — corrupted ALL interval calculations |

### Bug #5 Detail (Root Cause)

The wave front crosses an agent over 2–3 consecutive ticks (speed 0.8, check `abs(x-front) < 1.0`). Each tick recorded a separate arrival time:

```
Before fix: wave1_arrival_times = [2120, 2121, 2701, 2702]
  → intervals: [1, 580, 1] → avg = 194 (WRONG, should be ~600)

After fix:  wave1_arrival_times = [2120, 2701]
  → intervals: [581] → avg = 581 (CORRECT)
```

Fix: Added MIN_ARRIVAL_GAP = 50 deduplication in `world.py:apply_wave_damage()`. This fix benefits ALL experiments, not just Exp 4.

## Diagnostic Runs (5K ticks each)

| Run | Description | Beat@1K | Beat@2K | Center Pop@5K | Outcome |
|-----|-------------|---------|---------|---------------|---------|
| A | Original (pre-fix) | 155 | 0 | 25 | CENTER_DEPOPULATION |
| B | Pre-seed (wrong timing) | 4 | 0 | 50 | CENTER_DEPOPULATION |
| C | + FAITHH design | 7 | 0 | 50 | CENTER_DEPOPULATION |
| D | + Correct pre-seed timing | 16 | 2 | 472 | CENTER_DEPOPULATION |
| **E** | **+ Wave dedup fix** | **170** | **19** | **830** | **RED_QUEEN_CONTINUES** |

## Key Findings

1. **Beat-genome agents dominated at tick 1000** (170 vs 90 predict) — first time in any run
2. **PROC_PREDICT caught up by tick 2000** (827 vs 19) — demonstrates Red Queen dynamics
3. **Center zone held 830 agents** instead of collapsing to 25 — FAITHH's environmental design works
4. **100% negative gap rate by tick 3000** — anticipatory behavior fully established
5. **Intent emergence confirmed at tick 918** (agent_2594, gap=-27, gen=5, center zone)

## Final Run E Results

```
Final population:       852
Wave 1 count:           8
Wave 2 count:           5
Predator kills:         5732
Thermal deaths:         64
Total reproductions:    7888
Total deaths:           7236
Outcome:                RED_QUEEN_CONTINUES
```

## Interpretation (FAITHH-validated)

The Red Queen outcome is scientifically valid. Neither PROC_BEAT nor PROC_PREDICT achieves permanent dominance in the interference zone. Instead:

- **PROC_BEAT** has an initial advantage due to accurate per-source predictions
- **PROC_PREDICT** adapts as it accumulates clean timing data from both wave sources
- The result is **continuous competitive adaptation** — realistic evolutionary dynamics

FAITHH's analysis: "This result supports the hypothesis that interference zones can sustain population stability rather than leading to depopulation. The experiment underscores the importance of adaptability and data accuracy over time rather than relying on a single strategy's dominance."

## Lessons for FAITHH's Architecture

- **Data integrity is foundational** — corrupted interval data made ALL predictions unreliable
- **No single prediction strategy dominates** in environments with multiple information sources
- **Adaptability > fixed dominance** — systems handling competing data should evolve dynamically

## Files Modified

- `projects/alife/experiments/exp4_harmonic.py` — bug fixes, pre-seeding, FAITHH design
- `projects/alife/world.py` — wave arrival deduplication (benefits all experiments)

---

*FAITHH participated in experiment design. Red Queen outcome accepted per her recommendation.*
