#!/usr/bin/env python3
import sys
import os
import time
sys.path.append("/home/jonat/ai-stack")

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask working on port 5557"

@app.route('/health')
def health():
    return {"status": "ok", "port": 5557, "timestamp": time.time()}

if __name__ == '__main__':
    print("✅ Starting Flask on port 5557")
    app.run(host='0.0.0.0', port=5557, debug=False)
