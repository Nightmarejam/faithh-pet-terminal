# Vector store review

**2026-07-29** · measured against the live Chroma on `servicebox:8000`.
Companion to [FAITHH_REDESIGN.md](FAITHH_REDESIGN.md) and
[CHIP_SYSTEM_RECONCILIATION.md](CHIP_SYSTEM_RECONCILIATION.md).

## Inventory

| collection | docs | dim | space | status |
|---|---:|---:|---|---|
| `alife_lineage` | 339,900 | 384 | l2 | **wrong tool** — see below |
| `faithh_knowledge_base_v2` | 58,386 | **768** | l2 | ✅ current |
| `faithh_knowledge_base` | 56,066 | 384 | cosine | legacy |
| `governance_corpus` | 18,768 | 384 | l2 | stranded |
| `faithh_uncertainty_surface` | 175 | 384 | l2 | stranded |
| `faithh_session_metrics` | 59 | 384 | l2 | operational |
| `tomcat_sound_kb` | 0 | — | l2 | empty |
| `fgs_research_kb` | 0 | — | l2 | empty |
| **total** | **473,354** | | | 15 GB on disk |

Disk is not a constraint: 88 GB used of 916 GB (11%). **Nothing here needs to be
deleted to reclaim space.** Any change should be justified by retrieval quality,
not capacity.

## The structural finding

**Exactly one collection is 768-dim.** The live embedder is BGE-base-en-v1.5
(768); every other collection was written by all-MiniLM-L6-v2 (384).

That makes any cross-collection blend a dimension mismatch *by construction*.
It is not a bug in one code path — it is the shape of the store. The observed
error

```
❌ Error in ALIFE query: Collection expecting embedding with dimension of 384, got 768
```

comes from `faithh_professional_backend_fixed.py:1553`, which blends
`alife_lineage` into knowledge-base results for ALife queries. `governance_corpus`
would fail identically if anything blended it.

## `alife_lineage` is tabular data in a vector store

339,900 documents, 72% of everything. Content is one templated sentence per
agent, per tick:

```
Agent agent_51 at generation 1 reproduced at tick 4. Its genome expresses sense density …
Band2 agent B_00 pop=B tick=11: signal=0.49 resources=1.37 coop=37 defect=3 fitness=0.873
```

Full scan of all 339,900 by `event_type`:

| event_type | count | share |
|---|---:|---:|
| *(none — `band2_cooperation` records)* | 289,450 | 85.16% |
| `death_predator` | 41,798 | 12.30% |
| `reproduction` | 3,749 | 1.10% |
| `shield_activation` | 1,925 | 0.57% |
| `thermal_death` | 1,630 | 0.48% |
| `gap_snapshot` | 399 | 0.12% |
| `population_snapshot` | 376 | 0.11% |
| `trait_frequency_snapshot` | 366 | 0.11% |
| `flag_novel_genome` | 158 | 0.05% |
| `strategy_snapshot` | 47 | 0.01% |
| `flag_intent` | 2 | 0.00% |

**Snapshots + flags: 1,348 (0.40%). Per-tick fossil: 338,552 (99.60%).**

The 85% with no `event_type` are not metadata-less — they carry rich numeric
fields (`fitness`, `resources`, `cooperation_count`, `defection_count`,
`signal_strength`, `generation`, `tick`, `noise_amp`, `randomness_source`).

That is the whole point: **these are rows, not documents.** The real questions
about them are `fitness > 0.8`, `generation = 10`, `population = 'B'`,
`GROUP BY noise_amp` — filters and aggregates. Cosine similarity over 340k
near-identical templated sentences cannot discriminate; the embeddings are
crowded into a tiny region of the space by construction, so a query matches
everything and therefore nothing. Embedding this data does not make it
searchable, it makes it expensive.

## Recommendation

Ordered by risk. Nothing here is urgent — the system is healthy and disk is fine.

### 1. Drop the two empty collections — zero risk

`tomcat_sound_kb` and `fgs_research_kb` hold 0 documents. They only add noise to
every inventory.

### 2. Move `alife_lineage` to the right store — the real win

Export all 339,900 records with their metadata to **SQLite or Parquet**, where the
numeric queries they actually support are cheap and exact. Then keep only the
**1,348 snapshots and flags** in Chroma, re-embedded at 768-dim.

This is not data loss — it is moving data to a store that can answer questions
about it. It also *fixes* the ALife blend rather than working around it: a 768-dim
`alife_lineage` blends with `faithh_knowledge_base_v2` correctly.

Effect: Chroma drops from 473k to ~135k documents, and the one path that
currently throws starts working.

### 3. Decide on `faithh_knowledge_base` (legacy, 384)

Previously established as ~86% covered by the v2 ingests, with the ~34 remaining
"unique" titles being stale indexed docs (`AGENTS.md`, `README.md`). Retire once
that is re-confirmed.

### 4. Re-embed `governance_corpus` if it should participate

18,768 docs at 384-dim. Either bring it to 768 so it can be blended, or accept it
as offline archive. Right now it is neither — reachable but unusable.

## Re-indexing without getting bitten

`scripts/ingest/reindex_collection.py` already established the safe pattern, and
it is the only pattern to use:

1. **Write to a new collection.** Never mutate in place, never delete first.
2. **Prefix the ids** (`reidx_{source}_{id}`) so a partial run is idempotent and
   re-runnable.
3. **Verify before switching**: counts match, `peek()` shows 768-dim, and a known
   query returns a sane `best_distance` (not 1.0 — see below).
4. **Flip `CHROMA_COLLECTION`** in the service environment. That is the cutover,
   and it is one line to revert.
5. **Keep the old collection** until a few days of real queries have passed. Disk
   is not the constraint.

The failure mode to watch for is the documented one: `best_distance` of exactly
1.0 on every query. Note it can mean *either* a dimension mismatch *or* distances
being dropped in code — both have now been seen in this system.

## Chip system: not the problem

Worth stating plainly, because it looked implicated. ML chip centroids load as
**(15, 768)** — correctly aligned with `faithh_knowledge_base_v2` and BGE. The
chips are fine.

Coherence convergence still reports `signal_strength_only` for one narrow reason:
**RAG hit embeddings are not passed to the arbiter.** `query_collection` already
fetches them (`include=[..., "embeddings"]`), and `_extract_chip_embeddings` now
resolves chip centroids correctly, so chip embeddings arrive. The RAG half does
not, so `_calculate_convergence_matrix` never runs.

The reason they were not simply added to `rag_results` is that
`rag_processor.normalize_rag_hit_for_api` does `out = dict(entry)` and passes
every key through to the JSON response — numpy arrays there would break `jsonify`
on every chat. The fix is to pass embeddings to `measure_convergence` as a
separate argument, alongside `rag_results` rather than inside it.
