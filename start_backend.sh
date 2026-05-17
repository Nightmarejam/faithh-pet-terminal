#!/bin/bash
# FAITHH Backend v2.0 - Start Script (Fixed Version)
# Uses tmux for stable background execution with fixed async issues

SESSION_NAME="faithh-backend"
BACKEND_SCRIPT="faithh_professional_backend_fixed.py"

echo "🚀 Starting FAITHH Backend v2.0 (Fixed)..."

# Check if session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "✅ Backend already running in tmux session: $SESSION_NAME"
    echo "📝 Attach with: tmux attach -t $SESSION_NAME"
    echo "📝 Stop with: ./stop_backend.sh"
    echo ""
    echo "📊 Backend Status:"
    curl -s http://localhost:5557/api/status | python3 -m json.tool | head -10
    exit 0
fi

echo "🔧 Starting backend in new tmux session..."

# Change to backend directory
cd /home/jonat/ai-stack

# Activate virtual environment
source venv/bin/activate

# Start backend in tmux session
tmux new-session -d -s $SESSION_NAME python3 $BACKEND_SCRIPT

echo "✅ Backend started in tmux session: $SESSION_NAME"
echo "📝 Attach with: tmux attach -t $SESSION_NAME"
echo "📝 Stop with: ./stop_backend.sh"
echo "📊 Check status: curl -s http://localhost:5557/api/status"

# Wait a moment for startup
sleep 3

# Check if backend is responding
if curl -s http://localhost:5557/api/status > /dev/null 2>&1; then
    echo "✅ Backend is responding to requests"
else
    echo "❌ Backend is not responding - check logs with: tail -f /tmp/backend_debug.log"
fi