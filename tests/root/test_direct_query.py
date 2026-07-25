#!/usr/bin/env python3
import chromadb
client = chromadb.HttpClient(host='100.79.85.32', port=8000)
coll = client.get_collection('faithh_knowledge_base')

# Test direct query
results = coll.query(
    query_texts=["parasitic emergence experiment 5"],
    n_results=3
)

print("Query results:", len(results['documents'][0]))
for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0])):
    print(f"  {i+1}. Distance: {dist:.3f}")
    print(f"     Content: {doc[:100]}...")
    if 'experiment 5' in doc.lower() or 'parasitic' in doc.lower():
        print("     -> Exp 5 content found!")
