# Environment specification (FAITHH / ai-stack)

_Last refreshed: 2026-04-08. Counts are live samples from the configured Chroma host; re-verify after purges or reindex._

## ChromaDB (Gen8 LAN)

| Collection | Role | Document count (sample) |
|------------|------|-------------------------:|
| `faithh_knowledge_base` | Primary RAG corpus for general retrieval | 25,255 |
| `alife_lineage` | ALIFE experiment / lineage payloads | 339,900 |
| `governance_corpus` | Governance / civic corpus slice | 18,768 |

Connection: `CHROMA_HOST` / `CHROMA_PORT` (see `.env.example`). Default in many setups: `servicebox.taileb8c60.ts.net:8000`.

## Model routing (`auto` / `get_optimal_model_for_query`)

| Signal | Provider | Typical model |
|--------|----------|----------------|
| Low-complexity chit-chat / greetings (`is_low_complexity_chat_message`) | Ollama | `OLLAMA_GROUNDED_MODEL` or `qwen25-grounded:latest` |
| Doc-grounded phrasing (“according to my docs…”) | Ollama | Grounded model (same as above) |
| Complexity `complex` (patterns, length, intent flags) | Ollama | `OLLAMA_COMPLEX_MODEL` or `deepseek-r1:32b` |
| Complexity `creative` | Gemini | `gemini-2.0-flash-exp` (if configured) |
| Default | Ollama | Grounded model |

`configs/model_config.yaml` defines **fallback chains** per route key (`auto`, `code`, `fast`, `local`, `cloud`, `reasoning`). Groq is in the chain for `auto` / `fast` / `cloud`, but `backend/llm_providers.py` can strip Groq for simple local-first traffic when Ollama is healthy.

`config.yaml` sets `ai.primary_provider: ollama` and Groq model defaults under `ai.groq_models`; it does **not** force `mode: complex` for chat.

## Local GPU role (WSL2 workstation)

- **Query embeddings (SentenceTransformers path):** loaded on **CPU** in `faithh_professional_backend_fixed.py` (`get_query_embedder`, `device="cpu"`) to avoid sm_61 / dual-GPU init issues.
- **Chat / reasoning inference:** **Ollama** on the local GPU (see `CUDA_VISIBLE_DEVICES` at top of backend; typical RTX 3090 exposure).

## Environment variables (routing / RAG)

| Variable | Effect |
|----------|--------|
| `OLLAMA_GROUNDED_MODEL` | Overrides the default grounded Ollama tag for simple + default routes. |
| `OLLAMA_COMPLEX_MODEL` | Ollama model when complexity resolves to `complex`. |
| `RAG_MAX_DISTANCE_CONFIDENT` | Distance threshold for “confident” RAG hits (default `0.55`). |
| `CHROMA_HOST` / `CHROMA_PORT` | Chroma HTTP API target. |
| `CHROMA_COLLECTION` | Primary collection name (default `faithh_knowledge_base`). |
| `FAITHH_RAG_NORMALIZE_TRACE` | Set to `1` to log the first ~100 chars of each normalized RAG hit (`normalize_rag_hit_for_api`). |

## Gen8 (LAN)

- **LAN IP:** `servicebox.taileb8c60.ts.net` (see `CONTEXT.md`, `docs/guides/QUICKSTART.md`).
- **Services (from `docs/data/gen8-docker-compose.yml`):** ChromaDB `:8000`, Pi-hole DNS `:53`, Uptime Kuma `:3001`. Host may run additional stacks (SSH, Gitea, etc.) documented in `docs/guides/SSH_AND_NETWORKING.md` and `SYSTEMS_MAP.md`.

## Request performance log

Successful `/api/chat` completions append JSON lines to `logs/performance.log` with `rag_ms`, `llm_ms`, `post_ms`, `total_ms`, `provider`, `model`, `query_preview`, optional `vram_used_mib` / `vram_total_mib` from `nvidia-smi`.
