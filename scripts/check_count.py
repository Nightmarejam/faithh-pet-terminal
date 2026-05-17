#!/usr/bin/env python3
"""Simple script to check ChromaDB count and query for harmony docs."""
import chromadb

client = chromadb.HttpClient(host="192.158.1.10", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")
count = collection.count()
print(f"ChromaDB document count: {count:,}")

# Query for harmony docs
results = collection.query(
    query_texts=["resonance gating architecture premature synthesis"],
    n_results=5
)

print("\nTop 5 results for 'resonance gating':")
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    source = meta.get('source', 'unknown')
    indexed_by = meta.get('indexed_by', '')
    print(f"{i+1}. {source}")
    if 'harmony' in source.lower() or indexed_by == 'debug_indexer.py':
        print("   *** HARMONY DOC ***")
