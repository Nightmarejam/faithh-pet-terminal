# Retrieval Filter Profile

Last updated: 2026-03-30

## Goals

- Increase precision for governance and ALife reasoning queries.
- Prioritize high-signal indexed documents over noisy historical conversation text.
- Preserve lineage/deep telemetry access when explicitly requested.

## Governance query profile

Entry point: `smart_rag_query()`

Order:
1. `domain=constella_constitutional` (constitutional principles + mapping sections)
2. ALife fallback via `query_alife_collection()`
3. Strict fallback limited to:
   - `domain=constella_constitutional`
   - `domain=alife` + `source_type in {alife_experiment, synthesis_document, alife_cross_experiment_pattern}`

Broad/dev conversation fallback is disabled for governance queries.

Design notes:
- Constella master docs remain available for non-governance framework questions.
- Governance questions are intentionally routed through constitutional evidence first.

## ALife query profile

Entry point: `query_alife_collection()`

Default behavior (non-lineage query):
- Query and merge high-signal ALife sources from `faithh_knowledge_base_v2`:
  (ALife telemetry itself now lives in SQLite, not Chroma — see VECTOR_STORE_REVIEW.md)
  - `domain=alife AND source_type=alife_experiment`
  - `domain=alife AND source_type=synthesis_document`
  - `domain=alife AND source_type=alife_cross_experiment_pattern`
- Rerank merged results and return top N.

Lineage-specialized behavior:
- If query includes lineage telemetry terms (`lineage`, `genome`, `agent`, `tick`, `generation`, `hex`, `mutation`),
  lineage retrieval remains primary using `alife_lineage` collection.

## Metadata normalization profile

To improve filter and explanation consistency:
- Normalize missing `document_type` only for high-signal domains:
  - `alife`
  - `constella_constitutional`
  - `faithh_core`

Script:
- `scripts/normalize_high_signal_document_types.py`

This avoids bulk mutation of low-signal historical imports while cleaning targeted research/governance metadata.
