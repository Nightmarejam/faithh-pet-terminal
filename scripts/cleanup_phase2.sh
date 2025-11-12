#!/bin/bash

################################################################################
# FAITHH Project - Phase 2 Cleanup Script
# Created: $(date +%Y-%m-%d)
# Purpose: Clean up remaining root directory files
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups/cleanup_phase2_$(date +%Y%m%d_%H%M%S)"

echo "🎯 FAITHH Project - Phase 2 Cleanup"
echo "===================================="
echo "Project root: $PROJECT_ROOT"
echo "Backup: $BACKUP_DIR"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "✓ Created backup directory"

################################################################################
# Step 1: Move test files to tests/
################################################################################
echo ""
echo "🧪 Step 1: Moving test files to tests/..."

mkdir -p "$PROJECT_ROOT/tests"

for file in test_backend.py test_e2e.py test_gemini.py test_rag.py test_tool_executor.py; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        mv "$PROJECT_ROOT/$file" "$PROJECT_ROOT/tests/"
        echo "  → Moved $file to tests/"
    fi
done

echo "✓ Test files organized"

################################################################################
# Step 2: Move backend modules to backend/
################################################################################
echo ""
echo "🔧 Step 2: Moving backend modules to backend/..."

for file in rag_api.py rag_processor.py security_manager.py tool_executor.py tool_registry.py; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        mv "$PROJECT_ROOT/$file" "$PROJECT_ROOT/backend/"
        echo "  → Moved $file to backend/"
    fi
done

echo "✓ Backend modules organized"

################################################################################
# Step 3: Move utility scripts to scripts/
################################################################################
echo ""
echo "📜 Step 3: Moving utility scripts to scripts/..."

for file in \
    conversation_parsers.py \
    index_documents_chromadb.py \
    pulse_monitor.py \
    rag_cli.py \
    setup_rag.py \
    friday_validation.sh \
    thursday_first_parity.sh \
    wednesday_parity_setup.sh \
    update_parity_session_6.sh \
    SELF_DOCUMENTING_TEMPLATE.sh
do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        mv "$PROJECT_ROOT/$file" "$PROJECT_ROOT/scripts/"
        echo "  → Moved $file to scripts/"
    fi
done

# Move SCRIPTS_README.md
if [ -f "$PROJECT_ROOT/SCRIPTS_README.md" ]; then
    mv "$PROJECT_ROOT/SCRIPTS_README.md" "$PROJECT_ROOT/scripts/README.md"
    echo "  → Moved SCRIPTS_README.md to scripts/README.md"
fi

echo "✓ Utility scripts organized"

################################################################################
# Step 4: Move legacy UI to legacy/
################################################################################
echo ""
echo "📦 Step 4: Moving legacy files to legacy/..."

mkdir -p "$PROJECT_ROOT/legacy"

for file in chat_ui.py search_ui.py; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        mv "$PROJECT_ROOT/$file" "$PROJECT_ROOT/legacy/"
        echo "  → Moved $file to legacy/"
    fi
done

echo "✓ Legacy files organized"

################################################################################
# Step 5: Move data files to data/
################################################################################
echo ""
echo "💾 Step 5: Moving data files to data/..."

mkdir -p "$PROJECT_ROOT/data"

if [ -f "$PROJECT_ROOT/chroma.sqlite3" ]; then
    mv "$PROJECT_ROOT/chroma.sqlite3" "$PROJECT_ROOT/data/"
    echo "  → Moved chroma.sqlite3 to data/"
fi

echo "✓ Data files organized"

################################################################################
# Step 6: Move log files to logs/
################################################################################
echo ""
echo "📋 Step 6: Moving log files to logs/..."

mkdir -p "$PROJECT_ROOT/logs"

for file in api.log server.log; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        mv "$PROJECT_ROOT/$file" "$PROJECT_ROOT/logs/"
        echo "  → Moved $file to logs/"
    fi
done

echo "✓ Log files organized"

################################################################################
# Step 7: Archive old documentation
################################################################################
echo ""
echo "📚 Step 7: Archiving old documentation..."

for file in \
    ACTIVE_BACKEND_INFO.md \
    MASTER_ACTION_FAITHH.md \
    MASTER_ACTION_FAITHH_UPDATED.md
do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        mv "$PROJECT_ROOT/$file" "$PROJECT_ROOT/docs/session-reports/"
        echo "  → Moved $file to docs/session-reports/"
    fi
done

echo "✓ Old documentation archived"

################################################################################
# Step 8: Delete temporary files
################################################################################
echo ""
echo "🗑️  Step 8: Removing temporary files..."

TEMP_COUNT=0
for file in \
    file_list_config.txt \
    file_list_docs.txt \
    file_list_html.txt \
    file_list_python.txt \
    discovery_quick_*.txt
do
    if [ -f "$PROJECT_ROOT/$file" ] || ls "$PROJECT_ROOT/$file" 1> /dev/null 2>&1; then
        # Backup before deleting
        cp "$PROJECT_ROOT"/$file "$BACKUP_DIR/" 2>/dev/null || true
        rm -f "$PROJECT_ROOT"/$file
        TEMP_COUNT=$((TEMP_COUNT + 1))
        echo "  → Removed $file (backed up)"
    fi
done

echo "✓ Removed $TEMP_COUNT temporary files"

