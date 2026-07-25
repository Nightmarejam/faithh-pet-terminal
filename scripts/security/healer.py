#!/usr/bin/env python3
"""
Pulse Self-Healer - Automatic service recovery for FAITHH

Monitors services and automatically restarts them when unhealthy.
Defaults to dry-run unless invoked otherwise via API/CLI.
"""
from __future__ import annotations

import subprocess
import requests
import time
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ServiceConfig:
    """Configuration for a monitored service."""
    name: str
    health_url: str
    health_timeout: int = 5
    restart_command: Optional[str] = None
    max_restarts: int = 3
    restart_cooldown: int = 60  # seconds between restart attempts


@dataclass
class HealingAction:
    """Record of a healing action taken."""
    timestamp: str
    service: str
    action: str  # "restart", "alert", "escalate", "wait", "restart_dry_run", "error"
    success: bool
    details: str


class PulseSelfHealer:
    """Self-healing system for FAITHH infrastructure."""

    DEFAULT_SERVICES: Dict[str, ServiceConfig] = {
        "faithh_backend": ServiceConfig(
            name="faithh_backend",
            health_url="http://localhost:5557/health",
            restart_command="cd /home/jonat/ai-stack && ./restart_backend.sh",
            max_restarts=3,
        ),
        "ollama": ServiceConfig(
            name="ollama",
            health_url="http://localhost:11434/api/tags",
            restart_command="sudo systemctl restart ollama",
            max_restarts=3,
        ),
        "chromadb": ServiceConfig(
            name="chromadb",
            health_url="http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat",
            restart_command=None,  # remote - no local restart
            max_restarts=0,
        ),
    }

    def __init__(
        self,
        services: Dict[str, ServiceConfig] | None = None,
        log_file: str | None = None,
        dry_run: bool = False,
    ):
        self.services = services or self.DEFAULT_SERVICES
        self.log_file = log_file or "/home/jonat/ai-stack/logs/healer.log"
        self.dry_run = dry_run
        self.restart_counts: Dict[str, int] = {}
        self.last_restart: Dict[str, float] = {}
        self.history: List[HealingAction] = []

    def check_service(self, name: str) -> Dict:
        if name not in self.services:
            return {"status": "unknown", "error": f"Service {name} not configured"}
        config = self.services[name]
        try:
            start = time.time()
            response = requests.get(config.health_url, timeout=config.health_timeout)
            response_time = int((time.time() - start) * 1000)
            if response.status_code == 200:
                return {"status": "healthy", "response_time_ms": response_time, "error": None}
            return {"status": "unhealthy", "response_time_ms": response_time, "error": f"HTTP {response.status_code}"}
        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "Connection timed out"}
        except requests.exceptions.ConnectionError:
            return {"status": "unreachable", "error": "Connection refused"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_all_services(self) -> Dict[str, Dict]:
        return {name: self.check_service(name) for name in self.services}

    def heal_service(self, name: str) -> HealingAction:
        if name not in self.services:
            return HealingAction(datetime.utcnow().isoformat() + "Z", name, "error", False, f"Service {name} not configured")
        config = self.services[name]

        if not config.restart_command:
            action = HealingAction(datetime.utcnow().isoformat() + "Z", name, "alert", True, "No restart command configured - alerting only")
            self._record(action)
            return action

        count = self.restart_counts.get(name, 0)
        if count >= config.max_restarts:
            action = HealingAction(datetime.utcnow().isoformat() + "Z", name, "escalate", False, f"Max restarts ({config.max_restarts}) exceeded - needs manual intervention")
            self._record(action)
            return action

        last = self.last_restart.get(name, 0)
        elapsed = time.time() - last
        if elapsed < config.restart_cooldown:
            action = HealingAction(datetime.utcnow().isoformat() + "Z", name, "wait", True, f"In cooldown - {int(config.restart_cooldown - elapsed)}s remaining")
            self._record(action)
            return action

        if self.dry_run:
            action = HealingAction(datetime.utcnow().isoformat() + "Z", name, "restart_dry_run", True, f"Would run: {config.restart_command}")
        else:
            try:
                result = subprocess.run(
                    config.restart_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                success = result.returncode == 0
                action = HealingAction(
                    datetime.utcnow().isoformat() + "Z",
                    name,
                    "restart",
                    success,
                    result.stdout if success else result.stderr,
                )
                self.restart_counts[name] = count + 1
                self.last_restart[name] = time.time()
            except subprocess.TimeoutExpired:
                action = HealingAction(datetime.utcnow().isoformat() + "Z", name, "restart", False, "Restart command timed out")
            except Exception as e:
                action = HealingAction(datetime.utcnow().isoformat() + "Z", name, "restart", False, str(e))

        self._record(action)
        return action

    def run_healing_cycle(self) -> List[HealingAction]:
        actions: List[HealingAction] = []
        health = self.check_all_services()
        for name, status in health.items():
            if status.get("status") not in ["healthy"]:
                actions.append(self.heal_service(name))
        return actions

    def reset_restart_counts(self, service: str | None = None):
        if service:
            self.restart_counts[service] = 0
        else:
            self.restart_counts = {}

    def _record(self, action: HealingAction):
        self.history.append(action)
        self._log_action(action)

    def _log_action(self, action: HealingAction):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        log_entry = {
            "timestamp": action.timestamp,
            "event": "healing_action",
            "service": action.service,
            "action": action.action,
            "success": action.success,
            "details": action.details,
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_status_summary(self) -> Dict:
        health = self.check_all_services()
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": health,
            "restart_counts": dict(self.restart_counts),
            "recent_actions": [
                {
                    "timestamp": a.timestamp,
                    "service": a.service,
                    "action": a.action,
                    "success": a.success,
                }
                for a in self.history[-10:]
            ],
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pulse Self-Healer")
    parser.add_argument("--check", action="store_true", help="Check all services")
    parser.add_argument("--heal", action="store_true", help="Run healing cycle")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually restart")
    parser.add_argument("--reset", type=str, help="Reset restart count for service")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    healer = PulseSelfHealer(dry_run=args.dry_run)

    if args.reset:
        healer.reset_restart_counts(args.reset)
        print(f"Reset restart count for {args.reset}")
    elif args.heal:
        actions = healer.run_healing_cycle()
        if args.json:
            print(json.dumps([
                {"service": a.service, "action": a.action, "success": a.success, "details": a.details}
                for a in actions
            ], indent=2))
        else:
            print("=== Healing Cycle Results ===")
            if not actions:
                print("✅ All services healthy - no healing needed")
            for action in actions:
                status = "✅" if action.success else "❌"
                print(f"{status} {action.service}: {action.action}")
                print(f"   {action.details}")
    else:
        health = healer.check_all_services()
        if args.json:
            print(json.dumps(health, indent=2))
        else:
            print("=== Service Health Check ===")
            for name, status in health.items():
                icon = "✅" if status.get("status") == "healthy" else "❌"
                print(f"{icon} {name}: {status.get('status')}")
                if status.get("error"):
                    print(f"   Error: {status['error']}")
                if status.get("response_time_ms"):
                    print(f"   Response: {status['response_time_ms']}ms")
