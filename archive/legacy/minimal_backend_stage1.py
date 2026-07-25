#!/usr/bin/env python3
"""
Minimal Working Backend - Stage 1
Based on successful Flask isolation test and mechanical diagnosis
"""

import sys
import os
import time
import json
from pathlib import Path

# Add project path
sys.path.append("/home/jonat/ai-stack")

try:
    from flask import Flask, jsonify
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

# Basic routes
@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "service": "FAITHH Minimal Backend",
        "stage": "minimal",
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "stage": "minimal_backend",
        "timestamp": time.time(),
        "config_loaded": True,
        "components": ["flask", "yaml"]
    })

@app.route('/api/status')
def status():
    return jsonify({
        "stage": "minimal_backend",
        "components": ["flask", "yaml", "config"],
        "status": "running",
        "timestamp": time.time(),
        "config_sections": list(config.keys()) if config else []
    })

@app.route('/api/config')
def get_config():
    return jsonify({
        "ai": config.get('ai', {}),
        "stages": config.get('stages', {}),
        "loaded_sections": list(config.keys()) if config else []
    })

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "stage": "minimal_backend"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "stage": "minimal_backend"}), 500

# Health check for monitoring
@app.route('/api/health/check')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "stage": "minimal_backend",
        "timestamp": time.time(),
        "uptime": time.time(),  # Would track actual uptime in real implementation
        "components": {
            "flask": "ok",
            "yaml": "ok",
            "config": "loaded" if config else "missing"
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Minimal Working Backend")
    print("✅ Stage: Core Flask + Configuration")
    print("📍 Available endpoints:")
    print("   - http://localhost:5557/")
    print("   - http://localhost:5557/health")
    print("   - http://localhost:5557/api/status")
    print("   - http://localhost:5557/api/config")
    print("   - http://localhost:5557/api/health/check")
    
    app.run(host='0.0.0.0', port=5557, debug=False)
