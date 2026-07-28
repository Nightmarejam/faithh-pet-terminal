#!/usr/bin/env python3
"""Re-embed a 384-dim collection into the 768-dim BGE collection.

Older collections were indexed with all-MiniLM-L6-v2 (384-dim) and are therefore
unreachable by the backend, which queries with BAAI/bge-base-en-v1.5 (768-dim).
See AGENTS.md for the dimension rule. This reads documents + metadata out of the
source collection, re-embeds with BGE, and writes into the target.

    python reindex_collection.py governance_corpus --dry-run
    python reindex_collection.py governance_corpus --execute

Run this from a machine with a real GPU (the Gen8 cannot sustain GPU load —
see the power notes). It writes over the network to whatever --host points at.

IDs are prefixed so re-runs are idempotent and the origin stays traceable:
    reidx_<source>_<original_id>
"""
from __future__ import annotations

import argparse
import sys
import time

BATCH_READ = 1000
BATCH_WRITE = 128
TARGET = "faithh_knowledge_base_v2"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="source collection name (384-dim)")
    ap.add_argument("--target", default=TARGET)
    ap.add_argument("--host", default="servicebox.taileb8c60.ts.net")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--execute", action="store_true", help="write (default is dry-run)")
    ap.add_argument("--device", default=None)
    ap.add_argument("--limit", type=int, default=0, help="cap documents, for testing")
    args = ap.parse_args()

    import chromadb
    import torch
    from sentence_transformers import SentenceTransformer

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    client = chromadb.HttpClient(host=args.host, port=args.port)
    src = client.get_collection(args.source)
    dst = client.get_collection(args.target)
    total = src.count()
    if args.limit:
        total = min(total, args.limit)
    print(f"source {args.source}: {src.count():,} docs   target {args.target}: {dst.count():,}")
    print(f"device: {device}   re-embedding up to {total:,}")

    # ---- read everything out first (cheap; text only) ----
    ids, docs, metas = [], [], []
    off = 0
    while off < total:
        n = min(BATCH_READ, total - off)
        r = src.get(limit=n, offset=off, include=["documents", "metadatas"])
        got = r.get("ids") or []
        if not got:
            break
        for i, d, m in zip(got, r.get("documents") or [], r.get("metadatas") or []):
            if not d or not str(d).strip():
                continue
            meta = dict(m or {})
            meta["reindexed_from"] = args.source
            meta["source"] = meta.get("source") or args.source
            ids.append(f"reidx_{args.source}_{i}")
            docs.append(str(d))
            metas.append(meta)
        off += n
    print(f"read {len(ids):,} non-empty documents")

    # ---- skip anything already written ----
    existing = set()
    for i in range(0, len(ids), 500):
        existing.update(dst.get(ids=ids[i : i + 500], include=[]).get("ids") or [])
    keep = [i for i, cid in enumerate(ids) if cid not in existing]
    print(f"already present: {len(existing):,}   to write: {len(keep):,}")

    if not keep:
        print("nothing to do.")
        return 0
    if not args.execute:
        print("\nDRY RUN — pass --execute to write.")
        return 0

    model = SentenceTransformer("BAAI/bge-base-en-v1.5", device=device)
    t0, written = time.time(), 0
    for s in range(0, len(keep), BATCH_WRITE):
        idx = keep[s : s + BATCH_WRITE]
        batch = [docs[i] for i in idx]
        embs = model.encode(batch, batch_size=64, show_progress_bar=False).tolist()
        dst.add(
            ids=[ids[i] for i in idx],
            documents=batch,
            metadatas=[metas[i] for i in idx],
            embeddings=embs,
        )
        written += len(idx)
        el = time.time() - t0
        print(f"  {written:,}/{len(keep):,}  {written/max(el,0.01):.0f}/sec", flush=True)

    print(f"\ndone in {time.time()-t0:.0f}s   {args.target}: {dst.count():,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
