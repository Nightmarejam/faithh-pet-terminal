# Claude Code Handoff: Fix FAITHH Provider/Timeout Issues

**Created**: 2025-12-31 ~9:00 PM
**Priority**: HIGH - Get chat working again

---

## Current Problem

FAITHH UI shows "No response received" even though:
- ✅ Backend is running (localhost:5557)
- ✅ Ollama is running and responding (2.3s direct, 15s via backend)
- ✅ curl to backend works perfectly (returns full response in 15s)
- ❌ UI returns 502 almost instantly - frontend timeout too short

**Evidence from logs:**
```
INFO:werkzeug:127.0.0.1 - - [31/Dec/2025 21:55:00] "POST /api/chat HTTP/1.1" 502 -
```

But curl works fine:
```bash
curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "llama3.1:8b"}' | jq -r '.response'
# Returns full response after ~15 seconds
```

---

## Two Options (Pick One)

### Option A: Restore Groq Cloud (Fastest responses, ~1-2s)

Commit `f04d702` has "Multi-source knowledge base + Groq integration" but current code only has Ollama.

**Investigation:**
```bash
# See what Groq code looked like
git show f04d702:faithh_professional_backend_fixed.py | grep -A20 -i "groq"

# Check full diff
git diff HEAD f04d702 -- faithh_professional_backend_fixed.py | head -200
```

**What to restore:**
1. GROQ_API_KEY support in .env
2. Provider selection logic (Groq vs Ollama)
3. Groq API call function

**Add to .env:**
```
GROQ_API_KEY=gsk_xxxxx  # User will provide
MODEL_PROVIDER=groq     # or ollama
```

### Option B: Fix Frontend Timeout (Keep local Ollama)

The frontend gives up before Ollama finishes (~15s needed).

**Find the frontend:**
```bash
# Check what Flask serves
grep -n "render_template\|@app.route.*/" ~/ai-stack/faithh_professional_backend_fixed.py | head -10

# Find HTML templates
ls -la ~/ai-stack/templates/

# Search for fetch/timeout in templates
grep -rn "fetch\|timeout\|api/chat" ~/ai-stack/templates/
```

**Expected fix** - find the fetch call and increase timeout:
```javascript
// Current (probably short timeout or none specified)
fetch('/api/chat', { method: 'POST', body: JSON.stringify(data) })

// Fixed - add 2 minute timeout
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 120000);
try {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        signal: controller.signal
    });
    clearTimeout(timeoutId);
    // ... handle response
} catch (e) {
    if (e.name === 'AbortError') {
        showError('Request timed out - Ollama may be loading the model');
    }
}
```

---

## Also Fix These Bugs

### Bug 1: Status URL Malformation (Cosmetic)

**Problem:** `/api/status` shows wrong ChromaDB URL:
```json
"host": "http://http://192.158.1.243:8000:8000"
```

**Cause:** Double http:// because CHROMA_HOST already includes scheme.

**Fix:** Around line ~1262, find `chroma_url = f"http://{CHROMA_HOST}` and change to:
```python
if CHROMA_HOST.startswith("http"):
    chroma_url = f"{CHROMA_HOST}:{CHROMA_PORT}"
else:
    chroma_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}"
```

### Bug 2: Embedding Dimension Mismatch (Functional)

**Problem:** Auto-indexing fails:
```
❌ Index failed: Collection expecting embedding with dimension of 768, got 384
```

**Cause:** `index_conversation_background` uses wrong embedder (384-dim default instead of 768-dim BGE).

**Fix:** Find `index_conversation_background` function and make it use `query_embedder` (the BGE model already loaded) instead of creating its own embedder.

```bash
grep -n "index_conversation\|def index" ~/ai-stack/faithh_professional_backend_fixed.py
```

---

## Current System State

| Component | Status | Notes |
|-----------|--------|-------|
| Backend | ✅ Running | localhost:5557, v3.4 |
| Ollama | ✅ Working | llama3.1:8b, 2.3s direct response |
| ChromaDB | ✅ Connected | 192.158.1.243:8000, 27,568 docs |
| RAG | ✅ Working | BGE-768 embedder |
| UI Chat | ❌ Broken | 502 timeout before Ollama responds |
| Auto-index | ❌ Broken | 384/768 dimension mismatch |

---

## Key Files

- **Backend**: `/Users/macjohn/ai-stack/faithh_professional_backend_fixed.py`
- **Environment**: `/Users/macjohn/ai-stack/.env`
- **Templates**: `/Users/macjohn/ai-stack/templates/`
- **Logs**: Check terminal running backend, or `~/ai-stack/faithh.log`

---

## Test Commands

```bash
# Test Ollama directly (should be fast ~2s)
curl -s http://localhost:11434/api/generate -d '{"model": "llama3.1:8b", "prompt": "Hi", "stream": false}' | jq -r '.response'

# Test backend (works but slow ~15s)
curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "llama3.1:8b"}' | jq -r '.response' | head -c 200

# Check status
curl -s http://localhost:5557/api/status | jq '.services'

# Watch logs live
tail -f ~/ai-stack/faithh.log
```

---

## Success Criteria

1. [ ] UI chat returns responses (no "No response received")
2. [ ] Either Groq restored OR Ollama timeout fixed
3. [ ] Status endpoint shows correct ChromaDB URL
4. [ ] No embedding dimension errors in logs

---

## Git Reference

```bash
# Current HEAD
git log --oneline -5
# 1ab9791 (HEAD) Research: Chip synergy patterns
# 67808e0 Handoffs: Backend patching + Chip synergy research
# 836f58d Session 2025-12-30: Infrastructure audit
# f04d702 feat: Multi-source knowledge base + Groq integration  <-- GROQ WAS HERE
# 656da98 Session 2025-12-20: Gen8 setup complete

# To see Groq implementation
git show f04d702:faithh_professional_backend_fixed.py | grep -B5 -A30 -i "groq"
```

---

*Handoff created - Dec 31, 2025 ~9:00 PM PST*
