"""
FAITHH Backend v4 - Production Template
Designed to work with faithh_ui_v4.html

This is a template showing the architecture for a clean, scalable backend.
Adapt this to match your existing faithh_professional_backend.py structure.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import chromadb
import google.generativeai as genai
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# CORS configuration
# Development: Allow all origins
# Production: Restrict to your frontend domain
CORS(app, origins=['*'])  # Change to specific domains in production

# Configuration
class Config:
    """Application configuration"""
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # ChromaDB
    CHROMADB_HOST = os.getenv('CHROMADB_HOST', 'localhost')
    CHROMADB_PORT = int(os.getenv('CHROMADB_PORT', '8000'))
    
    # Server
    PORT = int(os.getenv('PORT', '5557'))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Limits
    MAX_MESSAGE_LENGTH = 5000
    MAX_TOKENS = 2000
    RATE_LIMIT = "10 per minute"

# Initialize services
def init_services():
    """Initialize external services"""
    try:
        # Configure Gemini
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            print("✅ Gemini API configured")
        else:
            print("⚠️  GEMINI_API_KEY not found in .env")
        
        # Connect to ChromaDB
        chroma_client = chromadb.HttpClient(
            host=Config.CHROMADB_HOST,
            port=Config.CHROMADB_PORT
        )
        
        # Test connection
        chroma_client.heartbeat()
        print(f"✅ ChromaDB connected at {Config.CHROMADB_HOST}:{Config.CHROMADB_PORT}")
        
        return chroma_client
        
    except Exception as e:
        print(f"❌ Service initialization error: {e}")
        return None

# Global services
chroma_client = init_services()

# In-memory session storage (replace with Redis/DB in production)
sessions = {}

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """API home - shows available endpoints"""
    return jsonify({
        "name": "FAITHH Backend API",
        "version": "4.0",
        "status": "online",
        "endpoints": {
            "GET /": "This page",
            "GET /status": "System status",
            "POST /chat": "Send chat message",
            "POST /search": "Search documents",
            "GET /models": "Available models",
            "GET /history": "Get chat history",
            "POST /history": "Create new session",
            "DELETE /history/<id>": "Delete session"
        }
    })


@app.route('/status', methods=['GET'])
def status():
    """
    Health check endpoint
    
    Returns:
        JSON with system status, ChromaDB info, available models
    """
    try:
        # Check ChromaDB
        chromadb_status = {
            "connected": False,
            "documents": 0,
            "collections": []
        }
        
        if chroma_client:
            try:
                collections = chroma_client.list_collections()
                chromadb_status["connected"] = True
                chromadb_status["collections"] = [col.name for col in collections]
                
                # Get document count from first collection
                if collections:
                    main_collection = chroma_client.get_collection(collections[0].name)
                    chromadb_status["documents"] = main_collection.count()
                    
            except Exception as e:
                print(f"ChromaDB status check error: {e}")
        
        # Available models
        models_available = ["gemini-pro", "gemini-flash"]
        if os.path.exists('/usr/local/bin/ollama'):
            models_available.extend(["ollama-llama2", "ollama-mistral"])
        
        return jsonify({
            "status": "online",
            "version": "4.0",
            "timestamp": datetime.now().isoformat(),
            "chromadb": chromadb_status,
            "models_available": models_available,
            "gemini_configured": bool(Config.GEMINI_API_KEY),
            "active_sessions": len(sessions)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    
    Request body:
        {
            "message": "User message",
            "model": "gemini-pro",
            "use_rag": true,
            "session_id": "optional",
            "max_tokens": 1000
        }
    
    Returns:
        {
            "text": "AI response",
            "tokens": 245,
            "sources": [...],
            "model_used": "gemini-pro",
            "processing_time": 1.2
        }
    """
    start_time = time.time()
    
    try:
        # Parse request
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        message = data.get('message', '').strip()
        model_name = data.get('model', 'gemini-pro')
        use_rag = data.get('use_rag', True)
        session_id = data.get('session_id')
        max_tokens = min(data.get('max_tokens', Config.MAX_TOKENS), Config.MAX_TOKENS)
        
        # Validate message
        if not message:
            return jsonify({"error": "Empty message"}), 400
        
        if len(message) > Config.MAX_MESSAGE_LENGTH:
            return jsonify({
                "error": f"Message too long (max {Config.MAX_MESSAGE_LENGTH} chars)"
            }), 400
        
        # Get RAG context if enabled
        context = ""
        sources = []
        if use_rag and chroma_client:
            context, sources = get_rag_context(message)
        
        # Build prompt
        if context:
            prompt = f"""Context from knowledge base:
{context}

User question: {message}

Please provide a helpful response based on the context above."""
        else:
            prompt = message
        
        # Call AI model
        if not Config.GEMINI_API_KEY:
            return jsonify({
                "error": "GEMINI_API_KEY not configured"
            }), 500
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
            )
        )
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        # Estimate tokens (rough)
        token_count = len(response.text.split()) + len(message.split())
        
        # Store in session if provided
        if session_id:
            if session_id not in sessions:
                sessions[session_id] = {
                    "id": session_id,
                    "created": datetime.now().isoformat(),
                    "messages": []
                }
            
            sessions[session_id]["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            sessions[session_id]["messages"].append({
                "role": "assistant",
                "content": response.text,
                "timestamp": datetime.now().isoformat(),
                "sources": sources
            })
        
        return jsonify({
            "text": response.text,
            "tokens": token_count,
            "sources": sources,
            "model_used": model_name,
            "processing_time": processing_time,
            "rag_used": use_rag and bool(context)
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route('/search', methods=['POST'])
def search():
    """
    RAG search endpoint - query ChromaDB directly
    
    Request body:
        {
            "query": "search term",
            "top_k": 5,
            "filters": {"type": "pdf"}
        }
    
    Returns:
        {
            "results": [...],
            "total_results": 5,
            "query_time": 0.15
        }
    """
    start_time = time.time()
    
    try:
        data = request.json
        query = data.get('query', '').strip()
        top_k = min(data.get('top_k', 5), 20)  # Max 20 results
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        if not chroma_client:
            return jsonify({"error": "ChromaDB not available"}), 503
        
        # Get collection (use first available or specified)
        collections = chroma_client.list_collections()
        if not collections:
            return jsonify({"error": "No collections found"}), 404
        
        collection = chroma_client.get_collection(collections[0].name)
        
        # Perform search
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filters if filters else None
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "document": results['metadatas'][0][i].get('source', 'unknown'),
                "content": results['documents'][0][i][:500],  # Truncate to 500 chars
                "score": round(1 - results['distances'][0][i], 3),  # Convert to similarity
                "metadata": results['metadatas'][0][i]
            })
        
        query_time = round(time.time() - start_time, 3)
        
        return jsonify({
            "results": formatted_results,
            "total_results": len(formatted_results),
            "query_time": query_time,
            "collection": collections[0].name
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            "error": "Search failed",
            "details": str(e)
        }), 500


