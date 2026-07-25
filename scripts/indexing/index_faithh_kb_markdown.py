#!/usr/bin/env python3
"""
Index markdown/text into the HTTP Chroma collection used by FAITHH
(faithh_knowledge_base by default). Uses the collection's configured embedding function.

Environment (aligned with faithh_professional_backend_fixed.py):
  CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION

Examples:
  venv/bin/python scripts/indexing/index_faithh_kb_markdown.py \\
    --file docs/research/harmonic_body/HARMONIC_BODY.md \\
    --domain faithh --category harmonic_architecture --force

  venv/bin/python scripts/indexing/index_faithh_kb_markdown.py \\
    --source docs/ --recursive --domain faithh --category documentation \\
    --document-type knowledge_base
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import chromadb  # noqa: E402
from chromadb.config import Settings  # noqa: E402

from chroma_ingest_guard import (  # noqa: E402
    check_post_ingest_growth,
    normalize_source_for_metadata,
    validate_bulk_metadata,
)

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
_TEXT_SUFFIXES = frozenset({".md", ".txt", ".markdown"})


def _parse_chroma_host_port() -> tuple[str, int]:
    """Match scripts/generate_db_map.py: CHROMA_HOST may be a bare host or http(s)://host:port."""
    raw = (os.environ.get("CHROMA_HOST") or "").strip()
    if not raw:
        legacy = (os.environ.get("CHROMADB_HOST") or "").strip()
        if legacy:
            p = os.environ.get("CHROMADB_PORT") or os.environ.get("CHROMA_PORT") or "8000"
            raw = legacy if "://" in legacy else f"http://{legacy}:{p}"
        else:
            raw = "127.0.0.1"
    if raw.startswith("http://") or raw.startswith("https://"):
        u = urlparse(raw)
        host = u.hostname or "localhost"
        port = int(os.environ.get("CHROMA_PORT", u.port or 8000))
        return host, port
    if ":" in raw and raw.count(":") == 1:
        h, _, p = raw.partition(":")
        return h, int(os.environ.get("CHROMA_PORT", p))
    return raw, int(os.environ.get("CHROMA_PORT", "8000"))


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = _REPO_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            for sep in ("\n\n", "\n", ". ", " "):
                boundary = text.rfind(sep, start + overlap, end)
                if boundary > start + overlap:
                    end = boundary + len(sep)
                    break
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def chunk_doc_id(rel_source: str, chunk_idx: int) -> str:
    h = hashlib.sha256(f"{rel_source}:{chunk_idx}".encode()).hexdigest()[:16]
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in rel_source[:40])
    return f"faithh_kb_{safe}_{chunk_idx}_{h}"


def _resolve_under_repo(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    resolved = p.resolve() if p.is_absolute() else (_REPO_ROOT / p).resolve()
    try:
        resolved.relative_to(_REPO_ROOT.resolve())
    except ValueError as exc:
        raise SystemExit(f"Path must be inside repo root: {resolved}") from exc
    return resolved


def _collect_index_paths(root: Path, recursive: bool) -> list[Path]:
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")
    if recursive:
        found = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in _TEXT_SUFFIXES]
    else:
        found = [p for p in root.iterdir() if p.is_file() and p.suffix.lower() in _TEXT_SUFFIXES]
    return sorted(found)


def _index_one_path(collection, path: Path, args: argparse.Namespace, script_name: str) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks = [c for c in chunk_text(text) if c.strip()]
    if not chunks:
        return 0

    rel_source = normalize_source_for_metadata(path, _REPO_ROOT)
    indexed_at = datetime.now(timezone.utc).isoformat()
    domain = args.domain.strip()
    category = args.category.strip()
    dt = (args.document_type or "").strip()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for i, chunk in enumerate(chunks):
        did = chunk_doc_id(rel_source, i)
        meta = {
            "domain": domain,
            "category": category,
            "source": rel_source,
            "filename": path.name,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "file_stem": path.stem,
            "indexed_at": indexed_at,
            "timestamp": indexed_at,
            "indexed_by": script_name,
        }
        if dt:
            meta["document_type"] = dt
        bad = validate_bulk_metadata(meta)
        if bad:
            raise SystemExit(f"Metadata guard: missing {bad} for chunk {did}")
        ids.append(did)
        documents.append(chunk)
        metadatas.append(meta)

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(chunks)


