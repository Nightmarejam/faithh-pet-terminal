#!/bin/bash
# FAITHH AI Stack Startup Script (Docker/WSL Optimized)
# Save as: ~/ai-stack/start_faithh_docker.sh
# Make executable: chmod +x ~/ai-stack/start_faithh_docker.sh

echo "🚀 Starting FAITHH AI Stack (Docker Mode)..."
echo "================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 1. Check/Start Docker Ollama
echo ""
echo "1️⃣  Checking Docker Ollama..."
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^ollama$"; then
    echo -e "${GREEN}✓${NC} Docker Ollama container is running"
    
    # Check if port is accessible
    if check_port 11434; then
        echo -e "${GREEN}✓${NC} Ollama accessible on port 11434"
    else
        echo -e "${YELLOW}⚠${NC}  Ollama container running but port not accessible"
        echo "   Waiting for port to become available..."
        sleep 3
        check_port 11434 && echo -e "${GREEN}✓${NC} Port now accessible" || echo -e "${RED}✗${NC} Port still not accessible"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Docker Ollama container not running"
    echo "   Attempting to start..."
    docker start ollama 2>/dev/null
    sleep 3
    
    if docker ps --format '{{.Names}}' | grep -q "^ollama$"; then
        echo -e "${GREEN}✓${NC} Ollama container started"
    else
        echo -e "${RED}✗${NC} Failed to start Ollama container"
        echo "   Try: docker start ollama"
    fi
fi

# 2. Check other Docker containers
echo ""
echo "2️⃣  Checking Docker Stack..."
CONTAINERS=$(docker ps --format "{{.Names}}" 2>/dev/null | grep -E "chromadb|embed|qwen|langflow|postgres")
if [ -n "$CONTAINERS" ]; then
    echo -e "${GREEN}✓${NC} Docker containers running:"
    echo "$CONTAINERS" | while read container; do
        echo "   - $container"
    done
else
    echo -e "${YELLOW}⚠${NC}  No additional Docker containers detected"
fi

# 3. Start Web Server (Python HTTP)
echo ""
echo "3️⃣  Checking Web Server (port 8080)..."
if check_port 8080; then
    echo -e "${GREEN}✓${NC} Web server already running"
else
    echo "   Starting web server..."
    cd ~/ai-stack
    nohup python3 -m http.server 8080 > ~/ai-stack/logs/webserver.log 2>&1 &
    sleep 2
    check_port 8080 && echo -e "${GREEN}✓${NC} Web server started" || echo -e "${RED}✗${NC} Failed to start web server"
fi

# 4. Start FAITHH Backend API (Flask)
echo ""
echo "4️⃣  Checking FAITHH Backend API (port 5555)..."
if check_port 5555; then
    echo -e "${GREEN}✓${NC} Backend API already running"
else
    echo "   Starting FAITHH Backend API..."
    cd ~/ai-stack
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    nohup python3 faithh_api.py > ~/ai-stack/logs/faithh_api.log 2>&1 &
    sleep 3
    check_port 5555 && echo -e "${GREEN}✓${NC} Backend API started" || echo -e "${RED}✗${NC} Failed to start Backend API"
fi

# 5. Check Streamlit (optional)
echo ""
echo "5️⃣  Checking Streamlit (port 8501)..."
if check_port 8501; then
    echo -e "${GREEN}✓${NC} Streamlit running"
else
    echo -e "${YELLOW}○${NC} Streamlit not running (optional)"
fi

# 6. Summary
echo ""
echo "================================"
echo "📊 SYSTEM STATUS SUMMARY"
echo "================================"

# Check Docker Ollama
if docker ps --format '{{.Names}}' | grep -q "^ollama$"; then
    if check_port 11434; then
        echo -e "${GREEN}✓${NC} Docker Ollama (11434)"
    else
        echo -e "${YELLOW}⚠${NC} Docker Ollama running but port not ready"
    fi
else
    echo -e "${RED}✗${NC} Docker Ollama (not running)"
fi

# Check other services
if check_port 8080; then
    echo -e "${GREEN}✓${NC} Web Server (8080)"
else
    echo -e "${RED}✗${NC} Web Server (8080)"
fi

if check_port 5555; then
    echo -e "${GREEN}✓${NC} Backend API (5555)"
else
    echo -e "${RED}✗${NC} Backend API (5555)"
fi

if check_port 8501; then
    echo -e "${GREEN}✓${NC} Streamlit (8501)"
else
    echo -e "${YELLOW}○${NC} Streamlit (8501) - Optional"
fi

echo ""
echo "🌐 Access FAITHH at: http://localhost:8080/faithh_pet_v2.html"
echo "📝 Logs located in: ~/ai-stack/logs/"
echo ""
echo "💡 Note: Ollama managed by Docker - use 'docker start/stop ollama'"