#!/bin/bash
# FAITHH Backend - Stop script (tmux session used by restart_backend.sh)
# restart_backend.sh uses session "faithh"; older docs used "faithh-backend".

echo "🛑 Stopping FAITHH Backend..."

SESSION_NAME=""
if tmux has-session -t faithh 2>/dev/null; then
    SESSION_NAME="faithh"
elif tmux has-session -t faithh-backend 2>/dev/null; then
    SESSION_NAME="faithh-backend"
fi

if [ -z "$SESSION_NAME" ]; then
    echo "❌ No tmux session 'faithh' or 'faithh-backend'"
    echo "📝 Sessions: tmux list-sessions"
    echo "   Or stop by PID: pkill -f faithh_professional_backend_fixed.py"
    exit 1
fi

echo "🔧 Stopping tmux session: $SESSION_NAME"

tmux send-keys -t "$SESSION_NAME" C-c 2>/dev/null
sleep 2

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "⚠️ Force killing tmux session..."
    tmux kill-session -t "$SESSION_NAME"
fi

echo "✅ Backend stopped successfully"
echo "📊 Session status:"
tmux list-sessions