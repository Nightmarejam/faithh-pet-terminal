# Attestation — the concept FAITHH has been building without naming
Phase 1 design note, 2026-07-02. Static discovery + design; no Gen8 needed.
Companion to CAPABILITY_MAP. Cross-refs constella docs/reference/confirmability.md.

## What you're actually striving for (the concept)
One idea runs through the whole stack and has never had a single name: **attestation** —
the act of attaching *checkable provenance* to a claim, and refusing to treat anything as
true without it. It has two faces that are the same shape:

- **Epistemic attestation (FAITHH):** how do we know a *claim* is true? → tier it
  (confirmed/asserted/speculative), cite its source, corroborate across independent
  signals. "An AI that shows its receipts."
- **Physical attestation (Constella / Proof-of-Life):** how do we know a *node* is a
  live, unique human? → hardware-rooted proof you can't fake by copying a key.

Confirmability (Constella) and this are not two concepts — they're attestation applied to
claims vs. to identities. Naming them together makes the framework and the flagship one
system: FAITHH is the working demo of the epistemic half; PoL is the governance half.

## What's ALREADY there but unnamed (the discovery)
FAITHH already has attestation primitives — they just aren't recognized as such:

1. **Coherence Arbiter = a corroboration engine.** `measure_convergence(rag_results,
   chip_activations, query_embedding)` scores agreement between two *independent* signal
   sources (semantic RAG vs. ML chip routing). That is exactly the promotion rule from
   the confirmability schema — "asserted rises toward confirmed when independent sources
   converge." It's computing a confidence score and calling it "coherence." Rename its
   output to a **corroboration score** and it becomes the tier-promotion signal.
2. **Anchor Validator = a stubbed claim-checker.** `validate_single_claim(claim_path)`
   is a generic interface for checking a claim against ground truth
   (`project_states.json`) — but it only supports one hardcoded path and is orphaned.
   This was the attestation enforcement hook, half-built and abandoned. It's the natural
   home for "given a claim, return its tier + receipt."
3. **RAG retrieval distances = raw confidence** already returned by `rag_processor.search`
   but thrown away at the response layer. That's the per-fact confidence input.
4. **The chat_export reranking penalty** (commit db3a2d6) is an *implicit* provenance
   rule — "conversation-sourced chunks are less trustworthy than doc-sourced." It's a
   tiering decision hidden in a reranker weight. Make it explicit as a source-tier.

So the honest status: FAITHH is ~40% of the way to an attestation layer and didn't know
it. The pieces exist as coherence/anchor/rerank; they've never been unified under one
concept or surfaced to the user.

## The design (epistemic attestation in FAITHH)
Minimal, uses what's there:
1. **Source tiers at ingest.** Every chunk carries a provenance tier in metadata:
   `doc` > `git/receipt` > `conversation` > `model-inferred`. (Formalizes the reranker
   penalty; hooks into the `rag/` package from the capability map.)
2. **Per-claim corroboration at query time.** Reuse the Coherence Arbiter's convergence
   output as a corroboration score; a claim supported by ≥2 independent high-tier sources
   is `confirmed`, one source is `asserted`, no retrieval hit is `speculative`.
3. **Attested responses.** Revive `validate_single_claim` as the response-side hook: the
   answer carries inline tier tags + a "receipts" footer (sources, tiers, corroboration).
   This is the demo differentiator — visible, checkable trust.
4. **Refusal to over-claim.** If everything retrieved is `speculative`, FAITHH says so
   instead of asserting. This is the RAG-drowning bug turned into a feature.

## Detailing with no concept yet (things in the code awaiting a name)
- `plc_state_manager` (orphan) — a deterministic state machine with "safety interlocks."
  There's no documented concept of FAITHH having a *governed state* with interlocks;
  either name it (a legitimate reliability concept) or archive it.
- `ml_learning_framework` (7 classes, live) + `ui_layout_optimizer` + `ai_driven_ux` —
  three modules doing online adaptation with no unifying concept. Candidate name:
  **the adaptive layer** (maps to Harmony's "online resonance tuning" — the return loop).
- `local_optimization` (748L, live) — substantial, purpose unclear from name; needs a
  read to decide if it's a concept or a grab-bag.

## Proof-of-Life → Proof-of-Work + hardware attestation (your reframe, captured)
You're right that PoL-as-whitepaper is the hardest artifact, and the pragmatic pivot is
sound: **don't invent novel consensus — borrow proven Proof-of-Work and move the novelty
into the attestation layer.** Sketch (speculative tier, for the RFC):
- **Liveness ≈ work already spent** (your energy-already-spent UCF anchor): a node proves
  participation via PoW-style expended compute, denominated in joules. Proven mechanism,
  no new consensus math to defend.
- **Uniqueness/humanity = hardware attestation**, not the PoW itself. This is where
  Trezor-class standards come in: a secure element signs an attestation that (a) this is
  a genuine device and (b) one human controls it. Third-party hardware root of trust does
  the heavy lifting cryptographers already solved (secure element, anti-tamper, PIN).
- **The three-party structure**: node (proves work) + hardware attester (proves it's a
  unique human-held device) + Constella ledger (records the attested liveness as a
  joule-denominated Proof-of-Life credit). No single party can forge a live human.
- **Why this is achievable and PoL-from-scratch isn't**: every hard part (consensus,
  device attestation) is delegated to a battle-tested standard; Constella only defines
  the *composition* and what a valid attestation buys you (UCF access, voting weight).
- Open question for the RFC: sybil resistance still leans on the hardware attester's
  enrollment being one-device-per-human — that's the trust assumption to state honestly.

## Next
- Decide the concept name to adopt repo-wide: **Attestation** (recommended — unifies
  FAITHH confirmability + Constella PoL) or keep them separate.
- If adopted: rename Coherence Arbiter's output to a corroboration score, revive
  `validate_single_claim` as the response hook, add source tiers to RAG ingest.
- Fold the PoL pivot into constella rfcs/001 as the "attestation layer" section.
