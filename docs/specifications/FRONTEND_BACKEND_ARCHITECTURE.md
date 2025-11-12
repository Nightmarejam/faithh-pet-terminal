# FAITHH UI v4 - Frontend-Backend Architecture

**Date:** 2025-11-09  
**Version:** 4.0  
**Focus:** Clean separation, modular design, scalable API

---

## Overview

The FAITHH UI v4 implements a modern, three-panel interface with clean backend integration through a RESTful API architecture. This document explains how the frontend and backend communicate.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Frontend)                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Sidebar    │  │  Main Chat   │  │   Context    │     │
│  │  (History)   │  │   (Messages) │  │   (Stats)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                           │                                  │
│                           │ HTTP/JSON                        │
│                           ▼                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            │ REST API
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                  Backend (Flask/FastAPI)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Endpoints Layer                      │  │
│  │  /chat, /search, /status, /models, /history          │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌─────────────────▼────────────────────────────────────┐  │
│  │            Business Logic Layer                       │  │
│  │  - Message handling    - RAG integration              │  │
│  │  - Model selection     - Context management           │  │
│  └─────────────────┬────────────────────────────────────┘  │
│                     │                                        │
│  ┌─────────────────▼────────────────────────────────────┐  │
│  │              Data Layer                               │  │
│  │  - ChromaDB       - Chat history                      │  │
│  │  - Gemini API     - Session storage                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### 1. Chat Endpoint
**Purpose:** Send messages and receive AI responses

**Request:**
```javascript
POST /chat
Content-Type: application/json

{
    "message": "What is machine learning?",
    "model": "gemini-pro",
    "use_rag": true,
    "session_id": "abc123",
    "max_tokens": 1000
}
```

**Response:**
```javascript
{
    "text": "Machine learning is...",
    "tokens": 245,
    "sources": [
        {
            "document": "ML_Fundamentals.pdf",
            "relevance": 0.92,
            "snippet": "..."
        }
    ],
    "model_used": "gemini-pro",
    "processing_time": 1.2
}
```

**Frontend Implementation:**
```javascript
async callBackend(message) {
    const response = await fetch(`${this.config.backendUrl}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            model: this.state.currentModel,
            use_rag: true
        })
    });
    return await response.json();
}
```

---

### 2. Status Endpoint
**Purpose:** Check backend health and configuration

**Request:**
```javascript
GET /status
```

**Response:**
```javascript
{
    "status": "online",
    "version": "4.0",
    "chromadb": {
        "connected": true,
        "documents": 91302,
        "collections": ["main_docs"]
    },
    "models_available": ["gemini-pro", "gemini-flash"],
    "uptime": 3600
}
```

**Frontend Implementation:**
```javascript
async checkBackendStatus() {
    const response = await fetch(`${this.config.backendUrl}/status`);
    if (response.ok) {
        const data = await response.json();
        this.updateStatus('connected', 'Connected');
        return data;
    }
}
```

---

### 3. Search Endpoint
**Purpose:** Query ChromaDB directly without AI response

**Request:**
```javascript
POST /search
Content-Type: application/json

{
    "query": "neural networks",
    "top_k": 5,
    "filters": {
        "type": "pdf"
    }
}
```

**Response:**
```javascript
{
    "results": [
        {
            "document": "Neural_Networks_101.pdf",
            "content": "Neural networks are...",
            "score": 0.94,
            "metadata": {
                "page": 3,
                "date": "2024-01-15"
            }
        }
    ],
    "total_results": 23,
    "query_time": 0.15
}
```

---

### 4. Models Endpoint
**Purpose:** Get available AI models

**Request:**
```javascript
GET /models
```

**Response:**
```javascript
{
    "models": [
        {
            "id": "gemini-pro",
            "name": "Gemini Pro",
            "provider": "Google",
            "capabilities": ["chat", "rag"],
            "max_tokens": 30000
        },
        {
            "id": "ollama-llama2",
            "name": "Llama 2",
            "provider": "Ollama (Local)",
            "capabilities": ["chat"],
            "max_tokens": 4096
        }
    ]
}
```

---

### 5. History Endpoint
**Purpose:** Manage chat sessions

**Request:**
```javascript
GET /history
GET /history/{session_id}
POST /history (create new)
DELETE /history/{session_id}
```

**Response:**
```javascript
{
    "sessions": [
        {
            "id": "abc123",
            "title": "Machine Learning Discussion",
            "messages": 12,
            "created": "2025-11-09T10:00:00Z",
            "updated": "2025-11-09T10:30:00Z"
        }
    ]
}
```

---

## Frontend State Management

### App State Structure
```javascript
const app = {
    config: {
        backendUrl: 'http://localhost:5557',
        endpoints: {
            chat: '/chat',
            search: '/search',
            status: '/status',
            models: '/models'
        }
    },
    state: {
        messages: [],              // Current conversation
        messageCount: 0,           // Total messages sent
        tokenCount: 0,             // Total tokens used
        sessionStart: new Date(),  // Session start time
        currentModel: 'gemini-pro', // Selected model
        isProcessing: false        // Busy state
    }
}
```

### Message Flow
```
1. User types message
   ├─> Input captured in textarea
   └─> Enter key or Send button click

2. Frontend validates
   ├─> Check if message is not empty
   ├─> Check if not already processing
   └─> Proceed if valid

3. UI updates
   ├─> Add user message to chat
   ├─> Show loading animation
   └─> Disable input/send button

4. Backend call
   ├─> POST request to /chat endpoint
   ├─> Include message, model, settings
   └─> Wait for response

5. Response handling
   ├─> Remove loading animation
   ├─> Add assistant response to chat
   ├─> Update statistics
   └─> Re-enable input

