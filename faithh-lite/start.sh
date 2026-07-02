#!/bin/bash
# Start FAITHH Lite (improved with PID tracking)

cd "$(dirname "$0")"
PIDFILE=".faithh.pid"

# Check if already running
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "FAITHH Lite already running (PID: $PID)"
        echo "Open: http://localhost:5557"
        exit 0
    fi
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors requests
else
    source venv/bin/activate
fi

# Check Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama..."
    brew services start ollama
    sleep 3
fi

# Start FAITHH in background
echo "Starting FAITHH Lite..."
nohup python faithh_lite.py > faithh.log 2>&1 &
echo $! > "$PIDFILE"

sleep 2

if ps -p $(cat "$PIDFILE") > /dev/null 2>&1; then
    echo "✅ FAITHH Lite running (PID: $(cat $PIDFILE))"
    echo "📍 Open: http://localhost:5557"
    echo "🛑 Stop: ./stop.sh"
else
    echo "❌ Failed to start. Check faithh.log"
    rm "$PIDFILE"
fi
