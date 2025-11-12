# 🗺️ FAITHH Chat Integration Roadmap

## Current State → Target State

### BEFORE (Now):
```
┌────────────┐     ┌──────────────┐     ┌─────────────┐
│ HTML UI    │────▶│ faithh_api   │     │  rag_api    │
│ (manual)   │     │ (tools+chat) │     │  (search)   │
└────────────┘     └──────────────┘     └─────────────┘
                          │                     │
                          ▼                     ▼
                   Tool Executor          ChromaDB
```

### AFTER (Goal):
```
┌─────────────────────────────────────────────────┐
│         Streamlit Chat UI ⭐                    │
│  Beautiful, Real-time, Easy to Use              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼ Single Connection
┌─────────────────────────────────────────────────┐
│      UNIFIED API (faithh_unified_api.py) ⭐     │
│  ┌───────────────────────────────────────────┐ │
│  │        Chat Orchestrator                  │ │
│  │  "Should I use RAG? Tools? Both?"         │ │
│  └───────────────────────────────────────────┘ │
└──┬────────────┬──────────────┬────────────────┘
   │            │              │
   ▼            ▼              ▼
┌─────┐    ┌────────┐    ┌──────────┐
│Gemini│   │  RAG   │    │  Tools   │
│ API  │   │ChromaDB│    │Executors │
└─────┘    └────────┘    └──────────┘
```

---

## 📅 Implementation Timeline

### Phase 1: Setup & Cleanup (15 min)
- [x] Assess current state
- [ ] Git commit current work
- [ ] Create .gitignore
- [ ] Test existing RAG system
- [ ] Document RAG flow

### Phase 2: Unified API (45 min)
- [ ] Create `faithh_unified_api.py`
  - [ ] Chat orchestrator (15 min)
  - [ ] RAG integration (15 min)
  - [ ] Tool integration (10 min)
  - [ ] Streaming support (5 min)

### Phase 3: Streamlit UI (60 min)
- [ ] Create `chat_ui.py`
  - [ ] Basic layout (10 min)
  - [ ] Chat interface (15 min)
  - [ ] RAG display (10 min)
  - [ ] Tool execution UI (10 min)
  - [ ] Settings panel (10 min)
  - [ ] Polish & styling (5 min)

### Phase 4: Integration (30 min)
- [ ] Connect UI → API
- [ ] Test full flow
- [ ] Debug issues
- [ ] Add error handling

### Phase 5: Testing & Polish (30 min)
- [ ] Test chat flow
- [ ] Test RAG activation
- [ ] Test tool execution
- [ ] UI/UX improvements
- [ ] Final git commit

**Total Time: ~3 hours**

---

## 🎯 Feature Checklist

### Chat Basics
- [ ] Send/receive messages
- [ ] Message history
- [ ] Clear history
- [ ] Copy messages
- [ ] Markdown rendering
- [ ] Code highlighting

### RAG Features
- [ ] Auto-detect when to use RAG
- [ ] Manual RAG toggle
- [ ] Show source documents
- [ ] Display similarity scores
- [ ] Highlight matched text
- [ ] Source metadata (date, file, etc.)

### Tool Features
- [ ] Detect tool needs from message
- [ ] Show tool execution progress
- [ ] Display tool results inline
- [ ] Handle tool errors gracefully
- [ ] Permission prompts
- [ ] Tool history

### Advanced
- [ ] Streaming responses (word-by-word)
- [ ] File upload (for RAG indexing)
- [ ] Export chat history
- [ ] Search in chat history
- [ ] Model switching (Gemini ↔ Ollama)
- [ ] Temperature/params control

---

## 🔧 Technical Details

### API Endpoints Needed

#### Unified API (`faithh_unified_api.py`):
```python
# HTTP Endpoints
POST   /api/chat              # Main chat (with RAG + tools)
GET    /api/status            # System health
GET    /api/rag/stats         # RAG database stats
POST   /api/tools/execute     # Direct tool execution

# WebSocket
WS     /ws/chat              # Streaming chat
```

### Data Flow Example

**User Message**: "What did we discuss about Docker yesterday?"

```
1. Streamlit sends: POST /api/chat
   {
     "message": "What did we discuss about Docker yesterday?",
     "use_rag": true,
     "use_tools": false
   }

2. Orchestrator analyzes:
   - Contains: "discuss", "yesterday" → RAG needed ✓
   - No tool mentions → Tools not needed ✗

3. RAG Search:
   - Query: "Docker discussion"
   - Results: 3 relevant chunks
   - Scores: [0.89, 0.82, 0.78]

4. Gemini Response:
   - Context: RAG results + conversation history
   - Generated answer with citations

5. Response to UI:
   {
     "answer": "Yesterday we discussed...",
     "sources": [...],
     "used_rag": true,
     "used_tools": false
   }
```

---

## 📚 Code Structure

