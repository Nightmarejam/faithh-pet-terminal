#!/bin/bash

# FAITHH Journey Dashboard Launcher
# Starts the dashboard server and opens the visualization

echo "🚀 Starting FAITHH Journey Dashboard..."

# Check if dashboard server is already running
if pgrep -f "dashboard_server.py" > /dev/null; then
    echo "✅ Dashboard server is already running"
else
    echo "📡 Starting dashboard server on port 8080..."
    python3 scripts/dashboard_server.py &
    sleep 2
fi

# Check if server started successfully
if curl -s http://localhost:8080/dashboard_data.json > /dev/null; then
    echo "✅ Dashboard server is healthy"
    echo ""
    echo "🌐 Dashboard available at: http://localhost:8080/faithh_journey_dashboard.html"
    echo "📊 API endpoint: http://localhost:8080/dashboard_data.json"
    echo "🔄 Refresh endpoint: http://localhost:8080/refresh"
    echo ""
    echo "💡 Tip: The dashboard automatically refreshes every 5 minutes"
    echo "💡 Tip: Call /refresh to manually regenerate data from chat archives"
    echo ""
    
    # Try to open in browser (Linux)
    if command -v xdg-open > /dev/null; then
        echo "🌐 Opening dashboard in browser..."
        xdg-open http://localhost:8080/faithh_journey_dashboard.html
    fi
else
    echo "❌ Failed to start dashboard server"
    echo "🔧 Check for errors in dashboard_server.py"
    exit 1
fi
