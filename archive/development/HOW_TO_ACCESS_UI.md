# 🖥️ How to Access FAITHH UI

**Problem:** You can't open `faithh_pet_v3.html` directly because browsers have security restrictions for local files.

**Solution:** You have 3 options.

---

## ✅ **Option 1: Simple HTTP Server (Recommended)**

The HTML file needs a web server because it makes API calls to `http://localhost:5557`.

### **Start HTTP Server:**

```bash
# In WSL terminal
cd ~/ai-stack
python -m http.server 8000
```

Then open in your browser:
```
http://localhost:8000/faithh_pet_v3.html
```

**Why this works:**
- Backend is on port 5557 (API server)
- HTTP server is on port 8000 (serves HTML files)
- Browser allows HTML on port 8000 to call API on port 5557

---

## ✅ **Option 2: VSCode Live Server (Easiest)**

If you have VSCode with Live Server extension:

1. Open `faithh_pet_v3.html` in VSCode
2. Right-click the file
3. Click "Open with Live Server"
4. Browser opens automatically at `http://127.0.0.1:5500/faithh_pet_v3.html`

**Advantage:** Automatically refreshes when you edit the file.

---

## ✅ **Option 3: Direct File Access (Limited)**

Open the file directly in browser:

**In Windows:**
1. Open File Explorer
2. Navigate to: `\\wsl.localhost\Ubuntu\home\jonat\ai-stack\`
3. Double-click `faithh_pet_v3.html`

**Or use this path:**
```
file:///\\wsl.localhost\Ubuntu\home\jonat\ai-stack\faithh_pet_v3.html
```

**⚠️ Limitation:** Some features won't work due to CORS security restrictions when accessing APIs from `file://` URLs.

---

## 🔍 **Understanding the Ports:**

| Port | Service | Purpose |
|------|---------|---------|
| **5557** | FAITHH Backend | API endpoints (/api/chat, /api/status, etc.) |
| **8000** | HTTP Server | Serves static HTML/CSS/JS files |
| **11434** | Ollama | Local AI models |
| **8188** | ComfyUI | Image generation (when running) |
| **7860** | Stable Diffusion | Image generation (when running) |

---

## 🎯 **Complete Startup Sequence:**

### **1. Start Backend (if not running):**
```bash
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend.py
```

**Check it's running:**
```bash
curl http://localhost:5557/health
```

### **2. Start HTTP Server:**
```bash
cd ~/ai-stack
python -m http.server 8000
```

**You should see:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### **3. Open Browser:**
```
http://localhost:8000/faithh_pet_v3.html
```

### **4. Test the UI:**
- Type a message in the chat
- Click Send or press Enter
- FAITHH should respond!

---

## 🐛 **Troubleshooting:**

### **"Port 8000 is already in use"**

Find and kill the process:
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill <PID>

# Or force kill all Python servers
pkill -f "python.*http.server"
```

### **"Cannot connect to backend"**

Check if backend is running:
```bash
curl http://localhost:5557/health
```

If not running:
```bash
cd ~/ai-stack
python faithh_professional_backend.py
```

### **UI opens but chat doesn't work**

1. Open browser developer console (F12)
2. Look for errors
3. Check if requests to `http://localhost:5557` are failing
4. Verify backend is running: `curl http://localhost:5557/api/status`

### **"This site can't be reached"**

Make sure you're using `http://localhost:8000` not `file://` URLs.

---

## 📱 **Access from Another Device (Optional):**

To access from another computer on your network:

1. Find your PC's IP address:
   ```bash
   hostname -I
   ```

2. Start HTTP server on all interfaces:
   ```bash
   python -m http.server 8000 --bind 0.0.0.0
   ```

3. Access from other device:
   ```
   http://YOUR_IP:8000/faithh_pet_v3.html
   ```

---

## 🎨 **Quick Reference:**

### **Start Everything:**
```bash
# Terminal 1: Backend
cd ~/ai-stack && python faithh_professional_backend.py

# Terminal 2: HTTP Server
cd ~/ai-stack && python -m http.server 8000
```

### **Open UI:**
```
http://localhost:8000/faithh_pet_v3.html
```

### **Stop Everything:**
```bash
# Stop backend
pkill -f faithh_professional_backend

# Stop HTTP server
pkill -f "python.*http.server"
```

---

## 💡 **Pro Tip: Create Startup Shortcuts**

### **Windows PowerShell Shortcut:**

Create `start-faithh.ps1`:
```powershell
# Start backend
Start-Process wsl -ArgumentList "bash -c 'cd ~/ai-stack && python faithh_professional_backend.py'"

# Wait 5 seconds
Start-Sleep -Seconds 5

# Start HTTP server
Start-Process wsl -ArgumentList "bash -c 'cd ~/ai-stack && python -m http.server 8000'"

# Wait 2 seconds
Start-Sleep -Seconds 2

# Open browser
Start-Process "http://localhost:8000/faithh_pet_v3.html"
```

Then just run: `.\start-faithh.ps1`

---

**Now you're ready to use FAITHH!** 🚀
