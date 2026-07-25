# WSL Crash Root Cause & Fix Log

**Last Updated:** 2026-03-09

---

## Root Cause (CONFIRMED)

WSL crashes were caused by **two separate SentenceTransformer instantiations** loading
without `device='cpu'`, causing PyTorch to detect and initialize CUDA on the GTX 1080 Ti
(sm_61 architecture). The RTX 3090 and GTX 1080 Ti conflict during CUDA init in WSL2.

### Evidence from backend.log

```
INFO:sentence_transformers.SentenceTransformer:Load pretrained SentenceTransformer: all-MiniLM-L6-v2
✅ SentenceTransformer imported (CPU-only mode)    ← query_embedder: CORRECT
...
INFO:sentence_transformers.SentenceTransformer:Use pytorch device_name: cuda:0   ← PA EMBEDDER: BUG
INFO:sentence_transformers.SentenceTransformer:Load pretrained SentenceTransformer: all-MiniLM-L6-v2
```

The second load (PA embedder in enhanced_chip_integration.py) had no `device` argument,
so PyTorch auto-detected cuda:0 and tried to initialize the 1080 Ti, triggering the crash.

---

## Files Fixed

### 1. backend/enhanced_chip_integration.py — `_get_pa_embedder()` (line ~110)
**Before:**
```python
_pa_embedder = SentenceTransformer('all-MiniLM-L6-v2')
```
**After:**
```python
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Block CUDA before import
_pa_embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
```

### 2. faithh_professional_backend_fixed.py — `get_query_embedder()` fallback (line ~357)
**Before:**
```python
query_embedder = _SentenceTransformer(EMBEDDING_MODEL_ID)
```
**After:**
```python
query_embedder = _SentenceTransformer(EMBEDDING_MODEL_ID, device='cpu')
```

---

## Crash Detection Setup

### What exists now
- `/home/jonat/ai-stack/logs/` — log directory with collectors.log, pulse.log, trends.log
- `/var/log/syslog` — WSL systemd journal (accessible via `journalctl`)
- `dmesg` — kernel ring buffer (survives within a WSL session, not across crashes)

### What was missing
WSL crashes terminate the entire Linux kernel process — there is NO log written at the
moment of crash. The WSL process just dies. The only forensic data available is:
- The last entry in `backend.log` before the gap
- Windows Event Viewer → Application Log (WSL entries)
- `dmesg` output after WSL restarts (shows boot messages, not crash cause)

### Crash Watchdog
`scripts/wsl_crash_watchdog.sh` — polls `/health`, logs crash events with context.
To run continuously: add to cron inside WSL or call from Windows Task Scheduler.
Cron setup: `crontab -e` → add: `*/2 * * * * /home/jonat/ai-stack/scripts/wsl_crash_watchdog.sh`

---

## How to Read a Crash

After a crash, run:
```bash
tail -50 ~/ai-stack/backend.log | grep -E "cuda|CUDA|SentenceTransformer|crash|error|ERROR"
dmesg | tail -20
cat ~/ai-stack/logs/crash_watchdog.log 2>/dev/null | tail -20
```

The gap in backend.log timestamps = the crash window.
What was logged just before the gap = the trigger.

---

## Prevention Rules (document infra_002)

1. **ALL SentenceTransformer instantiations MUST include `device='cpu'`**
2. **Set `os.environ["CUDA_VISIBLE_DEVICES"] = ""` before any sentence_transformers import**
3. **Never import torch or sentence_transformers at module level** (lazy load only)
4. **Never run large ChromaDB upserts without pre-chunking** (memory pressure)
5. **Never write Python scripts via PowerShell heredoc** (newline corruption)

---

## Pending
- Set up cron for watchdog
- Check Windows .wslconfig for memory cap (`C:\Users\jonat\.wslconfig`; current stack uses **memory=48GB** — see `runbook-to-rule-them-all/runbooks/entries/FAITHH_Runbook_v1.md`)
- Fix /etc/wsl.conf line 4 (unknown key 'boot.systemdTimeout')
