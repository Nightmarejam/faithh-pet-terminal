# FAITHH Project Reorganization Plan
Generated: 2025-11-04

## 📁 Proposed Directory Structure

```
ai-stack/
├── 📄 MASTER_CONTEXT.md          (Keep - Single source of truth)
├── 📄 README.md                   (Create - Quick start guide)
│
├── 📂 frontend/                   (Consolidate UI files)
│   ├── rag-chat.html             (Keep - Primary UI)
│   ├── faithh_pet_v3.html        (Review - may be newer version?)
│   └── assets/                   (Create - for CSS/JS if needed)
│
├── 📂 backend/                    (Consolidate APIs)
│   ├── core/
│   │   ├── faithh_unified_api.py (Keep - Main orchestrator)
│   │   └── config.yaml           (Keep - Configuration)
│   │
│   ├── adapters/
│   │   ├── faithh_backend_adapter.py (Keep - HTML bridge)
│   │   └── faithh_api_websocket.py   (Archive - if not needed)
│   │
│   └── services/
│       ├── rag_processor.py      (Keep - RAG logic)
│       ├── tool_executor.py      (Keep - Tool system)
│       └── security_manager.py   (Keep - Security)
│
├── 📂 executors/                  (Keep as-is)
│   ├── __init__.py
│   ├── filesystem.py
│   └── process.py
│
├── 📂 data/                       (Keep - RAG storage)
│   └── chroma/                   (ChromaDB files)
│
├── 📂 scripts/                    (Consolidate utilities)
│   ├── start_faithh.sh           (Keep - Main launcher)
│   ├── setup_rag.py              (Keep - RAG setup)
│   └── test_*.py                 (Keep - All tests)
│
├── 📂 docs/                       (Archive old docs)
│   ├── archive/
│   │   ├── FAITHH_CONTEXT.md    (Move - Original vision)
│   │   ├── SESSION_*.md         (Move - Session notes)
│   │   └── *_COMPLETE.md        (Move - Completion docs)
│   │
│   └── active/
│       ├── ARCHITECTURE.md      (Keep - Technical details)
│       ├── ROADMAP.md           (Keep - Future plans)
│       └── QUICKSTART.md        (Keep - User guide)
│
└── 📂 legacy/                     (Archive unused code)
    ├── chat_ui.py                (Move if not using Streamlit)
    ├── search_ui.py              (Move if not using Streamlit)
    └── old_apis/                 (Move deprecated APIs)
```

## 🔧 Immediate Actions

### 1. Context File Consolidation
- **Keep**: `MASTER_CONTEXT.md` as the single source of truth
- **Archive**: `FAITHH_CONTEXT.md` to docs/archive/ (historical reference)
- **Create**: Auto-updater script to maintain MASTER_CONTEXT.md

### 2. API Consolidation
```bash
# Determine which APIs are actively used
# Keep only necessary ones, archive others
```

### 3. Documentation Cleanup
```bash
# Move to organized structure
mkdir -p docs/{active,archive}
mkdir -p backend/{core,adapters,services}
mkdir -p scripts
mkdir -p legacy
```

## 📝 Files to Review

### Potentially Redundant:
1. `faithh_api.py` vs `faithh_unified_api.py` - Check if both needed
2. `rag_api.py` vs RAG in unified API - Consolidate?
3. Multiple HTML versions - Keep best one

### Missing/Needed:
1. `.gitignore` - Add if using Git
2. `requirements.txt` - Consolidate dependencies
3. `docker-compose.yml` - If using Docker

## 🎯 Clean Filing System Guidelines

### Naming Conventions:
- **APIs**: `{purpose}_api.py` (e.g., `chat_api.py`)
- **Services**: `{service}_service.py` (e.g., `rag_service.py`)
- **Tests**: `test_{component}.py`
- **Docs**: `{CATEGORY}_{TOPIC}.md`

### File Organization Rules:
1. **One responsibility per file** - Don't mix concerns
2. **Clear imports** - Use relative imports within modules
3. **Version control** - Archive old versions, don't delete
4. **Documentation** - Each major component gets a README

### Context Management:
1. **Single source**: MASTER_CONTEXT.md
2. **Auto-update**: Script to update on changes
3. **Version tracking**: Include update dates
4. **Reference system**: Link to relevant code files

## 🚀 Next Steps

1. **Backup current state**:
   ```bash
   cp -r ~/ai-stack ~/ai-stack-backup-$(date +%Y%m%d)
   ```

2. **Create new structure**:
   ```bash
   cd ~/ai-stack
   mkdir -p frontend backend/{core,adapters,services} docs/{active,archive} legacy scripts
   ```

3. **Move files to new locations** (see script below)

4. **Update imports** in Python files

5. **Test everything** still works

## 📜 Reorganization Script

```bash
#!/bin/bash
# reorganize_faithh.sh

# Create backup first
echo "Creating backup..."
cp -r ~/ai-stack ~/ai-stack-backup-$(date +%Y%m%d_%H%M%S)

# Create new directory structure
echo "Creating new structure..."
cd ~/ai-stack
mkdir -p frontend backend/{core,adapters,services} docs/{active,archive} legacy scripts

# Move files (examples - adjust as needed)
echo "Moving files..."

# Frontend files
mv rag-chat.html frontend/ 2>/dev/null
mv faithh_pet_v*.html frontend/ 2>/dev/null

# Backend core
mv faithh_unified_api.py backend/core/ 2>/dev/null
mv config.yaml backend/core/ 2>/dev/null

# Backend adapters
mv faithh_backend_adapter.py backend/adapters/ 2>/dev/null
mv faithh_api_websocket.py backend/adapters/ 2>/dev/null

# Services
mv rag_processor.py backend/services/ 2>/dev/null
mv tool_executor.py backend/services/ 2>/dev/null
mv security_manager.py backend/services/ 2>/dev/null
mv tool_registry.py backend/services/ 2>/dev/null

# Documentation
mv FAITHH_CONTEXT.md docs/archive/ 2>/dev/null
mv *_COMPLETE.md docs/archive/ 2>/dev/null
mv SESSION_*.md docs/archive/ 2>/dev/null
mv ARCHITECTURE.md docs/active/ 2>/dev/null
mv ROADMAP.md docs/active/ 2>/dev/null
mv QUICKSTART.md docs/active/ 2>/dev/null

# Scripts
mv start*.sh scripts/ 2>/dev/null
mv test_*.py scripts/ 2>/dev/null
mv setup_rag.py scripts/ 2>/dev/null

# Legacy (if not using)
mv chat_ui.py legacy/ 2>/dev/null
mv search_ui.py legacy/ 2>/dev/null

echo "Reorganization complete!"
echo "Remember to update import paths in Python files"
```

## 🔍 Questions to Resolve

1. **Which API is primary?** faithh_api.py or faithh_unified_api.py?
2. **HTML versions?** Is faithh_pet_v3.html newer than rag-chat.html?
3. **WebSocket needed?** Are you using WebSocket connections?
4. **Streamlit UIs?** Keep or archive chat_ui.py and search_ui.py?
5. **Docker usage?** Need docker-compose.yml in root?

## 📊 Benefits of Reorganization

1. **Clarity**: Clear separation of concerns
2. **Maintainability**: Easier to find and update files
3. **Scalability**: Room to grow without clutter
4. **Documentation**: Historical context preserved
5. **Development**: Faster to navigate and understand

---

**Note**: This plan is a suggestion. Adjust based on your actual usage and preferences.
