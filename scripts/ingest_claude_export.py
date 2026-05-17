#!/usr/bin/env python3
"""
FAITHH Claude Export Ingestion Pipeline
==========================================
Diff-based ingestion of Anthropic/Claude chat exports into ChromaDB.
Only indexes NEW or UPDATED conversations, cleans up redundant files,
and optionally runs the knowledge distiller on new content.

Workflow:
  1. Load new Claude export (conversations.json)
  2. Compare against manifest of already-indexed conversations
  3. Chunk and index only new/updated conversations into ChromaDB
  4. Update the manifest
  5. Optionally run knowledge distiller on new conversations
  6. Move processed export to archive (or delete)

Usage:
  cd ~/ai-stack

  # Basic: ingest a new export
  venv/bin/python scripts/ingest_claude_export.py /path/to/conversations.json

  # With distillation
  venv/bin/python scripts/ingest_claude_export.py /path/to/conversations.json --distill

  # Dry run (show what would be indexed)
  venv/bin/python scripts/ingest_claude_export.py /path/to/conversations.json --dry-run

  # Keep export file (don't archive)
  venv/bin/python scripts/ingest_claude_export.py /path/to/conversations.json --keep
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import chromadb

# ============================================================
# Configuration
# ============================================================

CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.10")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base")

BASE_DIR = Path(__file__).parent.parent  # ~/ai-stack
MANIFEST_FILE = BASE_DIR / "ml" / "output" / "claude_ingestion_manifest.json"
ARCHIVE_DIR = BASE_DIR / "AI_Chat_Exports" / "Claude_Chats" / "processed"

CHUNK_SIZE = 1500       # chars per chunk
CHUNK_OVERLAP = 200
MIN_CONVERSATION_LENGTH = 100  # chars, skip tiny conversations


# ============================================================
# Manifest management
# ============================================================

def load_manifest():
    """Load the ingestion manifest (tracks what's already indexed)."""
    if MANIFEST_FILE.exists():
        try:
            return json.loads(MANIFEST_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return {"version": "1.0", "conversations": {}, "last_ingestion": None}


def save_manifest(manifest):
    """Save the ingestion manifest."""
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    manifest["last_ingestion"] = datetime.now().isoformat()
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)


# ============================================================
# Claude export parsing
# ============================================================

def parse_export(export_path):
    """Parse a Claude conversations.json export file."""
    with open(export_path, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    parsed = []
    for conv in conversations:
        messages = conv.get("chat_messages", [])
        if not messages:
            continue

        # Extract text from all messages
        full_text = []
        for msg in messages:
            sender = msg.get("sender", "unknown")
            # Handle both flat text and content array formats
            text = msg.get("text", "")
            if not text:
                for content in msg.get("content", []):
                    if content.get("type") == "text":
                        text += content.get("text", "")
            if text.strip():
                full_text.append(f"{sender.upper()}: {text.strip()}")

        combined = "\n\n".join(full_text)
        if len(combined) < MIN_CONVERSATION_LENGTH:
            continue

        # Content hash for change detection
        content_hash = hashlib.md5(combined.encode()).hexdigest()

        parsed.append({
            "uuid": conv.get("uuid", ""),
            "name": conv.get("name", "Untitled"),
            "created_at": conv.get("created_at", ""),
            "updated_at": conv.get("updated_at", ""),
            "message_count": len(messages),
            "text": combined,
            "content_hash": content_hash,
        })

    return parsed


def diff_against_manifest(conversations, manifest):
    """Find new or updated conversations by comparing against manifest."""
    existing = manifest.get("conversations", {})

    new_convs = []
    updated_convs = []
    unchanged = 0

    for conv in conversations:
        uuid = conv["uuid"]
        if uuid not in existing:
            new_convs.append(conv)
        elif existing[uuid].get("content_hash") != conv["content_hash"]:
            updated_convs.append(conv)
        else:
            unchanged += 1

    return new_convs, updated_convs, unchanged


# ============================================================
# Chunking and indexing
# ============================================================

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def make_chunk_id(conv_uuid, chunk_index):
    """Create deterministic ID for a conversation chunk."""
    key = f"claude:{conv_uuid}:chunk_{chunk_index}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def index_conversations(collection, conversations, is_update=False):
    """Index conversations into ChromaDB with chunking."""
    total_chunks = 0
    action = "Updating" if is_update else "Indexing"

    for conv in conversations:
        chunks = chunk_text(conv["text"])
        if not chunks:
            continue

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = make_chunk_id(conv["uuid"], i)
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": f"Claude: {conv['name']}",
                "title": conv["name"],
                "conversation_id": conv["uuid"],
                "platform": "claude",
                "type": "conversation",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "message_count": conv["message_count"],
                "timestamp": conv.get("updated_at") or conv.get("created_at", ""),
                "content_hash": conv["content_hash"],
            })

        # Upsert handles both new and updated
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        total_chunks += len(chunks)

    return total_chunks


def remove_old_chunks(collection, conv_uuid):
    """Remove old chunks for a conversation before re-indexing."""
    try:
        results = collection.get(
            where={"conversation_id": conv_uuid},
            limit=10000,
        )
        if results and results["ids"]:
            collection.delete(ids=results["ids"])
            return len(results["ids"])
    except Exception:
        pass
    return 0


