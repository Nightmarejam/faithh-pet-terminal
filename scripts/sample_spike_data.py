#!/usr/bin/env python3
"""
Sample records from a metadata-defined spike cohort (default: 2026-03-31 + project_docs).

Run before purge_spike_data.py to confirm the cohort is safe to delete.

Usage:
  python scripts/sample_spike_data.py [--count 20] [--seed 42]
  python scripts/sample_spike_data.py --output-json /tmp/spike_samples.json

Environment: CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION, CHROMADB_* (legacy),
  CHROMA_MAINT_BATCH_SIZE, CHROMA_MAINT_REQUEST_TIMEOUT_S
"""

from __future__ import annotations

import argparse
import json
import os
import random
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


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Random samples from spike metadata cohort")
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--date",
        default="2026-03-31",
        help="Date prefix on indexed_at / created_at / timestamp / mtime (YYYY-MM-DD)",
    )
    ap.add_argument(
        "--category",
        default="project_doc",
        help="Substring match on category or document_type (default matches project_docs)",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("CHROMA_MAINT_BATCH_SIZE", "5000")),
        help="Paged get size",
    )
    ap.add_argument("--output-json", type=Path, default=None, help="Write samples to JSON file")
    ap.add_argument(
        "--collection",
        default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"),
    )
    args = ap.parse_args()

    rng = random.Random(args.seed)
    batch_size = max(1, args.batch_size)

    host, port = _parse_chroma_host_port()
    client = _chroma_client(host, port)
    coll = client.get_collection(name=args.collection)
    total = coll.count()

    print(f"Collection: {args.collection} @ {host}:{port}  |  Total rows: {total:,}")
    print(f"Cohort filter: date prefix {args.date!r} + category contains {args.category!r}\n")

    spike_ids: list[str] = []
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
                spike_ids.append(str(doc_id))
        offset += batch_size
        if offset % 50_000 == 0 or offset >= total:
            print(
                f"  Scanned {min(offset, total):,} / {total:,} ... spike candidates: {len(spike_ids):,}",
                flush=True,
            )

    print(f"\nTotal spike candidates found: {len(spike_ids):,}")
    if not spike_ids:
        print("Nothing matched — check date/category fields in the census report.")
        return 0

    k = min(args.count, len(spike_ids))
    sample_ids = rng.sample(spike_ids, k=k)
    rows = coll.get(ids=sample_ids, include=["metadatas", "documents"])
    rids = rows.get("ids") or []
    rmeta = rows.get("metadatas") or []
    rdocs = rows.get("documents") or []
    by_id: dict[str, tuple[dict | None, str | None]] = {}
    for j, rid in enumerate(rids):
        md = rmeta[j] if j < len(rmeta) else None
        meta = md if isinstance(md, dict) else None
        doc = rdocs[j] if j < len(rdocs) else None
        by_id[str(rid)] = (meta, doc if isinstance(doc, str) else None)

    records_out: list[dict[str, object]] = []
    print(f"\n--- {k} random samples from spike cohort ---\n")
    for idx, sid in enumerate(sample_ids):
        meta, doc = by_id.get(str(sid), (None, None))
        preview = (doc or "")[:200]
        print(f"[{idx + 1}] ID: {sid}")
        if meta:
            print(f"    category : {meta.get('category') or meta.get('document_type')}")
            print(f"    domain   : {meta.get('domain') or meta.get('project')}")
            print(f"    source   : {meta.get('source') or meta.get('filename') or '(none)'}")
            print(f"    indexed  : {meta.get('indexed_at') or meta.get('created_at')}")
        else:
            print("    (no metadata)")
        print(f"    preview  : {preview}")
        print()
        records_out.append(
            {
                "id": sid,
                "metadata": meta or {},
                "preview_200": preview,
            }
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(records_out, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Wrote JSON: {args.output_json.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
