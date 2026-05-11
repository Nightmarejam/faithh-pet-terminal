#!/usr/bin/env python3
"""Verify constitutional documents were indexed correctly"""

import chromadb

client = chromadb.HttpClient(host='192.158.1.243', port=8000)
collection = client.get_collection('faithh_knowledge_base')

# Get constitutional documents
results = collection.get(where={'domain': 'constella_constitutional'})

print(f"Constitutional documents in collection: {len(results['ids'])}")
print("\nDocument breakdown:")

principles = 0
mapping_sections = 0

for i, metadata in enumerate(results['metadatas']):
    doc_type = metadata.get('document_type', 'unknown')
    title = metadata.get('title', 'N/A')
    print(f"  {results['ids'][i]}: {doc_type} - {title}")
    
    if doc_type == 'principle':
        principles += 1
    elif doc_type == 'mapping_section':
        mapping_sections += 1

print(f"\nSummary:")
print(f"  Principles: {principles}")
print(f"  Mapping sections: {mapping_sections}")
print(f"  Total: {len(results['ids'])}")
