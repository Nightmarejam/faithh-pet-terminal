# 📁 Root Directory Files Analysis

**Generated:** $(date +%Y-%m-%d)

This document analyzes all files in the project root and recommends which should stay vs. be moved.

---

## ✅ **KEEP IN ROOT (Essential)**

These files should remain in root for easy access and functionality:

### **Active Code:**
- `faithh_professional_backend.py` - **Main backend** (ACTIVE, running on port 5557)
- `faithh_pet_v3.html` - **UI v3** (stable, production)
- `faithh_ui_v4.html` - **UI v4** (in development)
- `main.py` - Entry point for application

### **Configuration:**
- `.env` - Environment variables (API keys, ports)
- `.gitignore` - Git ignore rules
- `config.yaml` - Application configuration
- `docker-compose.yml` - Docker configuration
- `requirements.txt` - Python dependencies
- `keyring.json` - Security keyring

### **Essential Documentation:**
- `README.md` - Project overview
- `START_HERE.md` - Quick start guide
- `MASTER_INTEGRATION_DOCUMENT.md` - Main integration reference
- `MASTER_CONTEXT.md` - Project context
- `QUICK_START_GUIDE.md` - Quick start (just created)
- `PROJECT_STRUCTURE.md` - Structure inventory (just created)
- `CLEANUP_PLAN.md` - Cleanup documentation (just created)

### **Process IDs:**
- `.backend.pid` - Backend process ID (auto-generated)
- `.server.pid` - Server process ID (auto-generated)

**Total to keep: 19 files**

---

## 📦 **MOVE TO APPROPRIATE DIRECTORIES**

### **1. Documentation → docs/session-reports/**
- `ACTIVE_BACKEND_INFO.md` - Backend status info
- `MASTER_ACTION_FAITHH.md` - Old action document (superseded)
- `MASTER_ACTION_FAITHH_UPDATED.md` - Updated action doc (superseded by MASTER_INTEGRATION_DOCUMENT)

### **2. Scripts → scripts/**
- `SCRIPTS_README.md` - Should be in scripts/ folder
- `SELF_DOCUMENTING_TEMPLATE.sh` - Template script
- `friday_validation.sh` - Validation script
- `thursday_first_parity.sh` - Parity script
- `wednesday_parity_setup.sh` - Parity script
- `update_parity_session_6.sh` - Parity update script

### **3. Test Files → tests/**
- `test_backend.py`
- `test_e2e.py`
- `test_gemini.py`
- `test_rag.py`
- `test_tool_executor.py`

### **4. Backend Modules → backend/**
- `rag_api.py` - RAG API module
- `rag_processor.py` - RAG processing
- `security_manager.py` - Security module
- `tool_executor.py` - Tool execution
- `tool_registry.py` - Tool registry (if exists)

### **5. Utility Scripts → scripts/**
- `conversation_parsers.py` - Parsing utility
- `index_documents_chromadb.py` - ChromaDB indexing
- `pulse_monitor.py` - Monitoring utility
- `rag_cli.py` - RAG CLI tool
- `search_ui.py` - Search UI (legacy)
- `setup_rag.py` - RAG setup script

### **6. Legacy UI → legacy/**
- `chat_ui.py` - Old chat UI (superseded by HTML UIs)

### **7. Data Files → data/**
- `chroma.sqlite3` - ChromaDB database file

### **8. Log Files → logs/**
- `api.log` - API logs
- `server.log` - Server logs

### **9. Temporary Files → archive/ or DELETE**
- `file_list_config.txt` - Discovery temp file
- `file_list_docs.txt` - Discovery temp file
- `file_list_html.txt` - Discovery temp file
- `file_list_python.txt` - Discovery temp file
- `discovery_quick_20251108_022414.txt` - Discovery temp file

**Total to organize: 35+ files**

---

## 📊 **Impact Analysis**

### **Current State:**
- Root directory: **50+ files** (cluttered)
- Hard to find active code
- Mix of temp, legacy, and active files

### **After Phase 2 Cleanup:**
- Root directory: **~19 essential files** (clean)
- Clear separation: active code, config, docs
- Easy navigation and maintenance

### **Benefits:**
- ✅ Easier to find active backend and UI files
- ✅ Clear separation of concerns
- ✅ Better git diffs (less noise)
- ✅ Faster IDE indexing
- ✅ Professional project structure

---

## 🎯 **Recommended Actions**

### **Phase 2 Cleanup Priority:**

