#!/bin/bash
# stop.sh - Stop FAITHH Development Server

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PID_FILE=".server.pid"
LOG_FILE="server.log"

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${YELLOW}Stopping FAITHH Server${NC}              ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  No PID file found${NC}"
    echo -e "${GREEN}✓${NC} Checking for orphaned processes..."
    
    PORTS=(8080 8000 3000 5555)
    KILLED=0
    
    for PORT in "${PORTS[@]}"; do
        PIDS=$(lsof -ti:$PORT 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            echo -e "${YELLOW}⚠️  Found process on port $PORT${NC}"
            echo $PIDS | xargs kill -15 2>/dev/null || true
            sleep 1
            echo $PIDS | xargs kill -9 2>/dev/null || true
            KILLED=1
        fi
    done
    
    if [ $KILLED -eq 1 ]; then
        echo -e "${GREEN}✓${NC} Orphaned processes cleaned up"
    else
        echo -e "${GREEN}✓${NC} No server processes found"
    fi
    
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p $PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Server not running (PID: $PID)${NC}"
    rm "$PID_FILE"
    exit 0
fi

echo -e "${GREEN}✓${NC} Stopping server (PID: $PID)..."
kill -15 $PID 2>/dev/null || true

TIMEOUT=5
COUNTER=0
while ps -p $PID > /dev/null 2>&1 && [ $COUNTER -lt $TIMEOUT ]; do
    sleep 1
    COUNTER=$((COUNTER + 1))
    echo -n "."
done
echo ""

if ps -p $PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Force stopping...${NC}"
    kill -9 $PID 2>/dev/null || true
    sleep 1
fi

if ps -p $PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Failed to stop server${NC}"
    exit 1
else
    echo -e "${GREEN}✓${NC} ${GREEN}Server stopped successfully${NC}"
    rm "$PID_FILE"
    
    if [ -f "$LOG_FILE" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        mkdir -p logs
        mv "$LOG_FILE" "logs/server_${TIMESTAMP}.log" 2>/dev/null || rm "$LOG_FILE"
        echo -e "${GREEN}✓${NC} Log archived"
    fi
    echo ""
fi