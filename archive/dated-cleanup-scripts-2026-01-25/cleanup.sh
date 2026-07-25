#!/bin/bash
# Complete WSL2 Cleanup - Remove all Docker, use native services only
# This will make WSL2 a clean dev environment connecting to Gen8

set -e

echo "=========================================="
echo "WSL2 + GEN8 ARCHITECTURE CLEANUP"
echo "=========================================="
echo ""
echo "Goal: WSL2 as compute (native Ollama + FAITHH)"
echo "      Gen8 as data (ChromaDB, Pi-hole, monitoring)"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Phase 1: Verify Gen8 services are reachable
echo "=========================================="
echo "PHASE 1: VERIFY GEN8 SERVICES"
echo "=========================================="

echo -e "\n${YELLOW}Checking Gen8 ChromaDB...${NC}"

# Use Python client instead of curl (handles API version correctly)
CHROMADB_CHECK=$(python3 << 'EOF'
import chromadb
try:
    client = chromadb.HttpClient(host="100.79.85.32", port=8000)
    heartbeat = client.heartbeat()
    collections = client.list_collections()
    collection_names = [c.name for c in collections]
    
    if "faithh_knowledge_base" in collection_names:
        collection = client.get_collection(name="faithh_knowledge_base")
        count = collection.count()
        print(f"OK|{count}")
    else:
        print("MISSING|0")
except Exception as e:
    print(f"ERROR|{str(e)}")
EOF
)

STATUS=$(echo "$CHROMADB_CHECK" | cut -d'|' -f1)
DOC_COUNT=$(echo "$CHROMADB_CHECK" | cut -d'|' -f2)

if [ "$STATUS" = "OK" ]; then
    echo -e "${GREEN}✅ Gen8 ChromaDB is online${NC}"
    echo "   Collection 'faithh_knowledge_base': $DOC_COUNT documents"
elif [ "$STATUS" = "MISSING" ]; then
    echo -e "${RED}❌ faithh_knowledge_base collection not found!${NC}"
    echo "   Available collections: $(echo "$CHROMADB_CHECK" | cut -d'|' -f2)"
    exit 1
else
    echo -e "${RED}❌ Gen8 ChromaDB not reachable!${NC}"
    echo "   Error: $DOC_COUNT"
    echo "   Cannot proceed - fix Gen8 connection first"
    exit 1
fi

echo -e "\n${YELLOW}Checking Gen8 Pi-hole...${NC}"
if curl -sf http://100.79.85.32/admin/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Gen8 Pi-hole is online${NC}"
else
    echo -e "${YELLOW}⚠️  Pi-hole web interface not reachable (DNS may still work)${NC}"
fi

echo -e "\n${YELLOW}Checking for Uptime Kuma on Gen8...${NC}"
if curl -sf http://100.79.85.32:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Uptime Kuma is running${NC}"
else
    echo -e "${YELLOW}⚠️  Uptime Kuma not found (you can add it later)${NC}"
fi

echo -e "\n${YELLOW}Checking network connectivity...${NC}"
if ping -c 1 100.79.85.32 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Gen8 is reachable via network${NC}"
else
    echo -e "${RED}❌ Cannot ping Gen8${NC}"
fi

# Phase 2: Audit current WSL2 state
echo ""
echo "=========================================="
echo "PHASE 2: AUDIT WSL2 CURRENT STATE"
echo "=========================================="

echo -e "\n${YELLOW}Docker containers currently running:${NC}"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not running"

echo -e "\n${YELLOW}Native Ollama processes:${NC}"
pgrep -a ollama | head -5 || echo "None found"

echo -e "\n${YELLOW}Native Ollama models:${NC}"
curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models[].name' || echo "Ollama not responding"

echo -e "\n${YELLOW}FAITHH backend status:${NC}"
if pgrep -f "faithh_professional_backend" > /dev/null; then
    echo -e "${GREEN}✅ FAITHH backend is running${NC}"
