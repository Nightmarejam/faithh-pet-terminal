#!/usr/bin/env python3
"""
Pulse Audit Logger - Structured logging of all AI actions.

Logs JSON-L lines for easy parsing. Rotates daily by filename.
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class AuditEvent:
    """A single audit log entry."""
    event_id: str
    timestamp: str
    event_type: str  # chat, rag_search, file_access, tool_use, security, healing
    actor: str       # user, faithh, ollama, system, pulse
    action: str
    resource: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    success: bool = True
    session_id: Optional[str] = None
    risk_level: str = "low"  # low, medium, high, critical


class PulseAuditLogger:
    """Structured audit logging for FAITHH."""

    def __init__(self, log_dir: str | None = None, session_id: str | None = None):
        self.log_dir = Path(log_dir or "/home/jonat/ai-stack/logs/audit")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self._current_date: str | None = None
        self._log_file: Path | None = None

    def _get_log_file(self) -> Path:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if today != self._current_date:
            self._current_date = today
            self._log_file = self.log_dir / f"audit_{today}.jsonl"
        return self._log_file  # type: ignore

    def log(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource: str | None = None,
        details: Dict[str, Any] | None = None,
        success: bool = True,
        risk_level: str = "low",
    ) -> AuditEvent:
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            actor=actor,
            action=action,
            resource=resource,
            details=details,
            success=success,
            session_id=self.session_id,
            risk_level=risk_level,
        )
        self._write_event(event)
        return event

    def log_chat(self, message_preview: str, model: str, use_rag: bool, response_time_ms: int, success: bool = True):
        return self.log(
            event_type="chat",
            actor="user",
            action="send_message",
            details={
                "message_preview": message_preview[:100],
                "model": model,
                "use_rag": use_rag,
                "response_time_ms": response_time_ms,
            },
            success=success,
        )

    def log_rag_search(self, query_preview: str, results_count: int, search_time_ms: int):
        return self.log(
            event_type="rag_search",
            actor="faithh",
            action="search_knowledge_base",
            resource="chromadb",
            details={
                "query_preview": query_preview[:100],
                "results_count": results_count,
                "search_time_ms": search_time_ms,
            },
        )

    def log_security_event(self, threat_type: str, blocked: bool, risk_score: float, details: Dict[str, Any] | None = None):
        return self.log(
            event_type="security",
            actor="pulse",
            action="threat_detected" if blocked else "threat_monitored",
            details={
                "threat_type": threat_type,
                "blocked": blocked,
                "risk_score": risk_score,
                **(details or {}),
            },
            success=blocked,
            risk_level="high" if blocked else "medium",
        )

    def log_healing_action(self, service: str, action: str, success: bool, details: str):
        return self.log(
            event_type="healing",
            actor="pulse",
            action=action,
            resource=service,
            details={"message": details},
            success=success,
            risk_level="medium" if not success else "low",
        )

    def _write_event(self, event: AuditEvent):
        log_file = self._get_log_file()
        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(event)) + "\n")

    def query_recent(self, limit: int = 100, event_type: str | None = None, actor: str | None = None, since: str | None = None) -> List[AuditEvent]:
        events: List[AuditEvent] = []
        log_file = self._get_log_file()
        if not log_file.exists():
            return events
        with open(log_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if event_type and data.get("event_type") != event_type:
                        continue
                    if actor and data.get("actor") != actor:
                        continue
                    if since and data.get("timestamp", "") < since:
                        continue
                    events.append(AuditEvent(**data))
                except json.JSONDecodeError:
                    continue
        return events[-limit:]

    def get_summary(self) -> Dict[str, Any]:
        events = self.query_recent(limit=1000)
        summary: Dict[str, Any] = {
            "date": self._current_date,
            "total_events": len(events),
            "by_type": {},
            "by_actor": {},
            "security_events": 0,
            "healing_events": 0,
            "failed_events": 0,
        }
        for event in events:
            t = event.event_type
            a = event.actor
            summary["by_type"][t] = summary["by_type"].get(t, 0) + 1
            summary["by_actor"][a] = summary["by_actor"].get(a, 0) + 1
            if event.event_type == "security":
                summary["security_events"] += 1
            if event.event_type == "healing":
                summary["healing_events"] += 1
            if not event.success:
                summary["failed_events"] += 1
        return summary


_audit_instance: PulseAuditLogger | None = None

def get_audit_logger() -> PulseAuditLogger:
    global _audit_instance
    if _audit_instance is None:
        _audit_instance = PulseAuditLogger()
    return _audit_instance


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pulse Audit Logger")
    parser.add_argument("--summary", action="store_true", help="Show today's summary")
    parser.add_argument("--recent", type=int, default=10, help="Show N recent events")
    parser.add_argument("--type", type=str, help="Filter by event type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    audit = PulseAuditLogger()

    if args.summary:
        summary = audit.get_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("=== Audit Summary ===")
            print(f"Date: {summary['date']}")
            print(f"Total Events: {summary['total_events']}")
            print(f"Security Events: {summary['security_events']}")
            print(f"Healing Events: {summary['healing_events']}")
            print(f"Failed Events: {summary['failed_events']}")
            print("\nBy Type:")
            for t, c in summary["by_type"].items():
                print(f"  {t}: {c}")
    else:
        events = audit.query_recent(limit=args.recent, event_type=args.type)
        if args.json:
            print(json.dumps([asdict(e) for e in events], indent=2))
        else:
            print(f"=== Recent Events ({len(events)}) ===")
            for event in events:
                status = "✅" if event.success else "❌"
                print(f"{status} [{event.timestamp}] {event.event_type}/{event.action}")
                print(f"   Actor: {event.actor}, Resource: {event.resource or 'N/A'}")
