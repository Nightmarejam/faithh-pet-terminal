#!/usr/bin/env python3
"""
Test Flask in isolation to identify startup issues
"""

import sys
import os
import subprocess
import time
import requests
import socket
from pathlib import Path

def test_flask_isolation():
    """Test Flask app in isolation"""
    print("🔍 Testing Flask Isolation")
    
    # Test 1: Basic Flask import
    try:
        from flask import Flask
        print("✅ Flask import successful")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    # Test 2: Create minimal Flask app
    try:
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Flask working in isolation"
        
        @app.route('/health')
        def health():
            return {"status": "ok", "test": "isolation"}
        
        print("✅ Flask app creation successful")
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False
    
    # Test 3: Test Flask on different ports
    ports_to_test = [5558, 5559, 8080, 8081]
    
    for port in ports_to_test:
        print(f"🚀 Testing Flask on port {port}")
        
        # Check if port is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️ Port {port} already in use, skipping")
            continue
        
        # Start Flask app on this port
        flask_code = f'''
import sys
import os
import time
sys.path.append("/home/jonat/ai-stack")

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask working on port {port}"

@app.route('/health')
def health():
    return {{"status": "ok", "port": {port}, "timestamp": time.time()}}

if __name__ == '__main__':
    print(f"✅ Starting Flask on port {port}")
    app.run(host='0.0.0.0', port={port}, debug=False)
'''
        
        # Write Flask app
        test_app_path = Path("/home/jonat/ai-stack") / f"test_flask_port_{port}.py"
        with open(test_app_path, 'w') as f:
            f.write(flask_code)
        
        # Start Flask app
        cmd = [sys.executable, str(test_app_path)]
        
        process = subprocess.Popen(
            cmd,
            cwd="/home/jonat/ai-stack",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONPATH": "/home/jonat/ai-stack"}
        )
        
        # Wait for startup
        time.sleep(3)
        
        # Test if it's running
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Flask working on port {port}")
                print(f"   Response: {data}")
                
                # Stop the process
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                return True
            else:
                print(f"❌ Flask responded with status {response.status_code}")
        except Exception as e:
            print(f"❌ Flask connection failed: {e}")
        
        # Stop the process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        time.sleep(1)
    
    print("❌ All Flask isolation tests failed")
    return False

if __name__ == "__main__":
    success = test_flask_isolation()
    sys.exit(0 if success else 1)
