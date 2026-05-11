#!/usr/bin/env python3
"""
Minimal Working Backend - Stage 3
Add Anthropic API integration with fixed message format
"""

import sys
import os
import time
import json
import traceback
from pathlib import Path

# Add project path
sys.path.append("/home/jonat/ai-stack")

try:
    from flask import Flask, jsonify, request
    import yaml
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)

# Load configuration
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("✅ Configuration loaded")
except Exception as e:
    print(f"❌ Config loading failed: {e}")
    config = {}

# Anthropic configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
ANTHROPIC_DEFAULT_MODEL = config.get('ai', {}).get('anthropic', {}).get('default_model', 'claude-3-haiku-20240307')
ANTHROPIC_BACKUP_MODEL = config.get('ai', {}).get('anthropic', {}).get('backup_model', 'claude-3-haiku-20240307')

# Request logging middleware
@app.before_request
def log_request():
    print(f"📥 Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    print(f"📤 Response: {response.status_code} {request.path}")
    return response

# Basic routes
@app.route('/')
def home():
    try:
        return jsonify({
            "status": "ok",
            "service": "FAITHH Minimal Backend",
            "stage": "minimal_stage3",
            "features": ["flask", "yaml", "config", "anthropic"],
            "timestamp": time.time()
        })
    except Exception as e:
        print(f"❌ Home endpoint error: {e}")
        return jsonify({"error": "Internal error", "details": str(e)}), 500

@app.route('/health')
def health():
    try:
        return jsonify({
            "status": "ok",
            "stage": "minimal_backend_stage3",
            "timestamp": time.time(),
            "config_loaded": True,
            "anthropic_available": bool(ANTHROPIC_API_KEY),
            "components": ["flask", "yaml", "anthropic"]
        })
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return jsonify({"error": "Health check failed", "details": str(e)}), 500

@app.route('/api/status')
def status():
    try:
        return jsonify({
            "stage": "minimal_backend_stage3",
            "components": ["flask", "yaml", "config", "anthropic"],
            "status": "running",
            "timestamp": time.time(),
            "config_sections": list(config.keys()) if config else [],
            "anthropic_configured": bool(ANTHROPIC_API_KEY),
            "anthropic_model": ANTHROPIC_DEFAULT_MODEL
        })
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return jsonify({"error": "Status check failed", "details": str(e)}), 500

@app.route('/api/config')
def get_config():
    try:
        return jsonify({
            "ai": config.get('ai', {}),
            "stages": config.get('stages', {}),
            "loaded_sections": list(config.keys()) if config else [],
            "anthropic": {
                "configured": bool(ANTHROPIC_API_KEY),
                "default_model": ANTHROPIC_DEFAULT_MODEL,
                "backup_model": ANTHROPIC_BACKUP_MODEL
            }
        })
    except Exception as e:
        print(f"❌ Config endpoint error: {e}")
        return jsonify({"error": "Config retrieval failed", "details": str(e)}), 500

# Anthropic chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Missing message in request"}), 400
        
        message = data.get('message', '')
        provider = data.get('provider', 'anthropic')
        model = data.get('model', ANTHROPIC_DEFAULT_MODEL)
        
        print(f"🤖 Chat request: provider={provider}, model={model}")
        
        if provider == 'anthropic':
            return handle_anthropic_chat(message, model)
        else:
            return jsonify({"error": f"Provider {provider} not yet implemented"}), 400
            
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return jsonify({"error": "Chat processing failed", "details": str(e)}), 500

def handle_anthropic_chat(message, model):
    """Handle Anthropic chat with fixed message format"""
    try:
        if not ANTHROPIC_API_KEY:
            return jsonify({
                "error": "ANTHROPIC_API_KEY not configured",
                "provider": "anthropic",
                "model_attempted": model
            }), 501
        
        # Import Anthropic provider
        from backend.llm_providers import call_anthropic_chat
        
        # Create properly formatted messages (FIXED FORMAT)
        messages = [{"role": "user", "content": message}]
        
        print(f"   🔧 Calling Anthropic with model: {model}")
        
        # Call Anthropic API
        assistant_response, usage, api_data = call_anthropic_chat(
            messages=messages,
            model=model,
            max_tokens=1000,
            temperature=0.1,
            timeout_s=60,
            api_key=ANTHROPIC_API_KEY
        )
        
        print(f"   ✅ Anthropic response received: {len(assistant_response)} chars")
        
        return jsonify({
            "success": True,
            "response": assistant_response,
            "model_used": model,
            "provider": "anthropic",
            "usage": usage,
            "timestamp": time.time()
        })
        
    except Exception as e:
        print(f"❌ Anthropic chat error: {e}")
        return jsonify({
            "success": False,
            "error": f"Anthropic API error: {e}",
            "provider": "anthropic",
            "model_attempted": model,
            "timestamp": time.time()
        }), 502

# Model selection endpoint
@app.route('/api/models')
def get_models():
    try:
        models = [
            {"name": "qwen25-grounded:latest", "provider": "ollama"},
        ]
        
        if ANTHROPIC_API_KEY:
            models.extend([
                {"name": ANTHROPIC_DEFAULT_MODEL, "provider": "anthropic"},
                {"name": ANTHROPIC_BACKUP_MODEL, "provider": "anthropic"},
            ])
        
        return jsonify({
            "models": models,
            "count": len(models),
            "anthropic_available": bool(ANTHROPIC_API_KEY)
        })
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return jsonify({"error": "Models retrieval failed", "details": str(e)}), 500

# Enhanced error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "stage": "minimal_backend_stage3"}), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"❌ Internal error: {error}")
    return jsonify({"error": "Internal server error", "stage": "minimal_backend_stage3"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"❌ Unhandled exception: {e}")
    print(traceback.format_exc())
    return jsonify({"error": "Unhandled exception", "details": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Minimal Working Backend Stage 3")
    print("✅ Stage: Core Flask + Configuration + Anthropic Integration")
    print(f"✅ Anthropic API Key: {'Configured' if ANTHROPIC_API_KEY else 'Not configured'}")
    print(f"✅ Anthropic Model: {ANTHROPIC_DEFAULT_MODEL}")
    print("📍 Available endpoints:")
    print("   - http://localhost:5557/")
    print("   - http://localhost:5557/health")
    print("   - http://localhost:5557/api/status")
    print("   - http://localhost:5557/api/config")
    print("   - http://localhost:5557/api/models")
    print("   - http://localhost:5557/api/chat")
    
    try:
        app.run(host='0.0.0.0', port=5557, debug=False)
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        print(traceback.format_exc())
        sys.exit(1)
