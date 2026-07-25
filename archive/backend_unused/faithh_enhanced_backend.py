#!/usr/bin/env python3
"""
FAITHH Enhanced Backend API v2
Connects faithh_pet_v3.html to AI services with ChromaDB and Gemini
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from pathlib import Path
import chromadb
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

# Configuration
OLLAMA_HOST = "http://localhost:11434"
CHROMA_HOST = "http://localhost:8000"
CHROMA_COLLECTION = "documents"  # Your 91k documents collection

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent

# Initialize ChromaDB client
try:
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    collection = chroma_client.get_collection(name=CHROMA_COLLECTION)
    CHROMA_CONNECTED = True
    print(f"✅ ChromaDB connected: {collection.count()} documents available")
except Exception as e:
    CHROMA_CONNECTED = False
    collection = None
    print(f"⚠️ ChromaDB not connected: {e}")

# Check for Gemini API key
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

if GEMINI_AVAILABLE:
    print("✅ Gemini API key detected")
else:
    print("⚠️ Gemini API key not found in environment")

@app.route('/')
def index():
    """Serve the HTML UI"""
    return send_from_directory(BASE_DIR, 'faithh_pet_v3.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images for the UI"""
    images_dir = BASE_DIR / 'images'
    return send_from_directory(images_dir, filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with multiple AI providers"""
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', False)
        
        context = ""
        
        # If RAG is enabled, search ChromaDB
        if use_rag and CHROMA_CONNECTED:
            try:
                results = collection.query(
                    query_texts=[message],
                    n_results=3
                )
                if results['documents']:
                    context = "\n\nRelevant context:\n"
                    for doc in results['documents'][0]:
                        context += f"- {doc[:200]}...\n"
            except Exception as e:
                print(f"RAG search error: {e}")
        
        # Prepare the prompt with context
        full_prompt = f"{context}\n\nUser: {message}" if context else message
        
        # Try Gemini first if available and selected
        if GEMINI_AVAILABLE and 'gemini' in model.lower():
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = gemini_model.generate_content(full_prompt)
                
                return jsonify({
                    'success': True,
                    'response': response.text,
                    'model_used': 'gemini-2.0-flash-exp',
                    'rag_used': use_rag and bool(context)
                })
            except Exception as e:
                print(f"Gemini error, falling back to Ollama: {e}")
        
        # Use Ollama
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),
                'model_used': model,
                'rag_used': use_rag and bool(context)
            })
        else:
            return jsonify({
                'success': True,
                'response': f"[System Notice] Processing your message: '{message}'",
                'model_used': 'system',
                'rag_used': False
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f"Error processing request: {str(e)}"
        }), 500

@app.route('/api/rag_search', methods=['POST'])
def rag_search():
    """Search the RAG database directly"""
    if not CHROMA_CONNECTED:
        return jsonify({
            'success': False,
            'error': 'ChromaDB not connected'
        }), 503
    
    try:
        data = request.json
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return jsonify({
            'success': True,
            'results': results['documents'][0] if results['documents'] else [],
            'distances': results['distances'][0] if results['distances'] else [],
            'total_documents': collection.count()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Check status of services"""
    services = {}
    
    # Check Ollama
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/version", timeout=1)
        services['ollama'] = 'online' if r.status_code == 200 else 'offline'
    except:
        services['ollama'] = 'offline'
    
    # Check ChromaDB
    services['chromadb'] = 'online' if CHROMA_CONNECTED else 'offline'
    if CHROMA_CONNECTED:
        services['chromadb'] += f" ({collection.count()} docs)"
    
    # Check Gemini
    services['gemini'] = 'configured' if GEMINI_AVAILABLE else 'not configured'
    
    return jsonify({
        'success': True,
        'services': services
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    models = []
    
    try:
        # Get Ollama models
        r = requests.get(f"{OLLAMA_HOST}/api/tags")
        if r.status_code == 200:
            data = r.json()
            for model in data.get('models', []):
                models.append({
                    'name': model['name'],
                    'provider': 'ollama',
                    'size': model.get('size', 'unknown')
                })
    except:
        pass
    
    # Add Gemini if configured
    if GEMINI_AVAILABLE:
        models.append({
            'name': 'gemini-2.0-flash-exp',
            'provider': 'gemini',
            'size': 'cloud'
        })
    
    # Default model if none available
    if not models:
        models.append({
            'name': 'system',
            'provider': 'local',
            'size': 'mock'
        })
    
    return jsonify({
        'success': True,
        'models': models
    })

@app.route('/api/update_context', methods=['POST'])
def update_context():
    """Update the MASTER_CONTEXT.md with new information"""
    try:
        data = request.json
        update_type = data.get('type', 'general')
        content = data.get('content', '')
        
        context_file = BASE_DIR / 'MASTER_CONTEXT.md'
        
        # Read current context
        with open(context_file, 'r') as f:
            current_content = f.read()
        
        # Find the last updated line and update it
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_update = f"\n\n## Update: {timestamp}\n**Type**: {update_type}\n{content}\n"
        
        # Insert the update after the header
        lines = current_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('**Last Updated**:'):
                lines[i] = f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}"
                break
        
        # Add the new update
        updated_content = '\n'.join(lines) + new_update
        
        # Write back
        with open(context_file, 'w') as f:
            f.write(updated_content)
        
        return jsonify({
            'success': True,
            'message': 'Context updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FAITHH Enhanced Backend',
        'chromadb': CHROMA_CONNECTED,
        'gemini': GEMINI_AVAILABLE
    })

if __name__ == '__main__':
    print("=" * 60)
    print("FAITHH ENHANCED BACKEND v2")
    print("=" * 60)
    print(f"Starting server on http://localhost:5557")
    print(f"HTML UI: http://localhost:5557")
    print(f"ChromaDB: {'✅ Connected' if CHROMA_CONNECTED else '❌ Not connected'}")
    print(f"Gemini: {'✅ Available' if GEMINI_AVAILABLE else '❌ Not configured'}")
    print("=" * 60)
    
    # Run the server
    app.run(host='0.0.0.0', port=5557, debug=True)
