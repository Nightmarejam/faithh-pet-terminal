# 🎯 FAITHH v4 UI Component Specification
**Created:** November 9, 2025  
**Version:** 4.0 Final Design  
**Purpose:** Complete blueprint for VS Code implementation

---

## 📐 Layout Architecture

### Three-Panel Layout (Desktop)
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER BAR (Fixed, 60px height)                           │
│  • PET Terminal v4.0 title                                  │
│  • Connection status indicator                              │
├──────────┬──────────────────────────────┬──────────────────┤
│          │                              │                  │
│  LEFT    │     CENTER CHAT PANEL        │   RIGHT PANEL    │
│  SIDEBAR │     (Main conversation)      │   (Stats/Info)   │
│  200px   │     (Fluid width)            │   300px          │
│          │                              │                  │
│  Avatar  │  Message bubbles scroll here │  Model selector  │
│  Boxes   │  ▲                           │  Session stats   │
│          │  │ Scrollable                │  RAG toggle      │
│  FAITHH  │  │                           │  System status   │
│  ┌────┐  │  ▼                           │                  │
│  │ 🟦 │  │                              │  Source display  │
│  └────┘  │  ┌─────────────────────────┐ │  (when RAG used) │
│          │  │ Message input box       │ │                  │
│  PULSE   │  │ [Type message...]       │ │                  │
│  ┌────┐  │  └─────────────────────────┘ │                  │
│  │ 🔷 │  │  [SEND] [RAG]               │                  │
│  └────┘  │                              │                  │
└──────────┴──────────────────────────────┴──────────────────┘
```

---

## 🧩 Component Breakdown

### 1. LEFT SIDEBAR: Avatar Monitoring Boxes

#### Component: Avatar Box (Reusable)
```html
<div class="avatar-panel corner-accent">
    <div class="avatar-container {character}-avatar">
        <img src="images/faithh_v2.png" alt="FAITHH" class="avatar-image">
        <div class="avatar-glow"></div> <!-- Animated glow effect -->
    </div>
    <div class="avatar-info">
        <div class="avatar-name">FAITHH</div>
        <div class="avatar-status online">● Online</div>
        <div class="avatar-subtitle">Ready to help</div>
    </div>
</div>
```

**Behavior:**
- ✅ Always visible (fixed position)
- ✅ Subtle pulse/breathing animation on avatar
- ✅ Status indicator changes color: green (online), yellow (busy), red (offline)
- ✅ Clickable to expand to full character view (future feature)
- ✅ Shows activity indicator when processing

**States:**
- `online` - Green dot, normal animation
- `busy` - Yellow dot, faster pulse
- `offline` - Red dot, dimmed, no animation
- `active` - Highlighted border when actively responding

---

### 2. CENTER PANEL: Chat Interface

#### Component: Chat Container
```html
<div class="chat-panel">
    <div class="messages-container" id="messagesContainer">
        <!-- Messages dynamically inserted here -->
    </div>
    <div class="input-section">
        <textarea id="messageInput" 
                  placeholder="Type your message..." 
                  rows="3"></textarea>
        <div class="input-controls">
            <button id="sendButton" class="primary-btn">
                <span class="btn-icon">▶</span> SEND
            </button>
            <label class="toggle-switch">
                <input type="checkbox" id="ragToggle">
                <span class="toggle-slider"></span>
                <span class="toggle-label">RAG</span>
            </label>
        </div>
    </div>
</div>
```

**Behavior:**
- ✅ Auto-scroll to bottom when new message arrives
- ✅ Input textarea expands up to 5 rows as user types
- ✅ Send button disables while waiting for response
- ✅ Loading animation displays while processing
- ✅ RAG toggle glows cyan when enabled
- ✅ Enter key sends message (Shift+Enter for new line)

---

#### Component: Message Bubble
```html
<!-- User Message -->
<div class="message user-message">
    <div class="message-avatar user-avatar">U</div>
    <div class="message-content">
        <div class="message-text">User's question here</div>
        <div class="message-meta">
            <span class="timestamp">14:23:15</span>
        </div>
    </div>
