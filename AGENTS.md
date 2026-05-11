# Repository Guidelines (Updated 2026-02-15)

## Project Structure & Module Organization
FAITHH is a Python-first repo with a Flask backend and static HTML UI.

**CURRENT ARCHITECTURE STATUS (April 2026):**
- **Primary Backend**: `faithh_professional_backend_fixed.py` (canonical, port **5557**) — all main `/api/*` routes, including genomic endpoints when enabled.
- **Sidecar apps** (separate Flask processes, **not** imported by the canonical backend): `services/rag_api.py` (RAG microservice, port **5001**), `services/project_hub/app.py` (Program Advance / project API, port **5001** if run standalone).
- **Legacy backends** live under `archive/legacy/` (do not run in production).

**Active code at root (DO NOT move these):**
- `faithh_professional_backend_fixed.py` — Main backend (CURRENTLY RUNNING)
- `filesystem_chip.py` — Filesystem operations chip (imported by backend)
- `knowledge_graph.py` — Knowledge graph module (imported by backend)
- `pulse_pattern_tracker.py` — PULSE learning tracker (imported by backend)
- `faithh_pet_v4.html` — Primary Canvas UI
- `faithh_cockpit.html` — Mission Control / diagnostics Canvas (served at `/cockpit`)

**Modular directories (Canvas / unification):**
- `backend/` — Shared Python imported by the canonical backend (loaders, `llm_providers`, security, etc.)
- `services/` — Standalone Flask apps and sidecars (`rag_api.py`, `project_hub/`)
- `modules/` — Reserved for shared import-only libraries (empty package scaffold + README)
- `vendor/` — Reserved for large third-party trees (e.g. `llama.cpp` migration); see `vendor/README.md`

**Service Registry (Canvas Phase 3):** Any **new user-facing backend capability** (routes, optional modules, or tools the pet UI should expose) **must** be reflected in **`build_workspace_registry()`** and **`GET /api/workspace/registry`** in `faithh_professional_backend_fixed.py` so `faithh_pet_v4.html` can adapt navigation and send **`workspace_registry`** hints with **`POST /api/chat`**. Internal-only features should be marked inactive or omitted from `navigation` rather than left stale.

**Backend modules (extracted for modularity):**
- `backend/data_loaders.py` — JSON file I/O (memory, decisions, projects, scaffolding)
- `backend/intent_detection.py` — Query intent pattern matching
- `backend/context_builders.py` — Context assembly + personality prompt + project structure snapshot
- `backend/llm_providers.py` — Multi-provider LLM dispatch (Groq, Ollama, Gemini)

**State files:** `faithh_memory.json`, `decisions_log.json`, `project_states.json`, `scaffolding_state.json`, `config.yaml`
**Infra:** `docker-compose.yml` (Ollama, ChromaDB, Langflow, Postgres)
**Scripts:** All utility/one-off scripts live in `scripts/`
**Tests:** `tests/` (Python + shell)
**ML:** `ml/` (chip synthesis, LoRA training)

**Documentation structure (see `docs/README.md` for full index):**
- `docs/architecture/` — System design (SYSTEM_OVERVIEW, BACKEND_API, INFRASTRUCTURE)
- `docs/guides/` — How-to guides (QUICKSTART, GIT_WORKFLOW, IMAGE_GENERATION, SSH, DIAGNOSTICS)
- `docs/reference/` — Facts & inventories (CONSTELLA, LIFE_MAP, HARDWARE, MODELS, IDEAS)
- `docs/business/` — Business & financial (PORTFOLIO, TAX_GUIDE, TOMCAT_DASHBOARD)
- `docs/research/` — Research findings (7 consolidated research docs)
- `docs/roadmaps/` — Future plans (VS Code extension, passive collection, phase 2)
- `docs/data/` — Non-markdown reference data (JSON, YAML)
- `docs/archive/` — All consumed handoffs, stale reports, legacy docs

