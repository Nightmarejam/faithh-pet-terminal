# Claude Code Handoff: Parallel Chip Retrieval

**Created**: 2025-12-31 ~11:15 PM
**Goal**: Implement ThreadPoolExecutor for parallel chip retrieval
**Time Budget**: 30-45 minutes

---

## Current State

`build_integrated_context()` at line 736 retrieves chips sequentially.
All chips work, but RAG is the bottleneck (~1-2s).

## Implementation

### Step 1: Add ThreadPoolExecutor import and global (top of file, ~line 30)
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Global executor for parallel chip retrieval (5 workers = max concurrent chips)
CHIP_EXECUTOR = ThreadPoolExecutor(max_workers=5, thread_name_prefix="chip_")
```

### Step 2: Create individual chip retrieval functions (before build_integrated_context)
```python
def retrieve_conversation_history(session_id):
    """Chip: Conversation History"""
    if not session_id or session_id not in conversation_sessions:
        return None, 'conversation_history'
    history = conversation_sessions[session_id]["history"]
    if not history:
        return None, 'conversation_history'
    history_text = format_conversation_history(history, last_n=5)
    if history_text:
        return f"\n=== RECENT CONVERSATION ===\n{history_text}\n============================\n", 'conversation_history'
    return None, 'conversation_history'

def retrieve_self_awareness(intent):
    """Chip: Self-Awareness"""
    if not intent.get('is_self_query'):
        return None, 'self_awareness'
    context = get_self_awareness_context()
    return context, 'self_awareness' if context else None

def retrieve_constella(intent):
    """Chip: Constella Framework"""
    if not intent.get('is_constella_query'):
        return None, 'constella'
    context = get_constella_awareness_context()
    return context, 'constella' if context else None

def retrieve_decisions(query_text, intent):
    """Chip: Decision Log Search"""
    if not intent.get('is_why_question'):
        return None, 'decisions'
    context = search_decisions_log(query_text)
    return context, 'decisions' if context else None

def retrieve_project_state(query_text, intent):
    """Chip: Project State"""
    if not intent.get('is_next_action_query'):
        return None, 'project_state'
    project_name = None
    if 'faithh' in query_text.lower():
        project_name = 'faithh'
    elif 'constella' in query_text.lower():
        project_name = 'constella'
    context = get_project_state_context(project_name)
    return context, 'project_state' if context else None

def retrieve_scaffolding(query_text, intent):
    """Chip: Scaffolding"""
    if not (intent.get('needs_orientation') or intent.get('is_next_action_query')):
        return None, 'scaffolding'
    context = get_scaffolding_context(query_text)
    return context, 'scaffolding' if context else None

def retrieve_rag(query_text, intent, use_rag):
    """Chip: RAG Search (slowest - benefits most from parallelization)"""
    if not use_rag or not CHROMA_CONNECTED or intent.get('is_self_query'):
        return None, [], 'rag_search'
    
    if intent.get('needs_orientation') and not intent.get('is_constella_query') and not intent.get('is_business_query'):
        return None, [], 'rag_search'
    
    try:
        results = smart_rag_query(query_text, n_results=5, intent=intent)
        if results and results['documents'] and results['documents'][0]:
            rag_context = "\n=== KNOWLEDGE BASE ===\n"
            rag_results = []
            for i, doc in enumerate(results['documents'][0][:3]):
                rag_context += f"{i+1}. {doc[:1000]}...\n\n"
                rag_results.append(doc[:500])
            rag_context += "=====================\n"
            return rag_context.strip(), rag_results, 'rag_search'
    except Exception as e:
        print(f"   ⚠️ RAG query failed: {e}")
    return None, [], 'rag_search'
