# Handoff: Database Audit + Documentation Update

**Session date:** 2026-03-25  
**From:** Claude (architecture/design)  
**To:** Windsurf SWE-1.5  
**Repo:** `/home/jonat/ai-stack`

---

## Context

The FAITHH system has 36,700+ documents in ChromaDB but metadata quality is unknown. RAG retrieval works semantically but structured filtering (by domain, project, date, quality) is unreliable because documents were indexed without consistent metadata. Before any new data ingestion, we need to know what we actually have.

Additionally, MASTER_CONTEXT.md and related docs are stale — they do not reflect months of work including the full ALIFE experiment series, Google Search integration, Groq model updates, or security changes.

**Stop after each task and confirm before starting the next. Do not chain tasks.**

---

## Task 1 — ChromaDB Metadata Audit

**Goal:** Understand what metadata fields currently exist across the knowledge base.

Create `scripts/maintenance/audit_chroma_metadata.py`:

```python
#!/usr/bin/env python3
"""
ChromaDB metadata audit — samples documents and reports metadata coverage.
Usage: python scripts/maintenance/audit_chroma_metadata.py
"""
import sys
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_URL = os.getenv("CHROMA_URL", "http://servicebox.taileb8c60.ts.net:8000")
COLLECTION_NAME = "faithh_knowledge_base"
SAMPLE_SIZE = 200

def audit():
    client = chromadb.HttpClient(host=CHROMA_URL.replace("http://", "").split(":")[0],
                                  port=int(CHROMA_URL.split(":")[-1]))
    collection = client.get_collection(COLLECTION_NAME)
    total = collection.count()
    print(f"\n=== ChromaDB Metadata Audit ===")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Total documents: {total}")
    print(f"Sample size: {SAMPLE_SIZE}\n")

    # Get a random sample
    all_ids = collection.get(limit=total, include=[])["ids"]
    sample_ids = random.sample(all_ids, min(SAMPLE_SIZE, len(all_ids)))
    results = collection.get(ids=sample_ids, include=["metadatas", "documents"])

    # Analyze metadata fields
    field_counts = Counter()
    field_values = defaultdict(Counter)
    missing_fields = []
    doc_previews = []

    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
        if meta:
            for key, val in meta.items():
                field_counts[key] += 1
                if isinstance(val, str):
                    field_values[key][val[:50]] += 1
        else:
            missing_fields.append(results["ids"][i])

        if i < 10:
            doc_previews.append({
                "id": results["ids"][i],
                "preview": (doc or "")[:80],
                "metadata": meta or {}
            })

    # Report
    print("--- Field Coverage ---")
    for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
        pct = (count / SAMPLE_SIZE) * 100
        print(f"  {field:<30} {count:>4}/{SAMPLE_SIZE} ({pct:.0f}%)")

    print(f"\n--- Documents with NO metadata: {len(missing_fields)} ({len(missing_fields)/SAMPLE_SIZE*100:.0f}%) ---")

    print("\n--- Top values per field (top 5) ---")
    priority_fields = ["source_type", "domain", "project", "content_type", 
                       "quality_score", "privacy_level", "access_tier"]
    for field in priority_fields:
        if field in field_values:
            print(f"\n  {field}:")
            for val, cnt in field_values[field].most_common(5):
                print(f"    '{val}' — {cnt}x")
        else:
            print(f"\n  {field}: NOT PRESENT IN SAMPLE")

    print("\n--- 10 Document Previews ---")
    for p in doc_previews:
        print(f"\n  ID: {p['id'][:40]}...")
        print(f"  Content: {p['preview']}")
        print(f"  Metadata fields: {list(p['metadata'].keys()) or 'NONE'}")

    # Summary
    has_source_type = field_counts.get("source_type", 0)
    has_domain = field_counts.get("domain", 0)
    has_quality = field_counts.get("quality_score", 0)
    has_created = field_counts.get("created_at", 0)

    print("\n=== Summary ===")
    print(f"Core metadata coverage:")
    print(f"  source_type:   {has_source_type/SAMPLE_SIZE*100:.0f}%")
    print(f"  domain:        {has_domain/SAMPLE_SIZE*100:.0f}%")
    print(f"  quality_score: {has_quality/SAMPLE_SIZE*100:.0f}%")
    print(f"  created_at:    {has_created/SAMPLE_SIZE*100:.0f}%")

    if has_source_type < SAMPLE_SIZE * 0.5:
        print("\n⚠️  METADATA MIGRATION NEEDED: Less than 50% of documents have source_type")
    else:
        print("\n✅ Metadata coverage adequate for structured retrieval")

    # Save report
    report = {
        "total_documents": total,
        "sample_size": SAMPLE_SIZE,
        "field_coverage": {k: v/SAMPLE_SIZE for k, v in field_counts.items()},
        "documents_without_metadata": len(missing_fields),
        "needs_migration": has_source_type < SAMPLE_SIZE * 0.5
    }
    with open("logs/chroma_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to logs/chroma_audit_report.json")

if __name__ == "__main__":
    audit()
```

