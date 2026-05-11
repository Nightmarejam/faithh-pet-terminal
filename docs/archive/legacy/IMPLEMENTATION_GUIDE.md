# IMPLEMENTATION GUIDE: Master Action Document System

## 🎯 Purpose

This guide explains how to implement and use the MASTER_ACTION.md system for AI continuity across sessions, especially with Desktop Commander/MCP tools.

---

## 📥 SETUP (One-Time)

### Step 1: Create Your Master Document

```bash
# Copy the template to your project
cp MASTER_ACTION_TEMPLATE.md ~/ai-stack/MASTER_ACTION.md

# Or create it fresh with your project details
cd ~/ai-stack
nano MASTER_ACTION.md
```

### Step 2: Fill in Project-Specific Details

Edit the template and replace all `[placeholders]`:

```markdown
# MASTER ACTION DOCUMENT - FAITHH PET Terminal
**Last Updated**: 2025-11-08 | **Session**: 1 | **AI Used**: Claude Sonnet 4.5

## 🎯 PROJECT OVERVIEW
**What This Project Does**:
FAITHH PET is an AI assistant terminal with RAG (Retrieval-Augmented Generation) capabilities, 
combining ChromaDB with Gemini/Ollama for context-aware conversations.

**Current Status**: Active Development

**Key Technologies**:
- Python 3.10 (Flask, ChromaDB, Streamlit)
- Docker (ChromaDB server)
- WSL2 Ubuntu
- Gemini API (gemini-2.0-flash-exp)
- Desktop Commander (MCP tool integration)
```

### Step 3: Document Current State

Map your actual file structure:

```bash
# Generate your project tree
cd ~/ai-stack
tree -L 3 -I '__pycache__|*.pyc|venv' > project_structure.txt

# Paste into MASTER_ACTION.md under "PROJECT STRUCTURE" section
```

### Step 4: Add Absolute Paths

**Critical**: Use absolute paths for Desktop Commander:

```markdown
### Key Files to Know

| File | Purpose | Path |
|------|---------|------|
| `faithh_enhanced_backend.py` | Main API server | `/home/jonat/ai-stack/faithh_enhanced_backend.py` |
| `config.yaml` | System config | `/home/jonat/ai-stack/config.yaml` |
| `MASTER_CONTEXT.md` | Project documentation | `/home/jonat/ai-stack/MASTER_CONTEXT.md` |
```

---

## 🔄 DAILY WORKFLOW

### Starting a Session (AI Instructions)

**When starting ANY new chat with an AI**:

1. Upload `MASTER_ACTION.md` or paste its contents
2. Say: "Read MASTER_ACTION.md completely before proceeding"
3. AI should respond with:
   - Current project status summary
   - What was last worked on
   - What needs to happen next

### During a Session

**Human (You)**:
- Tell AI what you want to work on
- AI will reference MASTER_ACTION.md for context
- AI uses Desktop Commander instructions from the doc

**AI**:
- Reads current code state using instructions from MASTER_ACTION.md
- Follows the exact tool patterns specified
- Updates completion status as it works

### Ending a Session

**Before ending chat**:
1. AI should update MASTER_ACTION.md:
   - Mark completed tasks
   - Add session notes
   - Document any issues
   - List next steps clearly

2. Save the updated MASTER_ACTION.md:
```bash
# AI uses Desktop Commander to save
Tool: write_file
Path: "/home/jonat/ai-stack/MASTER_ACTION.md"
Content: [updated content]
```

---

## 🛠️ DESKTOP COMMANDER INTEGRATION

### Why This Works Well with Desktop Commander

Desktop Commander requires **explicit tool calls**. The MASTER_ACTION.md provides:
- ✅ Exact file paths (no guessing)
- ✅ Complete command syntax
- ✅ Tool usage patterns
- ✅ Expected outcomes

### Tool Call Templates in MASTER_ACTION.md

**Always format like this**:

```markdown
### Task: Update Backend API

**Step 1**: Read current implementation
```
Tool: read_file
Path: "/home/jonat/ai-stack/faithh_enhanced_backend.py"
Purpose: "Check current route definitions"
```

**Step 2**: Modify the file
```
Tool: write_file  
Path: "/home/jonat/ai-stack/faithh_enhanced_backend.py"
Content: [full updated file content here]
Purpose: "Add new /status endpoint"
```

**Step 3**: Test the change
```
Tool: start_process
Command: "cd /home/jonat/ai-stack && source venv/bin/activate && python faithh_enhanced_backend.py"
Timeout: 10000
Purpose: "Start updated backend to test"
```

**Step 4**: Verify it works
```
Tool: start_process
Command: "curl -s http://localhost:5557/status | jq"
Timeout: 5000
Purpose: "Test new endpoint"
```
```

### Key Patterns

**Reading Files**:
```markdown
Tool: read_file
Path: "[absolute path]"
Purpose: "[why you're reading this]"
```

**Writing Files**:
```markdown
Tool: write_file
Path: "[absolute path]"
Content: |
  [complete file content - indent properly]
Purpose: "[what this achieves]"
```

