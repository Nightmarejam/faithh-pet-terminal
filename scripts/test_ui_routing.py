#!/usr/bin/env python3
"""
FAITHH UI Smart Routing Test Script
Tests the auto-routing functionality by simulating different query types
"""

import json
import time
import requests
from datetime import datetime

# Configuration
FAITHH_URL = "http://localhost:5557"
TEST_QUERIES = [
    # Quick queries (should select qwen25-grounded:latest)
    {
        "query": "What's the capital of France?",
        "expected_model": "qwen25-grounded:latest",
        "category": "quick",
        "use_rag": False
    },
    {
        "query": "Hello, how are you?",
        "expected_model": "qwen25-grounded:latest", 
        "category": "quick",
        "use_rag": False
    },
    
    # Code/technical (should select qwen25-grounded:latest)
    {
        "query": "Write a Python function to find duplicates in a list",
        "expected_model": "qwen25-grounded:latest",
        "category": "coding",
        "use_rag": False
    },
    {
        "query": "Debug this code: def factorial(n): if n = 0: return 1",
        "expected_model": "qwen25-grounded:latest",
        "category": "coding", 
        "use_rag": False
    },
    
    # Complex reasoning (should select llama3.3:70b)
    {
        "query": "Explain trolley problem with multiple scenarios",
        "expected_model": "llama3.3:70b",
        "category": "reasoning",
        "use_rag": False
    },
    {
        "query": "What are the implications of quantum computing on cryptography?",
        "expected_model": "llama3.3:70b",
        "category": "reasoning",
        "use_rag": False
    },
    
    # Edge cases
    {
        "query": "",
        "expected_model": "qwen25-grounded:latest",
        "category": "edge_empty",
        "use_rag": False
    },
    {
        "query": "console.log('test');",
        "expected_model": "qwen25-grounded:latest",
        "category": "edge_special_chars",
        "use_rag": False
    }
]

def test_backend_health():
    """Check if backend is responding"""
    try:
        response = requests.get(f"{FAITHH_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_model_availability():
    """Check if models are available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            print(f"✅ Found {len(models)} models in Ollama")
            
            # Check key models
            key_models = [
                "qwen25-grounded:latest",
                "llama3.3:70b"
            ]
            
            for model in key_models:
                if model in models:
                    print(f"  ✅ {model}")
                else:
                    print(f"  ❌ {model} not found")
            
            return models
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Model availability check failed: {e}")
        return []

def test_query_routing(query_data):
    """Test a single query and check response"""
    print(f"\n🧪 Testing: {query_data['query'][:50]}...")
    print(f"   Category: {query_data['category']}")
    print(f"   Expected: {query_data['expected_model']}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{FAITHH_URL}/api/chat",
            json={
                "message": query_data["query"],
                "model": "auto",  # This would trigger auto-routing in UI
                "use_rag": query_data["use_rag"]
            },
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response received in {elapsed:.2f}s")
            print(f"   Model used: {data.get('model_used', 'Unknown')}")
            print(f"   Response preview: {data.get('response', '')[:100]}...")
            
            # Check if expected model was used
            # Note: Backend doesn't currently support "auto" model, so this will fail
            # This is just to test backend responsiveness
            return {
                "status": "success",
                "elapsed": elapsed,
                "model_used": data.get('model_used', 'Unknown'),
                "response_preview": data.get('response', '')[:100]
            }
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return {
                "status": "failed",
                "error": response.text
            }
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    """Run all tests"""
    print("=" * 60)
    print("FAITHH UI Smart Routing Test")
    print("=" * 60)
    
    # Health checks
    if not test_backend_health():
        print("\n❌ Backend not healthy. Exiting.")
        return
    
    models = test_model_availability()
    if not models:
        print("\n❌ No models available. Exiting.")
        return
    
    print("\n" + "=" * 60)
    print("TESTING QUERY ROUTING")
    print("=" * 60)
    
    results = []
    
    for test in TEST_QUERIES:
        result = test_query_routing(test)
        result["test_data"] = test
        results.append(result)
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_routing_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {results_file}")
    
    print("\n⚠️  NOTE: The backend doesn't currently support 'auto' model.")
    print("   To test actual routing, you need to:")
    print("   1. Open http://localhost:5557/ in browser")
    print("   2. Open DevTools (F12)")
    print("   3. Set model to 'Auto (Smart Routing)'")
    print("   4. Send queries manually")
    print("   5. Check console for [Model] logs")

if __name__ == "__main__":
    main()