# ============================================================
# Main pipeline
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="FAITHH Claude Export Ingestion")
    parser.add_argument("export_path", help="Path to conversations.json export file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be indexed without actually indexing")
    parser.add_argument("--distill", action="store_true",
                        help="Run knowledge distiller on new conversations after indexing")
    parser.add_argument("--keep", action="store_true",
                        help="Keep the export file (don't move to archive)")
    parser.add_argument("--force", action="store_true",
                        help="Re-index all conversations, ignoring manifest")
    args = parser.parse_args()

    export_path = Path(args.export_path).expanduser().resolve()
    if not export_path.exists():
        print(f"❌ Export file not found: {export_path}")
        sys.exit(1)

    print("=" * 60)
    print("FAITHH CLAUDE EXPORT INGESTION")
    print("=" * 60)
    print(f"Export: {export_path}")
    print(f"ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}/{COLLECTION_NAME}")
    start_time = time.time()

    # Step 1: Parse export
    print(f"\n📦 Step 1: Parse export file")
    conversations = parse_export(export_path)
    print(f"   Parsed {len(conversations)} conversations with content")

    # Step 2: Diff against manifest
    print(f"\n🔍 Step 2: Diff against ingestion manifest")
    manifest = load_manifest()

    if args.force:
        new_convs = conversations
        updated_convs = []
        unchanged = 0
        print(f"   --force: treating all {len(new_convs)} as new")
    else:
        new_convs, updated_convs, unchanged = diff_against_manifest(conversations, manifest)
        print(f"   New: {len(new_convs)}")
        print(f"   Updated: {len(updated_convs)}")
        print(f"   Unchanged: {unchanged}")

    total_to_process = len(new_convs) + len(updated_convs)
    if total_to_process == 0:
        print(f"\n✅ Nothing to index — all conversations already up to date.")
        return

    if args.dry_run:
        print(f"\n📊 Dry run — would index {total_to_process} conversations:")
        if new_convs:
            print(f"\n   NEW ({len(new_convs)}):")
            for c in new_convs[:20]:
                est_chunks = max(1, len(c["text"]) // (CHUNK_SIZE - CHUNK_OVERLAP))
                print(f"     {c['name'][:60]} ({c['message_count']} msgs, ~{est_chunks} chunks)")
            if len(new_convs) > 20:
                print(f"     ...and {len(new_convs) - 20} more")
        if updated_convs:
            print(f"\n   UPDATED ({len(updated_convs)}):")
            for c in updated_convs[:10]:
                print(f"     {c['name'][:60]} ({c['message_count']} msgs)")
        return

    # Step 3: Connect to ChromaDB and index
    print(f"\n📡 Step 3: Connect to ChromaDB and index")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(COLLECTION_NAME)
    before_count = collection.count()
    print(f"   Collection has {before_count:,} docs before indexing")

    # Index new conversations
    if new_convs:
        print(f"\n   Indexing {len(new_convs)} new conversations...")
        new_chunks = index_conversations(collection, new_convs, is_update=False)
        print(f"   ✅ Indexed {new_chunks} chunks from {len(new_convs)} new conversations")

    # Update changed conversations
    if updated_convs:
        print(f"\n   Updating {len(updated_convs)} changed conversations...")
        removed = 0
        for conv in updated_convs:
            removed += remove_old_chunks(collection, conv["uuid"])
        updated_chunks = index_conversations(collection, updated_convs, is_update=True)
        print(f"   ✅ Replaced {removed} old chunks with {updated_chunks} updated chunks")

    after_count = collection.count()
    print(f"\n   Collection: {before_count:,} → {after_count:,} docs")

    # Step 4: Update manifest
    print(f"\n📋 Step 4: Update ingestion manifest")
    for conv in new_convs + updated_convs:
        manifest["conversations"][conv["uuid"]] = {
            "name": conv["name"],
            "content_hash": conv["content_hash"],
            "message_count": conv["message_count"],
            "indexed_at": datetime.now().isoformat(),
            "updated_at": conv.get("updated_at", ""),
        }
    save_manifest(manifest)
    print(f"   Manifest: {len(manifest['conversations'])} conversations tracked")

    # Step 5: Archive export file
    if not args.keep:
        print(f"\n🗂️  Step 5: Archive export file")
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"conversations_{timestamp}.json"
        archive_path = ARCHIVE_DIR / archive_name
        shutil.move(str(export_path), str(archive_path))
        print(f"   Moved to: {archive_path}")
    else:
        print(f"\n   --keep: export file left in place")

    elapsed = time.time() - start_time

    # Step 6: Optionally run distiller
    if args.distill:
        print(f"\n🧠 Step 6: Running knowledge distiller on new content...")
        distiller_path = BASE_DIR / "scripts" / "knowledge_distiller.py"
        if distiller_path.exists():
            import subprocess
            env = os.environ.copy()
            result = subprocess.run(
                [sys.executable, str(distiller_path), "--provider", "ollama", "--skip-evaluated"],
                cwd=str(BASE_DIR),
                env=env,
                capture_output=False,
            )
            if result.returncode != 0:
                print(f"   ⚠️  Distiller exited with code {result.returncode}")
        else:
            print(f"   ⚠️  Distiller not found at {distiller_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ INGESTION COMPLETE")
    print(f"{'=' * 60}")
    print(f"   New conversations indexed: {len(new_convs)}")
    print(f"   Updated conversations: {len(updated_convs)}")
    print(f"   Unchanged (skipped): {unchanged}")
    print(f"   Collection size: {after_count:,} docs")
    print(f"   Duration: {elapsed:.1f}s")

    if args.distill:
        print(f"\n   Distillation report: ml/output/knowledge_distillation_report.md")


if __name__ == "__main__":
    main()
