#!/bin/bash

# start.sh - Start FAITHH Development Server
# Usage: ./start.sh [port]

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Config
DEFAULT_PORT=8080
PORT=${1:-$DEFAULT_PORT}
PID_FILE=".server.pid"
LOG_FILE="server.log"

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}FAITHH PET Terminal Server${NC}         ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Server already running (PID: $OLD_PID)${NC}"
        echo -e "   Use ${GREEN}./stop.sh${NC} first, or ${GREEN}./restart.sh${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Cleaning stale PID file...${NC}"
        rm "$PID_FILE"
    fi
fi

# Check port availability
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $PORT is already in use${NC}"
    echo -e "   Try: ${GREEN}./start.sh 3000${NC} (or any other port)"
    exit 1
fi

# Activate venv if exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment..."
    source venv/bin/activate
fi

# Create logs directory
mkdir -p logs

# Start server
echo -e "${GREEN}✓${NC} Starting Python HTTP server..."
python3 -m http.server $PORT > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Save PID
echo $SERVER_PID > "$PID_FILE"

# Verify startup
sleep 1
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo ""
    echo -e "${GREEN}✓${NC} ${GREEN}Server started successfully!${NC}"
    echo ""
    echo -e "  ${CYAN}🌐 URL:${NC}      http://localhost:$PORT"
    echo -e "  ${CYAN}📁 Files:${NC}    faithh_pet_v3.html"
    echo -e "  ${CYAN}📋 PID:${NC}      $SERVER_PID"
    echo -e "  ${CYAN}📝 Logs:${NC}     tail -f $LOG_FILE"
    echo ""
    echo -e "${YELLOW}💡 Quick Commands:${NC}"
    echo -e "   ${GREEN}./stop.sh${NC}     - Stop server"
    echo -e "   ${GREEN}./restart.sh${NC}  - Restart server"
    echo ""
    
    # Auto-open browser on WSL (optional)
    if grep -qi microsoft /proc/version; then
        echo -e "${CYAN}🚀 Opening in browser...${NC}"
        cmd.exe /c start http://localhost:$PORT/faithh_pet_v3.html 2>/dev/null || true
    fi
else
    echo -e "${RED}❌ Failed to start server${NC}"
    rm "$PID_FILE"
    cat "$LOG_FILE"
    exit 1
fi