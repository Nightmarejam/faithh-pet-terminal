# Gen8 Resource Monitoring Setup

**Date:** 2026-01-18  
**Server:** Gen8 (servicebox - servicebox.taileb8c60.ts.net)  
**Purpose:** Lightweight resource monitoring with hourly logging  

---

## Overview

Automated resource monitoring system tracking CPU, RAM, and disk usage on Gen8 server. Provides historical data for capacity planning and performance analysis.

---

## Files Created

### Monitoring Script
**Location:** `~/services/monitoring/check_resources.sh`
**Permissions:** `755` (executable)
**Purpose:** Collect and log system resource metrics

### Configuration Files
- **Log Rotation:** `~/services/monitoring/logrotate.conf`
- **Cron Job:** Hourly execution via system crontab

---

## Script Functionality

### Metrics Collected
- **CPU Usage:** Average utilization (1-minute sample)
- **RAM Usage:** Memory percentage used
- **Disk Usage:** 
  - Root filesystem (`/`)
  - Home directory (`/home`)

### Output Format
```
[TIMESTAMP] CPU: X% | RAM: Y% | DISK(/): Z% | DISK(/home): W%
```

**Example:**
```
[2026-01-19 08:01:13] CPU: 1.6% | RAM: 38.3% | DISK(/): 3% | DISK(/home): 3%
```

---

## Configuration Details

### Cron Job Schedule
```bash
0 * * * * /home/jonat/services/monitoring/check_resources.sh
```
- **Frequency:** Every hour at minute 0
- **User:** jonat
- **Execution:** Direct script run

### Log Rotation
```bash
~/services/monitoring/resource_usage.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 jonat jonat
}
```

**Retention Policy:**
- Keep last 30 days of logs
- Compress logs older than 1 day
- Skip empty/missing logs
- Maintain file permissions

---

## Directory Structure

```
~/services/monitoring/
├── check_resources.sh          # Main monitoring script
├── logrotate.conf             # Log rotation rules
└── resource_usage.log         # Current log file
```

---

## Usage Commands

### Check Current Stats
```bash
# Run script manually for immediate reading
~/services/monitoring/check_resources.sh

# View latest log entries
tail -5 ~/services/monitoring/resource_usage.log
```

### View Historical Trends
```bash
# Last 24 hours (24 entries)
tail -24 ~/services/monitoring/resource_usage.log

# Search for high CPU usage (>80%)
grep "CPU: [8-9][0-9]%" ~/services/monitoring/resource_usage.log

# Daily averages (basic)
awk '{print $1" "$2}' ~/services/monitoring/resource_usage.log | sort | uniq -c
```

### Log Management
```bash
# Check log file size
du -sh ~/services/monitoring/resource_usage.log

# Manual log rotation (if needed)
logrotate -f ~/services/monitoring/logrotate.conf

# List compressed logs
ls -la ~/services/monitoring/*.gz
```

---

## Performance Impact

### Resource Usage
- **CPU:** Minimal (brief top/free/df commands)
- **RAM:** Negligible (<1MB per execution)
- **Disk:** ~1KB per hour (24KB/day)
- **Network:** None (local operations only)

### Storage Requirements
- **Daily:** ~24KB of log data
- **Monthly:** ~720KB (uncompressed)
- **With compression:** ~200KB/month
- **30-day retention:** ~6MB total

---

## Monitoring Examples

### Current Status Check
```bash
ssh jonat@servicebox.taileb8c60.ts.net "~/services/monitoring/check_resources.sh"
# Output: [2026-01-19 08:01:13] CPU: 1.6% | RAM: 38.3% | DISK(/): 3% | DISK(/home): 3%
```

### Historical Analysis
```bash
# Peak CPU usage in last 24 hours
ssh jonat@servicebox.taileb8c60.ts.net "tail -24 ~/services/monitoring/resource_usage.log" | \
  awk -F'CPU: |%' '{print $2}' | sort -n | tail -1

# Memory trend analysis
ssh jonat@servicebox.taileb8c60.ts.net "tail -24 ~/services/monitoring/resource_usage.log" | \
  awk -F'RAM: |%' '{print $2}' | sort -n
```

### Alert Thresholds (Manual)
```bash
# Check for concerning values
ssh jonat@servicebox.taileb8c60.ts.net "tail -1 ~/services/monitoring/resource_usage.log" | \
  grep -E "CPU: [9][0-9]%|RAM: [9][0-9]%|DISK.+: [9][0-9]%"
```

---

## Integration with Uptime Kuma

### Recommended Monitors
1. **CPU Usage Monitor**
   - URL: Custom HTTP API (if you create one)
   - Method: Parse log file for latest CPU value
   - Threshold: Warning at 80%, Critical at 90%

2. **Disk Space Monitor**
   - URL: Custom HTTP API (if you create one)
   - Method: Parse log file for latest disk values
   - Threshold: Warning at 80%, Critical at 90%

3. **Log File Freshness**
   - URL: Check file modification time
   - Method: Verify log updated within last 2 hours
   - Threshold: Alert if log is stale

---

## Troubleshooting

### Common Issues

1. **Script Not Running**
   - Check cron: `crontab -l`
   - Check script permissions: `ls -la ~/services/monitoring/check_resources.sh`
   - Check cron logs: `grep CRON /var/log/syslog`

2. **Log File Not Created**
   - Verify directory exists: `ls -la ~/services/monitoring/`
   - Check write permissions: `touch ~/services/monitoring/test.log`
   - Run script manually: `~/services/monitoring/check_resources.sh`

3. **Incorrect Paths**
   - Verify absolute paths in script
   - Check home directory: `echo $HOME`
   - Test commands individually: `top -bn1`, `free`, `df /`

### Debug Commands
```bash
# Test individual components
ssh jonat@servicebox.taileb8c60.ts.net "top -bn1 | grep 'Cpu(s)'"
ssh jonat@servicebox.taileb8c60.ts.net "free | grep Mem"
ssh jonat@servicebox.taileb8c60.ts.net "df / | tail -1"

# Verify cron execution
ssh jonat@servicebox.taileb8c60.ts.net "ps aux | grep check_resources"

# Check system logs for cron errors
ssh jonat@servicebox.taileb8c60.ts.net "sudo grep CRON /var/log/syslog | tail -5"
```

---

## Future Enhancements

### Potential Improvements
1. **Alert System**: Email/webhook notifications for threshold breaches
2. **Web Dashboard**: Simple web interface for historical visualization
3. **API Endpoint**: HTTP endpoint for Uptime Kuma integration
4. **Additional Metrics**: Network usage, temperature, service-specific stats
5. **Automated Reports**: Weekly/monthly summary reports

### Implementation Ideas
- Python script with more sophisticated analysis
- Integration with existing monitoring tools
- Database storage for complex queries
- Grafana dashboard for visualization

---

## Verification Checklist

- [x] Monitoring directory created
- [x] Script created and executable
- [x] Cron job scheduled (hourly)
- [x] Log rotation configured
- [x] Manual test successful
- [x] Log file creation verified
- [x] Output format confirmed
- [x] Documentation complete

---

**Setup Complete:** 2026-01-18  
**Status:** Monitoring active and logging hourly  
**Next Review:** Check log accumulation after 24 hours
