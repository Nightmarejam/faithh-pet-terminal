#!/usr/bin/env python3
"""Search GPT conversations for embedding/BGE/reindex discussions."""
import json
from datetime import datetime
from pathlib import Path

conv_path = Path.home() / 'ai-stack/AI_Chat_Exports/Chat_GPT_Chats/Chat_GPT_Exports/conversations.json'

with open(conv_path, 'r') as f:
    data = json.load(f)

# Search terms
search_terms = ['BGE', 'bge-m3', 'embedding', 'reindex', 'chromadb', 'vector', '768', '384', 'mpnet']

print("=== Conversations mentioning embeddings/reindexing ===\n")

for conv in data:
    title = conv.get('title', 'Untitled')
    create_time = conv.get('create_time', 0)
    conv_id = conv.get('id', 'no-id')
    
    # Check title first
    title_match = any(term.lower() in title.lower() for term in search_terms)
    
    # Check content
    content_match = False
    mapping = conv.get('mapping', {})
    for node_id, node in mapping.items():
        msg = node.get('message')
        if msg and msg.get('content') and msg['content'].get('parts'):
            text = '\n'.join(msg['content']['parts']).lower()
            if any(term.lower() in text for term in search_terms):
                content_match = True
                break
    
    if title_match or content_match:
        if create_time:
            dt = datetime.fromtimestamp(create_time)
            days_ago = (datetime.now() - dt).days
            print(f"[{dt.strftime('%Y-%m-%d')}] ({days_ago}d ago) {title[:60]}")
            print(f"  ID: {conv_id}")
            print(f"  Match: {'title' if title_match else 'content'}")
            print()
