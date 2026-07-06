# Nomenclature pipeline — from ALife sandbox to FAITHH's usable vocabulary
Design capture 2026-07. Tier: design/speculative. Answers: "what pipelines do I need so
my AI can actually USE the terminology that emerges in the sandbox?" The goal is a
sandbox for *human/physical behavior in real time* — so the sandbox must produce a
**trustworthy, named vocabulary** FAITHH can reason with, without over-claiming that a
toy sim explains humans.

## The core insight: seeding is stage 0
A term the sandbox produces is only worth naming if it **reappears** — a behavior that
shows up under one random seed is a fluke; one that shows up across many seeds is a real,
nameable concept. So the seeding work (fossil_run.py) isn't just integrity-checking — it
is the **confirmation gate for the whole vocabulary.** No reproducibility, no nomenclature.

## The 7 stages

**1. EMERGENCE (in the sandbox).** Behaviors/strategies arise and get labels — some
hardcoded outcomes (`ARMS_RACE`, `PARASITISM_EMERGES`, `COLLAPSE`), some emergent (which
genomes persist), some metric-named (`first_parasite_tick`, `trust_network_stability`,
`stable_cooperative_networks`). This is raw vocabulary — unverified.

**2. EXTRACTION.** Pull the named phenomena out of the fossil records: what terms
appeared, when (`first_X_tick`), how often, in which lineages. (The fossils already hold
this; extraction is reading them, not new science.)

**3. GROUNDING — the receipt.** Each term gets a *mechanical definition tied to what
actually happened*, not just a label: "PARASITISM = an agent using ACT_SIGNAL to drain
energy from adjacent agents." A grounded, checkable definition. This is attestation
applied to vocabulary — a word without its mechanism is `speculative`.

**4. TIERING via REPRODUCIBILITY — where seeding pays off.** Run the experiment across
N seeds. A term emerging in most seeds → **`confirmed`** (robust concept). One seed →
**`speculative`** (fluke). Only confirmed terms graduate. *This stage is impossible
without the seeding you just built.*

**5. MAPPING — the isomorphism to human/physical (the risky, valuable part).** The
confirmed sandbox term is *offered* as an analogue to a human/physical behavior:
"sandbox-parasitism (energy drain) ↔ human free-riding / resource extraction." This is
the **Harmony-bridge pattern** (body↔civic), and it is **always `speculative`** — the
sandbox proves the concept exists *in the sim*, NOT that it validly describes humans.

**6. INGESTION.** The graduated vocabulary — {grounded definition + reproducibility
receipt + tentative human mapping, each tier-tagged} — enters FAITHH's knowledge base as
usable concepts (a "vocabulary" collection, distinct from raw conversation chunks).

**7. USE (real time).** FAITHH applies the vocabulary to describe real behavior, *always
carrying the tiers*: "this looks structurally like **parasitism** — confirmed in the
sandbox as neighbor-energy-drain; the mapping to what you're describing is my hypothesis,
not a fact." That sentence is the whole point: a named lens, honestly hedged.

## The honesty rule that keeps this from being pseudoscience
FAITHH using ALife-derived words for humans is the exact place over-claiming would ruin
it. The attestation tiers are the guardrail:
- The **concept** can be `confirmed` (reproducible in the sandbox).
- The **human mapping** stays `speculative` until there's independent human evidence.
- FAITHH must never collapse the two — "like sandbox-parasitism (confirmed)" is honest;
  "you are a parasite (fact)" is the failure mode. A toy model naming a real person is a
  hypothesis wearing a lab coat; the tiers keep the coat labeled.

## What to build (in order, matched to where you are)
1. **Seeds → reproducibility** ✅ done (fossil_run.py, all exp5-9).
2. **A term-extractor** — read fossils across seeds, list which named phenomena are
   reproducible (confirmed) vs one-off (speculative). Small, offline, next step.
3. **A grounded glossary** — for each confirmed term, the mechanical definition + the
   seeds/fossils that are its receipt. This IS the vocabulary artifact.
4. **Ingest the glossary into FAITHH** (a `vocabulary` KB collection) — Gen8-gated, but
   the glossary file can be built now.
5. **A USE rule in FAITHH** — when it reaches for a sandbox term, it must attach the tier
   (confirmed concept / speculative mapping). Wire into the attestation layer.

## Where this connects
- Same shape as the conversation pipeline (extract → ground → tier → ingest).
- Same discipline as confirmability (a term is `confirmed` only with a receipt).
- Same pattern as the Constella-Harmony bridge (cross-domain isomorphism, tiered).
- The ALife "index of chaotic understanding" (ACCURACY_REVIEW) *is* this vocabulary,
  once it's reproducibility-gated and grounded.
