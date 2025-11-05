#!/bin/bash
# Start FAITHH with HTML UI
# All-in-one launcher for the complete system

echo "🚀 FAITHH System Launcher (HTML UI Mode)"
echo "=========================================="
echo ""

# Check venv
if [ ! -d "venv" ]; then
    echo "❌ No virtual environment found!"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check services
echo "🔍 Checking prerequisite services..."

# Check ChromaDB
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB running (port 8000)"
else
    echo "⚠️  ChromaDB not running on port 8000"
    echo "   Start with: chroma run --path ./chroma_data --port 8000"
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama running (port 11434)"
else
    echo "⚠️  Ollama not running"
fi

echo ""
echo "=========================================="
echo "Starting FAITHH Backend Services..."
echo "=========================================="

# Start Unified API in background
echo "🔧 Starting Unified API (port 5556)..."
python3 faithh_unified_api.py > logs/unified_api.log 2>&1 &
UNIFIED_PID=$!
echo "   PID: $UNIFIED_PID"
sleep 2

# Check if it started
if ps -p $UNIFIED_PID > /dev/null; then
    echo "✅ Unified API started"
else
    echo "❌ Unified API failed to start. Check logs/unified_api.log"
    exit 1
fi

# Start Backend Adapter in background
echo "🔌 Starting Backend Adapter (port 5557)..."
python3 faithh_backend_adapter.py > logs/adapter.log 2>&1 &
ADAPTER_PID=$!
echo "   PID: $ADAPTER_PID"
sleep 2

# Check if it started
if ps -p $ADAPTER_PID > /dev/null; then
    echo "✅ Backend Adapter started"
else
    echo "❌ Backend Adapter failed to start. Check logs/adapter.log"
    kill $UNIFIED_PID
    exit 1
fi

# Start HTTP server for HTML UI
echo "🌐 Starting HTML UI Server (port 8080)..."
python3 -m http.server 8080 > logs/ui_server.log 2>&1 &
UI_PID=$!
echo "   PID: $UI_PID"
sleep 1

echo ""
echo "=========================================="
echo "✅ FAITHH System Running!"
echo "=========================================="
echo ""
echo "📡 Services:"
echo "   • Unified API:      http://localhost:5556"
echo "   • Backend Adapter:  http://localhost:5557"
echo "   • HTML UI:          http://localhost:8080/rag-chat.html"
echo ""
echo "🎯 Open your browser to:"
echo "   http://localhost:8080/rag-chat.html"
echo ""
echo "📊 Status endpoints:"
echo "   • Adapter status:   http://localhost:5557/status"
echo "   • API status:       http://localhost:5556/api/status"
echo ""
echo "🛑 To stop all services, press Ctrl+C"
echo ""

# Create stop script
cat > stop_faithh.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping FAITHH services..."
pkill -f "faithh_unified_api.py"
pkill -f "faithh_backend_adapter.py"
pkill -f "http.server 8080"
echo "✅ All services stopped"
EOF
chmod +x stop_faithh.sh

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $UNIFIED_PID $ADAPTER_PID $UI_PID 2>/dev/null; exit 0' INT

echo "Press Ctrl+C to stop all services..."
wait
