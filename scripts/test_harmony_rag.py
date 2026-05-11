#!/usr/bin/env python3
"""Test harmony docs RAG accuracy."""
import requests

BACKEND_URL = "http://127.0.0.1:5557"

queries = [
    ("resonance gating", ["resonance_gating", "harmony"]),
    ("inner monologue engine", ["ime", "inner_monologue"]),
    ("resonance transformer architecture", ["resonance_transformer", "harmony"]),
    ("harmony ai bridge", ["harmony_ai_bridge", "harmony"]),
]

print("=== Harmony Docs RAG Tests ===\n")

passed = 0
failed = 0

for query, expected_keywords in queries:
    r = requests.post(f"{BACKEND_URL}/api/rag_search", 
                     json={"query": query, "n_results": 5},
                     timeout=30)
    data = r.json()
    results = data.get("results", [])
    
    # Check if any result contains expected keywords
    found_harmony = False
    top_sources = []
    
    for result in results[:3]:
        if isinstance(result, dict):
            source = result.get("metadata", {}).get("source", "")
        else:
            source = str(result)
        top_sources.append(source[:50])
        
        for keyword in expected_keywords:
            if keyword.lower() in source.lower():
                found_harmony = True
                break
    
    status = "PASS" if found_harmony else "FAIL"
    if found_harmony:
        passed += 1
    else:
        failed += 1
    
    print(f"Query: '{query}'")
    print(f"  Status: {status}")
    print(f"  Top sources: {top_sources[:2]}")
    print()

print(f"=== Summary ===")
print(f"Passed: {passed}/{len(queries)}")
print(f"Failed: {failed}/{len(queries)}")
print(f"Overall: {'ALL PASSED' if failed == 0 else 'SOME FAILED'}")
