# FAITHH Knowledge Graph Integration

## Overview

This integration adds two major capabilities to FAITHH:

1. **Quality Filtering** - Intelligent tiered storage for the auto-indexer
2. **Knowledge Graph** - Self-awareness through structured project knowledge

## Files Included

| File | Purpose |
|------|---------|
| `faithh_knowledge_graph.yaml` | The master knowledge graph (YAML) |
| `quality_filter.py` | Quality filter module for tiered storage |
| `knowledge_graph.py` | Knowledge graph loader and query module |
| `generate_docs.py` | Generates markdown docs from YAML |
| `kg_sync.py` | Sync utility (git, backup, restore) |
| `apply_faithh_patch.py` | Patches existing backend |

## Quick Start

### 1. Copy Files to ai-stack

```bash
cd ~/ai-stack

# Copy the core modules
cp /path/to/quality_filter.py .
cp /path/to/knowledge_graph.py .
cp /path/to/faithh_knowledge_graph.yaml .
cp /path/to/generate_docs.py .
cp /path/to/kg_sync.py .
```

### 2. Test the Quality Filter

```bash
cd ~/ai-stack
source venv/bin/activate
python quality_filter.py
```

This runs test cases and shows how responses are classified.

### 3. Test the Knowledge Graph

```bash
python knowledge_graph.py
```

This loads the YAML and demonstrates queries.

### 4. Generate Documentation

```bash
python generate_docs.py faithh_knowledge_graph.yaml --output ./docs/generated/
```

Creates:
- `ROADMAP.md` - Development priorities
- `PROJECT_MAP.md` - Project relationships  
- `INDEXING_SPEC.md` - Filter specifications

### 5. Apply Backend Patch (Optional)

```bash
python apply_faithh_patch.py --dry-run  # Preview changes
python apply_faithh_patch.py            # Apply patch
```

## How It Works

### Quality Filter Tiers

| Tier | Storage | Criteria |
|------|---------|----------|
| **Tier 1** | ChromaDB (RAG) | Code blocks, decisions, 100+ words, project terms |
| **Tier 2** | Flat file archive | Short responses, acknowledgments |
| **Tier 3** | Discarded | Single words, greetings |
| **Negative** | Separate collection | Failed approaches, corrections |

### Knowledge Graph Structure

```yaml
entities:
  jonathan:      # The operator
  tom_cat_sound: # The business
  faithh:        # The AI system
  constella:     # The governance framework

relationships:
  - from: faithh
    to: jonathan
    type: serves
    
indexing_rules:
  tiers:
    tier_1_indexed: ...
    tier_2_archived: ...
    
vocabulary:
  project_names: ...
  concepts: ...
```

## Keeping the YAML Updated

### Option 1: Git Sync (Recommended)

```bash
# After making changes
python kg_sync.py push -m "Added new decision"

# On another machine
python kg_sync.py pull
```

### Option 2: Manual Updates

1. Edit `faithh_knowledge_graph.yaml`
2. Run `python generate_docs.py ...` to regenerate docs
3. Restart backend to pick up changes

### Option 3: Programmatic Updates

```python
from knowledge_graph import get_knowledge_graph

kg = get_knowledge_graph()
kg.add_decision(
    decision="Implemented quality filtering",
    reasoning="Reduce noise in RAG retrieval"
)
```

## Adding Decisions

The decisions log tracks important choices:

```bash
python kg_sync.py decision \
  --decision "Adopted tiered storage" \
  --reasoning "Improve RAG signal-to-noise ratio"
```

Or programmatically:
```python
from kg_sync import KGSync
sync = KGSync()
sync.add_decision("...", "...")
```

## Integration with Backend

After applying the patch, the backend will:

1. **On each response:** Classify using quality filter
2. **Tier 1 responses:** Index to ChromaDB
3. **Tier 2 responses:** Archive to flat file
4. **On queries:** Inject knowledge graph context

### Manual Integration

If the automatic patch doesn't work, add this to your backend:

```python
# At top of file
from quality_filter import QualityFilter, TieredStorage
from knowledge_graph import get_knowledge_graph

# Initialize
qf = QualityFilter()
storage = TieredStorage()
kg = get_knowledge_graph()

# In your chat handler, after getting response:
result = qf.classify(ai_response)
storage.store(ai_response, result)

# Before sending to LLM, add context:
context = kg.get_context_for_query(user_message)
```

## Monitoring

### Check Filter Stats

```python
from quality_filter import QualityFilter
qf = QualityFilter()
# ... after processing responses ...
print(qf.get_stats())
# {'tier_1_index': 45, 'tier_2_archive': 120, 'tier_3_discard': 30, 'negative_example': 5}
```

### Check Storage

```bash
# Tier 1 - ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Tier 2 - Archive
wc -l ~/ai-stack/data/tier2_archive.jsonl

# Negative examples
wc -l ~/ai-stack/data/negative_examples.jsonl
```

### Check Sync Status

```bash
python kg_sync.py status
```

## Troubleshooting

### "Knowledge graph not found"

```bash
# Check path
ls -la ~/ai-stack/faithh_knowledge_graph.yaml

# Copy from backup
cp /path/to/faithh_knowledge_graph.yaml ~/ai-stack/
```

### "ChromaDB connection failed"

```bash
# Check if running
docker ps | grep chromadb

# Start if needed
cd ~/ai-stack && docker-compose up -d chromadb
```

### "Quality filter not working"

```bash
# Test standalone
cd ~/ai-stack
python quality_filter.py -i
# Then paste text to test classification
```

## Roadmap

- [ ] Auto-sync knowledge graph changes to git
- [ ] Web UI for viewing/editing knowledge graph
- [ ] Metrics dashboard for filter performance
- [ ] Periodic cleanup of Tier 2 archive
- [ ] Integration with FAITHH UI for filter visibility

---

*Part of the FAITHH (Friendly AI Teaching & Helping Hub) project*
