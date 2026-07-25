#!/usr/bin/env bash
# Run the same five chat prompts: f16 KV vs q4_0 KV (8K ctx by default).
# Optional third leg: KV_QUALITY_INCLUDE_Q8=1 → q8_0 KV (middle ground vs f16).
# JSON includes an "environment" block when llama_kv_prompt_ablation.py runs (repro).
#
# Requires CUDA llama-server (same as run_llama_kv_cache_benchmark.sh).
# Does not call Ollama DELETE.
set -euo pipefail

export PATH="${HOME}/llama.cpp/build/bin:/usr/local/cuda/bin:${PATH:-}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

LLAMA_SERVER="${LLAMA_SERVER:-$(command -v llama-server || true)}"
if [[ -z "$LLAMA_SERVER" || ! -x "$LLAMA_SERVER" ]]; then
  LLAMA_SERVER="${HOME}/llama.cpp/build/bin/llama-server"
fi
if [[ ! -x "$LLAMA_SERVER" ]]; then
  echo "llama-server not found. Build: bash scripts/build_llama_cpp_cuda.sh" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVER="$SCRIPT_DIR/resolve_ollama_gguf.py"
# Match a name from `ollama list` / api/tags (gen5-delta is the repo’s KV-benchmark default).
OLLAMA_MODEL_REF="${OLLAMA_MODEL_REF:-qwen25-grounded-gen5-delta:latest}"

resolve_gguf() {
  python3 "$RESOLVER" "$OLLAMA_MODEL_REF"
}

if [[ -n "${GGUF_PATH:-}" && -f "$GGUF_PATH" ]]; then
  :
elif [[ -n "${GGUF_PATH:-}" && ! -f "$GGUF_PATH" ]]; then
  echo "GGUF_PATH invalid, resolving $OLLAMA_MODEL_REF..." >&2
  GGUF_PATH=$(resolve_gguf) || exit 1
else
  GGUF_PATH=$(resolve_gguf) || {
    echo "Set GGUF_PATH or fix Ollama resolver. Try: python3 $RESOLVER" >&2
    exit 1
  }
fi

export GGUF_PATH
export OLLAMA_MODEL_REF
export LLAMA_SERVER

PORT="${PORT:-8090}"
export PORT

# If 127.0.0.1:PORT accepts TCP, llama-server will fail with "couldn't bind HTTP server socket".
port_in_use() {
  python3 -c "
import socket, sys
p = int('${PORT}')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.25)
try:
    busy = s.connect_ex(('127.0.0.1', p)) == 0
finally:
    s.close()
sys.exit(0 if busy else 1)
"
}

if port_in_use; then
  echo "ERROR: 127.0.0.1:${PORT} is already in use (often another llama-server still running)." >&2
  echo "  Free the port, e.g.  pkill -f '[l]lama-server'  or stop the other process." >&2
  echo "  Or use a different port:  PORT=8091 CUDA_VISIBLE_DEVICES=0 bash scripts/run_llama_kv_quality_ablation.sh" >&2
  exit 1
fi

NGL="${LLAMA_NGL:-all}"
CTX="${KV_QUALITY_CTX:-8192}"
OUT_DIR="${KV_QUALITY_OUT_DIR:-$SCRIPT_DIR/../data/kv_vectors}"
ABLAT="$SCRIPT_DIR/llama_kv_prompt_ablation.py"
SERVER_PID=
SERVER_LOG=

stop_server() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=
}

