# FAITHH MacBook Pro Setup Plan
**Date**: 2025-12-03
**Machine**: MacBook Pro M1, 16GB RAM, macOS 26.1

---

## Current State

**Installed:**
- ✅ Python 3.13.6 (Homebrew)
- ✅ Homebrew
- ✅ Desktop Commander (Claude extension)
- ✅ Audio workflow scripts in ~/Audio-Scripts
- ✅ Constella framework in ~/Projects/constella-framework

**Not Installed:**
- ❌ Ollama (needed for local LLM)
- ❌ ChromaDB (optional for lightweight setup)
- ❌ FAITHH backend

---

## Setup Options

### Option A: Lightweight (Recommended for Start)
- Ollama with llama3.1-8b
- Simple Flask backend (no ChromaDB)
- Key documents embedded directly in prompts
- Fast, no dependencies on Windows machine

### Option B: Full Local
- Ollama with llama3.1-8b
- Local ChromaDB with subset of docs
- Full backend with integrations
- Independent but needs initial doc sync

### Option C: Remote Query
- No local LLM
- Query Windows FAITHH over network
- Dependent on Windows machine being on
- Simplest but least reliable for mobile use

---

## Recommended: Option A (Lightweight)

### Step 1: Install Ollama
```bash
brew install ollama
ollama serve &
ollama pull llama3.1:8b
```

### Step 2: Create Lightweight Backend
- Simple Flask server
- Ollama integration only
- Key context files loaded at startup:
  - LIFE_MAP.md
  - Constella core concepts
  - Audio workflow reference

### Step 3: UI
- Copy faithh_pet_v4.html (simplified)
- Or use terminal-only interface for speed

### Step 4: Sync Strategy
- Manual sync of key docs periodically
- Conversation ratings synced to Windows for analysis
- No real-time sync needed

---

## Installation Steps

### 1. Ollama
```bash
brew install ollama
```

### 2. Python Dependencies
```bash
cd ~/faithh
python3 -m venv venv
source venv/bin/activate
pip install flask requests
```

### 3. Backend
- Create faithh_lite.py (simplified backend)
- No ChromaDB, no complex integrations
- Just Ollama + context injection

### 4. Key Documents
- Copy from Windows: LIFE_MAP.md, constella core docs
- Or fetch via network when needed

---

## Audio Workflow Integration

The MacBook is for mastering work. FAITHH should:
- Answer quick questions during sessions
- Reference audio workflow docs (already in ~/Audio-Scripts)
- Not interrupt flow (fast responses)
- Work offline (no Windows dependency)

---

## Next Steps

1. [ ] Install Ollama
2. [ ] Pull llama3.1:8b model
3. [ ] Create faithh_lite.py backend
4. [ ] Copy key docs from Windows
5. [ ] Test basic query/response
6. [ ] Integrate with audio workflow
