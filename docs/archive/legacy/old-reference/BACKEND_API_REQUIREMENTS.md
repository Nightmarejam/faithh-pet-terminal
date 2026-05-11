# 🔧 Backend API Requirements for V4
**Created:** November 9, 2025
**Current Backend:** `faithh_professional_backend.py` (Port 5557)
**Status:** ✅ Stable - DO NOT BREAK

---

## 📊 Current Working Endpoints (V3)

### ✅ Already Implemented

#### 1. `GET /`
- **Purpose:** Serve HTML UI
- **Current:** Returns `faithh_pet_v3.html`
- **V4 Need:** Should be able to serve `faithh_pet_v4.html` or route based on version

#### 2. `GET /images/<path:filename>`
- **Purpose:** Serve avatar images and UI assets
- **Status:** ✅ Working
- **V4 Need:** Must continue working for FAITHH and PULSE avatars
- **Files Needed:**
  - `images/faithh.png` (or updated version)
  - `images/pulse.png` (or updated version)
  - Any new avatar variations

#### 3. `POST /api/chat`
**Request:**
```json
{
  "message": "User's message text",
  "model": "llama3.1-8b" or "gemini-2.0-flash-exp",
  "use_rag": true/false
}
```

**Response:**
```json
{
  "success": true,
  "response": "AI response text",
  "model_used": "gemini-2.0-flash-exp",
  "provider": "Google",
  "response_time": 2.456,
  "rag_used": true,
  "rag_results": ["context1", "context2", "context3"]
}
```

**Status:** ✅ Working perfectly
**V4 Need:** No changes required

---

#### 4. `POST /api/upload`
- **Purpose:** Handle file uploads
- **Supported:** txt, pdf, png, jpg, jpeg, gif, md, py, js, html, css, json, yaml, yml
- **Max Size:** 16MB
- **Status:** ✅ Working
- **V4 Need:** Keep as-is

---

#### 5. `POST /api/rag_search`
**Request:**
```json
{
  "query": "search term",
  "n_results": 3
}
```

**Response:**
```json
{
  "success": true,
  "results": [...],
  "count": 3
}
```

**Status:** ✅ Working
**V4 Need:** Keep as-is

---

#### 6. `GET /api/status`
**Response:**
```json
{
  "success": true,
  "services": {
    "chromadb": {
      "status": "online",
      "documents": 91302,
      "note": "Using text-based search"
    },
    "ollama": {
      "status": "online",
      "models": ["qwen2.5-7b:latest", "llama3.1-8b:latest"],
      "count": 2
    },
    "gemini": {
      "status": "configured",
      "model": "gemini-2.0-flash-exp"
    },
    "current_model": {
      "name": "llama3.1-8b",
      "provider": "Meta (via Ollama)",
      "last_response_time": 16.421316
    }
  },
  "workspace": {
    "upload_folder": "/home/jonat/ai-stack/uploads",
    "uploaded_files": 0
  }
}
```

**Status:** ✅ Working perfectly
**V4 Need:** This is PERFECT - no changes needed!

---

#### 7. `GET /api/workspace/scan`
- **Purpose:** Scan workspace for files
- **Status:** ✅ Working
- **V4 Need:** Keep as-is

---

#### 8. `GET /health`
- **Purpose:** Health check endpoint
- **Status:** ✅ Working
- **V4 Need:** Keep as-is

---

## 🆕 NEW Endpoints Needed for V4

### Priority 1: Essential for Avatar/Monitoring Features

