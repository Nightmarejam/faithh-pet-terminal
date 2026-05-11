# How FAITHH Works - System Designer's Guide
**For**: Jonathan (and future Jonathan when things break)  
**Level**: "System Designer by Brute Force" - Clear explanations, no assumptions  
**Last Updated**: 2025-11-25

---

## 🎯 What is FAITHH?

**FAITHH** = **F**riendly **AI** **T**eaching & **H**elping **H**ub

It's your personal AI assistant with:
- **Memory** - Remembers you, your projects, your conversations
- **Knowledge** - Has access to 91,000+ documents from your past conversations and project docs
- **Personality** - MegaMan Battle Network-inspired NetNavi companion
- **Local-First** - Runs on your hardware, uses your models

---

## 🏗️ The Big Picture Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        YOU (via Browser)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FAITHH Backend (Flask Python App)               │
│                  faithh_professional_backend_fixed.py        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Memory     │  │     RAG      │  │  Auto-Index  │     │
│  │   System     │  │   Search     │  │    Queue     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   ChromaDB   │   │    Ollama    │   │    Gemini    │
│  (Knowledge) │   │  (Local AI)  │   │ (Cloud AI)   │
│  Port 8000   │   │  Port 11434  │   │  (API Key)   │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 🧠 The Three Memory Systems

FAITHH has **three separate but connected** memory systems:

### 1. **Hot Memory** (faithh_memory.json)
**What**: JSON file with your profile, projects, recent topics  
**Where**: `~/ai-stack/faithh_memory.json`  
**Updated**: Manually (for now)  
**Size**: Small (~100KB)

**Contains**:
- Your name, role, preferences
- Current projects (FAITHH, ComfyUI, Constella)
- Last 50 conversation topics
- System preferences

**Think of it as**: FAITHH's "active RAM" - instantly loaded every conversation

### 2. **Warm Memory** (ChromaDB Vector Database)
**What**: Searchable database of all your documents and conversations  
**Where**: ChromaDB Docker container (port 8000)  
**Updated**: Automatically via background indexing  
**Size**: Large (91,604 documents currently)

**Contains**:
- All your past Claude conversations (chunked)
- FAITHH project documentation
- Audio production parity files
- Code files and configs

**Think of it as**: FAITHH's "long-term memory" - searchable via RAG

### 3. **Cold Memory** (Git Repository)
**What**: Full conversation exports and historical data  
**Where**: `~/ai-stack/AI_Chat_Exports/`  
**Updated**: Manual exports  
**Size**: Very large (full conversation archives)

**Think of it as**: FAITHH's "backup brain" - for deep historical searches

---

## 🔍 How RAG (Retrieval Augmented Generation) Works

RAG is how FAITHH searches its memory to answer your questions.

### The Process:

```
1. You ask: "What did we discuss about audio routing?"
           ↓
2. Your question gets converted to a 768-number vector (embedding)
           ↓
3. ChromaDB searches for similar vectors in 91,604 documents
           ↓
4. Top 3-5 most relevant chunks are found
           ↓
5. Those chunks are added to the prompt sent to the AI model
           ↓
6. AI generates response using both its knowledge + your context
```

### Smart RAG Features:

**Conversation Detection**: 
- If you ask "what did we talk about" or "what did we discuss"
- FAITHH prioritizes conversation chunks over documentation

**Category Filtering**:
- Documents are tagged: `documentation`, `code`, `parity_file`, `live_chat`, etc.
- FAITHH can search specific categories or mix them

**Distance Scoring**:
- Results have a "distance" score (0.0 = perfect match, 1.0 = unrelated)
- FAITHH only uses results with distance < 0.7 (good matches)

---

## 🔄 Auto-Indexing System (The New Thing!)

**Problem We Solved**: Flask couldn't make HTTP calls to itself (deadlock)  
**Solution**: Background threading with a queue

### How It Works:

```
1. You send a chat message to FAITHH
           ↓
2. FAITHH responds immediately (no waiting)
           ↓
3. Your conversation is added to a Queue (thread-safe list)
           ↓
4. Background thread (always running) picks it up
           ↓
5. Thread adds it to ChromaDB in the background
           ↓
6. 1-5 seconds later: "📝 Indexed: live_conv_[timestamp]"
```

**Key Point**: Chat returns FAST, indexing happens LATER in the background.

### What Gets Indexed:

Every conversation between you and FAITHH gets saved as:
```json
{
  "document": "User: [your message]\n\nAssistant: [FAITHH's response]",
  "metadata": {
    "type": "live_conversation",
    "category": "live_chat",
    "timestamp": "2025-11-25T02:35:37",
    "model": "llama3.1-8b",
    "rag_used": false
  },
  "id": "live_conv_20251125_023537_458776"
}
```

