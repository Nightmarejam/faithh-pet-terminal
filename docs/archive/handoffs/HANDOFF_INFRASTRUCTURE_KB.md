# AI Handoff: Infrastructure Knowledge Base Project

**Created:** 2026-01-13
**Context:** Claude.ai conversation with Jonathan
**Next AI:** Continue building the Infrastructure Knowledge Base for ai-stack
**Priority:** High - foundational work that enables everything else

---

## Executive Summary

Jonathan is building a comprehensive, machine-readable documentation system for his entire personal infrastructure. The goal is a "living system map" that:

1. Any AI can understand instantly (machine-readable JSON + human-readable MD)
2. Jonathan can recover context after being away for weeks
3. New tools/services get documented as they're added
4. Captures both WHAT exists and HOW to use it

We decided on **Option C: Build both schema and collectors iteratively**, starting with `ai-stack` (the most complex component).

---

## What Was Built This Session

### 1. Compass Dashboard (COMPLETE ✅)

A new tab in FAITHH PET Terminal for visualizing project states.

**Files Modified:**
- `faithh_professional_backend_fixed.py` - Added `/api/compass` and `/api/compass/log` endpoints
- `faithh_pet.html` - Added COMPASS tab, CSS, JavaScript

**Features:**
- Visual project nodes with status colors
- Quick Log panel for interstitial journaling
- "Adjacent Possible" section showing aggregated next steps
- Creates `work_log.json` automatically

**Status:** Implemented by Claude Code, tested and working.

### 2. Weekly Synthesis Job (COMPLETE ✅)

Transforms work log entries into journal-like insights - "journal yourself without journaling."

**Files Created:**
- `weekly_synthesis.py` - Main synthesis script
- `SYNTHESIS_SETUP.md` - Installation guide
- `example_synthesis.md` - Example output

**Features:**
- Analyzes work log entries for patterns
- Detects: focus areas, neglected projects, best days, time preferences, context switching
- Outputs both JSON (machine) and Markdown (human)
- Optional `--use-llm` flag for AI-generated reflection paragraph

**Status:** Script created, needs to be copied to `~/ai-stack/scripts/` and tested.

### 3. Infrastructure Knowledge Base (IN PROGRESS 🔄)

**This is the next major task.**

---

## The Infrastructure Knowledge Base Vision

### Problem Statement

Jonathan has a growing multi-machine infrastructure:
- Windows Desktop (gaming, VSCode, browser)
- WSL2 Ubuntu (ai-stack, FAITHH, Docker, Ollama)
- Gen8 MicroServer (ChromaDB, Pi-hole, future services)
- MacBook Pro (mobile development, Tailscale access)
- Cloud services (Groq API, GitHub, Claude.ai)

Currently, this knowledge is scattered across:
- `MASTER_CONTEXT.md` - High-level overview
- `project_states.json` - Project status (auto-updated)
- `dev_environment.md` - Some hardware details
- Various handoff docs in `docs/`
- ChatGPT conversation history (system monitoring scripts)

**Goal:** Unify into a single, structured, living knowledge base.

### Proposed Structure

```
~/ai-stack/infrastructure/
├── SYSTEM_MAP.json          # Machine-readable complete topology
├── SYSTEM_MAP.md            # Human-readable overview (auto-generated from JSON)
├── units/
│   ├── windows_desktop.md   # Per-unit runbooks
│   ├── wsl2_ubuntu.md
│   ├── gen8_server.md
│   └── macbook_pro.md
├── services/
│   ├── faithh.md            # Per-service documentation
│   ├── chromadb.md
│   ├── ollama.md
│   └── pihole.md
├── practices/
│   ├── daily_startup.md     # Standard operating procedures
│   ├── weekly_maintenance.md
│   └── recovery_procedures.md
└── collectors/
    ├── collect_wsl_state.py  # Auto-populate from live systems
    ├── collect_gen8_state.py
    └── reconcile_all.py      # Sync everything, detect drift
```

### What Each Unit Doc Should Capture

