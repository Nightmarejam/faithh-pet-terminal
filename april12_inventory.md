# April 12th (097e5f3) Complete File Inventory

**Total Files:** 1968  
**Current HEAD Files:** 158  
**Files Missing from HEAD:** 1810  
**Date:** 2026-05-11

## File Categorization

### By Directory
- **scripts/**: 410 files (automation, PULSE, RAG, security, indexing, testing)
- **docs/**: 516 files (documentation, handoffs, research, architecture)
- **archive/**: 250 files (backend variants, legacy code, dated scripts, UI variants)
- **projects/**: 189 files (alife experiments, tomcat-sound business docs, crypto)
- **ml/**: 95 files (output, experiments, genomic)
- **tests/**: 61 files (test suites, shell scripts)
- **backend/**: 38 files (backend modules, analytics, coherence)
- **app/**: 29 files (analytics, providers, services)
- **docs/data/**: 95 files (governance sources, imports)
- **Audio/**: 3 files (audio workflows)
- **infrastructure/**: 2 files (SYSTEM_MAP.json, SYSTEM_MAP.md)
- **services/**: 7 files (project_hub, rag_api)
- **ops/**: 5 files (monitoring: prometheus, alertmanager, docker-compose)
- **modules/**: 2 files (README, __init__.py)
- **experiments/**: 2 files (genomic)
- **configs/**: 1 file (model_config.yaml)
- **collectors/**: 3 files (system state collection)
- **security/**: 3 files (audit, key validator, permissions)
- **secure_logging/**: 3 files (error handler, performance logger, config)
- **snapshots/**: 4 files (framing, system_state)
- **templates/**: 1 file (CONTEXT_TEMPLATE)
- **vendor/**: 2 files (README, polar_quant)
- **images/**: 2 files (faithh.png, pulse.png)
- **icons/**: 6 files (faithh icons in various sizes)
- **knowledge_base/**: 2 files (clear_and_reindex.py, index_conversations.py)

### By File Type
- **Python files (.py)**: 616 files
- **Markdown files (.md)**: 686 files
- **JSON files (.json)**: 242 files
- **HTML files (.html)**: 11 files
- **YAML files (.yaml/.yml)**: 30 files
- **Shell scripts (.sh)**: 85 files
- **JavaScript (.js/.jsx)**: 8 files
- **Text files (.txt)**: 45 files
- **Configuration files**: 50 files (.env.example, config.yaml, etc.)
- **Binary files**: 90 files (images, modelfiles, databases)

## Key Directories to Restore

### 1. scripts/ (410 files) - CRITICAL
**Purpose:** Automation, PULSE, RAG, security, indexing, testing
**Status:** Missing from HEAD (only ~20 scripts present)
**Key subdirectories:**
- scripts/rag/ (RAG CLI, setup, diagnostics)
- scripts/security/ (audit, scanner, healer)
- scripts/setup/ (vllm, pihole, grafana, vaultwarden)
- scripts/pulse/ (monitor, scheduler, autonomous)
- scripts/indexing/ (reindex scripts)
- scripts/testing/ (comprehensive test scripts)

### 2. docs/ (516 files) - CRITICAL
**Purpose:** Documentation, handoffs, research, architecture
**Status:** Partially present (consolidated/ exists, but many missing)
**Key subdirectories:**
- docs/handoffs/ (session handoffs)
- docs/research/ (research documents)
- docs/architecture/ (system architecture)
- docs/guides/ (operator guides, runbooks)
- docs/data/ (governance sources, imports)
- docs/archive/ (legacy docs)

### 3. archive/ (250 files) - REFERENCE
**Purpose:** Backend variants, legacy code, dated scripts
**Status:** Missing from HEAD
**Key subdirectories:**
- archive/backend_unused/ (backend variants)
- archive/legacy/ (legacy backends)
- archive/dedupe_2026-01-07/ (deduplication artifacts)
- archive/development/ (development docs)
- archive/completed-handoffs-2026-01-25/ (handoffs)

### 4. projects/ (189 files) - CRITICAL
**Purpose:** ALife experiments, Tom Cat Sound business, crypto
**Status:** Partially present (projects/alife/, projects/crypto/ exist)
**Key subdirectories:**
- projects/alife/ (ALife experiments and results)
- projects/tomcat-sound/ (business docs, invoices, PowerBI)
- projects/status/ (project_status.json, component_map.json, dashboard.html)

### 5. ml/ (95 files) - CRITICAL
**Purpose:** ML outputs, experiments, genomic
**Status:** Missing from HEAD
**Key files:**
- ml/output/pulse_state.json (PULSE state)
- ml/output/staleness_report.md
- ml/output/divergence_report.md
- ml/output/branch_report.md
- ml/output/journal/index.json

### 6. backend/ (38 files) - CRITICAL
**Purpose:** Backend modules, analytics, coherence
**Status:** Missing from HEAD (only faithh_professional_backend_fixed.py at root)
**Key files:**
- backend/coherence_arbiter.py
- backend/rag_processor.py
- backend/enhanced_chip_integration.py
- backend/performance_monitor.py
- backend/security_manager.py
- backend/tool_executor.py

### 7. app/ (29 files) - CRITICAL
**Purpose:** Analytics, providers, services
**Status:** Partially present (app/services/ has 5 files)
**Key subdirectories:**
- app/analytics/ (constitutional, focus, system analytics)
- app/providers/ (anthropic provider)
- app/services/ (20+ service files)

### 8. tests/ (61 files) - CRITICAL
**Purpose:** Test suites, shell scripts
**Status:** Minimal (only test_backend.py and a few others)
**Key subdirectories:**
- tests/root/ (root-level tests)
- tests/ (test_*.py files)

### 9. services/ (7 files) - CRITICAL
**Purpose:** Project hub, RAG API
**Status:** Missing from HEAD
**Key files:**
- services/project_hub/app.py
- services/rag_api.py

### 10. ops/monitoring/ (5 files) - CRITICAL
**Purpose:** Prometheus, Alertmanager, Docker Compose
**Status:** Missing from HEAD
**Key files:**
- ops/monitoring/prometheus.yml
- ops/monitoring/alertmanager.yml
- ops/monitoring/docker-compose.yml
- ops/monitoring/alert_rules/security_alerts.yml

## Root-Level Files to Restore

### Configuration Files
- .env.example (104 lines - comprehensive configuration)
- config.yaml
- configs/model_config.yaml
- faithh_collection_rules.yaml

### Documentation Files
- SYSTEMS_MAP.md (400+ lines - comprehensive systems map)
- SYSTEM_FINGERPRINT.md
- MASTER_CONTEXT.md
- CONTEXT.md
- LIFE_MAP.md
- ARCHITECTURE.md
- DEPS.md
- AGENTS.md

### State Files
- pulse_patterns.json (chip sequences)
- faithh_live_state.json
- faithh_memory.json
- decisions_log.json
- scaffolding_state.json
- project_states.json

### UI Files
- faithh_pet_v4.html (faithh_pet.html was 0 lines at April 12th)
- faithh_cockpit.html (1014 lines at March 14)
- faithh_component_map.jsx
- manifest.json
- sw.js

### Other Files
- requirements.txt (comprehensive dependencies)
- stop_backend.sh
- start_backend.sh (may exist in scripts/)

## Files to Preserve from Current HEAD

- faithh_pet.html (3720 lines - more complete than April 12th version)
- faithh_professional_backend_fixed.py (227 lines - clean rebuild, keep as reference)
- CURSOR_CONTEXT.md (current context)
- Current .env (Proxmox-adapted)
- Current project_states.json (may be newer)
- Current faithh_live_state.json, faithh_memory.json (may be newer)

## Restoration Strategy

1. **Backup current state** - Create backup directory with current HEAD files
2. **Restore ALL files from 097e5f3** - Use git checkout to restore complete state
3. **Preserve current HEAD files** - Copy back preserved files over restored ones
4. **Adapt for Proxmox** - Update network paths, remove GPU config, update endpoints
5. **Validate restoration** - Run tests, check services, validate configuration

## Next Steps

1. Create backup of current state
2. Restore all files from 097e5f3
3. Preserve current HEAD files that are newer/better
4. Adapt for Proxmox environment
5. Validate and test
