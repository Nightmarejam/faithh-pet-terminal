#!/usr/bin/env python3
"""Backend performance tests."""
import requests
import time
import json

BACKEND_URL = "http://127.0.0.1:5557"

def test_health():
    start = time.time()
    r = requests.get(f"{BACKEND_URL}/health", timeout=10)
    latency = time.time() - start
    print(f"Health check: {r.status_code} ({latency:.3f}s)")
    return r.status_code == 200, latency

def test_rag_search():
    start = time.time()
    r = requests.post(f"{BACKEND_URL}/api/rag_search", 
                     json={"query": "resonance gating", "n_results": 3},
                     timeout=30)
    latency = time.time() - start
    data = r.json()
    results_count = len(data.get("results", []))
    print(f"RAG search: {r.status_code} ({latency:.3f}s) - {results_count} results")
    return r.status_code == 200, latency

def test_status():
    start = time.time()
    r = requests.get(f"{BACKEND_URL}/api/status", timeout=10)
    latency = time.time() - start
    print(f"Status: {r.status_code} ({latency:.3f}s)")
    return r.status_code == 200, latency

print("=== Backend Performance Tests ===\n")

results = []
results.append(("Health", *test_health()))
results.append(("Status", *test_status()))
results.append(("RAG Search", *test_rag_search()))

print("\n=== Summary ===")
all_passed = True
for name, passed, latency in results:
    status = "PASS" if passed else "FAIL"
    all_passed = all_passed and passed
    print(f"  {name}: {status} ({latency:.3f}s)")

print(f"\nOverall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