</div>

<!-- Assistant Message -->
<div class="message assistant-message">
    <div class="message-avatar assistant-avatar">
        <img src="images/faithh_v2_small.png" alt="FAITHH">
    </div>
    <div class="message-content">
        <div class="message-text">FAITHH's response here</div>
        <div class="message-meta">
            <span class="timestamp">14:23:18</span>
            <span class="model-badge">GEMINI</span>
            <span class="tokens">245 tokens</span>
        </div>
        <!-- Sources shown if RAG was used -->
        <div class="message-sources" style="display:none;">
            <div class="source-item">📄 document.md (relevance: 0.92)</div>
        </div>
    </div>
</div>

<!-- Loading Message (Temporary) -->
<div class="message assistant-message loading">
    <div class="message-avatar assistant-avatar">
        <img src="images/faithh_v2_small.png" alt="FAITHH">
    </div>
    <div class="message-content">
        <div class="loading-dots">
            <span></span><span></span><span></span>
        </div>
        <div class="message-meta">Thinking...</div>
    </div>
</div>
```

**Behavior:**
- ✅ User messages align right with different color
- ✅ Assistant messages align left with FAITHH avatar
- ✅ Loading message shows animated dots while waiting
- ✅ Sources collapse/expand when clicked
- ✅ Timestamps in HH:MM:SS format
- ✅ Copy button appears on hover (future)

---

### 3. RIGHT PANEL: Stats & Settings

#### Component: Model Selector
```html
<div class="panel-section">
    <label class="section-label">AI MODEL</label>
    <select id="modelSelector" class="model-dropdown">
        <option value="gemini-2.0-flash-exp" selected>GEMINI 2.0 FLASH</option>
        <option value="gemini-1.5-pro">GEMINI 1.5 PRO</option>
        <option value="llama3.1-8b">LLAMA 3.1 8B (Ollama)</option>
        <option value="qwen2.5-7b">QWEN 2.5 7B (Ollama)</option>
    </select>
</div>
```

**Behavior:**
- ✅ Dropdown with custom styling (cyan accent)
- ✅ Changes take effect immediately for next message
- ✅ Shows current model in conversation metadata
- ✅ Disables unavailable models (grayed out)

---

#### Component: Session Statistics
```html
<div class="panel-section stats-panel">
    <label class="section-label">SESSION STATS</label>
    <div class="stat-row">
        <span class="stat-label">Messages:</span>
        <span class="stat-value" id="messageCount">0</span>
    </div>
    <div class="stat-row">
        <span class="stat-label">Total Tokens:</span>
        <span class="stat-value" id="tokenCount">0</span>
    </div>
    <div class="stat-row">
        <span class="stat-label">Session Time:</span>
        <span class="stat-value" id="sessionTime">00:00:00</span>
    </div>
    <div class="stat-row">
        <span class="stat-label">Avg Response:</span>
        <span class="stat-value" id="avgResponse">0.0s</span>
    </div>
</div>
```

**Behavior:**
- ✅ Updates in real-time after each message
- ✅ Session time ticks every second
- ✅ Resets when chat is cleared
- ✅ Persists across page refreshes (localStorage)

---

#### Component: System Status Panel
```html
<div class="panel-section status-panel">
    <label class="section-label">SYSTEM STATUS</label>
    <div class="status-item">
        <span class="status-label">Backend:</span>
        <span class="status-indicator online">● ONLINE</span>
    </div>
    <div class="status-item">
        <span class="status-label">ChromaDB:</span>
        <span class="status-indicator online">● 91,302 docs</span>
    </div>
    <div class="status-item">
        <span class="status-label">Ollama:</span>
        <span class="status-indicator online">● 2 models</span>
    </div>
    <div class="status-item">
        <span class="status-label">Gemini API:</span>
        <span class="status-indicator online">● Ready</span>
    </div>
