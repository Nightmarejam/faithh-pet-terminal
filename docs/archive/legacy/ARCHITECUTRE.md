# FAITHH Architecture Document
**Version**: 1.0  
**Date**: October 31, 2025  
**Status**: Planning - Ready for Gemini Implementation  
**Target**: Desktop Commander-like Tool System

---

## 🎯 Project Vision

Transform FAITHH from a chat interface into an **agentic AI assistant** with Desktop Commander-like capabilities:
- Execute system commands safely
- Read/write files with proper permissions  
- Manage processes and services
- Search codebases and analyze data
- Battle Chip system = Tool/Function execution system

---

## 🏗️ Current State vs Target

### Current Implementation (✅ Working)
- **Frontend**: `faithh_pet_v3.html` (Battle Network aesthetic)
- **Backend**: `faithh_api.py` (Flask + Gemini API)
- **RAG**: ChromaDB with 4 months conversation history
- **Monitoring**: PULSE watchdog system
- **Docker**: Ollama containers (local AI fallback)
- **Git**: Clean, organized repository

### Target Implementation (🎯 To Build)
- **Tool Execution Backend**: MCP-compatible server
- **Security Layer**: Sandboxing and permissions
- **WebSocket**: Real-time tool execution streaming
- **Battle Chip Registry**: Dynamic tool loading/registration
- **File System Operations**: Safe read/write with validation
- **Process Management**: Start/stop/monitor processes

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────┐
│      BROWSER (faithh_pet_v3.html)       │
│  - Battle Chip Slots UI                 │
│  - Chat Interface                       │
│  - Real-time Status Display             │
└────────────────┬────────────────────────┘
                 │ HTTP/WebSocket
                 ↓
┌─────────────────────────────────────────┐
│     FLASK API (faithh_api.py)           │
│  ┌────────┬──────────┬──────────┐      │
│  │ Gemini │ RAG      │   Tool   │      │
│  │  API   │  System  │ Registry │      │
│  └────────┴──────────┴──────────┘      │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│    TOOL EXECUTION LAYER (NEW)           │
│  ┌────────────────────────────────┐    │
│  │  ToolExecutor + SecurityManager│    │
│  │  - Command execution           │    │
│  │  - File operations             │    │
│  │  - Process management          │    │
│  └────────────────────────────────┘    │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│   SYSTEM LAYER (WSL2/Docker)            │
│  - File System                          │
│  - Processes                            │
│  - Docker Containers                    │
└─────────────────────────────────────────┘
```

---

## 🔧 Core Components to Build

### 1. Tool Registry (`tool_registry.py`)

Manages available "battle chips" (tools) and their definitions.

**Key Classes**:
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, tool_def):
        """Register a new tool/chip"""
        self.tools[tool_def['name']] = tool_def
    
    def get_tool(self, name):
        """Get tool definition"""
        return self.tools.get(name)
    
    def list_tools(self, category=None):
        """List available tools"""
        return list(self.tools.values())
```

**Tool Definition Format**:
```python
{
    'name': 'read_file',
    'description': 'Read contents of a file',
    'chip_code': 'A',           # Battle Network chip code
    'icon': '📄',               # UI icon
    'category': 'filesystem',
    'permissions': ['file.read'],
    'params': {
        'path': {
            'type': 'string',
            'required': True,
            'description': 'File path to read'
        },
        'offset': {
            'type': 'int',
            'default': 0,
            'description': 'Line offset'
        },
        'length': {
            'type': 'int',
            'default': 1000,
            'description': 'Max lines to read'
        }
    },
    'executor_class': 'FileSystemExecutor',
    'executor_method': 'read_file'
}
```

---

### 2. Security Manager (`security_manager.py`)

Handles permissions, path validation, and command filtering.

**Key Classes**:
```python
class SecurityManager:
    def __init__(self, config_path='config.yaml'):
        self.allowed_paths = self.load_allowed_paths()
        self.blocked_commands = self.load_blocked_commands()
        self.permissions = self.load_permissions()
    
    def check_permission(self, tool, user_context):
        """Check if user can execute tool"""
        required = tool.get('permissions', [])
        user_perms = user_context.get('permissions', [])
        return all(p in user_perms for p in required)
    
    def validate_path(self, path):
        """Ensure path is within allowed directories"""
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(allowed) 
                   for allowed in self.allowed_paths)
    
    def validate_command(self, command):
        """Ensure command is not blocked"""
        cmd = command.split()[0]
        return cmd not in self.blocked_commands
```

**Config Format** (`config.yaml`):
```yaml
security:
  allowed_directories:
    - /home/jonat/ai-stack
    - /home/jonat/faithh
  blocked_commands:
    - rm
    - dd  
    - mkfs
  default_permissions:
    - file.read
    - process.read
```

