# Opus → Sonnet Handoff: Constella Self-Improving Knowledge System
**Date**: 2025-11-25  
**Reviewed By**: Claude Opus 4.5  
**For Execution By**: Claude Sonnet  
**Purpose**: Enable FAITHH to discover and improve Constella knowledge automatically

---

## Executive Summary

Instead of requiring Jonathan to manually fill in blanks, we've created a **self-improving system**:

1. **Living Master Reference** - Has known, partial, and unknown sections clearly marked
2. **Discovery System** - Searches existing 91k documents to fill gaps
3. **API Endpoints** - FAITHH can trigger discovery and log findings
4. **Approval Workflow** - Discoveries are logged for Jonathan's review before updating

**Jonathan's role**: Review discoveries and approve updates (5 min/week), not write documentation.

---

## Decisions Made (Do Not Revisit)

1. ✅ **Self-improving approach**: FAITHH discovers information, doesn't wait for manual input
2. ✅ **Confidence markers**: ✅ KNOWN, 🔶 PARTIAL, ❓ UNKNOWN in master doc
3. ✅ **Discovery queries**: Pre-defined for each unknown section
4. ✅ **Approval workflow**: Discoveries logged, not auto-applied
5. ✅ **Living document pattern**: Master reference updates over time

---

## Files Created by Opus

| File | Purpose | Status |
|------|---------|--------|
| `docs/CONSTELLA_MASTER_REFERENCE.md` | Living master reference with confidence markers | ✅ Ready |
| `scripts/discovery/discover_constella.py` | CLI discovery tool | ✅ Ready |
| `discovery_blueprint.py` | Flask API for discovery | ✅ Ready |

---

## Task 1: Run Initial Discovery (First Priority)

**Time**: 15 minutes

Run the discovery script to search your 91k documents for Constella information:

```bash
cd ~/ai-stack
source venv/bin/activate

# Run full discovery
python scripts/discovery/discover_constella.py

# Or run interactively
python scripts/discovery/discover_constella.py --interactive

# Or search specific section
python scripts/discovery/discover_constella.py --section tokens
```

**What it does**:
- Searches ChromaDB for each unknown/partial section
- Uses pre-defined discovery queries
- Shows relevant passages with confidence scores
- Saves results to `docs/constella_discoveries.json`

**Expected output**:
```
🔍 Discovering: UCF (Unified Civic Framework)
   Current confidence: PARTIAL
   Seeking: Specific mechanisms within UCF...

📚 Found 5 relevant passages:
[1] Relevance: HIGH (distance: 0.35)
    Content: UCF handles compliance through resonance-based verification...
```

---

## Task 2: Integrate Discovery Blueprint into Backend

**Time**: 30 minutes

Add the discovery API to the FAITHH backend:

### Step 2a: Import and register the blueprint

Edit `faithh_professional_backend_fixed.py`:

```python
# Add near the top imports
from discovery_blueprint import create_discovery_blueprint

# Add after other blueprint registrations (near end of file, before app.run)
# Discovery system for self-improving knowledge
discovery_bp = create_discovery_blueprint(collection, CHROMA_CONNECTED)
app.register_blueprint(discovery_bp)
print("✅ Discovery blueprint registered")
```

### Step 2b: Test the endpoints

```bash
# Check master reference status
curl http://localhost:5557/api/master_reference/status

# Discover information about tokens
curl http://localhost:5557/api/discover/tokens

# Discover all sections
curl http://localhost:5557/api/discover/all

# Check pending discoveries
curl http://localhost:5557/api/discovery/pending
```

---

## Task 3: Index Master Reference

**Time**: 15 minutes

Index the master reference with boosted priority:

```python
# ~/ai-stack/scripts/indexing/index_master_doc.py
# (Already created by Opus - just run it)

cd ~/ai-stack
source venv/bin/activate
python scripts/indexing/index_master_doc.py docs/CONSTELLA_MASTER_REFERENCE.md
```

Expected output:
```
✅ Indexed master document: master_constella_abc123
   Category: constella_master
   Priority: highest
```

---

## Task 4: Update smart_rag_query for Master Priority

**Time**: 30 minutes

Modify `smart_rag_query` in the backend to:
1. Detect Constella queries
2. Always retrieve master reference first
3. Then search for specific context

