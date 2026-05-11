#!/usr/bin/env python3
"""Analyze conversation exports before indexing"""
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent / "imports"

print("=" * 60)
print("EXPORT ANALYSIS")
print("=" * 60)

# Check ChatGPT
gpt_path = BASE / "chatgpt" / "conversations.json"
if gpt_path.exists():
    with open(gpt_path) as f:
        gpt = json.load(f)
    
    dates = []
    for c in gpt:
        if c.get("update_time"):
            dates.append(c["update_time"])
        elif c.get("create_time"):
            dates.append(c["create_time"])
    
    dates = sorted([d for d in dates if d])
    if dates:
        oldest = datetime.fromtimestamp(dates[0]).strftime("%Y-%m-%d")
        newest = datetime.fromtimestamp(dates[-1]).strftime("%Y-%m-%d")
        print(f"\n📗 ChatGPT: {len(gpt)} conversations")
        print(f"   Date range: {oldest} → {newest}")

# Check Claude
claude_path = BASE / "claude" / "conversations.json"
if claude_path.exists():
    with open(claude_path) as f:
        claude = json.load(f)
    
    dates = []
    for c in claude:
        if c.get("updated_at"):
            dates.append(c["updated_at"])
        elif c.get("created_at"):
            dates.append(c["created_at"])
    
    dates = sorted(dates)
    if dates:
        print(f"\n📙 Claude: {len(claude)} conversations")
        print(f"   Date range: {dates[0][:10]} → {dates[-1][:10]}")

# Check memories
mem_path = BASE / "claude" / "memories.json"
if mem_path.exists():
    with open(mem_path) as f:
        memories = json.load(f)
    print(f"\n📔 Claude Memories: {len(memories)} entries")

# Check Grok
grok_path = BASE / "grok" / "prod-grok-backend.json"
if grok_path.exists():
    with open(grok_path) as f:
        grok = json.load(f)
    convos = grok.get("conversations", [])
    print(f"\n📘 Grok: {len(convos)} conversations")

total = len(gpt) if gpt_path.exists() else 0
total += len(claude) if claude_path.exists() else 0
print(f"\n{'=' * 60}")
print(f"📊 TOTAL: {total} conversations to index")
print(f"{'=' * 60}")
