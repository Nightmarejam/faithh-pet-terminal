# Jonathan's Systems Map
<!-- 
  Created: 2026-02-07
  Purpose: Comprehensive, machine-readable map of all projects, infrastructure, 
           relationships, and current state. Designed for AI context injection.
  Maintainer: Jonathan + AI assistants
  Usage: Hand this to any AI session for instant orientation.
-->

---
type: systems_map
version: "2.0"
created: "2026-02-07"
last_verified: "2026-05-19"
owner: "Jonathan Morales"
---

## Identity

**Name:** Jonathan Morales  
**Role:** Audio Producer & AI Developer  
**Location:** Oregon  
**Core Challenge:** Maintaining project coherence when attention shifts between multiple long-term projects (ADHD)  
**Driving Question:** *"How do we build systems that actually serve people well?"*  
**Philosophy:** Celestial Equilibrium — resonance, harmonic alignment, dignity

---

## Project Inventory

### 1. FAITHH (Friendly AI Teaching & Helping Hub)
```yaml
type: ai_system
status: active
phase: "Phase 4 — IME, journal synthesis, production hardening"
location: ~/ai-stack/
theme: "MegaMan Battle Network"
purpose: "Thought partner that maintains project coherence when attention shifts"
not: "A search engine or Q&A bot"

phase_history:
  phase_1: "Core RAG + ChromaDB setup — complete"
  phase_2: "Backend v4.0-pulse, PULSE engine (3 tiers), ML chips — complete"
  phase_3: "Coherence Arbiter (convergence + anchor validation), threading fix — complete 2026-02-23"
  phase_4: "IME scaffold, journal synthesis, harmony docs indexed, production hardening — IN PROGRESS"

architecture:
  backend: faithh_professional_backend_fixed.py (Flask, port 5557, faithhvm Ubuntu, threaded=True)
  frontend: faithh_pet_v4.html (MegaMan Battle Network UI)
  database: ChromaDB on Gen8 (192.158.1.10:8000)
  collection: faithh_knowledge_base
  chunks: 38294 (as of 2026-03-01, includes harmony/IME docs)
  conversations_indexed: 306 (208 ChatGPT + 98 Claude)
  embedding: BAAI/bge-base-en-v1.5 (768-dim)  # migrated 2026-05-17, commit c8f7938
  ime: ime/ directory — C++ scaffold, reads journal entries, resonance gating (4 tests passing)
  llm_providers:
    - "vLLM (faithh RTX 3090) — qwen3-coder-30b-a3b-awq, :8000, 49K context, tool calling"
    - "cc_proxy — Claude Code → vLLM, :5558"
    - "Groq — cloud fallback (model_config.yaml)"
    - "Ollama — :11434 local"
    - "Gemini 2.0 Flash — cloud"

subsystems:
  memory:
    hot: "Current session state (RAM)"
    warm: "faithh_memory.json (persistent user/project context)"
    cold: "ChromaDB (32,499 chunks, semantic search)"
  scaffolding:
    file: scaffolding_state.json
    purpose: "Session continuity — open loops, parked tangents, orientation"
  pulse:
    status: "research phase"
    purpose: "AI immune system — security, pattern monitoring"
    files: [pulse_monitor.py, pulse_pattern_tracker.py, pulse_patterns.json]
  chips:
    status: "research phase"
    purpose: "MegaMan-inspired skill/discovery system — learns user patterns"
    files: [personalized_chips.json, filesystem_chip.py]
    research: [RESEARCH_HANDOFF_ChipSynthesis_v2_combined.md, RESEARCH_HANDOFF_ChipSynthesis_ML_Avatar_2026-02-04.md]
  context_injection:
    status: "built, needs refresh"
    purpose: "Generate unified AI context doc from source files"
    files: [scripts/generate_context.py, CONTEXT.md, templates/CONTEXT_TEMPLATE.md]
    snapshots: snapshots/framing/

key_files:
  - faithh_professional_backend_fixed.py  # canonical backend
  - faithh_pet_v4.html                    # canonical frontend (ROOT level)
  - faithh_memory.json                    # AI self-awareness + user profile
  - faithh_knowledge_graph.yaml           # graph: entities, relationships, rules
  - project_states.json                   # machine-readable project state
  - decisions_log.json                    # decision history with rationale
  - scaffolding_state.json                # session continuity
  - config.yaml                           # runtime config
  - docker-compose.yml                    # external services
```