## Build, Test, and Development Commands
- `./restart_backend.sh` – stop any running instance and start the Flask server on `:5557`.
- `./stop_backend.sh` – stop running backend instances.
- `python faithh_professional_backend_fixed.py` – run the backend directly (useful for debugging).
- `docker-compose up -d` – bring up Ollama/ChromaDB/Langflow/Postgres.
- `python -m pytest tests/ -v` – run Python tests.
- `tests/test_harmony.sh` or `tests/test_groq.sh` – run shell-based checks.
- `scripts/start_comfyui.sh` – start ComfyUI on RTX 3090.

## Critical File Locations (READ THIS FIRST)
- **Canonical frontend UI:** `faithh_pet_v4.html` (ROOT level, 5,034 lines)
- **Backend serves from ROOT:** `faithh_professional_backend_fixed.py` serves `faithh_pet_v4.html` from the project root
- **BEFORE editing any frontend file:** Verify which file the backend serves with: `grep "send_from_directory" faithh_professional_backend_fixed.py`
- **Test UI changes** by accessing `http://localhost:5557/` NOT by opening HTML files directly
- **Scripts go in `scripts/`** — do NOT add new .py scripts to root
- **Docs go in `docs/`** — do NOT add new .md files to root (except AGENTS.md, CONTEXT.md, SYSTEMS_MAP.md, README.md)

## Coding Style & Naming Conventions
- Follow existing style in each file; Python uses 4-space indentation.
- Prefer snake_case for Python functions/variables and UpperCamelCase for classes.
- Keep HTML/JS IDs and CSS classes lowercase with hyphens (e.g., `rag-panel`).

## Testing Guidelines
- Test suite lives in `tests/`; name new tests `test_*.py`.
- Use pytest for Python tests; shell tests live alongside as `.sh`.
- If you add backend endpoints, add a small test in `tests/`.

## Commit Guidelines
- Commit messages: descriptive subject with scope, multi-line body for substantial changes.
- See `docs/guides/GIT_WORKFLOW.md` for the latest pattern.

## Configuration & Security Notes
- Service ports: backend `5557`, ChromaDB `8000`, Ollama `11434+`.
- Runtime settings: `config.yaml`; secrets: `.env` (gitignored).
- **Default LLM model:** When `config.yaml` sets `ai.default_model` (and the active Ollama provider block), that value is authoritative; `.env` `DEFAULT_MODEL` is only a fallback when YAML does not pin the model.
- NEVER commit `.env`, `keyring.json`, or files in `uploads/`.

## AI Continuity Documentation Pattern ⭐4

Established framework for ensuring AI session continuity across tools and time:

