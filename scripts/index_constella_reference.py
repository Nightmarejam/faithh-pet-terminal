#!/usr/bin/env python3
"""
Index Constella reference documents into ChromaDB with highest priority.
"""

import os
import chromadb
from chromadb.utils import embedding_functions

# Configuration - matches your FAITHH setup
CONSTELLA_REPO = "./constella-framework"
REFERENCE_DIR = f"{CONSTELLA_REPO}/docs/reference"

DOCS_TO_INDEX = [
    {"file": "v1.5.4_HR1.md", "id": "constella_v1.5.4_hr1", "description": "Token mechanics, Astris/Auctor formulas, UCF allocation, governance"},
    {"file": "Robustness_Pack_v1.3.md", "id": "constella_robustness_pack", "description": "Evidence levels, validation pipeline, safety protocols"},
    {"file": "Framework_Master_v1.2.md", "id": "constella_framework_master", "description": "Module definitions - Echo Code, Sky Lattice, threads"},
    {"file": "README.md", "id": "constella_reference_index", "description": "Quick reference with key formulas"}
]

def main():
    print("🌌 Constella Reference Indexer")
    print("=" * 60)
    
    if not os.path.exists(REFERENCE_DIR):
        print(f"❌ Reference directory not found at {REFERENCE_DIR}")
        return
    
    # Connect to ChromaDB HTTP server
    print("\n📂 Connecting to ChromaDB...")
    client = chromadb.HttpClient(host="localhost", port=8000)
    
    # Use the same embedding function as your main collection
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-mpnet-base-v2"
    )
    
    collection = client.get_collection(name="documents_768", embedding_function=ef)
    print(f"✅ Connected! Collection has {collection.count()} documents")
    
    # Remove existing constella master docs if present
    print("\n🔍 Checking for existing Constella master documents...")
    existing_ids = [doc["id"] for doc in DOCS_TO_INDEX] + ["constella_celestial_equilibrium"]
    try:
        collection.delete(ids=existing_ids)
        print("   Cleared any existing entries")
    except:
        pass
    
    # Index each document
    print("\n📚 Indexing reference documents...")
    indexed_count = 0
    
    for doc_info in DOCS_TO_INDEX:
        file_path = os.path.join(REFERENCE_DIR, doc_info["file"])
        if not os.path.exists(file_path):
            print(f"   ⚠️  Skipping {doc_info['file']} - not found")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            "source": "constella_master",
            "category": "constella_master",
            "priority": "highest",
            "type": "framework_reference",
            "file": doc_info["file"],
            "description": doc_info["description"]
        }
        
        collection.add(documents=[content], metadatas=[metadata], ids=[doc_info["id"]])
        print(f"   ✅ {doc_info['file']} ({len(content)} chars)")
        indexed_count += 1
    
    # Index doctrine if available
    doctrine_path = f"{CONSTELLA_REPO}/docs/doctrine/README.md"
    if os.path.exists(doctrine_path):
        print("\n📜 Indexing Celestial Equilibrium doctrine...")
        with open(doctrine_path, 'r') as f:
            content = f.read()
        
        collection.add(
            documents=[content],
            metadatas=[{"source": "constella_master", "category": "constella_master", "priority": "highest", "type": "doctrine"}],
            ids=["constella_celestial_equilibrium"]
        )
        print(f"   ✅ Doctrine ({len(content)} chars)")
        indexed_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 COMPLETE: {indexed_count} documents indexed")
    print(f"   Total in collection: {collection.count()}")
    print("\n✨ Test with FAITHH: 'What is the Astris decay formula?'")

if __name__ == "__main__":
    main()
