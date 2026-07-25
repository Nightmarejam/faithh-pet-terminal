#!/usr/bin/env python3
"""
FAITHH Collection Router
=========================
Routes chunks to the correct ChromaDB collection based on metadata.
Creates collections automatically if they don't exist (dynamic provisioning).
Reads rules from faithh_collection_rules.yaml — no code changes needed
to add new collection types.

Usage:
    # As a library (called by indexing scripts):
    from scripts.collection_router import CollectionRouter
    router = CollectionRouter()
    router.add(text="...", metadata={"source_type": "conversation", ...})

    # As a CLI diagnostic:
    python scripts/collection_router.py --status
    python scripts/collection_router.py --audit-quarantine
    python scripts/collection_router.py --ttl-sweep --dry-run
    python scripts/collection_router.py --ttl-sweep  # actually deletes
"""

import json
import re
import uuid
import argparse
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

BASE_DIR  = Path(__file__).parent.parent
RULES_FILE = BASE_DIR / "faithh_collection_rules.yaml"
CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000


# ── Rules Loader ─────────────────────────────────────────────────────────────

class CollectionRules:
    """Loads and indexes faithh_collection_rules.yaml."""

    def __init__(self, rules_file: Path = RULES_FILE):
        if not rules_file.exists():
            raise FileNotFoundError(f"Rules file not found: {rules_file}")
        with open(rules_file) as f:
            self._raw = yaml.safe_load(f)

        self.routing    = self._raw.get("routing", {})
        self.collections = self._raw.get("collections", {})
        self.aliases    = self._raw.get("aliases", {})
        self.ttl_config = self._raw.get("ttl_sweep", {})

        # Build reverse index: source_type → collection_name
        self._type_to_collection = {}
        for coll_name, coll_cfg in self.collections.items():
            for source_type in coll_cfg.get("source_types", []):
                # If a type appears in multiple collections, highest priority wins
                existing = self._type_to_collection.get(source_type)
                if existing is None:
                    self._type_to_collection[source_type] = coll_name
                else:
                    existing_priority = self.collections[existing].get("priority", 0)
                    new_priority = coll_cfg.get("priority", 0)
                    if new_priority > existing_priority:
                        self._type_to_collection[source_type] = coll_name

    def resolve_alias(self, source_type: str) -> str:
        """Resolve raw source identifiers to canonical types."""
        return self.aliases.get(source_type, source_type)

    def route(self, source_type: str) -> tuple[str, dict]:
        """
        Returns (collection_name, collection_config) for a source_type.
        Falls back to quarantine for unknown types.
        """
        canonical = self.resolve_alias(source_type)
        coll_name = self._type_to_collection.get(canonical)

        if coll_name is None:
            behavior = self.routing.get("unknown_type_behavior", "quarantine")
            if behavior == "quarantine":
                coll_name = self.routing.get("quarantine_collection", "faithh_unclassified")
            elif behavior == "default":
                coll_name = self.routing.get("default_collection", "faithh_conversations")
            else:  # "reject"
                return None, None

        return coll_name, self.collections.get(coll_name, {})

    def should_reject(self, quality_score: float, coll_config: dict) -> bool:
        """Returns True if chunk should be rejected entirely (below min quality)."""
        global_min = self.routing.get("global_min_quality", 0.05)
        coll_min   = coll_config.get("min_quality_score", 0.0)
        threshold  = max(global_min, coll_min)
        return quality_score < threshold

    def get_ttl_date(self, coll_config: dict) -> Optional[str]:
        """Returns ISO expiry date string, or None if never expires."""
        ttl = coll_config.get("ttl_days", 90)
        if ttl >= 9999:
            return None
        expiry = datetime.now(timezone.utc) + timedelta(days=ttl)
        return expiry.strftime('%Y-%m-%d')


# ── Collection Router ─────────────────────────────────────────────────────────

