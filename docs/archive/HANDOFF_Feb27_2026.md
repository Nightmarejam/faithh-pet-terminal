# FAITHH + CPP Environment — Session Handoff
**Date:** February 27, 2026
**Written by:** Claude (end of session)
**For:** Windsurf execution tomorrow

---

## WHERE WE ARE

### What was accomplished today
- Fixed primary model routing bug: `deepseek-r1:32b` → `llama3.3:70b`
- Routing block in `faithh_professional_backend_fixed.py` lines ~119-126 is now correct
- Backend restarts cleanly via `./restart_backend.sh`
- Documented resonance gating architecture (new concept, see below)

### What is still broken
Two separate problems remain:

**Problem 1 — Routing still failing on some queries**
Tax/financial questions are being classified as "complex" and routed to
`llama3.3:70b` which takes 60-120s to respond. Our test curl times out
before getting a response. Need to either:
- Increase timeout tolerance in the frontend
- OR reclassify financial/retrieval queries as default (use qwen25-grounded)
- OR verify llama3.3:70b actually responds if given enough time

Coding queries still fail — `qwen2.5-coder:14b` is not installed.
The coding branch needs to fall back to `qwen25-grounded:latest`.

**Problem 2 — RAG retrieval not working**
Test queries with known answers in documents returned hallucinated content.
Example: Asked for FGS business plan conditions → got invented "Phase 3
Remote Studio Infrastructure" content that doesn't exist anywhere.
The documents are not being retrieved before generation, or ChromaDB
is not indexed with current project files.

---

## MODELS ACTUALLY AVAILABLE (verified)

```
qwen25-grounded:latest    14.8B   Q4_K_M   ← primary, use for everything
llama3.3:70b              70.6B   Q4_K_M   ← heavy reasoning only, slow
```

Nothing else. No coder model, no deepseek, no qwen3-faithh.

---

## TASK 1 — Fix Remaining Routing Issues

File: `/home/jonat/ai-stack/faithh_professional_backend_fixed.py`

Around line 114-126, the routing function needs two fixes:

**Fix A — Coding fallback:**
```python
if is_coding:
    # qwen2.5-coder:14b not installed, fall back to grounded
    return "qwen25-grounded:latest"
```

**Fix B — Complex query timeout:**
Either route complex queries to qwen25-grounded (faster, good enough)
or verify llama3.3:70b responds within 90s and update frontend timeout.
Recommended: Use qwen25-grounded for everything until llama3.3 load
time is profiled.

After fixing, restart backend and run:
```bash
cd /home/jonat/ai-stack && bash test_faithh_retrieval.sh
```

Success = no 502 errors, model_used shows available model.

---

## TASK 2 — Diagnose RAG Retrieval

The retrieval pipeline exists (ChromaDB connected at 192.158.1.243:8000)
but is not surfacing project documents in responses.

**Step 1 — Check what's indexed:**
```bash
cd /home/jonat/ai-stack
source venv/bin/activate
python3 -c "
import chromadb
client = chromadb.HttpClient(host='192.158.1.243', port=8000)
cols = client.list_collections()
for c in cols:
    col = client.get_collection(c.name)
    print(c.name, col.count())
"
```

**Step 2 — Test a direct RAG search:**
```bash
curl -s -X POST http://localhost:5557/api/rag/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "Floating Garden Soundworks business plan conditions", "n_results": 3}' \
  | python3 -m json.tool
```

**Step 3 — Check what directories are being watched for auto-index:**
Look in `faithh_professional_backend_fixed.py` for the auto-index
background thread. Find what paths it watches. Key paths that SHOULD
be indexed:
```
/home/jonat/ai-stack/projects/tomcat-sound/
/home/jonat/ai-stack/projects/constella-framework/harmony/docs/
/home/jonat/ai-stack/knowledge_base/
```

**Step 4 — If not indexed, manually trigger:**
```bash
curl -s -X POST http://localhost:5557/api/rag/index \
  -H 'Content-Type: application/json' \
  -d '{"path": "/home/jonat/ai-stack/projects/"}'
```
(endpoint name may differ — check the route definitions)

**Success criteria for RAG:**
Ask: "What conditions must be true before the Floating Garden Soundworks
final business plan can be written?"

Expected answer (from FGS_Master_Data_Aggregation.md Section 11):
1. Tom Cat Sound LLC clean (1065 filed)
2. Phase 1 revenue baseline (6-12 months)
3. TC relationship clarified
4. Breitenbush site visit done
5. Earth bermed construction contractor conversation
6. Grant landscape mapped

If the response matches these 6 points → RAG is working.
If it invents different content → still not retrieving.

---

## TASK 3 — CPP Environment Status Check

We don't know the current state of the CPP environment.
Need to find it and verify it runs.

**Step 1 — Find it:**
```bash
find /home/jonat -name "*.cpp" -o -name "CMakeLists.txt" \
  -o -name "*.cc" 2>/dev/null | head -20

ls /home/jonat/ai-stack/projects/ 2>/dev/null
```

**Step 2 — Check what it's supposed to do:**
Look for a README or any .md file in the cpp project directory.

**Step 3 — Try to build:**
```bash
# If CMake project:
mkdir -p build && cd build && cmake .. && make

# If simple compilation:
g++ -o test main.cpp && ./test
```

**Step 4 — Report back:**
What does it do, does it compile, does it run, what's broken.

---

## VERIFICATION TESTS (run after fixes)

Save as `/home/jonat/ai-stack/test_faithh_retrieval.sh`
(file already exists from today):

```bash
bash /home/jonat/ai-stack/test_faithh_retrieval.sh
```

The 4 tests in that file check:
1. Specific number retrieval (Tom Cat Sound NOL)
2. Honest incompleteness (TC's SSN — should say unknown)
3. Fresh document retrieval (resonance gating concept)
4. FGS conditions (6-point list from project docs)

---

## KEY FILES

| File | Purpose |
|------|---------|
| `faithh_professional_backend_fixed.py` | Main backend — routing fix here |
| `test_faithh_retrieval.sh` | 4 test queries |
| `restart_backend.sh` | Clean restart |
| `backend.log` | Live log — `tail -f backend.log` |
| `WINDSURF_FIX_model_routing.md` | Previous fix doc |
| `projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md` | New doc needs indexing |
| `projects/tomcat-sound/08_floating_garden/FGS_Master_Data_Aggregation.md` | FGS conditions doc |

---

## PRIORITY ORDER

1. Fix coding route fallback (5 min)
2. Verify llama3.3:70b response time or reroute (15 min)
3. Diagnose RAG — is anything indexed? (20 min)
4. Get RAG returning correct answers on test queries (variable)
5. CPP environment — find, assess, report state

---

*End of handoff — Claude, Feb 27 2026*
