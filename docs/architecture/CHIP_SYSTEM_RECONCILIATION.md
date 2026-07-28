# Chip system reconciliation

**Status:** analysis + decision · **2026-07-28**
Follows from [COMPONENT_INDEX.md](COMPONENT_INDEX.md) showing `parallel_chip_engine`
unreferenced while `enhanced_chip_integration` runs in production.

## The situation

Two modules implement parts of the same design. `enhanced_chip_integration.py`
(702 lines) is imported by the canonical backend; `parallel_chip_engine.py`
(774 lines) is imported by nothing.

The first assumption — that one is a stale duplicate of the other — is wrong.
They are **complementary halves of one architecture that were never connected**,
with a single genuinely duplicated function between them.

## What each actually owns

| | `parallel_chip_engine` (orphaned) | `enhanced_chip_integration` (live) |
|---|---|---|
| Retrieval | **`ChipRetriever`** — `retrieve_rag_search`, `retrieve_scaffolding`, `retrieve_decision_logs` | none |
| Parallelism | **`ThreadPoolExecutor`, used** | imports it, **never calls it** (dead import) |
| Types | **`ChipResult`, `QueryMetrics`** dataclasses | plain tuples and dicts |
| Token budget | **`count_tokens`, `classify_query_type`, `allocate_token_budget`** | none |
| Fusion | `ParallelChipEngine.weighted_rrf_fusion(Dict[str, ChipResult]) -> Dict` | `weighted_rrf_fusion(Dict[str, Tuple[str,str]]) -> str` |
| Program Advance | none | **`detect_program_advance`, `_hybrid`, `PROGRAM_ADVANCES`** |
| Merge strategies | none | **timeline_priority, evidence_chain, comprehensive, business_focus, default** |

The backend imports exactly seven names, all from the live module:
`detect_program_advance`, `detect_program_advance_hybrid`, `get_pa_chips_for_query`,
`build_enhanced_context`, `apply_merge_strategy`, `weighted_rrf_fusion`,
`PROGRAM_ADVANCES`.

## The one real duplication, and why it matters

Both define `weighted_rrf_fusion`, but over **different data**:

- **orphaned version** ranks `ChipResult` objects, which carry scores and ranks.
  Reciprocal Rank Fusion is defined over ranks: `score = Σ wᵢ / (k + rankᵢ)`.
- **live version** takes `Dict[str, Tuple[str, str]]` — chip name to
  *(context string, chip type)*. There are no ranks in a string.

So the production path is doing RRF over data that has already been flattened to
prose. Whatever it computes, **it is not reciprocal rank fusion** in the sense the
design intended — the ranks were discarded upstream, in the monolith, before the
fusion function ever sees them.

This is the substantive finding. It is not a tidiness problem; the retrieval
quality claim in `CHIP_SYNERGY.md` rests on a fusion that the running system is
not actually performing.

## Decision

**Do not merge the modules, and do not delete either one.** Neither is redundant.
The correct end state, consistent with the capability layer in
[FAITHH_REDESIGN.md](FAITHH_REDESIGN.md):

1. **`parallel_chip_engine` becomes the retrieval layer.** It already has the
   right shape — typed results, real parallelism, token budgeting. Retrieval
   currently living in the 6,725-line monolith moves here.
2. **`enhanced_chip_integration` keeps Program Advance and merge strategies.**
   That logic is genuinely its own and is working in production.
3. **One fusion implementation survives — the typed one**, operating on
   `ChipResult` before anything is flattened to a string. The string-based
   version is deleted once callers pass typed results.
4. **`build_enhanced_context` becomes the seam** between them: retrieval returns
   `ChipResult`s, fusion ranks them, merge strategies render the result.

## Why not do it now

The fusion change alters what the backend sends to the model on every request.
That is a behavioural change to the live system, and it should land with a
before/after comparison rather than as part of a cleanup pass — the Coherence
Arbiter's convergence scores are the obvious measure, since they exist precisely
to detect whether retrieval signals agree.

Sequence when it is picked up:
1. Add a test that captures current fused output for a fixed query set.
2. Thread `ChipResult` through the monolith's retrieval calls without changing fusion.
3. Switch to the typed fusion; compare Coherence Arbiter scores against the baseline.
4. Delete the string-based `weighted_rrf_fusion` and the dead `ThreadPoolExecutor`
   import from `enhanced_chip_integration`.

## Immediate, safe cleanup

- Remove the unused `ThreadPoolExecutor, as_completed` import from
  `enhanced_chip_integration.py` — it advertises parallelism the module does not do.
- Leave `parallel_chip_engine.py` in place, documented as the retrieval layer
  pending wiring, **not** as an archive candidate. The component index lists it
  as unreferenced, which is true and now explained.
