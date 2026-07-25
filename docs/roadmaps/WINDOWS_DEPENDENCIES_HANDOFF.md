# Windows Host Dependencies Handoff
**Date:** 2026-02-19  
**For:** Windsurf  
**Purpose:** Audit, clean up, and document all Windows-side dependencies. Establish a lean, intentional system where everything installed has a documented reason for existing.

---

## Philosophy: Documented or Removed

Going forward, every tool/runtime on the Windows host must have a documented purpose. If it belongs, it's in this file. If it's not here, it gets reviewed for removal.

---

## Current State: What's Installed and Working

### Confirmed Working (verified 2026-02-19)

| Tool | Version | Location | Purpose |
|------|---------|----------|---------|
| Python | 3.10.11 | `C:\Users\jonat\AppData\Local\Programs\Python\Python310\` | Windows-side scripts, legacy tooling |
| Node.js | 24.13.1 | `C:\Program Files\nodejs\` | MCP servers (Filesystem, Desktop Commander), JS tooling |
| npm | 11.8.0 | via Node.js | Package management for Node tools |
| uv | 0.10.4 | `C:\Users\jonat\.local\bin\` | Python package manager, required for Windows-MCP |
| Git | 2.51.0 | system | Version control |
| Winget | 1.12.460 | system | Windows package manager |
| Chocolatey | 2.5.0 | system | Windows package manager (legacy, prefer winget going forward) |
| WSL2 | 2.5.10.0 | system | Linux environment (Ubuntu), runs FAITHH backend |
| Ollama (Windows) | 0.12.3 | `C:\Users\jonat\AppData\Local\Programs\Ollama` | Windows-side model access (NOTE: primary Ollama is WSL-side) |
| CUDA | 12.2 | `C:\Program Files\NVIDIA GPU Computing Toolkit\` | GPU compute for RTX 3090 |
| Windsurf | latest | `C:\Users\jonat\AppData\Local\Programs\Windsurf\` | Primary IDE / AI coding agent |
| VS Code | latest | `C:\Users\jonat\AppData\Local\Programs\Microsoft VS Code\` | Secondary editor |
| Google Cloud SDK | latest | `C:\Users\jonat\AppData\Local\Google\Cloud SDK\` | Cloud access |
| dotnet | latest | `C:\Program Files\dotnet\` | .NET runtime, required by some tools |

### Installed But Needs Review

| Tool | Issue | Decision Needed |
|------|-------|----------------|
| Cursor | In PATH at `C:\Users\jonat\AppData\Local\Programs\cursor\` | Still using? Or fully migrated to Windsurf? |
| Chocolatey | Redundant with winget | Keep only for choco-specific packages, otherwise phase out |
| Langflow uv path | Dead PATH entry: `C:\Users\jonat\AppData\Local\com.Langflow\uv` | Is Langflow still in use? If not, remove PATH entry |
| Ollama (Windows) | Version mismatch: client 0.11.10 vs server 0.12.3 | Primary Ollama is WSL-side. Determine if Windows Ollama is needed |

---

## Remaining Issues to Fix

### 1. Python 3.13 — Required for Windows-MCP (ACTION NEEDED)

Windows-MCP (CursorTouch extension) requires Python 3.13 minimum. Python 3.10 will not run it.

**Decision: Install Python 3.13 alongside 3.10. Do NOT remove 3.10.**

Why keep both:
- Python 3.10 is on the PATH and used by existing Windows scripts
- Python 3.13 is only needed for Windows-MCP's uv-managed environment
- uv creates isolated virtual environments per tool so they will not conflict
- uv will automatically find and use 3.13 when running Windows-MCP

**Install command (run as Administrator):**
```powershell
winget install Python.Python.3.13
```

After install, verify:
```powershell
py -3.13 --version
```
Expected: `Python 3.13.x`

Do NOT change the default `python` command — leave it pointing to 3.10.

---

### 2. python3 alias — Microsoft Store stub still active

`python3` command still hits the Microsoft Store stub instead of Python 3.10.

**Fix:**
- Settings → Apps → Advanced app settings → App execution aliases
- Disable the entries labeled **"App Installer"** for `python.exe` and `python3.exe`
- These are distinct from other Store aliases — look specifically for the ones pointing to `WindowsApps\python`

After fix, verify:
```powershell
python3 --version
```
Expected: `Python 3.10.11`

---

### 3. Desktop Commander — Broken manifest, needs reinstall

Extension folder at:
`C:\Users\jonat\AppData\Roaming\Claude\Claude Extensions\ant.dir.gh.wonderwhy-er.desktopcommandermcp`

...exists but is corrupted. The `dist\` folder is empty, manifest.json and package.json are missing. Claude logs `Manifest file not found` on every startup.

**Fix:**
1. Quit Claude completely from system tray
2. Run in PowerShell:
```powershell
Remove-Item "C:\Users\jonat\AppData\Roaming\Claude\Claude Extensions\ant.dir.gh.wonderwhy-er.desktopcommandermcp" -Recurse -Force
```
3. Reopen Claude
4. Reinstall Desktop Commander from the Claude extensions panel (by wonderwhy-er)

---

### 4. PATH cleanup — Dead entries

The user PATH contains this dead entry from a Langflow install:
```
C:\Users\jonat\AppData\Local\com.Langflow\uv
```

Only remove if Langflow is confirmed no longer in use. Do not remove blindly — check first.

---

## MCP Servers Status

| Server | Status | Notes |
|--------|--------|-------|
| Filesystem | Working | Access to `C:\Users\jonat` and WSL Ubuntu home |
| Desktop Commander | Manifest error on startup | Working via cache but needs clean reinstall |
| Windows-MCP | Broken | Needs Python 3.13, then should work |

---

## Python Version Strategy

```
Python 3.10  →  Windows scripts, PATH default ("python" and "python3" commands)
Python 3.13  →  Windows-MCP only (managed by uv in isolated environment)
WSL Python   →  FAITHH backend and all WSL workloads (do not touch from Windows side)
```

uv handles isolation so both versions coexist without conflict. This is the intended pattern.

---

## What Lives in WSL, Not Windows

These do NOT need to be installed on the Windows host. They run in WSL Ubuntu:

- ChromaDB
- FAITHH backend (Flask/Python)
- Ollama (primary instance with all models)
- All pip packages for ai-stack
- All AI model files

---

## Verification Checklist (Run After All Fixes)

```powershell
uv --version          # uv 0.10.4 or higher
node --version        # v24.x.x
python --version      # Python 3.10.11
python3 --version     # Python 3.10.11 (not Store stub)
py -3.13 --version    # Python 3.13.x (after install)
git --version         # git 2.x.x

# Check Windows-MCP came up clean after Claude restart
Get-Content "C:\Users\jonat\AppData\Roaming\Claude\logs\mcp-server-Windows-MCP.log" -Tail 10
# Should show: "Server started and connected successfully"
```

---

## Future: Dependencies Journal

This document is the seed of a permanent Windows Dependencies Journal. The rule going forward:

- Every installed tool has a documented purpose in this file
- Before installing anything new, add it here first with the reason
- Quarterly review: anything with no active use case gets scheduled for removal
- WSL dependencies tracked separately at `/home/jonat/ai-stack/docs/WSL_DEPENDENCIES.md`

**If it belongs, it is documented. If it is not documented, it gets reviewed.**
