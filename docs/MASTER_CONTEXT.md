# FAITHH System - Master Context & Priority Matrix

**Last Updated:** 2024-11-14 23:45
**Current Session:** RAG restoration & documentation system setup
**System Status:** Backend operational, RAG broken (embedding mismatch)

---

## 🎯 CURRENT PRIORITY: P0 - Fix RAG Document Retrieval

**Status:** Backend running but ChromaDB embedding dimension mismatch
**Issue:** Collection expects 768-dim embeddings, backend using 384-dim default
**Impact:** FAITHH has no memory of your documents or conversations
**Fix Ready:** `faithh_professional_backend_fixed.py` with correct embedding model
**Next Step:** Deploy fixed backend and test document retrieval

---

## 📊 SYSTEM STATUS SNAPSHOT

### ✅ Working Components
- **FAITHH Backend**: Running on port 5557 (v3, with bugs)
- **Docker ChromaDB**: Running on port 8000, 91,302 documents stored
- **Ollama**: 3 models available (qwen2.5-coder:7b, qwen2.5-7b, llama3.1-8b)
- **Gemini API**: Configured (gemini-2.0-flash-exp)
- **Documentation System**: Parity files created in `~/ai-stack/docs/`

### 🚧 Partially Working
- **Chat endpoint**: Operational but some Flask return errors
- **RAG queries**: Connection works but embedding mismatch prevents retrieval
- **Status endpoint**: Sometimes times out

### ❌ Not Working / Broken
- **Document retrieval**: ChromaDB won't return documents (embedding dimension error)
- **Context-aware chat**: FAITHH has no knowledge of your system/docs
- **WSL->Docker volume mount**: ChromaDB using separate Docker volume instead of WSL data

### 🔍 Evidence of Current Issue
From FAITHH chat log:
```
USER: Do you know about my AI model FAITHH
FAITHH: I don't have any information about an AI model called "FAITHH"
```
This proves RAG is not providing context from your 91K documents.

---

## 🗺️ PROJECT ROADMAP - LINEAR EXECUTION PATH

### PHASE 1: Core Functionality Restoration (CURRENT)
**Objective:** Get FAITHH fully operational with working memory/RAG

#### 🔴 P0 - CRITICAL (Do Immediately)

**1.1 Deploy Fixed Backend**
- **File:** `~/ai-stack/faithh_professional_backend_fixed.py`
- **What it fixes:** Uses correct 768-dim embedding model (all-mpnet-base-v2)
- **Commands:**
  ```bash
  pkill -f faithh_professional_backend
  cd ~/ai-stack && source venv/bin/activate
  nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &
  ```
- **Test:** `curl -s http://localhost:5557/api/status | jq '.services.chromadb'`
- **Success criteria:** No embedding dimension errors in logs

**1.2 Verify RAG Document Retrieval**
- **Test query:** "What is FAITHH?" (should find docs about your system)
- **Endpoint:** POST to `/api/rag_search` with query
- **Expected:** Returns relevant documents from 91K collection
- **Update:** CURRENT_STATE.md with results

**1.3 Test FAITHH Conversation with Context**
- Ask FAITHH "Do you know about my AI model FAITHH?" again
- Should now return information from your documentation
- Verify context is being injected into responses

#### 🟡 P1 - HIGH PRIORITY (Do Next)

**1.4 Docker Services Audit**
- Run `docker ps -a` and document all containers
- Identify what's running: LangFlow, ChromaDB, others?
- Update DOCKER_SERVICES.md with complete inventory
- Clean up unused/dead containers

**1.5 Fix ChromaDB Volume Mount** (Optional)
- Current: ChromaDB uses Docker volume `ai-stack_chromadb_data`
- Your data: WSL directory `~/ai-stack/faithh_rag/` (91K docs)
- Decision needed: Keep separate or migrate to shared mount?
- **Note:** Not urgent since Docker ChromaDB has the 91K docs

---

### PHASE 2: Documentation & Continuity System
**Objective:** Self-documenting system that tracks changes and maintains context

#### 🟡 P1 - HIGH PRIORITY

**2.1 Parity File Entry Point System**
- **Purpose:** Claude/FAITHH read MASTER_CONTEXT.md at session start
- **Behavior:** Auto-fingerprint what to work on based on priority matrix
- **Location:** `~/ai-stack/docs/MASTER_CONTEXT.md` (this file!)
- **Integration:** 
  - Claude Code reads this on startup
  - FAITHH backend logs session summaries here
  - Auto-updates after each work session

**2.2 Session Summary Automation**
- **Goal:** Capture what you discussed with FAITHH and auto-document
- **Implementation ideas:**
  - Backend logs all chat interactions
  - Daily/session summary script extracts key topics
  - Updates CURRENT_STATE.md automatically
  - Flags code changes that need documentation

**2.3 Code Continuity Analysis**
- **Goal:** Detect when code changes break documented architecture
- **Implementation:**
  - Git hooks to detect backend changes
  - Compare against BACKEND_CONFIG.md
  - Alert when changes conflict with documented behavior
  - Suggest documentation updates

**2.4 Master Action Log System**
- **Goal:** Track all system changes automatically
- **Format:** Timestamped entries like git log but for all actions
- **Contents:**
  - Backend restarts
  - Configuration changes
  - RAG queries and results
  - Session summaries
- **Storage:** `~/ai-stack/logs/master_action.log`

#### 🟢 P2 - MEDIUM PRIORITY

**2.5 Create Management Scripts**
- `faithh_start.sh` - Start all services (backend, ChromaDB, Ollama)
- `faithh_stop.sh` - Stop all services gracefully
- `faithh_status.sh` - Health check all components
- `faithh_logs.sh` - Tail all relevant logs
- `faithh_update_docs.sh` - Regenerate documentation from current state

