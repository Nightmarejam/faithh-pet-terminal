# FAITHH Quick Start Guide

## ⚡ 60-Second Setup

```bash
cd ~/ai-stack

# 1. Install dependencies
bash install_deps.sh

# 2. Verify system works
python3 test_e2e.py

# 3. Start server
python3 faithh_api_websocket.py
```

## 🔌 API Endpoints

**WebSocket** (Real-time tools):
- `ws://localhost:5555/ws/tools`

**HTTP**:
- `GET  /api/status` - System health
- `POST /api/chat` - Gemini AI chat
- `GET  /` - API info

## 📝 WebSocket Example (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:5555/ws/tools');

// Execute tool
ws.send(JSON.stringify({
  action: 'execute_tool',
  tool_name: 'read_file',
  parameters: { path: '/tmp/test.txt' },
  permissions: ['file.read']
}));

// Receive result
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

## 🔨 Available Tools

| Tool | Category | Permissions | Parameters |
|------|----------|-------------|------------|
| `read_file` | filesystem | file.read | path |
| `write_file` | filesystem | file.write | path, content, mode |
| `run_command` | process | process.execute | command, timeout |

## 🛠️ Adding New Tools

```python
# 1. Register the tool
tool_registry.register_tool({
    'name': 'my_tool',
    'description': 'Does cool stuff',
    'category': 'custom',
    'executor': 'custom',
    'permissions': ['custom.use']
})

# 2. Create executor
class CustomExecutor:
    async def execute(self, tool_name, params):
        # Your logic here
        return {'result': 'data'}

# 3. Register executor
tool_executor.register_executor('custom', CustomExecutor())
```

## 🔐 Security Config

Edit `config.yaml`:

```yaml
security:
  allowed_directories:
    - /home/jonat/ai-stack
    - /tmp/faithh
  
  blocked_commands:
    - rm
    - dd
    - mkfs
  
  default_permissions:
    - file.read
    - process.read
```

## 📊 File Structure

```
ai-stack/
├── faithh_api_websocket.py  ← Start here
├── tool_executor.py          ← Core engine
├── tool_registry.py          ← Tool database
├── security_manager.py       ← Security checks
├── config.yaml               ← Configuration
├── executors/
│   ├── filesystem.py         ← File operations
│   └── process.py            ← Commands
└── tests/
    ├── test_tool_executor.py
    └── test_e2e.py           ← Run this first!
```

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Change port in faithh_api_websocket.py line 218:
app.run(host='0.0.0.0', port=5556, debug=True)
```

**Permission denied?**
- Check `allowed_directories` in config.yaml
- Verify file paths are absolute
- Add needed permissions to tool registration

**Tests failing?**
```bash
# Check Python version (need 3.7+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt  # Or use install_deps.sh
```

## 📚 Key Files to Read

1. `FINAL_STATUS.md` - Complete system overview
2. `test_e2e.py` - Usage examples
3. `tool_executor.py` - Core engine logic
4. `config.yaml` - All settings

## 🎯 Common Tasks

**Read a file via WebSocket**:
```json
{
  "action": "execute_tool",
  "tool_name": "read_file",
  "parameters": {"path": "config.yaml"},
  "permissions": ["file.read"]
}
```

**List available tools**:
```json
{"action": "list_tools"}
```

**Chat with Gemini**:
```bash
curl -X POST http://localhost:5555/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## 🚀 Next Steps

1. ✅ Run `test_e2e.py` to verify system
2. ✅ Start API server
3. ⏳ Build/connect frontend UI
4. ⏳ Add more tools (RAG, DB, etc.)
5. ⏳ Deploy to production

---

**Need help?** Check `FINAL_STATUS.md` for detailed documentation!
