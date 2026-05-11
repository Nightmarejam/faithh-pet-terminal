#!/usr/bin/env python3

import requests
import json

response = requests.post(
    "http://localhost:5557/api/chat",
    json={"message": "What is the Universal Civic Floor?"},
    timeout=10
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Constitutional reasoning: {'constitutional_reasoning' in data}")
else:
    print(f"Error: {response.text}")
