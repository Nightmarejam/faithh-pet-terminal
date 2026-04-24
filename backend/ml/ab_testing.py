"""
FAITHH Phase 2 - A/B Testing Framework
Compare ML-optimized weights vs baseline weights performance
"""

import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import statistics
from dataclasses import dataclass, asdict

@dataclass
class ABTestResult:
    """Results from A/B test comparison"""
    test_id: str
    timestamp: datetime
    query_count: int
    ml_avg_response_time: float
    baseline_avg_response_time: float
    ml_avg_accuracy: float
    baseline_avg_accuracy: float
    ml_success_rate: float
    baseline_success_rate: float
    improvement_percentage: float
    statistical_significance: str
    recommendation: str

class ABTestingFramework:
    """A/B testing for Phase 2 weight optimization validation"""
    
    def __init__(self, db_path: str = "/home/jonat/ai-stack/phase2_performance.db"):
        self.db_path = db_path
        self.test_results = []
    
    def get_recent_performance_data(self, days: int = 7) -> Tuple[List[Dict], List[Dict]]:
        """Get recent performance data for ML and baseline comparison"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get ML-optimized queries (after Phase 2 completion)
        ml_cutoff = datetime.now() - timedelta(days=days//2)
        cursor.execute("""
            SELECT * FROM query_performance 
            WHERE timestamp >= ? AND weights_used LIKE '%ml_optimized%'
            ORDER BY timestamp DESC
            LIMIT 100
        """, (ml_cutoff.isoformat(),))
        
        ml_data = []
        for row in cursor.fetchall():
            ml_data.append({
                'query_id': row[1],
                'timestamp': row[2],
                'response_time': float(row[6]) if row[6] else 0.0,
                'accuracy_score': float(row[9]) if row[9] else 0.0,
                'success': 1 if row[13] else 0,
                'weights_used': json.loads(row[4]) if row[4] else {}
            })
        
        # Get baseline queries (before ML optimization)
        baseline_cutoff = datetime.now() - timedelta(days=days)
        cursor.execute("""
            SELECT * FROM query_performance 
            WHERE timestamp >= ? AND (weights_used IS NULL OR weights_used NOT LIKE '%ml_optimized%')
            ORDER BY timestamp DESC
            LIMIT 100
        """, (baseline_cutoff.isoformat(),))
        
        baseline_data = []
        for row in cursor.fetchall():
            baseline_data.append({
                'query_id': row[1],
                'timestamp': row[2],
                'response_time': float(row[6]) if row[6] else 0.0,
                'accuracy_score': float(row[9]) if row[9] else 0.0,
                'success': 1 if row[13] else 0,
                'weights_used': json.loads(row[4]) if row[4] else {}
            })
        
        conn.close()
        
        return ml_data, baseline_data
    
    def calculate_metrics(self, data: List[Dict]) -> Dict[str, float]:
        """Calculate performance metrics for a dataset"""
        
        if not data:
            return {
                'avg_response_time': 0.0,
                'avg_accuracy': 0.0,
                'success_rate': 0.0,
                'query_count': 0
            }
        
        response_times = [d['response_time'] for d in data]
        accuracies = [d['accuracy_score'] for d in data]
        successes = [d['success'] for d in data]
        
        return {
            'avg_response_time': statistics.mean(response_times),
            'avg_accuracy': statistics.mean(accuracies),
            'success_rate': sum(successes) / len(successes),
            'query_count': len(data)
        }
    
    def run_ab_test(self, days: int = 7) -> ABTestResult:
        """Run A/B test comparing ML vs baseline performance"""
        
        print(f"🧪 Running A/B Test (last {days} days)")
        print("=" * 50)
        
        # Get performance data
        ml_data, baseline_data = self.get_recent_performance_data(days)
        
        print(f"📊 Data Collection:")
        print(f"  ML-optimized queries: {len(ml_data)}")
        print(f"  Baseline queries: {len(baseline_data)}")
        
        if len(ml_data) < 10 or len(baseline_data) < 10:
            print("⚠️  Insufficient data for reliable comparison")
            print("💡 Continue system usage to collect more performance data")
        
        # Calculate metrics
        ml_metrics = self.calculate_metrics(ml_data)
        baseline_metrics = self.calculate_metrics(baseline_data)
        
        print(f"\n📈 Performance Metrics:")
        print(f"  ML Response Time: {ml_metrics['avg_response_time']:.2f}s")
        print(f"  Baseline Response Time: {baseline_metrics['avg_response_time']:.2f}s")
        print(f"  ML Accuracy: {ml_metrics['avg_accuracy']:.3f}")
        print(f"  Baseline Accuracy: {baseline_metrics['avg_accuracy']:.3f}")
        print(f"  ML Success Rate: {ml_metrics['success_rate']:.3f}")
        print(f"  Baseline Success Rate: {baseline_metrics['success_rate']:.3f}")
        
        # Calculate improvement
        response_time_improvement = ((baseline_metrics['avg_response_time'] - ml_metrics['avg_response_time']) / baseline_metrics['avg_response_time']) * 100
        accuracy_improvement = ((ml_metrics['avg_accuracy'] - baseline_metrics['avg_accuracy']) / max(baseline_metrics['avg_accuracy'], 0.001)) * 100
        success_improvement = ((ml_metrics['success_rate'] - baseline_metrics['success_rate']) / max(baseline_metrics['success_rate'], 0.001)) * 100
        
        # Overall improvement (weighted average)
        overall_improvement = (response_time_improvement * 0.3 + accuracy_improvement * 0.4 + success_improvement * 0.3)
        
        # Statistical significance (simplified)
        if len(ml_data) >= 20 and len(baseline_data) >= 20:
            significance = "High"
        elif len(ml_data) >= 10 and len(baseline_data) >= 10:
            significance = "Medium"
        else:
            significance = "Low"
        
        # Recommendation
        if overall_improvement > 10:
            recommendation = "Deploy ML optimization widely"
        elif overall_improvement > 0:
            recommendation = "Continue with ML optimization"
        else:
            recommendation = "Review ML optimization parameters"
        
        print(f"\n🎯 Results:")
        print(f"  Response Time Improvement: {response_time_improvement:.1f}%")
        print(f"  Accuracy Improvement: {accuracy_improvement:.1f}%")
        print(f"  Success Rate Improvement: {success_improvement:.1f}%")
        print(f"  Overall Improvement: {overall_improvement:.1f}%")
        print(f"  Statistical Significance: {significance}")
        print(f"  Recommendation: {recommendation}")
        
        # Create result object
        result = ABTestResult(
            test_id=f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            query_count=len(ml_data) + len(baseline_data),
            ml_avg_response_time=ml_metrics['avg_response_time'],
            baseline_avg_response_time=baseline_metrics['avg_response_time'],
            ml_avg_accuracy=ml_metrics['avg_accuracy'],
            baseline_avg_accuracy=baseline_metrics['avg_accuracy'],
            ml_success_rate=ml_metrics['success_rate'],
            baseline_success_rate=baseline_metrics['success_rate'],
            improvement_percentage=overall_improvement,
            statistical_significance=significance,
            recommendation=recommendation
        )
        
        self.test_results.append(result)
        
        return result
    
    def generate_report(self) -> str:
        """Generate comprehensive A/B testing report"""
        
        if not self.test_results:
            return "No A/B test results available"
        
        latest_result = self.test_results[-1]
        
        report = f"""
