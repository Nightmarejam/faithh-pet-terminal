# FAITHH UI v4 - Quick Start Guide

**Goal:** Get the new UI running with your existing backend

---

## 🚀 Quick Start (5 minutes)

### Step 1: Place the Files

```bash
cd ~/ai-stack

# Move new UI to frontend
mv faithh_ui_v4.html frontend/html/

# Keep architecture docs in docs
mv FRONTEND_BACKEND_ARCHITECTURE.md docs/

# Reference backend template (don't overwrite your existing backend!)
mv faithh_backend_v4_template.py docs/backend_v4_template_reference.py
```

### Step 2: Update Your Existing Backend

Your existing `faithh_professional_backend.py` probably already has most endpoints. You just need to ensure:

**Required Endpoints:**
- `GET /status` - Health check
- `POST /chat` - Main chat endpoint
- `POST /search` - RAG search (optional but recommended)
- `GET /models` - Available models (optional)

**Add CORS if missing:**

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add this line
```

Install CORS if needed:
```bash
source venv/bin/activate
pip install flask-cors
```

### Step 3: Start Backend

```bash
cd ~/ai-stack
source venv/bin/activate
python backend/faithh_professional_backend.py
```

Expected output:
```
✅ Gemini API configured
✅ ChromaDB connected at localhost:8000
🚀 Server starting at http://localhost:5557
```

### Step 4: Start Frontend

**Option A: Simple HTTP Server**
```bash
cd ~/ai-stack/frontend/html
python -m http.server 8080
```

**Option B: Just open the file**
```bash
# Or just open directly in browser:
xdg-open ~/ai-stack/frontend/html/faithh_ui_v4.html
# or on Mac:
open ~/ai-stack/frontend/html/faithh_ui_v4.html
```

### Step 5: Test

1. Open browser to `http://localhost:8080/faithh_ui_v4.html`
2. Look for "Connected" indicator in header
3. Send a test message
4. Check browser console (F12) for connection status

**Success indicators:**
- ✅ Green dot in header (Connected)
- ✅ Console shows "✅ Backend connected"
- ✅ Messages send and receive responses

---

## 🔧 Configuration

### Backend URL

If your backend isn't on port 5557, edit the UI file:

```javascript
// In faithh_ui_v4.html, line ~450
const app = {
    config: {
        backendUrl: 'http://localhost:5557',  // Change this
        // ...
    }
}
```

### Model Options

Add/remove models in the HTML:

```html
<!-- In faithh_ui_v4.html, line ~270 -->
<select id="model-select">
    <option value="gemini-pro">Gemini Pro</option>
    <option value="your-model">Your Model</option>
</select>
```

---

## 🐛 Troubleshooting

### Problem: "Offline Mode" in header

**Cause:** Backend not running or wrong URL

**Fix:**
1. Check backend is running: `curl http://localhost:5557/status`
2. Check CORS is enabled in backend
3. Check browser console for errors
4. Verify backendUrl in UI matches backend

### Problem: CORS Error

**Error:** `Access to fetch at 'http://localhost:5557/chat' from origin 'http://localhost:8080' has been blocked by CORS policy`

**Fix:** Add to your backend:
```python
from flask_cors import CORS
CORS(app)
```

### Problem: Messages don't send

**Fix:**
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check Network tab for failed requests
4. Verify backend endpoint returns correct JSON

### Problem: Backend receives requests but UI shows error

**Check:**
- Backend returns correct JSON format
- Response has `text` field
- No Python errors in backend console

---

## 📝 Minimal Backend Additions

If starting from scratch, your backend needs these endpoints:

```python
@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "chromadb": {"documents": 91302}
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    
    # Your AI logic here
    response_text = get_ai_response(message)
    
    return jsonify({
        "text": response_text,
        "tokens": len(response_text.split())
    })
```

That's it! The UI is designed to work with minimal backend requirements.

---

## 🎨 Customization

### Change Colors

