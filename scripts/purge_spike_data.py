#!/usr/bin/env python3
"""
Surgical purge of a metadata-defined spike cohort (default: 2026-03-31 + project_docs).

Targets rows where:
  - indexed_at OR created_at OR timestamp OR mtime ... starts with the spike date
  - AND category / document_type contains the category substring (case-insensitive)

Default mode is dry-run (no deletes). Pass --execute to delete in chunks.

Optional:
  --date YYYY-MM-DD
  --category SUBSTRING  (default project_doc matches project_docs)

Environment: CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION, CHROMADB_* (legacy),
  CHROMA_MAINT_BATCH_SIZE, CHROMA_MAINT_DELETE_CHUNK, CHROMA_MAINT_REQUEST_TIMEOUT_S
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings

from chroma_spike_cohort import matches_spike_cohort


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


def _chunks(lst: list[str], n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Purge Chroma spike cohort by metadata")
    ap.add_argument("--execute", action="store_true", help="Perform deletes (default: dry-run)")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run (default); redundant unless combined with sanity checks",
    )
    ap.add_argument("--date", default="2026-03-31", help="Spike date prefix (YYYY-MM-DD)")
    ap.add_argument(
        "--category",
        default="project_doc",
        help="Category substring (default matches project_docs)",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("CHROMA_MAINT_BATCH_SIZE", "5000")),
    )
    ap.add_argument(
        "--delete-chunk",
        type=int,
        default=int(os.environ.get("CHROMA_MAINT_DELETE_CHUNK", "500")),
    )
    ap.add_argument(
        "--collection",
        default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"),
    )
    args = ap.parse_args()

    if args.execute and args.dry_run:
        print("Error: use only one of --execute or --dry-run.")
        return 2

    dry_run = not args.execute
    batch_size = max(1, args.batch_size)
    delete_chunk = max(1, args.delete_chunk)

    host, port = _parse_chroma_host_port()
    client = _chroma_client(host, port)
    coll = client.get_collection(name=args.collection)
    total = coll.count()

    print(f"Collection : {args.collection} @ {host}:{port}")
    print(f"Total rows : {total:,}")
    print(f"Targeting  : date prefix {args.date!r} + category contains {args.category!r}")
    print(f"Mode       : {'DRY RUN' if dry_run else '*** EXECUTE ***'}\n")

    to_delete: list[str] = []
    offset = 0
    while offset < total:
        batch = coll.get(limit=batch_size, offset=offset, include=["metadatas"])
        ids = batch.get("ids") or []
        metas = batch.get("metadatas") or []
        for i, doc_id in enumerate(ids):
            raw = metas[i] if i < len(metas) else None
            meta = raw if isinstance(raw, dict) else None
            if matches_spike_cohort(
                meta,
                date_prefix=args.date,
                category_substring=args.category,
            ):
                to_delete.append(str(doc_id))
        offset += batch_size
        if offset % 50_000 == 0 or offset >= total:
            print(
                f"[Progress] {min(offset, total):,} / {total:,} scanned "
                f"... targeted: {len(to_delete):,}",
                flush=True,
            )

    print("\nScan complete.")
    print(f"  Rows matching filter : {len(to_delete):,}")
    print(f"  Rows to keep         : {total - len(to_delete):,}")

    if dry_run:
        print("\nDry run — nothing deleted. Re-run with --execute to proceed.")
        return 0

    if not to_delete:
        print("Nothing to delete.")
        return 0

    print(f"\nDeleting in chunks of {delete_chunk}...")
    deleted = 0
    for chunk in _chunks(to_delete, delete_chunk):
        coll.delete(ids=chunk)
        deleted += len(chunk)
        print(f"  Deleted {deleted:,} / {len(to_delete):,} ...", flush=True)

    final_count = coll.count()
    print(f"\nDone. Removed {len(to_delete):,} documents.")
    print(f"Collection now has {final_count:,} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