1. **HIGH PRIORITY** (Do first):
   - Move test files to tests/
   - Move backend modules to backend/
   - Move scripts to scripts/
   - Move data/log files to proper folders

2. **MEDIUM PRIORITY**:
   - Archive old documentation
   - Move legacy UI to legacy/

3. **LOW PRIORITY** (Can delete):
   - Delete temp discovery files (file_list_*.txt)
   - Delete old temp files

---

## 🔍 **File-by-File Breakdown**

### **Core Files (KEEP IN ROOT):**

| File | Purpose | Status | Keep? |
|------|---------|--------|-------|
| `faithh_professional_backend.py` | Main backend | Active ✅ | ✅ YES |
| `faithh_pet_v3.html` | UI v3 | Stable ✅ | ✅ YES |
| `faithh_ui_v4.html` | UI v4 | In Progress ⏳ | ✅ YES |
| `main.py` | Entry point | Active ✅ | ✅ YES |
| `.env` | Config | Essential ✅ | ✅ YES |
| `config.yaml` | Config | Essential ✅ | ✅ YES |
| `requirements.txt` | Dependencies | Essential ✅ | ✅ YES |
| `README.md` | Documentation | Essential ✅ | ✅ YES |

### **Documentation (MOVE TO docs/):**

| File | Purpose | Destination |
|------|---------|------------|
| `ACTIVE_BACKEND_INFO.md` | Status info | docs/session-reports/ |
| `MASTER_ACTION_FAITHH.md` | Old action plan | docs/session-reports/ |
| `MASTER_ACTION_FAITHH_UPDATED.md` | Updated plan | docs/session-reports/ |

### **Scripts (MOVE TO scripts/):**

| File | Purpose | Destination |
|------|---------|------------|
| `friday_validation.sh` | Validation | scripts/ |
| `thursday_first_parity.sh` | Parity | scripts/ |
| `wednesday_parity_setup.sh` | Parity | scripts/ |
| `update_parity_session_6.sh` | Parity | scripts/ |
| `SELF_DOCUMENTING_TEMPLATE.sh` | Template | scripts/ |

### **Tests (MOVE TO tests/):**

| File | Purpose | Destination |
|------|---------|------------|
| `test_backend.py` | Backend test | tests/ |
| `test_e2e.py` | E2E test | tests/ |
| `test_gemini.py` | Gemini test | tests/ |
| `test_rag.py` | RAG test | tests/ |
| `test_tool_executor.py` | Tool test | tests/ |

### **Backend Modules (MOVE TO backend/):**

| File | Purpose | Destination |
|------|---------|------------|
| `rag_api.py` | RAG API | backend/ |
| `rag_processor.py` | RAG processor | backend/ |
| `security_manager.py` | Security | backend/ |
| `tool_executor.py` | Tool exec | backend/ |
| `tool_registry.py` | Tool registry | backend/ |

### **Utilities (MOVE TO scripts/):**

| File | Purpose | Destination |
|------|---------|------------|
| `conversation_parsers.py` | Parser | scripts/ |
| `index_documents_chromadb.py` | Indexer | scripts/ |
| `pulse_monitor.py` | Monitor | scripts/ |
| `rag_cli.py` | CLI tool | scripts/ |
| `search_ui.py` | Search UI | scripts/ or legacy/ |
| `setup_rag.py` | Setup | scripts/ |

### **Temporary Files (DELETE):**

| File | Purpose | Action |
|------|---------|--------|
| `file_list_config.txt` | Discovery temp | DELETE |
| `file_list_docs.txt` | Discovery temp | DELETE |
| `file_list_html.txt` | Discovery temp | DELETE |
| `file_list_python.txt` | Discovery temp | DELETE |
| `discovery_quick_*.txt` | Discovery temp | DELETE |

### **Data/Logs (MOVE):**

| File | Purpose | Destination |
|------|---------|------------|
| `chroma.sqlite3` | Database | data/ |
| `api.log` | Logs | logs/ |
| `server.log` | Logs | logs/ |

---

## 🚀 **Next Steps**

1. Review this analysis
2. Run phase 2 cleanup script: `./scripts/cleanup_phase2.sh`
3. Verify backend still works
4. Test UI functionality
5. Commit clean structure to git

---

## 📝 **Notes**

- All moves will create timestamped backups
- No files will be deleted without backup
- Backend will remain functional throughout
- Tests can be re-run after cleanup to verify

---

**This cleanup will reduce root directory from 50+ files to ~19 essential files!**
