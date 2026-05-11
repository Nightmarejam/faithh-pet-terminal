# Windsurf Handoff: Director UI Integration
**Date:** 2026-01-18
**Model:** GPT 5.1 Codex Max Low (free tier)
**Task:** Surface Director output in the PET Terminal UI

---

## TL;DR

Add a "System Status" card to the Pulse tab that shows the Director's analysis - attention items, suggested actions, and the AI context summary. This gives Jonathan at-a-glance awareness of what needs attention.

**This is ~100 lines of HTML/CSS/JS changes to `faithh_pet_v4.html`.**

---

## Current State

### Working ✅
- **Director endpoint**: `/api/compass/director` returns actionable intelligence
- **Collectors**: All 4 running OK (health, git, file_changes, terminal)
- **Pulse tab**: Already has collector status badges

### Director Response Structure
```json
{
  "success": true,
  "generated_at": "2026-01-18T16:28:54.716413Z",
  "context_for_ai": "System health: healthy. Git: 5 modified files. No urgent issues.",
  "attention_items": [
    {"priority": "high", "type": "health", "message": "ChromaDB degraded"}
  ],
  "suggested_actions": [
    "Run git push to sync commits"
  ],
  "raw_summary": {
    "total_issues": 0,
    "critical": 0,
    "high": 0,
    "services_healthy": "3/3"
  }
}
```

---

## What to Build

### 1. Add Director Status Card to Pulse Tab

Find the Pulse tab content section in `faithh_pet_v4.html` (around line ~1050-1150) and add this card:

```html
<!-- Director Status Card -->
<div class="pulse-card director-card">
    <div class="card-header">
        <span class="card-icon">🧭</span>
        <span class="card-title">SYSTEM DIRECTOR</span>
        <button class="refresh-btn" onclick="refreshDirectorStatus()">↻</button>
    </div>
    <div class="director-content">
        <div class="context-summary" id="directorContext">
            Loading...
        </div>
        <div class="status-badges">
            <div class="status-badge healthy" id="directorHealthy">
                <span class="badge-label">Healthy</span>
                <span class="badge-value" id="directorServicesOk">-</span>
            </div>
            <div class="status-badge warning" id="directorWarning" style="display:none;">
                <span class="badge-label">Attention</span>
                <span class="badge-value" id="directorAttentionCount">0</span>
            </div>
            <div class="status-badge critical" id="directorCritical" style="display:none;">
                <span class="badge-label">Critical</span>
                <span class="badge-value" id="directorCriticalCount">0</span>
            </div>
        </div>
        <div class="attention-items" id="attentionItems" style="display:none;">
            <!-- Populated by JS -->
        </div>
        <div class="suggested-actions" id="suggestedActions" style="display:none;">
            <!-- Populated by JS -->
        </div>
        <div class="director-meta">
            <span id="directorTimestamp">--</span>
        </div>
    </div>
</div>
```

### 2. Add CSS Styles

Add these styles to the `<style>` section (around line ~200-900):

