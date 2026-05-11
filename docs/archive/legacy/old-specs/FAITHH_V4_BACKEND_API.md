# 🔧 FAITHH v4 Backend API Architecture
**Created:** November 9, 2025  
**Version:** 4.0 Backend Design  
**Purpose:** API endpoints and data structures for v4 UI support

---

## 📊 Current Backend Status (v3)

### Existing Endpoints ✅
```python
# Already working in faithh_professional_backend.py

1. GET  /                          # Home/health check
2. GET  /images/<filename>         # Serve image assets
3. POST /api/chat                  # Main chat endpoint
4. POST /api/upload                # File upload
5. POST /api/rag_search            # RAG search
6. GET  /api/status                # System status
7. GET  /api/workspace/scan        # Workspace file scan
8. GET  /health                    # Simple health check
```

---

## 🆕 New Endpoints Needed for v4

### 1. Session Statistics Endpoint

**Purpose:** Track and retrieve session-level metrics for stats panel

```python
@app.route('/api/session/stats', methods=['GET'])
def get_session_stats():
    """
    Returns current session statistics.
    Stats tracked in memory, reset on server restart.
    """
    return jsonify({
        'success': True,
        'stats': {
            'message_count': session_stats['message_count'],
            'token_count': session_stats['total_tokens'],
            'session_start': session_stats['start_time'],  # ISO timestamp
            'session_duration': calculate_duration(),       # seconds
            'avg_response_time': calculate_avg_response(),  # seconds
            'last_activity': session_stats['last_activity'] # ISO timestamp
        }
    })
```

**UI Integration:**
- Called every 5 seconds to update stats panel
- Displayed in right sidebar
- Shows: messages, tokens, session time, avg response

---

### 2. Session Reset Endpoint

**Purpose:** Clear session statistics and start fresh

```python
@app.route('/api/session/reset', methods=['POST'])
def reset_session():
    """
    Resets session statistics to zero.
    Useful for starting new conversation threads.
    """
    session_stats['message_count'] = 0
    session_stats['total_tokens'] = 0
    session_stats['start_time'] = datetime.now().isoformat()
    session_stats['response_times'] = []
    session_stats['last_activity'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'message': 'Session statistics reset'
    })
```

**UI Integration:**
- Triggered by "Clear Chat" button
- Resets all stats to zero
- Keeps backend running

---

### 3. Avatar State Management Endpoint

**Purpose:** Track FAITHH and PULSE avatar states for UI display

```python
@app.route('/api/avatar/state', methods=['GET'])
def get_avatar_state():
    """
    Returns current state of both avatars.
    Used by UI to display status indicators.
    """
    return jsonify({
        'success': True,
        'avatars': {
            'faithh': {
                'status': avatar_state['faithh']['status'],  # online, busy, offline
                'activity': avatar_state['faithh']['activity'],  # idle, thinking, responding
                'last_active': avatar_state['faithh']['last_active']
            },
            'pulse': {
                'status': avatar_state['pulse']['status'],  # online, warning, error
                'activity': avatar_state['pulse']['activity'],  # monitoring, idle
                'metrics': {
                    'cpu_usage': get_cpu_usage(),
                    'memory_usage': get_memory_usage(),
                    'active_connections': count_active_connections()
                }
            }
        }
    })

@app.route('/api/avatar/state', methods=['POST'])
def update_avatar_state():
    """
    Updates avatar state (mainly for testing/manual control).
    In production, this would be set automatically by backend logic.
    """
    data = request.json
    character = data.get('character')  # faithh or pulse
    status = data.get('status')        # online, busy, offline, etc.
    activity = data.get('activity')    # thinking, responding, idle, etc.
    
    if character in ['faithh', 'pulse']:
        avatar_state[character]['status'] = status
        avatar_state[character]['activity'] = activity
        avatar_state[character]['last_active'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'updated': character
    })
```

**UI Integration:**
- Polled every 3 seconds to update avatar status indicators
- FAITHH shows: online (green), busy (yellow), offline (red)
- PULSE shows: system health metrics and status
- Avatar animations change based on activity state

---

### 4. Chat History Endpoint

**Purpose:** Retrieve conversation history for persistence

