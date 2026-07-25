#!/bin/bash
# Quick restart for testing Task 1

echo "🔄 Restarting FAITHH backend..."
pkill -9 -f "faithh_professional_backend"
sleep 2
cd ~/ai-stack
python faithh_professional_backend_fixed.py > backend.log 2>&1 &
sleep 3
echo "✅ Backend restarted"
echo "Test with: curl http://localhost:5557/api/status"
