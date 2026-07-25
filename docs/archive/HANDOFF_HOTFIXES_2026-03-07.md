# Windsurf Handoff — FAITHH Hot Fixes
# Date: 2026-03-07
# Priority: High — these affect answer quality directly

## What Needs Fixing and Why

FAITHH answered a "what's the current phase?" query by citing "Phase 2 Complete / Phase 3 Planning"
even though scaffolding_state.json correctly says Phase 4. Root cause: the RAG system retrieved
SYSTEMS_MAP.md (large, authoritative-looking doc) and it outweighed the structured chip data.
Claude has already updated SYSTEMS_MAP.md on disk. The remaining fixes are backend-level.

---

## Fix 1: Regenerate CONTEXT.md (2 minutes)

CONTEXT.md is auto-generated and currently stale (last generated 2026-02-19).
Run the generator to rebuild it from the now-current source files.

```bash
cd ~/ai-stack
source venv/bin/activate
python3 scripts/generate_context.py
```

Verify the output contains "Phase 4" and not "Phase 2" or "Phase 3 Planning".
If generate_context.py fails, check scripts/maintenance/ for an alternative.

---

## Fix 2: Re-index updated docs into ChromaDB (10 minutes)

SYSTEMS_MAP.md and CONTEXT.md were updated on disk but ChromaDB still has stale chunks.
The stale chunks are what FAITHH actually serves. Need to replace them.

CRITICAL: Do NOT use SentenceTransformer or torch — see WSL crash rule in
.windsurf/rules/faithhprojectspecifics.md. Use ChromaDB upsert with documents only.

Create scripts/reindex_core_docs.py with this content:

```python
#!/usr/bin/env python3
"""Re-index core orientation docs that were updated today."""
import sys
import hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

DOCS_TO_REINDEX = [
    BASE_DIR / "SYSTEMS_MAP.md",
    BASE_DIR / "CONTEXT.md",
    BASE_DIR / "scaffolding_state.json",
]

CHUNK_SIZE = 1500
OVERLAP = 200

def chunk_text(text):
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            for sep in ['\n\n', '\n', '. ']:
                b = text.rfind(sep, start + OVERLAP, end)
                if b > start + OVERLAP:
                    end = b + len(sep)
                    break
        chunks.append(text[start:end])
        start = end - OVERLAP
    return chunks

def doc_id(filepath, chunk_idx):
    h = hashlib.md5(f"{filepath.name}:{chunk_idx}".encode()).hexdigest()[:8]
    return f"core_{filepath.stem[:25]}_{h}"

import chromadb
client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
col = client.get_collection("faithh_knowledge_base")

print(f"Before: {col.count()} docs")
sys.stdout.flush()

for filepath in DOCS_TO_REINDEX:
    if not filepath.exists():
        print(f"SKIP (not found): {filepath.name}")
        continue
    text = filepath.read_text(encoding='utf-8')
    chunks = chunk_text(text)
    relative = str(filepath.relative_to(BASE_DIR))
    for i, chunk in enumerate(chunks):
        col.upsert(
            ids=[doc_id(filepath, i)],
            documents=[chunk],
            metadatas=[{
                "source": relative,
                "category": "core_orientation",
                "project": "faithh",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "timestamp": datetime.now().isoformat(),
                "indexed_by": "reindex_core_docs.py"
            }]
        )
    print(f"  {filepath.name}: {len(chunks)} chunks OK")
    sys.stdout.flush()

print(f"After: {col.count()} docs")
```

Run it:
```bash
cd ~/ai-stack
source venv/bin/activate
python3 scripts/reindex_core_docs.py
```

---

## Fix 3 (Optional, harder): Add recency boost to RAG results

The structural problem is that RAG returns chunks sorted only by cosine similarity.
A stale chunk from a large doc can outrank a fresh structured chunk.

In faithh_professional_backend_fixed.py, find where collection.query() results are processed.
After getting results, multiply each distance by a recency factor:
  - chunk timestamped within 30 days: distance * 1.0 (no penalty)
  - chunk with no timestamp: distance * 1.10 (slight penalty)  
  - chunk older than 30 days: distance * 1.15 (penalized further from top)

Lower distance = more relevant in ChromaDB, so multiplying pushes stale chunks down.

This is a 30-60 min change. Do Fix 1 and Fix 2 first — they may be sufficient.

---

## Fix 4: Index new AI conversation exports

Jonathan wants to feed FAITHH conversations from other AI tools (Gemini, Grok, etc.)
to test RAG breadth.

Use the same pattern as scripts/add_harmony_docs.py:
- ChromaDB upsert with documents= array and metadatas= array, no manual embeddings
- category: "conversation", provider: "gemini" / "grok" / etc.
- No torch, no sentence_transformers

Export format will vary — JSON preferred. Parse to extract (role, content) pairs,
combine into chunks of ~1500 chars, upsert. Simple.

---

## Verification After Fix 1 + 2

```bash
./restart_backend.sh
```

Then ask FAITHH:
- "What phase is the project in?" → expect Phase 4
- "What needs planning right now?" → expect journal synthesis / FGS / production hardening
- NOT: "Phase 2", "hybrid PA detection", "Experience Journal", "UI layout"

---

## Commit

```bash
git add scripts/reindex_core_docs.py CONTEXT.md
git commit -m "Hotfix: regenerate CONTEXT.md, reindex stale orientation docs"
```