#### 1. `GET /api/system/health` ⭐ NEW
**Purpose:** Detailed system health for PULSE monitoring display

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-11-09T17:30:00Z",
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 34.1,
    "uptime_seconds": 3600
  },
  "services": {
    "backend": {
      "status": "healthy",
      "port": 5557,
      "requests_handled": 1234,
      "avg_response_time": 2.3
    },
    "chromadb": {
      "status": "healthy",
      "documents": 91302,
      "last_query_time": 0.45
    },
    "ollama": {
      "status": "healthy",
      "models_loaded": 2
    }
  },
  "pulse_status": {
    "state": "optimal" | "warning" | "critical",
    "message": "All systems operational",
    "last_check": "2025-11-09T17:30:00Z"
  }
}
```

**Why Needed:** To populate PULSE's monitoring displays with real data

---

#### 2. `GET /api/stats/session` ⭐ NEW
**Purpose:** Session statistics for stats panel in V4 UI

**Response:**
```json
{
  "success": true,
  "session": {
    "started_at": "2025-11-09T16:00:00Z",
    "duration_seconds": 5400,
    "messages_sent": 45,
    "messages_received": 45,
    "total_tokens_used": 12500,
    "avg_response_time": 2.8
  },
  "current": {
    "active_model": "gemini-2.0-flash-exp",
    "rag_enabled": true,
    "last_query": "2 minutes ago"
  }
}
```

**Why Needed:** V4 has session statistics panel that needs real data

---

#### 3. `POST /api/avatar/state` ⭐ NEW
**Purpose:** Update avatar state/expression based on context

**Request:**
```json
{
  "avatar": "faithh" | "pulse",
  "state": "idle" | "thinking" | "speaking" | "error" | "happy",
  "context": "optional context for state change"
}
```

**Response:**
```json
{
  "success": true,
  "avatar": "faithh",
  "state": "thinking",
  "animation": "subtle-pulse",
  "image_url": "/images/faithh_thinking.png"
}
```

**Why Needed:** To make avatars react to conversation state

---

### Priority 2: Nice-to-Have Enhancements

#### 4. `GET /api/models/list` ⭐ NEW
**Purpose:** Get available models for model selector dropdown

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "id": "gemini-2.0-flash-exp",
      "name": "Gemini 2.0 Flash",
      "provider": "Google",
      "status": "available",
      "recommended": true
    },
    {
      "id": "llama3.1-8b",
      "name": "Llama 3.1 8B",
      "provider": "Meta (via Ollama)",
      "status": "available",
      "recommended": false
    },
    {
      "id": "qwen2.5-7b",
      "name": "Qwen 2.5 7B",
      "provider": "Alibaba (via Ollama)",
      "status": "available",
      "recommended": false
    }
  ]
}
```

**Why Needed:** V4 UI has model selector - needs to know what's available

---

#### 5. `POST /api/settings/update` ⭐ NEW
**Purpose:** Update user preferences/settings

**Request:**
```json
{
  "theme": "pet-terminal" | "modern" | "minimal",
  "default_model": "gemini-2.0-flash-exp",
  "rag_default": true,
  "avatar_animations": true
}
```

**Response:**
```json
{
  "success": true,
  "settings": { /* saved settings */ }
}
```

**Why Needed:** Persistence for UI preferences

---

#### 6. `GET /api/conversation/history` ⭐ NEW
**Purpose:** Retrieve conversation history

**Response:**
```json
{
  "success": true,
  "conversations": [
    {
      "id": "conv_123",
      "timestamp": "2025-11-09T16:00:00Z",
      "messages": [
        {
          "role": "user",
          "content": "Hello",
          "timestamp": "2025-11-09T16:00:00Z"
        },
        {
          "role": "assistant",
          "content": "Hi there!",
          "model": "gemini-2.0-flash-exp",
          "timestamp": "2025-11-09T16:00:05Z"
        }
      ]
    }
  ]
}
```

**Why Needed:** Conversation history feature (nice-to-have)

---

## 🎯 Implementation Plan

### Phase 1: Backend Stability (THIS WEEK)
**Goal:** Ensure v3 backend is rock-solid before adding features

#### Tasks:
- [x] Document all current endpoints
- [ ] Add comprehensive error handling
- [ ] Add request/response logging
- [ ] Create unit tests for existing endpoints
- [ ] Performance profiling
- [ ] Fix any bugs found during testing

**Timeline:** 2-3 days
**Tools:** VS Code Extension (this session)

---

### Phase 2: Priority 1 Endpoints (NEXT WEEK)
**Goal:** Add essential endpoints for v4 UI features

#### Tasks:
- [ ] Implement `/api/system/health`
- [ ] Implement `/api/stats/session`
- [ ] Implement `/api/avatar/state`
- [ ] Add session tracking middleware
- [ ] Create system monitoring utilities
- [ ] Test with v3 UI first (ensure no breaks)

