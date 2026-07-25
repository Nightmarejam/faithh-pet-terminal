# FAITHH Development Roadmap

*Auto-generated from knowledge graph on 2025-12-29*

---

## Current State

### Rag Pipeline ✅

**Status:** operational

- Database: ChromaDB
- Documents Indexed: 91,000

### Auto Indexer ✅

**Status:** operational

- Behavior: Indexes every response

### Web Interface ✅

**Status:** operational


### Local Llm ✅

**Status:** operational

- GPU: RTX 3090
- Performance: 6-7x improvement achieved

---

## Known Issues

### Rag Pipeline

- ⚠️ Embedding dimension mismatches (resolved)
- ⚠️ GPU routing issues (resolved)

### Auto Indexer

- ⚠️ Creates noise - indexes low-value responses
- ⚠️ No quality filtering

---

## Proposed Solutions

### Auto Indexer

- 💡 Pre-index quality scoring
- 💡 Tiered storage (indexed/archived/discarded)
- 💡 Negative examples archive

---

## Development Priorities

### 🔴 High Priority

- Quality filtering for auto-indexer
- Knowledge graph integration
- Self-awareness capabilities

### 🟡 Medium Priority

- Improved RAG query relevance
- Cross-project context linking

### 🟢 Low Priority

- UI improvements
- Additional model integrations

---

## Recent Decisions

### 2025-11

**Decision:** Integrated Constella Framework docs into RAG

**Reasoning:** Unified knowledge base across all projects

### 2025-12

**Decision:** Adopted hybrid knowledge graph approach

**Reasoning:** Machine-readable + human-friendly, best of both worlds
