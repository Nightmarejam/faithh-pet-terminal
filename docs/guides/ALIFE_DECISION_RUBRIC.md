# ALife Decision Rubric

Use this rubric to decide whether an experimental condition is promotable, independent of data volume.

## Purpose

The ALife pipeline now produces high-volume, high-quality artifacts. This rubric prevents overreacting to single metrics or run-to-run noise.

## Primary endpoint hierarchy

Evaluate conditions in this strict order:

1. **Mean Band 3 score gap (A-B)**
2. **Hypothesis support rate**
3. **Trust direction consistency** (`trust_stability_A_higher_fraction`)
4. **Band 3 candidate count gap (A-B)**
5. **Net resource gap (A-B)**

If two conditions tie on #1 within a small tolerance, use #2, then #3 as tiebreakers.

## Promotion thresholds

Default thresholds for a condition to be considered promotable:

- `mean_band3_score_mean_gap > 0`
- `hypothesis_support_rate >= 0.30`
- `trust_stability_A_higher_fraction >= 0.70`

If one threshold fails, classify as **candidate** (not promoted).  
If two or more fail, classify as **rejected for this phase**.

## Canon profile interpretation

Each field signature can be labeled:

- **Constructive**: stability score >= 0.66 and positive Band 3 score gap
- **Neutral**: stability score >= 0.40 and non-negative Band 3 score gap
- **Corrosive**: otherwise

Where stability score combines:

- hypothesis support rate
- trust direction consistency
- normalized Band 3 score gap

## Run budget policy

Use a two-stage budget:

- Discovery: `n=10` runs per condition
- Confirmation: `n=20` runs per condition

Only make promotion decisions on confirmation runs.

## Retention policy (default)

- Keep all aggregate JSON and synthesis markdown.
- Keep raw per-run JSON through active phase; archive older phases after synthesis lock.
- Keep Chroma experiment records while storage headroom remains healthy.

## Checklist before advancing phase

- [ ] Confirmation run count met
- [ ] Primary endpoint hierarchy applied
- [ ] Promotion thresholds checked
- [ ] Canon profile labels generated
- [ ] Synthesis markdown published
