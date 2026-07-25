---
description: Start a new work session with fingerprint refresh and compass check
---

# Session Startup Workflow

Run this workflow at the start of any work session to get oriented.

## Steps

1. Refresh the system fingerprint to get current state:
// turbo
```bash
source /home/jonat/ai-stack/venv/bin/activate && python3 /home/jonat/ai-stack/scripts/generate_fingerprint.py
```

2. Read and summarize the fingerprint state:
   - Open `fingerprint_state.json` and check:
     - `overall_status` — Is the system healthy?
     - `health.backend.status` — Is the backend running?
     - `health.chromadb.status` — Is ChromaDB accessible?
     - `health.ollama.status` — Is Ollama running?
     - `open_loops` — What's currently in progress?
     - `recent_decisions` — What was recently decided?

3. Query FAITHH compass for priorities:
// turbo
```bash
curl -s -X POST http://localhost:5557/api/chat -H "Content-Type: application/json" -d '{"message": "What should I work on next based on current project states?"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('COMPASS RESPONSE:'); print(d.get('response', 'No response')[:2000])"
```

4. Present a session summary to the user:
   - **System Health:** [healthy/degraded/unhealthy]
   - **Current Focus:** [from open_loops]
   - **Top 3 Priorities:** [from compass response]
   - **Any Blockers:** [from open_loops with blocked status]

5. Ask the user what they'd like to work on from the priorities.

## Quick Reference

- **Fingerprint location:** `fingerprint_state.json` (root)
- **Static fingerprint:** `SYSTEM_FINGERPRINT.md` (root)
- **Work tree:** `docs/roadmaps/WORK_TREE.md`
- **FAITHH UI:** http://localhost:5557/
- **Backend health:** `curl http://localhost:5557/health`

## When to Use

- Starting a new Windsurf session
- Returning after a break
- Feeling lost about what to work on
- Before making significant changes
