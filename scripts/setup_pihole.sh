#!/bin/bash

# Pi-hole Setup on Gen8
# Created: 2026-01-20

set -e

GEN8_IP="192.158.1.243"
PIHOLE_DIR="/home/jonat/services/pihole"

echo "🌐 Setting up Pi-hole on Gen8"
echo "=========================="

# Create Pi-hole directory
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "mkdir -p $PIHOLE_DIR/{etc-dnsmasq,etc-pihole}"

# Create docker-compose.yml
cat > /tmp/pihole.yml << 'EOF'
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
    volumes:
      - './etc-pihole:/etc/pihole'
      - './etc-dnsmasq:/etc/dnsmasq.d'
    cap_add:
      - NET_ADMIN
    networks:
      - pihole-net

networks:
  pihole-net:
    driver: bridge
EOF

ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cat > $PIHOLE_DIR/docker-compose.yml" < /tmp/pihole.yml

# Start Pi-hole
echo "🚀 Starting Pi-hole..."
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "cd $PIHOLE_DIR && docker-compose up -d"

# Wait for Pi-hole to start
echo "⏳ Waiting for Pi-hole to start..."
sleep 15

# Check status
echo "📋 Pi-hole Status:"
ssh -i ~/.ssh/servicebox_ed25519 jonat@$GEN8_IP "docker ps | grep pihole"

echo ""
echo "✅ Pi-hole Setup Complete!"
echo ""
echo "🔗 Access URLs:"
echo "  Pi-hole Admin: http://$GEN8_IP/admin"
echo "  Password: admin123"
echo ""
echo "📋 Next Steps:"
echo "  1. Configure your router to use $GEN8_IP as DNS server"
echo "  2. Or configure Windows network settings to use $GEN8_IP as DNS"
echo "  3. Add local DNS records in Pi-hole admin"
echo ""
echo "🔧 Windows DNS Configuration:"
echo "  Control Panel → Network and Internet → Network Connections"
echo "  Right-click your connection → Properties"
echo "  Internet Protocol Version 4 (TCP/IPv4) → Properties"
echo "  Use the following DNS server addresses:"
echo "    Preferred DNS: $GEN8_IP"
echo "    Alternate DNS: 8.8.8.8"
