#!/usr/bin/env python3

import chromadb

client = chromadb.HttpClient(host='servicebox.taileb8c60.ts.net', port=8000)
collection = client.get_collection('faithh_knowledge_base')

results = collection.query(
    query_texts=['Universal Civic Floor'],
    n_results=5,
    where={'domain': 'constella_constitutional'}
)

print(f"Found {len(results['documents'][0]) if results['documents'] and results['documents'][0] else 0} constitutional documents")

if results['documents'] and results['documents'][0]:
    for i, doc in enumerate(results['documents'][0][:2]):
        print(f"\nDocument {i+1}:")
        print(f"Content: {doc[:200]}...")
        if results['metadatas'] and results['metadatas'][0]:
            metadata = results['metadatas'][0][i]
            print(f"Metadata: {metadata}")
            print(f"Document type: {metadata.get('document_type')}")
            print(f"Is principle? {metadata.get('document_type') == 'principle'}")
