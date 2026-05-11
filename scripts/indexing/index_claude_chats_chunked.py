#!/usr/bin/env python3
"""
FAITHH Claude Chat Chunked Indexer
Indexes Claude conversations by breaking them into semantic chunks
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import sys

def load_conversations(json_path):
    """Load Claude conversations from export JSON"""
    print(f"\n1. Loading conversations from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    with_messages = [c for c in conversations if c.get('chat_messages')]
    print(f"✅ Loaded {len(conversations)} conversations")
    print(f"   {len(with_messages)} have messages")
    return with_messages

def chunk_conversation(conversation):
    """Break conversation into semantic chunks based on topic shifts"""
    chunks = []
    messages = conversation.get('chat_messages', [])
    
    if not messages:
        return chunks
    
    conv_name = conversation.get('name', 'Untitled')
    conv_uuid = conversation.get('uuid', '')
    created_at = conversation.get('created_at', '')
    
    # Strategy: Chunk by message pairs (user + assistant)
    current_chunk = []
    chunk_num = 1
    
    for i, msg in enumerate(messages):
        sender = msg.get('sender', 'unknown')
        text = msg.get('text', '')
        
        # Skip empty messages
        if not text.strip():
            continue
        
        current_chunk.append(f"{sender.upper()}: {text}")
        
        # Create chunk every 3-4 exchanges or at end
        if len(current_chunk) >= 6 or i == len(messages) - 1:
            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                
                # Create chunk metadata
                chunk_id = f"{conv_uuid}_chunk_{chunk_num}"
                chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()
                
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'metadata': {
                        'source': f"Claude Chat: {conv_name} (Part {chunk_num})",
                        'conversation_name': conv_name,
                        'conversation_uuid': conv_uuid,
                        'chunk_number': chunk_num,
                        'created_at': created_at,
                        'category': 'claude_conversation_chunk',
                        'type': 'conversation',
                        'hash': chunk_hash
                    }
                })
                
                chunk_num += 1
                current_chunk = []
    
    return chunks

def index_conversations(conversations, collection):
    """Index conversation chunks into ChromaDB"""
    print(f"\n3. Chunking and indexing {len(conversations)} conversations...")
    
    all_chunks = []
    for conv in conversations:
        chunks = chunk_conversation(conv)
        all_chunks.extend(chunks)
    
    print(f"✅ Created {len(all_chunks)} chunks from conversations")
    
    # Check for existing chunks
    existing_hashes = set()
    try:
        results = collection.get(
            where={"category": "claude_conversation_chunk"},
            include=['metadatas']
        )
        for meta in results['metadatas']:
            if 'hash' in meta:
                existing_hashes.add(meta['hash'])
    except:
        pass
    
    # Filter out duplicates
    new_chunks = [c for c in all_chunks if c['metadata']['hash'] not in existing_hashes]
    
    if not new_chunks:
        print("⏭️  All chunks already indexed!")
        return 0, len(all_chunks)
    
    print(f"📝 Indexing {len(new_chunks)} new chunks...")
    
    # Index in batches
    batch_size = 20
    indexed = 0
    
    for i in range(0, len(new_chunks), batch_size):
        batch = new_chunks[i:i + batch_size]
        
        ids = [c['id'] for c in batch]
        documents = [c['text'] for c in batch]
        metadatas = [c['metadata'] for c in batch]
        
        try:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            indexed += len(batch)
            print(f"   Indexed batch {i//batch_size + 1}: {len(batch)} chunks")
        except Exception as e:
            print(f"   ⚠️  Error in batch {i//batch_size + 1}: {e}")
    
    return indexed, len(all_chunks) - indexed

def test_search(collection):
    """Test search with sample queries"""
    print("\n5. Testing chunked conversations...")
    
    test_queries = [
        "FAITHH backend development",
        "ChromaDB and RAG system",
        "Project FAITHH environment setup",
        "Langflow dockerfile configuration"
    ]
    
    for query in test_queries:
        try:
            results = collection.query(
                query_texts=[query],
                n_results=3,
                where={"category": "claude_conversation_chunk"}
            )
            
            if results['documents'][0]:
                top_result = results['metadatas'][0][0]
                distance = results['distances'][0][0]
                print(f"   ✅ '{query}...'")
                print(f"      Found: {top_result['source']} (similarity: {1-distance:.2f})")
            else:
                print(f"   ❌ '{query}' - No results")
        except Exception as e:
            print(f"   ⚠️  Error testing '{query}': {e}")

def main():
    print("=" * 70)
    print("CLAUDE CHAT CHUNKED INDEXER")
    print("=" * 70)
    
    # Paths
    export_path = Path.home() / "ai-stack/AI_Chat_Exports/Claude_Chats/conversations.json"
    
    if not export_path.exists():
        print(f"❌ File not found: {export_path}")
        sys.exit(1)
    
    # Load conversations
    conversations = load_conversations(export_path)
    
    if not conversations:
        print("❌ No conversations with messages found!")
        sys.exit(1)
    
    # Connect to ChromaDB
    print("\n2. Connecting to ChromaDB at localhost:8000...")
    try:
        client = chromadb.HttpClient(host="localhost", port=8000)
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"
        )
        collection = client.get_collection(
            name="documents_768",
            embedding_function=embedding_func
        )
        print(f"✅ Connected to collection 'documents_768'")
        print(f"   Current documents: {collection.count()}")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        sys.exit(1)
    
    # Index conversations
    indexed, skipped = index_conversations(conversations, collection)
    
    print("\n4. Indexing complete!")
    print(f"   ✅ Indexed: {indexed} new chunks")
    print(f"   ⏭️  Skipped: {skipped} (already indexed)")
    print(f"   📊 Total in collection: {collection.count()}")
    
    # Test search
    test_search(collection)
    
    print("\n" + "=" * 70)
    print("CHUNKING COMPLETE")
    print("=" * 70)
    print("\n💡 Now ask FAITHH more specific questions:")
    print("   'What did we discuss about FAITHH backend?'")
    print("   'Tell me about ChromaDB setup'")
    print("   'What was our plan for Langflow?'")
    print()

if __name__ == "__main__":
    main()
