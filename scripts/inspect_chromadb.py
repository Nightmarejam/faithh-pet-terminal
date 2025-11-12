#!/usr/bin/env python3
"""Inspect existing ChromaDB setup"""

import chromadb
import os

# Try common locations
locations = ["./data", "./cache", "./chromadb", "."]

for location in locations:
    if not os.path.exists(location):
        continue
    
    print(f"\n🔍 Checking: {location}")
    try:
        client = chromadb.PersistentClient(path=location)
        collections = client.list_collections()
        
        if collections:
            print(f"✓ Found ChromaDB with {len(collections)} collection(s):")
            for col in collections:
                print(f"\n  📚 Collection: {col.name}")
                count = col.count()
                print(f"     Documents: {count}")
                
                # Show metadata if available
                if count > 0:
                    sample = col.get(limit=1)
                    if sample['metadatas']:
                        print(f"     Metadata: {sample['metadatas'][0]}")
        else:
            print("  (Empty database)")
    except Exception as e:
        print(f"  ✗ Not a valid ChromaDB: {e}")

print("\n✓ Inspection complete")