**Timeline:** 3-4 days
**Tools:** VS Code Extension

---

### Phase 3: Priority 2 Endpoints (WEEK 3)
**Goal:** Add nice-to-have features

#### Tasks:
- [ ] Implement `/api/models/list`
- [ ] Implement `/api/settings/update`
- [ ] Implement `/api/conversation/history`
- [ ] Add database for persistence (SQLite)
- [ ] Add configuration management

**Timeline:** 2-3 days

---

### Phase 4: V4 UI Integration (WEEK 3-4)
**Goal:** Connect new backend to designed V4 UI

#### Tasks:
- [ ] Build v4 UI based on Leonardo AI designs
- [ ] Connect to all endpoints
- [ ] Test avatar state changes
- [ ] Test monitoring displays
- [ ] End-to-end testing
- [ ] Performance optimization

**Timeline:** 4-5 days

---

## 🛡️ Safety Protocols

### During Backend Development:

1. **NEVER modify working endpoints directly**
   - Copy functions before changing
   - Test new code separately
   - Use feature flags

2. **Version Control**
   ```bash
   git commit -m "Stable v3 backend checkpoint"
   # Before making ANY changes
   ```

3. **Testing Protocol**
   - Test new endpoint in isolation
   - Test with v3 UI (ensure no breaks)
   - Test with v4 UI (new features)
   - Test error cases

4. **Rollback Plan**
   ```bash
   # Keep backup
   cp faithh_professional_backend.py faithh_professional_backend_v3_stable.py

   # If something breaks:
   cp faithh_professional_backend_v3_stable.py faithh_professional_backend.py
   ```

---

## 📋 Current Backend Dependencies

```python
# From requirements.txt and code inspection
flask                    # Web framework
flask-cors              # CORS support
chromadb                # Vector database
requests                # HTTP client
python-dotenv           # Environment variables
google-generativeai     # Gemini API
werkzeug               # File upload utilities
```

**Status:** ✅ All working, no conflicts

---

## 🔍 Endpoint Testing Commands

### Test Current Endpoints:

```bash
# 1. Status check
curl http://localhost:5557/api/status | jq

# 2. Chat test
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "llama3.1-8b", "use_rag": false}' | jq

# 3. RAG search
curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "n_results": 3}' | jq

# 4. Health check
curl http://localhost:5557/health

# 5. Workspace scan
curl http://localhost:5557/api/workspace/scan | jq
```

---

## ✅ Next Actions

### RIGHT NOW (VS Code):
1. ✅ Current endpoints documented
2. ⏳ Add error handling to existing endpoints
3. ⏳ Add logging for debugging
4. ⏳ Create test suite

### AFTER UI DESIGN (Desktop Commander):
5. Implement Priority 1 endpoints based on final UI design
6. Test incrementally
7. Integrate with v4 UI

### FINALLY:
8. Performance optimization
9. Security audit
10. Production deployment

---

## 🎯 Decision Point

### What to Work on NOW?

**Option A: Stabilize Current Backend** ⭐ RECOMMENDED
- Add error handling
- Add logging
- Add tests
- Profile performance
- Fix any bugs

**Why:** Solid foundation before building new features

---

**Option B: Design New Endpoints**
- Write endpoint specs
- Plan database schema
- Design API contracts

**Why:** Get architecture right first

---

**Option C: Generate UI Designs First**
- Use Leonardo AI prompts (already created!)
- Get visual design locked in
- Then build backend to match

**Why:** UI drives backend requirements

---

## 💡 My Recommendation

1. **NOW (15 min):** Quick stabilization pass
   - Add try/catch to all endpoints
   - Add basic logging
   - Test manually

2. **DESKTOP COMMANDER (1 hour):** Generate UI designs
   - Use Leonardo AI prompts
   - Create mockups
   - Finalize visual design

3. **BACK TO VS CODE:** Build to spec
   - Implement Priority 1 endpoints
   - Build v4 UI
   - Test integration

---

**Ready to proceed?** Which option do you want to tackle first?
