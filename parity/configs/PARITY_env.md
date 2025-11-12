# PARITY: .env
**Last Updated:** 2025-11-09
**Status:** Active (SECURED)
**Location:** Root directory (in .gitignore)

---

## Current State

**Purpose:** Store sensitive environment variables securely

**Key Settings:**
- `GEMINI_API_KEY` - Google Gemini API key
- `OLLAMA_HOST` - Ollama server URL
- `OLLAMA_URL` - Ollama API endpoint
- `BACKEND_PORT` - Backend server port (5557)
- `RAG_PORT` - RAG service port (5558)
- `CHROMADB_HOST` - ChromaDB host
- `CHROMADB_PORT` - ChromaDB port (8000)
- `ENVIRONMENT` - development/production
- `DEBUG` - Debug mode flag

**Used By:**
- faithh_professional_backend.py (loads via python-dotenv)

---

## Recent Changes

### 2025-11-08 - Initial Creation
**Created:**
- Created .env file with all configuration
- Added to .gitignore for security
- Configured backend to load from this file

**Reason:** Security best practice - no secrets in code

**Impact:** 
- All sensitive config centralized
- Easy environment-specific configuration
- No secrets in git repository

---

## Security Status

**✅ Secured:**
- File exists in root directory
- Listed in .gitignore (won't be committed)
- Only readable by user (should chmod 600)

**⚠️ Important:**
- NEVER commit this file to git
- NEVER share in chat/screenshots
- NEVER hardcode these values elsewhere

---

## Usage

**Loading in Python:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

**Loading in Bash:**
```bash
source .env
echo $GEMINI_API_KEY
```

---

## Template

**File Format:**
```env
# FAITHH Configuration
# Created: 2025-11-08

# Gemini API Key
GEMINI_API_KEY=your_key_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_URL=http://localhost:11434

# Backend Configuration
BACKEND_PORT=5557
RAG_PORT=5558

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# Environment
ENVIRONMENT=development
DEBUG=true
```

---

## Validation

**Check file exists and is secured:**
```bash
ls -la .env
# Should show: -rw------- (600 permissions)

# If not:
chmod 600 .env
```

**Check it's in .gitignore:**
```bash
grep ".env" .gitignore
# Should show: .env
```

---

## Notes

- Created as part of Monday security setup
- Replaced all hardcoded secrets
- Standard industry practice
- Works with python-dotenv package
- Template can be shared, actual file cannot

---

*Last reviewed: 2025-11-09*