**Key change** (add to smart_rag_query function):

```python
# Detect Constella queries
constella_keywords = ['constella', 'resonance', 'civic', 'governance', 'astris', 
                      'auctor', 'tome', 'penumbra', 'ucf', 'siting', 'dignity',
                      'celestial equilibrium', 'harmonic alignment']

if any(kw in query_lower for kw in constella_keywords):
    print(f"🎯 Detected Constella query")
    
    # Try master reference first
    try:
        master_results = collection.query(
            query_texts=[query_text],
            n_results=1,
            where={"category": "constella_master"}
        )
        
        if master_results['documents'] and master_results['documents'][0]:
            print(f"   📚 Found master reference")
            # Prepend master doc to results
            # ... (full implementation in previous handoff)
    except:
        pass
```

---

## Task 5: Test the System

**Time**: 20 minutes

### Test 1: Discovery works
```bash
curl http://localhost:5557/api/discover/all
```

### Test 2: Master reference is found
```bash
curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Constella?", "n_results": 5}'
```
Expected: Master reference should be first result

### Test 3: FAITHH can explain Constella
Use the UI or:
```bash
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain what Constella is and its philosophical foundation", "model": "llama3.1-8b", "use_rag": true}'
```

Expected: Response should reference:
- Resonance, dignity, renewal
- Celestial Equilibrium
- Proof-before-scale civic OS

### Test 4: Unknown sections are honest
```bash
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What exactly is the Penumbra Accord in Constella?", "model": "llama3.1-8b", "use_rag": true}'
```

Expected: Response should acknowledge uncertainty and possibly search for more info

---

## How the Self-Improving Loop Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. User asks about Constella                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. FAITHH checks master reference                          │
│     - If section is ✅ KNOWN: Answer confidently            │
│     - If section is 🔶 PARTIAL: Answer + note gaps          │
│     - If section is ❓ UNKNOWN: Search conversation history │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. If discovery finds good info:                           │
│     - Log to pending_discoveries.json                       │
│     - Mention in response: "I found some info about this"   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Jonathan reviews discoveries (weekly)                   │
│     - Approve good ones → Update master reference           │
│     - Reject bad ones → Improve discovery queries           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Master reference improves over time                     │
│     - ❓ UNKNOWN → 🔶 PARTIAL → ✅ KNOWN                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Jonathan's Weekly Review (5-10 minutes)

```bash
# See pending discoveries
curl http://localhost:5557/api/discovery/pending

# Or check the file directly
cat ~/ai-stack/docs/pending_discoveries.json
```

For each discovery:
- **If accurate**: Update master reference with the info
- **If inaccurate**: Delete from pending
- **If partial**: Note for further discovery

---

## Success Criteria

- [ ] Discovery script runs without errors
- [ ] Discovery blueprint responds to API calls
- [ ] Master reference is indexed with `constella_master` category
- [ ] Constella queries retrieve master reference first
- [ ] FAITHH can explain known sections confidently
- [ ] FAITHH acknowledges uncertainty on unknown sections
- [ ] Discoveries are logged for review

---

## Files to Create/Modify Summary

| File | Action | Purpose |
|------|--------|---------|
| `faithh_professional_backend_fixed.py` | Modify | Add discovery blueprint + update smart_rag_query |
| `scripts/indexing/index_master_doc.py` | Create | Index master docs with priority |
| `scripts/discovery/discover_constella.py` | Created ✅ | CLI discovery tool |
| `discovery_blueprint.py` | Created ✅ | Flask API for discovery |
| `docs/CONSTELLA_MASTER_REFERENCE.md` | Created ✅ | Living master reference |

---

## What This Approach Achieves

1. **Jonathan doesn't write docs** - System discovers from existing conversations
2. **Knowledge improves over time** - Each discovery fills gaps
3. **Honest uncertainty** - FAITHH admits what it doesn't know
4. **Reviewable process** - Discoveries are logged, not auto-applied
5. **Reusable pattern** - Can apply to other projects (FAITHH, Audio, etc.)

---

## Future Enhancements (Not Now)

- Auto-update master reference after N approvals
- Learning from corrections (improve discovery queries)
- Cross-reference between projects
- Summary generation for decisions section

---

**End of Handoff**

*Generated by Claude Opus 4.5 | 2025-11-25*
