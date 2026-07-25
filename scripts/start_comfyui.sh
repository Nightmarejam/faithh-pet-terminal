#!/bin/bash
# Start ComfyUI on RTX 3090
#
# GPU mapping (PyTorch ordering ≠ nvidia-smi ordering):
#   CUDA_VISIBLE_DEVICES=0 → RTX 3090 (24GB) ← USE THIS
#   CUDA_VISIBLE_DEVICES=1 → GTX 1080 Ti (11GB)
#   No env var → defaults to 1080 Ti (broken)
#
# Verified: CUDA_VISIBLE_DEVICES=0 python3 -c "import torch; print(torch.cuda.get_device_name(0))"
#   → "NVIDIA GeForce RTX 3090"

export CUDA_VISIBLE_DEVICES=0
cd /home/jonat/ComfyUI

echo "🚀 Starting ComfyUI on RTX 3090 (24GB VRAM)"
echo "   GPU: CUDA_VISIBLE_DEVICES=0 → RTX 3090"
echo "   URL: http://localhost:8188"
echo ""

python3 main.py --listen 0.0.0.0 --port 8188 "$@"
