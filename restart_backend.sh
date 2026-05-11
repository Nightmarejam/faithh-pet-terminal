#!/bin/bash
# FAITHH Backend - Clean Shutdown & Restart
# Gracefully stops all backend instances and restarts cleanly

echo "🛑 FAITHH Backend - Clean Shutdown & Restart"
echo "================================================"
echo ""

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$REPO_DIR/venv/bin/python"

if [ ! -x "$PY" ]; then
    echo "❌ Python not found at $PY"
    echo "   Activate or create the venv at ./venv before running this script."
    exit 1
fi

# Step 0: Kill ghost workers (gunicorn / duplicate backend) so new code always loads
echo "🧹 Step 0: Stopping gunicorn and stray faithh_professional_backend_fixed.py (pkill)..."
pkill -f "gunicorn" 2>/dev/null || true
pkill -f "faithh_professional_backend_fixed.py" 2>/dev/null || true
sleep 1

# Step 1: Find all running instances
echo "📋 Step 1: Finding running instances..."
PIDS=$(ps aux | grep "faithh_professional_backend" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "   ✅ No backend instances running"
else
    echo "   Found instances: $PIDS"
    
    # Step 2: Graceful shutdown (SIGTERM)
    echo ""
    echo "🔄 Step 2: Sending graceful shutdown signal (SIGTERM)..."
    for PID in $PIDS; do
        echo "   Stopping PID $PID..."
        kill $PID 2>/dev/null
    done
    
    # Wait for graceful shutdown
    echo "   Waiting 3 seconds for graceful shutdown..."
    sleep 3
    
    # Step 3: Check if still running
    REMAINING=$(ps aux | grep "faithh_professional_backend" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$REMAINING" ]; then
        echo ""
        echo "⚠️  Step 3: Some processes still running, forcing shutdown (SIGKILL)..."
        for PID in $REMAINING; do
            echo "   Force killing PID $PID..."
            kill -9 $PID 2>/dev/null
        done
        sleep 1
    else
        echo "   ✅ All instances stopped gracefully"
    fi
fi

# Step 4: Check port is free
echo ""
echo "🔍 Step 4: Checking port 5557..."
PORT_CHECK=$(lsof -i :5557 2>/dev/null)

if [ ! -z "$PORT_CHECK" ]; then
    echo "   ⚠️  Port 5557 still in use!"
    echo "$PORT_CHECK"
    echo ""
    echo "   Forcing port release..."
    fuser -k 5557/tcp 2>/dev/null
    sleep 2
fi

echo "   ✅ Port 5557 is free"

# Step 4b (optional): warm Ollama so first /api/chat avoids cold model load
# Enable with: OLLAMA_WARMUP=1 ./restart_backend.sh
# Override model: OLLAMA_WARMUP_MODEL=my-model:tag
if [ "${OLLAMA_WARMUP:-0}" = "1" ] || [ "${OLLAMA_WARMUP:-}" = "true" ]; then
    OLLAMA_BASE="${OLLAMA_HOST:-http://127.0.0.1:11434}"
    OLLAMA_BASE="${OLLAMA_BASE%/}"
    WARM_MODEL="${OLLAMA_WARMUP_MODEL:-qwen25-faithh-v3:latest}"
    echo ""
    echo "🔥 Step 4b: Ollama warm-up (model=${WARM_MODEL})..."
    if curl -sS -m 180 -X POST "${OLLAMA_BASE}/api/generate" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"${WARM_MODEL}\",\"prompt\":\".\",\"stream\":false,\"options\":{\"num_predict\":8}}" \
        -o /dev/null 2>/dev/null; then
        echo "   ✅ Ollama generate OK (${OLLAMA_BASE})"
    else
        echo "   ⚠️  Ollama warm-up failed or timed out (non-fatal — continuing)"
    fi
fi

# Step 5: Start fresh backend
echo ""
echo "🚀 Step 5: Starting fresh backend..."
cd "$REPO_DIR"

# Load .env so CUDA_VISIBLE_DEVICES, API keys, etc. apply to the backend process
ENV_FILE="$REPO_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    echo "📄 Loading environment from .env"
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
else
    echo "   (no .env file — copy .env.example to .env for CUDA/API keys)"
fi

# Local calibration: force Ollama-only /api/chat routing (no Groq fallbacks). Remove or set to 0 in .env to allow cloud.
export FAITHH_FORCE_LOCAL=1

# Kill any existing tmux session
tmux kill-session -t faithh 2>/dev/null

# Start in tmux session for stability (prevents WSL from killing the process)
tmux new-session -d -s faithh "cd $REPO_DIR && source venv/bin/activate && python3 faithh_professional_backend_fixed.py 2>&1 | tee backend.log"
BACKEND_PID=$(tmux list-panes -t faithh -F '#{pane_pid}' 2>/dev/null | head -1)

echo "   Backend started (PID: $BACKEND_PID)"
echo "   Logs: $REPO_DIR/backend.log"

# Step 6: Verify it's running (health-based)
# Large imports (faithh_professional_backend_fixed.py) can exceed 30s on WSL; allow override.
echo ""
echo "✅ Step 6: Verifying backend health..."
MAX_ATTEMPTS="${FAITHH_HEALTH_ATTEMPTS:-45}"
SLEEP_SECONDS="${FAITHH_HEALTH_SLEEP:-2}"
HEALTH_URL="${FAITHH_HEALTH_URL:-http://127.0.0.1:5557/health}"
ATTEMPT=1
HEALTH_OK=0
LAST_CODE=""

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    # Bounded curl: avoid hanging if port is closed or half-open
    LAST_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout 2 --max-time 8 \
        "$HEALTH_URL" 2>/dev/null || echo "000")
    if [ "$LAST_CODE" = "200" ]; then
        HEALTH_OK=1
        break
    fi
    echo "   Waiting for health... ($ATTEMPT/$MAX_ATTEMPTS) HTTP ${LAST_CODE:-?}"
    sleep "$SLEEP_SECONDS"
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $HEALTH_OK -eq 1 ]; then
    echo "   ✅ Backend responding at $HEALTH_URL"
    echo "   ✅ UI available at: http://localhost:5557"
