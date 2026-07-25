#!/usr/bin/env python3
"""
Index governance prose documents from staging into faithh_knowledge_base.

Source: /mnt/x/staging/ (X: drive — mount with: sudo mount -t drvfs X: /mnt/x)
Target: Gen8 ChromaDB faithh_knowledge_base at servicebox.taileb8c60.ts.net:8000

Documents:
- United Nations Charter
- Universal Declaration of Human Rights

Note: Bulk governance CSV/MD from repo lives under docs/data/governance_sources;
use scripts/index_governance_corpus.py for that pipeline.

Run: python3 scripts/index_governance_staging_prose.py
"""
import sys
from datetime import datetime

import chromadb

CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
COLLECTION = "faithh_knowledge_base"

GOVERNANCE_DOCS = [
    {
        "path": "/mnt/x/staging/United Nations Charter.md",
        "source": "un_charter",
        "type": "governance_prose",
        "title": "United Nations Charter",
    },
    {
        "path": "/mnt/x/staging/Universal Declaration of Human Rights.md",
        "source": "udhr",
        "type": "governance_prose",
        "title": "Universal Declaration of Human Rights",
    },
]

CHUNK_SIZE = 500
OVERLAP = 50


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if len(chunk) > 50:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def main() -> None:
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)

    count_before = col.count()
    print(f"Collection: {COLLECTION}")
    print(f"Documents before: {count_before:,}")

    all_docs: list[str] = []
    all_meta: list[dict] = []
    all_ids: list[str] = []

    for doc_info in GOVERNANCE_DOCS:
        try:
            with open(doc_info["path"], "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"ERROR: {doc_info['path']} not found. Is X: mounted?")
            sys.exit(1)

        chunks = chunk_text(text)
        print(f"  {doc_info['title']}: {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            all_docs.append(chunk)
            all_meta.append(
                {
                    "source": doc_info["source"],
                    "type": doc_info["type"],
                    "title": doc_info["title"],
                    "chunk": i,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            all_ids.append(f"{doc_info['source']}_chunk_{i:04d}")

    batch_size = 100
    for i in range(0, len(all_docs), batch_size):
        col.add(
            documents=all_docs[i : i + batch_size],
            metadatas=all_meta[i : i + batch_size],
            ids=all_ids[i : i + batch_size],
        )

    count_after = col.count()
    print(f"\nDocuments after: {count_after:,}")
    print(f"Added: {count_after - count_before:,}")


if __name__ == "__main__":
    main()
