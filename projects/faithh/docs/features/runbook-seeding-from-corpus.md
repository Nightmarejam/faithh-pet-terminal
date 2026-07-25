# Feature Spec: Runbook Seeding from Corpus

**Status:** Concept — not yet implemented  
**Date:** 2026-04-01  
**Author:** Jonathan Morales  
**System:** FAITHH + RunBook to Rule Them All

---

## Problem

Runbooks are written after the fact, manually, from memory.
This means:
- Steps get forgotten or compressed
- The runbook reflects what you remember, not what you did
- New runbooks only exist if someone decides to write them

---

## Concept

FAITHH's ChromaDB corpus (856,559 documents) contains implicit procedural
knowledge — session logs, terminal output, handoff docs, commit messages,
error traces. Clusters of related actions in this corpus are runbook seeds
that have never been extracted.

A periodic scan job identifies these clusters and surfaces them as:
- **Partial runbooks** — "You've done this 3 times, here are the steps we
  can infer. Fill in the gaps."
- **Runbook candidates** — "This looks like a repeatable process. Confirm?"

---

## Pipeline Design

### Stage 1 — Corpus scan (monthly or on-demand)

Query ChromaDB for document clusters that share:
- Similar tool sequences (bash commands, file paths, service names)
- Repeated temporal patterns (same steps across multiple sessions)
- High co-occurrence of specific keywords

Use BERTopic clustering (already researched for Chip Synthesis) to surface
natural groupings.

### Stage 2 — Pattern classification

For each cluster, classify:
- **Procedural** (looks like steps) → runbook candidate
- **Diagnostic** (looks like troubleshooting) → debugging guide candidate
- **Informational** (looks like reference) → skip or tag for docs

### Stage 3 — Seed generation

For procedural clusters, generate a scaffold:
- Inferred title from dominant terms
- Steps extracted from command sequences
- Gaps flagged as [INFERRED] or [VERIFY]
- Link back to source documents for human review

### Stage 4 — Human review and promotion

Present candidates in a simple review interface (could be a CLI or
Compass UI panel). Options:
- Approve → writes to runbook-to-rule-them-all
- Edit → opens scaffold for editing
- Reject → marks cluster as non-procedural

---

## Sandbox + Visual Recording

Each runbook execution should optionally record:
- Terminal output (already available via session logs)
- Screen capture tied to runbook step timestamps
- Step completion confirmations

This produces visual documentation automatically — future reference
shows not just what to do but what it looks like when done correctly.

Storage: Gen8 NAS, linked from runbook as optional media attachments.

---

## Connection to Existing Stack

- ChromaDB (Gen8): source corpus
- BERTopic: clustering (researched, not yet implemented)
- PULSE: pattern tracking — could flag "you've done this N times unrecorded"
- RunBook to Rule Them All: output destination
- Compass UI: review interface candidate

---

## Next Steps

- [ ] Define corpus query strategy for procedural pattern detection
- [ ] Prototype BERTopic scan on `faithh_knowledge_base` collection
- [ ] Design seed template format compatible with existing runbook structure
- [ ] Build review CLI (simple approve/reject/edit loop)
- [ ] Add PULSE trigger: "N similar sessions detected — runbook candidate?"
- [ ] Define visual recording capture method (screen + terminal sync)
