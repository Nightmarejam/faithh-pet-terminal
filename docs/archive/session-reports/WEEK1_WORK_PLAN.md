# FAITHH WEEK 1 WORK PLAN
**Week of: [Fill in your start date]**  
**Goal: Clean, Organized, Stable System**

---

## 📋 WEEK 1 OVERVIEW

**Total Time Required:** ~12-15 hours  
**Daily Commitment:** 2-3 hours/day (flexible)  
**End Goal:** Clean file structure, working Gemini API, organized docs, ready for Phase 2

**What You'll Have By Friday:**
- ✅ All files organized and categorized
- ✅ Gemini API working (or confirmed Ollama as primary)
- ✅ Clean directory structure
- ✅ Updated documentation
- ✅ Baseline parity structure
- ✅ Ready to add features in Week 2

---

## 📅 DAILY BREAKDOWN

### MONDAY: Discovery & Assessment (2-3 hours)

**Morning/Evening Session:**

#### Task 1: Run Discovery Scripts (30 min)
```bash
cd /home/jonat/ai-stack

# Make scripts executable
chmod +x project_discovery.sh quick_scan.sh

# Run quick scan first
./quick_scan.sh

# Then run full discovery
./project_discovery.sh
```

**What to do:**
- Copy output from quick_scan to a text file
- Upload to Claude
- Review discovery_reports/ folder

#### Task 2: Initial Review with Claude (60 min)
**Action Items:**
- Share quick scan output with Claude
- Discuss what you see
- Ask questions about confusing files
- Get initial "keep/archive/delete" recommendations

#### Task 3: Gemini API Investigation (30-60 min)
**Check these locations:**
```bash
# Check .env
cat /home/jonat/ai-stack/.env | grep -i gemini

# Check config
cat /home/jonat/ai-stack/config.yaml | grep -i gemini

# Check backend
grep -n "gemini\|GEMINI" /home/jonat/ai-stack/*backend*.py
```