```css
/* Director Card Styles */
.director-card {
    background: linear-gradient(135deg, rgba(0, 40, 60, 0.9), rgba(0, 20, 40, 0.95));
    border: 1px solid #00d4aa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
}

.director-card .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0, 212, 170, 0.3);
}

.director-card .card-icon {
    font-size: 20px;
}

.director-card .card-title {
    color: #00d4aa;
    font-weight: bold;
    font-size: 14px;
    letter-spacing: 1px;
    flex-grow: 1;
}

.director-card .refresh-btn {
    background: transparent;
    border: 1px solid #00d4aa;
    color: #00d4aa;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.director-card .refresh-btn:hover {
    background: rgba(0, 212, 170, 0.2);
}

.context-summary {
    background: rgba(0, 0, 0, 0.3);
    padding: 12px;
    border-radius: 6px;
    color: #e0e0e0;
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 12px;
    border-left: 3px solid #00d4aa;
}

.status-badges {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
}

.status-badge {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 16px;
    border-radius: 6px;
    min-width: 80px;
}

.status-badge.healthy {
    background: rgba(0, 200, 100, 0.2);
    border: 1px solid #00c864;
}

.status-badge.warning {
    background: rgba(255, 180, 0, 0.2);
    border: 1px solid #ffb400;
}

.status-badge.critical {
    background: rgba(255, 60, 60, 0.2);
    border: 1px solid #ff3c3c;
}

.status-badge .badge-label {
    font-size: 10px;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 4px;
}

.status-badge .badge-value {
    font-size: 18px;
    font-weight: bold;
}

.status-badge.healthy .badge-value { color: #00c864; }
.status-badge.warning .badge-value { color: #ffb400; }
.status-badge.critical .badge-value { color: #ff3c3c; }

.attention-items {
    margin-top: 12px;
    padding: 12px;
    background: rgba(255, 180, 0, 0.1);
    border-radius: 6px;
    border: 1px solid rgba(255, 180, 0, 0.3);
}

.attention-items h4 {
    color: #ffb400;
    font-size: 12px;
    margin: 0 0 8px 0;
    text-transform: uppercase;
}

.attention-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 12px;
    color: #e0e0e0;
}

.attention-item:last-child {
    border-bottom: none;
}

.attention-item .priority-badge {
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: bold;
    text-transform: uppercase;
}

.priority-badge.critical { background: #ff3c3c; color: white; }
.priority-badge.high { background: #ff6b35; color: white; }
.priority-badge.medium { background: #ffb400; color: black; }
.priority-badge.low { background: #6b7280; color: white; }

.suggested-actions {
    margin-top: 12px;
    padding: 12px;
    background: rgba(0, 150, 255, 0.1);
    border-radius: 6px;
    border: 1px solid rgba(0, 150, 255, 0.3);
}

.suggested-actions h4 {
    color: #0096ff;
    font-size: 12px;
    margin: 0 0 8px 0;
    text-transform: uppercase;
}

.suggested-action {
    padding: 4px 0;
    font-size: 12px;
    color: #e0e0e0;
}

.suggested-action::before {
    content: "→ ";
    color: #0096ff;
}

.director-meta {
    margin-top: 8px;
    font-size: 11px;
    color: #6b7280;
    text-align: right;
}
```

### 3. Add JavaScript Function

Add this function to the `<script>` section (around line ~1800-2100):

```javascript
// ===================================
// DIRECTOR STATUS
// ===================================

async function refreshDirectorStatus() {
    try {
        const response = await fetch('/api/compass/director');
        const data = await response.json();
        
        if (!data.success) {
            document.getElementById('directorContext').textContent = 
                'Director unavailable: ' + (data.error || 'Unknown error');
            return;
        }
        
        // Update context summary
        document.getElementById('directorContext').textContent = 
            data.context_for_ai || 'No context available';
        
        // Update service health badge
        const healthyBadge = document.getElementById('directorServicesOk');
        healthyBadge.textContent = data.raw_summary?.services_healthy || '-';
        
        // Handle attention items
        const attentionCount = data.attention_items?.length || 0;
        const criticalCount = data.raw_summary?.critical || 0;
        const highCount = data.raw_summary?.high || 0;
        
        // Show/hide warning badge
        const warningBadge = document.getElementById('directorWarning');
        const warningCount = document.getElementById('directorAttentionCount');
        if (attentionCount > 0 && criticalCount === 0) {
            warningBadge.style.display = 'flex';
            warningCount.textContent = attentionCount;
        } else {
            warningBadge.style.display = 'none';
        }
        
        // Show/hide critical badge
        const criticalBadge = document.getElementById('directorCritical');
        const criticalCountEl = document.getElementById('directorCriticalCount');
        if (criticalCount > 0) {
            criticalBadge.style.display = 'flex';
            criticalCountEl.textContent = criticalCount;
        } else {
            criticalBadge.style.display = 'none';
        }
        
        // Render attention items
        const attentionContainer = document.getElementById('attentionItems');
        if (attentionCount > 0) {
            attentionContainer.style.display = 'block';
            attentionContainer.innerHTML = '<h4>⚠️ Attention Required</h4>' +
                data.attention_items.map(item => `
                    <div class="attention-item">
                        <span class="priority-badge ${item.priority}">${item.priority}</span>
                        <span>${item.message}</span>
                    </div>
                `).join('');
        } else {
            attentionContainer.style.display = 'none';
        }
        
        // Render suggested actions
        const actionsContainer = document.getElementById('suggestedActions');
        if (data.suggested_actions?.length > 0) {
            actionsContainer.style.display = 'block';
            actionsContainer.innerHTML = '<h4>💡 Suggested Actions</h4>' +
                data.suggested_actions.map(action => `
                    <div class="suggested-action">${action}</div>
                `).join('');
        } else {
            actionsContainer.style.display = 'none';
        }
        
        // Update timestamp
        const timestamp = data.generated_at ? 
            new Date(data.generated_at).toLocaleTimeString() : '--';
        document.getElementById('directorTimestamp').textContent = 
            'Updated: ' + timestamp;
            
    } catch (error) {
        console.error('Director fetch error:', error);
        document.getElementById('directorContext').textContent = 
            'Error fetching director status';
    }
}

// Call on Pulse tab open
function onPulseTabOpen() {
    refreshDirectorStatus();
    refreshCollectorsStatus(); // existing function
}
```

