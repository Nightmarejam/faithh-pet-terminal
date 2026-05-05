#!/usr/bin/env bash
# Restart FAITHH Flask backend in tmux session `faithh`.
#
# Important: this script does NOT start vLLM / OpenAI-compatible servers unless you opt in.
# `restart_backend.sh` only starts the Python API (port 5557 by default). vLLM usually listens
# on :8000 with a separate process — start it manually (tmux session `vllm`) or set VLLM_AUTOSTART=1
# plus VLLM_START_CMD in ~/ai-stack/.env (see docs/ops/LEAN_LLM_VLLM_FIRST.md).

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

ENV_FILE="$REPO_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  echo "📄 Loading $ENV_FILE"
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
else
  echo "   (no .env — copy a template and set CHROMA_*, keys, etc.)"
fi

# Flask entrypoint (override with FAITHH_MAIN in .env). Slim clones may not have faithh_professional_backend_fixed.py.
if [[ -z "${FAITHH_MAIN:-}" ]]; then
  for candidate in \
      faithh_professional_backend_fixed.py \
      backend/faithh_enhanced_backend.py \
      backend/faithh_backend_adapter.py; do
    if [[ -f "$REPO_DIR/$candidate" ]]; then
      FAITHH_MAIN=$candidate
      break
    fi
  done
fi
if [[ -z "${FAITHH_MAIN:-}" ]] || [[ ! -f "$REPO_DIR/$FAITHH_MAIN" ]]; then
  echo "error: no Flask entrypoint found — expected one of:" >&2
  echo "  faithh_professional_backend_fixed.py (full FAITHH)" >&2
  echo "  backend/faithh_enhanced_backend.py (lighter)" >&2
  echo "Set FAITHH_MAIN=relative/path/to/file.py in .env or git pull a complete tree." >&2
  exit 1
fi
echo "   Entrypoint: $FAITHH_MAIN"

if [[ ! -x "$REPO_DIR/venv/bin/python" ]]; then
  echo "error: missing $REPO_DIR/venv/bin/python — create venv: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

# Default 1 = Ollama-only route lists in backend; 0 = use configs/model_config.yaml order (vLLM / local_webui first).
: "${FAITHH_FORCE_LOCAL:=1}"
export FAITHH_FORCE_LOCAL

VLLM_MODELS_URL="${VLLM_MODELS_URL:-http://127.0.0.1:8000/v1/models}"

# --- Optional: start vLLM in a second tmux session (same host as FAITHH) ---
if [[ "${VLLM_AUTOSTART:-0}" == "1" ]]; then
  if [[ -z "${VLLM_START_CMD:-}" ]]; then
    echo "error: VLLM_AUTOSTART=1 but VLLM_START_CMD is empty — set it in .env to your full vLLM launch line." >&2
    exit 1
  fi
  VLLM_TMUX_SESSION="${VLLM_TMUX_SESSION:-vllm}"
  echo "🚀 Starting vLLM tmux session: $VLLM_TMUX_SESSION"
  tmux kill-session -t "$VLLM_TMUX_SESSION" 2>/dev/null || true
  # VLLM_START_CMD should be one shell line (no raw double-quotes inside), e.g.
  #   source venv/bin/activate && vllm serve /path/to/model --host 0.0.0.0 --port 8000
  tmux new-session -d -s "$VLLM_TMUX_SESSION" "cd \"$REPO_DIR\" && bash -c $(printf '%q' "$VLLM_START_CMD")"
  sleep "${VLLM_BOOT_SLEEP_SEC:-8}"
  if ! tmux has-session -t "$VLLM_TMUX_SESSION" 2>/dev/null; then
    echo "error: tmux session $VLLM_TMUX_SESSION was not created — check tmux / disk / permissions." >&2
    exit 1
  fi
  if ! curl -fsS -m 3 "$VLLM_MODELS_URL" >/dev/null 2>&1; then
    echo "⚠️  vLLM tmux is running but $VLLM_MODELS_URL still down (model still loading or wrong port)." >&2
    echo "    Last lines from tmux $VLLM_TMUX_SESSION:" >&2
    tmux capture-pane -t "$VLLM_TMUX_SESSION" -p -S -30 2>/dev/null | tail -20 >&2 || true
    echo "    Fix VLLM_START_CMD / --port or raise VLLM_BOOT_SLEEP_SEC; then re-run this script." >&2
  fi
fi

# --- Warn when YAML routing expects local_webui but nothing answers on :8000 ---
if [[ "$FAITHH_FORCE_LOCAL" == "0" ]]; then
  if ! curl -fsS -m 3 "$VLLM_MODELS_URL" >/dev/null 2>&1; then
    echo "⚠️  FAITHH_FORCE_LOCAL=0 (vLLM-first routes) but $VLLM_MODELS_URL is not reachable."
    echo "    Start vLLM (e.g. tmux new -s vllm '…vllm serve…') or set VLLM_AUTOSTART=1 + VLLM_START_CMD in .env."
    echo "    Continuing anyway — Flask will start; /api/chat may fail until vLLM is up."
  fi
fi

echo ""
echo "🚀 (re)starting FAITHH backend tmux session: faithh"
tmux kill-session -t faithh 2>/dev/null || true
tmux new-session -d -s faithh "cd \"$REPO_DIR\" && source venv/bin/activate && python3 \"$FAITHH_MAIN\" 2>&1 | tee -a backend.log"

echo "   Logs: $REPO_DIR/backend.log"
echo "   Attach: tmux attach -t faithh   (Ctrl+B D to detach)"

HEALTH_URL="${FAITHH_HEALTH_URL:-http://127.0.0.1:${BACKEND_PORT:-5557}/health}"
MAX_ATTEMPTS="${FAITHH_HEALTH_ATTEMPTS:-45}"
SLEEP_SECONDS="${FAITHH_HEALTH_SLEEP:-2}"
echo ""
echo "✅ Waiting for HTTP $HEALTH_URL …"
ATTEMPT=1
while [[ $ATTEMPT -le $MAX_ATTEMPTS ]]; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 --max-time 8 "$HEALTH_URL" 2>/dev/null || echo 000)"
  if [[ "$code" == "200" ]]; then
    echo "   Health OK (HTTP $code)"
    exit 0
  fi
  echo "   attempt $ATTEMPT/$MAX_ATTEMPTS HTTP=$code — sleeping ${SLEEP_SECONDS}s"
  sleep "$SLEEP_SECONDS"
  ATTEMPT=$((ATTEMPT + 1))
done

echo "error: health check did not return 200: $HEALTH_URL" >&2
exit 1
