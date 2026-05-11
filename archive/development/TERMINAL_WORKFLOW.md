# 🖥️ Terminal Workflow (VS Code Extension Alternative)
**When Claude Code Extension Fails - Use This Instead!**

---

## ✅ Quick Setup (2 minutes)

### Option 1: Use Claude Web + Manual Editing (RECOMMENDED)
```bash
# Terminal 1: Keep backend running
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend.py

# Terminal 2: Serve UI
cd ~/ai-stack
python3 -m http.server 8000
# Access at: http://localhost:8000/faithh_pet_v3.html

# Terminal 3: Edit files
cd ~/ai-stack
nano faithh_professional_backend.py  # or vim, or your editor
```

**Workflow:**
1. Copy code from Claude Chat (this conversation)
2. Paste into nano/vim
3. Save and test
4. Backend auto-reloads on save!

---

## Option 2: Use Local Ollama as Code Assistant

### Install a coding model:
```bash
# Install coding-specific model
ollama pull qwen2.5-coder:7b  # Best for code
# or
ollama pull codellama:7b       # Also good
```

### Create a simple CLI assistant:
```bash
# Save this as ~/ai-stack/ask_ollama.sh
#!/bin/bash
echo "Question: $1"
echo "---"
ollama run qwen2.5-coder:7b "$1"
```

### Use it:
```bash
chmod +x ask_ollama.sh
./ask_ollama.sh "How do I fix embedding dimension mismatch in ChromaDB?"
```

---

## Option 3: Terminal-Based Code Editing Workflow

### For Quick Edits:
```bash
# Find and replace in files
sed -i "s/use_rag', False/use_rag', True/g" faithh_professional_backend.py

# View specific lines
sed -n '85,95p' faithh_professional_backend.py  # Show lines 85-95

# Search for patterns
grep -n "use_rag" faithh_professional_backend.py
```

### For Tab Fixing:
```bash
# Open HTML file at JavaScript section
nano +800 faithh_pet_v3.html
# or
vim +800 faithh_pet_v3.html
```

---

## 📋 Current Tasks (Do These in Terminal)

### Task 1: Fix UI Access
```bash
# The UI needs to be served separately
# Terminal 1: Backend (keep running)
cd ~/ai-stack && source venv/bin/activate && python faithh_professional_backend.py

# Terminal 2: UI Server (new terminal)
cd ~/ai-stack && python3 -m http.server 8000

# Access: http://localhost:8000/faithh_pet_v3.html
```

### Task 2: Fix Tab Switching
```bash
# Edit the HTML file
nano faithh_pet_v3.html

# Search for (Ctrl+W): "tab-button"
# Look for JavaScript section around line 800-900
# Add this if missing:

document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', function() {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        // Show selected tab
        const tabId = this.getAttribute('data-tab');
        document.getElementById(tabId).style.display = 'block';
    });
});
```

### Task 3: Set RAG to Always-On
```bash
# Edit backend
nano faithh_professional_backend.py

# Search for (Ctrl+W): "use_rag"
# Find this line (around line 90):
use_rag = data.get('use_rag', False)

# Change to:
use_rag = data.get('use_rag', True)

# Save (Ctrl+X, Y, Enter)
# Backend will auto-reload!
```

---

## 🔄 Terminal Commands Cheatsheet

### Navigation
```bash
cd ~/ai-stack           # Go to project
ls -la                  # List files
pwd                     # Current directory
```

### Editing
```bash
nano filename           # Easy editor
vim filename            # Advanced editor
cat filename            # View file
head -50 filename       # View first 50 lines
tail -50 filename       # View last 50 lines
```

### Search
```bash
grep "pattern" filename           # Find in file
grep -r "pattern" .               # Find in all files
find . -name "*.py"               # Find Python files
```

### Testing
```bash
curl http://localhost:5557/health          # Test backend
curl http://localhost:5557/api/status      # Check status
python3 -m json.tool < response.json       # Format JSON
```

---

## 💡 Why Terminal is Actually Better

1. **No token limits** - Edit as much as you want
2. **Direct control** - See exactly what changes
3. **Auto-reload** - Backend restarts on save
4. **Multiple terminals** - Run backend, UI, and edit simultaneously
5. **No extension bugs** - Just pure command line

---

## 🎯 Your Immediate Actions

1. **Terminal 1:** Keep backend running
2. **Terminal 2:** Start UI server with `python3 -m http.server 8000`
3. **Terminal 3:** Fix tab switching in HTML
4. **Terminal 4:** Set RAG to always-on

Then access: **http://localhost:8000/faithh_pet_v3.html**

---

**This is actually how most developers work - VS Code for viewing, terminal for execution!**