| Category | Fields |
|----------|--------|
| **Identity** | hostname, os, os_version, role, ip_lan, ip_tailscale |
| **Hardware** | cpu, ram, gpus[], storage[] |
| **Services** | name, port, health_endpoint, status, dependencies |
| **Access** | ssh_command, credentials_location, quick_connect |
| **Practices** | common_commands[], startup_procedure, maintenance_tasks[] |
| **Dependencies** | depends_on[], depended_by[] |
| **State Files** | config_paths[], backup_paths[], logs[] |

### Schema Design Considerations

1. **Machine-readable first** - JSON as source of truth, Markdown generated
2. **Hierarchical** - System → Units → Services → Endpoints
3. **Validatable** - Schema that can be checked for completeness
4. **Auto-discoverable where possible** - Collectors fill in what they can
5. **Human-annotated layer** - Practices, tips, "why" explanations

---

## Existing System State Tools

Jonathan already built (with ChatGPT) a system monitoring framework:

**Location:** `~/ai-stack/scripts/` and `~/ai-stack/parity/`

**Components:**
1. `collect_system_state.py` - Snapshots hardware, Docker, services, GPUs
2. `monitor_daemon.py` - Continuous monitoring with alerts
3. `sysq` - CLI tool for quick queries
4. Output files:
   - `parity/system_state_latest.json` - Full system state
   - `parity/live_status.json` - Quick status
   - `parity/ai_readable_summary.md` - For AI consumption

**Key Insight:** The collector already gathers a lot of live state. The Infrastructure Knowledge Base should:
- USE this collected data as input
- ADD static documentation (practices, access, rationale)
- RECONCILE live state against documented expectations

---

## Passive Data Sources for Journaling

Jonathan wants to capture work he does but forgets to log. Available sources:

| Source | Location | Effort |
|--------|----------|--------|
| Git commits | `~/ai-stack/.git` | Easy |
| File modification times | filesystem | Easy |
| Terminal history | `~/.bash_history` | Easy |
| AI conversation exports | `~/ai-stack/AI_Chat_Exports/` | Medium |
| ChromaDB indexing activity | logs | Easy |
| Session reports | `~/ai-stack/docs/session-reports/` | Easy |

**Proposed:** A reconciliation job that compares `work_log.json` against git/file activity and surfaces gaps.

---

## Jonathan's Infrastructure Overview

### Windows Desktop (DESKTOP-JJ1SUHB)

**Role:** Primary workstation, gaming, development via WSL2

**Hardware:**
- CPU: 12 cores / 24 threads
- RAM: 64GB (47GB visible to system per monitoring)
- GPU 0: GTX 1080 Ti 11GB (gaming, light inference)
- GPU 1: RTX 3090 24GB (heavy AI inference)
- Storage: Multiple drives (details TBD)

**Key Software:**
- Windows 10/11
- WSL2 with Ubuntu
- VSCode with Continue extension
- Docker Desktop (drives WSL2 Docker)

### WSL2 Ubuntu (ai-stack environment)

**Role:** Primary development environment, AI services

**Path:** `\\wsl.localhost\Ubuntu\home\jonat\ai-stack`

**Services Running (Docker):**
- `ollama` (port 11434) - Main LLM inference
- `ollama-embed` (port 11435) - Embeddings
- `ollama-qwen` (port 11436) - Qwen-specific
- `chromadb` (port 8000) - Local vector DB (backup, not primary)
- `langflow` (port 7860) - Visual LLM workflows
- `postgres` - Langflow database

**Non-Docker Services:**
- FAITHH backend (port 5557) - Python Flask app
- Various Python scripts in venv

**Key Files:**
- `faithh_professional_backend_fixed.py` - Main backend
- `faithh_pet.html` - Main UI
- `project_states.json` - Auto-updated project state
- `work_log.json` - Work logging (new)
- `docker-compose.yml` - Service definitions

### Gen8 MicroServer (servicebox)

**Role:** Always-on home server for persistent services

**Hardware:**
- HP ProLiant MicroServer Gen8
- CPU: Intel Xeon E3-1265L v2
- RAM: 16GB DDR3-1600 ECC
- OS: Ubuntu 22.04 LTS
- Docker: v28.2.2

