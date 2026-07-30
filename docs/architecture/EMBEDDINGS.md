# Embeddings — how retrieval actually works here

**2026-07-29** · the living reference for FAITHH's embedding and retrieval layer.
Companion to [VECTOR_STORE_REVIEW.md](VECTOR_STORE_REVIEW.md) (what is *in* the
store) and [CHIP_SYSTEM_RECONCILIATION.md](CHIP_SYSTEM_RECONCILIATION.md) (how
signals are fused).

If you read one thing: **an embedding is only comparable to another embedding made
by the same model.** Almost every retrieval bug in this system has been a
violation of that one sentence.

---

## 1. The mental model

Retrieval has two halves that must agree:

```
   INGEST                                QUERY
   text ─chunk─► embedder ─► vector       question ─► embedder ─► vector
                              │                                    │
                              └────► Chroma collection ◄────────────┘
                                     compares by distance
```

The comparison is only meaningful if **both** embedders are the same model. The
collection stores a fixed vector width and will reject anything else, so a
mismatch shows up either as a hard dimension error or — worse — as results that
come back but mean nothing.

**Vocabulary** (the field is called *information retrieval*, if you want to read
further):

| term | what it means here |
|---|---|
| **embedding** | a list of floats representing meaning; 768 of them for our model |
| **dimension** | how many floats. BGE-base = 768, MiniLM-L6 = 384 |
| **distance** | how far apart two vectors are. **Lower is better** |
| **space** | the distance formula: `l2` (straight-line) or `cosine` (angle) |
| **chunk** | documents are split before embedding; a chunk is one retrievable unit |
| **top-k / n_results** | how many nearest chunks to return |

---

## 2. What this system uses

| setting | value | where |
|---|---|---|
| model | **`BAAI/bge-base-en-v1.5`** | `backend/rag_processor.py:31`, `faithh_professional_backend_fixed.py:575` |
| dimension | **768** | property of the model |
| live collection | **`faithh_knowledge_base_v2`** | `CHROMA_COLLECTION` in the service env |
| space | `l2` | collection metadata |
| chunk / overlap | 500 / 50 chars | `rag_processor.py:36` |
| chat-export chunking | 5 messages per chunk | `scripts/ingest/manifest_claude_exports.py:37` |
| device | CUDA if available, else CPU | `_resolve_device()` |
| override | `FAITHH_EMBED_DEVICE=cpu` | when the GPU is busy with Plex |

**Canonical env var: `FAITHH_EMBEDDER_MODEL`.** `FAITHH_EMBED_MODEL` is accepted as
a compatibility alias — see the trap in §5.

CPU vs CUDA is not a rounding difference: measured 2026-07-26 on the Gen8,
**3.8 docs/sec on CPU against 135 docs/sec on CUDA (~36×)** — a 30-hour re-index
versus 50 minutes.

---

## 3. The 768 / 384 split

Only **one** collection matches the live embedder:

| collection | dim | comparable with the live query embedder? |
|---|---:|---|
| `faithh_knowledge_base_v2` | **768** | ✅ yes |
| `faithh_knowledge_base` | 384 | ❌ no — legacy MiniLM |
| `alife_lineage` | 384 | ❌ no |
| `governance_corpus` | 384 | ❌ no |
| `faithh_uncertainty_surface` | 384 | ❌ no |
| `faithh_session_metrics` | 384 | ❌ no |

Consequence: **cross-collection blending is a dimension mismatch by construction.**
That is the source of

```
❌ Error in ALIFE query: Collection expecting embedding with dimension of 384, got 768
```

which comes from the ALife blend at `faithh_professional_backend_fixed.py:1553`.

---

## 4. Diagnosing `best_distance`

`best_distance` is the distance of the closest chunk. **Lower is better.**

| value | reading |
|---|---|
| 0.0–0.35 | strong match, grounded |
| 0.35–0.60 | usable |
| > 0.60 | weak — trips `_preflight_failed` and injects a low-confidence hazard |
| **exactly 1.0** | **almost never a real measurement** |

### Why 1.0 is special

`1.0` is the *fallback literal* when no distances were collected:

```python
_best_distance = min(_rag_distances) if _rag_distances else 1.0   # ~line 2874
```

