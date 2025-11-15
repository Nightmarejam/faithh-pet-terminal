#!/usr/bin/env python3
"""
FAITHH RAG System Setup
Loads your existing embedding shards into ChromaDB for retrieval
"""

import chromadb
import json
import os
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure paths (adjust these to match your setup)
EMBEDDINGS_DIR = Path("C:/Users/jonat/Documents/FAITHH/imports/inbox/shards_20250827_051056/vectors")
CHROMADB_PATH = Path("C:/Users/jonat/Documents/FAITHH/chromadb")

def load_embedding_shards(embeddings_dir: Path) -> List[Dict]:
    """Load all embedding shard files"""
    all_embeddings = []
    
    shard_files = sorted(embeddings_dir.glob("embeddings_shard_*.jsonl"))
    logger.info(f"Found {len(shard_files)} shard files")
    
    for shard_file in shard_files:
        logger.info(f"Loading {shard_file.name}...")
        with open(shard_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    all_embeddings.append(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Error in {shard_file.name} line {line_num}: {e}")
    
    logger.info(f"Loaded {len(all_embeddings)} total embeddings")
    return all_embeddings

def create_chromadb_collection(db_path: Path, embeddings: List[Dict]):
    """Create ChromaDB collection and load embeddings"""
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=str(db_path))
    
    # Create or get collection
    collection_name = "chatgpt_conversations"
    try:
        # Try to delete existing collection if it exists
        client.delete_collection(collection_name)
        logger.info(f"Deleted existing collection: {collection_name}")
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "ChatGPT conversation embeddings for RAG"}
    )
    
    # Prepare data for batch insertion
    ids = []
    vectors = []
    metadatas = []
    documents = []
    
    for idx, emb in enumerate(embeddings):
        # Generate ID if not present
        doc_id = emb.get('id', f"doc_{idx}")
        ids.append(str(doc_id))
        
        # Extract vector (handle different possible formats)
        if 'vector' in emb:
            vectors.append(emb['vector'])
        elif 'embedding' in emb:
            vectors.append(emb['embedding'])
        else:
            logger.warning(f"No vector found in embedding {idx}")
            continue
        
        # Extract text content
        text = emb.get('text', emb.get('content', ''))
        documents.append(text)
        
        # Store metadata
        metadata = {
            'source': emb.get('source', 'chatgpt'),
            'timestamp': emb.get('timestamp', ''),
            'conversation_id': emb.get('conversation_id', ''),
            'message_type': emb.get('type', 'unknown')
        }
        metadatas.append(metadata)
    
    # Batch insert into ChromaDB
    logger.info(f"Inserting {len(ids)} documents into ChromaDB...")
    batch_size = 5000
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end_idx],
            embeddings=vectors[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        logger.info(f"Inserted batch {i//batch_size + 1} ({end_idx}/{len(ids)} documents)")
    
    logger.info("✓ ChromaDB setup complete!")
    return collection

def test_query(collection, query: str = "What is FAITHH?"):
    """Test the RAG system with a sample query"""
    logger.info(f"\nTesting query: '{query}'")
    
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    logger.info("\nTop 3 results:")
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        logger.info(f"\n{i}. Distance: {distance:.4f}")
        logger.info(f"   Source: {metadata.get('source', 'unknown')}")
        logger.info(f"   Text: {doc[:200]}...")

def main():
    """Main setup pipeline"""
    logger.info("Starting FAITHH RAG Setup...")
    
    # Check if embeddings directory exists
    if not EMBEDDINGS_DIR.exists():
        logger.error(f"Embeddings directory not found: {EMBEDDINGS_DIR}")
        logger.info("Please update EMBEDDINGS_DIR path in script")
        return
    
    # Load embeddings
    embeddings = load_embedding_shards(EMBEDDINGS_DIR)
    if not embeddings:
        logger.error("No embeddings loaded!")
        return
    
    # Create ChromaDB
    CHROMADB_PATH.mkdir(parents=True, exist_ok=True)
    collection = create_chromadb_collection(CHROMADB_PATH, embeddings)
    
    # Test the system
    test_query(collection)
    
    logger.info("\n✓ RAG system ready!")
    logger.info(f"ChromaDB location: {CHROMADB_PATH}")

if __name__ == "__main__":
    main()