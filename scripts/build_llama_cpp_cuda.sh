#!/usr/bin/env bash
# Configure and build llama.cpp with CUDA (RTX 3090 = sm_86).
# Prerequisites: nvcc on PATH (see install_cuda_toolkit_wsl2204.sh).
# Run from repo: bash scripts/build_llama_cpp_cuda.sh
set -euo pipefail

export PATH="/usr/local/cuda/bin:${PATH:-}"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"
export LD_LIBRARY_PATH="${CUDA_HOME}/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

if ! command -v nvcc >/dev/null 2>&1; then
  echo "nvcc not found. Install CUDA toolkit first:"
  echo "  sudo bash $(dirname "$0")/install_cuda_toolkit_wsl2204.sh"
  exit 1
fi

LLAMA_ROOT="${LLAMA_ROOT:-$HOME/llama.cpp}"
if [[ ! -d "$LLAMA_ROOT" ]]; then
  echo "Expected llama.cpp at $LLAMA_ROOT (set LLAMA_ROOT=... if elsewhere)"
  exit 1
fi

cd "$LLAMA_ROOT"
rm -rf build
cmake -B build \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=86 \
  -DCMAKE_BUILD_TYPE=Release

cmake -B build -L 2>/dev/null | grep -Ei 'GGML_CUDA|CUDAToolkit_NVCC' || true

cmake --build build --config Release -j"$(nproc)"

ls -lh build/bin/llama-server build/bin/llama-cli
./build/bin/llama-server --version 2>&1 | head -5

mkdir -p "$HOME/.local/bin"
ln -sf "$LLAMA_ROOT/build/bin/llama-server" "$HOME/.local/bin/llama-server"
ln -sf "$LLAMA_ROOT/build/bin/llama-cli" "$HOME/.local/bin/llama-cli"
echo "Symlinked to ~/.local/bin/llama-server and llama-cli"
echo ""
echo "WSL2: run with GPU visible, e.g. CUDA_VISIBLE_DEVICES=0 llama-server --version"
echo "      (without it, ggml may report no CUDA-capable device.)"
