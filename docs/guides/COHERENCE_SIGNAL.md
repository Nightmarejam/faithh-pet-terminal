# Coherence Signal (Phase 3)

**Last updated:** 2026-02-23

The FAITHH UI shows a **coherence indicator** on each assistant reply. This reflects how aligned the response is with FAITHH’s own knowledge base and canonical state, not whether the answer is “correct” in an absolute sense.

## What the indicator shows

- **Coherence: high** — Strong alignment between RAG retrieval and ML chip routing; anchor validation (when run) passed. Good confidence that the answer is grounded in FAITHH’s indexed knowledge and state.
- **Coherence: medium** — Moderate alignment or mixed signals. Response may still be useful; consider checking important details against sources.
- **Coherence: low** — Weak alignment or anchor validation failed. The system is less sure; verify important claims.

Tooltip text: *“How aligned this response is with FAITHH’s own knowledge base and anchors.”*

## Low-coherence hint

When coherence is low (or anchor validation is enabled but failed), a short advisory line appears below the reply:

> **FAITHH is less sure about this answer – consider verifying details.**

This is advisory only. It does not change the model’s reply or block the response. Use it to decide when to double-check against docs or state files.

## When anchor validation runs

Anchor validation (ground truth checks against `project_states.json`, ML chips, ChromaDB, PULSE) only runs when the response used **document-based RAG** (full convergence calculation). For **conversation-based RAG** (e.g. focused project queries), you may see a coherence tier from signal strength only and no anchor score; that is expected.

## Technical details

- Metadata is in the chat API response under `coherence`: `tier`, `reasons`, `low_confidence`, `suggested_behavior`.
- Thresholds and behavior are documented in `docs/architecture/SYSTEM_OVERVIEW.md` (Coherence Arbiter section) and implemented in `backend/coherence_arbiter.py` and `backend/anchor_validator.py`.
