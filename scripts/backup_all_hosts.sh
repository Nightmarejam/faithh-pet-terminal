#!/bin/bash
# backup_all_hosts.sh
# Backs up all hosts to NAS
# Run manually or via cron
# Updated: 2026-05-05

set -euo pipefail

# --- Config ---
NAS_BACKUP="/mnt/nas/media/backups"
DATE=$(date +%F)
TIMESTAMP=$(date +%F-%H%M%S)
LOG="$NAS_BACKUP/backup.log"

# --- Hosts ---
PVE_HOST="root@pve"
FAITHH_HOST="jonat@faithh.taileb8c60.ts.net"

# --- Logging ---
log() {
  echo "[$(date +%F\ %T)] $1" | tee -a "$LOG"
}

log "===== Backup started ====="

# --- 1. Verify NAS is mounted ---
if ! mountpoint -q /mnt/nas/media; then
  log "ERROR: NAS not mounted at /mnt/nas/media — aborting"
  exit 1
fi

# --- 2. Create directory structure ---
mkdir -p "$NAS_BACKUP"/{pve,vm-configs,ai-stack,faithh-vm,crypto,system}
log "Backup directories confirmed"

# --- 3. Proxmox VM configs ---
log "Backing up Proxmox VM configs..."
ssh "$PVE_HOST" "cat /etc/pve/qemu-server/100.conf" \
  > "$NAS_BACKUP/vm-configs/vm100_$DATE.conf"
ssh "$PVE_HOST" "cat /etc/pve/qemu-server/101.conf" \
  > "$NAS_BACKUP/vm-configs/vm101_$DATE.conf"

# Full PVE config snapshot
ssh "$PVE_HOST" "tar czf - /etc/pve/ 2>/dev/null" \
  > "$NAS_BACKUP/pve/pve_etc_$TIMESTAMP.tar.gz"
log "Proxmox configs backed up"

# --- 4. Gen8 ai-stack git bundle ---
log "Backing up Gen8 ai-stack..."
cd ~/ai-stack
git bundle create "$NAS_BACKUP/ai-stack/ai-stack_$TIMESTAMP.bundle" --all
log "ai-stack bundle written"

# --- 5. FAITHH VM ai-stack ---
log "Backing up FAITHH VM ai-stack..."
ssh "$FAITHH_HOST" "cd ~/ai-stack && git bundle create /tmp/faithh_ai-stack_$TIMESTAMP.bundle --all 2>/dev/null && cat /tmp/faithh_ai-stack_$TIMESTAMP.bundle && rm /tmp/faithh_ai-stack_$TIMESTAMP.bundle" \
  > "$NAS_BACKUP/faithh-vm/faithh_ai-stack_$TIMESTAMP.bundle"
log "FAITHH VM ai-stack bundle written"

# --- 6. Gen8 system configs ---
log "Backing up Gen8 system configs..."
cp /etc/fstab "$NAS_BACKUP/system/gen8_fstab_$DATE"
crontab -l > "$NAS_BACKUP/system/gen8_crontab_$DATE" 2>/dev/null || true
log "Gen8 system configs backed up"

# --- 7. Crypto pipeline data snapshot ---
log "Backing up crypto pipeline data..."
tar czf "$NAS_BACKUP/crypto/prices_$DATE.tar.gz" \
  ~/ai-stack/projects/crypto/data/prices/ 2>/dev/null || true
log "Crypto data backed up"

# --- 8. Rotate old backups (keep 7 days) ---
log "Rotating old backups..."
find "$NAS_BACKUP/vm-configs" -name "*.conf" -mtime +7 -delete 2>/dev/null || true
find "$NAS_BACKUP/ai-stack" -name "*.bundle" -mtime +7 -delete 2>/dev/null || true
find "$NAS_BACKUP/faithh-vm" -name "*.bundle" -mtime +7 -delete 2>/dev/null || true
find "$NAS_BACKUP/pve" -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true
find "$NAS_BACKUP/crypto" -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true
log "Old backups rotated (kept last 7 days)"

log "===== Backup complete ====="
echo ""
echo "Backup log: $LOG"
echo "NAS space remaining:"
df -h /mnt/nas/media | tail -1
