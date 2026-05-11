#!/usr/bin/env python3
"""
List Chroma HTTP collections and row counts (post-purge / silo audit).

Uses the same env as FAITHH: CHROMA_HOST, CHROMA_PORT, CHROMADB_* (legacy),
CHROMA_MAINT_REQUEST_TIMEOUT_S.

Example:
  python scripts/list_chroma_collections.py
"""

from __future__ import annotations

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


def main() -> int:
    _load_repo_dotenv()
    host, port = _parse_chroma_host_port()
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    settings = Settings(
        anonymized_telemetry=False,
        chroma_query_request_timeout_seconds=timeout_s,
        chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
    )
    client = chromadb.HttpClient(host=host, port=port, settings=settings)
    cols = client.list_collections()
    print(f"Chroma @ {host}:{port}")
    print(f"Collections found: {len(cols)}")
    for c in cols:
        col = client.get_collection(name=c.name)
        print(f"  {c.name}: {col.count():,} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
