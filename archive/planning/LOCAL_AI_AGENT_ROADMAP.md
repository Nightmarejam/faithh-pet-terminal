# 🤖 Building Your Local AI Coding Agent

**Goal:** Make your local Ollama AI work like Claude Code - able to read/write files, organize code, system design, and help you develop.

---

## 🎯 **What You Want:**

A local AI assistant that can:
- ✅ Read and write files
- ✅ Organize project structure
- ✅ Generate and edit code
- ✅ System design and architecture
- ✅ Run commands and tests
- ✅ Use RAG for context
- ✅ Work entirely offline (no API calls to Anthropic)

**This is absolutely achievable!** Here's the roadmap.

---

## 📊 **Architecture Overview:**

```
┌─────────────────────────────────────────────────┐
│                   FAITHH v4                     │
│           (Your Local AI Agent)                 │
└─────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │ Ollama  │    │   RAG   │    │  Tools  │
   │ Models  │    │ (Chroma)│    │ System  │
   └─────────┘    └─────────┘    └─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
              ┌─────▼─────┐      ┌────▼────┐      ┌─────▼─────┐
              │   File    │      │  Code   │      │  Command  │
              │   Tools   │      │  Tools  │      │   Tools   │
              └───────────┘      └─────────┘      └───────────┘
```

---

## 🔧 **Phase 1: Foundation (Week 1)**

### **What You Already Have:**

✅ Ollama running with qwen2.5-7b and llama3.1-8b
✅ Backend API on port 5557
✅ RAG system with 91,302 documents
✅ Chrome DB for document search
✅ Basic chat functionality

### **What You Need to Add:**

#### **1.1: Function Calling Support**

Ollama supports function calling with certain models. You need to:

```python
# backend/tool_system.py

class ToolSystem:
    """Function calling system for local AI"""

    def __init__(self):
        self.tools = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_directory": self.list_directory,
            "run_command": self.run_command,
            "search_code": self.search_code,
        }

    def read_file(self, filepath: str) -> dict:
        """Read a file and return contents"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, filepath: str, content: str) -> dict:
        """Write content to a file"""
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return {"success": True, "message": f"Wrote to {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ... more tools
```

#### **1.2: Better Models for Coding**

Install better coding models:

```bash
# These models support function calling and coding better
ollama pull qwen2.5-coder:7b    # Excellent for code
ollama pull deepseek-coder:6.7b # Great for code understanding
ollama pull codellama:13b       # Meta's coding model
```

**Best choice:** `qwen2.5-coder:7b` - specifically trained for coding tasks.

---

## 🚀 **Phase 2: Tool Integration (Week 2)**

### **2.1: Create Tool Definitions**

```python
# backend/tool_definitions.py

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write"
                }
            },
            "required": ["filepath", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "Edit a file by replacing old content with new content",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "old_content": {
                    "type": "string",
                    "description": "Content to replace"
                },
                "new_content": {
                    "type": "string",
                    "description": "New content"
                }
            },
            "required": ["filepath", "old_content", "new_content"]
        }
    },
    {
        "name": "run_bash_command",
        "description": "Execute a bash command",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to run"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "search_codebase",
        "description": "Search for code in the project",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "File pattern (e.g., '*.py', '*.js')"
                }
            },
            "required": ["query"]
        }
    }
]
```

### **2.2: Implement Agent Loop**

```python
# backend/agent.py

class LocalCodingAgent:
    """Your local AI coding assistant"""

    def __init__(self, model="qwen2.5-coder:7b"):
        self.model = model
        self.tool_system = ToolSystem()
        self.conversation_history = []

    def chat(self, message: str, max_iterations: int = 5):
        """Chat with tool calling support"""

        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        for iteration in range(max_iterations):
            # Call Ollama with tools
            response = self._call_ollama_with_tools()

            # Check if AI wants to use a tool
            if response.get("tool_calls"):
                # Execute tools
                tool_results = self._execute_tools(response["tool_calls"])

                # Add tool results to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "content": json.dumps(tool_results)
                })

                # Continue loop
                continue
            else:
                # AI gave final answer
                return response["content"]

        return "Max iterations reached"

    def _call_ollama_with_tools(self):
        """Call Ollama API with function calling"""

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": self.conversation_history,
                "tools": TOOLS,
                "stream": False
            }
        )

        return response.json()

    def _execute_tools(self, tool_calls):
        """Execute requested tools"""
        results = []

        for call in tool_calls:
            tool_name = call["name"]
            tool_args = call["arguments"]

            if tool_name in self.tool_system.tools:
                result = self.tool_system.tools[tool_name](**tool_args)
                results.append({
                    "tool": tool_name,
                    "result": result
                })

        return results
```

