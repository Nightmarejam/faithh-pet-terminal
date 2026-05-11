#!/usr/bin/env python3
"""
Add Harmony documents with proper category metadata for FAITHH backend
"""

import chromadb
import hashlib
from pathlib import Path
from chromadb.utils import embedding_functions

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def add_harmony_doc(filepath: str, category: str = "documentation"):
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-mpnet-base-v2"
    )
    
    collection = client.get_or_create_collection(
        name="documents_768",
        embedding_function=embedding_func
    )
    
    path = Path(filepath)
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 Processing: {path.name}")
    print(f"   Length: {len(text)} characters")
    
    # Chunk the text
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]
        # Use harmony_ prefix to make IDs unique
        chunk_id = hashlib.md5(f"harmony_{path.name}:{start}".encode()).hexdigest()
        
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "metadata": {
                "filename": path.name,
                "category": category,
                "source": "harmony_framework",
                "start_pos": start,
                "end_pos": end
            }
        })
        start += CHUNK_SIZE - CHUNK_OVERLAP
    
    print(f"   Created {len(chunks)} chunks with category='{category}'")
    
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk["text"]],
            metadatas=[chunk["metadata"]],
            ids=[chunk["id"]]
        )
        if (i + 1) % 10 == 0:
            print(f"   Processed {i + 1}/{len(chunks)} chunks")
    
    print(f"✅ Added {path.name} with category='{category}'")

if __name__ == "__main__":
    # Add all Harmony docs with 'documentation' category
    harmony_docs = [
        "/home/jonat/ai-stack/constella-framework/harmony/docs/harmony_framework_complete_v4.0.0.md",
        "/home/jonat/ai-stack/constella-framework/harmony/docs/harmony_ai_bridge_v1.0.0.md",
        "/home/jonat/ai-stack/constella-framework/harmony/docs/resonance_transformer_architecture_spec_v1.0.0.md",
        "/home/jonat/ai-stack/docs/HARMONY_CONTEXT.md",
    ]
    
    for doc in harmony_docs:
        add_harmony_doc(doc, category="documentation")
    
    print("\n✅ All Harmony documents indexed with proper metadata!")
