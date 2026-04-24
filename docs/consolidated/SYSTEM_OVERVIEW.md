# FAITHH System Fingerprint

> **Purpose:** This document is the authoritative reference for any AI session interacting with the FAITHH system. Read this first to understand identity, capabilities, constraints, and current state.
> 
> **📋 Multi-View Navigation**: [Basic Overview] • [🔧 Functional View] • [⚙️ Technical View] • [⚡ Live State]

---

## Identity

| Field | Value |
|-------|-------|
| **Name** | FAITHH (Friendly AI Teaching & Helping Hub) |
| **Purpose** | Thought partner for maintaining project coherence when attention shifts |
| **User** | Jonathan (Audio Producer & AI Developer) |
| **Philosophy** | Celestial Equilibrium — resonance, harmonic alignment, dignity |
| **Core Function** | Remember the "why" when motivation wanes; surface relevant context when returning to projects |

### What FAITHH Is
- A digital compass to better understanding and future
- Helps maintain harmonic alignment across projects
- Gently challenges while accepting incremental progress
- Surfaces connections across domains (resonance themes)

### What FAITHH Is NOT
- NOT a religious or philosophical framework about "faith"
- NOT just a search engine or Q&A bot
- NOT a task executor — more of a live journal with feedback

---

## Capabilities

### Available Tools

| Tool | Description | Location |
|------|-------------|----------|
| **RAG Search** | Semantic search across 38K+ indexed chunks | ChromaDB @ Gen8:8000 |
| **Multi-Provider LLM** | Ollama (local), Groq (cloud), Gemini (cloud) | Backend routing |
| **Intent Detection** | Classifies query type for routing | `backend/intent_detection.py` |
| **Coherence Arbiter** | Measures RAG/chip alignment | `backend/coherence_arbiter.py` |
| **Anchor Validator** | Validates claims against state files | `backend/anchor_validator.py` |
| **Context Builders** | Assembles context from memory/decisions/projects | `backend/context_builders.py` |
| **Filesystem Operations** | Read/write files in workspace | `filesystem_chip.py` |
| **Knowledge Graph** | Entity/relationship tracking | `knowledge_graph.py` |
| **PULSE Pattern Tracker** | Detects usage patterns for chip synthesis | `pulse_pattern_tracker.py` |
| **Decision Logging** | Records decisions with rationale | `decisions_log.json` |
| **Security Middleware** | Rate limiting, input validation, request protection | `backend/security_middleware.py` |
| **Connection Monitor** | Health checks for 5 services, graceful fallbacks | `backend/connection_monitor.py` |
| **Response Cache** | Intelligent caching with LRU eviction, performance optimization | `backend/cache.py` |
| **Performance Tracker** | Real-time metrics, system monitoring, analytics | `backend/performance.py` |
| **Local AI Optimization** | Query analysis, model selection, performance profiling | `backend/local_optimization.py` |
| **Genomic Impedance Sensor** | Environmental impedance detection for organisms | `app/services/genomic_impedance_sensor.py` |
| **Genomic Biasing Engine** | DNA copying bias based on impedance patterns | `app/services/genomic_biasing_engine.py` |
| **Program Advance Chips** | MegaMan-inspired parallel processing with 5 strategic advances | `backend/parallel_chip_engine.py` |

### Program Advance System (MegaMan Battle Network Inspired)
| Advance | Chips Used | Purpose | Trigger |
|---------|------------|---------|---------|
| **Full Recall** | scaffolding, rag_search, decisions, project_state | Maximum context assembly | "everything about", "complete history" |
| **Business Review** | project_state, rag_search | Business-focused analysis | "business", "revenue", "clients" |
| **Context Recovery** | scaffolding, rag_search | Timeline context recovery | "where was i", "catch me up" |
| **Decision Audit** | decisions, rag_search | Decision forensics with evidence | "why did", "rationale", "reasoning" |
| **Project Deep Dive** | project_state, rag_search, constella | Multi-domain project analysis | "project status", "progress", "phase" |

### LLM Providers