```python
@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """
    Returns conversation history for current session.
    Limit to last N messages (default: 50).
    """
    limit = request.args.get('limit', 50, type=int)
    
    return jsonify({
        'success': True,
        'messages': chat_history[-limit:],  # Last N messages
        'total_count': len(chat_history)
    })

@app.route('/api/chat/history', methods=['DELETE'])
def clear_chat_history():
    """
    Clears conversation history.
    """
    global chat_history
    chat_history = []
    
    return jsonify({
        'success': True,
        'message': 'Chat history cleared'
    })
```

**Data Structure:**
```python
chat_history = [
    {
        'id': 'msg_123',
        'role': 'user',
        'content': 'User message',
        'timestamp': '2025-11-09T14:23:15Z'
    },
    {
        'id': 'msg_124',
        'role': 'assistant',
        'content': 'FAITHH response',
        'model': 'gemini-2.0-flash-exp',
        'tokens': 245,
        'response_time': 1.8,
        'sources': [...],  # If RAG was used
        'timestamp': '2025-11-09T14:23:17Z'
    }
]
```

**UI Integration:**
- Load history on page load to restore conversation
- Display in chat panel
- Clear with "Clear Chat" button

---

### 5. Model Management Endpoint

**Purpose:** List available models and switch active model

```python
@app.route('/api/models', methods=['GET'])
def get_available_models():
    """
    Returns list of all available AI models.
    Includes Gemini and Ollama models.
    """
    return jsonify({
        'success': True,
        'models': {
            'gemini': {
                'available': [
                    {'id': 'gemini-2.0-flash-exp', 'name': 'Gemini 2.0 Flash', 'status': 'online'},
                    {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'status': 'online'}
                ],
                'default': 'gemini-2.0-flash-exp'
            },
            'ollama': {
                'available': get_ollama_models(),  # Returns list from Ollama API
                'status': 'online' if ollama_available else 'offline'
            }
        },
        'current_model': current_model['name']
    })

@app.route('/api/models/switch', methods=['POST'])
def switch_model():
    """
    Switches active AI model for next response.
    """
    data = request.json
    model_id = data.get('model_id')
    
    # Validate model exists
    if model_id in available_models:
        current_model['name'] = model_id
        current_model['provider'] = determine_provider(model_id)
        
        return jsonify({
            'success': True,
            'current_model': current_model
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Model not found'
        }), 404
```

**UI Integration:**
- Populate model selector dropdown
- Show current model in stats panel
- Disable unavailable models
- Apply selection to next message

---

### 6. Enhanced Status Endpoint

**Purpose:** Expand existing /api/status with more detailed information

```python
@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Enhanced status endpoint with more detailed metrics.
    Already exists but needs expansion for v4.
    """
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'services': {
            'chromadb': {
                'status': 'online' if chromadb_available else 'offline',
                'documents': get_document_count(),
                'collections': get_collection_count(),
                'health': check_chromadb_health()
            },
            'gemini': {
                'status': 'online' if gemini_key else 'offline',
                'model': 'gemini-2.0-flash-exp',
                'rate_limit': check_rate_limit()
            },
            'ollama': {
                'status': 'online' if ollama_available else 'offline',
                'models': get_ollama_model_list(),
                'count': len(get_ollama_model_list())
            }
        },
        'server': {
            'uptime': get_server_uptime(),
            'cpu_usage': get_cpu_usage(),
            'memory_usage': get_memory_usage(),
            'active_sessions': count_active_sessions()
        },
        'workspace': {
            'upload_folder': UPLOAD_FOLDER,
            'uploaded_files': count_uploaded_files()
        }
    })
```

**UI Integration:**
- Polled every 5 seconds for system status panel
- Shows health of all services
- Color-coded indicators (green/yellow/red)
- Expanded view shows detailed metrics

---

## 📝 Data Structures

### Session Statistics (In-Memory)
```python
session_stats = {
    'message_count': 0,
    'total_tokens': 0,
    'start_time': datetime.now().isoformat(),
    'last_activity': datetime.now().isoformat(),
    'response_times': []  # List of response times for avg calculation
}
```