**Network:**
- LAN: servicebox.taileb8c60.ts.net
- Tailscale: servicebox.taileb8c60.ts.net

**Services:**
- ChromaDB (port 8000) - **PRIMARY** knowledge base
  - Collection: `faithh_knowledge_base`
  - Documents: 28,876 chunks
  - Embedding: BGE-base-en-v1.5 (768-dim)
- Pi-hole (port 53/80) - Network DNS filtering

**SSH Access:**
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
```

### MacBook Pro

**Role:** Mobile development, remote access via Tailscale

**Details:** TBD - needs documentation

### Cloud Services

- **Groq API** - Primary LLM provider (llama-3.3-70b-versatile)
- **GitHub** - Code hosting (github.com:Nightmarejam/faithh-pet-terminal.git)
- **Claude.ai** - AI assistant (this conversation)
- **ChatGPT** - AI assistant (system monitoring work)

---

## Immediate Next Steps for Continuing AI

### Priority 1: Define the Schema

Create `SYSTEM_MAP.schema.json` that defines:
- Required fields for each unit type
- Required fields for each service type
- Validation rules
- Examples

### Priority 2: Build WSL2 Collector

Extend or adapt `collect_system_state.py` to output in the new schema format:
- Hardware details
- Docker services with health status
- Non-Docker services
- Key file locations
- Git status

### Priority 3: Create Template Unit Doc

Build `units/wsl2_ubuntu.md` as the reference template:
- Auto-generated sections (from collector)
- Manual sections (practices, tips, rationale)
- Clear separation between dynamic and static content

### Priority 4: Reconciliation Logic

Build a script that:
- Loads the schema/expected state
- Runs collectors for live state
- Compares and reports drift
- Optionally auto-updates dynamic sections

---

## Questions for Jonathan (When Resuming)

1. **Documentation audience priority** - Is this primarily for:
   - (a) AI assistants to understand your system quickly
   - (b) Your future self recovering context
   - (c) Potentially onboarding others / making this a template for "AI Companion Starter Kit"

2. **Automation vs accuracy tradeoff** - Prefer:
   - (a) Auto-generated with manual annotation layer
   - (b) Curated docs with auto-validation

3. **Scope of ai-stack docs** - Should capture:
   - Just software/services?
   - Hardware context (dual GPU setup)?
   - Data flows (what gets indexed where)?
   - Workflows (how you typically use it day-to-day)?

---

## Files to Reference

| File | Purpose |
|------|---------|
| `/mnt/project/MASTER_CONTEXT.md` | Current high-level system overview |
| `/mnt/project/project_states.json` | Auto-updated project states |
| `~/ai-stack/parity/system_state_latest.json` | Live system snapshot |
| `~/ai-stack/scripts/collect_system_state.py` | Existing collector |
| `~/ai-stack/docker-compose.yml` | Docker service definitions |
| `~/ai-stack/docs/GEN8_SERVICES_PLAN.md` | Gen8 documentation |

---

## Session Context

This conversation covered:
1. Jonathan feeling at a roadblock - needs clarity on priorities
2. Research on PKM tools, visual dashboards, organic project tracking
3. Building Compass Dashboard (implemented via Claude Code)
4. Weekly Synthesis job for "journaling without journaling"
5. Passive data capture discussion (git, files, AI conversations)
6. Infrastructure Knowledge Base vision and planning

The thread connects to parallel work Jonathan did with ChatGPT on:
- GPU optimization scripts
- System state monitoring (`collect_system_state.py`)
- `sysq` CLI tool
- Intent mapping for GPU roles

---

## Tone and Approach Notes

Jonathan appreciates:
- Direct, practical solutions over theoretical discussions
- Building iteratively rather than big-bang designs
- Machine-readable outputs that AI can query
- Systems that "journal themselves" - low friction capture
- Organic, interconnected views rather than rigid task lists

He's currently not working (mentioned bankruptcy timeline), so has time to invest in infrastructure but needs systems that help him focus rather than add overhead.

---

**End of Handoff**

*This document should give any AI enough context to continue the Infrastructure Knowledge Base work without re-explaining the full background.*
