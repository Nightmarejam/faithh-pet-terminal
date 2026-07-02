#!/usr/bin/env python3
"""
FAITHH Lite - Lightweight MacBook Companion
A simplified FAITHH backend for quick queries during audio work.
No ChromaDB, no complex integrations - just Ollama + context files.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1:8b"
FAITHH_DIR = Path(__file__).parent
CONTEXT_DIR = FAITHH_DIR / "context"

# Load context files at startup
def load_context_files():
    """Load key context files into memory"""
    context = {}
    
    if CONTEXT_DIR.exists():
        for file in CONTEXT_DIR.glob("*.md"):
            try:
                content = file.read_text()
                context[file.stem] = content
                print(f"✅ Loaded context: {file.name}")
            except Exception as e:
                print(f"⚠️ Failed to load {file.name}: {e}")
    
    return context

CONTEXT_FILES = {}

# System prompt
SYSTEM_PROMPT = """You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal thought partner.

You help with:
- Floating Garden Soundworks (FGS) audio production business
- Constella civic governance framework development  
- FAITHH AI assistant development
- General productivity and decision-making

Key context about Jonathan:
- Audio producer running boutique mastering label
- Building AI-powered knowledge management system
- Has ADHD - prefers clear, actionable guidance
- Values: dopamine-driven development, structural awareness

Keep responses concise and actionable. You're a companion during work sessions, not a lecturer."""

def build_context_for_query(query):
    """Build relevant context based on query keywords"""
    context_parts = []
    query_lower = query.lower()
    
    # Check which context files are relevant
    keyword_map = {
        'life_map': ['priority', 'focus', 'path', 'direction', 'what should', 'next'],
        'constella': ['constella', 'civic', 'governance', 'token', 'penumbra', 'accord'],
        'audio': ['audio', 'mastering', 'fgs', 'floating garden', 'luna', 'wavelab', 'mix'],
        'faithh': ['faithh', 'backend', 'rag', 'chromadb', 'integration']
    }
    
    for context_name, keywords in keyword_map.items():
        if any(kw in query_lower for kw in keywords):
            if context_name in CONTEXT_FILES:
                context_parts.append(f"=== {context_name.upper()} CONTEXT ===\n{CONTEXT_FILES[context_name][:2000]}")
    
    return "\n\n".join(context_parts) if context_parts else ""

def query_ollama(prompt, context=""):
    """Send query to Ollama"""
    full_prompt = SYSTEM_PROMPT
    
    if context:
        full_prompt += f"\n\n--- RELEVANT CONTEXT ---\n{context}\n--- END CONTEXT ---"
    
    full_prompt += f"\n\nUser: {prompt}\n\nFAITHH:"
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("response", ""),
                "model": MODEL,
                "eval_duration_ms": data.get("eval_duration", 0) / 1_000_000
            }
        else:
            return {"success": False, "error": f"Ollama error: {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Ollama not running. Start with: brew services start ollama"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Routes
@app.route('/')
def index():
    """Serve the UI"""
    return send_from_directory(FAITHH_DIR, 'faithh_lite.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"success": False, "error": "No message provided"})
    
    # Build context
    context = build_context_for_query(message)
    
    # Query Ollama
    result = query_ollama(message, context)
    
    # Add metadata
    result['timestamp'] = datetime.now().isoformat()
    result['context_used'] = bool(context)
    
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def status():
    """Health check"""
    # Check Ollama
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_ok = response.status_code == 200
        models = [m['name'] for m in response.json().get('models', [])] if ollama_ok else []
    except:
        ollama_ok = False
        models = []
    
    return jsonify({
        "status": "ok" if ollama_ok else "degraded",
        "ollama": ollama_ok,
        "model": MODEL,
        "available_models": models,
        "context_files": list(CONTEXT_FILES.keys()),
        "version": "lite-1.0"
    })

@app.route('/api/reload_context', methods=['POST'])
def reload_context():
    """Reload context files"""
    global CONTEXT_FILES
    CONTEXT_FILES = load_context_files()
    return jsonify({
        "success": True,
        "loaded": list(CONTEXT_FILES.keys())
    })

@app.route('/health', methods=['GET'])
def health():
    """Simple health check"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("=" * 50)
    print("FAITHH Lite - MacBook Companion")
    print("=" * 50)
    
    # Load context files
    CONTEXT_FILES = load_context_files()
    print(f"\n📁 Context files loaded: {len(CONTEXT_FILES)}")
    
    # Check Ollama
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if r.status_code == 200:
            print(f"✅ Ollama connected")
            print(f"✅ Model: {MODEL}")
        else:
            print(f"⚠️ Ollama returned status {r.status_code}")
    except:
        print("⚠️ Ollama not running - start with: brew services start ollama")
    
    print(f"\n🚀 Starting server on http://localhost:5557")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5557, debug=False)
