#!/usr/bin/env python3
"""
Check ChromaDB metadata for Constella documents.
Identifies how they're currently tagged and what needs updating.
"""
import chromadb
import json
from collections import Counter

client = chromadb.HttpClient(host="192.158.1.243", port=8000)
collection = client.get_collection("faithh_knowledge_base")

print(f"Total documents: {collection.count()}\n")

# Sample documents that mention Constella
results = collection.query(
    query_texts=["Constella Framework Astris Auctor governance token"],
    n_results=20,
    include=["documents", "metadatas", "distances"]
)

print("=== TOP 20 CONSTELLA-RELATED DOCS ===")
domains = []
source_types = []
for i, (doc, meta, dist) in enumerate(zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
)):
    domain = meta.get("domain", "MISSING")
    source_type = meta.get("source_type", "MISSING")
    domains.append(domain)
    source_types.append(source_type)
    print(f"\n[{i+1}] distance={dist:.3f}")
    print(f"  domain: {domain}")
    print(f"  source_type: {source_type}")
    print(f"  keys: {list(meta.keys())}")
    print(f"  text: {doc[:120]}...")

print("\n=== DOMAIN DISTRIBUTION (sample) ===")
for d, count in Counter(domains).most_common():
    print(f"  {d}: {count}")

print("\n=== SOURCE_TYPE DISTRIBUTION (sample) ===")
for s, count in Counter(source_types).most_common():
    print(f"  {s}: {count}")

# Now check what domains exist across the full collection by sampling
print("\n=== FULL COLLECTION DOMAIN SAMPLE (100 docs) ===")
sample = collection.get(limit=100, include=["metadatas"])
full_domains = [m.get("domain", "MISSING") for m in sample["metadatas"]]
for d, count in Counter(full_domains).most_common():
    print(f"  {d}: {count}")
