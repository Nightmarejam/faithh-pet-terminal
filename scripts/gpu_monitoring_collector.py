#!/usr/bin/env python3
"""
GPU & Process Monitor
Tracks which GPUs are being used by which processes/containers

Save to: ~/ai-stack/scripts/gpu_monitor.py
Usage: python3 gpu_monitor.py [--watch]
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class GPUMonitor:
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        
    def get_gpu_processes(self) -> List[Dict[str, Any]]:
        """Get detailed info about processes using GPUs"""
        try:
            # Query GPU processes with details
            query = "gpu_uuid,pid,process_name,used_memory"
            result = subprocess.run(
                ["nvidia-smi", "--query-compute-apps=" + query, "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            processes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    gpu_uuid = parts[0]
                    pid = int(parts[1])
                    process_name = parts[2]
                    used_memory_mb = int(parts[3])
                    
                    # Get GPU index from UUID
                    gpu_index = self._get_gpu_index_from_uuid(gpu_uuid)
                    
                    # Get more details about the process
                    process_details = self._get_process_details(pid)
                    
                    # Check if it's a Docker container
                    container_info = self._get_container_from_pid(pid)
                    
                    processes.append({
                        "gpu_index": gpu_index,
                        "gpu_uuid": gpu_uuid,
                        "pid": pid,
                        "process_name": process_name,
                        "memory_used_mb": used_memory_mb,
                        "process_details": process_details,
                        "container": container_info,
                    })
            
            return processes
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def _get_gpu_index_from_uuid(self, uuid: str) -> Optional[int]:
        """Map GPU UUID to index (0, 1, etc)"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,uuid", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.strip().split('\n'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2 and parts[1] == uuid:
                    return int(parts[0])
            
            return None
        except:
            return None
    
    def _get_process_details(self, pid: int) -> Dict[str, Any]:
        """Get detailed info about a process"""
        try:
            # Get command line
            with open(f"/proc/{pid}/cmdline", "r") as f:
                cmdline = f.read().replace('\x00', ' ').strip()
            
            # Get process status
            with open(f"/proc/{pid}/status", "r") as f:
                status_lines = f.readlines()
                
            status = {}
            for line in status_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    status[key.strip()] = value.strip()
            
            return {
                "cmdline": cmdline,
                "name": status.get("Name", "unknown"),
                "state": status.get("State", "unknown"),
                "threads": status.get("Threads", "unknown"),
                "vm_size": status.get("VmSize", "unknown"),
            }
        except:
            return {"error": "Could not read process details"}
    
    def _get_container_from_pid(self, pid: int) -> Optional[Dict[str, str]]:
        """Check if PID belongs to a Docker container"""
        try:
            # Get all running containers with PIDs
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.ID}}:{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.strip().split('\n'):
                if ':' not in line:
                    continue
                    
                container_id, container_name = line.split(':', 1)
                
                # Get container's main PID
                inspect = subprocess.run(
                    ["docker", "inspect", container_id, "--format", "{{.State.Pid}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                container_pid = int(inspect.stdout.strip())
                
                # Check if our PID is in the container's namespace
                # (either the main PID or a child process)
                if self._is_pid_in_container(pid, container_pid):
                    return {
                        "id": container_id,
                        "name": container_name,
                    }
            
            return None
            
        except:
            return None
    
    def _is_pid_in_container(self, pid: int, container_pid: int) -> bool:
        """Check if PID belongs to container namespace"""
        try:
            # Simple check: read cgroup
            with open(f"/proc/{pid}/cgroup", "r") as f:
                cgroup = f.read()
                
            # If cgroup contains docker, it's a container process
            return "docker" in cgroup.lower()
        except:
            return False
    
    def get_gpu_allocation_summary(self) -> Dict[str, Any]:
        """High-level summary of GPU usage"""
        processes = self.get_gpu_processes()
        
        # Group by GPU
        gpu_usage = {}
        for proc in processes:
            gpu_idx = proc.get("gpu_index", "unknown")
            
            if gpu_idx not in gpu_usage:
                gpu_usage[gpu_idx] = {
                    "total_memory_mb": 0,
                    "process_count": 0,
                    "processes": [],
                    "containers": [],
                }
            
            gpu_usage[gpu_idx]["total_memory_mb"] += proc.get("memory_used_mb", 0)
            gpu_usage[gpu_idx]["process_count"] += 1
            gpu_usage[gpu_idx]["processes"].append({
                "pid": proc.get("pid"),
                "name": proc.get("process_name"),
                "memory_mb": proc.get("memory_used_mb"),
            })
            
            container = proc.get("container")
            if container and container not in gpu_usage[gpu_idx]["containers"]:
                gpu_usage[gpu_idx]["containers"].append(container)
        
        return gpu_usage
    
    def get_ollama_gpu_usage(self) -> List[Dict[str, Any]]:
        """Specifically track Ollama's GPU usage"""
        processes = self.get_gpu_processes()
        
        ollama_processes = []
        for proc in processes:
            # Check if it's an Ollama process
            process_name = proc.get("process_name", "").lower()
            cmdline = proc.get("process_details", {}).get("cmdline", "").lower()
            container = proc.get("container")
            
            is_ollama = (
                "ollama" in process_name or
                "ollama" in cmdline or
                (container and "ollama" in container.get("name", "").lower())
            )
            
            if is_ollama:
                ollama_processes.append({
                    "gpu_index": proc.get("gpu_index"),
                    "pid": proc.get("pid"),
                    "process_name": proc.get("process_name"),
                    "memory_mb": proc.get("memory_used_mb"),
                    "container": container.get("name") if container else None,
                })
        
        return ollama_processes
    
    def get_complete_report(self) -> Dict[str, Any]:
        """Complete GPU monitoring report"""
        return {
            "timestamp": self.timestamp,
            "gpu_processes": self.get_gpu_processes(),
            "gpu_allocation_summary": self.get_gpu_allocation_summary(),
            "ollama_gpu_usage": self.get_ollama_gpu_usage(),
        }
    
    def print_summary(self):
        """Print human-readable summary"""
        print("=" * 70)
        print("GPU & PROCESS MONITOR")
        print("=" * 70)
        print(f"Timestamp: {self.timestamp}")
        print()
        
        # GPU allocation summary
        summary = self.get_gpu_allocation_summary()
        
        print("GPU ALLOCATION:")
        for gpu_idx, usage in summary.items():
            print(f"\n  GPU {gpu_idx}:")
            print(f"    Total VRAM Used: {usage['total_memory_mb']} MB")
            print(f"    Process Count:   {usage['process_count']}")
            
            if usage['containers']:
                print(f"    Containers:")
                for container in usage['containers']:
                    print(f"      - {container['name']} (ID: {container['id'][:12]})")
            
            if usage['processes']:
                print(f"    Processes:")
                for proc in usage['processes']:
                    print(f"      - PID {proc['pid']}: {proc['name']} ({proc['memory_mb']} MB)")
        
        # Ollama-specific summary
        ollama = self.get_ollama_gpu_usage()
        
        print("\n" + "=" * 70)
        print("OLLAMA GPU USAGE:")
        
        if ollama:
            for proc in ollama:
                gpu = proc['gpu_index']
                container = proc['container'] or "N/A"
                print(f"  GPU {gpu}: {proc['process_name']} ({proc['memory_mb']} MB)")
                print(f"           Container: {container}")
                print(f"           PID: {proc['pid']}")
        else:
            print("  No Ollama processes found using GPU")
        
        print("=" * 70)
    
    def save_report(self, output_dir: str = "~/ai-stack/parity"):
        """Save report to JSON file"""
        output_path = Path(output_dir).expanduser()
        output_path.mkdir(parents=True, exist_ok=True)
        
        report = self.get_complete_report()
        
        # Save timestamped version
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_path / f"gpu_report_{timestamp_str}.json"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save as latest
        latest_path = output_path / "gpu_report_latest.json"
        with open(latest_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {filepath}")
        return filepath


def watch_mode(interval: int = 5):
    """Continuous monitoring mode"""
    import time
    
    print("Starting GPU monitoring (Ctrl+C to stop)...")
    print(f"Update interval: {interval} seconds")
    print()
    
    try:
        while True:
            # Clear screen (works in most terminals)
            print("\033[2J\033[H", end="")
            
            monitor = GPUMonitor()
            monitor.print_summary()
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def main():
    parser = argparse.ArgumentParser(description="GPU & Process Monitor")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuous monitoring mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval in watch mode (seconds)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to JSON file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON"
    )
    
    args = parser.parse_args()
    
    if args.watch:
        watch_mode(args.interval)
    else:
        monitor = GPUMonitor()
        
        if args.json:
            report = monitor.get_complete_report()
            print(json.dumps(report, indent=2))
        else:
            monitor.print_summary()
        
        if args.save:
            monitor.save_report()


if __name__ == "__main__":
    main()
