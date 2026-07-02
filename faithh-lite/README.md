# FAITHH Lite - MacBook Companion

Lightweight FAITHH for quick queries during audio work sessions.

## Quick Start

```bash
cd ~/faithh
./start.sh
```

Then open: http://localhost:5557

## What This Is

- **Local LLM**: Ollama + llama3.1:8b (runs entirely on your MacBook)
- **No internet required**: Works offline
- **Fast responses**: ~2 seconds on M1
- **Context-aware**: Loads key docs from `context/` folder

## What This Is NOT

- Not the full FAITHH (that's on Windows with 93K+ indexed docs)
- No ChromaDB vector search
- No complex integrations
- No auto-indexing

## Files

```
~/faithh/
├── faithh_lite.py      # Backend
├── faithh_lite.html    # UI
├── start.sh            # Start script
├── context/            # Key context files (loaded at startup)
│   ├── life_map.md     # Priorities & focus
│   ├── constella.md    # Constella overview
│   └── audio.md        # Audio workflow reference
└── venv/               # Python dependencies
```

## Adding Context

Put markdown files in `context/` folder. Keywords in filenames determine when they're used:
- `life_map` / `priority` / `focus` / `direction`
- `constella` / `civic` / `governance`
- `audio` / `mastering` / `fgs`
- `faithh` / `backend` / `rag`

Reload context without restarting:
```bash
curl -X POST http://localhost:5557/api/reload_context
```

## Syncing with Windows FAITHH

For now, manually copy key files when needed:
- LIFE_MAP.md from Windows → context/life_map.md here
- Key decisions or updates as needed

Future: Could add rsync/ssh sync script

## Commands

**Start FAITHH Lite:**
```bash
./start.sh
# or
source venv/bin/activate && python faithh_lite.py
```

**Check status:**
```bash
curl http://localhost:5557/api/status
```

**Stop:**
```bash
pkill -f faithh_lite.py
```

**Stop Ollama (to save battery):**
```bash
brew services stop ollama
```

---

*Part of the FAITHH ecosystem - keeping you focused during audio work*