else
    echo "   ❌ Backend failed health check (last HTTP: ${LAST_CODE:-unknown}, url: $HEALTH_URL)"
    echo "   Tip: increase wait with FAITHH_HEALTH_ATTEMPTS=60 FAITHH_HEALTH_SLEEP=2 $0"
    echo "   Last 120 lines of backend.log:"
    tail -n 120 backend.log
    exit 1
fi

# Step 6b: Service registry must not 500 (stale bytecode can break imports)
REGISTRY_URL="${FAITHH_REGISTRY_URL:-http://127.0.0.1:5557/api/workspace/registry}"
REGISTRY_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout 2 --max-time 10 \
    "$REGISTRY_URL" 2>/dev/null || echo "000")
if [ "$REGISTRY_CODE" = "500" ]; then
    echo ""
    echo "⚠️  Service registry returned HTTP 500 at $REGISTRY_URL"
    echo "   Clearing __pycache__ under repo (skipping venv/.git) and restarting backend once..."
    find "$REPO_DIR" \( -path "$REPO_DIR/venv" -o -path "$REPO_DIR/.git" \) -prune -o \
        -type d -name __pycache__ -print0 2>/dev/null | xargs -0 rm -rf
    tmux kill-session -t faithh 2>/dev/null
    sleep 2
    tmux new-session -d -s faithh "cd $REPO_DIR && source venv/bin/activate && python3 faithh_professional_backend_fixed.py 2>&1 | tee backend.log"
    echo "   Re-waiting for health after recovery..."
    ATTEMPT=1
    HEALTH_OK=0
    LAST_CODE=""
    while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
        LAST_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout 2 --max-time 8 \
            "$HEALTH_URL" 2>/dev/null || echo "000")
        if [ "$LAST_CODE" = "200" ]; then
            HEALTH_OK=1
            break
        fi
        echo "   Waiting for health... ($ATTEMPT/$MAX_ATTEMPTS) HTTP ${LAST_CODE:-?}"
        sleep "$SLEEP_SECONDS"
        ATTEMPT=$((ATTEMPT + 1))
    done
    if [ $HEALTH_OK -ne 1 ]; then
        echo "   ❌ Health check failed after registry recovery (last HTTP: ${LAST_CODE:-unknown})"
        tail -n 120 backend.log
        exit 1
    fi
    REGISTRY_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout 2 --max-time 10 \
        "$REGISTRY_URL" 2>/dev/null || echo "000")
fi
echo "   Service registry: HTTP $REGISTRY_CODE ($REGISTRY_URL)"

echo ""
echo "================================================"
echo "✅ FAITHH BACKEND READY"
echo "================================================"
echo ""
echo "To monitor:"
echo "  tail -f ~/ai-stack/backend.log"
echo "  tmux attach -t faithh  # (Ctrl+B, D to detach)"
echo ""
echo "To stop:"
echo "  ./stop_backend.sh"
echo "  tmux kill-session -t faithh"
echo ""
echo "To check status:"
echo "  curl -s http://localhost:5557/api/plc/state | python3 -m json.tool | head -80"
echo ""
echo "UI: http://localhost:5557"
echo "================================================"
