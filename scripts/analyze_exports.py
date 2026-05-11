#!/usr/bin/env python3
"""Analyze AI Chat Exports folder to understand what's new and what can be removed."""
import json
import os
from pathlib import Path
from datetime import datetime
import zipfile

EXPORTS_DIR = Path("/home/jonat/ai-stack/AI_Chat_Exports")

def analyze_json_file(filepath):
    """Analyze a JSON file and return summary."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return {"type": "list", "count": len(data), "size_mb": filepath.stat().st_size / 1024 / 1024}
        elif isinstance(data, dict):
            return {"type": "dict", "keys": list(data.keys())[:10], "count": len(data), "size_mb": filepath.stat().st_size / 1024 / 1024}
    except Exception as e:
        return {"error": str(e)}

def analyze_zip_file(filepath):
    """Analyze a zip file and return summary."""
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            names = zf.namelist()
            json_files = [n for n in names if n.endswith('.json')]
            return {
                "total_files": len(names),
                "json_files": json_files,
                "size_mb": filepath.stat().st_size / 1024 / 1024
            }
    except Exception as e:
        return {"error": str(e)}

print("=" * 60)
print("AI CHAT EXPORTS ANALYSIS")
print("=" * 60)

# List all files
for item in sorted(EXPORTS_DIR.iterdir()):
    if item.is_file():
        size_mb = item.stat().st_size / 1024 / 1024
        mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        
        print(f"\n📄 {item.name}")
        print(f"   Size: {size_mb:.2f} MB | Modified: {mtime}")
        
        if item.suffix == '.json':
            info = analyze_json_file(item)
            if "error" not in info:
                print(f"   Type: {info['type']} | Count: {info.get('count', 'N/A')}")
                if info['type'] == 'dict' and 'keys' in info:
                    print(f"   Keys: {info['keys']}")
            else:
                print(f"   Error: {info['error']}")
        
        elif item.suffix == '.zip':
            info = analyze_zip_file(item)
            if "error" not in info:
                print(f"   Files: {info['total_files']} | JSON: {info['json_files']}")
            else:
                print(f"   Error: {info['error']}")
    
    elif item.is_dir():
        subfiles = list(item.iterdir())
        print(f"\n📁 {item.name}/ ({len(subfiles)} items)")
        for sf in subfiles[:5]:
            print(f"      - {sf.name}")
        if len(subfiles) > 5:
            print(f"      ... and {len(subfiles) - 5} more")

print("\n" + "=" * 60)
print("EXISTING INDEXED DATA CHECK")
print("=" * 60)

# Check what's already indexed
indexed_dir = Path("/home/jonat/ai-stack/AI_Chat_Exports")
chatgpt_dir = indexed_dir / "Chat_GPT_Exports"
claude_dir = indexed_dir / "Claude_Exports"

if chatgpt_dir.exists():
    chatgpt_files = list(chatgpt_dir.glob("**/*.json"))
    print(f"\nChatGPT Exports: {len(chatgpt_files)} JSON files")

if claude_dir.exists():
    claude_files = list(claude_dir.glob("**/*.json"))
    print(f"Claude Exports: {len(claude_files)} JSON files")

# Check ChromaDB indexed count
print("\n" + "=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)
print("""
Based on the analysis:

1. NEW EXPORTS TO INDEX:
   - Large ChatGPT zip (250MB) - contains conversations-000.json
   - Claude zip (13MB) - contains conversations.json (63MB uncompressed)
   - all_recent_convos.json (5.5MB) - likely combined recent conversations
   - recent_faithh_convos.json (700KB) - FAITHH-specific conversations

2. WHAT CAN BE REMOVED (after indexing):
   - .zipZone.Identifier files (Windows metadata, safe to delete)
   - Old exports in Chat_GPT_Exports/ and Claude_Exports/ if superseded
   - 01-19-2026 Exports/ if empty or already processed

3. INDEXING APPROACH:
   - Extract zips to temp location
   - Parse conversations.json from each
   - Chunk and index into ChromaDB
   - Use existing scripts/indexing/ patterns
""")