---

## 💡 **Phase 3: RAG Integration (Week 2)**

### **3.1: Enhanced RAG for Code Context**

```python
# backend/code_rag.py

class CodeRAG:
    """RAG system specifically for code understanding"""

    def __init__(self):
        self.chroma_client = chromadb.HttpClient(
            host="localhost",
            port=8000
        )
        self.collection = self.chroma_client.get_collection("documents")

    def get_relevant_code(self, query: str, n_results: int = 5):
        """Find relevant code files for a query"""

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"$or": [
                {"filename": {"$regex": ".*\\.py$"}},
                {"filename": {"$regex": ".*\\.js$"}},
                {"filename": {"$regex": ".*\\.html$"}}
            ]}
        )

        return results

    def get_file_context(self, filepath: str):
        """Get full context of a file and related files"""

        # Read the file
        with open(filepath, 'r') as f:
            content = f.read()

        # Find related files
        related = self.get_relevant_code(
            f"related to {filepath}",
            n_results=3
        )

        return {
            "file": filepath,
            "content": content,
            "related_files": related
        }
```

### **3.2: Automatic Code Indexing**

```python
# scripts/index_codebase.py

import os
import chromadb
from pathlib import Path

def index_codebase():
    """Index all code files for RAG"""

    client = chromadb.HttpClient(host="localhost", port=8000)
    collection = client.get_or_create_collection("documents")

    code_extensions = {'.py', '.js', '.html', '.css', '.md', '.yaml', '.json'}
    base_dir = Path.home() / 'ai-stack'

    documents = []
    metadatas = []
    ids = []

    for filepath in base_dir.rglob('*'):
        if filepath.suffix in code_extensions:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()

                documents.append(content)
                metadatas.append({
                    "filename": str(filepath.relative_to(base_dir)),
                    "type": filepath.suffix,
                    "size": filepath.stat().st_size
                })
                ids.append(str(filepath))

            except Exception as e:
                print(f"Error indexing {filepath}: {e}")

    # Add to ChromaDB
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Indexed {len(documents)} files")

if __name__ == "__main__":
    index_codebase()
```

---

## 🎨 **Phase 4: UI Integration (Week 3)**

### **4.1: Add Agent Mode to UI**

Update `faithh_pet_v4.html` to include:

```html
<!-- Agent Mode Toggle -->
<div class="agent-mode">
    <label>
        <input type="checkbox" id="agentMode">
        Enable Agent Mode (file operations)
    </label>
</div>

<!-- Tool Output Display -->
<div id="toolOutput" class="tool-output">
    <!-- Tool execution results will appear here -->
</div>
```

```javascript
// Add to chat handler
async function sendMessage() {
    const message = document.getElementById('chatInput').value;
    const agentMode = document.getElementById('agentMode').checked;

    const response = await fetch('http://localhost:5557/api/agent/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            message: message,
            agent_mode: agentMode,
            use_rag: true
        })
    });

    const data = await response.json();

    // Display response
    displayMessage(data.response);

    // Display tool calls if any
    if (data.tool_calls) {
        displayToolCalls(data.tool_calls);
    }
}
```

### **4.2: Real-time Tool Execution Display**

Show what the AI is doing:

```javascript
function displayToolCalls(toolCalls) {
    const toolOutput = document.getElementById('toolOutput');

    toolCalls.forEach(call => {
        const toolDiv = document.createElement('div');
        toolDiv.className = 'tool-call';
        toolDiv.innerHTML = `
            <div class="tool-name">🔧 ${call.tool}</div>
            <div class="tool-args">${JSON.stringify(call.arguments, null, 2)}</div>
            <div class="tool-result">${JSON.stringify(call.result, null, 2)}</div>
        `;
        toolOutput.appendChild(toolDiv);
    });
}
```

---

## 🔐 **Phase 5: Safety & Permissions (Week 3)**

### **5.1: Permission System**

