#!/usr/bin/env python3
"""
FAITHH Knowledge Base v2 Reindexer
Target: faithh_knowledge_base_v2 (BGE-base-en-v1.5, 768-dim)
Sources:
  - Claude export (conversations.json + batch zips)
  - ChatGPT export (conversations.json)
  - Cursor/Windsurf session markdown/txt files

Run in tmux:
  tmux new -s reindex
  cd ~/ai-stack && source venv/bin/activate
  python reindex_kb_v2.py 2>&1 | tee /tmp/reindex_v2.log

Detach:   Ctrl+B then D
Reattach: tmux attach -t reindex
"""

import json
import os
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer

# ── CONFIG ────────────────────────────────────────────────────────────────────
CHROMA_HOST     = os.environ.get("CHROMA_HOST", "192.158.1.10")
CHROMA_PORT     = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base_v2"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
DEVICE          = "cuda"   # 3090 idle compute; auto-falls back to cpu
CHUNK_SIZE      = 1800
CHUNK_OVERLAP   = 200
BATCH_SIZE      = 64

IMPORTS_DIR = Path(__file__).parent / "knowledge_base" / "imports"

# Files in the claude dir that are NOT conversation lists
CLAUDE_SKIP_FILES = {"conversations.json", "users.json", "memories.json"}
# ── END CONFIG ────────────────────────────────────────────────────────────────


def chunk_text(text: str) -> List[str]:
    if not text or not text.strip():
        return []
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start:start + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def make_id(prefix: str, index: int) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}-{index}"


# ── CLAUDE ────────────────────────────────────────────────────────────────────

def _extract_claude_text(conv: Dict) -> str:
    parts = []
    for msg in conv.get("chat_messages", []):
        role = msg.get("sender", "unknown")
        content = msg.get("text", "") or ""
        if not content and isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if isinstance(block, dict):
                    content += block.get("text", "") or ""
        if content.strip():
            parts.append(f"{role}: {content.strip()}")
    return "\n\n".join(parts)


def load_claude(imports_dir: Path) -> List[Dict]:
    claude_dir = imports_dir / "claude"
    docs = []

    # 1. Main conversations.json (pre-merged from both zip batches)
    conv_file = claude_dir / "conversations.json"
    if conv_file.exists():
        print(f"  Loading {conv_file.name}")
        data = json.load(open(conv_file))
        convs = data if isinstance(data, list) else data.get("conversations", [])
        before = len(docs)
        for conv in convs:
            text = _extract_claude_text(conv)
            title = conv.get("name") or conv.get("title") or "Untitled"
            created = conv.get("created_at", "")
            for i, chunk in enumerate(chunk_text(text)):
                docs.append({
                    "text": chunk,
                    "metadata": {
                        "source": "claude",
                        "document_type": "chat_export",
                        "domain": "live_conversation",
                        "conversation_title": title[:200],
                        "conversation_id": conv.get("uuid", conv.get("id", "")),
                        "chunk_index": i,
                        "export_date": created[:10] if created else "",
                        "indexed_at": datetime.utcnow().isoformat(),
                    }
                })
        print(f"    → {len(docs) - before} chunks from {len(convs)} conversations")
    else:
        print(f"  [WARN] No conversations.json at {conv_file}")

    # 2. Any extra batch JSONs (skip metadata-only files)
    batch_start = len(docs)
    for jf in sorted(claude_dir.glob("*.json")):
        if jf.name in CLAUDE_SKIP_FILES:
            continue
        print(f"  Loading batch file {jf.name}")
        try:
            data = json.load(open(jf))
            convs = data if isinstance(data, list) else []
            for conv in convs:
                text = _extract_claude_text(conv)
                title = conv.get("name") or conv.get("title") or jf.stem
                created = conv.get("created_at", "")
                for i, chunk in enumerate(chunk_text(text)):
                    docs.append({
                        "text": chunk,
                        "metadata": {
                            "source": "claude_batch",
                            "document_type": "chat_export",
                            "domain": "live_conversation",
                            "conversation_title": title[:200],
                            "conversation_id": conv.get("uuid", conv.get("id", "")),
                            "chunk_index": i,
                            "export_date": created[:10] if created else "",
                            "indexed_at": datetime.utcnow().isoformat(),
                            "batch_file": jf.name,
                        }
                    })
        except Exception as e:
            print(f"    [WARN] Could not parse {jf.name}: {e}")
    if len(docs) - batch_start:
        print(f"    → {len(docs) - batch_start} additional chunks from batch files")

    # 3. Project prompt_templates
    projects_dir = claude_dir / "projects"
    proj_start = len(docs)
    if projects_dir.exists():
        for pf in sorted(projects_dir.glob("*.json")):
            try:
                data = json.load(open(pf))
                name = data.get("name", pf.stem)
                desc = data.get("description", "")
                prompt = data.get("prompt_template", "")
                text = f"Claude Project: {name}\nDescription: {desc}\nSystem Prompt:\n{prompt}".strip()
                if len(text) < 50:
                    continue
                for i, chunk in enumerate(chunk_text(text)):
                    docs.append({
                        "text": chunk,
                        "metadata": {
                            "source": "claude_project",
                            "document_type": "project_template",
                            "domain": "project_config",
                            "project_name": name[:200],
                            "project_uuid": data.get("uuid", ""),
                            "chunk_index": i,
                            "indexed_at": datetime.utcnow().isoformat(),
                        }
                    })
            except Exception as e:
                print(f"    [WARN] Could not parse {pf.name}: {e}")
        added = len(docs) - proj_start
        if added:
            print(f"    → {added} chunks from {len(list(projects_dir.glob('*.json')))} project templates")

    return docs


