# Active Indexing Pipeline

Last updated: 2026-03-30

## Canonical collection

- `faithh_knowledge_base` on ChromaDB (`servicebox.taileb8c60.ts.net:8000`)

## Primary active indexers

- `scripts/index_alife_core.py`
  - Indexes core ALife experiment summaries (Exp 5/6/7/8b/9) and synthesis docs.
  - Tags with `domain=alife` and high-quality metadata.

- `scripts/index_constella_constitutional.py`
  - Indexes constitutional principles and evidence mapping from `projects/constella-framework`.
  - Tags with `domain=constella_constitutional`.

- `scripts/index_claude_memories.py`
  - Indexes high-signal Claude memory summaries.
  - Tags with `domain=faithh_core`, `source_type=claude_memory`.

## Supplemental/targeted indexers

- `scripts/index_exp5_results.py`
- `scripts/index_exp6_results.py`
- `scripts/index_exp7_results.py`
- `scripts/index_exp8b_results.py`
- `scripts/index_alife_findings.py`
- `scripts/index_alife_results.py`
- `scripts/index_alife_bottomup.py`

These are scenario-specific or historical and should be used selectively.

## Removed stale indexers (2026-03-30)

- `scripts/index_chromadb_direct.py`
- `scripts/index_to_chromadb.py`

Reason: both relied on legacy missing path
`/home/jonat/ai-stack/knowledge_base/extracted/conversations_for_chromadb.json`
and were superseded by active indexers above.

## Health check command

Run:

`python3 scripts/audit_chroma_health.py`

This prints:
- domain/source/document_type distributions
- critical counts (`alife`, `alife_experiment`, `constella_constitutional`, `faithh_core`)
- stale script presence check

## Operational quick runbook

Use this single command from repo root to execute the current audit loop:

`source venv/bin/activate && python3 scripts/audit_chroma_health.py`