```python
# backend/permissions.py

class PermissionSystem:
    """Control what the AI can do"""

    def __init__(self):
        self.allowed_write_dirs = [
            "/home/jonat/ai-stack/backend",
            "/home/jonat/ai-stack/frontend",
            "/home/jonat/ai-stack/scripts",
            "/home/jonat/ai-stack/tests"
        ]

        self.forbidden_files = [
            ".env",
            "*.key",
            "*_api_key*"
        ]

        self.allowed_commands = [
            "ls", "cat", "grep", "find",
            "git status", "git diff",
            "python", "pytest",
            "npm", "node"
        ]

    def can_write_file(self, filepath: str) -> bool:
        """Check if AI can write to this file"""

        # Check if in allowed directory
        for allowed_dir in self.allowed_write_dirs:
            if filepath.startswith(allowed_dir):
                # Check not forbidden
                for forbidden in self.forbidden_files:
                    if fnmatch.fnmatch(filepath, forbidden):
                        return False
                return True

        return False

    def can_run_command(self, command: str) -> bool:
        """Check if AI can run this command"""

        # Check against allowed commands
        for allowed in self.allowed_commands:
            if command.startswith(allowed):
                return True

        return False
```

### **5.2: Confirmation System**

For dangerous operations, ask user:

```python
def write_file_with_confirmation(filepath, content):
    """Write file with user confirmation"""

    if not permissions.can_write_file(filepath):
        return {
            "success": False,
            "error": "Permission denied",
            "requires_confirmation": True,
            "message": f"AI wants to write to {filepath}. Allow?"
        }

    # For critical files, always ask
    if is_critical_file(filepath):
        return {
            "success": False,
            "requires_confirmation": True,
            "preview": content,
            "message": f"Review changes to {filepath}"
        }

    # Safe to write
    with open(filepath, 'w') as f:
        f.write(content)

    return {"success": True}
```

---

## 📊 **Phase 6: Advanced Features (Week 4)**

### **6.1: Multi-Step Tasks**

```python
class TaskPlanner:
    """Plan and execute multi-step coding tasks"""

    def execute_task(self, task_description: str):
        """
        Example task: "Add error handling to all API endpoints"

        Steps:
        1. Find all API endpoint files
        2. Analyze each for error handling
        3. Generate improved versions
        4. Show diffs for review
        5. Apply changes if approved
        """

        # Step 1: Plan
        plan = self.agent.chat(f"""
        Create a step-by-step plan for this task:
        {task_description}

        List concrete steps with files and actions needed.
        """)

        # Step 2: Execute each step
        for step in plan['steps']:
            result = self.agent.chat(f"Execute: {step}")
            yield {"step": step, "result": result}
```

### **6.2: Code Generation Templates**

```python
class CodeGenerator:
    """Generate code from templates"""

    templates = {
        "api_endpoint": """
@app.route('/api/{endpoint}', methods=['{method}'])
def {function_name}():
    try:
        # Your code here
        return jsonify({{"success": True}})
    except Exception as e:
        return jsonify({{"success": False, "error": str(e)}}), 500
""",
        "test_function": """
def test_{function_name}():
    # Arrange

    # Act
    result = {function_name}()

    # Assert
    assert result is not None
"""
    }

    def generate(self, template_name: str, **kwargs):
        """Generate code from template"""
        template = self.templates[template_name]
        return template.format(**kwargs)
```

---

## 🎯 **Implementation Roadmap:**

### **Week 1: Foundation**
- [ ] Install coding models (qwen2.5-coder:7b)
- [ ] Create ToolSystem class
- [ ] Implement basic file operations
- [ ] Test with simple file read/write

### **Week 2: Agent System**
- [ ] Create LocalCodingAgent class
- [ ] Implement tool calling loop
- [ ] Add RAG integration
- [ ] Create permission system

### **Week 3: UI & Safety**
- [ ] Add agent mode to UI
- [ ] Display tool execution
- [ ] Implement confirmation system
- [ ] Add safety checks

### **Week 4: Advanced Features**
- [ ] Multi-step task planning
- [ ] Code generation templates
- [ ] Git integration
- [ ] Testing automation

---

## 🚀 **Quick Start (Today!):**

### **Step 1: Install Better Model**

```bash
ollama pull qwen2.5-coder:7b
```

### **Step 2: Test Function Calling**

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder:7b",
  "messages": [
    {
      "role": "user",
      "content": "Read the file faithh_professional_backend.py"
    }
  ],
  "tools": [
    {
      "name": "read_file",
      "description": "Read a file",
      "parameters": {
        "type": "object",
        "properties": {
          "filepath": {"type": "string"}
        }
      }
    }
  ]
}'
```

### **Step 3: Create Basic Tool System**

```python
# Save as backend/simple_agent.py
# (I'll create this file next)
```

---

## 📚 **Resources:**

- **Ollama Function Calling:** https://ollama.com/blog/tool-support
- **LangChain for Agents:** https://python.langchain.com/docs/modules/agents/
- **Best Coding Models:** qwen2.5-coder, deepseek-coder, codellama

---

**This is a 4-week project to build your own local Claude Code!**

Want me to create the actual implementation files to get started? 🚀
