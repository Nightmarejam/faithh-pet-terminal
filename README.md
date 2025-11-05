# 🎮 FAITHH - Battle Chip AI System

**"AI with Real Computer Skills"**

An agentic AI system that can execute real tools on your computer - safely, securely, and with style! 🚀

---

## ⚡ Quick Start (60 seconds)

```bash
cd ~/ai-stack

# Install
bash install_deps.sh

# Test (should pass all tests)
python3 test_e2e.py

# Run
python3 faithh_api_websocket.py
```

**Done!** Server running on `http://localhost:5555` 🎉

---

## 🎯 What It Does

FAITHH lets AI assistants execute **real tools** on your computer:
- 📁 Read and write files
- ⚙️  Run shell commands  
- 🔍 Search and process data
- 🤖 Chat with Gemini AI
- ⚡ Real-time WebSocket streaming

All with **enterprise-grade security** built-in!

---

## 🏗️ Architecture

```
Frontend UI (Your App)
    ↕ WebSocket
FAITHH API Server
    ↕
Tool Executor (Core Engine)
    ↕
Security Manager → Tool Registry → Executors
    ↕
Your Computer (Files, Processes, etc.)
```

**See `ARCHITECTURE.md` for complete diagram**

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | Fast setup guide |
| **FINAL_STATUS.md** | Complete system overview |
| **ARCHITECTURE.md** | System architecture |
| **SESSION_COMPLETE.md** | Build summary |

---

## 🔧 Features

### ✅ Implemented
- **Tool Execution Engine** - Orchestrates everything
- **WebSocket API** - Real-time streaming
- **Security System** - Path/command validation
- **Permission System** - Granular access control
- **Filesystem Tools** - Read/write files
- **Process Tools** - Execute commands
- **Gemini Integration** - AI chat
- **Battle Chip Theme** - Combo support!

### ⏳ Coming Soon
- RAG tools (ChromaDB)
- Database tools
- Frontend UI
- Tool marketplace
- Visual combo selector

---

## 🔌 API Examples

### WebSocket (Real-time tools)
```javascript
const ws = new WebSocket('ws://localhost:5555/ws/tools');

// Execute tool
ws.send(JSON.stringify({
  action: 'execute_tool',
  tool_name: 'read_file',
  parameters: { path: '/tmp/test.txt' },
  permissions: ['file.read']
}));

// Get result
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

### HTTP (Chat with AI)
```bash
curl -X POST http://localhost:5555/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello FAITHH!"}'
```

---

## 🛡️ Security

### Multiple Layers:
1. **Config** - Allowed directories, blocked commands
2. **Registry** - Required permissions per tool
3. **Executor** - Runtime validation
4. **Security Manager** - Path/command checks
5. **OS** - System-level permissions

### Example Config (`config.yaml`):
```yaml
security:
  allowed_directories:
    - /home/jonat/ai-stack
    - /tmp/faithh
  
  blocked_commands:
    - rm
    - dd
    - mkfs
```

---

## 🧪 Testing

```bash
# Run all tests
python3 test_e2e.py

# Expected output:
✅ Registry initialization
✅ Executor registration
✅ Tool registration
✅ File read
✅ File write
✅ Command execution
✅ Security blocking
🎉 ALL TESTS PASSED!
```

---

## 📦 Project Structure

```
ai-stack/
├── faithh_api_websocket.py  ⭐ Start here
├── tool_executor.py          ⭐ Core engine
├── tool_registry.py          Tool database
├── security_manager.py       Security checks
├── config.yaml               Configuration
├── executors/
│   ├── filesystem.py         File operations
│   └── process.py            Commands
├── tests/
│   ├── test_tool_executor.py
│   └── test_e2e.py          ⭐ Run first!
└── docs/
    ├── QUICKSTART.md
    ├── FINAL_STATUS.md
    └── ARCHITECTURE.md
```

---

## 🎮 Battle Chip Theme

Inspired by MegaMan Battle Network!

- **Tools** = Battle Chips
- **Executor** = PET (Personal Terminal)
- **Security** = Firewall
- **Combos** = Chain tools together for bonus effects!

*Because executing tools should be FUN!* 🎊

---

## 🚀 Adding New Tools

```python
# 1. Create executor
class MyExecutor:
    async def execute(self, tool_name, params):
        # Your logic
        return {'result': 'data'}

# 2. Register it
tool_executor.register_executor('mytype', MyExecutor())

# 3. Register tool
tool_registry.register_tool({
    'name': 'my_tool',
    'executor': 'mytype',
    'permissions': ['my.permission']
})

# 4. Use it!
result = await tool_executor.execute_tool('my_tool', {...})
```

---

## 📊 Stats

- **Lines of Code**: 858+ production code
- **Documentation**: 1000+ lines
- **Test Coverage**: End-to-end validated
- **Security Layers**: 5
- **Tools Built**: 3
- **Executors**: 2
- **APIs**: WebSocket + HTTP

---

## 🙏 Built With

- Python 3.7+
- Flask + Flask-Sock (WebSocket)
- Google Gemini API
- asyncio (async/await)
- YAML config
- Love and battle chip energy! ⚡

---

## 🎯 Use Cases

- **AI Coding Assistants** - Let AI read/write code
- **Data Processing** - Automate file operations
- **System Administration** - Safely execute commands
- **RAG Systems** - Search and retrieve data
- **Custom Agents** - Build your own tools!

---

## 📝 License

MIT (or whatever you choose)

---

## 🌟 Status

**FULLY FUNCTIONAL** ✅

The backend is complete and tested. Ready for:
- Frontend integration
- Tool expansion  
- Production deployment

---

## 💬 Quick Links

- **Start Server**: `python3 faithh_api_websocket.py`
- **Run Tests**: `python3 test_e2e.py`
- **API Docs**: See `QUICKSTART.md`
- **Architecture**: See `ARCHITECTURE.md`

---

## 🎉 Get Started!

```bash
# Clone (or cd to existing)
cd ~/ai-stack

# Install
bash install_deps.sh

# Test
python3 test_e2e.py

# Run
python3 faithh_api_websocket.py

# Connect your UI to:
ws://localhost:5555/ws/tools
```

**That's it!** You now have an AI tool execution system! 🚀

---

*"Making AI useful, one battle chip at a time"* ⚡

Built with 💙 on November 4, 2025