</div>
```

**Behavior:**
- ✅ Polls `/api/status` every 5 seconds
- ✅ Color-coded indicators: green (online), red (offline), yellow (warning)
- ✅ Shows document count for ChromaDB
- ✅ Shows model count for Ollama
- ✅ Clickable to expand details (future)

---

#### Component: RAG Source Display (Conditional)
```html
<div class="panel-section sources-panel" id="sourcesPanel" style="display:none;">
    <label class="section-label">RAG SOURCES</label>
    <div class="source-list" id="sourceList">
        <!-- Dynamically populated when RAG used -->
        <div class="source-item">
            <div class="source-title">document_name.md</div>
            <div class="source-relevance">Relevance: 92%</div>
            <div class="source-preview">Preview of content...</div>
        </div>
    </div>
</div>
```

**Behavior:**
- ✅ Only visible when RAG is enabled and sources exist
- ✅ Shows up to 5 most relevant sources
- ✅ Click to expand full content (modal or side panel)
- ✅ Relevance score shown as percentage
- ✅ Collapses when RAG is disabled

---

## 🎨 Visual Design System

### Color Palette
```css
/* Primary Colors */
--cyan-primary: #00ffff;        /* FAITHH accent, highlights */
--blue-primary: #3b82f6;        /* PULSE accent, secondary */
--dark-bg: #0a0e27;             /* Main background */
--darker-bg: #050810;           /* Panel backgrounds */
--black-bg: #000000;            /* Deep shadows */

/* Status Colors */
--status-online: #22c55e;       /* Green - online/success */
--status-warning: #eab308;      /* Yellow - warning/busy */
--status-error: #ef4444;        /* Red - error/offline */

/* Text Colors */
--text-primary: #ffffff;        /* Main text */
--text-secondary: #94a3b8;      /* Secondary text */
--text-muted: #64748b;          /* Muted text */

/* UI Colors */
--border-color: #1e293b;        /* Panel borders */
--border-glow: rgba(0, 255, 255, 0.3); /* Glowing borders */
```

### Typography
```css
/* Fonts */
--font-display: 'Orbitron', 'Share Tech Mono', monospace;  /* Headers, titles */
--font-mono: 'Courier New', 'Roboto Mono', monospace;      /* Code, tech elements */
--font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI'; /* Body text */

/* Sizes */
--text-xs: 0.75rem;    /* 12px - small labels */
--text-sm: 0.875rem;   /* 14px - secondary text */
--text-base: 1rem;     /* 16px - body text */
--text-lg: 1.125rem;   /* 18px - emphasized text */
--text-xl: 1.5rem;     /* 24px - headings */
--text-2xl: 2rem;      /* 32px - large titles */
```

### Spacing Scale
```css
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */
--space-4: 1rem;       /* 16px */
--space-6: 1.5rem;     /* 24px */
--space-8: 2rem;       /* 32px */
```

---

## 🎭 Animations & Effects

### 1. Avatar Pulse Animation
```css
@keyframes avatar-pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
}

.avatar-image {
    animation: avatar-pulse 3s ease-in-out infinite;
}
```

### 2. Loading Dots
```css
@keyframes loading-dots {
    0%, 20% { opacity: 0; }
    50% { opacity: 1; }
    100% { opacity: 0; }
}

.loading-dots span {
    animation: loading-dots 1.4s infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
```

### 3. CRT Scanline Effect
```css
@keyframes scanline {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100%); }
}

.scanline-overlay::before {
    animation: scanline 8s linear infinite;
}
```

### 4. Corner Accent Glow
```css
@keyframes corner-glow {
    0%, 100% { opacity: 0.5; box-shadow: 0 0 10px var(--cyan-primary); }
    50% { opacity: 1; box-shadow: 0 0 20px var(--cyan-primary); }
}

