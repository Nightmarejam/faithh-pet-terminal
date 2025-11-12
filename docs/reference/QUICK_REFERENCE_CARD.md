# ⚡ FAITHH v4 Quick Reference Card
**Use this for fast lookups during implementation**

---

## 🎨 Color Codes (Copy/Paste Ready)
```css
--cyan-primary: #00ffff;     /* FAITHH accent */
--blue-primary: #3b82f6;     /* PULSE accent */
--dark-bg: #0a0e27;          /* Main background */
--darker-bg: #050810;        /* Panels */
--status-online: #22c55e;    /* Green */
--status-warning: #eab308;   /* Yellow */
--status-error: #ef4444;     /* Red */
--text-primary: #ffffff;     /* White text */
--text-secondary: #94a3b8;   /* Gray text */
```

---

## 📁 File Paths
```bash
# UI Files
~/ai-stack/faithh_pet_v3.html                      # v3 stable (keep!)
~/ai-stack/frontend/html/faithh_pet_v4_final.html # v4 new

# Images
~/ai-stack/images/faithh_v2/avatars/faithh_small.png
~/ai-stack/images/faithh_v2/avatars/pulse_small.png

# Backend
~/ai-stack/faithh_professional_backend.py         # Main backend

# Backups
~/ai-stack/backups/faithh_professional_backend_v3_stable_*.py

# Documentation
~/ai-stack/docs/LEONARDO_AI_PROMPTS_ENHANCED.md
~/ai-stack/docs/FAITHH_V4_UI_SPECIFICATION.md
~/ai-stack/docs/FAITHH_V4_BACKEND_API.md
~/ai-stack/docs/VS_CODE_IMPLEMENTATION_HANDOFF.md

# Parity
~/ai-stack/parity/frontend/PARITY_UI_faithh_pet_v4_final.md
~/ai-stack/parity/backend/PARITY_BACKEND_v4.md
```

---

## 🔌 API Endpoints Quick List

### Existing (v3):
```bash
GET  /                      # Home
GET  /images/<filename>     # Images
POST /api/chat              # Main chat
POST /api/upload            # Upload files
POST /api/rag_search        # RAG search
GET  /api/status            # System status
GET  /api/workspace/scan    # Scan workspace
GET  /health                # Health check
```

### New (v4):
```bash
GET    /api/session/stats      # Session statistics
POST   /api/session/reset      # Reset session
GET    /api/avatar/state       # Avatar states
POST   /api/avatar/state       # Update avatar
GET    /api/chat/history       # Chat history
DELETE /api/chat/history       # Clear history
GET    /api/models             # List models
POST   /api/models/switch      # Switch model
```

---

## 🧪 Quick Test Commands
```bash
# Test backend is running
curl http://localhost:5557/api/status

# Test session stats
curl http://localhost:5557/api/session/stats

# Test avatar state
curl http://localhost:5557/api/avatar/state

# Test chat (send message)
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello FAITHH","use_rag":true}'

# Reset session
curl -X POST http://localhost:5557/api/session/reset

# Switch model
curl -X POST http://localhost:5557/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_id":"llama3.1-8b"}'
```

---

## 🚨 Emergency Rollback
```bash
# If backend breaks:
pkill -f faithh_professional_backend
cp backups/faithh_professional_backend_v3_stable_*.py \
   faithh_professional_backend.py
python faithh_professional_backend.py

# If UI breaks:
# Just reload faithh_pet_v3.html instead of v4

# Full git rollback:
git checkout HEAD -- faithh_professional_backend.py
git status
```

---

## 📐 Layout Measurements
```
Desktop Layout (1920x1080):
├─ LEFT SIDEBAR:  200px width (fixed)
├─ CENTER CHAT:   ~60% width (fluid)
└─ RIGHT PANEL:   300px width (fixed)

Header Bar: 60px height (fixed)

Avatar Boxes: 180x200px each (stacked vertically)

Message Bubbles:
- Max width: 70% of chat panel
- Padding: 12px
- Margin: 8px between messages

Input Box:
- Min height: 3 rows
- Max height: 5 rows
```

---

## 🎭 Key Animations
```css
/* Avatar Pulse */
@keyframes avatar-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

/* Loading Dots */
@keyframes loading-dots {
    0%, 20% { opacity: 0; }
    50% { opacity: 1; }
    100% { opacity: 0; }
}

/* Scanline */
@keyframes scanline {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100%); }
}

/* Glow */
@keyframes glow {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}
```

---

## 🔧 Backend Data Structures
```python
# Session Stats
session_stats = {
    'message_count': 0,
    'total_tokens': 0,
    'start_time': datetime.now().isoformat(),
    'last_activity': datetime.now().isoformat(),
    'response_times': []
}

# Avatar State
avatar_state = {
    'faithh': {
        'status': 'online',  # online, busy, offline
        'activity': 'idle',  # idle, thinking, responding
        'last_active': datetime.now().isoformat()
    },
    'pulse': {
        'status': 'online',  # online, warning, error
        'activity': 'monitoring',
        'last_active': datetime.now().isoformat()
    }
}

# Chat History
chat_history = [
    {
        'id': 'msg_123',
        'role': 'user',  # or 'assistant'
        'content': 'Message text',
        'timestamp': '2025-11-09T14:23:15Z',
        'model': 'gemini-2.0-flash-exp',  # assistant only
        'tokens': 245,                     # assistant only
        'response_time': 1.8,              # assistant only
        'sources': [...]                   # if RAG used
    }
]

# Current Model
current_model = {
    'name': 'gemini-2.0-flash-exp',
    'provider': 'gemini',
    'last_response_time': 0.0,
    'last_tokens': 0
}
```

