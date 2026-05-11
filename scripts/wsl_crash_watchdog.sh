#!/bin/bash
# WSL Crash Watchdog
# Runs from Windows Task Scheduler or PowerShell — monitors FAITHH backend
# and logs crash events with timestamps and last-known state.
#
# Run from PowerShell: wsl -d Ubuntu -- bash ~/ai-stack/scripts/wsl_crash_watchdog.sh
# Or add to crontab: */2 * * * * /home/jonat/ai-stack/scripts/wsl_crash_watchdog.sh

BACKEND_URL="http://localhost:5557/health"
LOG_FILE="/home/jonat/ai-stack/logs/crash_watchdog.log"
STATE_FILE="/tmp/faithh_watchdog_state"
RESTART_SCRIPT="/home/jonat/ai-stack/restart_backend.sh"

timestamp() { date '+%Y-%m-%dT%H:%M:%S'; }

log() {
    echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

# Check if backend is responding
if curl -sf --max-time 5 "$BACKEND_URL" > /dev/null 2>&1; then
    # Backend healthy — write heartbeat
    echo "$(timestamp) OK" > "$STATE_FILE"
    exit 0
fi

# Backend not responding — log the crash event
log "CRASH_DETECTED: Backend at $BACKEND_URL not responding"
log "CRASH_CONTEXT: WSL uptime=$(uptime -p 2>/dev/null || echo unknown)"
log "CRASH_CONTEXT: Last journal entry=$(journalctl -n 1 --no-pager 2>/dev/null | tail -1 || echo unavailable)"
log "CRASH_CONTEXT: dmesg tail=$(dmesg 2>/dev/null | tail -3 | tr '\n' '|' || echo unavailable)"

# Check if this is a WSL-level crash vs just backend down
if ! pgrep -f "faithh_professional_backend" > /dev/null 2>&1; then
    log "CRASH_TYPE: Backend process gone (killed or WSL crash)"
    
    # Attempt auto-restart
    log "RECOVERY: Attempting backend restart..."
    cd /home/jonat/ai-stack && source venv/bin/activate && bash "$RESTART_SCRIPT" >> "$LOG_FILE" 2>&1
    
    if curl -sf --max-time 10 "$BACKEND_URL" > /dev/null 2>&1; then
        log "RECOVERY: Backend restored successfully"
    else
        log "RECOVERY: Backend restart failed — manual intervention needed"
    fi
else
    log "CRASH_TYPE: Backend process exists but not responding (hung?)"
    PID=$(pgrep -f "faithh_professional_backend" | head -1)
    log "CRASH_CONTEXT: PID=$PID, memory=$(ps -o rss= -p $PID 2>/dev/null || echo unknown)KB"
fi
