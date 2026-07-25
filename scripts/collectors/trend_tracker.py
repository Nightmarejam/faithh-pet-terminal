#!/usr/bin/env python3
"""
Trend tracker for Compass - collects and stores historical data.
"""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

class TrendTracker:
    """Tracks Compass data over time for trend analysis."""
    
    def __init__(self):
        self.trends_dir = Path.home() / "ai-stack" / "collectors" / "trends"
        self.trends_dir.mkdir(exist_ok=True)
        self.daily_file = self.trends_dir / f"daily_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
        
    def collect_snapshot(self) -> Dict[str, Any]:
        """Collect a snapshot of current system state."""
        from scripts.collectors.director import CompassDirector
        
        director = CompassDirector()
        result = director.analyze()
        
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hour": datetime.now(timezone.utc).hour,
            "system_health": result.get("raw_summary", {}),
            "attention_items": result.get("attention_items", []),
            "collector_status": {},
            "project_states": result.get("project_states", {})
        }
        
        # Add collector status
        collectors_dir = Path.home() / "ai-stack" / "collectors" / "state"
        for name in ['health', 'git', 'file_changes', 'terminal']:
            state_file = collectors_dir / f'{name}.json'
            if state_file.exists():
                with open(state_file) as f:
                    data = json.load(f)
                    snapshot["collector_status"][name] = {
                        'success': data.get('success', False),
                        'collected_at': data.get('collected_at'),
                        'error': data.get('error') if not data.get('success') else None
                    }
        
        return snapshot
    
    def save_snapshot(self, snapshot: Dict[str, Any]):
        """Save snapshot to daily file."""
        # Load existing data
        if self.daily_file.exists():
            with open(self.daily_file) as f:
                daily_data = json.load(f)
        else:
            daily_data = {"date": self.daily_file.stem.replace("daily_", ""), "snapshots": []}
        
        # Add new snapshot
        daily_data["snapshots"].append(snapshot)
        
        # Keep only last 24 hours of snapshots
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        daily_data["snapshots"] = [
            s for s in daily_data["snapshots"]
            if datetime.fromisoformat(s["timestamp"].replace("Z", "+00:00")) > cutoff
        ]
        
        # Save back
        with open(self.daily_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
    
    def get_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get trend data for the last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        trends = {
            "health_trend": [],
            "issue_trend": [],
            "collector_uptime": {},
            "activity_pattern": {}
        }
        
        # Collect from daily files
        for daily_file in sorted(self.trends_dir.glob("daily_*.json")):
            if not daily_file.name.endswith(".json"):
                continue
                
            with open(daily_file) as f:
                daily_data = json.load(f)
            
            for snapshot in daily_data.get("snapshots", []):
                snapshot_time = datetime.fromisoformat(snapshot["timestamp"].replace("Z", "+00:00"))
                if snapshot_time > cutoff:
                    # Health trend
                    services_healthy = snapshot["system_health"].get("services_healthy", "0/0")
                    if "/" in services_healthy:
                        healthy, total = map(int, services_healthy.split("/"))
                        health_score = healthy / total if total > 0 else 0
                        trends["health_trend"].append({
                            "timestamp": snapshot["timestamp"],
                            "health_score": health_score
                        })
                    
                    # Issue trend
                    total_issues = snapshot["system_health"].get("total_issues", 0)
                    critical = snapshot["system_health"].get("critical", 0)
                    high = snapshot["system_health"].get("high", 0)
                    
                    trends["issue_trend"].append({
                        "timestamp": snapshot["timestamp"],
                        "total": total_issues,
                        "critical": critical,
                        "high": high
                    })
                    
                    # Collector uptime
                    for collector, status in snapshot.get("collector_status", {}).items():
                        if collector not in trends["collector_uptime"]:
                            trends["collector_uptime"][collector] = []
                        trends["collector_uptime"][collector].append({
                            "timestamp": snapshot["timestamp"],
                            "success": status.get("success", False)
                        })
                    
                    # Activity pattern
                    hour = snapshot["hour"]
                    if hour not in trends["activity_pattern"]:
                        trends["activity_pattern"][hour] = 0
                    trends["activity_pattern"][hour] += 1
        
        return trends
    
    def generate_insights(self, trends: Dict[str, Any]) -> List[str]:
        """Generate insights from trend data."""
        insights = []
        
        # Health insights
        if trends["health_trend"]:
            avg_health = sum(t["health_score"] for t in trends["health_trend"]) / len(trends["health_trend"])
            if avg_health < 0.9:
                insights.append(f"⚠️ System health averaging {avg_health:.1%} - consider investigation")
        
        # Issue insights
        if trends["issue_trend"]:
            recent_issues = trends["issue_trend"][-6:]  # Last 6 snapshots
            if all(t["total"] > 0 for t in recent_issues):
                insights.append("📊 Persistent issues detected - review attention items")
        
        # Collector insights
        for collector, data in trends["collector_uptime"].items():
            if data:
                uptime = sum(1 for d in data if d["success"]) / len(data)
                if uptime < 0.8:
                    insights.append(f"🔧 {collector.title()} collector uptime: {uptime:.1%} - needs attention")
        
        # Activity insights
        if trends["activity_pattern"]:
            peak_hour = max(trends["activity_pattern"], key=trends["activity_pattern"].get)
            insights.append(f"📈 Peak activity hour: {peak_hour:02d}:00")
        
        return insights

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Track Compass trends")
    parser.add_argument("--collect", action="store_true", help="Collect and save snapshot")
    parser.add_argument("--trends", type=int, default=24, help="Get trends for last N hours")
    parser.add_argument("--insights", action="store_true", help="Generate insights from trends")
    
    args = parser.parse_args()
    
    tracker = TrendTracker()
    
    if args.collect:
        snapshot = tracker.collect_snapshot()
        tracker.save_snapshot(snapshot)
        print(f"✅ Snapshot collected: {snapshot['timestamp']}")
    
    if args.trends:
        trends = tracker.get_trends(args.trends)
        print(f"📊 Trends for last {args.trends} hours:")
        print(f"  Health points: {len(trends['health_trend'])}")
        print(f"  Issue points: {len(trends['issue_trend'])}")
        print(f"  Collectors tracked: {len(trends['collector_uptime'])}")
    
    if args.insights:
        trends = tracker.get_trends(24)
        insights = tracker.generate_insights(trends)
        print("\n💡 Insights:")
        for insight in insights:
            print(f"  {insight}")
