#!/usr/bin/env python3
"""Test if ChromaDB upsert works without embeddings."""
import chromadb

client = chromadb.HttpClient(host='servicebox.taileb8c60.ts.net', port=8000)
collection = client.get_collection(name='faithh_knowledge_base')

print(f"Collection count before: {collection.count():,}")

# Try to upsert without embedding
try:
    collection.upsert(
        ids=['test_upsert_001'], 
        documents=['This is a test document for upsert without embedding'], 
        metadatas=[{'source': 'test_upsert.py', 'test': True}]
    )
    print('Upsert without embedding: SUCCESS')
except Exception as e:
    print(f'Upsert without embedding: FAILED')
    print(f'Error: {e}')

print(f"Collection count after: {collection.count():,}")

# Check if the doc exists
result = collection.get(ids=['test_upsert_001'])
if result['ids']:
    print(f"Document found: {result['ids']}")
else:
    print("Document NOT found")
