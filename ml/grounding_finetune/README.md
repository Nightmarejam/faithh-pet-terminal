# FAITHH Grounding Fine-Tune

QLoRA fine-tuning pipeline to teach small LLMs (8B/14B) to follow grounding rules — cite context accurately, refuse to fabricate, and reference only real files.

## Why This Exists

Prompt engineering alone only works with 70B+ models. Smaller models (8B, 14B, even 32B) ignore grounding instructions and fabricate file names, commit messages, feature descriptions, and metrics. Fine-tuning teaches the model the *behavior* of grounding rather than relying on it to follow instructions.

## Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU | RTX 3090 (24GB) | RTX 3090 |
| RAM | 32GB | 48GB |
| Disk | 20GB free | 50GB free |

**Critical:** Must target RTX 3090 (GPU 1) with:
```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1
```

## Quick Start

```bash
# 1. Set up environment (one-time)
bash setup.sh

# 2. Activate venv
source venv/bin/activate

# 3. Generate training data from real project context
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 \
  python generate_training_data.py --count 500

# 4. Train (QLoRA, ~1-3 hours on RTX 3090)
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 \
  python train.py

# 5. Load into Ollama
ollama create llama31-grounded -f output/faithh-grounded/Modelfile
```

## File Structure

```
ml/grounding_finetune/
├── README.md                  # This file
├── setup.sh                   # Venv + dependency install
├── generate_training_data.py  # Pulls real context → JSONL training data
├── train.py                   # QLoRA training with Unsloth
├── data/
│   └── grounding_train.jsonl  # Generated training examples (ShareGPT format)
└── output/
    └── faithh-grounded/       # Trained model + GGUF + Modelfile
```

## Training Data Categories

| Category | Weight | What It Teaches |
|----------|--------|-----------------|
| recent_changes_grounded | 25% | Cite git log commits accurately |
| recent_changes_refuse | 15% | Say "I don't know" when git log is missing |
| file_reference_grounded | 15% | Only reference files in the structure snapshot |
| rag_grounded | 15% | Use RAG chunks faithfully without embellishing |
| nonexistent_refusal | 15% | Refuse to describe files that don't exist |
| decision_grounded | 15% | Cite decisions_log.json entries accurately |

## Training Config

| Parameter | Value | Notes |
|-----------|-------|-------|
| Base model | `unsloth/Meta-Llama-3.1-8B-Instruct` | Optimized for Unsloth |
| Quantization | QLoRA (4-bit) | Fits in 24GB VRAM |
| LoRA rank | 16 | Good balance of quality vs speed |
| Learning rate | 2e-4 | Standard for QLoRA |
| Epochs | 3 | Sufficient for 500 examples |
| Batch size | 2 × 4 (grad accum) = 8 effective | |
| Max seq length | 4096 | Matches FAITHH context window |
| Export | GGUF q4_k_m | For Ollama deployment |

## Iterating

After initial training, test with the same hallucination queries:
1. "What was the last update we did?"
2. "Tell me about rag_processor.py" (should describe based on structure, not fabricate)
3. "What changes did we make to security?" (should refuse if no evidence)

If failures persist, add those failure cases to the training data and retrain. This is the continuous improvement loop.

## Decision Log

- **2026-02-16**: Created pipeline after testing showed 8B/14B/32B models all fail grounding via prompt engineering alone. Only Groq 70B followed grounding rules. Fine-tuning is the path to a grounded small model.
