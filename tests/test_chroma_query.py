#!/usr/bin/env python3
"""Test what ChromaDB returns for Harmony query"""

import chromadb
from chromadb.utils import embedding_functions

client = chromadb.HttpClient(host="localhost", port=8000)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)

collection = client.get_collection(
    name="documents_768",
    embedding_function=embedding_func
)

query = "What are the four mechanisms in the Harmony-AI Bridge document?"

print(f"Query: {query}\n")
print("=" * 60)

# Test with documentation category (what backend should use)
categories = ["constella_master", "claude_conversation_chunk", "claude_conversation", 
             "documentation", "code", "parity", "conversation"]

results = collection.query(
    query_texts=[query],
    n_results=5,
    where={"category": {"$in": categories}}
)

print("Results with category filter:")
for i in range(len(results['documents'][0])):
    doc = results['documents'][0][i]
    meta = results['metadatas'][0][i]
    dist = results['distances'][0][i]
    print(f"\n{i+1}. Distance: {dist:.4f}")
    print(f"   Category: {meta.get('category', 'NONE')}")
    print(f"   Filename: {meta.get('filename', 'NONE')}")
    print(f"   Text: {doc[:150]}...")
