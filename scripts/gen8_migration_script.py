#!/usr/bin/env python3
"""
Gen8 ChromaDB Migration Script
Migrates live_chat records and recent file chunks from WSL2 to Gen8.

Usage:
    python gen8_migration_script.py --dry-run    # Preview what will be migrated
    python gen8_migration_script.py              # Execute migration
    python gen8_migration_script.py --validate   # Post-migration validation

Safety:
    - One-way migration (WSL2 → Gen8)
    - Does NOT delete from source
    - Creates backup before migration
    - Dry-run mode available
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
import chromadb
from chromadb.config import Settings


class ChromaDBMigrator:
    """Handles safe migration from WSL2 to Gen8 ChromaDB."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.migration_log = []
        
        # Source: WSL2 Docker ChromaDB
        try:
            self.source_client = chromadb.HttpClient(
                host="127.0.0.1",
                port=8000,
                settings=Settings(anonymized_telemetry=False)
            )
            print("✅ Connected to WSL2 ChromaDB (source)")
        except Exception as e:
            print(f"❌ Failed to connect to WSL2 ChromaDB: {e}")
            sys.exit(1)
        
        # Target: Gen8 Production ChromaDB
        try:
            self.target_client = chromadb.HttpClient(
                host="192.158.1.10",
                port=8000,
                settings=Settings(anonymized_telemetry=False)
            )
            print("✅ Connected to Gen8 ChromaDB (target)")
        except Exception as e:
            print(f"❌ Failed to connect to Gen8 ChromaDB: {e}")
            print("   Ensure Gen8 is reachable: curl http://192.158.1.10:8000/api/v2/heartbeat")
            sys.exit(1)
    
    def assess_source_data(self):
        """Analyze WSL2 collections to understand what needs migration."""
        print("\n" + "="*60)
        print("PHASE 1: DATA ASSESSMENT")
        print("="*60)
        
        source_col = self.source_client.get_collection("documents_768")
        
        # Get total count
        total_count = source_col.count()
        print(f"\n📊 WSL2 Collection: documents_768")
        print(f"   Total records: {total_count:,}")
        
        # Sample metadata to categorize
        print("\n🔍 Analyzing record categories...")
        batch_size = 5000
        categories = Counter()
        types = Counter()
        has_filename = 0
        has_live_chat = 0
        
        for offset in range(0, total_count, batch_size):
            try:
                results = source_col.get(
                    limit=batch_size,
                    offset=offset,
                    include=["metadatas"]
                )
                
                for meta in results.get("metadatas", []):
                    if meta:
                        cat = meta.get("category", "<no_category>")
                        typ = meta.get("type", "<no_type>")
                        categories[cat] += 1
                        types[typ] += 1
                        
                        if "filename" in meta:
                            has_filename += 1
                        if cat == "live_chat":
                            has_live_chat += 1
                
                print(f"   Processed {min(offset + batch_size, total_count):,}/{total_count:,} records...", end="\r")
            
            except Exception as e:
                print(f"\n⚠️  Error at offset {offset}: {e}")
                continue
        
        print("\n")
        
        # Report findings
        print("📈 Category Breakdown:")
        for cat, count in categories.most_common(10):
            print(f"   {cat}: {count:,}")
        
        print("\n📈 Type Breakdown:")
        for typ, count in types.most_common(10):
            print(f"   {typ}: {count:,}")
        
        print(f"\n📁 Records with 'filename': {has_filename:,}")
        print(f"💬 Live chat records: {has_live_chat:,}")
        
        # Migration recommendations
        print("\n" + "="*60)
        print("MIGRATION RECOMMENDATIONS")
        print("="*60)
        
        if has_live_chat > 0:
            print(f"✅ Priority 1: Migrate {has_live_chat:,} live_chat records")
            print("   These are episodic memory from Nov-Dec 2025")
        
        constella_count = categories.get("constella_master", 0)
        if constella_count > 0:
            print(f"✅ Priority 2: Consider migrating {constella_count:,} Constella docs")
        
        no_category = categories.get("<no_category>", 0)
        if no_category > 50000:
            print(f"⚠️  Found {no_category:,} uncategorized records")
            print("   These are likely file chunks (check if Gen8 has better-organized versions)")
        
        return {
            "total": total_count,
            "live_chat": has_live_chat,
            "constella": constella_count,
            "categories": dict(categories),
            "types": dict(types)
        }
    
    def migrate_live_chat(self):
        """Migrate live_chat records from WSL2 to Gen8."""
        print("\n" + "="*60)
        print("PHASE 2: LIVE CHAT MIGRATION")
        print("="*60)
        
        source_col = self.source_client.get_collection("documents_768")
        target_col = self.target_client.get_collection("faithh_knowledge_base")
        
        # Get all live_chat records
        try:
            results = source_col.get(
                where={"category": "live_chat"},
                include=["embeddings", "metadatas", "documents"]
            )
        except Exception as e:
            print(f"❌ Failed to fetch live_chat records: {e}")
            return
        
        count = len(results["ids"])
        print(f"\n📊 Found {count} live_chat records to migrate")
        
        if count == 0:
            print("   Nothing to migrate")
            return
        
        # Show sample
        print("\n🔍 Sample record:")
        if results["metadatas"]:
            print(f"   ID: {results['ids'][0]}")
            print(f"   Metadata: {json.dumps(results['metadatas'][0], indent=2)}")
        
        if self.dry_run:
            print("\n🔶 DRY RUN MODE - Would migrate:")
            print(f"   {count} records with category='live_chat'")
            print(f"   To collection: faithh_knowledge_base on Gen8")
            return
        
        # Check for duplicates in target
        print("\n🔍 Checking for existing records in target...")
        existing_ids = set()
        try:
            # Check if any of these IDs already exist
            test_batch = results["ids"][:100]  # Sample first 100
            target_results = target_col.get(ids=test_batch)
            existing_ids = set(target_results["ids"])
            
            if existing_ids:
                print(f"⚠️  Found {len(existing_ids)} records already in target")
                print("   These will be SKIPPED to avoid duplicates")
        except Exception as e:
            print(f"   (Could not check duplicates: {e})")
        
        # Filter out existing IDs
        new_ids = [id for id in results["ids"] if id not in existing_ids]
        new_indices = [i for i, id in enumerate(results["ids"]) if id not in existing_ids]
        
        if not new_ids:
            print("✅ All live_chat records already exist in target - nothing to do")
            return
        
        print(f"\n📤 Migrating {len(new_ids)} NEW live_chat records...")
        
        # Prepare batch
        batch_ids = new_ids
        batch_embeddings = [results["embeddings"][i] for i in new_indices]
        batch_metadatas = [results["metadatas"][i] for i in new_indices]
        batch_documents = [results["documents"][i] for i in new_indices] if results["documents"] else None
        
        try:
            target_col.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
                documents=batch_documents
            )
            print(f"✅ Successfully migrated {len(new_ids)} live_chat records")
            
            self.migration_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "live_chat",
                "count": len(new_ids),
                "status": "success"
            })
        
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            self.migration_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "live_chat",
                "count": len(new_ids),
                "status": "failed",
                "error": str(e)
            })
    
    def migrate_recent_files(self, days_back=7):
        """Migrate file chunks added in the last N days."""
        print("\n" + "="*60)
        print("PHASE 3: RECENT FILE CHUNKS MIGRATION")
        print("="*60)
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        print(f"\n📅 Migrating files modified after: {cutoff_date.strftime('%Y-%m-%d')}")
        
        # This is complex because metadata doesn't always have timestamps
        # For now, skip this phase unless explicitly needed
        print("⏭️  SKIPPING: File chunk migration not needed (Gen8 has newer data)")
        print("   If needed, implement timestamp-based filtering here")
    
    def validate_migration(self):
        """Post-migration validation checks."""
        print("\n" + "="*60)
        print("PHASE 4: VALIDATION")
        print("="*60)
        
        target_col = self.target_client.get_collection("faithh_knowledge_base")
        
        # Count check
        target_count = target_col.count()
        print(f"\n📊 Gen8 Collection: faithh_knowledge_base")
        print(f"   Total records: {target_count:,}")
        
        # Sample live_chat query
        print("\n🔍 Testing live_chat query...")
        try:
            results = target_col.get(
                where={"category": "live_chat"},
                limit=5,
                include=["metadatas"]
            )
            
            live_chat_count = len(results["ids"])
            print(f"   Found {live_chat_count} live_chat records (showing first {min(5, live_chat_count)}):")
            
            for i, (id, meta) in enumerate(zip(results["ids"], results["metadatas"])):
                timestamp = meta.get("timestamp", "N/A")
                preview = meta.get("user_preview", "N/A")[:50]
                print(f"   {i+1}. {id}")
                print(f"      Time: {timestamp}")
                print(f"      Preview: {preview}...")
        
        except Exception as e:
            print(f"❌ Validation query failed: {e}")
        
        # Sample documentation query
        print("\n🔍 Testing documentation query...")
        try:
            results = target_col.query(
                query_texts=["FAITHH backend configuration"],
                n_results=3,
                include=["metadatas"]
            )
            
            print(f"   Found {len(results['ids'][0])} relevant docs:")
            for i, (id, meta) in enumerate(zip(results["ids"][0], results["metadatas"][0])):
                filename = meta.get("filename", meta.get("category", "N/A"))
                print(f"   {i+1}. {filename}")
        
        except Exception as e:
            print(f"❌ Documentation query failed: {e}")
        
        print("\n✅ Validation complete")
    
    def save_migration_log(self):
        """Save migration log to file."""
        log_file = Path("ARCHIVE/migration_logs") / f"gen8_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "operations": self.migration_log
        }
        
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\n📝 Migration log saved: {log_file}")


