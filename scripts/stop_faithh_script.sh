#!/bin/bash
# scripts/stop_faithh.sh
# Gracefully stop FAITHH backend

set -e

LOG_DIR="logs"
PID_FILE="$LOG_DIR/faithh_backend.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 Stopping FAITHH Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  No PID file found${NC}"
    echo "   Backend may not be running"
    
    # Try to find it anyway
    PIDS=$(pgrep -f "faithh_professional_backend")
    if [ ! -z "$PIDS" ]; then
        echo ""
        echo "Found possible backend processes:"
        ps -p $PIDS -o pid,cmd
        read -p "Kill these processes? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill $PIDS
            echo -e "${GREEN}✓${NC} Processes killed"
        fi
    fi
    exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping backend (PID: $PID)..."
    
    # Try graceful shutdown first
    kill -TERM "$PID"
    
    # Wait up to 10 seconds
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            echo -e "${GREEN}✅ Backend stopped gracefully${NC}"
            rm "$PID_FILE"
            exit 0
        fi
        sleep 1
        echo -n "."
    done
    
    # Force kill if still running
    echo ""
    echo "Forcing shutdown..."
    kill -9 "$PID" 2>/dev/null || true
    
    if ! kill -0 "$PID" 2>/dev/null; then
        echo -e "${GREEN}✅ Backend stopped (forced)${NC}"
        rm "$PID_FILE"
    else
        echo -e "${RED}❌ Failed to stop backend${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Process not running (stale PID file)${NC}"
    rm "$PID_FILE"
fi
