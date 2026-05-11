#!/usr/bin/env python3
"""Compare what's indexed in ChromaDB vs what's in the exports folder."""
import json
from pathlib import Path
from datetime import datetime

# Check existing indexing scripts
SCRIPTS_DIR = Path("/home/jonat/ai-stack/scripts/indexing")
EXPORTS_DIR = Path("/home/jonat/ai-stack/AI_Chat_Exports")

print("=" * 70)
print("INDEXED VS EXPORTS COMPARISON")
print("=" * 70)

# 1. Check existing indexing scripts
print("\n## EXISTING INDEXING SCRIPTS")
print("-" * 70)

if SCRIPTS_DIR.exists():
    for script in sorted(SCRIPTS_DIR.glob("*.py")):
        print(f"   📜 {script.name}")
else:
    print("   ⚠️ No scripts/indexing/ directory found")

# 2. Query ChromaDB for indexed conversation stats
print("\n## CHROMADB INDEXED DATA")
print("-" * 70)

try:
    import chromadb
    client = chromadb.HttpClient(host="192.158.1.243", port=8000)
    col = client.get_collection("faithh_knowledge_base")
    
    total_docs = col.count()
    print(f"   Total documents: {total_docs}")
    
    # Sample some documents to understand the data
    sample = col.get(limit=100, include=["metadatas"])
    
    sources = {}
    categories = {}
    for meta in sample.get("metadatas", []):
        if meta:
            src = meta.get("source", "unknown")
            cat = meta.get("category", "unknown")
            sources[src] = sources.get(src, 0) + 1
            categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n   Sample sources (from 100 docs):")
    for src, count in sorted(sources.items(), key=lambda x: -x[1])[:10]:
        print(f"      {src}: {count}")
    
    print(f"\n   Sample categories:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"      {cat}: {count}")

except Exception as e:
    print(f"   ❌ ChromaDB error: {e}")

# 3. Check what conversations are in the exports
print("\n## EXPORT CONVERSATION COUNTS")
print("-" * 70)

export_counts = {}

# Check Claude_Exports
claude_conv = EXPORTS_DIR / "Claude_Exports" / "conversations.json"
if claude_conv.exists():
    try:
        with open(claude_conv) as f:
            data = json.load(f)
        export_counts["Claude_Exports/conversations.json"] = len(data) if isinstance(data, list) else len(data.keys())
    except:
        export_counts["Claude_Exports/conversations.json"] = "error"

# Check Chat_GPT_Exports
chatgpt_conv = EXPORTS_DIR / "Chat_GPT_Exports" / "conversations.json"
if chatgpt_conv.exists():
    try:
        with open(chatgpt_conv) as f:
            data = json.load(f)
        export_counts["Chat_GPT_Exports/conversations.json"] = len(data) if isinstance(data, list) else len(data.keys())
    except:
        export_counts["Chat_GPT_Exports/conversations.json"] = "error"

# Check 01-19-2026 Exports
old_exports = EXPORTS_DIR / "01-19-2026 Exports"
if old_exports.exists():
    for subdir in old_exports.iterdir():
        if subdir.is_dir():
            conv_file = subdir / "conversations.json"
            if conv_file.exists():
                try:
                    with open(conv_file) as f:
                        data = json.load(f)
                    export_counts[f"01-19-2026/{subdir.name}/conversations.json"] = len(data) if isinstance(data, list) else len(data.keys())
                except:
                    export_counts[f"01-19-2026/{subdir.name}/conversations.json"] = "error"

for path, count in export_counts.items():
    print(f"   {path}: {count} conversations")

# 4. Recommendations
print("\n## DEDUPLICATION ANALYSIS")
print("-" * 70)

print("""
Based on the analysis:

NEW EXPORTS (March 2026):
- ChatGPT ZIP (238MB): conversations-000/001/002.json - LIKELY SUPERSEDES Chat_GPT_Exports/
- Claude ZIP (12MB): conversations.json - LIKELY SUPERSEDES Claude_Exports/

OLD EXPORTS (January 2026):
- 01-19-2026 Exports/ (705MB) - Contains older versions, may have duplicates

RECOMMENDED CLEANUP AFTER INDEXING NEW ZIPS:
1. Index the new March 2026 zips first
2. Compare conversation IDs/titles with existing indexed data
3. Remove old exports that are fully superseded
4. Keep unique conversations from older exports if any

SAFE TO DELETE NOW:
- All .zipZone.Identifier files
- all_recent_convos.json (old, from Dec 2025)
- recent_faithh_convos.json (old, from Dec 2025)
""")