| Provider | Model | Use Case | Status |
|----------|-------|----------|--------|
| **Ollama** | `qwen25-grounded:latest` | Default, grounded responses | ✅ Active |
| **Ollama** | `deepseek-r1:32b` | Heavy reasoning, complex queries | ✅ Active |
| **Groq** | `llama-3.3-70b-versatile` | Fast cloud responses | ✅ Available |
| **Gemini** | `gemini-2.0-flash-exp` | Fallback, cost-efficient | ✅ Available |

### Not Available
- Real-time web search (no live internet access from backend)
- Arbitrary code execution (read-only unless explicitly requested)
- External API calls (except configured providers)

---

## Knowledge Sources

| Source | Location | Purpose | Update Frequency |
|--------|----------|---------|------------------|
| `faithh_memory.json` | Root | Self-awareness, user profile, project connections | Manual |
| `project_states.json` | Root | Project status, phases, priorities | Per session |
| `decisions_log.json` | Root | Decision history with rationale | Per decision |
| `scaffolding_state.json` | Root | Open loops, active tasks | Per session |
| `config.yaml` | Root | System configuration, model settings | Rarely |
| ChromaDB | Gen8:8000 | 38K+ indexed conversation chunks | Batch indexing |
| ML Chips | `ml/output/chips.json` | 15 macro-chips for semantic routing | Synthesis runs |
| `CONTEXT.md` | Root | Auto-generated project snapshot | Script-generated |
| `AGENTS.md` | Root | Repository guidelines, AI rules | Manual |

### ChromaDB Statistics
- **Collection:** `faithh_knowledge_base`
- **Total Chunks:** ~38,000
- **Conversations Indexed:** 306 (208 ChatGPT + 98 Claude)
- **Embedding Model:** all-MiniLM-L6-v2 (384-dim)
- **Chunking:** 1500 chars with 200 char overlap

---

## Routing Logic

### Query Processing Flow

```
User Query
    ↓
Intent Detection (backend/intent_detection.py)
    ↓
┌─────────────────────────────────────────┐
│ Intent Types:                           │
│ - self_query (about FAITHH)             │
│ - project_query (about projects)        │
│ - why_query (reasoning/rationale)       │
│ - next_action (what to do next)         │
│ - technical (code/architecture)         │
│ - general (everything else)             │
└─────────────────────────────────────────┘
    ↓
Complexity Assessment
    ↓
┌─────────────────────────────────────────┐
│ Simple → qwen25-grounded (fast, local)  │
│ Complex → deepseek-r1:32b (reasoning)   │
│ Cloud fallback → Groq or Gemini         │
└─────────────────────────────────────────┘
    ↓
Context Assembly (context_builders.py)
    ↓
RAG Retrieval (if needed)
    ↓
Coherence Scoring (coherence_arbiter.py)
    ↓
LLM Response Generation
    ↓
Response with Metadata
```

### Model Selection Criteria

| Criteria | Model |
|----------|-------|
| Default/simple queries | `qwen25-grounded:latest` |
| Heavy reasoning, multi-step | `deepseek-r1:32b` |
| Fast cloud response needed | Groq `llama-3.3-70b-versatile` |
| Groq unavailable | Gemini `gemini-2.0-flash-exp` |

---

## Guardrails

### MUST DO
- ✅ Activate venv before Python: `source /home/jonat/ai-stack/venv/bin/activate`
- ✅ Use `python3`, never bare `python`
- ✅ Read `AGENTS.md` before significant changes
- ✅ Check `project_states.json` for current priorities
- ✅ Log decisions to `decisions_log.json` with rationale
- ✅ Verify backend health before assuming it's running

### MUST NOT
- ❌ NEVER retry failed commands more than once without stopping
- ❌ NEVER run background processes without checking they started
- ❌ NEVER commit until tests pass and changes are verified
- ❌ NEVER modify code to fix tests without understanding root cause
- ❌ NEVER commit `.env`, `keyring.json`, or `uploads/`
- ❌ NEVER use the 70B model (`llama3.3:70b`) — crashes WSL

### After Completing Tasks
- Run verification ONCE, report result, then STOP
- Do not loop on verification commands
- If task fails, report failure and ask for guidance

---

## Infrastructure

### Services