---

### 3. Tool Executor (`tool_executor.py`)

Executes tools with security checks and sandboxing.

**Key Classes**:
```python
class ToolExecutor:
    def __init__(self, registry, security):
        self.registry = registry
        self.security = security
        self.executors = self._load_executors()
    
    def execute(self, tool_name, params, user_context):
        """
        Execute a tool
        
        Steps:
        1. Get tool definition
        2. Check permissions
        3. Validate parameters
        4. Execute in sandbox
        5. Return results
        """
        # Get tool
        tool = self.registry.get_tool(tool_name)
        if not tool:
            raise ToolNotFoundError(tool_name)
        
        # Security check
        if not self.security.check_permission(tool, user_context):
            raise PermissionDeniedError()
        
        # Validate params
        validated = self._validate_params(tool, params)
        
        # Execute
        executor_class = self.executors[tool['executor_class']]
        executor_method = getattr(executor_class, tool['executor_method'])
        
        result = executor_method(validated)
        return result
```

---

### 4. Tool Executors (Individual Classes)

#### FileSystemExecutor (`executors/filesystem.py`)
```python
class FileSystemExecutor:
    def __init__(self, security_manager):
        self.security = security_manager
    
    def read_file(self, params):
        """Read file with security checks"""
        path = params['path']
        
        # Security validation
        if not self.security.validate_path(path):
            raise SecurityError("Path not allowed")
        
        # Read file
        with open(path, 'r') as f:
            lines = f.readlines()
        
        # Apply offset/length
        offset = params.get('offset', 0)
        length = params.get('length', 1000)
        
        return {
            'status': 'success',
            'content': ''.join(lines[offset:offset+length]),
            'total_lines': len(lines)
        }
    
    def write_file(self, params):
        """Write file with security checks"""
        path = params['path']
        content = params['content']
        mode = params.get('mode', 'rewrite')
        
        if not self.security.validate_path(path):
            raise SecurityError("Path not allowed")
        
        file_mode = 'w' if mode == 'rewrite' else 'a'
        with open(path, file_mode) as f:
            f.write(content)
        
        return {'status': 'success', 'path': path}
    
    def list_directory(self, params):
        """List directory contents"""
        path = params['path']
        depth = params.get('depth', 2)
        
        if not self.security.validate_path(path):
            raise SecurityError("Path not allowed")
        
        # Recursive listing implementation
        results = self._list_recursive(path, depth)
        return {'status': 'success', 'files': results}
```

#### ProcessExecutor (`executors/process.py`)
```python
class ProcessExecutor:
    def __init__(self, security_manager):
        self.security = security_manager
    
    def start_process(self, params):
        """Execute command safely"""
        command = params['command']
        timeout = params.get('timeout_ms', 8000) / 1000
        
        if not self.security.validate_command(command):
            raise SecurityError("Command blocked")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            'status': 'success',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    
    def list_processes(self, params):
        """List running processes"""
        # Platform-specific process listing
        if sys.platform == 'win32':
            cmd = 'tasklist'
        else:
            cmd = 'ps aux'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {'status': 'success', 'output': result.stdout}
```

---

## 📡 API Endpoints

### REST Endpoints (Add to faithh_api.py)

#### Execute Tool
```python
@app.route('/api/tools/execute', methods=['POST'])
def execute_tool():
    """
    Execute a battle chip (tool)
    
    Request Body:
    {
        "tool": "read_file",
        "params": {"path": "/home/jonat/test.txt"}
    }
    
    Response:
    {
        "status": "success",
        "result": {...},
        "execution_time_ms": 123
    }
    """
    data = request.json
    tool_name = data['tool']
    params = data['params']
    
    user_context = {'permissions': ['file.read', 'file.write', 'process.read']}
    
    try:
        result = tool_executor.execute(tool_name, params, user_context)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
```

#### List Available Tools
```python
@app.route('/api/tools/list', methods=['GET'])
def list_tools():
    """
    Get all available battle chips
    
    Response:
    {
        "tools": [
            {
                "name": "read_file",
                "chip_code": "A",
                "icon": "📄",
                "description": "...",
                ...
            }
        ]
    }
    """
    tools = tool_registry.list_tools()
    return jsonify({'tools': tools})
```

---

