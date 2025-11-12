#!/bin/bash
# Wednesday Parity System Setup - Self-Documenting Edition
# Creates parity file structure and establishes tracking system

set -e

cd /home/jonat/ai-stack

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Session info
SESSION_NUM=4
SESSION_DATE=$(date +%Y-%m-%d)
SESSION_DAY="Wednesday"
SESSION_START=$(date +%H:%M:%S)

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   FAITHH Wednesday - Parity System Setup           ║"
echo "║   Self-Documenting Automation                      ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Initialize work log
WORK_LOG=".wednesday_work_log.tmp"
cat > "$WORK_LOG" << EOF
## Session $SESSION_NUM - $SESSION_DATE - $SESSION_DAY
**Week:** 1, Day 3
**Focus:** Parity system initialization and structure setup

**Completed:**
EOF

# Logging functions
log_action() {
    echo "- $1" >> "$WORK_LOG"
    echo -e "${GREEN}✅ $1${NC}"
}

log_decision() {
    echo "$1" >> "$WORK_LOG.decisions"
}

# ============================================================
# PHASE 1: Create Parity Directory Structure
# ============================================================
echo -e "${BLUE}Phase 1: Creating Parity Directory Structure${NC}"
echo "=================================================="
echo ""

# Create main parity directories
mkdir -p parity/backend
mkdir -p parity/frontend
mkdir -p parity/configs
mkdir -p parity/docs
mkdir -p parity/changelog
mkdir -p parity/templates

log_action "Created parity directory structure (6 folders)"

# Create .gitkeep files to preserve structure
touch parity/backend/.gitkeep
touch parity/frontend/.gitkeep
touch parity/configs/.gitkeep
touch parity/docs/.gitkeep
touch parity/changelog/.gitkeep
touch parity/templates/.gitkeep

log_action "Added .gitkeep files to preserve empty directories"

echo ""

# ============================================================
# PHASE 2: Create Parity System Documentation
# ============================================================
echo -e "${BLUE}Phase 2: Creating Parity Documentation${NC}"
echo "=================================================="
echo ""

# Main parity README
cat > parity/README.md << 'EOF'
# FAITHH Parity System
**Self-Documenting File Change Tracking**

## What is Parity?

The parity system is a lightweight change tracking mechanism where each important file has a corresponding "parity file" that documents:
- Current state and version
- Recent changes made
- Decisions and rationale
- Known issues
- Pending changes

## Directory Structure

```
parity/
├── backend/           # Backend code parity files
├── frontend/          # UI parity files
├── configs/           # Configuration parity files
├── docs/              # Documentation parity files
├── changelog/         # Overall change logs
└── templates/         # Parity file templates
```

## How It Works

### 1. Important File Created/Modified
When you modify an important file (e.g., `faithh_professional_backend.py`):

### 2. Parity File Updated
The corresponding parity file (`parity/backend/PARITY_backend.md`) is updated with:
- What changed
- Why it changed
- Current status

### 3. Automatic Updates
Scripts automatically update parity files as they work, creating perfect audit trail.

## Parity File Format

Each parity file follows this structure:

```markdown
# PARITY: [Filename]
**Last Updated:** [Date]
**Status:** [Active/Stable/Deprecated]

## Current State
- Version: X.Y.Z
- Purpose: [What this file does]
- Dependencies: [What it relies on]

## Recent Changes
### [Date] - [Description]
- [Change 1]
- [Change 2]
- Reason: [Why changes made]

## Known Issues
- [Issue 1]
- [Issue 2]

## Pending Changes
- [ ] [Planned change 1]
- [ ] [Planned change 2]
```

## Usage Patterns

### Manual Update (Rare)
```bash
nano parity/backend/PARITY_backend.md
# Add your changes under "Recent Changes"
```

### Automatic Update (Preferred)
Scripts that modify files automatically update corresponding parity files:
```bash
# Script modifies backend
# Script logs changes to parity file
# You = zero manual work!
```

## Benefits

✅ **Perfect Audit Trail** - Know what changed and why
✅ **Context Preservation** - Future you/AI knows the history
✅ **Change Justification** - Decisions are documented
✅ **Issue Tracking** - Problems noted immediately
✅ **Local AI Ready** - Works with any LLM