### `faithh_unified_api.py` Structure:
```python
# 1. Imports & Setup
from flask import Flask, request, jsonify
from flask_sock import Sock
import chromadb
from tool_executor import get_executor
import google.generativeai as genai

# 2. Orchestrator Class
class ChatOrchestrator:
    def __init__(self):
        self.rag_client = chromadb.HttpClient(...)
        self.tool_executor = get_executor()
        self.gemini = genai.GenerativeModel(...)
    
    async def handle_message(self, message, context):
        # Decision logic
        # RAG search
        # Tool execution
        # Response generation
        pass

# 3. Flask Routes
@app.route('/api/chat', methods=['POST'])
def chat():
    orchestrator = get_orchestrator()
    result = orchestrator.handle_message(...)
    return jsonify(result)

# 4. WebSocket Handler
@sock.route('/ws/chat')
def websocket_chat(ws):
    while True:
        message = ws.receive()
        for chunk in stream_response(message):
            ws.send(chunk)
```

### `chat_ui.py` Structure:
```python
# 1. Setup
import streamlit as st
import requests

# 2. Page Config
st.set_page_config(
    page_title="FAITHH Chat",
    page_icon="💬",
    layout="wide"
)

# 3. Sidebar
with st.sidebar:
    # Settings
    model = st.selectbox(...)
    use_rag = st.toggle(...)
    # Stats
    st.metric("Messages", len(st.session_state.messages))

# 4. Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            # Show RAG sources
            pass

# 5. Input & Processing
if prompt := st.chat_input():
    response = call_api(prompt)
    st.session_state.messages.append(response)
    st.rerun()
```

---

## 🎨 UI Design Mockup

### Streamlit Chat Interface:
```
╔════════════════════════════════════════════════════╗
║  💬 FAITHH Chat                     [Settings ⚙️]  ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  🤖 Assistant                                      ║
║  ┌──────────────────────────────────────────────┐ ║
║  │ Hello! I can help with chat, RAG search,    │ ║
║  │ and tool execution. What would you like?    │ ║
║  └──────────────────────────────────────────────┘ ║
║                                                    ║
║  👤 You                                            ║
║  ┌──────────────────────────────────────────────┐ ║
║  │ Read my config.yaml file                     │ ║
║  └──────────────────────────────────────────────┘ ║
║                                                    ║
║  🤖 Assistant                                      ║
║  ┌──────────────────────────────────────────────┐ ║
║  │ I'll read that file for you.                 │ ║
║  │                                               │ ║
║  │ 🔧 Executing: read_file(path="config.yaml") │ ║
║  │ ✅ Success: Read 1252 bytes, 64 lines        │ ║
║  │                                               │ ║
║  │ Here's what I found:                         │ ║
║  │ • Security: 3 allowed directories            │ ║
║  │ • Timeout: 30000ms                           │ ║
║  │ • Tools: enabled                             │ ║
║  └──────────────────────────────────────────────┘ ║
║                                                    ║
║  ┌──────────────────────────────────────────────┐ ║
║  │ 💬 Ask anything...                           │ ║
║  └──────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════╝

Sidebar:
┌────────────────┐
│ Settings       │
├────────────────┤
│ Model: Gemini ▼│
│ ☑ Enable RAG   │
│ ☑ Enable Tools │
├────────────────┤
│ Stats          │
│ Messages: 4    │
│ RAG Docs: 1.2k │
│ Tools Used: 1  │
└────────────────┘
```

---

## 🚀 Quick Actions

### Action 1: Git Commit Now
```bash
cd ~/ai-stack
git add .
git commit -m "feat: complete tool execution system

- tool_executor.py (226 lines)
- executors: filesystem + process
- faithh_api_websocket.py with WebSocket
- Comprehensive documentation
- All tests passing"
git push
```

### Action 2: Test Existing RAG
```bash
# Start ChromaDB (if not running)
chroma run --path ./chroma_data --port 8000

# Start Ollama (if not running)
# Check embeddings work
curl http://localhost:11435/api/embeddings \
  -d '{"model":"nomic-embed","prompt":"test"}'

# Test search
python3 search_ui.py
```

### Action 3: Create Unified API
Start with skeleton:
```python
# faithh_unified_api.py
from flask import Flask, request, jsonify
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    # TODO: Implement
    return jsonify({"response": "Hello"})

if __name__ == '__main__':
    app.run(port=5556, debug=True)
```

---

## ✅ Validation Points

After each phase, verify:

### Phase 1:
- [x] Current code committed to git
- [ ] Can list all files with `git status`
- [ ] RAG system accessible (ChromaDB running)
- [ ] Can query RAG with existing tools

### Phase 2:
- [ ] Unified API starts without errors
- [ ] `/api/chat` endpoint responds
- [ ] Can integrate with RAG
- [ ] Can integrate with tools
- [ ] Streaming works

### Phase 3:
- [ ] Streamlit UI launches (`streamlit run chat_ui.py`)
- [ ] Can send messages
- [ ] Messages display correctly
- [ ] UI is responsive

### Phase 4:
- [ ] UI connects to API
- [ ] Full chat flow works
- [ ] RAG activates correctly
- [ ] Tools execute from chat
- [ ] Errors handled gracefully

### Phase 5:
- [ ] All features working
- [ ] UI polished
- [ ] Performance acceptable
- [ ] Committed to git

---

**Ready to start?** 

Recommend order:
1. Git commit (5 min)
2. Test existing RAG (10 min)
3. Create unified API skeleton (15 min)
4. Build from there!

What would you like to do first?
