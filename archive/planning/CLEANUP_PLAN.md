# 🧹 FAITHH Project - Cleanup & Organization Plan

**Generated:** $(date +%Y-%m-%d)
**Status:** Ready to execute

---

## 📊 Current Analysis

### Directory Sizes
- **ai-stack**: ~41GB total
  - models/: 33GB (AI models)
  - venv/: 7.8GB (Python virtual environment)
  - faithh_rag/: 239MB (RAG database)
  - docs/: 384KB
  - other: ~500MB

- **ComfyUI**: 55GB (image generation + models)
- **stable-diffusion-webui**: 310MB (alternative image gen)

### Files to Organize
- **49 markdown files** in root (→ docs/ subdirectories)
- **28 Python scripts** in root (→ scripts/ or backend/)
- **2 HTML files** in root (→ frontend/ or keep in root for v3)
- **55 Zone.Identifier** files (→ delete, Windows metadata)
- **3 backup copies** of backend (→ archive)
- **5 log files** in WSL home (→ archive)

### AI Services Status
- ❌ FAITHH Backend (port 5557) - **NOT RUNNING**
- ❌ Ollama (port 11434) - **NOT RUNNING**
- ❌ ComfyUI - **NOT RUNNING**
- ❌ Stable Diffusion WebUI - **NOT RUNNING**

---

## 🎯 Cleanup Actions

### 1. Remove Redundant Files ✨
**Action:** Delete Windows Zone.Identifier files (55 files)
**Reason:** These are Windows metadata files not needed in WSL
**Impact:** No functional change, ~220KB freed

### 2. Organize Documentation 📚
**Action:** Move 49 markdown files to appropriate docs/ subdirectories

**New Structure:**
```
docs/
├── guides/               # How-to guides and tutorials
│   ├── WORKFLOW_GUIDE.md
│   ├── IMAGE_GENERATION_SETUP.md
│   ├── SESSION_STARTUP_PROTOCOL.md
│   └── ... (12 files)
│
├── reference/           # Quick references and API docs
│   ├── QUICK_REFERENCE_CARD.md
│   ├── COMPLETE_PACKAGE_INDEX.md
│   ├── UI_COMPONENTS_LIBRARY.md
│   └── ... (7 files)
│
├── session-reports/     # Session summaries and status
│   ├── CURRENT_STATUS_SUMMARY.md
│   ├── WEEK1_COMPLETION_REPORT.md
│   ├── SESSION_CONTINUATION_PLAN.md
│   └── ... (12 files)
│
└── specifications/      # Design specs and architecture
    ├── FAITHH_V4_UI_SPECIFICATION.md
    ├── FAITHH_V4_BACKEND_API.md
    ├── UI_VISUAL_LAYOUT_GUIDE.md
    └── ... (14 files)
```

**Keep in Root:**
- START_HERE.md (quick access)
- README.md (project overview)
- MASTER_INTEGRATION_DOCUMENT.md (main reference)
- MASTER_CONTEXT.md (context)
- ACTIVE_BACKEND_INFO.md (status)

### 3. Organize Python Scripts 🐍
**Action:** Move scripts to appropriate locations

**Scripts → scripts/:**
- analyze_dependencies.py
- system_health_check.py
- fix_chromadb_embeddings.py
- inspect_chromadb.py
- test_env_loading.py
- check_faithh_health.sh (from home dir)

**Backend scripts → backend/:**
- faithh_backend_adapter.py
- faithh_enhanced_backend.py
- faithh_unified_api.py
- faithh_backend_v4_template.py

**Keep in Root:**
- faithh_professional_backend.py (main backend - active)
- main.py (entry point)

### 4. Archive Backup Copies 🗄️
**Action:** Move to backups/ directory
- faithh_professional_backend.py.original
- faithh_professional_backend.py.prefixbackup

### 5. Clean WSL Home Directory 🏠
**Action:** Archive log files from ~/
- pip_version.log
- pip_which.log
- python_version.log
- python_which.log
- wsl_status.log

---

## 🚀 Execution Steps

### Option 1: Automatic (Recommended)
Run the cleanup script:
```bash
cd ~/ai-stack
./scripts/cleanup_and_organize.sh
```

This will:
1. Create a timestamped backup
2. Organize all files automatically
3. Generate PROJECT_STRUCTURE.md
4. Show summary of changes

### Option 2: Manual Review
Review proposed changes first:
```bash
cd ~/ai-stack
cat scripts/cleanup_and_organize.sh  # Review what it does
```

Then execute with confirmation at each step.

---

## 📋 Post-Cleanup Checklist

After running cleanup:

- [ ] **Verify structure**: Check that files moved correctly
  ```bash
  ls -la docs/guides/
  ls -la docs/reference/
  ls -la backend/
  ls -la scripts/
  ```

- [ ] **Start backend**: Ensure backend still works
  ```bash
  cd ~/ai-stack
  python faithh_professional_backend.py
  ```

- [ ] **Test endpoints**: Verify API functionality
  ```bash
  curl http://localhost:5557/api/status
  curl http://localhost:5557/health
  ```

- [ ] **Run tests**: Ensure nothing broke
  ```bash
  cd ~/ai-stack
  python -m pytest tests/ -v
  ```

- [ ] **Check UI**: Open and test v3 UI
  ```bash
  cd ~/ai-stack
  python -m http.server 8000
  # Open http://localhost:8000/faithh_pet_v3.html
  ```

- [ ] **Commit changes**: Save organized structure
  ```bash
  cd ~/ai-stack
  git add .
  git commit -m "chore: organize project structure and clean up redundant files"
  git status
  ```

---

## 🎯 Benefits After Cleanup

### Organization ✨
- Clear separation of concerns
- Easy to find documentation
- Logical file grouping
- Reduced root directory clutter

### Maintainability 🔧
- Easier navigation for new contributors
- Better file discovery
- Consistent structure
- Standard project layout

### Performance 📈
- Faster file searches
- Reduced directory scan times
- Cleaner git status
- Easier IDE indexing

---

## 🔄 Rollback Plan

If something goes wrong:

1. **Backups location**: `~/ai-stack/backups/cleanup_YYYYMMDD_HHMMSS/`
2. **Restore from backup**:
   ```bash
   cd ~/ai-stack/backups/
   ls -lt | head -5  # Find most recent backup
   # Manually restore needed files
   ```

3. **Git reset** (if committed):
   ```bash
   cd ~/ai-stack
   git log --oneline -5  # Find commit before cleanup
   git reset --hard <commit-hash>
   ```

---

## 💡 Recommendations

1. **Run cleanup now** - It's safe and creates backups
2. **Review PROJECT_STRUCTURE.md** after - Understand new layout
3. **Update bookmarks/shortcuts** - Docs moved to subdirectories
4. **Test thoroughly** - Verify all systems work
5. **Commit to git** - Save organized state

---

## ❓ FAQ

**Q: Will this break my existing setup?**
A: No. Only moves files, doesn't modify content. Active backend stays in root.

**Q: What if I need a file that was moved?**
A: Check PROJECT_STRUCTURE.md for new locations. Backups are in backups/ directory.

**Q: Can I customize what gets moved?**
A: Yes, edit scripts/cleanup_and_organize.sh before running.

**Q: Will this affect ComfyUI or Stable Diffusion?**
A: No, they're in separate directories and won't be touched.

---

**Ready to execute?** Run: `cd ~/ai-stack && ./scripts/cleanup_and_organize.sh`