## Key Principles

1. **Lightweight** - Just markdown files, no complex tools
2. **Automatic** - Scripts update parity files themselves
3. **Human Readable** - Anyone can read and understand
4. **AI Friendly** - Perfect for LLM context
5. **Portable** - Works offline, no dependencies

## Getting Started

1. Create parity file for important code file
2. Document initial state
3. Update parity file when code changes
4. Review parity files to understand history

## Examples

See `templates/` folder for parity file templates.

---

*Part of FAITHH self-documenting automation system*
EOF

log_action "Created parity/README.md (system documentation)"

# ============================================================
# PHASE 3: Create Parity File Templates
# ============================================================
echo -e "${BLUE}Phase 3: Creating Parity Templates${NC}"
echo "=================================================="
echo ""

# Backend parity template
cat > parity/templates/PARITY_backend_template.md << 'EOF'
# PARITY: [filename].py
**Last Updated:** [YYYY-MM-DD]
**Status:** Active | Stable | Deprecated
**Version:** 1.0.0

---

## Current State

**Purpose:** [What this file does - one sentence]

**Key Features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

**Dependencies:**
- [Python package 1]
- [Python package 2]
- [Internal file 1]

**Entry Points:**
- [Function/class that starts things]

---

## Recent Changes

### [YYYY-MM-DD] - [Brief description]
**Changed:**
- [Specific change 1]
- [Specific change 2]

**Reason:** [Why this change was made]

**Impact:** [What this affects]

---

## Known Issues

- [ ] [Issue 1 - describe the problem]
- [ ] [Issue 2 - describe the problem]

---

## Pending Changes

- [ ] [Planned improvement 1]
- [ ] [Planned improvement 2]
- [ ] [Planned refactor 3]

---

## Configuration

**Environment Variables Required:**
- `ENV_VAR_1` - [description]
- `ENV_VAR_2` - [description]

**Config File Settings:**
```yaml
setting1: value
setting2: value
```

---

## Testing

**How to Test:**
```bash
# Test command
python3 [filename].py
```

**Expected Behavior:**
- [What should happen]

---

## Notes

[Any additional context, gotchas, or important information]

---

*Last reviewed: [YYYY-MM-DD]*
EOF

log_action "Created backend parity template"

# Frontend parity template
cat > parity/templates/PARITY_frontend_template.md << 'EOF'
# PARITY: [filename].html
**Last Updated:** [YYYY-MM-DD]
**Status:** Active | Stable | Deprecated
**Version:** 1.0.0

---

## Current State

**Purpose:** [What this UI does - one sentence]

**Key Features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

**Dependencies:**
- [External library 1]
- [External library 2]
- Backend API: [endpoint]

---

## Recent Changes

### [YYYY-MM-DD] - [Brief description]
**Changed:**
- [UI change 1]
- [UI change 2]

**Reason:** [Why this change was made]

**User Impact:** [How users are affected]

---

## Known Issues

- [ ] [UI issue 1]
- [ ] [UI issue 2]

---

## Pending Changes

- [ ] [Planned UI improvement 1]
- [ ] [Planned feature 2]

---

## API Endpoints Used

**Backend Connection:**
- `POST /api/chat` - [purpose]
- `GET /api/status` - [purpose]
- `POST /api/upload` - [purpose]

---

## Testing

**How to Test:**
1. Open in browser: `file:///path/to/file.html`
2. Or start backend and navigate to: `http://localhost:5557`
3. Test features: [list test scenarios]

**Expected Behavior:**
- [What should happen]

---

## Notes

[Any additional context, design decisions, or important information]

---

*Last reviewed: [YYYY-MM-DD]*
EOF

log_action "Created frontend parity template"

# Config parity template
cat > parity/templates/PARITY_config_template.md << 'EOF'
# PARITY: [filename].[ext]
**Last Updated:** [YYYY-MM-DD]
**Status:** Active | Stable | Deprecated

---

## Current State

**Purpose:** [What this config controls]

**Key Settings:**
- `setting1` - [description]
- `setting2` - [description]
- `setting3` - [description]