### Avatar State (In-Memory)
```python
avatar_state = {
    'faithh': {
        'status': 'online',      # online, busy, offline
        'activity': 'idle',      # idle, thinking, responding
        'last_active': datetime.now().isoformat()
    },
    'pulse': {
        'status': 'online',      # online, warning, error
        'activity': 'monitoring', # monitoring, idle
        'last_active': datetime.now().isoformat()
    }
}
```

### Current Model State (In-Memory)
```python
current_model = {
    'name': 'gemini-2.0-flash-exp',
    'provider': 'gemini',
    'last_response_time': 0.0,
    'last_tokens': 0
}
```

---

## 🔄 Enhanced /api/chat Endpoint

**Expand existing endpoint to support new features:**

```python
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Enhanced chat endpoint with session tracking.
    Already exists, needs modifications for v4.
    """
    data = request.json
    message = data.get('message', '')
    use_rag = data.get('use_rag', True)
    model = data.get('model', current_model['name'])
    
    # Update avatar state: FAITHH is thinking
    avatar_state['faithh']['status'] = 'busy'
    avatar_state['faithh']['activity'] = 'thinking'
    
    start_time = time.time()
    
    # ... existing chat logic ...
    
    response_time = time.time() - start_time
    
    # Update session stats
    session_stats['message_count'] += 1
    session_stats['total_tokens'] += response_tokens
    session_stats['response_times'].append(response_time)
    session_stats['last_activity'] = datetime.now().isoformat()
    
    # Update current model stats
    current_model['last_response_time'] = response_time
    current_model['last_tokens'] = response_tokens
    
    # Reset avatar state: FAITHH is idle
    avatar_state['faithh']['status'] = 'online'
    avatar_state['faithh']['activity'] = 'idle'
    
    # Add to chat history
    chat_history.append({
        'id': f'msg_{len(chat_history)}',
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    
    chat_history.append({
        'id': f'msg_{len(chat_history)}',
        'role': 'assistant',
        'content': response_text,
        'model': model,
        'tokens': response_tokens,
        'response_time': response_time,
        'sources': sources if use_rag else None,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'success': True,
        'response': response_text,
        'sources': sources if use_rag else None,
        'metadata': {
            'model': model,
            'tokens': response_tokens,
            'response_time': response_time,
            'rag_used': use_rag
        }
    })
```

---

## 🛠️ Implementation Plan

### Phase 1: Add Session Tracking (30 min)
```python
# Add to faithh_professional_backend.py

# Initialize session tracking variables
session_stats = {
    'message_count': 0,
    'total_tokens': 0,
    'start_time': datetime.now().isoformat(),
    'last_activity': datetime.now().isoformat(),
    'response_times': []
}

# Add helper functions
def calculate_duration():
    start = datetime.fromisoformat(session_stats['start_time'])
    return (datetime.now() - start).total_seconds()

def calculate_avg_response():
    times = session_stats['response_times']
    return sum(times) / len(times) if times else 0.0

# Add new endpoint
@app.route('/api/session/stats', methods=['GET'])
def get_session_stats():
    # Implementation from above
    pass
```

### Phase 2: Add Avatar State Management (20 min)
```python
# Initialize avatar state
avatar_state = {
    'faithh': {'status': 'online', 'activity': 'idle', 'last_active': datetime.now().isoformat()},
    'pulse': {'status': 'online', 'activity': 'monitoring', 'last_active': datetime.now().isoformat()}
}

# Add endpoints
@app.route('/api/avatar/state', methods=['GET', 'POST'])
def avatar_state_handler():
    # Implementation from above
    pass
```

### Phase 3: Add Chat History (20 min)
```python
# Initialize history
chat_history = []

# Add endpoints
@app.route('/api/chat/history', methods=['GET', 'DELETE'])
def chat_history_handler():
    # Implementation from above
    pass

# Update /api/chat to add messages to history
```

### Phase 4: Enhance Model Management (30 min)
```python
# Add model listing
@app.route('/api/models', methods=['GET'])
def get_available_models():
    # Implementation from above
    pass

# Add model switching
@app.route('/api/models/switch', methods=['POST'])
def switch_model():
    # Implementation from above
    pass
```

### Phase 5: Enhance Status Endpoint (15 min)
```python
# Expand existing /api/status endpoint
# Add server metrics, uptime, etc.
```

---

## 🧪 Testing Commands

