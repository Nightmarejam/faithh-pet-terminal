#!/usr/bin/env python3
"""
FAITHH RAG Diagnostic Tool
Tests RAG functionality directly
"""

import requests
import json

def test_rag_search():
    """Test the RAG search endpoint directly"""
    print("=" * 70)
    print("TESTING RAG SEARCH ENDPOINT")
    print("=" * 70)
    
    queries = [
        "FAITHH backend development",
        "ChromaDB setup",
        "Langflow configuration",
        "Ollama models"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            response = requests.post(
                "http://localhost:5557/api/rag_search",
                json={"query": query, "n_results": 3}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data.get('documents', []))} results")
                
                for i, doc in enumerate(data.get('documents', [])[:1]):
                    meta = data.get('metadatas', [[]])[i]
                    dist = data.get('distances', [[]])[i]
                    print(f"   Top result: {meta.get('source', 'unknown')[:60]}...")
                    print(f"   Distance: {dist:.3f}")
                    print(f"   Category: {meta.get('category', 'unknown')}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_chat_with_rag():
    """Test the chat endpoint WITH RAG enabled"""
    print("\n" + "=" * 70)
    print("TESTING CHAT WITH RAG ENABLED")
    print("=" * 70)
    
    test_messages = [
        "What did we discuss about FAITHH backend?",
        "Tell me about ChromaDB setup"
    ]
    
    for message in test_messages:
        print(f"\n💬 Message: '{message}'")
        try:
            response = requests.post(
                "http://localhost:5557/api/chat",
                json={
                    "message": message,
                    "model": "llama3.1-8b",
                    "use_rag": True  # CRITICAL!
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('response', 'No response')
                print(f"✅ Response preview: {reply[:200]}...")
                
                # Check if response indicates RAG was used
                if any(word in reply.lower() for word in ['just started', 'just begun', "haven't discussed"]):
                    print("⚠️  Response suggests RAG was NOT used!")
                else:
                    print("✅ Response suggests RAG was used!")
            else:
                print(f"❌ Error {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_chat_without_rag():
    """Test chat WITHOUT RAG to confirm difference"""
    print("\n" + "=" * 70)
    print("TESTING CHAT WITHOUT RAG (for comparison)")
    print("=" * 70)
    
    message = "What did we discuss about FAITHH backend?"
    print(f"\n💬 Message: '{message}'")
    
    try:
        response = requests.post(
            "http://localhost:5557/api/chat",
            json={
                "message": message,
                "model": "llama3.1-8b",
                "use_rag": False  # Explicitly disabled
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get('response', 'No response')
            print(f"✅ Response preview: {reply[:200]}...")
            print("   (Should say 'just started' since no RAG)")
        else:
            print(f"❌ Error {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_backend_config():
    """Check backend status"""
    print("\n" + "=" * 70)
    print("CHECKING BACKEND STATUS")
    print("=" * 70)
    
    try:
        response = requests.get("http://localhost:5557/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status', 'unknown')}")
            print(f"   Model: {data.get('model', 'unknown')}")
            if 'chromadb' in data:
                print(f"   ChromaDB: {data['chromadb'].get('status', 'unknown')}")
                print(f"   Documents: {data['chromadb'].get('documents', 0)}")
        else:
            print(f"❌ Error {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "🔍 FAITHH RAG DIAGNOSTIC TOOL 🔍".center(70))
    print()
    
    # Run all tests
    check_backend_config()
    test_rag_search()
    test_chat_with_rag()
    test_chat_without_rag()
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print("\n💡 If 'CHAT WITH RAG' still shows 'just started' response:")
    print("   1. Check if backend is reading use_rag parameter")
    print("   2. Verify smart_rag_query is being called")
    print("   3. Check backend logs for RAG query activity")
    print()

if __name__ == "__main__":
    main()
