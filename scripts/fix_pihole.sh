#!/bin/bash

# Fix Pi-hole Configuration
# Created: 2026-01-20

GEN8_IP="192.158.1.243"
PIHOLE_DIR="/home/jonat/services/pihole"

echo "🔧 Fixing Pi-hole Configuration"
echo "=============================="

# Stop current Pi-hole
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd $PIHOLE_DIR && docker-compose down"

# Create proper setupVars.conf
cat > /tmp/setupVars.conf << EOF
PIHOLE_INTERFACE=eth0
IPV4_ADDRESS=$GEN8_IP
IPV6_ADDRESS=
PIHOLE_DNS_1=1.1.1.1
PIHOLE_DNS_2=8.8.8.8
QUERY_LOGGING=true
INSTALL_WEB_SERVER=true
INSTALL_WEB_INTERFACE=true
LIGHTTPD_ENABLED=true
CACHE_SIZE=10000
DNS_FQDN_REQUIRED=true
DNS_BOGUS_PRIV=true
DNSSEC=false
REV_SERVER=false
EOF

# Create custom dnsmasq config
cat > /tmp/99-custom.conf << 'EOF'
# Allow queries from local network
server=1.1.1.1
server=8.8.8.8

# Listen on all interfaces
interface=eth0
bind-interfaces

# Allow local network
local-service=1

# Log queries
log-queries
log-facility=/var/log/pihole.log

# DHCP settings (disabled)
no-dhcp-interface=eth0
EOF

# Copy configs to Gen8
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $PIHOLE_DIR/etc-pihole/setupVars.conf" < /tmp/setupVars.conf
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $PIHOLE_DIR/etc-dnsmasq.d/99-custom.conf" < /tmp/99-custom.conf

# Update docker-compose.yml with proper config
cat > /tmp/pihole-fixed.yml << 'EOF'
version: "3.8"
services:
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    restart: unless-stopped
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "80:80/tcp"
      - "443:443/tcp"
    environment:
      TZ: 'America/Los_Angeles'
      WEBPASSWORD: 'admin123'
      DNS1: '1.1.1.1'
      DNS2: '8.8.8.8'
      ServerIP: '192.158.1.243'
    volumes:
      - './etc-pihole:/etc/pihole'
      - './etc-dnsmasq.d:/etc/dnsmasq.d'
    cap_add:
      - NET_ADMIN
    network_mode: host
    dns:
      - 127.0.0.1
      - 1.1.1.1
EOF

ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $PIHOLE_DIR/docker-compose.yml" < /tmp/pihole-fixed.yml

# Start Pi-hole
echo "🚀 Starting fixed Pi-hole..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd $PIHOLE_DIR && docker-compose up -d"

# Wait for startup
sleep 10

# Check status
echo "📋 Pi-hole Status:"
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "docker ps | grep pihole"

# Test DNS
echo "🔍 Testing DNS from Gen8..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "nslookup google.com localhost"

echo ""
echo "✅ Pi-hole Fixed!"
echo ""
echo "🔗 Admin URL: http://$GEN8_IP/admin"
echo "🔑 Password: admin123"
echo ""
echo "📋 Next Steps:"
echo "1. Set Windows DNS to $GEN8_IP"
echo "2. Test with: nslookup google.com"
echo "3. Check query logs in admin panel"