### 4. Wire Up Tab Switching

Find the tab switching code and ensure `onPulseTabOpen()` is called when the Pulse tab is selected. Look for something like:

```javascript
// In the tab click handler, add:
if (tabName === 'pulse') {
    onPulseTabOpen();
}
```

### 5. Initial Load

Add to the document ready / initial load section:

```javascript
// Load director status on page load if Pulse is visible
if (document.getElementById('pulse-tab')?.classList.contains('active')) {
    onPulseTabOpen();
}
```

---

## Testing

After implementation:

1. Open http://localhost:5557
2. Click the **PULSE** tab
3. You should see:
   - System Director card with context summary
   - "Healthy 3/3" badge (when all services OK)
   - No attention items (when system is healthy)
4. To test with issues, temporarily break a service and refresh

---

## Success Criteria

✅ Implementation complete when:

1. Director card appears in Pulse tab
2. `context_for_ai` displays in the summary box
3. Service health badge shows "3/3"
4. Attention items appear when Director reports issues
5. Suggested actions appear when Director has recommendations
6. Refresh button updates the data
7. Timestamp shows when data was fetched

---

## File to Edit

| File | Changes |
|------|---------|
| `faithh_pet_v4.html` | Add HTML card (~30 lines), CSS (~120 lines), JS function (~80 lines) |

---

## Notes for AI Assistant

- **Working Directory:** `/home/jonat/ai-stack`
- **UI File:** `faithh_pet_v4.html` is the canonical UI
- **Endpoint:** `/api/compass/director` is already working
- **Style:** Match existing PET Terminal v4.0 aesthetic (cyan/teal accents, dark background)
- **Keep it simple:** This is display-only, no editing functionality needed

---

## Visual Reference

The card should fit with the existing Pulse tab design:
- Dark background with cyan/teal accents
- Consistent with the "Collectors Status" card styling
- Compact but informative

---

**Endpoint to use:** `GET /api/compass/director`


---

## Additional Issue: Missing Console Feature

### Background
Previously, the backend was also accessible at `http://127.0.0.1:43772/` which had a **console send/return feature** in the bottom right corner. This appears to have been either:
- A VS Code port forwarding with additional debug features
- A separate Flask instance running in debug mode with an interactive console

The current `localhost:5557` instance does NOT have this console feature.

### Investigation Needed
1. Check if there's a debug mode flag in the backend that enables the console
2. Look for any Flask-SocketIO or similar real-time console implementation
3. Check if VS Code's port forwarding was adding this feature

### Possible Solutions
1. **Find existing console code**: Search the backend for console/terminal/repl related endpoints
2. **Add a simple console**: Implement a basic send/receive console using Flask + JavaScript
3. **Use VS Code forwarding**: Document how to enable the VS Code port forward that had this feature

### Search Commands (for investigation)
```bash
# Look for console-related code in the backend
grep -n -i "console\|terminal\|repl\|socket" faithh_professional_backend_fixed.py

# Check if there's a debug config
grep -n "debug\|DEBUG" faithh_professional_backend_fixed.py

# Look for any separate backend files
ls -la *backend*.py
```

### If Adding Console Feature
If you want to add a console to the main UI, it would need:
1. A backend endpoint like `/api/console/execute` that runs commands
2. A WebSocket or polling-based UI component
3. Security considerations (what commands are allowed?)

**Priority:** Low - this is a nice-to-have feature, not blocking the Director UI work.

---
