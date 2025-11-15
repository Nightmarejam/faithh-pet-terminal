#!/usr/bin/env python3
"""Quick test of existing RAG system"""
import chromadb

try:
    client = chromadb.HttpClient(host="localhost", port=8000)
    print("✅ Connected to ChromaDB")
    
    collections = client.list_collections()
    print(f"📚 Collections: {[c.name for c in collections]}")
    
    try:
        coll = client.get_collection("documents")
        count = coll.count()
        print(f"📄 Documents indexed: {count}")
        
        # Try a test query
        if count > 0:
            results = coll.query(
                query_texts=["test"],
                n_results=1
            )
            print(f"✅ Query test successful")
    except Exception as e:
        print(f"⚠️  Collection 'documents' not found or empty: {e}")
    
except Exception as e:
    print(f"❌ Could not connect to ChromaDB: {e}")
    print("   Make sure ChromaDB is running on port 8000")
