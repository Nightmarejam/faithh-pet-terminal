#!/usr/bin/env bash
# VRAM comparison: f16 vs q4_0 KV at 8K and 32K ctx using CUDA llama-server.
#
# We intentionally do NOT call Ollama DELETE: /api/delete can remove model blobs from disk and
# break GGUF paths for this script and llama-server. Free VRAM yourself (e.g. wait for keep_alive,
# avoid a concurrent `ollama run`, or briefly stop the ollama service if you need headroom).
#
# WSL2: Without CUDA_VISIBLE_DEVICES=0, ggml often reports "no CUDA-capable device".
# Router mode (no model loaded) happens when --model is missing/empty — verify GGUF_PATH.
set -euo pipefail

export PATH="${HOME}/llama.cpp/build/bin:/usr/local/cuda/bin:${PATH:-}"
# Empty export would hide the GPU; force a visible device index on WSL.
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

LLAMA_SERVER="${LLAMA_SERVER:-$(command -v llama-server || true)}"
if [[ -z "$LLAMA_SERVER" || ! -x "$LLAMA_SERVER" ]]; then
  LLAMA_SERVER="${HOME}/llama.cpp/build/bin/llama-server"
fi
if [[ ! -x "$LLAMA_SERVER" ]]; then
  echo "llama-server not found. Build first: bash scripts/build_llama_cpp_cuda.sh"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVER="$SCRIPT_DIR/resolve_ollama_gguf.py"
# Default matches docs/experiments/KV_CACHE_QUANT_BENCHMARK_20260405.md; override if needed.
OLLAMA_MODEL_REF="${OLLAMA_MODEL_REF:-qwen25-grounded-gen5-delta:latest}"

resolve_gguf() {
  python3 "$RESOLVER" "$OLLAMA_MODEL_REF"
}

if [[ -n "${GGUF_PATH:-}" && -f "$GGUF_PATH" ]]; then
  :
elif [[ -n "${GGUF_PATH:-}" && ! -f "$GGUF_PATH" ]]; then
  echo "GGUF_PATH not found on disk: $GGUF_PATH" >&2
  echo "Trying Ollama manifest resolver ($OLLAMA_MODEL_REF)..." >&2
  GGUF_PATH=$(resolve_gguf) || exit 1
else
  GGUF_PATH=$(resolve_gguf) || {
    echo "Set GGUF_PATH to your .gguf or blob, or export OLLAMA_MODELS if models are not under ~/.ollama." >&2
    echo "Check: ollama list  &&  python3 $RESOLVER" >&2
    exit 1
  }
fi
if [[ ! -s "$GGUF_PATH" ]]; then
  echo "GGUF is empty: $GGUF_PATH"
  exit 1
fi

echo "Using model: $GGUF_PATH" >&2
echo "Using llama-server: $LLAMA_SERVER" >&2
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES" >&2

export OLLAMA_MODEL_REF

vram_used() {
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' '
}

PORT="${PORT:-8090}"
export PORT

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
  echo "ERROR: 127.0.0.1:${PORT} is already in use (often another llama-server)." >&2
  echo "  Free it:  pkill -f '[l]lama-server'   or   PORT=8091 bash scripts/run_llama_kv_cache_benchmark.sh" >&2
  exit 1
fi

SERVER_PID=
SERVER_LOG=
NGL="${LLAMA_NGL:-all}"

stop_server() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=
  SERVER_LOG=
}

# Wait for single-model server (not router). Log must show "server is listening" without "router server".
wait_llama_ready() {
  local logfile="$1"
  local max_wait="${2:-180}"
  local i=0
  while (( i < max_wait )); do
    if [[ -f "$logfile" ]] && grep -q 'router server is listening' "$logfile" 2>/dev/null; then
      echo "ERROR: llama-server started in router mode (no model). Usually means --model was empty or not parsed." >&2
      echo "  GGUF_PATH=$GGUF_PATH" >&2
      echo "  Fix: set GGUF_PATH to the real blob; avoid broken shell paste merging two commands." >&2
      return 1
    fi
    if [[ -f "$logfile" ]] && grep -q 'server is listening on' "$logfile" 2>/dev/null \
      && ! grep -q 'router server is listening' "$logfile" 2>/dev/null; then
      return 0
    fi
    if [[ -n "${SERVER_PID:-}" ]] && ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "ERROR: llama-server exited early. Last log lines:" >&2
      tail -40 "$logfile" >&2 || true
      return 1
    fi
    sleep 2
    (( i += 2 )) || true
  done
  echo "ERROR: timeout waiting for llama-server (see $logfile)" >&2
  tail -40 "$logfile" >&2 || true
  return 1
}

