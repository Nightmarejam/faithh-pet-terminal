# RAG Indexing Scripts Audit

**Date:** 2026-01-25
**Status:** CRITICAL - Fragmented, needs consolidation
**Problem:** 28,876 chunks → 208 documents (chunking was lost)

---

## Script Inventory

### Root Level (ai-stack/)

| Script | Chunking | Target | Collection | Embedding | Status |
|--------|----------|--------|------------|-----------|--------|
| `extract_conversations.py` | ❌ None | JSON file | N/A | N/A | ACTIVE |
| `index_chromadb_direct.py` | ❌ None | Gen8 (192.158.1.243) | faithh_knowledge_base | ChromaDB built-in | ACTIVE |
| `index_to_chromadb.py` | ❌ None | Gen8 (REST API) | faithh_knowledge_base | ChromaDB built-in | DUPLICATE |

### Backend (backend/)

| Script | Chunking | Target | Collection | Embedding | Status |
|--------|----------|--------|------------|-----------|--------|
| `rag_processor.py` | ✅ 500 chars, 50 overlap | localhost:8000 | documents | Ollama nomic-embed | LEGACY |

### Scripts/Indexing (scripts/indexing/)

| Script | Chunking | Target | Collection | Embedding | Status |
|--------|----------|--------|------------|-----------|--------|
| `index_claude_chats_chunked.py` | ✅ 6-message groups | localhost:8000 | documents_768 | all-mpnet-base-v2 | LEGACY |
| `index_documents_chromadb.py` | ✅ 1000 chars, 200 overlap | Local persistent | documents | Ollama nomic-embed | LEGACY |
| `index_claude_chats.py` | ? | ? | ? | ? | UNKNOWN |
| `index_recent_docs.py` | ? | ? | ? | ? | UNKNOWN |

### Scripts/ (scripts/)

| Script | Chunking | Target | Collection | Embedding | Status |
|--------|----------|--------|------------|-----------|--------|
| `index_docs_to_gen8.py` | ✅ 1500 chars, 200 overlap | Gen8 (192.158.1.243 Tailscale) | faithh_knowledge_base | BGE-base-en-v1.5 | BEST DOCS |
| `reindex_with_metadata.py` | ✅ 1500 chars, 200 overlap | localhost:8000 | documents_768_v2 | all-mpnet-base-v2 | BEST CONVOS |

---

## The Problem

### Before (28,876 chunks):
- Conversations were chunked into 500-1500 character pieces
- Each conversation became ~100 chunks on average
- Better for semantic search on specific topics

### Now (208 documents):
- Whole conversations stored as single documents
- Average document size: ~5,000-50,000 characters
- Poor semantic search (embedding of huge text loses specificity)

### Why It Happened:
1. Database was lost during container recreation
2. Rebuild used `extract_conversations.py` + `index_chromadb_direct.py`
3. These scripts DON'T chunk - they store whole conversations

---

## Configuration Chaos

### ChromaDB Hosts Used:
- `localhost:8000` - Old local ChromaDB
- `192.158.1.243:8000` - Gen8 via Tailscale
- `192.158.1.243:8000` - Gen8 via LAN ← CURRENT

### Collection Names Used:
- `documents` - Original
- `documents_768` - MPNet embeddings
- `documents_768_v2` - Reindex version
- `faithh_knowledge_base` ← CURRENT

### Embedding Models Used:
- `nomic-embed-text` via Ollama - Old
- `all-mpnet-base-v2` - Sentence Transformers (768 dim)
- `BAAI/bge-base-en-v1.5` - Gen8 default (768 dim) ← CURRENT

---

## Recommended Canonical Configuration

### Target:
- **Host:** 192.158.1.243:8000 (Gen8 LAN)
- **Collection:** faithh_knowledge_base
- **Embedding:** BAAI/bge-base-en-v1.5 (768 dim) - ChromaDB default

### Chunking Strategy:
- **Conversations:** 1500 chars, 200 overlap (better context than 500)
- **Documents:** 1500 chars, 200 overlap
- **Sentence boundary aware:** Yes