**Running Commands**:
```markdown
Tool: start_process
Command: "[full command including cd if needed]"
Timeout: [ms - usually 5000-10000]
Purpose: "[what this does]"
```

**Searching Code**:
```markdown
Tool: start_search
Path: "[directory to search]"
Pattern: "[what to find]"
SearchType: "content"  # or "files"
Purpose: "[what you're looking for]"
```

---

## 📝 EXAMPLE: Real FAITHH Session

### Starting a New Session

**You**: "Continue working on FAITHH. Here's MASTER_ACTION.md [paste or upload]"

**AI**: "I've read the MASTER_ACTION.md. Current status:
- ChromaDB running with 91,302 documents
- Backend API at port 5557
- Last session: Added tool execution system
- Next priority: Test RAG search functionality

Should I proceed with Priority 1: Testing RAG Search?"

### AI Following Instructions

**AI**: "I'll test the RAG search following the instructions in MASTER_ACTION.md"

```
Tool: start_process
Command: "cd /home/jonat/ai-stack && source venv/bin/activate && curl -X POST http://localhost:5557/api/rag_search -H 'Content-Type: application/json' -d '{\"query\": \"battle chips\", \"n_results\": 5}'"
Timeout: 10000
Purpose: "Test RAG search with example query"
```

**AI**: "RAG search returned 5 results. Now checking if results are relevant..."

```
Tool: read_file
Path: "/home/jonat/ai-stack/faithh_enhanced_backend.py"
Purpose: "Verify RAG search implementation matches expected behavior"
```

### AI Updating MASTER_ACTION.md

**At end of session**:

```
Tool: write_file
Path: "/home/jonat/ai-stack/MASTER_ACTION.md"
Content: |
  # MASTER ACTION DOCUMENT - FAITHH PET Terminal
  **Last Updated**: 2025-11-08 | **Session**: 2 | **AI Used**: Claude Sonnet 4.5
  
  ## WHERE WE ARE NOW
  
  ### ✅ What's Working
  - ChromaDB: 91,302 documents indexed
  - Backend API: Port 5557 (tested)
  - RAG Search: Working with good results ✅ NEW
  - Tool execution: Functional
  
  ### 🚧 In Progress
  - [ ] HTML UI needs backend connection
  - [ ] Audio workflow integration pending
  
  ## IMMEDIATE NEXT ACTIONS
  
  ### Priority 1: Connect HTML UI to Backend (NEXT SESSION)
  **Goal**: Update HTML to use unified backend
  
  [rest of document...]
  
  ## SESSION NOTES
  
  ### Session 2 - 2025-11-08
  **AI**: Claude Sonnet 4.5 with Desktop Commander
  **Focus**: RAG search testing
  **Completed**:
  - ✅ Tested RAG search endpoint
  - ✅ Verified ChromaDB connection
  - ✅ Confirmed results relevance
  
  **Next Session Should**:
  - Update HTML UI to connect to backend
  - Test end-to-end workflow
Purpose: "Update session progress and prepare for next session"
```

---

## 🎯 BEST PRACTICES

### For You (Human)

1. **Keep MASTER_ACTION.md Updated**
   - After every significant change
   - Before starting complex tasks
   - When switching between AIs

2. **Be Specific in Action Items**
   - Include exact file paths
   - List specific line numbers if known
   - Provide expected outcomes

3. **Document Decisions**
   - Why you chose approach A over B
   - What you tried that didn't work
   - Lessons learned

4. **Version Control**
   ```bash
   git add MASTER_ACTION.md
   git commit -m "Session 2: RAG testing completed"
   git push
   ```

### For AI

1. **Always Read MASTER_ACTION.md First**
   - Before suggesting anything
   - Before reading any code
   - Before making any changes

2. **Follow Tool Patterns Exactly**
   - Use absolute paths specified
   - Include timeout values
   - Add purpose statements

3. **Verify Before Proceeding**
   - Read current state before changing
   - Test after making changes
   - Confirm expected outcomes

4. **Update Documentation**
   - Mark completed tasks
   - Add session notes
   - Document new issues

---

## 🚀 ADVANCED PATTERNS

### Multi-Step Workflows

For complex tasks, break into detailed steps:

```markdown
### Priority 1: Implement New Feature

**Goal**: Add search history to FAITHH

**Dependencies**:
- ChromaDB must be running
- Backend API must be accessible

**Pre-checks**:
1. Verify ChromaDB status:
   ```
   Tool: start_process
   Command: "docker ps | grep chromadb"
   ```

**Implementation Steps**:

**Step 1**: Create database schema
```
Tool: read_file
Path: "/home/jonat/ai-stack/database/schema.sql"
Purpose: "Check existing schema"
```

**Step 2**: Add search history table
```
Tool: write_file
Path: "/home/jonat/ai-stack/database/schema.sql"
Content: |
  -- [existing content]
  
  CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  );
Purpose: "Add new table for search history"
```

**Step 3**: Update backend API
[Detailed steps...]

**Step 4**: Test implementation
[Test steps...]

**Rollback Plan** (if things break):
1. Restore backup: `cp file.py.backup file.py`
2. Restart services: `./restart.sh`
3. Verify old state works
```

### Error Handling

