#!/usr/bin/env python3
"""
FAITHH System Health Check and Launcher
Tests all components and provides a unified entry point
"""

import subprocess
import time
import json
import sys
import os
from pathlib import Path

class SystemHealthChecker:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.results = {
            'services': {},
            'apis': {},
            'files': {},
            'recommendations': []
        }
    
    def check_service(self, name, port, path='/'):
        """Check if a service is running on a port"""
        try:
            result = subprocess.run(
                f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port}{path}",
                shell=True, capture_output=True, text=True, timeout=2
            )
            is_running = result.stdout.strip() != '000'
            self.results['services'][name] = {
                'port': port,
                'running': is_running,
                'status_code': result.stdout.strip()
            }
            return is_running
        except:
            self.results['services'][name] = {
                'port': port,
                'running': False,
                'status_code': 'error'
            }
            return False
    
    def check_process(self, name):
        """Check if a process is running"""
        try:
            result = subprocess.run(
                f"ps aux | grep -E '{name}' | grep -v grep",
                shell=True, capture_output=True, text=True
            )
            is_running = bool(result.stdout.strip())
            return is_running
        except:
            return False
    
    def check_python_module(self, module):
        """Check if a Python module is installed"""
        try:
            result = subprocess.run(
                f"python3 -c 'import {module}'",
                shell=True, capture_output=True, text=True,
                cwd=self.base_dir
            )
            return result.returncode == 0
        except:
            return False
    
    def check_file_exists(self, filename):
        """Check if a file exists"""
        file_path = self.base_dir / filename
        exists = file_path.exists()
        self.results['files'][filename] = exists
        return exists
    
    def print_results(self):
        """Print formatted results"""
        print("=" * 60)
        print("FAITHH SYSTEM HEALTH CHECK")
        print("=" * 60)
        
        # Services
        print("\n📡 SERVICES:")
        print("-" * 40)
        for name, info in self.results['services'].items():
            status = "✅ RUNNING" if info['running'] else "❌ DOWN"
            print(f"  {name:<20} Port {info['port']:<6} {status}")
        
        # Critical Files
        print("\n📁 CRITICAL FILES:")
        print("-" * 40)
        for filename, exists in self.results['files'].items():
            status = "✅" if exists else "❌"
            print(f"  {status} {filename}")
        
        # Recommendations
        if self.results['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            print("-" * 40)
            for rec in self.results['recommendations']:
                print(f"  • {rec}")
    
    def run_checks(self):
        """Run all health checks"""
        print("Running system checks...")
        
        # Check services
        self.check_service('ChromaDB', 8000, '/api/v1/heartbeat')
        self.check_service('Ollama Main', 11434, '/api/version')
        self.check_service('Ollama Embed', 11435, '/api/version')
        self.check_service('Unified API', 5556, '/health')
        self.check_service('Backend Adapter', 5557, '/health')
        self.check_service('HTML UI', 8080, '/')
        self.check_service('Streamlit', 8501, '/')
        
        # Check critical files
        self.check_file_exists('faithh_unified_api.py')
        self.check_file_exists('faithh_backend_adapter.py')
        self.check_file_exists('faithh_pet_v3.html')
        self.check_file_exists('rag-chat.html')
        self.check_file_exists('requirements.txt')
        self.check_file_exists('MASTER_CONTEXT.md')
        
        # Check Python dependencies
        missing_modules = []
        for module in ['flask', 'chromadb', 'requests', 'streamlit']:
            if not self.check_python_module(module):
                missing_modules.append(module)
        
        if missing_modules:
            self.results['recommendations'].append(
                f"Install missing modules: pip install {' '.join(missing_modules)}"
            )
        
        # Add recommendations based on results
        if not self.results['services']['ChromaDB']['running']:
            self.results['recommendations'].append(
                "Start ChromaDB: docker-compose up -d chromadb"
            )
        
        if not self.results['services']['Unified API']['running']:
            self.results['recommendations'].append(
                "Start Unified API: python3 faithh_unified_api.py"
            )
        
        return self.results

def main():
    checker = SystemHealthChecker()
    checker.run_checks()
    checker.print_results()
    
    # Check if we should start services
    print("\n" + "=" * 60)
    print("LAUNCH OPTIONS")
    print("=" * 60)
    print("1. Run health check only (done)")
    print("2. Start missing services")
    print("3. Start complete system")
    print("4. Connect HTML UI to backend")
    print("5. Exit")
    
    try:
        choice = input("\nChoice (1-5): ").strip()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    
    if choice == '2':
        print("\nStarting missing services...")
        # Logic to start only missing services
        if not checker.results['services']['Unified API']['running']:
            print("Starting Unified API...")
            subprocess.Popen(['python3', 'faithh_unified_api.py'])
            time.sleep(2)
    
    elif choice == '3':
        print("\nStarting complete system...")
        # Start everything in order
        print("1. Starting ChromaDB...")
        print("2. Starting Unified API...")
        print("3. Starting Backend Adapter...")
        print("4. Starting HTML UI server...")
        
    elif choice == '4':
        print("\nUpdating HTML UI to connect to backend...")
        print("This will modify faithh_pet_v3.html to connect to the backend adapter")
        # We'll implement this next
    
    print("\nSystem check complete!")

if __name__ == "__main__":
    main()