This means future FAITHH conversations can search your past FAITHH conversations!

---

## 🤖 The AI Models

FAITHH can use multiple AI models:

### Local Models (via Ollama)

You have **3 Ollama containers** running different models:

**Container 1: ollama** (Port 11434)
- Primary inference server
- GPU 1 (RTX 3090 or RTX 1080 Ti)
- 28GB RAM limit
- Models: llama3.1-8b (your main model)

**Container 2: ollama-embed** (Port 11435)
- Embedding model server (converts text to vectors)
- GPU 0
- 12GB RAM limit
- Used for RAG search

**Container 3: ollama-qwen** (Port 11436)
- Qwen model family
- GPU 1
- 32GB RAM limit
- Alternative models for specific tasks

### Cloud Model (via API)

**Gemini 2.0 Flash Exp**
- Google's latest model
- Accessed via API key
- Used when you select "gemini" in the UI
- Faster for some tasks, but requires internet

---

## 🐳 Docker Container Stack

You're running **6 containers** in docker-compose:

```
┌─────────────────────────────────────────┐
│  ollama          (Main LLM, GPU 1)      │ Port 11434
├─────────────────────────────────────────┤
│  ollama-embed    (Embeddings, GPU 0)    │ Port 11435
├─────────────────────────────────────────┤
│  ollama-qwen     (Qwen models, GPU 1)   │ Port 11436
├─────────────────────────────────────────┤
│  langflow        (Visual AI builder)    │ Port 7860
├─────────────────────────────────────────┤
│  postgres        (Database for LangFlow)│
├─────────────────────────────────────────┤
│  chromadb        (Vector database)      │ Port 8000
└─────────────────────────────────────────┘
```

**Manage them**:
```bash
# See what's running
docker ps

# Start all containers
cd ~/ai-stack
docker-compose up -d

# Stop all containers
docker-compose down

# Restart one container
docker restart chromadb

# View logs
docker logs chromadb -f
```

---

## 📁 Critical Files & Locations

### Backend Code
- **Main Backend**: `~/ai-stack/faithh_professional_backend_fixed.py`
- **Phase 2 Blueprint**: `~/ai-stack/phase2_blueprint.py` (independent executor system)

### Memory & Data
- **Hot Memory**: `~/ai-stack/faithh_memory.json`
- **Uploads**: `~/ai-stack/uploads/`
- **Logs**: `~/ai-stack/faithh_backend.log`

### Documentation
- **Architecture**: `~/ai-stack/docs/ARCHITECTURE.md` (authoritative)
- **Parity Files**: `~/ai-stack/parity/` (real-world system state)
- **This Guide**: `~/ai-stack/docs/HOW_IT_WORKS.md`

### Configuration
- **Docker Setup**: `~/ai-stack/docker-compose.yml`
- **Environment**: `~/ai-stack/.env` (API keys, secrets)
- **Git Ignore**: `~/ai-stack/.gitignore` (security patterns)

---

## 🚀 Startup Sequence

When you want to run FAITHH:

```bash
# 1. Make sure Docker is running (check Docker Desktop on Windows)

# 2. Start ChromaDB if not running
docker start chromadb

# 3. Navigate to project
cd ~/ai-stack

# 4. Activate Python environment
source venv/bin/activate

# 5. Start FAITHH backend
python faithh_professional_backend_fixed.py

# 6. Look for these lines:
#    ✅ ChromaDB connected: 91604 documents available
#    ✅ Using all-mpnet-base-v2 (768-dim) embedding model
#    ✅ Auto-index background thread started

# 7. Open browser to http://localhost:5557
```

---

## 🔧 Common Operations

### Check System Status
```bash
curl http://localhost:5557/api/status
```

### Test Memory System
```bash
curl http://localhost:5557/api/test_memory
```

### Search Your Knowledge Base
```bash
curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "audio production", "n_results": 5}'
```

### Check What's Indexed Recently
```bash
# Search for conversations from today
curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "live_conv", "n_results": 10}'
```

---

## ❓ Troubleshooting Guide

### Backend Won't Start

**Error**: `Port 5557 already in use`
```bash
# Kill existing process
lsof -ti:5557 | xargs kill -9

# Then restart
python faithh_professional_backend_fixed.py
```

**Error**: `ChromaDB not connected`
```bash
# Check if ChromaDB is running
docker ps | grep chroma

# Start it if stopped
docker start chromadb

# Check logs if it's failing
docker logs chromadb
```

### Auto-Index Not Working

**Symptom**: No `📝 Indexed:` messages in log

**Check**:
1. Is ChromaDB running? `docker ps | grep chroma`
2. Is the background thread starting? Look for `✅ Auto-index background thread started`
3. Check backend log for errors: `tail -f ~/ai-stack/faithh_backend.log`