---

## 🎨 Leonardo AI Quick Settings
```
Model: Leonardo Phoenix (characters) or Kino XL (UI mockups)
Resolution: 1024x1024 (avatars), 1920x1080 (mockups)
Guidance Scale: 7-10
Number of Images: 4
Negative Prompt: blurry, low quality, distorted
```

---

## 📋 Component HTML Templates

### Avatar Box:
```html
<div class="avatar-panel corner-accent">
    <div class="avatar-container faithh-avatar">
        <img src="images/faithh_v2/avatars/faithh_small.png" alt="FAITHH">
    </div>
    <div class="avatar-name">FAITHH</div>
    <div class="avatar-status online">● Online</div>
</div>
```

### Message Bubble (User):
```html
<div class="message user-message">
    <div class="message-avatar user-avatar">U</div>
    <div class="message-content">
        <div class="message-text">User's message</div>
        <div class="message-meta">
            <span class="timestamp">14:23:15</span>
        </div>
    </div>
</div>
```

### Message Bubble (Assistant):
```html
<div class="message assistant-message">
    <div class="message-avatar assistant-avatar">
        <img src="images/faithh_v2/avatars/faithh_small.png" alt="FAITHH">
    </div>
    <div class="message-content">
        <div class="message-text">FAITHH's response</div>
        <div class="message-meta">
            <span class="timestamp">14:23:18</span>
            <span class="model-badge">GEMINI</span>
            <span class="tokens">245 tokens</span>
        </div>
    </div>
</div>
```

### Stats Panel:
```html
<div class="stats-panel">
    <div class="stat-row">
        <span class="stat-label">Messages:</span>
        <span class="stat-value" id="messageCount">0</span>
    </div>
    <div class="stat-row">
        <span class="stat-label">Tokens:</span>
        <span class="stat-value" id="tokenCount">0</span>
    </div>
</div>
```

---

## 🔢 Common Calculations

### Average Response Time:
```javascript
function calculateAvgResponse(responseTimes) {
    if (responseTimes.length === 0) return 0;
    const sum = responseTimes.reduce((a, b) => a + b, 0);
    return (sum / responseTimes.length).toFixed(2);
}
```

### Session Duration:
```javascript
function calculateSessionDuration(startTime) {
    const start = new Date(startTime);
    const now = new Date();
    const seconds = Math.floor((now - start) / 1000);
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${pad(hours)}:${pad(mins)}:${pad(secs)}`;
}

function pad(n) {
    return n.toString().padStart(2, '0');
}
```

### Format Timestamp:
```javascript
function formatTimestamp(date) {
    return date.toTimeString().split(' ')[0]; // HH:MM:SS
}
```

---

## ⚡ Performance Tips

### Backend:
- Use in-memory storage (dict/list) for session data
- Don't persist to disk unless needed
- Limit chat_history to last 100 messages
- Cache system status for 5 seconds
- Use threading for long-running tasks

### Frontend:
- Debounce rapid API calls
- Limit chat container to 100 visible messages
- Use requestAnimationFrame for animations
- Lazy load old messages on scroll
- Cache avatar images

---

## 🐛 Common Issues & Fixes

### "Backend not responding"
```bash
# Check if running
ps aux | grep faithh_professional_backend

# Check port
lsof -i :5557

# Restart
pkill -f faithh_professional_backend
cd ~/ai-stack && python faithh_professional_backend.py
```

### "CORS error in browser console"
```python
# Add to backend
from flask_cors import CORS
CORS(app)
```

### "Images not loading"
```javascript
// Check image paths
console.log('Image path:', document.querySelector('img').src);

// Use absolute paths
<img src="/images/faithh_v2/avatars/faithh_small.png" alt="FAITHH">
```

### "Stats not updating"
```javascript
// Check polling interval
setInterval(updateStats, 5000); // Every 5 seconds

// Check API response
fetch('/api/session/stats')
    .then(r => r.json())
    .then(data => console.log('Stats:', data));
```

---

## ✅ Quick Validation Checklist

### Before Committing Code:
- [ ] Backend responds to all endpoints
- [ ] UI loads without console errors
- [ ] Can send and receive messages
- [ ] Stats update correctly
- [ ] Animations run smoothly
- [ ] Tested in browser
- [ ] v3 still works (no regressions)

### Before Switching from v3 to v4:
- [ ] v4 has all v3 features
- [ ] v4 tested for 1 hour minimum
- [ ] No crashes or major bugs
- [ ] Backups created
- [ ] Confident in the change

---

## 📞 When You Need Help

### Check These First:
1. Browser console (F12) for errors
2. Backend terminal for error logs
3. curl test endpoints directly
4. Compare with working v3 code
5. Review specification docs

### Common Solutions:
- Clear browser cache
- Restart backend
- Check file paths
- Verify JSON structure
- Test with simple data first

---

**Keep this document open while coding for quick reference!** ⚡

---

**Created:** November 9, 2025  
**Purpose:** Fast lookups during FAITHH v4 implementation  
**Use:** Copy/paste code, check paths, verify endpoints, debug issues
