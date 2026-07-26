> ⚠️ **SUPERSEDED 2026-07-25.** This was one of six competing "master" context documents.
> All live context now lives in **`AGENTS.md`** at the repo root. Kept for history only —
> its state claims were stale (services listed as running that had been down for months).
> Do not read this as current.

---

# AI Stack - Master Context

**Last Updated:** 2026-04-12  
**System Owner:** Jonathan (jonat)  
**Primary Environment:** Ubuntu 24.04 (WSL2) + Gen8 Server (Ubuntu 22.04)  
**Truth sources:** `AGENTS.md`, `fingerprint_state.json` (regenerate via `python3 scripts/generate_fingerprint.py`), `project_states.json`

---

## System Overview

This is Jonathan's unified AI development and personal project management system. It integrates:
- Multi-LLM backend (**Ollama default** per `config.yaml` `ai.default_model`, e.g. `qwen25-faithh-v3:latest`; Groq / Gemini / Anthropic optional)
- RAG via ChromaDB on Gen8 (`faithh_knowledge_base` — on the order of **~54k** chunks; see live fingerprint)
- **`faithh_uncertainty_surface`** — maintenance collection for migrated low-quality / boilerplate rows (**not** RAG)
- Real-time coherence detection with PULSE + Coherence Arbiter
- Professional portfolio management (Tom Cat Sound LLC, Constella Harmony framework)
- Gen8 home server infrastructure (12+ services)
- ALIFE artificial life simulation framework
- Google Custom Search integration

---

## Current Infrastructure

### Development Environment
- **Primary Machine:** DESKTOP-JJ1SUHB (WSL2, Ubuntu 24.04)
- **Working Directory:** `/home/jonat/ai-stack`
- **Python Environment:** venv with backend dependencies
- **Git Status:** Main branch, active development
- **Remote:** github.com:Nightmarejam/faithh-pet-terminal.git

### Gen8 Server (servicebox)
- **Hostname:** servicebox
- **IP Addresses:**
  - LAN: servicebox.taileb8c60.ts.net (canonical for Chroma / SSH / metrics in repo docs)
  - Tailscale: use `tailscale status` on a connected host if needed; do not substitute the LAN address as a Tailscale IP
- **OS:** Ubuntu 22.04 LTS
- **Docker:** v28.2.2
- **User:** jonat
- **Status:** ✅ Online, SSH configured

#### Services Running on Gen8

**ChromaDB** (Production - Gen8, ongoing reindex/migrations)
- Location: `~/services/chromadb/` (on servicebox)
- Port: 8000
- API: http://servicebox.taileb8c60.ts.net:8000
- **Primary collection:** `faithh_knowledge_base` (~54k chunks — use `fingerprint_state.json` or `GET http://127.0.0.1:5557/health` for current count)
- **Other:** `faithh_uncertainty_surface` (noise / gated content), `faithh_session_metrics` (telemetry, not RAG), `alife_lineage` (ALIFE)
- Embedding: all-MiniLM-L6-v2 (384 dimensions) for typical KB paths
- Status: ✅ Running when Gen8 and network path are up

---

## RAG System Status

### Current State (as of April 2026)
- **Primary KB:** `faithh_knowledge_base` — scale **~54k** chunks (verify with fingerprint / health endpoint)
- **Uncertainty surface:** `faithh_uncertainty_surface` — rows migrated from KB when they match noise/heuristic patterns (see `docs/archive/HANDOFF_2026-04-12_model-fix-and-kb-cleanup.md`)
- **Session metrics:** `faithh_session_metrics` — operational telemetry only (**do not** treat as RAG knowledge)
- **ALIFE:** `alife_lineage` on Gen8 for simulation exports (large; separate from personal KB)
- **Embedding model:** all-MiniLM-L6-v2 (384 dimensions) for standard ingest/query
- **Low confidence:** When best retrieval distance exceeds `RAG_MAX_DISTANCE_CONFIDENT`, backend sets `rag_relevance.low_confidence` and prepends a no-fabrication banner (see `AGENTS.md`)

---

## Supported LLM Providers

### 1. Ollama (Local — default path when `config.yaml` says so)
- **Default model (YAML):** `qwen25-faithh-v3:latest` (check `ai.default_model` and `providers.ollama`)
- **Host:** http://127.0.0.1:11434
- **GPU:** RTX 3090 (typical for heavy local models); align Ollama service `CUDA_VISIBLE_DEVICES` with FAITHH docs
- **Usage:** Primary local inference; stop sequences + `num_predict` cap wired in `backend/llm_providers.py`

### 2. Groq (Cloud, optional)
- **Models:** llama-3.3-70b-versatile, others as configured
- **API:** https://api.groq.com/openai/v1
- **Usage:** When enabled and routed (not assumed primary in current YAML)

### 3. Gemini (Google)
- **Model:** gemini-2.0-flash
- **API:** Generative Language API
- **Usage:** Alternative provider, specific tasks

