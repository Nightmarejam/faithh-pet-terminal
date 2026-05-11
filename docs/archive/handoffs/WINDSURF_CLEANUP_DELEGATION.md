# FAITHH Cleanup & Finalization - Windsurf Delegation

**Created:** 2026-01-19
**Status:** READY FOR WINDSURF IMPLEMENTATION

---

## 📊 Current State Summary

### Git: 54 uncommitted files
- 9 modified tracked files
- 45 new untracked files (docs, scripts, tests)

### Ollama Models: 12 total
Need to consolidate to 7 (remove redundant base models pulled during setup).

---

## 🎯 TASK 1: Finalize Model List

### KEEP (7 models):
| Model | Size | Purpose | Reason |
|-------|------|---------|--------|
| `llama31-faithh:latest` | 8.5GB | Daily chat | FAITHH persona, best all-rounder |
| `qwen3-faithh:latest` | 18GB | Deep analysis | FAITHH persona, high throughput |
| `qwen2.5:7b` | 4.7GB | Quick tasks | Fastest, no persona needed |
| `qwen2.5-coder:14b` | 9.0GB | Coding | Specialist, no persona needed |
| `deepseek-r1:32b` | 19GB | Reasoning | Opus-like, no persona needed |
| `llama31-clean:latest` | 4.9GB | Baseline testing | For A/B comparison |
| `qwen3-clean:latest` | 18GB | Baseline testing | For A/B comparison |

### DELETE (5 models - save ~42GB):
```bash
ollama rm deepseek-r1-optimized:latest    # Duplicate of deepseek-r1:32b
ollama rm qwen25-coder-optimized:latest   # Duplicate of qwen2.5-coder:14b
ollama rm qwen25-optimized:latest         # Duplicate of qwen2.5:7b
ollama rm qwen3:30b-a3b                   # Base model, have qwen3-faithh
ollama rm llama3.1:8b                     # Base model, have llama31-faithh
```

**Rationale:** The `-optimized` variants added hardware params (num_ctx, num_batch) but benchmarks showed negligible improvement. Keep clean baselines for testing, remove duplicates.

---

## 🎯 TASK 2: Update Modelfiles for Consistency

### llama31-faithh - ADD hardware optimization:
```bash
cat > /tmp/llama31-faithh-update.Modelfile << 'EOF'
FROM llama31-faithh:latest
PARAMETER num_ctx 8192
PARAMETER num_batch 512
PARAMETER num_gpu 99
EOF
ollama create llama31-faithh:latest -f /tmp/llama31-faithh-update.Modelfile
```

### qwen3-faithh - REMOVE "concise" system prompt (may hurt reasoning):
```bash
cat > /tmp/qwen3-faithh-update.Modelfile << 'EOF'
FROM qwen3:30b-a3b
PARAMETER num_ctx 8192
PARAMETER num_batch 256
PARAMETER num_gpu 99
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop <|im_end|>
PARAMETER stop <|endoftext|>
EOF
ollama create qwen3-faithh:latest -f /tmp/qwen3-faithh-update.Modelfile
```

**Note:** Removed `SYSTEM You are a helpful AI assistant. Keep responses concise and relevant.` - backend handles persona.

---

## 🎯 TASK 3: Git Cleanup & Commit

### Step 1: Add new directories
```bash
git add modelfiles/
git add scripts/benchmarks/
git add scripts/setup_ollama_env.sh
git add docs/MODEL_INVENTORY_AND_RECOMMENDATIONS.md
git add docs/WINDSURF_HANDOFF_MODEL_ROUTING.md
git add docs/BASELINE_VS_PERSONA_RESULTS.md
```

### Step 2: Add modified core files
```bash
git add faithh_pet_v4.html
git add project_states.json
git add MASTER_CONTEXT.md
git add pulse_patterns.json
```

### Step 3: Ignore temp/test files
```bash
echo "test_routing_results_*.json" >> .gitignore
echo "test_ui_routing.py" >> .gitignore
echo ".coverage" >> .gitignore
git add .gitignore
```

### Step 4: Commit
```bash
git commit -m "Session 2026-01-19: Model system optimization & smart routing

- Added smart model routing to UI (auto-select based on intent)
- Benchmarked 5 models: speed, reasoning, coding
- Created baseline models for A/B testing
- Added environment setup script for RTX 3090
- Cleaned up duplicate models (~40GB saved)
- Updated MODEL_INVENTORY with final recommendations

Key findings:
- llama31-faithh best all-rounder (3/3 reasoning + coding)
- deepseek-r1:32b best for complex reasoning
- qwen2.5:7b fastest for quick tasks
- Personas have negligible performance impact"
```

---

## 🎯 TASK 4: Update UI Model Dropdown

Current MODEL_OPTIONS in `faithh_pet_v4.html` should match final 7 models:

```javascript
const MODEL_OPTIONS = [
    // Quick
    { id: 'qwen2.5:7b', label: '⚡ Qwen2.5 (7B) - Fastest', category: 'quick' },
    
    // FAITHH Persona
    { id: 'llama31-faithh:latest', label: '🤖 Llama31 FAITHH (8B) - Daily Chat', category: 'faithh' },
    { id: 'qwen3-faithh:latest', label: '🤖 Qwen3 FAITHH (30.5B) - Deep Analysis', category: 'faithh' },
    
    // Specialists
    { id: 'qwen2.5-coder:14b', label: '💻 Qwen2.5-Coder (14B) - Code', category: 'specialist' },
    { id: 'deepseek-r1:32b', label: '🧠 DeepSeek-R1 (32B) - Reasoning', category: 'specialist' },
    
    // Auto
    { id: 'auto', label: '🔄 Auto-Select (Smart Routing)', category: 'auto' }
];
```

Remove any references to `-optimized` or `-clean` variants from UI (keep clean models for backend testing only).

---

## 🎯 TASK 5: Verify Pulse Patterns

Check `pulse_patterns.json` is tracking chip usage correctly:

```bash
# Count recent patterns
cat pulse_patterns.json | jq '.chip_sequences | length'

# Check most common chip combos
cat pulse_patterns.json | jq '[.chip_sequences[].chips] | group_by(.) | map({combo: .[0], count: length}) | sort_by(-.count) | .[0:5]'
```

Expected chips: `rag_search`, `self_awareness`, `decisions`, `scaffolding`, `rag_search_fallback`

---

## ✅ Verification Checklist

After completing all tasks:

- [ ] `ollama list` shows exactly 7 models
- [ ] `git status` shows clean working tree
- [ ] UI dropdown shows 6 options (5 models + auto)
- [ ] Backend starts without errors
- [ ] Quick test: Send "Hello" with auto-routing → should use llama31-faithh
- [ ] Quick test: Send "Write Python code" → should use qwen2.5-coder

---

## 📝 Summary for Windsurf

**Execute in order:**
1. Delete 5 redundant Ollama models
2. Update llama31-faithh and qwen3-faithh Modelfiles
3. Git add/commit with provided message
4. Update UI MODEL_OPTIONS array
5. Run verification checklist

**Time estimate:** 15-20 minutes

**If issues:** Check `docs/WINDSURF_HANDOFF_MODEL_ROUTING.md` for detailed context.
