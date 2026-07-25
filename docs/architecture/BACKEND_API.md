# FAITHH Backend API Reference

**Last Updated:** 2026-04-09
**Version:** v4.0-pulse
**File:** `faithh_professional_backend_fixed.py` (shim: `faithh_professional_backend.py`)
**Port:** 5557

---

## Endpoints

### Core
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Serves `faithh_pet_v4.html` |
| GET | `/health` | Health check (JSON) |
| GET | `/api/health/gpu-hint` | GPU env diagnostic: compares process `CUDA_VISIBLE_DEVICES` to `FAITHH_CUDA_PHYSICAL_DEVICE` (`alignment`: MATCH/MISMATCH); includes `ollama_note` (Ollama uses its own process env) |
| GET | `/api/plc/state` | **Canonical ecosystem snapshot**: registry rows, `project_status`, `recent_component_changes`, embedded `faithh_status` (Ollama/Chroma/Gemini, `current_model`, ML chips, PULSE report ages) |
| GET | `/api/workspace/registry` | **Canvas service registry**: `services` map (chat/rag/genomic/pulse/diagnostics) + `navigation` for `faithh_pet_v4.html`; clients may send `workspace_registry` on `POST /api/chat` |
| GET | `/api/status` | Legacy alias: same body as `faithh_status` above (no PLC/registry fields) |
| POST | `/api/chat` | Main chat endpoint (optional body field `workspace_registry`: JSON snapshot from `/api/workspace/registry` for LLM tool hints) |
| GET | `/api/metrics/summary` | Session operational telemetry aggregate (`?days=7&limit=100`); sources Chroma `faithh_session_metrics` |
| GET | `/api/metrics/sessions` | Recent session metric documents (`?limit=20&date=YYYY-MM-DD`) |
| POST | `/api/metrics/flush-session` | **Dev / localhost only:** `{"session_id": "..."}` — flush accumulator and write closed session row (`FAITHH_DEV_MODE=true` or `REMOTE_ADDR` loopback) |
| POST | `/api/rag_search` | Direct RAG query |
| POST | `/api/upload` | Document upload |

### ML Chips
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/ml/chips` | List all 15 ML macro-chips |
| POST | `/api/ml/chips/activate` | Activate chips by query (cosine similarity) |

### PULSE Reflection Engine
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/pulse/reflection/status` | Reflection engine status + report ages |
| GET | `/api/pulse/reflection/staleness` | Latest staleness report (Tier 1) |
| GET | `/api/pulse/reflection/divergence` | Latest decision divergence report (Tier 2) |
| GET | `/api/pulse/reflection/branches` | Latest branch exploration report (Tier 3) |
| POST | `/api/pulse/reflection/run` | Trigger reflection sweep (`{"tier": "1"\|"2"\|"3"\|"all"}`) |

### PULSE Pattern Learning
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/pulse/status` | PULSE learning status |
| GET | `/api/pulse/proposals` | Pending chip proposals |
| POST | `/api/pulse/approve` | Approve a chip proposal |
| POST | `/api/pulse/reject` | Reject a chip proposal |
| GET | `/api/pulse/chips` | Personalized chip library |

### PULSE Security
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/pulse/security/scan` | Run security scanner on text |
| GET | `/api/pulse/health/check` | Check all service health |
| POST | `/api/pulse/health/heal` | Run healing cycle (dry-run default) |
| GET | `/api/pulse/audit/summary` | Audit log summary |
| GET | `/api/pulse/audit/recent` | Recent audit events |

### Compass Dashboard
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/compass` | Unified dashboard data |
| GET | `/api/compass/director` | Director analysis (actionable intelligence) |
| POST | `/api/compass/log` | Log work activity |
| GET | `/api/context/collectors` | Aggregated collector data |
| GET | `/api/context/collectors/status` | Collector status |
| POST | `/api/context/collectors/run` | Run a specific collector |
| GET | `/collectors/status` | HTML collector status page |

### Journal & Avatar
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/journal` | List journal entries (or `?date=YYYY-MM-DD` for specific) |
| POST | `/api/journal/generate` | Generate journal entry (`{"date": "...", "skip_llm": true}`) |
| GET | `/api/avatar` | Get user personality profile |
| POST | `/api/avatar/generate` | Generate/refresh avatar profile |

