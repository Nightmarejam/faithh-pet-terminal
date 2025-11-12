#!/usr/bin/env python3
"""
FAITHH Backend Adapter for HTML UI
Connects rag-chat.html to the unified API system
Provides Ollama-compatible endpoints + enhanced features
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
from typing import Dict, Any, Optional
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

# Configuration
UNIFIED_API_URL = "http://localhost:5556"  # Our unified API
OLLAMA_URL = "http://localhost:11434"      # Fallback to Ollama
RAG_API_URL = "http://localhost:5556"      # RAG through unified API

# Model routing configuration
MODEL_ROUTING = {
    'auto': 'gemini',  # Auto-route to Gemini by default
    'llama3.1-8b': 'ollama',
    'qwen2.5-7b': 'ollama',
    'qwen30b-coding': 'ollama',
    'gemini': 'unified',
    'claude-opus': 'claude',  # Future: Claude Opus support
}

# ============= HELPER FUNCTIONS =============

def route_to_unified_api(prompt: str, use_rag: bool = True) -> Dict[str, Any]:
    """Route request to unified API"""
    try:
        response = requests.post(
            f"{UNIFIED_API_URL}/api/chat",
            json={
                'message': prompt,
                'use_rag': use_rag,
                'use_tools': True
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'response': data.get('response', ''),
                'used_rag': data.get('used_rag', False),
                'sources': data.get('rag_sources', []),
                'tools': data.get('tool_results', [])
            }
        else:
            return {'success': False, 'error': f'API error: {response.status_code}'}
    except Exception as e:
        logger.error(f"Unified API error: {e}")
        return {'success': False, 'error': str(e)}

def route_to_ollama(model: str, prompt: str) -> Dict[str, Any]:
    """Route request to Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'response': data.get('response', '')
            }
        else:
            return {'success': False, 'error': f'Ollama error: {response.status_code}'}
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return {'success': False, 'error': str(e)}

# ============= API ENDPOINTS =============

@app.route('/api/generate', methods=['POST'])
def generate():
    """
    Main endpoint - Ollama-compatible format for HTML UI
    Intelligently routes to Unified API (Gemini) or Ollama
    """
    data = request.json
    model = data.get('model', 'auto')
    prompt = data.get('prompt', '')
    stream = data.get('stream', False)  # HTML UI uses stream=false
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    logger.info(f"💬 Generate request: model={model}, prompt={prompt[:50]}...")
    
    # Determine routing
    routing = MODEL_ROUTING.get(model, 'ollama')
    
    if routing == 'unified' or model == 'auto' or model == 'gemini':
        # Route to unified API (Gemini + RAG + Tools)
        logger.info(f"🎯 Routing to Unified API (Gemini)")
        result = route_to_unified_api(prompt, use_rag=True)
        
        if result['success']:
            response_data = {
                'model': 'gemini-flash',
                'response': result['response'],
                'done': True
            }
            
            # Add context info if RAG was used (HTML UI expects this format)
            if result.get('used_rag') and result.get('sources'):
                # Format sources for HTML UI display
                response_data['context'] = [
                    {
                        'text': src['content'],
                        'metadata': src.get('metadata', {}),
                        'score': src.get('score', 0)
                    }
                    for src in result['sources']
                ]
            
            return jsonify(response_data)
        else:
            return jsonify({'error': result.get('error')}), 500
    
    elif routing == 'ollama':
        # Route to Ollama directly
        logger.info(f"🔄 Routing to Ollama: {model}")
        result = route_to_ollama(model, prompt)
        
        if result['success']:
            return jsonify({
                'model': model,
                'response': result['response'],
                'done': True
            })
        else:
            return jsonify({'error': result.get('error')}), 500
    
    elif routing == 'claude':
        # Future: Claude Opus support
        return jsonify({'error': 'Claude support coming soon'}), 501
    
    else:
        return jsonify({'error': f'Unknown routing: {routing}'}), 400

