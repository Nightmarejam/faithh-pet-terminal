#!/bin/bash
# Stop FAITHH Lite gracefully

PIDFILE="/Users/macjohn/faithh/.faithh.pid"

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping FAITHH Lite (PID: $PID)..."
        kill $PID
        rm "$PIDFILE"
        echo "✅ FAITHH Lite stopped"
    else
        echo "PID file exists but process not running. Cleaning up..."
        rm "$PIDFILE"
    fi
else
    # Try to find and kill by name
    PIDS=$(pgrep -f "faithh_lite.py")
    if [ -n "$PIDS" ]; then
        echo "Stopping FAITHH Lite..."
        pkill -f "faithh_lite.py"
        echo "✅ FAITHH Lite stopped"
    else
        echo "FAITHH Lite is not running"
    fi
fi
