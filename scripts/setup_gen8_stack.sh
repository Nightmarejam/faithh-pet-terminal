#!/bin/bash

# Gen8 Server Full Stack Setup
# Created: 2026-01-20
# Purpose: Set up ChromaDB, CI/CD, Monitoring, Package Registry

set -e

echo "🚀 Gen8 Server Full Stack Setup"
echo "================================"

# Configuration
GEN8_IP="servicebox.taileb8c60.ts.net"
SERVICES_DIR="/home/jonat/services"
DOCKER_REGISTRY_DIR="/home/jonat/services/docker-registry"
MONITORING_DIR="/home/jonat/services/monitoring"
CICD_DIR="/home/jonat/services/cicd"

# Create service directories
echo "📁 Creating service directories..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "mkdir -p $SERVICES_DIR/{chromadb/backups,docker-registry,monitoring,cicd,logs}"

# 1. Fix ChromaDB Backup
echo "🔧 Fixing ChromaDB backup script..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "sed -i 's|~/|/home/jonat/|g' /home/jonat/services/chromadb/backup.sh"

# 2. Set up Docker Registry
echo "📦 Setting up Docker Registry..."
cat > /tmp/docker-registry.yml << 'EOF'
version: "3.8"
services:
  registry:
    image: registry:2
    container_name: docker-registry
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY: /data
    volumes:
      - ./data:/data
    networks:
      - registry-net

  registry-ui:
    image: joxit/docker-registry-ui:latest
    container_name: registry-ui
    restart: unless-stopped
    ports:
      - "5001:80"
    environment:
      REGISTRY_TITLE: "Gen8 Docker Registry"
      REGISTRY_URL: http://localhost:5000
      DELETE_IMAGES: "true"
    depends_on:
      - registry
    networks:
      - registry-net

networks:
  registry-net:
    driver: bridge
EOF

ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $DOCKER_REGISTRY_DIR/docker-compose.yml" < /tmp/docker-registry.yml
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "mkdir -p $DOCKER_REGISTRY_DIR/data"

# 3. Set up Monitoring (Prometheus + Grafana)
echo "📊 Setting up Monitoring Stack..."
cat > /tmp/monitoring.yml << 'EOF'
version: "3.8"
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin123
    volumes:
      - ./grafana/data:/var/lib/grafana
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

networks:
  default:
    name: monitoring-net
EOF

ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $MONITORING_DIR/docker-compose.yml" < /tmp/monitoring.yml

# Create Prometheus config
cat > /tmp/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'chromadb'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'uptime-kuma'
    static_configs:
      - targets: ['localhost:3001']
    metrics_path: '/metrics'

  - job_name: 'docker-registry'
    static_configs:
      - targets: ['localhost:5000']
EOF

ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $MONITORING_DIR/prometheus.yml" < /tmp/prometheus.yml
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "mkdir -p $MONITORING_DIR/{data,grafana/data}"

# 4. Set up CI/CD Runner (GitLab)
echo "🔄 Setting up CI/CD Runner..."
cat > /tmp/cicd.yml << 'EOF'
version: "3.8"
services:
  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./config:/etc/gitlab-runner
    privileged: true

  gitea:
    image: gitea/gitea:latest
    container_name: gitea
    restart: unless-stopped
    ports:
      - "2222:22"
      - "3002:3000"
    environment:
      - USER_UID=1000
      - USER_GID=1000
    volumes:
      - ./gitea:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro

networks:
  default:
    name: cicd-net
EOF

ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $CICD_DIR/docker-compose.yml" < /tmp/cicd.yml
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "mkdir -p $CICD_DIR/{config,gitea}"

# 5. Start all services
echo "🚀 Starting all services..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd $DOCKER_REGISTRY_DIR && docker-compose up -d"
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd $MONITORING_DIR && docker-compose up -d"
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd $CICD_DIR && docker-compose up -d"

# 6. Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# 7. Check service status
echo "📋 Service Status:"
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "✅ Services Setup Complete!"
echo ""
echo "🔗 Access URLs:"
echo "  ChromaDB: http://$GEN8_IP:8000"
echo "  Docker Registry: http://$GEN8_IP:5000"
echo "  Registry UI: http://$GEN8_IP:5001"
echo "  Prometheus: http://$GEN8_IP:9090"
echo "  Grafana: http://$GEN8_IP:3000 (admin/admin123)"
echo "  Gitea: http://$GEN8_IP:3002"
echo "  Uptime Kuma: http://$GEN8_IP:3001"
echo ""
echo "📊 Next Steps:"
echo "  1. Configure Grafana dashboards"
echo "  2. Set up GitLab runner registration"
echo "  3. Configure Pi-hole DNS settings"
echo "  4. Test ChromaDB backups"
echo "  5. Set up monitoring alerts"
