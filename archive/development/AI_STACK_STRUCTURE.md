# AI-Stack File Structure Map
**Purpose**: Clear guide for where files go - reduces "where does this belong?" confusion  
**Principle**: Keep it simple, don't overdesign  
**Created**: 2025-11-29

---

## 📁 Directory Structure Overview

```
~/ai-stack/
├── Core Files (root level)
│   ├── Configuration & State
│   ├── Documentation & Planning
│   └── Scripts & Utilities
│
├── testing/
│   └── Test artifacts & validation
│
└── [Future: conversations/, backups/, logs/]
```

---

## 🗂️ FILE PLACEMENT GUIDE

### ✅ ROOT LEVEL - Core Files

**Configuration & State** (JSON files that change):
```
faithh_memory.json          - FAITHH's persistent knowledge about you & projects
project_states.json         - Current phase/status of each project
decisions_log.json          - Record of decisions with rationale
scaffolding_state.json      - Structural state (where you are in projects)
```

**Documentation & Planning** (Markdown files, mostly static):
```
SONNET_HANDOFF_*.md         - Handoff documents between AI sessions
SESSION_SUMMARY_*.md        - What happened in a session
WEEKLY_PLAN_*.md            - Usage plans and priorities
OPEN_QUESTIONS.md           - Living doc of current challenges
CONVERSATIONAL_ENHANCEMENT_PLAN.md  - Architecture/design docs
TESTING_SYSTEM_VISION.md    - Future feature designs
AI_STACK_STRUCTURE.md       - This file!
resonance_journal.md        - Usage journal (testing feedback)
```

**Backend Code** (Python files):
```
faithh_professional_backend_fixed.py  - Main backend server
scaffolding_integration.py            - Scaffolding system functions
[Other .py files for specific features]
```

**Frontend Code** (HTML/JS files):
```
faithh_pet_v3.html          - Main UI interface
[Other .html files for UI variants]
```

**Scripts & Utilities** (Shell scripts):
```
quick_restart.sh            - Restart backend quickly
apply_scaffolding.sh        - Deploy scaffolding updates
[Other .sh files for automation]
```

---

### ✅ testing/ - Test Artifacts

**Purpose**: Keep test-related files separate from core system

```
testing/
├── TESTING_SYSTEM_VISION.md     - Design for future automation
├── test_session_template.md     - Template for manual testing
├── test_log.json                - (Future) Raw test Q&A
├── rated_tests.json             - (Future) Human + AI ratings
└── test_sessions/               - (Future) By-session archives
    ├── 2025-11-29.json
    └── 2025-11-30.json
```

**What goes here**:
- Test templates
- Test results
- Testing documentation
- Validation artifacts

---

## 🎯 DECISION TREE - "Where Does This File Go?"

### New File Type → Placement

**Is it configuration or state that changes?**
→ Root level, .json extension
→ Examples: `*_states.json`, `*_log.json`, `*_memory.json`

**Is it documentation or a plan?**
→ Root level, .md extension
→ Use CAPS for importance or dates in filename
→ Examples: `PLAN_*.md`, `SESSION_SUMMARY_*.md`

**Is it backend code?**
→ Root level, .py extension
→ Descriptive filename: `faithh_*_backend.py` or `*_integration.py`

**Is it frontend code?**
→ Root level, .html or .js extension
→ Version in filename: `faithh_pet_v3.html`

**Is it a utility script?**
→ Root level, .sh extension
→ Verb-based filename: `restart_*.sh`, `deploy_*.sh`

**Is it test-related?**
→ `testing/` directory
→ Prefix with `test_` or `TEST_`

**Is it a backup or archive?**
→ (Future) `backups/` or `archives/` directory
→ Date in filename: `YYYY-MM-DD_*`

**Is it a log file?**
→ (Future) `logs/` directory  
→ Currently: `backend.log` at root (acceptable for now)

**Not sure?**
→ Put it at root level with descriptive name
→ Can reorganize later if pattern emerges

---

## 📋 FILE NAMING CONVENTIONS

### Capitalization Signals Importance:

