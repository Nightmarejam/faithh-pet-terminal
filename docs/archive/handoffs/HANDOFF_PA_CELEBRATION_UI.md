# Handoff: Program Advance Celebration UI

**Priority**: P1
**Owner**: FAITHH
**Agents**: [claude_code]
**Date**: 2026-01-03

---

## Objective

Add MMBN-style "PROGRAM ADVANCE!" celebration animation to FAITHH UI when a PA unlocks.

## Context

- Backend now returns `pa_unlocked` object when a PA is unlocked
- PULSE tracks chip combinations and unlocks PAs at 3+ occurrences
- First PA "Project Historian" already unlocked
- UI needs to display celebration when `pa_unlocked` is present in response

## Files to Modify

- `faithh_pet_v4.html` - Add celebration CSS and JS

---

## Implementation

### Step 1: Add Celebration CSS

Add to the `<style>` section:
```css
/* Program Advance Celebration Overlay */
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
    0% { 
        transform: scale(8) rotate(-5deg); 
        opacity: 0; 
    }
    50% { 
        opacity: 0.5; 
    }
    80% { 
        transform: scale(1.1) rotate(2deg); 
    }
    100% { 
        transform: scale(1) rotate(0deg); 
        opacity: 1; 
    }
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
    0% { 
        opacity: 0; 
        transform: translateY(20px); 
    }
    100% { 
        opacity: 1; 
        transform: translateY(0); 
    }
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
    background: linear-gradient(180deg, #5179F1 0%, #3050B0 100%);
    box-shadow: 0 0 10px rgba(96, 160, 255, 0.5);
}

/* Screen shake on PA */
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

### Step 2: Add Celebration HTML

Add before closing `</body>` tag:
```html
<!-- Program Advance Celebration Overlay -->
<div class="pa-celebration-overlay" id="paCelebration">
    <div class="pa-title">PROGRAM ADVANCE!</div>
    <div class="pa-name" id="paName"></div>
    <div class="pa-message" id="paMessage"></div>
    <button class="pa-dismiss" onclick="dismissPACelebration()">AWESOME!</button>
</div>
```

### Step 3: Add Celebration JavaScript

Add to the `<script>` section:
```javascript
// Program Advance Celebration
function showPACelebration(paData) {
    const overlay = document.getElementById('paCelebration');
    const nameEl = document.getElementById('paName');
    const messageEl = document.getElementById('paMessage');
    
    nameEl.textContent = paData.name;
    messageEl.textContent = paData.message;
    
    // Add screen shake to main container
    document.querySelector('.pet-container').classList.add('screen-shake');
    
    // Show overlay
    overlay.classList.add('active');
    
    // Remove shake after animation
    setTimeout(() => {
        document.querySelector('.pet-container').classList.remove('screen-shake');
    }, 300);
    
    // Store that we've seen this PA (for progressive reduction)
    const seenPAs = JSON.parse(localStorage.getItem('faithh_seen_pas') || '{}');
    seenPAs[paData.name] = (seenPAs[paData.name] || 0) + 1;
    localStorage.setItem('faithh_seen_pas', JSON.stringify(seenPAs));
}

function dismissPACelebration() {
    const overlay = document.getElementById('paCelebration');
    overlay.classList.remove('active');
}

// Check if we should show full celebration (progressive reduction)
function shouldShowFullCelebration(paName) {
    const seenPAs = JSON.parse(localStorage.getItem('faithh_seen_pas') || '{}');
    const timessSeen = seenPAs[paName] || 0;
    return timessSeen < 3; // Show full celebration first 3 times
}
```

### Step 4: Integrate with sendMessage Function

Find the `sendMessage` function and modify the response handling to check for `pa_unlocked`:
```javascript
// After receiving response from /api/chat
// Find where response is processed and add:

if (data.pa_unlocked && shouldShowFullCelebration(data.pa_unlocked.name)) {
    showPACelebration(data.pa_unlocked);
}
```

Look for code like:
```javascript
fetch('/api/chat', { ... })
    .then(response => response.json())
    .then(data => {
        // ADD PA CHECK HERE
        if (data.pa_unlocked && shouldShowFullCelebration(data.pa_unlocked.name)) {
            showPACelebration(data.pa_unlocked);
        }
        // ... rest of response handling
    });
```

---

## Testing

1. Clear localStorage to reset PA celebration tracking:
```javascript
localStorage.removeItem('faithh_seen_pas');
```

2. Trigger a PA by sending queries that fire decisions + scaffolding:
```
"Why did we choose this approach and where do we stand?"
```

3. Verify celebration appears with:
   - White flash on appearance
   - "PROGRAM ADVANCE!" text slams in
   - PA name fades up
   - Screen shakes briefly
   - Dismiss button works

4. Test progressive reduction - after 3 views, celebration should skip

---

## Acceptance Criteria

- [ ] PA celebration overlay appears when `pa_unlocked` is in response
- [ ] Animation includes flash, slam, shake effects
- [ ] PA name and message displayed correctly
- [ ] Dismiss button closes overlay
- [ ] Progressive reduction after 3 views
- [ ] No errors in console
- [ ] Celebration feels satisfying, not annoying

---

## Visual Reference

Based on MMBN research:
- Flash: 100ms white overlay fade
- Slam: 500ms scale from 8x to 1x with bounce
- Colors: Gold (#FFD700) title, Cyan (#00CED1) name
- Shake: 300ms horizontal displacement

## Rollback

Remove the CSS, HTML, and JS additions from faithh_pet_v4.html
