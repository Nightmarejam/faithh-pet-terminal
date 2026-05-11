#!/usr/bin/env python3
"""
Retro-tag Chroma rows with domain missing or set to unknown (case-insensitive).

Pages the collection like purge/dedupe scripts; classifies from metadata (source,
filename, category) and an optional document snippet. Default is dry-run; use --execute
to apply batched metadata updates.

Environment: CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION,
  CHROMA_MAINT_BATCH_SIZE (default 5000), CHROMA_MAINT_REQUEST_TIMEOUT_S

Examples:
  python scripts/tag_unknown_domains.py --dry-run
  python scripts/tag_unknown_domains.py --execute
"""

from __future__ import annotations

import argparse
import os
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _chroma_host_raw() -> str:
    h = (os.environ.get("CHROMA_HOST") or "").strip()
    if h:
        return h
    legacy = (os.environ.get("CHROMADB_HOST") or "").strip()
    if legacy:
        p = os.environ.get("CHROMADB_PORT") or os.environ.get("CHROMA_PORT") or "8000"
        if "://" in legacy:
            return legacy
        return f"http://{legacy}:{p}"
    return "localhost"


def _parse_chroma_host_port() -> tuple[str, int]:
    raw = _chroma_host_raw()
    if raw.startswith("http://") or raw.startswith("https://"):
        u = urlparse(raw)
        host = u.hostname or "localhost"
        port = int(os.environ.get("CHROMA_PORT", u.port or 8000))
        return host, port
    if ":" in raw and raw.count(":") == 1:
        h, _, p = raw.partition(":")
        return h, int(os.environ.get("CHROMA_PORT", p))
    return raw, int(os.environ.get("CHROMA_PORT", "8000"))


def _client(host: str, port: int) -> chromadb.ClientAPI:
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    return chromadb.HttpClient(
        host=host,
        port=port,
        settings=Settings(
            anonymized_telemetry=False,
            chroma_query_request_timeout_seconds=timeout_s,
            chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
        ),
    )


def _is_unknown_domain(meta: dict | None) -> bool:
    if not meta:
        return True
    d = meta.get("domain")
    if d is None:
        return True
    s = str(d).strip().lower()
    return s in ("", "unknown", "none")


def classify_domain(meta: dict | None, doc_snippet: str) -> str:
    """Return new domain label (handoff heuristics + category hints)."""
    m = meta or {}
    cat = str(m.get("category") or "").lower()
    src = " ".join(
        str(m.get(k) or "")
        for k in ("source", "filename", "path", "file_stem", "title")
    ).lower()
    blob = f"{src} {doc_snippet[:800].lower()}"

    if cat in ("irs_pub", "oregon_tax") or any(
        x in blob for x in ("irs.gov", "irs-pdf", "1040", "schedule c", "schedule e")
    ):
        return "reference_tax"
    if cat in ("land_use",) or any(
        x in blob
        for x in (
            "oregonlegislature",
            "ors ",
            "oregon law",
            "statute",
            "/bills_laws/ors",
        )
    ):
        return "reference_law"
    if cat == "constella" or "constella" in blob:
        return "constella"
    if cat in ("alife_experiment", "alife_results", "alife_cross_experiment_pattern") or "alife" in blob:
        return "alife"
    if any(
        x in blob
        for x in (
            "faithh",
            "faithh_professional_backend",
            "chromadb",
            "workspace registry",
            "rag_api",
            "/api/chat",
        )
    ):
        return "faithh"
    return "general_knowledge"


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Tag unknown-domain Chroma metadata.")
    ap.add_argument(
        "--collection",
        default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"),
    )
    ap.add_argument("--execute", action="store_true", help="Apply updates (default dry-run)")
    ap.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("CHROMA_MAINT_BATCH_SIZE", "5000")),
    )
    ap.add_argument(
        "--update-chunk",
        type=int,
        default=500,
        help="Rows per collection.update call",
    )
    ap.add_argument("--limit", type=int, default=0, help="Max rows to consider (0=all)")
    args = ap.parse_args()

    batch_size = max(1, args.batch_size)
    update_chunk = max(1, args.update_chunk)
    host, port = _parse_chroma_host_port()
    coll = _client(host, port).get_collection(name=args.collection)

    total = coll.count()
    offset = 0
    examined = 0
    would_change = 0
    hist: Counter[str] = Counter()
    pending_ids: list[str] = []
    pending_metas: list[dict] = []

    def flush_updates() -> None:
        nonlocal pending_ids, pending_metas
        if not pending_ids:
            return
        if args.execute:
            coll.update(ids=pending_ids, metadatas=pending_metas)
        pending_ids = []
        pending_metas = []

    while offset < total:
        if args.limit and examined >= args.limit:
            break
        take = min(batch_size, total - offset)
        if args.limit:
            take = min(take, args.limit - examined)
        if take <= 0:
            break
        page = coll.get(
            limit=take,
            offset=offset,
            include=["metadatas", "documents"],
        )
        offset += take
        ids = page.get("ids") or []
        metas = page.get("metadatas") or []
        docs = page.get("documents") or []
        for i, rid in enumerate(ids):
            examined += 1
            meta = metas[i] if i < len(metas) else {}
            doc = docs[i] if i < len(docs) else ""
            if not _is_unknown_domain(meta):
                continue
            label = classify_domain(meta, doc or "")
            hist[label] += 1
            would_change += 1
            if meta.get("domain") == label:
                continue
            new_meta = dict(meta) if meta else {}
            new_meta["domain"] = label
            new_meta["domain_tagged_by"] = "tag_unknown_domains.py"
            pending_ids.append(rid)
            pending_metas.append(new_meta)
            if len(pending_ids) >= update_chunk:
                flush_updates()

    flush_updates()

    print(
        f"Host {host}:{port} collection={args.collection} total_rows={total} "
        f"examined={examined} unknown_tagged={would_change}"
    )
    print("Proposed domain distribution (for rows that were unknown/missing):")
    for k, v in hist.most_common():
        print(f"  {k}: {v}")
    if args.execute:
        print("Applied updates (--execute).")
    else:
        print("Dry-run: no writes. Pass --execute to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
