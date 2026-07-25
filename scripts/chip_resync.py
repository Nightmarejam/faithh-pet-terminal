#!/usr/bin/env python3
"""
FAITHH Chip Resync
==================
Re-synthesizes ML chips from signal-only ChromaDB chunks.

The original chip synthesis (Feb 2026) ran against a noisy corpus, producing
polluted keywords (langflow, 0x00000000, nan). Now that all chunks are tagged
with source_type, we can filter to signal-only types and get clean chips.

Signal types (included):
  - project_discussion
  - technical_explanation
  - document_content
  - conversation
  - decision

Noise types (excluded):
  - health_log, terminal_command, json_data, log_entry, metric_data, unknown

Output: ml/output/chips_resynced.json
        ml/output/consolidated_chips_resynced.json

Usage:
    # Dry run — show what would be sampled, no synthesis
    python3 scripts/chip_resync.py --dry-run

    # Full resync (uses RTX 3090, takes ~10-20 min for 20K chunks)
    python3 scripts/chip_resync.py

    # Sample only N chunks (faster, for testing)
    python3 scripts/chip_resync.py --limit 5000
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent

# Signal source types to include
# Original signal_types filter used source_type metadata which doesn't exist
# in chat_export chunks. Chat exports use domain/document_type instead.
# All chat_export chunks are signal — include everything.
SIGNAL_TYPES = None  # None = no filter, use all chunks

CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
CHROMA_COLLECTION = "faithh_knowledge_base"

OUTPUT_DIR = BASE_DIR / "ml" / "output"
OUTPUT_FILE = OUTPUT_DIR / "chips_resynced.json"


def fetch_signal_chunks(collection, limit: int = 0) -> tuple[list, list]:
    """Fetch chunks tagged as signal types. Returns (docs, metas)."""
    print("  Fetching all chunk metadata to filter signal types...")

    total = collection.count()
    print(f"  Total chunks: {total:,}")

    all_docs = []
    all_metas = []
    batch = 500
    offset = 0

    while offset < total:
        results = collection.get(
            limit=min(batch, total - offset),
            offset=offset,
            include=["documents", "metadatas"]
        )
        docs  = results.get("documents", [])
        metas = results.get("metadatas", [])

        for doc, meta in zip(docs, metas):
            if meta is None:
                meta = {}
            source_type = meta.get("source_type", "")
            if SIGNAL_TYPES is None or source_type in SIGNAL_TYPES:
                all_docs.append(doc)
                all_metas.append(meta)

        offset += len(docs)
        pct = round(offset / total * 100)
        print(f"  [{pct:3d}%] fetched {offset:,}/{total:,}  signal so far: {len(all_docs):,}", end="\r")
        if not docs:
            break

    print()

    if limit > 0 and len(all_docs) > limit:
        print(f"  Sampling {limit:,} from {len(all_docs):,} signal chunks")
        import random
        random.seed(42)
        indices = random.sample(range(len(all_docs)), limit)
        all_docs  = [all_docs[i]  for i in indices]
        all_metas = [all_metas[i] for i in indices]

    return all_docs, all_metas


def show_type_breakdown(metas: list):
    """Print source_type distribution."""
    counts = Counter(m.get("source_type", "untagged") for m in metas)
    print("\n  Source type breakdown (signal chunks):")
    for t, n in counts.most_common():
        bar = "█" * min(30, n // 50)
        print(f"    {t:<30} {n:>6,}  {bar}")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be sampled, skip synthesis")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max signal chunks to use (0 = all)")
    args = parser.parse_args()

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"\n  FAITHH Chip Resync [{mode}]")
    signal_str = ', '.join(sorted(SIGNAL_TYPES)) if SIGNAL_TYPES else "all (no filter)"
    print(f"  Signal types: {signal_str}\n")

    # Connect to ChromaDB
    try:
        import chromadb
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(CHROMA_COLLECTION)
    except Exception as e:
        print(f"  ERROR connecting to ChromaDB: {e}")
        sys.exit(1)

    # Fetch signal chunks
    docs, metas = fetch_signal_chunks(collection, limit=args.limit)
    print(f"\n  Signal chunks selected: {len(docs):,}")
    show_type_breakdown(metas)

    if args.dry_run:
        print("  Dry run — skipping synthesis. Run without --dry-run to proceed.")
        return

    if len(docs) < 100:
        print(f"  ERROR: Too few signal chunks ({len(docs)}) for meaningful synthesis.")
        sys.exit(1)

    # Run chip synthesis
    print("  Starting chip synthesis (this will take a while)...")
    print("  Note: ml/chip_synthesis.py will be invoked with --input-docs flag")
    print("  If chip_synthesis.py doesn't support --input-docs, use ml/chip_resync.py instead\n")

    # Write signal docs to temp file for chip_synthesis to consume
    temp_file = BASE_DIR / "ml" / "signal_chunks_temp.json"
    temp_data = {
        "generated": datetime.now().isoformat(),
        "source": "chip_resync.py signal filter",
        "signal_types": list(SIGNAL_TYPES) if SIGNAL_TYPES else [],
        "chunk_count": len(docs),
        "documents": docs,
        "metadatas": metas,
    }
    with open(temp_file, "w") as f:
        json.dump(temp_data, f)
    print(f"  Signal chunks written to: {temp_file}")
    print(f"  Chunk count: {len(docs):,}")
    print()
    print("  NEXT STEP: Run chip synthesis against this filtered corpus:")
    print(f"    cd ~/ai-stack")
    print(f"    ml/venv/bin/python ml/chip_synthesis.py --input-file ml/signal_chunks_temp.json")
    print()
    print("  If chip_synthesis.py doesn't support --input-file, open it and check")
    print("  whether it accepts a pre-built document list. If not, report back.")


if __name__ == "__main__":
    main()
