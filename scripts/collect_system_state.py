#!/usr/bin/env python3
"""
Comprehensive System State Collector
Generates machine-readable snapshots of the entire AI workstation state

Save to: ~/ai-stack/scripts/collect_system_state.py
Run: python3 ~/ai-stack/scripts/collect_system_state.py
Output: ~/ai-stack/parity/system_state_[timestamp].json
"""

import json
import os
import platform
import socket
import subprocess
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import psutil
    import requests
    _IMPORT_ERROR = None
except ImportError as exc:
    psutil = None
    requests = None
    _IMPORT_ERROR = exc

class SystemStateCollector:
    def __init__(self, output_dir: str = None) -> None:
        self.output_dir = Path(output_dir or "~/ai-stack/parity").expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().isoformat()
        
    def collect_all(self) -> Dict[str, Any]:
        """Collect complete system state"""
        print("🔍 Collecting system state...")
        
        state: Dict[str, Any] = {
            "metadata": self.get_metadata(),
            "hardware": self.get_hardware_state(),
            "gpu": self.get_gpu_state(),
            "storage": self.get_storage_state(),
            "network": self.get_network_state(),
            "docker": self.get_docker_state(),
            "services": self.get_service_state(),
            "performance": self.get_performance_metrics(),
            "environment": self.get_environment_config(),
            "health": self.get_health_status(),
        }
        
        return state
    
    def get_metadata(self) -> Dict[str, Any]:
        """Collection metadata"""
        return {
            "collected_at": self.timestamp,
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        }
    
    def get_hardware_state(self) -> Dict[str, Any]:
        """CPU, RAM, and system hardware info"""
        cpu_freq = psutil.cpu_freq()
        
        return {
            "cpu": {
                "model": self._run_command("lscpu | grep 'Model name' | cut -d: -f2").strip(),
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "frequency_mhz": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None,
                },
                "usage_percent": psutil.cpu_percent(interval=1, percpu=True),
                "usage_average": psutil.cpu_percent(interval=1),
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                "percent_used": psutil.virtual_memory().percent,
            },
            "swap": {
                "total_gb": round(psutil.swap_memory().total / (1024**3), 2),
                "used_gb": round(psutil.swap_memory().used / (1024**3), 2),
                "percent_used": psutil.swap_memory().percent,
            },
        }
    
    def get_gpu_state(self) -> Dict[str, Any]:
        """NVIDIA GPU state via nvidia-smi"""
        try:
            # Get detailed GPU info
            query = "index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw,power.limit,clocks.gr,clocks.mem,pcie.link.gen.current,pcie.link.width.current"
            
            result = self._run_command(
                f"nvidia-smi --query-gpu={query} --format=csv,noheader,nounits"
            )
            
            gpus: List[Dict[str, Any]] = []
            for line in result.strip().split('\n'):
                if not line:
                    continue
                    
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 13:
                    gpus.append({
                        "index": int(parts[0]),
                        "name": parts[1],
                        "temperature_c": self._safe_float(parts[2]),
                        "utilization_percent": self._safe_float(parts[3]),
                        "memory_utilization_percent": self._safe_float(parts[4]),
                        "memory_used_mb": self._safe_float(parts[5]),
                        "memory_total_mb": self._safe_float(parts[6]),
                        "power_draw_w": self._safe_float(parts[7]),
                        "power_limit_w": self._safe_float(parts[8]),
                        "clock_graphics_mhz": self._safe_float(parts[9]),
                        "clock_memory_mhz": self._safe_float(parts[10]),
                        "pcie_gen": self._safe_int(parts[11]),
                        "pcie_width": self._safe_int(parts[12]),
                    })
            
            # Get persistence mode
            persistence = self._run_command("nvidia-smi -q -d PERSISTENCE_MODE | grep 'Persistence Mode'")
            
            # Get compute mode
            compute = self._run_command("nvidia-smi -q -d COMPUTE_MODE | grep 'Compute Mode'")
            
            return {
                "gpus": gpus,
                "driver_version": self._run_command("nvidia-smi --query-gpu=driver_version --format=csv,noheader").strip(),
                "cuda_version": self._run_command("nvidia-smi --query-gpu=cuda_version --format=csv,noheader").strip(),
                "persistence_mode": "Enabled" in persistence,
                "compute_mode": compute.split(':')[-1].strip() if compute else "Unknown",
            }
        except Exception as e:
            return {"error": str(e), "available": False}
    
    def get_storage_state(self) -> Dict[str, Any]:
        """Disk usage and mount points"""
        partitions: List[Dict[str, Any]] = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent_used": usage.percent,
                })
            except PermissionError:
                continue
        
        # Disk I/O stats
        io_counters = psutil.disk_io_counters()
        
        return {
            "partitions": partitions,
            "io_stats": {
                "read_count": io_counters.read_count,
                "write_count": io_counters.write_count,
                "read_mb": round(io_counters.read_bytes / (1024**2), 2),
                "write_mb": round(io_counters.write_bytes / (1024**2), 2),
            } if io_counters else None,
        }
    
    def get_network_state(self) -> Dict[str, Any]:
        """Network interfaces, connections, and Tailscale status"""
        interfaces: Dict[str, Any] = {}
        
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info: Dict[str, Any] = {
                "addresses": [],
                "stats": None,
            }
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interface_info["addresses"].append({
                        "type": "ipv4",
                        "address": addr.address,
                        "netmask": addr.netmask,
                    })
                elif addr.family == socket.AF_INET6:
                    interface_info["addresses"].append({
                        "type": "ipv6",
                        "address": addr.address,
                    })
            
            # Get interface stats
            stats = psutil.net_if_stats().get(interface)
            if stats:
                interface_info["stats"] = {
                    "is_up": stats.isup,
                    "speed_mbps": stats.speed,
                    "mtu": stats.mtu,
                }
            
            interfaces[interface] = interface_info
        
        # Tailscale status
        tailscale_status = self._get_tailscale_status()
        
        # Active connections count
        connections = psutil.net_connections()
        
        return {
            "interfaces": interfaces,
            "tailscale": tailscale_status,
            "active_connections": len(connections),
            "connections_by_status": self._count_connections_by_status(connections),
        }
    
    def _get_tailscale_status(self) -> Dict[str, Any]:
        """Get Tailscale network status"""
        try:
            result = self._run_command("tailscale status --json")
            if result:
                return json.loads(result)
        except:
            pass
        
        return {"available": False, "error": "Tailscale not available or not running"}
    
    def _count_connections_by_status(self, connections: List) -> Dict[str, int]:
        """Count connections by status"""
        counts: Dict[str, int] = {}
        for conn in connections:
            status = conn.status
            counts[status] = counts.get(status, 0) + 1
        return counts
    
    def get_docker_state(self) -> Dict[str, Any]:
        """Docker containers, networks, and volumes"""
        try:
            # Container info
            containers_json = self._run_command("docker ps -a --format '{{json .}}'")
            containers: List[Dict[str, Any]] = []
            
            for line in containers_json.strip().split('\n'):
                if line:
                    try:
                        container = json.loads(line)
                        
                        # Get detailed stats
                        container_id = container.get('ID', '')
                        stats = self._get_container_stats(container_id)
                        
                        containers.append({
                            "id": container_id,
                            "name": container.get('Names', ''),
                            "image": container.get('Image', ''),
                            "status": container.get('Status', ''),
                            "state": container.get('State', ''),
                            "ports": container.get('Ports', ''),
                            "stats": stats,
                        })
                    except json.JSONDecodeError:
                        continue
            
            # Network info
            networks = self._run_command("docker network ls --format '{{json .}}'")
            network_list: List[Dict[str, Any]] = []
            for line in networks.strip().split('\n'):
                if line:
                    try:
                        network_list.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            # Volume info
            volumes = self._run_command("docker volume ls --format '{{json .}}'")
            volume_list: List[Dict[str, Any]] = []
            for line in volumes.strip().split('\n'):
                if line:
                    try:
                        volume_list.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            # Docker info
            docker_info = self._run_command("docker info --format '{{json .}}'")
            info: Dict[str, Any] = json.loads(docker_info) if docker_info else {}
            
            return {
                "available": True,
                "containers": containers,
                "container_count": len(containers),
                "running_containers": len([c for c in containers if c['state'] == 'running']),
                "networks": network_list,
                "volumes": volume_list,
                "info": {
                    "server_version": info.get('ServerVersion'),
                    "storage_driver": info.get('Driver'),
                    "total_containers": info.get('Containers'),
                    "images": info.get('Images'),
                },
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _get_env_value(self, key: str) -> Optional[str]:
        value = os.environ.get(key)
        if value:
            return value

        env_path = Path(__file__).resolve().parents[1] / ".env"
        if not env_path.exists():
            return None

        try:
            with env_path.open() as env_file:
                for line in env_file:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    name, raw_value = line.split("=", 1)
                    if name.strip() == key:
                        return raw_value.strip().strip('"').strip("'")
        except OSError:
            return None

        return None

    def _get_chromadb_url(self) -> str:
        host = self._get_env_value("CHROMADB_HOST")
        port = self._get_env_value("CHROMADB_PORT")
        chroma_host = self._get_env_value("CHROMA_HOST")
        scheme = "http"

        if chroma_host:
            parsed = urlparse(chroma_host)
            if parsed.scheme:
                scheme = parsed.scheme
            if parsed.hostname and not host:
                host = parsed.hostname
            if parsed.port and not port:
                port = str(parsed.port)

        if not host:
            host = "localhost"
        if not port:
            port = "8000"

        return f"{scheme}://{host}:{port}/api/v1/heartbeat"
    
    def _get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Get container resource usage stats"""
        try:
            stats_json = self._run_command(
                f"docker stats {container_id} --no-stream --format '{{{{json .}}}}'"
            )
            if stats_json:
                return json.loads(stats_json)
        except:
            pass
        return None
    
    def get_service_state(self) -> Dict[str, Any]:
        """Check status of key services (Ollama, ChromaDB, etc)"""
        services: Dict[str, Any] = {}
        
        # Ollama instances
        ollama_ports = [11434, 11435, 11437]
        for port in ollama_ports:
            service_name = f"ollama_{port}"
            services[service_name] = self._check_http_service(
                f"http://localhost:{port}/api/tags",
                timeout=5
            )
        
        # ChromaDB
        chromadb_url = self._get_chromadb_url()
        services["chromadb"] = self._check_http_service(chromadb_url, timeout=5)
        
        # FAITHH Backend
        services["faithh_backend"] = self._check_http_service(
            "http://localhost:5557/api/status",
            timeout=5
        )
        
        # LangFlow
        services["langflow"] = self._check_http_service(
            "http://localhost:7860",
            timeout=5
        )
        
        return services
    
    def _check_http_service(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        """Check if HTTP service is responding"""
        try:
            response = requests.get(url, timeout=timeout)
            return {
                "available": True,
                "status_code": response.status_code,
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
            }
        except requests.exceptions.ConnectionError:
            return {"available": False, "error": "Connection refused"}
        except requests.exceptions.Timeout:
            return {"available": False, "error": "Timeout"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """System performance metrics"""
        return {
            "uptime_seconds": self._get_uptime(),
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "processes": {
                "total": len(psutil.pids()),
                "top_cpu": self._get_top_processes_by_cpu(5),
                "top_memory": self._get_top_processes_by_memory(5),
            },
        }
    
    def _get_uptime(self) -> int:
        """Get system uptime in seconds"""
        return int(psutil.boot_time())
    
    def _get_top_processes_by_cpu(self, n: int) -> List[Dict[str, Any]]:
        """Get top N processes by CPU usage"""
        processes: List[Dict[str, Any]] = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return processes[:n]
    
    def _get_top_processes_by_memory(self, n: int) -> List[Dict[str, Any]]:
        """Get top N processes by memory usage"""
        processes: List[Dict[str, Any]] = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        return processes[:n]
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Environment configuration and paths"""
        home = Path.home()
        
        return {
            "paths": {
                "home": str(home),
                "ai_stack": str(Path("~/ai-stack").expanduser()),
                "faithh": str(Path("~/faithh").expanduser()) if Path("~/faithh").expanduser().exists() else None,
            },
            "environment_variables": {
                "PATH": os.environ.get("PATH"),
                "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
                "DOCKER_HOST": os.environ.get("DOCKER_HOST"),
            },
            "shell": os.environ.get("SHELL"),
            "user": os.environ.get("USER"),
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Overall system health assessment"""
        issues: List[str] = []
        warnings: List[str] = []
        
        # Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 90:
            issues.append(f"High CPU usage: {cpu_usage}%")
        elif cpu_usage > 75:
            warnings.append(f"Elevated CPU usage: {cpu_usage}%")
        
        # Check memory usage
        mem_percent = psutil.virtual_memory().percent
        if mem_percent > 90:
            issues.append(f"High memory usage: {mem_percent}%")
        elif mem_percent > 75:
            warnings.append(f"Elevated memory usage: {mem_percent}%")
        
        # Check disk usage
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 90:
                    issues.append(f"Disk {partition.mountpoint} nearly full: {usage.percent}%")
                elif usage.percent > 80:
                    warnings.append(f"Disk {partition.mountpoint} filling up: {usage.percent}%")
            except:
                pass
        
        # Check GPU temperatures
        try:
            gpu_temps = self._run_command(
                "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader"
            )
            for idx, temp in enumerate(gpu_temps.strip().split('\n')):
                temp_val = float(temp)
                if temp_val > 85:
                    issues.append(f"GPU {idx} high temperature: {temp_val}°C")
                elif temp_val > 80:
                    warnings.append(f"GPU {idx} elevated temperature: {temp_val}°C")
        except:
            pass
        
        # Overall health score
        health_score = 100
        health_score -= len(issues) * 20
        health_score -= len(warnings) * 5
        health_score = max(0, health_score)
        
        status: str = "healthy"
        if health_score < 50:
            status = "critical"
        elif health_score < 75:
            status = "degraded"
        elif health_score < 95:
            status = "warning"
        
        return {
            "status": status,
            "health_score": health_score,
            "issues": issues,
            "warnings": warnings,
            "checks_performed": datetime.now().isoformat(),
        }
    
    def _run_command(self, command: str) -> str:
        """Run shell command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to int"""
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def save_state(self, state: Dict[str, Any]) -> Path:
        """Save state to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_state_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        # Also save as "latest"
        latest_path = self.output_dir / "system_state_latest.json"
        with open(latest_path, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        return filepath
    
    def generate_summary(self, state: Dict[str, Any]) -> str:
        """Generate human-readable summary"""
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("SYSTEM STATE SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Collected: {state['metadata']['collected_at']}")
        lines.append(f"Hostname: {state['metadata']['hostname']}")
        lines.append("")
        
        # Hardware
        lines.append("HARDWARE:")
        hw = state['hardware']
        lines.append(f"  CPU: {hw['cpu']['cores_physical']}C/{hw['cpu']['cores_logical']}T @ {hw['cpu']['usage_average']}%")
        lines.append(f"  RAM: {hw['memory']['used_gb']:.1f}GB / {hw['memory']['total_gb']:.1f}GB ({hw['memory']['percent_used']:.1f}%)")
        
        # GPU
        if state['gpu'].get('available', True):
            lines.append("  GPUs:")
            for gpu in state['gpu']['gpus']:
                lines.append(f"    [{gpu['index']}] {gpu['name']}")
                lines.append(f"        Temp: {gpu['temperature_c']}°C | Util: {gpu['utilization_percent']}% | VRAM: {gpu['memory_used_mb']:.0f}MB/{gpu['memory_total_mb']:.0f}MB")
                lines.append(f"        Power: {gpu['power_draw_w']:.1f}W / {gpu['power_limit_w']:.1f}W")
        
        lines.append("")
        
        # Docker
        lines.append("DOCKER:")
        docker = state['docker']
        if docker.get('available'):
            lines.append(f"  Containers: {docker['running_containers']}/{docker['container_count']} running")
            for container in docker['containers'][:5]:  # Show first 5
                status_emoji = "✓" if container['state'] == 'running' else "✗"
                lines.append(f"    {status_emoji} {container['name']}: {container['status']}")
        
        lines.append("")
        
        # Services
        lines.append("SERVICES:")
        for service_name, status in state['services'].items():
            emoji = "✓" if status.get('available') else "✗"
            detail = f"({status.get('response_time_ms')}ms)" if status.get('response_time_ms') else ""
            lines.append(f"  {emoji} {service_name} {detail}")
        
        lines.append("")
        
        # Health
        lines.append("HEALTH:")
        health = state['health']
        lines.append(f"  Status: {health['status'].upper()} (Score: {health['health_score']}/100)")
        if health['issues']:
            lines.append("  Issues:")
            for issue in health['issues']:
                lines.append(f"    - {issue}")
        if health['warnings']:
            lines.append("  Warnings:")
            for warning in health['warnings']:
                lines.append(f"    - {warning}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def main() -> None:
    import sys
    
    print("🤖 System State Collector v1.0")
    print("=" * 60)
    
    # Check for dependencies
    if psutil is None or requests is None:
        print(f"❌ Missing dependency: {_IMPORT_ERROR}")
        print("Install with: pip install psutil requests")
        sys.exit(1)
    
    # Collect state
    collector = SystemStateCollector()
    state = collector.collect_all()
    
    # Save to file
    filepath = collector.save_state(state)
    print(f"\n✅ State saved to: {filepath}")
    
    # Print summary
    summary = collector.generate_summary(state)
    print("\n" + summary)
    
    print(f"\n📄 Full details: {filepath}")
    print(f"📄 Latest snapshot: {collector.output_dir}/system_state_latest.json")


if __name__ == "__main__":
    main()
