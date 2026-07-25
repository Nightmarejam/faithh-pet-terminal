#!/usr/bin/env python3
"""
Remove ChromaDB chunks that look like accidental noise (venv paths, inventory logs, etc.).

Scans the collection in pages (default 5,000 rows) with metadata-only payloads first, then
fetches document text only for rows that need body inspection. Deletes run in chunks (default
500) to avoid oversized HTTP requests on remote servers.

Uses collection.count() + collection.get(limit, offset). Default collection matches backend:
faithh_knowledge_base.

Environment (optional):
  CHROMA_MAINT_BATCH_SIZE   — scan page size (default 5000)
  CHROMA_MAINT_DOC_SUBCHUNK — ids per get(ids=...) for document fetch (default 200)
  CHROMA_MAINT_DELETE_CHUNK — ids per coll.delete (default 500)
  CHROMA_MAINT_REQUEST_TIMEOUT_S — chromadb Settings query/sysdb timeouts (default 120)

Examples:
  python scripts/purge_chroma_noise.py --dry-run
  python scripts/purge_chroma_noise.py --execute
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings


def _load_repo_dotenv() -> None:
    """Populate os.environ from repo-root .env; never override already-exported vars."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _chroma_host_raw() -> str:
    """Prefer CHROMA_HOST, then legacy CHROMADB_HOST+port, then localhost."""
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


NOISE_FILENAME = re.compile(
    r"(^|/)current_file_inventory\.log$|\.pyc$|\.pyo$",
    re.I,
)
NOISE_PATH_HINT = re.compile(
    r"(/|\\)(venv|\.venv|env|node_modules|__pycache__|\.git)(/|\\)|"
    r"site-packages|current_file_inventory\.log",
    re.I,
)


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


def _noise_from_metadata_only(meta: dict | None) -> bool:
    fn = (meta or {}).get("filename") or ""
    src = (meta or {}).get("source") or ""
    pathish = f"{src}/{fn}".lower()
    if NOISE_FILENAME.search(fn or ""):
        return True
    if NOISE_PATH_HINT.search(pathish):
        return True
    return False


def _noise_from_document(doc: str | None) -> bool:
    blob = (doc or "")[:8000]
    if NOISE_PATH_HINT.search(blob):
        return True
    if "current_file_inventory.log" in blob.lower():
        return True
    return False


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Purge noise documents from a Chroma collection.")
    ap.add_argument(
        "--collection",
        default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"),
        help="Chroma collection name",
    )
    ap.add_argument("--execute", action="store_true", help="Actually delete (default is dry-run)")
    ap.add_argument("--limit", type=int, default=0, help="Max ids to delete (0 = no limit)")
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

    doc_subchunk = int(os.environ.get("CHROMA_MAINT_DOC_SUBCHUNK", "200"))
    batch_size = max(1, args.batch_size)
    delete_chunk = max(1, args.delete_chunk_size)

    host, port = _parse_chroma_host_port()
    client = _chroma_client(host, port)
    coll = client.get_collection(name=args.collection)

    total = coll.count()
    to_delete: list[str] = []
    scanned = 0
    offset = 0

    while offset < total:
        page = coll.get(
            limit=batch_size,
            offset=offset,
            include=["metadatas"],
        )
        ids = page.get("ids") or []
        if not ids:
            break
        metas = page.get("metadatas") or []

        need_docs: list[str] = []
        for i, doc_id in enumerate(ids):
            meta = metas[i] if i < len(metas) else None
            md = meta if isinstance(meta, dict) else None
            if _noise_from_metadata_only(md):
                to_delete.append(str(doc_id))
            else:
                need_docs.append(str(doc_id))

        for j in range(0, len(need_docs), doc_subchunk):
            chunk_ids = need_docs[j : j + doc_subchunk]
            dres = coll.get(ids=chunk_ids, include=["metadatas", "documents"])
            dids = dres.get("ids") or []
            ddocs = dres.get("documents") or []
            dmetas = dres.get("metadatas") or []
            by_id: dict[str, tuple[str | None, dict | None]] = {}
            for k, did in enumerate(dids):
                doc = ddocs[k] if k < len(ddocs) else None
                m = dmetas[k] if k < len(dmetas) else None
                md2 = m if isinstance(m, dict) else None
                by_id[str(did)] = (doc, md2)
            for did in chunk_ids:
                doc, md2 = by_id.get(did, (None, None))
                if _noise_from_document(doc):
                    to_delete.append(did)

        scanned += len(ids)
        print(
            f"[Progress] {scanned:,} / {total:,} records scanned... "
            f"(Noise candidates: {len(to_delete):,})",
            flush=True,
        )
        offset += batch_size

    if args.limit and len(to_delete) > args.limit:
        to_delete = to_delete[: args.limit]

    print(f"Collection: {args.collection} @ {host}:{port}")
    print(f"Total rows: {total:,}")
    print(f"Noise candidates: {len(to_delete):,}")

    if not to_delete:
        return 0

    for sample in to_delete[:25]:
        print(f"  - {sample}")

    if not args.execute:
        print("Dry-run only. Pass --execute to delete.")
        return 0

    for i in range(0, len(to_delete), delete_chunk):
        chunk = to_delete[i : i + delete_chunk]
        coll.delete(ids=chunk)
        print(f"Deleted {len(chunk):,} ids...", flush=True)

    print(f"Done. Removed {len(to_delete):,} documents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