### 2. Tom Cat Sound LLC (dba Floating Garden Soundworks)
```yaml
type: business
status: active
phase: "Operations & Growth"
location: ~/ai-stack/projects/tomcat-sound/
jurisdiction: Oregon
ein: "99-2000135"
formed: "2024-03-19"

partners:
  jonathan: { ownership: 0.34, role: "Manager", location: "Oregon", status: "active" }
  thomas:   { ownership: 0.33, role: "Member",  location: "South Dakota", status: "active" }
  kevin:    { ownership: 0.33, role: "Member",  status: "exiting", buyout: 0 }
post_exit_ownership: { jonathan: 0.51, thomas: 0.49 }

revenue:
  equipment_resale: { total: 33000, platforms: ["Reverb", "eBay", "local"] }
  audio_services:   { total: 3625 }
monthly_overhead: 574  # rent 400, insurance 44, software 40, internet 40, misc 50

equipment_value: 74941  # business 46167 + personal 19175

recent_work:  # as of Feb 2026
  - "2024 tax package COMPLETED (Jan 26, 2026) — CPA_PACKAGE_2024/"
  - "NAS setup for partner access — /mnt/z/Business/TomCatSound_LLC/2024_Tax_Filing/"
  - "Equipment inventory: 192 items cataloged"
  - "Bank transactions: 1,058 extracted from Chase/SoFi PDFs"
  - "Net operating loss: ~$10,509.90 (deductions for all partners)"

outstanding:
  - "Form 1065 filing (pending, with First Time Penalty Abatement)"
  - "Kevin Dunn exit (sign withdrawal agreement, file OR SOS amendment)"
  - "Operating Agreement update post-Kevin"
  - "Business bank account opening"
  - "Collect: rent/insurance receipts, Daniel Baker invoices, partner addresses"

tools:
  daw: Luna DAW
  mastering: WaveLab 11.2
  interface_main: UAD Volt 1
  interface_recording: PreSonus Studio 1810c
  remote_audio: SonoBus
  monitoring: Sonarworks reference
```

### 3. Constella Framework
```yaml
type: framework
status: active (documentation phase)
phase: "Phase 1 Integration"
version: "v1.5.x"
location: ~/ai-stack/projects/constella-framework/
repository: github.com/Nightmarejam
purpose: "Civic governance system — token-based community decision-making"
philosophy: "Celestial Equilibrium — governance through resonance, dignity, renewal"

key_concepts:
  astris:  { type: "soul-bound merit token", decay: "2% weekly" }
  auctor:  { type: "fixed-pool civic voice token", decay: "5% quarterly" }
  penumbra_accord: "Restorative justice: mediation → repair → reintegration"
  ucf: "Universal Civic Floor — baseline resource allocation"
  civic_tome: "Living governance document"

indexed_in_faithh: true
documents_count: 1904
conversations: "88,000+ lines of design reasoning"

applications: ["Neighborhood associations", "Cooperatives", "Intentional communities", "Municipal participatory budgeting"]

open_questions:
  - "Facilitator load caps"
  - "Tie-break protocol refinements"
  - "Cross-vault rebalancing guardrails"
```

### 4. ComfyUI / Image Generation
```yaml
type: creative_tool
status: setup_complete
purpose: "Local image generation with RTX 3090"
location: "Outside ai-stack (exact path needs verification)"
tools: [ComfyUI, Stable Diffusion]
use_case: "Custom UI elements and artwork for FAITHH and other projects"
```

---


### Claude Code local stack (faithhvm)
```yaml
host: faithhvm
local_ip: 192.158.1.100
gpu: NVIDIA RTX 3090 24GB (passthrough)
model: qwen3-coder-30b-a3b-awq
model_path: ~/models/qwen3-coder-30b-a3b-awq/
vllm:
  port: 8000
  max_model_len: 49152  # tune via start_vllm.sh; fp8 KV cache
  aliases: [qwen3-coder-30b, claude-sonnet-4-6, claude-opus-4-7]
cc_proxy:
  port: 5558
  role: caps max_tokens, 413 on input overflow
claude_code_env:
  ANTHROPIC_BASE_URL: http://localhost:5558
  ANTHROPIC_API_KEY: faithh-local
workflow: "/compact every 2-3 tool-heavy turns; see ~/ai-stack/CLAUDE.md"
samba_mount: //192.158.1.10/shared on /mnt/shared
```

