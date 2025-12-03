# FAITHH Backend - Quick Reference
**Easy commands for managing the backend**

---

## 🚀 Start Backend (Clean)

```bash
cd ~/ai-stack
chmod +x restart_backend.sh
./restart_backend.sh
```

**What it does**:
1. Stops all running instances gracefully
2. Frees port 5557
3. Starts fresh backend
4. Verifies it's working
5. Shows you the UI link

**Use when**:
- Starting FAITHH for the day
- Backend seems stuck
- Port already in use error
- Want to ensure clean state

---

## 🛑 Stop Backend (Clean)

```bash
cd ~/ai-stack
chmod +x stop_backend.sh
./stop_backend.sh
```

**What it does**:
1. Finds all backend instances
2. Sends graceful shutdown (SIGTERM)
3. Waits 3 seconds
4. Force kills if needed (SIGKILL)
5. Confirms all stopped

**Use when**:
- Done working for the day
- Need to update backend code
- System feels sluggish
- Before restarting

---

## ✅ Check Status

```bash
# Quick check (is it running?)
curl http://localhost:5557/health

# Detailed status
curl http://localhost:5557/api/status | python3 -m json.tool

# Check integrations
curl http://localhost:5557/api/test_integrations | python3 -m json.tool
```

---

## 📊 Monitor Logs

```bash
# Watch live logs
tail -f ~/ai-stack/backend.log

# View recent logs
tail -50 ~/ai-stack/backend.log

# Search logs for errors
grep ERROR ~/ai-stack/backend.log
```

---

## 🔧 Common Issues

### "Address already in use" Error

**Problem**: Another instance is using port 5557

**Solution**:
```bash
./restart_backend.sh
```

This handles it automatically.

---

### Backend Won't Start

**Check the logs**:
```bash
cat ~/ai-stack/backend.log
```

**Common causes**:
- ChromaDB not running (start it: `docker compose up -d`)
- Python virtual environment not activated (`source venv/bin/activate`)
- Missing dependencies (`pip install -r requirements.txt`)

---

### Backend Running But Not Responding

**Check if process is alive**:
```bash
ps aux | grep faithh_professional_backend
```

**Check port**:
```bash
lsof -i :5557
```

**Restart**:
```bash
./restart_backend.sh
```

---

### Want to See What's Running

```bash
# Show all FAITHH processes
ps aux | grep faithh

# Show what's on port 5557
lsof -i :5557

# Show backend status with PID
pgrep -fl faithh_professional_backend
```

---

## 🎯 Daily Workflow

**Morning** (start working):
```bash
cd ~/ai-stack
./restart_backend.sh
# Open http://localhost:5557 in browser
```

**During day** (if issues):
```bash
./restart_backend.sh  # Quick reset
```

**Evening** (done working):
```bash
./stop_backend.sh  # Clean shutdown
```

**Or just leave it running** - it's fine!

---

## 🔍 Debugging Commands

**Is ChromaDB running?**
```bash
docker ps | grep chroma
curl http://localhost:8000/api/v1/heartbeat
```

**Is Ollama running?**
```bash
curl http://localhost:11434/api/tags
```

**What ports are in use?**
```bash
lsof -i :5557  # Backend
lsof -i :8000  # ChromaDB
lsof -i :11434 # Ollama
```

**Kill everything and start fresh**:
```bash
./stop_backend.sh
docker compose down
docker compose up -d
sleep 5
./restart_backend.sh
```

---

## 💡 Pro Tips

1. **Use the scripts** - They handle edge cases
   - `./restart_backend.sh` for starting
   - `./stop_backend.sh` for stopping

2. **Check logs when confused**
   - `tail -f ~/ai-stack/backend.log`
   - Logs show intent detection and context building

3. **Don't manually kill processes**
   - Let scripts do it gracefully
   - Prevents zombie processes

4. **Leave backend running**
   - It's fine to keep it up
   - Only restart if having issues

5. **Monitor the first startup**
   - Watch for ✅ symbols
   - Should show 3 integrations loaded

---

## 📁 Important Files

```
~/ai-stack/
├── faithh_professional_backend_fixed.py  # Main backend (v3.2)
├── restart_backend.sh                    # Start/restart script
├── stop_backend.sh                       # Stop script
├── backend.log                           # Runtime logs
├── faithh_memory.json                    # User memory
├── decisions_log.json                    # Decision history
└── project_states.json                   # Project tracking
```

---

## 🆘 If All Else Fails

**Nuclear option** (start completely fresh):

```bash
cd ~/ai-stack

# Stop everything
./stop_backend.sh
pkill -9 -f faithh  # Force kill anything FAITHH-related
docker compose down

# Wait
sleep 5

# Start ChromaDB
docker compose up -d
sleep 3

# Start backend
./restart_backend.sh
```

**Then check**: http://localhost:5557

---

## ✅ Success Checklist

Backend is healthy when:
- [ ] `./restart_backend.sh` shows all ✅ green checks
- [ ] http://localhost:5557 loads the UI
- [ ] `curl http://localhost:5557/health` returns JSON
- [ ] Logs show "INTEGRATED" and 3 integrations
- [ ] No "Address already in use" errors

---

**Keep this file handy** - bookmark or pin it!

---

*Last updated: 2025-11-27*
