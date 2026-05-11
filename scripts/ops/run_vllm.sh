#!/usr/bin/env bash
# Tuned 2026-05-08 — qwen2.5-14b-awq on RTX 3090
# Launch: tmux new -s vllm "$PWD/scripts/ops/run_vllm.sh"
set -euo pipefail
cd "$(dirname "$0")/../.."
source venv/bin/activate
exec vllm serve /mnt/nas/models/qwen2.5-14b-awq \
  --served-model-name qwen2.5-14b-awq \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.92 \
  --max-model-len 8192 \
  --safetensors-load-strategy prefetch \
  --max-num-seqs 4 \
  --enable-chunked-prefill