Edit CSS variables at top of HTML file:

```css
:root {
    --primary: #2563eb;      /* Main blue */
    --success: #10b981;      /* Green */
    --bg-dark: #0f172a;      /* Background */
    /* ... */
}
```

### Disable Context Panel

```css
/* Add to CSS */
.context-panel {
    display: none;
}

.app-container {
    grid-template-columns: 300px 1fr; /* Remove 350px */
}
```

### Change Layout

The grid is defined here:

```css
.app-container {
    grid-template-columns: 300px 1fr 350px; /* sidebar, main, context */
    grid-template-rows: 60px 1fr;           /* header, content */
}
```

---

## 📊 Compare with Old UI

### Old UI (faithh_pet_v3.html)
- ✅ Simple, functional
- ❌ No model selector
- ❌ No context visibility
- ❌ No session stats
- ❌ Basic styling

### New UI (faithh_ui_v4.html)
- ✅ Model selector dropdown
- ✅ Live context panel
- ✅ Session statistics
- ✅ Professional design
- ✅ Responsive layout
- ✅ Better error handling
- ✅ Loading animations

---

## 🚀 Next Steps

### Week 2 Enhancements

1. **Add Chat History Persistence**
   - Save to localStorage
   - Or use backend `/history` endpoints
   
2. **Show RAG Sources**
   - Display documents used
   - Add relevance scores
   
3. **Settings Panel**
   - Temperature control
   - Max tokens slider
   - RAG on/off toggle

4. **Export Functionality**
   - Download as Markdown
   - Copy to clipboard
   - Share link generation

### Week 3+ Features

1. **File Upload**
   - Drag & drop interface
   - Add to ChromaDB
   - Process and index

2. **Streaming Responses**
   - Real-time text display
   - Word-by-word output
   - Better UX

3. **Multiple Chats**
   - Tabs for conversations
   - Quick switching
   - Auto-save

---

## 📦 File Structure

After setup, you should have:

```
~/ai-stack/
├── backend/
│   └── faithh_professional_backend.py  (your existing backend)
├── frontend/
│   └── html/
│       ├── faithh_pet_v3.html          (old - keep as backup)
│       └── faithh_ui_v4.html           (new - use this!)
└── docs/
    ├── FRONTEND_BACKEND_ARCHITECTURE.md
    └── backend_v4_template_reference.py
```

---

## ✅ Validation Checklist

Before moving on:

- [ ] Backend runs without errors
- [ ] CORS is enabled
- [ ] UI shows "Connected" status
- [ ] Can send messages
- [ ] Messages get responses
- [ ] Model selector works
- [ ] Context panel shows stats
- [ ] Console has no errors

---

## 🆘 Getting Help

**Check Console First:**
```javascript
// In browser console (F12)
console.log(app.config);  // See configuration
console.log(app.state);   // See current state
```

**Test Backend Directly:**
```bash
# Test status endpoint
curl http://localhost:5557/status

# Test chat endpoint
curl -X POST http://localhost:5557/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

**Common Issues:**
1. CORS errors → Add CORS to backend
2. Connection failed → Check backend URL
3. Empty responses → Check backend response format
4. Styling broken → Check CSS loaded correctly

---

## 📈 Performance Tips

1. **Lazy Load Messages**
   - Load older messages on scroll
   - Keep UI responsive
   
2. **Debounce Input**
   - Wait for user to finish typing
   - Reduce API calls

3. **Cache Responses**
   - Store common queries
   - Faster responses

4. **Optimize RAG**
   - Limit document retrieval
   - Better relevance scoring

---

## 🎯 Success!

If everything works:
- ✅ You have a modern, professional UI
- ✅ Clean backend integration
- ✅ Ready for Week 2 enhancements
- ✅ Scalable architecture

**Time to Week 1 Session 6:** Document this in MASTER_ACTION! 🎉

---

*Created: 2025-11-09*  
*For: FAITHH Week 2 UI Improvements*