# ── CHATGPT ───────────────────────────────────────────────────────────────────

def load_chatgpt(imports_dir: Path) -> List[Dict]:
    conv_file = imports_dir / "chatgpt" / "conversations.json"
    if not conv_file.exists():
        print("  [SKIP] No ChatGPT conversations.json found")
        return []

    size_mb = conv_file.stat().st_size // 1_000_000
    print(f"  Loading {conv_file.name} ({size_mb}MB)...")
    data = json.load(open(conv_file))
    convs = data if isinstance(data, list) else data.get("conversations", [])
    print(f"  {len(convs)} conversations")

    docs = []
    for conv in convs:
        title = conv.get("title", "Untitled")
        created = conv.get("create_time", 0)
        created_str = datetime.utcfromtimestamp(created).strftime("%Y-%m-%d") if created else ""

        parts = []
        for node in conv.get("mapping", {}).values():
            msg = node.get("message")
            if not msg:
                continue
            role = msg.get("author", {}).get("role", "unknown")
            content = msg.get("content", {})
            if isinstance(content, dict):
                text = " ".join(p for p in content.get("parts", []) if isinstance(p, str))
            elif isinstance(content, str):
                text = content
            else:
                text = ""
            if text.strip():
                parts.append(f"{role}: {text.strip()}")

        full_text = "\n\n".join(parts)
        for i, chunk in enumerate(chunk_text(full_text)):
            docs.append({
                "text": chunk,
                "metadata": {
                    "source": "chatgpt",
                    "document_type": "chat_export",
                    "domain": "live_conversation",
                    "conversation_title": title[:200],
                    "conversation_id": conv.get("id", conv.get("conversation_id", "")),
                    "chunk_index": i,
                    "export_date": created_str,
                    "indexed_at": datetime.utcnow().isoformat(),
                }
            })

    print(f"    → {len(docs)} chunks")
    return docs


# ── CURSOR / WINDSURF ─────────────────────────────────────────────────────────

