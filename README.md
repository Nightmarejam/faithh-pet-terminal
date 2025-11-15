# FAITHH AI System
**Friendly AI Teaching & Helping Hub**

Personal AI assistant with MegaMan Battle Network aesthetic

## Quick Start
```bash
# Start backend
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend_fixed.py

# Access UI at http://localhost:5557
```

## Features

- RAG System: 91,604+ indexed documents
- Persistent Memory: Maintains context across sessions
- Custom UI: MegaMan Battle Network themed
- Local LLMs: Ollama (Llama 3.1-8B, Qwen 2.5-7B)
- Auto-Indexing: Conversations saved automatically

## Project Structure
```
ai-stack/
├── faithh_professional_backend_fixed.py  # Main backend
├── faithh_pet_v3.html                    # UI
├── faithh_memory.json                    # Persistent memory
├── docs/                                 # Documentation
└── scripts/                              # Utilities
    ├── indexing/                         # Document indexers
    ├── memory/                           # Memory system
    ├── rag/                              # RAG optimization
    ├── personality/                      # Personality tuning
    └── maintenance/                      # Cleanup tools
```

## Status

Last Updated: 2025-11-14

Completed:
- RAG system operational
- Conversation chunking (145 chunks)
- Persistent memory system
- Enhanced personality
- Auto-indexing

## Documentation

See `docs/` for detailed documentation and session summaries.