**Used By:**
- [Component 1]
- [Component 2]

---

## Recent Changes

### [YYYY-MM-DD] - [Brief description]
**Changed:**
- [Setting changed]
- [New setting added]

**Reason:** [Why this change was made]

**Impact:** [What components are affected]

---

## Known Issues

- [ ] [Config issue 1]
- [ ] [Config issue 2]

---

## Pending Changes

- [ ] [Planned config change 1]
- [ ] [Planned addition 2]

---

## Security Notes

**Sensitive Values:**
- [List what should be in .env, not hardcoded]

**Access Control:**
- [Who/what should have access]

---

## Testing

**Validation:**
```bash
# How to validate config is correct
```

**Expected Behavior:**
- [What should happen with this config]

---

## Notes

[Any additional context or important information]

---

*Last reviewed: [YYYY-MM-DD]*
EOF

log_action "Created config parity template"

echo ""

# ============================================================
# PHASE 4: Create Changelog Structure
# ============================================================
echo -e "${BLUE}Phase 4: Creating Changelog System${NC}"
echo "=================================================="
echo ""

# Main changelog
cat > parity/changelog/CHANGELOG.md << EOF
# FAITHH Project Changelog
**Comprehensive Change History**

This file tracks all significant changes across the FAITHH project.

---

## [Week 1] - November 2025

### Session 1 - 2025-11-06 - Initial Setup
**Added:**
- ChromaDB integration (91,302 documents)
- Unified backend system
- Streamlit UI alternative
- Complete documentation system

### Session 2 - 2025-11-08 - Monday - Environment Setup
**Added:**
- .env file for secure configuration
- .gitignore for security
- python-dotenv integration
- Self-documenting script system

**Changed:**
- Backend now uses .env instead of hardcoded keys
- Project directory organized

**Removed:**
- ~/faithh old project folder
- Hardcoded API keys from backend

### Session 3 - 2025-11-09 - Tuesday - File Organization
**Added:**
- Documentation organization system
- Script organization system
- ROOT_FILES_GUIDE.md
- docs/DOCUMENTATION_INDEX.md

**Changed:**
- 28 documentation files archived
- 22 scripts moved to scripts/
- Session reports moved to docs/session-reports/

**Organized:**
- Backend files
- Frontend files
- Documentation structure

### Session 4 - $SESSION_DATE - Wednesday - Parity Setup
**Added:**
- Parity directory structure
- Parity system documentation
- Parity file templates
- This changelog

**System:**
- Self-documenting automation established
- Perfect audit trail implemented

---

## Change Categories

**Added** - New features or files
**Changed** - Modifications to existing functionality
**Deprecated** - Features marked for removal
**Removed** - Deleted features or files
**Fixed** - Bug fixes
**Security** - Security improvements
**Organized** - Structural improvements

---

*This changelog is automatically updated by self-documenting scripts*
EOF

log_action "Created parity/changelog/CHANGELOG.md"

# Create session-specific changelog
cat > parity/changelog/SESSION_4_CHANGELOG.md << EOF
# Session 4 Detailed Changelog
**Date:** $SESSION_DATE
**Focus:** Parity System Setup

---

## Changes Made

