#!/usr/bin/env python3
"""
simple_rag.py - Minimal RAG system for FAITHH
This is a STARTING POINT - simple and functional

Usage:
    python3 simple_rag.py add "Your text here"
    python3 simple_rag.py query "What did I say about X?"
"""

import chromadb
import sys
import os
from datetime import datetime

class SimpleRAG:
    def __init__(self, db_path="./faithh_rag"):
        """Initialize ChromaDB"""
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="faithh_memory",
            metadata={"description": "FAITHH conversation memory"}
        )
        
        print(f"✓ RAG initialized: {self.collection.count()} memories stored")
    
    def add_memory(self, text, metadata=None):
        """Store a memory"""
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {"timestamp": datetime.now().isoformat()}],
            ids=[memory_id]
        )
        
        print(f"✓ Memory stored: {memory_id}")
        return memory_id
    
    def query_memory(self, query, n_results=3):
        """Search memories"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results
    
    def show_stats(self):
        """Show database stats"""
        count = self.collection.count()
        print(f"\n=== FAITHH RAG Stats ===")
        print(f"Total memories: {count}")
        
        if count > 0:
            # Show recent memories
            recent = self.collection.get(limit=5)
            print(f"\nRecent memories:")
            for doc in recent['documents']:
                preview = doc[:100] + "..." if len(doc) > 100 else doc
                print(f"  • {preview}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 simple_rag.py add 'Your text here'")
        print("  python3 simple_rag.py query 'Search for something'")
        print("  python3 simple_rag.py stats")
        sys.exit(1)
    
    rag = SimpleRAG()
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Provide text to add")
            sys.exit(1)
        
        text = sys.argv[2]
        rag.add_memory(text)
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("Error: Provide search query")
            sys.exit(1)
        
        query = sys.argv[2]
        results = rag.query_memory(query)
        
        print(f"\n=== Search Results for: '{query}' ===\n")
        
        for i, doc in enumerate(results['documents'][0], 1):
            print(f"{i}. {doc}\n")
    
    elif command == "stats":
        rag.show_stats()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()