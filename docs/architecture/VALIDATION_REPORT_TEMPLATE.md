# Data Aggregation Validation Report Template

Date: YYYY-MM-DD  
Run ID: `<generated>`

## Scope

- Collection: `faithh_knowledge_base_v2`  <!-- template: keep in sync with CHROMA_COLLECTION -->
- Top-k: 5
- Query classes:
  - governance principle
  - ALife mechanism
  - Constella constitutional reasoning

## Retrieval quality snapshot

For each query class:
- total queries run
- median top distance
- source_type mix in top-k
- domain mix in top-k

## Drift vs previous baseline

- Baseline report: `<path>`
- Source-mix drift by class:
  - governance principle: `<diff>`
  - ALife mechanism: `<diff>`
  - Constella constitutional: `<diff>`

## Pass/Fail criteria

- Governance class includes `governance_source`, `constella_synthesis`, or `principle` documents in top-k.
- ALife class includes `alife_experiment`, `synthesis_document`, or `governance_seed_link` in top-k.
- Constella constitutional class includes `constella_constitutional` domain majority in top-k.
- No obvious drift toward `unknown` or low-signal source types.

## Actions

- [ ] Keep current retrieval profile
- [ ] Tighten filters for failing class(es)
- [ ] Re-index specific source lanes
- [ ] Re-run validation after fixes
