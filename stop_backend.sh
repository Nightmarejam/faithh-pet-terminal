#!/bin/bash
# FAITHH Backend - Clean Stop Only
# Gracefully stops all backend instances

echo "🛑 Stopping FAITHH Backend..."
echo "================================================"

# Find all running instances
PIDS=$(ps aux | grep "faithh_professional_backend" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ No backend instances running"
    exit 0
fi

echo "Found instances: $PIDS"
echo ""

# Graceful shutdown (SIGTERM)
echo "Sending graceful shutdown signal (SIGTERM)..."
for PID in $PIDS; do
    echo "  Stopping PID $PID..."
    kill $PID 2>/dev/null
done

# Wait for graceful shutdown
echo "Waiting 3 seconds for graceful shutdown..."
sleep 3

# Check if still running
REMAINING=$(ps aux | grep "faithh_professional_backend" | grep -v grep | awk '{print $2}')

if [ ! -z "$REMAINING" ]; then
    echo ""
    echo "Some processes still running, forcing shutdown (SIGKILL)..."
    for PID in $REMAINING; do
        echo "  Force killing PID $PID..."
        kill -9 $PID 2>/dev/null
    done
    sleep 1
fi

# Final check
STILL_RUNNING=$(ps aux | grep "faithh_professional_backend" | grep -v grep)

if [ -z "$STILL_RUNNING" ]; then
    echo ""
    echo "✅ All backend instances stopped"
    echo "================================================"
else
    echo ""
    echo "⚠️  Warning: Some instances may still be running"
    echo "$STILL_RUNNING"
fi
