# Claude Code Handoff: FAITHH Backend Bug Fixes

**Created**: 2025-12-30 ~10:25 PM
**Status**: Two bugs need fixing before Phase 2

---

## Session Context

FAITHH backend is running and functional but has two bugs introduced during Codex session. System is otherwise working: Ollama connected, ChromaDB connected (27,568 docs), RAG queries working.

---

## 🐛 Bug 1: Status Endpoint URL Malformation (Cosmetic)

**Priority**: Low (cosmetic only)
**File**: `/Users/macjohn/ai-stack/faithh_professional_backend_fixed.py`

### Problem
The `/api/status` endpoint shows malformed ChromaDB URL:
```json
"host": "http://http://192.158.1.243:8000:8000"
```

### Root Cause
Around line ~1262, Codex added:
```python
chroma_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}"
```

But `CHROMA_HOST` already contains `http://192.158.1.243` from env parsing earlier in the file (likely around lines 100-200).

### Fix
Search for where `chroma_url` is constructed in the `/api/status` endpoint and replace with:
```python
if CHROMA_HOST.startswith("http"):
    chroma_url = f"{CHROMA_HOST}:{CHROMA_PORT}"
else:
    chroma_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}"
```

### Test
```bash
curl -s http://localhost:5557/api/status | jq '.services.chromadb.host'
# Should return: "http://192.158.1.243:8000"
# NOT: "http://http://192.158.1.243:8000:8000"
```

---

## 🐛 Bug 2: Auto-Indexer Embedding Dimension Mismatch (Functional)

**Priority**: High (breaks conversation indexing)
**File**: `/Users/macjohn/ai-stack/faithh_professional_backend_fixed.py`

### Problem
Auto-indexing conversations to ChromaDB fails with:
```
❌ Index failed: Collection expecting embedding with dimension of 768, got 384
```

This appears every time a message is sent.

### Root Cause
The auto-indexer (`index_conversation_background` function) uses a different embedding model than the collection:
- **Collection**: Uses `bge-base-en-v1.5` (768-dimensional embeddings)
- **Auto-indexer**: Likely uses `all-MiniLM-L6-v2` (384-dimensional embeddings)

### Investigation Steps
1. Search for `index_conversation_background` function
2. Search for `def index_conversation` or similar
3. Look for where embeddings are generated for indexing
4. Check if it uses `query_embedder` (correct, 768-dim) or a different embedder (wrong, 384-dim)

### Expected Fix
The indexer should use the same `query_embedder` that's used for RAG queries. Look for something like:

**Current (broken)**:
```python
# Probably using sentence_transformers default model
embeddings = some_other_embedder.encode(text)
```

**Should be**:
```python
# Use the BGE embedder that's already loaded
embeddings = query_embedder.encode(text)
```

### Where to Look
- Search for `SentenceTransformer` - there should be only ONE instance loaded (BGE)
- Search for `all-MiniLM` - if found, this is the problem
- Search for `384` in comments or dimension checks
- The auto-indexer is likely in a background thread or async function

### Test
```bash
# Send a test message
curl -s -X POST http://localhost:5557/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Test indexing", "use_rag": false, "model": "llama3.1:8b"}'

# Check logs - should show success
tail -20 /Users/macjohn/ai-stack/faithh.log

# Should see: ✅ Indexed conversation (or similar success message)
# Should NOT see: ❌ Index failed: Collection expecting embedding with dimension of 768, got 384
```

---

## 📊 Current System State

| Component | Status | Details |
|-----------|--------|---------|
| Backend | ✅ Running | localhost:5557, v3.4 |
| Ollama | ✅ Connected | llama3.1:8b, llama3.2:3b |
| ChromaDB | ✅ Connected | 192.158.1.243:8000 |
| Collection | ✅ Working | faithh_knowledge_base, 27,568 docs |
| Query Embedder | ✅ Correct | BGE-base-en-v1.5 (768-dim) |
| RAG Queries | ✅ Working | Using 768-dim embeddings |
| Auto-indexing | ❌ Broken | Using 384-dim embeddings (mismatch) |
| Status Endpoint | ⚠️ Cosmetic Bug | URL shows double http:// |

---

## 🚫 Do NOT Do

- Don't modify `.env` - correctly configured
- Don't clear ChromaDB - 27,568 docs indexed
- Don't change the query embedder (BGE-base-en-v1.5) - it's correct
- Don't restart backend until both fixes are applied
- Don't add a new embedder - fix the existing one to use BGE

---

## 📁 Key Files

- **Backend**: `/Users/macjohn/ai-stack/faithh_professional_backend_fixed.py`
- **Env**: `/Users/macjohn/ai-stack/.env` (reference only - don't modify)
- **Logs**: `/Users/macjohn/ai-stack/faithh.log`
- **Restart Script**: `/Users/macjohn/ai-stack/restart_backend.sh`

---

## 🔍 Files Modified by Codex (for context)

These were changed in the last session - useful context for debugging:
- `faithh_professional_backend_fixed.py` - env-driven config, better error handling
- `restart_backend.sh` - venv-safe, health-based checks
- `filesystem_agent.py` - added metadata action
- `filesystem_chip.py` - metadata handler, limit support
- `scripts/faithh_fs_cli.py` - aligned with backend endpoints

---

## ✅ Success Criteria

1. [ ] Status endpoint shows correct ChromaDB URL (no double http://)
2. [ ] Auto-indexing completes without dimension mismatch errors
3. [ ] Test message successfully indexes to ChromaDB
4. [ ] Backend logs show no embedding errors

---

## 🚀 After Fixes

Once both bugs are fixed, the system is ready for **Phase 2** implementation (parallel chip retrieval with ThreadPoolExecutor).

Research docs available:
- `/Users/macjohn/ai-stack/docs/CHIP_SYNERGY_RESEARCH_FINDINGS.md`
- `/Users/macjohn/ai-stack/docs/CHIP_SYNERGY_RESEARCH_SUPPLEMENT.md`

---

*Handoff created - Dec 30, 2025 ~10:25 PM*
