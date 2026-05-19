#!/usr/bin/env bash
STACK_DIR="$HOME/ai-stack"
SESSION="faithh"
echo "━━━ Orchestrator ━━━"

# 🚀 1. Fire up local vLLM on the 3090 in Pane 0
echo "Initializing local vLLM engine on RTX 3090..."
tmux send-keys -t "${SESSION}:0.0" "source $STACK_DIR/venv/bin/activate && bash $STACK_DIR/start_vllm.sh" Enter

# 🔄 2. Wait for it to claim its VRAM and bind to 8000
echo "Waiting for vLLM (up to 120s)..."
for i in $(seq 1 40); do
    curl -sf http://localhost:8000/health > /dev/null 2>&1 && echo "✅ vLLM up" && break
    printf "  [%02d/40]\r" $i
    sleep 3
done

curl -sf http://localhost:8000/health > /dev/null 2>&1 || { echo "❌ vLLM failed"; read; exit 1; }

echo "Starting cc_proxy..."
# 🛠️ Fixed the truncated line here to properly execute python3 cc_proxy.py
tmux send-keys -t "${SESSION}:0.2" "source $STACK_DIR/venv/bin/activate && echo '━━━ cc_proxy (5558) ━━━' && fuser -k 5558/tcp 2>/dev/null; sleep 1; GROQ_API_KEY=$(grep GROQ_API_KEY $STACK_DIR/.env | cut -d= -f2 | tr -d '\"\x27') python3 $STACK_DIR/cc_proxy.py 2>&1 | tee $STACK_DIR/cc_proxy.log; echo 'cc_proxy exited'; read" Enter

sleep 5
curl -sf http://localhost:5558/ > /dev/null 2>&1 && echo "✅ cc_proxy up" || echo "⚠️ cc_proxy slow"

echo "Starting backend..."
tmux send-keys -t "${SESSION}:0.1" "echo '━━━ Backend (5557) ━━━' && bash $STACK_DIR/restart_backend.sh; echo 'Backend done'; read" Enter

# 🔄 Fixed Polling Loop with Visual Feedback
BACKEND_UP=false
for i in $(seq 1 25); do
    if curl -sf http://localhost:5557/health > /dev/null 2>&1; then
        echo "✅ Backend up"
        BACKEND_UP=true
        break
    fi
    printf "   Waiting for backend... [%02d/25]\r" $i
    sleep 2
done

if [ "$BACKEND_UP" = false ]; then
    echo "⚠️ Backend validation timed out, continuing to status grid..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "vLLM     (8000): "; curl -sf http://localhost:8000/health > /dev/null 2>&1 && echo "✅" || echo "❌"
printf "cc_proxy (5558): "; curl -sf http://localhost:5558/        > /dev/null 2>&1 && echo "✅" || echo "❌"
printf "Backend  (5557): "; curl -sf http://localhost:5557/health  > /dev/null 2>&1 && echo "✅" || echo "❌"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stack ready."
# Keep the session open by spawning a persistent shell
exec /bin/bash
