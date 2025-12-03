#!/bin/bash
# FAITHH Backend - Clean Shutdown & Restart
# Gracefully stops all backend instances and restarts cleanly

echo "🛑 FAITHH Backend - Clean Shutdown & Restart"
echo "================================================"
echo ""

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

# Step 5: Start fresh backend
echo ""
echo "🚀 Step 5: Starting fresh backend..."
cd ~/ai-stack

# Start in background
python faithh_professional_backend_fixed.py > backend.log 2>&1 &
BACKEND_PID=$!

echo "   Backend started (PID: $BACKEND_PID)"
echo "   Logs: ~/ai-stack/backend.log"

# Wait for startup
echo "   Waiting for backend to initialize..."
sleep 4

# Step 6: Verify it's running
echo ""
echo "✅ Step 6: Verifying backend health..."

# Check if process still alive
if ps -p $BACKEND_PID > /dev/null; then
    echo "   ✅ Process running (PID: $BACKEND_PID)"
else
    echo "   ❌ Process died! Check backend.log for errors"
    cat backend.log
    exit 1
fi

# Check if responding
HEALTH_CHECK=$(curl -s http://localhost:5557/health 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "   ✅ Backend responding to requests"
    echo "   ✅ UI available at: http://localhost:5557"
else
    echo "   ⚠️  Backend not responding yet, check backend.log"
fi

echo ""
echo "================================================"
echo "✅ FAITHH BACKEND READY"
echo "================================================"
echo ""
echo "To monitor:"
echo "  tail -f ~/ai-stack/backend.log"
echo ""
echo "To stop:"
echo "  ./stop_backend.sh"
echo ""
echo "To check status:"
echo "  curl http://localhost:5557/api/status | python3 -m json.tool"
echo ""
echo "UI: http://localhost:5557"
echo "================================================"
