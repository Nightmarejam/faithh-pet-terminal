#!/usr/bin/env bash
set +e
STACK_DIR="$HOME/ai-stack"

echo "━━━ Orchestrator ━━━"

# 1. Wait for vLLM (started in pane 0 by start_faithh.sh)
echo "Waiting for vLLM (up to 180s)..."
for i in $(seq 1 60); do
    curl -sf http://localhost:8000/health > /dev/null 2>&1 && echo "✅ vLLM up" && break
    printf "  [%02d/60]\r" "$i"
    sleep 3
done
curl -sf http://localhost:8000/health > /dev/null 2>&1 || { echo "❌ vLLM failed"; exec bash -i; }

# 2. Start cc_proxy
echo "Starting cc_proxy..."
fuser -k 5558/tcp 2>/dev/null
sleep 1
GROQ_API_KEY=$(grep GROQ_API_KEY "$STACK_DIR/.env" | cut -d= -f2 | tr -d '"' | tr -d "'") \
    python3 "$STACK_DIR/cc_proxy.py" >> "$STACK_DIR/cc_proxy.log" 2>&1 &
sleep 3
curl -sf http://localhost:5558/ > /dev/null 2>&1 && echo "✅ cc_proxy up" || echo "⚠️  cc_proxy slow"

# 3. Start backend
echo "Starting backend..."
bash "$STACK_DIR/restart_backend.sh" > /dev/null 2>&1 &
for i in $(seq 1 30); do
    curl -sf http://localhost:5557/health > /dev/null 2>&1 && echo "✅ Backend up" && break
    printf "   Waiting for backend... [%02d/30]\r" "$i"
    sleep 2
done

# 4. Status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "vLLM     (8000): "; curl -sf http://localhost:8000/health > /dev/null 2>&1 && echo "✅" || echo "❌"
printf "cc_proxy (5558): "; curl -sf http://localhost:5558/ > /dev/null 2>&1 && echo "✅" || echo "❌"
printf "Backend  (5557): "; curl -sf http://localhost:5557/health > /dev/null 2>&1 && echo "✅" || echo "❌"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stack ready."
exec bash -i
