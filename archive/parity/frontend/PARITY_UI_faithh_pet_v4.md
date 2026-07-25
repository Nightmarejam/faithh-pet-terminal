# UI PARITY FILE - faithh_pet_v4_enhanced.html

**File:** faithh_pet_v4_enhanced.html  
**Version:** 4.0  
**Last Updated:** 2025-11-09  
**Lines:** ~1300  
**Purpose:** Main UI for FAITHH PET Terminal interface

---

## FILE OVERVIEW

**Theme:** MegaMan Battle Network PET Terminal  
**Style:** Retro gaming terminal with CRT effects  
**Architecture:** Single-file HTML with embedded CSS and JavaScript  
**Dependencies:** None (pure HTML/CSS/JS)

---

## COMPONENT MAP

This file contains **12 major components**. Each section is clearly marked with comment blocks for easy navigation and updating.

### 1. CONFIGURATION SECTION (Lines 10-50)
**Location:** `<script>` tag in `<head>`  
**Purpose:** Central configuration for all UI behavior

**Contains:**
```javascript
UI_CONFIG = {
    backend: { url, endpoints, timeout },
    models: { default, available[] },
    features: { rag, autoScroll, soundEffects, saveHistory },
    ui: { typingDelay, messageDelay, maxMessages, statusCheckInterval },
    theme: { colors }
}
```

**How to Update:**
- Change backend URL: Edit `UI_CONFIG.backend.url`
- Add new model: Add to `UI_CONFIG.models.available[]`
- Toggle features: Edit `UI_CONFIG.features.*`
- Adjust behavior: Edit `UI_CONFIG.ui.*`

**Update Frequency:** Weekly or as needed

---

### 2. BASE STYLES (Lines 52-105)
**Location:** CSS `/* BASE STYLES */` section  
**Purpose:** Core styling, body, and reset styles

