#!/usr/bin/env python3
"""
Clear conversation entries from Gen8 ChromaDB (keep documentation)
Then reindex all conversations fresh.

Usage:
    cd ~/ai-stack
    source venv/bin/activate
    python knowledge_base/clear_and_reindex.py --dry-run   # Preview
    python knowledge_base/clear_and_reindex.py             # Execute
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import chromadb

# === CONFIGURATION ===
CHROMADB_HOST = "192.158.1.243"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    parser.add_argument("--skip-clear", action="store_true", help="Skip clearing, just index")
    args = parser.parse_args()
    
    print("=" * 60)
    print("FAITHH KNOWLEDGE BASE - CLEAR & REINDEX")
    print("=" * 60)
    
    # Connect to ChromaDB
    print(f"\n🔌 Connecting to {CHROMADB_HOST}:{CHROMADB_PORT}...")
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection = client.get_collection(name=COLLECTION_NAME)
    
    initial_count = collection.count()
    print(f"📊 Current document count: {initial_count}")
    
    if not args.skip_clear:
        # Get sample to understand what we have
        print("\n📖 Analyzing existing entries...")
        sample = collection.get(limit=1000, include=["metadatas"])
        
        sources = {}
        for meta in sample["metadatas"]:
            src = meta.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1
        
        print("   Source distribution (sample of 1000):")
        for src, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"   - {src}: {count}")
        
        # Get IDs to delete (conversations only)
        print("\n🔍 Finding conversation entries to delete...")
        
        # Get all chatgpt entries
        chatgpt_results = collection.get(
            where={"source": "chatgpt"},
            include=["metadatas"]
        )
        chatgpt_ids = chatgpt_results["ids"]
        print(f"   ChatGPT entries: {len(chatgpt_ids)}")
        
        # Get all claude entries  
        claude_results = collection.get(
            where={"source": "claude"},
            include=["metadatas"]
        )
        claude_ids = claude_results["ids"]
        print(f"   Claude entries: {len(claude_ids)}")
        
        total_to_delete = len(chatgpt_ids) + len(claude_ids)
        print(f"\n📝 Total entries to delete: {total_to_delete}")
        print(f"   Will keep: {initial_count - total_to_delete} (documentation + other)")
        
        if args.dry_run:
            print("\n⚠️  DRY RUN - No changes made")
            print("   Run without --dry-run to execute deletion")
            return
        
        # Confirm
        print("\n⚠️  This will delete conversation entries. Continue? (yes/no)")
        confirm = input("> ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            return
        
        # Delete in batches
        print("\n🗑️  Deleting conversation entries...")
        
        if chatgpt_ids:
            # Delete in batches of 1000
            for i in range(0, len(chatgpt_ids), 1000):
                batch = chatgpt_ids[i:i+1000]
                collection.delete(ids=batch)
                print(f"   Deleted ChatGPT batch {i//1000 + 1}: {len(batch)} entries")
        
        if claude_ids:
            for i in range(0, len(claude_ids), 1000):
                batch = claude_ids[i:i+1000]
                collection.delete(ids=batch)
                print(f"   Deleted Claude batch {i//1000 + 1}: {len(batch)} entries")
        
        remaining = collection.count()
        print(f"\n✅ Deletion complete. Remaining: {remaining} entries")
    
    # Now run the indexer
    print("\n" + "=" * 60)
    print("INDEXING NEW CONVERSATIONS")
    print("=" * 60)
    print("\nRun: python knowledge_base/index_conversations.py")


if __name__ == "__main__":
    main()
