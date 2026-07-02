# FAITHH — Friendly AI Teaching & Helping Hub

Personal AI companion and knowledge management system, inspired by MegaMan Battle Network NetNavi.

## Quick Start

```bash
./restart_backend.sh        # Start Flask backend on :5557
# Open http://localhost:5557
```

## What FAITHH Does

- **Chat** with multi-provider LLM routing (Groq, Ollama, Gemini)
- **RAG** search across 32,499 indexed chunks (ChromaDB + BGE embeddings)
- **ML Chips** — 15 semantic routing chips that activate based on query intent
- **Decision memory** — tracks and cites past decisions with rationale
- **Project awareness** — knows current state of FAITHH, Constella, Tom Cat Sound
- **VS Code extension** — FAITHH chat sidebar in your editor

## Current State (2026-03-28) - Phase 4.5 Complete ✅

| Component | Status | Location |
|-----------|--------|----------|
| Backend | ✅ Enhanced with retry logic & monitoring (port 5557) | `faithh_professional_backend_fixed.py` |
| Frontend | ✅ PET Terminal v4 | `faithh_pet_v4.html` |
| RAG | ✅ 38K+ chunks with project summaries | ChromaDB on Gen8 (192.158.1.243:8000) |
| **Anthropic Optimization** | ✅ 150% response quality improvement | `backend/context_builders.py` |
| **Retry Logic** | ✅ Exponential backoff for API reliability | `backend/llm_providers.py` |
| **Service Monitoring** | ✅ Real-time health checks via `/api/monitoring/services` | `backend/llm_providers.py` |
| **Project Summaries** | ✅ 5 comprehensive project summaries | `docs/project_summaries/` |
| **Quality Monitoring** | ✅ Framework for response quality tracking | `backend/local_optimization.py` |
| **Genomic Experiments** | ✅ 3 phases completed (190 organisms tested) | `experiments/genomic/` |
| Genomic Endpoints | ✅ 5 endpoints operational | `/api/genomic/*` |
| LLM (Cloud) | ✅ Groq, Anthropic, Gemini with monitoring | via API keys in `.env` |
| LLM (Local) | ✅ Ollama (qwen25-grounded optimized) | systemd service, port 11434 |
| ML Chips | ✅ 491 chips including 14 Anthropic optimization | Loaded at startup |
| **Advanced Analytics** | ✅ Predictive analytics & insights | `backend/advanced_analytics_simple.py` |
| **AI-Driven UX** | ✅ Personalized user experience | `backend/ai_driven_ux.py` |
| **Program Advance** | ✅ Optimized with caching & auto-tuning | `backend/program_advance_optimizer.py` |
| **ALIFE Research** | ✅ Cultural evolution breakthrough | `projects/alife/experiments/` |
| **Security** | ✅ Rate limiting, input validation | `backend/security_middleware.py` |
| **Monitoring** | ✅ Health checks (4 providers) + connection monitor | `backend/connection_monitor.py` |
| **Caching** | ✅ 100MB intelligent cache | `backend/cache.py` |
| **Performance** | ✅ Real-time metrics | `backend/performance.py` |
| **AI Optimization** | ✅ Intelligent model selection + auto-tuning | `backend/local_optimization.py` |

### Phase 6.0 Achievements 🧬
- **Genomic Impedance Reading**: First successful integration of environmental impedance detection with biological systems
- **Genomic Biasing Engine**: DNA copying bias based on impedance patterns with cognitive enhancement
- **Multi-Phase Experiments**: Large-scale testing, environmental adaptation, and multi-generational evolution
- **190 Organisms Tested**: Across 3 experimental phases with perfect correlation results
- **5 Genomic Endpoints**: Complete API for genomic sensor creation, biasing analysis, and pattern analysis
- **Statistical Validation**: Perfect correlation (1.000) between biasing potential and cognitive enhancement

### Phase 4.5 Achievements 🎉
- **Anthropic API Optimization**: 150% response quality improvement with Claude-optimized prompts
- **Retry Logic Implementation**: Exponential backoff for API reliability and error handling
- **Service Monitoring**: Real-time health checks for all providers via `/api/monitoring/services`
- **Project State Synthesis**: 5 comprehensive project summaries automatically generated
- **Quality Monitoring Framework**: Response quality tracking and auto-tuning capabilities
- **Enhanced ML Chips**: 491 total chips including 14 new Anthropic optimization chips
- **Connection Monitoring**: Automatic service health detection and recovery
- **Documentation Refresh**: Complete API reference and implementation guides

