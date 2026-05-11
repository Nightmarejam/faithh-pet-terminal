#!/bin/bash
# FAITHH System Health Check

echo "=== FAITHH Health Check $(date) ==="

# 1. Docker containers
echo -e "\n--- Docker Containers ---"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. GPU Status
echo -e "\n--- GPU Status ---"
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader

# 3. Ollama Models
echo -e "\n--- Ollama Models ---"
docker exec faithh-ollama ollama list

# 4. Quick Model Test
echo -e "\n--- Quick Model Test ---"
echo "Testing Llama 3.1..."
docker exec faithh-ollama ollama run llama31-faithh "Say 'OK' if working" 2>&1 | head -n 3

# 5. Disk Space
echo -e "\n--- Disk Space ---"
df -h /mnt/c | tail -n 1

# 6. Memory
echo -e "\n--- System Memory ---"
free -h | grep "Mem:"

echo -e "\n=== Health Check Complete ==="