1. **AGENTS.md** (this file) — permanent repo-level rules, always read first
2. **SYSTEM_FINGERPRINT.md** — system identity, capabilities, guardrails, routing logic
3. **fingerprint_state.json** — dynamic state snapshot (health, models, open loops, recent decisions)
4. **CONTEXT.md** — framing snapshots for FAITHH's personality and project state
5. **docs/** structure — authoritative reference by category (architecture, guides, reference, research, business, roadmaps)
6. **State files** (`faithh_memory.json`, `decisions_log.json`, `project_states.json`, `scaffolding_state.json`) — machine-readable current state
7. **ML outputs** (`ml/output/`) — distilled insights, reports, chip data

**Rule:** New AI sessions should read AGENTS.md + SYSTEM_FINGERPRINT.md + fingerprint_state.json before starting work. Refresh fingerprint with `python3 scripts/generate_fingerprint.py`. Handoff docs go to `docs/archive/` after consumption. State files are the single source of truth for project status.

**Recent handoff (2026-04-12):** `docs/archive/HANDOFF_2026-04-12_model-fix-and-kb-cleanup.md` — Ollama runaway fixes, KB indexing quality gate, `qwen25-faithh-v3` baseline, config authority, and queued audits (KB noise, uncertainty surface, chat export filters, RAG UI score, warm-up script).

## AI Agent Behavior Rules
- After completing a task and verifying it works, **REPORT FINDINGS AND STOP**
- Do NOT continue running verification commands in a loop
- Run verification commands ONCE, confirm success, then summarize and end
- If a task fails, report the failure and ask for guidance — don't retry indefinitely
- Always read handoff docs in `docs/` before starting work if referenced
- **New scripts → `scripts/`**, **New docs → `docs/`**, keep root clean
- **Before marking any task complete:** consult `DEPS.md` to identify which other files need updating
- **Technical questions about this repo:** Before answering, check `GET http://127.0.0.1:5557/api/workspace/registry` (or the Canvas `workspace_registry` snapshot sent with chat) for live services—RAG signal, pulse, genomic, diagnostics—so answers reflect runtime capability instead of guessing.
- **Session metrics:** Operational telemetry is written to the Chroma collection `faithh_session_metrics` (env `CHROMA_METRICS_COLLECTION`), never to `faithh_knowledge_base` or conversation collections. Do not treat session metrics as RAG knowledge or merge them into retrieval.

## Operational standards (FAITHH operator contract)

Human and model answers about **repo state, git history, Compass projects, and live metrics** must follow the **evidence-only** rules in **`docs/guides/FAITHH_OPERATOR_CONTRACT.md`** (immutable commit subjects, latency reporting without invented splits, silo separation for `scaffolding_state.json` vs `faithh_live_state.json` vs git, raw field names for ambiguous JSON, and horizon / sync-date boundaries). New agents and prompt changes should keep that doc and `backend/context_builders.py` `get_faithh_personality()` aligned.

## RAG low confidence behavior

When `rag_signal.low_confidence` is True (retrieval distance above `RAG_MAX_DISTANCE_CONFIDENT`), the backend prepends an explicit no-fabrication banner to the context sent to the model. The LLM must not invent API endpoints, file paths, collection names, or system states. If the context does not contain the answer, respond with something like: “I don’t have reliable context for that — check [relevant source]” (e.g. `GET /api/workspace/registry`, `docs/architecture/BACKEND_API.md`, or the repo file named in metadata).

## Project Maintenance Protocols (NEW - March 2026)

### Monthly Major Cleanup
1. **Backend Architecture Review**
   - Verify single canonical backend
   - Archive experimental variants
   - Update SYSTEM_FINGERPRINT.md with current reality
   - Check for endpoint conflicts

2. **File Organization Audit**
   - Archive legacy backend files to `archive/legacy/`
   - Organize experiments into `experiments/` subdirectories
   - Clean root directory (< 20 files)
   - Consolidate archive locations

3. **Documentation Synchronization**
   - Regenerate CONTEXT.md with current state
   - Update project_states.json with recent progress
   - Review and update decisions_log.json
   - Verify all top-level docs reflect reality

### Weekly Minor Maintenance
1. **Documentation Updates**
   - Regenerate CONTEXT.md
   - Update project_states.json
   - Review recent decisions

2. **Backend Health Check**
   - Verify canonical backend running
   - Test key endpoints
   - Check log files for issues

3. **Experiment Organization**
   - Move any new experiments to `experiments/`
   - Update experiment documentation

### Cleanup Protocol Triggers
**IMMEDIATE CLEANUP REQUIRED WHEN:**
- Backend files exceed 5 variants
- Root directory exceeds 20 files
- Documentation drift detected (docs don't match reality)
- Experiments completed but endpoints inaccessible

**CLEANUP AUTOMATION:**
- Use `scripts/maintenance/cleanup_project.py` for automated tasks
- Manual review required for architectural decisions
- Sonnet consultation for major changes

### Decision Log for Architecture Changes
All backend architecture changes MUST be documented in `decisions_log.json` with:
- `rationale`: Why the change was needed
- `alternatives_considered`: Other options evaluated
- `impact`: What this change affects
- `status`: implemented/planned/deprecated
