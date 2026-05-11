#!/bin/bash

################################################################################
# FAITHH Project - Cleanup and Organization Script
# Created: $(date +%Y-%m-%d)
# Purpose: Clean up redundant files and organize project structure
################################################################################

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups/cleanup_$(date +%Y%m%d_%H%M%S)"

echo "🎯 FAITHH Project Cleanup & Organization"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo "Backup will be saved to: $BACKUP_DIR"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "✓ Created backup directory"

################################################################################
# Step 1: Remove Windows Zone.Identifier files
################################################################################
echo ""
echo "📝 Step 1: Removing Zone.Identifier files..."
ZONE_COUNT=$(find "$PROJECT_ROOT" -name "*:Zone.Identifier" -type f 2>/dev/null | wc -l)
if [ "$ZONE_COUNT" -gt 0 ]; then
    find "$PROJECT_ROOT" -name "*:Zone.Identifier" -type f -delete 2>/dev/null || true
    echo "✓ Removed $ZONE_COUNT Zone.Identifier files"
else
    echo "✓ No Zone.Identifier files found"
fi

################################################################################
# Step 2: Organize documentation files
################################################################################
echo ""
echo "📚 Step 2: Organizing documentation files..."

# Ensure docs subdirectories exist
mkdir -p "$PROJECT_ROOT/docs/guides"
mkdir -p "$PROJECT_ROOT/docs/reference"
mkdir -p "$PROJECT_ROOT/docs/session-reports"
mkdir -p "$PROJECT_ROOT/docs/specifications"

# Move documentation files from root to appropriate docs folders
cd "$PROJECT_ROOT"

# Guides and how-tos
for file in \
    WORKFLOW_GUIDE.md \
    GET_STARTED_CHECKLIST.md \
    IMAGE_GENERATION_SETUP.md \
    LOCAL_IMAGE_GENERATION_SETUP.md \
    ULTRA_QUICK_START_IMAGE_GEN.md \
    DO_THIS_NOW_IMAGE_GENERATION.md \
    SELF_DOCUMENTING_SYSTEM_GUIDE.md \
    SESSION_STARTUP_PROTOCOL.md \
    SESSION_ENDING_PROTOCOL.md \
    PARITY_SYSTEM_GUIDE.md \
    VS_CODE_IMPLEMENTATION_HANDOFF.md \
    WEEK1_AUTOMATION_GUIDE.md
do
    if [ -f "$file" ]; then
        mv "$file" "$PROJECT_ROOT/docs/guides/" 2>/dev/null || true
        echo "  → Moved $file to docs/guides/"
    fi
done

# Reference documentation
for file in \
    QUICK_REFERENCE_CARD.md \
    FAITHH_QUICK_REFERENCE.md \
    COMPLETE_PACKAGE_INDEX.md \
    UI_COMPONENTS_LIBRARY.md \
    ROOT_FILES_GUIDE.md \
    WHY_LOCAL_IMAGE_GENERATION.md \
    BACKEND_API_REQUIREMENTS.md
do
    if [ -f "$file" ]; then
        mv "$file" "$PROJECT_ROOT/docs/reference/" 2>/dev/null || true
        echo "  → Moved $file to docs/reference/"
    fi
done

# Session and status reports
for file in \
    CURRENT_STATUS_SUMMARY.md \
    SESSION_CONTINUATION_PLAN.md \
    SESSION_UI_IMPROVEMENTS_LOG.md \
    CONVERSATION_COMPLETE.md \
    WEEK1_COMPLETION_REPORT.md \
    WEEK1_CHECKLIST.md \
    WEEK1_WORK_PLAN.md \
    WEEK2_PREVIEW.md \
    TUESDAY_QUICK_START.md \
    IMMEDIATE_NEXT_STEPS.md \
    STABLE_V3_RESTORE_POINT.md \
    HOME_DIRECTORY_DECISIONS.md
do
    if [ -f "$file" ]; then
        mv "$file" "$PROJECT_ROOT/docs/session-reports/" 2>/dev/null || true
        echo "  → Moved $file to docs/session-reports/"
    fi
done

# Specifications and design docs
for file in \
    FAITHH_V4_UI_SPECIFICATION.md \
    FAITHH_V4_BACKEND_API.md \
    UI_V3_TO_V4_COMPARISON.md \
    UI_V4_COMPLETE_SUMMARY.md \
    UI_V4_QUICK_START.md \
    UI_VISUAL_LAYOUT_GUIDE.md \
    V3_VS_V4_ANALYSIS.md \
    FRONTEND_BACKEND_ARCHITECTURE.md \
    LEONARDO_AI_PROMPTS.md \
    LEONARDO_AI_PROMPTS_ENHANCED.md \
    READY_TO_USE_PROMPTS.md \
    ENHANCED_UI_PACKAGE_SUMMARY.md \
    FAITHH_UI_ENHANCEMENT_GUIDE.md \
    UI_MODULAR_UPDATE_GUIDE.md
do
    if [ -f "$file" ]; then
        mv "$file" "$PROJECT_ROOT/docs/specifications/" 2>/dev/null || true
        echo "  → Moved $file to docs/specifications/"
    fi
done

# Keep these in root (they're important quick-access files)
# - START_HERE.md
# - README.md
# - MASTER_INTEGRATION_DOCUMENT.md
# - MASTER_CONTEXT.md
# - MASTER_ACTION_FAITHH.md
# - ACTIVE_BACKEND_INFO.md

echo "✓ Documentation organized"