### Test Session Stats
```bash
# Get current stats
curl http://localhost:5557/api/session/stats

# Reset session
curl -X POST http://localhost:5557/api/session/reset
```

### Test Avatar State
```bash
# Get avatar states
curl http://localhost:5557/api/avatar/state

# Update FAITHH state
curl -X POST http://localhost:5557/api/avatar/state \
  -H "Content-Type: application/json" \
  -d '{"character":"faithh","status":"busy","activity":"thinking"}'
```

### Test Chat History
```bash
# Get history
curl http://localhost:5557/api/chat/history

# Get last 10 messages
curl "http://localhost:5557/api/chat/history?limit=10"

# Clear history
curl -X DELETE http://localhost:5557/api/chat/history
```

### Test Models
```bash
# List available models
curl http://localhost:5557/api/models

# Switch to different model
curl -X POST http://localhost:5557/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_id":"llama3.1-8b"}'
```

---

## 🔐 Safety & Rollback

### Before Making Changes
```bash
# 1. Backup current backend
cp faithh_professional_backend.py faithh_professional_backend.py.v3_backup

# 2. Git commit stable state
git add faithh_professional_backend.py
git commit -m "v3 stable - before v4 backend changes"

# 3. Test current backend works
curl http://localhost:5557/api/status
```

### If Something Breaks
```bash
# Quick rollback
cp faithh_professional_backend.py.v3_backup faithh_professional_backend.py

# Restart backend
pkill -f faithh_professional_backend
python faithh_professional_backend.py
```

---

## ✅ Implementation Checklist

### Backend Changes Required:
- [ ] Add session statistics tracking
- [ ] Add session stats endpoint (`/api/session/stats`)
- [ ] Add session reset endpoint (`/api/session/reset`)
- [ ] Add avatar state management
- [ ] Add avatar state endpoints (`/api/avatar/state`)
- [ ] Add chat history storage
- [ ] Add chat history endpoints (`/api/chat/history`)
- [ ] Add model listing endpoint (`/api/models`)
- [ ] Add model switch endpoint (`/api/models/switch`)
- [ ] Enhance status endpoint (`/api/status`)
- [ ] Update chat endpoint to track stats
- [ ] Add helper functions (calculate_duration, etc.)
- [ ] Add error handling for all new endpoints
- [ ] Add logging for debugging
- [ ] Test all endpoints with curl
- [ ] Update CORS settings if needed

---

## 📊 Expected Backend Structure

```python
# faithh_professional_backend.py structure after v4 changes

# Imports
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from datetime import datetime
# ... other imports ...

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# === NEW: Session tracking variables ===
session_stats = {...}
avatar_state = {...}
chat_history = []
current_model = {...}

# === Helper functions ===
def calculate_duration(): pass
def calculate_avg_response(): pass
def get_cpu_usage(): pass
def get_memory_usage(): pass

# === Existing endpoints (keep as-is) ===
@app.route('/')
@app.route('/images/<filename>')
@app.route('/api/chat', methods=['POST'])  # Enhance with tracking
@app.route('/api/upload', methods=['POST'])
@app.route('/api/rag_search', methods=['POST'])
@app.route('/api/status', methods=['GET'])  # Enhance with more data
@app.route('/api/workspace/scan', methods=['GET'])
@app.route('/health')

# === NEW: v4 endpoints ===
@app.route('/api/session/stats', methods=['GET'])
@app.route('/api/session/reset', methods=['POST'])
@app.route('/api/avatar/state', methods=['GET', 'POST'])
@app.route('/api/chat/history', methods=['GET', 'DELETE'])
@app.route('/api/models', methods=['GET'])
@app.route('/api/models/switch', methods=['POST'])

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5557, debug=False)
```

---

## 🎯 Success Criteria

### Backend is v4-ready when:
- ✅ All new endpoints respond without errors
- ✅ Session stats track correctly
- ✅ Avatar states update properly
- ✅ Chat history persists across requests
- ✅ Model switching works
- ✅ Enhanced status shows detailed info
- ✅ v3 features still work (no regressions)
- ✅ Backend doesn't crash under load
- ✅ All endpoints have error handling
- ✅ Logging helps with debugging

---

**Ready for VS Code implementation!**  
Use this document as reference when coding the backend changes.
