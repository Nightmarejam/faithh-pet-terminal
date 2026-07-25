#!/usr/bin/env python3
"""Debug RAG ranking for resonance gating query."""
import chromadb

client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")

# Query without category filter
results = collection.query(
    query_texts=["resonance gating"],
    n_results=10
)

print("Top 10 results for 'resonance gating':")
for i, (doc, meta, dist) in enumerate(zip(
    results['documents'][0], 
    results['metadatas'][0], 
    results['distances'][0]
)):
    source = meta.get('source', 'unknown')[:50]
    category = meta.get('category', 'unknown')
    print(f"{i+1}. [{category}] {source} (dist: {dist:.3f})")

print("\n--- project_docs only ---")
results2 = collection.query(
    query_texts=["resonance gating"],
    n_results=5,
    where={"category": "project_docs"}
)

for i, (doc, meta, dist) in enumerate(zip(
    results2['documents'][0], 
    results2['metadatas'][0], 
    results2['distances'][0]
)):
    source = meta.get('source', 'unknown')[:50]
    print(f"{i+1}. {source} (dist: {dist:.3f})")
