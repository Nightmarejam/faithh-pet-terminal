FAITHH Master Context Document
Version: 2.0
Last Updated: 2025-10-23
Status: Active Development - UI Design Phase

🎯 Project Vision
FAITHH (Fidelity AI Through Holistic Harmonization) is a personal AI assistant system inspired by Megaman Battle Network's PET (PErsonal Terminal) device.
Core Concept

Personal AI companion (like MegaMan's Navi)
Battle Chips = Python tools/functions
Civic Framework integration for "living documentation"
RAG system with 4 months of AI conversation history

Design Philosophy

Retro-futuristic terminal aesthetic (Battle Network inspired)
Modular chip system for extensible functionality
PULSE watchdog for system monitoring (like antivirus programs in the games)
Real-time status displays and health monitoring


🏗️ Current Technical Stack
Frontend

Main UI: faithh_pet_v2.html
Port: 8080 (Python http.server)
Style: Terminal/PET aesthetic with cyan/purple/orange color scheme
Framework: Vanilla HTML/CSS/JS (no dependencies)

Backend

API: Flask (faithh_api.py)
Port: 5555
Language: Python 3.12

AI Providers (Hybrid System)

Google Gemini 2.0 Flash (Primary)

Model: gemini-2.0-flash-exp
API Key: Configured in environment
Mode: Free tier (60 req/min, 1500/day)
Purpose: Main AI reasoning, UI development assistance


Local Ollama (Fallback)

Running in Docker containers
Models: qwen2.5-7b, llama3.1-8b
Ports: 11434 (main), 11435 (embed), 11436 (qwen)
Purpose: Offline capability, privacy-sensitive tasks



Data Storage

Vector Database: ChromaDB
RAG System: 4 months of AI chat history
Purpose: Context retrieval, conversation continuity

Monitoring

PULSE: Custom watchdog system
Services Monitored: Ollama, Gemini, Web Server, Backend API
Auto-restart: Enabled for critical services


💻 System Environment
Hardware

OS: WSL2 Ubuntu 24.04.3 LTS on Windows 11 Pro
CPU: AMD Ryzen 9 3900X (12C/24T)
RAM: 64GB DDR4
GPU 1: NVIDIA RTX 3090 (24GB VRAM)
GPU 2: NVIDIA GTX 1080 Ti (11GB VRAM)
Storage: Samsung 970 EVO 1TB NVMe SSD

Software

Python: 3.12 (venv: ~/ai-stack/venv)
Docker: Running Ollama containers
Node/npm: Not installed (using vanilla JS)

Key Directories
