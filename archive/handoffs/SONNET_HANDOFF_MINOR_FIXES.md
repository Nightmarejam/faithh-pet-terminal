# Sonnet Handoff: Minor Fixes
**Created**: 2025-12-02 by Opus 4.5  
**Priority**: Minor cleanup tasks  
**Estimated Time**: 30-45 minutes total

---

## Context

Jonathan just completed a major repository cleanup with Opus. FAITHH is at v3.3-scaffolding with 93,606 indexed documents. The system is stable and ready for testing. These are small fixes to clean up before Jonathan starts daily testing.

---

## Task 1: Fix Indexing Script Display Bug
**File**: `scripts/indexing/index_recent_docs.py`  
**Time**: 5 minutes  
**Priority**: Low (cosmetic)

### Problem
Line ~200 throws `KeyError: 'source'` at the end of the script:
```python
print(f"   Top result: {results['metadatas'][0][0]['source']}")
```

The metadata key might not always be 'source' depending on what was indexed.

### Fix
Wrap in try/except or check key exists:
```python
try:
    if results['metadatas'] and results['metadatas'][0]:
        meta = results['metadatas'][0][0]
        source = meta.get('source', meta.get('filename', 'unknown'))
        print(f"   Top result: {source}")
except (IndexError, KeyError):
    print(f"   Top result: (metadata unavailable)")
```

### Test
```bash
cd ~/ai-stack && source venv/bin/activate
python scripts/indexing/index_recent_docs.py
# Should complete without error
```

---

## Task 2: Update Backend to Return integrations_used
**File**: `faithh_professional_backend_fixed.py`  
**Time**: 20-30 minutes  
**Priority**: Medium (improves testing visibility)

### Problem
The UI (faithh_pet_v4.html) expects the backend to return which integrations fired:
```javascript
// UI expects this in response:
// data.integrations_used = ["rag_search", "constella", "scaffolding"]
```

Currently the backend doesn't return this, so the UI just shows "RAG Search" as a fallback.

### What to Track
The `build_integrated_context()` function already knows what fired. We need to:
1. Track which integrations were used
2. Return them in the API response

### Implementation

In `build_integrated_context()` (around line 500-600), add tracking:

```python
def build_integrated_context(query_text, intent, use_rag=True):
    """Build context from all available integrations"""
    context_parts = []
    integrations_used = []  # ADD THIS
    
    # Integration 1: Self-awareness
    if intent.get('is_self_query'):
        memory = load_memory()
        if memory:
            context_parts.append(format_memory_context(memory))
            integrations_used.append('self_query')  # ADD THIS
    
    # Integration 2: Decision citation
    if intent.get('is_why_question'):
        decisions = load_decisions()
        if decisions:
            # ... existing code ...
            integrations_used.append('decisions')  # ADD THIS
    
    # Integration 3: Project state
    if intent.get('is_next_action_query'):
        # ... existing code ...
        integrations_used.append('scaffolding')  # ADD THIS
    
    # Integration 4: Scaffolding
    if intent.get('needs_orientation') or intent.get('is_next_action_query'):
        scaffolding_context = get_scaffolding_context(query_text)
        if scaffolding_context:
            context_parts.append(scaffolding_context)
            integrations_used.append('scaffolding')  # ADD THIS (if not already)
    
    # Integration 5: Constella
    if intent.get('is_constella_query'):
        # ... existing code ...
        integrations_used.append('constella')  # ADD THIS
    
    # Integration 6: RAG
    if use_rag and CHROMA_CONNECTED and not intent['is_self_query']:
        # ... existing code ...
        if rag_results:
            integrations_used.append('rag_search')  # ADD THIS
    
    # Return both context and integrations
    return "\n\n".join(context_parts), list(set(integrations_used))  # MODIFY RETURN
```

Then in the `/api/chat` endpoint, include integrations in response:

```python
@app.route('/api/chat', methods=['POST'])
def chat():
    # ... existing code ...
    
    # Build context
    context, integrations_used = build_integrated_context(message, intent, use_rag)  # MODIFY
    
    # ... existing LLM call ...
    
    return jsonify({
        'success': True,
        'response': response_text,
        'model': model,
        'integrations_used': integrations_used,  # ADD THIS
        'intent': {
            'patterns_matched': intent.get('patterns_matched', [])
        }
    })
```

### Test
```bash
# Restart backend
./restart_backend.sh

# Test with curl
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Constella?"}' | python3 -m json.tool

# Should see: "integrations_used": ["constella", "rag_search"]
```

---

## Task 3: Update README.md
**File**: `README.md`  
**Time**: 10 minutes  
**Priority**: Low

### Problem
Doc health check flagged README as 18 days old. It likely references old structure.

### What to Update
- Current version: v3.3-scaffolding
- Current doc count: 93,606
- Point to LIFE_MAP.md as the compass
- Point to START_HERE.md for onboarding
- Remove any references to old files

### Template
```markdown
# FAITHH - Friendly AI Teaching & Helping Hub

Personal thought partner and knowledge management system.

**Version**: v3.3-scaffolding  
**Documents Indexed**: 93,606+

## Quick Start

```bash
./restart_backend.sh
# Open http://localhost:5557
```

## Key Files

| Need | File |
|------|------|
| Direction & priorities | `LIFE_MAP.md` |
| Getting started | `START_HERE.md` |
| System architecture | `ARCHITECTURE.md` |
| Testing guide | `FAITHH_TESTING_GUIDE.md` |

## What FAITHH Does

- Maintains context across projects (FAITHH, Constella, FGS audio)
- Searches 93K+ indexed conversations and documents
- Tracks decisions and rationale
- Provides structural orientation ("Where was I?")

## Repository Structure

See `REPOSITORY_STRUCTURE.md` for full layout.

---

*Part of Jonathan's Celestial Equilibrium ecosystem*
```

---

## Task 4: Commit Changes
After completing tasks 1-3:

```bash
cd ~/ai-stack
git add -A
git commit -m "Minor fixes: indexing script, backend integrations_used, README update

- Fixed KeyError in index_recent_docs.py test output
- Backend now returns integrations_used array for UI chip display
- Updated README.md to reflect current state (v3.3, 93K docs)"
```

---

## Do NOT Do

- Don't restructure any files (cleanup is done)
- Don't modify the UI (faithh_pet_v4.html) - it already handles integrations_used
- Don't change ChromaDB or indexing logic (beyond the display fix)
- Don't start on MacBook setup (separate handoff coming)

---

## Files Reference

- Backend: `faithh_professional_backend_fixed.py`
- UI: `faithh_pet_v4.html`
- Indexing: `scripts/indexing/index_recent_docs.py`
- README: `README.md`

---

## Success Criteria

1. ✅ `python scripts/indexing/index_recent_docs.py` completes without error
2. ✅ `/api/chat` response includes `integrations_used` array
3. ✅ UI shows correct chips when asking Constella/scaffolding questions
4. ✅ README reflects current state
5. ✅ All changes committed to git

---

*Handoff created by Opus 4.5 - 2025-12-02*