### WebSocket Endpoints (NEW - Add Flask-SocketIO)

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('execute_tool')
def handle_tool_execution(data):
    """
    Execute tool with streaming progress
    
    Receives:
    {
        "tool": "search_codebase",
        "params": {...},
        "request_id": "uuid"
    }
    
    Emits:
    - 'progress': {"status": "running", "message": "..."}
    - 'result': {"status": "success", "data": {...}}
    - 'error': {"status": "error", "error": "..."}
    """
    tool_name = data['tool']
    params = data['params']
    request_id = data.get('request_id', 'unknown')
    
    try:
        # For streaming tools
        if tool_name in ['search_codebase', 'start_process']:
            for progress in tool_executor.execute_streaming(tool_name, params):
                emit('progress', {
                    'request_id': request_id,
                    'status': 'running',
                    'data': progress
                })
        
        # Final result
        result = tool_executor.execute(tool_name, params, user_context)
        emit('result', {
            'request_id': request_id,
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        emit('error', {
            'request_id': request_id,
            'status': 'error',
            'error': str(e)
        })
```

---

## 🎮 Frontend Integration

### WebSocket Client (Add to faithh_pet_v3.html)

```javascript
class ToolExecutionClient {
    constructor() {
        this.socket = io('http://localhost:5555');
        this.setupHandlers();
        this.pendingRequests = new Map();
    }
    
    setupHandlers() {
        this.socket.on('progress', (data) => {
            const callback = this.pendingRequests.get(data.request_id);
            if (callback && callback.onProgress) {
                callback.onProgress(data);
            }
        });
        
        this.socket.on('result', (data) => {
            const callback = this.pendingRequests.get(data.request_id);
            if (callback && callback.onComplete) {
                callback.onComplete(data);
            }
            this.pendingRequests.delete(data.request_id);
        });
        
        this.socket.on('error', (data) => {
            const callback = this.pendingRequests.get(data.request_id);
            if (callback && callback.onError) {
                callback.onError(data);
            }
            this.pendingRequests.delete(data.request_id);
        });
    }
    
    executeChip(chipName, params, callbacks = {}) {
        const requestId = this.generateRequestId();
        this.pendingRequests.set(requestId, callbacks);
        
        this.socket.emit('execute_tool', {
            tool: chipName,
            params: params,
            request_id: requestId
        });
        
        return requestId;
    }
    
    generateRequestId() {
        return 'req_' + Math.random().toString(36).substr(2, 9);
    }
}

// Usage
const toolClient = new ToolExecutionClient();

// Execute a chip
toolClient.executeChip('read_file', 
    {path: '/home/jonat/test.txt'},
    {
        onProgress: (data) => console.log('Progress:', data),
        onComplete: (data) => displayResult(data),
        onError: (error) => showError(error)
    }
);
```

---

## 🛠️ Initial Tool Set

### Priority Tools (Implement First)

1. **read_file** - Read file contents
2. **write_file** - Write/append to file
3. **list_directory** - List files and folders
4. **start_process** - Execute command
5. **search_codebase** - Search for patterns in code
6. **rag_query** - Search conversation history

### Secondary Tools

7. **edit_block** - Surgical file editing
8. **get_file_info** - File metadata
9. **create_directory** - Make directories
10. **move_file** - Move/rename files
11. **list_processes** - Show running processes
12. **git_status** - Git repository status

### Advanced Tools (Phase 2)

13. **docker_ps** - List Docker containers
14. **docker_logs** - View container logs
15. **analyze_data** - CSV/JSON analysis
16. **generate_diagram** - Create visualizations

---

## 🔒 Security Considerations

### Path Validation
```python
ALLOWED_PATHS = [
    '/home/jonat/ai-stack',
    '/home/jonat/faithh'
]

def validate_path(path):
    abs_path = os.path.abspath(os.path.expanduser(path))
    return any(abs_path.startswith(allowed) for allowed in ALLOWED_PATHS)
```

### Command Blocking
```python
BLOCKED_COMMANDS = [
    'rm -rf /',
    'dd',
    'mkfs',
    'format',
    ':(){:|:&};:',  # Fork bomb
]

def validate_command(cmd):
    return not any(blocked in cmd for blocked in BLOCKED_COMMANDS)
```

### Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: 'global')

@app.route('/api/tools/execute')
@limiter.limit("60 per minute")
def execute_tool():
    ...
```

---

## 📦 Implementation Phases

### Phase 1: Foundation (Week 1) - IMPLEMENT FIRST
**Goal**: Basic tool execution working

- [ ] Create `tool_registry.py`
- [ ] Create `security_manager.py`
- [ ] Create `tool_executor.py`
- [ ] Create `executors/filesystem.py`
- [ ] Add `/api/tools/execute` endpoint to `faithh_api.py`
- [ ] Implement 3 tools: read_file, write_file, list_directory
- [ ] Create `config.yaml` with security settings
- [ ] Test with curl/Postman

**Deliverables**: Basic tool execution via REST API

---

### Phase 2: WebSocket & Streaming (Week 2)
**Goal**: Real-time execution

- [ ] Add Flask-SocketIO dependency
- [ ] Implement WebSocket handler
- [ ] Add streaming support for long-running tools
- [ ] Update frontend to use WebSocket
- [ ] Implement progress indicators in UI

**Deliverables**: Real-time tool execution with progress

---

### Phase 3: Tool Library (Week 3)
**Goal**: Complete tool set

- [ ] Implement remaining filesystem tools
- [ ] Create `executors/process.py`
- [ ] Create `executors/search.py`
- [ ] Create `executors/rag.py`
- [ ] Add all 12 priority tools
- [ ] Document each tool

**Deliverables**: Full tool ecosystem

---

### Phase 4: UI Polish (Week 4)
**Goal**: Beautiful interface

- [ ] Chip slot drag-and-drop
- [ ] Tool execution animations
- [ ] Better error messages
- [ ] Keyboard shortcuts
- [ ] Tool favorites system

**Deliverables**: Production-ready UI

---

## 📝 File Structure After Implementation

```
ai-stack/
├── faithh_api.py              # Main API (updated)
├── faithh_pet_v3.html         # Frontend (updated)
├── config.yaml                # NEW - Security config
├── tool_registry.py           # NEW - Tool management
├── security_manager.py        # NEW - Security layer
├── tool_executor.py           # NEW - Execution engine
├── executors/                 # NEW - Tool executors
│   ├── __init__.py
│   ├── filesystem.py          # File operations
│   ├── process.py             # Process management
│   ├── search.py              # Search operations
│   └── rag.py                 # RAG queries
├── tools/                     # NEW - Tool definitions
│   └── definitions.json       # Tool specs
├── tests/                     # NEW - Tests
│   ├── test_executor.py
│   ├── test_security.py
│   └── test_tools.py
└── requirements.txt           # Updated dependencies
```

---

## 📚 Dependencies to Add

```txt
# Add to requirements.txt
flask-socketio==5.3.5
python-socketio==5.10.0
eventlet==0.33.3
flask-limiter==3.5.0
pyyaml==6.0.1
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
def test_read_file_success():
    result = executor.execute('read_file', 
                             {'path': '/home/jonat/test.txt'}, 
                             user_context)
    assert result['status'] == 'success'

def test_read_file_blocked_path():
    with pytest.raises(SecurityError):
        executor.execute('read_file',
                        {'path': '/etc/passwd'},
                        user_context)
```

### Integration Tests
```python
def test_tool_execution_endpoint():
    response = client.post('/api/tools/execute', json={
        'tool': 'read_file',
        'params': {'path': '/home/jonat/test.txt'}
    })
    assert response.status_code == 200
```

---

## 🎯 Success Criteria

### Phase 1 Complete When:
- [ ] Can execute read_file, write_file, list_directory via REST API
- [ ] Security validation prevents forbidden paths
- [ ] Error handling works correctly
- [ ] Unit tests pass
- [ ] Can read/write files in ai-stack directory safely

### Final System Complete When:
- [ ] All 12 tools working
- [ ] WebSocket streaming functional
- [ ] Security hardened
- [ ] UI polished
- [ ] Can perform Desktop Commander-like tasks:
  - ✅ Read and analyze files
  - ✅ Execute commands safely
  - ✅ Search codebase
  - ✅ Manage processes
  - ✅ Update project files

---

## 💬 Questions for Gemini

1. **Flask-SocketIO vs native websockets** - Which is better for our use case?
2. **Sandboxing approach** - Docker containers vs subprocess restrictions?
3. **Tool registration** - Dynamic loading from JSON vs hardcoded in Python?
4. **Error recovery** - How to handle tool crashes gracefully?
5. **Streaming implementation** - Generator functions or callback-based?

---

## 🔗 References

- **Project Root**: `/home/jonat/ai-stack/`
- **GitHub**: https://github.com/Nightmarejam/faithh-pet-terminal
- **Related Docs**:
  - `FAITHH_CONTEXT.md` - Project overview
  - `GEMINI_HANDOFF.md` - Gemini collaboration guide
  - `README.md` - Project readme

---

## 🚀 Ready for Implementation!

This document provides everything needed to build the tool system. Start with Phase 1 (Foundation) and iterate from there.

**Next Steps**:
1. Review this architecture
2. Create config.yaml with security settings
3. Implement tool_registry.py
4. Implement security_manager.py
5. Implement tool_executor.py
6. Create filesystem executor with 3 basic tools
7. Add REST endpoint to faithh_api.py
8. Test with curl/Postman

Good luck! 🎉