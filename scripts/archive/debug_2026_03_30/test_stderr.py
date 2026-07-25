#!/usr/bin/env python3

import requests
import json
import subprocess
import time

# Start a simple test that captures stderr
print("Testing constitutional reasoning with stderr capture...")

response = requests.post(
    "http://localhost:5557/api/chat",
    json={"message": "What is the Universal Civic Floor?"},
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Constitutional reasoning: {'constitutional_reasoning' in data}")
    print(f"Integrations: {data.get('integrations_used', [])}")
    print(f"Response preview: {data.get('response', '')[:100]}...")
else:
    print(f"Error: {response.text}")
