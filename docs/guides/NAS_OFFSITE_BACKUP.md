# NAS Backup Setup

**Last Updated:** 2026-03-15

## Why

3TB of data on one drive = single point of failure.
Backup protects against NAS failure. Offsite backup also protects against theft/fire.

---

## Option 1: Local Backup to D: Drive (FREE)

**Best for:** Immediate protection, no monthly cost, fast restore

### Setup via robocopy (Windows)

```powershell
# Create backup folder
mkdir D:\NAS_Backup

# Sync priority folders (run periodically or schedule)
robocopy \\192.158.1.65\Personal\documents D:\NAS_Backup\documents /MIR /R:3 /W:5
robocopy \\192.158.1.65\Personal\photos D:\NAS_Backup\photos /MIR /R:3 /W:5
robocopy \\192.158.1.65\Audio\tomcat D:\NAS_Backup\audio-tomcat /MIR /R:3 /W:5
robocopy \\192.158.1.65\AI\projects D:\NAS_Backup\ai-projects /MIR /R:3 /W:5
```

### Setup via rsync (WSL)

```bash
# Sync from NAS mount to D: drive
rsync -avh --progress /mnt/x/Personal/documents/ /mnt/d/NAS_Backup/documents/
rsync -avh --progress /mnt/x/Personal/photos/ /mnt/d/NAS_Backup/photos/
rsync -avh --progress /mnt/x/Audio/tomcat/ /mnt/d/NAS_Backup/audio-tomcat/
```

### Scheduled Task (Windows)

1. Open Task Scheduler
2. Create Basic Task → "NAS Backup"
3. Trigger: Weekly (Sunday 3 AM)
4. Action: Start a program
5. Program: `robocopy`
6. Arguments: `\\192.158.1.65\Personal\documents D:\NAS_Backup\documents /MIR /R:3 /W:5`

**D: Drive Space:** 930GB free ✓

**Limitation:** Not offsite — fire/theft affects both NAS and PC

---

## Option 2: Backblaze B2 (Cloud - ~$18/month for 3TB)

**Best for:** True offsite protection, disaster recovery

### Tool: rclone

Already installed on NAS at `/volume1/@appstore/rclone/bin/rclone` (v1.73.0)

### Costs

- $0.006/GB/month storage
- 3TB = ~$18/month
- Free egress up to 3x storage amount
- Signup: https://www.backblaze.com/cloud-storage

### Setup Steps

#### 1. Create Backblaze B2 Account

1. Go to https://www.backblaze.com/cloud-storage
2. Create account
3. Create a bucket called `jonathan-nas-backup`
4. Go to App Keys → Create Application Key
5. Save the Key ID and Application Key

#### 2. Configure rclone on NAS

```bash
ssh nas
/volume1/@appstore/rclone/bin/rclone config

# Interactive prompts:
# n) New remote
# name> b2backup
# Storage> b2 (Backblaze B2)
# account> YOUR_KEY_ID
# key> YOUR_APPLICATION_KEY
# hard_delete> (leave default)
# q) Quit config
```

#### 3. Test Connection

```bash
ssh nas '/volume1/@appstore/rclone/bin/rclone ls b2backup:jonathan-nas-backup'
```

#### 4. Initial Sync

```bash
ssh nas '/volume1/@appstore/rclone/bin/rclone sync /volume1/Personal/documents \
  b2backup:jonathan-nas-backup/documents --progress'
ssh nas '/volume1/@appstore/rclone/bin/rclone sync /volume1/Personal/photos \
  b2backup:jonathan-nas-backup/photos --progress'
ssh nas '/volume1/@appstore/rclone/bin/rclone sync /volume1/Audio/tomcat \
  b2backup:jonathan-nas-backup/audio-tomcat --progress'
```

---

## What to Backup

### Priority 1 (Irreplaceable) - ~150GB

| Path | Size | Content |
|------|------|---------|
| /volume1/Personal/documents | 19GB | Tax returns, legal docs |
| /volume1/Personal/photos | 70GB | Personal photos |
| /volume1/Audio/tomcat | 128GB | Music production |
| /volume1/AI/projects | ~5GB | Code, configs |

### Priority 2 (Can be re-downloaded) - Skip

| Path | Reason |
|------|--------|
| /volume1/AI/media | Re-downloadable via TorBox |
| /volume1/Backups/legacy | Old backups, lower priority |
| /volume1/AI/knowledge | Books are replaceable |
| /volume1/AI/models | Re-downloadable from HuggingFace |

## Automated Daily Backup

Add to NAS Task Scheduler (DSM → Control Panel → Task Scheduler):

```bash
# Create script on NAS
ssh nas 'cat > /volume1/AI/scripts/daily_backup.sh << "EOF"
#!/bin/bash
RCLONE=/volume1/@appstore/rclone/bin/rclone
LOG=/volume1/AI/logs/rclone_$(date +%Y%m%d).log

echo "=== Backup started $(date) ===" >> $LOG

$RCLONE sync /volume1/Personal/documents b2backup:jonathan-nas-backup/documents >> $LOG 2>&1
$RCLONE sync /volume1/Personal/photos b2backup:jonathan-nas-backup/photos >> $LOG 2>&1
$RCLONE sync /volume1/Audio/tomcat b2backup:jonathan-nas-backup/audio-tomcat >> $LOG 2>&1

echo "=== Backup completed $(date) ===" >> $LOG
EOF
chmod +x /volume1/AI/scripts/daily_backup.sh'
```

Then in DSM Task Scheduler:
- Create → Scheduled Task → User-defined script
- Schedule: Daily at 3:00 AM
- Run command: `/volume1/AI/scripts/daily_backup.sh`

## Estimated Costs

| Data Size | Monthly Cost | Annual Cost |
|-----------|--------------|-------------|
| 150GB | $0.90 | $10.80 |
| 500GB | $3.00 | $36.00 |
| 1TB | $6.00 | $72.00 |

## Restore Commands

```bash
# List remote contents
ssh nas '/volume1/@appstore/rclone/bin/rclone ls b2backup:jonathan-nas-backup/documents'

# Restore single file
ssh nas '/volume1/@appstore/rclone/bin/rclone copy \
  b2backup:jonathan-nas-backup/documents/important.pdf \
  /volume1/Personal/documents/'

# Restore entire folder
ssh nas '/volume1/@appstore/rclone/bin/rclone sync \
  b2backup:jonathan-nas-backup/photos \
  /volume1/Personal/photos_restored/'
```

## DS220j Philosophy

The NAS has 512MB RAM — it's a storage device, not a compute node.
rclone sync runs fine but don't run multiple heavy operations simultaneously.
Schedule backups during off-hours (3 AM) when NAS isn't serving files.
