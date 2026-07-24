#!/usr/bin/env python3
"""
Set up basic monitoring alerts in Prometheus
"""

import yaml
import requests

# Configuration
PROMETHEUS_URL = "http://servicebox.taileb8c60.ts.net:9090"

def create_alert_rules():
    """Create alert rules for Gen8 monitoring"""
    
    alert_rules = {
        "groups": [
            {
                "name": "gen8_system_alerts",
                "rules": [
                    {
                        "alert": "HighCPUUsage",
                        "expr": "100 * (1 - avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m]))) > 80",
                        "for": "5m",
                        "labels": {
                            "severity": "warning"
                        },
                        "annotations": {
                            "summary": "High CPU usage on {{ $labels.instance }}",
                            "description": "CPU usage is {{ $value }}% for more than 5 minutes"
                        }
                    },
                    {
                        "alert": "HighMemoryUsage",
                        "expr": "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 85",
                        "for": "5m",
                        "labels": {
                            "severity": "warning"
                        },
                        "annotations": {
                            "summary": "High memory usage on {{ $labels.instance }}",
                            "description": "Memory usage is {{ $value }}% for more than 5 minutes"
                        }
                    },
                    {
                        "alert": "DiskSpaceLow",
                        "expr": "100 * (1 - (node_filesystem_avail_bytes{fstype!=\"tmpfs\"} / node_filesystem_size_bytes{fstype!=\"tmpfs\"})) > 90",
                        "for": "10m",
                        "labels": {
                            "severity": "critical"
                        },
                        "annotations": {
                            "summary": "Low disk space on {{ $labels.instance }}",
                            "description": "Disk {{ $labels.mountpoint }} is {{ $value }}% full"
                        }
                    },
                    {
                        "alert": "NodeDown",
                        "expr": "up{job=\"node-exporter\"} == 0",
                        "for": "1m",
                        "labels": {
                            "severity": "critical"
                        },
                        "annotations": {
                            "summary": "Node {{ $labels.instance }} is down",
                            "description": "Node has been down for more than 1 minute"
                        }
                    },
                    {
                        "alert": "ChromaDBDown",
                        "expr": "up{job=\"chromadb\"} == 0",
                        "for": "2m",
                        "labels": {
                            "severity": "critical"
                        },
                        "annotations": {
                            "summary": "ChromaDB is down",
                            "description": "ChromaDB has been down for more than 2 minutes"
                        }
                    }
                ]
            }
        ]
    }
    
    return yaml.dump(alert_rules, default_style=False)

def main():
    print("🚨 Setting up Monitoring Alerts")
    print("==============================")
    
    # Create alert rules file
    rules_yaml = create_alert_rules()
    
    # Save rules file
    with open("/tmp/gen8_alerts.yml", "w") as f:
        f.write(rules_yaml)
    
    print("📝 Alert rules created:")
    print(rules_yaml)
    
    # Note: In a real setup, you'd reload Prometheus
    # For now, just show what would be configured
    
    print("\n✅ Alert Rules Ready!")
    print("\n📋 Alerts configured:")
    print("  - High CPU Usage (>80%)")
    print("  - High Memory Usage (>85%)")
    print("  - Low Disk Space (>90%)")
    print("  - Node Down")
    print("  - ChromaDB Down")
    print("\n🔧 To apply these rules:")
    print("  1. Copy /tmp/gen8_alerts.yml to Gen8")
    print("  2. Add to prometheus.yml configuration")
    print("  3. Reload Prometheus")
    
    # Copy to Gen8
    import subprocess
    result = subprocess.run(
        ["scp", "/tmp/gen8_alerts.yml", "jonat@servicebox.taileb8c60.ts.net:/home/jonat/services/monitoring/"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("\n✅ Alert rules copied to Gen8")
    else:
        print(f"\n❌ Failed to copy rules: {result.stderr}")

if __name__ == "__main__":
    main()