class CollectionRouter:
    """
    Main interface for routing chunks to ChromaDB collections.
    Creates collections dynamically using get_or_create_collection().
    """

    def __init__(self, rules_file: Path = RULES_FILE,
                 host: str = CHROMA_HOST, port: int = CHROMA_PORT):
        self.rules = CollectionRules(rules_file)
        self._client = None
        self._collections = {}  # cache: name → collection object
        self._host = host
        self._port = port

    @property
    def client(self):
        """Lazy ChromaDB connection."""
        if self._client is None:
            import chromadb
            self._client = chromadb.HttpClient(host=self._host, port=self._port)
        return self._client

    def get_or_create(self, collection_name: str, coll_config: dict):
        """
        Returns ChromaDB collection, creating it if needed.
        This is the dynamic provisioning core.
        """
        if collection_name in self._collections:
            return self._collections[collection_name]

        description = coll_config.get("description", collection_name)
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": description,
                "created_by":  "collection_router",
                "created_at":  datetime.now(timezone.utc).isoformat(),
                "rules_version": self.rules._raw.get("version", "unknown"),
            }
        )
        self._collections[collection_name] = collection
        return collection

    def add(self,
            text: str,
            metadata: dict,
            doc_id: Optional[str] = None,
            quality_score: Optional[float] = None) -> dict:
        """
        Route and insert a single chunk.

        Args:
            text:          The chunk text
            metadata:      Must include 'source_type'. Other fields are enriched.
            doc_id:        Optional ID (auto-generated if not provided)
            quality_score: Pre-computed quality score (computed here if not provided)

        Returns:
            dict with routing decision info
        """
        source_type = metadata.get("source_type", "unknown")

        # Route to collection
        coll_name, coll_config = self.rules.route(source_type)
        if coll_name is None:
            return {"status": "rejected", "reason": "unknown_type_behavior=reject",
                    "source_type": source_type}

        # Quality check
        if quality_score is None:
            quality_score = self._quick_quality(text)

        if self.rules.should_reject(quality_score, coll_config):
            return {"status": "rejected", "reason": "below_min_quality",
                    "quality_score": quality_score,
                    "threshold": max(
                        self.rules.routing.get("global_min_quality", 0.05),
                        coll_config.get("min_quality_score", 0.0)
                    )}

        # Enrich metadata
        ttl_date = self.rules.get_ttl_date(coll_config)
        defaults = coll_config.get("metadata_defaults", {})
        enriched_meta = {
            **defaults,
            **metadata,
            "source_type":       source_type,
            "collection_name":   coll_name,
            "quality_score":     quality_score,
            "indexed_at":        datetime.now(timezone.utc).isoformat(),
            "router_version":    "1.0",
        }
        if ttl_date:
            enriched_meta["expires_at"] = ttl_date

        # Insert
        collection = self.get_or_create(coll_name, coll_config)
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        collection.add(
            documents=[text],
            metadatas=[enriched_meta],
            ids=[doc_id]
        )

        return {
            "status":          "indexed",
            "collection":      coll_name,
            "doc_id":          doc_id,
            "quality_score":   quality_score,
            "expires_at":      ttl_date,
            "source_type":     source_type,
        }

    def add_batch(self, chunks: list[dict]) -> dict:
        """
        Route and insert multiple chunks.

        Args:
            chunks: list of {"text": str, "metadata": dict, "id": optional str}

        Returns:
            Summary stats dict
        """
        stats = {"indexed": 0, "rejected": 0, "by_collection": {}, "errors": []}

        for chunk in chunks:
            try:
                result = self.add(
                    text=chunk["text"],
                    metadata=chunk.get("metadata", {}),
                    doc_id=chunk.get("id"),
                    quality_score=chunk.get("quality_score"),
                )
                if result["status"] == "indexed":
                    stats["indexed"] += 1
                    coll = result["collection"]
                    stats["by_collection"][coll] = stats["by_collection"].get(coll, 0) + 1
                else:
                    stats["rejected"] += 1
            except Exception as e:
                stats["errors"].append(str(e))

        return stats

    def _quick_quality(self, text: str) -> float:
        """Fast heuristic quality score. Will be replaced by ML classifier."""
        score = 0.5
        length = len(text.strip())
        if length < 50:   score -= 0.4
        elif length < 150: score -= 0.1
        elif length > 300: score += 0.1
        alpha = sum(c.isalpha() for c in text) / max(length, 1)
        if alpha < 0.4: score -= 0.3
        elif alpha > 0.65: score += 0.1
        ts = len(re.findall(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}', text))
        score -= min(ts, 3) * 0.15
        return round(max(0.0, min(1.0, score)), 3)


# ── TTL Sweep ────────────────────────────────────────────────────────────────

def run_ttl_sweep(router: CollectionRouter, dry_run: bool = True) -> dict:
    """
    Delete chunks past their expiry date from all collections.
    Protected collections (faithh_decisions) are never swept.
    
    Note: expires_at is stored as ISO date string (YYYY-MM-DD).
    ChromaDB $lte doesn't work with strings, so we fetch chunks with
    expires_at metadata and filter in Python.
    """
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    protected = router.rules.ttl_config.get("protected_collections", [])
    batch_size = router.rules.ttl_config.get("batch_size", 500)

    stats = {"collections_checked": 0, "deleted": 0, "would_delete": 0, "errors": []}

    try:
        all_collections = router.client.list_collections()
    except Exception as e:
        stats["errors"].append(f"Could not list collections: {e}")
        return stats

    for coll_obj in all_collections:
        name = coll_obj.name if hasattr(coll_obj, 'name') else str(coll_obj)
        if name in protected:
            print(f"  [PROTECTED] {name} — skipping")
            continue

        stats["collections_checked"] += 1

        try:
            collection = router.client.get_collection(name)
            
            # Fetch chunks that have expires_at metadata (in batches)
            # Then filter in Python since ChromaDB $lte doesn't work with date strings
            offset = 0
            expired_ids = []
            
            while True:
                results = collection.get(
                    where={"expires_at": {"$ne": ""}},  # has expires_at
                    include=["metadatas"],
                    limit=batch_size,
                    offset=offset
                )
                
                ids = results.get("ids", [])
                metas = results.get("metadatas", [])
                
                if not ids:
                    break
                
                # Filter: expires_at <= today (string comparison works for ISO dates)
                for doc_id, meta in zip(ids, metas):
                    exp = meta.get("expires_at", "") if meta else ""
                    if exp and exp <= today:
                        expired_ids.append(doc_id)
                
                offset += len(ids)
                
                # Safety limit
                if offset > 50000:
                    break

            count = len(expired_ids)

            if dry_run:
                stats["would_delete"] += count
                if count > 0:
                    print(f"  [DRY RUN] {name}: would delete {count} expired chunks")
            else:
                if count > 0:
                    # Delete in batches
                    for i in range(0, count, batch_size):
                        batch_ids = expired_ids[i:i+batch_size]
                        collection.delete(ids=batch_ids)
                    stats["deleted"] += count
                    print(f"  [SWEPT] {name}: deleted {count} expired chunks")

        except Exception as e:
            stats["errors"].append(f"{name}: {e}")

    return stats


# ── CLI ───────────────────────────────────────────────────────────────────────

def cmd_status(router: CollectionRouter):
    """Show current collection status."""
    print(f"\n  FAITHH Collection Status")
    print(f"  Rules: {RULES_FILE}")
    print(f"  {'='*50}")

    try:
        all_collections = router.client.list_collections()
        existing_names = set()

        for coll_obj in all_collections:
            name = coll_obj.name if hasattr(coll_obj, 'name') else str(coll_obj)
            existing_names.add(name)
            try:
                coll = router.client.get_collection(name)
                count = coll.count()
                cfg = router.rules.collections.get(name, {})
                ttl = cfg.get("ttl_days", "?")
                desc = cfg.get("description", "unknown")
                known = "✓" if name in router.rules.collections else "?"
                print(f"  {known} {name:<35} {count:>7,} chunks  TTL:{ttl}d")
                print(f"    {desc}")
            except Exception as e:
                print(f"  ? {name:<35} ERROR: {e}")

        # Show collections defined in rules but not yet created
        print(f"\n  Defined in rules but not yet created:")
        for name, cfg in router.rules.collections.items():
            if name not in existing_names:
                print(f"  ○ {name} (will be created on first use)")

    except Exception as e:
        print(f"  ERROR: {e}")
    print()


def cmd_audit_quarantine(router: CollectionRouter):
    """Show what's in the quarantine collection."""
    q_name = router.rules.routing.get("quarantine_collection", "faithh_unclassified")
    print(f"\n  Quarantine collection: {q_name}")
    try:
        coll = router.client.get_collection(q_name)
        count = coll.count()
        print(f"  {count} chunks in quarantine")
        if count > 0:
            sample = coll.get(limit=10, include=["documents", "metadatas"])
            for doc, meta in zip(sample["documents"], sample["metadatas"]):
                src = meta.get("source_type", "unknown") if meta else "unknown"
                print(f"  [{src}] {doc[:100].replace(chr(10), ' ')}")
    except Exception as e:
        print(f"  Quarantine collection doesn't exist yet or error: {e}")
    print()


def main():
    parser = argparse.ArgumentParser(description="FAITHH Collection Router")
    parser.add_argument("--status",          action="store_true", help="Show collection status")
    parser.add_argument("--audit-quarantine", action="store_true", help="Show quarantine contents")
    parser.add_argument("--ttl-sweep",       action="store_true", help="Run TTL sweep")
    parser.add_argument("--dry-run",         action="store_true", help="Dry run (with --ttl-sweep)")
    args = parser.parse_args()

    router = CollectionRouter()

    if args.status:
        cmd_status(router)
    elif args.audit_quarantine:
        cmd_audit_quarantine(router)
    elif args.ttl_sweep:
        dry = args.dry_run
        mode = "DRY RUN" if dry else "LIVE"
        print(f"\n  TTL Sweep [{mode}]")
        stats = run_ttl_sweep(router, dry_run=dry)
        if dry:
            print(f"  Would delete: {stats['would_delete']} chunks")
        else:
            print(f"  Deleted: {stats['deleted']} chunks")
        if stats["errors"]:
            print(f"  Errors: {stats['errors']}")
        print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
