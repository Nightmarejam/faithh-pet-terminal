# FAITHH Repository Structure (Final)
**Updated**: 2025-12-02

---

## 📁 Root Directory - Clean & Minimal

```
ai-stack/
├── 📄 README.md                 # Project overview
├── 📄 START_HERE.md             # Onboarding guide  
├── 📄 LIFE_MAP.md               # Your compass ⭐
├── 📄 QUICK_START_GUIDE.md      # Quick reference
├── 📄 ARCHITECTURE.md           # System architecture
├── 📄 FAITHH_TESTING_GUIDE.md   # Testing guide ⭐
├── 📄 REPOSITORY_STRUCTURE.md   # This file
├── 📄 context_quality_tests.md  # Test questions
├── 📄 resonance_journal.md      # Usage tracking
├── 📄 SESSION_SUMMARY_2025-12-02.md  # Today's work
│
├── 🐍 faithh_professional_backend_fixed.py  # THE backend ⭐
├── 🌐 faithh_pet_v4.html                    # THE UI ⭐
├── 🐍 scaffolding_integration.py            # Scaffolding system
├── 🐍 phase1_conversation_memory.py         # Conversation memory
│
├── 📋 faithh_memory.json        # Memory state
├── 📋 project_states.json       # Project tracking
├── 📋 decisions_log.json        # Decision history
├── 📋 scaffolding_state.json    # Scaffolding state
├── 📋 config.yaml               # Configuration
├── 📋 .env                      # Environment variables
│
├── 🔧 restart_backend.sh        # Start FAITHH ⭐
├── 🔧 stop_backend.sh           # Stop FAITHH
├── 🔧 requirements.txt          # Python dependencies
├── 🐳 docker-compose.yml        # Docker services
├── 📋 keyring.json              # Security keyring
```

**Total root files: ~25** (down from ~80)

---

## 📁 Data Directories

```
├── 📁 AI_Chat_Exports/          # Source conversations
│   ├── Claude_Chats/            # Claude exports (conversations.json)
│   ├── Chat_GPT_Chats/          # ChatGPT exports + images
│   └── Grok_Chats/              # Grok exports
│
├── 📁 chroma_db/                # Vector database (93K+ docs)
├── 📁 faithh_rag/               # RAG index data
├── 📁 constella-framework/      # Constella docs (own git repo)
├── 📁 images/                   # UI assets (faithh.png, pulse.png)
├── 📁 models/active/            # LLM GGUF models
```

---

## 📁 Support Directories

```
├── 📁 scripts/                  # All utility scripts
│   ├── restart scripts, tests, diagnostics
│   ├── indexing/                # Document indexing
│   ├── maintenance/             # System maintenance
│   ├── rag/                     # RAG utilities
│   └── memory/                  # Memory system
│
├── 📁 docs/                     # Additional documentation
│   ├── guides/                  # How-to guides
│   ├── reference/               # Reference docs
│   └── specifications/          # UI/API specs
│
├── 📁 backend/                  # Backend modules
├── 📁 tests/                    # Test files
├── 📁 testing/                  # Test templates
├── 📁 parity/                   # Parity file system
├── 📁 configs/modelfiles/       # Ollama modelfiles
├── 📁 logs/                     # Log files
├── 📁 backups/                  # Backup files
```

---

## 📁 Archive (Historical Reference)

```
├── 📁 archive/
│   ├── sessions/        # 7 session summaries
│   ├── handoffs/        # 10 AI handoff docs
│   ├── development/     # 20+ phase/integration docs
│   ├── planning/        # 10+ old planning docs
│   ├── legacy/          # Old code, scripts, one-time patches
│   └── ui_reference/    # faithh_pet_v3.html (chip aesthetic reference)
```

---

## 🎯 Daily Workflow Files

| Action | File | Command |
|--------|------|---------|
| **Start FAITHH** | `restart_backend.sh` | `./restart_backend.sh` |
| **Stop FAITHH** | `stop_backend.sh` | `./stop_backend.sh` |
| **Access UI** | `faithh_pet_v4.html` | http://localhost:5557 |
| **Check compass** | `LIFE_MAP.md` | Read when lost |
| **Test FAITHH** | `FAITHH_TESTING_GUIDE.md` | Daily testing ritual |
| **Log usage** | `resonance_journal.md` | Morning/evening check |

---

## 📊 Cleanup Summary

**Before**: ~80 files in root, mixed documentation, multiple backend versions  
**After**: ~25 files in root, clear purpose for each file

**Moved to archive**: 60+ files
- Session summaries
- Handoff documents  
- Development docs
- Planning docs
- Legacy code
- One-time patches
- Obsolete scripts

**v3 UI preserved** at `archive/ui_reference/faithh_pet_v3.html` for chip aesthetic reference

---

## 🔄 What to Index in FAITHH

**High priority** (current context):
1. `LIFE_MAP.md` — Your compass
2. `FAITHH_TESTING_GUIDE.md` — Testing framework
3. `SESSION_SUMMARY_2025-12-02.md` — Today's work

**Already indexed** (in ChromaDB):
- Constella framework docs
- Previous conversation exports
- Old session summaries (still searchable)

---

*Repository is now organized for human + AI collaboration.*
