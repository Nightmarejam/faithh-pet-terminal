#!/bin/bash
# Quick start script for FAITHH Unified System

echo "🚀 Starting FAITHH Unified System..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if ChromaDB is running
echo "🔍 Checking ChromaDB..."
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB is running"
else
    echo "⚠️  ChromaDB not detected on port 8000"
    echo "   To start: chroma run --path ./chroma_data --port 8000"
fi

# Check if Ollama is running
echo "🔍 Checking Ollama embeddings..."
if curl -s http://localhost:11435/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama not detected on port 11435"
fi

echo ""
echo "="*60
echo "Choose what to start:"
echo "="*60
echo "1. Unified API only (backend)"
echo "2. Streamlit UI only (requires API running)"
echo "3. Both (API + UI in separate terminals)"
echo ""
read -p "Choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Unified API on port 5556..."
        python3 faithh_unified_api.py
        ;;
    2)
        echo ""
        echo "🎨 Starting Streamlit UI..."
        echo "   API should be running on http://localhost:5556"
        streamlit run chat_ui.py
        ;;
    3)
        echo ""
        echo "🚀 Starting both..."
        echo "   Opening API in background..."
        python3 faithh_unified_api.py > api.log 2>&1 &
        API_PID=$!
        echo "   API started (PID: $API_PID)"
        sleep 3
        echo "   Opening Streamlit..."
        streamlit run chat_ui.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
