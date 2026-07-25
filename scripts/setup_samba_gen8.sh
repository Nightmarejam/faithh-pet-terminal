#!/usr/bin/env bash
# Run this directly on gen8 (servicebox) as a user with sudo.
# Sets up a guest Samba share at /srv/shared accessible by all LAN devices.
set -euo pipefail

SHARE_ROOT="/srv/shared"

echo "==> Installing Samba..."
sudo apt-get update -qq
sudo apt-get install -y samba

echo "==> Creating share directory structure..."
sudo mkdir -p "$SHARE_ROOT"/{drop,data,exchange}
sudo chmod -R 0777 "$SHARE_ROOT"
sudo chown -R nobody:nogroup "$SHARE_ROOT"

echo "==> Backing up existing smb.conf..."
sudo cp /etc/samba/smb.conf "/etc/samba/smb.conf.bak.$(date +%Y%m%d)"

echo "==> Appending share block to smb.conf..."
sudo tee -a /etc/samba/smb.conf > /dev/null << 'SMBEOF'

[shared]
   path = /srv/shared
   browseable = yes
   writable = yes
   guest ok = yes
   guest only = yes
   create mask = 0664
   directory mask = 0775
   force user = nobody
   force group = nogroup
SMBEOF

echo "==> Validating config..."
sudo testparm -s

echo "==> Enabling and restarting Samba..."
sudo systemctl enable --now smbd nmbd
sudo systemctl restart smbd nmbd

echo "==> Opening firewall ports (if ufw is active)..."
if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
    sudo ufw allow samba
fi

LOCAL_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "==> Share is live:"
echo "    Windows:  \\\\${LOCAL_IP}\\shared"
echo "    Linux:    //${LOCAL_IP}/shared"
echo "    Mac:      smb://${LOCAL_IP}/shared"
echo "    Dirs:     drop/  data/  exchange/"
