#!/usr/bin/env python3
"""
Multi-Platform AI Chat Indexer with Proper Metadata
Re-indexes ChatGPT, Claude, and Grok exports into ChromaDB with full metadata.

Usage:
    python scripts/reindex_with_metadata.py --dry-run  # Preview without indexing
    python scripts/reindex_with_metadata.py            # Full re-index
"""

import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Generator, Dict, Any, List
import chromadb
from sentence_transformers import SentenceTransformer

# Configuration
EXPORT_BASE = Path.home() / "ai-stack" / "AI_Chat_Exports"
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION_NAME = "documents_768_v2"
EMBEDDING_MODEL = "all-mpnet-base-v2"

# Category keywords for auto-classification
CATEGORY_KEYWORDS = {
    "faithh": ["faithh", "rag", "chromadb", "embedding", "backend", "frontend"],
    "constella": ["constella", "astris", "auctor", "governance", "civic", "token"],
    "audio": ["audio", "mastering", "wavelab", "sonarworks", "daw", "mixing", "soundworks"],
    "infrastructure": ["tailscale", "nas", "synology", "network", "server", "proliant", "docker"],
    "coding": ["python", "javascript", "code", "function", "api", "debug", "error"],
}

class ConversationParser:
    """Base class for parsing AI platform exports."""
    
    def __init__(self, platform: str):
        self.platform = platform
    
    def parse(self, filepath: Path) -> Generator[Dict[str, Any], None, None]:
        raise NotImplementedError
    
    def infer_category(self, text: str, title: str = "") -> str:
        """Infer category from content keywords."""
        combined = (text + " " + title).lower()
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            scores[category] = sum(1 for kw in keywords if kw in combined)
        
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "general"
    
    def chunk_text(self, text: str, max_chars: int = 1500, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks


class ChatGPTParser(ConversationParser):
    """Parser for ChatGPT exports."""
    
    def __init__(self):
        super().__init__("chatgpt")
    
    def parse(self, filepath: Path) -> Generator[Dict[str, Any], None, None]:
        with open(filepath, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        for conv in conversations:
            conv_id = conv.get("conversation_id", conv.get("id", "unknown"))
            title = conv.get("title", "Untitled")
            create_time = conv.get("create_time")
            model = conv.get("default_model_slug", "unknown")
            
            # Extract messages from mapping structure
            mapping = conv.get("mapping", {})
            messages = []
            
            for node_id, node in mapping.items():
                message = node.get("message")
                if message and message.get("content"):
                    content = message["content"]
                    parts = content.get("parts", [])
                    role = message.get("author", {}).get("role", "unknown")
                    
                    text = ""
                    for part in parts:
                        if isinstance(part, str):
                            text += part + "\n"
                    
                    if text.strip():
                        messages.append({
                            "role": role,
                            "content": text.strip(),
                            "message_id": message.get("id", node_id)
                        })
            
            # Combine into conversation chunks
            full_text = f"# {title}\n\n"
            for msg in messages:
                full_text += f"**{msg['role'].upper()}**: {msg['content']}\n\n"
            
            category = self.infer_category(full_text, title)
            
            # Chunk and yield
            for i, chunk in enumerate(self.chunk_text(full_text)):
                yield {
                    "text": chunk,
                    "metadata": {
                        "source": f"ChatGPT: {title}",
                        "platform": "chatgpt",
                        "conversation_id": conv_id,
                        "chunk_index": i,
                        "timestamp": datetime.fromtimestamp(create_time).isoformat() if create_time else None,
                        "category": category,
                        "type": "conversation",
                        "model": model,
                        "title": title
                    }
                }


class ClaudeParser(ConversationParser):
    """Parser for Claude exports."""
    
    def __init__(self):
        super().__init__("claude")
    
    def parse(self, filepath: Path) -> Generator[Dict[str, Any], None, None]:
        with open(filepath, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        for conv in conversations:
            conv_id = conv.get("uuid", "unknown")
            title = conv.get("name", "Untitled")
            summary = conv.get("summary", "")
            created_at = conv.get("created_at")
            messages = conv.get("chat_messages", [])
            
            # Build full text
            full_text = f"# {title}\n\n"
            if summary:
                full_text += f"*Summary: {summary}*\n\n"
            
            for msg in messages:
                role = msg.get("sender", "unknown")
                content = msg.get("text", "")
                if content:
                    full_text += f"**{role.upper()}**: {content}\n\n"
            
            category = self.infer_category(full_text, title)
            
            # Chunk and yield
            for i, chunk in enumerate(self.chunk_text(full_text)):
                yield {
                    "text": chunk,
                    "metadata": {
                        "source": f"Claude: {title}",
                        "platform": "claude",
                        "conversation_id": conv_id,
                        "chunk_index": i,
                        "timestamp": created_at,
                        "category": category,
                        "type": "conversation",
                        "title": title,
                        "summary": summary[:200] if summary else None
                    }
                }


class GrokParser(ConversationParser):
    """Parser for Grok exports (structure TBD)."""
    
    def __init__(self):
        super().__init__("grok")
    
    def parse(self, filepath: Path) -> Generator[Dict[str, Any], None, None]:
        # TODO: Implement after structure analysis
        print(f"⚠️ Grok parser not yet implemented for {filepath}")
        return
        yield  # Make it a generator


class MultiPlatformIndexer:
    """Indexes conversations from multiple AI platforms into ChromaDB."""
    
    def __init__(self, collection_name: str = COLLECTION_NAME, dry_run: bool = False):
        self.dry_run = dry_run
        self.collection_name = collection_name
        
        # Initialize embedding model
        print(f"Loading embedding model: {EMBEDDING_MODEL}...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        
        # Initialize ChromaDB
        if not dry_run:
            print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
            self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            
            # Create or get collection
            try:
                self.collection = self.client.get_collection(collection_name)
                print(f"Using existing collection: {collection_name} ({self.collection.count()} docs)")
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"Created new collection: {collection_name}")
        
        # Initialize parsers
        self.parsers = {
            "chatgpt": ChatGPTParser(),
            "claude": ClaudeParser(),
            "grok": GrokParser(),
        }
        
        self.stats = {
            "total_chunks": 0,
            "by_platform": {},
            "by_category": {},
            "errors": []
        }
    
    def generate_id(self, text: str, metadata: dict) -> str:
        """Generate unique ID for a chunk."""
        unique_str = f"{metadata['platform']}:{metadata['conversation_id']}:{metadata.get('chunk_index', 0)}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]
    
    def index_file(self, filepath: Path, parser: ConversationParser):
        """Index a single export file."""
        print(f"\n📄 Processing: {filepath.name}")
        
        chunks = []
        for item in parser.parse(filepath):
            chunks.append(item)
        
        print(f"   Found {len(chunks)} chunks")
        
        if self.dry_run:
            # Just count stats
            for item in chunks:
                platform = item["metadata"]["platform"]
                category = item["metadata"]["category"]
                self.stats["by_platform"][platform] = self.stats["by_platform"].get(platform, 0) + 1
                self.stats["by_category"][category] = self.stats["by_category"].get(category, 0) + 1
                self.stats["total_chunks"] += 1
            return
        
        # Batch embed and index
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            texts = [c["text"] for c in batch]
            metadatas = [c["metadata"] for c in batch]
            ids = [self.generate_id(c["text"], c["metadata"]) for c in batch]
            
            # Generate embeddings
            embeddings = self.embedder.encode(texts).tolist()
            
            # Add to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            # Update stats
            for meta in metadatas:
                platform = meta["platform"]
                category = meta["category"]
                self.stats["by_platform"][platform] = self.stats["by_platform"].get(platform, 0) + 1
                self.stats["by_category"][category] = self.stats["by_category"].get(category, 0) + 1
                self.stats["total_chunks"] += 1
            
            print(f"   Indexed batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
    
    def index_all(self):
        """Index all discovered exports."""
        print("\n" + "="*60)
        print("MULTI-PLATFORM AI CHAT INDEXER")
        print("="*60)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made\n")
        
        # ChatGPT
        chatgpt_file = EXPORT_BASE / "Chat_GPT_Exports" / "conversations.json"
        if chatgpt_file.exists():
            self.index_file(chatgpt_file, self.parsers["chatgpt"])
        
        # Claude
        claude_file = EXPORT_BASE / "Claude_Exports" / "conversations.json"
        if claude_file.exists():
            self.index_file(claude_file, self.parsers["claude"])
        
        # Grok (once implemented)
        grok_dir = EXPORT_BASE / "Grok_Exports"
        if grok_dir.exists():
            for json_file in grok_dir.rglob("*.json"):
                if "prod-grok" in json_file.name:
                    self.index_file(json_file, self.parsers["grok"])
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print indexing summary."""
        print("\n" + "="*60)
        print("INDEXING SUMMARY")
        print("="*60)
        
        print(f"\nTotal chunks indexed: {self.stats['total_chunks']}")
        
        print("\nBy Platform:")
        for platform, count in sorted(self.stats["by_platform"].items()):
            print(f"  {platform}: {count}")
        
        print("\nBy Category:")
        for category, count in sorted(self.stats["by_category"].items()):
            print(f"  {category}: {count}")
        
        if not self.dry_run:
            print(f"\nCollection '{self.collection_name}' now has {self.collection.count()} documents")
        
        if self.stats["errors"]:
            print(f"\n⚠️ Errors: {len(self.stats['errors'])}")
            for err in self.stats["errors"][:5]:
                print(f"  - {err}")


def main():
    parser = argparse.ArgumentParser(description="Multi-Platform AI Chat Indexer")
    parser.add_argument("--dry-run", action="store_true", help="Preview without indexing")
    parser.add_argument("--collection", default=COLLECTION_NAME, help="Collection name")
    args = parser.parse_args()
    
    indexer = MultiPlatformIndexer(
        collection_name=args.collection,
        dry_run=args.dry_run
    )
    indexer.index_all()


if __name__ == "__main__":
    main()