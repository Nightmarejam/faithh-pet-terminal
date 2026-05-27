#!/usr/bin/env bash
source ~/ai-stack/venv/bin/activate
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=0

echo "━━━ vLLM (port 8000) ━━━"

# Kill any stuck vLLM processes including ghost EngineCores
pkill -9 -f "vllm serve" 2>/dev/null
pkill -9 -f "VLLM::EngineCore" 2>/dev/null
fuser -k 8000/tcp 2>/dev/null
sleep 5

# Wait for VRAM to clear
echo "Waiting for VRAM to clear..."
for i in $(seq 1 30); do
    VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
    if [ "${VRAM_USED:-99999}" -lt 1000 ]; then
        echo "VRAM clear (${VRAM_USED}MiB) — launching..."
        break
    fi
    # Kill any remaining GPU processes
    nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | xargs -r kill -9 2>/dev/null
    echo "  VRAM: ${VRAM_USED}MiB — waiting... [${i}/30]"
    sleep 3
done

vllm serve ~/models/qwen3-coder-30b-a3b-awq \
  --served-model-name qwen3-coder-30b claude-sonnet-4-6 claude-opus-4-7 \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 65536 \
  --kv-cache-dtype fp8_e5m2 \
  --enable-prefix-caching \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder

echo "vLLM exited."
exec /bin/bash