Run it:
```bash
cd /home/jonat/ai-stack
source venv/bin/activate
python scripts/maintenance/audit_chroma_metadata.py
```

**Report:** paste the full console output. Stop here.

---

## Task 2 — Fix qwen25-grounded System Prompt (RAG Context)

**Goal:** The model currently ignores retrieved RAG documents. Fix the system prompt so it synthesizes from retrieved context.

**File:** `faithh_professional_backend_fixed.py`

Find the system prompt construction — look for where the Ollama/qwen25-grounded prompt is built. It currently instructs the model to use project structure and git log. Change it so that:

1. When RAG context is present in the request, the system prompt says:

```
You are FAITHH, Jonathan's personal AI assistant. You have access to retrieved context from the knowledge base shown below. Use this context to answer the question. Cite specific details from the context. If the context is insufficient, say so clearly.
```

2. When no RAG context is present, fall back to the current project-aware behavior.

The condition to check: if the `context` parameter passed to the chat endpoint is non-empty, use the RAG-grounded prompt. Otherwise use the existing project-aware prompt.

**Verify** by sending a test message that should retrieve ALife experiment data:
```bash
curl -s http://localhost:5557/api/chat -X POST \
  -H 'Content-Type: application/json' \
  -d @- << 'EOF'
{"message": "What were the key findings of Experiment 3 in the ALIFE project?", "model": "qwen25-grounded:latest"}
EOF
```

Report the response. If it mentions negative anticipation gaps, Red Queen dynamics, or memory emergence — RAG is working. If it gives generic AI answers — report that and stop.

---

## Task 3 — Update MASTER_CONTEXT.md

**Goal:** Bring the main context file up to date with current system state.

Read the current `MASTER_CONTEXT.md`. Update these sections:

**Section: RAG System Status** — update to reflect:
- Total chunks: 36,700+ (as of March 2026)
- Conversations: 285+ indexed
- Note: alife_lineage collection exists separately on Gen8 with ALIFE experiment data

**Section: Supported LLM Providers** — update to reflect current model list:
```
1. Groq — llama-3.3-70b-versatile (default), llama-3.1-8b-instant, openai/gpt-oss-120b
2. Ollama — qwen25-grounded:latest (primary local), deepseek-r1:32b (preserved, not routed)
3. Gemini — gemini-2.0-flash
4. Anthropic — claude-3-haiku (API, $4 budget reserve)
```

**Section: Active Projects** — add ALIFE project entry:
```
### 4. ALIFE (Artificial Life Simulation)
**Path:** `projects/alife/`
**Status:** Experiment 3 complete (FULL_SUCCESS), Experiment 4 in progress
**Key result:** Anticipatory behavior confirmed — agents evolved predictive shield 
activation before threat detection (negative anticipation gap). Red Queen dynamics 
observed across 200,000 ticks.
**ChromaDB:** alife_lineage collection on Gen8, 50,000+ documents
**Next:** Experiment 4 (harmonic interference, Wave 2 arrival bug pending)
```

**Section: Services** — add Google Search:
```
Google Custom Search:
  Status: configured
  Engine ID: 430369bf618924d21
  Endpoint: /api/search
  Rate limit: 100 queries/day
```

