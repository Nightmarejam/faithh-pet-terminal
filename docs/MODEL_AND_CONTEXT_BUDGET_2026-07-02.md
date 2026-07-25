# NetNavi model & context budget — design capture
tier: speculative/design, 2026-07-02. Companion to CONNECTIVE_ARCHITECTURE +
pet_attestation_device (constella). Captured so it's on the trail — recurring theme,
will circle back. No build implied.

## Three devices hide under "PET" (difficulty, easy→hard)
1. **Thin-client terminal** — offloads thinking to the Mac/lab; screen+mic+input+link.
   EASIEST. Off-the-shelf (phone, Pi, SBC). It IS docked mode — a software switch, not
   hard hardware.
2. **Standalone NetNavi** — runs a small model ON the PET, no computer nearby. The
   genuinely HARD one — and it's a *model-size* problem, not a device problem: fitting
   "enough of a self" into pocket-class compute.
3. **Tier 0 attestation** — PUF/secure element. Hard SILICON, the only part needing
   specialized manufacturing.
Correction to the instinct that "the housing is hardest": housing is easy; the model is
hard. Effort belongs on the standalone model.

## Training: Unsloth is the right tool, with one rule
- Unsloth = efficient LoRA/QLoRA on a single consumer GPU. The **3090 (24GB) fits it**;
  realistic targets: Llama 3.2 3B, Qwen 2.5 3B/7B.
- **THE RULE: fine-tune the stable self; retrieve the daily self.**
  - Fine-tuning bakes in persona/voice/values — the "standard of existence." Done once
    or rarely. Slow, expensive; you don't retrain weekly.
  - Daily/weekly inputs = RAG, NOT weights. That's the day-loop, and it's the existing
    hot/warm/cold memory tiering (SYSTEMS_MAP). Training daily experience in is how models
    get expensive AND forgetful.

## Context budget = confirmability applied to the token window
"How much context is the irreducible self vs. room for the day" is a real, answerable
budgeting problem:
- **Identity core** — small (a few thousand tokens): who it is, values, its person.
  High-tier, ALWAYS loaded, never evicted.
- **Retrieval window** — recent daily/weekly inputs. Lower-tier, evictable, refreshed by
  the day-loop.
- **Budget rule**: identity outranks recency when space runs short. Same tier logic as
  the confirmability schema, pointed at the token budget instead of at facts.

## Honest difficulty ordering (for planning)
standalone model  >  attestation silicon  >  housing  >  thin client (easy)
Unsloth is the attack on the hard one; "minimal context" is the right sub-problem —
a budgeting exercise, not open research.

## When circled back to — first questions
- Which base model (3B for PET-class vs 7B for lab-class)?
- What's actually IN the identity core, and its token size?
- Fine-tune dataset = ? (curated FAITHH conversations? the persona docs?)
- Does the identity core differ per person, or is there a shared base + personal LoRA?
