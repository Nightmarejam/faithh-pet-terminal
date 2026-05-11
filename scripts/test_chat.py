#!/usr/bin/env python3
"""Test chat endpoint without RAG to verify fix."""
import requests
import json

url = "http://localhost:5557/api/chat"
payload = {
    "message": "Hello, what phase is FAITHH in?",
    "model": "auto",
    "rag_enabled": False
}

print("Testing chat endpoint (RAG disabled)...")
try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status: {response.status_code}")
    data = response.json()
    if "response" in data:
        print(f"Response: {data['response'][:500]}...")
    else:
        print(f"Data: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")
