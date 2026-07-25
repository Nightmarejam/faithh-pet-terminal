#!/bin/bash
# FAITHH Master Launch Script
# This starts everything needed for the FAITHH system

echo "============================================================"
echo "             FAITHH SYSTEM LAUNCHER v2.0"
echo "             Battle Network PET System"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local name=$1
    local port=$2
    local url=$3
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is running on port $port${NC}"
        return 0
    else
        echo -e "${RED}❌ $name is not running on port $port${NC}"
        return 1
    fi
}

# Step 1: Check current status
echo "🔍 Checking current system status..."
echo "----------------------------------------"
check_service "ChromaDB" 8000 "http://localhost:8000/api/v1/heartbeat"
CHROMA_RUNNING=$?

check_service "Ollama" 11434 "http://localhost:11434/api/version"
OLLAMA_RUNNING=$?

check_service "Backend API" 5557 "http://localhost:5557/health"
BACKEND_RUNNING=$?

echo ""
echo "============================================================"
echo "                    LAUNCH OPTIONS"
echo "============================================================"
echo "1. Start HTML UI with simple backend (Recommended)"
echo "2. Start full system (All services)"
echo "3. Start backend only"
echo "4. Open HTML in browser"
echo "5. System health check"
echo "6. Exit"
echo ""
read -p "Choose option (1-6): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Starting FAITHH Simple Backend...${NC}"
        
        # Check if virtual environment exists
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        
        # Install required packages if needed
        echo "Checking Python dependencies..."
        pip install flask flask-cors requests > /dev/null 2>&1
        
        # Start the simple backend
        echo -e "${GREEN}Starting backend on http://localhost:5557${NC}"
        echo -e "${GREEN}HTML UI will be available at http://localhost:5557${NC}"
        echo ""
        python3 faithh_simple_backend.py
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}Starting full FAITHH system...${NC}"
        
        # Start ChromaDB if not running
        if [ $CHROMA_RUNNING -ne 0 ]; then
            echo "Starting ChromaDB..."
            docker-compose up -d chromadb 2>/dev/null || echo "ChromaDB docker not configured"
        fi
        
        # Start Ollama if not running
        if [ $OLLAMA_RUNNING -ne 0 ]; then
            echo "Starting Ollama..."
            docker-compose up -d ollama 2>/dev/null || echo "Ollama docker not configured"
        fi
        
        # Start backend
        if [ $BACKEND_RUNNING -ne 0 ]; then
            echo "Starting backend API..."
            python3 faithh_simple_backend.py &
            BACKEND_PID=$!
            echo "Backend started with PID: $BACKEND_PID"
        fi
        
        echo ""
        echo -e "${GREEN}System started!${NC}"
        echo "Access the UI at: http://localhost:5557"
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}Starting backend only...${NC}"
        python3 faithh_simple_backend.py
        ;;
        
    4)
        echo ""
        echo -e "${YELLOW}Opening HTML in browser...${NC}"
        
        # Try different commands to open browser
        if command -v xdg-open > /dev/null; then
            xdg-open "http://localhost:5557" &
        elif command -v open > /dev/null; then
            open "http://localhost:5557" &
        else
            echo "Please open http://localhost:5557 in your browser"
        fi
        ;;
        
    5)
        echo ""
        echo -e "${YELLOW}Running system health check...${NC}"
        python3 system_health_check.py
        ;;
        
    6)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac