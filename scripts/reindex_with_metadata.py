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
import os

# CRITICAL: Set CUDA env BEFORE importing torch/sentence_transformers to prevent WSL crash
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = ""

import chromadb
from sentence_transformers import SentenceTransformer

# Configuration
EXPORT_BASE = Path.home() / "ai-stack" / "AI_Chat_Exports"
CHROMA_HOST = "servicebox.taileb8c60.ts.net"  # Gen8 server via Tailscale
CHROMA_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

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
            
            # Chunk and yield with date fields for temporal queries
            timestamp_dt = datetime.fromtimestamp(create_time) if create_time else None
            for i, chunk in enumerate(self.chunk_text(full_text)):
                yield {
                    "text": chunk,
                    "metadata": {
                        "source": f"ChatGPT: {title}",
                        "platform": "chatgpt",
                        "conversation_id": conv_id,
                        "chunk_index": i,
                        "timestamp": timestamp_dt.isoformat() if timestamp_dt else "",
                        "date_year": str(timestamp_dt.year) if timestamp_dt else "",
                        "date_month": timestamp_dt.strftime("%Y-%m") if timestamp_dt else "",
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
            
            # Parse timestamp and add date fields for temporal queries
            timestamp_dt = None
            if created_at:
                try:
                    timestamp_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    pass
            
            # Chunk and yield
            for i, chunk in enumerate(self.chunk_text(full_text)):
                yield {
                    "text": chunk,
                    "metadata": {
                        "source": f"Claude: {title}",
                        "platform": "claude",
                        "conversation_id": conv_id,
                        "chunk_index": i,
                        "timestamp": created_at or "",
                        "date_year": str(timestamp_dt.year) if timestamp_dt else "",
                        "date_month": timestamp_dt.strftime("%Y-%m") if timestamp_dt else "",
                        "category": category,
                        "type": "conversation",
                        "title": title,
                        "summary": summary[:200] if summary else ""
                    }
                }


class GrokParser(ConversationParser):
    """Parser for Grok exports (prod-grok-backend.json format)."""
    
    def __init__(self):
        super().__init__("grok")
    
    def _parse_mongo_timestamp(self, ct) -> datetime:
        """Parse MongoDB-style timestamp."""
        if isinstance(ct, dict) and "$date" in ct:
            ms = ct["$date"].get("$numberLong")
            if ms:
                return datetime.fromtimestamp(int(ms) / 1000)
        elif isinstance(ct, (int, float)):
            return datetime.fromtimestamp(ct / 1000 if ct > 1e12 else ct)
        return None
    
    def parse(self, filepath: Path) -> Generator[Dict[str, Any], None, None]:
        """Parse Grok's prod-grok-backend.json format.
        
        Actual structure:
        - conversations array with 'conversation' (metadata) and 'responses' (messages)
        - Each response has 'response' wrapper containing 'message', 'sender', 'create_time'
        - create_time is MongoDB-style: {"$date": {"$numberLong": "milliseconds"}}
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversations = data.get("conversations", [])
        
        for conv_wrapper in conversations:
            # Get conversation metadata
            conv_meta = conv_wrapper.get("conversation", {})
            conv_id = conv_meta.get("id", "unknown")
            title = conv_meta.get("title") or conv_meta.get("summary") or "Grok Conversation"
            
            # Get responses (messages)
            responses = conv_wrapper.get("responses", [])
            
            # Get first response timestamp for conversation date
            create_time = None
            if responses:
                first_resp = responses[0].get("response", {})
                ct = first_resp.get("create_time", {})
                create_time = self._parse_mongo_timestamp(ct)
            
            # Build full text from responses
            full_text = f"# {title}\n\n"
            for resp_wrapper in responses:
                resp = resp_wrapper.get("response", {})
                role = resp.get("sender", "unknown")
                content = resp.get("message", "") or resp.get("text", "")
                if content:
                    # Normalize role names
                    role_display = "USER" if role == "human" else "ASSISTANT" if role == "assistant" else role.upper()
                    full_text += f"**{role_display}**: {content}\n\n"
            
            if len(full_text.strip()) < 50:  # Skip empty/tiny conversations
                continue
            
            category = self.infer_category(full_text, title)
            
            # Chunk and yield
            for i, chunk in enumerate(self.chunk_text(full_text)):
                timestamp_str = create_time.isoformat() if create_time else ""
                date_year = str(create_time.year) if create_time else ""
                date_month = create_time.strftime("%Y-%m") if create_time else ""
                
                yield {
                    "text": chunk,
                    "metadata": {
                        "source": f"Grok: {title[:50]}",
                        "platform": "grok",
                        "conversation_id": conv_id,
                        "chunk_index": i,
                        "timestamp": timestamp_str,
                        "date_year": date_year,
                        "date_month": date_month,
                        "category": category,
                        "type": "conversation",
                        "title": title[:100]
                    }
                }


class MultiPlatformIndexer:
    """Indexes conversations from multiple AI platforms into ChromaDB."""
    
    def __init__(self, collection_name: str = COLLECTION_NAME, dry_run: bool = False):
        self.dry_run = dry_run
        self.collection_name = collection_name
        
        # Initialize embedding model with CPU to prevent CUDA crashes
        print(f"Loading embedding model: {EMBEDDING_MODEL} (CPU mode)...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL, device='cpu')
        
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
    
    def clean_metadata(self, metadata: dict) -> dict:
        """Clean metadata to ensure JSON serializable."""
        cleaned = {}
        for k, v in metadata.items():
            if v is None:
                cleaned[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                cleaned[k] = v
            elif isinstance(v, list):
                cleaned[k] = str(v)
            else:
                cleaned[k] = str(v)
        return cleaned
    
    def generate_id(self, text: str, metadata: dict) -> str:
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
            metadatas = [self.clean_metadata(c["metadata"]) for c in batch]
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
    
    def delete_old_conversations(self):
        """Delete old conversation chunks from ChromaDB."""
        if self.dry_run:
            print("🔍 DRY RUN: Would delete old conversation chunks")
            return 0
        
        print("\n🗑️ Deleting old conversation chunks...")
        deleted = 0
        
        for platform in ["chatgpt", "claude", "grok"]:
            try:
                # Get all IDs with this platform
                results = self.collection.get(
                    where={"platform": platform},
                    include=[]
                )
                if results and results.get("ids"):
                    ids_to_delete = results["ids"]
                    if ids_to_delete:
                        self.collection.delete(ids=ids_to_delete)
                        print(f"   Deleted {len(ids_to_delete)} {platform} chunks")
                        deleted += len(ids_to_delete)
            except Exception as e:
                print(f"   ⚠️ Error deleting {platform} chunks: {e}")
        
        print(f"   Total deleted: {deleted} chunks")
        return deleted
    
    def index_all(self):
        """Index all discovered exports."""
        print("\n" + "="*60)
        print("MULTI-PLATFORM AI CHAT INDEXER")
        print("="*60)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made\n")
        
        # Export directories to scan
        export_dirs = [
            # Newest exports (March 2026)
            ("ChatGPT_Mar2026", "chatgpt", "conversations.json"),
            ("Claude_Mar2026", "claude", "conversations.json"),
            # January 2026 exports
            ("01-19-2026 Exports/ChatGPT", "chatgpt", "conversations.json"),
            ("01-19-2026 Exports/Claude", "claude", "conversations.json"),
            # December exports
            ("Chat_GPT_Exports", "chatgpt", "conversations.json"),
            ("Claude_Exports", "claude", "conversations.json"),
        ]
        
        for subdir, platform, filename in export_dirs:
            filepath = EXPORT_BASE / subdir / filename
            if filepath.exists():
                self.index_file(filepath, self.parsers[platform])
            else:
                # Try without subdirectory for flat structure
                filepath = EXPORT_BASE / subdir
                if filepath.is_file() and filepath.suffix == '.json':
                    self.index_file(filepath, self.parsers[platform])
        
        # Grok exports (special structure)
        grok_dir = EXPORT_BASE / "Grok_Exports"
        if grok_dir.exists():
            for json_file in grok_dir.rglob("*.json"):
                if "prod-grok-backend" in json_file.name:
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
    parser.add_argument("--delete-old", action="store_true", help="Delete old conversation chunks before indexing")
    parser.add_argument("--collection", default=COLLECTION_NAME, help="Collection name")
    args = parser.parse_args()
    
    indexer = MultiPlatformIndexer(
        collection_name=args.collection,
        dry_run=args.dry_run
    )
    
    # Delete old conversation chunks if requested
    if args.delete_old:
        indexer.delete_old_conversations()
    
    indexer.index_all()


if __name__ == "__main__":
    main()