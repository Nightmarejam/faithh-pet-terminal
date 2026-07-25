#!/usr/bin/env python3
"""
Claude Chat Export Parser and Indexer
Extracts conversations from Claude export and indexes them into ChromaDB
"""

import json
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from datetime import datetime
import hashlib

# Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION_NAME = "documents_768"
CLAUDE_EXPORT = Path.home() / "ai-stack" / "AI_Chat_Exports" / "Claude_Chats" / "conversations.json"

def get_conversation_hash(conv_uuid):
    """Create unique ID from conversation UUID"""
    return f"claude_conv_{conv_uuid}"

def parse_message_content(message):
    """Extract text from message content array"""
    texts = []
    for content in message.get('content', []):
        if content.get('type') == 'text':
            texts.append(content.get('text', ''))
    return '\n'.join(texts)

def format_conversation(conv):
    """Format a conversation into indexable text"""
    name = conv.get('name', 'Untitled Conversation')
    created = conv.get('created_at', '')
    updated = conv.get('updated_at', '')
    messages = conv.get('chat_messages', [])
    
    # Header
    text = f"# Claude Conversation: {name}\n\n"
    text += f"Created: {created}\n"
    text += f"Updated: {updated}\n"
    text += f"Messages: {len(messages)}\n\n"
    text += "---\n\n"
    
    # Messages
    for msg in messages:
        sender = msg.get('sender', 'unknown')
        timestamp = msg.get('created_at', '')
        content = parse_message_content(msg)
        
        if content:  # Only include if there's actual text
            text += f"**{sender.upper()}** ({timestamp}):\n{content}\n\n"
    
    return text

def main():
    print("=" * 70)
    print("CLAUDE CHAT EXPORT INDEXER")
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
    
    # Index conversations
    print(f"\n3. Indexing {len(conversations_with_messages)} conversations...")
    
    indexed = 0
    skipped = 0
    errors = 0
    
    batch_size = 10
    batch_ids = []
    batch_docs = []
    batch_metas = []
    
    for i, conv in enumerate(conversations_with_messages):
        try:
            conv_id = get_conversation_hash(conv['uuid'])
            
            # Check if already indexed
            try:
                existing = collection.get(ids=[conv_id], include=[])
                if existing['ids']:
                    skipped += 1
                    continue
            except:
                pass
            
            # Format conversation
            text = format_conversation(conv)
            
            # Skip if no meaningful content
            if len(text) < 100:
                skipped += 1
                continue
            
            # Metadata
            metadata = {
                'source': f"Claude Chat: {conv.get('name', 'Untitled')}",
                'category': 'claude_conversation',
                'created_at': conv.get('created_at', ''),
                'updated_at': conv.get('updated_at', ''),
                'message_count': len(conv.get('chat_messages', [])),
                'hash': hashlib.md5(conv['uuid'].encode()).hexdigest()
            }
            
            batch_ids.append(conv_id)
            batch_docs.append(text)
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
                    print(f"   Indexed batch {(i//batch_size)+1}: {len(batch_ids)} conversations")
                    
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
            print(f"   ⚠️  Error processing conversation {i}: {e}")
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
            print(f"   Indexed final batch: {len(batch_ids)} conversations")
        except Exception as e:
            print(f"   ⚠️  Error indexing final batch: {e}")
            errors += len(batch_ids)
    
    print(f"\n4. Indexing complete!")
    print(f"   ✅ Indexed: {indexed} conversations")
    print(f"   ⏭️  Skipped: {skipped} (already indexed or too short)")
    print(f"   ❌ Errors:  {errors}")
    print(f"   📊 Total in collection: {collection.count()}")
    
    # Test query
    print(f"\n5. Testing indexed conversations...")
    test_queries = [
        "FAITHH Professional Backend development",
        "Project FAITHH environment setup",
        "ChromaDB RAG system"
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=2,
            where={"category": "claude_conversation"}
        )
        
        if results['documents'] and results['documents'][0]:
            print(f"   ✅ '{query[:50]}...'")
            print(f"      Found: {results['metadatas'][0][0]['source']}")
        else:
            print(f"   ⚠️  '{query}' - No results")
    
    print("\n" + "=" * 70)
    print("INDEXING COMPLETE")
    print("=" * 70)
    print("\n💡 Now ask FAITHH: 'What did we discuss about FAITHH development?'")

if __name__ == "__main__":
    main()
