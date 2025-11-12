#!/usr/bin/env python3
"""
FAITHH Backend API - Gemini + Ollama Hybrid
Save as: ~/ai-stack/faithh_api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

# Import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Google Gemini SDK not installed. Run: pip install google-generativeai")

app = Flask(__name__)
CORS(app)

# ============= CONFIGURATION =============
CONFIG = {
    'ollama_url': 'http://localhost:11434',
    'ollama_model': 'qwen2.5-7b',
    'gemini_model': 'gemini-2.0-flash-exp',  # Latest Gemini model
    'default_mode': 'gemini',  # Use Gemini by default
}

# Get Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # API key removed for security

# Initialize Gemini
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(CONFIG['gemini_model'])
        print("✅ Google Gemini initialized")
    except Exception as e:
        gemini_model = None
        print(f"⚠️  Gemini initialization failed: {e}")
else:
    gemini_model = None
    print("⚠️  Gemini not available")

# ============= AI PROVIDERS =============

def chat_ollama(message, model=None):
    """Chat with local Ollama"""
    try:
        model = model or CONFIG['ollama_model']
        response = requests.post(
            f"{CONFIG['ollama_url']}/api/generate",
            json={
                'model': model,
                'prompt': message,
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'response': response.json()['response'],
                'provider': 'ollama',
                'model': model
            }
        else:
            return {
                'success': False,
                'error': f"Ollama error: {response.status_code}"
            }
    except Exception as e:
        return {
            'success': False,
            'error': f"Ollama connection failed: {str(e)}"
        }

def chat_gemini(message):
    """Chat with Google Gemini"""
    if not gemini_model:
        return {
            'success': False,
            'error': 'Gemini not configured'
        }
    
    try:
        response = gemini_model.generate_content(message)
        return {
            'success': True,
            'response': response.text,
            'provider': 'gemini',
            'model': CONFIG['gemini_model']
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Gemini error: {str(e)}"
        }

def smart_route(message):
    """Intelligently route queries"""
    # Try Gemini first (free tier, good quality)
    if gemini_model:
        print(f"🔀 Routing to Gemini")
        return chat_gemini(message)
    else:
        # Fallback to local Ollama
        print(f"🔀 Routing to Ollama (Gemini unavailable)")
        return chat_ollama(message)

# ============= API ENDPOINTS =============

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    message = data.get('message', '')
    mode = data.get('mode', CONFIG['default_mode'])
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    print(f"\n💬 Query: {message[:60]}...")
    print(f"📍 Mode: {mode}")
    
    # Route based on mode
    if mode == 'ollama':
        result = chat_ollama(message)
    elif mode == 'gemini':
        result = chat_gemini(message)
    elif mode == 'auto':
        result = smart_route(message)
    else:
        return jsonify({'error': f'Unknown mode: {mode}'}), 400
    
    if result['success']:
        return jsonify({
            'response': result['response'],
            'provider': result['provider'],
            'model': result['model'],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': result['error']}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """System status endpoint"""
    
    # Check Ollama
    ollama_status = 'offline'
    try:
        r = requests.get(f"{CONFIG['ollama_url']}/api/tags", timeout=2)
        if r.status_code == 200:
            ollama_status = 'online'
    except:
        pass
    
    return jsonify({
        'services': {
            'ollama': ollama_status,
            'gemini': 'online' if gemini_model else 'offline',
        },
        'config': {
            'default_mode': CONFIG['default_mode'],
            'ollama_model': CONFIG['ollama_model'],
            'gemini_model': CONFIG['gemini_model']
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    models = {
        'ollama': [],
        'gemini': ['gemini-1.5-flash', 'gemini-1.5-pro'] if GEMINI_AVAILABLE else []
    }
    
    # Get Ollama models
    try:
        r = requests.get(f"{CONFIG['ollama_url']}/api/tags", timeout=2)
        if r.status_code == 200:
            models['ollama'] = [m['name'] for m in r.json()['models']]
    except:
        pass
    
    return jsonify(models)

@app.route('/api/config', methods=['GET', 'POST'])
def config_endpoint():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify({
            'config': CONFIG,
            'has_gemini_key': bool(GEMINI_API_KEY and GEMINI_API_KEY != '')
        })
    else:
        # Update config
        data = request.json
        for key in ['ollama_model', 'gemini_model', 'default_mode']:
            if key in data:
                CONFIG[key] = data[key]
        return jsonify({'success': True, 'config': CONFIG})

@app.route('/', methods=['GET'])
def root():
    """API info"""
    return jsonify({
        'name': 'FAITHH Backend API',
        'version': '2.1',
        'providers': {
            'ollama': 'available',
            'gemini': 'online' if gemini_model else 'offline'
        },
        'endpoints': [
            'GET  /api/status - System status',
            'POST /api/chat - Chat with AI',
            'GET  /api/models - List models',
            'GET  /api/config - Configuration'
        ]
    })

# ============= STARTUP =============

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🤖 FAITHH Backend API Starting...")
    print("="*50)
    print("\n📡 Available Providers:")
    print(f"   Ollama:  ✅")
    print(f"   Gemini:  {'✅' if gemini_model else '❌ (API key issue)'}")
    print(f"\n🎯 Default Mode: {CONFIG['default_mode']}")
    print("\n📡 Endpoints:")
    print("   GET  /api/status - System status")
    print("   POST /api/chat - Chat with FAITHH")
    print("   GET  /api/models - List models")
    print("\n" + "="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5555, debug=True)