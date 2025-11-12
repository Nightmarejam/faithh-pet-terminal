# 🚀 FAITHH Project - Quick Start Guide

**Last Updated:** $(date +%Y-%m-%d)

This guide will help you clean up, organize, and start your FAITHH project environment.

---

## 📊 Current Status Summary

### Project Structure
- **Location:** `~/ai-stack` (~41GB)
- **Backend:** v3 (stable, not running)
- **UI:** v3 (MegaMan Battle Network style)
- **Status:** Clean up needed, then ready to start

### What Needs to Be Done
1. ✨ Clean up and organize files
2. 🚀 Start backend services
3. ✅ Run tests to verify stability
4. 🎨 (Optional) Generate avatar images with ComfyUI

---

## 🧹 Step 1: Clean Up and Organize (5 minutes)

Your project has files scattered in the root directory. Let's organize them properly.

### What Will Be Cleaned:
- 55 Windows Zone.Identifier files (metadata)
- 49 markdown docs → moved to `docs/` subdirectories
- 28 Python scripts → moved to `scripts/` or `backend/`
- 5 log files in home directory → archived
- 3 backup copies → archived

### Run the Cleanup:

```bash
cd ~/ai-stack

# Review what will be done (optional)
cat CLEANUP_PLAN.md

# Execute cleanup (creates automatic backup)
./scripts/cleanup_and_organize.sh

# Review new structure
cat PROJECT_STRUCTURE.md
```

**Safe to run:** Creates timestamped backup before making any changes.

---

## 🚀 Step 2: Start Services (2 minutes)

After cleanup, start your FAITHH backend and check service health.

```bash
cd ~/ai-stack

# Start backend and check all services
./scripts/start_services.sh
```

### What This Does:
- ✅ Checks if backend is already running
- ✅ Starts FAITHH backend on port 5557
- ✅ Checks Ollama status (port 11434)
- ✅ Shows status of ComfyUI and Stable Diffusion
- ✅ Provides next steps and commands

### Expected Output:
```
✅ FAITHH Backend: RUNNING
   URL: http://localhost:5557
   Health: http://localhost:5557/health

✅ Ollama: RUNNING
   URL: http://localhost:11434

⭕ ComfyUI: NOT RUNNING
   To start: cd ~/ComfyUI && python main.py --listen
```

---

## ✅ Step 3: Verify Everything Works (3 minutes)

### Test Backend API:

```bash
# Check health
curl http://localhost:5557/health

# Check status
curl http://localhost:5557/api/status | jq

# Send a test message
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello FAITHH, please introduce yourself","use_rag":false}'
```

### Open the UI:

```bash
cd ~/ai-stack
python -m http.server 8000
```

Then open in browser:
- **v3 UI:** http://localhost:8000/faithh_pet_v3.html
- **v4 UI:** http://localhost:8000/faithh_ui_v4.html

### Run Tests:

```bash
cd ~/ai-stack

# Run all tests
python -m pytest tests/ -v

# Or run specific tests
python test_backend.py
python test_rag.py
python test_gemini.py
```

---

## 🎨 Step 4: (Optional) Generate Avatar Images

Based on your conversation with Claude Desktop, you wanted to generate FAITHH and PULSE avatar images.

### Quick Method - Use ComfyUI:

```bash
# Start ComfyUI
cd ~/ComfyUI
CUDA_VISIBLE_DEVICES=1 python main.py --listen --cuda-device 1

# Open in browser
# http://localhost:8188

# Follow the workflow from your recall:
# 1. Load your reference image (FAITHH_UI_TEST.png)
# 2. Set up image-to-image workflow
# 3. Use the prompts from DO_THIS_NOW_IMAGE_GENERATION.md
# 4. Generate 10 variations each for FAITHH and PULSE
```

### Alternative - Use Stable Diffusion WebUI:

```bash
# Start Stable Diffusion WebUI
cd ~/stable-diffusion-webui
./webui.sh --listen

# Open in browser
# http://localhost:7860

# Generate using the prompts from:
cat ~/ai-stack/docs/specifications/READY_TO_USE_PROMPTS.md
```

---

## 📁 New Project Structure (After Cleanup)

```
~/ai-stack/
├── START_HERE.md                          ← You are here!
├── README.md                              ← Project overview
├── MASTER_INTEGRATION_DOCUMENT.md         ← Main reference
├── QUICK_START_GUIDE.md                   ← This file
├── CLEANUP_PLAN.md                        ← Cleanup details
├── PROJECT_STRUCTURE.md                   ← Structure inventory
│
├── faithh_professional_backend.py         ← Main backend (keep in root)
├── faithh_pet_v3.html                     ← UI v3 (active)
├── faithh_ui_v4.html                      ← UI v4 (in progress)
├── main.py                                ← Entry point
│
├── backend/                               ← Backend modules
│   ├── core/
│   ├── services/
│   ├── adapters/
│   └── faithh_backend_adapter.py
│
├── frontend/                              ← Frontend files
│   └── (organized UI components)
│
├── docs/                                  ← All documentation
│   ├── guides/                            ← How-tos and tutorials
│   ├── reference/                         ← Quick references
│   ├── session-reports/                   ← Status and summaries
│   ├── specifications/                    ← Design specs
│   └── archive/                           ← Deprecated docs
│
├── scripts/                               ← Automation scripts
│   ├── cleanup_and_organize.sh           ← Cleanup script
│   ├── start_services.sh                 ← Service startup
│   ├── system_health_check.py            ← Health checks
│   └── check_faithh_health.sh
│
├── models/                                ← AI models (33GB)
├── venv/                                  ← Python environment (7.8GB)
├── faithh_rag/                           ← RAG database (239MB)
├── data/                                  ← Application data
├── cache/                                 ← Temp files
├── logs/                                  ← Log files
├── parity/                                ← Version tracking
├── tests/                                 ← Test files
└── backups/                               ← Timestamped backups
```

