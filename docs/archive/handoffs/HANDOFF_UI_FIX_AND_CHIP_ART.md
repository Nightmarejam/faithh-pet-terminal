# Handoff: Fix UI Issues + Add MMBN Chip Artwork

**Priority**: P1
**Date**: 2026-01-04
**Time Budget**: ~10% session remaining

---

## Context

PA celebration IS WORKING in current UI - don't break it!
But: tabs broken, images missing, needs chip artwork styling.

## Objectives (in priority order)

### 1. FIX: Restore tabs and images (CRITICAL)
- Tabs (chat/stats/pulse/settings) should switch content properly
- Images (faithh.png, pulse.png) should load from /images/

### 2. ADD: MMBN-style chip card styling
Style chips to look like MegaMan Battle Network battle chips:
- Rectangular card shape with rounded corners
- Dark blue/navy background (#000080)
- Chip name at top in bold
- Chip "code" letter (A, B, C, etc.) in corner
- Element/type indicator (colored bar or icon)
- MB (memory) cost display
- Hover glow effect (cyan)

Reference: MMBN chips have:
- 58x50 pixel art icon area
- Name bar at bottom
- Letter code in corner
- Color-coded by element (red=fire, blue=aqua, green=wood, yellow=elec)

### 3. ADD: Program Advance chip display
When PA is unlocked, show combined chip visualization:
- 3 chips merging animation
- PA chip is larger/golden
- Special border effect

---

## Files

- **Main UI**: `~/ai-stack/faithh_pet_v4.html` (the one backend serves)
- **Reference**: `~/ai-stack/frontend/html/faithh_pet_v4_enhanced.html` (has PA code but broken tabs)
- **Backend**: Already serves from BASE_DIR

## Current Chip Types

From PULSE/backend:
- rag_search (RAG Search)
- decisions (Decisions)
- scaffolding (Scaffolding)
- constella (Constella)
- self_awareness (Self Awareness)
- project_state (Project State)

Assign each a:
- Letter code (A-Z)
- Element color
- MB cost (for display)

Example mapping:
```javascript
const CHIP_STYLES = {
    'rag_search': { code: 'R', element: 'aqua', color: '#00CED1', mb: 20 },
    'decisions': { code: 'D', element: 'elec', color: '#FFD700', mb: 30 },
    'scaffolding': { code: 'S', element: 'wood', color: '#32CD32', mb: 25 },
    'constella': { code: 'C', element: 'fire', color: '#FF4500', mb: 40 },
    'self_awareness': { code: 'A', element: 'null', color: '#9370DB', mb: 15 },
    'project_state': { code: 'P', element: 'break', color: '#FF69B4', mb: 35 }
};
```

---

## CSS for MMBN Chip Cards
```css
.chip-card {
    width: 80px;
    height: 100px;
    background: linear-gradient(180deg, #000080 0%, #000040 100%);
    border: 2px solid #4169E1;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 4px;
    position: relative;
    cursor: pointer;
    transition: all 0.2s ease;
}

.chip-card:hover {
    box-shadow: 0 0 15px rgba(0, 206, 209, 0.7);
    transform: translateY(-2px);
}

.chip-card .chip-icon {
    width: 50px;
    height: 50px;
    background: #001040;
    border: 1px solid #60A0FF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.chip-card .chip-name {
    font-size: 10px;
    color: #fff;
    text-align: center;
    margin-top: 4px;
    text-transform: uppercase;
}

.chip-card .chip-code {
    position: absolute;
    top: 2px;
    right: 4px;
    font-size: 12px;
    font-weight: bold;
    color: #FFD700;
}

.chip-card .chip-mb {
    position: absolute;
    bottom: 2px;
    right: 4px;
    font-size: 8px;
    color: #aaa;
}

.chip-card .element-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: 0 0 6px 6px;
}

/* Element colors */
.chip-card.aqua .element-bar { background: #00CED1; }
.chip-card.fire .element-bar { background: #FF4500; }
.chip-card.elec .element-bar { background: #FFD700; }
.chip-card.wood .element-bar { background: #32CD32; }
.chip-card.null .element-bar { background: #9370DB; }
.chip-card.break .element-bar { background: #FF69B4; }

/* PA Chip (larger, golden) */
.chip-card.program-advance {
    width: 100px;
    height: 120px;
    border-color: #FFD700;
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}
```

---

## Testing

1. Verify tabs work (click each, content switches)
2. Verify images load (FAITHH avatar, PULSE wolf)
3. Test chip card rendering in CHIPS tab
4. Test PA celebration still works
5. Console: `window.showPACelebration({ name: "Test", message: "Works!" })`

## Do NOT Break

- PA celebration animation
- /api/chat functionality
- /api/pulse/* endpoints
- Status polling

---

## Quick Win Approach

1. First: Fix tabs by checking event listeners
2. Second: Fix image paths
3. Third: Add chip card CSS
4. Fourth: Update chip display HTML to use new card style
