#!/bin/bash

# Vaultwarden Setup on Gen8
# Created: 2026-01-20

set -e

GEN8_IP="servicebox.taileb8c60.ts.net"
VAULTWARDEN_DIR="/home/jonat/services/vaultwarden"

echo "🔐 Setting up Vaultwarden on Gen8"
echo "==============================="

# Create directories
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "mkdir -p $VAULTWARDEN_DIR/{data}"

# Create docker-compose.yml
cat > /tmp/vaultwarden.yml << 'EOF'
version: "3.8"
services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    ports:
      - "8080:80"
      - "3012:3012"
    environment:
      - WEBSOCKET_ENABLED=true
      - SIGNUPS_ALLOWED=false
      - ADMIN_TOKEN=vaultwarden_admin_token_change_me
      - DOMAIN=http://servicebox.taileb8c60.ts.net:8080
    volumes:
      - ./data:/data
    networks:
      - vaultwarden-net

networks:
  vaultwarden-net:
    driver: bridge
EOF

ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $VAULTWARDEN_DIR/docker-compose.yml" < /tmp/vaultwarden.yml

# Start Vaultwarden
echo "🚀 Starting Vaultwarden..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd $VAULTWARDEN_DIR && docker-compose up -d"

# Wait for startup
sleep 10

# Check status
echo "📋 Vaultwarden Status:"
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "docker ps | grep vaultwarden"

echo ""
echo "✅ Vaultwarden Setup Complete!"
echo ""
echo "🔗 Access URLs:"
echo "  Vaultwarden: http://$GEN8_IP:8080"
echo "  Admin Panel: http://$GEN8_IP:8080/admin"
echo ""
echo "🔑 Admin Token: vaultwarden_admin_token_change_me"
echo ""
echo "📋 Configuration:"
echo "  - Signups: Disabled (security)"
echo "  - WebSockets: Enabled"
echo "  - Domain: Set to Gen8 IP"
echo ""
echo "🔧 Next Steps:"
echo "  1. Access admin panel to change admin token"
echo "  2. Create your account"
echo "  3. Install Bitwarden client on your devices"
echo "  4. Configure self-hosted server URL"
