#!/usr/bin/env python3
"""Extract specific conversations by ID for review."""
import json
from pathlib import Path

conv_path = Path.home() / 'ai-stack/AI_Chat_Exports/Chat_GPT_Chats/Chat_GPT_Exports/conversations.json'

# Target conversation IDs
target_ids = [
    '693dd9e1-5a4c-8333-91b0-ffd90588f2b0',  # Backend handoff document review
    '6938f259-cfc8-8329-bb9c-ce8db107c4d9',  # Brain function model
    '6938f02f-3380-8331-83bd-7a9e8424105b',  # Consciousness architecture model
    '693b2678-4fc4-8331-bac1-44bfd558e0de',  # RTX 3090 LLM guide
]

with open(conv_path, 'r') as f:
    data = json.load(f)

def extract_messages(mapping):
    """Extract messages in order from GPT conversation mapping."""
    messages = []
    for node_id, node in mapping.items():
        msg = node.get('message')
        if msg and msg.get('content') and msg['content'].get('parts'):
            role = msg.get('author', {}).get('role', 'unknown')
            text = '\n'.join(msg['content']['parts'])
            create_time = msg.get('create_time', 0)
            if text.strip():
                messages.append({
                    'role': role,
                    'text': text,
                    'time': create_time
                })
    # Sort by time
    return sorted(messages, key=lambda x: x['time'] if x['time'] else 0)

for conv in data:
    if conv.get('id') in target_ids:
        title = conv.get('title', 'Untitled')
        print(f"\n{'='*80}")
        print(f"CONVERSATION: {title}")
        print(f"ID: {conv.get('id')}")
        print('='*80)
        
        messages = extract_messages(conv.get('mapping', {}))
        
        # Print first 3000 chars of each message (truncated for overview)
        for i, msg in enumerate(messages[:30], 1):  # First 30 messages
            role = msg['role'].upper()
            text = msg['text'][:2000] + ('...[truncated]' if len(msg['text']) > 2000 else '')
            print(f"\n--- {role} [{i}] ---")
            print(text)
        
        if len(messages) > 30:
            print(f"\n... [{len(messages) - 30} more messages] ...")
        
        print(f"\n[END OF {title}]")
