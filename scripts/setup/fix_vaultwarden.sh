#!/bin/bash
# Fix Vaultwarden - use HTTP only but on localhost, with nginx for HTTPS
# Simpler approach: Just use HTTP on internal network (it's your home network)

cd ~/services/vaultwarden

# Stop everything
docker-compose down 2>/dev/null || true
docker stop vaultwarden-caddy 2>/dev/null || true
docker rm vaultwarden-caddy 2>/dev/null || true

# Simple HTTP-only config (works on internal network)
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
      - DOMAIN=http://servicebox.taileb8c60.ts.net:8080
    volumes:
      - ./data:/data
    ports:
      - "8080:80"
      - "3012:3012"

ENDOFFILE

docker-compose up -d
sleep 5
echo "Vaultwarden running at: http://servicebox.taileb8c60.ts.net:8080"
docker ps | grep vaultwarden
