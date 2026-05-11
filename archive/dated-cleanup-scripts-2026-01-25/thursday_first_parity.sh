#!/bin/bash
# Thursday First Parity Files - Self-Documenting Edition
# Creates actual parity files for active system components

set -e

cd /home/jonat/ai-stack

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Session info
SESSION_NUM=5
SESSION_DATE=$(date +%Y-%m-%d)
SESSION_DAY="Thursday"
SESSION_START=$(date +%H:%M:%S)

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   FAITHH Thursday - First Parity Files             ║"
echo "║   Self-Documenting Automation                      ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Initialize work log
WORK_LOG=".thursday_work_log.tmp"
cat > "$WORK_LOG" << EOF
## Session $SESSION_NUM - $SESSION_DATE - $SESSION_DAY
**Week:** 1, Day 4
**Focus:** Create first parity files for active system components

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
# PHASE 1: Backend Parity File
# ============================================================
echo -e "${BLUE}Phase 1: Creating Backend Parity File${NC}"
echo "=================================================="
echo ""

cat > parity/backend/PARITY_faithh_professional_backend.md << 'EOF'
# PARITY: faithh_professional_backend.py
**Last Updated:** 2025-11-09
**Status:** Active
**Version:** 3.0.0

---

## Current State

**Purpose:** Main backend server for FAITHH AI assistant with RAG capabilities

**Key Features:**
- ChromaDB integration (91,302 documents)
- Gemini API integration via environment variables
- Ollama local model support
- Tool execution system
- File upload support
- Workspace scanning
- Model identification

**Dependencies:**
- Flask (web framework)
- ChromaDB (vector database)
- python-dotenv (environment variables)
- requests (HTTP client)
- Gemini API (cloud LLM)
- Ollama (local LLM)

**Entry Points:**
- Main server: `python3 faithh_professional_backend.py`
- Serves on: `http://localhost:5557`
- Debugger PIN: 587-685-700

---

## Recent Changes

### 2025-11-08 - Environment Variable Integration
**Changed:**
- Modified to load API keys from .env file
- Added `from dotenv import load_dotenv` import
- Added `load_dotenv()` call at startup
- Replaced hardcoded `GEMINI_API_KEY` with `os.getenv("GEMINI_API_KEY")`

**Reason:** Security improvement - no hardcoded secrets in code

**Impact:** 
- Requires .env file with GEMINI_API_KEY
- More secure deployment
- Easier configuration management

### 2025-11-06 - Initial Creation
**Created:**
- Fixed embedding dimensions (using text search)
- Model identification system
- File upload support
- Workspace scanning capabilities

**Reason:** Unified backend to replace multiple fragmented backends

---

## Known Issues

- [ ] Running on Flask development server (should use production WSGI for deployment)
- [ ] No rate limiting implemented
- [ ] Error handling could be more robust

---

## Pending Changes

- [ ] Add production WSGI server configuration
- [ ] Implement rate limiting middleware
- [ ] Add comprehensive error handling
- [ ] Add request/response logging
- [ ] Create health check endpoint enhancements

---

## Configuration

