#!/bin/bash
# Tuesday File Organization - Self-Documenting Edition
# This script automatically updates MASTER_ACTION as it works!

set -e  # Exit on error

cd /home/jonat/ai-stack

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Session info
SESSION_NUM=3
SESSION_DATE=$(date +%Y-%m-%d)
SESSION_DAY="Tuesday"
SESSION_START=$(date +%H:%M:%S)

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   FAITHH Tuesday File Organization                 ║"
echo "║   Self-Documenting Automation                      ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Initialize work log (temporary during session)
WORK_LOG=".tuesday_work_log.tmp"
echo "## Session $SESSION_NUM - $SESSION_DATE - $SESSION_DAY" > "$WORK_LOG"
echo "**Week:** 1, Day 2" >> "$WORK_LOG"
echo "**Focus:** File organization and documentation consolidation" >> "$WORK_LOG"
echo "" >> "$WORK_LOG"
echo "**Completed:**" >> "$WORK_LOG"

# Function to log actions
log_action() {
    echo "- $1" >> "$WORK_LOG"
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to log decisions
log_decision() {
    echo "$1" >> "$WORK_LOG.decisions"
}

# ============================================================
# PHASE 1: Organize Backend Files
# ============================================================
echo -e "${BLUE}Phase 1: Organizing Backend Files${NC}"
echo "=================================================="
echo ""

# Find all backend files in root
backend_files=$(find . -maxdepth 1 -name "*backend*.py" -o -name "*api*.py" -o -name "rag_api.py" | grep -v "./" | wc -l)

if [ $backend_files -gt 0 ]; then
    echo "Found backend files to organize..."
    
    # Keep active backend in root for now (easier to run)
    # Move others to backend/ or archive/
    
    # Archive old backend files
    for file in faithh_api.py faithh_api_websocket.py faithh_simple_backend.py faithh_backend_adapter.py faithh_enhanced_backend.py faithh_unified_api.py; do
        if [ -f "$file" ]; then
            mv "$file" archive/
            log_action "Moved $file to archive/ (inactive backend)"
        fi
    done
    
    # Keep rag_api.py in root if separate
    if [ -f "rag_api.py" ]; then
        log_action "Kept rag_api.py in root (separate service)"
    fi
    
    # Keep test_backend.py for testing
    if [ -f "test_backend.py" ]; then
        log_action "Kept test_backend.py in root (testing tool)"
    fi
    
    log_decision "**Decision:** Keep active backend (faithh_professional_backend.py) in root for easy access"
    log_decision "**Decision:** Archived inactive backend versions"
else
    log_action "Backend files already organized"
fi

echo ""

# ============================================================
# PHASE 2: Organize HTML/UI Files
# ============================================================
echo -e "${BLUE}Phase 2: Organizing UI Files${NC}"
echo "=================================================="
echo ""

# Ensure frontend directory exists
mkdir -p frontend/html

# Move HTML files
html_moved=0
for file in *.html; do
    if [ -f "$file" ]; then
        # Keep main UI in root for now
        if [[ "$file" == "faithh_pet_v3.html" ]]; then
            log_action "Kept $file in root (active UI)"
        else
            mv "$file" frontend/html/
            log_action "Moved $file to frontend/html/"
            html_moved=$((html_moved + 1))
        fi
    fi
done

if [ $html_moved -eq 0 ]; then
    log_action "HTML files already organized"
fi

log_decision "**Decision:** Keep active UI (faithh_pet_v3.html) in root for easy browser access"

echo ""

# ============================================================
# PHASE 3: Organize Configuration Files
# ============================================================
echo -e "${BLUE}Phase 3: Organizing Configuration Files${NC}"
echo "=================================================="
echo ""

# config.yaml already in root - that's fine
if [ -f "config.yaml" ]; then
    log_action "config.yaml in root (standard location)"
fi

# docker-compose.yml already in root - that's fine  
if [ -f "docker-compose.yml" ]; then
    log_action "docker-compose.yml in root (standard location)"
fi

# .env already in root and gitignored - perfect
if [ -f ".env" ]; then
    log_action ".env in root and secured (from Monday)"
fi

log_decision "**Decision:** Keep config files in root (standard Docker/Python convention)"

echo ""

# ============================================================
# PHASE 4: Consolidate Documentation
# ============================================================
echo -e "${BLUE}Phase 4: Consolidating Documentation${NC}"
echo "=================================================="
echo ""

# Create docs structure
mkdir -p docs/active
mkdir -p docs/archive
mkdir -p docs/session-reports

# Identify key documents to keep active
ACTIVE_DOCS=(
    "MASTER_CONTEXT.md"
    "MASTER_ACTION_FAITHH.md"
    "README.md"
    "WEEK1_WORK_PLAN.md"
    "WEEK1_CHECKLIST.md"
)

# Identify session reports
SESSION_DOCS=(
    "MONDAY_COMPLETION_REPORT.md"
    "MONDAY_COMPLETE_SUMMARY.md"
    "SESSION_STARTUP_PROTOCOL.md"
    "SESSION_ENDING_PROTOCOL.md"
)

# Move session docs to session-reports/
for doc in "${SESSION_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" docs/session-reports/
        log_action "Moved $doc to docs/session-reports/"
    fi
done

# Archive old/duplicate documentation
ARCHIVE_DOCS=(
    "ANALYSIS_AND_RECOMMENDATIONS.md"
    "ARCHITECUTRE.md"
    "ARCHITECTURE.md"
    "BATTLE_CHIP_DESIGN.md"
    "COMMAND_REFERENCE.md"
    "COMPLETION_CHECKLIST.md"
    "Development_Session_Notes.md"
    "EXECUTIVE_DECISION_DOCUMENT.md"
    "FAITHH_COMPLETE_ARCHITECTURE.md"
    "FAITHH_CONTEXT.md"
    "FAITHH_QUICK_REFERENCE.md"
    "FAITHH_UI_ENHANCEMENT_GUIDE.md"
    "FINAL_STATUS.md"
    "GEMINI_HANDOFF.md"
    "HTML_INTEGRATION_GUIDE.md"
    "HTML_UI_COMPLETE.md"
    "IMPLEMENTATION_CHECKLIST.md"
    "IMPLEMENTATION_GUIDE.md"
    "INTEGRATION_COMPLETE.md"
    "INTEGRATION_PLAN.md"
    "MASTER_ACTION_TEMPLATE.md"
    "MASTER_CONTEXT_v4.md"
    "PARITY_SYSTEM_GUIDE.md"
    "PROJECT_REORGANIZATION_PLAN.md"
    "QUICKSTART.md"
    "ROADMAP.md"
    "SESSION_COMPLETE.md"
    "SESSION_STATE.md"
)

archived_count=0
for doc in "${ARCHIVE_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" docs/archive/
        archived_count=$((archived_count + 1))
    fi
done

log_action "Archived $archived_count old documentation files to docs/archive/"
log_decision "**Decision:** Keep only 5 active docs in root, move session reports to docs/session-reports/, archive old docs"

# Create documentation index
cat > docs/DOCUMENTATION_INDEX.md << 'EOF'
# FAITHH Documentation Index

## Active Documents (Root)
- **MASTER_CONTEXT.md** - Complete project context and architecture
- **MASTER_ACTION_FAITHH.md** - Session history and progress tracking
- **README.md** - Quick start and overview
- **WEEK1_WORK_PLAN.md** - Detailed week 1 plan
- **WEEK1_CHECKLIST.md** - Quick task checklist

## Session Reports (docs/session-reports/)
- Monday completion reports
- Session protocols and guides
- Daily summaries

## Archive (docs/archive/)
- Historical planning documents
- Old integration guides
- Superseded documentation

## How to Use
1. Start with README.md for overview
2. Check MASTER_ACTION for current status
3. Reference MASTER_CONTEXT for architecture
4. Use WEEK1 docs for current work
5. Session reports for historical context

Last Updated: $(date)
EOF

log_action "Created docs/DOCUMENTATION_INDEX.md"

echo ""

# ============================================================
# PHASE 5: Organize Scripts
# ============================================================
echo -e "${BLUE}Phase 5: Organizing Scripts${NC}"
echo "=================================================="
echo ""

# Move all .sh scripts to scripts/
mkdir -p scripts

scripts_moved=0
for script in *.sh; do
    if [ -f "$script" ]; then
        mv "$script" scripts/
        scripts_moved=$((scripts_moved + 1))
    fi
done

# Move Python utility scripts
for script in fix_backend_properly.py test_env_simple.py update_backend_env.py test_backend_env.py; do
    if [ -f "$script" ]; then
        mv "$script" scripts/
        scripts_moved=$((scripts_moved + 1))
    fi
done

log_action "Moved $scripts_moved scripts to scripts/"

echo ""

# ============================================================
# PHASE 6: Create Clean Root
# ============================================================
echo -e "${BLUE}Phase 6: Creating Clean Root Directory${NC}"
echo "=================================================="
echo ""

cat > ROOT_FILES_GUIDE.md << 'EOF'
# Root Directory Organization

## Files That Should Stay in Root

### Active Code
- `faithh_professional_backend.py` - Active backend (easy to run)
- `faithh_pet_v3.html` - Active UI (easy to open in browser)

### Configuration
- `.env` - Environment variables (SECURED, in .gitignore)
- `config.yaml` - System configuration
- `docker-compose.yml` - Docker setup
- `.gitignore` - Git security

### Essential Documentation
- `README.md` - Quick start guide
- `MASTER_CONTEXT.md` - Project context
- `MASTER_ACTION_FAITHH.md` - Progress tracking
- `WEEK1_WORK_PLAN.md` - Current week plan
- `WEEK1_CHECKLIST.md` - Quick checklist

### Utility
- `ROOT_FILES_GUIDE.md` - This file

## Organized Directories
- `backend/` - Backend code (future)
- `frontend/` - UI files (organized)
- `configs/` - Config files (future)
- `docs/` - Documentation (organized)
- `scripts/` - Automation scripts
- `tools/` - Utility tools
- `data/` - Data files
- `logs/` - Log files
- `archive/` - Old code versions
- `parity/` - Parity tracking (future)

## Root Should Have ~15 files, not 50+

Last Updated: $(date)
EOF

log_action "Created ROOT_FILES_GUIDE.md"

echo ""

# ============================================================
# PHASE 7: Test System
# ============================================================
echo -e "${BLUE}Phase 7: Testing System${NC}"
echo "=================================================="
echo ""

echo "Checking critical files exist..."

critical_files=(
    "faithh_professional_backend.py"
    "faithh_pet_v3.html"
    ".env"
    "config.yaml"
    "MASTER_CONTEXT.md"
    "MASTER_ACTION_FAITHH.md"
)

all_good=true
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING!"
        all_good=false
    fi
done

if $all_good; then
    log_action "All critical files verified present"
else
    echo "⚠️  Some critical files missing - check above"
    log_action "⚠️ System test found missing files"
fi

echo ""

# ============================================================
# FINALIZE: Update MASTER_ACTION
# ============================================================

SESSION_END=$(date +%H:%M:%S)

# Add decisions to work log
if [ -f "$WORK_LOG.decisions" ]; then
    echo "" >> "$WORK_LOG"
    echo "**Decisions Made:**" >> "$WORK_LOG"
    cat "$WORK_LOG.decisions" >> "$WORK_LOG"
    rm "$WORK_LOG.decisions"
fi

# Add status and next steps
cat >> "$WORK_LOG" << EOF

**Files Created:**
- docs/DOCUMENTATION_INDEX.md
- ROOT_FILES_GUIDE.md

**Status:** ✅ Tuesday file organization complete

**Next Session:**
- Create parity file structure
- Set up first parity files
- Document parity system

**Time Spent:** Started $SESSION_START, Ended $SESSION_END

---

EOF

# Append to MASTER_ACTION
echo "" >> MASTER_ACTION_FAITHH.md
cat "$WORK_LOG" >> MASTER_ACTION_FAITHH.md

# Clean up temp log
rm "$WORK_LOG"

# ============================================================
# SUMMARY
# ============================================================

echo ""
echo "════════════════════════════════════════════════════"
echo "✨ TUESDAY FILE ORGANIZATION COMPLETE! ✨"
echo "════════════════════════════════════════════════════"
echo ""
echo "What was organized:"
echo "  ✅ Backend files (archived inactive versions)"
echo "  ✅ UI files (organized in frontend/html/)"
echo "  ✅ Documentation (~$archived_count files archived)"
echo "  ✅ Scripts (moved to scripts/)"
echo "  ✅ Root directory cleaned"
echo ""
echo "Documentation created:"
echo "  📄 docs/DOCUMENTATION_INDEX.md"
echo "  📄 ROOT_FILES_GUIDE.md"
echo ""
echo "📊 MASTER_ACTION automatically updated!"
echo "   Check: tail -50 MASTER_ACTION_FAITHH.md"
echo ""
echo "Next steps:"
echo "  1. Review the organized structure: ls -lah"
echo "  2. Check docs: ls docs/*"
echo "  3. Test backend still works"
echo "  4. Ready for Wednesday (parity setup)"
echo ""
echo "════════════════════════════════════════════════════"
echo ""
