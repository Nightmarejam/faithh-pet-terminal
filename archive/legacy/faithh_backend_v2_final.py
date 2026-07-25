#!/usr/bin/env python3
"""
FAITHH Backend v2.0 - Modular Architecture
Clean, maintainable backend with service layer pattern
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
    print("✅ Flask import successful")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

# Import application components
try:
    from app import config
    from app.providers import provider_registry
    from app.services import health_service, chat_service, provider_service
    from app.models import ChatRequest, ChatResponse
    print("✅ Application components imported successfully")
except ImportError as e:
    print(f"❌ Component import failed: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)

# Request logging middleware
@app.before_request
def log_request():
    print(f"📥 Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    print(f"📤 Response: {response.status_code} {request.path}")
    return response

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "service": "faithh_backend_v2"}), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"❌ Internal error: {error}")
    return jsonify({"error": "Internal server error", "service": "faithh_backend_v2"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"❌ Unhandled exception: {e}")
    print(traceback.format_exc())
    return jsonify({"error": "Unhandled exception", "details": str(e)}), 500)

# Basic routes
@app.route('/')
def home():
    try:
        return jsonify({
            "status": "ok",
            "service": "FAITHH Backend v2.0",
            "architecture": "modular_monolith",
            "features": ["flask", "config", "providers", "services"],
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": "Home endpoint failed", "details": str(e)}), 500

@app.route('/health')
def health():
    try:
        health_status = health_service.get_health_status()
        return jsonify({
            "status": health_status.status,
            "stage": "faithh_backend_v2",
            "timestamp": health_status.timestamp,
            "uptime": health_status.uptime,
            "components": health_status.components
        })
    except Exception as e:
        return jsonify({"error": "Health check failed", "details": str(e)}), 500

@app.route('/api/status')
def status():
    try:
        detailed_health = health_service.get_detailed_health()
        return jsonify({
            "stage": "faithh_backend_v2",
            "components": ["flask", "config", "providers", "services"],
            "status": "running",
            "timestamp": time.time(),
            "health": detailed_health
        })
    except Exception as e:
        return jsonify({"error": "Status check failed", "details": str(e)}), 500

@app.route('/api/config')
def get_config():
    try:
        return jsonify({
            "ai": config.get_ai_config(),
            "anthropic": config.get_anthropic_config(),
            "anthropic_models": config.get_anthropic_models(),
            "anthropic_available": config.is_anthropic_available()
        })
    except Exception as e:
        return jsonify({"error": "Config retrieval failed", "details": str(e)}), 500

@app.route('/api/models')
def get_models():
    try:
        models = provider_service.get_available_models()
        return jsonify({
            "models": models,
            "count": len(models),
            "anthropic_available": config.is_anthropic_available()
        })
    except Exception as e:
        return jsonify({"error": "Models retrieval failed", "details": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
async def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        response = await chat_service.process_chat(data)
        
        if response.success:
            return jsonify({
                "success": True,
                "response": response.response,
                "model_used": response.model_used,
                "provider": response.provider,
                "usage": response.usage,
                "timestamp": response.timestamp
            })
        else:
            return jsonify({
                "success": False,
                "error": response.error,
                "provider": response.provider,
                "model_attempted": response.model_used,
                "timestamp": response.timestamp
            }), 500
            
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return jsonify({"error": "Chat processing failed", "details": str(e)}), 500

@app.route('/api/chat/info')
def chat_info():
    try:
        return jsonify(chat_service.get_chat_info())
    except Exception as e:
        return jsonify({"error": "Chat info retrieval failed", "details": str(e)}), 500

@app.route('/api/providers')
def providers():
    try:
        return jsonify(provider_service.get_provider_status())
    except Exception as e:
        return jsonify({"error": "Provider status failed", "details": str(e)}), 500)

@app.route('/api/health/check')
def health_check():
    """Comprehensive health check endpoint"""
    try:
        return jsonify(health_service.get_detailed_health())
    except Exception as e:
        return jsonify({"error": "Health check failed", "details": str(e)}), 500)

if __name__ == '__main__':
    print("🚀 Starting FAITHH Backend v2.0")
    print("✅ Architecture: Modular Monolith with Service Layer")
    print("✅ Components: Flask + Config + Providers + Services")
    print(f"✅ Config loaded: {len(config.config._config)} sections")
    print(f"✅ Providers registered: {len(provider_registry._providers)}")
    print(f"✅ Anthropic available: {config.is_anthropic_available()}")
    
    print("📍 Available endpoints:")
    print("   - http://localhost:5557/")
    print("   - http://localhost:5557/health")
    print("   - http://localhost:5557/api/status")
    print("   - http://localhost:5557/api/config")
    print("   - http://localhost:5557/api/models")
    print("   - http://localhost:5557/api/chat")
    print("   - http://localhost:5557/api/providers")
    print("   - http://localhost:5557/api/health/check")
    
    try:
        app.run(host='0.0.0.0', port=5557, debug=False)
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        print(traceback.format_exc())
        sys.exit(1)