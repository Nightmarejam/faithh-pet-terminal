# Active Backend Information
**Last Updated:** $(date)

## Current Backend
**File:** faithh_professional_backend.py  
**Version:** v3  
**Port:** 5557  
**Status:** Active and running

## Features
- ✅ ChromaDB integration (91,302 documents)
- ✅ Fixed embedding dimensions
- ✅ Model identification enabled
- ✅ File upload support
- ✅ Workspace scanning

## Other Backend Files (Archived/Legacy)
- faithh_enhanced_backend.py (9KB) - Older version
- faithh_unified_api.py (13KB) - Has hardcoded key (to be removed)
- faithh_backend_adapter.py (9.6KB) - Adapter/wrapper
- rag_api.py (2.6KB) - Separate RAG endpoint

## Configuration
**Environment Variables:** Loaded from .env  
**Gemini API:** Via GEMINI_API_KEY environment variable  
**Ollama:** http://localhost:11434

## Startup Command
```bash
cd ~/ai-stack
source venv/bin/activate
python3 faithh_professional_backend.py
```

## Next Steps
- [ ] Update backend to use .env for API key
- [ ] Remove hardcoded keys from faithh_unified_api.py
- [ ] Archive non-active backend files
