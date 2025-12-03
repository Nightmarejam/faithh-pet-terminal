import chromadb

client = chromadb.HttpClient(host='localhost', port=8000)
collections = client.list_collections()

print(f'=== ChromaDB HTTP Server (port 8000) ===')
print(f'Total collections: {len(collections)}')
for col in collections:
    print(f'  - {col.name}: {col.count()} docs')

# Try a test query on the documents collection
try:
    docs_col = client.get_collection('documents')
    results = docs_col.query(
        query_texts=['What is FAITHH?'],
        n_results=2
    )
    print(f'\n=== Test Query Results ===')
    print(f'Found {len(results["documents"][0])} results')
    for i, doc in enumerate(results['documents'][0]):
        print(f'\nResult {i+1}:')
        print(doc[:200] + '...' if len(doc) > 200 else doc)
except Exception as e:
    print(f'\nError querying: {e}')
