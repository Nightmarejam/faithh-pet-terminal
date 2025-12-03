# PARITY: faithh_pet_v3.html
**Last Updated:** 2025-11-09
**Status:** Active
**Version:** 3.0.0

---

## Current State

**Purpose:** MegaMan Battle Network themed chat interface for FAITHH AI assistant

**Key Features:**
- Real-time chat with AI
- Model selection dropdown
- RAG toggle switch
- System status indicator (heartbeat every 30s)
- MegaMan aesthetic (cyan/green gradient)
- Battle chip UI elements
- Responsive design

**Dependencies:**
- Backend API: http://localhost:5557
- No external CDN dependencies (self-contained)
- Pure HTML/CSS/JavaScript

---

## Recent Changes

### 2025-11-09 - Kept in Root
**Decision:**
- Kept in root directory for easy browser access
- Other HTML files moved to frontend/html/

**Reason:** Active UI should be easily accessible

### 2025-11-04 - Version 3 Creation
**Created:**
- MegaMan themed interface
- Battle chip design elements
- System status heartbeat
- Model selection feature
- RAG toggle

---

## Known Issues

- [ ] System status panel sometimes disappears (mentioned by user)
- [ ] No error message display for failed API calls
- [ ] No loading indicator during API requests
- [ ] No message history persistence

---

## Pending Changes

- [ ] Add context visibility panel
- [ ] Add process queue display
- [ ] Add battle chip system for tools
- [ ] Add message history save/load
- [ ] Improve error handling UI
- [ ] Add loading animations

---

## API Endpoints Used

**Backend Connection:**
- `GET /api/status` - Health check (polled every 30s)
- `POST /api/chat` - Send message, receive response
  - Body: `{message: string, model: string, use_rag: boolean}`
- `GET /api/models` - Get available model list

**Expected Responses:**
```javascript
// /api/status
{status: "ok", chromadb_docs: 91302}

// /api/chat
{response: "AI response text here"}

// /api/models
{models: ["gemini-pro", "llama3.1", ...]}
```

---

## UI Components

**Main Areas:**
1. **Header** - Title and branding
2. **System Status** - Server health indicator
3. **Chat Area** - Message display
4. **Controls** - Model select, RAG toggle
5. **Input** - Text input and send button

**Design Theme:**
- MegaMan Battle Network inspired
- Cyan/green color palette
- Retro-futuristic aesthetic
- Battle chip UI elements

---

## Testing

**How to Test:**
1. Ensure backend running: `python3 faithh_professional_backend.py`
2. Open in browser: `file:///home/jonat/ai-stack/faithh_pet_v3.html`
   - Or navigate to: `http://localhost:5557/`
3. Check system status shows green heartbeat
4. Send test message
5. Verify response appears

**Expected Behavior:**
- UI loads without errors
- System status shows "ONLINE" with heartbeat
- Can send messages
- Receives responses
- Model selection works
- RAG toggle works

---

## Configuration

**Backend URL:**
```javascript
const BACKEND_URL = 'http://localhost:5557';
```

**Polling Interval:**
```javascript
const STATUS_CHECK_INTERVAL = 30000; // 30 seconds
```

---

## Future Enhancements

**Planned Features (from architecture docs):**
1. **Context Panel** - Show what AI can see (RAG docs, files)
2. **Process Queue** - Display what AI is doing
3. **Battle Chips** - Visual tool selection system
4. **PULSE Monitor** - System health visualization
5. **Session History** - Save/load conversations

---

## Design Philosophy

**Goals:**
- Make AI interaction fun and engaging
- Visual feedback for all actions
- Clear system status
- Retro aesthetic that's still modern
- Battle chip metaphor for tools/commands

**Inspiration:**
- MegaMan Battle Network series
- Retro terminal UIs
- Cyberpunk aesthetics

---

## Notes

- Self-contained single file (no separate CSS/JS files)
- Works offline once loaded (except API calls)
- Kept in root for convenience
- 35KB file size (reasonable)
- No build process required

---

*Last reviewed: 2025-11-09*