@app.route('/models', methods=['GET'])
def get_models():
    """
    Get available AI models
    
    Returns:
        {
            "models": [
                {
                    "id": "gemini-pro",
                    "name": "Gemini Pro",
                    "provider": "Google",
                    "capabilities": ["chat", "rag"],
                    "max_tokens": 30000
                }
            ]
        }
    """
    models = [
        {
            "id": "gemini-pro",
            "name": "Gemini Pro",
            "provider": "Google",
            "capabilities": ["chat", "rag", "reasoning"],
            "max_tokens": 30720,
            "available": bool(Config.GEMINI_API_KEY)
        },
        {
            "id": "gemini-flash",
            "name": "Gemini Flash",
            "provider": "Google",
            "capabilities": ["chat", "rag", "fast"],
            "max_tokens": 8192,
            "available": bool(Config.GEMINI_API_KEY)
        }
    ]
    
    # Check for Ollama
    if os.path.exists('/usr/local/bin/ollama'):
        models.extend([
            {
                "id": "ollama-llama2",
                "name": "Llama 2",
                "provider": "Ollama (Local)",
                "capabilities": ["chat"],
                "max_tokens": 4096,
                "available": True
            },
            {
                "id": "ollama-mistral",
                "name": "Mistral",
                "provider": "Ollama (Local)",
                "capabilities": ["chat"],
                "max_tokens": 8192,
                "available": True
            }
        ])
    
    return jsonify({"models": models})


@app.route('/history', methods=['GET'])
def get_history():
    """Get all chat sessions"""
    session_list = [
        {
            "id": sid,
            "title": f"Chat {sid[:8]}",
            "messages": len(data["messages"]),
            "created": data["created"],
            "updated": data["messages"][-1]["timestamp"] if data["messages"] else data["created"]
        }
        for sid, data in sessions.items()
    ]
    
    return jsonify({"sessions": session_list})


@app.route('/history/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific chat session"""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(sessions[session_id])


@app.route('/history', methods=['POST'])
def create_session():
    """Create new chat session"""
    session_id = f"sess_{int(time.time())}_{len(sessions)}"
    sessions[session_id] = {
        "id": session_id,
        "created": datetime.now().isoformat(),
        "messages": []
    }
    
    return jsonify({"session_id": session_id})


@app.route('/history/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete chat session"""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"status": "deleted"})
    
    return jsonify({"error": "Session not found"}), 404


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_rag_context(query, top_k=5):
    """
    Get relevant context from ChromaDB
    
    Args:
        query: User's question
        top_k: Number of documents to retrieve
    
    Returns:
        (context_text, sources_list)
    """
    if not chroma_client:
        return "", []
    
    try:
        # Get collection
        collections = chroma_client.list_collections()
        if not collections:
            return "", []
        
        collection = chroma_client.get_collection(collections[0].name)
        
        # Query ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Build context text
        context_parts = []
        for doc in results['documents'][0]:
            context_parts.append(doc)
        
        context = "\n\n".join(context_parts)
        
        # Build sources list
        sources = []
        for i in range(len(results['documents'][0])):
            sources.append({
                "document": results['metadatas'][0][i].get('source', 'unknown'),
                "relevance": round(1 - results['distances'][0][i], 3),
                "snippet": results['documents'][0][i][:200]  # First 200 chars
            })
        
        return context, sources
        
    except Exception as e:
        print(f"RAG error: {e}")
        return "", []


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("FAITHH Backend v4 - Starting")
    print("=" * 60)
    print(f"Port: {Config.PORT}")
    print(f"Debug: {Config.DEBUG}")
    print(f"Gemini: {'✅' if Config.GEMINI_API_KEY else '❌'}")
    print(f"ChromaDB: {'✅' if chroma_client else '❌'}")
    print("=" * 60)
    print(f"\n🚀 Server starting at http://localhost:{Config.PORT}\n")
    
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )
