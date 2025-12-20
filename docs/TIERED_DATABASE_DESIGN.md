# Tiered Database Design - RAG Architecture

**Status:** Design Document (Not Implemented)
**Created:** 2025-12-20
**Target Implementation:** Phase 3

---

## Executive Summary

This document outlines a tiered architecture for the RAG (Retrieval-Augmented Generation) system to improve performance, reduce local storage requirements, and enable scalable conversation indexing.

**Key Goals:**
1. Reduce local storage footprint (currently 93k+ documents)
2. Improve query latency with hot cache
3. Enable archive/cold storage for historical data
4. Support distributed deployment (local + Gen8 server)
5. Add metadata tracking for conversation provenance

---

## Current State Analysis

### Existing Architecture
```
┌─────────────────────────────────────┐
│  Local ChromaDB (DESKTOP-JJ1SUHB)  │
│  Collection: documents_768          │
│  Documents: 93,000+                 │
│  Chunks Ready: 27,732               │
│  Embedding: text-embedding-3-small  │
│  Dimensions: 768                    │
└─────────────────────────────────────┘
         ↑
         │ Query/Index
         │
┌────────┴─────────┐
│  rag_processor.py │
│  (No metadata)    │
└──────────────────┘
```

### Problems with Current Approach

1. **Duplicate Indexing**
   - Same conversations indexed multiple times
   - No way to identify or deduplicate
   - 93k documents likely has 60k+ duplicates

2. **No Metadata Tracking**
   - Can't identify source conversation
   - No timestamp or author information
   - Can't filter by date range or topic

3. **Single-Tier Storage**
   - All data local (storage constraint)
   - No hot/cold data separation
   - Query performance not optimized

4. **Scalability Concerns**
   - Local disk space limited
   - All queries hit same database
   - No path to multi-user or distributed access

5. **No Archival Strategy**
   - Old conversations equally accessible as new
   - No lifecycle management
   - Can't prioritize recent/relevant data

---

## Proposed Tiered Architecture

### Three-Tier Design

```
┌────────────────────────────────────────────────────────────┐
│                    Query Processor                          │
│  (Smart routing: check Tier 1 → Tier 2 → Tier 3)          │
└───────┬────────────────┬────────────────┬──────────────────┘
        │                │                │
        ▼                ▼                ▼
┌───────────────┐  ┌──────────────┐  ┌─────────────┐
│   TIER 1      │  │   TIER 2     │  │   TIER 3    │
│  Hot Cache    │  │ Full Corpus  │  │   Archive   │
├───────────────┤  ├──────────────┤  ├─────────────┤
│ Location:     │  │ Location:    │  │ Location:   │
│ Local (SSD)   │  │ Gen8 Server  │  │ S3/Glacier  │
│               │  │              │  │ (optional)  │
│ Size:         │  │ Size:        │  │             │
│ ~5k docs      │  │ ~100k docs   │  │ Unlimited   │
│ (2 months)    │  │ (all active) │  │             │
│               │  │              │  │             │
│ Strategy:     │  │ Strategy:    │  │ Strategy:   │
│ LRU cache     │  │ Full index   │  │ Rarely      │
│ Frequent hits │  │ All queries  │  │ accessed    │
│ Fast queries  │  │ Persistent   │  │ Long-term   │
└───────────────┘  └──────────────┘  └─────────────┘
```

### Tier Specifications

#### Tier 1: Hot Cache (Local)
**Purpose:** Fast access to recently/frequently accessed conversations

- **Location:** Local SSD (`~/ai-stack/chroma_db/tier1_hot/`)
- **Size Limit:** ~5,000 documents (~2 months of recent conversations)
- **Eviction Policy:** LRU (Least Recently Used)
- **Population:**
  - Auto-populated on Tier 2 cache miss
  - Manually promoted high-value conversations
  - Recent activity (last 60 days)
- **Metadata:**
  - `conversation_id`
  - `timestamp`
  - `access_count`
  - `last_accessed`
  - `source` (chatgpt, claude, etc.)
  - `topic_tags` (optional)

**Performance Target:** < 50ms query latency

#### Tier 2: Full Corpus (Gen8 Server)
**Purpose:** Complete conversation history for active use

- **Location:** Gen8 server ChromaDB (`servicebox:~/chromadb/tier2_corpus/`)
- **Size Limit:** ~100k documents (or ~5 years of conversations)
- **Access:** Network query via HTTP API
- **Population:**
  - All indexed conversations
  - Primary source of truth
  - Continuous indexing from new conversations
- **Metadata:**
  - All Tier 1 metadata plus:
  - `conversation_title`
  - `message_count`
  - `participants`
  - `embedding_version`
  - `index_date`

**Performance Target:** < 200ms query latency (LAN)

#### Tier 3: Archive (Optional - Future)
**Purpose:** Long-term storage for historical/inactive conversations

- **Location:** Cloud storage (S3 + Glacier) or external disk
- **Size Limit:** Unlimited
- **Access:** Manual retrieval or scheduled restore
- **Population:**
  - Conversations older than 5 years
  - Manually archived low-value conversations
  - Deleted from Tier 2 after archival
- **Metadata:**
  - Minimal (conversation_id, archive_date, s3_key)

**Performance Target:** Minutes to hours (acceptable for rare access)

---

## Query Flow

### Smart Routing Logic

```python
def query_tiered_rag(query: str, n_results: int = 5):
    """
    Query RAG with tiered fallback
    """
    results = []

    # 1. Check Tier 1 (local hot cache)
    tier1_results = query_tier1(query, n_results)
    results.extend(tier1_results)

    if len(results) >= n_results:
        # Cache hit - return immediately
        return results[:n_results]

    # 2. Query Tier 2 (Gen8 full corpus)
    remaining = n_results - len(results)
    tier2_results = query_tier2(query, remaining * 2)  # Get extras for dedup

    # Promote Tier 2 results to Tier 1 cache
    for result in tier2_results[:remaining]:
        promote_to_tier1(result)

    results.extend(tier2_results[:remaining])

    if len(results) >= n_results:
        return results[:n_results]

    # 3. Optional: Check Tier 3 (archive)
    # Only if user explicitly requests deep search
    # (Not implemented initially)

    return results
```

### Cache Promotion Strategy

- **Automatic:** Any Tier 2 result accessed → promote to Tier 1
- **Manual:** High-value conversations flagged for permanent Tier 1
- **Eviction:** LRU eviction when Tier 1 exceeds size limit
- **Re-population:** Evicted docs can be re-promoted on next access

---

## Metadata Schema

### Enhanced Document Metadata

```python
{
    # Core identifiers
    "conversation_id": "chatgpt_2025-01-15_abc123",
    "message_id": "msg_456",
    "chunk_index": 0,  # If message split into chunks

    # Temporal
    "created_at": "2025-01-15T10:30:00Z",
    "indexed_at": "2025-12-20T12:00:00Z",

    # Source
    "source": "chatgpt",  # chatgpt, claude, manual
    "author": "user" | "assistant" | "system",
    "conversation_title": "Debugging RAG Performance",

    # Access tracking
    "access_count": 5,
    "last_accessed": "2025-12-20T11:00:00Z",
    "tier": 1,  # Current tier

    # Content
    "message_length": 1200,  # chars
    "embedding_model": "text-embedding-3-small",
    "embedding_version": "v1",

    # Optional classification
    "topics": ["rag", "performance", "debugging"],
    "priority": "high" | "medium" | "low",
    "manual_flag": false  # User-flagged important
}
```

### Collection Naming Convention

- Tier 1: `tier1_hot_768` (local)
- Tier 2: `tier2_corpus_768` (Gen8)
- Archive: `archive_YYYY_768` (yearly buckets)

---

## Migration Path

### Phase 1: Cleanup Current Database (Week 1)
**Goal:** Clean slate with metadata-enabled indexing

1. **Audit existing database**
   ```bash
   python scripts/analyze_rag_metadata.py
   # Output: Identify duplicates, estimate cleanup
   ```

2. **Backup current collection**
   ```python
   # Export current collection to JSON
   python scripts/export_chromadb_backup.py
   ```

3. **Delete duplicates or start fresh**
   - Option A: Deduplicate in place (complex)
   - Option B: Fresh index with prepared chunks (recommended)

4. **Create new collection with metadata schema**
   ```python
   from backend.rag_processor import RAGProcessor
   rag = RAGProcessor(collection_name="tier2_corpus_768")
   rag.init_metadata_schema()
   ```

### Phase 2: Set Up Tier 2 (Gen8 Deployment) (Week 1-2)
**Goal:** Gen8 server running ChromaDB as Tier 2

1. **Deploy ChromaDB on Gen8**
   ```bash
   # SSH into servicebox
   ssh -i ~/.ssh/servicebox_ed25519 jonat@100.79.85.32

   # Create service directory
   mkdir -p ~/services/chromadb
   cd ~/services/chromadb

   # Create docker-compose.yml
   cat > docker-compose.yml << 'EOF'
   version: '3'
   services:
     chromadb:
       container_name: chromadb
       image: chromadb/chroma:latest
       ports:
         - "8000:8000"
       volumes:
         - ./data:/chroma/chroma
       environment:
         - CHROMA_SERVER_HOST=0.0.0.0
         - CHROMA_SERVER_HTTP_PORT=8000
       restart: unless-stopped
   EOF

   docker-compose up -d
   ```

2. **Test remote connection**
   ```python
   import chromadb
   client = chromadb.HttpClient(host="100.79.85.32", port=8000)
   print(client.heartbeat())  # Should return timestamp
   ```

3. **Index prepared chunks to Tier 2**
   ```python
   # Use existing 27,732 prepared chunks
   python scripts/index_to_tier2.py
   ```

### Phase 3: Implement Tier 1 Cache (Week 2)
**Goal:** Local hot cache with LRU eviction

1. **Create Tier 1 collection**
   ```python
   rag_tier1 = RAGProcessor(collection_name="tier1_hot_768")
   ```

2. **Implement cache promotion logic**
   - Auto-promote on Tier 2 access
   - LRU eviction when > 5k docs

3. **Update backend to use tiered queries**
   ```python
   # Modify backend/rag_processor.py
   # Add query_tiered_rag() function
   ```

### Phase 4: Update API & Backend Integration (Week 2-3)
**Goal:** Transparent tiered queries from frontend

1. **Update RAGProcessor class**
   - Add `tier` parameter to queries
   - Implement smart routing logic
   - Add cache promotion/eviction

2. **Add metadata tracking**
   - Update indexing pipeline
   - Extract conversation_id, timestamp, source
   - Store in ChromaDB metadata

3. **Update API endpoints**
   - `/api/rag/query` - Use tiered query
   - `/api/rag/promote` - Manual promotion (optional)
   - `/api/rag/stats` - Cache hit rates, tier sizes

### Phase 5: Testing & Optimization (Week 3-4)
**Goal:** Verify performance and correctness

1. **Run stress tests**
   ```bash
   python tests/test_rag_quality.py --tiered
   ```

2. **Benchmark query latency**
   - Tier 1 cache hits
   - Tier 2 fallback queries
   - End-to-end response times

3. **Tune cache size**
   - Adjust Tier 1 limit based on hit rate
   - Monitor disk usage on Gen8

4. **Optimize embedding API calls**
   - Batch indexing
   - Rate limiting
   - Error handling

---

## API Changes

### Backend (rag_processor.py)

#### Current Interface
```python
class RAGProcessor:
    def __init__(self, collection_name="documents_768"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(collection_name)

    def query(self, query_text: str, n_results: int = 5):
        # Simple single-tier query
        return self.collection.query(query_texts=[query_text], n_results=n_results)
```

#### New Interface (Tiered)
```python
class TieredRAGProcessor:
    def __init__(self):
        # Tier 1: Local hot cache
        self.tier1_client = chromadb.PersistentClient(path="./chroma_db/tier1")
        self.tier1 = self.tier1_client.get_or_create_collection("tier1_hot_768")

        # Tier 2: Gen8 remote
        self.tier2_client = chromadb.HttpClient(host="100.79.85.32", port=8000)
        self.tier2 = self.tier2_client.get_or_create_collection("tier2_corpus_768")

        self.tier1_max_docs = 5000

    def query(self, query_text: str, n_results: int = 5,
              metadata_filter: dict = None):
        """
        Smart tiered query with automatic cache promotion
        """
        results = []

        # Check Tier 1
        tier1_results = self.tier1.query(
            query_texts=[query_text],
            n_results=n_results,
            where=metadata_filter
        )
        results.extend(self._format_results(tier1_results, tier=1))

        if len(results) >= n_results:
            self._update_access_metadata(results)
            return results[:n_results]

        # Fallback to Tier 2
        tier2_results = self.tier2.query(
            query_texts=[query_text],
            n_results=n_results * 2,
            where=metadata_filter
        )

        # Promote to Tier 1
        for result in tier2_results['documents'][0][:n_results]:
            self._promote_to_tier1(result, tier2_results['metadatas'][0])

        results.extend(self._format_results(tier2_results, tier=2))
        return results[:n_results]

    def _promote_to_tier1(self, document, metadata):
        """Promote frequently accessed docs to hot cache"""
        # Check if Tier 1 is full
        if self.tier1.count() >= self.tier1_max_docs:
            self._evict_lru()

        # Add to Tier 1 with updated metadata
        metadata['tier'] = 1
        metadata['promoted_at'] = datetime.utcnow().isoformat()
        self.tier1.add(
            documents=[document],
            metadatas=[metadata],
            ids=[metadata['conversation_id'] + "_" + metadata['message_id']]
        )

    def _evict_lru(self):
        """Remove least recently used document from Tier 1"""
        # Query for oldest last_accessed
        results = self.tier1.get(include=['metadatas'], limit=1,
                                  order_by='last_accessed')
        if results['ids']:
            self.tier1.delete(ids=[results['ids'][0]])
```

### Frontend API Changes

#### New Endpoints
```python
# In faithh_professional_backend_fixed.py

@app.route('/api/rag/query', methods=['POST'])
def rag_query_tiered():
    """
    Tiered RAG query with optional metadata filters
    """
    data = request.json
    query = data.get('query')
    n_results = data.get('n_results', 5)

    # Optional filters
    date_range = data.get('date_range')  # e.g., {"start": "2025-01-01", "end": "2025-12-31"}
    source_filter = data.get('source')   # e.g., "chatgpt"

    # Build metadata filter
    metadata_filter = {}
    if date_range:
        metadata_filter['created_at'] = {'$gte': date_range['start'],
                                          '$lte': date_range['end']}
    if source_filter:
        metadata_filter['source'] = source_filter

    results = tiered_rag.query(query, n_results, metadata_filter)

    return jsonify({
        'results': results,
        'metadata': {
            'tier1_hits': sum(1 for r in results if r.get('tier') == 1),
            'tier2_hits': sum(1 for r in results if r.get('tier') == 2)
        }
    })

@app.route('/api/rag/stats', methods=['GET'])
def rag_stats():
    """
    Get cache statistics
    """
    return jsonify({
        'tier1': {
            'count': tiered_rag.tier1.count(),
            'max_docs': tiered_rag.tier1_max_docs,
            'utilization': tiered_rag.tier1.count() / tiered_rag.tier1_max_docs
        },
        'tier2': {
            'count': tiered_rag.tier2.count()
        }
    })
```

---

## Estimated Effort

### Development Time

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| **Phase 1: Cleanup** | Audit, backup, fresh index | 2-3 hours |
| **Phase 2: Gen8 Setup** | ChromaDB deployment, testing | 2-4 hours |
| **Phase 3: Tier 1 Cache** | Local cache, LRU eviction | 3-5 hours |
| **Phase 4: API Updates** | Backend integration, metadata | 4-6 hours |
| **Phase 5: Testing** | Stress tests, optimization | 3-5 hours |
| **Documentation** | Update docs, session reports | 1-2 hours |
| **Total** | | **15-25 hours** |

