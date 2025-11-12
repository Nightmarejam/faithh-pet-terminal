# Get Started Checklist - Enhanced PET Terminal v4

**Quick 15-Minute Setup**

---

## ✅ Phase 1: Placement (2 minutes)

```bash
cd ~/ai-stack

# 1. Move new UI file
mv faithh_pet_v4_enhanced.html frontend/html/

# 2. Move documentation
mv PARITY_UI_faithh_pet_v4.md parity/frontend/
mv UI_MODULAR_UPDATE_GUIDE.md docs/

# 3. Backup your v3 (just in case)
cp frontend/html/faithh_pet_v3.html frontend/html/faithh_pet_v3_backup.html
```

**Status:** Files in place ✓

---

## ✅ Phase 2: Configuration (3 minutes)

Open `frontend/html/faithh_pet_v4_enhanced.html` in your editor.

### 1. Set Backend URL (Line 23)
```javascript
backend: {
    url: 'http://localhost:5557',  // ← Change if different
    // ...
}
```

### 2. Review Available Models (Lines 25-30)
```javascript
models: {
    default: 'gemini-pro',  // ← Change default if needed
    available: [
        { id: 'gemini-pro', name: 'GEMINI PRO', color: '#00ffff' },
        // Add/remove models as needed
    ]
}
```

### 3. Check Feature Flags (Lines 35-40)
```javascript
features: {
    rag: true,              // ← Knowledge base enabled
    autoScroll: true,       // ← Auto-scroll chat
    soundEffects: false,    // ← Not implemented yet
    saveHistory: true       // ← Save to localStorage
}
```

**Status:** Configured ✓

---

## ✅ Phase 3: Backend Check (5 minutes)

### 1. Ensure Backend is Running
```bash
cd ~/ai-stack
source venv/bin/activate
python backend/faithh_professional_backend.py
```

**Expected output:**
```
✅ Gemini API configured
✅ ChromaDB connected at localhost:8000
🚀 Server starting at http://localhost:5557
```

### 2. Test Backend Status
```bash
# In another terminal
curl http://localhost:5557/api/status
```

**Should return:** JSON with `"success": true`

### 3. Add CORS if Needed
If backend doesn't have CORS, add to your backend file:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add this line
```

Install if needed:
```bash
pip install flask-cors --break-system-packages
```

**Status:** Backend ready ✓

---

## ✅ Phase 4: First Launch (3 minutes)

### 1. Open in Browser

**Option A:** HTTP Server
```bash
cd ~/ai-stack/frontend/html
python -m http.server 8080

# Then open: http://localhost:8080/faithh_pet_v4_enhanced.html
```

**Option B:** Direct File
```bash
xdg-open ~/ai-stack/frontend/html/faithh_pet_v4_enhanced.html
# or on Mac:
open ~/ai-stack/frontend/html/faithh_pet_v4_enhanced.html
```

### 2. Check Connection

Look for these indicators:
- ✅ Green dot next to "PET" (connected)
- ✅ "Backend ● ONLINE" in status panel
- ✅ No console errors (press F12)

### 3. Send Test Message

1. Type: "Hello FAITHH!"
2. Press Enter or click SEND
3. Should get response

**Status:** Working! ✓

---

## ✅ Phase 5: Explore Features (2 minutes)

### Try These:

**1. Model Selector**
- Click dropdown at top
- Select different model
- Send message
- Watch it use new model

**2. Statistics**
- Send a few messages
- Watch counters update
- See session time increase

**3. RAG Toggle**
- Click "Knowledge Base (RAG)" toggle
- Try with RAG on/off
- Compare responses

**4. Status Panel**
- Check connection status
- See response times
- Watch sources used count

**Status:** Features tested ✓

---

## ✅ Phase 6: First Customization (Optional)

### Quick Win: Change a Color

**Edit line 48:**
```javascript
theme: {
    primaryColor: '#00ff00',  // Changed from cyan to green!
    // ...
}
```

**Find/Replace in CSS:**
- Find: `#00ffff`
- Replace: `#00ff00`

**Save, refresh, see green theme!**

**Status:** Customized! ✓

---

## 🎯 Troubleshooting Checklist

### Problem: Can't see UI
- [ ] Is file in correct location?
- [ ] Did you open in browser?
- [ ] Check file path is correct

### Problem: "Offline" status
- [ ] Is backend running? (check terminal)
- [ ] Correct backend URL in config? (line 23)
- [ ] CORS enabled on backend?
- [ ] Firewall blocking port?

### Problem: No response to messages
- [ ] Check browser console (F12) for errors
- [ ] Backend receiving requests? (check backend terminal)
- [ ] API endpoint correct? (line 24)
- [ ] Model available on backend?

### Problem: Looks broken/wrong
- [ ] Clear browser cache (Ctrl+Shift+R)
- [ ] Check for JavaScript errors (F12 console)
- [ ] CSS loaded correctly?
- [ ] Using modern browser?

---

## 📚 Reference Card

**Quick Links:**
- Main UI: `frontend/html/faithh_pet_v4_enhanced.html`
- Parity File: `parity/frontend/PARITY_UI_faithh_pet_v4.md`
- Update Guide: `docs/UI_MODULAR_UPDATE_GUIDE.md`

**Key Lines:**
- Config: Lines 10-50
- Backend URL: Line 23
- Models: Lines 25-30
- Features: Lines 35-40

**Common Tasks:**
- Add model: Edit line 27
- Change color: Edit line 48
- Add stat: See Component 7 in parity file
- Toggle feature: Edit lines 35-40

---

## ✨ You're Ready!

### Completed:
- ✅ Files placed correctly
- ✅ Configuration set
- ✅ Backend connected
- ✅ UI launched
- ✅ Features tested
- ✅ (Optional) First customization

### Next Steps:
1. Read the parity file to understand structure
2. Try adding a new stat
3. Customize colors to your liking
4. Explore the update guide

---

## 🚀 Week 2 Goals

Now that setup is done:

**Today/Tomorrow:**
- [ ] Get comfortable with the UI
- [ ] Test all features
- [ ] Read parity file
- [ ] Try one small change

**This Week:**
- [ ] Add custom stat
- [ ] Modify colors/styling
- [ ] Add new model
- [ ] Document in MASTER_ACTION

**Week 3:**
- [ ] Build custom component
- [ ] Add new feature
- [ ] Master the modular system

---

## 💡 Pro Tips

1. **Keep parity file open** while editing
2. **Test after every change** (save → refresh)
3. **Use browser console** (F12) to debug
4. **Start small** (colors, text) before big changes
5. **Document your changes** in parity file

---

## 🎉 Success!

If everything works:
- ✅ PET Terminal displays
- ✅ MegaMan aesthetic intact
- ✅ Can send messages
- ✅ Backend connected
- ✅ Stats updating
- ✅ Ready to customize

**You're ready to start Week 2 UI improvements!**

---

**Questions?**
- Check parity file for component locations
- Review update guide for procedures
- Look at comparison doc for v3→v4 changes
- Test in browser console for debugging

**Remember:**
- Small changes first
- Test frequently
- Document everything
- Have fun!

---

*Setup time: 15 minutes*  
*Difficulty: Easy*  
*Requirements: Browser + Backend*  
*Result: Awesome modular UI!*

🚀 **READY TO GO!** 🚀

---

*Checklist created: 2025-11-09*  
*For: FAITHH PET Terminal v4 Setup*  
*Estimated completion: 15 minutes*
