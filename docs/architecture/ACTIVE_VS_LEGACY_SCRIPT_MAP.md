> **Superseded 2026-07-28** by [COMPONENT_INDEX.md](COMPONENT_INDEX.md), which is
> generated from the source and covers all 85 modules. This one was hand-written,
> partial, and had drifted. Kept for history.

---

# Active vs Legacy Script Map

Last updated: 2026-03-30

## Purpose

Keep `scripts/` maintainable by separating active operational scripts from legacy or one-off helpers.

## Active (operational)

- `scripts/index_alife_core.py`
- `scripts/index_constella_constitutional.py`
- `scripts/index_claude_memories.py`
- `scripts/audit_chroma_health.py`
- `scripts/normalize_high_signal_document_types.py`

These are part of the current indexing + audit workflow.

## Active (targeted/manual)

- `scripts/index_exp5_results.py`
- `scripts/index_exp6_results.py`
- `scripts/index_exp7_results.py`
- `scripts/index_exp8b_results.py`
- `scripts/index_alife_findings.py`
- `scripts/index_alife_results.py`
- `scripts/index_alife_bottomup.py`

Use these only for focused re-index tasks or historical backfills.

## Legacy removed

- `scripts/index_chromadb_direct.py` (removed)
- `scripts/index_to_chromadb.py` (removed)

Reason: relied on missing legacy path
`/home/jonat/ai-stack/knowledge_base/extracted/conversations_for_chromadb.json`
and duplicated modern index flows.

## Archived debug/test scripts

Moved from root `scripts/` to:

- `scripts/archive/debug_2026_03_30/`

This keeps active operational scripts discoverable and reduces accidental execution of stale diagnostics.
