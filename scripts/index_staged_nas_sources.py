#!/usr/bin/env python3
"""
Index staged NAS ALife/Constella source docs from local intake folders.
Emits a JSON report under reports/index_runs (or --report-dir).
Removes stale chunk IDs per source file before upserting the current chunk set.
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

from chroma_ingest_guard import check_post_ingest_growth, validate_bulk_metadata

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = REPO_ROOT / "reports/index_runs"
COLLECTION_NAME = "faithh_knowledge_base"
ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}


def normalized_source_path(path: Path) -> str:
    """Canonical key for Chroma metadata and stale-cleanup queries."""
    return str(path.resolve())


def chunk_text(text: str, size: int = 1800, overlap: int = 200) -> list[str]:
    text = text.strip()
    if not text:
        return []
    out = []
    i = 0
    while i < len(text):
        out.append(text[i : i + size])
        if i + size >= len(text):
            break
        i += max(1, size - overlap)
    return out


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".json":
        try:
            return json.dumps(json.loads(path.read_text(encoding="utf-8", errors="ignore")), indent=2)
        except json.JSONDecodeError:
            return path.read_text(encoding="utf-8", errors="ignore")
    return path.read_text(encoding="utf-8", errors="ignore")


def build_file_records(
    path: Path,
    domain: str,
    source_type: str,
    document_type: str,
    indexed_at: str,
) -> list[tuple[str, str, dict[str, Any]]]:
    text = read_text(path)
    chunks = chunk_text(text)
    if not chunks:
        return []
    path_fp = hashlib.sha256(normalized_source_path(path).encode("utf-8")).hexdigest()[:10]
    source_path_key = normalized_source_path(path)
    try:
        rel_source = str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        rel_source = source_path_key
    recs: list[tuple[str, str, dict[str, Any]]] = []
    for i, ch in enumerate(chunks):
        doc_id = f"nas_seed_{domain}_{path.stem}_{path_fp}_{i:03d}"
        recs.append(
            (
                doc_id,
                ch,
                {
                    "domain": domain,
                    "source_type": source_type,
                    "document_type": document_type,
                    "category": "project_docs",
                    "quality_score": 0.9,
                    "source": rel_source,
                    "source_path": source_path_key,
                    "chunk_index": i,
                    "chunk_total": len(chunks),
                    "indexed_at": indexed_at,
                },
            )
        )
    return recs


def delete_stale_for_file(
    col: Any,
    source_path: str,
    domain: str,
    source_type: str,
    new_ids: set[str],
    report: dict[str, Any],
    errors: list[str],
) -> bool:
    """
    Remove collection IDs for this source_path/domain/source_type that are not in new_ids.
    Returns False if cleanup failed (caller should skip upsert for this file).
    """
    try:
        existing = col.get(
            where={
                "$and": [
                    {"source_path": source_path},
                    {"domain": domain},
                    {"source_type": source_type},
                ]
            },
            limit=50_000,
            include=[],
        )
        ex_ids = set(existing.get("ids") or [])
        stale = ex_ids - new_ids
        if stale:
            col.delete(ids=list(stale))
            report["stale_chunk_ids_deleted"] += len(stale)
        return True
    except Exception as exc:  # noqa: BLE001 — surface to report.errors
        errors.append(f"stale_cleanup_failed path={source_path!r} err={exc!r}")
        return False


def scan_root(
    root: Path,
    domain: str,
    source_type: str,
    document_type: str,
    col: Any,
    report: dict[str, Any],
    errors: list[str],
    indexed_at: str,
) -> list[tuple[str, str, dict[str, Any]]]:
    all_recs: list[tuple[str, str, dict[str, Any]]] = []
    if not root.exists():
        report["intake_roots_scanned"].append({"path": str(root), "status": "missing"})
        return all_recs

    report["intake_roots_scanned"].append({"path": str(root.resolve()), "status": "ok"})

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        report["files"]["scanned_total"] += 1
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            report["files"]["skipped"].append({"path": str(path), "reason": "unsupported_extension"})
            continue

        try:
            file_recs = build_file_records(path, domain, source_type, document_type, indexed_at)
        except OSError as exc:
            report["files"]["skipped"].append({"path": str(path), "reason": f"read_error:{exc}"})
            errors.append(f"read {path}: {exc!r}")
            continue

        if not file_recs:
            report["files"]["skipped"].append({"path": str(path), "reason": "empty_after_chunk"})
            continue

        new_ids = {r[0] for r in file_recs}
        sp = normalized_source_path(path)
        if not delete_stale_for_file(col, sp, domain, source_type, new_ids, report, errors):
            report["files"]["skipped"].append({"path": str(path), "reason": "stale_cleanup_failed"})
            continue

        all_recs.extend(file_recs)
        report["files"]["indexed"] += 1

    return all_recs


def main() -> None:
    parser = argparse.ArgumentParser(description="Index staged NAS ALife/Constella docs")
    parser.add_argument("--host", default=os.getenv("CHROMA_HOST", "192.158.1.243"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CHROMA_PORT", "8000")))
    parser.add_argument("--intake-root", default=str(REPO_ROOT / "docs/data"))
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory for staged_nas_index_report_<timestamp>.json",
    )
    parser.add_argument("--collection", default=COLLECTION_NAME)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override BULK_INGEST_GUARD when collection grows >3× in one run",
    )
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    started = datetime.now(UTC)
    indexed_at = started.isoformat()
    intake = Path(args.intake_root)
    alife_root = intake / "alife_sources" / "nas_import"
    constella_root = intake / "constella_sources" / "nas_import"

    report: dict[str, Any] = {
        "timestamp_utc": indexed_at,
        "intake_root": str(intake),
        "intake_roots_scanned": [],
        "collection": args.collection,
        "chroma_host": args.host,
        "chroma_port": args.port,
        "files": {
            "scanned_total": 0,
            "indexed": 0,
            "skipped": [],
        },
        "chunks_produced": 0,
        "upserts_performed": 0,
        "stale_chunk_ids_deleted": 0,
        "per_domain_record_counts": {},
        "errors": [],
    }
    errors: list[str] = []

    client = chromadb.HttpClient(host=args.host, port=args.port)
    col = client.get_collection(args.collection)
    pre_count = col.count()

    source_type = "nas_seeded_document"
    document_type = "seed_source"

    records: list[tuple[str, str, dict[str, Any]]] = []
    records.extend(
        scan_root(alife_root, "alife", source_type, document_type, col, report, errors, indexed_at)
    )
    records.extend(
        scan_root(
            constella_root,
            "constella_constitutional",
            source_type,
            document_type,
            col,
            report,
            errors,
            indexed_at,
        )
    )

    report["errors"].extend(errors)
    report["chunks_produced"] = len(records)

    for _, _, meta in records:
        d = meta.get("domain", "unknown")
        report["per_domain_record_counts"][d] = report["per_domain_record_counts"].get(d, 0) + 1

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"staged_nas_index_report_{stamp}.json"

    if not records:
        report["finished_utc"] = datetime.now(UTC).isoformat()
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("No staged ALife/Constella records found.")
        print(f"Report: {report_path}")
        return

    ids = [r[0] for r in records]
    docs = [r[1] for r in records]
    metas = [r[2] for r in records]

    try:
        embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        embs = embedder.encode(docs, show_progress_bar=False).tolist()
    except Exception as exc:  # noqa: BLE001
        report["errors"].append(f"embed_failed:{exc!r}")
        report["finished_utc"] = datetime.now(UTC).isoformat()
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Embedding failed: {exc}")
        print(f"Report: {report_path}")
        return

    for m in metas:
        bad = validate_bulk_metadata(m)
        if bad:
            report["errors"].append(f"metadata_missing_keys:{bad!r}")
            report["finished_utc"] = datetime.now(UTC).isoformat()
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"Abort: metadata missing required keys {bad} (domain, category, source). Report: {report_path}")
            return

    batch = 64
    try:
        for i in range(0, len(ids), batch):
            col.upsert(
                ids=ids[i : i + batch],
                documents=docs[i : i + batch],
                embeddings=embs[i : i + batch],
                metadatas=metas[i : i + batch],
            )
            report["upserts_performed"] += min(batch, len(ids) - i)
    except Exception as exc:  # noqa: BLE001
        report["errors"].append(f"upsert_failed:{exc!r}")

    post_count = col.count()
    try:
        check_post_ingest_growth(
            pre_count,
            post_count,
            multiplier=3.0,
            force=args.force,
            label=args.collection,
        )
    except SystemExit as exc:
        report["errors"].append(f"bulk_guard:{exc!s}")
        report["finished_utc"] = datetime.now(UTC).isoformat()
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(str(exc))
        print(f"Report: {report_path}")
        raise

    report["finished_utc"] = datetime.now(UTC).isoformat()
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Indexed staged NAS seed records: {len(ids)}")
    print(f"Report: {report_path}")
    if report["stale_chunk_ids_deleted"]:
        print(f"Stale chunk IDs removed: {report['stale_chunk_ids_deleted']}")
    if report["errors"]:
        print(f"Errors recorded: {len(report['errors'])}")


if __name__ == "__main__":
    main()
