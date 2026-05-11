# Windsurf Task: Gen8 Resource Monitoring Script

## Objective
Create a lightweight resource monitoring script on Gen8 that tracks CPU, RAM, and disk usage.

## Requirements
- SSH to Gen8: `ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243`
- Create script at: `~/services/monitoring/check_resources.sh`
- Log to: `~/services/monitoring/resource_usage.log`
- Track: CPU %, RAM %, Disk % for / and /home
- Include timestamp with each entry
- Keep last 30 days of logs (auto-rotate)

## Implementation Steps

1. **Create monitoring directory**
   ```bash
   mkdir -p ~/services/monitoring
   ```

2. **Create resource check script** (`~/services/monitoring/check_resources.sh`)
   - Use `top`, `free`, `df` commands
   - Output format: `[TIMESTAMP] CPU: X% | RAM: Y% | DISK(/): Z% | DISK(/home): W%`
   - Append to resource_usage.log

3. **Add cron job for hourly monitoring**
   ```bash
   0 * * * * /home/jonat/services/monitoring/check_resources.sh
   ```

4. **Create log rotation rule**
   - Keep last 30 days
   - Compress old logs

5. **Test the script** (run once manually)
   - Verify output format
   - Check log file creation

6. **Document in** `docs/GEN8_MONITORING_SETUP.md`
   - Script location
   - Log location
   - How to check current stats
   - How to view historical trends

## Success Criteria
- Script runs without errors
- Log file updates with current stats
- Cron job scheduled
- Documentation created

**Then STOP and report.**
