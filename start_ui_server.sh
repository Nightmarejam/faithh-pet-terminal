#!/bin/bash
# Quick UI Server Setup for FAITHH
# This runs the UI on port 8000 while backend runs on 5557

echo "🚀 Starting FAITHH UI Server..."
echo "================================"

# Check if backend is running
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:5557/health" | grep -q "200"; then
    echo "✅ Backend detected on port 5557"
else
    echo "⚠️  Backend not detected. Start it with:"
    echo "    cd ~/ai-stack && source venv/bin/activate && python faithh_professional_backend.py"
fi

# Start HTTP server for UI
echo ""
echo "📡 Starting UI server on port 8000..."
cd ~/ai-stack

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✅ Starting server..."
    echo ""
    echo "🌐 Access your UI at:"
    echo "   http://localhost:8000/faithh_pet_v3.html"
    echo ""
    echo "Press Ctrl+C to stop"
    python3 -m http.server 8000
else
    echo "❌ Python3 not found"
fi