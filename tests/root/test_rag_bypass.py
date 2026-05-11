#!/usr/bin/env python3
import chromadb
from chromadb.utils import embedding_functions

# Connect to ChromaDB
client = chromadb.HttpClient(host='100.79.85.32', port=8000)
coll = client.get_collection('faithh_knowledge_base')

# Create the same embedding function as the backend
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Test query with backend's embedding function
query_text = "parasitic emergence experiment 5"
query_embedding = embedder([query_text])

print(f"Query embedding shape: {len(query_embedding[0])} dimensions")
print(f"Query embedding type: {type(query_embedding)}")

# Try the query
results = coll.query(
    query_embeddings=query_embedding,
    n_results=3
)

print(f"\nQuery results: {len(results['documents'][0])}")
for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0])):
    print(f"  {i+1}. Distance: {dist:.3f}")
    if 'experiment 5' in doc.lower() or 'parasitic' in doc.lower():
        print(f"     -> Exp 5 content: {doc[:50]}...")
