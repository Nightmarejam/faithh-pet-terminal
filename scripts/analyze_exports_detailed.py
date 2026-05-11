#!/usr/bin/env python3
"""Detailed analysis of AI Chat Exports - what's new, what's indexed, what can be removed."""
import json
import os
from pathlib import Path
from datetime import datetime
import zipfile

EXPORTS_DIR = Path("/home/jonat/ai-stack/AI_Chat_Exports")

def get_file_info(filepath):
    """Get file size and modification time."""
    stat = filepath.stat()
    return {
        "size_mb": stat.st_size / 1024 / 1024,
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
    }

def count_conversations_in_json(filepath):
    """Count conversations in a JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            # ChatGPT format often has conversations as values
            return len(data)
    except:
        return -1

print("=" * 70)
print("DETAILED AI CHAT EXPORTS ANALYSIS")
print("=" * 70)

# 1. Analyze the new zip files
print("\n## NEW ZIP FILES (to be indexed)")
print("-" * 70)

new_zips = []
for f in EXPORTS_DIR.glob("*.zip"):
    if "Zone.Identifier" in f.name:
        continue
    info = get_file_info(f)
    
    # Check contents
    try:
        with zipfile.ZipFile(f, 'r') as zf:
            names = zf.namelist()
            json_files = [n for n in names if n.endswith('.json')]
            conv_files = [n for n in json_files if 'conversation' in n.lower()]
    except Exception as e:
        json_files = []
        conv_files = []
    
    new_zips.append({
        "name": f.name[:50] + "..." if len(f.name) > 50 else f.name,
        "full_name": f.name,
        "size_mb": info["size_mb"],
        "mtime": info["mtime"],
        "json_files": json_files,
        "conv_files": conv_files
    })
    
    print(f"\n📦 {f.name[:60]}...")
    print(f"   Size: {info['size_mb']:.2f} MB | Modified: {info['mtime']}")
    print(f"   JSON files: {len(json_files)} | Conversation files: {conv_files}")

# 2. Analyze existing extracted folders
print("\n\n## EXISTING EXTRACTED EXPORTS")
print("-" * 70)

existing_data = {}
for subdir in ["Chat_GPT_Exports", "Claude_Exports", "Grok_Exports", "01-19-2026 Exports"]:
    subpath = EXPORTS_DIR / subdir
    if not subpath.exists():
        continue
    
    files = list(subpath.rglob("*"))
    json_files = [f for f in files if f.suffix == '.json']
    total_size = sum(f.stat().st_size for f in files if f.is_file()) / 1024 / 1024
    
    existing_data[subdir] = {
        "total_files": len([f for f in files if f.is_file()]),
        "json_files": len(json_files),
        "total_size_mb": total_size
    }
    
    print(f"\n📁 {subdir}/")
    print(f"   Files: {existing_data[subdir]['total_files']} | JSON: {existing_data[subdir]['json_files']} | Size: {total_size:.2f} MB")
    
    # List JSON files
    for jf in json_files[:5]:
        conv_count = count_conversations_in_json(jf)
        print(f"      - {jf.name} ({conv_count} items)")
    if len(json_files) > 5:
        print(f"      ... and {len(json_files) - 5} more JSON files")

# 3. Analyze standalone JSON files
print("\n\n## STANDALONE JSON FILES")
print("-" * 70)

for f in EXPORTS_DIR.glob("*.json"):
    info = get_file_info(f)
    conv_count = count_conversations_in_json(f)
    print(f"\n📄 {f.name}")
    print(f"   Size: {info['size_mb']:.2f} MB | Modified: {info['mtime']} | Items: {conv_count}")

# 4. Files that can be safely removed
print("\n\n## FILES SAFE TO REMOVE")
print("-" * 70)

removable = []
for f in EXPORTS_DIR.glob("*.Identifier"):
    removable.append(f.name)
    print(f"   🗑️ {f.name} (Windows zone identifier)")

for f in EXPORTS_DIR.glob("*Zone.Identifier"):
    if f.name not in [r for r in removable]:
        removable.append(f.name)
        print(f"   🗑️ {f.name} (Windows zone identifier)")

# Check for empty directories
for subdir in EXPORTS_DIR.iterdir():
    if subdir.is_dir():
        contents = list(subdir.iterdir())
        if len(contents) == 0:
            print(f"   🗑️ {subdir.name}/ (empty directory)")

# 5. Summary and recommendations
print("\n\n" + "=" * 70)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 70)

print("""
## What needs to be indexed:

1. **Large ChatGPT ZIP** (238 MB)
   - Contains: conversations-000.json, conversations-001.json, conversations-002.json
   - This is your main ChatGPT export with all conversations
   - Action: Extract and index with scripts/indexing/index_chatgpt_chats.py

2. **Claude ZIP** (12 MB → 63 MB uncompressed)
   - Contains: conversations.json, projects.json, memories.json
   - This is your Claude export
   - Action: Extract and index with scripts/indexing/index_claude_chats.py

## What can be removed after indexing:

1. **.zipZone.Identifier files** - Windows metadata, safe to delete now
2. **Old exports in Chat_GPT_Exports/** - If the new ZIP supersedes them
3. **Old exports in Claude_Exports/** - If the new ZIP supersedes them
4. **01-19-2026 Exports/** - Check if these are already processed

## Automation opportunities:

1. Create a unified indexing script that:
   - Detects new exports (by checking file dates vs last index date)
   - Extracts zips to temp location
   - Parses and chunks conversations
   - Indexes to ChromaDB
   - Logs what was indexed

2. Schedule periodic re-indexing (cron or manual trigger)

3. Add a "last indexed" metadata field to track freshness
""")