## Infrastructure

### Hardware
```yaml
windows_desktop:
  hostname: DESKTOP-JJ1SUHB
  os: "Windows 11 + WSL2 Ubuntu 24.04"
  cpu: "AMD Ryzen 9 3900X (12C/24T)"
  ram: "64GB DDR4-3200"
  gpu_primary: "RTX 3090 24GB (AI inference, slot: PCIe Gen3 x16)"
  gpu_secondary: "GTX 1080 Ti 11GB (display/streaming)"
  storage:
    c_drive: "Samsung 970 EVO 1TB NVMe (62% used)"
    e_drive: "1.81TB SSD (51% free)"
    d_drive: "WD My Passport 931GB (backup)"
  psu: "FSP PT-1000FM 1000W Platinum"
  role: "Primary workstation — development, AI inference, audio production"
  local_ip: 192.158.1.232
  tailscale_ip: 100.115.225.100

gen8_server:
  hostname: servicebox
  model: "HP ProLiant MicroServer Gen8"
  os: "Ubuntu 22.04 LTS"
  cpu: "Intel Xeon E3-1265L v2 (4C/8T)"
  ram: "15GB DDR3 ECC"
  storage: "915GB available"
  docker: v28.2.2
  local_ip: 192.158.1.10  # gen8 servicebox
  tailscale_ip: "mesh-specific (see tailscale status); Chroma/SSH in docs use local_ip"
  role: "Infrastructure server — 12 Docker services"

macbook:
  model: "MacBook Pro M1"
  ram: "Unknown (verify)"
  storage: "500GB"
  local_ip: 192.158.1.132
  tailscale_ip: 100.122.56.106
  role: "Mobile workstation — mastering, FAITHH Lite, Constella dev"
  software: [FAITHH Lite, Ollama, WaveLab, Luna DAW]

synology_nas:
  model: DS220j
  cpu: "Realtek RTD1296 (ARM quad-core)"
  ram: "512MB"
  drives: "1x Seagate IronWolf Pro 16TB"
  local_ip: 192.158.1.65
  role: "File storage, backups, project archives, partner access"
  mounts:
    z_drive: "/mnt/z/ — mapped in WSL"
    tax_package: "/mnt/z/Business/TomCatSound_LLC/2024_Tax_Filing/"

unifi:
  model: "UniFi Dream Machine (Gen1)"
  firmware: "UniFi OS 4.4.6"
  ip: 192.168.1.1
  role: "Network router + WiFi controller"
  issue: "Double-NAT with ISP modem (Nighthawk C7000v2)"
  accessories: ["UniFi AP LR", "UniFi 8-port switch"]

iphone:
  role: "Mobile access via Tailscale"
  access: "FAITHH API via Tailscale when Windows is on"
```

### Gen8 Services (12 Running)
```yaml
chromadb:    { port: 8000, purpose: "RAG database (32,499 chunks)", status: "running" }
grafana:     { port: 3000, purpose: "Monitoring UI", creds: "admin/Grafana2026!", status: "running" }
prometheus:  { port: 9090, purpose: "Metrics collection", status: "running" }
node_export: { port: 9100, purpose: "System metrics", status: "running" }
pihole:      { port: "80/53", purpose: "DNS filtering", creds: "admin/PiHole2026!", status: "running" }
gitea:       { port: "3002 (SSH:2222)", purpose: "Git hosting", status: "running" }
gitlab_run:  { purpose: "CI/CD runner", status: "running" }
vaultwarden: { port: 8080, purpose: "Password manager", status: "running" }
docker_reg:  { port: "5000 (UI:5001)", purpose: "Private image registry", status: "running" }
uptime_kuma: { port: 3001, purpose: "Service monitoring", status: "running" }
registry_ui: { port: 5001, purpose: "Registry web UI", status: "running" }
```

### Network
```yaml
topology: "ISP → Nighthawk C7000v2 (router mode) → UDM (router mode) → Switch → Devices"
known_issue: "Double-NAT causing random disconnections"
vpn: Tailscale (all devices connected)
local_subnet: 192.158.1.x  # intentionally non-standard
ssh_config: ~/.ssh/config  # configured for: gen8, nas, mac, unifi
ssh_hub: ~/ai-stack/scripts/ssh_hub.sh  # menu-based SSH access (created Jan 26)
```

