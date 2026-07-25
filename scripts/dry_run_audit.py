#!/usr/bin/env python3
"""
Quick Dry Run Audit - No heavy imports
Counts chunks from exports without loading embedding model.
"""

import json
from pathlib import Path
from collections import defaultdict

EXPORT_BASE = Path.home() / "ai-stack" / "AI_Chat_Exports"

CATEGORY_KEYWORDS = {
    "faithh": ["faithh", "rag", "chromadb", "embedding", "backend"],
    "constella": ["constella", "astris", "auctor", "governance", "civic"],
    "audio": ["audio", "mastering", "wavelab", "sonarworks", "daw"],
    "infrastructure": ["tailscale", "nas", "synology", "network", "server"],
    "coding": ["python", "javascript", "code", "function", "api"],
}

def infer_category(text: str) -> str:
    text_lower = text.lower()
    scores = {cat: sum(1 for kw in kws if kw in text_lower) 
              for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"

def chunk_text(text: str, max_chars: int = 1500) -> int:
    """Return number of chunks."""
    if len(text) <= max_chars:
        return 1
    return (len(text) // (max_chars - 200)) + 1

def parse_chatgpt(filepath: Path) -> dict:
    """Parse ChatGPT export."""
    stats = {"conversations": 0, "chunks": 0, "categories": defaultdict(int)}
    
    with open(filepath, 'r') as f:
        conversations = json.load(f)
    
    for conv in conversations:
        title = conv.get("title", "")
        mapping = conv.get("mapping", {})
        
        # Extract text
        text = title + " "
        for node in mapping.values():
            msg = node.get("message")
            if msg and msg.get("content"):
                parts = msg["content"].get("parts", [])
                for part in parts:
                    if isinstance(part, str):
                        text += part + " "
        
        cat = infer_category(text)
        n_chunks = chunk_text(text)
        
        stats["conversations"] += 1
        stats["chunks"] += n_chunks
        stats["categories"][cat] += n_chunks
    
    return stats

def parse_claude(filepath: Path) -> dict:
    """Parse Claude export."""
    stats = {"conversations": 0, "chunks": 0, "categories": defaultdict(int)}
    
    with open(filepath, 'r') as f:
        conversations = json.load(f)
    
    for conv in conversations:
        title = conv.get("name", "")
        messages = conv.get("chat_messages", [])
        
        text = title + " "
        for msg in messages:
            text += msg.get("text", "") + " "
        
        cat = infer_category(text)
        n_chunks = chunk_text(text)
        
        stats["conversations"] += 1
        stats["chunks"] += n_chunks
        stats["categories"][cat] += n_chunks
    
    return stats

def parse_grok(filepath: Path) -> dict:
    """Parse Grok export."""
    stats = {"conversations": 0, "chunks": 0, "categories": defaultdict(int)}
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    conversations = data.get("conversations", [])
    if isinstance(conversations, dict):
        conversations = list(conversations.values())
    
    for conv in conversations:
        if isinstance(conv, dict):
            # Try common fields
            title = conv.get("title", conv.get("name", ""))
            messages = conv.get("messages", conv.get("chat_messages", []))
            
            text = title + " "
            if isinstance(messages, list):
                for msg in messages:
                    if isinstance(msg, dict):
                        text += msg.get("text", msg.get("content", "")) + " "
                    elif isinstance(msg, str):
                        text += msg + " "
            
            cat = infer_category(text)
            n_chunks = chunk_text(text)
            
            stats["conversations"] += 1
            stats["chunks"] += n_chunks
            stats["categories"][cat] += n_chunks
    
    return stats

def main():
    print("=" * 60)
    print("DRY RUN AUDIT - Export Analysis")
    print("=" * 60)
    
    total_stats = {
        "conversations": 0,
        "chunks": 0,
        "by_platform": {},
        "by_category": defaultdict(int)
    }
    
    # ChatGPT
    chatgpt_file = EXPORT_BASE / "Chat_GPT_Exports" / "conversations.json"
    if chatgpt_file.exists():
        print(f"\n📄 ChatGPT: {chatgpt_file.name}")
        stats = parse_chatgpt(chatgpt_file)
        print(f"   Conversations: {stats['conversations']}")
        print(f"   Chunks: {stats['chunks']}")
        total_stats["by_platform"]["chatgpt"] = stats
        total_stats["conversations"] += stats["conversations"]
        total_stats["chunks"] += stats["chunks"]
        for cat, count in stats["categories"].items():
            total_stats["by_category"][cat] += count
    
    # Claude
    claude_file = EXPORT_BASE / "Claude_Exports" / "conversations.json"
    if claude_file.exists():
        print(f"\n📄 Claude: {claude_file.name}")
        stats = parse_claude(claude_file)
        print(f"   Conversations: {stats['conversations']}")
        print(f"   Chunks: {stats['chunks']}")
        total_stats["by_platform"]["claude"] = stats
        total_stats["conversations"] += stats["conversations"]
        total_stats["chunks"] += stats["chunks"]
        for cat, count in stats["categories"].items():
            total_stats["by_category"][cat] += count
    
    # Grok
    grok_file = EXPORT_BASE / "Grok_Exports" / "data" / "prod-grok-backend.json"
    if grok_file.exists():
        print(f"\n📄 Grok: {grok_file.name}")
        stats = parse_grok(grok_file)
        print(f"   Conversations: {stats['conversations']}")
        print(f"   Chunks: {stats['chunks']}")
        total_stats["by_platform"]["grok"] = stats
        total_stats["conversations"] += stats["conversations"]
        total_stats["chunks"] += stats["chunks"]
        for cat, count in stats["categories"].items():
            total_stats["by_category"][cat] += count
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nTotal Conversations: {total_stats['conversations']}")
    print(f"Total Chunks (estimated): {total_stats['chunks']}")
    
    print("\nBy Platform:")
    for platform, stats in total_stats["by_platform"].items():
        print(f"  {platform}: {stats['conversations']} convos → {stats['chunks']} chunks")
    
    print("\nBy Category (chunk distribution):")
    for cat, count in sorted(total_stats["by_category"].items(), key=lambda x: -x[1]):
        pct = count / total_stats["chunks"] * 100 if total_stats["chunks"] > 0 else 0
        print(f"  {cat}: {count} ({pct:.1f}%)")
    
    print("\n✅ Dry run complete. Ready for actual indexing.")

if __name__ == "__main__":
    main()
