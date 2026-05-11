# PARITY: faithh_professional_backend.py
**Last Updated:** 2025-11-09
**Status:** Active
**Version:** 3.0.0

---

## Current State

**Purpose:** Main backend server for FAITHH AI assistant with RAG capabilities

**Key Features:**
- ChromaDB integration (91,302 documents)
- Gemini API integration via environment variables
- Ollama local model support
- Tool execution system
- File upload support
- Workspace scanning
- Model identification

**Dependencies:**
- Flask (web framework)
- ChromaDB (vector database)
- python-dotenv (environment variables)
- requests (HTTP client)
- Gemini API (cloud LLM)
- Ollama (local LLM)

**Entry Points:**
- Main server: `python3 faithh_professional_backend.py`
- Serves on: `http://localhost:5557`
- Debugger PIN: 587-685-700

---

## Recent Changes

### 2025-11-08 - Environment Variable Integration
**Changed:**
- Modified to load API keys from .env file
- Added `from dotenv import load_dotenv` import
- Added `load_dotenv()` call at startup
- Replaced hardcoded `GEMINI_API_KEY` with `os.getenv("GEMINI_API_KEY")`

**Reason:** Security improvement - no hardcoded secrets in code

**Impact:** 
- Requires .env file with GEMINI_API_KEY
- More secure deployment
- Easier configuration management

### 2025-11-06 - Initial Creation
**Created:**
- Fixed embedding dimensions (using text search)
- Model identification system
- File upload support
- Workspace scanning capabilities

**Reason:** Unified backend to replace multiple fragmented backends

---

## Known Issues

- [ ] Running on Flask development server (should use production WSGI for deployment)
- [ ] No rate limiting implemented
- [ ] Error handling could be more robust

---

## Pending Changes

- [ ] Add production WSGI server configuration
- [ ] Implement rate limiting middleware
- [ ] Add comprehensive error handling
- [ ] Add request/response logging
- [ ] Create health check endpoint enhancements

---

## Configuration

**Environment Variables Required:**
- `GEMINI_API_KEY` - Google Gemini API key for cloud LLM
- `OLLAMA_HOST` - Ollama server URL (default: http://localhost:11434)

**Config File Settings:**
```yaml
# From config.yaml
chromadb:
  host: localhost
  port: 8000
```

---

## API Endpoints

**Core Endpoints:**
- `GET /` - Serve UI
- `GET /api/status` - Health check (called every 30s by UI)
- `POST /api/chat` - Main chat endpoint
- `POST /api/upload` - File upload
- `GET /api/models` - List available models

---

## Testing

**How to Test:**
```bash
# Activate venv
source venv/bin/activate

# Start server
python3 faithh_professional_backend.py

# Should see:
# ✅ ChromaDB connected: 91302 documents available
# Starting on http://localhost:5557

# Test with curl
curl http://localhost:5557/api/status

# Or open UI in browser
# Open faithh_pet_v3.html
```

**Expected Behavior:**
- Server starts without errors
- ChromaDB connects successfully
- UI can send messages
- Responses are generated

---

## Architecture Notes

**Request Flow:**
```
UI (faithh_pet_v3.html)
    ↓
POST /api/chat
    ↓
Backend processes request
    ↓
RAG search in ChromaDB (if needed)
    ↓
LLM generation (Gemini or Ollama)
    ↓
Response to UI
```

**Model Selection:**
- Tries Gemini first (if API key available)
- Falls back to Ollama local models
- User can select model via UI

---

## Security

**Implemented:**
- ✅ API key in .env file (not hardcoded)
- ✅ .env in .gitignore (not committed)

**Needs Implementation:**
- [ ] Rate limiting
- [ ] Input validation
- [ ] CORS configuration
- [ ] Authentication/authorization

---

## Performance

**Current Stats:**
- ChromaDB: 91,302 documents indexed
- Response time: ~2-5s with RAG
- Memory usage: ~500MB

**Optimization Opportunities:**
- Cache frequent queries
- Batch process uploads
- Implement query result caching

---

## Notes

- Backend is kept in root directory for easy execution
- Multiple backup copies exist (.original, .prefixbackup)
- Flask debug mode enabled (disable for production)
- Watching file changes (auto-reloads on edits)

---

*Last reviewed: 2025-11-09*
