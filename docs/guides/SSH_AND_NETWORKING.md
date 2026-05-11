# SSH Hub - Quick Setup Guide

**Created:** January 26, 2026  
**Purpose:** Easy access to all your devices with persistent SSH sessions

---

## 🎯 What You Have Now

### ✅ SSH Config Updated
Location: `~/.ssh/config`

You can now connect to any device using simple aliases:

```bash
# Gen8 Server
ssh gen8              # Via Tailscale (preferred)
ssh gen8-local        # Via local network

# Synology NAS
ssh nas

# MacBook Pro M1
ssh mac

# UniFi Dream Machine
ssh unifi

# Gitea
ssh gitea
```

### ✅ SSH Hub Script Created
Location: `~/ai-stack/scripts/ssh_hub.sh`

This gives you a menu-based interface to connect to all devices.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Make Script Executable
```bash
cd ~/ai-stack/scripts
chmod +x ssh_hub.sh
```

### Step 2: Install tmux (for persistent sessions)
```bash
sudo apt install tmux -y
```

### Step 3: Run the SSH Hub
```bash
~/ai-stack/scripts/ssh_hub.sh
```

Or create an alias in your `~/.bashrc`:
```bash
echo "alias sshhub='~/ai-stack/scripts/ssh_hub.sh'" >> ~/.bashrc
source ~/.bashrc
```

Then just type: `sshhub`

---

## 📱 What Each Device Needs

### Gen8 Server ✅
**Status:** Ready to use!  
**Connection:** `ssh gen8`  
**Key:** Already set up (`~/.ssh/servicebox_ed25519`)

### Synology NAS ⚠️
**Status:** Needs SSH key setup  
**Connection:** `ssh nas` (will ask for password)  
**To set up key:**
1. SSH to NAS: `ssh nas`
2. On NAS: `mkdir -p ~/.ssh && chmod 700 ~/.ssh`
3. From your PC: `ssh-copy-id nas`

### MacBook Pro M1 ⚠️
**Status:** Needs Remote Login enabled  
**Connection:** `ssh mac`  
**To enable:**
1. On Mac: System Preferences → Sharing
2. Enable "Remote Login"
3. Add your user to allowed users
4. From PC: `ssh-copy-id mac`

### UniFi Dream Machine ⚠️
**Status:** Needs SSH enabled  
**Connection:** `ssh unifi`  
**To enable:**
1. UniFi Controller → Settings → System
2. Enable "SSH"
3. Set password or use key auth

---

## 🔑 SSH Key Setup (One-Time)

If you need to create SSH keys for devices that don't have them:

```bash
# For NAS
ssh-keygen -t ed25519 -f ~/.ssh/synology_ed25519 -C "jonat@nas"

# For Mac
ssh-keygen -t ed25519 -f ~/.ssh/mac_ed25519 -C "jonat@mac"

# Then copy to device
ssh-copy-id -i ~/.ssh/synology_ed25519 nas
ssh-copy-id -i ~/.ssh/mac_ed25519 mac
```

---

## 💡 Using tmux for Persistent Sessions

### What is tmux?
tmux lets you keep SSH sessions running even if you disconnect. Perfect for long-running tasks!

### Basic tmux Commands
```bash
# Create new session
tmux new -s mysession

# Detach from session (keeps it running)
Ctrl+b, then d

# List sessions
tmux ls

# Attach to session
tmux attach -t mysession

# Kill session
tmux kill-session -t mysession
```

### The SSH Hub Does This Automatically!
When you connect via the SSH hub script, it automatically:
- Creates a tmux session for each device
- Lets you detach and reattach anytime
- Keeps your sessions alive

---

## 🎨 SSH Hub Features

### Menu Interface
```
╔════════════════════════════════════════════════════════╗
║           SSH HUB - Device Manager                     ║
╚════════════════════════════════════════════════════════╝

Device Status:
● Gen8 Server (Tailscale)
● Gen8 Server (Local)
● Synology NAS (offline)
● MacBook Pro M1
● UniFi Dream Machine

Select a device to connect:

  1) Gen8 Server (Tailscale) - Main access
  2) Gen8 Server (Local) - Backup route
  3) Synology NAS - File storage
  4) MacBook Pro M1 - Mobile workstation
  5) UniFi Dream Machine - Network admin

  6) List all active tmux sessions
  7) Kill a tmux session

  q) Quit
```

