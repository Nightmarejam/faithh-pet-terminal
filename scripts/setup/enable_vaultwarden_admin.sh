#!/bin/bash
cd ~/services/vaultwarden

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
      - ADMIN_TOKEN=vaultwarden_admin_2026
      - DOMAIN=https://servicebox.taileb8c60.ts.net
    volumes:
      - ./data:/data
    ports:
      - "127.0.0.1:8080:80"
      - "127.0.0.1:3012:3012"
EOF

docker-compose up -d
echo "Admin panel enabled at: https://servicebox.taileb8c60.ts.net/admin"
echo "Token: vaultwarden_admin_2026"