@app.route('/search', methods=['POST'])
def search():
    """
    RAG search endpoint (called by HTML UI when RAG toggle is ON)
    Routes to unified API's RAG system
    """
    data = request.json
    query = data.get('query', '')
    n_results = data.get('n_results', 3)
    
    if not query:
        return jsonify([]), 400
    
    logger.info(f"🔍 RAG search: {query}")
    
    try:
        # Use unified API's RAG
        response = requests.post(
            f"{UNIFIED_API_URL}/api/chat",
            json={
                'message': query,
                'use_rag': True,
                'use_tools': False
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            sources = data.get('rag_sources', [])
            
            # Format for HTML UI
            formatted_sources = [
                {
                    'text': src['content'],
                    'metadata': src.get('metadata', {'filename': 'unknown'}),
                    'score': src.get('score', 0)
                }
                for src in sources[:n_results]
            ]
            
            return jsonify(formatted_sources)
        else:
            return jsonify([]), 500
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        return jsonify([]), 500

@app.route('/api/tags', methods=['GET'])
def list_models():
    """
    List available models (for HTML UI model selector)
    Combines Ollama models + our enhanced models
    """
    models = {
        'models': [
            {'name': 'auto', 'title': '🤖 Auto (Smart Routing)'},
            {'name': 'gemini', 'title': '✨ Gemini Flash (Fast + RAG)'},
            {'name': 'llama3.1-8b', 'title': '💬 Llama 3.1 8B'},
            {'name': 'qwen2.5-7b', 'title': '⚡ Qwen 2.5 7B'},
            {'name': 'qwen30b-coding', 'title': '💻 Qwen 30B Coding'},
            # Future: {'name': 'claude-opus', 'title': '🧠 Claude Opus (Complex)'}
        ]
    }
    
    # Try to get actual Ollama models
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            ollama_models = response.json().get('models', [])
            logger.info(f"✅ Ollama: {len(ollama_models)} models available")
    except:
        logger.warning("⚠️  Could not connect to Ollama")
    
    return jsonify(models)

@app.route('/status', methods=['GET'])
def status():
    """System status check"""
    status_data = {
        'adapter': 'online',
        'unified_api': 'unknown',
        'ollama': 'unknown',
        'rag': 'unknown'
    }
    
    # Check unified API
    try:
        r = requests.get(f"{UNIFIED_API_URL}/api/status", timeout=2)
        if r.status_code == 200:
            status_data['unified_api'] = 'online'
            api_status = r.json()
            status_data['rag'] = api_status.get('services', {}).get('chromadb', 'unknown')
    except:
        pass
    
    # Check Ollama
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            status_data['ollama'] = 'online'
    except:
        pass
    
    return jsonify(status_data)

@app.route('/', methods=['GET'])
def root():
    """API info"""
    return jsonify({
        'name': 'FAITHH Backend Adapter',
        'version': '1.0',
        'description': 'Connects rag-chat.html to unified API system',
        'endpoints': {
            'POST /api/generate': 'Chat (Ollama-compatible)',
            'POST /search': 'RAG search',
            'GET /api/tags': 'List models',
            'GET /status': 'System status'
        },
        'routing': {
            'gemini': 'Unified API (RAG + Tools)',
            'ollama': 'Direct to Ollama',
            'auto': 'Smart routing'
        }
    })

# ============= STARTUP =============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔌 FAITHH Backend Adapter")
    print("="*60)
    print("\n📡 Connecting:")
    print(f"   • HTML UI → This adapter (port 5557)")
    print(f"   • Adapter → Unified API ({UNIFIED_API_URL})")
    print(f"   • Adapter → Ollama ({OLLAMA_URL})")
    print("\n🎯 Routing:")
    print("   • auto/gemini → Unified API (Gemini + RAG + Tools)")
    print("   • llama/qwen → Direct to Ollama")
    print("\n📝 Update HTML UI to use: http://localhost:5557")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5557, debug=True)
