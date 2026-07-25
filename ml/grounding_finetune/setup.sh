#!/usr/bin/env bash
# FAITHH Grounding Fine-Tune — Environment Setup
# Run once to create the venv and install dependencies.
# MUST use RTX 3090 (GPU 1): CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=== FAITHH Grounding Fine-Tune Setup ==="

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip

# Unsloth — fast QLoRA fine-tuning (2x speedup, 60% less VRAM)
pip install "unsloth[cu128-torch2.10] @ git+https://github.com/unslothai/unsloth.git"

# Core deps (some may already come with unsloth)
pip install datasets transformers trl peft accelerate bitsandbytes
pip install torchvision        # Required by unsloth_zoo.vision_utils
pip install unsloth_zoo        # Required companion package
pip install gguf protobuf sentencepiece  # For GGUF export
pip install chromadb          # For pulling training data from ChromaDB
pip install pyyaml            # For config

echo ""
echo "✅ Setup complete. Activate with:"
echo "   source $VENV_DIR/bin/activate"
echo ""
echo "⚠️  Always run training with:"
echo "   CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 TORCHDYNAMO_DISABLE=1 python train.py"
echo ""
echo "Note: TORCHDYNAMO_DISABLE=1 avoids nvcc permission errors in WSL2"
