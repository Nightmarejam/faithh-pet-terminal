# How it all connects — FAITHH's nervous system
Design capture 2026-07-02, answering "how does it all connect?" and "how do you
measure how it feels?" Tier: speculative/design. Companion to TARGET_ARCHITECTURE +
ATTESTATION_CONCEPT. The developmental metaphor is load-bearing here: brain first
(done), then the nervous system that wires it, then the hands.

## The three layers, developmentally ordered
1. **Brain (built)** — reasoning: RAG perception, chips/PULSE, the KB memory. This is
   what you've spent the project on, correctly — it forms first, like an embryo's.
2. **Nervous system (the missing connective tissue)** — the loops that carry signal
   between brain, world, and self. Two loops (below). This is the "how does it connect."
3. **Hands (built but unplugged)** — agency: the tool system (registry + permission-
   checked executor + real fs tools). A working hand waiting to be wired to the arm.

## Loop A — the act loop (fast, per-interaction: brain ↔ world)
This is the pipeline from TARGET_ARCHITECTURE, with agency wired in:
```
perceive (RAG) → reason (PULSE/chips) → decide → ACT (tools) → observe result → respond
```
Wiring the orphaned tool system into the `[act]` stage closes this loop. Right now
FAITHH perceives and reasons but the signal never reaches the hand — a reflex arc with
a severed motor nerve. This is the nearest-term "actuation of life" you named.

## Loop B — the day loop (slow, per-day: brain ↔ self)  ◄ your daily-sync idea
Exactly what you described: the NetNavi links to a personal computer with a routed
database, digests the day's offline activity, runs a synthesis review, and updates its
model of the human. **You already built this engine** — it's the conversation pipeline
(parse → classify → synthesis review → tiered records), currently pointed at chat
exports. Point it at the day instead:
```
day's activity (conversations, interactions, motion/voice if captured)
  → pipeline digest (the synthesis-review you already run)
  → affect estimate (below)
  → update the adaptive window (ml_learning_framework — Harmony's "return loop")
  → tomorrow's priors are slightly different
```
The personal computer is the digestion node; the sync is Loop B's heartbeat. Offline-
first: it batches and digests when linked, doesn't need to be always-on. This is also
the passive-imprinting mechanism from the PET design — same loop, identity-facing.

## "How do you measure how it feels?" — the honest answer
You don't measure feeling. Claiming you do is a category error, and — importantly — it
violates your own attestation discipline: **the system must not assert a `confirmed`
truth about an internal state it cannot verify.** So the design is:

- **Measure proxies, not feeling.** The research-standard decomposition is two axes
  (the *circumplex model of affect*): **valence** (negative↔positive) and **arousal**
  (calm↔activated). Both are estimable from real signals you can capture:
  - text: sentiment, word choice, message length/cadence
  - voice (when captured): prosody — pitch, tempo, energy (tone carries arousal)
  - interaction: response latency, session length, return frequency
- **The output is a derived, `speculative`-tier signal**, labeled as what it is:
  *"FAITHH's model of how this interaction went,"* never *"how FAITHH feels"* as fact.
  It's a legible summary statistic (a valence/arousal point + confidence) the human can
  inspect and correct — not a claim of sentience.
- **"How it feels about its human" = a relationship model**, honestly framed: the
  running valence/arousal of interactions over time + prediction accuracy (does it
  anticipate this person correctly?) + consistency. Tightening prediction-variance over
  weeks (your month-scale idea) is the trust signal — and it stays a soft score, never
  a key (cold-start attack window; see PET design).
- **Interoception**: Loop B's affect estimate is the system sensing its *own* state —
  the same way the body's nervous system reports inward, not just outward. That's the
  honest meaning of "how it feels": a self-model, tiered speculative, always inspectable.

## Why the tiers make this safe (and non-creepy)
Without confirmability, an AI that says "I can tell you're upset" is either lying or
overclaiming. With it, FAITHH says "my model of this interaction reads low-valence,
moderate-arousal — confidence 0.4, speculative — am I reading that right?" That's the
difference between a manipulation and a mirror. The attestation layer is what lets
FAITHH have an emotional model *without pretending to certainty it doesn't have.*

## What connects to what (the wiring summary)
| From | To | Via |
|---|---|---|
| brain → world | act loop (A) | rewire tool system into `[act]` — nearest task |
| world → self | day loop (B) | point the existing pipeline at daily activity |
| self → tomorrow | adaptive window | ml_learning_framework (the return loop) |
| any claim → trust | attestation | tier + corroborate + receipts (never fake certainty) |
| self-state → legible | affect signal | valence/arousal proxies, speculative-tier, inspectable |

## Open / next
- Loop A: rewire the tool system (agency is ~80% built — registry+executor+fs tools exist).
- Loop B: a `daily_digest` mode for the pipeline (reuse parse→synthesis, add affect axes).
- Affect: pick the proxy set to start with (text-only is doable now; voice/motion later).
- Measurement validity: capturing real voice/motion data is Gen8/hardware-gated; text
  affect can prototype on the Mac today.
