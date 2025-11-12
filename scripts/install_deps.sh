#!/bin/bash
# Install dependencies for FAITHH API with WebSocket support

echo "📦 Installing FAITHH dependencies..."

pip install flask flask-cors flask-sock google-generativeai pyyaml

echo "✅ Installation complete!"
echo ""
echo "You can now run:"
echo "  python3 faithh_api_websocket.py"
