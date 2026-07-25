#!/usr/bin/env python3
"""Direct test of constitutional reasoning without buffering issues"""

import subprocess
import time
import requests
import json
import signal
import sys
import os

# Start backend in background
print("Starting backend...")
backend_proc = subprocess.Popen([
    'python3', 'faithh_professional_backend_fixed.py'
], cwd='/home/jonat/ai-stack', 
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT,
    text=True,
    env={**dict(os.environ), 'PYTHONPATH': '/home/jonat/ai-stack'})

# Wait for backend to start
print("Waiting for backend to start...")
time.sleep(10)

# Test health
try:
    response = requests.get('http://localhost:5557/health', timeout=5)
    if response.status_code == 200:
        print("✅ Backend is healthy")
    else:
        print(f"❌ Backend health check failed: {response.status_code}")
        backend_proc.terminate()
        sys.exit(1)
except Exception as e:
    print(f"❌ Cannot connect to backend: {e}")
    backend_proc.terminate()
    sys.exit(1)

# Test constitutional reasoning
print("\nTesting constitutional reasoning...")
test_query = "What is the Universal Civic Floor?"

try:
    response = requests.post(
        'http://localhost:5557/api/chat',
        json={
            "message": test_query,
            "use_rag": True
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Request successful")
        print(f"Constitutional reasoning present: {'constitutional_reasoning' in data}")
        print(f"Integrations used: {data.get('integrations_used', [])}")
        
        if 'constitutional_reasoning' in data:
            const_data = data['constitutional_reasoning']
            print(f"Principles retrieved: {const_data.get('principles_retrieved', 0)}")
            print(f"Mechanisms: {const_data.get('mechanisms', [])}")
            print("🎉 CONSTITUTIONAL REASONING WORKING!")
        else:
            print("❌ No constitutional reasoning detected")
    else:
        print(f"❌ Request failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Test request failed: {e}")

# Show some backend output
print("\nBackend output (last 10 lines):")
backend_output = []
while True:
    line = backend_proc.stdout.readline()
    if not line:
        break
    backend_output.append(line)
    if len(backend_output) > 100:
        backend_output.pop(0)

for line in backend_output[-10:]:
    if any(keyword in line for keyword in ['🔍', '🏛️', 'GOVERNANCE', 'constitutional']):
        print(f"   {line.strip()}")

# Clean up
print("\nStopping backend...")
backend_proc.terminate()
backend_proc.wait()
print("Test complete.")
