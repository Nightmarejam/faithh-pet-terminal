# 🎯 FAITHH Frontend Integration & RAG Chat Plan

## 📊 Current State Assessment

### ✅ What We Have (Backend)
1. **Tool Execution System** ✅
   - `tool_executor.py` - Complete engine
   - `executors/filesystem.py` - File operations
   - `executors/process.py` - Command execution
   - `faithh_api_websocket.py` - WebSocket + HTTP API

2. **RAG Infrastructure** ✅ (Already exists!)
   - `rag_api.py` - Flask API for RAG search
   - `rag_processor.py` - Document processing
   - `search_ui.py` - Streamlit search interface
   - `setup_rag.py` - RAG setup scripts
   - ChromaDB integration (port 8000)
   - Ollama embeddings (nomic-embed, port 11435)

3. **Existing UI** ✅
   - `rag-chat.html` - HTML/JS chat interface (506 lines!)
   - Connected to RAG backend
   - Model selector (Gemini/Ollama)
   - RAG toggle

### ❌ What's Missing
1. Connection between tool system and chat UI
2. Unified API that combines chat + RAG + tools
3. Streamlit chat experience (you want this!)
4. Git tracking of progress

---

## 🎯 Goal: Seamless Chat Experience

### What "Seamless" Means:
```
User types message
    ↓
System decides: RAG needed? Tools needed? Just chat?
    ↓
Executes appropriate actions
    ↓
Streams response back in real-time
    ↓
Beautiful UI shows everything
```

---

## 🏗️ Architecture Plan

### Option A: Unified API (RECOMMENDED)
```
┌─────────────────────────────────────────────────────┐
│          Streamlit Chat UI (New!)                   │
│  Beautiful, fast, easy to iterate                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼ HTTP/WebSocket
┌─────────────────────────────────────────────────────┐
│     UNIFIED FAITHH API (faithh_unified_api.py)      │
│  ┌───────────────────────────────────────────────┐ │
│  │  Chat Orchestrator                            │ │
│  │  • Decides: RAG? Tools? Just chat?            │ │
│  │  • Streams responses                          │ │
│  │  • Handles context                            │ │
│  └───────────────────────────────────────────────┘ │
└──┬──────────────┬──────────────┬───────────────────┘
   │              │              │
   ▼              ▼              ▼
┌────────┐  ┌──────────┐  ┌──────────────┐
│ Gemini │  │ RAG      │  │ Tool System  │
│ Chat   │  │ Search   │  │ (Executors)  │
└────────┘  └──────────┘  └──────────────┘
```

**Benefits**:
- Single endpoint for everything
- Smart routing
- Clean architecture
- Easy to extend

### Option B: Keep Separate (Current)
```
Streamlit UI → Multiple backends
    ├→ faithh_api_websocket.py (tools + chat)
    └→ rag_api.py (RAG search)
```

**Issues**:
- Multiple connections
- Complex coordination
- Harder to maintain

---

## 🎨 Streamlit Chat UI Design

### Core Features:
1. **Chat Interface**
   - Message history
   - Streaming responses
   - Code highlighting
   - File attachments

2. **RAG Integration**
   - Auto-search on relevant queries
   - Show source documents
   - Similarity scores
   - Toggle RAG on/off

3. **Tool Execution**
   - Show tool calls in chat
   - Display results inline
   - Progress indicators
   - Error handling

