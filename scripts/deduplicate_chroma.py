#!/usr/bin/env python3
"""
De-duplicate ChromaDB documents in the main knowledge collection.

Streams the collection in pages (default 5,000 rows) with metadatas + documents per page,
tracks the best keeper per content hash across all batches, then deletes losers in chunks
(default 500) to avoid oversized delete requests on remote servers.

Groups rows by SHA-256 of normalized document text (or metadata fingerprint when text is empty).
Within each group, keeps one row (preferring the newest mtime from metadata when present) and
deletes the rest.

Run noise purge first when cleaning a polluted index:
  python scripts/purge_chroma_noise.py --execute
  python scripts/deduplicate_chroma.py --dry-run
  python scripts/deduplicate_chroma.py --execute

Environment: CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION (same as FAITHH backend).

Optional:
  CHROMA_MAINT_BATCH_SIZE    — scan page size (default 5000)
  CHROMA_MAINT_DELETE_CHUNK  — ids per coll.delete (default 500)
  CHROMA_MAINT_REQUEST_TIMEOUT_S — chromadb Settings query/sysdb timeouts (default 120)
"""

from __future__ import annotations

import argparse
import hashlib
import os
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


def _chroma_client(host: str, port: int) -> chromadb.ClientAPI:
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    settings = Settings(
        anonymized_telemetry=False,
        chroma_query_request_timeout_seconds=timeout_s,
        chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
    )
    return chromadb.HttpClient(host=host, port=port, settings=settings)


def _normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def _content_hash(doc: str | None, meta: dict | None) -> str:
    body = _normalize_text(doc)
    if body:
        return hashlib.sha256(body.encode("utf-8", errors="ignore")).hexdigest()
    m = meta or {}
    fingerprint = "|".join(
        str(m.get(k) or "")
        for k in ("filename", "source", "chunk_index", "session_id", "path")
    )
    return hashlib.sha256(fingerprint.encode("utf-8", errors="ignore")).hexdigest()


def _meta_mtime(meta: dict | None) -> float:
    if not meta:
        return 0.0
    for key in ("mtime", "indexed_at", "last_modified", "updated_at", "ts"):
        v = meta.get(key)
        if v is None:
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return 0.0


def _consider_duplicate(
    h: str,
    sid: str,
    mt: float,
    seen: dict[str, tuple[str, float, str]],
    to_delete: list[str],
    dup_hashes: set[str],
) -> None:
    if h not in seen:
        seen[h] = (sid, mt, sid)
        return
    dup_hashes.add(h)
    keep_id, keep_mt, keep_sort = seen[h]
    if (mt, sid) > (keep_mt, keep_sort):
        to_delete.append(keep_id)
        seen[h] = (sid, mt, sid)
    else:
        to_delete.append(sid)


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="De-duplicate Chroma collection by content hash.")
    ap.add_argument(
        "--collection",
        default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"),
        help="Chroma collection name",
    )
    ap.add_argument("--execute", action="store_true", help="Delete duplicates (default is dry-run)")
    ap.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("CHROMA_MAINT_BATCH_SIZE", "5000")),
        help="Rows per scan page (default 5000 or CHROMA_MAINT_BATCH_SIZE)",
    )
    ap.add_argument(
        "--delete-chunk-size",
        type=int,
        default=int(os.environ.get("CHROMA_MAINT_DELETE_CHUNK", "500")),
        help="Ids per delete request (default 500 or CHROMA_MAINT_DELETE_CHUNK)",
    )
    args = ap.parse_args()

    batch_size = max(1, args.batch_size)
    delete_chunk = max(1, args.delete_chunk_size)

    host, port = _parse_chroma_host_port()
    client = _chroma_client(host, port)
    coll = client.get_collection(name=args.collection)

    total = coll.count()
    seen: dict[str, tuple[str, float, str]] = {}
    to_delete: list[str] = []
    dup_hashes: set[str] = set()
    scanned = 0
    offset = 0

    while offset < total:
        page = coll.get(
            limit=batch_size,
            offset=offset,
            include=["metadatas", "documents"],
        )
        ids = page.get("ids") or []
        if not ids:
            break
        metas = page.get("metadatas") or []
        docs = page.get("documents") or []

        for i, doc_id in enumerate(ids):
            meta = metas[i] if i < len(metas) else None
            doc = docs[i] if i < len(docs) else None
            md = meta if isinstance(meta, dict) else None
            h = _content_hash(doc, md)
            mt = _meta_mtime(md)
            sid = str(doc_id)
            _consider_duplicate(h, sid, mt, seen, to_delete, dup_hashes)

        scanned += len(ids)
        print(
            f"[Progress] {scanned:,} / {total:,} records scanned... "
            f"(Duplicates found: {len(to_delete):,})",
            flush=True,
        )
        offset += batch_size

    dup_groups = len(dup_hashes)

    print(f"Collection: {args.collection} @ {host}:{port}")
    print(f"Total rows: {total:,}")
    print(f"Duplicate groups: {dup_groups:,}")
    print(f"IDs to delete: {len(to_delete):,}")

    for sample in to_delete[:30]:
        print(f"  - {sample}")
    if len(to_delete) > 30:
        print(f"  ... and {len(to_delete) - 30:,} more")

    if not to_delete:
        return 0

    if not args.execute:
        print("Dry-run only. Pass --execute to delete duplicates.")
        return 0

    for i in range(0, len(to_delete), delete_chunk):
        chunk = to_delete[i : i + delete_chunk]
        coll.delete(ids=chunk)
        print(f"Deleted {len(chunk):,} ids...", flush=True)

    print(f"Done. Removed {len(to_delete):,} duplicate documents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
