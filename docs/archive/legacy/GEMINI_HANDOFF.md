# FAITHH Development - Gemini Handoff Prompt Template

Use this template when switching to Gemini for specific coding tasks.

---

## 📋 CONTEXT PRIMER FOR GEMINI

**Copy and paste this section when starting a new conversation with Gemini/FAITHH:**

```
Hi FAITHH! I'm working on the FAITHH PET Terminal project. Here's the quick context:

PROJECT: Personal AI assistant inspired by Megaman Battle Network
TECH STACK: 
- Frontend: HTML/CSS/JS (~/ai-stack/faithh_pet_v3.html)
- Backend: Flask Python API (~/ai-stack/faithh_api.py, port 5555)
- AI: Google Gemini 2.0 Flash + Local Ollama (Docker)
- Database: ChromaDB (RAG system with 4 months of conversations)
- Version Control: Git (commit regularly!)

CURRENT FEATURES:
✅ Chat interface with Gemini/Ollama
✅ Service status monitoring
✅ Battle chip system with execute/remove functionality
✅ PULSE watchdog system with hardware metrics
✅ Agentic workflow support (chips as agent tools)
⏳ RAG integration (UI ready, backend needed)
⏳ Chip execution backend (UI ready, backend needed)
⏳ Hardware metrics collection (UI ready, backend needed)

ENVIRONMENT:
- WSL2 Ubuntu 24.04.3
- Python 3.12 (venv: ~/ai-stack/venv)
- Gemini API Key: Configured in $GEMINI_API_KEY
- Services managed by start_faithh_docker.sh
- Hardware: Ryzen 9 3900X, 64GB RAM, RTX 3090 + GTX 1080 Ti

IMPORTANT REMINDERS:
- Keep token limits in mind - break large tasks into chunks
- Use code formatters: Black (Python), Prettier (JavaScript)
- Sanitize ALL user inputs for security
- Include comprehensive error handling
- Write unit tests for new features

For full context, see: ~/ai-stack/FAITHH_CONTEXT.md
```

---

## 🎯 TASK-SPECIFIC PROMPTS

### For Backend API Work

```
TASK: [Describe specific task]

FILE: ~/ai-stack/faithh_api.py
CURRENT STATE: [Describe what exists]
GOAL: [What you want to achieve]

REQUIREMENTS:
- [Specific requirement 1]
- [Specific requirement 2]

EXAMPLE:
[If applicable, show example input/output]

Can you help implement this?
```

### For Frontend UI Work

```
TASK: [Describe specific task]

FILE: ~/ai-stack/faithh_pet_v2.html (or v3.0)
SECTION: [Which part of the UI]
GOAL: [What you want to achieve]

DESIGN NOTES:
- Color scheme: Primary (#3B5A9D), Secondary (#E8A87C)
- Terminal/retro aesthetic
- Should match existing style

Can you help add this feature?
```

### For Battle Chip System

```
TASK: Implement battle chip [chip name]

CHIP DETAILS:
- Name: [chip name]
- Icon: [emoji or description]
- Code: [A-Z]
- Function: [What it does]
- Input: [What parameters it needs]
- Output: [What it returns]

INTEGRATION:
- Should work with chip slot system
- Needs to call backend API endpoint
- Should provide visual feedback

Can you help create this chip?
```

### For RAG Integration

```
TASK: Connect RAG system to [specific feature]

CONTEXT:
- RAG Database: ChromaDB
- Content: 4 months of AI conversations
- Location: [specify if known]

GOAL: [What you want to query/retrieve]

ENDPOINT NEEDED:
- POST /api/rag/query
- Input: {"query": "search term"}
- Output: {"results": [...]}

Can you help implement this?
```

---

## 🔄 ITERATING WITH GEMINI

### After Getting Code

```
Thanks! I tested this and [describe what happened].

[If it works]:
Great! Can you also add [next feature]?

[If there's an issue]:
I'm getting this error: [paste error]
The code is in [file:line]. Can you help fix it?

[If you need explanation]:
This works, but can you explain how [specific part] works?
```

### For Code Review

```
Can you review this code for:
- [ ] Bugs or errors
- [ ] Performance issues
- [ ] Best practices
- [ ] Security concerns

[paste code here]
```

---

## 🐛 DEBUGGING WITH GEMINI

### For Errors

```
I'm getting this error:

ERROR MESSAGE:
[paste full error]

FILE: [file path]
FUNCTION: [function name if known]

WHAT I WAS DOING:
[Steps to reproduce]

EXPECTED:
[What should happen]

ACTUAL:
[What actually happened]

Can you help diagnose and fix this?
```

### For Unexpected Behavior

```
Something isn't working right:

FEATURE: [what feature]
EXPECTED BEHAVIOR: [what should happen]
ACTUAL BEHAVIOR: [what's happening instead]

RELEVANT CODE:
[paste relevant code section]

Any ideas what might be wrong?
```

---

## 💡 BEST PRACTICES FOR GEMINI CONVERSATIONS

### DO:
✅ Be specific about file names and locations
✅ Describe what you've already tried
✅ Provide error messages in full
✅ Ask for explanations when needed
✅ Test code before moving to next task

### DON'T:
❌ Assume Gemini remembers previous conversations (it doesn't)
❌ Give vague descriptions like "make it better"
❌ Skip testing between iterations
❌ Forget to mention which file you're working on

---

## 📝 EXAMPLE COMPLETE HANDOFF

```
Hi FAITHH! Working on the FAITHH PET Terminal.

CONTEXT:
- Backend API running on port 5555
- Using Gemini 2.0 Flash for AI responses
- File: ~/ai-stack/faithh_api.py
- Full context: ~/ai-stack/FAITHH_CONTEXT.md

TASK: Add RAG query endpoint

REQUIREMENTS:
1. Endpoint: POST /api/rag/query
2. Input: {"query": "search term", "limit": 5}
3. Should search ChromaDB vector store
4. Return: {"results": [{"text": "...", "score": 0.95}]}
5. Include error handling

CURRENT STATE:
- ChromaDB not yet initialized in faithh_api.py
- Need to add chromadb import
- Need to set up collection on startup

Can you help me implement this endpoint with proper error handling?
```

---

## 🎓 LEARNING FROM GEMINI

When Gemini provides code, ask:

```
Thanks for the code! A few questions:

1. Why did you use [specific approach] instead of [alternative]?
2. What does [specific line/function] do?
3. Are there any edge cases I should watch out for?
4. How can I test this properly?
```

---

## 🔄 SWITCHING BACK TO CLAUDE

When you need Claude again for:
- Major architectural decisions
- Complex UI/UX design
- System-wide refactoring
- Documentation

Come back with:
```
Hey Claude! I've been working with Gemini on [task]. 
Here's what we built: [description]
Now I need help with [bigger picture item]
```

---

Save this file as: `~/ai-stack/GEMINI_HANDOFF.md`
Reference it anytime you switch to working with Gemini!