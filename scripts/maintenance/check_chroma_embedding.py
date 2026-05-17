#!/usr/bin/env python3
import chromadb
client = chromadb.HttpClient(host='192.158.1.10', port=8000)
coll = client.get_collection('faithh_knowledge_base')

# Get collection metadata
try:
    # Try to get the embedding function info
    print("Collection name:", coll.name)
    print("Document count:", coll.count())
    
    # The embedding function is not directly accessible via the client
    # But we can infer from the collection's behavior
    print("\nTesting embedding compatibility...")
    
    # Test a simple query to see if it works
    results = coll.query(
        query_texts=["test"],
        n_results=1
    )
    print("Query successful:", len(results['documents'][0]) > 0)
    
except Exception as e:
    print(f"Error: {e}")
