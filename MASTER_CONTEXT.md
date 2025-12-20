# AI Stack - Master Context

**Last Updated:** 2025-12-20
**System Owner:** Jonathan (jonat)
**Primary Environment:** Ubuntu 22.04 (WSL2) + Gen8 Server (Ubuntu 22.04)

---

## System Overview

This is Jonathan's unified AI development and personal project management system. It integrates:
- Multi-LLM backend (OpenRouter, Anthropic, local inference)
- RAG-powered conversation indexing (27,732 chunks from ChatGPT exports)
- Real-time coherence detection
- Professional portfolio management (Tom Cat Sound LLC, Constella Harmony framework)
- Gen8 home server infrastructure

---

## Current Infrastructure

### Development Environment
- **Primary Machine:** DESKTOP-JJ1SUHB (WSL2, Ubuntu)
- **Working Directory:** `/home/jonat/ai-stack`
- **Python Environment:** venv with backend dependencies
- **Git Status:** Main branch, multiple uncommitted projects/docs

### Gen8 Server (servicebox)
- **Hostname:** servicebox
- **IP Addresses:**
  - LAN: 192.158.1.243
  - Tailscale: 100.79.85.32
- **OS:** Ubuntu 22.04 LTS
- **Docker:** v28.2.2
- **User:** jonat
- **Status:** ✓ Online, SSH configured

