#!/bin/bash
# Fix Vaultwarden - use Tailscale for HTTPS
# Tailscale provides automatic HTTPS via tailscale serve

cd ~/services/vaultwarden

# Stop existing
docker-compose down 2>/dev/null || true

# Update config with Tailscale domain
cat > docker-compose.yml << 'ENDOFFILE'
version: "3.8"

services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    environment:
      - WEBSOCKET_ENABLED=true
      - SIGNUPS_ALLOWED=true
      - DOMAIN=https://servicebox.taileb8c60.ts.net
    volumes:
      - ./data:/data
    ports:
      - "127.0.0.1:8080:80"
      - "127.0.0.1:3012:3012"

ENDOFFILE

docker-compose up -d
sleep 3

# Set up Tailscale serve to proxy HTTPS to Vaultwarden
echo "Setting up Tailscale HTTPS proxy..."
sudo tailscale serve --bg --https=443 http://127.0.0.1:8080

echo ""
echo "=== Vaultwarden Setup Complete ==="
echo "Access via: https://servicebox.taileb8c60.ts.net"
echo ""
docker ps | grep vaultwarden
tailscale serve status
