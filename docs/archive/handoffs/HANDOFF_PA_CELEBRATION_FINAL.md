# Handoff: PA Celebration UI - Final Implementation

**Priority**: P1
**Date**: 2026-01-03
**Status**: Needs clean implementation

---

## Problem

The PA celebration code exists in `frontend/html/faithh_pet_v4_enhanced.html` but:
1. That file has different tab structure than the working `faithh_pet_v4.html`
2. Images don't load correctly
3. Tabs don't work properly
4. The two files have diverged significantly

## Objective

Add PA celebration to the WORKING `faithh_pet_v4.html` file without breaking existing functionality.

## Current State

- Backend: Working at localhost:5557
- PULSE API: Working (`/api/pulse/chips` returns unlocked PAs)
- PA unlocked: "Project Historian" (decisions + scaffolding combo)
- Working UI: `faithh_pet_v4.html` in BASE_DIR
- Broken UI: `frontend/html/faithh_pet_v4_enhanced.html`

## Required Changes to faithh_pet_v4.html

### 1. Add CSS (before </style>)
```css
/* Program Advance Celebration */
.pa-celebration-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 9999;
    display: none;
    justify-content: center;
    align-items: center;
    flex-direction: column;
}

.pa-celebration-overlay.active {
    display: flex;
    animation: flashIn 0.2s ease-out;
}

@keyframes flashIn {
    0% { background: rgba(255, 255, 255, 0.9); }
    100% { background: rgba(0, 0, 0, 0.8); }
}

.pa-title {
    font-family: 'Courier New', monospace;
    font-size: 3rem;
    font-weight: bold;
    color: #FFD700;
    text-shadow: 
        0 0 10px rgba(255, 215, 0, 0.8),
        0 0 20px rgba(255, 215, 0, 0.6),
        0 0 40px rgba(255, 140, 0, 0.4),
        3px 3px 0 #FF8C00;
    animation: slamIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    text-align: center;
}

@keyframes slamIn {
    0% { transform: scale(8) rotate(-5deg); opacity: 0; }
    50% { opacity: 0.5; }
    80% { transform: scale(1.1) rotate(2deg); }
    100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

.pa-name {
    font-family: 'Courier New', monospace;
    font-size: 2rem;
    color: #00CED1;
    text-shadow: 0 0 10px rgba(0, 206, 209, 0.8);
    margin-top: 1rem;
    animation: fadeSlideUp 0.5s ease-out 0.3s both;
}

@keyframes fadeSlideUp {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}

.pa-message {
    font-size: 1rem;
    color: #aaa;
    margin-top: 1rem;
    max-width: 400px;
    text-align: center;
    animation: fadeSlideUp 0.5s ease-out 0.5s both;
}

.pa-dismiss {
    margin-top: 2rem;
    padding: 0.5rem 2rem;
    background: linear-gradient(180deg, #4169E1 0%, #2040A0 100%);
    border: 2px solid #60A0FF;
    color: #fff;
    font-family: 'Courier New', monospace;
    cursor: pointer;
    animation: fadeSlideUp 0.5s ease-out 0.7s both;
}

.pa-dismiss:hover {
    box-shadow: 0 0 15px rgba(96, 160, 255, 0.7);
}

.screen-shake {
    animation: shake 0.3s ease-out;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-5px); }
    40% { transform: translateX(5px); }
    60% { transform: translateX(-3px); }
    80% { transform: translateX(3px); }
}
```

### 2. Add HTML (before </body>)
```html
<!-- Program Advance Celebration Overlay -->
<div id="paCelebrationOverlay" class="pa-celebration-overlay" aria-hidden="true">
    <div class="pa-title">PROGRAM ADVANCE!</div>
    <div class="pa-name" id="paCelebrationName">—</div>
    <div class="pa-message" id="paCelebrationMessage">—</div>
    <button class="pa-dismiss" id="paCelebrationDismissBtn">JACK OUT</button>
</div>
```

### 3. Add JavaScript (in script section, after APP_STATE)
```javascript
// ========================================
// PROGRAM ADVANCE CELEBRATION
// ========================================
const PA_SEEN_KEY = 'faithh_seen_pas_v1';

function getSeenPAs() {
    try { return JSON.parse(localStorage.getItem(PA_SEEN_KEY) || '[]'); }
    catch { return []; }
}

function markPASeen(name) {
    const seen = new Set(getSeenPAs());
    seen.add(name);
    localStorage.setItem(PA_SEEN_KEY, JSON.stringify([...seen]));
}

function hasSeenPA(name) {
    return getSeenPAs().includes(name);
}

window.showPACelebration = function(pa) {
    if (!pa || !pa.name) return;
    if (hasSeenPA(pa.name)) return;
    
    const overlay = document.getElementById('paCelebrationOverlay');
    const nameEl = document.getElementById('paCelebrationName');
    const msgEl = document.getElementById('paCelebrationMessage');
    
    nameEl.textContent = pa.name;
    msgEl.textContent = pa.message || 'New synergy unlocked!';
    
    document.body.classList.add('screen-shake');
    setTimeout(() => document.body.classList.remove('screen-shake'), 350);
    
    overlay.classList.add('active');
    overlay.setAttribute('aria-hidden', 'false');
    
    markPASeen(pa.name);
};

window.dismissPACelebration = function() {
    const overlay = document.getElementById('paCelebrationOverlay');
    overlay.classList.remove('active');
    overlay.setAttribute('aria-hidden', 'true');
};

async function pollProgramAdvancesOnce() {
    try {
        const res = await fetch('/api/pulse/chips');
        if (!res.ok) return;
        const data = await res.json();
        const pas = data.program_advances || [];
        
        for (const pa of pas) {
            const name = typeof pa === 'string' ? pa : pa.name;
            if (name && !hasSeenPA(name)) {
                window.showPACelebration({
                    name: name,
                    message: pa.message || 'Program Advance detected!'
                });
                break;
            }
        }
    } catch (e) {
        console.warn('PA poll failed:', e);
    }
}

// Wire up dismiss handlers
document.addEventListener('DOMContentLoaded', function() {
    const dismissBtn = document.getElementById('paCelebrationDismissBtn');
    const overlay = document.getElementById('paCelebrationOverlay');
    
    if (dismissBtn) {
        dismissBtn.addEventListener('click', window.dismissPACelebration);
    }
    if (overlay) {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) window.dismissPACelebration();
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') window.dismissPACelebration();
    });
    
    // Poll for PAs on load
    pollProgramAdvancesOnce();
});
```

### 4. Hook into sendMessage response

Find where `/api/chat` response is handled and add:
```javascript
if (data.pa_unlocked) {
    window.showPACelebration(data.pa_unlocked);
}
```

---

## Testing

1. Hard refresh browser (Cmd+Shift+R)
2. Console test: `window.showPACelebration({ name: "Test", message: "Works!" })`
3. Clear cache test: `localStorage.removeItem('faithh_seen_pas_v1'); location.reload()`
4. Chat test: Send "Why did we choose this and where do we stand?"

## Acceptance Criteria

- [ ] Original tabs still work
- [ ] Images still load
- [ ] PA celebration shows on page load (Project Historian)
- [ ] Dismiss works (button, click outside, Escape)
- [ ] De-dupe works (no repeat celebrations)
- [ ] Chat responses with pa_unlocked trigger celebration