**Deliverable:** Know where your Gemini API key is (or isn't)

#### Task 4: Decision Making (30 min)
**Decide:**
- Which folders definitely belong in ai-stack?
- Which folders can be archived?
- Do you want Gemini or Ollama as primary?
- What's the timeline for this week realistically?

**Monday End State:** You know what you have and what needs to happen.

---

### TUESDAY: File Organization & Cleanup (2-3 hours)

**Focus: Physical file organization**

#### Task 1: Create New Directory Structure (30 min)
```bash
cd /home/jonat/ai-stack

# Create organized structure
mkdir -p {
    backend,
    frontend/html,
    frontend/streamlit,
    configs,
    docs/archive,
    docs/active,
    tools/scripts,
    tools/utils,
    data,
    logs,
    parity
}
```

**Verify:**
```bash
tree -L 2 -d
```

#### Task 2: Classify Files (60-90 min)
**Create three lists:**

1. **KEEP & MOVE** (Active files)
   - Current backend
   - Current HTML UI
   - Active configs
   - Essential docs

2. **ARCHIVE** (Old versions, experiments)
   - Old HTML versions
   - Test scripts
   - Backup files
   - Outdated docs

3. **DELETE** (Truly unnecessary)
   - Logs
   - Temp files
   - Duplicates
   - True junk

**Method:**
- Work with Claude using quick_scan output
- Go folder by folder
- When unsure, archive (don't delete)

#### Task 3: Move Files (60 min)
```bash
# Example moves (Claude will provide specific commands)
mv faithh_enhanced_backend.py backend/
mv 1762593516269_faithh_pet_v3.html frontend/html/
mv config.yaml configs/
# etc...
```

**Be careful:**
- Move, don't copy first
- Test after each major move
- Keep terminal with running services open

#### Task 4: Update Path References (30 min)
**Files that might need path updates:**
- Backend imports
- Config file paths
- HTML API endpoints (check if needed)
- Docker compose volumes

**Tuesday End State:** Clean directory structure, all files in logical places.

---

### WEDNESDAY: Configuration & Connections (2-3 hours)

**Focus: Get Gemini working or confirm Ollama setup**

#### Task 1: Fix Gemini API (60-90 min)

**If you WANT Gemini:**
```bash
# Create/update .env
cd /home/jonat/ai-stack
nano .env

# Add:
GEMINI_API_KEY=your_actual_key_here
OLLAMA_HOST=http://localhost:11434
```

**Update backend to prioritize Gemini:**
```python
# In backend/*.py
# Change model selection to try Gemini first
# Claude will provide specific code
```

**Test:**
```bash
# Restart backend
# Send message in UI
# Check which model responds
```

**If you PREFER Ollama:**
- Document that Ollama is primary
- Test model switching works
- Confirm Gemini is available as fallback

#### Task 2: Verify All Connections (45 min)
**Test checklist:**
- [ ] Backend starts without errors
- [ ] UI connects to backend
- [ ] Chat messages work
- [ ] Model selection works (if implemented)
- [ ] RAG search works
- [ ] ChromaDB accessible

**Create test log:**
```bash
# In project root
touch TEST_LOG.md
# Document what works and what doesn't
```

#### Task 3: Config Consolidation (30 min)
**Ensure you have ONE source of truth:**
- All API keys in .env
- All settings in config.yaml
- No hardcoded configs in code

**Create backup:**
```bash
cp .env .env.backup
cp configs/config.yaml configs/config.yaml.backup
```

**Wednesday End State:** API working, all connections verified, configs clean.

---

### THURSDAY: Documentation & Parity Setup (2-3 hours)

**Focus: Update docs and create parity foundation**

#### Task 1: Update Master Documentation (60 min)
**Edit these files:**

1. **MASTER_CONTEXT.md**
   - Add new directory structure
   - Update file locations
   - Document current state

2. **MASTER_ACTION.md** (or create MASTER_ACTION_WEEK1.md)
   - Document what you did Mon-Wed
   - Note any issues encountered
   - Record decisions made

3. **README.md** (project root)
   - Quick start guide
   - Directory structure
   - How to run system

#### Task 2: Create Parity Structure (45 min)
```bash
cd /home/jonat/ai-stack/parity

# Create parity folders
mkdir -p {
    backend,
    frontend,
    configs,
    changelog
}

# Create first parity file
touch backend/PARITY_backend.md
```

**In PARITY_backend.md:**
```markdown
# Backend Parity File
**Last Updated:** [Date]
**Version:** 1.0.0

## Current State
- File: backend/faithh_enhanced_backend.py
- Status: Stable
- Last Modified: [Date]

## Recent Changes
### [Date] - Initial Parity Setup
- Moved to organized structure
- Confirmed Gemini/Ollama connection
- No functional changes

## Known Issues
- [List any]

## Pending Changes
- [List any planned changes]
```

#### Task 3: Archive Old Docs (30 min)
```bash
# Move outdated docs to archive
mv old_docs/* docs/archive/
mv experiment_notes.md docs/archive/

# Keep a list of what was archived
ls docs/archive/ > docs/ARCHIVED_FILES.txt
```

**Thursday End State:** All documentation current, parity system initialized.

---

### FRIDAY: Testing, Validation & Planning (2-3 hours)

**Focus: Verify everything works and plan Week 2**

#### Task 1: Complete System Test (60 min)
**Full workflow test:**
```bash
# Terminal 1: Start backend
cd /home/jonat/ai-stack
python backend/faithh_enhanced_backend.py

# Terminal 2: Monitor logs
tail -f logs/backend.log

# Browser: Test UI
# 1. Open HTML UI
# 2. Send test messages
# 3. Try RAG search
# 4. Switch models (if implemented)
# 5. Test edge cases
```

**Document results in TEST_LOG.md**

#### Task 2: Performance Check (30 min)
**Monitor:**
- Response times
- Memory usage
- CPU usage
- Any errors or warnings

**Tools:**
```bash
# Check Docker containers
docker ps
docker stats

# Check system resources
htop

# Check disk usage
du -sh /home/jonat/ai-stack/*
```

#### Task 3: Create Week 2 Plan (45 min)
**With Claude, plan:**
- [ ] What UI features to add
- [ ] Which parity files to create
- [ ] Any remaining technical debt
- [ ] Time estimates for Week 2

#### Task 4: Celebrate & Document (30 min)
**Create WEEK1_COMPLETION.md:**
```markdown
# Week 1 Completion Report

## Accomplished
- [x] All files discovered and organized
- [x] Directory structure cleaned
- [x] Gemini API: [working/not working/using Ollama]
- [x] Documentation updated
- [x] Parity structure created
- [x] System tested and stable

## Challenges Encountered
- [List any issues]

## Solutions Applied
- [How you solved them]

## Ready for Week 2
- [What's next]

## Hours Spent
- Monday: X hours
- Tuesday: X hours
- Wednesday: X hours  
- Thursday: X hours
- Friday: X hours
- Total: X hours
```

**Friday End State:** Clean system, working API, ready to build features!

---

## 🎯 SUCCESS CRITERIA FOR WEEK 1

By end of week, you should be able to:

✅ **Navigate your project easily** - Know where everything is  
✅ **Explain your directory structure** - Each folder has a purpose  
✅ **Run your system confidently** - No mysterious errors  
✅ **Understand your configs** - Know what settings do what  
✅ **Find any file quickly** - Organized and logical  
✅ **Document a change** - Using parity files  
✅ **Tell someone how it works** - You understand the system  

---

## ⚠️ IF YOU GET STUCK

**Problem: Too many files, feeling overwhelmed**
- Solution: Work with Claude folder-by-folder
- Take breaks between folders
- Archive when unsure (don't delete)

**Problem: Scared to break something**
- Solution: Git commit before big moves
- Create backups before changes
- Test immediately after changes

**Problem: Not enough time this week**
- Solution: Adjust timeline
- Focus on Tasks 1-2 each day
- Extend to 10-day plan if needed

**Problem: Technical errors**
- Solution: Share error logs with Claude
- Don't try to fix everything at once
- Document issues in TEST_LOG.md

---

## 📊 TRACKING YOUR PROGRESS

**Daily Check-in Questions:**
1. What did I accomplish today?
2. What's blocking me?
3. What do I need help with?
4. Am I on track for Week 1 goals?

**End-of-day habit:**
```bash
# Update your action log
echo "## $(date +%Y-%m-%d)" >> MASTER_ACTION_WEEK1.md
echo "- [What you did today]" >> MASTER_ACTION_WEEK1.md
echo "- Time spent: X hours" >> MASTER_ACTION_WEEK1.md
echo "" >> MASTER_ACTION_WEEK1.md
```

---

## 🚀 WEEK 2 PREVIEW

**What's coming next week:**
- Add model selector to UI
- Add context visibility panel  
- Create basic process queue
- More parity files
- Maybe: First agent prototype

**But don't think about that yet!** Focus on Week 1. 

---

## 💡 FINAL TIPS

1. **Take breaks** - This is a marathon, not a sprint
2. **Ask Claude** - When you're unsure about a file, just ask
3. **Git commit often** - After each major change
4. **Document as you go** - Don't save all docs for Thursday
5. **Celebrate wins** - Moved 10 files? That's progress!
6. **Stay organized** - When you're tempted to create a temp file, put it in the right place from the start

---

**Ready to start? Run the quick_scan.sh script and share the results!**
