# Gen8 Hardening Command Pack

Use this on `gen8` over SSH. Run in order. Stop on errors and verify each step.

## 1) Identify real SSH daemon and config source

```bash
hostname
ps -ef | grep -E "sshd|openssh|s6-supervise"
sudo ss -tulpen | grep ":22 "
sudo systemctl status ssh || sudo systemctl status sshd
```

If SSH is container-managed (`s6-supervise openssh`), harden the container config path.
If host-managed (`systemd ssh/sshd`), harden `/etc/ssh/sshd_config`.

## 2) Backup SSH config before changes

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%Y%m%d_%H%M%S)
```

## 3) Enforce key-only SSH

Append or edit these directives:

```bash
sudo tee -a /etc/ssh/sshd_config >/dev/null <<'EOF'
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
MaxAuthTries 3
LoginGraceTime 30
EOF
```

Optional allowlist (recommended once verified):

```bash
echo "AllowUsers jonat" | sudo tee -a /etc/ssh/sshd_config
```

Validate and reload:

```bash
sudo sshd -t
sudo systemctl reload ssh || sudo systemctl reload sshd
```

## 4) Install and enable fail2ban

```bash
sudo apt-get update
sudo apt-get install -y fail2ban
sudo tee /etc/fail2ban/jail.local >/dev/null <<'EOF'
[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
maxretry = 5
findtime = 10m
bantime = 1h
EOF
sudo systemctl enable --now fail2ban
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

## 5) Firewall baseline (UFW)

WARNING: keep current SSH session open while applying rules.

```bash
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow from 100.64.0.0/10 to any port 22 proto tcp
sudo ufw allow from 192.168.0.0/16 to any port 22 proto tcp
sudo ufw enable
sudo ufw status verbose
```

Then explicitly restrict high-risk infra ports to LAN/Tailscale only:

```bash
for p in 3000 3001 3002 5000 5001 8000 9090 9100; do
  sudo ufw allow from 100.64.0.0/10 to any port "$p" proto tcp
  sudo ufw allow from 192.168.0.0/16 to any port "$p" proto tcp
  sudo ufw deny "$p"/tcp
done
sudo ufw status numbered
```

## 6) Verify external exposure after hardening

```bash
sudo ss -tulpen
sudo ufw status verbose
```

From a trusted client:

```bash
nc -vz servicebox.taileb8c60.ts.net 22
nc -vz servicebox.taileb8c60.ts.net 8000
nc -vz servicebox.taileb8c60.ts.net 9090
```

Expected: only explicitly allowed paths respond.

## 7) Rollback safety

If lockout occurs:

```bash
sudo cp /etc/ssh/sshd_config.bak.YYYYMMDD_HHMMSS /etc/ssh/sshd_config
sudo systemctl restart ssh || sudo systemctl restart sshd
sudo ufw disable
```
