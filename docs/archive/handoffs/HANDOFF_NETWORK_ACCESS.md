# Handoff: Enable Network Access for FAITHH Backend

**Priority**: P0
**Owner**: FAITHH
**Agents**: [claude_code]

—

## Snapshot
- Date: 2026-01-01
- Backend runs on Mac localhost:5557
- Not accessible from other Tailscale devices
- Phone can reach Tailscale network but not FAITHH

## Objective
Make FAITHH backend accessible from any Tailscale device (phone, other computers).

## Files to Touch
- `faithh_professional_backend_fixed.py` (~line 1500, app.run)

## Implementation

### Step 1: Find current app.run
```bash
grep -n “app.run” ~/ai-stack/faithh_professional_backend_fixed.py
