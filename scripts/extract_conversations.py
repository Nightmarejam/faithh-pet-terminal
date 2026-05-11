#!/usr/bin/env python3
"""
Extract and prepare conversations for ChromaDB indexing
"""

import json
import os
from pathlib import Path
from datetime import datetime

def extract_chatgpt_conversations(file_path):
    """Extract messages from ChatGPT export format"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    conversations = []
    for conv in data:
        title = conv.get('title', 'Untitled')
        conv_id = conv.get('conversation_id', conv.get('id', 'unknown'))
        create_time = conv.get('create_time', 0)
        
        # Extract messages from mapping
        mapping = conv.get('mapping', {})
        messages = []
        
        for node_id, node in mapping.items():
            if node.get('message'):
                msg = node['message']
                content = msg.get('content', {})
                
                # Handle different content formats
                if isinstance(content, dict):
                    parts = content.get('parts', [])
                    text = ' '.join(part if isinstance(part, str) else str(part) for part in parts)
                else:
                    text = str(content)
                
                if text.strip():
                    messages.append({
                        'role': msg.get('author', {}).get('role', 'unknown'),
                        'text': text,
                        'timestamp': msg.get('create_time', create_time)
                    })
        
        if messages:
            conversations.append({
                'id': conv_id,
                'title': title,
                'messages': messages,
                'source': 'chatgpt',
                'created': datetime.fromtimestamp(create_time).isoformat()
            })
    
    return conversations

def extract_claude_conversations(file_path):
    """Extract messages from Claude export format"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    conversations = []
    for conv in data:
        conversations.append({
            'id': conv.get('id', 'unknown'),
            'title': conv.get('title', 'Untitled'),
            'messages': conv.get('messages', []),
            'source': 'claude',
            'created': conv.get('created', datetime.now().isoformat())
        })
    
    return conversations

def prepare_for_chromadb(conversations, output_file):
    """Prepare conversations for ChromaDB indexing"""
    documents = []
    metadatas = []
    ids = []
    
    for conv in conversations:
        # Create a document from the entire conversation
        full_text = []
        for msg in conv['messages']:
            role = msg.get('role', 'unknown')
            text = msg.get('text', '')
            if text.strip():
                full_text.append(f"{role.title()}: {text}")
        
        if full_text:
            doc_text = "\n".join(full_text)
            
            documents.append(doc_text)
            metadatas.append({
                'conversation_id': conv['id'],
                'title': conv['title'],
                'source': conv['source'],
                'message_count': len(conv['messages']),
                'created': conv['created'],
                'indexed': datetime.now().isoformat()
            })
            ids.append(conv['id'])
    
    # Save prepared data
    prepared = {
        'documents': documents,
        'metadatas': metadatas,
        'ids': ids
    }
    
    with open(output_file, 'w') as f:
        json.dump(prepared, f, indent=2)
    
    return len(documents)

def main():
    base_dir = Path("/home/jonat/ai-stack/AI_Chat_Exports/01-19-2026 Exports")
    output_dir = Path("/home/jonat/ai-stack/knowledge_base/extracted")
    output_dir.mkdir(exist_ok=True)
    
    all_conversations = []
    
    # Process ChatGPT exports
    chatgpt_dir = base_dir / "ChatGPT"
    if (chatgpt_dir / "conversations.json").exists():
        print("Processing ChatGPT conversations...")
        convs = extract_chatgpt_conversations(chatgpt_dir / "conversations.json")
        all_conversations.extend(convs)
        print(f"Extracted {len(convs)} ChatGPT conversations")
    
    # Process Claude exports
    claude_dir = base_dir / "Claude"
    for json_file in claude_dir.glob("*.json"):
        print(f"Processing {json_file.name}...")
        try:
            convs = extract_claude_conversations(json_file)
            all_conversations.extend(convs)
            print(f"Extracted {len(convs)} conversations from {json_file.name}")
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    # Prepare for ChromaDB
    output_file = output_dir / "conversations_for_chromadb.json"
    doc_count = prepare_for_chromadb(all_conversations, output_file)
    
    print(f"\n✅ Extraction Complete!")
    print(f"Total conversations: {len(all_conversations)}")
    print(f"Documents prepared: {doc_count}")
    print(f"Output: {output_file}")
    
    # Save raw conversations for reference
    raw_output = output_dir / "raw_conversations.json"
    with open(raw_output, 'w') as f:
        json.dump(all_conversations, f, indent=2)
    
    print(f"Raw data saved to: {raw_output}")

if __name__ == "__main__":
    main()
