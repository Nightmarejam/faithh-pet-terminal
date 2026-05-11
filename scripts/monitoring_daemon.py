#!/usr/bin/env python3
"""
Continuous System Monitoring Daemon
Watches system state and updates parity files automatically

Save to: ~/ai-stack/scripts/monitor_daemon.py
Run as service: systemctl start ai-monitor
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import threading
import signal
import sys

# Import the state collector
sys.path.insert(0, str(Path(__file__).parent))
from collect_system_state import SystemStateCollector

# Import ML learning framework for health checks
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.ml_learning_framework import MLLearningFramework

class MonitoringDaemon:
    def __init__(
        self,
        check_interval: int = 60,  # seconds
        parity_dir: str = "~/ai-stack/parity",
        log_dir: str = "~/ai-stack/logs"
    ):
        self.check_interval = check_interval
        self.parity_dir = Path(parity_dir).expanduser()
        self.log_dir = Path(log_dir).expanduser()
        
        # Create directories
        self.parity_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_file = self.log_dir / f"monitor_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # State tracking
        self.running = False
        self.collector = SystemStateCollector(output_dir=str(self.parity_dir))
        self.last_state = None
        self.state_history = []
        self.max_history = 100  # Keep last 100 states
        
        # ML Learning Framework for health checks
        self.ml_framework = MLLearningFramework()
        
        # Alert thresholds
        self.thresholds = {
            "cpu_percent": 90,
            "memory_percent": 90,
            "disk_percent": 90,
            "gpu_temp_c": 85,
            "gpu_memory_percent": 95,
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the monitoring daemon"""
        self.running = True
        self.logger.info("🚀 Monitoring daemon started")
        self.logger.info(f"Check interval: {self.check_interval}s")
        self.logger.info(f"Parity directory: {self.parity_dir}")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        analysis_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the monitoring daemon"""
        self.running = False
        self.logger.info("🛑 Monitoring daemon stopped")
        
        # Save final state
        if self.last_state:
            self._save_shutdown_state()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect current state
                state = self.collector.collect_all()
                
                # Update last state
                self.last_state = state
                
                # Add to history
                self.state_history.append(state)
                if len(self.state_history) > self.max_history:
                    self.state_history.pop(0)
                
                # Check for issues
                system_alerts = self._check_thresholds(state)
                ml_alerts = self._check_ml_learning_health()
                
                # Combine alerts
                all_alerts = system_alerts + ml_alerts
                
                # Update parity files
                self._update_parity_files(state)
                
                # Log summary
                health = state['health']
                ml_issues = len(ml_alerts)
                total_issues = len(health['issues']) + ml_issues
                
                self.logger.info(
                    f"Health: {health['status']} ({health['health_score']}/100) | "
                    f"CPU: {state['hardware']['cpu']['usage_average']:.1f}% | "
                    f"RAM: {state['hardware']['memory']['percent_used']:.1f}% | "
                    f"Issues: {total_issues} (system: {len(health['issues'])}, ml: {ml_issues})"
                )
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
            
            # Sleep until next check
            time.sleep(self.check_interval)
    
    def _analysis_loop(self):
        """Analyze trends and patterns"""
        while self.running:
            try:
                # Run analysis every 5 minutes
                time.sleep(300)
                
                if len(self.state_history) < 5:
                    continue
                
                # Analyze trends
                trends = self._analyze_trends()
                
                # Save trends
                trends_file = self.parity_dir / "system_trends.json"
                with open(trends_file, 'w') as f:
                    json.dump(trends, f, indent=2, default=str)
                
                # Log interesting findings
                if trends.get('alerts'):
                    for alert in trends['alerts']:
                        self.logger.warning(f"Trend alert: {alert}")
                
            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}", exc_info=True)
    
    def _check_thresholds(self, state: Dict[str, Any]):
        """Check if any thresholds are exceeded"""
        alerts = []
        
        # CPU check
        cpu_usage = state['hardware']['cpu']['usage_average']
        if cpu_usage > self.thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {cpu_usage:.1f}%")
        
        # Memory check
        mem_usage = state['hardware']['memory']['percent_used']
        if mem_usage > self.thresholds['memory_percent']:
            alerts.append(f"High memory usage: {mem_usage:.1f}%")
        
        # Disk check
        for partition in state['storage']['partitions']:
            if partition['percent_used'] > self.thresholds['disk_percent']:
                alerts.append(
                    f"High disk usage on {partition['mountpoint']}: "
                    f"{partition['percent_used']:.1f}%"
                )
        
        # GPU checks
        if state['gpu'].get('available', True):
            for gpu in state['gpu']['gpus']:
                if gpu['temperature_c'] and gpu['temperature_c'] > self.thresholds['gpu_temp_c']:
                    alerts.append(
                        f"GPU {gpu['index']} high temperature: {gpu['temperature_c']}°C"
                    )
                
                mem_percent = (gpu['memory_used_mb'] / gpu['memory_total_mb'] * 100)
                if mem_percent > self.thresholds['gpu_memory_percent']:
                    alerts.append(
                        f"GPU {gpu['index']} high memory usage: {mem_percent:.1f}%"
                    )
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"⚠️  {alert}")
        
        return alerts
    
    def _check_ml_learning_health(self) -> List[str]:
        """Check ML learning framework health"""
        alerts = []
        
        try:
            # Check learning nodes
            total_nodes = len(self.ml_framework.nodes)
            if total_nodes == 0:
                alerts.append("No ML learning nodes found")
                return alerts
            
            # Check for stale nodes (no updates in last 24 hours)
            stale_threshold = datetime.now() - timedelta(hours=24)
            stale_nodes = []
            
            for node_id, node in self.ml_framework.nodes.items():
                if node.last_updated < stale_threshold:
                    stale_nodes.append(node_id)
            
            if stale_nodes:
                alerts.append(f"Stale learning nodes: {len(stale_nodes)} (no updates >24h)")
            
            # Check for nodes with poor performance
            poor_performance_nodes = []
            for node_id, node in self.ml_framework.nodes.items():
                if node.performance_metrics:
                    avg_performance = sum(node.performance_metrics.values()) / len(node.performance_metrics)
                    if avg_performance < 0.3:  # Less than 30% average performance
                        poor_performance_nodes.append(node_id)
            
            if poor_performance_nodes:
                alerts.append(f"Poor performance nodes: {len(poor_performance_nodes)} (avg <30%)")
            
            # Check learning activity (nodes updated in last hour)
            active_threshold = datetime.now() - timedelta(hours=1)
            active_nodes = sum(1 for node in self.ml_framework.nodes.values() 
                             if node.last_updated > active_threshold)
            
            if active_nodes == 0 and total_nodes > 0:
                alerts.append("No active learning (no updates >1h)")
            
            # Log ML learning status
            self.logger.info(
                f"ML Learning: {total_nodes} nodes, {active_nodes} active, "
                f"{len(stale_nodes)} stale, {len(poor_performance_nodes)} poor"
            )
            
        except Exception as e:
            alerts.append(f"ML learning health check failed: {str(e)}")
            self.logger.error(f"Error checking ML learning health: {e}", exc_info=True)
        
        return alerts
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze historical data for trends"""
        if len(self.state_history) < 5:
            return {"error": "Insufficient data"}
        
        # Get recent states (last 30 minutes)
        recent_states = self.state_history[-30:]
        
        # CPU trend
        cpu_values = [s['hardware']['cpu']['usage_average'] for s in recent_states]
        cpu_trend = self._calculate_trend(cpu_values)
        
        # Memory trend
        mem_values = [s['hardware']['memory']['percent_used'] for s in recent_states]
        mem_trend = self._calculate_trend(mem_values)
        
        # GPU temperature trends
        gpu_temps = {}
        if recent_states[0]['gpu'].get('available', True):
            for gpu_idx in range(len(recent_states[0]['gpu']['gpus'])):
                temps = [
                    s['gpu']['gpus'][gpu_idx]['temperature_c']
                    for s in recent_states
                    if s['gpu']['gpus'][gpu_idx]['temperature_c']
                ]
                gpu_temps[f"gpu_{gpu_idx}"] = self._calculate_trend(temps)
        
        # Service availability
        service_uptime = {}
        for service_name in recent_states[0]['services'].keys():
            available_count = sum(
                1 for s in recent_states
                if s['services'][service_name].get('available', False)
            )
            uptime_percent = (available_count / len(recent_states)) * 100
            service_uptime[service_name] = uptime_percent
        
        # Generate alerts
        alerts = []
        if cpu_trend == "increasing" and cpu_values[-1] > 80:
            alerts.append("CPU usage trending up and high")
        if mem_trend == "increasing" and mem_values[-1] > 80:
            alerts.append("Memory usage trending up and high")
        
        for service, uptime in service_uptime.items():
            if uptime < 95:
                alerts.append(f"{service} uptime low: {uptime:.1f}%")
        
        return {
            "analyzed_at": datetime.now().isoformat(),
            "samples": len(recent_states),
            "cpu_trend": {
                "direction": cpu_trend,
                "current": cpu_values[-1],
                "average": sum(cpu_values) / len(cpu_values),
                "min": min(cpu_values),
                "max": max(cpu_values),
            },
            "memory_trend": {
                "direction": mem_trend,
                "current": mem_values[-1],
                "average": sum(mem_values) / len(mem_values),
                "min": min(mem_values),
                "max": max(mem_values),
            },
            "gpu_temperature_trends": gpu_temps,
            "service_uptime": service_uptime,
            "alerts": alerts,
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate if trend is increasing, decreasing, or stable"""
        if len(values) < 3:
            return "unknown"
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # Classify trend
        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _update_parity_files(self, state: Dict[str, Any]):
        """Update parity files with current state"""
        
        # 1. Update live_status.json (minimal, for quick reads)
        live_status = {
            "last_updated": state['metadata']['collected_at'],
            "health": state['health']['status'],
            "health_score": state['health']['health_score'],
            "cpu_percent": state['hardware']['cpu']['usage_average'],
            "memory_percent": state['hardware']['memory']['percent_used'],
            "gpus": [
                {
                    "index": gpu['index'],
                    "name": gpu['name'],
                    "temp_c": gpu['temperature_c'],
                    "util_percent": gpu['utilization_percent'],
                    "vram_used_mb": gpu['memory_used_mb'],
                    "vram_total_mb": gpu['memory_total_mb'],
                }
                for gpu in state['gpu'].get('gpus', [])
            ],
            "services": {
                name: status.get('available', False)
                for name, status in state['services'].items()
            },
            "containers_running": state['docker'].get('running_containers', 0),
        }
        
        live_file = self.parity_dir / "live_status.json"
        with open(live_file, 'w') as f:
            json.dump(live_status, f, indent=2)
        
        # 2. Update hardware_config.json (static config, update less frequently)
        # Only update if file doesn't exist or it's been > 1 hour
        hw_config_file = self.parity_dir / "hardware_config.json"
        should_update_hw = True
        
        if hw_config_file.exists():
            with open(hw_config_file, 'r') as f:
                old_config = json.load(f)
                last_update = datetime.fromisoformat(old_config.get('last_updated', '2000-01-01'))
                if datetime.now() - last_update < timedelta(hours=1):
                    should_update_hw = False
        
        if should_update_hw:
            hw_config = {
                "last_updated": datetime.now().isoformat(),
                "cpu": state['hardware']['cpu'],
                "memory_total_gb": state['hardware']['memory']['total_gb'],
                "gpus": [
                    {
                        "index": gpu['index'],
                        "name": gpu['name'],
                        "memory_total_mb": gpu['memory_total_mb'],
                        "pcie_gen": gpu['pcie_gen'],
                        "pcie_width": gpu['pcie_width'],
                    }
                    for gpu in state['gpu'].get('gpus', [])
                ],
                "storage": state['storage']['partitions'],
                "network_interfaces": list(state['network']['interfaces'].keys()),
            }
            
            with open(hw_config_file, 'w') as f:
                json.dump(hw_config, f, indent=2)
        
        # 3. Update docker_state.json
        docker_state_file = self.parity_dir / "docker_state.json"
        with open(docker_state_file, 'w') as f:
            json.dump(state['docker'], f, indent=2, default=str)
        
        # 4. Create AI-readable summary
        ai_summary = self._create_ai_summary(state)
        ai_summary_file = self.parity_dir / "ai_readable_summary.md"
        with open(ai_summary_file, 'w') as f:
            f.write(ai_summary)
    
    def _create_ai_summary(self, state: Dict[str, Any]) -> str:
        """Create a concise, AI-readable summary"""
        lines = []
        
        lines.append("# System State Summary for AI Analysis")
        lines.append(f"**Generated:** {state['metadata']['collected_at']}")
        lines.append(f"**Host:** {state['metadata']['hostname']}")
        lines.append("")
        
        lines.append("## Quick Status")
        health = state['health']
        lines.append(f"- **Overall Health:** {health['status'].upper()} (Score: {health['health_score']}/100)")
        lines.append(f"- **Active Issues:** {len(health['issues'])}")
        lines.append(f"- **Warnings:** {len(health['warnings'])}")
        lines.append("")
        
        lines.append("## Resource Usage")
        hw = state['hardware']
        lines.append(f"- **CPU:** {hw['cpu']['usage_average']:.1f}% ({hw['cpu']['cores_physical']}C/{hw['cpu']['cores_logical']}T)")
        lines.append(f"- **RAM:** {hw['memory']['used_gb']:.1f}GB / {hw['memory']['total_gb']:.1f}GB ({hw['memory']['percent_used']:.1f}%)")
        
        if state['gpu'].get('available', True):
            lines.append(f"- **GPUs:** {len(state['gpu']['gpus'])} available")
            for gpu in state['gpu']['gpus']:
                lines.append(
                    f"  - GPU {gpu['index']} ({gpu['name']}): "
                    f"{gpu['temperature_c']}°C, "
                    f"{gpu['utilization_percent']}% util, "
                    f"{gpu['memory_used_mb']:.0f}MB/{gpu['memory_total_mb']:.0f}MB VRAM"
                )
        lines.append("")
        
        lines.append("## Services")
        all_up = all(s.get('available', False) for s in state['services'].values())
        lines.append(f"- **All Services:** {'✓ UP' if all_up else '✗ DEGRADED'}")
        for service, status in state['services'].items():
            emoji = "✓" if status.get('available') else "✗"
            lines.append(f"  - {emoji} {service}")
        lines.append("")
        
        lines.append("## Docker")
        docker = state['docker']
        if docker.get('available'):
            lines.append(f"- **Containers:** {docker['running_containers']}/{docker['container_count']} running")
            for container in docker['containers']:
                if container['state'] == 'running':
                    lines.append(f"  - ✓ {container['name']}")
        lines.append("")
        
        if health['issues']:
            lines.append("## Active Issues")
            for issue in health['issues']:
                lines.append(f"- ⚠️ {issue}")
            lines.append("")
        
        if health['warnings']:
            lines.append("## Warnings")
            for warning in health['warnings']:
                lines.append(f"- ⚠ {warning}")
            lines.append("")
        
        lines.append("---")
        lines.append("*This summary is automatically generated and updated every minute.*")
        
        return "\n".join(lines)
    
    def _save_shutdown_state(self):
        """Save final state on shutdown"""
        shutdown_file = self.parity_dir / "last_shutdown_state.json"
        with open(shutdown_file, 'w') as f:
            json.dump(self.last_state, f, indent=2, default=str)
        
        self.logger.info(f"Saved shutdown state to {shutdown_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="System Monitoring Daemon")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--parity-dir",
        type=str,
        default="~/ai-stack/parity",
        help="Directory for parity files (default: ~/ai-stack/parity)"
    )
    
    args = parser.parse_args()
    
    daemon = MonitoringDaemon(
        check_interval=args.interval,
        parity_dir=args.parity_dir
    )
    
    daemon.start()


if __name__ == "__main__":
    main()