### Real-time Status
- Green ● = Device online
- Red ● = Device offline
- Automatically checks before connecting

### Session Management
- Each device gets its own tmux session
- Sessions persist even if you close the hub
- Reconnect anytime without losing your place

---

## 📋 Quick Reference

### Connect to a Device
```bash
# Method 1: Direct SSH
ssh gen8

# Method 2: Via SSH Hub
~/ai-stack/scripts/ssh_hub.sh
# Then select device from menu

# Method 3: Create tmux session manually
tmux new -s gen8 "ssh gen8"
```

### Check What's Running
```bash
# List tmux sessions
tmux ls

# List SSH connections
ps aux | grep ssh
```

### Disconnect but Keep Session Alive
```bash
# Inside tmux session
Ctrl+b, then d

# Or close terminal - session stays alive!
```

---

## 🔒 Security Notes

### Current Setup (Development Mode)
- SSH keys with no passphrase (for convenience)
- Persistent sessions (easy reconnect)
- ForwardAgent enabled (for Git operations)

### Production Mode (Future)
When you're ready to lock down:
1. Add passphrases to SSH keys
2. Disable ForwardAgent
3. Use SSH certificates instead of keys
4. Enable 2FA on devices that support it
5. Restrict SSH to specific IPs

---

## 🐛 Troubleshooting

### "Permission denied (publickey)"
```bash
# Check if key exists
ls -la ~/.ssh/

# Check SSH config
cat ~/.ssh/config

# Test connection with verbose output
ssh -v gen8
```

### "Connection refused"
```bash
# Check if device is reachable
ping 192.158.1.243

# Check if SSH port is open
nc -zv 192.158.1.243 22
```

### "tmux: command not found"
```bash
# Install tmux
sudo apt install tmux -y
```

### SSH Hub script won't run
```bash
# Make it executable
chmod +x ~/ai-stack/scripts/ssh_hub.sh

# Check if bash is available
which bash

# Run directly
bash ~/ai-stack/scripts/ssh_hub.sh
```

---

## 🎯 Next Steps

### Immediate (5 minutes)
1. Test Gen8 connection: `ssh gen8`
2. Run SSH hub: `~/ai-stack/scripts/ssh_hub.sh`
3. Create alias for quick access

### This Week
1. Enable SSH on Mac (System Preferences → Sharing)
2. Set up SSH key for NAS
3. Enable SSH on UniFi (if needed for network management)

### Future
1. Set up SSH keys for all devices
2. Configure SSH agent for key management
3. Add partner's Mac Mini when ready
4. Consider SSH jump host for external access

---

## 📞 Quick Commands Cheat Sheet

```bash
# Connect to devices
ssh gen8              # Gen8 via Tailscale
ssh nas               # Synology NAS
ssh mac               # MacBook Pro M1
ssh unifi             # UniFi Dream Machine

# SSH Hub
sshhub                # If alias is set up
~/ai-stack/scripts/ssh_hub.sh  # Full path

# tmux basics
tmux ls               # List sessions
tmux attach -t gen8   # Attach to gen8 session
Ctrl+b d              # Detach from session
tmux kill-session -t gen8  # Kill session

# Check connectivity
ping 192.158.1.243     # Gen8 (LAN)
ping 192.158.1.65     # NAS

# SSH debugging
ssh -v gen8           # Verbose output
ssh -vvv gen8         # Very verbose
```

---

**Ready to use!** Just run `~/ai-stack/scripts/ssh_hub.sh` to get started.


---

# SSH Key for Gitea

To add your SSH key to Gitea:

1. Go to: http://192.158.1.243:3002
2. Sign in with your GitHub account
3. Click on your avatar → Settings
4. Go to "SSH / GPG Keys" tab
5. Click "Add Key"
6. Paste this key:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILumrtmlOlN/Jp0cqJFbH+i8RcA3/VbtHDkD4ptK0DNr jonathan.mo1@hotmail.com
```

7. Title: "Windows Desktop"
8. Click "Add Key"

Test SSH connection:
```bash
ssh -T git@192.158.1.243 -p 2222
```
