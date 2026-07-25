#!/usr/bin/env python3
"""
FAITHH Backend API with WebSocket Tool Execution
Combines Gemini/Ollama chat with real-time tool execution
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sock import Sock
import requests
import os
import json
import asyncio
from datetime import datetime

# Import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import our tool system
from tool_executor import get_executor
from tool_registry import get_registry
from executors.filesystem import FilesystemExecutor
from executors.process import ProcessExecutor

app = Flask(__name__)
CORS(app)
sock = Sock(app)  # WebSocket support

# ============= CONFIGURATION =============
CONFIG = {
    'ollama_url': 'http://localhost:11434',
    'ollama_model': 'qwen2.5-7b',
    'gemini_model': 'gemini-2.0-flash-exp',
    'default_mode': 'gemini',
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

# Initialize tool system
tool_executor = get_executor()
tool_registry = get_registry()

# Register executors
tool_executor.register_executor('filesystem', FilesystemExecutor())
tool_executor.register_executor('process', ProcessExecutor())

# Register basic tools
tool_registry.register_tool({
    'name': 'read_file',
    'description': 'Read file contents',
    'category': 'filesystem',
    'executor': 'filesystem',
    'permissions': ['file.read']
})

print("✅ Tool system initialized")

# ============= WEBSOCKET ENDPOINT =============

@sock.route('/ws/tools')
def websocket_tools(ws):
    """WebSocket endpoint for real-time tool execution"""
    print("🔌 WebSocket client connected")
    
    try:
        while True:
            # Receive message from client
            message = ws.receive()
            if not message:
                break
            
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'execute_tool':
                # Execute tool request
                tool_name = data.get('tool_name')
                parameters = data.get('parameters', {})
                permissions = data.get('permissions')
                
                # Send acknowledgment
                ws.send(json.dumps({
                    'type': 'status',
                    'message': f'Executing {tool_name}...'
                }))
                
                # Execute tool asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    tool_executor.execute_tool(tool_name, parameters, permissions)
                )
                loop.close()
                
                # Send result
                ws.send(json.dumps({
                    'type': 'result',
                    'data': result
                }))
                
            elif action == 'list_tools':
                # List available tools
                tools = tool_registry.list_tools()
                ws.send(json.dumps({
                    'type': 'tools_list',
                    'tools': tools
                }))
            
            elif action == 'ping':
                ws.send(json.dumps({'type': 'pong'}))
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws.send(json.dumps({
            'type': 'error',
            'message': str(e)
        }))
    finally:
        print("🔌 WebSocket client disconnected")

# ============= HTTP ENDPOINTS (from original) =============

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint (Gemini/Ollama)"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Use Gemini
    if gemini_model:
        try:
            response = gemini_model.generate_content(message)
            return jsonify({
                'response': response.text,
                'provider': 'gemini',
                'model': CONFIG['gemini_model'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': f'Gemini error: {str(e)}'}), 500
    else:
        return jsonify({'error': 'No AI provider available'}), 503

@app.route('/api/status', methods=['GET'])
def status():
    """System status"""
    return jsonify({
        'services': {
            'gemini': 'online' if gemini_model else 'offline',
            'tools': 'online',
            'websocket': 'online'
        },
        'executors': list(tool_executor.executors.keys()),
        'tool_count': len(tool_registry.list_tools()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def root():
    """API info"""
    return jsonify({
        'name': 'FAITHH Backend API',
        'version': '3.0',
        'features': ['chat', 'tool_execution', 'websocket'],
        'endpoints': {
            'http': [
                'GET  /api/status - System status',
                'POST /api/chat - Chat with AI',
            ],
            'websocket': [
                'WS   /ws/tools - Real-time tool execution'
            ]
        }
    })

# ============= STARTUP =============

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🤖 FAITHH Backend API v3.0 Starting...")
    print("="*50)
    print("\n✨ Features:")
    print("   • Gemini AI Chat")
    print("   • Tool Execution System")
    print("   • WebSocket Streaming")
    print(f"\n🔧 Executors: {list(tool_executor.executors.keys())}")
    print(f"🔨 Tools: {len(tool_registry.list_tools())} registered")
    print("\n📡 Endpoints:")
    print("   HTTP:      http://localhost:5555")
    print("   WebSocket: ws://localhost:5555/ws/tools")
    print("\n" + "="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5555, debug=True)