---

## Development Environment (IDE)

### Windsurf
```yaml
type: ide
status: active
location: ~/ai-stack/
purpose: "Primary development environment for FAITHH"
configuration:
  rules_file: ".windsurf/rules/faithhprojectspecifics.md"
  plans_directory: ".windsurf/plans/"
  memory_plugin: "Not detected (clean configuration)"
  mcp_servers: "None configured (clean separation from Cursor)"
key_files:
  - .windsurf/rules/faithhprojectspecifics.md
  - .windsurf/plans/ (5 planning files from recent sessions)
```

### Cursor
```yaml
type: ide
status: active
purpose: "Alternative development environment with MCP integration"
configuration:
  cache_location: "~/.cursor/plugins/cache/cursor-public/"
  project_mcps: "~/.cursor/projects/home-jonat-ai-stack/mcps/"
  mcp_logs: "~/.cache/claude-cli-nodejs/-home-jonat-ai-stack/mcp-logs-claude-vscode/"
plugins:
  - context7-plugin: "Documentation lookup via https://mcp.context7.com/mcp"
  - continual-learning: "Automated AGENTS.md updates via hooks"
  - parallel: "Web search and research (parallel.ai)"
issues:
  - mcp_method_not_found: "Claude VSCode integration error -32601 (Jan/Feb 2026)"
  - impact: "Claude tool availability in VSCode, extension works via direct backend"
```

### MCP Servers (Active)
```yaml
context7_plugin:
  server_id: "plugin-context7-plugin-context7"
  type: "HTTP endpoint"
  url: "https://mcp.context7.com/mcp"
  purpose: "Up-to-date documentation lookup from source repositories"
  tools: ["resolve-library-id", "query-docs"]
  status: "✅ Configured and cached"

cursor_ide_browser:
  server_id: "cursor-ide-browser"
  type: "Built-in Cursor service"
  purpose: "Web browsing and content extraction"
  status: "✅ Configured"

compound_engineering_context7:
  server_id: "plugin-compound-engineering-context7"
  type: "HTTP endpoint (Context7 variant)"
  purpose: "Engineering-specific documentation lookup"
  tools: ["resolve-library-id", "query-docs"]
  status: "✅ Configured"
```

### FAITHH VS Code Extension
```yaml
name: "faithh-vscode"
version: "0.1.0"
publisher: "faithh"
purpose: "FAITHH NetNavi AI companion for VS Code"
features:
  - Chat sidebar (webview)
  - File context integration
  - Direct backend communication (localhost:5557)
configuration:
  backend_url: "http://localhost:5557"
  send_file_context: true
  default_model: "Uses backend default"
mcp_integration:
  - "No direct MCP calls found in extension source"
  - "MCP errors from Claude client, not extension"
  - "Extension works via direct HTTP API calls"
```

---

## Relationships (Project Graph)

```
                    ┌──────────────────────────────┐
                    │       JONATHAN                │
                    │  Audio Producer & AI Developer│
                    │  "How do we build systems     │
                    │   that serve people well?"    │
                    └──────┬───────┬────────┬───────┘
                           │       │        │
              serves ──────┘       │        └────── creates
                    ┌──────┐       │        ┌──────────────┐
                    │FAITHH│◄──────┘        │  CONSTELLA   │
                    │(AI)  │   indexes      │  (Governance)│
                    │      ├───────────────►│              │
                    │      │◄───────────────┤              │
                    │      │  informed_by    │              │
                    └──┬───┘                └──────────────┘
                       │                           │
                       │ supports                  │ philosophically_aligned
                       ▼                           ▼
                    ┌──────────────────────────────────┐
                    │     TOM CAT SOUND LLC             │
                    │  (Audio Business / Income Source) │
                    └──────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │ Gen8     │   │ NAS      │   │ Network  │
              │ Server   │   │ DS220j   │   │ (UniFi)  │
              │ 12 svcs  │   │ Storage  │   │ Tailscale│
              └──────────┘   └──────────┘   └──────────┘
```

**Edge Types:**
- **FAITHH → Jonathan:** serves (maintains coherence when attention shifts)
- **FAITHH → Constella:** indexes (1,904 governance documents)
- **FAITHH → Tom Cat Sound:** indexes (business docs, conversations)
- **Constella → FAITHH:** informed_by (conversations developed Constella concepts)
- **Tom Cat Sound ↔ Constella:** philosophically_aligned (dignity, fair systems)
- **All → Jonathan:** unified_by ("How do we build systems that serve people well?")

