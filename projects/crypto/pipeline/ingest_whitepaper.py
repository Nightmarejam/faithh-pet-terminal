#!/usr/bin/env python3
"""G2 whitepaper ingestion: PDF -> chunk -> embed -> ChromaDB."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb
import requests
from sentence_transformers import SentenceTransformer

try:
    from pypdf import PdfReader
except ImportError as exc:  # noqa: F841
    raise SystemExit("pypdf is required: pip install pypdf") from None

LOGGER = logging.getLogger("crypto.ingest_whitepaper")

ROOT = Path(__file__).resolve().parents[1]
WHITEPAPERS_DIR = ROOT / "data" / "whitepapers"

CHUNK_SIZE = 1800
CHUNK_OVERLAP = 200
BATCH_SIZE = 32
DEFAULT_COLLECTION = "faithh_knowledge_base_v2"
DEFAULT_CHROMA_HOST = "192.158.1.10"
DEFAULT_CHROMA_PORT = 8000

# Embedding dimension -> model used by this stack
_DIM_TO_MODEL: dict[int, str] = {
    768: "BAAI/bge-base-en-v1.5",
    384: "sentence-transformers/all-MiniLM-L6-v2",
    1024: "BAAI/bge-large-en-v1.5",
}


@dataclass
class IngestResult:
    source: str
    symbol: str
    collection: str
    pdf_path: str
    total_pages: int
    total_chars: int
    chunks_written: int
    chunks_skipped: int
    embedding_model: str
    elapsed_seconds: float
    ingested_at_utc: str
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "symbol": self.symbol,
            "collection": self.collection,
            "pdf_path": self.pdf_path,
            "total_pages": self.total_pages,
            "total_chars": self.total_chars,
            "chunks_written": self.chunks_written,
            "chunks_skipped": self.chunks_skipped,
            "embedding_model": self.embedding_model,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "ingested_at_utc": self.ingested_at_utc,
            "errors": self.errors,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest a crypto whitepaper (PDF) into ChromaDB."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="URL or local file path to the whitepaper PDF.",
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Coin symbol (e.g. BTC, ETC). Stored as metadata on every chunk.",
    )
    parser.add_argument(
        "--chroma-host",
        default=DEFAULT_CHROMA_HOST,
        help="ChromaDB HTTP host.",
    )
    parser.add_argument(
        "--chroma-port",
        type=int,
        default=DEFAULT_CHROMA_PORT,
        help="ChromaDB HTTP port.",
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help="ChromaDB collection name.",
    )
    parser.add_argument(
        "--embedding-model",
        default="",
        help="sentence-transformers model. If omitted, inferred from collection dimension.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device for embedding model.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(WHITEPAPERS_DIR),
        help="Directory where downloaded PDFs and ingestion logs are saved.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help="Characters per chunk.",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help="Overlap characters between consecutive chunks.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract and chunk but do not write to ChromaDB.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser.parse_args()


def acquire_pdf(source: str, output_dir: Path) -> Path:
    """Download URL to output_dir, or verify local path exists. Returns local path."""
    output_dir.mkdir(parents=True, exist_ok=True)

    if source.startswith("http://") or source.startswith("https://"):
        filename = source.split("?")[0].rstrip("/").split("/")[-1]
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        dest = output_dir / filename
        if dest.exists():
            LOGGER.info("PDF already downloaded: %s", dest)
            return dest
        LOGGER.info("Downloading %s -> %s", source, dest)
        resp = requests.get(
            source,
            headers={"User-Agent": "Mozilla/5.0 (compatible; crypto-pipeline/1.0)"},
            timeout=60,
            stream=True,
        )
        resp.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=65536):
                fh.write(chunk)
        return dest

    local = Path(source).expanduser().resolve()
    if not local.exists():
        raise FileNotFoundError(f"Local PDF not found: {local}")
    return local


def extract_text(pdf_path: Path) -> tuple[str, int]:
    """Return (full_text, page_count) extracted from a PDF."""
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text.strip())
    return "\n\n".join(pages), len(reader.pages)


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if not text.strip():
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def make_chunk_id(source: str, symbol: str, chunk_index: int) -> str:
    raw = f"{source}|{symbol.upper()}|{chunk_index}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"wp_{symbol.lower()}_{digest}_{chunk_index}"


def connect_chroma(host: str, port: int, collection_name: str) -> tuple[chromadb.HttpClient, Any]:
    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_or_create_collection(collection_name)
    return client, collection


def infer_embedding_model(collection: Any, explicit: str) -> str:
    if explicit:
        return explicit

    # Check collection metadata first
    meta = getattr(collection, "metadata", None) or {}
    if "embedding_model" in meta:
        LOGGER.debug("Inferred model from collection metadata: %s", meta["embedding_model"])
        return meta["embedding_model"]

    # Probe from existing embedding dimension
    try:
        result = collection.get(limit=1, include=["embeddings"])
        embeddings = result.get("embeddings") or []
        if embeddings and embeddings[0]:
            dim = len(embeddings[0])
            model = _DIM_TO_MODEL.get(dim)
            if model:
                LOGGER.info("Inferred model %s from collection dimension %d", model, dim)
                return model
            LOGGER.warning("Unknown embedding dimension %d; falling back to bge-base", dim)
    except Exception as exc:
        LOGGER.debug("Could not probe collection dimension: %s", exc)

    fallback = "BAAI/bge-base-en-v1.5"
    LOGGER.info("Using default embedding model: %s", fallback)
    return fallback


def embed_and_upsert(
    collection: Any,
    embedder: SentenceTransformer,
    chunks: list[str],
    source: str,
    symbol: str,
    pdf_path: str,
    ingested_at: str,
) -> tuple[int, int]:
    """Upsert chunks in batches. Returns (written, skipped)."""
    written = 0
    skipped = 0
    total = len(chunks)

    for batch_start in range(0, total, BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        ids = [make_chunk_id(source, symbol, batch_start + i) for i in range(len(batch))]
        metadatas = [
            {
                "source": source,
                "symbol": symbol.upper(),
                "type": "whitepaper",
                "chunk_index": batch_start + i,
                "total_chunks": total,
                "pdf_path": pdf_path,
                "ingested_at": ingested_at,
            }
            for i in range(len(batch))
        ]

        embeddings = embedder.encode(
            batch,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True,
        ).tolist()

        collection.upsert(
            ids=ids,
            documents=batch,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        written += len(batch)
        LOGGER.debug(
            "Upserted batch %d-%d / %d",
            batch_start,
            batch_start + len(batch) - 1,
            total,
        )

    return written, skipped


def write_log(output_dir: Path, result: IngestResult) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "ingestion_log.jsonl"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(result.to_dict()) + "\n")
    latest = output_dir / "latest_ingestion.json"
    latest.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    LOGGER.info("Ingestion log: %s", log_path)
    LOGGER.info("Latest summary: %s", latest)


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    output_dir = Path(args.output_dir).expanduser().resolve()
    t0 = time.monotonic()
    ingested_at = datetime.now(timezone.utc).isoformat()
    errors: list[str] = []

    # Acquire PDF
    pdf_path = acquire_pdf(args.source, output_dir)
    LOGGER.info("PDF: %s", pdf_path)

    # Extract text
    LOGGER.info("Extracting text from PDF...")
    text, page_count = extract_text(pdf_path)
    LOGGER.info("Extracted %d chars from %d pages", len(text), page_count)

    if not text.strip():
        LOGGER.error("No text extracted from PDF. Possibly a scanned/image PDF.")
        errors.append("no_text_extracted")

    # Chunk
    chunks = chunk_text(text, args.chunk_size, args.chunk_overlap)
    LOGGER.info("Split into %d chunks (size=%d, overlap=%d)", len(chunks), args.chunk_size, args.chunk_overlap)

    if args.dry_run:
        LOGGER.info("Dry-run: skipping ChromaDB upsert.")
        result = IngestResult(
            source=args.source,
            symbol=args.symbol.upper(),
            collection=args.collection,
            pdf_path=str(pdf_path),
            total_pages=page_count,
            total_chars=len(text),
            chunks_written=0,
            chunks_skipped=len(chunks),
            embedding_model="(dry-run)",
            elapsed_seconds=time.monotonic() - t0,
            ingested_at_utc=ingested_at,
            errors=errors,
        )
        write_log(output_dir, result)
        print(f"Dry-run complete: {len(chunks)} chunks from {page_count} pages, not written.")
        return 0

    # Connect to ChromaDB
    LOGGER.info("Connecting to ChromaDB at %s:%d ...", args.chroma_host, args.chroma_port)
    _, collection = connect_chroma(args.chroma_host, args.chroma_port, args.collection)
    LOGGER.info("Collection: %s (count before: %d)", args.collection, collection.count())

    # Resolve embedding model
    model_name = infer_embedding_model(collection, args.embedding_model)
    LOGGER.info("Loading embedding model: %s (device=%s)", model_name, args.device)
    try:
        embedder = SentenceTransformer(model_name, device=args.device)
    except Exception:
        LOGGER.warning("Failed to load on %s, falling back to cpu", args.device)
        embedder = SentenceTransformer(model_name, device="cpu")
    LOGGER.info("Embedding dim: %d", embedder.get_sentence_embedding_dimension())

    # Embed and upsert
    LOGGER.info("Embedding and upserting %d chunks...", len(chunks))
    written, skipped = embed_and_upsert(
        collection=collection,
        embedder=embedder,
        chunks=chunks,
        source=args.source,
        symbol=args.symbol,
        pdf_path=str(pdf_path),
        ingested_at=ingested_at,
    )
    LOGGER.info("Collection count after: %d", collection.count())

    elapsed = time.monotonic() - t0
    result = IngestResult(
        source=args.source,
        symbol=args.symbol.upper(),
        collection=args.collection,
        pdf_path=str(pdf_path),
        total_pages=page_count,
        total_chars=len(text),
        chunks_written=written,
        chunks_skipped=skipped,
        embedding_model=model_name,
        elapsed_seconds=elapsed,
        ingested_at_utc=ingested_at,
        errors=errors,
    )
    write_log(output_dir, result)

    print(
        f"Ingested {written} chunks ({page_count} pages, {len(text):,} chars) "
        f"into '{args.collection}' in {elapsed:.1f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
