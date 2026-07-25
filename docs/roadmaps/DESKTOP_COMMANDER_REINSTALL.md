# Desktop Commander Reinstall Handoff
**Date:** 2026-02-19
**For:** Windsurf
**Priority:** Low — Desktop Commander is functional but logging ENOENT errors on every startup

---

## What Happened

During the Windows dependencies cleanup, the corrupted Desktop Commander extension
folder was correctly deleted:

  C:\Users\jonat\AppData\Roaming\Claude\Claude Extensions\ant.dir.gh.wonderwhy-er.desktopcommandermcp

That folder is now completely gone (confirmed). However, the reinstall from the
Claude extensions panel has not been done yet. Claude is running Desktop Commander
from an internal cache, which is why tools still work, but the UI assets are missing:

  MCP error -32603: ENOENT: no such file or directory
  open '...desktopcommandermcp\dist\ui\file-preview\index.html'

This error fires on every startup and any time Claude tries to render the
file-preview UI widget. It does not break functionality but it is noisy and
will eventually cause issues when Claude is updated and drops the cache.

---

## The Fix — One Step, Manual UI Action Required

Windsurf cannot do this step programmatically. It requires clicking in the
Claude desktop app.

**Steps:**
1. Make sure Claude desktop is running (do not quit it)
2. Click the extensions/integrations icon in the Claude sidebar
   (looks like a puzzle piece or grid icon depending on app version)
3. Search for "Desktop Commander"
4. Find the one by **wonderwhy-er** (not any other publisher)
5. Click Install (or Reinstall if that option appears)
6. Wait for the download to complete — it will repopulate the folder at:
   C:\Users\jonat\AppData\Roaming\Claude\Claude Extensions\ant.dir.gh.wonderwhy-er.desktopcommandermcp
7. Restart Claude from the system tray (right-click tray icon → Quit, then reopen)

---

## Verification

After reinstall and restart, check the log:

```powershell
Get-Content "C:\Users\jonat\AppData\Roaming\Claude\logs\mcp-server-Desktop Commander.log" -Tail 20
```

You should see a clean startup with NO mention of:
- "Manifest file not found"
- "ENOENT: no such file or directory"
- Any error at all in the last 10 lines

Also verify the folder is repopulated:

```powershell
Get-ChildItem "C:\Users\jonat\AppData\Roaming\Claude\Claude Extensions\ant.dir.gh.wonderwhy-er.desktopcommandermcp"
```

Expected output should include: dist, node_modules, manifest.json, package.json, icon.png, LICENSE, README.md

---

## While You Are In the Extensions Panel

Also check that Windows-MCP is still installed and enabled. After the full
Claude restart, check its log too:

```powershell
Get-Content "C:\Users\jonat\AppData\Roaming\Claude\logs\mcp-server-Windows-MCP.log" -Tail 15
```

If it shows "Server started and connected successfully" — Windows-MCP is alive.
If it still shows "spawn uv ENOENT" — Claude has not fully restarted yet and
picked up the new PATH. Quit and reopen Claude again.

---

## Context: Why This Is Safe to Do

- Desktop Commander tools are working right now from Claude's internal cache
- The reinstall only affects the local extension folder, not any configuration
- No FAITHH project files, WSL, or backend are touched by this operation
- After reinstall, behavior will be identical but errors will stop
