# Windsurf Handoff: Passive Collection System
**Date:** 2026-01-16
**Model:** GPT 5.2 Codex (High Reasoning) or Claude Sonnet 4 (Thinking)
**Task:** Implement the Passive Collection System per PASSIVE_COLLECTION_SPEC_PATCHED.md

---

## TL;DR

Build a passive data collection layer that automatically captures git activity, file changes, and service health. Output JSON files that aggregate into a unified system state for AI context.

**Deliverables:**
1. 4 collector classes in `scripts/collectors/`
2. Aggregator that combines outputs
3. CLI runner with cron support
4. Backend endpoint for AI consumption

---

## Current State (Verified 2026-01-15)

### ✅ What's Working
- **Backend:** `faithh_professional_backend_fixed.py` at localhost:5557
- **ChromaDB:** 29,013 docs in `faithh_knowledge_base` collection (192.158.1.243:8000)
- **Models:** `llama31-faithh:latest` + `qwen3-faithh:latest` via Ollama
- **Git:** Clean working tree, pushed to origin (commit b8e7a89)

### 📁 Relevant Existing Files
```
~/ai-stack/
├── faithh_professional_backend_fixed.py   # Add endpoint here
├── scripts/
│   ├── collect_system_state.py            # Reference for patterns
│   ├── system_health_check.py             # Reference for service checks
│   └── maintenance/
│       └── update_parity_files.py         # Reference for file watching
├── parity/
│   └── system_state_latest.json           # Current state output (update with collectors)
└── .env                                    # Has CHROMA_URL, OLLAMA_URL
```

---

## Implementation Requirements

### Directory Structure to Create
```bash
mkdir -p ~/ai-stack/scripts/collectors
mkdir -p ~/ai-stack/collectors/state
mkdir -p ~/ai-stack/collectors/daily
mkdir -p ~/ai-stack/logs
```

### Files to Create

| File | Purpose |
|------|---------|
| `scripts/collectors/__init__.py` | Package exports |
| `scripts/collectors/base_collector.py` | Abstract base class |
| `scripts/collectors/git_collector.py` | Git activity tracking |
| `scripts/collectors/file_collector.py` | File change detection |
| `scripts/collectors/health_collector.py` | Service health checks |
| `scripts/collectors/terminal_collector.py` | Command history (optional) |
| `scripts/collectors/aggregator.py` | Combines all outputs |
| `scripts/collectors/run_collectors.py` | CLI entry point |
| `collectors/config.json` | Collector configuration |

### Output File Naming Convention (CRITICAL)
Each collector has a `name` attribute that determines its output filename:
- `GitCollector.name = "git"` → outputs `collectors/state/git.json`
- `FileCollector.name = "file_changes"` → outputs `collectors/state/file_changes.json`
- `HealthCollector.name = "health"` → outputs `collectors/state/health.json`
- `TerminalCollector.name = "terminal"` → outputs `collectors/state/terminal.json`

Daily snapshots: `collectors/daily/YYYY-MM-DD.json`

---

## Specification Reference

The complete specification with all code is in:
**`docs/PASSIVE_COLLECTION_SPEC_PATCHED.md`**

This includes:
- Full implementation code for each collector
- JSON output schemas
- Aggregator logic
- Cron setup instructions
- Backend integration endpoint

**Read the full spec before implementing.** It's ~1100 lines with complete, tested code.

---

## Key Design Decisions

### 1. BaseCollector Pattern
All collectors inherit from `BaseCollector`:
```python
class BaseCollector(ABC):
    name: str = "base"
    version: str = "1.0"
    
    @abstractmethod
    def collect(self) -> dict: pass
    
    def run(self) -> dict:
        # Wraps collect() with metadata + error handling
        # Saves to collectors/state/{self.name}.json
```

### 2. Service Health Endpoints
```python
SERVICES = {
    "faithh_backend": {
        "url": "http://localhost:5557/health",
        "type": "http"
    },
    "ollama": {
        "url": "http://localhost:11434/api/tags",
        "type": "http"
    },
    "chromadb_gen8": {
        "url": "http://192.158.1.243:8000/api/v2/heartbeat",
        "type": "chromadb",
        "expected_docs": 29013,
        "collection": "faithh_knowledge_base"
    }
}
```

### 3. File Categorization
```python
def _categorize(path: Path) -> str:
    if path.name in ["project_states.json", "decisions_log.json", "work_log.json"]:
        return "state"
    elif path.suffix == ".md":
        return "documentation"
    elif path.suffix == ".py":
        return "code"
    elif path.suffix in [".html", ".css", ".js"]:
        return "ui"
    return "other"
```

### 4. Ignore Patterns
```python
IGNORE_PATTERNS = [
    '__pycache__', '.git', 'node_modules', '*.pyc', 
    '.venv', 'venv', '*.log', 'collectors/state', 'worktrees'
]
```

---

## Backend Integration

Add this endpoint to `faithh_professional_backend_fixed.py`:

```python
@app.route('/api/context/collectors')
def get_collector_context():
    """Return aggregated collector data for AI consumption"""
    try:
        # Add to imports at top: sys.path.insert(0, str(Path(__file__).parent))
        from scripts.collectors.aggregator import Aggregator
        aggregator = Aggregator()
        return jsonify(aggregator.aggregate())
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
```

---

## Testing Commands

```bash
# After implementation, test with:
cd ~/ai-stack

# Run all collectors
python -m scripts.collectors.run_collectors --all

# Check outputs
cat collectors/state/git.json | jq '.data.status'
cat collectors/state/health.json | jq '.data.services'
cat collectors/state/file_changes.json | jq '.data.summary'

# Test aggregation
python -m scripts.collectors.run_collectors --aggregate

# Test daily snapshot
python -m scripts.collectors.run_collectors --snapshot
ls collectors/daily/

# Test backend endpoint (after adding)
curl http://localhost:5557/api/context/collectors | jq '.ai_context.status_line'
```

---

## Success Criteria

✅ Implementation is complete when:

1. `python -m scripts.collectors.run_collectors --all` runs without errors
2. Four JSON files exist in `collectors/state/`:
   - `git.json`
   - `file_changes.json`  
   - `health.json`
   - `terminal.json`
3. Each JSON has correct structure: `collected_at`, `collector`, `version`, `success`, `data`
4. Aggregator produces combined output with `ai_context.status_line`
5. Daily snapshot saves to `collectors/daily/2026-01-16.json`
6. `/api/context/collectors` endpoint returns aggregated data

---

## Notes for AI Assistant

- **Working Directory:** `/home/jonat/ai-stack` (WSL2 Ubuntu)
- **Python:** Use system Python or create venv in `~/ai-stack/venv`
- **Git:** Repo is clean, commit your changes with meaningful message
- **Style:** Follow existing patterns in `scripts/collect_system_state.py`
- **Error Handling:** Fail gracefully - one collector failing shouldn't break others

---

## After Implementation

1. Run full test suite
2. Commit with message: `feat(collectors): implement passive collection system`
3. Set up cron jobs per spec
4. Verify cron runs work (check logs after 15 min)

---

**Full specification:** `docs/PASSIVE_COLLECTION_SPEC_PATCHED.md`
