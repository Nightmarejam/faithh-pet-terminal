# Gen8 ChromaDB Backup Setup

**Date:** 2026-01-18  
**Server:** Gen8 (servicebox.taileb8c60.ts.net)  
**Service:** ChromaDB  
**Purpose:** Automated daily backups with 7-day retention  

---

## Overview

Automated backup system for ChromaDB data running on Gen8 server. The system creates daily compressed backups at 3 AM and maintains a 7-day rolling backup window.

---

## Files Created

### Backup Script
**Location:** `~/services/chromadb/backup.sh`
**Permissions:** `755` (executable)
**Size:** 1,530 bytes

### Cron Job
**Schedule:** Daily at 3:00 AM
**Command:** `/home/jonat/services/chromadb/backup.sh >> /home/jonat/services/chromadb/backup.log 2>&1`

---

## Backup Script Features

### Core Functionality
1. **Stop ChromaDB Container** - Graceful shutdown before backup
2. **Compress Data** - Creates timestamped tar.gz archive
3. **Restart Container** - Restarts ChromaDB after backup
4. **Health Check** - Verifies container is running
5. **Cleanup** - Removes backups older than 7 days
6. **Logging** - Timestamped output to backup.log

### Safety Features
- `set -e` - Exit on any error
- Container state verification
- Error handling with exit codes
- Wait periods for graceful shutdown/startup

---

## Directory Structure

```
~/services/chromadb/
├── backup.sh              # Main backup script
├── backup.log             # Execution log (created automatically)
├── docker-compose.yml     # ChromaDB service definition
├── data/                  # ChromaDB data directory
└── backups/               # Backup storage (created automatically)
    └── chromadb_backup_YYYY-MM-DD_HH-MM-SS.tar.gz
```

---

## Configuration

### Backup Settings
- **Retention:** 7 days (configurable via `RETENTION_DAYS`)
- **Compression:** gzip (tar.gz)
- **Schedule:** Daily 3:00 AM
- **Container Name:** `chromadb`

### Paths
- **Data Source:** `~/services/chromadb/data/`
- **Backup Target:** `~/services/chromadb/backups/`
- **Log File:** `~/services/chromadb/backup.log`

---

## Usage

### Manual Backup
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
cd ~/services/chromadb
./backup.sh
```

### View Backups
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
ls -la ~/services/chromadb/backups/
```

### View Logs
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
tail -f ~/services/chromadb/backup.log
```

### Restore from Backup
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
cd ~/services/chromadb
docker-compose stop chromadb
rm -rf data/*
tar -xzf backups/chromadb_backup_YYYY-MM-DD_HH-MM-SS.tar.gz -C data/
docker-compose start chromadb
```

---

## Cron Job Details

### Current Crontab
```bash
0 3 * * * /home/jonat/services/chromadb/backup.sh >> /home/jonat/services/chromadb/backup.log 2>&1
```

### Cron Schedule Breakdown
- **Minute:** 0 (top of hour)
- **Hour:** 3 (3 AM)
- **Day:** * (every day)
- **Month:** * (every month)
- **Weekday:** * (every day)

---

## Monitoring

### Check Last Backup
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
ls -lt ~/services/chromadb/backups/ | head -2
```

### Check Backup Size
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
du -sh ~/services/chromadb/backups/
```

### Verify Cron Job
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
crontab -l
```

---

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure backup.sh is executable: `chmod +x backup.sh`

2. **Container Won't Stop**
   - Check container status: `docker-compose ps`
   - Force stop: `docker-compose stop chromadb`

3. **Disk Space**
   - Monitor backup directory size
   - Adjust retention if needed

4. **Cron Not Running**
   - Check cron service: `systemctl status cron`
   - View cron logs: `grep CRON /var/log/syslog`

---

## Security Considerations

- SSH key authentication required (`servicebox_ed25519`)
- Backups stored locally on Gen8 server
- No external transmission of data
- File permissions: 755 (script), 644 (backups)

---

## Performance Impact

- **Downtime:** ~15 seconds per backup (stop + restart)
- **Storage:** Variable based on ChromaDB data size
- **CPU:** Minimal (gzip compression)
- **Network:** None (local operations only)

---

## Future Enhancements

Potential improvements for consideration:
1. Remote backup to separate storage
2. Backup verification/integrity checks
3. Email notifications on backup failure
4. Incremental backups for large datasets
5. Backup rotation with monthly archives

---

## Setup Verification

✅ **Completed Tasks:**
- [x] Backup script created and made executable
- [x] Cron job scheduled for 3 AM daily
- [x] 7-day retention policy configured
- [x] Logging configured
- [x] Directory structure verified

---

**Setup Complete:** 2026-01-18  
**Status:** Automated backups active  
**Next Backup:** 3:00 AM (next occurrence)
