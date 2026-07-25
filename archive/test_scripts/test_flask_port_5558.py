
import sys
import os
import time
sys.path.append("/home/jonat/ai-stack")

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask working on port 5558"

@app.route('/health')
def health():
    return {"status": "ok", "port": 5558, "timestamp": time.time()}

if __name__ == '__main__':
    print(f"✅ Starting Flask on port 5558")
    app.run(host='0.0.0.0', port=5558, debug=False)
