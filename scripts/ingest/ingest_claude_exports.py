#!/usr/bin/env python3
"""Ingest Claude conversation chunks into ChromaDB — Job A, phase 3.

WRITES to Chroma. Run the manifest first and review it; this uses the identical
parsing, chunking, IDs and classifier, so what the manifest showed is what lands.

    python ingest_claude_exports.py ~/ingest/raw --dry-run     # count only
    python ingest_claude_exports.py ~/ingest/raw --execute

Idempotent: chunk IDs are deterministic (claude_chunk_{uuid}_{n}) and existing
IDs are skipped, so re-running after adding an export only writes the new ones.

Embeds with BAAI/bge-base-en-v1.5 (768-dim) to match faithh_knowledge_base_v2.
Uses the GPU when available — see AGENTS.md for the dimension rule and the
FAITHH_EMBED_DEVICE override.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from manifest_claude_exports import (  # noqa: E402
    COLLECTION,
    chunk_conversation,
    message_text,
    parse_dt,
)
from classify import classify  # noqa: E402

BATCH = 128


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--execute", action="store_true", help="actually write (default is dry-run)")
    ap.add_argument("--since")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--device", default=None, help="cpu|cuda (default: auto)")
    args = ap.parse_args()

    import chromadb
    import torch
    from sentence_transformers import SentenceTransformer

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device: {device}")

    since = args.since
    files = sorted(Path(args.root).rglob("conversations.json"))
    if not files:
        print(f"no conversations.json under {args.root}", file=sys.stderr)
        return 1

    # ---- build the payload (same path the manifest took) ----
    ids, docs, metas = [], [], []
    for f in files:
        source = f.parent.name
        import json

        convs = json.loads(f.read_text(encoding="utf-8"))
        print(f"reading {source}: {len(convs)} conversations")
        for conv in convs:
            dt = parse_dt(conv.get("created_at"))
            if since and (not dt or dt.date().isoformat() < since):
                continue
            chunks = chunk_conversation(conv)
            if not chunks:
                continue
            msgs = [
                {"sender": m.get("sender"), "text": message_text(m)}
                for m in (conv.get("chat_messages") or [])
            ]
            res = classify(conv.get("name") or "", msgs)
            uuid = conv.get("uuid") or "nouuid"
            for c in chunks:
                ids.append(f"claude_chunk_{uuid}_{c['chunk_num']}")
                docs.append(c["text"])
                metas.append(
                    {
                        "source": "claude_export",
                        "source_account": source,
                        "conversation_uuid": uuid,
                        "conversation_title": (conv.get("name") or "Untitled")[:200],
                        "date": dt.date().isoformat() if dt else "",
                        "chunk_num": c["chunk_num"],
                        "messages_in_chunk": c["messages"],
                        "topic": res.topic,
                        "modes": ",".join(res.modes) if res.modes else "unclassified",
                        "primary_mode": res.primary_mode,
                        "human_ratio": res.structure.get("human_ratio", 0),
                        "ingested": time.strftime("%Y-%m-%d"),
                    }
                )

    print(f"prepared {len(ids):,} chunks")

    client = chromadb.HttpClient(host=args.host, port=args.port)
    col = client.get_collection(COLLECTION)
    before = col.count()
    print(f"collection {COLLECTION}: {before:,} documents before")

    # ---- skip what is already there ----
    existing = set()
    for i in range(0, len(ids), 500):
        got = col.get(ids=ids[i : i + 500], include=[])
        existing.update(got.get("ids") or [])
    keep = [i for i, cid in enumerate(ids) if cid not in existing]
    print(f"already present: {len(existing):,}   to write: {len(keep):,}")

    if not keep:
        print("nothing new — done.")
        return 0
    if not args.execute:
        print("\nDRY RUN — pass --execute to write.")
        return 0

    model = SentenceTransformer("BAAI/bge-base-en-v1.5", device=device)
    t0 = time.time()
    written = 0
    for s in range(0, len(keep), BATCH):
        idx = keep[s : s + BATCH]
        batch_docs = [docs[i] for i in idx]
        embs = model.encode(batch_docs, batch_size=64, show_progress_bar=False).tolist()
        col.add(
            ids=[ids[i] for i in idx],
            documents=batch_docs,
            metadatas=[metas[i] for i in idx],
            embeddings=embs,
        )
        written += len(idx)
        el = time.time() - t0
        print(f"  {written:,}/{len(keep):,}  {written/max(el,0.01):.0f} chunks/sec", flush=True)

    after = col.count()
    print(f"\ndone in {time.time()-t0:.0f}s")
    print(f"collection {COLLECTION}: {before:,} -> {after:,}  (+{after-before:,})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
