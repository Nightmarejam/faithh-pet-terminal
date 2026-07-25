# FAITHH Grounding Fine-Tune Roadmap

> Teaching small LLMs to stop hallucinating via QLoRA fine-tuning

## Problem Statement

When FAITHH uses small local models (8B/14B/32B via Ollama), they fabricate:
- File names, feature descriptions, and metrics
- Git commit messages and decision log entries
- Descriptions of "recent work" that never happened

Prompt engineering alone only works with 70B+ models (Groq). Fine-tuning is required to teach small models the *behavior* of grounding.

## Current Status: Infrastructure Ready (2026-02-16)

### Completed
- [x] Anti-hallucination prompt engineering (personality rewrite, grounding rules)
- [x] `is_recent_changes_query` intent detection (suppresses misleading RAG)
- [x] Git log injection into every prompt (structure chip)
- [x] Training data generator (`ml/grounding_finetune/generate_training_data.py`)
- [x] QLoRA training script (`ml/grounding_finetune/train.py`)
- [x] 500 training examples generated from real project context
- [x] GPU targeting verified (RTX 3090 via `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1`)

### Next Steps
- [ ] Install Unsloth in dedicated venv (`bash ml/grounding_finetune/setup.sh`)
- [ ] Run initial QLoRA training (~1-3 hours)
- [ ] Export GGUF → load into Ollama as `llama31-grounded`
- [ ] Test with hallucination benchmark queries
- [ ] Iterate: add failure cases to training data, retrain

## Model Test Results (Pre-Fine-Tune)

| Model | Size | Provider | Follows Grounding? |
|-------|------|----------|-------------------|
| llama31-faithh | 8B | Ollama | ❌ Fabricates freely |
| qwen2.5-coder | 14B | Ollama | ❌ Invents commits |
| deepseek-r1 | 32B | Ollama | ❌ Acknowledges rules then fabricates |
| llama-3.3-70b | 70B | Groq | ✅ Follows grounding rules |

## Training Data Sources

All pulled from the real FAITHH project:
- **Git log**: 30 commits with actual messages and changed files
- **Project structure**: Live 2-level-deep file listing
- **ChromaDB**: 100 real RAG chunks from 37K+ document collection
- **State files**: decisions_log.json, project_states.json, scaffolding_state.json

## Architecture Decision

**Why QLoRA over full fine-tuning:**
- Full fine-tune of 8B needs ~64GB VRAM (impossible on RTX 3090)
- QLoRA fits in 12-16GB with comparable quality
- Unsloth gives 2x speedup + 60% less VRAM
- LoRA adapter is small (~50-100MB) and can be swapped

**Why not just use Groq 70B for everything:**
- Rate limits (100K TPD on free tier)
- Latency (network round-trip vs local inference)
- Privacy (local = no data leaves the machine)
- Cost (free tier may not scale)

## Future: Continuous Improvement Loop

```
1. User asks FAITHH a question
2. FAITHH answers (grounded or not)
3. If hallucination detected → add to training data as negative example
4. Periodically retrain with expanded dataset
5. Model improves over time
```

This is the "personal blade" approach — the model gets sharper with each interaction.

## Related Decisions
- `faithh_008`: PULSE Reflection Engine (staleness detection feeds into training data quality)
- Anti-hallucination commits: `3f9f583`, `417b71a`