def main() -> None:
    _load_repo_dotenv()

    ap = argparse.ArgumentParser(
        description="Index markdown/text into faithh_knowledge_base (HTTP Chroma)",
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="Single .md/.txt path under the repo")
    src.add_argument("--source", help="Directory under the repo to index (use with --recursive for tree)")
    ap.add_argument(
        "--recursive",
        action="store_true",
        help="With --source, include all nested .md/.txt/.markdown files",
    )
    ap.add_argument("--domain", required=True, help="Metadata domain (e.g. faithh)")
    ap.add_argument("--category", required=True, help="Metadata category (e.g. documentation)")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Override BULK_INGEST_GUARD when collection grows >3× in this run",
    )
    ap.add_argument(
        "--collection",
        default="faithh_knowledge_base",
        help="Chroma collection name (FAITHH RAG default: faithh_knowledge_base)",
    )
    ap.add_argument(
        "--document-type",
        default="",
        help="Optional metadata document_type (e.g. knowledge_base)",
    )
    args = ap.parse_args()

    if args.source and not args.recursive:
        raise SystemExit("--source requires --recursive (explicit opt-in to tree ingest)")

    script_name = Path(__file__).name
    host, port = _parse_chroma_host_port()
    collection_name = args.collection.strip()
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    client = chromadb.HttpClient(
        host=host,
        port=port,
        settings=Settings(
            anonymized_telemetry=False,
            chroma_query_request_timeout_seconds=timeout_s,
            chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
        ),
    )
    collection = client.get_collection(name=collection_name)

    if args.file:
        path = _resolve_under_repo(args.file)
        if not path.is_file():
            raise SystemExit(f"File not found: {path}")
        pre_count = collection.count()
        n = _index_one_path(collection, path, args, script_name)
        if n == 0:
            raise SystemExit("No non-empty content to index.")
        post_count = collection.count()
        try:
            check_post_ingest_growth(
                pre_count,
                post_count,
                multiplier=3.0,
                force=args.force,
                label=f"{collection_name} (index_faithh_kb_markdown)",
            )
        except SystemExit as exc:
            print(str(exc), file=sys.stderr)
            raise
        print(f"Indexed {n} chunk(s) from {normalize_source_for_metadata(path, _REPO_ROOT)}")
        print(f"Collection {collection_name}: {pre_count:,} -> {post_count:,}")
        return

    root = _resolve_under_repo(args.source)
    paths = _collect_index_paths(root, recursive=True)
    if not paths:
        raise SystemExit(f"No .md/.txt/.markdown files under {root}")

    pre_count = collection.count()
    total_chunks = 0
    skipped_empty = 0
    for i, p in enumerate(paths, start=1):
        try:
            n = _index_one_path(collection, p, args, script_name)
        except Exception as e:
            print(f"ERROR {p.relative_to(_REPO_ROOT)}: {e}", file=sys.stderr)
            raise
        if n == 0:
            skipped_empty += 1
        else:
            total_chunks += n
        if i % 25 == 0 or i == len(paths):
            print(f"Progress: {i}/{len(paths)} files, {total_chunks} chunks, {skipped_empty} empty", flush=True)

    post_count = collection.count()
    try:
        check_post_ingest_growth(
            pre_count,
            post_count,
            multiplier=3.0,
            force=args.force,
            label=f"{collection_name} (index_faithh_kb_markdown tree)",
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        raise

    print(f"Indexed {total_chunks} chunk(s) from {len(paths)} file(s) ({skipped_empty} empty skipped)")
    print(f"Collection {collection_name}: {pre_count:,} -> {post_count:,}")


if __name__ == "__main__":
    main()
