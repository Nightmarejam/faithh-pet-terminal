# PARITY: faithh_professional_backend_fixed.py
**Last Updated:** 2026-01-16
**Status:** Active
**Version:** 1.0.0

---

## Current State

**Purpose:** Flask backend serving chat/RAG API for FAITHH, integrating Ollama, ChromaDB, collectors, and UI endpoints.

**Key Features:**
- Chat endpoint `/api/chat` with model/provider reporting and ping fastpath guard
- RAG search endpoint `/api/rag_search` (ChromaDB) with CPU-forced embedder
- Collector status endpoints `/api/context/collectors/status` and `/collectors/status` (HTML)
- Safe collector runner `/api/context/collectors/run` (whitelisted commands)
- Health/status endpoint `/api/status`

**Dependencies:**
- Python: Flask, requests, chromadb, sentence-transformers, pydantic
- Services: Ollama at `http://127.0.0.1:11434`, ChromaDB at `http://servicebox.taileb8c60.ts.net:8000`
- Internal: `faithh_pet_v4.html`, `decisions_log.json`, `faithh_memory.json`, `project_states.json`

**Entry Points:**
- `faithh_professional_backend_fixed.py` (`app.run`)
- `./restart_backend.sh` (preferred launcher)

---

## Recent Changes

### 2026-01-16 - Stability & Observability
**Changed:**
- Added collector status JSON + HTML and safe re-run endpoint
- Forced embedder to CPU to avoid CUDA kernel image errors
- Adjusted chat ping fastpath to respect explicit queries
- Exposed model/provider in chat responses for UI display

**Reason:** Improve monitoring, avoid GPU embedder crashes, and prevent RAG/chat from misrouting to ping fastpath.

**Impact:**
- Collector visibility available for humans/Pulse
- RAG stable (all tests passing) with reliable embedding
- Chat correctly reports model/provider and avoids false "pong" responses

---

## Known Issues

- WSL GPU isolation: Ollama PID shows on both GPUs despite `CUDA_VISIBLE_DEVICES=1`; performance acceptable on 3090.
- Embedder runs on CPU by design; expect some latency but avoids CUDA kernel errors.

---

## Pending Changes
- Integrate collector status badges into Pulse tab/UI.
- Consider default RAG-on in chat API if desired.

---

## Configuration

**Environment Variables Required:**
- `OLLAMA_HOST` (default `http://127.0.0.1:11434`)
- `CHROMA_HOST` (default `http://servicebox.taileb8c60.ts.net:8000`)
- `CHROMA_COLLECTION` (default `faithh_knowledge_base`)
- `EMBEDDING_MODEL_ID` (default `BAAI/bge-base-en-v1.5`)
- `DEFAULT_MODEL` (e.g., `qwen3-faithh:latest`)
- `GOOGLE_API_KEY` (for Gemini, if used)

**Config File Settings (sample):**
```yaml
ai:
  primary_provider: gemini
  fallback_provider: ollama
  ollama:
    model: llama31-faithh:latest
    base_url: http://localhost:11434
    gpu_layers: -1
    context_size: 0
    batch_size: 512
    keep_alive: 24h
```

---

## Testing

**How to Test:**
```bash
./restart_backend.sh
python -m pytest tests/ -v
./scripts/test_rag_stability.sh
```

**Expected Behavior:**
- `/api/status` reports Chroma online and lists Ollama models
- `/api/rag_search` returns results with embedding_model noted
- `/api/chat` returns model_used/provider and honors RAG when requested

---

## Notes
- UI: `faithh_pet_v4.html` shows model/provider and links to collectors status.
- Collectors cron uses absolute paths and working directory; manual run via `/api/context/collectors/run`.

---

*Last reviewed: 2026-01-16*
