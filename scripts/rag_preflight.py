#!/usr/bin/env python3
"""Fail loudly when the query embedder and the target collection disagree on dimension.

This is the check that would have caught the 2026-07-26 incident, where
CHROMA_COLLECTION pointed at a 384-dim collection while queries were embedded at
768. Chroma rejected every query, the backend swallowed the error, best_distance
reported a default 1.0, and answers came back fluent but completely ungrounded —
a silent failure that reads as working software.

Deliberately does NOT load the embedding model: it maps model name -> dimension
from a table, so it runs anywhere in under a second with no GPU, no torch, and no
model download. That is what makes it cheap enough to run on every start.

Exit codes:  0 = healthy   1 = misconfigured   2 = could not check
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

# Dimensions of embedders this project has actually used. A model missing here is
# reported as unknown rather than assumed compatible — guessing would defeat the point.
KNOWN_DIMS = {
    "BAAI/bge-base-en-v1.5": 768,
    "BAAI/bge-small-en-v1.5": 384,
    "BAAI/bge-large-en-v1.5": 1024,
    "all-MiniLM-L6-v2": 384,
    "sentence-transformers/all-MiniLM-L6-v2": 384,
}

DEFAULT_HOST = "servicebox.taileb8c60.ts.net"


def _host_port() -> tuple[str, int]:
    raw = os.environ.get("CHROMA_HOST") or os.environ.get("CHROMADB_HOST") or DEFAULT_HOST
    port = int(os.environ.get("CHROMA_PORT") or os.environ.get("CHROMADB_PORT") or 8000)
    # CHROMA_HOST is written both bare and as a URL across this repo's configs.
    raw = raw.replace("http://", "").replace("https://", "").rstrip("/")
    if ":" in raw:
        host, _, maybe_port = raw.partition(":")
        if maybe_port.isdigit():
            return host, int(maybe_port)
        return host, port
    return raw, port


def _get(url: str, timeout: int = 15):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode())


def main() -> int:
    host, port = _host_port()
    base = f"http://{host}:{port}/api/v2/tenants/default_tenant/databases/default_database"

    collection = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base_v2")
    model = (os.environ.get("FAITHH_EMBEDDER_MODEL")
             or os.environ.get("FAITHH_EMBED_MODEL")
             or "BAAI/bge-base-en-v1.5")

    print(f"chroma      : {host}:{port}")
    print(f"collection  : {collection}")
    print(f"embedder    : {model}")

    try:
        cols = _get(f"{base}/collections")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"\nCANNOT CHECK: Chroma unreachable at {host}:{port} — {exc}")
        return 2

    by_name = {c["name"]: c for c in cols}
    if collection not in by_name:
        print(f"\nMISCONFIGURED: collection {collection!r} does not exist.")
        print("  available: " + ", ".join(
            f"{c['name']} ({c.get('dimension')}d)" for c in cols))
        return 1

    col_dim = by_name[collection].get("dimension")
    want = KNOWN_DIMS.get(model)

    if want is None:
        print(f"\nCANNOT CHECK: dimension of {model!r} is unknown.")
        print(f"  collection reports {col_dim}d. Add the model to KNOWN_DIMS.")
        return 2

    print(f"expected dim: {want}   collection dim: {col_dim}")

    if col_dim != want:
        print(f"\nMISCONFIGURED: {model} emits {want}d but {collection} is {col_dim}d.")
        print("  Every query will be rejected and best_distance will report 1.0 —")
        print("  answers will look fluent and be completely ungrounded.")
        alts = [c["name"] for c in cols if c.get("dimension") == want]
        if alts:
            print("  Compatible collections: " + ", ".join(alts))
        else:
            print(f"  No {want}d collection exists. Re-index, or change the embedder")
            print("  only if you accept orphaning the current one.")
        return 1

    print("\nOK: embedder and collection agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