def load_cursor_windsurf(imports_dir: Path) -> List[Dict]:
    cw_dir = imports_dir / "cursor_windsurf"
    if not cw_dir.exists():
        print("  [SKIP] No cursor_windsurf directory found")
        return []

    files = [f for f in sorted(cw_dir.iterdir())
             if f.suffix.lower() in (".md", ".txt", ".markdown")]
    if not files:
        print("  [SKIP] No .md/.txt files in cursor_windsurf")
        return []

    print(f"  {len(files)} files")
    docs = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception as e:
            print(f"    [WARN] Could not read {f.name}: {e}")
            continue
        if len(text) < 50:
            continue
        source = ("cursor" if "cursor" in f.name.lower() else
                  "windsurf" if "windsurf" in f.name.lower() else
                  "session_doc")
        for i, chunk in enumerate(chunk_text(text)):
            docs.append({
                "text": chunk,
                "metadata": {
                    "source": source,
                    "document_type": "session_handoff",
                    "domain": "faithh_ops",
                    "filename": f.name,
                    "chunk_index": i,
                    "indexed_at": datetime.utcnow().isoformat(),
                }
            })

    print(f"    → {len(docs)} chunks")
    return docs


# ── EMBED + UPSERT ────────────────────────────────────────────────────────────

def upsert_batch(collection, embedder, docs: List[Dict], offset: int):
    texts = [d["text"] for d in docs]
    embeddings = embedder.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
    ).tolist()
    ids = [make_id("kb2", offset + i) for i in range(len(docs))]
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=[d["metadata"] for d in docs],
    )


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("FAITHH KB v2 Reindex")
    print(f"  Collection : {COLLECTION_NAME}")
    print(f"  Model      : {EMBEDDING_MODEL} on {DEVICE}")
    print(f"  ChromaDB   : {CHROMA_HOST}:{CHROMA_PORT}")
    print(f"  Imports    : {IMPORTS_DIR}")
    print("=" * 60)

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"description": "FAITHH KB v2 — BGE-base-en-v1.5 768-dim", "dimension": 768}
    )
    print(f"\nCollection current count: {collection.count()}")

    print(f"\nLoading {EMBEDDING_MODEL} on {DEVICE}...")
    try:
        embedder = SentenceTransformer(EMBEDDING_MODEL, device=DEVICE)
    except Exception as e:
        print(f"  CUDA failed ({e}), falling back to CPU")
        embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    print(f"  Embedding dim: {embedder.get_sentence_embedding_dimension()}")

    print("\n── Loading sources ──────────────────────────────────────")
    all_docs = []

    print("\n[1/3] Claude")
    all_docs += load_claude(IMPORTS_DIR)

    print("\n[2/3] ChatGPT")
    all_docs += load_chatgpt(IMPORTS_DIR)

    print("\n[3/3] Cursor / Windsurf")
    all_docs += load_cursor_windsurf(IMPORTS_DIR)

    total = len(all_docs)
    print(f"\nTotal chunks to index: {total}")

    if not all_docs:
        print("Nothing to index. Check that imports directory is populated.")
        return

    print(f"\n── Embedding + upserting (batch={BATCH_SIZE}) ──────────")
    t0 = time.time()
    for i in range(0, total, BATCH_SIZE):
        batch = all_docs[i:i + BATCH_SIZE]
        upsert_batch(collection, embedder, batch, i)
        done = i + len(batch)
        elapsed = time.time() - t0
        rate = done / elapsed if elapsed > 0 else 0
        eta = (total - done) / rate if rate > 0 else 0
        print(f"  {done:>6}/{total}  {done/total*100:.0f}%  "
              f"{rate:.0f} chunks/s  ETA {eta/60:.1f}m", flush=True)

    final = collection.count()
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"DONE — {final} documents in '{COLLECTION_NAME}'")
    print(f"Total time: {elapsed/60:.1f} minutes")
    print(f"{'='*60}")
    print("\nCutover steps when ready:")
    print("  1. Test:    python ~/ai-stack/scripts/test_rag_query.py")
    print("  2. Switch:  edit .env → CHROMA_COLLECTION=faithh_knowledge_base_v2")
    print("  3. Restart: sudo systemctl restart faithh-backend")
    print("  4. Cleanup: delete faithh_knowledge_base (old collection) when satisfied")


if __name__ == "__main__":
    main()