**Environment Variables Required:**
- `GEMINI_API_KEY` - Google Gemini API key for cloud LLM
- `OLLAMA_HOST` - Ollama server URL (default: http://localhost:11434)

**Config File Settings:**
```yaml
# From config.yaml
chromadb:
  host: localhost
  port: 8000
```

---

## API Endpoints

**Core Endpoints:**
- `GET /` - Serve UI
- `GET /api/status` - Health check (called every 30s by UI)
- `POST /api/chat` - Main chat endpoint
- `POST /api/upload` - File upload
- `GET /api/models` - List available models

---

## Testing

**How to Test:**
```bash
# Activate venv
source venv/bin/activate

# Start server
python3 faithh_professional_backend.py

# Should see:
# ✅ ChromaDB connected: 91302 documents available
# Starting on http://localhost:5557

# Test with curl
curl http://localhost:5557/api/status

# Or open UI in browser
# Open faithh_pet_v3.html
```

**Expected Behavior:**
- Server starts without errors
- ChromaDB connects successfully
- UI can send messages
- Responses are generated

---

## Architecture Notes

**Request Flow:**
```
UI (faithh_pet_v3.html)
    ↓
POST /api/chat
    ↓
Backend processes request
    ↓
RAG search in ChromaDB (if needed)
    ↓
LLM generation (Gemini or Ollama)
    ↓
Response to UI
```

**Model Selection:**
- Tries Gemini first (if API key available)
- Falls back to Ollama local models
- User can select model via UI

---

## Security

**Implemented:**
- ✅ API key in .env file (not hardcoded)
- ✅ .env in .gitignore (not committed)

**Needs Implementation:**
- [ ] Rate limiting
- [ ] Input validation
- [ ] CORS configuration
- [ ] Authentication/authorization

---

## Performance

**Current Stats:**
- ChromaDB: 91,302 documents indexed
- Response time: ~2-5s with RAG
- Memory usage: ~500MB

**Optimization Opportunities:**
- Cache frequent queries
- Batch process uploads
- Implement query result caching

---

## Notes

- Backend is kept in root directory for easy execution
- Multiple backup copies exist (.original, .prefixbackup)
- Flask debug mode enabled (disable for production)
- Watching file changes (auto-reloads on edits)

---

*Last reviewed: 2025-11-09*
EOF

log_action "Created parity/backend/PARITY_faithh_professional_backend.md"

echo ""

# ============================================================
# PHASE 2: Frontend Parity File
# ============================================================
echo -e "${BLUE}Phase 2: Creating Frontend Parity File${NC}"
echo "=================================================="
echo ""

cat > parity/frontend/PARITY_faithh_pet_v3.md << 'EOF'
# PARITY: faithh_pet_v3.html
**Last Updated:** 2025-11-09
**Status:** Active
**Version:** 3.0.0

---

## Current State

**Purpose:** MegaMan Battle Network themed chat interface for FAITHH AI assistant

**Key Features:**
- Real-time chat with AI
- Model selection dropdown
- RAG toggle switch
- System status indicator (heartbeat every 30s)
- MegaMan aesthetic (cyan/green gradient)
- Battle chip UI elements
- Responsive design

**Dependencies:**
- Backend API: http://localhost:5557
- No external CDN dependencies (self-contained)
- Pure HTML/CSS/JavaScript

---

## Recent Changes

### 2025-11-09 - Kept in Root
**Decision:**
- Kept in root directory for easy browser access
- Other HTML files moved to frontend/html/

**Reason:** Active UI should be easily accessible

### 2025-11-04 - Version 3 Creation
**Created:**
- MegaMan themed interface
- Battle chip design elements
- System status heartbeat
- Model selection feature
- RAG toggle

---

## Known Issues

- [ ] System status panel sometimes disappears (mentioned by user)
- [ ] No error message display for failed API calls
- [ ] No loading indicator during API requests
- [ ] No message history persistence

---

## Pending Changes

- [ ] Add context visibility panel
- [ ] Add process queue display
- [ ] Add battle chip system for tools
- [ ] Add message history save/load
- [ ] Improve error handling UI
- [ ] Add loading animations

---

## API Endpoints Used

**Backend Connection:**
- `GET /api/status` - Health check (polled every 30s)
- `POST /api/chat` - Send message, receive response
  - Body: `{message: string, model: string, use_rag: boolean}`
- `GET /api/models` - Get available model list

**Expected Responses:**
```javascript
// /api/status
{status: "ok", chromadb_docs: 91302}

// /api/chat
{response: "AI response text here"}

// /api/models
{models: ["gemini-pro", "llama3.1", ...]}
```

---

## UI Components

**Main Areas:**
1. **Header** - Title and branding
2. **System Status** - Server health indicator
3. **Chat Area** - Message display
4. **Controls** - Model select, RAG toggle
5. **Input** - Text input and send button

**Design Theme:**
- MegaMan Battle Network inspired
- Cyan/green color palette
- Retro-futuristic aesthetic
- Battle chip UI elements

---

## Testing

**How to Test:**
1. Ensure backend running: `python3 faithh_professional_backend.py`
2. Open in browser: `file:///home/jonat/ai-stack/faithh_pet_v3.html`
   - Or navigate to: `http://localhost:5557/`
3. Check system status shows green heartbeat
4. Send test message
5. Verify response appears

**Expected Behavior:**
- UI loads without errors
- System status shows "ONLINE" with heartbeat
- Can send messages
- Receives responses
- Model selection works
- RAG toggle works

---

## Configuration

**Backend URL:**
```javascript
const BACKEND_URL = 'http://localhost:5557';
```

**Polling Interval:**
```javascript
const STATUS_CHECK_INTERVAL = 30000; // 30 seconds
```

---

## Future Enhancements

**Planned Features (from architecture docs):**
1. **Context Panel** - Show what AI can see (RAG docs, files)
2. **Process Queue** - Display what AI is doing
3. **Battle Chips** - Visual tool selection system
4. **PULSE Monitor** - System health visualization
5. **Session History** - Save/load conversations

---

## Design Philosophy

**Goals:**
- Make AI interaction fun and engaging
- Visual feedback for all actions
- Clear system status
- Retro aesthetic that's still modern
- Battle chip metaphor for tools/commands

**Inspiration:**
- MegaMan Battle Network series
- Retro terminal UIs
- Cyberpunk aesthetics

---

## Notes

- Self-contained single file (no separate CSS/JS files)
- Works offline once loaded (except API calls)
- Kept in root for convenience
- 35KB file size (reasonable)
- No build process required

---

*Last reviewed: 2025-11-09*
EOF

log_action "Created parity/frontend/PARITY_faithh_pet_v3.md"

echo ""

# ============================================================
# PHASE 3: Config Parity Files
# ============================================================
echo -e "${BLUE}Phase 3: Creating Config Parity Files${NC}"
echo "=================================================="
echo ""

# .env parity
cat > parity/configs/PARITY_env.md << 'EOF'
# PARITY: .env
**Last Updated:** 2025-11-09
**Status:** Active (SECURED)
**Location:** Root directory (in .gitignore)

---

## Current State

**Purpose:** Store sensitive environment variables securely

**Key Settings:**
- `GEMINI_API_KEY` - Google Gemini API key
- `OLLAMA_HOST` - Ollama server URL
- `OLLAMA_URL` - Ollama API endpoint
- `BACKEND_PORT` - Backend server port (5557)
- `RAG_PORT` - RAG service port (5558)
- `CHROMADB_HOST` - ChromaDB host
- `CHROMADB_PORT` - ChromaDB port (8000)
- `ENVIRONMENT` - development/production
- `DEBUG` - Debug mode flag

**Used By:**
- faithh_professional_backend.py (loads via python-dotenv)

---

## Recent Changes

### 2025-11-08 - Initial Creation
**Created:**
- Created .env file with all configuration
- Added to .gitignore for security
- Configured backend to load from this file

**Reason:** Security best practice - no secrets in code

**Impact:** 
- All sensitive config centralized
- Easy environment-specific configuration
- No secrets in git repository

---

## Security Status

**✅ Secured:**
- File exists in root directory
- Listed in .gitignore (won't be committed)
- Only readable by user (should chmod 600)

**⚠️ Important:**
- NEVER commit this file to git
- NEVER share in chat/screenshots
- NEVER hardcode these values elsewhere

---

## Usage

**Loading in Python:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

**Loading in Bash:**
```bash
source .env
echo $GEMINI_API_KEY
```

---

## Template

**File Format:**
```env
# FAITHH Configuration
# Created: 2025-11-08

# Gemini API Key
GEMINI_API_KEY=your_key_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_URL=http://localhost:11434

# Backend Configuration
BACKEND_PORT=5557
RAG_PORT=5558

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# Environment
ENVIRONMENT=development
DEBUG=true
```

---

## Validation

**Check file exists and is secured:**
```bash
ls -la .env
# Should show: -rw------- (600 permissions)

# If not:
chmod 600 .env
```

**Check it's in .gitignore:**
```bash
grep ".env" .gitignore
# Should show: .env
```

---

## Notes

- Created as part of Monday security setup
- Replaced all hardcoded secrets
- Standard industry practice
- Works with python-dotenv package
- Template can be shared, actual file cannot

---

*Last reviewed: 2025-11-09*
EOF

log_action "Created parity/configs/PARITY_env.md"

# config.yaml parity
cat > parity/configs/PARITY_config.md << 'EOF'
# PARITY: config.yaml
**Last Updated:** 2025-11-09
**Status:** Active
**Location:** Root directory

---

## Current State

**Purpose:** Non-sensitive system configuration

**Key Settings:**
```yaml
chromadb:
  host: localhost
  port: 8000
  
models:
  gemini: gemini-pro
  ollama_default: llama3.1
  
rag:
  enabled: true
  max_results: 5
```

**Used By:**
- Backend for system configuration
- Various utilities and tools

---

## Recent Changes

### 2025-11-03 - Initial Configuration
**Created:**
- Basic ChromaDB configuration
- Model settings
- RAG configuration

---

## Settings Explained

**ChromaDB:**
- `host` - Where ChromaDB runs (localhost for local)
- `port` - ChromaDB port (8000 standard)

**Models:**
- `gemini` - Gemini model identifier
- `ollama_default` - Default Ollama model

**RAG:**
- `enabled` - Whether to use RAG by default
- `max_results` - How many docs to retrieve

---

## Notes

- Non-sensitive config (safe to commit)
- YAML format for readability
- Can be extended as needed
- Separate from .env (which has secrets)

---

*Last reviewed: 2025-11-09*
EOF

log_action "Created parity/configs/PARITY_config.md"

echo ""

# ============================================================
# PHASE 4: Update Changelog
# ============================================================
echo -e "${BLUE}Phase 4: Updating Changelog${NC}"
echo "=================================================="
echo ""

# Add to main changelog
cat >> parity/changelog/CHANGELOG.md << EOF

### Session 5 - $SESSION_DATE - Thursday - First Parity Files
**Added:**
- PARITY_faithh_professional_backend.md (backend documentation)
- PARITY_faithh_pet_v3.md (frontend documentation)
- PARITY_env.md (environment config documentation)
- PARITY_config.md (system config documentation)

**System:**
- Parity system now operational with real files
- Complete documentation for active components
- Audit trail established

EOF

log_action "Updated parity/changelog/CHANGELOG.md"

# Create session changelog
cat > parity/changelog/SESSION_5_CHANGELOG.md << EOF
# Session 5 Detailed Changelog
**Date:** $SESSION_DATE
**Focus:** Create First Parity Files

---

## Changes Made

### Parity Files Created

**1. Backend Parity**
- File: parity/backend/PARITY_faithh_professional_backend.md
- Documents: Active backend server
- Includes: Architecture, API endpoints, configuration, known issues

**2. Frontend Parity**
- File: parity/frontend/PARITY_faithh_pet_v3.md
- Documents: Main UI
- Includes: Features, API usage, design philosophy, enhancements

**3. Config Parity**
- File: parity/configs/PARITY_env.md
- Documents: Environment variables (sensitive)
- Includes: Security status, usage, validation

- File: parity/configs/PARITY_config.md
- Documents: System configuration (non-sensitive)
- Includes: Settings explained, purpose

---

## Documentation Coverage

**Active Components:**
- ✅ Backend server
- ✅ Main UI
- ✅ Environment config
- ✅ System config

**Total Parity Files:** 4

---

## Impact

- ✅ Complete documentation of active system
- ✅ Technical details preserved
- ✅ Change history tracked
- ✅ Known issues documented
- ✅ Future improvements planned

---

## Next Steps

1. Test parity update workflow with real changes
2. Create parity files for additional components as needed
3. Establish routine parity maintenance

---

*Auto-generated by thursday_first_parity.sh*
EOF

log_action "Created SESSION_5_CHANGELOG.md"

log_decision "**Decision:** Start with 4 core parity files (backend, frontend, 2 configs)"
log_decision "**Decision:** Add more parity files as needed, not all at once"
log_decision "**Decision:** Focus on active components first"

echo ""

# ============================================================
# PHASE 5: Demonstrate Parity Status
# ============================================================
echo -e "${BLUE}Phase 5: Parity System Status${NC}"
echo "=================================================="
echo ""

echo "Current parity files:"
find parity -name "PARITY_*.md" -type f | sort

echo ""
echo "Statistics:"
echo "  Backend parity files: $(find parity/backend -name "PARITY_*.md" 2>/dev/null | wc -l)"
echo "  Frontend parity files: $(find parity/frontend -name "PARITY_*.md" 2>/dev/null | wc -l)"
echo "  Config parity files: $(find parity/configs -name "PARITY_*.md" 2>/dev/null | wc -l)"
echo "  Total: $(find parity -name "PARITY_*.md" -type f 2>/dev/null | wc -l)"

echo ""

# ============================================================
# FINALIZE: Update MASTER_ACTION
# ============================================================

SESSION_END=$(date +%H:%M:%S)

if [ -f "$WORK_LOG.decisions" ]; then
    echo "" >> "$WORK_LOG"
    echo "**Decisions Made:**" >> "$WORK_LOG"
    cat "$WORK_LOG.decisions" >> "$WORK_LOG"
    rm "$WORK_LOG.decisions"
fi

cat >> "$WORK_LOG" << EOF

**Parity Files Created:**
- parity/backend/PARITY_faithh_professional_backend.md
- parity/frontend/PARITY_faithh_pet_v3.md
- parity/configs/PARITY_env.md
- parity/configs/PARITY_config.md

**Changelog Updates:**
- Updated main CHANGELOG.md
- Created SESSION_5_CHANGELOG.md

**System Status:**
- 4 active parity files
- Core components fully documented
- Parity system operational

**Status:** ✅ Thursday first parity files complete

**Next Session:**
- Complete Week 1 validation
- End-to-end system test
- Verify all automation working
- Week 1 completion report

**Time Spent:** Started $SESSION_START, Ended $SESSION_END

---

EOF

echo "" >> MASTER_ACTION_FAITHH.md
cat "$WORK_LOG" >> MASTER_ACTION_FAITHH.md
rm "$WORK_LOG"

# ============================================================
# SUMMARY
# ============================================================

echo ""
echo "════════════════════════════════════════════════════"
echo "✨ THURSDAY FIRST PARITY FILES COMPLETE! ✨"
echo "════════════════════════════════════════════════════"
echo ""
echo "Parity Files Created:"
echo "  ✅ Backend (faithh_professional_backend.py)"
echo "  ✅ Frontend (faithh_pet_v3.html)"
echo "  ✅ Config (.env - secured)"
echo "  ✅ Config (config.yaml)"
echo ""
echo "System Documentation:"
echo "  📊 4 active parity files"
echo "  📝 Complete technical details"
echo "  🔄 Change history tracked"
echo "  ⚠️  Known issues documented"
echo ""
echo "Helper Commands:"
echo "  📊 Status: ./scripts/parity_status.sh"
echo "  ✏️  Update: ./scripts/update_parity.sh [type] [file]"
echo ""
echo "📊 MASTER_ACTION automatically updated!"
echo "   Check: tail -50 MASTER_ACTION_FAITHH.md"
echo ""
echo "Next: Friday - Complete Week 1 validation"
echo ""
echo "════════════════════════════════════════════════════"
echo ""
