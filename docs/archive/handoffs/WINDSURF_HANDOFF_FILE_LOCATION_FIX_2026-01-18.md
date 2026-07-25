# Windsurf Handoff: File Location Correction Required

**Date:** 2026-01-18
**Priority:** High
**Issue Type:** File location mismatch - changes applied to wrong file

---

## Summary

The Pulse Security UI changes from the previous session were applied to the **wrong file**. The backend serves a different HTML file than the one that was edited.

---

## The Problem

### What Was Edited (WRONG FILE)
```
~/ai-stack/active/frontend/faithh_pet_v4.html
- Size: 26KB (796 lines)
- Modified: 2026-01-16
- Status: NOT served by backend
```

### What Should Have Been Edited (CORRECT FILE)
```
~/ai-stack/faithh_pet_v4.html  (ROOT LEVEL)
- Size: 117KB (3,291 lines)
- Modified: 2026-01-18
- Status: SERVED by backend at localhost:5557
```

### Backend Route (from faithh_professional_backend_fixed.py, line ~1230)
```python
@app.route('/')
def index():
    """Serve the HTML UI"""
    return send_from_directory(BASE_DIR, 'faithh_pet_v4.html')
```

`BASE_DIR` = `~/ai-stack/` (root), NOT `~/ai-stack/active/frontend/`

---

## Required Actions

### 1. Merge Pulse Security UI Changes
The following features need to be ported from `active/frontend/faithh_pet_v4.html` to the root-level `faithh_pet_v4.html`:

- **Pulse Security card** with:
  - Scan Input/Output buttons
  - Health Check button
  - Heal (dry-run) button
  - Audit Summary button
  - Audit Events table
  - Environment-aware health hints (dev vs prod thresholds)

- **JavaScript functions:**
  - `scanSecurity(type)` - calls `/api/pulse/security/scan`
  - `refreshHealthStatus()` - calls `/api/pulse/health/check`
  - `runHealCycle()` - calls `/api/pulse/health/heal`
  - `fetchAuditSummary()` - calls `/api/pulse/audit/summary`
  - `fetchRecentAuditEvents()` - calls `/api/pulse/audit/recent`

### 2. Verify Backend Endpoints Exist
These endpoints should already be in `faithh_professional_backend_fixed.py`:
- `POST /api/pulse/security/scan`
- `GET /api/pulse/health/check`
- `POST /api/pulse/health/heal`
- `GET /api/pulse/audit/summary`
- `GET /api/pulse/audit/recent`

### 3. Clean Up Redundant Files
After merging, consider consolidating or removing redundant locations:

| Location | Purpose | Action |
|----------|---------|--------|
| `~/ai-stack/faithh_pet_v4.html` | **CANONICAL** - served by backend | KEEP & UPDATE |
| `~/ai-stack/faithh_pet.html` | Legacy/alias? | Investigate |
| `~/ai-stack/active/frontend/faithh_pet_v4.html` | Outdated copy | DELETE or sync |
| `~/ai-stack/frontend/` | Another frontend dir? | Investigate |

---

## Guidance for Future Sessions

### ALWAYS Verify File Locations Before Editing

1. **Check what the backend serves:**
   ```bash
   grep -n "send_from_directory\|send_file" faithh_professional_backend_fixed.py | head -20
   ```

2. **Find the actual route:**
   ```bash
   grep -A2 "@app.route('/')" faithh_professional_backend_fixed.py
   ```

3. **Compare file sizes to identify canonical version:**
   ```bash
   find ~/ai-stack -name "faithh_pet*.html" -exec ls -lh {} \;
   ```

4. **Test changes by accessing the backend URL:**
   ```
   http://localhost:5557/
   ```
   NOT by opening the file directly in browser.

### File Location Patterns in This Project

| Type | Canonical Location | Notes |
|------|-------------------|-------|
| Backend | `~/ai-stack/faithh_professional_backend_fixed.py` | Root level |
| Frontend UI | `~/ai-stack/faithh_pet_v4.html` | Root level, served by backend |
| Security modules | `~/ai-stack/scripts/security/` | Correctly placed |
| Docs | `~/ai-stack/docs/` | Handoffs, context, guides |
| Active code | `~/ai-stack/active/` | May be outdated - verify before using |
| Archives | `~/ai-stack/archive/`, `~/ai-stack/ARCHIVE/` | Legacy code |

---

## Verification Steps After Fix

1. Restart backend:
   ```bash
   ./restart_backend.sh
   ```

2. Open UI in browser:
   ```
   http://localhost:5557/
   ```

3. Navigate to **Pulse** tab

4. Verify Pulse Security card appears with all buttons

5. Test each button:
   - Scan Input → should show scan results
   - Health Check → should show service status
   - Audit Summary → should show event counts

---

## Reference: Working Endpoint Tests (from previous session)

```bash
# These all work - backend endpoints are correct
curl -s -X POST http://localhost:5557/api/pulse/security/scan \
  -H "Content-Type: application/json" \
  -d '{"text":"test","type":"input"}'

curl -s http://localhost:5557/api/pulse/health/check | jq '.'

curl -s -X POST http://localhost:5557/api/pulse/health/heal \
  -H "Content-Type: application/json" \
  -d '{"dry_run":true}' | jq '.'

curl -s http://localhost:5557/api/pulse/audit/summary | jq '.'
```

---

## Context Files to Review

- `MASTER_CONTEXT.md` - System overview
- `project_states.json` - Current project state
- `docs/WINDSURF_HANDOFF_PULSE_SECURITY_2026-01-18.md` - Previous session details

---

**End of Handoff**