wait_llama_ready() {
  local logfile="$1"
  local max_wait="${2:-180}"
  local i=0
  while (( i < max_wait )); do
    if [[ -f "$logfile" ]] && grep -q 'router server is listening' "$logfile" 2>/dev/null; then
      echo "ERROR: router mode (no model). Check GGUF_PATH." >&2
      return 1
    fi
    if [[ -f "$logfile" ]] && grep -q 'server is listening on' "$logfile" 2>/dev/null \
      && ! grep -q 'router server is listening' "$logfile" 2>/dev/null; then
      return 0
    fi
    if [[ -n "${SERVER_PID:-}" ]] && ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "ERROR: llama-server exited. Log:" >&2
      tail -40 "$logfile" >&2 || true
      return 1
    fi
    sleep 2
    (( i += 2 )) || true
  done
  echo "ERROR: timeout waiting for llama-server" >&2
  tail -40 "$logfile" >&2 || true
  return 1
}

run_one_kv_profile() {
  local label="$1"
  local outjson="$2"
  local cache_kv="$3"
  shift 3

  stop_server
  sleep 2
  SERVER_LOG=$(mktemp /tmp/llama-kv-quality.XXXXXX.log)
  echo "=== Starting server: $label ===" >&2
  env CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
    "$LLAMA_SERVER" \
    --model "$GGUF_PATH" \
    --port "$PORT" \
    --host 127.0.0.1 \
    -ngl "$NGL" \
    --ctx-size "$CTX" \
    "$@" >>"$SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  if ! wait_llama_ready "$SERVER_LOG" "${LLAMA_READY_TIMEOUT:-180}"; then
    rm -f "$SERVER_LOG"
    stop_server
    return 1
  fi
  sleep "${LLAMA_POST_READY_SLEEP:-5}"

  mkdir -p "$OUT_DIR"
  export KV_ABLATION_CTX="$CTX"
  export KV_ABLATION_CACHE_KV="$cache_kv"
  export KV_ABLATION_NGL="$NGL"
  python3 "$ABLAT" run \
    --base-url "http://127.0.0.1:${PORT}/v1" \
    --out "$outjson" \
    --label "$label" \
    --max-tokens "${KV_QUALITY_MAX_TOKENS:-256}" \
    --temperature 0.0 \
    --timeout "${KV_QUALITY_TIMEOUT:-300}"

  rm -f "$SERVER_LOG"
  stop_server
  sleep 3
}

trap stop_server EXIT

echo "GGUF: $GGUF_PATH" >&2
echo "CTX:  $CTX  PORT: $PORT" >&2
echo "Outputs under: $OUT_DIR" >&2

F16_OUT="$OUT_DIR/llama_kv_ablation_f16_${CTX}.json"
Q4_OUT="$OUT_DIR/llama_kv_ablation_q4_0_${CTX}.json"
Q8_OUT="$OUT_DIR/llama_kv_ablation_q8_0_${CTX}.json"

run_one_kv_profile "f16_kv_ctx${CTX}" "$F16_OUT" "f16"
run_one_kv_profile "q4_0_kv_ctx${CTX}" "$Q4_OUT" "q4_0" --cache-type-k q4_0 --cache-type-v q4_0

if [[ "${KV_QUALITY_INCLUDE_Q8:-}" == "1" ]]; then
  run_one_kv_profile "q8_0_kv_ctx${CTX}" "$Q8_OUT" "q8_0" --cache-type-k q8_0 --cache-type-v q8_0
fi

echo "" >&2
echo "=== Summary ===" >&2
echo "f16:   $F16_OUT" >&2
echo "q4_0:  $Q4_OUT" >&2
if [[ "${KV_QUALITY_INCLUDE_Q8:-}" == "1" ]]; then
  echo "q8_0:  $Q8_OUT" >&2
  echo "Multi: python3 $ABLAT compare-multi $F16_OUT $Q4_OUT $Q8_OUT" >&2
  python3 "$ABLAT" compare-multi "$F16_OUT" "$Q4_OUT" "$Q8_OUT" || true
else
  echo "Diff:  python3 $ABLAT compare $F16_OUT $Q4_OUT" >&2
  echo "(Optional third leg: KV_QUALITY_INCLUDE_Q8=1)" >&2
  python3 "$ABLAT" compare "$F16_OUT" "$Q4_OUT" || true
fi
