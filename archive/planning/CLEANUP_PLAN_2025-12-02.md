# FAITHH Repository Cleanup Plan
**Created**: 2025-12-02  
**Purpose**: Organize the ai-stack folder for clarity, reduce noise for indexing, prepare for FAITHH handoff

---

## 📊 Current State Analysis

**Total items**: ~500+ files across the repository  
**Key observation**: Lots of session summaries, handoff docs, backup files, and legacy code accumulated over development

### What I Found

#### 🔴 DELETE - No longer needed
These files serve no purpose and add noise:

**Backup files in root** (we have git + backups folder):
- `faithh_professional_backend_fixed.py.backup.20251115_185026`
- `faithh_professional_backend_fixed.py.backup.20251115_185131`
- `faithh_professional_backend_fixed.py.bak_pre_scaffolding`
- `faithh_professional_backend_fixed.py.backup_pre_phase1`
- `faithh_professional_backend_fixed.py.backup_20251127_170901`
- `faithh_professional_backend_fixed.py.bak`
- `quick_restart.shZone.Identifier` (Windows zone identifier junk)
- `SYSTEM_AUDIT_FOR_OPUS.mdZone.Identifier` (Windows zone identifier junk)

**Duplicate/obsolete UI files**:
- `faithh_ui_v4.html` (duplicate of faithh_pet_v4.html?)
- `faithh_pet_v3.html` (superseded by v4)

**Old logs** (in logs folder - can clear periodically):
- `server_20251025_*.log` (old dated logs)

#### 🟡 ARCHIVE - Historical value, move out of main view
These have reference value but clutter the active workspace:

**Session summaries** (move to `archive/sessions/`):
- `SESSION_SUMMARY_2025-11-25.md`
- `SESSION_SUMMARY_2025-11-27.md`
- `SESSION_SUMMARY_2025-11-29.md`
- `SESSION_2025-11-26_AFTERNOON.md`
- `SESSION_2025-11-26_CONTEXT_INFRASTRUCTURE.md`
- `SESSION_COMPLETE.md`
- `SESSION_HANDOFF_2025-11-19.md`

**Handoff documents** (move to `archive/handoffs/`):
- `OPUS_HANDOFF_INSTRUCTIONS.md`
- `OPUS_HANDOFF_AUTOMATION.md`
- `OPUS_HANDOFF_AGENT_PERSONALITY_2025-11-27.md`
- `OPUS_HANDOFF_CONSTELLA_2025-11-25.md`
- `OPUS_TO_SONNET_HANDOFF_2025-11-26.md`
- `OPUS_REVIEW_LOG.md`
- `SONNET_HANDOFF_2025-11-28.md`
- `SONNET_HANDOFF_CONSTELLA_IMPLEMENTATION.md`
- `CLAUDE_CODE_HANDOFF.md`
- `HANDOFF_COMPLETION_SUMMARY.md`

**Phase/integration docs** (move to `archive/development/`):
- `PHASE1_READY.md`
- `PHASE1_INTEGRATION_COMPLETE.md`
- `PHASE1_INTEGRATION_GUIDE.md`
- `PHASE1_FIXES_NEEDED.md`
- `BACKEND_INTEGRATION_v3.2.md`
- `MASTER_INTEGRATION_DOCUMENT.md`

**Old planning docs** (move to `archive/planning/`):
- `WEEKLY_PLAN_2025-11-29.md`
- `JOURNAL_ENTRY_2025-11-29.md`
- `AUTO_JOURNAL_PLAN.md`
- `CONVERSATIONAL_ENHANCEMENT_PLAN.md`
- `DEVELOPMENT_ROADMAP.md`
- `LOCAL_AI_AGENT_ROADMAP.md`
- `CLEANUP_PLAN.md`
- `GIT_CLEANUP_AND_PREP.md`

#### 🟢 KEEP - Active/Essential files

**Core application**:
- `faithh_professional_backend_fixed.py` ← THE active backend
- `faithh_pet_v4.html` ← THE active UI
- `faithh_memory.json` ← Memory state
- `project_states.json` ← Project tracking
- `decisions_log.json` ← Decision history
- `scaffolding_state.json` ← Scaffolding state
- `config.yaml` ← Configuration
- `.env` ← Environment variables

**Documentation (current)**:
- `LIFE_MAP.md` ← Your compass
- `FAITHH_TESTING_GUIDE.md` ← This week's testing
- `SESSION_SUMMARY_2025-12-02.md` ← Today's work
- `README.md` ← Project overview
- `ARCHITECTURE.md` ← System architecture
- `START_HERE.md` ← Onboarding
- `QUICK_START_GUIDE.md` ← Quick reference
- `resonance_journal.md` ← Usage tracking

**Essential scripts**:
- `restart_backend.sh`
- `stop_backend.sh`
- `apply_scaffolding.sh`
- `requirements.txt`
- `docker-compose.yml`

