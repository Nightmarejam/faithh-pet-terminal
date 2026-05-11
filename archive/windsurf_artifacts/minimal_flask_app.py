
import sys
import os
import time
sys.path.append("/home/jonat/ai-stack")

from flask import Flask, jsonify
import yaml

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'stage': 'core_flask',
        'timestamp': time.time()
    })

@app.route('/api/status')
def status():
    return jsonify({
        'stage': 'core_flask',
        'components': ['flask', 'yaml'],
        'status': 'running'
    })

if __name__ == '__main__':
    print("✅ Core Flask app starting on port 5557")
    app.run(host='0.0.0.0', port=5557, debug=False)
