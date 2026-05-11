#!/usr/bin/env python3
"""
Smart scheduler for collectors based on development hours analysis.
Adjusts collection intervals based on actual usage patterns.
"""
import subprocess
import json
from datetime import datetime, timezone
from pathlib import Path

class SmartScheduler:
    """Manages dynamic collector scheduling based on development patterns."""
    
    def __init__(self):
        self.crontab_path = Path.home() / "ai-stack" / "scripts" / "collectors" / "smart_crontab"
        self.current_crontab = Path.home() / "ai-stack" / "scripts" / "collectors" / "current_crontab"
        
    def get_current_interval(self, hour: int) -> dict:
        """Get optimal intervals based on development hour analysis."""
        
        # High activity windows: 4 AM, 5 PM, 10 PM-2 AM
        if hour == 4 or hour == 17 or hour >= 22 or hour <= 2:
            return {
                "health": "*/15 * * * *",
                "git": "*/15 * * * *",
                "file_changes": "*/15 * * * *",
                "terminal": "*/30 * * * *",
                "label": "high_activity"
            }
        
        # Medium activity windows: 1-3 AM, 11 PM, 6 PM
        elif hour in [1, 2, 3, 23, 18]:
            return {
                "health": "*/15 * * * *",
                "git": "*/30 * * * *",
                "file_changes": "*/30 * * * *",
                "terminal": "0 * * * *",
                "label": "medium_activity"
            }
        
        # Low activity windows: 6 AM-9 AM, 12 PM-4 PM, 7 PM-9 PM
        else:
            return {
                "health": "*/15 * * * *",
                "git": "0 */2 * * *",
                "file_changes": "0 */2 * * *",
                "terminal": "0 */2 * * *",
                "label": "low_activity"
            }
    
    def generate_smart_crontab(self) -> str:
        """Generate crontab with dynamic intervals."""
        current_hour = datetime.now(timezone.utc).hour
        intervals = self.get_current_interval(current_hour)
        
        crontab = f"""# Smart Collector Schedule - {intervals['label']} (Hour: {current_hour})
# Generated: {datetime.now(timezone.utc).isoformat()}

# Health collector - always frequent
{intervals['health']} cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --health >> /home/jonat/ai-stack/logs/collectors.log 2>&1

# Git collector - dynamic based on activity
{intervals['git']} cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --git >> /home/jonat/ai-stack/logs/collectors.log 2>&1

# File changes collector - dynamic based on activity
{intervals['file_changes']} cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --files >> /home/jonat/ai-stack/logs/collectors.log 2>&1

# Terminal collector - dynamic based on activity
{intervals['terminal']} cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --terminal >> /home/jonat/ai-stack/logs/collectors.log 2>&1

# Trend collection - every hour
0 * * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python scripts/collectors/trend_tracker.py --collect >> /home/jonat/ai-stack/logs/trends.log 2>&1

# Daily full collection and snapshot
0 0 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --all --snapshot >> /home/jonat/ai-stack/logs/collectors.log 2>&1

# PULSE Reflection Engine — nightly sweeps
30 2 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python scripts/staleness_detector.py --output staleness_report >> /home/jonat/ai-stack/logs/pulse.log 2>&1
45 2 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python scripts/decision_divergence.py --output divergence_report >> /home/jonat/ai-stack/logs/pulse.log 2>&1
0 3 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python scripts/branch_explorer.py --output branch_report >> /home/jonat/ai-stack/logs/pulse.log 2>&1
15 3 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python scripts/auto_journal.py --skip-llm >> /home/jonat/ai-stack/logs/journal.log 2>&1
20 3 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python scripts/pulse_autonomous.py --dry-run >> /home/jonat/ai-stack/logs/pulse.log 2>&1
"""
        return crontab
    
    def update_crontab(self) -> bool:
        """Update the system crontab with smart scheduling."""
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current = result.stdout if result.returncode == 0 else ""
            
            # Save current crontab
            self.current_crontab.write_text(current)
            
            # Generate new smart crontab
            smart_crontab = self.generate_smart_crontab()
            
            # Install new crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=smart_crontab)
            
            if process.returncode == 0:
                print(f"✅ Smart crontab installed ({self.get_current_interval(datetime.now(timezone.utc).hour)['label']})")
                return True
            else:
                print("❌ Failed to install smart crontab")
                return False
                
        except Exception as e:
            print(f"❌ Error updating crontab: {e}")
            return False
    
    def restore_original_crontab(self) -> bool:
        """Restore the original crontab."""
        try:
            if self.current_crontab.exists():
                original = self.current_crontab.read_text()
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=original)
                
                if process.returncode == 0:
                    print("✅ Original crontab restored")
                    return True
            return False
        except Exception as e:
            print(f"❌ Error restoring crontab: {e}")
            return False
    
    def get_next_schedule_change(self) -> str:
        """Get when the next schedule change will occur."""
        current_hour = datetime.now(timezone.utc).hour
        
        # Find next activity window change
        if current_hour < 4:
            next_change = 4
        elif current_hour < 17:
            next_change = 17
        elif current_hour < 22:
            next_change = 22
        else:
            next_change = 4  # Next day
        
        return f"Next change at {next_change:02d}:00 UTC"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart collector scheduler")
    parser.add_argument("--install", action="store_true", help="Install smart crontab")
    parser.add_argument("--restore", action="store_true", help="Restore original crontab")
    parser.add_argument("--preview", action="store_true", help="Preview smart crontab")
    parser.add_argument("--status", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    scheduler = SmartScheduler()
    
    if args.install:
        scheduler.update_crontab()
    elif args.restore:
        scheduler.restore_original_crontab()
    elif args.preview:
        print(scheduler.generate_smart_crontab())
    elif args.status:
        current_hour = datetime.now(timezone.utc).hour
        intervals = scheduler.get_current_interval(current_hour)
        print(f"Current hour: {current_hour:02d}:00 UTC")
        print(f"Activity level: {intervals['label']}")
        print(f"Next change: {scheduler.get_next_schedule_change()}")
    else:
        print("Use --install to install smart scheduling")
        print("Use --restore to restore original crontab")
        print("Use --preview to preview the schedule")
        print("Use --status to show current status")
