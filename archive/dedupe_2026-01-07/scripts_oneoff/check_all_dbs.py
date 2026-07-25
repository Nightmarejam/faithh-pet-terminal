#!/usr/bin/env python3
"""Check all ChromaDB databases for their contents"""
import chromadb
import tempfile
import shutil
import os

databases = [
    ("faithh_rag (current)", "./faithh_rag"),
    ("chroma_db (current)", "./chroma_db"),
]

backup_files = [
    ("backup 91K #1", "./backups/chroma_20251112_161400_RAG_91K_DOCS.sqlite3"),
    ("backup 91K #2", "./backups/chroma_20251112_162344_91K_DOCS.sqlite3"),
]

print("=" * 60)
print("CHECKING CURRENT DATABASES")
print("=" * 60)

for name, path in databases:
    print(f"\n📁 {name}: {path}")
    if os.path.exists(path):
        try:
            client = chromadb.PersistentClient(path=path)
            collections = client.list_collections()
            print(f"   Collections: {len(collections)}")
            total = 0
            for c in collections:
                coll = client.get_collection(c.name)
                count = coll.count()
                total += count
                print(f"   - {c.name}: {count} docs")
            print(f"   TOTAL: {total} docs")
        except Exception as e:
            print(f"   ERROR: {e}")
    else:
        print(f"   NOT FOUND")

print("\n" + "=" * 60)
print("CHECKING BACKUP DATABASES")
print("=" * 60)

for name, backup_path in backup_files:
    print(f"\n📁 {name}: {backup_path}")
    if os.path.exists(backup_path):
        temp_dir = tempfile.mkdtemp()
        try:
            shutil.copy(backup_path, f"{temp_dir}/chroma.sqlite3")
            client = chromadb.PersistentClient(path=temp_dir)
            collections = client.list_collections()
            print(f"   Collections: {len(collections)}")
            total = 0
            for c in collections:
                coll = client.get_collection(c.name)
                count = coll.count()
                total += count
                print(f"   - {c.name}: {count} docs")
                # Show sample metadata
                if count > 0:
                    sample = coll.peek(limit=2)
                    if sample.get("metadatas") and sample["metadatas"]:
                        print(f"     Sample keys: {list(sample['metadatas'][0].keys())}")
            print(f"   TOTAL: {total} docs")
        except Exception as e:
            print(f"   ERROR: {e}")
        finally:
            shutil.rmtree(temp_dir)
    else:
        print(f"   NOT FOUND")

print("\n" + "=" * 60)
print("CHECKING GEN8 REMOTE DATABASE")
print("=" * 60)
try:
    import requests
    resp = requests.get("http://100.79.85.32:8000/api/v2/tenants/default_tenant/databases/default_database/collections", timeout=5)
    if resp.status_code == 200:
        collections = resp.json()
        print(f"   Collections: {len(collections)}")
        for c in collections:
            coll_id = c['id']
            count_resp = requests.get(f"http://100.79.85.32:8000/api/v2/tenants/default_tenant/databases/default_database/collections/{coll_id}/count", timeout=5)
            count = count_resp.json() if count_resp.status_code == 200 else "?"
            print(f"   - {c['name']}: {count} docs")
    else:
        print(f"   ERROR: {resp.status_code}")
except Exception as e:
    print(f"   ERROR: {e}")
