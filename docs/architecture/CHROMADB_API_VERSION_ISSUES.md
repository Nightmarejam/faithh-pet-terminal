# ChromaDB API Version Issues

## Issue: Collection Count Endpoint Changes

### Problem
The ChromaDB collection count API endpoint has changed between versions, causing validation failures in the Coherence Arbiter's anchor validation.

### Current Status
- **v1 API**: `GET /api/v1/collections/{collection_name}/count` returns `410 Gone` (unimplemented)
- **v2 API**: `GET /api/v2/collections/{collection_name}/count` returns no response (likely incorrect format)
- **v2 Heartbeat**: `GET /api/v2/heartbeat` works correctly

### Working Endpoints
```bash
# ✅ Working - Heartbeat check
curl http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat
# Returns: {"nanosecond heartbeat": 1771901150685085006}

# ❌ Failing - v1 count (410 Gone)
curl http://servicebox.taileb8c60.ts.net:8000/api/v1/collections/faithh_knowledge_base/count
# Returns: {"error":"Unimplemented","message":"The v1 API is unimplemented"}

# ❌ Failing - v2 count (no response)
curl http://servicebox.taileb8c60.ts.net:8000/api/v2/collections/faithh_knowledge_base/count
# Returns: No response (likely incorrect endpoint format)
```

### Workaround in Coherence Arbiter
The anchor validator gracefully handles this by:
1. Trying both v1 and v2 endpoints
2. Falling back to heartbeat proxy when count APIs fail
3. Awarding partial credit (0.175/0.35) for ChromaDB being operational

### Correct v2 API Format (To Be Researched)
The correct v2 format likely requires:
- Different endpoint structure (possibly with tenant/database context)
- Different request method (POST instead of GET)
- Different authentication or headers

### Impact on Validation
- **Current Score**: 0.825/1.0 (82.5%) due to partial ChromaDB credit
- **Expected Score**: 1.0/1.0 when count API is fixed
- **Validation Status**: Still valid (exceeds 0.7 threshold)

### Resolution Needed
1. Research correct ChromaDB v2 API format for collection operations
2. Update anchor validator with correct endpoint
3. Test full validation scoring

### Related Files
- `backend/anchor_validator.py` - Contains the workaround logic
- `backend/coherence_arbiter.py` - Uses the validation results
- `docs/architecture/INFRASTRUCTURE.md` - Should reference this issue

### FAITHH runtime vs raw REST (2026-04-12)

Production RAG uses the **Python `chromadb` HTTP client** against Gen8 (`CHROMA_HOST` / `CHROMA_PORT`): collection sizing and queries go through the client API (e.g. `collection.count()`, `query()`), not manual `curl` to `/api/v1/.../count`. Raw REST path behavior below can still differ from what the app uses; treat anchor-validation fallbacks as defensive, not as proof the server lacks counts.

### Last Updated
2026-04-12 — Refreshed; original workaround 2026-02-23
