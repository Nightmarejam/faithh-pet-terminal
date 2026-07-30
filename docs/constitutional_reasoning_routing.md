# Constitutional Reasoning Routing Logic

## Overview

Added constitutional reasoning capability to FAITHH backend that prioritizes constitutional principles and evidence mapping for governance-related queries.

## Implementation Details

### 1. Governance Keyword Detection

Added comprehensive keyword detection in `smart_rag_query()` function:

```python
governance_keywords = [
    'constitution', 'constitutional', 'governance', 'governing', 'ucf', 'penumbra', 
    'civic tome', 'astris', 'auctor', 'token', 'floor', 'diversity floor',
    'principle', 'framework', 'charter', 'bylaws', 'rules', 'regulation',
    'gamer', 'minimum compliance', 'structural', 'mechanism', 'policy',
    'governance design', 'participation', 'civic', 'democratic', 'decision making'
]
```

### 2. Retrieval Priority Order

For governance queries, the system now follows this priority:

1. **Domain: constella_constitutional** (highest priority)
   - 14 constitutional principles with metadata
   - 3 mapping document chunks (UCF, Penumbra, Epistemic table)
   
2. **Domain: alife** (fallback)
   - ALIFE experiment results and lineage data
   
3. **General knowledge base** (final fallback)
   - All other documents

### 3. Metadata Extraction

When constitutional principles are retrieved, the system extracts:

```python
principle_metadata = {
    'principle_id': unique identifier,
    'mechanism': which Constella doc it belongs to,
    'experiment_ids': supporting ALIFE experiments,
    'confidence': low/medium/high,
    'title': principle name
}
```

### 4. Response Enhancement

Added `constitutional_reasoning` field to chat responses:

```python
response_data["constitutional_reasoning"] = {
    'principles_retrieved': count,
    'principles': [metadata objects],
    'mechanisms': [unique mechanisms referenced],
    'supporting_experiments': [unique experiment IDs]
}
```

## Routing Flow

```
User Query
    ↓
Keyword Detection (governance_keywords)
    ↓
Is governance query?
    ↓ YES
Query domain=constella_constitutional
    ↓
Results found?
    ↓ YES
Extract principle metadata
    ↓
Add constitutional_reasoning to response
    ↓ NO
Query domain=alife
    ↓ NO
Fall back to general knowledge base
```

## Example Query Flow

**Query:** "What is the Universal Civic Floor and how does it work?"

1. ✅ Governance keywords detected: "ucf", "floor"
2. 🔍 Query ChromaDB: `where={"domain": "constella_constitutional"}`
3. 📄 Retrieved: 2 UCF principles + mapping sections
4. 🏛️ Response includes:
   - `ucf-targeted-floor` principle (high confidence, experiments [5,6,7,9])
   - `ucf-automatic-activation` principle (high confidence, experiments [9])
   - Mechanisms: ["Universal Civic Floor (UCF)"]
   - Supporting experiments: ["5", "6", "7", "9"]

## Integration Points

### Modified Functions

1. **`smart_rag_query()`** - Added governance detection and constitutional retrieval
2. **`_finalize_response()`** - Added constitutional reasoning to response data

### New Files Created

1. **`config/constitutional_principles.json`** - Machine-readable principles
2. **`scripts/index_constella_constitutional.py`** - Indexing script
3. **`scripts/test_constitutional_reasoning.py`** - Test script

### ChromaDB Collection

- **Collection:** `faithh_knowledge_base_v2` (768-dim BGE)
- **Domain:** `constella_constitutional`
- **Documents:** 17 total (14 principles + 3 mapping chunks)

## Testing

Use the test script to verify functionality:

```bash
cd /home/jonat/ai-stack
source venv/bin/activate
python3 scripts/test_constitutional_reasoning.py
```

The script tests 8 governance queries and verifies:
- Constitutional reasoning activation
- Principle retrieval count
- Mechanism identification
- Supporting experiment references

## Benefits

1. **Targeted Retrieval:** Governance queries get precise constitutional principles
2. **Evidence Traceability:** Each principle links to supporting ALIFE experiments  
3. **Mechanism Awareness:** System knows which Constella components are relevant
4. **Fallback Safety:** Falls back to ALIFE data then general knowledge if needed
5. **No Frontend Changes:** Pure backend retrieval enhancement

## Future Enhancements

1. **Confidence Weighting:** Use principle confidence to rank responses
2. **Cross-Reference Links:** Link between principles and mapping document sections
3. **Experiment Details:** Include brief experiment summaries in responses
4. **Dynamic Thresholds:** Adjust keyword detection based on usage patterns
