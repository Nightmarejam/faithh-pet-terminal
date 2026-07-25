# FAITHH System Overview

**Last Updated:** 2026-04-12  
**Version:** v3.4-filesystem (canonical backend unchanged; ops/metadata refreshed)

---

## What FAITHH Is

FAITHH (Friendly AI Teaching & Helping Hub) is a personal AI thought partner and knowledge management system. Inspired by MegaMan Battle Network NetNavi companions, it maintains context across projects and conversations.

**Core Purpose:** Help Jonathan maintain coherence across FAITHH development, Constella framework, and Floating Garden Soundworks audio production.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│              YOU (Browser or VS Code Extension)           │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│         faithh_professional_backend_fixed.py              │
│                   v3.4-filesystem (Port 5557)             │
├──────────────────────────────────────────────────────────┤
│ Flask Server                                              │
│ ├── /                  Serves faithh_pet_v4.html          │
│ ├── /api/chat          Main chat (all integrations)       │
│ ├── /api/workspace/registry  Canvas registry snapshot     │
│ ├── /api/status        System health + stats              │
│ ├── /api/rag_search    Direct RAG query                   │
│ ├── /api/upload        Document upload                    │
│ ├── /api/pulse/*       ML chip analytics                  │
│ └── /health            Liveness check                     │
├──────────────────────────────────────────────────────────┤
│ Backend Modules (extracted for modularity)                 │
│ ├── backend/data_loaders.py      JSON file I/O            │
│ ├── backend/intent_detection.py  Query intent matching     │
│ ├── backend/context_builders.py  Context assembly          │
│ └── backend/llm_providers.py     Multi-provider dispatch   │
├──────────────────────────────────────────────────────────┤
│ Parallel Chip Retrieval (build_integrated_context)        │
│ ├── project_structure  Live file listing (always)         │
│ ├── conversation_history  Recent turns                    │
│ ├── self_awareness     faithh_memory.json                 │
│ ├── constella          Civic framework context            │
│ ├── decisions          decisions_log.json                 │
│ ├── project_state      project_states.json                │
│ ├── scaffolding        scaffolding_state.json             │
│ └── rag_search         ChromaDB (faithh_knowledge_base ~54k docs) │
├──────────────────────────────────────────────────────────┤
│ Intent Detection                                          │
│ ├── is_self_query       Questions about FAITHH            │
│ ├── is_why_question     Decision rationale                │
│ ├── is_next_action      What to work on                   │
│ ├── is_project_query    Project/business questions         │
│ ├── is_constella_query  Civic framework                   │
│ └── needs_orientation   Catch-me-up requests              │
├──────────────────────────────────────────────────────────┤
│ LLM Providers                                             │
│ ├── Ollama (local, default per config.yaml)  e.g. faithh-v3 │
│ ├── Groq (cloud)           Optional when enabled          │
│ └── Gemini (cloud)         Optional fallback               │
└──────────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   ChromaDB   │ │    Ollama    │ │   ComfyUI    │
│  (Gen8 svr)  │ │  (systemd)   │ │  (RTX 3090)  │
│  Port 8000   │ │  Port 11434  │ │  Port 8188   │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## Memory Architecture

### Hot Memory (JSON state files, loaded per-request)
| File | Purpose | Update Frequency |
|------|---------|------------------|
| `faithh_memory.json` | FAITHH identity, capabilities, personality | Rarely |
| `decisions_log.json` | Why decisions were made, alternatives | Per major decision |
| `project_states.json` | Current phase of each project | Per session |
| `scaffolding_state.json` | Open loops, milestones, blockers | Per session |

### Warm Memory (ChromaDB vector database)
- **Host:** Gen8 server at servicebox.taileb8c60.ts.net:8000 (`CHROMA_HOST` / `CHROMA_PORT` in `.env`)
- **Primary collection:** `faithh_knowledge_base` — on the order of **~54k** chunks (see `fingerprint_state.json` `health.backend.chromadb_docs` after `scripts/generate_fingerprint.py`)
- **Maintenance collection:** `faithh_uncertainty_surface` — gated / noisy rows migrated out of the main KB (not used as RAG knowledge)
- **Session metrics:** `faithh_session_metrics` (or `CHROMA_METRICS_COLLECTION`) — telemetry only; **not** RAG (per `AGENTS.md`)
- **Embedding:** `all-MiniLM-L6-v2` (384 dimensions) for KB ingest/query in typical paths
- **Search:** Semantic similarity; low-confidence path when best distance exceeds `RAG_MAX_DISTANCE_CONFIDENT`

### Live Context (project structure snapshot)
- Generated on every request by `get_project_structure_snapshot()`
- Lists actual files in the repo right now
- Prevents FAITHH from hallucinating file references

---

## Request Flow

```
User Query
    │
    ▼
┌─────────────────┐
│ Intent Detection │ ← Pattern matching on query text
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│   build_integrated_context()                 │
│   ThreadPoolExecutor (5 workers, 10s timeout)│
│                                              │
│   Parallel chip retrieval:                   │
│   ├── project_structure (always)             │
│   ├── conversation_history (always)          │
│   ├── self_awareness (if self query)         │
│   ├── constella (if constella query)         │
│   ├── decisions (if why question)            │
│   ├── project_state (if project query)       │
│   ├── scaffolding (if orientation needed)    │
│   └── rag_search (most queries, async)       │
│                                              │
│   Token budgets enforce context limits:      │
│   RAG=1800, Scaffolding=900, Decisions=675,  │
│   Project=450, Constella=450, Self=450,      │
│   Structure=300, History=225                 │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ LLM Provider    │ ← System prompt + personality + context + query
│ (Groq/Ollama/   │
│  Gemini)        │
└────────┬────────┘
         │
         ▼
    Response + auto-index conversation to ChromaDB
```

---

## Coherence Arbiter (Phase 1–3)

The Coherence Arbiter measures semantic convergence between RAG retrieval and ML chip routing, then validates claims against canonical state (anchor validation).

**Phase 1:** Convergence score from RAG–chip embedding alignment; signal strength weighting.

**Phase 2:** Anchor validation against `project_states.json` (FAITHH phase): ML chips loaded, ChromaDB scale, PULSE engine presence; optional checks for default-provider decision and PULSE documentation in state. Score ≥ 0.7 is considered valid.

**Phase 3:** Response metadata is enriched with:
- **tier:** `high` | `medium` | `low` (from convergence + anchor score).
- **reasons:** List of signals (e.g. `rag_chip_alignment`, `anchor_validation_0.82`).
- **low_confidence:** `true` when tier is low or anchor is enabled but invalid.
- **suggested_behavior:** `ok` | `hedge` | `recheck_sources` for UI or routing.

Thresholds are centralized in `backend/coherence_arbiter.py` (`COHERENCE_TIER_HIGH_THRESHOLD`, `COHERENCE_TIER_MEDIUM_THRESHOLD`, `ANCHOR_VALID_THRESHOLD`). The UI shows a coherence indicator and an advisory hint when `low_confidence` is true. See `docs/guides/COHERENCE_SIGNAL.md` for how to interpret the signal.

---

## ML Pipeline

### Chip Synthesis
- **Script:** `ml/chip_synthesis.py` (BERTopic clustering)
- **Output:** 15 macro-chips from 32K conversation chunks
- **Centroids:** 384-dim embeddings for cosine similarity routing
- **Integration:** Backend loads chips at startup, activates based on query similarity

### Image Generation
- **ComfyUI** on RTX 3090 (port 8188)
- **SDXL** checkpoint (1024x1024) + **FAITHH LoRA** (13MB, trained on 38 MMBN reference images)
- **Script:** `scripts/generate_chip_art.py --sdxl --lora`
- **Output:** `images/chips/` (15 chip icons + named copies for UI)

### LoRA Training
- **Script:** `ml/lora/train_pixel_art_lora.py`
- **Data:** `ml/lora/training_data/` (38 images, auto WebP→PNG conversion)
- **Venv:** `ml/lora_venv/` (PyTorch 2.6, diffusers, peft)
- **GPU:** RTX 3090 via `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1`

---

## Key Files

| Need | File |
|------|------|
| Start FAITHH | `./restart_backend.sh` |
| Main backend | `faithh_professional_backend_fixed.py` |
| Frontend UI | `faithh_pet_v4.html` |
| Backend modules | `backend/*.py` |
| System config | `config.yaml`, `.env` |
| Docker stack | `docker-compose.yml` |
| Scripts | `scripts/` |
| Tests | `tests/` |
| ML pipeline | `ml/` |
| Documentation | `docs/` |

---

*Consolidated from ARCHITECTURE.md, HOW_IT_WORKS.md, ECOSYSTEM_MAP.md, BACKEND_CONFIG.md, DOCKER_SERVICES.md — counts/models refreshed 2026-04-12 (`fingerprint_state.json`, `AGENTS.md`).*