---

## Documentation Architecture

### Source of Truth Layer
```yaml
# Machine-readable state (auto/manual update)
project_states.json:      { updated: "2026-01-25", staleness: "low" }
faithh_memory.json:       { updated: "2025-11-29", staleness: "HIGH — needs refresh" }
decisions_log.json:       { updated: "2025-11-27", staleness: "HIGH — no Dec-Feb decisions" }
scaffolding_state.json:   { updated: "2026-01-15", staleness: "moderate" }
faithh_knowledge_graph.yaml: { updated: "2025-12-29", staleness: "moderate" }
```

### Human-Readable Layer
```yaml
MASTER_CONTEXT.md:       { updated: "2026-01-25", purpose: "Technical overview" }
LIFE_MAP.md:             { updated: "2026-01-18", purpose: "Philosophy, strategy, the 'why'" }
SYSTEMS_MAP.md:          { updated: "2026-02-07", purpose: "THIS FILE — comprehensive map" }
docs/ECOSYSTEM_MAP.md:   { updated: "2026-01-25", purpose: "Network topology, devices, services" }
```

### Generated Layer
```yaml
CONTEXT.md:              { updated: "2026-02-04", purpose: "AI injection doc (auto-generated)" }
snapshots/framing/:      { purpose: "Immutable framing snapshots" }
templates/:              { purpose: "Templates for generation" }
generator: scripts/generate_context.py
```

### Research Documents
```yaml
docs/OPUS_RESEARCH_HANDOFF_2026-02-04.md:        "Context injection architecture"
docs/RESEARCH_AI_CONTEXT_INJECTION_2026-02-04.md: "External research on context injection"
docs/RESEARCH_HANDOFF_ChipSynthesis_ML_Avatar_2026-02-04.md: "ML chip synthesis + user avatar"
docs/RESEARCH_HANDOFF_ChipSynthesis_v2_combined.md:          "Chip synthesis clustering design"
docs/RESEARCH_CHIP_SYNERGY.md:                    "Chip routing and fusion"
docs/RESEARCH_PULSE_AI_IMMUNE_SYSTEM_2026-01-18.md: "PULSE immune system design"
docs/RESEARCH_BRIEF_UI_DESIGN.md:                 "UI design research"
```

---

## Staleness Report (Feb 7, 2026)

| File | Last Updated | Status | Notes |
|------|-------------|--------|-------|
| project_states.json | Mar 1 | ✅ Current | FGS + IME projects added |
| scaffolding_state.json | Mar 1 | ✅ Current | Phase 4 active, IME scaffold complete |
| decisions_log.json | Mar 1 | ✅ Current | infra_002 WSL crash rule added |
| SYSTEMS_MAP.md | Mar 1 | ✅ Current | This file |
| faithh_memory.json | Feb 18 | ⚠️ Slightly stale | May not reflect IME/harmony work |
| CONTEXT.md | Feb 19 | ⚠️ Slightly stale | Needs regeneration from updated sources |
| LIFE_MAP.md | Jan 18 | ✅ OK | Philosophy stable, no update needed |

### Current System State (Mar 1, 2026)
- Embedding model: **BAAI/bge-base-en-v1.5 (768-dim)** — migrated 2026-05-17 (commit c8f7938, "Migrate to BGE-768: reindex KB v2")
- Collection: **faithh_knowledge_base** — 38,294 documents including harmony/IME architecture docs
- Phase: **Phase 4** — IME scaffold built, journal synthesis pending, production hardening in progress

---

## Key Scripts & Tools

```yaml
# Backend management
restart_backend.sh:          "Stop + start FAITHH backend on :5557"
stop_backend.sh:             "Stop FAITHH backend"
gen8_health_check.sh:        "Health check Gen8 services"

# Context & documentation
scripts/generate_context.py: "Generate CONTEXT.md from source files"
scripts/maintenance/:        "Update scripts (project_states, etc.)"

# SSH & infrastructure
scripts/ssh_hub.sh:          "Menu-based SSH access to all devices"

# RAG & indexing
scripts/index_docs_to_gen8.py:    "Index documents to ChromaDB"
scripts/reindex_with_metadata.py: "Reindex with proper metadata"
scripts/chunk_claude_chats.py:    "Chunk Claude exports for indexing"

# Testing
scripts/test_rag_stability.sh:     "RAG stability tests"
scripts/comprehensive_faithh_test.py: "Full FAITHH test suite"
scripts/test_r1_health.py:         "R1 (Echo) health check"

# Monitoring
scripts/gpu_monitor.py:            "GPU usage monitoring"
scripts/pulse_monitor.py:          "PULSE pattern monitoring"
scripts/monitoring_daemon.py:      "Background monitoring"
```

