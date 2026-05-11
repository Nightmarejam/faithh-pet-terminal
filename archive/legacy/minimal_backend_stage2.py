#!/usr/bin/env python3
"""
Minimal Working Backend - Stage 2
Enhanced with better error handling and logging
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

# Request logging middleware
@app.before_request
def log_request():
    print(f"📥 Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    print(f"📤 Response: {response.status_code} {request.path}")
    return response

# Basic routes with enhanced error handling
@app.route('/')
def home():
    try:
        return jsonify({
            "status": "ok",
            "service": "FAITHH Minimal Backend",
            "stage": "minimal_stage2",
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
            "stage": "minimal_backend_stage2",
            "timestamp": time.time(),
            "config_loaded": True,
            "components": ["flask", "yaml"]
        })
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return jsonify({"error": "Health check failed", "details": str(e)}), 500

@app.route('/api/status')
def status():
    try:
        return jsonify({
            "stage": "minimal_backend_stage2",
            "components": ["flask", "yaml", "config"],
            "status": "running",
            "timestamp": time.time(),
            "config_sections": list(config.keys()) if config else []
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
            "loaded_sections": list(config.keys()) if config else []
        })
    except Exception as e:
        print(f"❌ Config endpoint error: {e}")
        return jsonify({"error": "Config retrieval failed", "details": str(e)}), 500

# Enhanced error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "stage": "minimal_backend_stage2"}), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"❌ Internal error: {error}")
    return jsonify({"error": "Internal server error", "stage": "minimal_backend_stage2"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"❌ Unhandled exception: {e}")
    print(traceback.format_exc())
    return jsonify({"error": "Unhandled exception", "details": str(e)}), 500

# Health check for monitoring
@app.route('/api/health/check')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        return jsonify({
            "status": "healthy",
            "stage": "minimal_backend_stage2",
            "timestamp": time.time(),
            "uptime": time.time(),
            "components": {
                "flask": "ok",
                "yaml": "ok",
                "config": "loaded" if config else "missing"
            }
        })
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return jsonify({"error": "Health check failed", "details": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Minimal Working Backend Stage 2")
    print("✅ Stage: Core Flask + Configuration + Enhanced Error Handling")
    print("📍 Available endpoints:")
    print("   - http://localhost:5557/")
    print("   - http://localhost:5557/health")
    print("   - http://localhost:5557/api/status")
    print("   - http://localhost:5557/api/config")
    print("   - http://localhost:5557/api/health/check")
    
    try:
        app.run(host='0.0.0.0', port=5557, debug=False)
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        print(traceback.format_exc())
        sys.exit(1)
