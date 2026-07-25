# FAITHH Phase 2 Implementation Checklist
## Session: December 30, 2025

### Pre-Implementation Status
- ✅ Backend running on localhost:5557
- ✅ ChromaDB connected (27,568 docs)
- ✅ RAG fallback implemented
- ✅ Business keywords working
- ✅ Research compiled (main + supplement)

---

## This Session: Parallel Retrieval + Token Budgeting

### Task 1: Add ThreadPoolExecutor for Parallel Chip Retrieval
**File**: `/Users/macjohn/ai-stack/faithh_professional_backend_fixed.py`

**Changes needed**:
1. Add import: `from concurrent.futures import ThreadPoolExecutor, as_completed`
2. Create global executor: `CHIP_EXECUTOR = ThreadPoolExecutor(max_workers=5)`
3. Refactor chip retrieval into parallelizable functions
4. Implement `parallel_chip_retrieval()` function

**Expected impact**: 3-5x latency reduction for multi-chip queries

### Task 2: Implement Token Budget Allocation
**Changes needed**:
1. Add `count_tokens()` utility function
2. Add `QUERY_TYPE_BUDGETS` configuration
3. Add `allocate_budget()` function
4. Add `enforce_budget()` to each chip's retrieval

**Default budgets** (8k context):
- Total chip context: 4,500 tokens
- rag_search: 40% (1,800)
- scaffolding: 20% (900)
- decision_logs: 15% (675)
- project_state: 10% (450)
- constella: 10% (450)

### Task 3: Add Basic Metrics Logging
**Changes needed**:
1. Add timing to each chip retrieval
2. Log chip latencies, tokens used
3. Store in faithh.log with structured format

---

## Testing Checklist

After implementation, test these queries:

| Query | Expected Chips | Success Criteria |
|-------|---------------|------------------|
| "What is Tom Cat Sound?" | rag_search | < 5s, business info returned |
| "What are you?" | self_awareness + rag_fallback | < 3s |
| "What's the Astris formula?" | constella | Constella content returned |
| "What projects am I working on?" | rag_search + scaffolding | Multiple chips, < 8s |
| "Summarize recent decisions" | decision_logs + rag | Parallel retrieval working |

---

## Files to Modify

1. **faithh_professional_backend_fixed.py** - Main changes
2. **faithh.log** - Verify structured logging

## Files Created This Session

1. `docs/CHIP_SYNERGY_RESEARCH_SUPPLEMENT.md` - Gap analysis research
2. `docs/PHASE2_IMPLEMENTATION_CHECKLIST.md` - This file

---

## Success Metrics

- [ ] Multi-chip queries complete in < 8 seconds
- [ ] Token budgets enforced (no context overflow)
- [ ] Chip latencies logged per request
- [ ] No regression on single-chip queries

---

## Rollback Plan

If issues arise:
1. Backend file has implicit backup in git
2. Can revert to sequential retrieval by commenting out ThreadPoolExecutor
3. Token budgeting is additive, can be disabled

---

*Ready to implement!*
