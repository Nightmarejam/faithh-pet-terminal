#!/bin/bash
# scripts/start_faithh.sh
# Production startup script for FAITHH backend

set -e

BACKEND_FILE="faithh_professional_backend_fixed.py"
BACKEND_PORT=5557
LOG_DIR="logs"
PID_FILE="$LOG_DIR/faithh_backend.pid"
LOG_FILE="$LOG_DIR/faithh_backend.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 FAITHH Professional Backend Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Backend already running (PID: $OLD_PID)${NC}"
        echo "   Stop it first with: ./scripts/stop_faithh.sh"
        exit 1
    else
        echo "Cleaning up stale PID file..."
        rm "$PID_FILE"
    fi
fi

# Pre-flight checks
echo ""
echo "🔍 Pre-flight Checks"
echo "────────────────────"

# Check Python environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Run: python3 -m venv venv"
    exit 1
fi
echo -e "${GREEN}✓${NC} Virtual environment found"

# Activate venv
source venv/bin/activate

# Check backend file exists
if [ ! -f "$BACKEND_FILE" ]; then
    echo -e "${RED}❌ Backend file not found: $BACKEND_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Backend file found"

# Check ChromaDB
if python3 -c "import chromadb; c=chromadb.HttpClient(host='servicebox.taileb8c60.ts.net',port=8000); c.heartbeat()" 2>/dev/null; then
    DOCS=$(python3 -c "import chromadb; c=chromadb.HttpClient(host='servicebox.taileb8c60.ts.net',port=8000); col=c.get_collection('faithh_knowledge_base'); print(col.count())" 2>/dev/null)
    echo -e "${GREEN}✓${NC} ChromaDB online (Gen8: $DOCS documents)"
else
    echo -e "${RED}❌ ChromaDB not available on Gen8 (servicebox.taileb8c60.ts.net:8000)${NC}"
    exit 1
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    MODELS=$(curl -s http://localhost:11434/api/tags | jq -r '.models | length' 2>/dev/null || echo "?")
    echo -e "${GREEN}✓${NC} Ollama online ($MODELS models loaded)"
else
    echo -e "${YELLOW}⚠️  Ollama not responding${NC}"
    echo "   Some features may not work"
fi

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    echo -e "${GREEN}✓${NC} GPU available: $GPU_INFO"
else
    echo -e "${YELLOW}⚠️  nvidia-smi not found${NC}"
fi

# Check Python dependencies
echo ""
echo "🔍 Checking Dependencies"
echo "────────────────────────"

REQUIRED_PACKAGES=(
    "flask"
    "flask_cors"
    "chromadb"
    "google.generativeai"
    "requests"
)

ALL_OK=true
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $pkg"
    else
        echo -e "${RED}✗${NC} $pkg (missing)"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    echo ""
    echo -e "${RED}Missing dependencies. Install with:${NC}"
    echo "  pip install flask flask-cors chromadb google-generativeai requests"
    exit 1
fi

# Start the backend
echo ""
echo "🚀 Starting Backend"
echo "────────────────────"
echo "   Port: $BACKEND_PORT"
echo "   Logs: $LOG_FILE"
echo "   PID file: $PID_FILE"
echo ""

# Start backend in background
python3 "$BACKEND_FILE" > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!

# Save PID
echo "$BACKEND_PID" > "$PID_FILE"

# Wait a moment for startup
sleep 3

# Check if it's running
if kill -0 "$BACKEND_PID" 2>/dev/null; then
    # Try to hit the status endpoint
    if curl -s http://localhost:$BACKEND_PORT/api/status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend started successfully!${NC}"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "   API: http://localhost:$BACKEND_PORT"
        echo "   Status: http://localhost:$BACKEND_PORT/api/status"
        echo "   Logs: tail -f $LOG_FILE"
        echo "   Stop: ./scripts/stop_faithh.sh"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else
        echo -e "${YELLOW}⚠️  Backend process started but not responding yet${NC}"
        echo "   Check logs: tail -f $LOG_FILE"
        echo "   PID: $BACKEND_PID"
    fi
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo ""
    echo "Last 20 lines of log:"
    tail -20 "$LOG_FILE"
    rm "$PID_FILE"
    exit 1
fi
