#!/bin/bash

# Gen8 Health Check Script (Simplified)
GEN8_IP="192.158.1.243"
FAILED=0

echo "🏥 Gen8 Server Health Check"
echo "========================="
echo "Timestamp: $(date)"
echo ""

# Check containers
echo "📦 Container Status:"
containers=("chromadb" "grafana" "prometheus" "node-exporter" "pihole" "gitea" "vaultwarden" "docker-registry" "registry-ui" "uptime-kuma" "gitlab-runner")

for container in "${containers[@]}"; do
    echo -n "🐳 $container... "
    if ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "docker ps --format '{{.Names}}' | grep -q '^$container$'"; then
        echo "✅"
    else
        echo "❌"
        FAILED=$((FAILED + 1))
    fi
done

# Check key services
echo ""
echo "🌐 Key Services:"
services=("ChromaDB:8000:/api/v2/heartbeat" "Grafana:3000:/api/health" "Gitea:3002:/")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    path=$(echo $service | cut -d: -f3)
    
    echo -n "🔍 $name... "
    if curl -s -o /dev/null -w "%{http_code}" "http://$GEN8_IP:$port$path" | grep -q "200"; then
        echo "✅"
    else
        echo "❌"
        FAILED=$((FAILED + 1))
    fi
done

# Check DNS
echo ""
echo -n "🌍 DNS Resolution... "
if nslookup google.com $GEN8_IP >/dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
    FAILED=$((FAILED + 1))
fi

# System resources
echo ""
echo "📊 System Resources:"
cpu=$(ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1")
mem=$(ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "free | grep Mem | awk '{printf \"%.1f%%\", (\$3/\$2) * 100.0}'")
disk=$(ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "df -h / | tail -1 | awk '{print \$5}'")
echo "CPU: ${cpu}% | Memory: ${mem} | Disk: ${disk}"

# ChromaDB docs
docs=$(curl -s http://$GEN8_IP:8000/api/v2/collections/faithh_knowledge_base/count 2>/dev/null || echo "0")
echo "📚 ChromaDB Documents: $docs"

# Summary
echo ""
echo "========================="
if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL SERVICES HEALTHY!"
else
    echo "⚠️  $FAILED services failed"
fi
echo "========================="

exit $FAILED
