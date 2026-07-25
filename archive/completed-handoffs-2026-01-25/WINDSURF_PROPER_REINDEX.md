# Windsurf: Proper RAG Reindex with Chunking

**Priority:** HIGH
**Problem:** RAG has 208 whole documents instead of ~6,000+ chunked pieces
**Impact:** Semantic search is poor - can't find specific topics within conversations

---

## Quick Summary

The current extraction stored whole conversations as single documents. We need to:
1. Update the best script (`reindex_with_metadata.py`) to point to Gen8
2. Clear the current 208 documents
3. Reindex with proper chunking (1500 chars, 200 overlap)
4. Verify we get 5,000+ chunks

---

## Step 1: Update Script Configuration

Edit `scripts/reindex_with_metadata.py`:

```python
# Change these lines near the top:

# OLD:
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION_NAME = "documents_768_v2"

# NEW:
CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"
```

Also update the export paths to use the latest exports:

```python
# OLD:
EXPORT_BASE = Path.home() / "ai-stack" / "AI_Chat_Exports"

# Verify these paths exist:
# ChatGPT: AI_Chat_Exports/01-19-2026 Exports/ChatGPT/conversations.json
# Claude: AI_Chat_Exports/01-19-2026 Exports/Claude/conversations.json
```

---

## Step 2: Test with Dry Run

```bash
cd ~/ai-stack
source venv/bin/activate
python scripts/reindex_with_metadata.py --dry-run
```

**Expected output:**
- Should find ~200+ ChatGPT conversations
- Should find ~90+ Claude conversations  
- Should report ~5,000-8,000 total chunks

---

## Step 3: Clear Existing Documents

```bash
python -c "
import chromadb
client = chromadb.HttpClient(host='servicebox.taileb8c60.ts.net', port=8000)
col = client.get_collection('faithh_knowledge_base')
existing = col.get()
if existing['ids']:
    print(f'Clearing {len(existing[\"ids\"])} documents...')
    col.delete(existing['ids'])
    print('Done')
else:
    print('Collection already empty')
"
```

---

## Step 4: Run Full Reindex

```bash
python scripts/reindex_with_metadata.py
```

**This will:**
1. Load all conversations
2. Chunk them (1500 chars, 200 overlap)
3. Generate embeddings (all-mpnet-base-v2)
4. Index to Gen8 ChromaDB

**Expected time:** 5-15 minutes depending on embedding speed

---

## Step 5: Verify Results

```bash
python -c "
import chromadb
client = chromadb.HttpClient(host='servicebox.taileb8c60.ts.net', port=8000)
col = client.get_collection('faithh_knowledge_base')
count = col.count()
print(f'Total chunks: {count}')

# Test query
results = col.query(
    query_texts=['FAITHH backend development'],
    n_results=5
)
print(f'\nTest query results:')
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f'{i+1}. {meta.get(\"source\", \"Unknown\")[:50]}')
    print(f'   Preview: {doc[:100]}...\n')
"
```

**Success criteria:**
- Count should be 5,000+ chunks (not 208)
- Test queries should return relevant, focused results

---

## Step 6: Update FAITHH Backend

The backend should already be configured to use Gen8, but verify:

```bash
grep -E "CHROMA|chromadb" ~/ai-stack/.env
```

Should show:
```
CHROMADB_HOST=servicebox.taileb8c60.ts.net
# or
CHROMA_URL=http://servicebox.taileb8c60.ts.net:8000
```

Then restart backend:
```bash
./restart_backend.sh
```

---

## Troubleshooting

### "Collection not found"
```python
# Create it
client.create_collection(
    name="faithh_knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
```

### Embedding model not found
```bash
pip install sentence-transformers
```

### Connection refused
```bash
# Check Gen8 is reachable
curl http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat
```

### Out of memory
Reduce batch size in script from 100 to 50 or 25

---

## Report Back

Please report:
1. Dry-run results (how many chunks expected)
2. Actual indexed count
3. Sample query results
4. Any errors encountered

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/reindex_with_metadata.py` | Main script to update and run |
| `docs/RAG_SCRIPTS_AUDIT.md` | Full audit of all indexing scripts |
| `AI_Chat_Exports/01-19-2026 Exports/` | Source data |

---

**End of Handoff**
