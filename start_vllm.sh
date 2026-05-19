#!/usr/bin/env bash
pkill -f "vllm serve" 2>/dev/null
sleep 2
source ~/ai-stack/venv/bin/activate
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=0
vllm serve ~/models/qwen3-coder-30b-a3b-awq \
  --served-model-name qwen3-coder-30b claude-sonnet-4-6 claude-opus-4-7 \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.92 \
  --max-model-len 49152 \
  --kv-cache-dtype fp8_e5m2 \
  --enable-prefix-caching \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
echo "vLLM starting on port 8000 (qwen3-coder-30b-a3b-awq)..."
