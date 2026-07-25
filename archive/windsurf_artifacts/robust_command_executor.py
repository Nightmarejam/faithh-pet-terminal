#!/usr/bin/env python3
"""
Robust Command Executor
Sonnet-approved enhanced command monitoring system
"""

import subprocess
import time
import requests
import json
import signal
import os
from typing import Dict, Any, Optional

class RobustCommandExecutor:
    """Enhanced command executor with timeout and retry monitoring"""
    
    def __init__(self):
        self.timeout_map = {
            "curl": 30,      # Network operations
            "python3": 120,  # Long-running scripts
            "bash": 60       # Shell commands
        }
        self.max_retries = 3
        self.health_check_interval = 10
        self.backend_url = "http://localhost:5557/health"
        
    def identify_command_type(self, command: str) -> str:
        """Identify command type for timeout configuration"""
        if "curl" in command:
            return "curl"
        elif "python3" in command:
            return "python3"
        elif "bash" in command:
            return "bash"
        else:
            return "bash"  # Default
    
    def execute_with_monitoring(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute command with timeout and retry monitoring"""
        command_type = self.identify_command_type(command)
        timeout = self.timeout_map.get(command_type, 60)
        
        print(f"🔧 Executing: {command[:50]}...")
        print(f"⏱️  Timeout: {timeout}s, Type: {command_type}")
        
        for attempt in range(self.max_retries):
            try:
                print(f"📝 Attempt {attempt + 1}/{self.max_retries}")
                
                # Execute with timeout
                result = subprocess.run(
                    command, cwd=cwd, timeout=timeout,
                    capture_output=True, text=True, shell=True
                )
                
                if result.returncode == 0:
                    print(f"✅ Success: {len(result.stdout)} chars output")
                    return {"success": True, "output": result.stdout}
                else:
                    print(f"❌ Command failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"⚠️ Command timed out (attempt {attempt + 1}/{self.max_retries})")
                self.cleanup_hanging_processes(command_type)
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                
        return {"success": False, "error": "Max retries exceeded"}
    
    def cleanup_hanging_processes(self, command_type: str):
        """Clean up hanging processes"""
        print(f"🧹 Cleaning up hanging {command_type} processes...")
        
        try:
            if command_type == "curl":
                subprocess.run(["pkill", "-f", "curl"], capture_output=True)
            elif command_type == "python3":
                subprocess.run(["pkill", "-f", "python3"], capture_output=True)
            elif command_type == "bash":
                subprocess.run(["pkill", "-f", "bash"], capture_output=True)
                
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    def health_check(self) -> bool:
        """Monitor backend health"""
        try:
            response = requests.get(self.backend_url, timeout=5)
            if response.status_code == 200:
                print("💚 Backend healthy")
                return True
            else:
                print(f"💔 Backend unhealthy: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"💔 Backend health check failed: {e}")
            return False
    
    def restart_backend(self):
        """Restart backend if needed"""
        print("🔄 Restarting backend...")
        
        try:
            # Stop backend
            subprocess.run(["./stop_backend.sh"], cwd="/home/jonat/ai-stack", capture_output=True)
            time.sleep(2)
            
            # Start backend
            start_cmd = "tmux new-session -d -s faithh-backend python3 faithh_backend_phase3b.py"
            subprocess.run(start_cmd, cwd="/home/jonat/ai-stack", shell=True)
            time.sleep(3)
            
            print("✅ Backend restarted")
            
        except Exception as e:
            print(f"❌ Backend restart failed: {e}")
    
    def test_phase3b_endpoints(self) -> Dict[str, Any]:
        """Test Phase 3B endpoints specifically"""
        print("🧪 Testing Phase 3B endpoints...")
        
        endpoints = [
            "http://localhost:5557/api/phase3b/load-alife-data",
            "http://localhost:5557/api/phase3b/map-signatures",
            "http://localhost:5557/api/phase3b/identify-domains"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            print(f"🔍 Testing: {endpoint}")
            
            try:
                response = requests.get(endpoint, timeout=30)
                if response.status_code == 200:
                    results[endpoint] = {
                        "success": True,
                        "status_code": response.status_code,
                        "response_length": len(response.text)
                    }
                    print(f"✅ {endpoint}: {response.status_code}")
                else:
                    results[endpoint] = {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    }
                    print(f"❌ {endpoint}: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                results[endpoint] = {
                    "success": False,
                    "error": "Timeout after 30s"
                }
                print(f"⏰ {endpoint}: Timeout")
                
            except Exception as e:
                results[endpoint] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ {endpoint}: {e}")
        
        return results

def main():
    """Main execution"""
    executor = RobustCommandExecutor()
    
    print("🚀 Robust Command Executor - Sonnet Approved")
    print("=" * 60)
    
    # Test backend health
    print("\n🏥 Backend Health Check:")
    if not executor.health_check():
        print("🔄 Restarting backend...")
        executor.restart_backend()
        time.sleep(5)
    
    # Test Phase 3B endpoints
    print("\n🧪 Phase 3B Endpoint Testing:")
    results = executor.test_phase3b_endpoints()
    
    print("\n📊 Results Summary:")
    for endpoint, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {endpoint}: {result.get('status_code', 'ERROR')}")
    
    # Test the specific hanging command
    print("\n🔧 Testing Hanging Command:")
    hanging_command = "curl -s http://localhost:5557/api/phase3b/map-signatures"
    result = executor.execute_with_monitoring(hanging_command, cwd="/home/jonat/ai-stack")
    
    if result["success"]:
        print("✅ Command succeeded!")
        print(f"Output: {result['output'][:200]}...")
    else:
        print("❌ Command failed!")
        print(f"Error: {result.get('error', 'Unknown')}")
    
    print("\n🎯 Execution Complete!")

if __name__ == "__main__":
    main()