---

## The Core Tension

> You keep building infrastructure for coherence (FAITHH) instead of using what you have to generate income (FGS). This makes sense because FAITHH solves the coherence problem... but it creates a loop.

### Possible Paths
- **Path A:** Income First — FGS focus, use FAITHH as-is
- **Path B:** FAITHH Investment — complete the tool before using it
- **Path C:** Parallel Tracks — 40% FGS / 30% FAITHH / 20% Permaculture / 10% Constella

### The Compass Question
*Stop building the compass and start using it.* FAITHH at current state is functional. The question isn't whether it's perfect — it's whether you're consulting it when you get lost.

---

## Recent Timeline (Dec 2025 - Feb 2026)

| Date | Event |
|------|-------|
| Dec 29, 2025 | Knowledge graph YAML created |
| Jan 6, 2026 | System state snapshot created |
| Jan 14, 2026 | Architecture verified, ecosystem reviewed |
| Jan 15, 2026 | Scaffolding state updated |
| Jan 18, 2026 | LIFE_MAP updated, PULSE research, test results |
| Jan 20, 2026 | Gen8 services deployed (Grafana, Gitea, Vaultwarden, etc.) |
| Jan 25, 2026 | ChromaDB reindexed (32,499 chunks, new embedding model) |
| Jan 25, 2026 | Project states updated, master context refreshed |
| Jan 26, 2026 | Tom Cat Sound tax package COMPLETED |
| Jan 26, 2026 | NAS setup for partner access |
| Jan 26, 2026 | SSH hub created (ssh_hub.sh, ~/.ssh/config) |
| Feb 4, 2026 | Context injection system built (generate_context.py, CONTEXT.md) |
| Feb 4, 2026 | First framing snapshot created |
| Feb 4, 2026 | Research: AI context injection, chip synthesis ML/avatar |
| Feb 7, 2026 | This systems map created |

---

## For AI Assistants

### Quick Orientation
1. Read this file for the full picture
2. Check `CONTEXT.md` for the condensed AI-injectable version
3. Check `project_states.json` for machine-readable current state
4. Check `LIFE_MAP.md` for the philosophical "why"
5. Check `decisions_log.json` before proposing changes

### Critical Rules
- **Canonical frontend:** `faithh_pet_v4.html` at ROOT level (not active/frontend/)
- **Canonical backend:** `faithh_professional_backend_fixed.py` (port 5557)
- **Before frontend edits:** `grep -A2 "@app.route('/')" faithh_professional_backend_fixed.py`
- **Test UI at:** http://localhost:5557/ (not by opening HTML files)
- **Don't confuse:** "FAITHH" (this AI system) ≠ "faith" (religious concept)
- **Don't confuse:** "Constella" (civic governance) ≠ software framework

### Communication Preferences
- Technical but accessible
- Show the "why" alongside the "what"
- Milestone-based planning, not calendar-based
- Comprehensive documentation (ADHD accommodation)
- MegaMan Battle Network aesthetic for FAITHH UI

---

**End of Systems Map**

## Claude Code Setup (Updated 2026-05-19)

### Proxy Config
- cc_proxy.py routes to local vLLM (localhost:8000), NOT Groq
- Groq free tier TPM limit (6000) is too low for Claude Code system prompts (~40k tokens)
- Proxy translates OpenAI format -> Anthropic format for Claude Code compatibility
- ANTHROPIC_BASE_URL=http://localhost:5558 in environment

### Startup Sequence
1. bash start_faithh.sh        # builds tmux, starts vLLM + orchestrator
2. bash start_faithh.sh --kill # full clean restart

### Claude Code Usage
- cd ~/ai-stack/app/services && claude --dangerously-skip-permissions
- Launch from subdirectory to minimize context
- Simple Q&A works well; file operations work but are slow (~150 tok/s)
