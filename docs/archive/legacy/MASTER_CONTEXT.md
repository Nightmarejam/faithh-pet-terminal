# AI Stack - Master Context

**Last Updated:** 2026-01-25
**System Owner:** Jonathan (jonat)
**Primary Environment:** Ubuntu 22.04 (WSL2) + Gen8 Server (Ubuntu 22.04)

---

## System Overview

This is Jonathan's unified AI development and personal project management system. It integrates:
- Multi-LLM backend (Groq primary, Ollama local, Gemini optional)
- RAG-powered conversation indexing (32,499 chunks across 306 conversations)
- Real-time coherence detection
- Professional portfolio management (Tom Cat Sound LLC, Constella Harmony framework)
- Gen8 home server infrastructure (12 services: ChromaDB, Grafana, Prometheus, Gitea, Vaultwarden, Pi-hole, Docker Registry, Uptime Kuma, GitLab Runner, Node Exporter, Registry UI)

---

## Current Infrastructure

### Development Environment
- **Primary Machine:** DESKTOP-JJ1SUHB (WSL2, Ubuntu 24.04)
- **Working Directory:** `/home/jonat/ai-stack`
- **Python Environment:** venv with backend dependencies
- **Git Status:** Main branch, clean (head: 2d3a1f0)
- **Remote:** github.com:Nightmarejam/faithh-pet-terminal.git

### Gen8 Server (servicebox)
- **Hostname:** servicebox
- **IP Addresses:**
  - LAN: servicebox.taileb8c60.ts.net
  - Tailscale: servicebox.taileb8c60.ts.net
- **OS:** Ubuntu 22.04 LTS
- **Docker:** v28.2.2
- **User:** jonat
- **Status:** ✅ Online, SSH configured

#### Services Running on Gen8

**ChromaDB** (Production - deployed 2025-12-29, reindexed 2026-01-25)
- Location: `~/services/chromadb/`
- Port: 8000
- API: http://servicebox.taileb8c60.ts.net:8000
- Collection: `faithh_knowledge_base`
- Documents: 32,499 chunks
- Embedding: all-MiniLM-L6-v2 (384 dimensions)
- Status: ✅ Running, heartbeat OK

**Grafana** (Production - deployed 2026-01-20)
- Port: 3000
- URL: http://servicebox.taileb8c60.ts.net:3000
- Credentials: admin/Grafana2026!
- Status: ✅ Running

**Gitea** (Production - deployed 2026-01-20)
- HTTP Port: 3002, SSH Port: 2222
- URL: http://servicebox.taileb8c60.ts.net:3002
- Status: ✅ Running

**Vaultwarden** (Production - deployed 2026-01-20)
- Port: 8080
- URL: http://servicebox.taileb8c60.ts.net:8080
- Status: ✅ Running

**Pi-hole** (Production - deployed 2025-12-20)
- Location: `~/services/pihole/`
- DNS: Port 53 (UDP/TCP)
- Web UI: http://servicebox.taileb8c60.ts.net/admin
- Credentials: admin/PiHole2026!
- Upstream DNS: Cloudflare (1.1.1.1, 8.8.8.8)
- Status: ✅ Running

**Prometheus** (Production - deployed 2026-01-20)
- Port: 9090
- URL: http://servicebox.taileb8c60.ts.net:9090
- Status: ✅ Running

**Docker Registry** (Production - deployed 2026-01-20)
- Registry Port: 5000, UI Port: 5001
- URL: http://servicebox.taileb8c60.ts.net:5001
- Status: ✅ Running

**Uptime Kuma** (Production - deployed 2026-01-20)
- Port: 3001
- URL: http://servicebox.taileb8c60.ts.net:3001
- Status: ✅ Running

**GitLab Runner** (Production - deployed 2026-01-20)
- Status: ✅ Running

**Node Exporter** (Production - deployed 2026-01-20)
- Port: 9100
- Status: ✅ Running

---

## RAG System Status

