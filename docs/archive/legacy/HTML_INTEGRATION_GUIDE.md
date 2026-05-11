# 🎯 HTML UI Integration Guide

## Quick Start

### Step 1: Start Backend Services
```bash
cd ~/ai-stack
source venv/bin/activate

# Terminal 1: Start Unified API
python3 faithh_unified_api.py

# Terminal 2: Start Backend Adapter
python3 faithh_backend_adapter.py

# Terminal 3: Serve HTML UI
python3 -m http.server 8080
```

### Step 2: Update HTML UI (One-time)

Edit `rag-chat.html` line ~250-260:

**BEFORE:**
```javascript
const OLLAMA_URL = 'http://localhost:11434';
const RAG_API = 'http://localhost:5000';
```

**AFTER:**
```javascript
const OLLAMA_URL = 'http://localhost:5557';  // Backend Adapter
const RAG_API = 'http://localhost:5557';      // Backend Adapter
```

### Step 3: Open Browser
Navigate to: **http://localhost:8080/rag-chat.html**

---

## Architecture Flow

```
Browser (rag-chat.html)
    ↓ http://localhost:5557
Backend Adapter (port 5557)
    ↓
    ├→ Unified API (5556) → Gemini + RAG + Tools
    └→ Ollama (11434) → Local models
```

---

## Model Selection in UI

| Model in UI | Routes To | Features |
|-------------|-----------|----------|
| Auto | Unified API | Gemini + RAG + Tools ⭐ |
| Gemini | Unified API | Fast + RAG + Tools |
| Llama 3.1 | Ollama | Local model |
| Qwen 2.5 | Ollama | Local model |
| Qwen 30B | Ollama | Local model (coding) |

**Recommendation**: Use "Auto" or "Gemini" for best experience!

---

## Features Available

### With Gemini/Auto:
✅ Fast responses  
✅ RAG search (91k documents)  
✅ Tool execution  
✅ Smart context injection  
✅ Source citations  

### With Ollama Models:
✅ Local processing  
✅ Privacy  
✅ Offline capable  
❌ No automatic RAG  
❌ No tool execution  

---

## RAG Toggle Behavior

**RAG ON + Gemini/Auto**:
- Automatically searches 91k documents
- Injects relevant context
- Shows sources in UI

**RAG ON + Ollama**:
- Pre-searches documents
- Adds context to prompt
- Ollama generates response

**RAG OFF**:
- Pure model response
- No document search
- Faster (no RAG overhead)

---

## Testing the Integration

### Test 1: Basic Chat
1. Select "Auto" or "Gemini"
2. Type: "Hello, how are you?"
3. Should get Gemini response

### Test 2: RAG Query
1. Enable RAG toggle
2. Type: "What did we discuss about Docker?"
3. Should see context boxes with sources

### Test 3: Tool Detection
1. Type: "Read my config.yaml file"
2. Should get response mentioning file contents

### Test 4: Ollama Model
1. Select "Llama 3.1"
2. Type any question
3. Should route directly to Ollama

---

## Troubleshooting

### "Connection failed" error
**Fix**: Make sure backend adapter is running
```bash
python3 faithh_backend_adapter.py
```

### "API error" in console
**Fix**: Check unified API is running
```bash
python3 faithh_unified_api.py
```

### RAG not working
**Fix**: Verify ChromaDB is running
```bash
curl http://localhost:8000/api/v1/heartbeat
```

### No models showing
**Fix**: Check Ollama is running
```bash
curl http://localhost:11434/api/tags
```

---

## Port Reference

| Service | Port | Check Health |
|---------|------|--------------|
| HTML UI | 8080 | http://localhost:8080 |
| Backend Adapter | 5557 | http://localhost:5557/status |
| Unified API | 5556 | http://localhost:5556/api/status |
| Ollama | 11434 | http://localhost:11434/api/tags |
| ChromaDB | 8000 | http://localhost:8000/api/v1/heartbeat |

---

## Next Steps

### Add Claude Opus (Optional)
1. Get Anthropic API key
2. Update `faithh_backend_adapter.py`
3. Add routing for complex queries

### Customize RAG Behavior
1. Edit `faithh_unified_api.py`
2. Modify `should_use_rag()` function
3. Add/remove trigger keywords

### Add More Tools
1. Create new executor in `executors/`
2. Register in tool_registry
3. Tools auto-suggested in chat

---

## Files Modified

✅ Created: `faithh_backend_adapter.py` (305 lines)  
⏳ To Edit: `rag-chat.html` (2 lines, URLs only)  

**That's it!** Minimal changes to your beautiful UI.