################################################################################
# Step 3: Organize Python scripts
################################################################################
echo ""
echo "🐍 Step 3: Organizing Python scripts..."

# Move utility scripts to scripts/
for file in \
    analyze_dependencies.py \
    system_health_check.py \
    fix_chromadb_embeddings.py \
    inspect_chromadb.py \
    test_env_loading.py
do
    if [ -f "$file" ]; then
        mv "$file" "$PROJECT_ROOT/scripts/" 2>/dev/null || true
        echo "  → Moved $file to scripts/"
    fi
done

# Move backend-related scripts to backend/
for file in \
    faithh_backend_adapter.py \
    faithh_enhanced_backend.py \
    faithh_unified_api.py \
    faithh_backend_v4_template.py
do
    if [ -f "$file" ]; then
        mv "$file" "$PROJECT_ROOT/backend/" 2>/dev/null || true
        echo "  → Moved $file to backend/"
    fi
done

echo "✓ Python scripts organized"

################################################################################
# Step 4: Clean up backup copies
################################################################################
echo ""
echo "🗑️  Step 4: Cleaning up backup copies..."

# Move old backups to backup directory
for file in \
    faithh_professional_backend.py.original \
    faithh_professional_backend.py.prefixbackup
do
    if [ -f "$file" ]; then
        mv "$file" "$BACKUP_DIR/" 2>/dev/null || true
        echo "  → Archived $file to backup"
    fi
done

echo "✓ Backup copies archived"

################################################################################
# Step 5: Clean up log files in WSL home
################################################################################
echo ""
echo "📋 Step 5: Cleaning WSL home directory logs..."

cd "$HOME"
for file in \
    pip_version.log \
    pip_which.log \
    python_version.log \
    python_which.log \
    wsl_status.log
do
    if [ -f "$file" ]; then
        mv "$file" "$BACKUP_DIR/" 2>/dev/null || true
        echo "  → Archived $file from home directory"
    fi
done

# Also clean up the check script
if [ -f "check_faithh_health.sh" ]; then
    mv "check_faithh_health.sh" "$PROJECT_ROOT/scripts/" 2>/dev/null || true
    echo "  → Moved check_faithh_health.sh to scripts/"
fi

echo "✓ Home directory cleaned"

################################################################################
# Step 6: Create inventory of current structure
################################################################################
echo ""
echo "📊 Step 6: Creating structure inventory..."

cd "$PROJECT_ROOT"
cat > "$PROJECT_ROOT/PROJECT_STRUCTURE.md" << 'EOF'
# FAITHH Project Structure

Last updated: $(date +%Y-%m-%d)

## Directory Organization

### Root Directory
- **START_HERE.md** - Quick start guide (keep in root)
- **README.md** - Project overview (keep in root)
- **MASTER_INTEGRATION_DOCUMENT.md** - Main integration reference (keep in root)
- **MASTER_CONTEXT.md** - Project context (keep in root)
- **ACTIVE_BACKEND_INFO.md** - Current backend status (keep in root)

### Backend (`/backend/`)
- Core backend implementations
- Adapters and unified APIs
- Backend templates

### Frontend (`/frontend/`)
- UI files (v3 and v4)
- HTML, CSS, and client-side JavaScript

### Docs (`/docs/`)
- **guides/** - How-to guides and tutorials
- **reference/** - Quick references and API docs
- **session-reports/** - Session summaries and status updates
- **specifications/** - Design specs and UI/backend specifications
- **archive/** - Old/deprecated documentation

### Scripts (`/scripts/`)
- Automation scripts
- Utility tools
- Health checks and monitoring

### Models (`/models/`)
- AI model files
- Model configurations

### Data (`/data/`)
- Application data
- Caches and temporary files

### Parity (`/parity/`)
- Parity tracking system
- Changelogs and version tracking

### Tests (`/tests/`)
- Unit tests
- Integration tests
- E2E tests

### Cache (`/cache/`)
- Temporary cache files

### Backups (`/backups/`)
- Timestamped backups
- Archive of old versions

## File Types

- **Python files (.py)**: Backend logic, APIs, utilities
- **HTML files (.html)**: UI interfaces
- **Markdown files (.md)**: Documentation
- **YAML files (.yaml)**: Configuration
- **JSON files (.json)**: Data and config
- **Shell scripts (.sh)**: Automation

## External Dependencies

- **ComfyUI** (`~/ComfyUI/`) - Image generation tool (55GB)
- **Stable Diffusion WebUI** (`~/stable-diffusion-webui/`) - Alt image gen (310MB)

## Size Summary

- **models/**: ~33GB
- **venv/**: ~7.8GB
- **faithh_rag/**: ~239MB
- **docs/**: ~384KB
- **Total project**: ~41GB
EOF

echo "✓ Structure inventory created: PROJECT_STRUCTURE.md"

################################################################################
# Step 7: Summary
################################################################################
echo ""
echo "========================================"
echo "✅ Cleanup Complete!"
echo "========================================"
echo ""
echo "Summary:"
echo "  • Removed Zone.Identifier files"
echo "  • Organized documentation into docs/ subdirectories"
echo "  • Moved Python scripts to appropriate locations"
echo "  • Archived backup copies"
echo "  • Cleaned WSL home directory"
echo "  • Created PROJECT_STRUCTURE.md inventory"
echo ""
echo "Backup saved to: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "  1. Review PROJECT_STRUCTURE.md"
echo "  2. Start FAITHH backend: cd $PROJECT_ROOT && python faithh_professional_backend.py"
echo "  3. Run tests: cd $PROJECT_ROOT && python -m pytest tests/"
echo ""
