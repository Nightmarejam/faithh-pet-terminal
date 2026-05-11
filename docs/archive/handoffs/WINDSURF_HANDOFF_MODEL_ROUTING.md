# WINDSURF HANDOFF: FAITHH Model System & UI Updates (COMPLETE)

**Created:** 2026-01-19
**Author:** Claude (Opus 4.5) + Jonathan
**Status:** READY FOR WINDSURF

---

## 🎯 Session Summary

This session accomplished:
1. ✅ Audited and cleaned up duplicate model files (~40GB saved)
2. ✅ Installed new models (deepseek-r1:32b, qwen2.5-coder:14b, qwen2.5:7b)
3. ✅ Created benchmark system for model comparison
4. ✅ Ran full benchmarks (speed, reasoning, coding)
5. ⏳ Partially implemented smart model routing in UI
6. ✅ Created optimized Modelfiles for RTX 3090
7. ✅ Created setup script for environment variables

---

## 📁 NEW FILES CREATED

| File | Purpose |
|------|---------|
| `modelfiles/llama31-clean.Modelfile` | Baseline Llama 3.1 8B (no persona) |
| `modelfiles/qwen3-clean.Modelfile` | Baseline Qwen3 30.5B (no persona) |
| `modelfiles/qwen25-optimized.Modelfile` | Speed-optimized Qwen2.5 7B |
| `modelfiles/qwen25-coder-optimized.Modelfile` | Optimized coder model |
| `modelfiles/deepseek-r1-optimized.Modelfile` | Reasoning-optimized DeepSeek |
| `scripts/setup_ollama_env.sh` | Quick-start environment setup |
| `scripts/benchmarks/benchmark_models.py` | Benchmark suite |
| `docs/MODEL_INVENTORY_AND_RECOMMENDATIONS.md` | Final inventory |

---

## 🔧 TASKS FOR WINDSURF

### Task 1: Set Up Optimal Ollama Environment

Run the setup script to configure optimal settings for RTX 3090 + 47GB RAM:

```bash
cd ~/ai-stack
source scripts/setup_ollama_env.sh
# Select option 4 (all of the above)
```

This will:
- Set environment variables for current session
- Add them to ~/.bashrc for persistence
- Create optimized model variants

**Or manually add to ~/.bashrc:**
```bash
# FAITHH Ollama Settings
export OLLAMA_NUM_PARALLEL=2          # 2 concurrent requests
export OLLAMA_MAX_LOADED_MODELS=2     # 2 models hot in VRAM
export OLLAMA_FLASH_ATTENTION=1       # Enable flash attention
export OLLAMA_NUM_GPU=1               # Use RTX 3090
export OLLAMA_KEEP_ALIVE=10m          # Keep models loaded
```

---

### Task 2: Create Clean Baseline Models for Testing

To test whether personas affect benchmarks, create clean versions:

```bash
cd ~/ai-stack

# Create clean Llama 3.1 (removes temperature=0.7)
ollama create llama31-clean -f modelfiles/llama31-clean.Modelfile

# Create clean Qwen3 (removes system prompt + params)
ollama create qwen3-clean -f modelfiles/qwen3-clean.Modelfile

# Create optimized versions with hardware tuning
ollama create qwen25-optimized -f modelfiles/qwen25-optimized.Modelfile
ollama create qwen25-coder-optimized -f modelfiles/qwen25-coder-optimized.Modelfile
ollama create deepseek-r1-optimized -f modelfiles/deepseek-r1-optimized.Modelfile
```

---

### Task 3: Run Baseline vs Persona Benchmark

After creating clean models, run comparison:

```bash
cd ~/ai-stack
source venv/bin/activate

# Benchmark clean vs persona versions
python scripts/benchmarks/benchmark_models.py \
  --models llama31-clean llama31-faithh:latest qwen3-clean qwen3-faithh:latest \
  --tests speed reasoning coding \
  --save
```

This will show if the FAITHH personas (temperature=0.7, system prompts) affect performance.

---

### Task 4: Fix sendMessage() Fallback Endpoint

