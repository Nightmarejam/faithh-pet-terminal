#!/usr/bin/env python3
"""
Real-Time Genomic Monitoring Experiment
Advanced real-time monitoring of genomic processes
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path

class RealtimeGenomicMonitor:
    """Real-time genomic monitoring system"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
    
    def monitor_genomic_processes(self, duration_minutes: int = 5):
        """Monitor genomic processes in real-time"""
        print("🔍 Starting Real-Time Genomic Monitoring")
        print("=" * 50)
        
        end_time = time.time() + (duration_minutes * 60)
        monitoring_data = []
        
        while time.time() < end_time:
            try:
                # Canonical PLC snapshot (mission + faithh_status)
                response = requests.get(f"{self.backend_url}/api/plc/state", timeout=10)

                if response.status_code == 200:
                    plc_data = response.json()
                    monitoring_data.append({
                        "timestamp": datetime.now().isoformat(),
                        "plc_state": plc_data,
                    })
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"Error monitoring: {e}")
                time.sleep(30)
        
        # Save monitoring data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"realtime_monitoring_results_{timestamp}.json"
        
        results_dir = Path("/home/jonat/ai-stack/genomic_results")
        results_dir.mkdir(exist_ok=True)
        
        with open(results_dir / filename, 'w') as f:
            json.dump(monitoring_data, f, indent=2)
        
        print(f"📄 Monitoring data saved to: {filename}")
        return {"status": "success", "data_points": len(monitoring_data)}

def main():
    """Main execution function"""
    monitor = RealtimeGenomicMonitor()
    results = monitor.monitor_genomic_processes()
    
    print("\n🚀 Real-Time Genomic Monitoring Completed!")

if __name__ == "__main__":
    main()