### 4. Anthropic (Reserved)
- **Model:** claude-3-haiku
- **Budget:** $4 reserve
- **Usage:** Emergency backup, specific API tasks

---

## Active Projects

### 1. FAITHH Backend System
**Status:** Production (v4.0-pulse)
**Key Features:**
- Multi-provider LLM dispatch
- RAG integration with ChromaDB
- PULSE Reflection Engine (staleness detection)
- Project structure awareness
- Real-time coherence scoring

### 2. ALIFE (Artificial Life Simulation)
**Path:** `projects/alife/`
**Status:** Experiment 3 complete (FULL_SUCCESS), Experiment 4 in progress
**Key result:** Anticipatory behavior confirmed — agents evolved predictive shield activation before threat detection (negative anticipation gap). Red Queen dynamics observed across 200,000 ticks.
**ChromaDB:** alife_lineage collection on Gen8, 50,000+ documents
**Next:** Experiment 4 (harmonic interference, Wave 2 arrival bug pending)

### 3. VS Code Extension
**Path:** `faithh-vscode/`
**Status:** Phase 1-2 complete, Phase 3 in progress
**Features:** Inline completion, code actions, sidebar integration
**Next:** Full companion experience with ML chips

### 4. PULSE Reflection Engine
**Status:** Tier 1 operational, development ongoing
**Purpose:** Self-awareness and system health monitoring
**Components:** Staleness detection, decision divergence, branch exploration
**Next:** Tier 2 implementation

---

## Services

### Core Infrastructure
- **ChromaDB:** Vector database, RAG storage
- **Grafana:** Monitoring dashboards
- **Prometheus:** Metrics collection
- **Gitea:** Git server
- **Vaultwarden:** Password management
- **Pi-hole:** DNS ad blocking

### Development Services
- **Docker Registry:** Container storage
- **GitLab Runner:** CI/CD
- **Uptime Kuma:** Service monitoring
- **Node Exporter:** System metrics

### External Integrations
**Google Custom Search:**
- Status: configured
- Engine ID: 430369bf618924d21
- Endpoint: /api/search
- Rate limit: 100 queries/day

---

## Recent Changes (Git Log)

### April 2026
- **KB hygiene:** Noise rows migrated to `faithh_uncertainty_surface`; indexing quality gate on assistant replies (`_index_eligible`)
- **Ollama stability:** Stop sequences + output cap; default chat model migration to `qwen25-faithh-v3:latest` (see `config.yaml`)
- **Docs/UI:** Architecture doc refresh; Canvas RAG similarity display aligned with Chroma distance semantics

### March 2026
- **RAG / model fixes:** Context usage and metadata audits on earlier chunk counts
- **ALIFE Progress:** Experiment 3 completed with anticipatory behavior findings

### February 2026
- **PULSE Development:** Tier 1 staleness detector operational
- **Documentation Updates:** Multiple roadmap documents created
- **System Optimization:** Performance improvements and bug fixes

---

## Security & Compliance

### Authentication
- **API Keys:** Stored in `.env` (gitignored)
- **Keyring:** Encrypted credential storage
- **SSH Keys:** Configured for Gen8 access

### Data Protection
- **Privacy Levels:** public, internal, confidential classification
- **Retention Policies:** Automated cleanup of old data
- **Backups:** Regular snapshots to NAS

---

## Development Workflow

### Code Organization
- **Backend:** `faithh_professional_backend_fixed.py`
- **Modules:** `backend/` (data loaders, intent detection, context builders)
- **Projects:** `projects/` (ALIFE, VS Code extension)
- **Scripts:** `scripts/` (maintenance, testing, utilities)
- **Documentation:** `docs/` (architecture, guides, reference)

### Testing
- **Unit Tests:** `tests/` directory
- **Integration Tests:** API endpoint testing
- **Performance Tests:** Query latency monitoring

---

## Next Steps & Roadmap

### Immediate (This Week)
- Complete ALIFE Experiment 4 debugging
- Implement metadata migration strategy
- Optimize RAG tier performance

### Short Term (Next Month)
- Deploy VS Code extension Phase 3
- Complete PULSE Tier 2 implementation
- GPU installation (Tesla T1000)

### Long Term (Next Quarter)
- ALIFE Phase 2 (Gen8 QEMU deployment)
- Advanced ML chip integration
- Public data aggregation pipeline

---

## Troubleshooting

### Common Issues
- **Backend restart:** Use `./restart_backend.sh`
- **ChromaDB connection:** Check Gen8 connectivity
- **GPU issues:** Monitor with `nvidia-smi`
- **RAG queries:** Verify metadata quality

### Monitoring Commands
```bash
# Backend health
curl -s http://localhost:5557/health | python3 -m json.tool | head -20
curl http://localhost:5557/api/status

# ChromaDB heartbeat
curl http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat

# System resources
htop
df -h
```

---

*This document is maintained as part of the development workflow. Update after major changes.*