### Broken Down by Role

**System Admin (Gen8 Setup):** 2-4 hours
- Deploy ChromaDB container
- Configure networking
- Test connectivity

**Backend Developer (Python):** 10-15 hours
- Implement TieredRAGProcessor class
- Add metadata tracking
- Update API endpoints
- Write tests

**DevOps (Testing & Optimization):** 3-6 hours
- Run stress tests
- Benchmark performance
- Tune cache parameters
- Monitor production

---

## Risks & Mitigations

### Risk 1: Network Latency (Tier 2 Queries)
**Impact:** Slow queries if Gen8 unreachable or LAN is slow
**Mitigation:**
- Keep Tier 1 cache hit rate high (> 70%)
- Use Tailscale for reliable connectivity
- Implement query timeout and fallback to local-only

### Risk 2: Data Consistency
**Impact:** Tier 1 cache may be stale
**Mitigation:**
- TTL on cache entries (e.g., 7 days)
- Periodic cache invalidation
- Manual cache clear command

### Risk 3: Disk Space on Gen8
**Impact:** Tier 2 database grows unbounded
**Mitigation:**
- Set maximum Tier 2 size (e.g., 100k docs)
- Implement Tier 3 archival for old conversations
- Monitor disk usage alerts

### Risk 4: Embedding API Costs
**Impact:** Re-indexing 27k chunks costs ~$0.03 (text-embedding-3-small)
**Mitigation:**
- Acceptable one-time cost
- Use batch API for efficiency
- Consider caching embeddings during migration

### Risk 5: Complexity Overhead
**Impact:** More code to maintain, more points of failure
**Mitigation:**
- Comprehensive testing
- Fallback to single-tier on errors
- Clear documentation and logging

---

## Success Metrics

### Performance Targets
- **Tier 1 Cache Hit Rate:** > 70%
- **Tier 1 Query Latency:** < 50ms (p95)
- **Tier 2 Query Latency:** < 200ms (p95)
- **End-to-End Query Time:** < 300ms (p95)

### Operational Metrics
- **Tier 1 Size:** Stable around 5k docs
- **Tier 2 Growth:** < 500 docs/week (steady indexing rate)
- **Disk Usage (Gen8):** < 10GB for Tier 2

### Quality Metrics
- **Zero Duplicates:** After cleanup and metadata tracking
- **Metadata Coverage:** 100% of new documents have full metadata
- **Search Relevance:** No degradation vs. single-tier (baseline)

---

## Future Enhancements

### Post-V1 Improvements

1. **Smart Pre-fetching**
   - Predict likely queries based on conversation context
   - Pre-load related conversations into Tier 1

2. **Multi-User Support**
   - User-specific Tier 1 caches
   - Shared Tier 2 corpus

3. **Advanced Metadata**
   - Automatic topic extraction (ML-based)
   - Sentiment analysis
   - Entity recognition

4. **Tier 3 Archive Implementation**
   - S3 backup for conversations > 5 years old
   - Glacier for ultra-long-term storage
   - Restore-on-demand API

5. **Distributed Tier 2**
   - Multiple Gen8-like servers for redundancy
   - Load balancing across Tier 2 instances

6. **Embedding Model Versioning**
   - Support multiple embedding dimensions
   - Seamless migration to better models

---

## Conclusion

The tiered RAG architecture provides a scalable, performant solution for managing growing conversation history while maintaining fast local queries. The migration path is incremental and can be completed in 2-4 weeks of focused development.

**Recommendation:** Proceed with implementation starting Phase 1 (cleanup) in next session.

---

**Document Status:** Ready for Review
**Next Steps:**
1. Review and approve design
2. Schedule Phase 1 (cleanup) session
3. Prepare Gen8 for ChromaDB deployment

**Related Documents:**
- `MASTER_CONTEXT.md` - Current system state
- `project_states.json` - Project status
- `docs/session-reports/SESSION_2025-12-20_gen8_setup.md` - Today's session

**Last Updated:** 2025-12-20
