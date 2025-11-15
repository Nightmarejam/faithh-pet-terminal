import chromadb
import shutil
import os

print('=== Current faithh_rag ===')
client = chromadb.PersistentClient(path='./faithh_rag')
collections = client.list_collections()
for col in collections:
    print(f'{col.name}: {col.count()} docs')

print('\n=== Backup structure ===')
temp_path = './temp_inspect'
if os.path.exists(temp_path):
    shutil.rmtree(temp_path)
os.makedirs(temp_path)
shutil.copy('./backups/chroma_20251112_162344_91K_DOCS.sqlite3', f'{temp_path}/chroma.sqlite3')

backup_client = chromadb.PersistentClient(path=temp_path)
backup_collections = backup_client.list_collections()
for col in backup_collections:
    print(f'  - {col.name}: {col.count()} docs')
    
shutil.rmtree(temp_path)
