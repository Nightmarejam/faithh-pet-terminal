# FAITHH Knowledge Base Reindex - Claude Code Handoff
## Date: January 6, 2026

## Task
Clear old conversation entries from Gen8 ChromaDB and reindex all 285 conversations from fresh exports.

## Current State
- **Gen8 ChromaDB**: 27,616 chunks at http://servicebox.taileb8c60.ts.net:8000
  - 18,401 ChatGPT chunks (Oct-Dec 2025 only)
  - 2,264 Claude chunks (Oct-Dec 2025 only)
  - 6,951 Documentation chunks (KEEP THESE)

## Fresh Exports Ready
Location: `~/ai-stack/knowledge_base/imports/`
- `chatgpt/conversations.json` - 202 conversations (Feb 2024 → Jan 2026)
- `claude/conversations.json` - 83 conversations (Aug 2025 → Jan 2026)
- `claude/memories.json` - 1 memory entry

## Scripts Ready
1. `~/ai-stack/knowledge_base/clear_and_reindex.py` - Clears old conversations
2. `~/ai-stack/knowledge_base/index_conversations.py` - Indexes new conversations

## Execution Steps

```bash
# 1. Navigate and activate
cd ~/ai-stack
source venv/bin/activate

# 2. Clear old conversation entries (keep documentation)
python knowledge_base/clear_and_reindex.py
# Type "yes" when prompted

# 3. Reindex all conversations
python knowledge_base/index_conversations.py

# 4. Verify
curl -s "http://servicebox.taileb8c60.ts.net:8000/api/v2/tenants/default_tenant/databases/default_database/collections/71e13a01-cbb6-48ba-a126-2a16320d40c0/count"
```

## Expected Results
- Delete: 20,665 conversation chunks
- Keep: ~6,951 documentation chunks
- Add: ~25,000-30,000 new conversation chunks (285 convos, chunked)
- Final total: ~32,000-37,000 chunks

## Embedding Model
- Model: `BAAI/bge-base-en-v1.5` (768 dimensions)
- May need to download on first run (~400MB)

## Verification Queries After Indexing
```bash
# Test query
cd ~/ai-stack
source venv/bin/activate
python -c "
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.HttpClient(host='servicebox.taileb8c60.ts.net', port=8000)
coll = client.get_collection('faithh_knowledge_base')
print(f'Total docs: {coll.count()}')

embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')
query = 'FAITHH backend setup'
emb = embedder.encode([query]).tolist()
results = coll.query(query_embeddings=emb, n_results=3)
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f'{i+1}. [{meta.get(\"source\")}] {meta.get(\"title\", \"\")[:50]}')
"
```

## Notes
- Gen8 IP: servicebox.taileb8c60.ts.net (Tailscale)
- Collection: faithh_knowledge_base
- This will give complete conversation history from Feb 2024