---

## 🎯 Common Tasks

### Start Backend:
```bash
cd ~/ai-stack
./scripts/start_services.sh
```

### Stop Backend:
```bash
kill $(cat ~/ai-stack/.backend.pid)
```

### View Backend Logs:
```bash
tail -f ~/ai-stack/logs/backend.log
```

### Restart Backend:
```bash
kill $(cat ~/ai-stack/.backend.pid)
./scripts/start_services.sh
```

### Run Tests:
```bash
cd ~/ai-stack
python -m pytest tests/ -v
```

### Update Documentation:
```bash
cd ~/ai-stack
# Edit relevant files in docs/
git add .
git commit -m "docs: update documentation"
```

### Check System Health:
```bash
cd ~/ai-stack
python scripts/system_health_check.py
```

---

## 🔧 Troubleshooting

### Backend Won't Start
1. Check if already running: `curl http://localhost:5557/health`
2. Check logs: `tail -20 ~/ai-stack/logs/backend.log`
3. Verify .env file exists: `ls -la ~/ai-stack/.env`
4. Check port: `netstat -tlnp | grep 5557`

### Ollama Not Working
```bash
# Check if running
curl http://localhost:11434/api/version

# Start if not running
ollama serve

# List models
ollama list
```

### ComfyUI CUDA Errors
From your recall, you had CUDA compatibility issues with the 1080 Ti.

**Solution 1:** Use CPU mode (slower but works)
```bash
cd ~/ComfyUI
python main.py --listen --cpu
```

**Solution 2:** Use RTX 3090
```bash
cd ~/ComfyUI
CUDA_VISIBLE_DEVICES=1 python main.py --listen --cuda-device 1
```

**Solution 3:** Fix PyTorch (10 min)
```bash
pip3 uninstall torch torchvision torchaudio --break-system-packages -y
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --break-system-packages
```

### UI Not Loading
```bash
# Make sure backend is running
curl http://localhost:5557/health

# Start HTTP server
cd ~/ai-stack
python -m http.server 8000

# Open in browser:
# http://localhost:8000/faithh_pet_v3.html
```

---

## 📚 Important Documentation

### Quick References
- [START_HERE.md](START_HERE.md) - Original start guide
- [MASTER_INTEGRATION_DOCUMENT.md](MASTER_INTEGRATION_DOCUMENT.md) - Complete integration reference
- [CLEANUP_PLAN.md](CLEANUP_PLAN.md) - Detailed cleanup plan
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File organization guide

### Guides (in docs/guides/)
- `WORKFLOW_GUIDE.md` - Development workflow
- `IMAGE_GENERATION_SETUP.md` - ComfyUI/SD setup
- `SESSION_STARTUP_PROTOCOL.md` - How to start sessions

### Specifications (in docs/specifications/)
- `FAITHH_V4_UI_SPECIFICATION.md` - UI v4 design
- `FAITHH_V4_BACKEND_API.md` - API specifications
- `UI_VISUAL_LAYOUT_GUIDE.md` - Layout reference

---

## ✅ Success Checklist

After completing the quick start:

- [ ] Cleanup completed successfully
- [ ] PROJECT_STRUCTURE.md exists and looks good
- [ ] Backend is running on port 5557
- [ ] Backend health check passes
- [ ] Can send chat messages via API
- [ ] UI opens in browser (v3)
- [ ] Tests pass (or identified failures)
- [ ] (Optional) Avatar images generated
- [ ] Git commit created with organized structure

---

## 🚀 Next Steps

After quick start is complete:

1. **Review v3 UI** - Make sure it's stable and working
2. **Generate avatar images** - Follow prompts from your recall
3. **Update v3 with new avatars** - Replace placeholder images
4. **Plan v4 UI work** - Review FAITHH_V4_UI_SPECIFICATION.md
5. **Implement v4 backend endpoints** - Follow FAITHH_V4_BACKEND_API.md

---

## 💬 Getting Help

### Check Documentation
```bash
cd ~/ai-stack/docs
find . -name "*.md" | fzf  # Interactive search (if fzf installed)
# or
ls -R docs/
```

### View Recent Changes
```bash
cd ~/ai-stack
git log --oneline -10
cat docs/session-reports/CURRENT_STATUS_SUMMARY.md
```

### System Health
```bash
cd ~/ai-stack
python scripts/system_health_check.py
./scripts/start_services.sh  # Shows all service statuses
```

---

**Ready to start?** Run these three commands:

```bash
cd ~/ai-stack
./scripts/cleanup_and_organize.sh    # Clean up (5 min)
./scripts/start_services.sh          # Start services (2 min)
python -m pytest tests/ -v           # Run tests (3 min)
```

**Total time:** ~10 minutes to a clean, organized, and running FAITHH environment! 🎉
