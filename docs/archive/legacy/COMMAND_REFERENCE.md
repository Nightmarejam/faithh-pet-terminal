# 📋 FAITHH Command Reference Card

## 🚀 Quick Commands

### Setup
```bash
cd ~/ai-stack
bash install_deps.sh              # Install dependencies
```

### Testing
```bash
python3 test_e2e.py               # Run all tests (should pass)
python3 test_tool_executor.py     # Unit tests only
```

### Running
```bash
python3 faithh_api_websocket.py   # Start server (port 5555)
```

### Checking
```bash
curl http://localhost:5555/api/status           # Check status
curl http://localhost:5555                       # API info
```

---

## 🔌 WebSocket Commands

### Connect
```javascript
const ws = new WebSocket('ws://localhost:5555/ws/tools');
```

### Execute Tool
```javascript
ws.send(JSON.stringify({
  action: 'execute_tool',
  tool_name: 'read_file',
  parameters: { path: '/tmp/test.txt' },
  permissions: ['file.read']
}));
```

### List Tools
```javascript
ws.send(JSON.stringify({ action: 'list_tools' }));
```

### Ping
```javascript
ws.send(JSON.stringify({ action: 'ping' }));
```

---

## 🔨 Available Tools

| Tool | Parameters | Permissions |
|------|-----------|-------------|
| `read_file` | `{path}` | `file.read` |
| `write_file` | `{path, content, mode}` | `file.write` |
| `run_command` | `{command, timeout}` | `process.execute` |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `faithh_api_websocket.py` | Main server (START HERE) |
| `tool_executor.py` | Core engine |
| `config.yaml` | Configuration |
| `test_e2e.py` | Tests (RUN FIRST) |
| `README.md` | Project overview |
| `QUICKSTART.md` | Detailed guide |

---

## 🐛 Troubleshooting

**Tests fail?**
```bash
pip install -r requirements.txt
python3 test_e2e.py
```

**Port in use?**
- Edit line 218 in `faithh_api_websocket.py`
- Change port from 5555 to something else

**Permission denied?**
- Check `config.yaml` → `security.allowed_directories`
- Make sure paths are absolute
- Add needed directories to allowed list

**Import errors?**
```bash
cd ~/ai-stack
pip install flask flask-cors flask-sock google-generativeai pyyaml
```

---

## 📚 Documentation Quick Links

- **Quick Start**: `QUICKSTART.md` (179 lines)
- **Full Status**: `FINAL_STATUS.md` (274 lines)
- **Architecture**: `ARCHITECTURE.md` (174 lines)
- **Completion**: `COMPLETION_CHECKLIST.md` (287 lines)

---

## ✅ Verification Checklist

```bash
# 1. Check files exist
ls tool_executor.py executors/*.py faithh_api_websocket.py

# 2. Run tests
python3 test_e2e.py
# Should see: "ALL TESTS PASSED"

# 3. Start server
python3 faithh_api_websocket.py
# Should start on port 5555

# 4. Test API
curl http://localhost:5555/api/status
# Should return JSON
```

---

## 🎯 Common Tasks

### Add New Tool
```python
# In faithh_api_websocket.py or separate file:
tool_registry.register_tool({
    'name': 'my_tool',
    'description': 'Does something',
    'category': 'custom',
    'executor': 'custom',
    'permissions': ['custom.use']
})
```

### Change Security Settings
Edit `config.yaml`:
```yaml
security:
  allowed_directories:
    - /your/path/here
  blocked_commands:
    - dangerous_command
```

### Test Specific Tool
```bash
# In Python:
import asyncio
from tool_executor import get_executor

executor = get_executor()
result = asyncio.run(
    executor.execute_tool('read_file', 
                         {'path': '/tmp/test.txt'})
)
print(result)
```

---

## 🚨 Emergency Commands

### Kill Server
```bash
# Find process
ps aux | grep faithh_api_websocket

# Kill it
kill <PID>

# Or use Ctrl+C in terminal
```

### Reset Everything
```bash
cd ~/ai-stack
rm -rf __pycache__ executors/__pycache__
pip install -r requirements.txt --force-reinstall
python3 test_e2e.py
```

### Check Logs
Server runs with debug=True, logs print to console

---

## 💡 Pro Tips

1. **Always test first**: `python3 test_e2e.py`
2. **Use absolute paths**: Not relative ones
3. **Check permissions**: If tool fails, check config.yaml
4. **WebSocket errors**: Look at browser console
5. **Server issues**: Check if port 5555 is free

---

## 📞 Quick Help

**Problem**: Tests fail  
**Solution**: `bash install_deps.sh && python3 test_e2e.py`

**Problem**: Can't connect WebSocket  
**Solution**: Check server is running on port 5555

**Problem**: Permission denied  
**Solution**: Add path to `config.yaml` allowed_directories

**Problem**: Tool not found  
**Solution**: Check tool is registered in registry

---

## 🎉 Success Indicators

✅ `test_e2e.py` passes all tests  
✅ Server starts without errors  
✅ Can curl `/api/status` and get response  
✅ WebSocket connects successfully  

**If all above work → System is functional!** 🚀

---

*Keep this card handy for quick reference!*
