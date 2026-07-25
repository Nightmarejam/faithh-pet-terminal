#!/usr/bin/env bash
# List large Ollama weight blobs without scanning all of /mnt/c (that can hang for hours).
# Usage: bash scripts/quick_find_ollama_blobs.sh [min_size_megabytes]

set -euo pipefail
MIN_MB="${1:-100}"
echo "Searching known Ollama blob dirs only (maxdepth 1), +${MIN_MB}M files..."
echo "---"

search_dir() {
  local d="$1"
  [[ -d "$d" ]] || return 0
  find "$d" -maxdepth 1 -type f -name 'sha256-*' -size "+${MIN_MB}M" -print 2>/dev/null || true
}

search_dir "${OLLAMA_MODELS:-}/models/blobs"
search_dir "${HOME}/.ollama/models/blobs"
search_dir "/usr/share/ollama/.ollama/models/blobs"

if [[ -d /mnt/c/Users ]]; then
  while IFS= read -r -d '' udir; do
    search_dir "${udir}/.ollama/models/blobs"
    search_dir "${udir}/AppData/Local/Ollama/models/blobs"
  done < <(find /mnt/c/Users -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
fi

echo "---"
echo "Done. For GGUF path by model name, use: python3 scripts/resolve_ollama_gguf.py <name:tag>"
