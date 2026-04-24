"""
FAITHH Backend — Data Loaders
JSON file I/O for persistent state: memory, decisions, project states, scaffolding.
Extracted from faithh_professional_backend_fixed.py for modularity.
"""

import json
from pathlib import Path
from datetime import datetime

# File paths
BASE_DIR = Path.home() / "ai-stack"
MEMORY_FILE = BASE_DIR / "faithh_memory.json"
DECISIONS_LOG = BASE_DIR / "decisions_log.json"
PROJECT_STATES = BASE_DIR / "project_states.json"
SCAFFOLDING_FILE = BASE_DIR / "scaffolding_state.json"


def load_json_file(filepath):
    """Generic JSON file loader"""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"❌ Error loading {filepath.name}: {e}")
        return None


def load_memory():
    """Load persistent memory from disk"""
    memory = load_json_file(MEMORY_FILE)
    if memory is None:
        print("⚠️  Memory file not found, using defaults")
        return {"user_profile": {"name": "Jonathan"}}
    return memory


def load_decisions():
    """Load decisions log"""
    return load_json_file(DECISIONS_LOG)


def load_project_states():
    """Load project states"""
    return load_json_file(PROJECT_STATES)


def load_scaffolding():
    """Load scaffolding state for structural awareness"""
    return load_json_file(SCAFFOLDING_FILE)


def save_scaffolding(scaffolding):
    """Persist scaffolding state to disk"""
    try:
        scaffolding['meta']['last_updated'] = datetime.now().isoformat()
        with open(SCAFFOLDING_FILE, 'w') as f:
            json.dump(scaffolding, f, indent=2)
        print(f"🏗️  Scaffolding saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error saving scaffolding: {e}")


def save_memory(memory):
    """Persist memory to disk"""
    try:
        memory["last_updated"] = datetime.now().isoformat()
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=2)
        print(f"💾 Memory saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error saving memory: {e}")