.corner-accent {
    animation: corner-glow 2s ease-in-out infinite;
}
```

---

## 📱 Responsive Behavior

### Desktop (1200px+)
- Three-panel layout as designed
- Sidebars fixed width
- Center panel fluid

### Tablet (768px - 1199px)
- Right panel collapses to icon buttons
- Left sidebar reduces to 150px
- Stats shown in overlay on click

### Mobile (< 768px)
- Single column layout
- Avatar boxes shown as header bar icons
- Stats and settings in slide-out drawer
- Full-width chat panel

---

## 🔌 Backend Integration Points

### API Endpoints Required
```javascript
// Chat endpoint (existing)
POST /api/chat
Body: { message, model, use_rag }
Response: { response, sources?, tokens, time }

// Status endpoint (existing)
GET /api/status
Response: { services: {chromadb, gemini, ollama}, workspace }

// New endpoints needed:
GET /api/session/stats
Response: { message_count, token_count, session_start, avg_response_time }

POST /api/session/reset
Response: { success: true }

GET /api/avatar/state
Response: { faithh_status, pulse_status, activity }

POST /api/avatar/state
Body: { character, status, activity }
Response: { success: true }
```

---

## 🧪 Component Testing Checklist

### Avatar Boxes
- [ ] FAITHH avatar loads correctly
- [ ] PULSE avatar loads correctly
- [ ] Pulse animation plays smoothly
- [ ] Status indicators change color
- [ ] Click expands to full view (future)

### Chat Interface
- [ ] Messages send successfully
- [ ] Loading indicator appears while waiting
- [ ] Responses display properly
- [ ] Auto-scroll works
- [ ] RAG toggle functions correctly
- [ ] Sources display when RAG used

### Stats Panel
- [ ] Message count increments
- [ ] Token count updates
- [ ] Session time ticks every second
- [ ] Average response time calculates correctly

### System Status
- [ ] Backend status shows online/offline
- [ ] ChromaDB document count displays
- [ ] Ollama model count shows
- [ ] Status updates every 5 seconds

---

## 📦 File Structure

```
~/ai-stack/
├── frontend/html/
│   └── faithh_pet_v4_final.html         ← Main UI file
├── images/faithh_v2/
│   ├── avatars/
│   │   ├── faithh_small.png             ← Avatar box (128x128)
│   │   └── pulse_small.png              ← Avatar box (128x128)
│   ├── characters/
│   │   ├── faithh_full.png              ← Full character (512x512+)
│   │   └── pulse_full.png               ← Full character (512x512+)
│   └── icons/
│       └── ui_icons.png                 ← Icon sprite sheet
└── backend/
    └── faithh_professional_backend.py   ← Backend (needs new endpoints)
```

---

## ✅ Implementation Checklist (For VS Code)

### Phase 1: Structure (30 min)
- [ ] Create HTML structure with 3-panel layout
- [ ] Add avatar boxes (left sidebar)
- [ ] Add chat container (center)
- [ ] Add stats panels (right sidebar)

### Phase 2: Styling (45 min)
- [ ] Apply color palette
- [ ] Add CRT effects and scanlines
- [ ] Style message bubbles
- [ ] Style buttons and controls
- [ ] Add corner accents

### Phase 3: JavaScript (60 min)
- [ ] Connect to backend API
- [ ] Implement message send/receive
- [ ] Add loading states
- [ ] Implement RAG toggle
- [ ] Update session stats
- [ ] Poll system status

### Phase 4: Animations (30 min)
- [ ] Add avatar pulse animation
- [ ] Add loading dots animation
- [ ] Add scanline effect
- [ ] Add glow effects

### Phase 5: Testing (30 min)
- [ ] Test all features
- [ ] Test on different screens
- [ ] Fix bugs
- [ ] Performance optimization

---

## 🎯 Success Criteria

### UI is ready when:
- ✅ All components render correctly
- ✅ Avatar boxes show FAITHH and PULSE
- ✅ Chat messages send and display
- ✅ RAG toggle works
- ✅ Stats update in real-time
- ✅ System status reflects backend health
- ✅ Animations run smoothly
- ✅ Responsive on desktop
- ✅ No console errors
- ✅ Retro aesthetic feels right

---

**This specification is ready for VS Code implementation!**  
All components, behaviors, and styles are documented in detail.