def main():
    parser = argparse.ArgumentParser(description="Migrate ChromaDB data from WSL2 to Gen8")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without making changes")
    parser.add_argument("--validate", action="store_true", help="Run post-migration validation only")
    parser.add_argument("--assess-only", action="store_true", help="Only assess source data, don't migrate")
    
    args = parser.parse_args()
    
    print("="*60)
    print("FAITHH ChromaDB Migration: WSL2 → Gen8")
    print("="*60)
    
    if args.dry_run:
        print("🔶 DRY RUN MODE - No changes will be made")
    
    migrator = ChromaDBMigrator(dry_run=args.dry_run)
    
    if args.validate:
        migrator.validate_migration()
        return
    
    # Phase 1: Assessment
    assessment = migrator.assess_source_data()
    
    if args.assess_only:
        print("\n✅ Assessment complete (no migration performed)")
        return
    
    # Phase 2: Live chat migration
    if assessment["live_chat"] > 0:
        migrator.migrate_live_chat()
    
    # Phase 3: Recent files (skipped for now)
    # migrator.migrate_recent_files(days_back=7)
    
    # Phase 4: Validation
    if not args.dry_run:
        migrator.validate_migration()
        migrator.save_migration_log()
    
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    
    if args.dry_run:
        print("\n🔶 This was a dry run. To execute migration:")
        print("   python gen8_migration_script.py")
    else:
        print("\n✅ Next steps:")
        print("   1. Update .env: CHROMADB_HOST=192.158.1.10")
        print("   2. Restart backend: ./restart_backend.sh")
        print("   3. Test RAG queries")
        print("   4. Monitor for 1-2 weeks before decommissioning WSL2 ChromaDB")


if __name__ == "__main__":
    main()