**Data directories**:
- `AI_Chat_Exports/` ← Source conversations
- `chroma_db/` ← Vector database
- `faithh_rag/` ← RAG data
- `constella-framework/` ← Constella docs
- `images/` ← UI assets
- `models/` ← LLM models

---

## 🗂️ Proposed New Structure

```
ai-stack/
├── README.md                    # Project overview
├── START_HERE.md               # Onboarding guide
├── LIFE_MAP.md                 # Your compass (new)
├── QUICK_START_GUIDE.md        # Quick reference
│
├── 📁 core/                     # Active application files
│   ├── faithh_professional_backend_fixed.py
│   ├── faithh_pet_v4.html
│   ├── scaffolding_integration.py
│   └── phase1_conversation_memory.py
│
├── 📁 config/                   # Configuration files
│   ├── .env
│   ├── config.yaml
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── modelfiles/
│
├── 📁 state/                    # Runtime state files
│   ├── faithh_memory.json
│   ├── project_states.json
│   ├── decisions_log.json
│   └── scaffolding_state.json
│
├── 📁 docs/                     # Current documentation
│   ├── ARCHITECTURE.md
│   ├── FAITHH_TESTING_GUIDE.md
│   ├── resonance_journal.md
│   └── guides/                  # How-to guides
│
├── 📁 scripts/                  # Utility scripts (cleaned)
│   ├── restart_backend.sh
│   ├── stop_backend.sh
│   ├── indexing/
│   └── maintenance/
│
├── 📁 data/                     # Data sources
│   ├── AI_Chat_Exports/
│   ├── chroma_db/
│   ├── faithh_rag/
│   └── constella-framework/
│
├── 📁 assets/                   # Static assets
│   └── images/
│
├── 📁 archive/                  # Historical reference
│   ├── sessions/               # Session summaries
│   ├── handoffs/               # AI handoff docs
│   ├── development/            # Phase docs
│   ├── planning/               # Old plans
│   └── legacy/                 # Old code
│
├── 📁 backups/                  # Backups (keep as-is)
│
└── 📁 tests/                    # Test files
```

---

## 🎯 Cleanup Actions

### Phase 1: Quick Wins (Do Now)
1. Delete Zone.Identifier files
2. Delete root-level .py backup files
3. Move session summaries to archive
4. Move handoff docs to archive

### Phase 2: Reorganization (This Week)
1. Create new folder structure
2. Move files to appropriate locations
3. Update any hardcoded paths in scripts
4. Update .gitignore for new structure

### Phase 3: Data Hygiene (When Ready)
1. Deduplicate AI chat exports
2. Re-index cleaned documents
3. Verify ChromaDB has no duplicates

---

## ⚠️ Files That Need Investigation

**Multiple backend versions** - which is authoritative?
- `faithh_professional_backend_fixed.py` (root)
- `faithh_professional_backend.py` (root, older?)
- `faithh_backend_integrated.py` (root)
- `faithh_professional_backend_v3.1.py` (root)
- `backend/faithh_enhanced_backend.py`
- `backend/faithh_unified_api.py`
- `active/backend/faithh_professional_backend.py`

**Multiple UI versions**:
- `faithh_pet_v4.html` (root) ← NEW
- `faithh_pet_v3.html` (root)
- `faithh_ui_v4.html` (root) - different from pet_v4?
- `frontend/html/faithh_pet_v4_enhanced.html`
- `active/frontend/faithh_pet_v4.html`

**Recommendation**: Pick ONE authoritative location for backend and UI, archive the rest.

---

## 🔧 Immediate Action: Delete Junk Files

These can be deleted right now with no risk:

```bash
# Zone identifier files (Windows junk)
rm quick_restart.shZone.Identifier
rm SYSTEM_AUDIT_FOR_OPUS.mdZone.Identifier

# Root-level backup files (git has history)
rm faithh_professional_backend_fixed.py.backup.20251115_185026
rm faithh_professional_backend_fixed.py.backup.20251115_185131
rm faithh_professional_backend_fixed.py.bak_pre_scaffolding
rm faithh_professional_backend_fixed.py.backup_pre_phase1
rm faithh_professional_backend_fixed.py.backup_20251127_170901
rm faithh_professional_backend_fixed.py.bak
```

---

## 📋 Questions for You

1. **Backend**: Is `faithh_professional_backend_fixed.py` THE authoritative backend? Can we archive the others?

2. **UI**: The new `faithh_pet_v4.html` I created - should it replace everything, or do you want to keep v3 for reference?

3. **Chat exports**: The `AI_Chat_Exports` folder has lots of image files from ChatGPT. Do those need to be indexed, or just the conversation JSON?

4. **Constella**: The `constella-framework/` folder is its own git repo. Should it stay embedded here, or be a separate project?

5. **Archive policy**: Are you comfortable archiving old session/handoff docs, knowing git has the history?

---

*This cleanup will make the project much more navigable and reduce noise in RAG indexing.*
