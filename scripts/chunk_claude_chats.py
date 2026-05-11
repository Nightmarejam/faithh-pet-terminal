#!/usr/bin/env python3
"""
Claude Chat Chunker - Better Semantic Matching
Breaks long conversations into topical chunks for better RAG retrieval
"""

import json
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from datetime import datetime
import hashlib
import re

# Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION_NAME = "documents_768"
CLAUDE_EXPORT = Path.home() / "ai-stack" / "AI_Chat_Exports" / "Claude_Chats" / "conversations.json"

def get_chunk_id(conv_uuid, chunk_num):
    """Create unique ID for conversation chunk"""
    return f"claude_chunk_{conv_uuid}_{chunk_num}"

def parse_message_content(message):
    """Extract text from message content array"""
    texts = []
    for content in message.get('content', []):
        if content.get('type') == 'text':
            texts.append(content.get('text', ''))
    return '\n'.join(texts)

def chunk_conversation(conv, chunk_size=5):
    """Break conversation into chunks of N message pairs"""
    name = conv.get('name', 'Untitled Conversation')
    created = conv.get('created_at', '')
    messages = conv.get('chat_messages', [])
    
    chunks = []
    for i in range(0, len(messages), chunk_size):
        chunk_messages = messages[i:i+chunk_size]
        
        # Create chunk header
        chunk_text = f"# {name} (Part {i//chunk_size + 1})\n\n"
        chunk_text += f"Created: {created}\n"
        chunk_text += f"Messages in chunk: {len(chunk_messages)}\n\n"
        chunk_text += "---\n\n"
        
        # Add messages
        for msg in chunk_messages:
            sender = msg.get('sender', 'unknown')
            timestamp = msg.get('created_at', '')
            content = parse_message_content(msg)
            
            if content:
                # Clean up content
                content = content.strip()
                chunk_text += f"**{sender.upper()}**:\n{content}\n\n"
        
        # Only add if has substantial content
        if len(chunk_text) > 200:
            chunks.append({
                'text': chunk_text,
                'chunk_num': i // chunk_size,
                'message_count': len(chunk_messages),
                'first_message': chunk_messages[0].get('created_at', '') if chunk_messages else ''
            })
    
    return chunks

def main():
    print("=" * 70)
    print("CLAUDE CHAT CHUNKER - BETTER SEMANTIC MATCHING")
    print("=" * 70)
    
    # Load conversations
    print(f"\n1. Loading conversations from {CLAUDE_EXPORT}...")
    try:
        with open(CLAUDE_EXPORT, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    print(f"✅ Loaded {len(conversations)} conversations")
    
    # Filter conversations with messages
    conversations_with_messages = [c for c in conversations if c.get('chat_messages')]
    print(f"   {len(conversations_with_messages)} have messages")
    
    # Connect to ChromaDB
    print(f"\n2. Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"
        )
        
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func
        )
        
        print(f"✅ Connected to collection '{COLLECTION_NAME}'")
        print(f"   Current documents: {collection.count()}")
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")
        return
    
    # Delete old conversation entries (they'll be replaced with chunks)
    print(f"\n3. Removing old full conversation entries...")
    try:
        # Get all claude_conversation documents
        old_convs = collection.get(
            where={"category": "claude_conversation"},
            include=['ids']
        )
        
        if old_convs['ids']:
            collection.delete(ids=old_convs['ids'])
            print(f"   ✅ Removed {len(old_convs['ids'])} old conversation entries")
        else:
            print(f"   ℹ️  No old entries to remove")
    except Exception as e:
        print(f"   ⚠️  Error removing old entries: {e}")
    
    # Chunk and index conversations
    print(f"\n4. Chunking and indexing conversations...")
    
    total_chunks = 0
    indexed = 0
    errors = 0
    
    batch_size = 10
    batch_ids = []
    batch_docs = []
    batch_metas = []
    
    for conv in conversations_with_messages:
        try:
            chunks = chunk_conversation(conv, chunk_size=5)  # 5 message pairs per chunk
            total_chunks += len(chunks)
            
            for chunk in chunks:
                chunk_id = get_chunk_id(conv['uuid'], chunk['chunk_num'])
                
                # Metadata
                metadata = {
                    'source': f"Claude: {conv.get('name', 'Untitled')} (Part {chunk['chunk_num']+1})",
                    'category': 'claude_conversation_chunk',
                    'conversation_name': conv.get('name', 'Untitled'),
                    'created_at': conv.get('created_at', ''),
                    'chunk_num': chunk['chunk_num'],
                    'message_count': chunk['message_count'],
                    'hash': hashlib.md5(chunk_id.encode()).hexdigest()
                }
                
                batch_ids.append(chunk_id)
                batch_docs.append(chunk['text'])
                batch_metas.append(metadata)
                
                # Add batch when full
                if len(batch_ids) >= batch_size:
                    try:
                        collection.add(
                            ids=batch_ids,
                            documents=batch_docs,
                            metadatas=batch_metas
                        )
                        indexed += len(batch_ids)
                        
                        batch_ids = []
                        batch_docs = []
                        batch_metas = []
                    except Exception as e:
                        print(f"   ⚠️  Error indexing batch: {e}")
                        errors += len(batch_ids)
                        batch_ids = []
                        batch_docs = []
                        batch_metas = []
        
        except Exception as e:
            print(f"   ⚠️  Error processing conversation: {e}")
            errors += 1
    
    # Add remaining batch
    if batch_ids:
        try:
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas
            )
            indexed += len(batch_ids)
        except Exception as e:
            print(f"   ⚠️  Error indexing final batch: {e}")
            errors += len(batch_ids)
    
    print(f"\n5. Chunking complete!")
    print(f"   ✅ Created: {total_chunks} chunks from {len(conversations_with_messages)} conversations")
    print(f"   ✅ Indexed: {indexed} chunks")
    print(f"   ❌ Errors:  {errors}")
    print(f"   📊 Total in collection: {collection.count()}")
    
    # Test queries
    print(f"\n6. Testing chunked conversations...")
    test_queries = [
        "FAITHH environment setup",
        "Project FAITHH planning",
        "Langflow dockerfile optimization"
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=2,
            where={"category": "claude_conversation_chunk"}
        )
        
        if results['documents'] and results['documents'][0]:
            print(f"   ✅ '{query}'")
            print(f"      → {results['metadatas'][0][0]['source']}")
        else:
            print(f"   ⚠️  '{query}' - No results")
    
    print("\n" + "=" * 70)
    print("CHUNKING COMPLETE")
    print("=" * 70)
    print("\n💡 Chunks are smaller and more focused for better semantic matching!")
    print("💡 Now restart backend and test FAITHH again")

if __name__ == "__main__":
    main()
