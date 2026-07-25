# 🟢 STABLE V3 RESTORE POINT
**Created:** November 9, 2025  
**Status:** ✅ WORKING - DO NOT DELETE

## Current Stable Configuration

### Backend (Port 5557)
```bash
File: ~/ai-stack/faithh_professional_backend.py
Status: Running and stable
Port: 5557
Dependencies: Flask, ChromaDB, Gemini API
```

### Frontend UI
```bash
File: ~/ai-stack/faithh_pet_v3.html
Status: Working
Style: MegaMan Battle Network PET Terminal
Connection: http://localhost:5557
```

### Database
```bash
ChromaDB: ~/ai-stack/chroma.sqlite3
Documents: 91,302 indexed
Status: Operational
```

## How to Restore This Configuration

### Quick Restore (If Something Breaks)
```bash
# 1. Stop any running backend
pkill -f faithh_professional_backend.py

# 2. Start the stable v3 backend
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend.py

# 3. Open stable v3 UI
# In your browser: file:///home/jonat/ai-stack/faithh_pet_v3.html
```

### Full Restore (If Files Are Lost)
```bash
# Backend backup
cp ~/ai-stack/faithh_professional_backend.py.original \
   ~/ai-stack/faithh_professional_backend.py

# Or use the prefix backup
cp ~/ai-stack/faithh_professional_backend.py.prefixbackup \
   ~/ai-stack/faithh_professional_backend.py
```

## What's Working Right Now
✅ Backend API responding on port 5557  
✅ UI v3 connected and functional  
✅ ChromaDB queries working  
✅ Gemini API integration active  
✅ RAG system operational  

## Files That Make This Work
```
~/ai-stack/
├── faithh_professional_backend.py      ← Main backend (STABLE)
├── faithh_pet_v3.html                  ← Main UI (STABLE)
├── chroma.sqlite3                      ← Database (STABLE)
├── .env                                ← API keys (SECURE)
├── venv/                               ← Python environment
└── requirements.txt                    ← Dependencies list
```

## Testing This Configuration
```bash
# Test 1: Backend Health
curl http://localhost:5557/api/status

# Expected: {"status": "online", ...}

# Test 2: Send a message
# Open faithh_pet_v3.html in browser
# Type: "Hello FAITHH"
# Expected: Response from Gemini via RAG system
```

## When to Use This
- ✅ Before trying UI v4
- ✅ Before backend modifications
- ✅ Before ChromaDB updates
- ✅ After any breaking changes
- ✅ Weekly backups

## V4 Files (Not Active Yet)
These are ready but NOT in use:
```
~/ai-stack/frontend/html/faithh_pet_v4_enhanced.html
~/ai-stack/parity/frontend/PARITY_UI_faithh_pet_v4.md
~/ai-stack/docs/UI_MODULAR_UPDATE_GUIDE.md
```

## Next Steps (When Ready)
1. Document current v3 behavior
2. Create backup of v3 UI
3. Test v4 UI in parallel
4. Compare functionality
5. Switch when confident

---

**Remember:** This v3 setup is your safety net. Always test new changes with v3 running as backup!