So a 1.0 means one of two very different things, and both have now occurred here:

1. **Dimension mismatch** — the query embedder disagrees with the collection.
2. **Distances dropped in code** — retrieval worked, but the distances never
   reached the calculation. This happened when the RAG fallback flattened hits to
   bare strings, discarding the distances Chroma had already returned.

The tell for case 2 is `rag_hits > 0` *with* `best_distance == 1.0`: documents came
back, so retrieval was fine, therefore the loss is in the plumbing.

### The same trap, generalised

This system has produced **three** constants that impersonated measurements:

| symptom | looked like | actually was |
|---|---|---|
| `best_distance: 1.0` | no relevant docs | distances discarded in code |
| `convergence_score: 0.5` | medium coherence | a hardcoded fallback after a swallowed exception |
| Groq/Gemini `degraded` | provider outage | health probes sent without credentials |

**If a metric never changes, distrust it before you trust it.** Vary the input and
confirm the number moves.

---

## 5. Traps that are still live

### Two env var names, historically

`rag_processor.py` read `FAITHH_EMBED_MODEL`; the backend reads
`FAITHH_EMBEDDER_MODEL`. Setting only one left the ingest and query halves on
different embedders. `rag_processor.py` now accepts both, preferring
`FAITHH_EMBEDDER_MODEL`. **Use that name.**

### Ingest scripts default to the 384 model

`scripts/indexing/index_chat_exports.py` defaults to `all-MiniLM-L6-v2` (384) and
to the `faithh_knowledge_base` collection. Those two defaults are consistent with
*each other*, which is why it works — but point it at `faithh_knowledge_base_v2`
without setting `FAITHH_EMBEDDER_MODEL` and it will try to write 384-dim vectors
into a 768-dim collection.

**Always set the model explicitly when running any ingest:**

```bash
FAITHH_EMBEDDER_MODEL=BAAI/bge-base-en-v1.5 CHROMA_COLLECTION=faithh_knowledge_base_v2 python <script>
```

### Chip centroids are a third embedder surface

`ml/consolidate_chips.py` embeds chip descriptions to build centroids. It defaults
to BGE (768), which currently matches — chips load as `(15, 768)`. If the KB is
ever re-embedded with a different model, **the chips must be rebuilt too**, or
chip↔RAG convergence silently degrades to `signal_strength_only`.

---

## 6. Verifying the system

```bash
# 1. What dimensions are actually stored?
python - <<'PY'
import chromadb
c = chromadb.HttpClient(host='localhost', port=8000)
for col in c.list_collections():
    n = col if isinstance(col, str) else col.name
    h = c.get_collection(n); pk = h.peek(limit=1); e = pk.get('embeddings')
    dim = len(e[0]) if e is not None and len(e) and e[0] is not None else None
    print(f'{n:<32}{h.count():>9,}  dim={dim}')
PY
```

```bash
# 2. Is retrieval grounded? Expect best_distance well under 0.60, never exactly 1.0
curl -s -X POST http://servicebox.taileb8c60.ts.net:5557/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is the Constella governance model?"}' \
  | python -c "import json,sys; d=json.load(sys.stdin); print(d['best_distance'], d['rag_hits'], d['integrations_used'])"
```

```bash
# 3. Is convergence measuring, or falling back?
#    Want ['rag_chip_alignment']. ['signal_strength_only'] means no embeddings reached the arbiter.
#    Run it twice with different questions — if the number never moves, it is not a measurement.
```

---

## 7. Re-indexing safely

Never mutate a collection in place. The pattern in
`scripts/ingest/reindex_collection.py`:

1. **Write to a new collection** — the old one keeps serving throughout.
2. **Prefix the ids** (`reidx_{source}_{id}`) so a partial run is re-runnable.
3. **Verify**: counts match, `peek()` shows the expected dimension, and a known
   query returns a sane `best_distance`.
4. **Flip `CHROMA_COLLECTION`** in the service env and restart. That is the
   cutover, and it is one line to revert.
5. **Rebuild chip centroids** if the model changed (§5).
6. **Keep the old collection** for a few days. Disk is not the constraint —
   15 GB used of 916 GB.
