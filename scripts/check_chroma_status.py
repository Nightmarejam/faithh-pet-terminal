#!/usr/bin/env python3
"""Check ChromaDB collection status."""
import chromadb

c = chromadb.HttpClient(host="192.158.1.243", port=8000)
col = c.get_collection("faithh_knowledge_base")
print(f"Total docs: {col.count()}")

# Check conversation chunks by platform
for platform in ["chatgpt", "claude", "grok"]:
    try:
        results = col.get(where={"platform": platform}, limit=3, include=["metadatas"])
        count = len(results["ids"]) if results and results.get("ids") else 0
        print(f"\n{platform.upper()} samples ({count} shown):")
        if results and results.get("metadatas"):
            for meta in results["metadatas"][:2]:
                print(f"  - date_month: {meta.get('date_month')}, date_year: {meta.get('date_year')}, category: {meta.get('category')}")
    except Exception as e:
        print(f"  Error: {e}")

# Test temporal query
print("\n--- Temporal Query Test: 'February 2026' ---")
results = col.query(
    query_texts=["What did I work on in February 2026?"],
    n_results=5,
    where={"date_month": "2026-02"}
)
if results and results.get("documents"):
    print(f"Found {len(results['documents'][0])} results for Feb 2026")
    for i, (doc, meta) in enumerate(zip(results["documents"][0][:2], results["metadatas"][0][:2])):
        print(f"  {i+1}. [{meta.get('platform')}] {meta.get('title', 'No title')[:50]}...")
