#!/usr/bin/env python3
"""
Index governance corpus into ChromaDB with strict metadata and dedupe.

Canonical input root:
  /home/jonat/ai-stack/docs/data/governance_sources
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


REPO_ROOT = Path("/home/jonat/ai-stack")
DEFAULT_INPUT_ROOT = REPO_ROOT / "docs/data/governance_sources"
DEFAULT_REPORT_DIR = REPO_ROOT / "reports/index_runs"
COLLECTION_NAME = "faithh_knowledge_base"

ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def classify_source(path: Path, text: str) -> str:
    lower = f"{str(path).lower()} {text[:400].lower()}"
    if any(k in lower for k in ("constitution", "charter", "bill of rights", "amendment")):
        return "charter"
    if any(k in lower for k in ("treaty", "declaration", "convention", "accord", "united nations", "un ")):
        return "treaty"
    if any(k in lower for k in ("policy", "framework", "governance", "regulation", "statute", "law")):
        return "policy_reference"
    return "analysis"


def chunk_text(text: str, chunk_size: int = 1800, overlap: int = 200) -> list[str]:
    text = text.strip()
    if not text:
        return []
    chunks: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)
        if i + chunk_size >= n:
            break
        i += max(1, chunk_size - overlap)
    return chunks


def load_text(path: Path) -> str:
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            return json.dumps(data, ensure_ascii=True, indent=2)
        except json.JSONDecodeError:
            return path.read_text(encoding="utf-8", errors="ignore")
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> None:
    parser = argparse.ArgumentParser(description="Index governance source corpus")
    parser.add_argument("--input-root", default=str(DEFAULT_INPUT_ROOT))
    parser.add_argument("--host", default=os.getenv("CHROMA_HOST", "servicebox.taileb8c60.ts.net"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CHROMA_PORT", "8000")))
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    input_root = Path(args.input_root)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not input_root.exists():
        raise FileNotFoundError(f"Input root not found: {input_root}")

    files = sorted(
        p for p in input_root.rglob("*") if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    )

    client = chromadb.HttpClient(host=args.host, port=args.port)
    collection = client.get_collection(COLLECTION_NAME)
    existing = collection.get(
        where={"source_type": "governance_source"},
        limit=collection.count(),
        include=["metadatas"],
    )
    existing_hashes = {
        (m or {}).get("content_hash")
        for m in existing.get("metadatas", [])
        if (m or {}).get("content_hash")
    }

    accepted: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    records: list[tuple[str, str, dict[str, Any]]] = []
    indexed_at = datetime.now(UTC).isoformat()

    for path in files:
        text = load_text(path).strip()
        if not text:
            skipped.append({"path": str(path), "reason": "empty_content"})
            continue
        if len(text) < 120:
            skipped.append({"path": str(path), "reason": "too_short"})
            continue

        content_hash = sha256_text(text)
        if content_hash in existing_hashes:
            skipped.append({"path": str(path), "reason": "duplicate_hash"})
            continue

        source_class = classify_source(path, text)
        chunks = chunk_text(text)
        if not chunks:
            skipped.append({"path": str(path), "reason": "chunking_failed"})
            continue

        rel = str(path.relative_to(REPO_ROOT)) if str(path).startswith(str(REPO_ROOT)) else str(path)
        base_id = sha256_text(f"{rel}:{content_hash}")[:16]

        for idx, chunk in enumerate(chunks):
            doc_id = f"governance_{base_id}_{idx:03d}"
            metadata = {
                "domain": "constella_constitutional",
                "source_type": "governance_source",
                "document_type": source_class,
                "category": "project_docs",
                "quality_score": 0.96,
                "source_path": rel,
                "content_hash": content_hash,
                "chunk_index": idx,
                "chunk_total": len(chunks),
                "indexed_at": indexed_at,
            }
            records.append((doc_id, chunk, metadata))

        accepted.append(
            {
                "path": str(path),
                "source_class": source_class,
                "chunks": len(chunks),
                "content_hash": content_hash,
            }
        )

    if not args.dry_run and records:
        embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        docs = [r[1] for r in records]
        embs = embedder.encode(docs, show_progress_bar=False).tolist()
        ids = [r[0] for r in records]
        metas = [r[2] for r in records]
        batch = 64
        for i in range(0, len(ids), batch):
            collection.upsert(
                ids=ids[i : i + batch],
                documents=docs[i : i + batch],
                embeddings=embs[i : i + batch],
                metadatas=metas[i : i + batch],
            )

    report = {
        "timestamp_utc": indexed_at,
        "input_root": str(input_root),
        "dry_run": args.dry_run,
        "files_discovered": len(files),
        "accepted_files": len(accepted),
        "skipped_files": len(skipped),
        "documents_prepared": len(records),
        "accepted": accepted,
        "skipped": skipped,
    }
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out = report_dir / f"governance_ingest_report_{stamp}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report: {out}")
    print(
        f"files={len(files)} accepted={len(accepted)} skipped={len(skipped)} docs={len(records)}"
    )


if __name__ == "__main__":
    main()