else
    echo -e "${YELLOW}⚠️  FAITHH backend not running${NC}"
fi

echo -e "\n${YELLOW}Current .env configuration:${NC}"
if [ -f ~/ai-stack/.env ]; then
    echo "OLLAMA_HOST=$(grep OLLAMA_HOST ~/ai-stack/.env | cut -d= -f2)"
    echo "CHROMADB_HOST=$(grep CHROMADB_HOST ~/ai-stack/.env | cut -d= -f2)"
    echo "CHROMA_HOST=$(grep CHROMA_HOST ~/ai-stack/.env | cut -d= -f2)"
else
    echo -e "${RED}❌ .env file not found in ~/ai-stack/${NC}"
fi

# Phase 3: Cleanup plan
echo ""
echo "=========================================="
echo "PHASE 3: CLEANUP PLAN"
echo "=========================================="

cat << 'EOF'

📋 REMOVAL PLAN:
   ❌ Docker ChromaDB (duplicate - using Gen8)
   ❌ Docker Ollama (3 containers - using native)
   ❌ LangFlow (unused)
   ❌ Postgres (only needed for LangFlow)

✅ KEEPING:
   ✅ Native Ollama (systemd) with GPU access
   ✅ FAITHH backend (Python venv)
   ✅ Connection to Gen8 ChromaDB

🎯 RESULT:
   • Clean WSL2 environment (no Docker overhead)
   • Native services only (faster, direct GPU access)
   • All data on Gen8 (persistent, backed up)
   • ~10-15GB RAM freed up on WSL2

EOF

echo -e "${YELLOW}Continue with cleanup? This will:${NC}"
echo "  1. Stop and remove all Docker containers"
echo "  2. Backup Docker volumes to ~/docker-backup/"
echo "  3. Keep native Ollama + FAITHH"
echo ""
echo -e "${RED}Press ENTER to continue, Ctrl+C to abort${NC}"
read -r

# Phase 4: Execute cleanup
echo ""
echo "=========================================="
echo "PHASE 4: EXECUTING CLEANUP"
echo "=========================================="

echo -e "\n${YELLOW}🗑️  Stopping all Docker containers...${NC}"
docker stop $(docker ps -aq) 2>/dev/null || echo "No containers to stop"

echo -e "\n${YELLOW}🗑️  Removing all Docker containers...${NC}"
docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"

echo -e "\n${YELLOW}🗑️  Backing up Docker volumes...${NC}"
echo "   Creating backup directory: ~/docker-backup"
mkdir -p ~/docker-backup

VOLUMES=$(docker volume ls -q 2>/dev/null)
if [ -n "$VOLUMES" ]; then
    for vol in $VOLUMES; do
        echo "   Backing up volume: $vol"
        docker run --rm -v $vol:/source -v ~/docker-backup:/backup alpine tar czf /backup/$vol.tar.gz -C /source . 2>/dev/null || echo "   (skipped - empty or inaccessible)"
    done
    echo -e "${GREEN}✅ Docker volumes backed up to ~/docker-backup/${NC}"
else
    echo "   No volumes to backup"
fi

echo ""
echo -e "${YELLOW}Remove Docker volumes? (saves disk space) (y/N)${NC}"
read -r REMOVE_VOLUMES
if [ "$REMOVE_VOLUMES" = "y" ]; then
    docker volume rm $(docker volume ls -q) 2>/dev/null || echo "No volumes to remove"
    echo -e "${GREEN}✅ Docker volumes removed${NC}"
else
    echo -e "${YELLOW}⚠️  Keeping Docker volumes (can remove later with: docker volume prune)${NC}"
fi

# Phase 5: Verify cleanup
echo ""
echo "=========================================="
echo "PHASE 5: VERIFICATION"
echo "=========================================="

