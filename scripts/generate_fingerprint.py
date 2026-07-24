#!/usr/bin/env python3
"""
FAITHH System Fingerprint Generator

Generates a unified system fingerprint capturing current state for AI session context.
Queries live services and reads state files to produce fingerprint_state.json.

Usage:
    python scripts/generate_fingerprint.py
    
Output:
    fingerprint_state.json (root directory)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_DIR = Path(__file__).parent.parent
FINGERPRINT_OUTPUT = BASE_DIR / "fingerprint_state.json"


def check_backend_health() -> dict:
    """Check FAITHH backend health."""
    try:
        import requests
        r = requests.get("http://localhost:5557/health", timeout=5)
        if r.ok:
            data = r.json()
            return {
                "status": "healthy",
                "port": 5557,
                "chromadb_docs": data.get("chromadb", {}).get("documents", 0),
                "features": len(data.get("features", [])),
                "providers": data.get("providers", {})
            }
        return {"status": "unhealthy", "port": 5557, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "unreachable", "port": 5557, "error": str(e)}


def check_chromadb_health() -> dict:
    """Check ChromaDB health on Gen8."""
    try:
        import requests
        r = requests.get("http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat", timeout=5)
        if r.ok:
            return {"status": "healthy", "host": "servicebox.taileb8c60.ts.net", "port": 8000}
        return {"status": "unhealthy", "host": "servicebox.taileb8c60.ts.net", "port": 8000, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "unreachable", "host": "servicebox.taileb8c60.ts.net", "port": 8000, "error": str(e)}


def check_ollama_health() -> dict:
    """Check Ollama service and list models."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.ok:
            models = [m["name"] for m in r.json().get("models", [])]
            return {"status": "healthy", "port": 11434, "models": models}
        return {"status": "unhealthy", "port": 11434, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "unreachable", "port": 11434, "error": str(e)}


def get_active_model_config() -> dict:
    """Read active model configuration from config.yaml."""
    config_path = BASE_DIR / "config.yaml"
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        ai_config = config.get("ai", {})
        ollama_config = ai_config.get("ollama", {})
        
        return {
            "default": ollama_config.get("default", {}).get("model", "qwen25-grounded:latest"),
            "reasoning": ollama_config.get("heavy_reasoning", {}).get("model", "deepseek-r1:32b"),
            "provider": "ollama",
            "groq_available": bool(os.environ.get("GROQ_API_KEY")),
            "gemini_available": bool(os.environ.get("GEMINI_API_KEY"))
        }
    except Exception as e:
        return {
            "default": "qwen25-grounded:latest",
            "reasoning": "deepseek-r1:32b",
            "provider": "ollama",
            "error": str(e)
        }


def get_open_loops() -> list:
    """Extract open loops from scaffolding_state.json."""
    scaffolding_path = BASE_DIR / "scaffolding_state.json"
    try:
        with open(scaffolding_path, 'r') as f:
            data = json.load(f)
        
        loops = []
        open_loops_data = data.get("open_loops", [])
        
        # Handle both list and dict formats
        if isinstance(open_loops_data, list):
            for loop_data in open_loops_data:
                if isinstance(loop_data, dict):
                    loops.append({
                        "id": loop_data.get("id", ""),
                        "description": loop_data.get("description", loop_data.get("what", "")),
                        "status": loop_data.get("status", "open"),
                        "priority": loop_data.get("priority", "medium"),
                        "created": loop_data.get("created", loop_data.get("when", ""))
                    })
        elif isinstance(open_loops_data, dict):
            for loop_id, loop_data in open_loops_data.items():
                if isinstance(loop_data, dict):
                    loops.append({
                        "id": loop_id,
                        "description": loop_data.get("description", ""),
                        "status": loop_data.get("status", "unknown"),
                        "priority": loop_data.get("priority", "medium"),
                        "created": loop_data.get("created", "")
                    })
        
        # Also check active_context for current focus
        active = data.get("active_context", {})
        if active:
            loops.insert(0, {
                "id": "current_focus",
                "description": active.get("phase_goal", active.get("position_summary", ""))[:100],
                "status": "active",
                "priority": "high",
                "created": active.get("entered_phase", "")
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        loops.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))
        
        return loops[:10]  # Return top 10
    except Exception as e:
        return [{"error": str(e)}]