**2.6 Create docker-compose.yml**
- Define all Docker services in one file
- ChromaDB with proper volume mount
- LangFlow configuration
- Easy `docker-compose up -d` startup

---

### PHASE 3: UI & User Experience
**Objective:** Polish the MegaMan Battle Network interface

#### 🟢 P2 - MEDIUM PRIORITY

**3.1 FAITHH v4 UI Polish**
- Fix styling inconsistencies
- Add loading animations (NetNavi style)
- Implement proper error handling/display
- Voice input integration

**3.2 ComfyUI Avatar Generation**
- Generate FAITHH character (cyan theme)
- Generate PULSE character (blue theme)
- Create battle chip animations
- Integrate avatars into UI

**3.3 Session Logging in UI**
- Display current session info
- Show RAG hit/miss indicators
- Model switching UI
- Context window usage display

---

### PHASE 4: Advanced Features
**Objective:** DAW integration and production workflow

#### 🔵 P3 - FUTURE ENHANCEMENTS

**4.1 Luna DAW Integration**
- Voice commands for plugin control
- Code generation for audio scripts
- Project file analysis
- Session recall by audio description

**4.2 Voice-to-Text Integration**
- Hands-free FAITHH interaction
- Audio logging for session recap
- Voice command shortcuts

**4.3 Multi-modal RAG**
- Index audio files (stems, mixdowns)
- Search by audio similarity
- Lyrics/metadata indexing

---

## 🎨 PROJECT VISION & THEMES

### Core Identity
- **Name:** FAITHH (Friendly AI Teaching & Helping Hub)
- **Aesthetic:** MegaMan Battle Network retro-futuristic terminal
- **Characters:** 
  - FAITHH (cyan, helpful assistant)
  - PULSE (blue, technical monitor)
- **Purpose:** Personal AI assistant with memory, integrated into creative workflow

### Design Principles
1. **Memory-first:** Always knows context from past work
2. **Self-documenting:** System maintains its own documentation
3. **Continuity-aware:** Detects when changes break established patterns
4. **Creative-focused:** Built for audio production workflow
5. **Aesthetically cohesive:** MegaMan BN theme throughout

---

## 📁 KEY FILE LOCATIONS

### Documentation (Entry Points)
- **MASTER_CONTEXT.md** (this file) - Overall roadmap and priorities
- **CURRENT_STATE.md** - What's working/broken right now
- **CHROMADB_STATUS.md** - ChromaDB diagnostics and solutions
- **DOCKER_SERVICES.md** - Service architecture
- **BACKEND_CONFIG.md** - Backend management guide
- **README.md** - Quick start guide

### Code
- **Backend (current):** `~/ai-stack/faithh_professional_backend.py` (v3, buggy)
- **Backend (fixed):** `~/ai-stack/faithh_professional_backend_fixed.py` (v3.1, ready)
- **UI:** `~/ai-stack/faithh_v4.html`
- **ChromaDB:** `~/ai-stack/faithh_rag/chroma.sqlite3` (239MB, 91K docs)

### Logs
- **Backend:** `~/ai-stack/faithh_backend.log`
- **Future:** `~/ai-stack/logs/master_action.log`

### Uploads & Workspace
- **Uploads:** `~/ai-stack/uploads/`
- **Project root:** `~/ai-stack/`

---

## 🚦 HOW TO USE THIS FILE

### For You (Jonathan)
1. **At session start:** Read "CURRENT PRIORITY" section
2. **Check:** What phase and priority level you're on
3. **Execute:** Tasks in linear order (P0 → P1 → P2 → P3)
4. **Update:** CURRENT_STATE.md when tasks complete
5. **Return here:** When done or stuck, re-evaluate priorities

### For Claude (Chat/Code)
1. **On session start:** Read this file FIRST
2. **Identify:** Current priority tasks (P0)
3. **Check:** CURRENT_STATE.md for latest status
4. **Execute:** Work on highest priority incomplete task
5. **Update:** Both files after completing work
6. **Document:** Changes in relevant config files

### For FAITHH (Future Integration)
1. **On startup:** Load this context via RAG
2. **During chat:** Reference this for system awareness
3. **After session:** Generate summary and update docs
4. **Continuous:** Monitor for code changes that need documentation

---

## 🎯 SUCCESS METRICS

### Phase 1 Complete When:
- ✅ RAG returns relevant documents on queries
- ✅ FAITHH knows about itself and your system
- ✅ No embedding dimension errors in logs
- ✅ Status endpoint returns accurate data
- ✅ All Docker services documented

### Phase 2 Complete When:
- ✅ Session summaries auto-generate
- ✅ MASTER_CONTEXT updates automatically
- ✅ Code changes trigger documentation alerts
- ✅ Management scripts operational

### Phase 3 Complete When:
- ✅ UI is polished and error-free
- ✅ FAITHH/PULSE avatars integrated
- ✅ Voice input working

### Phase 4 Complete When:
- ✅ Luna DAW responds to voice commands
- ✅ Multi-modal RAG searches audio files
- ✅ Production workflow fully integrated

---

## 🔄 MAINTENANCE SCHEDULE

### Daily (Automated)
- Session summary generation
- Log rotation
- CURRENT_STATE.md update

### Weekly (Manual)
- Review completed tasks
- Adjust priorities based on progress
- Clean up unused files/containers

### Monthly (Manual)
- Full system audit
- Documentation review
- Archive old sessions

---

**Remember:** Linear execution prevents choking. Work P0 → P1 → P2 → P3. Don't skip ahead. Document as you go.
