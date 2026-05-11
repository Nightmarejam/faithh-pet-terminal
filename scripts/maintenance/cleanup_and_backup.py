#!/usr/bin/env python3
"""
FAITHH Project Cleanup & Git Backup
Organizes files and creates a clean Git commit
"""

from pathlib import Path
import shutil
from datetime import datetime
import subprocess

def organize_scripts():
    """Organize scripts into categories"""
    
    scripts_dir = Path.home() / "ai-stack/scripts"
    
    # Create organized subdirectories
    categories = {
        "indexing": ["index_recent_docs.py", "index_claude_chats.py", "index_claude_chats_chunked.py"],
        "memory": ["add_memory_system.py", "auto_integrate_memory.py", "fix_memory_integration.py", 
                  "add_memory_test.py", "fix_system_prompt.py"],
        "rag": ["apply_rag_patch.py", "fix_smart_rag_parameter.py", "improve_smart_rag.py",
                "analyze_backend_rag.py", "test_rag_diagnostic.py"],
        "personality": ["create_enhanced_personality.py", "apply_enhanced_personality.py"],
        "maintenance": ["update_parity_files.py", "apply_final_fix.py"],
        "archive": []  # Older/duplicate scripts
    }
    
    print("📁 Organizing scripts...")
    
    for category, script_list in categories.items():
        category_dir = scripts_dir / category
        category_dir.mkdir(exist_ok=True)
        
        for script in script_list:
            src = scripts_dir / script
            if src.exists():
                dst = category_dir / script
                if not dst.exists():
                    shutil.move(str(src), str(dst))
                    print(f"   ✅ Moved {script} → {category}/")
    
    print("✅ Scripts organized!\n")

def organize_docs():
    """Organize documentation"""
    
    docs_dir = Path.home() / "ai-stack/docs"
    
    print("📚 Organizing documentation...")
    
    # Ensure proper structure
    subdirs = ["specifications", "guides", "parity", "plans", "patches", "archive"]
    for subdir in subdirs:
        (docs_dir / subdir).mkdir(exist_ok=True)
    
    # Move session summaries to docs root
    ai_stack = Path.home() / "ai-stack"
    for item in ai_stack.glob("SESSION_*.md"):
        dst = docs_dir / item.name
        if not dst.exists():
            shutil.copy2(item, dst)
            print(f"   ✅ Copied {item.name} to docs/")
    
    print("✅ Documentation organized!\n")

def cleanup_backups():
    """Archive old backups"""
    
    ai_stack = Path.home() / "ai-stack"
    backups_dir = ai_stack / "backups"
    backups_dir.mkdir(exist_ok=True)
    
    print("🗑️  Archiving backup files...")
    
    backup_count = 0
    for backup in ai_stack.glob("*.backup*"):
        dst = backups_dir / backup.name
        if not dst.exists():
            shutil.move(str(backup), str(dst))
            backup_count += 1
    
    print(f"   ✅ Archived {backup_count} backup files\n")

def create_gitignore():
    """Create .gitignore if needed"""
    
    ai_stack = Path.home() / "ai-stack"
    gitignore = ai_stack / ".gitignore"
    
    ignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Logs
*.log
nohup.out

# Backups
*.backup*
backups/

# Temporary files
*.tmp
.DS_Store

# ChromaDB data
chroma_data/

# Large exports (optional - comment out if you want to track these)
# AI_Chat_Exports/

# Environment variables
.env

# IDE
.vscode/
.idea/
"""
    
    if not gitignore.exists():
        gitignore.write_text(ignore_content)
        print("✅ Created .gitignore\n")
    else:
        print("✅ .gitignore exists\n")

def create_readme():
    """Create or update README"""
    
    ai_stack = Path.home() / "ai-stack"
    readme = ai_stack / "README.md"
    
    content = f"""# FAITHH AI System
**Friendly AI Teaching & Helping Hub**

> Personal AI assistant with MegaMan Battle Network aesthetic

## Overview

FAITHH is a personal AI system featuring:
- 🧠 **RAG System**: 91,604+ indexed documents with semantic search
- 💾 **Persistent Memory**: Maintains context across sessions
- 🎨 **Custom UI**: MegaMan Battle Network themed interface
- 🤖 **Local LLMs**: Ollama (Llama 3.1-8B, Qwen 2.5-7B)
- ☁️ **Cloud Fallback**: Gemini API integration
- 📚 **Auto-Indexing**: Conversations automatically added to knowledge base

## Quick Start

```bash
# Start ChromaDB
docker start chromadb  # or your ChromaDB startup command

# Start FAITHH backend
cd ~/ai-stack
source venv/bin/activate
python faithh_professional_backend_fixed.py

# Access UI
open http://localhost:5557
```

## Architecture

### Components
- **Backend**: Flask (port 5557)
- **Vector DB**: ChromaDB (port 8000)
- **Embeddings**: all-mpnet-base-v2 (768-dim)
- **Frontend**: faithh_pet_v3.html
- **Memory**: faithh_memory.json

### Data Flow
```
User → UI → Backend → RAG (ChromaDB) + Memory → LLM → Response
                                                   ↓
                                            Auto-Index
```

## Project Structure

