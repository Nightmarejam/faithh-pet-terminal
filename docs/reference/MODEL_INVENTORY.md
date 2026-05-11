# FAITHH Model Inventory - Final Configuration

**Updated:** 2026-01-19
**Hardware:** RTX 3090 (24GB), GTX 1080 Ti (11GB), 47GB RAM
**Total Model Storage:** ~60GB

---

## Active Models (Ollama)

| Model | Size | Category | Speed | Reasoning | Coding | Best For |
|-------|------|----------|-------|-----------|--------|----------|
| **qwen2.5:7b** | 4.7GB | Quick | ⚡⚡⚡ 1.89s | 2/3 | 3/3 | Fast general tasks |
| **llama31-faithh:latest** | 8.5GB | FAITHH | ⚡⚡ 2.91s | **3/3** | 3/3 | Daily chat, best all-rounder |
| **qwen2.5-coder:14b** | 9.0GB | Specialist | ⚡ 3.45s | 2/3 | 3/3 | Code generation |
| **qwen3-faithh:latest** | 18GB | FAITHH | ⚡ 3.83s | 2/3 | 3/3 | Deep analysis |
| **deepseek-r1:32b** | 19GB | Reasoning | 🐢 4.64s | **3/3** | 1/3 | Complex reasoning |

---

## Benchmark Results (2026-01-19)

### Speed Test (Simple queries)
```
qwen2.5:7b            ████████████████████ 1.89s  (69-101 tok/s)
llama31-faithh        ██████████████████████████ 2.91s  (55-73 tok/s)
qwen2.5-coder:14b     ██████████████████████████████ 3.45s  (51-60 tok/s)
qwen3-faithh          ████████████████████████████████ 3.83s  (64-99 tok/s)
deepseek-r1:32b       ███████████████████████████████████ 4.64s  (30-32 tok/s)
```

### Reasoning Test (Logic puzzles, sequences, planning)
```
deepseek-r1:32b       ████ 3/3 - ONLY model to solve sequence puzzle
llama31-faithh        ████ 3/3 - Fast + accurate
qwen2.5:7b            ███  2/3
qwen2.5-coder:14b     ███  2/3
qwen3-faithh          ███  2/3
```

### Coding Test (Function generation, bug fixes, explanations)
```
qwen2.5:7b            ████ 3/3 @ 101 tok/s (FASTEST)
qwen3-faithh          ████ 3/3 @ 98 tok/s
llama31-faithh        ████ 3/3 @ 73 tok/s
qwen2.5-coder:14b     ████ 3/3 @ 59 tok/s
deepseek-r1:32b       █    1/3 (thinking tags interfere)
```

---

## Model Selection Guide

| Task Type | Recommended Model | Why |
|-----------|-------------------|-----|
| Quick questions | qwen2.5:7b | Fastest response (1.89s) |
| Daily chat | llama31-faithh | Best balance, FAITHH persona |
| Code writing | qwen2.5-coder:14b | Specialist, clean output |
| Code review | qwen2.5:7b | Fast + accurate |
| Complex reasoning | deepseek-r1:32b | Shows thinking process |
| Deep analysis | qwen3-faithh | High throughput, FAITHH persona |
| Architecture decisions | deepseek-r1:32b | Chain-of-thought |

---

## FAITHH Persona Configuration

### Current State
Both FAITHH models have **minimal personas**:

**llama31-faithh:**
- Temperature: 0.7
- No system prompt
- Uses base Llama 3.1 8B

**qwen3-faithh:**
- Temperature: 0.7
- Top-p: 0.9
- System: "You are a helpful AI assistant. Keep responses concise and relevant."
- Context: 4096 tokens

### Recommendation
Keep personas minimal in Modelfiles, inject full FAITHH personality via backend:
- `faithh_memory.json` - Self-awareness
- `project_states.json` - Project context
- `decisions_log.json` - Decision history
- RAG context - Conversation history

---

## Optimal Environment Settings

### Ollama Environment Variables
```bash
# Add to ~/.bashrc
export OLLAMA_NUM_PARALLEL=2          # 2 concurrent requests
export OLLAMA_MAX_LOADED_MODELS=2     # 2 models in VRAM
export OLLAMA_FLASH_ATTENTION=1       # Enable flash attention
export OLLAMA_NUM_GPU=1               # Use RTX 3090
```

### Recommended Model Parameters

**Speed Models (qwen2.5:7b):**
```
PARAMETER num_ctx 4096
PARAMETER num_batch 512
PARAMETER num_gpu 99
```

**Reasoning Models (deepseek-r1:32b):**
```
PARAMETER num_ctx 8192
PARAMETER num_batch 256
PARAMETER temperature 0.6
```

**FAITHH Models:**
```
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
```

---

## Storage Cleanup Summary

### Deleted (Saved ~40GB)
- WSL: `Meta-Llama-3.1-8B-Instruct-Q8_0.gguf` (duplicate)
- WSL: `Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf` (duplicate)
- X: drive: Multiple duplicate GGUF files

### Kept
- WSL: `nomic-embed-text-v1.5.Q4_K_M.gguf` (81MB, for RAG)
- WSL: `qwen2.5-7b-instruct-q8_0.gguf` (unused, could delete)

---

## Quick Commands

```bash
# List models
ollama list

# Run benchmark
cd ~/ai-stack && source venv/bin/activate
python scripts/benchmarks/benchmark_models.py --quick

# Full benchmark
python scripts/benchmarks/benchmark_models.py --tests speed reasoning coding --save

# Test specific model
ollama run qwen2.5:7b "Hello, briefly introduce yourself"

# Check model details
ollama show llama31-faithh:latest --modelfile
```

---

**Last Benchmark:** 2026-01-19 12:56:13
**Results File:** `scripts/docs/benchmark_results/benchmark_20260119_125613.json`
