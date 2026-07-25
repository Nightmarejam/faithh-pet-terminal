# FAITHH Dependency Map

_Last updated: 2026-04-03_

This document describes **runtime services, external APIs, and model inventory** as wired in the repo today. It is distinct from root `DEPS.md`, which tracks **change-impact** (what to update when you edit X).

## Runtime services

| Service | Port | Started by | Health endpoint | What breaks if down |
|---------|------|------------|-----------------|---------------------|
| FAITHH backend (Flask) | `5557` (env `BACKEND_PORT`) | `./restart_backend.sh` or `python faithh_professional_backend_fixed.py` | `/api/health`, `/health` | All UI/API; chat, RAG, tools |
| Ollama (main) | `11434` | `docker-compose` (`ollama`) or host install | `GET /api/tags` on `OLLAMA_HOST` | Local LLM inference, `/api/models` Ollama list |
| Ollama (embed) | `11435` (mapped to container 11434) | `docker-compose` (`ollama-embed`) | `GET /api/tags` on that host:port | Workloads using `OLLAMA_EMBED_URL` / second instance |
| Ollama (qwen) | `11436` (mapped to container 11434) | `docker-compose` (`ollama-qwen`) | `GET /api/tags` | Optional third Ollama instance |
| ChromaDB | `8000` (default; override via `CHROMA_HOST` / `CHROMA_PORT` / `CHROMA_URL`) | `docker-compose` (`chromadb`) | Docker healthcheck: `http://localhost:8000/api/v2/heartbeat` (in-container) | RAG (`/api/rag_search`), collections; backend may start with `CHROMA_CONNECTED=False` |
| Postgres | `5432` (internal to compose network) | `docker-compose` (`postgres`) | `pg_isready` (compose healthcheck) | Langflow DB only (not FAITHH core chat) |
| Langflow | `7860` | `docker-compose` (`langflow`) | (image default) | Langflow UI/workflows only |
| Prometheus | `9090` (bound to `127.0.0.1`) | `ops/monitoring/docker-compose.yml` | `/-/healthy` | Metrics collection for that stack |
| Alertmanager | `9093` (bound to `127.0.0.1`) | `ops/monitoring/docker-compose.yml` | `/-/healthy` | Alert routing from Prometheus |
| node-exporter | `9100` (expected per `prometheus.yml`) | external / host | `/metrics` | Host metrics in Prometheus |
| fail2ban exporter | `9635` (per `prometheus.yml`) | external | `/metrics` | Security scrape targets |
| Grafana | `3000` (scrape target in `prometheus.yml`; not defined in root compose) | separate install | `/api/health` (typical) | Dashboards only |
| Uptime Kuma | `3001` (per `prometheus.yml`) | separate install | `/metrics` (scrape path in config) | Uptime monitoring only |
| text-generation-webui (local) | `7001` (per `configs/model_config.yaml` `local_webui`) | manual | (depends on install) | Phase-2 `local_webui` provider in `backend/llm_providers.py` |

**Note:** `config.yaml` lists `api.port: 5557` while `allowed_origins` still mention `8080` — treat **`5557` as canonical** for the Flask app unless overridden by `.env`.

## External API dependencies

| Provider | Used for | Fallback if unavailable | Key env var / config |
|----------|----------|-------------------------|----------------------|
| Groq | Cloud chat (`/api/chat` when provider/model resolves to Groq) | None as automatic substitute for all paths | `GROQ_API_KEY` |
| Google Gemini | Optional cloud path in `llm_providers` / backend | None | `GEMINI_API_KEY`, `GOOGLE_API_KEY` |
| Anthropic | SWE / Claude paths in `llm_providers`, optional backend | Configured backup model in `config.yaml` | `ANTHROPIC_API_KEY` |
| Hugging Face / SentenceTransformer | Query embedding when RAG embedder loads | RAG may degrade or skip embedding-dependent paths | `HF_*`, offline flags in backend |
| UniFi UDM | `scripts/unifi_snapshot.sh` → API snapshot | Script fails; no FAITHH runtime dependency | `UDM_BASE_URL`, `UDM_USER`, `UDM_PASS`, `UDM_MFA_TOKEN` (and related snapshot scripts) |

## Model inventory (representative)

| Model / name | Provider | Used for | Config / code location |
|--------------|----------|----------|------------------------|
| `qwen25-grounded:latest` | Ollama | Default local chat / grounded paths | `faithh_professional_backend_fixed.py` `DEFAULT_MODEL`, `get_optimal_model_for_query` doc-grounded |
| `llama3.3:70b` | Ollama | Complex reasoning (smart routing helper) | `backend/llm_providers.py` `get_optimal_model_for_query` |
| `gemini-2.0-flash-exp` | Gemini | “Creative” branch in `get_optimal_model_for_query` | `backend/llm_providers.py` |
| `llama31-faithh:latest` / `qwen3-faithh:latest` (comments) | Ollama | Example in Phase-2 YAML | `configs/model_config.yaml` |
| `qwen/qwen3-32b` | Groq | Phase-2 default Groq model | `configs/model_config.yaml` |
| `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `openai/gpt-oss-120b` | Groq | Named in `config.yaml` `groq_models` | `config.yaml` |
| Claude Haiku | Anthropic | Fallback / Anthropic blocks | `config.yaml` `anthropic` |

## Routing module vs main backend

- **`backend/llm_providers.py`** exposes `run_llm_route`, `run_llm_route_with_pin`, and `run_llm_smart_route`, with **`ollama_is_healthy()`** and the **Groq exclusion gate** for simple queries when Ollama is healthy.
- **`faithh_professional_backend_fixed.py`** `/api/chat` (2026-04-03+) calls **`run_llm_route_with_pin`** using **`configs/model_config.yaml`** after building `full_prompt`. Anthropic and Gemini still use dedicated branches.

## Phase-2 YAML drift

`configs/model_config.yaml` route **`auto`** still lists **`groq` first**. `run_llm_route` appends missing providers from `["local_webui", "ollama", "groq"]` but does not reorder existing entries. For **simple** queries with healthy Ollama, **`_apply_groq_gate_for_simple_local`** removes `groq` from the attempt list even if it was first in YAML.

## What currently has no fallback (or weak degradation)

- [ ] **ChromaDB unreachable** — backend logs warning; RAG-heavy features fail or return empty depending on path.
- [ ] **Ollama down + no Groq key** — cloud paths unavailable; local inference fails.
- [ ] **Groq excluded for simple + healthy Ollama** — if local providers then fail, there is **no Groq retry** for that request (intentional per routing policy).
- [ ] **FAITHH process** — no supervisor in repo; use manual restart scripts.
- [ ] **`/api/health`** may return non-200 while server still accepts traffic (observed `500` in one run with metric/registry issues).

## llama.cpp

See [llamacpp_assessment.md](./llamacpp_assessment.md) for binaries, server mode, and GGUF inventory on this workspace.

## ALife vs FAITHH backend

`projects/alife/` experiments import **`faithh_observer.PulseWatcher`** (local observer helper), not HTTP to `:5557`. **No runtime requirement** on the FAITHH Flask server for those scripts unless you add such calls.
