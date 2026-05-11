#!/usr/bin/env python3
"""Integration tests - end-to-end chat with RAG context."""
import requests
import time

BACKEND_URL = "http://127.0.0.1:5557"

def test_chromadb_connection():
    """Test ChromaDB connectivity via backend."""
    r = requests.get(f"{BACKEND_URL}/health", timeout=10)
    data = r.json()
    connected = data.get("chromadb", {}).get("connected", False)
    doc_count = data.get("chromadb", {}).get("documents", 0)
    print(f"ChromaDB: {'Connected' if connected else 'Disconnected'} ({doc_count:,} docs)")
    return connected

def test_ollama_availability():
    """Test Ollama LLM availability."""
    r = requests.get(f"{BACKEND_URL}/health", timeout=10)
    data = r.json()
    ollama_url = data.get("providers", {}).get("ollama", "")
    print(f"Ollama: {ollama_url}")
    
    # Try to reach Ollama directly
    try:
        ollama_r = requests.get(f"{ollama_url}/api/tags", timeout=5)
        models = ollama_r.json().get("models", [])
        model_names = [m.get("name", "unknown") for m in models[:3]]
        print(f"  Models available: {model_names}")
        return True
    except Exception as e:
        print(f"  Warning: Could not reach Ollama: {e}")
        return False

def test_chat_endpoint():
    """Test basic chat functionality."""
    print("Chat endpoint: Testing...")
    
    try:
        r = requests.post(f"{BACKEND_URL}/api/chat",
                         json={
                             "message": "What is resonance gating?",
                             "model": "qwen25-grounded:latest"
                         },
                         timeout=60)
        
        if r.status_code == 200:
            data = r.json()
            response = data.get("response", "")[:100]
            rag_used = len(data.get("rag_results", [])) > 0
            print(f"  Status: 200 OK")
            print(f"  RAG context used: {rag_used}")
            print(f"  Response preview: {response}...")
            return True
        else:
            print(f"  Status: {r.status_code}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_providers():
    """Test LLM provider availability."""
    r = requests.get(f"{BACKEND_URL}/health", timeout=10)
    data = r.json()
    providers = data.get("providers", {})
    
    print("LLM Providers:")
    for name, status in providers.items():
        status_str = status if isinstance(status, str) else ("Available" if status else "Unavailable")
        print(f"  {name}: {status_str}")
    
    return any(providers.values())

print("=== Integration Tests ===\n")

results = []

# Test 1: ChromaDB
results.append(("ChromaDB Connection", test_chromadb_connection()))
print()

# Test 2: Ollama
results.append(("Ollama Availability", test_ollama_availability()))
print()

# Test 3: Providers
results.append(("LLM Providers", test_providers()))
print()

# Test 4: Chat (skip if Ollama unavailable)
if results[1][1]:  # If Ollama is available
    results.append(("Chat Endpoint", test_chat_endpoint()))
else:
    print("Chat endpoint: SKIPPED (Ollama unavailable)")
    results.append(("Chat Endpoint", None))

print("\n=== Summary ===")
passed = sum(1 for _, r in results if r is True)
failed = sum(1 for _, r in results if r is False)
skipped = sum(1 for _, r in results if r is None)

for name, result in results:
    if result is True:
        status = "PASS"
    elif result is False:
        status = "FAIL"
    else:
        status = "SKIP"
    print(f"  {name}: {status}")

print(f"\nPassed: {passed}, Failed: {failed}, Skipped: {skipped}")
