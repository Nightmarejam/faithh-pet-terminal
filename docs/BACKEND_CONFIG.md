# FAITHH Backend Configuration

## Current Configuration

**File:** `~/ai-stack/faithh_professional_backend.py`

### Port & Host
- **Port:** 5557
- **Host:** 0.0.0.0 (all interfaces)
- **Access URLs:**
  - http://localhost:5557
  - http://127.0.0.1:5557
  - http://192.158.1.232:5557

### Running Status
- **PIDs:** 16440 (parent), 16481 (worker with debugger)
- **Mode:** Background with nohup
- **Logs:** `~/ai-stack/faithh_backend.log`
- **Debug Mode:** ON (auto-reload on code changes)

### AI Service Connections

#### ChromaDB (BROKEN)
```python
# Line 47-48
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_collection(name="documents")
```
**Status:** Offline - expects Docker ChromaDB on port 8000
**Issue:** Container not running

#### Ollama (WORKING)
- **Models Available:** 3
  - qwen2.5-coder:7b
  - qwen2.5-7b:latest  
  - llama3.1-8b:latest
- **Status:** Online

#### Gemini API (CONFIGURED)
- **Model:** gemini-2.0-flash-exp
- **Status:** Configured (API key present)

### Features Enabled
- ✅ Fixed embedding dimensions (text search)
- ✅ Model identification
- ✅ File upload support
- ✅ Workspace scanning
- ❌ ChromaDB/RAG (offline)

### Workspace
- **Upload Folder:** `/home/jonat/ai-stack/uploads`
- **Uploaded Files:** 1

## API Endpoints

### Status Check
```bash
curl -s http://localhost:5557/api/status | jq
```

### RAG Query (currently broken)
```bash
curl -X POST http://localhost:5557/api/rag_query \
  -H "Content-Type: application/json" \
  -d '{"query": "your question here"}'
```

## Backend Management Commands

### Start
```bash
cd ~/ai-stack
source venv/bin/activate
nohup python faithh_professional_backend.py > faithh_backend.log 2>&1 &
```

### Stop
```bash
pkill -f faithh_professional_backend.py
```

### Restart
```bash
pkill -f faithh_professional_backend.py
cd ~/ai-stack
source venv/bin/activate
nohup python faithh_professional_backend.py > faithh_backend.log 2>&1 &
```

### Check Status
```bash
ps aux | grep faithh_professional_backend | grep -v grep
```

### View Logs (Live)
```bash
tail -f ~/ai-stack/faithh_backend.log
```

### Check Port
```bash
ss -tlnp | grep 5557
# or
lsof -i :5557
```

## Common Issues & Fixes

### Port Already in Use
```bash
# Find and kill process on 5557
lsof -i :5557 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### ChromaDB Connection Failed
See CHROMADB_STATUS.md for solutions:
- Option A: Start Docker ChromaDB on port 8000
- Option B: Switch to PersistentClient

### Backend Not Starting
```bash
# Check for errors
cat ~/ai-stack/faithh_backend.log

# Verify venv activated
which python  # Should show: /home/jonat/ai-stack/venv/bin/python

# Check dependencies
pip list | grep -E "chromadb|flask|ollama"
```

## Configuration Changes Needed

### To Fix ChromaDB (Option B - Local)
Replace lines 47-48 with:
```python
chroma_client = chromadb.PersistentClient(path="./faithh_rag")
collection = chroma_client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)
```

### To Fix ChromaDB (Option A - Docker)
1. Start ChromaDB container (see DOCKER_SERVICES.md)
2. No code changes needed (already configured for this)

## Dependencies
```
Flask==3.0.0
chromadb==0.4.18
sentence-transformers==2.2.2
ollama==0.1.6
google-generativeai==0.3.1
```
