#!/usr/bin/env python3
"""
FAITHH R1 Health Check - Echo Level Testing
Tests: Does the system respond?

Run this anytime to verify FAITHH is working.
Takes ~1 minute.
"""

import sys
import time
import requests
import chromadb
from chromadb.utils import embedding_functions

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def test_result(name, passed, message=""):
    """Print test result with color"""
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"{status} - {name}")
    if message:
        print(f"        {message}")
    return passed

def main():
    print("=" * 60)
    print("🔍 FAITHH R1 HEALTH CHECK - Echo Level")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Backend Running
    print("Test 1: Backend Running (port 5557)")
    try:
        response = requests.get("http://localhost:5557/api/status", timeout=5)
        passed = response.status_code == 200
        if passed:
            data = response.json()
            msg = f"Backend v{data.get('version', 'unknown')}"
        else:
            msg = f"HTTP {response.status_code}"
        results.append(test_result("Backend", passed, msg))
    except Exception as e:
        results.append(test_result("Backend", False, str(e)))
    
    print()
    
    # Test 2: ChromaDB Connection
    print("Test 2: ChromaDB Connection (port 8000)")
    try:
        client = chromadb.HttpClient(host="localhost", port=8000)
        collections = client.list_collections()
        passed = len(collections) > 0
        msg = f"{len(collections)} collection(s) found"
        results.append(test_result("ChromaDB", passed, msg))
    except Exception as e:
        results.append(test_result("ChromaDB", False, str(e)))
    
    print()
    
    # Test 3: Collection Access
    print("Test 3: Main Collection Access")
    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"
        )
        collection = client.get_collection(name="documents_768", embedding_function=ef)
        count = collection.count()
        passed = count > 90000  # Should have ~93K docs
        msg = f"{count:,} documents"
        results.append(test_result("Collection", passed, msg))
    except Exception as e:
        results.append(test_result("Collection", False, str(e)))
    
    print()
    
    # Test 4: RAG Query Function
    print("Test 4: RAG Query Response")
    try:
        start = time.time()
        results_rag = collection.query(
            query_texts=["test query"],
            n_results=3
        )
        elapsed = time.time() - start
        passed = (results_rag['documents'] and 
                 len(results_rag['documents'][0]) > 0 and
                 elapsed < 5.0)
        msg = f"Returned {len(results_rag['documents'][0])} results in {elapsed:.2f}s"
        results.append(test_result("RAG Query", passed, msg))
    except Exception as e:
        results.append(test_result("RAG Query", False, str(e)))
    
    print()
    
    # Test 5: Constella Master Docs
    print("Test 5: Constella Master Documents")
    try:
        constella_results = collection.query(
            query_texts=["Astris Auctor tokens"],
            n_results=5,
            where={"category": "constella_master"}
        )
        count = len(constella_results['documents'][0]) if constella_results['documents'] else 0
        passed = count >= 3
        msg = f"{count} Constella docs found"
        results.append(test_result("Constella Docs", passed, msg))
    except Exception as e:
        results.append(test_result("Constella Docs", False, str(e)))
    
    print()
    
    # Test 6: Chat Endpoint
    print("Test 6: Chat Endpoint Response")
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:5557/api/chat",
            json={"message": "test", "use_rag": False},
            timeout=30
        )
        elapsed = time.time() - start
        passed = response.status_code == 200
        msg = f"Responded in {elapsed:.1f}s"
        results.append(test_result("Chat Endpoint", passed, msg))
    except Exception as e:
        results.append(test_result("Chat Endpoint", False, str(e)))
    
    print()
    print("=" * 60)
    
    # Summary
    passed_count = sum(results)
    total_count = len(results)
    
    if passed_count == total_count:
        print(f"{GREEN}🎉 ALL TESTS PASSED ({passed_count}/{total_count}){RESET}")
        print("FAITHH is healthy and ready to use!")
    elif passed_count >= 4:
        print(f"{YELLOW}⚠️  MOSTLY WORKING ({passed_count}/{total_count}){RESET}")
        print("Core functionality is working, some issues detected.")
    else:
        print(f"{RED}❌ SYSTEM UNHEALTHY ({passed_count}/{total_count}){RESET}")
        print("Critical issues detected. Check logs.")
    
    print("=" * 60)
    
    # Exit code
    sys.exit(0 if passed_count == total_count else 1)

if __name__ == "__main__":
    main()
