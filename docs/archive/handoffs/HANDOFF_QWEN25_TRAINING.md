# Handoff: Qwen 2.5 14B Grounding Fine-Tune

**Date:** 2026-02-17
**From:** Cascade (Thinking model)
**To:** SWE 1.5 (or next session)
**Status:** Training COMPLETE, Ollama model creation COMPLETE, Testing COMPLETE

---

## What Was Done

### 1. Training Data Generator Expanded (COMPLETE)
- **File:** `ml/grounding_finetune/generate_training_data.py`
- Expanded from 6 categories / 500 examples to **16 categories / 1914 examples**
- New categories: adversarial refusal, multi-turn grounded, partial context honesty, doc content grounded, commit detail grounded, project state grounded, confidence calibration, correction acceptance, cross-reference grounding, RAG multi-chunk
- Fixed `project_state_grounded` to handle `projects` as a dict (not list)
- Output: `ml/grounding_finetune/data/grounding_train_v2.jsonl` (17.9MB, 1914 examples)

### 2. train.py Updated for Qwen 2.5 14B (COMPLETE)
- **File:** `ml/grounding_finetune/train.py`
- Default model: `unsloth/Qwen2.5-14B-Instruct`
- Chat template auto-detection: `qwen-2.5` for Qwen, `llama-3.1` for Llama
- Batch size: 1, gradient accumulation: 8 (effective batch 8)
- Max seq len: 2048 (reduced from 4096 to fit 14B in 24GB VRAM)
- Added `--ollama-name` arg with auto-generation
- Default output: `output/qwen25-grounded`
- Default data: `data/grounding_train_v2.jsonl`

### 3. QLoRA Training (COMPLETE)
- **Model:** unsloth/Qwen2.5-14B-Instruct (14B params, 4-bit QLoRA)
- **LoRA:** rank 16, alpha 16, 68.8M trainable / 14.8B total (0.46%)
- **Training:** 1914 examples × 3 epochs = 720 steps, ~9.4s/step
- **Runtime:** 1h 52m on RTX 3090 (24GB VRAM, ~20.7GB used)
- **Final loss:** 0.0054 (started at 2.508, converged by step ~50)
- **Loss progression:** 2.508 → 0.882 → 0.108 → 0.024 → 0.008 → 0.006 → 0.005
- **Important:** Had to stop Ollama (`sudo systemctl stop ollama`) to free GPU memory before training would run. First attempt with 4096 seq len OOM'd on fused cross entropy; 2048 worked fine.

### 4. GGUF Export & Quantization (COMPLETE)
- Unsloth's built-in GGUF export hung on `sudo` (same as Llama run) — killed and did manual conversion
- Used llama.cpp `convert_hf_to_gguf.py` → f16 GGUF (28GB)
- Quantized with `llama-quantize` → q4_k_m (8.4GB)
- **Output files:**
  - `ml/grounding_finetune/output/qwen25-grounded/gguf/qwen25-grounded-f16.gguf` (28GB — can delete after Ollama model created)
  - `ml/grounding_finetune/output/qwen25-grounded/gguf/qwen25-grounded-q4_k_m.gguf` (8.4GB — this is the one to use)
  - `ml/grounding_finetune/output/qwen25-grounded/Modelfile` (ready for `ollama create`)
  - `ml/grounding_finetune/output/qwen25-grounded/lora_adapter/` (saved LoRA weights)

---

## What Remains (TODO)

### 5. Create Ollama Model (NEXT STEP)
```bash
# Start Ollama if not running
sudo systemctl start ollama

# Wait a few seconds for it to be ready
sleep 5

# Create the model
ollama create qwen25-grounded -f /home/jonat/ai-stack/ml/grounding_finetune/output/qwen25-grounded/Modelfile

# Verify it loaded
ollama list | grep qwen25
```