### Parity System
- Created \`parity/\` directory structure
- Added 6 subdirectories for organization
- Created comprehensive README.md
- Established parity file format standard

### Templates
- Backend parity template
- Frontend parity template
- Config parity template

### Documentation
- System overview and usage guide
- Changelog structure established
- Example parity files

---

## Decisions Made

1. **Lightweight Format**: Use markdown for human and AI readability
2. **Automatic Updates**: Scripts update parity files, not humans
3. **Directory Structure**: Organized by file type (backend/frontend/config)
4. **Template-Based**: Consistent format across all parity files

---

## Impact

- ✅ Perfect audit trail established
- ✅ Change history preserved
- ✅ Future AI can understand all changes
- ✅ Local AI ready
- ✅ Zero external dependencies

---

## Next Steps

1. Create first parity file for active backend
2. Create parity file for active UI
3. Establish update workflow
4. Test with actual changes

---

*Auto-generated by wednesday_parity_setup.sh*
EOF

log_action "Created SESSION_4_CHANGELOG.md"

echo ""

# ============================================================
# PHASE 5: Create Parity Update Helper Script
# ============================================================
echo -e "${BLUE}Phase 5: Creating Helper Scripts${NC}"
echo "=================================================="
echo ""

# Create helper script for manual parity updates
cat > scripts/update_parity.sh << 'HELPER'
#!/bin/bash
# Helper script to update parity files
# Usage: ./update_parity.sh [backend|frontend|config] [filename]

PARITY_DIR="parity"
TYPE=$1
FILENAME=$2
DATE=$(date +%Y-%m-%d)

if [ -z "$TYPE" ] || [ -z "$FILENAME" ]; then
    echo "Usage: ./update_parity.sh [backend|frontend|config] [filename]"
    echo ""
    echo "Examples:"
    echo "  ./update_parity.sh backend faithh_professional_backend.py"
    echo "  ./update_parity.sh frontend faithh_pet_v3.html"
    echo "  ./update_parity.sh config config.yaml"
    exit 1
fi

PARITY_FILE="$PARITY_DIR/$TYPE/PARITY_${FILENAME%.*}.md"

if [ ! -f "$PARITY_FILE" ]; then
    echo "⚠️  Parity file doesn't exist: $PARITY_FILE"
    echo "Creating from template..."
    
    # Copy appropriate template
    case $TYPE in
        backend)
            cp parity/templates/PARITY_backend_template.md "$PARITY_FILE"
            ;;
        frontend)
            cp parity/templates/PARITY_frontend_template.md "$PARITY_FILE"
            ;;
        config)
            cp parity/templates/PARITY_config_template.md "$PARITY_FILE"
            ;;
    esac
    
    # Update filename in template
    sed -i "s/\[filename\]/$FILENAME/g" "$PARITY_FILE"
    sed -i "s/\[YYYY-MM-DD\]/$DATE/g" "$PARITY_FILE"
    
    echo "✅ Created new parity file: $PARITY_FILE"
fi

echo "📝 Opening parity file for editing..."
nano "$PARITY_FILE"

echo "✅ Parity file updated!"
HELPER

chmod +x scripts/update_parity.sh

log_action "Created scripts/update_parity.sh helper"

# Create quick status script
cat > scripts/parity_status.sh << 'STATUS'
#!/bin/bash
# Show parity system status

echo "╔════════════════════════════════════════════════════╗"
echo "║   FAITHH Parity System Status                      ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

echo "📁 Parity Directory Structure:"
tree -L 2 parity/ 2>/dev/null || find parity/ -type d | sort

echo ""
echo "📊 Parity Files by Category:"
echo "  Backend: $(find parity/backend -name "PARITY_*.md" 2>/dev/null | wc -l) files"
echo "  Frontend: $(find parity/frontend -name "PARITY_*.md" 2>/dev/null | wc -l) files"
echo "  Config: $(find parity/configs -name "PARITY_*.md" 2>/dev/null | wc -l) files"
echo "  Docs: $(find parity/docs -name "PARITY_*.md" 2>/dev/null | wc -l) files"

echo ""
echo "📝 Recent Changes (from changelog):"
tail -20 parity/changelog/CHANGELOG.md | grep -E "^###|^-" | head -10

echo ""
echo "✅ Parity system operational!"
STATUS

chmod +x scripts/parity_status.sh

log_action "Created scripts/parity_status.sh status checker"

echo ""

# ============================================================
# PHASE 6: Document Integration with MASTER_ACTION
# ============================================================
echo -e "${BLUE}Phase 6: Integration Documentation${NC}"
echo "=================================================="
echo ""

cat > parity/docs/INTEGRATION_GUIDE.md << 'EOF'
# Parity System Integration Guide

## How Parity Integrates with MASTER_ACTION

### Two Levels of Documentation

**1. MASTER_ACTION (High-Level)**
- Session-by-session progress
- What was accomplished
- Decisions made
- Status updates

**2. Parity Files (Detail-Level)**
- File-specific changes
- Technical details
- Code-level decisions
- Implementation notes

### The Relationship

```
MASTER_ACTION
    ↓