def get_recent_decisions() -> list:
    """Extract recent decisions from decisions_log.json."""
    decisions_path = BASE_DIR / "decisions_log.json"
    try:
        with open(decisions_path, 'r') as f:
            data = json.load(f)
        
        decisions = data.get("decisions", [])
        recent = decisions[-5:] if len(decisions) > 5 else decisions
        
        return [
            {
                "id": d.get("id", ""),
                "decision": d.get("decision", "")[:100],  # Truncate
                "date": d.get("date", ""),
                "status": d.get("status", ""),
                "project": d.get("project", "")
            }
            for d in reversed(recent)
        ]
    except Exception as e:
        return [{"error": str(e)}]


def get_project_summary() -> dict:
    """Extract project summary from project_states.json."""
    states_path = BASE_DIR / "project_states.json"
    try:
        with open(states_path, 'r') as f:
            data = json.load(f)
        
        projects = {}
        for proj_id, proj_data in data.get("projects", {}).items():
            if isinstance(proj_data, dict):
                projects[proj_id] = {
                    "name": proj_data.get("name", proj_id),
                    "phase": proj_data.get("phase", "Unknown"),
                    "status": proj_data.get("phase_status", proj_data.get("status", "Unknown"))
                }
        
        return {
            "last_updated": data.get("last_updated", ""),
            "current_quarter": data.get("strategic_plan", {}).get("current_quarter", ""),
            "projects": projects
        }
    except Exception as e:
        return {"error": str(e)}


def get_ml_chips_summary() -> dict:
    """Get ML chips summary."""
    chips_path = BASE_DIR / "ml" / "output" / "chips.json"
    try:
        with open(chips_path, 'r') as f:
            data = json.load(f)
        
        chips = data if isinstance(data, list) else data.get("chips", [])
        return {
            "total_chips": len(chips),
            "chip_names": [c.get("name", c.get("id", "unknown"))[:30] for c in chips[:15]]
        }
    except Exception as e:
        return {"total_chips": 0, "error": str(e)}


def generate_fingerprint() -> dict:
    """Generate complete system fingerprint."""
    print("🔍 Generating system fingerprint...")
    
    fingerprint = {
        "generated_at": datetime.now().isoformat(),
        "generator": "scripts/generate_fingerprint.py",
        "version": "1.0",
        
        "health": {
            "backend": check_backend_health(),
            "chromadb": check_chromadb_health(),
            "ollama": check_ollama_health()
        },
        
        "active_model": get_active_model_config(),
        
        "open_loops": get_open_loops(),
        
        "recent_decisions": get_recent_decisions(),
        
        "projects": get_project_summary(),
        
        "ml_chips": get_ml_chips_summary(),
        
        "session_context": {
            "last_query": None,
            "conversation_id": None,
            "chips_activated": []
        }
    }
    
    # Calculate overall health status
    health_statuses = [
        fingerprint["health"]["backend"].get("status"),
        fingerprint["health"]["chromadb"].get("status"),
        fingerprint["health"]["ollama"].get("status")
    ]
    
    if all(s == "healthy" for s in health_statuses):
        fingerprint["overall_status"] = "healthy"
    elif any(s == "healthy" for s in health_statuses):
        fingerprint["overall_status"] = "degraded"
    else:
        fingerprint["overall_status"] = "unhealthy"
    
    return fingerprint


def main():
    """Main entry point."""
    fingerprint = generate_fingerprint()
    
    # Write to file
    with open(FINGERPRINT_OUTPUT, 'w') as f:
        json.dump(fingerprint, f, indent=2)
    
    print(f"✅ Fingerprint written to: {FINGERPRINT_OUTPUT}")
    print(f"   Overall status: {fingerprint['overall_status']}")
    print(f"   Backend: {fingerprint['health']['backend'].get('status')}")
    print(f"   ChromaDB: {fingerprint['health']['chromadb'].get('status')}")
    print(f"   Ollama: {fingerprint['health']['ollama'].get('status')}")
    print(f"   Open loops: {len(fingerprint['open_loops'])}")
    print(f"   Recent decisions: {len(fingerprint['recent_decisions'])}")
    
    return fingerprint


if __name__ == "__main__":
    main()