chat_once() {
  local model_id="$1"
  python3 - "$model_id" << 'PY'
import json, sys, urllib.request
mid = sys.argv[1]
port = int(__import__("os").environ.get("PORT", "8090"))
body = {
    "model": mid,
    "messages": [{"role": "user", "content": "Say hello in one sentence."}],
    "max_tokens": 32,
}
req = urllib.request.Request(
    f"http://127.0.0.1:{port}/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    ch = (d.get("choices") or [{}])[0].get("message", {}).get("content", "")
    print(ch[:200] if ch else json.dumps(d)[:300])
except Exception as e:
    print(f"(chat request failed: {e})", file=sys.stderr)
PY
}

# Usage: run_case "label" vram_var_name -- extra llama-server args...
run_case() {
  local label="$1"
  local outvar="$2"
  shift 2
  echo "" >&2
  echo "=== $label ===" >&2
  stop_server
  sleep 2
  if [[ ! -r "$GGUF_PATH" ]]; then
    echo "ERROR: GGUF not readable (wrong path or deleted?): $GGUF_PATH" >&2
    echo "  Re-run: GGUF_PATH=\$(python3 \"$RESOLVER\" \"\$OLLAMA_MODEL_REF\")" >&2
    return 1
  fi
  local before after post
  before=$(vram_used)
  SERVER_LOG=$(mktemp /tmp/llama-kv-bench.XXXXXX.log)
  # Child must see the GPU on WSL; env duplicates export for clarity.
  env CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
    "$LLAMA_SERVER" \
    --model "$GGUF_PATH" \
    --port "$PORT" \
    --host 127.0.0.1 \
    -ngl "$NGL" \
    "$@" >>"$SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  if ! wait_llama_ready "$SERVER_LOG" "${LLAMA_READY_TIMEOUT:-180}"; then
    rm -f "$SERVER_LOG"
    stop_server
    return 1
  fi
  sleep "${LLAMA_POST_READY_SLEEP:-5}"
  after=$(vram_used)
  echo "VRAM used (MiB): before_idle=${before} after_load=${after}" >&2
  local model_id
  model_id=$(python3 -c "
import json, urllib.request, os
port = os.environ.get('PORT', '8090')
with urllib.request.urlopen(f'http://127.0.0.1:{port}/v1/models', timeout=30) as r:
    d = json.load(r)
ids = [x.get('id','') for x in d.get('data', [])]
print(ids[0] if ids else '')
" 2>/dev/null || echo "")
  if [[ -z "$model_id" ]]; then
    echo "(no model id from /v1/models; skipping chat probe)" >&2
    tail -25 "$SERVER_LOG" >&2 || true
  else
    chat_once "$model_id" >&2 || true
  fi
  post=$(vram_used)
  echo "VRAM used after inference (MiB): ${post}" >&2
  rm -f "$SERVER_LOG"
  stop_server
  sleep 3
  printf -v "$outvar" '%s' "$after"
}

BASELINE=; Q4_8K=; F16_32K=; Q4_32K=
set +e
run_case "Baseline f16 KV, 8K ctx" BASELINE --ctx-size 8192 || BASELINE="ERR"
run_case "q4_0 KV, 8K ctx" Q4_8K --ctx-size 8192 --cache-type-k q4_0 --cache-type-v q4_0 || Q4_8K="ERR"
run_case "f16 KV, 32K ctx" F16_32K --ctx-size 32768 || F16_32K="ERR"
run_case "q4_0 KV, 32K ctx" Q4_32K --ctx-size 32768 --cache-type-k q4_0 --cache-type-v q4_0 || Q4_32K="ERR"
set -e
stop_server

echo ""
echo "=== Summary (MiB used after server load) ==="
echo "f16 8K:    ${BASELINE}"
echo "q4_0 8K:   ${Q4_8K}"
echo "f16 32K:   ${F16_32K}"
echo "q4_0 32K:  ${Q4_32K}"
echo "Paste into docs/experiments/KV_CACHE_QUANT_BENCHMARK_20260405.md"
