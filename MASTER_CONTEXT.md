# 🎯 FAITHH Master Context & Project State

**Last Updated**: 2025-11-06  
**Updated by**: Claude (taking over from Sonnet)
**Current Status**: ✅ OPERATIONAL - Simple backend running

---

## 📊 Current System State

### Working Configuration
```
faithh_pet_v3.html (Frontend - Port 5557)
    ↓ HTTP/AJAX
faithh_simple_backend.py (Port 5557)
    ↓
Ollama (llama3.1-8b, qwen2.5-7b)
```

### Active Components
- **Frontend**: `faithh_pet_v3.html` - Battle Network themed UI ✅
- **Backend**: `faithh_simple_backend.py` - Lightweight Flask server ✅
- **AI Models**: Ollama with llama3.1-8b and qwen2.5-7b ✅
- **RAG System**: ChromaDB with 91,302 documents (ready but not connected)
- **Status**: System operational, chat working!

---

## 🔧 Active Services

| Service | Port | Status | Purpose |
|---------|------|--------|---------|
| ChromaDB | 8000 | ✅ Running | RAG document store (91k docs) |
| Ollama | 11434/11435 | ✅ Running | Embeddings (nomic-embed) |
| Unified API | 5556 | ⏳ To Start | Core orchestration |
| Backend Adapter | 5557 | ⏳ To Start | HTML UI connector |
| HTML UI | 8080 | ⏳ To Start | User interface |

---

## 📁 Key Files & Purpose

### Frontend
- `rag-chat.html` (506 lines) - Main UI (Ollama + RAG support)

### Backend APIs
- `faithh_backend_adapter.py` - NEW: Connects HTML UI to unified API
- `faithh_unified_api.py` (404 lines) - Chat + RAG + Tools orchestrator
- `faithh_api_websocket.py` (218 lines) - Original WebSocket API
- `rag_api.py` - Original RAG-only API

### Tool System
- `tool_executor.py` (226 lines) - Core orchestration engine
- `tool_registry.py` - Tool database
- `security_manager.py` - Security validation
- `config.yaml` - System configuration

### Executors
- `executors/filesystem.py` (125 lines) - File operations
- `executors/process.py` (84 lines) - Command execution

### RAG System
- `rag_processor.py` - Document processing
- `setup_rag.py` - RAG initialization
- ChromaDB collection: "documents" (91,302 docs)

### UI Alternatives
- `chat_ui.py` (275 lines) - Streamlit interface
- `search_ui.py` - Streamlit search interface

---

## 🎯 Current Task: HTML UI Integration

### What We Need:
1. ✅ Backend adapter for HTML UI (`faithh_backend_adapter.py`)
2. ⏳ Update HTML to point to adapter
3. ⏳ Test full flow: HTML → Adapter → Unified API → Services
4. ⏳ Add Claude model support (Opus for complex tasks)

### Backend Adapter Requirements:
- Accept requests from `rag-chat.html`
- Format: Compatible with existing HTML expectations
- Endpoints needed:
  - `POST /api/generate` - Chat (Ollama-compatible format)
  - `POST /search` - RAG search
  - `GET /api/tags` - Available models
  - `GET /status` - System health

### HTML UI Expectations (from code):
```javascript
// Chat request format
{
  model: "modelName",
  prompt: "user message",
  stream: false
}

// RAG search format
{
  query: "search query",
  n_results: 3
}

// Expected response
{
  response: "AI response text"
}
```

---

## 🔑 API Keys & Configuration

### Gemini
- API Key: Stored in env/config
- Model: `gemini-2.0-flash-exp`
- Status: ✅ Initialized

### Claude (Anthropic)
- To Add: For Opus model support
- Use Case: Complex reasoning, long context
- Integration Point: Backend adapter

### Ollama
- Models Available: llama3.1-8b, qwen2.5-7b, qwen30b-coding
- Embedding Model: nomic-embed
- Ports: 11434 (main), 11435 (embed)

---

## 🗂️ Project Structure

```
ai-stack/
├── Frontend
│   └── rag-chat.html ⭐ Main UI
│
├── Backend APIs
│   ├── faithh_backend_adapter.py ⭐ NEW! HTML connector
│   ├── faithh_unified_api.py     Core orchestrator
│   ├── faithh_api_websocket.py   WebSocket API
│   └── rag_api.py                RAG-only API
│
├── Core System
│   ├── tool_executor.py          Execution engine
│   ├── tool_registry.py          Tool database
│   ├── security_manager.py       Security
│   └── config.yaml               Configuration
│
├── Executors
│   ├── __init__.py
│   ├── filesystem.py             File ops
│   └── process.py                Commands
│
├── RAG System
│   ├── rag_processor.py
│   ├── setup_rag.py
│   └── ChromaDB (91,302 docs)
│
├── UI Alternatives
│   ├── chat_ui.py                Streamlit chat
│   └── search_ui.py              Streamlit search
│
├── Documentation
│   ├── MASTER_CONTEXT.md ⭐ This file
│   ├── INTEGRATION_COMPLETE.md
│   ├── ROADMAP.md
│   ├── QUICKSTART.md
│   └── [15+ other docs]
│
└── Scripts
    ├── start_faithh.sh           Launcher
    ├── test_e2e.py              Integration tests
    └── test_rag.py              RAG tests
```

---

## 🎯 Immediate Next Steps

1. **Create Backend Adapter** ✓ (in progress)
   - File: `faithh_backend_adapter.py`
   - Port: 5557
   - Purpose: Bridge HTML UI to unified API

2. **Test Connection Flow**
   - HTML → Adapter → Unified API → Gemini
   - HTML → Adapter → Unified API → RAG
   - HTML → Adapter → Unified API → Tools

3. **Add Claude/Opus Support**
   - Anthropic API integration
   - Model routing logic
   - Context injection system

4. **Update HTML UI (minimal changes)**
   - Point to adapter: `http://localhost:5557`
   - Keep existing UI/UX
   - Add Claude model option

---

## 📝 Decision Log

### 2025-11-04 - Frontend Choice
- **Decision**: Use existing `rag-chat.html` instead of Streamlit
- **Reason**: User prefers the existing beautiful gradient UI
- **Action**: Create backend adapter to connect HTML to unified API

### 2025-11-04 - Master Context System
- **Decision**: Create MASTER_CONTEXT.md for state tracking
- **Reason**: Maintain consistency across Claude conversations
- **Action**: Auto-update on key changes

### 2025-11-04 - Model Strategy
- **Decision**: Support Gemini (fast) + Claude Opus (complex)
- **Reason**: Best of both worlds - speed and depth
- **Action**: Add model routing in adapter

---

## 💡 Key Insights

### RAG System
- **91,302 documents** indexed and ready!
- Embedding dimension: 768 (collection) vs 384 (current model)
- Workaround: Use `query_texts` instead of embeddings
- Performance: Fast searches, good relevance

### Tool System
- Fully functional executor framework
- Security validation working
- All tests passing
- Ready for integration

### HTML UI
- Beautiful, modern design
- RAG toggle built-in
- Model selector present
- Ollama-compatible API expected

---

## 🔄 Auto-Update Triggers

This file should be updated when:
- New services are started/stopped
- Architecture changes
- New files are created
- Configuration changes
- Major decisions made
- Integration milestones reached

---

## 🎮 Battle Chip References

**Current Status**: "Loading Battle Chips..."
- Tool Registry: ✅ Battle Chip Folder
- Executors: ✅ Battle Chip Programs  
- Security: ✅ Firewall Protection
- Combos: ✅ Supported (1.5x multiplier)

---

**End of Master Context - Updated: 2025-11-04**