Says: "Updated backend to use .env"
    ↓
PARITY_backend.md
    ↓
Details: "Modified lines 47-48, added load_dotenv(), 
          removed hardcoded key, tested with .env file"
```

### When to Use Each

**MASTER_ACTION for:**
- Session summaries
- Overall progress tracking
- High-level decisions
- Continuity between sessions

**Parity Files for:**
- Technical implementation details
- Code-specific changes
- File-level documentation
- Developer reference

### Workflow

```
1. Script does work
2. Script updates parity file (technical details)
3. Script updates MASTER_ACTION (session summary)
4. Both stay in sync automatically!
```

### Example

**MASTER_ACTION Entry:**
```markdown
## Session 5
- Updated backend security
- Fixed configuration loading
```

**Parity File Entry:**
```markdown
### 2025-11-10 - Security Enhancement
- Added input validation on lines 150-165
- Implemented rate limiting middleware
- Updated JWT token expiration to 24h
Reason: Address security audit findings
```

### Benefits of Dual System

✅ **High-level** progress in MASTER_ACTION
✅ **Low-level** details in parity files  
✅ **Best of both worlds** - overview + depth
✅ **AI-friendly** - can read either level as needed

---

*Part of self-documenting automation system*
EOF

log_action "Created parity/docs/INTEGRATION_GUIDE.md"

log_decision "**Decision:** Use parity system for file-level detail, MASTER_ACTION for session summaries"
log_decision "**Decision:** Scripts update both systems automatically"
log_decision "**Decision:** Lightweight markdown format for universal compatibility"

echo ""

# ============================================================
# FINALIZE: Update MASTER_ACTION
# ============================================================

SESSION_END=$(date +%H:%M:%S)

# Add decisions
if [ -f "$WORK_LOG.decisions" ]; then
    echo "" >> "$WORK_LOG"
    echo "**Decisions Made:**" >> "$WORK_LOG"
    cat "$WORK_LOG.decisions" >> "$WORK_LOG"
    rm "$WORK_LOG.decisions"
fi

# Add summary
cat >> "$WORK_LOG" << EOF

**Files Created:**
- parity/README.md (system documentation)
- parity/templates/*.md (3 templates)
- parity/changelog/CHANGELOG.md
- parity/changelog/SESSION_4_CHANGELOG.md
- parity/docs/INTEGRATION_GUIDE.md
- scripts/update_parity.sh (helper)
- scripts/parity_status.sh (status checker)

**Directory Structure:**
- parity/backend/
- parity/frontend/
- parity/configs/
- parity/docs/
- parity/changelog/
- parity/templates/

**Status:** ✅ Wednesday parity setup complete

**Next Session:**
- Create first parity files for active code
- Establish parity update workflow
- Test parity system with actual changes

**Time Spent:** Started $SESSION_START, Ended $SESSION_END

---

EOF

# Append to MASTER_ACTION
echo "" >> MASTER_ACTION_FAITHH.md
cat "$WORK_LOG" >> MASTER_ACTION_FAITHH.md

# Clean up
rm "$WORK_LOG"

# ============================================================
# SUMMARY
# ============================================================

echo ""
echo "════════════════════════════════════════════════════"
echo "✨ WEDNESDAY PARITY SETUP COMPLETE! ✨"
echo "════════════════════════════════════════════════════"
echo ""
echo "Parity System Created:"
echo "  ✅ Directory structure (6 folders)"
echo "  ✅ System documentation"
echo "  ✅ 3 parity file templates"
echo "  ✅ Changelog system"
echo "  ✅ Helper scripts"
echo "  ✅ Integration guide"
echo ""
echo "Helper Commands:"
echo "  📊 Status: ./scripts/parity_status.sh"
echo "  ✏️  Update: ./scripts/update_parity.sh [type] [file]"
echo ""
echo "📊 MASTER_ACTION automatically updated!"
echo "   Check: tail -50 MASTER_ACTION_FAITHH.md"
echo ""
echo "Next: Thursday - Create first parity files"
echo ""
echo "════════════════════════════════════════════════════"
echo ""