```
ai-stack/
├── faithh_professional_backend_fixed.py  # Main backend
├── faithh_pet_v3.html                    # Production UI
├── faithh_memory.json                    # Persistent memory
├── docs/                                 # Documentation
│   ├── specifications/                   # Technical specs
│   ├── guides/                          # How-to guides
│   ├── parity/                          # Tracking files
│   └── plans/                           # Future plans
├── scripts/                             # Utility scripts
│   ├── indexing/                       # Document indexing
│   ├── memory/                         # Memory system
│   ├── rag/                           # RAG optimization
│   └── maintenance/                    # Cleanup & updates
└── AI_Chat_Exports/                    # Conversation exports

## Current Status

**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}

### Completed
- ✅ RAG system operational (91,604 documents)
- ✅ Conversation chunking (145 semantic chunks)
- ✅ Persistent memory system
- ✅ Enhanced personality prompt
- ✅ Auto-indexing conversations
- ✅ Smart RAG query prioritization

### In Progress
- 🔄 Memory context integration refinement
- 🔄 ChatGPT/Grok export indexing
- 🔄 UI polish and feedback

### Planned
- 📋 Voice-to-text integration
- 📋 Session history viewer
- 📋 Direct DAW integration
- 📋 ComfyUI workflow integration

## Documentation

- [Current State](docs/CURRENT_STATE.md) - System status
- [Master Action Log](MASTER_ACTION_LOG.md) - Decision history
- [ChromaDB Status](docs/CHROMADB_STATUS.md) - Database metrics
- [Session Summaries](docs/) - Development sessions

## Development

Created by Jonathan for personal AI assistance in audio production and development work.

**Theme Inspiration**: MegaMan Battle Network NetNavi companions

---

*FAITHH - Your digital companion for creative and technical work* 🎮✨
```

    readme.write_text(content)
    print("✅ README.md updated\n")

def git_status():
    """Check Git status"""
    
    ai_stack = Path.home() / "ai-stack"
    
    print("🔍 Checking Git status...")
    
    # Check if git repo exists
    if not (ai_stack / ".git").exists():
        print("   ⚠️  Not a Git repository")
        print("   Run: git init")
        return False
    
    # Get status
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ai_stack,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(f"\n   Modified files: {len(result.stdout.splitlines())}")
        print(result.stdout[:500])
    else:
        print("   ✅ Working tree clean")
    
    return True

def create_commit_message():
    """Create detailed commit message"""
    
    message = f"""Major Milestone: RAG + Memory System Complete

Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Features Added
- ✅ RAG system with 91,604+ documents
- ✅ Conversation chunking (145 semantic chunks)
- ✅ Persistent memory system (faithh_memory.json)
- ✅ Enhanced FAITHH personality prompt
- ✅ Auto-indexing of conversations
- ✅ Smart RAG query prioritization

## Technical Improvements
- Added smart_rag_query() function
- Implemented memory load/save functions
- Created conversation chunk indexer
- Enhanced system prompt with memory context
- Added debug logging for RAG queries

## Documentation
- Updated CURRENT_STATE.md
- Created SESSION_SUMMARY_2025-11-14.md
- Updated MASTER_ACTION_LOG.md
- Added PERSISTENT_MEMORY_DESIGN.md

## Scripts Added
- Indexing: index_recent_docs, index_claude_chats_chunked
- Memory: add_memory_system, fix_memory_integration
- RAG: apply_rag_patch, improve_smart_rag
- Maintenance: update_parity_files, cleanup scripts

## Next Steps
- Refine memory context integration
- Index ChatGPT/Grok exports
- UI polish and feedback improvements
"""
    
    return message

def main():
    print("=" * 70)
    print("FAITHH PROJECT CLEANUP & GIT BACKUP")
    print("=" * 70)
    print()
    
    # Organize
    organize_scripts()
    organize_docs()
    cleanup_backups()
    create_gitignore()
    create_readme()
    
    # Git status
    print("=" * 70)
    has_git = git_status()
    print()
    
    # Show commit message
    print("📝 Suggested commit message:")
    print("-" * 70)
    print(create_commit_message())
    print("-" * 70)
    print()
    
    # Instructions
    print("🎯 Next Steps:")
    print()
    
    if not has_git:
        print("1. Initialize Git repository:")
        print("   cd ~/ai-stack")
        print("   git init")
        print()
    
    print("2. Review changes:")
    print("   cd ~/ai-stack")
    print("   git status")
    print()
    
    print("3. Stage files:")
    print("   git add .")
    print()
    
    print("4. Commit:")
    print("   git commit -m 'Major Milestone: RAG + Memory System Complete'")
    print()
    
    print("5. (Optional) Create remote backup:")
    print("   git remote add origin <your-repo-url>")
    print("   git push -u origin main")
    print()
    
    print("=" * 70)
    print("✅ CLEANUP COMPLETE")
    print("=" * 70)
    print()
    print(f"📊 Summary:")
    print(f"   - Scripts organized into categories")
    print(f"   - Documentation structured")
    print(f"   - Backups archived")
    print(f"   - README.md created/updated")
    print(f"   - .gitignore created")
    print()

if __name__ == "__main__":
    main()
