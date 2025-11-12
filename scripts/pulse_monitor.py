#!/usr/bin/env python3
"""
PULSE - Persistent Universal Logic & System Engine
Watchdog monitor for FAITHH AI Stack
Save as: ~/ai-stack/pulse_monitor.py
Run with: python3 ~/ai-stack/pulse_monitor.py
"""

import subprocess
import time
import requests
import os
import socket
from datetime import datetime

class PulseMonitor:
    def __init__(self):
        self.services = {
            'ollama': {
                'port': 11434, 
                'name': 'Ollama', 
                'start_cmd': 'ollama serve',
                'auto_restart': True
            },
            'webserver': {
                'port': 8080, 
                'name': 'Web Server',
                'start_cmd': 'cd ~/ai-stack && python3 -m http.server 8080',
                'auto_restart': True
            },
            'backend': {
                'port': 5555, 
                'name': 'FAITHH Backend',
                'start_cmd': 'cd ~/ai-stack && python3 faithh_api.py',
                'auto_restart': True
            },
            'streamlit': {
                'port': 8501, 
                'name': 'Streamlit',
                'start_cmd': None,  # User must start manually
                'auto_restart': False
            }
        }
        self.log_file = os.path.expanduser('~/ai-stack/logs/pulse.log')
        self.check_interval = 30  # seconds
        
    def log(self, message, level='INFO'):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')
    
    def check_port(self, port):
        """Check if a port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    
    def start_service(self, service_key):
        """Start a service"""
        service = self.services[service_key]
        
        if not service['start_cmd']:
            self.log(f"{service['name']} must be started manually", 'WARN')
            return False
        
        self.log(f"Starting {service['name']}...", 'INFO')
        try:
            # Start service in background
            cmd = service['start_cmd']
            log_path = os.path.expanduser(f"~/ai-stack/logs/{service_key}.log")
            
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=open(log_path, 'a'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setpgrp
            )
            
            time.sleep(3)  # Wait for service to start
            
            if self.check_port(service['port']):
                self.log(f"{service['name']} started successfully on port {service['port']}", 'SUCCESS')
                return True
            else:
                self.log(f"Failed to start {service['name']}", 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"Error starting {service['name']}: {e}", 'ERROR')
            return False
    
    def check_services(self):
        """Check all services and restart if needed"""
        status = {}
        
        for key, service in self.services.items():
            is_running = self.check_port(service['port'])
            status[key] = is_running
            
            if is_running:
                self.log(f"✓ {service['name']} is running (port {service['port']})", 'INFO')
            else:
                self.log(f"✗ {service['name']} is down (port {service['port']})", 'WARN')
                
                if service['auto_restart']:
                    self.log(f"Auto-restart enabled for {service['name']}", 'INFO')
                    self.start_service(key)
        
        return status
    
    def run_continuous(self):
        """Run continuous monitoring"""
        self.log("🐕 PULSE Monitor starting...", 'INFO')
        self.log(f"Monitoring interval: {self.check_interval} seconds", 'INFO')
        
        # Initial startup check
        self.log("Performing initial service check...", 'INFO')
        self.check_services()
        
        self.log("Entering monitoring loop. Press Ctrl+C to stop.", 'INFO')
        
        try:
            while True:
                time.sleep(self.check_interval)
                self.log("--- Performing periodic check ---", 'INFO')
                self.check_services()
                
        except KeyboardInterrupt:
            self.log("PULSE Monitor stopped by user", 'INFO')
    
    def run_once(self):
        """Run a single check"""
        self.log("🐕 PULSE Monitor - Single Check", 'INFO')
        status = self.check_services()
        
        print("\n" + "="*50)
        print("SERVICE STATUS SUMMARY")
        print("="*50)
        
        for key, service in self.services.items():
            status_icon = "✓" if status[key] else "✗"
            status_text = "ONLINE" if status[key] else "OFFLINE"
            print(f"{status_icon} {service['name']:20} (port {service['port']:5}) - {status_text}")
        
        print("="*50)
        
        all_critical_up = all(status[k] for k in ['ollama', 'webserver', 'backend'])
        
        if all_critical_up:
            print("✅ All critical services are operational")
            print("🌐 Access FAITHH at: http://localhost:8080/faithh_pet_v2.html")
        else:
            print("⚠️  Some critical services are down")
            print("💡 Run this script with --start to attempt auto-start")
        
        return status


def main():
    import sys
    
    monitor = PulseMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--continuous' or sys.argv[1] == '-c':
            monitor.run_continuous()
        elif sys.argv[1] == '--start' or sys.argv[1] == '-s':
            monitor.log("Starting all services...", 'INFO')
            monitor.check_services()
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("""
🐕 PULSE Monitor - FAITHH AI Stack Watchdog

Usage:
  python3 pulse_monitor.py              Run single check
  python3 pulse_monitor.py --continuous Run continuous monitoring
  python3 pulse_monitor.py --start      Check and start services
  python3 pulse_monitor.py --help       Show this help

Monitored Services:
  - Ollama (port 11434)
  - Web Server (port 8080)
  - FAITHH Backend API (port 5555)
  - Streamlit (port 8501)

Logs: ~/ai-stack/logs/pulse.log
            """)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        monitor.run_once()


if __name__ == '__main__':
    main()