**ALL CAPS** = Critical reference docs, handoffs, plans
```
SONNET_HANDOFF_2025-11-28.md
SESSION_SUMMARY_2025-11-29.md
WEEKLY_PLAN_2025-11-29.md
OPEN_QUESTIONS.md
```

**lowercase** = Code, configs, utilities
```
faithh_professional_backend_fixed.py
faithh_memory.json
quick_restart.sh
```

**Sentence Case** = Less critical docs, notes
```
resonance_journal.md
```

### Date Formats:

**For dated files**: YYYY-MM-DD at end or in middle
```
SESSION_SUMMARY_2025-11-29.md
SONNET_HANDOFF_2025-11-28.md
```

**For timestamps in JSON**: ISO 8601
```json
"last_updated": "2025-11-29T02:00:00"
```

### Versioning:

**Backend/Frontend**: Version in filename
```
faithh_professional_backend_fixed.py  (implicit v3.3)
faithh_pet_v3.html
```

**Config files**: Version field inside JSON
```json
"version": "2.2"
```

---

## 🗺️ SYSTEM COMPONENT MAP

### How Files Connect:

```
Frontend (faithh_pet_v3.html)
    ↓ HTTP requests to
Backend (faithh_professional_backend_fixed.py)
    ↓ Reads from
Configuration Files:
├── faithh_memory.json (self-awareness, projects, user profile)
├── project_states.json (current phases, priorities, blockers)
├── decisions_log.json (why we made choices)
└── scaffolding_state.json (structural position tracking)
    ↓ Uses
ChromaDB (vector database)
├── Port: 8000
├── Collection: documents_768
└── 93,565 indexed documents
    ↓ Queries
LLM (Gemini or Ollama)
├── Gemini 2.0 Flash Exp (cloud, fast)
└── Ollama llama3.1-8b (local, private)
```

### Data Flow:

```
User Query (UI)
    → Backend receives query
    → Analyze intent (is_self_query, is_constella_query, etc.)
    → Build context:
        1. Self-awareness (from faithh_memory.json)
        2. Constella awareness (if constella query)
        3. Decisions (from decisions_log.json)
        4. Project state (from project_states.json)
        5. Scaffolding (from scaffolding_state.json)
        6. RAG (from ChromaDB) - unless skipped
    → Send to LLM with context
    → Return response to UI
    → Auto-index conversation (background thread)
```

---

## 🚫 COMMON MISTAKES TO AVOID

### ❌ Don't Do This:
- Create deeply nested directories (confusing, hard to find files)
- Mix test files with core files at root
- Use inconsistent naming (some dated, some not)
- Put everything in one giant file

### ✅ Do This Instead:
- Keep root relatively flat (easy to scan)
- Group related files by prefix (`faithh_*`, `test_*`)
- Use dates consistently in filenames
- Break large files into logical components

---

## 📝 WHEN TO CREATE NEW DIRECTORIES

**Only create new directories when**:
1. You have 5+ files of the same type (like testing/)
2. The files are clearly a separate concern (not core system)
3. You'll reference them as a group

**Don't create directories for**:
- 1-2 files
- Files that connect tightly to core system
- Premature organization

---

## 🎯 QUICK REFERENCE

**Adding a new feature?**
→ Code: root level `.py` file
→ State: root level `.json` file
→ Docs: root level `.md` file (CAPS if important)

**Creating a plan or handoff?**
→ Root level, CAPS filename with date

**Testing something?**
→ `testing/` directory

**Archiving old stuff?**
→ (Future) Create `archives/` when you have 10+ old files

**Not sure?**
→ Root level, descriptive name, move later if needed

---

## 💡 PHILOSOPHY

**"Simple beats perfect"**
- Flat structure > deep nesting
- Descriptive names > clever abbreviations  
- Easy to find > perfectly organized
- Reorganize when patterns emerge, not preemptively

**"Files should explain themselves"**
- Filename tells you what it is
- First few lines tell you why it exists
- Related files use consistent prefixes

**"Don't fight the mess, map it"**
- You have ADHD, organization is hard
- The map adapts to how you actually work
- This document evolves as usage patterns emerge

---

*Last updated: 2025-11-29*  
*Evolve this as needed - it's a map, not a law*
