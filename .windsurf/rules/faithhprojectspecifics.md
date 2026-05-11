---
trigger: always_on
---

FAITHH CANONICAL FILES:
- Backend: faithh_professional_backend_fixed.py (port 5557)
- Frontend UI: faithh_pet_v4.html (ROOT level, NOT active/frontend/)
- The active/frontend/ copy is OUTDATED - never edit it

TESTING:
- UI: http://localhost:5557/
- Backend health: curl http://localhost:5557/health
- ChromaDB: curl http://192.158.1.243:8000/api/v2/heartbeat

BEFORE FRONTEND CHANGES:
- Verify: grep -A2 "@app.route('/')" faithh_professional_backend_fixed.py

---

WSL CRASH PREVENTION (CRITICAL — READ BEFORE WRITING ANY SCRIPT):

NEVER import sentence_transformers or torch in WSL scripts.
Reason: PyTorch CUDA init against GTX 1080 Ti (sm_61) crashes WSL catastrophically.
This happens at import time, not inference time. CUDA_VISIBLE_DEVICES='' does NOT prevent it.

For ChromaDB indexing, use ONE of:
  Option A: collection.upsert() without embeddings — ChromaDB handles embedding server-side
  Option B: Route through backend HTTP API (only when backend is already running)
  Option C: Use the scripts/add_*.py pattern (proven to work — see scripts/add_harmony_docs.py)

NEVER write a script that does: from sentence_transformers import SentenceTransformer
NEVER write a script that does: import torch

Decision documented: decisions_log.json infra_002

---

SCRIPT WRITING RULES (CRITICAL — PowerShell corrupts heredocs):

NEVER write Python scripts using wsl bash -c 'cat > file.py << EOF ... EOF'
PowerShell intercepts and corrupts the heredoc — line endings and quotes break silently.
The script appears to write but hangs or fails when run because indentation is destroyed.

CORRECT ways to write script files in this environment:
  Option A: Use Windsurf's built-in file editor (new file / edit file)
  Option B: Use the faithh-filesystem MCP write tool if available
  Option C: Use Desktop Commander write_file tool

NEVER diagnose a "hanging script" without first verifying the file contents look correct.
A script that hangs after chromadb.HttpClient() is almost always a corrupted file, not a ChromaDB issue.

---

TERMINAL EXECUTION RULES (ALWAYS FOLLOW):

1. ALWAYS activate venv before running Python:
   source /home/jonat/ai-stack/venv/bin/activate && python3 ...
   NEVER use bare 'python' - use 'python3' always

2. NEVER retry a failed command more than once without stopping.
   If a command fails twice, STOP and report the error. Do not loop.

3. NEVER run background processes (&) without immediately checking they started:
   nohup python3 script.py > /tmp/script.log 2>&1 &
   sleep 2 && cat /tmp/script.log

4. AFTER COMPLETING A TASK - STOP. Do not run additional verification
   commands in a loop. Run verification ONCE, report result, then stop.

5. If a task fails, report the failure with the exact error and ask for
   guidance. Do not invent workarounds or retry with variations.

6. NEVER modify code to fix a failing test without first understanding
   whether the test or the implementation is wrong. Check the actual
   implementation before changing assertions.

---

PROCESS MANAGEMENT:

- FAITHH backend: ./restart_backend.sh (always use the script, never pkill manually)
- Dashboard server: source venv/bin/activate && nohup python3 scripts/dashboard_server.py > /tmp/dashboard.log 2>&1 &
- Monitoring daemon: source venv/bin/activate && nohup python3 scripts/monitoring_daemon.py > /tmp/monitoring.log 2>&1 &
- Verify any background process: sleep 2 && cat /tmp/<logfile>.log | head -10

---

COMMIT DISCIPLINE:
- Never commit until tests pass and the change is manually verified
- Commit message must state what was verified, not just what was changed
- Do not commit test fixes that change assertions to match wrong behavior

---

SYSTEM FINGERPRINT (AI Session Startup):

1. READ FIRST on new sessions:
   - SYSTEM_FINGERPRINT.md — System identity, capabilities, guardrails
   - fingerprint_state.json — Current health, models, open loops

2. REFRESH fingerprint when needed:
   source venv/bin/activate && python3 scripts/generate_fingerprint.py

3. FINGERPRINT provides:
   - System health (backend, ChromaDB, Ollama)
   - Active models (default: qwen25-grounded, reasoning: deepseek-r1:32b)
   - Current project focus and open loops
   - Recent decisions with rationale

4. USE fingerprint to:
   - Understand system state before making changes
   - Route queries to appropriate models
   - Respect documented guardrails
   - Continue work from previous sessions coherently
