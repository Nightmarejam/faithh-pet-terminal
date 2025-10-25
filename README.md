# FAITHH PET Terminal

Personal AI assistant inspired by Megaman Battle Network's PET (PErsonal Terminal) system.

## 🎮 Features

- **Battle Chip System** - Modular AI tools with agentic workflows
- **FAITHH Assistant** - AI companion powered by Gemini & Ollama
- **PULSE Monitor** - System watchdog and health monitoring
- **RAG System** - 4 months of conversation history searchable
- **Civic Framework** - Living document collaboration system

## 🚀 Quick Start

```bash
# Start all services
./start_faithh_docker.sh

# Access interface
http://localhost:8080/faithh_pet_v3.html

# Stop services
./stop_faithh_docker.sh
```

## 💻 Tech Stack

- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Backend**: Python Flask
- **AI**: Google Gemini 2.0 Flash + Ollama (Docker)
- **Database**: ChromaDB (vector store)
- **Environment**: WSL2 Ubuntu 24.04

## 📋 Requirements

- Python 3.12+
- Docker
- Ollama (in Docker)
- Gemini API key

## 🎴 Battle Chips

Chips are modular tools that can work independently or chain together:
- RAG Query - Search knowledge base
- Code Generator - Create code from descriptions
- Debugger - Find and fix bugs
- PULSE Check - System health monitoring
- ...and more!

## 🏗️ Project Structure

```
ai-stack/
├── faithh_pet_v3.html      # Main UI
├── faithh_api.py           # Backend API
├── start_faithh_docker.sh  # Startup script
├── stop_faithh_docker.sh   # Shutdown script
├── pulse_monitor.py        # Service monitor
├── images/                 # Avatar images
├── logs/                   # Service logs
└── chips/                  # Battle chip modules (coming soon)
```

## 📖 Documentation

- [Master Context](FAITHH_CONTEXT.md)
- [Battle Chip Design](BATTLE_CHIP_DESIGN.md)
- [Gemini Handoff Guide](GEMINI_HANDOFF.md)

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt!

## 📝 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- Inspired by Megaman Battle Network (Capcom)
- Built with assistance from Claude (Anthropic) and Gemini (Google)

---

**Status**: Active Development (v3.1)
