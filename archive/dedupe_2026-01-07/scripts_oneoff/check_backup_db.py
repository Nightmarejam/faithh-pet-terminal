#!/usr/bin/env python3
import chromadb
import tempfile
import shutil

backup_path = "./backups/chroma_20251112_162344_91K_DOCS.sqlite3"
temp_dir = tempfile.mkdtemp()
try:
    shutil.copy(backup_path, f"{temp_dir}/chroma.sqlite3")
    client = chromadb.PersistentClient(path=temp_dir)
    collections = client.list_collections()
    print(f"Total collections: {len(collections)}")
    for c in collections:
        coll = client.get_collection(c.name)
        count = coll.count()
        print(f"  {c.name}: {count} docs")
        if count > 0:
            sample = coll.peek(limit=2)
            if sample.get("metadatas") and sample["metadatas"]:
                print(f"    Sample metadata: {sample['metadatas'][0]}")
finally:
    shutil.rmtree(temp_dir)
