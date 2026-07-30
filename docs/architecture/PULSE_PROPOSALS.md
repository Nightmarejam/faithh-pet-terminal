# PULSE proposals — design

**Design doc** · 2026-07-30 · **not yet implemented**
Companion to [FAITHH_REDESIGN.md](FAITHH_REDESIGN.md) (who approves capability
growth) and [VECTOR_STORE_REVIEW.md](VECTOR_STORE_REVIEW.md).

## The question this answers

FAITHH accumulates state faster than a person can supervise it: 63,700 chunks, 244
living documents, 21 decisions, a routing table, chip centroids. Managing that by
hand does not scale, and the failures are quiet — nothing crashes, retrieval just
gets worse.

But the one component that already acted autonomously did real damage. The
conversation auto-indexer observed chats and wrote to the knowledge base
unsupervised. Its topic tagger was allowed to overwrite *provenance*, so FAITHH's own
answers were relabelled `document_type: decision` and retrieved as authoritative. A
wrong answer became a citation, which made the next wrong answer better supported.
Nine such records accumulated before anything noticed — and they were only noticed
because retrieval started working well enough for them to matter.

**That is the failure mode PULSE must not reproduce at larger scale.**

## Principle

> **PULSE proposes. The human disposes. Nothing writes to the knowledge base without
> an approval that can be traced back to a person.**

This is not caution for its own sake. It is the specific lesson of the auto-indexer:
an agent that writes what it infers will eventually infer something wrong, and a
knowledge base cannot tell the difference between a fact and a confident mistake.

## What already exists

Ten routes are implemented in `faithh_professional_backend_fixed.py`, and **none has
a UI** — this is the largest unexposed capability in the system
(see [FRONTEND_AUDIT.md](FRONTEND_AUDIT.md)):

| route | purpose |
|---|---|
| `/api/pulse/status` | engine state |
| `/api/pulse/proposals` | pending proposals |
| `/api/pulse/approve` | accept one |
| `/api/pulse/reject` | decline one |
| `/api/pulse/chips` | chip-related proposals |
| `/api/pulse/audit/summary` | what PULSE has done |
| `/api/pulse/audit/recent` | recent activity |
| `/api/pulse/health/check` | read-only assessment |
| `/api/pulse/health/heal` | **auto-remediation — see Staging** |
| `/api/pulse/security/scan` | security posture |

There is **no `pulse` module in `backend/`**. The routes exist; the engine does not.
That is an advantage: the contract can be designed before anything is built.

## Proposal shape

A proposal is a *diff plus its evidence*. The evidence requirement is what makes
review possible in seconds rather than minutes.

```json
{
  "id": "prop_20260730_001",
  "kind": "doc.stale | doc.dedupe | chip.new | index.reindex | config.drift",
  "title": "EMBEDDINGS.md contradicts SYSTEM_OVERVIEW.md on embedder dimension",
  "confidence": 0.86,
  "evidence": [
    {"source": "docs/architecture/EMBEDDINGS.md:44", "quote": "768-dim"},
    {"source": "docs/consolidated/SYSTEM_OVERVIEW.md:97", "quote": "384-dim"},
    {"source": "runtime", "quote": "query embedder reports 768"}
  ],
  "proposed_change": {"file": "...", "diff": "unified diff"},
  "reversible": true,
  "blast_radius": "1 document, 7 chunks re-embedded",
  "detected_by": "observer:doc-currency",
  "status": "pending"
}
```

Non-negotiable fields:

- **`evidence`** — at least two independent sources, each quotable. A proposal that
  cannot cite why it believes something is not reviewable, and an unreviewable
  proposal will be approved on vibes.
- **`reversible`** and **`blast_radius`** — the reviewer's actual question is "what
  happens if this is wrong", and the system should answer it rather than making them
  work it out.
- **`detected_by`** — which check produced this. When a check starts producing bad
  proposals you need to disable *it*, not stop trusting the queue.

## Staging

Ordered by how much damage a mistake does. Do not skip ahead.

### Stage 1 — Observe (implemented)

`scripts/ops/observer_report.py`. Read-only: dimension invariant, deploy drift,
model-output canary, doc currency, reachability, disk. Writes nothing, heals nothing.

An observer you trust is worth more than a healer you have to supervise. This stage
also generates the evidence corpus later stages depend on.

### Stage 2 — Propose (next)

Turn observer findings into proposals and expose `/api/pulse/proposals` in the UI.
Still no writes: approving only enqueues.

Build the **review screen** before the generator. A queue with no reviewer becomes a
queue nobody reads, and the point of PULSE is the human in the loop.

### Stage 3 — Apply, narrowly

Execute approved proposals for **reversible, verifiable** changes only:

- ✅ re-index a collection (old one is kept; cutover is one env var)
- ✅ correct a doc's stated config where a live check contradicts it
- ✅ restart a unit
- ❌ **never** write inferred facts into the knowledge base
- ❌ **never** relabel provenance
- ❌ **never** delete a record

Every application writes an audit entry (`/api/pulse/audit/recent`) with the
proposal id, the approver, and the diff actually applied.

### Stage 4 — `health/heal`, last

Auto-remediation without per-instance approval, and only for a **fixed allowlist** of
actions proven at Stage 3, each individually revocable. This is the endpoint most
likely to recreate the auto-indexer failure, so it is the last thing built and the
first thing disabled when anything looks wrong.

## What PULSE must never do

Direct consequences of the auto-indexer incident:

1. **Never write model output into the knowledge base as fact.** FAITHH's answers are
   output, not evidence. Retrieval already excludes them
   (`RAG_EXCLUDE_MODEL_OUTPUT`); PULSE must not reintroduce them by another route.
2. **Never let an inferred label overwrite provenance.** Topic classification is an
   inference. `type`, `category`, `document_type` and `source` are facts about origin.
3. **Never delete history.** Records are how the system explains itself. Down-weight
   them (`document_type: doc_record`); do not remove them.
4. **Never act on a proposal it generated *and* approved.** If PULSE ever gains an
   auto-approve path, that path must not consume its own proposals.

## Correction carried in

The roadmap in [../roadmaps/PULSE_REFLECTION_ENGINE.md](../roadmaps/PULSE_REFLECTION_ENGINE.md)
specified embedding documents with `all-MiniLM-L6-v2` (384-dim) and comparing them
against sampled ChromaDB chunks. Those chunks are **768-dim**. That comparison would
not have been merely inaccurate — it would have been meaningless, and PULSE would
have drawn confident staleness conclusions from noise. Corrected there; noted here
because it is the shape of mistake this design exists to catch.

## Open questions

- **Who approves when Jonathan is away?** Probably nobody, and the queue simply
  grows. That is the correct default.
- **Do proposals expire?** A stale proposal referencing a file that has since changed
  should be invalidated rather than applied against drifted state.
- **How is confidence calibrated?** Until there is a track record, treat it as
  ordering only — never as an auto-approve threshold.