################################################################################
# Step 9: Update PROJECT_STRUCTURE.md
################################################################################
echo ""
echo "📊 Step 9: Updating PROJECT_STRUCTURE.md..."

cat > "$PROJECT_ROOT/PROJECT_STRUCTURE.md" << 'EOF'
# FAITHH Project Structure (Updated)

**Last updated:** $(date +%Y-%m-%d)

## 📁 Root Directory (Clean)

### **Active Code** (Keep in root):
- `faithh_professional_backend.py` - Main backend (running on port 5557)
- `faithh_pet_v3.html` - UI v3 (stable, production)
- `faithh_ui_v4.html` - UI v4 (in development)
- `main.py` - Application entry point

### **Configuration** (Keep in root):
- `.env` - Environment variables (API keys, ports)
- `.gitignore` - Git ignore rules
- `config.yaml` - Application configuration
- `docker-compose.yml` - Docker setup
- `requirements.txt` - Python dependencies
- `keyring.json` - Security keyring

### **Essential Documentation** (Keep in root):
- `README.md` - Project overview
- `START_HERE.md` - Quick start guide
- `MASTER_INTEGRATION_DOCUMENT.md` - Main integration reference
- `MASTER_CONTEXT.md` - Project context
- `QUICK_START_GUIDE.md` - Quickstart instructions
- `PROJECT_STRUCTURE.md` - This file
- `CLEANUP_PLAN.md` - Cleanup documentation
- `ROOT_FILES_ANALYSIS.md` - File analysis

**Total in root: ~19 essential files** ✨

---

## 📂 Directory Structure

### **backend/** - Backend Modules
- Core backend implementations
- API modules (rag_api.py, rag_processor.py)
- Security (security_manager.py)
- Tool execution (tool_executor.py, tool_registry.py)
- Adapters and unified APIs

### **frontend/** - Frontend Files
- UI components (future organization)
- Client-side JavaScript
- CSS and assets

### **docs/** - All Documentation
- **guides/** - How-to guides and tutorials
- **reference/** - Quick references and API docs
- **session-reports/** - Session summaries and status updates
- **specifications/** - Design specs and UI/backend specifications
- **archive/** - Old/deprecated documentation

### **scripts/** - Automation & Utilities
- Cleanup scripts (cleanup_and_organize.sh, cleanup_phase2.sh)
- Service management (start_services.sh)
- Health checks (system_health_check.py, check_faithh_health.sh)
- Utility scripts (conversation_parsers.py, pulse_monitor.py)
- RAG tools (rag_cli.py, setup_rag.py, index_documents_chromadb.py)
- Parity tracking scripts

### **tests/** - Test Files
- Backend tests (test_backend.py)
- End-to-end tests (test_e2e.py)
- Integration tests (test_gemini.py, test_rag.py)
- Tool tests (test_tool_executor.py)

### **legacy/** - Deprecated Code
- Old UI implementations (chat_ui.py, search_ui.py)
- Superseded modules

### **models/** - AI Models (~33GB)
- Model files
- Model configurations

### **data/** - Application Data
- Databases (chroma.sqlite3)
- Caches and temporary files
- Upload storage

### **logs/** - Log Files
- Application logs (backend.log, api.log, server.log)
- Debug logs
- Error logs

### **parity/** - Parity Tracking System
- Changelogs and version tracking
- Feature parity documentation

### **cache/** - Temporary Cache
- Runtime cache files

### **backups/** - Timestamped Backups
- Cleanup backups (cleanup_YYYYMMDD_HHMMSS/)
- Archive of old versions

### **venv/** - Python Virtual Environment (~7.8GB)
- Python packages
- Dependencies

---

## 🎯 File Count Summary

- **Root:** ~19 essential files
- **Backend:** ~15 modules
- **Scripts:** ~25 utilities
- **Docs:** ~50 markdown files
- **Tests:** ~5 test files
- **Total organized:** Clean, maintainable structure

---

## 🚀 Quick Commands

### Start Backend:
```bash
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend.py
```

### Run Tests:
```bash
cd ~/ai-stack/tests
python test_backend.py
```

### Open UI:
```bash
cd ~/ai-stack
python -m http.server 8000
# Then open: http://localhost:8000/faithh_pet_v3.html
```

---

**Project is now clean, organized, and maintainable!** ✨
EOF

echo "✓ PROJECT_STRUCTURE.md updated"

################################################################################
# Step 10: Summary
################################################################################
echo ""
echo "===================================="
echo "✅ Phase 2 Cleanup Complete!"
echo "===================================="
echo ""
echo "Summary:"
echo "  • Moved test files to tests/"
echo "  • Moved backend modules to backend/"
echo "  • Moved utility scripts to scripts/"
echo "  • Moved legacy files to legacy/"
echo "  • Moved data files to data/"
echo "  • Moved log files to logs/"
echo "  • Archived old documentation to docs/session-reports/"
echo "  • Removed $TEMP_COUNT temporary files"
echo "  • Updated PROJECT_STRUCTURE.md"
echo ""
echo "Backup saved to: $BACKUP_DIR"
echo ""
echo "Root directory reduced from 50+ files to ~19 essential files!"
echo ""
echo "Next steps:"
echo "  1. Verify backend still works: curl http://localhost:5557/health"
echo "  2. Run tests: cd ~/ai-stack/tests && python test_backend.py"
echo "  3. Review new structure: cat ~/ai-stack/PROJECT_STRUCTURE.md"
echo ""
