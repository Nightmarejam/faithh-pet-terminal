#!/usr/bin/env bash
STACK_DIR="$HOME/ai-stack"
SESSION="faithh"
log() { echo "[$(date '+%H:%M:%S')] $*"; }

log "=== FAITHH Stack Startup ==="

# Only kill if explicitly requested
if [ "$1" = "--kill" ]; then
    log "Killing existing services..."
    pkill -9 -f "vllm serve" 2>/dev/null || true
    fuser -k 8000/tcp 2>/dev/null || true
    fuser -k 5558/tcp 2>/dev/null || true
    fuser -k 5557/tcp 2>/dev/null || true
    sleep 3
fi

tmux kill-session -t "$SESSION" 2>/dev/null || true
sleep 1

log "Building tmux session..."
tmux new-session -d -s "$SESSION" -x 220 -y 50 -n "faithh"
tmux split-window -v -t "$SESSION:0"
sleep 0.3
tmux split-window -h -t "$SESSION:0.0"
sleep 0.3
tmux split-window -h -t "$SESSION:0.2"
sleep 0.3
tmux select-layout -t "$SESSION:0" tiled

log "tmux ready ($(tmux list-panes -t $SESSION | wc -l) panes)"
log "Firing up runners..."

tmux send-keys -t "$SESSION:0.0" "source $STACK_DIR/venv/bin/activate && bash $STACK_DIR/start_vllm.sh" Enter
sleep 1
tmux send-keys -t "$SESSION:0.3" "bash $STACK_DIR/.faithh_orch.sh" Enter

log "Monitor: tmux attach -t $SESSION"
