#!/bin/bash

################################################################################
# FAITHH Project - Start All Services
# Created: $(date +%Y-%m-%d)
# Purpose: Start backend and check service health
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 FAITHH Project - Service Startup"
echo "===================================="
echo ""

################################################################################
# Check if services are already running
################################################################################
echo "🔍 Checking for running services..."
echo ""

# Check backend
if curl -s http://localhost:5557/health > /dev/null 2>&1; then
    echo "✅ FAITHH Backend is already running on port 5557"
    BACKEND_RUNNING=true
else
    echo "⭕ FAITHH Backend is not running"
    BACKEND_RUNNING=false
fi

# Check Ollama
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is already running on port 11434"
    OLLAMA_RUNNING=true
else
    echo "⭕ Ollama is not running"
    OLLAMA_RUNNING=false
fi

echo ""

################################################################################
# Start Backend if not running
################################################################################
if [ "$BACKEND_RUNNING" = false ]; then
    echo "🎯 Starting FAITHH Backend..."

    cd "$PROJECT_ROOT"

    # Check if venv exists
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "  ✓ Activated virtual environment"
    else
        echo "  ⚠️ Warning: No virtual environment found"
    fi

    # Check if .env exists
    if [ -f ".env" ]; then
        echo "  ✓ Found .env file"
    else
        echo "  ⚠️ Warning: No .env file found - backend may not start properly"
    fi

    # Start backend in background
    nohup python faithh_professional_backend_fixed.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "  ✓ Started backend (PID: $BACKEND_PID)"
    echo "$BACKEND_PID" > .backend.pid

    # Wait for backend to start
    echo "  ⏳ Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5557/health > /dev/null 2>&1; then
            echo "  ✅ Backend is healthy and responding!"
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""

    # Check if backend started successfully
    if curl -s http://localhost:5557/health > /dev/null 2>&1; then
        echo "✅ FAITHH Backend started successfully on port 5557"
    else
        echo "❌ Failed to start backend - check logs/backend.log"
        tail -20 logs/backend.log
        exit 1
    fi
else
    echo "✅ FAITHH Backend already running - skipping startup"
fi

echo ""

################################################################################
# Check Ollama
################################################################################
if [ "$OLLAMA_RUNNING" = false ]; then
    echo "📝 Ollama is not running"
    echo "   To start Ollama manually, run: ollama serve"
    echo "   Or if using systemd: sudo systemctl start ollama"
    echo ""
else
    echo "✅ Ollama is running"

    # List available models
    echo "   Available models:"
    ollama list 2>/dev/null | grep -v "^NAME" | awk '{print "     - " $1}' || echo "     (could not list models)"
    echo ""
fi

################################################################################
# Service Status Summary
################################################################################
echo "===================================="
echo "📊 Service Status Summary"
echo "===================================="
echo ""

# Backend status
if curl -s http://localhost:5557/health > /dev/null 2>&1; then
    BACKEND_STATUS=$(curl -s http://localhost:5557/api/status)
    echo "✅ FAITHH Backend: RUNNING"
    echo "   URL: http://localhost:5557"
    echo "   Health: http://localhost:5557/health"
    echo "   Status: http://localhost:5557/api/status"
    echo ""
else
    echo "❌ FAITHH Backend: NOT RUNNING"
    echo ""
fi

# Ollama status
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama: RUNNING"
    echo "   URL: http://localhost:11434"
    echo ""
else
    echo "❌ Ollama: NOT RUNNING"
    echo "   Start with: ollama serve"
    echo ""
fi

# ComfyUI status (check but don't start automatically)
if curl -s http://localhost:8188 > /dev/null 2>&1; then
    echo "✅ ComfyUI: RUNNING"
    echo "   URL: http://localhost:8188"
    echo ""
else
    echo "⭕ ComfyUI: NOT RUNNING"
    echo "   To start: cd ~/ComfyUI && python main.py --listen"
    echo ""
fi

# Stable Diffusion WebUI status
if curl -s http://localhost:7860 > /dev/null 2>&1; then
    echo "✅ Stable Diffusion WebUI: RUNNING"
    echo "   URL: http://localhost:7860"
    echo ""
else
    echo "⭕ Stable Diffusion WebUI: NOT RUNNING"
    echo "   To start: cd ~/stable-diffusion-webui && ./webui.sh --listen"
    echo ""
fi

################################################################################
# Next Steps
################################################################################
echo "===================================="
echo "🎯 Next Steps"
echo "===================================="
echo ""
echo "1. Test the backend:"
echo "   curl http://localhost:5557/api/status | jq"
echo ""
echo "2. Open the UI:"
echo "   cd $PROJECT_ROOT"
echo "   python -m http.server 8000"
echo "   # Then open: http://localhost:8000/faithh_pet_v3.html"
echo ""
echo "3. Test chat:"
echo "   curl -X POST http://localhost:5557/api/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\":\"Hello FAITHH\",\"use_rag\":false}'"
echo ""
echo "4. View logs:"
echo "   tail -f $PROJECT_ROOT/logs/backend.log"
echo ""
echo "5. Stop backend:"
echo "   kill \$(cat $PROJECT_ROOT/.backend.pid)"
echo ""
echo "===================================="
echo "✅ Service startup complete!"
echo "===================================="
