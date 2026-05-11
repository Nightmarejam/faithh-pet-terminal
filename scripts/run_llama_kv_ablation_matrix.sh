#!/usr/bin/env bash
# Run KV chat ablation (f16 / q4_0 / optional q8_0) for multiple context sizes, then summarize.
#
# Default: ctx 8192 and 32768, with q8 enabled — use to compare "short slot" vs "long slot" behavior.
# If f16 @ 32K OOMs, the leg is logged and the script continues (unless KV_MATRIX_STOP_ON_ERROR=1).
#
# Example:
#   export CUDA_VISIBLE_DEVICES=0
#   KV_QUALITY_TIMEOUT=600 bash scripts/run_llama_kv_ablation_matrix.sh
#
# Optional:
#   KV_MATRIX_CONTEXTS="8192"          — only 8K
#   KV_MATRIX_CONTEXTS="32768"         — only 32K (after verifying VRAM)
#   KV_QUALITY_INCLUDE_Q8=0           — f16 + q4_0 only per ctx
#   KV_MATRIX_STOP_ON_ERROR=1         — exit on first failed leg
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="${KV_QUALITY_OUT_DIR:-$REPO_ROOT/data/kv_vectors}"
LOG="${KV_MATRIX_LOG:-$OUT_DIR/ablation_matrix.log}"
export KV_QUALITY_INCLUDE_Q8="${KV_QUALITY_INCLUDE_Q8:-1}"

CTX_LIST="${KV_MATRIX_CONTEXTS:-8192 32768}"

mkdir -p "$OUT_DIR"
{
  echo "======== matrix start $(date -Iseconds) ========"
  echo "CTX_LIST=$CTX_LIST"
  echo "KV_QUALITY_INCLUDE_Q8=$KV_QUALITY_INCLUDE_Q8"
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-}"
} | tee -a "$LOG"

failures=0
for CTX in $CTX_LIST; do
  echo "" | tee -a "$LOG"
  echo "======== matrix leg KV_QUALITY_CTX=$CTX $(date -Iseconds) ========" | tee -a "$LOG"
  KV_QUALITY_CTX="$CTX" bash "$SCRIPT_DIR/run_llama_kv_quality_ablation.sh" 2>&1 | tee -a "$LOG"
  st="${PIPESTATUS[0]}"
  if [[ "$st" -eq 0 ]]; then
    echo "OK ctx=$CTX" | tee -a "$LOG"
  else
    echo "FAIL ctx=$CTX exit=$st (see log above)" | tee -a "$LOG"
    failures=$((failures + 1))
    if [[ "${KV_MATRIX_STOP_ON_ERROR:-0}" == "1" ]]; then
      exit 1
    fi
  fi
done

echo "" | tee -a "$LOG"
echo "======== summarize $(date -Iseconds) ========" | tee -a "$LOG"
python3 "$SCRIPT_DIR/summarize_kv_ablation_runs.py" "$OUT_DIR" --markdown "$OUT_DIR/KV_ABLATION_SUMMARY.md" 2>&1 | tee -a "$LOG"
sum_st="${PIPESTATUS[0]}"
if [[ "$sum_st" -ne 0 ]]; then
  echo "summarize_kv_ablation_runs.py exited $sum_st" | tee -a "$LOG"
  failures=$((failures + 1))
fi

echo "" | tee -a "$LOG"
echo "Matrix done. failures=$failures  log=$LOG  summary=$OUT_DIR/KV_ABLATION_SUMMARY.md" | tee -a "$LOG"
if [[ "$failures" -gt 0 ]]; then
  exit 1
fi
exit 0
