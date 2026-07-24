# Handoff: Index Harmony Docs into FAITHH RAG
**Date:** 2026-03-01
**Written by:** Claude (MCP session)
**Single task — should take < 5 minutes**
**Archive to:** `docs/archive/` after consumption

---

## Context

IME scaffold is built and working (see previous session). The one remaining
gap: harmony docs not indexed in ChromaDB, so FAITHH can't answer questions
about resonance gating, the IME architecture, or inner monologue design.

The indexer script is already written: `scripts/index_harmony_docs.py`

---

## TASK: Run the Indexer

```bash
cd ~/ai-stack
source venv/bin/activate
python scripts/index_harmony_docs.py
```

Expected output:
```
📄 Found 9 docs to index
   projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md
   ...
🔌 Connecting to ChromaDB at servicebox.taileb8c60.ts.net:8000...
   Collection 'faithh_knowledge_base': 38,284 documents
🧠 Loading all-MiniLM-L6-v2...
  📝 resonance_gating_architecture_note_v1.0.md → 2 chunks
     ✅ Indexed 2 chunks
  ...
✅ Done: N chunks added, 0 skipped
🔍 Verifying with test query: 'resonance gating premature synthesis'
  1. [projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md]: ...
```

If harmony docs appear in the verification query output → **done**.

---

## Verify in FAITHH

```bash
curl -s -X POST http://localhost:5557/api/rag_search \
  -H 'Content-Type: application/json' \
  -d '{"query": "resonance gating premature synthesis exploration consolidation", "n_results": 3}' \
  | python3 -c "import json,sys; r=json.load(sys.stdin); [print(f'{i+1}. {m.get(\"source\",\"?\")}: {d[:80]}') for i,(d,m) in enumerate(zip(r['results'],r.get('metadatas',[{}]*3)))]" 2>/dev/null || \
  curl -s -X POST http://localhost:5557/api/rag_search \
  -H 'Content-Type: application/json' \
  -d '{"query": "resonance gating premature synthesis", "n_results": 3}' | python3 -m json.tool | head -20
```

**Success:** results include `resonance_gating_architecture_note_v1.0.md` as a source
**Failure:** only PULSE/general Harmony docs appear

---

## If It Fails

Most likely issue: embedding model mismatch. Check:
```bash
# Verify model loads
python3 -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); print(m.encode(['test']).shape)"
# Should print: (1, 384)
```

If shape is wrong → the collection was indexed with a different model.
Report the shape and the error. Don't guess.

---

## After Success

Commit:
```bash
cd ~/ai-stack
git add scripts/index_harmony_docs.py ime/ project_states.json scaffolding_state.json
git commit -m "feat: IME C++ scaffold + harmony docs indexer

- ime/ - Inner Monologue Engine scaffold (C++17, CMake)
  - Reads journal entries, evaluates resonance levels
  - 4 tests passing
- scripts/index_harmony_docs.py - Index harmony/IME docs into ChromaDB
- project_states.json - Added inner_monologue_engine project entry
- scaffolding_state.json - Updated session summary

IME is the journal's inner monologue, distinct from FAITHH.
Architecture foundation: harmony/docs/resonance_* specs."
```

---

*Archive this to docs/archive/ after running.*
*Claude, 2026-03-01*