| Service | Host | Port | Purpose |
|---------|------|------|---------|
| FAITHH Backend | localhost (WSL) | 5557 | Main API |
| ChromaDB | Gen8 (192.158.1.243) | 8000 | Vector database |
| Ollama | localhost (WSL) | 11434 | Local LLM inference |
| Postgres | Docker | 5432 | Langflow data |

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Backend health check |
| `/api/chat` | POST | Main chat endpoint |
| `/api/search` | POST | RAG search |
| `/api/models` | GET | List available models |
| `/api/fingerprint` | GET | System fingerprint (dynamic) |
| `/api/genomic/impedance-sensor` | POST | Create genomic impedance sensor |
| `/api/genomic/biasing-analysis` | POST | Analyze genomic biasing effects |

### Health Check Commands

```bash
# Backend health
curl http://localhost:5557/health

# ChromaDB health
curl http://192.158.1.243:8000/api/v2/heartbeat

# Ollama models
ollama list
```

---

## Current State

> **Note:** For live state, check `fingerprint_state.json` or call `/api/fingerprint`

### Active Projects

| Project | Phase | Status | Priority |
|---------|-------|--------|----------|
| FAITHH | Phase 2 Data Collection | 75% Complete, Collecting | High |
| Genomic Experiments | Phase 1-3 Complete | COMPLETED - 190 organisms tested | High |
| Tom Cat Sound | Operations & Growth | Active | Medium |
| Constella | Phase 1 Integration | In Progress | Low |

### Open Loops
- See `scaffolding_state.json` for current open loops
- See `project_states.json` for project-specific priorities

### Recent Decisions
- See `decisions_log.json` for decision history with rationale

---

## File Conventions

### Canonical Files (DO NOT MOVE)
- `faithh_professional_backend_fixed.py` — Main backend (CURRENTLY RUNNING)
- `faithh_backend_optimized.py` — Genomic experiments backend (HAS GENOMIC ENDPOINTS)
- `faithh_pet_v4.html` — Frontend UI (ROOT level)
- `config.yaml` — System configuration

### Backend Architecture Status
- **Primary Backend**: `faithh_professional_backend_fixed.py` (port 5557)
- **Genomic Backend**: `faithh_backend_optimized.py` (genomic endpoints)
- **Status**: Architecture confusion - needs consolidation
- **Action**: See Sonnet cleanup request for resolution strategy

### Directory Structure
- `backend/` — Modular backend components
- `scripts/` — Utility scripts (new scripts go here)
- `tests/` — Test files
- `docs/` — Documentation (new docs go here)
- `ml/` — ML pipeline, chips, grounding
- `docs/archive/` — Consumed handoffs, stale docs

### State Files (Runtime, Don't Commit Frequently)
- `pulse_patterns.json` — Usage patterns
- `scaffolding_state.json` — Session state
- `project_states.json` — Project status

---

## For AI Sessions

### Startup Checklist
1. Read this `SYSTEM_FINGERPRINT.md`
2. Check `fingerprint_state.json` for current health/state
3. Review `AGENTS.md` for repo rules
4. Check `project_states.json` for priorities

### Before Making Changes
1. Verify which file the backend serves: `grep "send_from_directory" faithh_professional_backend_fixed.py`
2. Check if backend is running: `curl http://localhost:5557/health`
3. Understand existing decisions: `cat decisions_log.json | jq '.decisions[-3:]'`

### Communication Style
- Technical but accessible
- Show the "why" alongside the "what"
- Comprehensive documentation (ADHD accommodation)
- Milestone-based planning, not calendar-based

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-01 | Initial fingerprint creation |

---

