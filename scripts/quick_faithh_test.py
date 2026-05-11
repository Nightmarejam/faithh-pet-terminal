#!/usr/bin/env python3
"""Quick FAITHH test using Ollama (local) to avoid API dependencies"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:5557"

# Simple test queries
TESTS = [
    "What is 2+2?",
    "Tell me a short joke",
    "What is FAITHH?"
]

print("=" * 60)
print("🧪 QUICK FAITHH TEST (Using Ollama)")
print("=" * 60)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test 1: Backend Health
print("🔍 Test 1: Backend Health")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend healthy\n")
    else:
        print(f"   ❌ Backend unhealthy: {response.status_code}\n")
        exit(1)
except Exception as e:
    print(f"   ❌ Backend error: {e}\n")
    exit(1)

# Test 2: ChromaDB Status
print("🔍 Test 2: ChromaDB Status")
try:
    response = requests.get(f"{BACKEND_URL}/api/status", timeout=10)
    if response.status_code == 200:
        data = response.json()
        docs = data.get("services", {}).get("chromadb", {}).get("documents", 0)
        print(f"   ✅ ChromaDB: {docs} documents\n")
    else:
        print(f"   ❌ Status API failed: {response.status_code}\n")
except Exception as e:
    print(f"   ❌ Status error: {e}\n")

# Test 3: Simple Chat (Ollama, no RAG)
print("🔍 Test 3: Simple Chat (Ollama, no RAG)")
try:
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={
            "message": "What is 2+2? Answer in one sentence.",
            "model": "llama31-faithh:latest",
            "use_rag": False
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get("response", "")
        print(f"   ✅ Response: {answer[:100]}...\n")
    else:
        print(f"   ❌ Chat failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}\n")
except Exception as e:
    print(f"   ❌ Chat error: {e}\n")

# Test 4: Chat with RAG
print("🔍 Test 4: Chat with RAG")
try:
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={
            "message": "What is FAITHH? Answer briefly.",
            "model": "llama31-faithh:latest",
            "use_rag": True
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get("response", "")
        print(f"   ✅ Response: {answer[:150]}...\n")
    else:
        print(f"   ❌ Chat with RAG failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}\n")
except Exception as e:
    print(f"   ❌ Chat with RAG error: {e}\n")

print("=" * 60)
print("✅ Quick test complete!")
print("=" * 60)