### Phase 5.2 Achievements 🎉
- **Advanced Analytics**: Predictive analytics with AI-powered insights and anomaly detection
- **AI-Driven UX**: Intelligent user experience with personalization and behavior analysis
- **Cultural Evolution Breakthrough**: First successful ALIFE cultural transmission (17,205 transmissions)
- **Complex Cultural Systems**: Maximum protocol complexity achieved with multi-generational persistence
- **Performance Optimization**: Program Advance system with intelligent caching and auto-tuning
- **8 New API Endpoints**: Comprehensive analytics and UX capabilities
- **Scientific Leadership**: 19,889 protocols created across 5 generations with 109 cultural tags
| Image Gen | ✅ ComfyUI + SD 1.5 (RTX 3090) | `scripts/start_comfyui.sh` |
| VS Code | ✅ Extension installed | `faithh-vscode/` |

## Project Structure

```
ai-stack/
├── faithh_professional_backend_fixed.py  # Main backend (1,944 lines)
├── faithh_pet_v4.html                    # Frontend UI (5,034 lines)
├── config.yaml                           # Runtime config
├── docker-compose.yml                    # Ollama, ChromaDB, Langflow, Postgres
├── restart_backend.sh / stop_backend.sh  # Backend lifecycle
│
├── backend/                # Extracted backend modules
│   ├── data_loaders.py     #   JSON file I/O
│   ├── intent_detection.py #   Query intent analysis
│   ├── context_builders.py #   Context assembly + personality
│   └── llm_providers.py    #   Multi-provider LLM dispatch
│
├── scripts/                # One-off and utility scripts
├── docs/                   # Living documentation
├── tests/                  # Python + shell tests
├── ml/                     # ML pipeline (chip synthesis, LoRA training)
├── images/                 # Generated chip art + assets
├── faithh-vscode/          # VS Code extension source
├── knowledge_base/         # RAG indexing scripts
├── collectors/             # Passive data collectors
├── projects/               # Subprojects (Constella, Tom Cat Sound)
├── archive/                # Stale docs + old attempts
│
├── faithh_memory.json      # Persistent memory state
├── decisions_log.json      # Decision history
├── project_states.json     # Project phase tracking
├── scaffolding_state.json  # Structural awareness
├── AGENTS.md               # AI agent behavior rules
├── CONTEXT.md              # Session context for AI
└── SYSTEMS_MAP.md          # Full system architecture
```

## Key Commands

```bash
./restart_backend.sh                    # Start/restart backend
./stop_backend.sh                       # Stop backend
curl http://localhost:5557/health       # Health check
curl -s http://localhost:5557/api/plc/state | head -c 2000   # PLC + faithh_status (canonical)
python -m pytest tests/ -v             # Run tests
scripts/start_comfyui.sh               # Start ComfyUI on RTX 3090
```

## Hardware

- **WSL2**: Ryzen 9 3900X, 47GB RAM, RTX 3090 (24GB) + GTX 1080 Ti (11GB)
- **Gen8**: Xeon E3-1265L V2, 15GB RAM, ChromaDB + Docker services
- **Networking**: Gen8 services documented at LAN **192.158.1.243** (ChromaDB, SSH, metrics); workstation Tailscale IP varies by host.

## Documentation

| Doc | Purpose |
|-----|---------|
| `AGENTS.md` | Rules for AI agents working in this repo |
| `CONTEXT.md` | Current context snapshot for AI sessions |
| `SYSTEMS_MAP.md` | Full system architecture diagram |
| `docs/README.md` | Documentation master index |
| `docs/architecture/SYSTEM_OVERVIEW.md` | Technical architecture details |
| `docs/reference/LIFE_MAP.md` | Personal roadmap / true north |

## Status (2026-07-02)
Active. Gen8/NAS nodes are temporarily offline (Tailscale re-auth pending physical
access ~mid-July 2026); docs tagged `[VERIFY]` await that. Recent: docs corrected
against git receipts, business records relocated out of this repo, passthrough
runbook added (docs/PROXMOX_WIN11_PASSTHROUGH_RUNBOOK.md). License: MIT.

## The ecosystem (how this repo fits)

| Repo | Role |
|---|---|
| [constella-framework](https://github.com/Nightmarejam/constella-framework) | Civic governance framework — also the **logic basis** for everything here (confirmability tiers, concept lineage, Harmony bridge) |
| [faithh-pet-terminal](https://github.com/Nightmarejam/faithh-pet-terminal) | FAITHH — personal AI companion: Flask + ChromaDB RAG + vLLM on a Proxmox homelab |
| [SensorBridge](https://github.com/Nightmarejam/SensorBridge) | Host→VM hardware telemetry (gRPC/WMI); pivoted to node-health monitoring feeding FAITHH |
| [celestial-equilibrium](https://github.com/Nightmarejam/celestial-equilibrium) | Doctrine text (CC BY 4.0), consumed by constella as a submodule |
| [runbook-to-rule-them-all](https://github.com/Nightmarejam/runbook-to-rule-them-all) | Ops runbooks for the homelab systems |
| homelab / research-notes / tomcat-sound | Private: hardware+pipeline knowledge, theory notes, business records |

Work is human-directed and AI-assisted — see [PROVENANCE.md](PROVENANCE.md).
