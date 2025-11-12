# PARITY: config.yaml
**Last Updated:** 2025-11-09
**Status:** Active
**Location:** Root directory

---

## Current State

**Purpose:** Non-sensitive system configuration

**Key Settings:**
```yaml
chromadb:
  host: localhost
  port: 8000
  
models:
  gemini: gemini-pro
  ollama_default: llama3.1
  
rag:
  enabled: true
  max_results: 5
```

**Used By:**
- Backend for system configuration
- Various utilities and tools

---

## Recent Changes

### 2025-11-03 - Initial Configuration
**Created:**
- Basic ChromaDB configuration
- Model settings
- RAG configuration

---

## Settings Explained

**ChromaDB:**
- `host` - Where ChromaDB runs (localhost for local)
- `port` - ChromaDB port (8000 standard)

**Models:**
- `gemini` - Gemini model identifier
- `ollama_default` - Default Ollama model

**RAG:**
- `enabled` - Whether to use RAG by default
- `max_results` - How many docs to retrieve

---

## Notes

- Non-sensitive config (safe to commit)
- YAML format for readability
- Can be extended as needed
- Separate from .env (which has secrets)

---

*Last reviewed: 2025-11-09*
