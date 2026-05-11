#!/usr/bin/env python3
"""List ALL recent GPT conversations to find the PML/Harmony work."""
import json
from datetime import datetime
from pathlib import Path

conv_path = Path.home() / 'ai-stack/AI_Chat_Exports/Chat_GPT_Chats/Chat_GPT_Exports/conversations.json'

with open(conv_path, 'r') as f:
    data = json.load(f)

print(f"Total conversations: {len(data)}\n")
print("=== ALL Conversations from Last 14 Days ===\n")

recent = []
for conv in data:
    title = conv.get('title', 'Untitled')
    create_time = conv.get('create_time', 0)
    
    if create_time:
        dt = datetime.fromtimestamp(create_time)
        days_ago = (datetime.now() - dt).days
        if days_ago <= 14:
            recent.append({
                'title': title,
                'date': dt.strftime('%Y-%m-%d %H:%M'),
                'days_ago': days_ago,
                'id': conv.get('id'),
                'mapping': conv.get('mapping', {})
            })

# Sort by date
for i, r in enumerate(sorted(recent, key=lambda x: x['date'], reverse=True), 1):
    print(f"{i:2}. [{r['date']}] ({r['days_ago']}d ago)")
    print(f"    {r['title'][:80]}")
    print(f"    ID: {r['id']}")
    print()

print(f"Total recent: {len(recent)}")

# Save all recent for review
output = Path.home() / 'ai-stack/AI_Chat_Exports/all_recent_convos.json'
with open(output, 'w') as f:
    json.dump(sorted(recent, key=lambda x: x['date'], reverse=True), f, indent=2)
print(f"Saved to: {output}")
