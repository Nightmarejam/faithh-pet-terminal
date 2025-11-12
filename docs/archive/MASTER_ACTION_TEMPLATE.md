# MASTER ACTION DOCUMENT - [PROJECT NAME]
**Last Updated**: [DATE] | **Session**: [#] | **AI Used**: [Claude/Gemini/etc]

---

## 🎯 PROJECT OVERVIEW

**What This Project Does**:
[1-2 sentence description of the project's purpose]

**Current Status**: [Active Development / Testing / Production]

**Key Technologies**:
- [List main tech stack]
- [Framework/Libraries]
- [Tools being used]

---

## 📍 WHERE WE ARE NOW

### ✅ What's Working
- [Feature 1]: Fully implemented and tested
- [Feature 2]: Working with known limitations
- [Service/Component]: Running on [port/location]

### ⚠️ Known Issues
1. **[Issue Name]**
   - **Problem**: [Description]
   - **Impact**: [How it affects the system]
   - **Workaround**: [Temporary fix if any]

### 🚧 In Progress
- [ ] [Task being worked on]
- [ ] [Partially completed feature]

---

## 📂 PROJECT STRUCTURE

```
project-root/
├── src/
│   ├── core/              # [Purpose: Main business logic]
│   │   ├── file.py       # [What it does]
│   │   └── another.py    # [What it does]
│   ├── api/              # [Purpose: API endpoints]
│   └── ui/               # [Purpose: User interface]
├── config/
│   ├── settings.yaml     # [Main configuration]
│   └── .env             # [Environment variables - REQUIRED]
├── data/                # [Data storage location]
├── scripts/             # [Utility scripts]
│   ├── start.sh        # [How to start: ./start.sh]
│   └── setup.sh        # [Initial setup script]
└── docs/               # [Additional documentation]
```

### Key Files to Know

| File | Purpose | Critical? | Last Modified |
|------|---------|-----------|---------------|
| `file1.py` | Main entry point | ⚠️ YES | [Date] |
| `config.yaml` | System config | ⚠️ YES | [Date] |
| `helper.py` | Utility functions | No | [Date] |

---

## 🛠️ DESKTOP COMMANDER INSTRUCTIONS

### Reading Code Structure

```bash
# View project structure
Desktop Commander: start_process
Command: "cd /path/to/project && find . -type f -name '*.py' | head -20"

# Read specific file
Desktop Commander: read_file
Path: "/path/to/project/src/main.py"

# Search for specific code
Desktop Commander: start_search
Path: "/path/to/project"
Pattern: "def function_name"
SearchType: "content"
```

### File Operations

```bash
# Create new file
Desktop Commander: write_file
Path: "/path/to/project/new_file.py"
Content: [code content]

# Update existing file
Desktop Commander: start_process
Command: "cd /path/to/project && sed -i 's/old_text/new_text/' file.py"

# Backup before changes
Desktop Commander: start_process
Command: "cp /path/to/file.py /path/to/file.py.backup"
```

### Running Commands

```bash
# Activate virtual environment and run
Desktop Commander: start_process
Command: "cd /path/to/project && source venv/bin/activate && python main.py"
Timeout: 10000

# Check service status
Desktop Commander: start_process
Command: "curl -s http://localhost:PORT/health | jq"
Timeout: 5000
```

---

## 🎬 IMMEDIATE NEXT ACTIONS

### Priority 1: [High Priority Task]
**Goal**: [What needs to be accomplished]

**Steps**:
1. [ ] Read current implementation:
   ```bash
   Desktop Commander: read_file
   Path: "/path/to/current/file.py"
   ```

2. [ ] Identify the section to modify:
   - Look for: `[specific code pattern]`
   - Located at: Line [number range]

3. [ ] Make the change:
   ```bash
   Desktop Commander: write_file
   Path: "/path/to/file.py"
   Content: [new code]
   ```

4. [ ] Test the change:
   ```bash
   Desktop Commander: start_process
   Command: "cd /path && python -m pytest tests/test_feature.py"
   ```

5. [ ] Verify result:
   - Expected output: [description]
   - Check at: [URL or location]

**Tool Commands Needed**:
- `read_file` - [Specific files]
- `write_file` - [Files to create/modify]
- `start_process` - [Commands to run]

---

### Priority 2: [Next Important Task]
[Same structure as Priority 1]

---

## 🔄 COMMON WORKFLOWS

### Starting the System
```bash
# 1. Navigate to project
cd ~/path/to/project

# 2. Activate environment
source venv/bin/activate

# 3. Start services (in order)
docker-compose up -d          # If using Docker
python backend.py &           # Start backend
python -m http.server 8080    # Start frontend

# 4. Verify services
curl http://localhost:8080/health
```

### Making Code Changes
```bash
# 1. Backup current version
cp file.py file.py.backup

# 2. Make changes (use Desktop Commander)

# 3. Test changes
python -m pytest tests/

# 4. If good, commit
git add file.py
git commit -m "Description of change"
git push
```

### Debugging
```bash
# Check logs
tail -f logs/app.log

# Check service status
ps aux | grep python

# Test API endpoint
curl -X POST http://localhost:PORT/endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

---

## 📋 DECISION LOG

### [Date] - Decision: [What was decided]
**Context**: [Why this decision was made]
**Options Considered**:
1. [Option 1] - Pros/Cons
2. [Option 2] - Pros/Cons

**Chosen**: [Selected option]
**Rationale**: [Why this was best]
**Impact**: [What changed as a result]

---

## 🧪 TESTING CHECKLIST

- [ ] Unit tests pass: `python -m pytest tests/`
- [ ] Integration works: [Specific test scenario]
- [ ] UI loads correctly: http://localhost:PORT
- [ ] API responds: `curl http://localhost:PORT/health`
- [ ] Data persists: [How to verify]
- [ ] Error handling works: [Test error case]

---

## 🚨 CRITICAL NOTES FOR AI

### Before Making Changes
1. **ALWAYS read the current file first** using Desktop Commander's `read_file`
2. **Verify the project structure** with `start_process` and `find` commands
3. **Check what's running** with `ps aux | grep [process]`
4. **Backup critical files** before modifications

### Desktop Commander Patterns

**Reading Code**:
```
Tool: read_file
Path: [absolute path]
Purpose: [Why reading this]
```

**Writing Code**:
```
Tool: write_file
Path: [absolute path]
Content: [complete file content]
Purpose: [What this achieves]
```

**Running Commands**:
```
Tool: start_process
Command: "[full command with cd if needed]"
Timeout: [milliseconds]
Purpose: [What this does]
```

### When Stuck
1. Read MASTER_ACTION.md completely
2. Check "Where We Are Now" section
3. Look at "Immediate Next Actions"
4. Follow the Desktop Commander instructions exactly
5. Verify each step before proceeding

---

## 🔗 RELATED DOCUMENTS

- `README.md` - General project information
- `ARCHITECTURE.md` - System design and architecture
- `API_DOCS.md` - API endpoint documentation
- `SETUP.md` - Initial setup instructions

---

## 📝 SESSION NOTES

### Session [#] - [Date]
**AI**: [Which AI used]
**Focus**: [What was worked on]
**Completed**:
- [Task 1]
- [Task 2]

**Issues Encountered**:
- [Problem and solution]

**Next Session Should**:
- [Continue with X]
- [Address Y]

---

## 🎯 ULTIMATE GOALS

### Short Term (This Week)
- [ ] [Goal 1]
- [ ] [Goal 2]

### Medium Term (This Month)
- [ ] [Milestone 1]
- [ ] [Milestone 2]

### Long Term (This Quarter)
- [ ] [Major feature]
- [ ] [System improvement]

---

## 💬 HOW TO USE THIS DOCUMENT

### For Human (You)
1. Update "Last Updated" and "Session" at the top each time
2. Check off completed items in "Immediate Next Actions"
3. Add new decisions to "Decision Log"
4. Update "Session Notes" after each work session

### For AI (Claude/Gemini/etc)
1. **Start by reading this entire document**
2. Focus on "Where We Are Now" section first
3. Check "Immediate Next Actions" for priority tasks
4. Follow "Desktop Commander Instructions" exactly
5. Use "Common Workflows" for standard operations
6. Reference "Critical Notes for AI" before any file operations
7. Update "Session Notes" when making progress

### Handoff Between AIs
**Previous AI should**:
- Update all completion status
- Document any issues encountered
- Clearly state what's ready for next steps

**New AI should**:
- Read this document completely first
- Verify current state before proceeding
- Confirm understanding of next actions
- Ask clarifying questions if anything is unclear

---

## ⚡ QUICK START FOR NEW AI SESSION

```bash
# 1. Read this document completely
# 2. Verify project location and structure
Desktop Commander: start_process
Command: "cd ~/project && ls -la"

# 3. Check what's currently running
Desktop Commander: start_process
Command: "ps aux | grep -E '(python|node|docker)'"

# 4. Review current code state
Desktop Commander: read_file
Path: "/path/to/main/file.py"

# 5. Proceed with "Immediate Next Actions"
```

---

**Remember**: This document is the SINGLE SOURCE OF TRUTH for project continuity. Keep it updated!