After editing, run:
```bash
git add MASTER_CONTEXT.md
git commit -m "docs: update MASTER_CONTEXT.md with current system state (March 2026)"
```

Report commit hash and stop.

---

## Task 4 — Update project_states.json

**Goal:** Add ALIFE project to the machine-readable state file.

In `project_states.json`, under `projects`, add:

```json
"alife": {
  "name": "ALIFE (Artificial Life Simulation)",
  "category": "Research / AI development",
  "status": "active",
  "phase": "Experiment 4 in progress",
  "phase_status": "debugging",
  "summary": "Evolutionary ALife simulation running on Python (Gen8 target). Agents evolve under environmental pressure. Experiment 3 confirmed anticipatory behavior emergence (negative anticipation gap). Red Queen dynamics documented across 200K ticks. Experiment 4 adds harmonic dual-wave interference.",
  "location": "projects/alife/",
  "key_findings": [
    "Experiment 0: stable population economics confirmed",
    "Experiment 1: Shield trait fixation under lethal predator pressure",
    "Experiment 2: Disruption strategy dominates under dual pressure (Stripe Test)",
    "Experiment 3: FULL_SUCCESS — anticipatory behavior emerged at tick 402, spread through population, Red Queen dynamics observed",
    "Experiment 4: Harmonic interference in progress — Wave 2 arrival recording bug pending fix"
  ],
  "infrastructure": {
    "simulation": "Python, projects/alife/",
    "observer": "faithh_observer.py → ChromaDB alife_lineage collection",
    "chroma_collection": "alife_lineage",
    "chroma_documents": "50000+",
    "next_phase": "Port to TempleOS QEMU on Gen8 after Experiment 5"
  },
  "next_steps": [
    "Fix Wave 2 arrival recording in world.py (PROC_BEAT bug)",
    "Run Experiment 4 full 200K tick run",
    "Design Experiment 5 (interference zone with Fibonacci frequency ratios)",
    "Build training pipeline from alife_lineage ChromaDB data",
    "Port simulation to Gen8 QEMU for Phase 2"
  ]
}
```

Update `meta.generated_at` to today's date.

Run:
```bash
git add project_states.json
git commit -m "docs: add ALIFE project to project_states.json"
```

Report commit hash and stop.

---

## Task 5 — Create Documentation Update Protocol

**Goal:** Establish a lightweight habit, not a heavy process.

Create `docs/UPDATE_PROTOCOL.md` (or update if it exists) with:

```markdown
# Documentation Update Protocol

## The Rule
At the end of any session that produces a meaningful result, update ONE document.
Not a sprint. Not a ceremony. One file, committed.

## What Counts as "Meaningful Result"
- Experiment completed or failed with findings
- New service deployed or configured
- Bug fixed that changes system behavior  
- New model or provider added
- Architecture decision made

## Which Document to Update
| Result type | Document to update |
|---|---|
| ALIFE experiment | project_states.json + alife section |
| Infrastructure change | MASTER_CONTEXT.md services section |
| New provider/model | MASTER_CONTEXT.md providers section |
| Business decision | projects/tomcat-sound/ relevant doc |
| Architecture decision | decisions_log.json |
| Major session summary | docs/session-reports/ |

## Minimum Viable Update
A one-line entry in the right section is better than no update.
Don't let perfect be the enemy of done.

## Stale Document Detection
PULSE runs staleness checks. Any document not updated in 30+ days 
gets flagged. The flag is informational, not blocking.
```

Run:
```bash
git add docs/UPDATE_PROTOCOL.md
git commit -m "docs: add lightweight documentation update protocol"
```

Report commit hash and stop. Do not begin any other work.

---

## Success Criteria

| Task | Done when |
|---|---|
| Task 1 | Audit script runs, report printed and saved to logs/ |
| Task 2 | Test query returns ALife-specific answer, not generic |
| Task 3 | MASTER_CONTEXT.md committed with updated sections |
| Task 4 | project_states.json committed with ALIFE entry |
| Task 5 | UPDATE_PROTOCOL.md committed |

**Do not start Task 2 until Task 1 results are reported.**  
**Do not start Task 3 until Task 2 result is confirmed.**  
**Tasks 3, 4, 5 can run in sequence without human review between them.**