**File:** `faithh_pet_v4.html`
**Location:** Search for `regularEndpoint` (around line 3180-3200)

**Find this pattern:**
```javascript
const fallbackResponse = await fetch(regularEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: message,
        model: currentModel,  // <-- CHANGE THIS
        use_rag: ragEnabled
    })
});
```

**Replace `model: currentModel` with `model: effectiveModel`**

---

### Task 5: Update Model Select Change Handler

**Find:** The event listener for `modelSelect`

**Ensure it handles 'auto' mode:**
```javascript
document.getElementById('modelSelect').addEventListener('change', (e) => {
    currentModel = e.target.value;
    if (currentModel === 'auto') {
        console.log('[Model] Auto-routing enabled');
    }
});
```

---

### Task 6: Add CSS for Auto-Route Info

**Add to the `<style>` section:**
```css
.auto-route-info {
    display: inline-block;
    margin-left: 10px;
    font-size: 0.75em;
}

.auto-route-info small {
    color: #888;
    font-style: italic;
}
```

---

## 📊 CURRENT BENCHMARK RESULTS

### Speed Rankings
| Model | Avg Time | Tokens/sec |
|-------|----------|------------|
| qwen2.5:7b | 1.89s | 69-101 |
| llama31-faithh | 2.91s | 55-73 |
| qwen2.5-coder:14b | 3.45s | 51-60 |
| qwen3-faithh | 3.83s | 64-99 |
| deepseek-r1:32b | 4.64s | 30-32 |

### Quality Rankings
| Test | Winner | Score |
|------|--------|-------|
| Reasoning | deepseek-r1:32b, llama31-faithh | 3/3 |
| Coding | All except deepseek-r1 | 3/3 |
| Speed | qwen2.5:7b | 1.89s |

---

## 🔍 CURRENT MODELFILE ANALYSIS

| Model | Customizations | Impact |
|-------|---------------|--------|
| **llama31-faithh** | `temperature 0.7` only | Minimal - slight randomness |
| **qwen3-faithh** | System prompt + `temp 0.7, top_p 0.9, num_ctx 4096` | May truncate reasoning |
| **qwen2.5:7b** | Default system prompt | Clean baseline |
| **qwen2.5-coder:14b** | Default system prompt | Clean baseline |
| **deepseek-r1:32b** | None | Clean baseline |

**Hypothesis to test:** The "concise" system prompt in qwen3-faithh might hurt reasoning scores.

---

## 🧪 TESTING CHECKLIST

After completing tasks:

1. [ ] Run `source scripts/setup_ollama_env.sh` (option 4)
2. [ ] Verify new models created: `ollama list`
3. [ ] Run baseline benchmark: `python scripts/benchmarks/benchmark_models.py --models llama31-clean llama31-faithh:latest --quick`
4. [ ] Open `faithh_pet_v4.html` in browser
5. [ ] Test model dropdown shows all options
6. [ ] Test auto-select mode
7. [ ] Verify auto-route info displays

---

## 💡 DESIGN DECISION: Modelfiles vs Backend

**Conclusion from analysis:**

| Setting | Where | Reason |
|---------|-------|--------|
| Hardware optimization (num_ctx, num_batch, num_gpu) | **Modelfile** | Model-specific tuning |
| Temperature, top_p | **Modelfile** | Model-specific defaults |
| FAITHH persona/identity | **Backend** | Dynamic, already in faithh_memory.json |
| System prompts | **Backend preferred** | Can change per-request |
| RAG injection | **Backend** | Already implemented |

**Action:** Keep Modelfiles minimal (hardware only), let backend handle persona.

---

## 📝 NOTES

1. **Clean models are for testing** - Compare `llama31-clean` vs `llama31-faithh` to see if temperature=0.7 matters

2. **Hardware optimizations are separate** - The `-optimized` variants have tuning for your RTX 3090, independent of persona

3. **Benchmark script accepts any model list** - Use `--models model1 model2 model3` to test specific combinations

4. **Results saved to JSON** - Check `scripts/docs/benchmark_results/` for historical data

---

**End of Handoff Document**
