# FAITHH Project Structure (Updated)

**Last updated:** $(date +%Y-%m-%d)

## 📁 Root Directory (Clean)

### **Active Code** (Keep in root):
- `faithh_professional_backend.py` - Main backend (running on port 5557)
- `faithh_pet_v3.html` - UI v3 (stable, production)
- `faithh_ui_v4.html` - UI v4 (in development)
- `main.py` - Application entry point

### **Configuration** (Keep in root):
- `.env` - Environment variables (API keys, ports)
- `.gitignore` - Git ignore rules
- `config.yaml` - Application configuration
- `docker-compose.yml` - Docker setup
- `requirements.txt` - Python dependencies
- `keyring.json` - Security keyring

### **Essential Documentation** (Keep in root):
- `README.md` - Project overview
- `START_HERE.md` - Quick start guide
- `MASTER_INTEGRATION_DOCUMENT.md` - Main integration reference
- `MASTER_CONTEXT.md` - Project context
- `QUICK_START_GUIDE.md` - Quickstart instructions
- `PROJECT_STRUCTURE.md` - This file
- `CLEANUP_PLAN.md` - Cleanup documentation
- `ROOT_FILES_ANALYSIS.md` - File analysis

**Total in root: ~19 essential files** ✨

---

## 📂 Directory Structure

### **backend/** - Backend Modules
- Core backend implementations
- API modules (rag_api.py, rag_processor.py)
- Security (security_manager.py)
- Tool execution (tool_executor.py, tool_registry.py)
- Adapters and unified APIs

### **frontend/** - Frontend Files
- UI components (future organization)
- Client-side JavaScript
- CSS and assets

### **docs/** - All Documentation
- **guides/** - How-to guides and tutorials
- **reference/** - Quick references and API docs
- **session-reports/** - Session summaries and status updates
- **specifications/** - Design specs and UI/backend specifications
- **archive/** - Old/deprecated documentation

### **scripts/** - Automation & Utilities
- Cleanup scripts (cleanup_and_organize.sh, cleanup_phase2.sh)
- Service management (start_services.sh)
- Health checks (system_health_check.py, check_faithh_health.sh)
- Utility scripts (conversation_parsers.py, pulse_monitor.py)
- RAG tools (rag_cli.py, setup_rag.py, index_documents_chromadb.py)
- Parity tracking scripts

### **tests/** - Test Files
- Backend tests (test_backend.py)
- End-to-end tests (test_e2e.py)
- Integration tests (test_gemini.py, test_rag.py)
- Tool tests (test_tool_executor.py)

### **legacy/** - Deprecated Code
- Old UI implementations (chat_ui.py, search_ui.py)
- Superseded modules

### **models/** - AI Models (~33GB)
- Model files
- Model configurations

### **data/** - Application Data
- Databases (chroma.sqlite3)
- Caches and temporary files
- Upload storage

### **logs/** - Log Files
- Application logs (backend.log, api.log, server.log)
- Debug logs
- Error logs

### **parity/** - Parity Tracking System
- Changelogs and version tracking
- Feature parity documentation

### **cache/** - Temporary Cache
- Runtime cache files

### **backups/** - Timestamped Backups
- Cleanup backups (cleanup_YYYYMMDD_HHMMSS/)
- Archive of old versions

### **venv/** - Python Virtual Environment (~7.8GB)
- Python packages
- Dependencies

---

## 🎯 File Count Summary

- **Root:** ~19 essential files
- **Backend:** ~15 modules
- **Scripts:** ~25 utilities
- **Docs:** ~50 markdown files
- **Tests:** ~5 test files
- **Total organized:** Clean, maintainable structure

---

## 🚀 Quick Commands

### Start Backend:
```bash
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend.py
```

### Run Tests:
```bash
cd ~/ai-stack/tests
python test_backend.py
```

### Open UI:
```bash
cd ~/ai-stack
python -m http.server 8000
# Then open: http://localhost:8000/faithh_pet_v3.html
```

---

**Project is now clean, organized, and maintainable!** ✨
