# ALife sandbox review — did the experiments hold up?
Reviewed 2026-07 under the attestation discipline (claims need receipts). Companion to
constella `docs/alife/ACCURACY_REVIEW.md` (which reviewed the *docs*); this reviews the
*code and results*. Question asked: is the sandbox real, does it keep fossil records with
stable readouts, and did it produce truthful concepts (Red Queen etc.)?

## Verdict in one line
**The sandbox is real and well-designed; the results are not yet truthful/stable — many
are empty or honestly null, and the flagship Red Queen run has no captured outcome.**
The infrastructure earned confidence; the conclusions have not.

## 1. The sandbox — HELD UP ✅
A legitimate, sophisticated ALife engine, not a toy:
- Real energy economy (sources, regen, drain, reproduction cost/threshold).
- Four mutation operators (point, byte-swap, slot dup/del, category crossing).
- A **moving predator wave** with variance + 30% stealth/lethal waves — selection that
  rewards *prediction*, by design ("memory confers survival advantage").
- **Lineage is tracked**: agents carry `parent_id` + `generation`; an `alife_lineage`
  ChromaDB collection is the intended fossil record.
- A real experiment progression: exp0 primordial → exp1 pressure → exp2 stripe →
  exp3 anticipation → exp4 harmonic → exp5 parasitic/poison → exp6-9 (UCF/cultural/diversity).

## 2. The experiments — WELL-DESIGNED ✅
This is real experimental method, not vibes:
- **Pre-registered `success_criteria`** per experiment (you can see pass/fail honestly).
- **Proper scale where it counts**: exp5 parasitic configured for **50,000 ticks, pop 200**;
  cultural transmission for 30,000 ticks.
- **Red Queen is genuinely present**: exp5's *adaptive predator* "tracks Shield dominance,
  gains effectiveness over time; Shield becomes progressively useless" — a coevolutionary
  antagonist forcing continual adaptation. That IS the Red Queen mechanic, correctly built.
- They ran **noise sweeps and confirmation generations** (band2 gen6/gen7) — the right
  instinct: test whether an effect is real or noise.

## 3. The results — THE HONEST GAP ⚠️
Where the "solid full picture" isn't there yet:
- **Empty outcomes.** The flagship **exp5 parasitic (Red Queen)** result file has the run
  *parameters* (50k ticks, pop 200) but **`results: []`** — no captured outcome. Same for
  exp9 diversity floor. The runs were configured (maybe started) but the truthful readout
  wasn't saved/finished. So Red Queen is **designed, not demonstrated**.
- **Where data exists, it's honestly null/partial** — which is good science, but not a
  breakthrough:
  - **exp8 cultural transmission**: success_criteria recorded as `protocol_evolution: True,
    cultural_transmission: FALSE, knowledge_encoding: True, generational_persistence: FALSE`
    — **2 of 4 hypotheses failed**, and only **3 generations** ran. This directly
    **contradicts the old inflated "cultural evolution breakthrough (17,205 transmissions)"**
    claim — the sim's own honest record says transmission and persistence did *not* hold.
  - **band2 cooperation noise sweep**: the A-vs-B score gap oscillates around zero
    (+0.20, −0.11, +0.01, −0.03 …) and the hypothesis flips run to run. That's a **null
    result at noise level**, on tiny 15-tick / 30-agent runs.
- **Fossil records: designed but not readable now.** Lineage persists to the
  `alife_lineage` ChromaDB collection on **Gen8, which is offline**; local result JSONs are
  often empty. So the fossil record can't currently be read back as a stable dataset.

## 4. Red Queen specifically (the concept you named)
- **The ingredient is correctly built** (adaptive coevolving predator, exp5).
- **The result is not captured** (empty outcome file). So we cannot say the sim *produced*
  Red Queen dynamics — only that it's *set up to*. That's an honest "not yet," not a "no."

## 5. What's needed to reach "truthful stable concepts"
The gap is capture + rigor, not architecture:
1. **Finish and SAVE the flagship runs** (exp5 parasitic especially) — an outcome file with
   real readouts, not just parameters. Right now the Red Queen claim has no receipt.
2. **Get the lineage/fossil record off Gen8 or persist locally** — a readable, stable
   dataset (JSONL lineage log like the attestation chain would work offline).
3. **Report criteria honestly** as the sim already does (2/4 failed is a real finding) —
   and stop inheriting the old inflated summaries (the README claims are contradicted by
   the sim's own success_criteria).
4. **Replication + noise floor** on the experiments that matter (they started this with
   band2 gen6/7 — extend it to exp3/exp5).

## Bottom line
You built a genuine sandbox with the right concepts, including a correct Red Queen setup —
that's the hard part and it held up. What hasn't happened yet is *capturing truthful,
stable readouts*: the flagship results are empty, the completed ones honestly show null/
partial effects, and the fossil record is stranded on an offline box. The path to a "solid
full picture" is finishing and honestly recording the runs — not rebuilding anything.
