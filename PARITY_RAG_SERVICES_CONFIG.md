# 📡 PARITY: RAG & Services Configuration
**Created:** November 9, 2025
**Purpose:** Track RAG stability, service architecture, and microservices decisions
**Status:** Active Configuration Document

---

## 🎯 RAG Configuration Decision

### **RECOMMENDATION: Always-On RAG for Personal AI**

**Decision:** ✅ **ENABLE RAG BY DEFAULT**

### Why RAG Should Always Be On:

1. **Personal Knowledge Base**
   - 91,302 documents already indexed
   - Your conversations, code, documentation
   - No external privacy concerns (it's YOUR data)

2. **Negligible Overhead**
   ```python
   # Current performance metrics:
   RAG Search Time: ~0.45 seconds
   Additional Memory: ~200MB
   CPU Impact: < 5%
   ```

3. **Better Context Always**
   - Every query benefits from your project history
   - Prevents duplicate work
   - Maintains continuity across sessions

### Implementation:
```python
# In faithh_professional_backend.py, change default:
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    use_rag = data.get('use_rag', True)  # Changed default to True
    # ... rest of code
```

---

## 🔧 Service Architecture (Based on UI Mockups)

Looking at your UI designs, you're envisioning these service panels:

### **Core Services (Always Active)**
```yaml
faithh_core:
  - chat_engine        # Main conversation handler
  - rag_system         # Knowledge retrieval
  - memory_system      # Session/conversation memory
  - personality_engine # FAITHH character responses

pulse_monitoring:
  - system_health      # CPU/Memory/Disk monitoring
  - service_status     # Check all microservices
  - log_aggregation    # Collect logs from all services
  - alert_system       # Notifications for issues
```

### **Tool Services (On-Demand)**
```yaml
code_tools:
  - file_operations    # Read/write/edit files
  - git_integration    # Version control operations
  - code_analysis      # Syntax checking, linting
  - test_runner        # Execute tests

data_tools:
  - web_scraper        # Gather external data
  - data_processor     # Transform/clean data
  - visualization      # Generate charts/graphs
  - export_tools       # Various format exports

creative_tools:
  - image_generation   # ComfyUI/Stable Diffusion
  - text_generation    # Advanced prompting
  - audio_processing   # TTS/STT if needed
  - workflow_automation # Chain multiple tools
```

---

## 🚀 Quick RAG Test Suite

### Test 1: Basic RAG Search
```bash
# Test if RAG is responding
curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "FAITHH project backend", "n_results": 3}' | jq
```

**Expected Response:**
```json
{
  "success": true,
  "results": [...],
  "count": 3
}
```

### Test 2: Chat with RAG
```bash
# Test chat with RAG enabled
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What endpoints does my backend have?",
    "model": "llama3.1-8b",
    "use_rag": true
  }' | jq
```

### Test 3: RAG Performance
```bash
# Measure RAG search time
time curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "n_results": 10}' | jq '.count'
```

---

## 💻 VS Code vs Terminal Decision

### **RECOMMENDATION: Use Both Strategically**

| Use Case | Tool | Why |
|----------|------|-----|
| **Active Development** | VS Code Extension | Better file navigation, inline editing |
| **Quick Commands** | Terminal | Faster for one-off tasks |
| **Long Sessions** | VS Code Extension | Better context retention |
| **Automation Scripts** | Terminal | Can be scripted/automated |
| **UI Development** | VS Code Extension | Live preview, debugging |
| **System Monitoring** | Terminal | Better for watching logs |

### Suggested Workflow:
```bash
# Terminal 1: Backend monitoring
watch -n 2 'curl -s http://localhost:5557/api/status | jq'

# Terminal 2: Log watching
tail -f ~/ai-stack/backend.log

# VS Code: Active development
# Use Claude Code extension for file editing and complex tasks
```

---

## 🎨 Service Panel Mapping (From UI Mockups)

Based on your Leonardo-generated UIs:

### Panel 1 (Top Left) - Character/Status
```javascript
// FAITHH main status
{
  "service": "faithh_core",
  "avatar": "images/faithh.png",
  "status": "ONLINE",
  "metrics": {
    "responses_today": 142,
    "avg_response_time": "2.3s",
    "knowledge_base": 91302
  }
}
```

### Panel 2 (Top Right) - Active Services
```javascript
// Microservices status grid
{
  "services": [
    {"name": "RAG", "status": "active", "cpu": "5%"},
    {"name": "Ollama", "status": "active", "models": 2},
    {"name": "ChromaDB", "status": "active", "docs": 91302},
    {"name": "ComfyUI", "status": "idle", "ready": true}
  ]
}
```

### Panel 3 (Bottom) - Activity Monitor
```javascript
// Recent operations/tool calls
{
  "recent_activity": [
    {"time": "2m ago", "action": "file_read", "target": "backend.py"},
    {"time": "5m ago", "action": "rag_search", "query": "API endpoints"},
    {"time": "8m ago", "action": "chat", "model": "llama3.1-8b"}
  ]
}
```

---

## 📊 Microservice Health Endpoints

### Add these to your backend:

```python
# backend/service_monitor.py

import psutil
import subprocess

class ServiceMonitor:
    def get_system_health(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict()
        }
    
    def check_service(self, service_name, port):
        try:
            result = subprocess.run(
                ['curl', '-s', f'http://localhost:{port}/health'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def get_all_services_status(self):
        return {
            "faithh_backend": self.check_service("backend", 5557),
            "ollama": self.check_service("ollama", 11434),
            "comfyui": self.check_service("comfyui", 8188),
            "stable_diffusion": self.check_service("sd", 7860)
        }
```

---

## 🔄 Service Discovery Pattern

For your microservice architecture:

```python
# backend/service_registry.py

class ServiceRegistry:
    """Central registry for all microservices"""
    
    services = {
        "core": {
            "chat": "http://localhost:5557/api/chat",
            "rag": "http://localhost:5557/api/rag_search",
            "status": "http://localhost:5557/api/status"
        },
        "models": {
            "ollama": "http://localhost:11434/api",
            "gemini": "https://generativelanguage.googleapis.com/v1beta"
        },
        "tools": {
            "file_ops": "http://localhost:5557/api/tools/file",
            "git_ops": "http://localhost:5557/api/tools/git",
            "code_ops": "http://localhost:5557/api/tools/code"
        },
        "creative": {
            "comfyui": "http://localhost:8188/api",
            "sd_webui": "http://localhost:7860/api"
        }
    }
    
    def discover(self, service_type, service_name):
        """Discover service endpoint"""
        return self.services.get(service_type, {}).get(service_name)
    
    def health_check_all(self):
        """Check health of all registered services"""
        results = {}
        for category, services in self.services.items():
            for name, url in services.items():
                results[f"{category}.{name}"] = self._check_health(url)
        return results
```

---

## ✅ Action Items

### Immediate (Today):
1. ✅ Set RAG to always-on by default
2. ✅ Test RAG with the curl commands above
3. ✅ Create this parity file in your project

### This Week:
1. [ ] Implement ServiceMonitor class
2. [ ] Add service health endpoints
3. [ ] Create service registry
4. [ ] Build UI panel for service status

### Next Phase:
1. [ ] Add more tool services
2. [ ] Implement service discovery
3. [ ] Create workflow automation
4. [ ] Build the full microservice dashboard

---

## 📝 Testing Log

### RAG Stability Test Results:
```bash
# Run these and log results:
Date: _______
RAG Search Time: _______
Success Rate: _______
Documents Returned: _______
Memory Usage: _______
```

### Service Integration Tests:
```bash
# Test each service endpoint:
[ ] Chat API - Working?
[ ] RAG API - Working?
[ ] Status API - Working?
[ ] Ollama - Responding?
[ ] File operations - Permitted?
```

---

## 🎯 Decision Summary

1. **RAG:** Always on for personal AI ✅
2. **Tool:** VS Code for development, terminal for monitoring ✅
3. **Architecture:** Microservice-based with service registry ✅
4. **UI:** Multi-panel dashboard showing all services ✅
5. **Priority:** Get RAG stable first, then add services incrementally ✅

---

**Next Update:** After RAG stability testing
**File Version:** 1.0.0
**Tracking:** All service architecture decisions