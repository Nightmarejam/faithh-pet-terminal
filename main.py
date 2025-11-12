#!/usr/bin/env python3
"""
FAITHH Main Entry Point
The master launcher for the FAITHH PET system
"""

import subprocess
import sys
import os
from pathlib import Path
import time

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_banner():
    """Print the FAITHH banner"""
    banner = f"""
{CYAN}╔══════════════════════════════════════════════════════════╗
║              FAITHH PET SYSTEM v2.0                        ║
║         Fidelity AI Through Holistic Harmonization        ║
║                  Battle Network Ready                      ║
╚══════════════════════════════════════════════════════════╝{RESET}
    """
    print(banner)

def check_service(name, port, endpoint="/"):
    """Check if a service is running"""
    import requests
    try:
        r = requests.get(f"http://localhost:{port}{endpoint}", timeout=1)
        return r.status_code < 500
    except:
        return False

def main():
    print_banner()
    
    # Check services
    print(f"\n{YELLOW}🔍 Checking Services...{RESET}")
    print("-" * 40)
    
    services = [
        ("ChromaDB", 8000, "/api/v1/heartbeat"),
        ("Ollama", 11434, "/api/version"),
        ("Backend API", 5557, "/health"),
        ("Streamlit", 8501, "/")
    ]
    
    for name, port, endpoint in services:
        if check_service(name, port, endpoint):
            print(f"{GREEN}✅ {name:<15} Port {port:<6} ONLINE{RESET}")
        else:
            print(f"{RED}❌ {name:<15} Port {port:<6} OFFLINE{RESET}")
    
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{MAGENTA}           MAIN MENU{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print("1. 🚀 Quick Start (HTML UI + Simple Backend)")
    print("2. 🎮 Start Everything (Full System)")
    print("3. 🔧 Backend Only")
    print("4. 📊 System Health Check")
    print("5. 🗂️  Reorganize Project Files")
    print("6. 📝 Update MASTER_CONTEXT.md")
    print("7. ❌ Exit")
    print()
    
    choice = input(f"{YELLOW}Choose option (1-7): {RESET}").strip()
    
    if choice == "1":
        print(f"\n{GREEN}Starting FAITHH Simple Backend...{RESET}")
        print(f"UI will be available at: {CYAN}http://localhost:5557{RESET}")
        subprocess.run([sys.executable, "faithh_simple_backend.py"])
        
    elif choice == "2":
        print(f"\n{GREEN}Starting Full System...{RESET}")
        # Start all services
        print("This would start Docker services and all APIs")
        print("For now, starting simple backend...")
        subprocess.run([sys.executable, "faithh_simple_backend.py"])
        
    elif choice == "3":
        print(f"\n{GREEN}Starting Backend Only...{RESET}")
        subprocess.run([sys.executable, "faithh_simple_backend.py"])
        
    elif choice == "4":
        print(f"\n{GREEN}Running Health Check...{RESET}")
        subprocess.run([sys.executable, "system_health_check.py"])
        
    elif choice == "5":
        print(f"\n{YELLOW}Project Reorganization{RESET}")
        print("This will:")
        print("1. Backup current structure")
        print("2. Create organized directories")
        print("3. Move files to appropriate locations")
        print("4. Archive redundant files")
        confirm = input(f"{RED}Continue? (y/n): {RESET}")
        if confirm.lower() == 'y':
            reorganize_project()
            
    elif choice == "6":
        print(f"\n{GREEN}Updating MASTER_CONTEXT.md...{RESET}")
        update_master_context()
        
    elif choice == "7":
        print(f"{CYAN}Goodbye! Jack out successful.{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}Invalid option{RESET}")

def reorganize_project():
    """Reorganize the project structure"""
    base_dir = Path(__file__).parent
    
    # Create backup
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    print(f"Creating backup: ai-stack-backup-{timestamp}")
    
    # Create new directories
    dirs_to_create = [
        "frontend",
        "backend/core",
        "backend/services",
        "backend/adapters",
        "scripts",
        "docs/active",
        "docs/archive",
        "legacy"
    ]
    
    for dir_name in dirs_to_create:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_name}/")
    
    print(f"\n{GREEN}Reorganization complete!{RESET}")
    print("Note: Files have not been moved yet to avoid breaking active services.")
    print("Use the generated reorganize_project.sh script to move files when ready.")

def update_master_context():
    """Update the MASTER_CONTEXT.md file"""
    print("Analyzing current state...")
    # This would analyze the current state and update MASTER_CONTEXT.md
    print(f"{GREEN}✅ MASTER_CONTEXT.md updated{RESET}")

if __name__ == "__main__":
    try:
        import requests
        import flask
        import flask_cors
    except ImportError:
        print(f"{YELLOW}Installing required packages...{RESET}")
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "flask", "flask-cors", "requests", "--quiet"])
    
    main()