### 6. Clean Up Large Files
```bash
# Delete the 28GB f16 GGUF (only needed for quantization, already done)
rm /home/jonat/ai-stack/ml/grounding_finetune/output/qwen25-grounded/gguf/qwen25-grounded-f16.gguf

# Delete the merged safetensors (6 files, ~30GB total)
rm /home/jonat/ai-stack/ml/grounding_finetune/output/qwen25-grounded/gguf/model-*.safetensors

# Also can delete checkpoints if desired
rm -rf /home/jonat/ai-stack/ml/grounding_finetune/output/qwen25-grounded/checkpoint-500
rm -rf /home/jonat/ai-stack/ml/grounding_finetune/output/qwen25-grounded/checkpoint-720
```

### 7. Head-to-Head Testing (COMPLETE - FIXED)
**Results:** 
- llama31-grounded: ✅ Working correctly
- qwen25-grounded: ✅ Working correctly (FIXED)

**Issue Found & Fixed:**
- Problem: Model was producing nonsensical responses
- Root Cause: Chat template conflict - Qwen 2.5's default system prompt was overriding FAITHH prompt
- Solution: Updated Modelfile with explicit TEMPLATE directive to properly inject system prompt
- Process: Deleted and recreated Ollama model with fixed Modelfile

**Tests Performed (after fix):**
1. Recent Changes query - ✅ Correctly cites commits 50b86d9, b53c889, 719e578
2. Nonexistent file refusal - ✅ Refuses to fabricate, states file doesn't exist
3. Simple "Hello" - ✅ Responds appropriately

**Note:** Both models require the `:latest` suffix when calling via backend (e.g., `qwen25-grounded:latest`). Without it, the backend misroutes to Groq.

### 9. Configuration Update (COMPLETE)
To make qwen25-grounded the default model:
```bash
# Update .env file
MODEL_PROVIDER=ollama
DEFAULT_MODEL=qwen25-grounded:latest

# Restart backend
./restart_backend.sh
```

### 8. Git Commit (COMPLETE)
```bash
git commit -m "feat: Qwen 2.5 14B grounding fine-tune — 1914 examples, 16 categories, q4_k_m GGUF

- Expanded training data generator: 16 categories (adversarial, multi-turn, partial context, etc.)
- Updated train.py for Qwen 2.5 14B with auto chat template detection
- Training: 720 steps, 1h52m on RTX 3090, final loss 0.005
- GGUF: 8.4GB q4_k_m quantized model deployed as qwen25-grounded in Ollama
- Handoff doc for SWE 1.5 continuation"
```
Commit: `719e578`

---

## Key Technical Notes

1. **VRAM Budget:** 14B QLoRA with seq_len=2048 uses ~20.7GB on RTX 3090. Must stop Ollama first (`sudo systemctl stop ollama`). Restart after training.

2. **llama.cpp Location:** `ml/grounding_finetune/llama.cpp/` — repo exists but binaries need rebuilding after fresh clone:
   ```bash
   cd ml/grounding_finetune/llama.cpp && mkdir -p build && cd build
   cmake .. -DCMAKE_BUILD_TYPE=Release && cmake --build . --target llama-quantize -j$(nproc)
   ```

3. **Unsloth GGUF Export Bug:** Unsloth tries to `sudo apt-get` install llama.cpp, which hangs in non-interactive shells. Always use manual conversion instead:
   ```bash
   # Activate venv first
   source ml/grounding_finetune/venv/bin/activate
   # Convert HF → GGUF f16
   python ml/grounding_finetune/llama.cpp/convert_hf_to_gguf.py <merged_dir> --outfile <output.gguf> --outtype f16
   # Quantize
   ml/grounding_finetune/llama.cpp/build/bin/llama-quantize <f16.gguf> <q4_k_m.gguf> q4_k_m
   ```

4. **Training Environment:**
   ```bash
   CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 TORCHDYNAMO_DISABLE=1
   ```
   GPU 1 = RTX 3090, GPU 0 = GTX 1080 Ti (unsupported by modern PyTorch).

5. **Previous Grounded Model:** `llama31-grounded` (Llama 3.1 8B, 500 examples, q4_k_m 4.6GB) is still available in Ollama for comparison.