```

### Step 3: Replace build_integrated_context with parallel version
```python
def build_integrated_context(query_text, intent, use_rag=True, session_id=None):
    """
    Build context from all available sources based on query intent
    NOW WITH PARALLEL CHIP RETRIEVAL! (Phase 2)
    """
    start_time = time.time()
    context_parts = []
    integrations_used = []
    rag_results = []
    
    # Submit all chip retrievals in parallel
    futures = {}
    
    # Fast chips (file I/O)
    futures[CHIP_EXECUTOR.submit(retrieve_conversation_history, session_id)] = 'history'
    futures[CHIP_EXECUTOR.submit(retrieve_self_awareness, intent)] = 'self'
    futures[CHIP_EXECUTOR.submit(retrieve_constella, intent)] = 'constella'
    futures[CHIP_EXECUTOR.submit(retrieve_decisions, query_text, intent)] = 'decisions'
    futures[CHIP_EXECUTOR.submit(retrieve_project_state, query_text, intent)] = 'project'
    futures[CHIP_EXECUTOR.submit(retrieve_scaffolding, query_text, intent)] = 'scaffolding'
    
    # Slow chip (network I/O) - benefits most from parallelization
    futures[CHIP_EXECUTOR.submit(retrieve_rag, query_text, intent, use_rag)] = 'rag'
    
    # Collect results as they complete (with 10s timeout)
    chip_results = {}
    for future in as_completed(futures, timeout=10.0):
        chip_name = futures[future]
        try:
            result = future.result()
            chip_results[chip_name] = result
        except Exception as e:
            print(f"   ⚠️ Chip {chip_name} failed: {e}")
            chip_results[chip_name] = None
    
    # Process results in priority order (for consistent output)
    priority_order = ['history', 'self', 'constella', 'decisions', 'project', 'scaffolding', 'rag']
    
    for chip in priority_order:
        result = chip_results.get(chip)
        if result is None:
            continue
            
        if chip == 'rag':
            context, rag_docs, chip_type = result
            if context:
                context_parts.append(context)
                rag_results = rag_docs
                integrations_used.append('rag_search')
                print(f"   ✅ Added RAG context ({len(rag_docs)} results)")
        else:
            context, chip_type = result
            if context:
                context_parts.append(context)
                if chip_type:
                    integrations_used.append(chip_type)
                print(f"   ✅ Added {chip} context")
    
    # RAG Fallback (only if RAG didn't fire)
    if use_rag and CHROMA_CONNECTED and 'rag_search' not in integrations_used:
        if not intent.get('needs_orientation'):
            print("   🔄 RAG fallback - no specific chip triggered")
            try:
                fallback_results = query_collection(query_text, n_results=3)
                if fallback_results and fallback_results.get('documents') and fallback_results['documents'][0]:
                    rag_results = fallback_results['documents'][0]
                    integrations_used.append('rag_search_fallback')
                    print(f"   ✅ RAG fallback found {len(rag_results)} results")
                    rag_context = "\n=== KNOWLEDGE BASE ===\n"
                    for i, doc in enumerate(rag_results[:3]):
                        rag_context += f"{i+1}. {doc[:1000]}...\n\n"
                    rag_context += "=====================\n"
                    context_parts.append(rag_context.strip())
            except Exception as e:
                print(f"   ⚠️ RAG fallback error: {e}")
    
    # Combine all context
    full_context = "\n\n".join(context_parts) if context_parts else ""
    
    elapsed = time.time() - start_time
    print(f"   ⏱️ Parallel chip retrieval: {elapsed:.3f}s")
    
    return full_context, rag_results, integrations_used
```

---

## Test Commands
```bash
# Restart backend
pkill -f faithh_professional && cd ~/ai-stack && ./venv/bin/python faithh_professional_backend_fixed.py &

# Wait for startup
sleep 10

# Test and check timing
curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is FAITHH and what should I work on next?", "model": "llama3.1:8b"}' | jq -r '.response_time'

# Check logs for parallel timing
tail -20 ~/ai-stack/backend.log | grep "Parallel chip"
```

## Success Criteria

1. [ ] Backend starts without errors
2. [ ] Chat endpoint still works
3. [ ] Logs show "⏱️ Parallel chip retrieval: X.XXXs"
4. [ ] Multiple chips fire on complex queries
5. [ ] Response time improved (target: <2s for chip retrieval)

---

## Key Files

- **Backend**: `/Users/macjohn/ai-stack/faithh_professional_backend_fixed.py`
- **Research**: `/Users/macjohn/ai-stack/docs/CHIP_SYNERGY_RESEARCH_SUPPLEMENT.md`

---

*Handoff created - Dec 31, 2025 ~11:15 PM PST*