4. **Settings Panel**
   - Model selection (Gemini/Ollama)
   - RAG settings (# results, threshold)
   - Tool permissions
   - Theme toggle

---

## 🔧 Implementation Steps

### Phase 1: Git Setup (5 min)
```bash
cd ~/ai-stack
git add .
git commit -m "feat: complete tool execution system with docs"
git push
```

### Phase 2: Create Unified API (30 min)
File: `faithh_unified_api.py`

**Components**:
1. Chat orchestrator
2. RAG integration (from existing rag_api.py)
3. Tool execution (from faithh_api_websocket.py)
4. Smart routing logic
5. Streaming responses

**Pseudocode**:
```python
async def handle_message(message, context):
    # 1. Analyze message
    needs_rag = should_use_rag(message)
    needs_tools = detect_tool_needs(message)
    
    # 2. Get RAG context if needed
    if needs_rag:
        rag_results = await search_rag(message)
        context.add(rag_results)
    
    # 3. Generate response with Gemini
    response = await gemini.generate(message, context)
    
    # 4. Execute tools if mentioned
    if needs_tools:
        tool_results = await execute_tools(response)
        response.append(tool_results)
    
    # 5. Stream back to UI
    yield response
```

### Phase 3: Streamlit Chat UI (45 min)
File: `chat_ui.py`

**Features**:
```python
import streamlit as st

# Layout
st.title("💬 FAITHH Chat")
st.caption("AI with RAG + Tools")

# Sidebar
with st.sidebar:
    model = st.selectbox("Model", ["Gemini", "Ollama"])
    use_rag = st.toggle("Enable RAG", value=True)
    use_tools = st.toggle("Enable Tools", value=True)

# Chat interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- {src}")

# Input
if prompt := st.chat_input("Ask anything..."):
    # Send to unified API
    response = call_unified_api(prompt, use_rag, use_tools)
    # Stream response
    with st.chat_message("assistant"):
        st.write_stream(response)
```

### Phase 4: Connect Everything (20 min)
1. Update unified API endpoints
2. Test Streamlit → API connection
3. Verify RAG integration
4. Test tool execution from chat

### Phase 5: Polish (30 min)
1. Error handling
2. Loading states
3. Source citations
4. Tool execution UI
5. Settings persistence

---

## 📁 New Files to Create

1. **`faithh_unified_api.py`** (~300 lines)
   - Combines: chat, RAG, tools
   - Single endpoint: `/api/chat`
   - WebSocket: `/ws/chat` (streaming)

2. **`chat_ui.py`** (~200 lines)
   - Streamlit interface
   - Clean, modern design
   - Real-time streaming

3. **`chat_orchestrator.py`** (~150 lines)
   - Smart routing logic
   - Context management
   - RAG decision making

4. **`.gitignore`** (if not exists)
   - venv/
   - __pycache__/
   - *.pyc
   - .env

---

## 🎯 RAG Integration Details

### When to Use RAG:
```python
def should_use_rag(message: str) -> bool:
    # Use RAG for:
    # - Questions about past conversations
    # - "Remember when..." queries
    # - Document references
    # - Knowledge retrieval
    
    rag_keywords = [
        'remember', 'told you', 'said', 'mentioned',
        'conversation', 'chat', 'discussed',
        'document', 'file', 'note'
    ]
    
    return any(kw in message.lower() for kw in rag_keywords)
```

### RAG Response Format:
```python
{
    "answer": "Based on your documents...",
    "sources": [
        {
            "content": "...",
            "metadata": {...},
            "score": 0.85
        }
    ],
    "used_rag": True
}
```

---

## 🔨 Tool Integration in Chat

### Tool Detection:
```python
def detect_tool_needs(message: str) -> List[str]:
    # Detect tool mentions:
    tools = []
    
    if 'read' in message and 'file' in message:
        tools.append('read_file')
    if 'run' in message or 'execute' in message:
        tools.append('run_command')
    if 'list' in message and ('files' in message or 'directory' in message):
        tools.append('list_directory')
    
    return tools
```

### Tool Execution UI:
```
User: "Read the config.yaml file"
    ↓
Assistant: "I'll read that file for you."
    [🔧 Executing: read_file(path=config.yaml)]
    ↓
    [✅ Success: Read 1252 bytes, 64 lines]
    ↓
Assistant: "Here's what I found in config.yaml:
    - Security settings: 3 allowed directories...
    - Tool timeout: 30000ms
    - ..."
```

---

## 💾 Git Commit Strategy

### Commit Points:
1. **Now**: "feat: complete tool execution system"
2. **After unified API**: "feat: create unified API with RAG + tools"
3. **After Streamlit UI**: "feat: add Streamlit chat interface"
4. **After integration**: "feat: connect UI to unified backend"
5. **After polish**: "polish: improve UX and error handling"

### Example Commits:
```bash
git add .
git commit -m "feat: complete tool execution system with docs

- Created tool_executor.py (226 lines)
- Added filesystem and process executors
- Implemented WebSocket API
- All tests passing
- Comprehensive documentation"

git push
```

---

## 🚀 Quick Start Implementation

### Fastest Path (2 hours):
1. ✅ Git commit current work (5 min)
2. ✅ Create `faithh_unified_api.py` (30 min)
3. ✅ Create `chat_ui.py` (45 min)
4. ✅ Connect and test (20 min)
5. ✅ Polish + commit (20 min)

### Result:
```
User opens: streamlit run chat_ui.py
    ↓
Beautiful chat interface
    ↓
Type: "What did I say about Docker?"
    ↓
System: Uses RAG → Finds conversation → Answers
    ↓
Type: "Read my config file"
    ↓
System: Executes tool → Shows result → Explains
```

---

## 📊 Expected Architecture

### Files After Integration:
```
ai-stack/
├── faithh_unified_api.py      ← NEW! Single API
├── chat_ui.py                  ← NEW! Streamlit UI
├── chat_orchestrator.py        ← NEW! Smart routing
├── tool_executor.py            ← Existing
├── rag_api.py                  ← Merge into unified
├── rag_processor.py            ← Keep for indexing
├── search_ui.py                ← Optional: Keep or replace
├── faithh_api_websocket.py     ← Deprecate or keep
└── executors/
    ├── filesystem.py
    ├── process.py
    └── rag.py                  ← NEW! RAG as executor
```

---

## 🎯 Success Criteria

✅ User opens Streamlit UI  
✅ Can chat with Gemini/Ollama  
✅ RAG automatically activates for relevant queries  
✅ Can execute tools from chat  
✅ Responses stream in real-time  
✅ Beautiful, polished interface  
✅ All features work together seamlessly  

---

## 🤔 Decision Points

### Question 1: Keep existing HTML UI?
- **Option A**: Keep as backup/alternative
- **Option B**: Replace with Streamlit entirely ⭐

**Recommendation**: B - Streamlit is easier to iterate

### Question 2: Unified API or separate?
- **Option A**: Single unified API ⭐
- **Option B**: Keep split

**Recommendation**: A - Much cleaner

### Question 3: When to use RAG?
- **Option A**: Auto-detect ⭐
- **Option B**: Always use
- **Option C**: User toggle

**Recommendation**: A + C - Auto but allow override

---

## 🎨 Next Steps

**What do you want to do first?**

1. **Git commit** current work?
2. **Create unified API** (faithh_unified_api.py)?
3. **Create Streamlit UI** (chat_ui.py)?
4. **Explore existing RAG** setup first?

I recommend: **1 → 4 → 2 → 3** (commit, explore RAG, build API, build UI)

This gives us clean checkpoints and understanding of what exists!
