#!/usr/bin/env python3
"""Extract recent GPT conversations relevant to FAITHH/PML work."""
import json
from datetime import datetime
from pathlib import Path

# Load the conversations
conv_path = Path.home() / 'ai-stack/AI_Chat_Exports/Chat_GPT_Chats/Chat_GPT_Exports/conversations.json'
print(f"Loading {conv_path}...")

with open(conv_path, 'r') as f:
    data = json.load(f)

print(f"Total conversations: {len(data)}")

# Keywords to search for
keywords = ['FAITHH', 'PML', 'Phase Mediation', 'Harmony', 'backend', 'Constella', 
            'provider', 'Groq', 'temp_v2', 'Wu Xing', 'mediation', 'Earth', 'tier']

recent = []

for conv in data:
    title = conv.get('title', 'Untitled')
    create_time = conv.get('create_time', 0)
    
    if create_time:
        dt = datetime.fromtimestamp(create_time)
        # Only last 45 days
        if (datetime.now() - dt).days <= 45:
            # Check if any keyword in title
            if any(kw.lower() in title.lower() for kw in keywords):
                recent.append({
                    'title': title,
                    'date': dt.strftime('%Y-%m-%d'),
                    'id': conv.get('id', 'no-id'),
                    'mapping': conv.get('mapping', {})
                })

print(f"\n=== Recent FAITHH/PML Conversations ({len(recent)}) ===")
for i, r in enumerate(sorted(recent, key=lambda x: x['date'], reverse=True)[:25], 1):
    print(f"{i:2}. [{r['date']}] {r['title'][:70]}")
    print(f"     ID: {r['id']}")

# Save the filtered conversations for detailed review
output_path = Path.home() / 'ai-stack/AI_Chat_Exports/recent_faithh_convos.json'
with open(output_path, 'w') as f:
    json.dump(sorted(recent, key=lambda x: x['date'], reverse=True), f, indent=2)
print(f"\nSaved {len(recent)} conversations to: {output_path}")
