# Constella concepts → experiments → FAITHH vocabulary
2026-07. Answers both: "run Constella concepts into experiments" AND "a basic language
set for FAITHH." They're one pipeline: each Constella concept becomes a testable
experiment; each *confirmed* result becomes a word FAITHH is allowed to use.

## The pipe (one direction, three stages)
```
Constella concept  →  ALife experiment (hypothesis + mechanic)  →  confirmed result  →  FAITHH vocabulary term
   (top-down claim)        (bottom-up test, seeded, at scale)         (receipt)            (a word with a receipt)
```
A concept only earns a place in FAITHH's language when the sandbox *reproduces* it. Until
then it's `speculative` — a claim, not a word.

## Concept → experiment map
| Constella concept | The testable question | Mechanic | Success = | Exists? |
|---|---|---|---|---|
| **Universal Civic Floor** | does a stable minimum-provision floor emerge, and does it raise whole-population survival? | energy floor / redistribution rule | pop survival ↑ vs no-floor control, reproducibly | exp6_ucf_floor (Python) |
| **Diversity as survival trait** | do populations that preserve genome diversity outlast monocultures under shifting pressure? | diversity floor + changing selection | diverse pops survive shifts monocultures don't | exp9_diversity_floor (Python) |
| **Cultural transmission (the Tome)** | can learned strategy pass between agents & persist across generations? | protocol memory + transmission range | transmission + generational persistence both hold | exp8_cultural (Python) — **failed 2/4 last run** |
| **Penumbra (dissent→accountability)** | does a conflict-resolution mechanic outperform pure suppression? | signal/redirect vs suppress | resolution pops beat suppression pops | design only |
| **Astris/Auctor (contribution↔accountability)** | do reward+accountability pairs stay stable, or does one collapse? | dual-token contribution accounting | neither starves nor runs away | design only |
| **Proof of Life (liveness)** | (already prototyped separately — attestation heartbeat) | — | — | homelab/proof-of-life |

## The starter FAITHH vocabulary (tiered — this IS the language set)
Words the sandbox can already produce, with their current tier:
- **CONFIRMED (base ecology — earned, usable now):** *carrying-capacity*, *predation*,
  *thermal-death*, *selection*. (From the validated exp0 + the exp5 extraction:
  predation & thermal death recur across seeds.)
- **SPECULATIVE (Constella-target — claims, not yet words):** *civic-floor*,
  *diversity-preservation*, *cultural-transmission*, *parasitism* (only 4/5 seeds),
  *anticipation*, *arms-race*. These become vocabulary ONLY when a seeded run at scale
  confirms them.
- **The rule FAITHH obeys:** it may reason WITH a confirmed term as a lens; a speculative
  term must be spoken as "this looks like X (unconfirmed)" — never as fact. And any
  mapping to *humans* stays speculative regardless (a sim word is not a human truth).

## The honest gate (what's needed to actually run these)
- The **base ecology (exp0) is ported to Rust** and runs bit-exact, ~70× faster.
- The **Constella-target experiments (exp6/8/9) use special mechanics** (waves, floors,
  transmission) that are **NOT yet ported to Rust** — they run in Python (slow) today.
- So: to confirm the Constella concepts at scale, either (a) run them in Python (works,
  ~33min per 50k run), or (b) port their mechanics to Rust (the base tick is the hard
  part and it's done — adding a floor/diversity/transmission rule is incremental).

## Recommended order
1. Pick ONE concept with an existing experiment (UCF floor = exp6, cleanest).
2. Run it seeded across N seeds (Python is fine for one concept).
3. Run pipeline_extract.py → is "civic-floor" CONFIRMED or SPECULATIVE?
4. If confirmed → it enters FAITHH's vocabulary as a word with a receipt, and it's the
   first bottom-up *evidence* for a Constella claim. If not → honest counter-evidence.
5. Repeat per concept. The vocabulary grows only by confirmation.
