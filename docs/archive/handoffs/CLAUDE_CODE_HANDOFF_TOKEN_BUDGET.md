# Claude Code Handoff: Token Budget Allocation

**Created**: 2025-12-31 ~11:50 PM
**Goal**: Add token budgeting to prevent context overflow
**Time Budget**: 10 minutes

---

## Implementation

### Step 1: Add token utilities (after CHIP_EXECUTOR, ~line 52)
```python
# Token budget configuration (4,500 total for chips with 8k context)
CHIP_TOKEN_BUDGETS = {
    'rag_search': 1800,      # 40% - Primary knowledge
    'scaffolding': 900,      # 20% - Project context
    'decisions': 675,        # 15% - Decision history
    'project_state': 450,    # 10% - Structured state
    'constella': 450,        # 10% - Framework
    'self_awareness': 450,   # 10% - Identity
    'conversation_history': 225,  # 5% - Recent turns
}

def count_tokens(text: str) -> int:
    """Rough token count (avg 4 chars per token)"""
    if not text:
        return 0
    return len(text) // 4

def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Truncate text to fit within token budget"""
    if not text:
        return text
    current_tokens = count_tokens(text)
    if current_tokens <= max_tokens:
        return text
    # Truncate to approximate character limit
    max_chars = max_tokens * 4
    truncated = text[:max_chars]
    # Try to end at a sentence or newline
    last_break = max(truncated.rfind('\n'), truncated.rfind('. '))
    if last_break > max_chars * 0.8:  # Only if we keep 80%+
        truncated = truncated[:last_break + 1]
    return truncated + "\n[...truncated for context limit...]"
```

### Step 2: Apply budgets in build_integrated_context (in the priority_order loop)

Find this section (~line 857-875):
```python
for chip in priority_order:
    result = chip_results.get(chip)
    if result is None:
        continue
```

Replace with:
```python
for chip in priority_order:
    result = chip_results.get(chip)
    if result is None:
        continue
    
    # Get budget for this chip type
    chip_type_for_budget = chip if chip != 'self' else 'self_awareness'
    chip_type_for_budget = chip_type_for_budget if chip_type_for_budget != 'history' else 'conversation_history'
    max_tokens = CHIP_TOKEN_BUDGETS.get(chip_type_for_budget, 500)
        
    if chip == 'rag':
        context, rag_docs, chip_type = result
        if context:
            context = truncate_to_budget(context, max_tokens)
            context_parts.append(context)
            rag_results = rag_docs
            integrations_used.append('rag_search')
            print(f"   ✅ Added RAG context ({len(rag_docs)} results, {count_tokens(context)} tokens)")
    else:
        context, chip_type = result
        if context:
            context = truncate_to_budget(context, max_tokens)
            context_parts.append(context)
            if chip_type:
                integrations_used.append(chip_type)
            print(f"   ✅ Added {chip} context ({count_tokens(context)} tokens)")
```

### Step 3: Log total context tokens (before return)

Find:
```python
elapsed = time.time() - start_time
print(f"   ⏱️ Parallel chip retrieval: {elapsed:.3f}s")
```

Add after:
```python
total_tokens = count_tokens(full_context)
print(f"   📊 Total context: {total_tokens} tokens")
```

---

## Test
```bash
curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is FAITHH?", "model": "llama3.1:8b"}' | jq -r '.response_time'

# Check logs for token counts
tail -30 ~/ai-stack/backend.log | grep -E "tokens|Parallel"
```

## Success Criteria

1. [ ] Logs show token counts per chip
2. [ ] Logs show total context tokens
3. [ ] No context overflow errors
4. [ ] Chat still works

---
