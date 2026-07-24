# FAITHH system state (ground truth)

_Last updated: 2026-04-03_

Snapshot for Cursor handoff: services, models, routing, and open questions.

## Ollama models (from `ollama show`)

| Model | Size | Quant | Notes |
|-------|------|-------|-------|
| `qwen25-grounded:latest` | 14.8B | Q4_K_M | **Default** grounded tag in docs + typical `.env`; verify backend / `configs/model_config.yaml` on your machine |
| `qwen25-grounded-gen5-delta:latest` | 14.8B | Q4_K_M | Alternate grounded build (KV benchmark / experiments); different Modelfile blob vs baseline |
| `deepseek-r1:32b` | 32.8B | Q4_K_M | **Reasoning / complex** slot (`OLLAMA_REASONING_MODEL`, `OLLAMA_COMPLEX_MODEL`, intent `reasoning` route) |
| `llama3.3:70b` | 70.6B | Q4_K_M | Still pullable; **not** default for `get_optimal_model_for_query` complex branch anymore (replaced by DeepSeek) |

### Difference: `qwen25-grounded-gen5-delta` vs `qwen25-grounded`

From `ollama show … --modelfile` (same arch, params, quant):

| | gen5-delta | original |
|---|------------|----------|
| **FROM blob** | `sha256-98ebf1f55fe7…` | `sha256-78047f1a5e13…` (different artifact) |
| **TEMPLATE** | `{{ .Prompt }}` + separate **SYSTEM** line (FAITHH grounded system prompt) | Chat template with `\|im_start\|…\|im_end\|` and **stop** on end token |
| **Interpretation** | Newer packaging / Gen5 delta weights or rebuild; simpler prompt template path | Older chat-template Modelfile |

*Fine-tune vs rebuild only:* not fully determined from metadata alone; blob hash proves **different built image**, not just a tag alias.

## Services (expected / confirmed)

| Service | Port | Notes |
|---------|------|--------|
| FAITHH backend | 5557 | Chat path uses `run_llm_route_with_pin` + `configs/model_config.yaml` after 2026-04-03 changes |
| Ollama primary | 11434 | Main inference; `OLLAMA_HOST` |
| Ollama embed | 11435 | Second daemon (`OLLAMA_EMBED_URL` in `.env.example`) |
| Ollama qwen | 11436 | Third compose service |
| ChromaDB | 8000 | RAG; `CHROMA_HOST` in `.env` should target Gen8 LAN (e.g. `servicebox.taileb8c60.ts.net`) per current docs |
| Langflow | 7860 | **Idle** for core FAITHH chat unless you use Langflow flows explicitly |
| Postgres | 5432 | Langflow DB |
| Grafana | 3000 | Monitoring UI (scrape target in `ops/monitoring/prometheus.yml`) |
| Prometheus | 9090 | `127.0.0.1:9090` in compose |
| node-exporter | 9100 | Gen8 / host metrics scrape |
| fail2ban exporter | 9635 | **Not returning metrics** in one WSL check (empty `curl`); verify on Gen8 host |

### Pending

- **NAS node_exporter** on DS220J — Synology Container Manager job; Prometheus scrape for NAS IP TBD.
- **`llama-server` on PATH** — binary at `~/ai-stack/llama.cpp/llama-server`; symlink added to `~/.local/bin/llama-server` (ensure `~/.local/bin` is on PATH).

## Multi-Ollama instances (:11435 / :11436)

- **Compose** defines separate GPUs/volumes per service (`docker-compose.yml`).
- **FAITHH canonical** chat uses **`OLLAMA_HOST` (11434)** unless you change env or `model_config` `base_url`.
- **11435** is referenced for embed (`OLLAMA_EMBED_URL`) and fallback handlers in `backend/connection_monitor.py` (not primary chat).
- **11436** is a third Ollama instance; **no automatic routing** from `faithh_professional_backend_fixed.py` unless configured.

**Which models are loaded on each:** run on the host: `curl -s http://127.0.0.1:11434/api/tags` (and `:11435`, `:11436`). Not captured in-repo.

## text-generation-webui (:7001)

- `curl -s http://127.0.0.1:7001/v1/models` returned **empty** during doc write — treat **local_webui provider as likely failing** until the server is up.
- `configs/model_config.yaml` `local_webui` entry should match whatever model text-generation-webui actually loads (often `qwen25-grounded:latest`).

## Routing (post 2026-04-03)

- `/api/chat` → **`run_llm_route_with_pin`** with YAML providers + **`_apply_groq_gate_for_simple_local`** (Ollama `/api/tags` health probe).
- Route **`reasoning`** when `intent['is_reasoning']` or `intent['is_complex_query']`; Ollama model forced to **`OLLAMA_REASONING_MODEL`** (default `deepseek-r1:32b`).
- `get_optimal_model_for_query` **complex** → **`OLLAMA_COMPLEX_MODEL`** default `deepseek-r1:32b` (replaces prior `llama3.3:70b` default).
- `config.yaml` **`heavy_reasoning`** documents Ollama DeepSeek settings (not yet auto-loaded by Flask; env + routing own the live choice).

## `/api/health`

- **Root cause** of `NoneType ... 'requests'`: **`SecurityMiddleware`** with `enable_rate_limiting=False` set **`rate_limiter = None`**, but **`get_security_stats()`** called **`len(self.rate_limiter.requests)`**. **Fixed** in `backend/security_middleware.py`.
- **Hardening**: `/api/health` now **isolates** connection, performance, cache, and security sub-checks so one failure **does not** return a bare 500.
- **Restart required** for a running server to pick up changes.

## UI session backlog (document only)

| ID | Module | Scope |
|----|--------|--------|
| UI-1 | Compass | Self-awareness, Compass Director |
| UI-2 | Cockpit | Ops dashboard — models, routing, health |
| UI-3 | PULSE | Pattern tracking UI |
| UI-4 | Chip interface | Chip browser / active context |
| UI-5 | Chat QoL | Upload, agents, history |
| UI-6 | API visibility | Provider status panel |
| UI-7 | Facelift | Layout / theme consistency |

Start each with a **design brief** before code.

## Power BI track (parallel)

Example dataset: **Tom Cat Sound LLC** 2024 Form 1065 (1065 line items + K-1 splits). Use as the canonical **import → model → DAX → dashboard** runbook example.
