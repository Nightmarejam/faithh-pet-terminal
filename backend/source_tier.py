#!/usr/bin/env python3
"""Confirmability source tiering for retrieval — the fix for the RAG-drowning bug.

Ported 2026-07-31 from homelab/experiments/autonomy/reflect.py, where the same
idea was proven against files. This adapts it to Chroma: reflect.py tiered by
*path*, this tiers by *collection plus per-entry metadata*.

## Not to be confused with tiered_rag_processor.py

That module is **storage** tiering — a hot/warm cache that promotes and demotes
documents by access frequency, for speed. This is **confirmability** tiering —
weighting a hit by how well-attested its source is, for correctness. Same word,
unrelated jobs. A document can be hot and speculative, or cold and confirmed.

## The problem

`faithh_knowledge_base_v2` holds 63,770 raw chat-transcript chunks.
`faithh_curated` holds a few hundred reviewed entries distilled from that same
material, each carrying a confirmability tier. Query both naively and the bulk
wins on volume alone: at roughly 1:280, top-k by distance will essentially never
return the curated version of a fact. The distilled answer gets buried by the
transcript it was distilled from.

## The rule

    score = (1 - distance) * source_tier

Weights follow reflect.py's scale, and the tiers follow
constella-framework/docs/reference/confirmability.md, which is canonical for the
whole ecosystem:

    confirmed    3.0   backed by a receipt — a live check, git history, a benchmark
    asserted     1.0   stated from conversation, plausible, unverified
    speculative  0.8   hypothesis or design intent — never feeds reasoning-as-fact
    bulk         0.15  raw transcript / imported reference

A confirmed entry therefore outranks a raw chunk by 20x before distance is even
considered, which is the intent: attested knowledge should have to be *clearly*
less relevant before unattested bulk beats it.

## Dimension safety

Collections whose dimension disagrees with the embedder are skipped rather than
queried. Querying a 384-dim collection with 768-dim vectors is the 2026-07-26
failure — Chroma rejects it, the error gets swallowed, and best_distance reports
a default 1.0 while answers come back fluent and completely ungrounded.
`faithh_knowledge_base` (384) is skipped for exactly this reason.
"""
from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger(__name__)

# Weight by confirmability tier. Source: constella-framework confirmability.md.
TIER_WEIGHT: dict[str, float] = {
    "confirmed": 3.0,
    "asserted": 1.0,
    "speculative": 0.8,
    "refuted": 0.0,       # checked and found false — never surfaced as support
}
BULK_WEIGHT = 0.15

# Collections to search, in no particular order. A collection not listed here is
# not searched at all; listing is deliberate so a new collection cannot start
# influencing answers just by existing.
CURATED_COLLECTION = os.environ.get("FAITHH_CURATED_COLLECTION", "faithh_curated")
BULK_COLLECTION = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base_v2")


def weight_for(collection_name: str, metadata: dict[str, Any] | None) -> float:
    """Weight one hit. Curated entries carry their own tier; bulk gets the floor."""
    md = metadata or {}
    if collection_name == CURATED_COLLECTION:
        # Prefer the explicit numeric weight stage 4 wrote; fall back to the tier.
        explicit = md.get("source_tier")
        if isinstance(explicit, (int, float)):
            return float(explicit)
        return TIER_WEIGHT.get(str(md.get("tier", "asserted")), 1.0)
    return BULK_WEIGHT


def tiered_search(client, embed, query: str, n_results: int = 5,
                  per_collection: int = 20) -> list[dict[str, Any]]:
    """Search curated + bulk, re-rank by (1 - distance) * source_tier.

    `client` is a chromadb client, `embed` a callable str -> list[float]. Both are
    injected so this module stays importable without torch present — it is pure
    ranking logic and should be testable without a GPU.

    Over-fetches per collection (`per_collection`) before re-ranking, because a
    curated entry that would win on weight can sit outside a naive top-5.
    """
    vec = embed(query)
    dim = len(vec)
    hits: list[dict[str, Any]] = []

    for name in (CURATED_COLLECTION, BULK_COLLECTION):
        try:
            col = client.get_collection(name)
        except Exception as exc:
            log.warning("source_tier: collection %s unavailable (%s)", name, exc)
            continue

        col_dim = (col.metadata or {}).get("dimension")
        if col_dim is not None and int(col_dim) != dim:
            # Skipping is the whole point: querying anyway yields silent garbage.
            log.warning("source_tier: skipping %s — %sd collection vs %sd query",
                        name, col_dim, dim)
            continue

        try:
            res = col.query(query_embeddings=[vec], n_results=per_collection,
                            include=["documents", "metadatas", "distances"])
        except Exception as exc:
            log.warning("source_tier: query failed on %s (%s)", name, exc)
            continue

        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for doc, md, dist in zip(docs, metas, dists):
            w = weight_for(name, md)
            if w <= 0:
                continue        # refuted: excluded, not merely down-ranked
            hits.append({
                "text": doc,
                "metadata": md or {},
                "distance": dist,
                "collection": name,
                "source_tier": w,
                "score": (1.0 - float(dist)) * w,
            })

    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:n_results]