# Phase 2 A/B Testing Report

**Test ID**: {latest_result.test_id}
**Timestamp**: {latest_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Queries Analyzed**: {latest_result.query_count}

## Performance Comparison

### Response Time
- **ML-Optimized**: {latest_result.ml_avg_response_time:.2f}s
- **Baseline**: {latest_result.baseline_avg_response_time:.2f}s
- **Improvement**: {((latest_result.baseline_avg_response_time - latest_result.ml_avg_response_time) / latest_result.baseline_avg_response_time * 100):.1f}%

### Accuracy
- **ML-Optimized**: {latest_result.ml_avg_accuracy:.3f}
- **Baseline**: {latest_result.baseline_avg_accuracy:.3f}
- **Improvement**: {((latest_result.ml_avg_accuracy - latest_result.baseline_avg_accuracy) / max(latest_result.baseline_avg_accuracy, 0.001) * 100):.1f}%

### Success Rate
- **ML-Optimized**: {latest_result.ml_success_rate:.3f}
- **Baseline**: {latest_result.baseline_success_rate:.3f}
- **Improvement**: {((latest_result.ml_success_rate - latest_result.baseline_success_rate) / max(latest_result.baseline_success_rate, 0.001) * 100):.1f}%

## Overall Assessment

**Improvement**: {latest_result.improvement_percentage:.1f}%
**Statistical Significance**: {latest_result.statistical_significance}
**Recommendation**: {latest_result.recommendation}

## Conclusion

{latest_result.recommendation}
"""
        
        return report
    
    def save_report(self, filename: str = None) -> str:
        """Save A/B testing report to file"""
        
        if filename is None:
            filename = f"phase2_ab_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"📄 A/B Test Report saved: {filename}")
        return filename

def main():
    """Main A/B testing execution"""
    
    print("🧪 Phase 2 A/B Testing Framework")
    print("=" * 50)
    
    # Initialize A/B testing framework
    ab_tester = ABTestingFramework()
    
    # Run A/B test
    result = ab_tester.run_ab_test(days=7)
    
    # Generate and save report
    report_file = ab_tester.save_report()
    
    print(f"\n🎯 A/B Testing Complete!")
    print(f"📊 Overall Improvement: {result.improvement_percentage:.1f}%")
    print(f"💡 Recommendation: {result.recommendation}")
    print(f"📄 Report: {report_file}")
    
    return result.improvement_percentage > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
