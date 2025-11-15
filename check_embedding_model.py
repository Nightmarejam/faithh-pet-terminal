import chromadb

client = chromadb.HttpClient(host='localhost', port=8000)
docs_col = client.get_collection('documents')

print(f'Collection metadata: {docs_col.metadata}')

# Check embedding dimensions
sample = docs_col.get(limit=1, include=['embeddings'])
print(f'\nSample data keys: {sample.keys()}')
print(f'Embeddings type: {type(sample["embeddings"])}')
print(f'Number of embeddings: {len(sample["embeddings"])}')

if len(sample['embeddings']) > 0:
    first_embedding = sample['embeddings'][0]
    print(f'First embedding type: {type(first_embedding)}')
    print(f'First embedding shape/len: {len(first_embedding)}')
    
    # Common models by dimension
    models = {
        384: 'all-MiniLM-L6-v2 (default ChromaDB)',
        768: 'all-mpnet-base-v2 or BERT-base',
        1536: 'OpenAI text-embedding-ada-002'
    }
    suggested_model = models.get(len(first_embedding), f'Unknown ({len(first_embedding)}-dim)')
    print(f'\n✅ Embedding dimension: {len(first_embedding)}')
    print(f'✅ Likely model: {suggested_model}')
