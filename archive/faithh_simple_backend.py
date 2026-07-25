#!/usr/bin/env python3
"""
FAITHH Simple Backend API
A lightweight backend to connect faithh_pet_v3.html to AI services
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

# Configuration
OLLAMA_HOST = "http://localhost:11434"
CHROMA_HOST = "http://localhost:8000"

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent

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
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        
        # For now, use Ollama for chat
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": message,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated')
            })
        else:
            # Fallback response if Ollama is down
            return jsonify({
                'success': True,
                'response': f"[System Notice] Backend connecting... Your message: '{message}' was received. Services are being initialized."
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f"Error processing request: {str(e)}"
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
    try:
        r = requests.get(f"{CHROMA_HOST}/api/v1", timeout=1)
        services['chromadb'] = 'online' if r.status_code == 200 else 'offline'
    except:
        services['chromadb'] = 'offline'
    
    # Check for Gemini (placeholder)
    services['gemini'] = 'configured' if os.environ.get('GEMINI_API_KEY') else 'not configured'
    
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
    if os.environ.get('GEMINI_API_KEY'):
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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'FAITHH Backend'})

if __name__ == '__main__':
    print("=" * 60)
    print("FAITHH SIMPLE BACKEND")
    print("=" * 60)
    print(f"Starting server on http://localhost:5557")
    print(f"HTML UI will be available at http://localhost:5557")
    print("=" * 60)
    
    # Run the server
    app.run(host='0.0.0.0', port=5557, debug=True)
