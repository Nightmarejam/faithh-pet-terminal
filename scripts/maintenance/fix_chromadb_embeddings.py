#!/usr/bin/env python3
"""
Fix ChromaDB embedding dimension mismatch
The collection was created with 768-dim embeddings, but nomic-embed-text uses 384
"""

import chromadb
import requests

print("🔍 Checking ChromaDB embedding configuration...")

# Connect to ChromaDB
client = chromadb.HttpClient(host="localhost", port=8000)

# Check current collection
try:
    collection = client.get_collection(name="documents")
    print(f"✅ Found collection 'documents' with {collection.count()} documents")
    
    # Get collection metadata
    metadata = collection.metadata if hasattr(collection, 'metadata') else {}
    print(f"📊 Collection metadata: {metadata}")
    
    # The issue: Collection expects 768 dimensions (probably from sentence-transformers)
    # but nomic-embed-text provides 384 dimensions
    
    print("\n⚠️ Embedding dimension mismatch detected!")
    print("Collection expects: 768 dimensions")
    print("Current model provides: 384 dimensions (nomic-embed-text)")
    
    print("\n🔧 Solutions:")
    print("1. Use text search without embeddings (query_texts)")
    print("2. Create new collection with current embedding model")
    print("3. Use a 768-dimension model (like sentence-transformers/all-MiniLM-L6-v2)")
    
    # Test which Ollama embedding models are available
    print("\n🤖 Checking available Ollama embedding models...")
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        models = response.json().get('models', [])
        embed_models = [m for m in models if 'embed' in m['name'].lower()]
        print(f"Found embedding models: {[m['name'] for m in embed_models]}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Recommendation: Use query_texts parameter instead of embeddings for now")
print("This will use ChromaDB's default embedding function internally")