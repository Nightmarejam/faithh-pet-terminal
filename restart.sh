#!/bin/bash
# restart.sh - Restart FAITHH Development Server

CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}    Restarting FAITHH Server           ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

./stop.sh
sleep 2
./start.sh "$@"