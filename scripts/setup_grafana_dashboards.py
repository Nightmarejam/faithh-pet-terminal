#!/usr/bin/env python3
"""
Set up Grafana dashboards for Gen8 monitoring
"""

import json
import requests
import time

# Configuration
GRAFANA_URL = "http://192.158.1.243:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin123"

def create_datasource():
    """Create Prometheus datasource"""
    datasource = {
        "name": "Prometheus-Gen8",
        "type": "prometheus",
        "access": "proxy",
        "url": "http://prometheus:9090",
        "isDefault": True,
        "basicAuth": False,
        "jsonData": {
            "httpMethod": "POST"
        }
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/datasources",
        json=datasource,
        auth=(GRAFANA_USER, GRAFANA_PASS),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✅ Prometheus datasource created")
        return True
    else:
        print(f"❌ Failed to create datasource: {response.text}")
        return False

def create_system_dashboard():
    """Create system overview dashboard"""
    dashboard = {
        "dashboard": {
            "id": None,
            "title": "Gen8 System Overview",
            "tags": ["gen8", "system"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "CPU Usage",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "100 * (1 - avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])))",
                            "legendFormat": "{{instance}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": 0},
                                    {"color": "yellow", "value": 70},
                                    {"color": "red", "value": 90}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Memory Usage",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))",
                            "legendFormat": "Memory Usage"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": 0},
                                    {"color": "yellow", "value": 70},
                                    {"color": "red", "value": 90}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Disk Usage",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "100 * (1 - (node_filesystem_avail_bytes{fstype!=\"tmpfs\"} / node_filesystem_size_bytes{fstype!=\"tmpfs\"}))",
                            "legendFormat": "{{mountpoint}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": 0},
                                    {"color": "yellow", "value": 80},
                                    {"color": "red", "value": 95}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                },
                {
                    "id": 4,
                    "title": "Network Traffic",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(node_network_receive_bytes_total[5m]) * 8",
                            "legendFormat": "RX {{device}}"
                        },
                        {
                            "expr": "rate(node_network_transmit_bytes_total[5m]) * 8",
                            "legendFormat": "TX {{device}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "bps"
                        }
                    },
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
                },
                {
                    "id": 5,
                    "title": "System Load",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "node_load1",
                            "legendFormat": "1m"
                        },
                        {
                            "expr": "node_load5",
                            "legendFormat": "5m"
                        },
                        {
                            "expr": "node_load15",
                            "legendFormat": "15m"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 24}
                },
                {
                    "id": 6,
                    "title": "Uptime",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "node_time_seconds - node_boot_time_seconds",
                            "legendFormat": "Uptime"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "s"
                        }
                    },
                    "gridPos": {"h": 4, "w": 12, "x": 12, "y": 24}
                }
            ],
            "time": {"from": "now-1h", "to": "now"},
            "refresh": "5s"
        }
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        json=dashboard,
        auth=(GRAFANA_USER, GRAFANA_PASS),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ System dashboard created: {data['id']}")
        return data['id']
    else:
        print(f"❌ Failed to create dashboard: {response.text}")
        return None

def create_docker_dashboard():
    """Create Docker monitoring dashboard"""
    dashboard = {
        "dashboard": {
            "id": None,
            "title": "Docker Services - Gen8",
            "tags": ["gen8", "docker"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Running Containers",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "count(container_last_seen)",
                            "legendFormat": "Containers"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Container CPU Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(container_cpu_usage_seconds_total{name!=\"\"}[5m]) * 100",
                            "legendFormat": "{{name}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent"
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Container Memory Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "container_memory_usage_bytes{name!=\"\"} / 1024 / 1024",
                            "legendFormat": "{{name}}"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "MB"
                        }
                    },
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                }
            ],
            "time": {"from": "now-1h", "to": "now"},
            "refresh": "5s"
        }
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        json=dashboard,
        auth=(GRAFANA_USER, GRAFANA_PASS),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Docker dashboard created: {data['id']}")
        return data['id']
    else:
        print(f"❌ Failed to create dashboard: {response.text}")
        return None

def main():
    print("📊 Setting up Grafana Dashboards")
    print("==============================")
    
    # Wait for Grafana to be ready
    print("⏳ Checking Grafana availability...")
    for i in range(10):
        try:
            response = requests.get(f"{GRAFANA_URL}/api/health", auth=(GRAFANA_USER, GRAFANA_PASS))
            if response.status_code == 200:
                print("✅ Grafana is ready")
                break
        except:
            pass
        time.sleep(2)
    else:
        print("❌ Grafana not ready")
        return
    
    # Create datasource
    if not create_datasource():
        return
    
    # Create dashboards
    system_id = create_system_dashboard()
    docker_id = create_docker_dashboard()
    
    print("\n✅ Dashboard Setup Complete!")
    print(f"🔗 Grafana: {GRAFANA_URL}")
    print(f"   User: {GRAFANA_USER}")
    print(f"   Password: {GRAFANA_PASS}")
    print("\n📊 Dashboards created:")
    if system_id:
        print(f"   System Overview: {GRAFANA_URL}/d/{system_id}")
    if docker_id:
        print(f"   Docker Services: {GRAFANA_URL}/d/{docker_id}")

if __name__ == "__main__":
    main()
