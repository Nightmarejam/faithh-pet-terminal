# FAITHH Bug Fix — Model Routing Override
**Date:** February 27, 2026
**Priority:** BLOCKING — backend non-functional for primary use case
**File:** faithh_professional_backend_fixed.py

---

## What's Happening

The auto-router correctly selects `qwen25-grounded:latest` for FAITHH
context queries. But somewhere downstream, the model is being overridden
to `deepseek-r1:32b` which is not installed. The Ollama call fails with
404, the response is missing required fields, and the UI shows an error.

**Console output showing the problem:**
```
[Auto-Router] Intent: faithh, Model: qwen25-grounded:latest, Reason: FAITHH context - grounded model (Qwen 2.5 14B)
Attempt 1 failed with status 502, retrying...
API Response: Missing required fields ["response", "model_used"]
{
  error: "Ollama returned status 404",
  model_attempted: "deepseek-r1:32b",   ← WRONG MODEL
  details: '{"error":"model 'deepseek-r1:32b' not found"}',
  provider: "ollama",
  success: false
}
```

---

## Models Actually Available (verified via Ollama API)

```
qwen25-grounded:latest   14.8B   Q4_K_M   (Qwen 2.5 - our primary model)
llama3.3:70b             70.6B   Q4_K_M   (large reasoning model)
```

`deepseek-r1:32b` is NOT installed and NOT available.

---

## Where to Look

The override is happening between the auto-router decision and the
Ollama API call. Likely candidates:

1. **DEFAULT_MODEL variable** — probably set to `deepseek-r1:32b`
   somewhere in the backend config or at the top of
   `faithh_professional_backend_fixed.py`. Search for:
   ```python
   DEFAULT_MODEL
   deepseek-r1
   ```

2. **GPU-aware model selection block** — there's a section around
   line 80 labeled `# GPU-AWARE MODEL SELECTION`. This may be
   overriding the router's decision based on detected VRAM.

3. **config.yaml** — may have a hardcoded default model that
   overrides everything.

4. **CURRENT_MODEL global** — the /api/chat handler uses
   `global CURRENT_MODEL`. If this is being set at startup to
   deepseek it will override per-request routing.

---

## The Fix

**Step 1:** Find and update DEFAULT_MODEL:
```python
# Change from:
DEFAULT_MODEL = "deepseek-r1:32b"
# To:
DEFAULT_MODEL = "qwen25-grounded:latest"
```

**Step 2:** Check GPU-aware selection block (~line 80).
If it's trying to select models based on VRAM and falling back to
deepseek, update the fallback chain to use available models:
```python
# Fallback priority should be:
# 1. qwen25-grounded:latest  (14.8B - fits in most VRAM configs)
# 2. llama3.3:70b            (70.6B - only if sufficient VRAM)
```

**Step 3:** Check config.yaml for any hardcoded model references:
```bash
grep -r "deepseek" /home/jonat/ai-stack/
```

**Step 4:** Verify the auto-router's model selection is not being
overridden after it runs. The router correctly identifies
`qwen25-grounded:latest` — that decision should be honored all the
way to the Ollama call.

---

## Secondary Issue — Auto-Indexing New Documents

The resonance gating architecture notes created today
(`harmony_ai_bridge_v1.0.0.md` updated, `resonance_gating_architecture_note_v1.0.md` created)
need to be in ChromaDB for retrieval to work.

Check whether the auto-index background thread is picking up:
```
/home/jonat/ai-stack/projects/constella-framework/harmony/docs/
```

If not, manually trigger indexing of that directory or add it
to the watched paths.

---

## Test Queries to Verify Fix

After fixing, run these through the UI and check responses:

**Test 1 — Basic retrieval (known answer):**
> What is the net operating loss for Tom Cat Sound LLC in 2024?
> Expected: ~$9,677-$10,510, mentions Reverb equipment cost basis

**Test 2 — Honest incompleteness (should NOT invent):**
> What is TC's current mailing address for the K-1 filing?
> Expected: States it doesn't have this information, not an invented address

**Test 3 — Fresh document retrieval:**
> Why would single-timescale resonance gating produce inhuman AI behavior?
> Expected: Pulls from resonance_gating_architecture_note or harmony_ai_bridge Section 9

**Test 4 — Cross-document reasoning:**
> What conditions must be true before the Floating Garden Soundworks final business plan can be written?
> Expected: Lists the 6 conditions from FGS_Master_Data_Aggregation.md Section 11

---

## Success Criteria

- [ ] `/api/chat` call with `qwen25-grounded:latest` actually hits that model
- [ ] No more 502 / 404 errors in console
- [ ] Response contains `"model_used": "qwen25-grounded:latest"`
- [ ] Test 2 returns honest incompleteness, not invented data
- [ ] Test 1 returns specific numbers from documents

---

*Logged by Claude — ready for Windsurf execution*
