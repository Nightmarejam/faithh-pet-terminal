#!/usr/bin/env bash
source ~/ai-stack/venv/bin/activate
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=0

echo "━━━ vLLM (port 8000) ━━━"
vllm serve ~/models/qwen3-coder-30b-a3b-awq \
  --served-model-name qwen3-coder-30b claude-sonnet-4-6 claude-opus-4-7 \
  --host 0.0.0.0 --port 8000 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 32768 \
  --kv-cache-dtype fp8_e5m2 \
  --enable-prefix-caching \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder

echo "vLLM exited"