### Filesystem
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/filesystem` | Execute filesystem operations (token-protected) |
| GET | `/api/filesystem/capabilities` | List filesystem chip capabilities |

### Static Assets
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/images/<path>` | Chip art images |
| GET | `/faithh-character.png` | FAITHH avatar |

---

## Chat API

### Request
```bash
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What files are in this project?",
    "provider": "groq",
    "model": "llama-3.3-70b-versatile",
    "session_id": "optional-session-id"
  }'
```

### Provider Options
| Provider | Models | Notes |
|----------|--------|-------|
| `groq` | llama-3.3-70b-versatile, qwen/qwen3-32b, etc. | Default, fastest |
| `ollama` | llama31-faithh, qwen3-faithh, deepseek-r1:32b | Local, private |
| `gemini` | gemini-2.0-flash | Cloud fallback |
| `anthropic` | claude-3-haiku-20240307, claude-3-sonnet-20240229, claude-3-opus-20240229 | **NEW** - Claude-optimized responses |

### Anthropic Provider Features
- **Enhanced Responses**: Claude-optimized system prompts for expansive, detailed answers
- **Natural Conversation**: Temperature 0.7 for more interactive dialogue
- **Context Utilization**: Optimized RAG integration with thorough context use
- **Honest Responses**: Claude admits when context is insufficient while providing value

#### Anthropic Example
```bash
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "provider": "anthropic",
    "model": "claude-3-haiku-20240307"
  }'
```

### Response
```json
{
  "success": true,
  "response": "Here are the files...",
  "model": "llama-3.3-70b-versatile",
  "provider": "groq",
  "integrations_used": ["project_structure", "rag_search"],
  "rag_docs": 3,
  "session_id": "abc123"
}
```

---

## Backend Modules

```
backend/
├── data_loaders.py       # JSON file I/O (memory, decisions, projects, scaffolding)
├── intent_detection.py   # Query intent pattern matching
├── context_builders.py   # Context assembly + personality prompts + project structure snapshot
│   ├── get_faithh_personality()     # Original FAITHH personality (concise, accurate)
│   └── get_claude_personality()     # **NEW** Claude-optimized personality (expansive, thorough)
└── llm_providers.py      # Multi-provider LLM dispatch (Groq, Ollama, Gemini, Anthropic)
```

### Context Building Pipeline
1. `detect_query_intent()` — Classifies the query (self, why, project, constella, orientation)
2. `build_integrated_context()` — Retrieves context chips in parallel (ThreadPoolExecutor, 5 workers)
3. **Conditional Personality Selection** — Chooses personality based on provider:
   - `get_claude_personality()` for Anthropic (expansive, thorough reasoning)
   - `get_faithh_personality()` for other providers (concise, accurate responses)
4. LLM provider dispatches to Groq/Ollama/Gemini/Anthropic based on user selection

### RAG Temporal Weighting
RAG queries now blend cosine similarity with recency. Configurable via env vars:
- `RAG_TEMPORAL_WEIGHT=0.15` — 15% weight to recency (0 to disable)
- `RAG_TEMPORAL_HALFLIFE_DAYS=30` — recency score halves every 30 days

Query fetches 3× results, reranks with `score = similarity × 0.85 + recency × 0.15`, returns top N.

### Token Budgets (per chip)
```
rag_search:           1800 tokens (40%)
scaffolding:           900 tokens (20%)
decisions:             675 tokens (15%)
project_state:         450 tokens (10%)
constella:             450 tokens (10%)
self_awareness:        450 tokens (10%)
project_structure:     300 tokens (live file listing)
conversation_history:  225 tokens (5%)
```

---

## Management

### Start / Stop
```bash
./restart_backend.sh       # Stop + start
./stop_backend.sh          # Stop only
```

### Manual Start (for debugging)
```bash
source venv/bin/activate
python faithh_professional_backend_fixed.py
```

### Health Check
```bash
curl http://localhost:5557/health
```

### View Logs
```bash
tail -f backend.log
```

---

## Configuration

### Environment (.env)
```
MODEL_PROVIDER=groq
GROQ_API_KEY=...
GEMINI_API_KEY=...
```

### Config (config.yaml)
Runtime settings for model selection, RAG parameters, etc.

---

*Consolidated from BACKEND_CONFIG.md, FILESYSTEM_INTEGRATION.md (Feb 2026)*
