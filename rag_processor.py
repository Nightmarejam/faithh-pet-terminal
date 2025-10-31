#!/usr/bin/env python3
"""
RAG Document Processor
Chunks documents, generates embeddings, and stores in ChromaDB
"""

import requests
import chromadb
import hashlib
from pathlib import Path
from typing import List, Dict

# Configuration
OLLAMA_EMBED_URL = "http://localhost:11435"
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

class RAGProcessor:
    def __init__(self):
        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "User documents for RAG"}
        )
    
    def chunk_text(self, text: str, filename: str) -> List[Dict]:
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end]
            chunk_id = hashlib.md5(f"{filename}:{start}".encode()).hexdigest()
            
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "start_pos": start,
                    "end_pos": end
                }
            })
            
            start += CHUNK_SIZE - CHUNK_OVERLAP
        
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        response = requests.post(
            f"{OLLAMA_EMBED_URL}/api/embeddings",
            json={
                "model": "nomic-embed",
                "prompt": text
            }
        )
        response.raise_for_status()
        return response.json()["embedding"]
    
    def add_document(self, filepath: str):
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"📄 Processing: {path.name}")
        print(f"   Length: {len(text)} characters")
        
        chunks = self.chunk_text(text, path.name)
        print(f"   Created {len(chunks)} chunks")
        
        print("   Generating embeddings...")
        for i, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk["text"])
            
            self.collection.add(
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[chunk["metadata"]],
                ids=[chunk["id"]]
            )
            
            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{len(chunks)} chunks")
        
        print(f"✅ Added {path.name} to database")
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        query_embedding = self.get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted
    
    def list_documents(self) -> List[str]:
        all_items = self.collection.get()
        filenames = set()
        
        if all_items['metadatas']:
            for metadata in all_items['metadatas']:
                filenames.add(metadata.get('filename', 'unknown'))
        
        return sorted(list(filenames))


def main():
    import sys
    
    processor = RAGProcessor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add document:    python rag_processor.py add <filepath>")
        print("  Search:          python rag_processor.py search <query>")
        print("  List documents:  python rag_processor.py list")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Please provide a file path")
            return
        processor.add_document(sys.argv[2])
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please provide a search query")
            return
        query = " ".join(sys.argv[2:])
        results = processor.search(query)
        
        print(f"\n🔍 Search results for: '{query}'\n")
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  File: {result['metadata']['filename']}")
            print(f"  Text: {result['text'][:200]}...")
            if result['distance']:
                print(f"  Distance: {result['distance']:.4f}")
            print()
    
    elif command == "list":
        docs = processor.list_documents()
        print(f"\n📚 Indexed documents ({len(docs)}):")
        for doc in docs:
            print(f"  - {doc}")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
