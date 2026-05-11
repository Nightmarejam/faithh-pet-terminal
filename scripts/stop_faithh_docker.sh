#!/bin/bash
# FAITHH AI Stack Stop Script (Docker/WSL Safe)
# This version does NOT stop Docker Ollama
# Save as: ~/ai-stack/stop_faithh_docker.sh
# Make executable: chmod +x ~/ai-stack/stop_faithh_docker.sh

echo "🛑 Stopping FAITHH AI Stack (Docker Safe Mode)..."
echo "================================"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to stop a service on a specific port
stop_port() {
    local port=$1
    local name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "Stopping ${name}..."
        kill $(lsof -t -i:$port) 2>/dev/null
        sleep 1
        
        # Check if still running
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠${NC}  ${name} still running, forcing..."
            kill -9 $(lsof -t -i:$port) 2>/dev/null
        fi
        echo -e "${GREEN}✓${NC} ${name} stopped"
    else
        echo -e "${YELLOW}○${NC} ${name} was not running"
    fi
}

# Stop Web Server (port 8080)
stop_port 8080 "Web Server"

# Stop Backend API (port 5555)
stop_port 5555 "FAITHH Backend API"

# Stop Streamlit (port 8501)
stop_port 8501 "Streamlit"

# DO NOT stop Docker Ollama - just report status
echo ""
echo "ℹ️  Docker Services (not stopped):"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "ollama"; then
    echo -e "${GREEN}✓${NC} Docker Ollama still running (managed by Docker)"
else
    echo -e "${YELLOW}○${NC} Docker Ollama not running"
fi

# Stop PULSE monitor if running
echo ""
echo "Stopping PULSE monitor..."
if pgrep -f "pulse_monitor.py" > /dev/null; then
    pkill -f "pulse_monitor.py" 2>/dev/null
    echo -e "${GREEN}✓${NC} PULSE monitor stopped"
else
    echo -e "${YELLOW}○${NC} PULSE monitor was not running"
fi

echo ""
echo "================================"
echo "✅ FAITHH web services stopped"
echo "================================"
echo ""
echo "💡 Docker Ollama remains running (use 'docker stop ollama' to stop)"
echo "To restart web services: ~/ai-stack/start_faithh_docker.sh"