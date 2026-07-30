#!/usr/bin/env python3
"""Measure how much of a legacy collection is already represented in the live one.

Answers the only question that matters before deleting a collection: is this content
retrievable from somewhere else? Title comparison cannot answer it — the two
collections chunk differently (legacy: 1500 chars; v2: 5 messages per chunk), so ids
and titles never line up even when the same conversation is present in both.

So compare semantically. Sample from the legacy collection, embed each sample with the
LIVE embedder, query v2, and record the nearest distance. A sample with a close
neighbour in v2 is covered; one without is unique and would be lost.

Run from the workstation — the Gen8 cannot sustain GPU compute
(docs/architecture/GEN8_POWER_CONSTRAINT.md). Reads only; deletes nothing.

Usage:
    python scripts/ingest/measure_overlap.py --sample 400
"""
from __future__ import annotations

import argparse
import os
import random
import sys

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
MODEL = os.environ.get("FAITHH_EMBEDDER_MODEL", "BAAI/bge-base-en-v1.5")
DEVICE = os.environ.get("FAITHH_EMBED_DEVICE", "cpu")

# Below this, the sampled text has a near-equivalent already in the target.
COVERED = float(os.environ.get("OVERLAP_COVERED_DISTANCE", "0.35"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="faithh_knowledge_base")
    ap.add_argument("--target", default="faithh_knowledge_base_v2")
    ap.add_argument("--sample", type=int, default=400)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args()

    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    src = client.get_collection(args.source)
    tgt = client.get_collection(args.target)
    total = src.count()
    print(f"source {args.source}: {total:,}")
    print(f"target {args.target}: {tgt.count():,}")

    # Spread the sample across the whole collection rather than taking a prefix:
    # these were written in ingest order, so a prefix is one era of conversations.
    random.seed(args.seed)
    offsets = sorted(random.sample(range(max(1, total)), min(args.sample, total)))

    docs, metas = [], []
    for off in offsets:
        try:
            b = src.get(limit=1, offset=off, include=["documents", "metadatas"])
            d = (b.get("documents") or [None])[0]
            if d and d.strip():
                docs.append(d)
                metas.append((b.get("metadatas") or [{}])[0] or {})
        except Exception:
            continue
    print(f"sampled {len(docs)} documents\n")

    model = SentenceTransformer(MODEL, device=DEVICE)
    print(f"embedding with {MODEL} ({model.get_sentence_embedding_dimension()}-dim) on {DEVICE}")

    covered, uncovered = 0, []
    B = 32
    for i in range(0, len(docs), B):
        batch = docs[i : i + B]
        embs = model.encode(batch, batch_size=16, show_progress_bar=False).tolist()
        res = tgt.query(query_embeddings=embs, n_results=1, include=["distances"])
        for j, dist_row in enumerate(res.get("distances") or []):
            d = dist_row[0] if dist_row else 1.0
            if d <= COVERED:
                covered += 1
            else:
                uncovered.append((d, metas[i + j], batch[j][:110]))
        print(f"  {min(i+B, len(docs))}/{len(docs)}", end="\r", flush=True)

    n = covered + len(uncovered)
    print(f"\n\noverlap at distance <= {COVERED}:")
    print(f"   covered   {covered:>5} / {n}  ({100*covered/max(1,n):.1f}%)")
    print(f"   uncovered {len(uncovered):>5} / {n}  ({100*len(uncovered)/max(1,n):.1f}%)")
    print(f"\n   projected unique documents: ~{int(total * len(uncovered) / max(1, n)):,} of {total:,}")

    if uncovered:
        print("\n   least-covered samples:")
        # Sort on distance only. Tuple comparison falls through to the metadata dicts
        # whenever two distances tie, and dicts are not orderable.
        for d, m, text in sorted(uncovered, key=lambda u: u[0], reverse=True)[:8]:
            label = str(m.get("source") or m.get("title") or "?")[:40]
            # Windows consoles default to cp1252; sampled chat text is full of em
            # dashes and emoji. Coerce rather than let the report die on an encode.
            safe = text[:60].encode("ascii", "replace").decode("ascii")
            print(f"     d={d:.3f}  {label:<42} {safe!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
