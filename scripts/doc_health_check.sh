#!/bin/bash
# FAITHH Doc Health Check
# Simple script to flag potentially stale documentation
# Run: ./scripts/doc_health_check.sh

echo "📋 FAITHH Documentation Health Check"
echo "====================================="
echo ""

cd ~/ai-stack

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get current date in seconds
NOW=$(date +%s)
WEEK_AGO=$((NOW - 604800))  # 7 days
MONTH_AGO=$((NOW - 2592000)) # 30 days

echo "📄 Core Documentation"
echo "---------------------"

# Check key documentation files
check_doc() {
    local file=$1
    local name=$2
    
    if [ -f "$file" ]; then
        local mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
        local age_days=$(( (NOW - mtime) / 86400 ))
        
        if [ $mtime -gt $WEEK_AGO ]; then
            echo -e "  ${GREEN}✓${NC} $name (${age_days}d old)"
        elif [ $mtime -gt $MONTH_AGO ]; then
            echo -e "  ${YELLOW}⚠${NC} $name (${age_days}d old) - review recommended"
        else
            echo -e "  ${RED}✗${NC} $name (${age_days}d old) - likely stale"
        fi
    else
        echo -e "  ${RED}✗${NC} $name - FILE MISSING"
    fi
}

check_doc "LIFE_MAP.md" "Life Map"
check_doc "ARCHITECTURE.md" "Architecture"
check_doc "FAITHH_TESTING_GUIDE.md" "Testing Guide"
check_doc "README.md" "README"
check_doc "REPOSITORY_STRUCTURE.md" "Repository Structure"

echo ""
echo "📋 State Files"
echo "--------------"

check_doc "faithh_memory.json" "FAITHH Memory"
check_doc "decisions_log.json" "Decisions Log"
check_doc "project_states.json" "Project States"
check_doc "scaffolding_state.json" "Scaffolding State"

echo ""
echo "📁 Parity Files"
echo "---------------"

check_doc "parity/PARITY_INDEX.md" "Parity Index"
check_doc "parity/audio_workspace.md" "Audio Workspace"
check_doc "parity/network_infrastructure.md" "Network Infrastructure"
check_doc "parity/backend/PARITY_faithh_professional_backend.md" "Backend Parity"

echo ""
echo "🔧 Core Code vs Docs"
echo "--------------------"

# Check if backend is newer than architecture doc
BACKEND_TIME=$(stat -c %Y faithh_professional_backend_fixed.py 2>/dev/null || stat -f %m faithh_professional_backend_fixed.py 2>/dev/null)
ARCH_TIME=$(stat -c %Y ARCHITECTURE.md 2>/dev/null || stat -f %m ARCHITECTURE.md 2>/dev/null)

if [ $BACKEND_TIME -gt $ARCH_TIME ]; then
    echo -e "  ${YELLOW}⚠${NC} Backend modified after ARCHITECTURE.md - may need sync"
else
    echo -e "  ${GREEN}✓${NC} ARCHITECTURE.md is current with backend"
fi

# Check if UI is newer than its parity
UI_TIME=$(stat -c %Y faithh_pet_v4.html 2>/dev/null || stat -f %m faithh_pet_v4.html 2>/dev/null)
UI_PARITY_TIME=$(stat -c %Y parity/frontend/PARITY_UI_faithh_pet_v4.md 2>/dev/null || stat -f %m parity/frontend/PARITY_UI_faithh_pet_v4.md 2>/dev/null)

if [ -n "$UI_PARITY_TIME" ] && [ $UI_TIME -gt $UI_PARITY_TIME ]; then
    echo -e "  ${YELLOW}⚠${NC} UI modified after its parity file - may need sync"
else
    echo -e "  ${GREEN}✓${NC} UI parity is current (or doesn't exist)"
fi

echo ""
echo "📊 Summary"
echo "----------"

# Count files by age
FRESH=$(find . -maxdepth 1 -name "*.md" -mtime -7 2>/dev/null | wc -l)
STALE=$(find . -maxdepth 1 -name "*.md" -mtime +30 2>/dev/null | wc -l)

echo "  Root .md files updated in last 7 days: $FRESH"
echo "  Root .md files older than 30 days: $STALE"

echo ""
echo "💡 Recommendations"
echo "------------------"

if [ $STALE -gt 3 ]; then
    echo "  • Several docs are stale - consider a documentation review session"
fi

echo "  • Run this check weekly: ./scripts/doc_health_check.sh"
echo "  • Update LIFE_MAP.md when priorities change"
echo "  • Update decisions_log.json when making key decisions"
echo ""
echo "====================================="
