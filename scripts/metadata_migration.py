#!/usr/bin/env python3
"""
FAITHH Metadata Migration
==========================
Tags existing ChromaDB chunks with source_type and expires_at metadata.
This is a one-time migration that enables the TTL sweep to work.

Run ONCE after audit confirms the classifier is working.
Safe to re-run — uses upsert logic, won't duplicate chunks.

Usage:
    python scripts/metadata_migration.py --dry-run    # show what would change
    python scripts/metadata_migration.py --batch 500  # process 500 chunks
    python scripts/metadata_migration.py              # process all (slow)
    python scripts/metadata_migration.py --limit 2000 # process first N chunks
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000
CHROMA_COLLECTION = "faithh_knowledge_base"
BATCH_SIZE = 200

# Import classifier from chroma_audit
sys.path.insert(0, str(BASE_DIR))
from scripts.chroma_audit import detect_type, score_quality, TTL_MAP, COLLECTION_MAP


def get_expiry_date(source_type: str) -> str | None:
    ttl = TTL_MAP.get(source_type, 90)
    if ttl >= 9999:
        return None
    expiry = datetime.now(timezone.utc) + timedelta(days=ttl)
    return expiry.strftime('%Y-%m-%d')


def already_tagged(metadata: dict) -> bool:
    """Check if chunk already has source_type metadata."""
    return bool(metadata.get("source_type"))


def migrate_batch(collection, ids: list, documents: list,
                  metadatas: list, dry_run: bool) -> dict:
    """Tag a batch of chunks with source_type and expires_at."""
    stats = {"tagged": 0, "skipped_already_tagged": 0, "updated": []}

    updated_ids = []
    updated_metadatas = []

    for doc_id, doc, meta in zip(ids, documents, metadatas):
        if meta is None:
            meta = {}

        # Skip if already tagged
        if already_tagged(meta):
            stats["skipped_already_tagged"] += 1
            continue

        # Classify
        source_type = detect_type(doc)
        quality = score_quality(doc, source_type)
        expiry = get_expiry_date(source_type)
        suggested_collection = COLLECTION_MAP.get(source_type, "faithh_unclassified")

        # Build updated metadata
        new_meta = {
            **meta,
            "source_type": source_type,
            "quality_score": quality,
            "suggested_collection": suggested_collection,
            "migrated_at": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        }
        if expiry:
            new_meta["expires_at"] = expiry

        updated_ids.append(doc_id)
        updated_metadatas.append(new_meta)
        stats["tagged"] += 1

    if not dry_run and updated_ids:
        # ChromaDB upsert updates metadata in place
        collection.update(
            ids=updated_ids,
            metadatas=updated_metadatas,
        )

    stats["updated"] = updated_ids[:5]  # preview
    return stats


def main():
    parser = argparse.ArgumentParser(description="FAITHH Metadata Migration")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    parser.add_argument("--batch",   type=int, default=BATCH_SIZE,
                        help=f"Batch size (default: {BATCH_SIZE})")
    parser.add_argument("--limit",   type=int, default=0,
                        help="Process only first N chunks (0 = all)")
    args = parser.parse_args()

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"\n  FAITHH Metadata Migration [{mode}]")
    print(f"  Target: {CHROMA_HOST}:{CHROMA_PORT}/{CHROMA_COLLECTION}\n")

    try:
        import chromadb
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(CHROMA_COLLECTION)
        total = collection.count()
        print(f"  Total chunks: {total:,}")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    limit = args.limit if args.limit > 0 else total
    to_process = min(limit, total)
    print(f"  Processing: {to_process:,} chunks in batches of {args.batch}\n")

    totals = {"tagged": 0, "skipped": 0}
    type_counts = Counter()
    offset = 0

    while offset < to_process:
        batch_limit = min(args.batch, to_process - offset)

        try:
            results = collection.get(
                limit=batch_limit,
                offset=offset,
                include=["documents", "metadatas"]
            )
        except Exception as e:
            print(f"  ERROR at offset {offset}: {e}")
            break

        ids   = results.get("ids", [])
        docs  = results.get("documents", [])
        metas = results.get("metadatas", [])

        if not ids:
            break

        stats = migrate_batch(collection, ids, docs, metas, args.dry_run)
        totals["tagged"]  += stats["tagged"]
        totals["skipped"] += stats["skipped_already_tagged"]

        # Count types for report
        for doc in docs:
            t = detect_type(doc)
            type_counts[t] += 1

        offset += len(ids)
        pct = round(offset / to_process * 100)
        print(f"  [{pct:3d}%] {offset:,}/{to_process:,}  "
              f"tagged: {totals['tagged']:,}  skipped: {totals['skipped']:,}",
              end="\r")

    print(f"\n\n  {'='*50}")
    print(f"  Migration {'(DRY RUN) ' if args.dry_run else ''}complete")
    print(f"  Tagged:  {totals['tagged']:,}")
    print(f"  Skipped: {totals['skipped']:,} (already tagged)")
    print(f"\n  Type breakdown:")
    for t, count in type_counts.most_common(10):
        print(f"    {t:<30} {count:,}")

    if args.dry_run:
        print(f"\n  Run without --dry-run to apply changes.")
    print()


if __name__ == "__main__":
    main()