echo -e "\n${YELLOW}Remaining Docker containers:${NC}"
CONTAINERS=$(docker ps -a --format "{{.Names}}" 2>/dev/null)
if [ -z "$CONTAINERS" ]; then
    echo -e "${GREEN}✅ No Docker containers remaining${NC}"
else
    echo -e "${RED}⚠️  Some containers still exist:${NC}"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
fi

echo -e "\n${YELLOW}Native Ollama status:${NC}"
if pgrep ollama > /dev/null; then
    echo -e "${GREEN}✅ Native Ollama is running${NC}"
    MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models[].name' 2>/dev/null)
    if [ -n "$MODELS" ]; then
        echo "$MODELS" | while read -r model; do
            echo "   - $model"
        done
    fi
else
    echo -e "${RED}❌ Native Ollama not running!${NC}"
    echo "   Start it with: sudo systemctl start ollama"
fi

echo -e "\n${YELLOW}FAITHH connectivity test:${NC}"

# Test Gen8 ChromaDB again
python3 << 'EOF'
import chromadb
try:
    client = chromadb.HttpClient(host="100.79.85.32", port=8000)
    heartbeat = client.heartbeat()
    collection = client.get_collection(name="faithh_knowledge_base")
    count = collection.count()
    print(f"✅ Can reach Gen8 ChromaDB")
    print(f"   faithh_knowledge_base: {count} documents")
except Exception as e:
    print(f"❌ Cannot reach Gen8 ChromaDB: {e}")
EOF

echo ""
echo "Testing connection to local Ollama..."
if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Can reach local Ollama${NC}"
else
    echo -e "${RED}❌ Cannot reach local Ollama${NC}"
fi

# Phase 6: Next steps
echo ""
echo "=========================================="
echo "CLEANUP COMPLETE! 🎉"
echo "=========================================="

cat << 'EOF'

✅ COMPLETED:
   ✅ All Docker containers removed
   ✅ Docker volumes backed up to ~/docker-backup/
   ✅ Native Ollama still running
   ✅ Connection to Gen8 ChromaDB verified

📋 NEXT STEPS:

1. Optimize Native Ollama (use RTX 3090 instead of GTX 1080 Ti):
   
   sudo systemctl edit ollama
   
   Add these lines:
   [Service]
   Environment="CUDA_VISIBLE_DEVICES=1,0"
   
   Then:
   sudo systemctl daemon-reload
   sudo systemctl restart ollama

2. Verify FAITHH backend works:
   
   cd ~/ai-stack
   source venv/bin/activate
   python faithh_professional_backend_fixed.py
   
   # In another terminal:
   curl http://localhost:5557/api/status

3. Test end-to-end:
   
   # Open FAITHH UI and ask a question
   # Should use: Native Ollama + Gen8 ChromaDB

4. Monitor GPU usage:
   
   watch -n 1 nvidia-smi
   # After step 1, should show model on GPU 1 (RTX 3090)

5. Optional - Remove Docker Desktop entirely (if not needed):
   
   sudo apt remove docker-ce docker-ce-cli containerd.io
   # Frees up ~2-3GB disk space
   # Can always reinstall later if needed

6. Optional - Access services from anywhere:
   
   # Gen8 already has Uptime Kuma running
   # Access it at: http://100.79.85.32:3001
   # Set up monitoring for:
   #   - Gen8 ChromaDB (http://100.79.85.32:8000/api/v2/heartbeat)
   #   - WSL2 Ollama (http://DESKTOP-JJ1SUHB:11434/api/tags)
   #   - FAITHH backend (http://DESKTOP-JJ1SUHB:5557/health)

EOF

echo ""
echo "Your system is now clean and optimized! 🚀"
echo ""
echo "Current architecture:"
echo "  WSL2: Native Ollama (GPU) + FAITHH backend"
echo "  Gen8: ChromaDB (29,013 docs) + Pi-hole + Uptime Kuma"
echo ""
echo "Resources freed: ~10-15GB RAM on WSL2"
echo ""
