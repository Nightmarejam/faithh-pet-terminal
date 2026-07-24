#!/bin/bash
# Setup Vaultwarden with HTTPS on Gen8
# Run this script ON the Gen8 server

set -e

VAULTWARDEN_DIR=~/services/vaultwarden

echo "=== Vaultwarden HTTPS Setup ==="

# Backup existing data
if [ -d "$VAULTWARDEN_DIR/data" ]; then
    echo "📦 Backing up existing data..."
    cp -r "$VAULTWARDEN_DIR/data" "$VAULTWARDEN_DIR/data.backup.$(date +%Y%m%d)"
fi

# Stop existing container
echo "🛑 Stopping existing Vaultwarden..."
cd "$VAULTWARDEN_DIR"
docker-compose down 2>/dev/null || true

# Create new docker-compose.yml
echo "📝 Creating new docker-compose.yml with Caddy..."
cat > docker-compose.yml << 'EOF'
version: "3.8"

services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    environment:
      - WEBSOCKET_ENABLED=true
      - SIGNUPS_ALLOWED=true
      - DOMAIN=https://servicebox.taileb8c60.ts.net:8443
    volumes:
      - ./data:/data
    networks:
      - vaultwarden-net

  caddy:
    image: caddy:latest
    container_name: vaultwarden-caddy
    restart: unless-stopped
    ports:
      - "8443:443"
      - "8080:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./caddy-data:/data
      - ./caddy-config:/config
    networks:
      - vaultwarden-net
    depends_on:
      - vaultwarden

networks:
  vaultwarden-net:
    driver: bridge
EOF

# Create Caddyfile
echo "📝 Creating Caddyfile..."
cat > Caddyfile << 'EOF'
{
    auto_https disable_redirects
}

:443 {
    tls internal
    
    reverse_proxy vaultwarden:80 {
        header_up X-Real-IP {remote_host}
    }
}

:80 {
    redir https://{host}:8443{uri} permanent
}
EOF

# Start services
echo "🚀 Starting Vaultwarden with HTTPS..."
docker-compose up -d

# Wait for startup
echo "⏳ Waiting for services to start..."
sleep 10

# Check status
echo ""
echo "=== Status ==="
docker ps | grep -E "vaultwarden|caddy"

echo ""
echo "✅ Vaultwarden is now available at:"
echo "   https://servicebox.taileb8c60.ts.net:8443"
echo ""
echo "⚠️  Your browser will show a certificate warning (self-signed cert)"
echo "   Click 'Advanced' → 'Proceed' to continue"
echo ""
echo "📝 After creating your account, disable signups:"
echo "   sed -i 's/SIGNUPS_ALLOWED=true/SIGNUPS_ALLOWED=false/' docker-compose.yml"
echo "   docker-compose up -d"