*Last Updated: 2026-03-01*
*Generator: Manual (will be auto-generated in future)*
- **RAG Search**: Semantic search across 38K+ indexed chunks
- **Multi-Provider LLM**: Ollama (local), Groq (cloud), Gemini (cloud)
- **Intent Detection**: Classifies query type for routing
- **Coherence Arbiter**: Measures RAG/chip alignment
- **Anchor Validator**: Validates claims against state files
- **Context Builders**: Assembles context from memory/decisions/projects
- **Filesystem Operations**: Read/write files in workspace
- **Knowledge Graph**: Entity/relationship tracking
- **PULSE Pattern Tracker**: Detects usage patterns for chip synthesis
- **Decision Logging**: Records decisions with rationale
- **Security Middleware**: Rate limiting, input validation, request protection
- **Connection Monitor**: Health checks for 5 services, graceful fallbacks
- **Response Cache**: Intelligent caching with LRU eviction, performance optimization
- **Performance Tracker**: Real-time metrics, system monitoring, analytics
- **Local AI Optimization**: Query analysis, model selection, performance profiling
- **Genomic Impedance Sensor**: Environmental impedance detection for organisms
- **Genomic Biasing Engine**: DNA copying bias based on impedance patterns
- **Program Advance Chips**: MegaMan-inspired parallel processing with 5 strategic advances

### ALIFE Capabilities
- **Cultural Evolution**: Multi-generational protocol development
- **Social Specialization**: Agent role emergence and cooperation
- **Protocol Complexity**: Sophisticated cultural systems
- **Parasitic Impedance**: Novel energy feeding mechanisms
- **Multi-Generational Knowledge**: Knowledge accumulation across generations

---

## 📁 Project Structure

### Major Components

**Active Projects**:
- **FAITHH (AI Stack)**: active - Production AI assistant with RAG integration running on WSL2 + Gen8. Full conversation history (Feb 2024-Jan 2026) indexed. ChromaDB on Gen8 with 32,499 chunks (properly chunked 2026-01-25). Full infrastructure stack deployed (12 services).
- **Gen8 MicroServer (servicebox)**: production - HP ProLiant MicroServer Gen8 running Ubuntu 22.04 with Docker. Full infrastructure stack deployed (12 services): ChromaDB, Grafana, Prometheus, Gitea, Vaultwarden, Pi-hole, Docker Registry, Uptime Kuma, GitLab Runner, Node Exporter, Registry UI, and monitoring.
- **Tom Cat Sound LLC**: active - Audio engineering and production business. Financial tracking, client management, and grant applications in progress.
- **Floating Garden Soundworks (FGS)**: planning - Long-horizon vision for a physical recording studio + artist retreat + research facility inspired by Breitenbush Hot Springs and Japanese onsen tradition. Cymatics-informed acoustic design, earth bermed structures, geothermal potential. Connected to Tom Cat Sound LLC but likely a separate entity.
- **Inner Monologue Engine (IME)**: conceptual - A high-reasoning companion intelligence that serves as the journal's inner monologue and eventual seed of an artificial life program. Distinct from FAITHH (which handles task coherence) — IME handles reflective synthesis, pattern recognition across life domains, and the long accumulation of authentic human reasoning that will inform artificial life design.
- **Constella Harmony Framework**: active - Personal framework for multi-modal creativity, coherence detection, and real-time feedback systems.
- **ALIFE (Artificial Life Simulation)**: active - Evolutionary ALife simulation running on Python (Gen8 target). Agents evolve under environmental pressure. Experiment 3 confirmed anticipatory behavior emergence (negative anticipation gap). Red Queen dynamics documented across 200K ticks. Experiment 4 validated harmonic interference dynamics. Experiment 5 confirmed parasitic emergence under adaptive predator pressure. Experiment 6 demonstrated cognitive specialization with Fibonacci mathematical pattern recognition.

**Resource Allocation**:
- **Time**: FAITHH 30%, Business 40%
- **Financial**: Reinvestment 50%, Infrastructure 20%


---

## 🚀 Getting Started

### Quick Start
```bash
./restart_backend.sh        # Start FAITHH backend
# Open http://localhost:5557
```

### Health Check
```bash
curl http://localhost:5557/health
```

### Key Endpoints
- **Chat**: `POST /api/chat` - Main AI interaction
- **Search**: `POST /api/search` - RAG search
- **Genomic**: `POST /api/genomic/impedance-sensor` - Create genomic sensor
- **Status**: `GET /api/status` - System status

---

## 📚 Documentation Structure

This consolidated documentation includes:
- **System Overview**: Complete system understanding
- **Technical Documentation**: Architecture, APIs, implementation
- **Research Documentation**: ALIFE experiments and findings
- **User Guides**: How-to guides and tutorials
- **Maintenance Documentation**: Protocols and procedures

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