#### Services Running on Gen8
- **Pi-hole** (as of 2025-12-20)
  - Location: `~/services/pihole/`
  - DNS: Port 53 (UDP/TCP)
  - Web UI: Port 80 (http://192.158.1.243/admin)
  - Upstream DNS: Cloudflare (1.1.1.1, 1.0.0.1)
  - Container: `pihole` (docker-compose)
  - Password: changeme123 (needs update)
  - Status: ✓ Running and tested

### Planned Services (Gen8)
- [ ] ChromaDB (tiered RAG architecture) - design doc created
- [ ] Local LLM inference (Ollama/llama.cpp)
- [ ] Backup/sync services
- [ ] Media server (optional)

---

## RAG System Status

### Current State
- **Collection:** `documents_768`
- **Documents:** 93,000+ (from multiple indexing runs)
- **Chunks Prepared:** 27,732 (from latest ChatGPT export)
- **Embedding Model:** text-embedding-3-small (768 dimensions)
- **Database:** Local ChromaDB (single-tier)
- **Location:** `~/ai-stack/chroma_db/`

### Known Issues
- Duplicate indexing (ran multiple times without cleanup)
- No metadata tracking (can't identify source conversations)
- Single-tier architecture (all local, no tiering)

### Planned Improvements
- **Tiered Database Architecture** (design doc: `docs/TIERED_DATABASE_DESIGN.md`)
  - Tier 1: Hot cache (local)
  - Tier 2: Full corpus (Gen8 ChromaDB)
  - Tier 3: Archive (optional)
- Re-index with metadata tracking
- Migrate to Gen8 for primary storage

---

## Backend Components

### Core Files
- `backend/llm_providers.py` - Multi-provider abstraction (OpenRouter, Anthropic, local)
- `backend/coherence_sensor.py` - Real-time coherence detection
- `backend/rag_processor.py` - RAG indexing pipeline
- `configs/model_config.yaml` - LLM model configuration

### Supported LLM Providers
1. **OpenRouter** - Primary (GPT-4, Claude, Gemini, etc.)
2. **Anthropic Direct** - Claude models
3. **Local Inference** - Planned (Ollama/llama.cpp on Gen8)

### Features
- Streaming support
- Token counting
- Error handling and retries
- Provider failover
- Coherence scoring (experimental)

---

## Active Projects

### 1. Tom Cat Sound LLC
**Path:** `projects/tomcat-sound/`
**Status:** Active business entity
**Priority:** High

**Components:**
- Financial records (ledger, Venmo statements)
- Client payment tracking
- Equipment inventory
- Business documentation (EIN, operating agreement, insurance)
- Grant research and applications

**Recent Work:**
- Equipment inventory analysis (Dec 2025)
- Client payment reconciliation
- Financial tracking setup
- Grant opportunity research

**Next Steps:**
- Complete financial reconciliation
- File quarterly taxes
- Update equipment inventory
- Apply for identified grants

### 2. Constella Harmony Framework
**Path:** `projects/constella-framework/`
**Status:** Active development
**Priority:** Medium

**Description:** Personal framework for multi-modal creativity and coherence detection.

**Components:**
- Coherence sensing algorithms
- Multi-modal integration (text, audio, visual)
- Real-time feedback systems
- Documentation framework

**Recent Work:**
- Framework organization and structure
- Documentation setup
- Integration planning

**Next Steps:**
- Complete Phase 1 integration (see PHASE1_INTEGRATION_GUIDE.md)
- Implement coherence sensors
- Build example applications

### 3. AI Stack Enhancement
**Status:** Ongoing
**Priority:** High

**Focus Areas:**
- RAG system improvement (tiered architecture)
- Gen8 server setup and services
- Backend reliability and testing
- Multi-LLM provider support

---

## Development Workflow

### Daily Operations
1. Work in `/home/jonat/ai-stack`
2. Use venv for Python dependencies
3. Test locally before deploying to Gen8
4. Document all sessions in `docs/session-reports/`

### Session Protocol
1. Start: Review MASTER_CONTEXT.md and latest session report
2. During: Update project_states.json as work progresses
3. End: Create session report, update docs, commit changes
4. See: `docs/UPDATE_PROTOCOL.md` for detailed checklist

### Git Workflow
- **Branch:** main (no feature branches currently)
- **Commit frequency:** End of logical work units
- **Push policy:** Manual only (not automatic)
- **Convention:** "Session YYYY-MM-DD: [accomplishment]"

---

## Key Documentation

### Setup & Infrastructure
- `docs/GEN8_SETUP_CHECKLIST.md` - Server setup guide
- `docs/UPDATE_PROTOCOL.md` - Session handoff procedures
- `docs/gen8-docker-compose.yml` - Planned service definitions

### Architecture & Design
- `docs/TIERED_DATABASE_DESIGN.md` - RAG architecture plan
- `PHASE1_INTEGRATION_GUIDE.md` - Constella Harmony integration
- `docs/PORTFOLIO_OVERVIEW.md` - Project portfolio summary

### Session History
- `docs/session-reports/` - Chronological session logs
- `docs/CLAUDE_CODE_HANDOFF_PHASE2.md` - Phase 2 planning
- `docs/compass_artifact_wf-*.md` - Archived design docs

---

## Scripts & Utilities

### RAG Scripts
- `scripts/extract_recent_gpt.py` - Extract recent ChatGPT conversations
- `scripts/extract_specific_convos.py` - Extract by ID/date
- `scripts/list_recent_gpt.py` - List available conversations
- `scripts/search_embedding_convos.py` - Search embeddings
- `scripts/analyze_rag_metadata.py` - Analyze RAG metadata
- `scripts/audit_exports.py` - Audit export quality

### Testing
- `tests/test_rag_quality.py` - RAG stress tests (27k chunks)

### System Scripts
- `add_harmony_docs.py` - Add Constella docs to RAG
- Gaming/dev mode scripts (created, not yet committed)

---

## Configuration Files

### Active Configs
- `configs/model_config.yaml` - LLM provider settings
- `.claude/settings.local.json` - Claude Code settings
- `backend/` - Python backend modules

### Backups
- `configs/model_config.yaml.bak` - Config backup

---

## Current Session State (2025-12-20)

### Completed Today
✓ SSH key setup for Gen8 (servicebox)
✓ Pi-hole installation and configuration
✓ Port 53 conflict resolution (systemd-resolved)
✓ Pi-hole verification (DNS + Web UI)
✓ UPDATE_PROTOCOL.md creation
✓ MASTER_CONTEXT.md creation (this file)

### In Progress
- Session report creation
- project_states.json update
- TIERED_DATABASE_DESIGN.md creation
- Git commit of all changes

### Next Session Priorities
1. Change Pi-hole web password
2. Configure devices to use Pi-hole DNS
3. Set up ChromaDB on Gen8
4. Re-index RAG with metadata tracking
5. Continue Constella Harmony integration

---

## Quick Reference

### SSH to Gen8
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@100.79.85.32
# or
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243
```

### Pi-hole Access
- Web: http://192.158.1.243/admin (or http://100.79.85.32/admin)
- Password: changeme123
- Change password: `docker exec -it pihole pihole -a -p`

### RAG Status Check
```bash
cd ~/ai-stack
python -c "from backend.rag_processor import RAGProcessor; r = RAGProcessor(); print(r.collection.count())"
```

### Start Backend
```bash
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend_fixed.py
```

---

## Important Notes

1. **RAG Needs Cleanup:** 93k documents includes duplicates; need full re-index
2. **Gen8 Services Isolated:** Using docker-compose per service (no shared compose file yet)
3. **No Auto-Push:** All git commits are local until explicitly pushed
4. **Session Reports Required:** Every session should create a report in docs/session-reports/
5. **Pi-hole Password:** Currently "changeme123" - change on next access

---

**End of Master Context**
For update procedures, see: `docs/UPDATE_PROTOCOL.md`