### Current State (as of 2026-01-25)
- **Collection:** `faithh_knowledge_base`
- **Total Chunks:** 32,499 (properly chunked with 1500 char chunks, 200 char overlap)
- **Conversations:** 306 total (208 ChatGPT + 98 Claude)
- **Date Range:** Feb 2024 → Jan 2026 (full history)
- **ChatGPT Chunks:** 28,255
- **Claude Chunks:** 4,244
- **Embedding Model:** all-MiniLM-L6-v2 (384 dimensions)
- **Database:** Gen8 ChromaDB (http://servicebox.taileb8c60.ts.net:8000)
- **Status:** ✅ Properly chunked for semantic search, fully indexed

### Recent Changes
- **2026-01-25:** Proper chunking reindex - 32,499 chunks (1500 chars, 200 overlap)
- **2026-01-25:** Gen8 infrastructure complete - 12 services deployed
- **2026-01-20:** Vaultwarden, Grafana, Gitea, monitoring stack deployed
- **2026-01-18:** Pulse Security integrated (scanner, healer, audit)
- **2026-01-18:** Automated ChromaDB backups configured (daily 3 AM)
- **2026-01-08:** Automated `project_states.json` updater deployed
- **2025-12-29:** Migrated ChromaDB to Gen8 server

### Maintenance Commands
```bash
# Check ChromaDB health
curl -s "http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat"

# Update project_states.json automatically
python3 scripts/maintenance/update_project_states.py --write

# Preview changes without writing
python3 scripts/maintenance/update_project_states.py --diff
```

---

## Backend Components

### Core Files
- `faithh_professional_backend_fixed.py` - Main backend (port 5557)
- `backend/llm_providers.py` - Multi-provider abstraction
- `backend/coherence_sensor.py` - Real-time coherence detection
- `backend/rag_processor.py` - RAG indexing pipeline

### Supported LLM Providers
1. **Groq** - Primary (llama-3.3-70b-versatile, fast cloud inference)
2. **Ollama** - Local fallback (llama31-faithh:latest, qwen3-faithh:latest via localhost:11434)
3. **Gemini** - Optional (Gemini 2.0 Flash via API key)

### Frontend
- **Canonical UI:** `faithh_pet_v4.html` (ROOT level - served by backend)
- **Legacy:** `faithh_pet.html` (same content, legacy name)
- **Note:** `active/frontend/faithh_pet_v4.html` is outdated - DO NOT EDIT

### Features
- Streaming support
- Token counting
- Error handling and retries
- Provider failover (Groq → Gemini → Ollama)
- Coherence scoring (experimental)
- **Pulse Security** (scanner, healer, audit - integrated 2026-01-18)

---

## Active Projects

### 1. FAITHH (AI Stack)
**Status:** Phase 2 Complete / Phase 3 Planning
**Priority:** High

Core AI assistant with RAG integration. See `project_states.json` for full details.

### 2. Tom Cat Sound LLC
**Path:** `projects/tomcat-sound/`
**Status:** Active business entity
**Priority:** High

Audio engineering and production business. Financial tracking and grant applications in progress.

### 3. Constella Harmony Framework
**Path:** `projects/constella-framework/` (git submodule)
**Status:** Phase 1 Integration
**Priority:** Medium

Personal framework for multi-modal creativity and coherence detection.

---

## Quick Reference

### Start Backend
```bash
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend_fixed.py
```

### SSH to Gen8
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
```

### Check System Status
```bash
# Backend health
curl -s http://localhost:5557/health | jq

# ChromaDB health  
curl -s "http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat"

# Update project states
python3 scripts/maintenance/update_project_states.py --diff
```

### Git Workflow
```bash
# Standard commit
git add -A && git commit -m "Session 2026-01-08: [description]"

# Push to remote
git push
```

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `project_states.json` | Machine-readable system state (source of truth) |
| `MASTER_CONTEXT.md` | This file - human-readable overview |
| `docs/GPT_PROJECT_CONTEXT.md` | ChatGPT-specific context |
| `docs/CONTEXT_PARITY_GUIDE.md` | How to keep context files in sync |
| `docs/UPDATE_PROTOCOL.md` | Session handoff procedures |
| `LIFE_MAP.md` | Life goals and project priorities |

### Session Reports
All session logs in `docs/session-reports/` - check latest for current state.

---

## Environment Configuration

### Required Environment Variables (`.env`)
```bash
GROQ_API_KEY=<key>
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
CHROMA_URL=http://servicebox.taileb8c60.ts.net:8000
OLLAMA_READ_TIMEOUT=180
```

### Optional
```bash
GEMINI_API_KEY=<key>  # For Gemini fallback
```

---

## Submodules

| Path | Repository | Purpose |
|------|------------|---------|
| `projects/constella-framework` | github.com:Nightmarejam/constella-framework | Constella Harmony framework |
| `projects/constella-framework/docs/celestial-equilibrium` | (nested) | Philosophy documentation |

Update submodules: `git submodule update --init --recursive`

---

**End of Master Context**

*For update procedures, see: `docs/UPDATE_PROTOCOL.md`*
*For context sync rules, see: `docs/CONTEXT_PARITY_GUIDE.md`*