6. Error handling (if backend fails)
   ├─> Show error message
   ├─> Log to console
   └─> Re-enable input
```

---

## Backend Requirements

### Minimal Backend Structure

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Initialize services
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    try:
        collection = chroma_client.get_collection("main_docs")
        doc_count = collection.count()
        
        return jsonify({
            "status": "online",
            "version": "4.0",
            "chromadb": {
                "connected": True,
                "documents": doc_count
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    message = data.get('message')
    model_name = data.get('model', 'gemini-pro')
    use_rag = data.get('use_rag', True)
    
    try:
        # Get RAG context if enabled
        context = ""
        sources = []
        if use_rag:
            context, sources = get_rag_context(message)
        
        # Call AI model
        model = genai.GenerativeModel(model_name)
        prompt = f"{context}\n\nUser: {message}"
        response = model.generate_content(prompt)
        
        return jsonify({
            "text": response.text,
            "tokens": len(response.text.split()),  # Rough estimate
            "sources": sources,
            "model_used": model_name
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/search', methods=['POST'])
def search():
    """RAG search endpoint"""
    data = request.json
    query = data.get('query')
    top_k = data.get('top_k', 5)
    
    try:
        collection = chroma_client.get_collection("main_docs")
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "document": results['metadatas'][0][i].get('source', 'unknown'),
                "content": results['documents'][0][i],
                "score": results['distances'][0][i]
            })
        
        return jsonify({
            "results": formatted_results,
            "total_results": len(formatted_results)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

def get_rag_context(query, top_k=5):
    """Helper function to get RAG context"""
    collection = chroma_client.get_collection("main_docs")
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    context = "\n\n".join(results['documents'][0])
    sources = [
        {
            "document": meta.get('source', 'unknown'),
            "relevance": 1 - dist  # Convert distance to relevance score
        }
        for meta, dist in zip(results['metadatas'][0], results['distances'][0])
    ]
    
    return context, sources

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5557, debug=True)
```

---

## CORS Configuration

**Why CORS is needed:**
- Browser security prevents frontend (HTML file) from calling backend API on different origin
- Must be configured on backend

**Flask CORS setup:**
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable all origins

# OR restrict to specific origins:
CORS(app, origins=['http://localhost:8080', 'http://127.0.0.1:8080'])
```

---

## Error Handling

### Frontend Error Handling
```javascript
try {
    const response = await fetch(`${this.config.backendUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, model: this.state.currentModel })
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
    
} catch (error) {
    console.error('Backend error:', error);
    
    // Fallback to mock response for development
    return {
        text: "Backend unavailable. This is a mock response.",
        tokens: 0,
        sources: []
    };
}
```

### Backend Error Handling
```python
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Main logic here
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400
        
    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500
```

---

## Security Considerations

### 1. API Key Protection
- ✅ Store in .env file (backend)
- ✅ Never expose to frontend
- ✅ Use environment variables

### 2. Input Validation
- Validate message length
- Sanitize user input
- Check for injection attacks

### 3. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # Handle chat
```

### 4. CORS Restrictions
- Only allow trusted origins in production
- Don't use wildcard (*) in production

---

## Testing the Connection

### 1. Start Backend
```bash
cd ~/ai-stack
source venv/bin/activate
python backend/faithh_professional_backend.py
```

### 2. Open Frontend
```bash
# Simple HTTP server
cd ~/ai-stack/frontend/html
python -m http.server 8080

# Then open: http://localhost:8080/faithh_ui_v4.html
```

### 3. Test Connection
- Open browser console (F12)
- Look for "✅ Backend connected" message
- Send a test message
- Check console for API calls

### 4. Debug Issues
```javascript
// In browser console:
fetch('http://localhost:5557/status')
    .then(r => r.json())
    .then(d => console.log('Backend status:', d))
    .catch(e => console.error('Connection failed:', e))
```

---

## Development Workflow

### 1. Frontend Development
```bash
# Work on UI without backend
# UI gracefully falls back to mock responses
# Focus on design, interactions, styling
```

### 2. Backend Development
```bash
# Test endpoints independently
# Use tools like Postman or curl
curl -X POST http://localhost:5557/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### 3. Integration Testing
```bash
# Run both services
# Test full message flow
# Verify error handling
```

---

## Deployment Considerations

### Development
- Frontend: Local HTTP server
- Backend: Flask development server (port 5557)
- CORS: Wide open for testing

### Production
- Frontend: Static hosting (Nginx, S3, Vercel)
- Backend: Production WSGI server (Gunicorn, uWSGI)
- CORS: Restricted to frontend domain
- HTTPS: Required for security
- Rate limiting: Prevent abuse
- Authentication: API keys, JWT tokens

---

## Next Steps

### Week 2 Enhancements
1. **Add chat history persistence** (SQLite or JSON files)
2. **Implement source display** in UI when RAG is used
3. **Add model comparison view** (side-by-side responses)
4. **Create settings panel** (temperature, max tokens, etc.)
5. **Add export functionality** (download chats as MD/PDF)

### Week 3+ Features
1. **File upload for documents**
2. **Real-time streaming responses**
3. **Multi-modal support** (images, audio)
4. **Collaborative sessions**
5. **Custom agent creation UI**

---

## Summary

**Key Principles:**
- ✅ Clean separation of concerns
- ✅ RESTful API design
- ✅ Graceful error handling
- ✅ Security by default
- ✅ Easy to test and debug

**Connection Pattern:**
```
Frontend (HTML/JS) 
  ↓ HTTP/JSON
Backend (Flask/Python)
  ↓ API Calls
Services (ChromaDB, Gemini)
```

**Status:** Ready for Week 2 implementation!

---

*Created: 2025-11-09*  
*Version: 1.0*  
*Author: FAITHH Development Team*