### RAG Returning No Results

**Symptom**: FAITHH says "I don't have information on that"

**Possible Causes**:
1. ChromaDB is empty or not connected
2. Your query is too specific (try broader terms)
3. Embedding dimension mismatch (should be 768, check status endpoint)

**Debug**:
```bash
# Check document count
curl http://localhost:5557/api/status | grep documents

# Try manual RAG search
curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "n_results": 5}'
```

---

## 🎓 Understanding the Code Flow

When you send a message to FAITHH, here's what happens:

```python
# 1. Message arrives at /api/chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    
    # 2. Load your memory from JSON file
    memory = load_memory()
    memory_context = format_memory_context(memory)
    
    # 3. Get FAITHH's personality prompt
    personality = get_faithh_personality()
    
    # 4. If RAG is enabled, search ChromaDB
    if use_rag:
        results = smart_rag_query(message)
        context = format_results(results)
    
    # 5. Combine everything into full prompt
    full_prompt = f"{personality}\n{memory_context}\n{context}\n{message}"
    
    # 6. Send to AI model (Ollama or Gemini)
    response = model.generate(full_prompt)
    
    # 7. Queue conversation for background indexing
    index_queue.put({
        'user_msg': message,
        'assistant_msg': response,
        'metadata': {...}
    })
    
    # 8. Return response immediately (don't wait for indexing)
    return jsonify({'response': response})
```

Meanwhile, in the background:
```python
# Background thread (always running)
def process_index_queue():
    while True:
        item = index_queue.get()  # Wait for next item
        index_conversation_background(**item)  # Add to ChromaDB
        # Logs: 📝 Indexed: live_conv_[timestamp]
```

---

## 📊 System Metrics

**Current State** (as of 2025-11-25):
- **Documents in ChromaDB**: 91,604
- **Embedding Model**: all-mpnet-base-v2 (768 dimensions)
- **Primary AI Model**: llama3.1-8b
- **Backend Version**: v3.1
- **Python Environment**: Python 3.11 in virtualenv

---

## 🔮 What's Next (Future Development)

### Planned Features:
1. **Conversation Threading** - Link related conversations together
2. **Memory Consolidation** - Weekly summaries of your work
3. **Domain Collections** - Separate audio, dev, personal knowledge bases
4. **Mobile Access** - Access FAITHH from phone/tablet
5. **Voice Integration** - Talk to FAITHH via audio

### Documentation TODO:
- [ ] API Reference Guide
- [ ] Deployment to Production Server guide
- [ ] Backup & Recovery procedures
- [ ] Performance tuning guide

---

## 🆘 When Things Break

### Emergency Rollback
```bash
cd ~/ai-stack
git log --oneline -10  # See recent commits
git checkout [commit-hash] -- faithh_professional_backend_fixed.py
```

### Known Good Commit
- **Commit e54e3fc**: Last known stable before auto-index threading
- **Commit [current]**: With auto-index threading (2025-11-25)

### Get Help
1. Check `~/ai-stack/HANDOFF_COMPLETION_SUMMARY.md` for recent changes
2. Check `~/ai-stack/QUICK_TEST_CARD.md` for test procedures
3. Review backend logs: `tail -100 ~/ai-stack/faithh_backend.log`
4. Ask Claude for help (with context from this guide)

---

## 📚 Related Documentation

- **ARCHITECTURE.md** - Deep technical architecture (authoritative source)
- **PARITY_INDEX.md** - Master index of system state documentation
- **audio_workspace.md** - Audio production setup and workflows
- **network_infrastructure.md** - Network topology and configs
- **dev_environment.md** - Development environment details

---

## 💡 Pro Tips

1. **Keep Docker Running**: Set Docker Desktop to start with Windows
2. **Use Screen/Tmux**: Keep FAITHH backend running in background session
3. **Regular Backups**: Export conversations monthly to cold storage
4. **Watch the Logs**: `tail -f faithh_backend.log` when debugging
5. **Document as You Go**: Update parity files when hardware/workflows change

---

## 🎯 The Philosophy

FAITHH is designed to be:
- **Transparent**: You can see how everything works
- **Local-First**: Your data stays on your hardware
- **Memory-Enabled**: Builds context over time
- **ADHD-Friendly**: Clear documentation, no hidden complexity
- **Extensible**: Add features without breaking existing ones

You're not just using an AI - you're building a companion that learns with you.

---

**Last Updated**: 2025-11-25  
**Maintainer**: Jonathan + FAITHH system  
**Status**: Living document - update as system evolves

---

*"I'm FAITHH. I remember our work together. Let's build something amazing."*