### Expected Results:
- 306 conversations × ~20 chunks each = **~6,000+ chunks**
- Plus documentation = **~7,000-10,000 total chunks**

---

## Consolidation Plan

### KEEP (Canonical):
1. **`scripts/reindex_with_metadata.py`** - Best conversation indexer
   - UPDATE: Change host to 192.158.1.243
   - UPDATE: Change collection to faithh_knowledge_base
   - UPDATE: Change embedding to BGE (or use ChromaDB default)

### ARCHIVE (Move to ARCHIVE/scripts/):
- `extract_conversations.py` (no chunking)
- `index_chromadb_direct.py` (no chunking)
- `index_to_chromadb.py` (duplicate)
- `backend/rag_processor.py` (old config)
- `scripts/indexing/index_claude_chats_chunked.py` (old config)
- `scripts/indexing/index_documents_chromadb.py` (old config)
- `scripts/index_docs_to_gen8.py` (docs only, old Tailscale IP)

### CREATE:
- `scripts/faithh_reindex.py` - Single canonical script that:
  1. Reads all exports (ChatGPT, Claude, Grok)
  2. Chunks properly (1500 chars, 200 overlap)
  3. Indexes to Gen8 ChromaDB
  4. Has dry-run mode
  5. Shows progress and stats

---

## Immediate Action Items

### Step 1: Test Current Scripts
```bash
# Check what reindex_with_metadata.py would do
cd ~/ai-stack
source venv/bin/activate
python scripts/reindex_with_metadata.py --dry-run
```

### Step 2: Update Configuration
Edit `scripts/reindex_with_metadata.py`:
```python
CHROMA_HOST = "192.158.1.243"  # Gen8 LAN
CHROMA_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"
# Keep embedding as all-mpnet-base-v2 or switch to BGE
```

### Step 3: Clear and Reindex
```bash
# Clear existing (208 docs)
python -c "
import chromadb
client = chromadb.HttpClient(host='192.158.1.243', port=8000)
col = client.get_collection('faithh_knowledge_base')
col.delete(col.get()['ids'])
print('Cleared')
"

# Reindex with chunking
python scripts/reindex_with_metadata.py
```

### Step 4: Verify
```bash
python -c "
import chromadb
client = chromadb.HttpClient(host='192.158.1.243', port=8000)
col = client.get_collection('faithh_knowledge_base')
print(f'Documents: {col.count()}')
"
# Should be 5,000+ chunks
```

---

## Long-term: Unified Script Specification

```python
# faithh_reindex.py - Canonical Indexer

SOURCES = {
    "chatgpt": "AI_Chat_Exports/01-19-2026 Exports/ChatGPT/conversations.json",
    "claude": "AI_Chat_Exports/01-19-2026 Exports/Claude/conversations.json",
    "docs": ["docs/", "projects/", "MASTER_CONTEXT.md", "LIFE_MAP.md"]
}

CONFIG = {
    "chroma_host": "192.158.1.243",
    "chroma_port": 8000,
    "collection": "faithh_knowledge_base",
    "chunk_size": 1500,
    "chunk_overlap": 200,
    "embedding": "ChromaDB default (BGE)"
}

FEATURES = [
    "Dry-run mode",
    "Progress bar",
    "Deduplication",
    "Category inference",
    "Incremental updates",
    "Backup before clear"
]
```

---

## File Archive Checklist

Move to `ARCHIVE/scripts/indexing-legacy/`:
- [ ] extract_conversations.py
- [ ] index_chromadb_direct.py  
- [ ] index_to_chromadb.py
- [ ] backend/rag_processor.py (copy)
- [ ] scripts/indexing/index_claude_chats_chunked.py
- [ ] scripts/indexing/index_documents_chromadb.py
- [ ] scripts/index_docs_to_gen8.py

Keep and consolidate:
- [ ] scripts/reindex_with_metadata.py → Update config, rename to faithh_reindex.py

---

**End of Audit**