Include error recovery in MASTER_ACTION.md:

```markdown
### Common Issues

**Issue**: "ChromaDB connection timeout"
**Solution**:
```
Tool: start_process
Command: "docker restart chromadb && sleep 5"
Timeout: 10000
Purpose: "Restart ChromaDB service"
```

**Issue**: "Port already in use"
**Solution**:
```
Tool: start_process
Command: "lsof -ti:5557 | xargs kill -9"
Timeout: 5000
Purpose: "Kill process using port 5557"
```
```

### Context Preservation

For long-running features:

```markdown
### Feature: Audio Workflow Integration

**Overall Goal**: Integrate audio production docs into RAG

**Current Phase**: 2 of 4
**Estimated Completion**: 75%

**Completed Phases**:
- ✅ Phase 1: Document audio workflow
- ✅ Phase 2: Create embedding scripts

**Current Phase 2 Details**:
**Status**: Testing embeddings
**Last Action**: Created batch_embed.sh
**Next Action**: Load audio docs into ChromaDB
**Blockers**: None
**Files Modified**:
- `/home/jonat/ai-stack/Audio/batch_embed.sh`
- `/home/jonat/ai-stack/config.yaml` (added audio paths)

**Remaining Phases**:
- [ ] Phase 3: Test search across audio content
- [ ] Phase 4: Add audio-specific queries to UI
```

---

## 🎓 TRAINING AIS TO USE THIS SYSTEM

### Initial Prompt Template

When starting with a new AI:

```
I have a MASTER_ACTION.md document that contains complete context for my project. 
Here's what you need to know:

1. This document is the SINGLE SOURCE OF TRUTH
2. Read it completely before proceeding
3. Follow the "Desktop Commander Instructions" section exactly
4. Update the document as you complete tasks
5. Add session notes before we end

[Paste or upload MASTER_ACTION.md]

Please:
1. Summarize the current project state
2. List what was worked on last session
3. Confirm what the next priority tasks are
4. Ask any clarifying questions before starting

After you understand the context, I'll tell you what to work on.
```

### Mid-Session Reminders

If AI seems to forget context:

```
Please refer back to MASTER_ACTION.md, specifically:
- "Where We Are Now" section
- "Immediate Next Actions" 
- "Desktop Commander Instructions"

What does the document say about [specific thing]?
```

### Session End Checklist

Before ending a chat:

```
Before we finish this session, please:

1. Update MASTER_ACTION.md with:
   - Completed tasks (mark with ✅)
   - Any issues encountered
   - Session notes
   - Clear next steps

2. Save the updated MASTER_ACTION.md to the project directory

3. Summarize what was accomplished

4. Confirm what the next session should start with
```

---

## 💡 TIPS & TRICKS

### Quick Updates

Keep a "Quick Updates" section for minor changes:

```markdown
## 🔄 QUICK UPDATES

**2025-11-08 15:30** - Fixed RAG search bug (timeout increased to 10s)
**2025-11-08 14:20** - Updated Gemini API key in .env
**2025-11-08 12:00** - ChromaDB restart required after server update
```

### Code Snippets Library

Include frequently used code:

```markdown
## 📚 CODE SNIPPETS

### Start All Services
```bash
cd ~/ai-stack
source venv/bin/activate
docker-compose up -d
python faithh_enhanced_backend.py &
python -m http.server 8080 &
```

### Quick RAG Test
```python
from simple_rag import SimpleRAG
rag = SimpleRAG()
results = rag.search("test query")
print(len(results))
```
```

### External References

Link to other important docs:

```markdown
## 🔗 RELATED DOCUMENTS

- [MASTER_CONTEXT.md](./MASTER_CONTEXT.md) - Full system architecture
- [AUDIO_WORKFLOW.md](./Audio/WORKFLOW.md) - Audio production setup
- [API_DOCS.md](./docs/API_DOCS.md) - API endpoint reference
- [GitHub Repo](https://github.com/Nightmarejam/faithh-pet-terminal)
```

---

## ✅ SUCCESS CRITERIA

You'll know this system is working when:

1. **New AI sessions start smoothly**
   - AI immediately understands project context
   - No repeated explanations needed
   - AI knows where files are located

2. **Changes are tracked**
   - Session notes capture progress
   - Decisions are documented
   - Issues are recorded with solutions

3. **Continuity is maintained**
   - Next session picks up where last left off
   - No lost work or context
   - Clear path forward always visible

4. **Desktop Commander works reliably**
   - Tool calls succeed on first try
   - File paths are correct
   - Commands execute as expected

---

## 🎯 YOUR NEXT STEPS

1. **Copy template to your project**
   ```bash
   cp MASTER_ACTION_TEMPLATE.md ~/ai-stack/MASTER_ACTION.md
   ```

2. **Fill in FAITHH-specific details**
   - Project structure
   - Current services and ports
   - Immediate next actions

3. **Test with next AI session**
   - Upload MASTER_ACTION.md
   - See if AI understands context
   - Make adjustments as needed

4. **Refine over time**
   - Add patterns that work
   - Remove things that don't
   - Keep it current

---

**Remember**: This is a living document system. It gets better the more you use it!