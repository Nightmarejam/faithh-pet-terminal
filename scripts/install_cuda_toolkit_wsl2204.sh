#!/usr/bin/env bash
# Install NVIDIA CUDA Toolkit on Ubuntu 22.04 (WSL2). Requires sudo.
# Run: bash scripts/install_cuda_toolkit_wsl2204.sh
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Re-exec with sudo..."
  exec sudo bash "$0" "$@"
fi

DEB=/tmp/cuda-keyring.deb
wget -qO "$DEB" \
  https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
dpkg -i "$DEB"
apt-get update -y
apt-get install -y cuda-toolkit-12-8

echo ""
echo "Installed. Verify:"
/usr/local/cuda/bin/nvcc --version || true

echo ""
echo "Add to ~/.bashrc (if missing), then open a new shell:"
cat << 'SNIP'
# CUDA Toolkit
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export CUDA_HOME=/usr/local/cuda
SNIP