**Contains:**
- CSS reset
- Body gradient background
- Font family (Courier New monospace)
- Core colors (#00ffff cyan theme)

**How to Update:**
- Change background: Edit `body { background: linear-gradient(...) }`
- Change font: Edit `font-family` property
- Adjust padding: Edit `body { padding: 20px }`

**Update Frequency:** Rarely (stable foundation)

---

### 3. SCANLINE EFFECTS (Lines 107-165)
**Location:** CSS `/* SCANLINE EFFECTS */` section  
**Purpose:** CRT monitor scanline overlay effect

**Contains:**
- `body::after` - Horizontal scanlines
- `body::before` - Darker scanlines for depth
- Fixed positioning and z-index management

**How to Update:**
- Adjust scanline intensity: Edit `rgba(0, 255, 255, 0.05)`
- Change scanline spacing: Edit `transparent 2px`
- Toggle effect: Comment out entire section

**Update Frequency:** Never (visual signature)

---

### 4. CORNER ACCENT SYSTEM (Lines 167-235)
**Location:** CSS `/* CORNER ACCENT SYSTEM */` section  
**Purpose:** Cyan corner borders on panels (MegaMan style)

**Contains:**
- `.corner-accent` class with ::before and ::after
- `.corner-bottom` class for bottom corners
- Box-shadow glow effects

**How to Update:**
- Change corner color: Edit `border-*: 3px solid #00ffff`
- Adjust corner size: Edit `width/height: 25px`
- Change glow: Edit `box-shadow: 0 0 15px rgba(...)`

**Update Frequency:** Never (visual signature)

---

### 5. HEADER COMPONENT (Lines 237-305)
**Location:** CSS `/* HEADER COMPONENT */` + HTML lines 870-880  
**Purpose:** Top bar with PET indicator, title, and clock

**Contains:**
- `.header` - Main container
- `.pet-indicator` - PET label with status dot
- `.terminal-title` - "FAITHH v4.0" title
- `.clock` - Real-time clock display

**How to Update:**
- Change title: Edit HTML `<div class="terminal-title">`
- Adjust status dot: Edit `.status-dot` CSS
- Modify colors: Edit color properties

**Update Frequency:** Rarely (version changes only)

**HTML Structure:**
```html
<div class="header">
    <div class="pet-indicator">
        <div class="status-dot" id="connectionDot"></div>
        <span>PET</span>
    </div>
    <div class="terminal-title">FAITHH v4.0</div>
    <div class="clock" id="clock">00:00:00 AM</div>
</div>
```

---

### 6. MODEL SELECTOR COMPONENT (Lines 307-380)
**Location:** CSS `/* MODEL SELECTOR COMPONENT */` + HTML lines 890-900  
**Purpose:** Dropdown to choose AI model

**Contains:**
- `.model-selector-panel` - Container with orange theme
- `.model-select` - Dropdown element
- `.model-info` - Subtitle text
- JavaScript population from `UI_CONFIG.models.available`

**How to Update:**
- Add new model: Add to `UI_CONFIG.models.available[]`
- Change colors: Edit border/background colors
- Modify dropdown style: Edit `.model-select` CSS

**Update Frequency:** Weekly (as models are added/removed)

**HTML Structure:**
```html
<div class="model-selector-panel corner-accent">
    <div class="model-selector-header">
        <div class="model-selector-title">🤖 AI MODEL</div>
        <select class="model-select" id="modelSelect"></select>
    </div>
    <div class="model-info">Select AI model</div>
</div>
```

**JavaScript Hook:**
- Function: `initializeModels()` (line ~1050)
- Populates dropdown from config

---

### 7. STATS PANEL COMPONENT (Lines 382-470)
**Location:** CSS `/* TOP SECTION */` + HTML lines 910-930  
**Purpose:** Display session statistics (messages, tokens, time)

**Contains:**
- `.stats-panel` - Container with cyan theme
- `.stats-grid` - 3-column grid layout
- `.stat-card` - Individual stat display
- Real-time updates via JavaScript

**How to Update:**
- Add new stat: Add HTML `.stat-card` + JavaScript update
- Change grid: Edit `grid-template-columns`
- Modify styling: Edit `.stat-card` CSS

**Update Frequency:** Monthly (as new metrics are added)

**HTML Structure:**
```html
<div class="stats-panel corner-accent">
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="messageCount">0</div>
            <div class="stat-label">Messages</div>
        </div>
        <!-- More stat cards -->
    </div>
</div>
```

**JavaScript Hooks:**
- Function: `updateStats()` (line ~1220)
- Updates: `messageCount`, `tokenCount`, `sessionTime`

---

### 8. AVATAR PANELS (Lines 472-550)
**Location:** CSS + HTML lines 935-950  
**Purpose:** MegaMan.EXE and PULSE character displays

**Contains:**
- `.mega-panel` - FAITHH.EXE avatar (orange theme)
- `.avatar-panel` - PULSE avatar (purple theme)
- Avatar containers with emoji placeholders

**How to Update:**
- Change avatar: Replace emoji with `<img>` tag
- Modify colors: Edit border/background colors
- Adjust size: Edit `.mega-avatar-container` dimensions

**Update Frequency:** Rarely (cosmetic only)

**HTML Structure:**
```html
<div class="mega-panel corner-accent">
    <div class="mega-avatar-container">🤖</div>
    <div class="mega-name">FAITHH.EXE</div>
    <div class="status-indicator">
        <span class="status-online">Online</span>
    </div>
</div>
```

---

### 9. NAVIGATION TABS (Lines 552-610)
**Location:** CSS `/* NAVIGATION TABS */` + HTML lines 960-980  
**Purpose:** Switch between different views (Chat, Stats, Pulse, Settings)

**Contains:**
- `.nav-tabs` - Tab container
- `.nav-tab` - Individual tab
- `.active` state styling
- Click event listeners

**How to Update:**
- Add new tab: Add HTML `.nav-tab` + event handler
- Change active tab: JavaScript toggles `.active` class
- Modify styling: Edit `.nav-tab` CSS

**Update Frequency:** Quarterly (new features)

**HTML Structure:**
```html
<div class="nav-tabs">
    <div class="nav-tab active" data-tab="chat">
        <span class="tab-icon">💬</span>
        <span>CHAT</span>
    </div>
    <!-- More tabs -->
</div>
```

**JavaScript Hook:**
- Event listener in `initializeEventListeners()` (line ~1240)

---

### 10. CHAT PANEL COMPONENT (Lines 612-750)
**Location:** CSS `/* CHAT PANEL COMPONENT */` + HTML lines 1000-1020  
**Purpose:** Main message display and input area

**Contains:**
- `.chat-panel` - Container with cyan theme
- `.chat-display` - Scrollable message area
- `.chat-input-container` - Input box and send button
- Message rendering with `.message` class

**How to Update:**
- Adjust height: Edit `min-height/max-height` in `.chat-panel`
- Change colors: Edit border/background colors
- Modify scrollbar: Edit `::-webkit-scrollbar` styles

**Update Frequency:** Weekly (UX improvements)

**HTML Structure:**
```html
<div class="chat-panel corner-accent">
    <div class="chat-display" id="chatDisplay">
        <!-- Messages populated by JavaScript -->
    </div>
    <div class="chat-input-container">
        <input type="text" class="chat-input" id="chatInput">
        <button class="btn-send" onclick="sendMessage()">SEND</button>
    </div>
</div>
```

**JavaScript Hooks:**
- Function: `sendMessage()` (line ~1120)
- Function: `addMessage()` (line ~1180)
- Function: `addTypingIndicator()` (line ~1200)

---

### 11. STATUS PANEL COMPONENT (Lines 752-840)
**Location:** CSS `/* STATUS PANEL COMPONENT */` + HTML lines 1025-1060  
**Purpose:** System status, RAG toggle, and session info

**Contains:**
- `.status-panel` - Container with purple theme
- `.status-list` - Service status display
- `.rag-toggle` - RAG enable/disable switch
- `.session-stats` - Response time, sources, etc.

**How to Update:**
- Add service: Add HTML `.status-item`
- Modify RAG toggle: Edit `.rag-toggle` CSS
- Add stat: Add HTML `.session-stat`

**Update Frequency:** Weekly (new services/features)

**HTML Structure:**
```html
<div class="status-panel corner-accent">
    <div class="status-list" id="statusList">
        <div class="status-item">
            <span class="status-name">Backend</span>
            <span class="status-value">● ONLINE</span>
        </div>
    </div>
    <div class="rag-toggle active" id="ragToggle" onclick="toggleRAG()">
        <span class="rag-label">Knowledge Base (RAG)</span>
        <div class="toggle-switch"></div>
    </div>
    <div class="session-stats">
        <!-- Session statistics -->
    </div>
</div>
```

**JavaScript Hooks:**
- Function: `toggleRAG()` (line ~1230)
- Function: `checkSystemStatus()` (line ~1100)
- Function: `updateSystemStatus()` (line ~1110)

---

### 12. APPLICATION LOGIC (Lines 1000-1300)
**Location:** `<script>` tag at bottom of HTML  
**Purpose:** All JavaScript functionality

**Contains:**
- `APP_STATE` - Application state object
- Initialization functions
- Event handlers
- API communication
- UI updates

**Major Functions:**
1. `initializeModels()` - Populate model dropdown
2. `initializeClock()` - Start clock and session timer
3. `initializeSystemCheck()` - Start status polling
4. `initializeEventListeners()` - Bind UI events
5. `sendMessage()` - Handle chat submission
6. `addMessage()` - Display message in chat
7. `checkSystemStatus()` - Poll backend status
8. `toggleRAG()` - Enable/disable RAG
9. `saveChatHistory()` - Save to localStorage
10. `loadChatHistory()` - Load from localStorage

**How to Update:**
- Add feature: Create new function + call from init
- Modify behavior: Edit existing functions
- Add event: Register in `initializeEventListeners()`

**Update Frequency:** Daily (active development)

---

## COLOR SCHEME

**Primary Colors:**
- Cyan: `#00ffff` - Main accent (headers, borders, text)
- Orange: `#ffa500` - Secondary accent (PET indicator, MEGA panel)
- Purple: `#b44cff` - Tertiary accent (PULSE panel, status)
- Red: `#ff6666` - Error states
- Green: `#00ff00` - Success states, online indicators

**Background Colors:**
- Dark: `#0a0e27` - Main background
- Medium: `#1a1f3a` - Gradient background
- Panel: `rgba(15, 20, 45, 0.9)` - Panel backgrounds
- Accent: `rgba(59, 90, 157, 0.3)` - Interactive elements

**Text Colors:**
- Primary: `#00ffff` - Main text
- Secondary: `#8899aa` - Subtitles, labels
- Content: `#e0e0e0` - Message content

---

## UPDATE PROCEDURES

### To Add a New Component:

1. **CSS Section:**
   ```css
   /* ===================================
      NEW COMPONENT NAME
      Description of purpose
      =================================== */
   .new-component {
       /* Styles here */
   }
   ```

2. **HTML Section:**
   ```html
   <!-- ===================================
        NEW COMPONENT NAME
        Description
        =================================== -->
   <div class="new-component corner-accent">
       <div class="corner-bottom"></div>
       <!-- Content -->
   </div>
   ```

3. **JavaScript Function:**
   ```javascript
   // ========================================
   // NEW COMPONENT NAME
   // Description
   // ========================================
   function initializeNewComponent() {
       // Logic here
   }
   ```

4. **Call from Init:**
   ```javascript
   document.addEventListener('DOMContentLoaded', function() {
       // ...
       initializeNewComponent();  // Add this
   });
   ```

### To Modify Existing Component:

1. Find component in **Component Map** above
2. Navigate to specified line range
3. Edit CSS/HTML/JavaScript as needed
4. Test in browser
5. Update this parity file with changes

### To Change Colors:

1. Edit `UI_CONFIG.theme` object (lines 45-50)
2. Find/replace color codes in CSS
3. Test contrast and readability

### To Add New Model:

1. Edit `UI_CONFIG.models.available[]` (lines 25-30)
2. Add object: `{ id: 'model-id', name: 'MODEL NAME', color: '#hexcolor' }`
3. No other changes needed (dropdown auto-populates)

### To Add New Stat:

1. Add HTML in stats-grid (lines 920-925):
   ```html
   <div class="stat-card">
       <div class="stat-value" id="newStat">0</div>
       <div class="stat-label">New Stat</div>
   </div>
   ```

2. Update JavaScript `APP_STATE.stats` (line ~1015):
   ```javascript
   stats: {
       messageCount: 0,
       tokenCount: 0,
       newStat: 0  // Add this
   }
   ```

3. Update in `updateStats()` function (line ~1220):
   ```javascript
   document.getElementById('newStat').textContent = APP_STATE.stats.newStat;
   ```

---

## FEATURE FLAGS

Current features can be toggled in `UI_CONFIG.features` (lines 35-40):

```javascript
features: {
    rag: true,              // Show RAG toggle (✅ Active)
    autoScroll: true,       // Auto-scroll chat (✅ Active)
    soundEffects: false,    // Sound FX (🚧 Not implemented)
    saveHistory: true       // Save to localStorage (✅ Active)
}
```

---

## DEPENDENCIES

**None!** This is a pure HTML/CSS/JavaScript file with:
- ✅ No frameworks (React, Vue, etc.)
- ✅ No build process (Webpack, Vite, etc.)
- ✅ No external CSS (Bootstrap, Tailwind, etc.)
- ✅ No external JS libraries (jQuery, Lodash, etc.)

**Advantages:**
- Fast loading
- Easy to edit
- Works anywhere
- No npm/node needed

---

## BROWSER COMPATIBILITY

**Tested on:**
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers

**Required Features:**
- CSS Grid (all modern browsers)
- CSS Animations (all modern browsers)
- Fetch API (all modern browsers)
- localStorage (all modern browsers)

---

## PERFORMANCE

**File Size:** ~50KB (single file)  
**Load Time:** <100ms on average connection  
**Memory Usage:** ~5-10MB (depends on message count)  
**CPU Usage:** Low (animations use GPU)

**Optimizations:**
- CSS-only animations (no JavaScript)
- Efficient DOM updates (appendChild vs innerHTML)
- Debounced status checks (30s intervals)
- Limited message history (max 100 by default)

---

## KNOWN ISSUES

1. **Avatar Images:** Currently using emojis, need actual images
   - Location: Lines 940, 970
   - Fix: Replace emoji with `<img src="images/avatar.png">`

2. **Tab Switching:** Tabs exist but don't switch views yet
   - Location: Lines 960-980
   - Fix: Implement view switching in JavaScript

3. **Sound Effects:** Feature flag exists but not implemented
   - Location: UI_CONFIG.features.soundEffects
   - Fix: Add Web Audio API implementation

---

## VERSION HISTORY

**v4.0 (2025-11-09):**
- ✅ Added modular component structure
- ✅ Added UI_CONFIG for easy customization
- ✅ Added model selector dropdown
- ✅ Enhanced status panel with RAG toggle
- ✅ Added session statistics
- ✅ Added localStorage chat history
- ✅ Improved code organization and comments
- ✅ Created this parity file

**v3.1 (Previous):**
- Original PET Terminal design
- Basic chat functionality
- Fixed model selection
- Simple status display

---

## MAINTENANCE CHECKLIST

**Weekly:**
- [ ] Check for console errors
- [ ] Test all buttons and inputs
- [ ] Verify backend connection
- [ ] Update model list if changed
- [ ] Test on mobile

**Monthly:**
- [ ] Review performance metrics
- [ ] Clean up localStorage if needed
- [ ] Update version number
- [ ] Review and update this parity file

**Quarterly:**
- [ ] Consider new features
- [ ] Refactor if needed
- [ ] Update documentation
- [ ] Test on new browsers

---

## QUICK REFERENCE

**Files to Update:**
1. **This file only!** (faithh_pet_v4_enhanced.html)

**Common Edits:**
- Backend URL: Line 23
- Add model: Line 27
- Change colors: Lines 45-50
- Adjust stats: Line 920
- Modify chat: Line 1000

**Testing:**
1. Open in browser
2. Open console (F12)
3. Check for errors
4. Test chat functionality
5. Verify status updates

---

**Last Parity Check:** 2025-11-09  
**Next Parity Check:** 2025-11-16  
**Maintained by:** FAITHH Development Team
