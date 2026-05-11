#!/usr/bin/env python3
"""
Phase 2 Data Collection Script
Systematically collects performance data for weight optimization model training.
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class Phase2DataCollector:
    """Collects performance data for Phase 2 weight optimization training"""
    
    def __init__(self):
        self.test_queries = {
            'alife_query': [
                "What is the status of Experiment 4?",
                "How are the ALIFE agents performing?",
                "What happened with the harmonic interference?",
                "Tell me about the red queen dynamics",
                "How did the genome evolution work out?",
                "What were the results of the wave simulation?",
                "How did agents adapt to the interference patterns?",
                "What did we learn from the ALIFE experiments?",
                "How did the beat-genome agents perform?",
                "What was the outcome of Experiment 4?"
            ],
            'self_query': [
                "What can FAITHH do for me?",
                "How does FAITHH maintain project coherence?",
                "What are FAITHH's capabilities?",
                "Tell me about FAITHH's architecture",
                "How does FAITHH help with multiple projects?",
                "What is FAITHH's purpose?",
                "How does FAITHH integrate different systems?",
                "What makes FAITHH unique?",
                "How does FAITHH learn and adapt?"
            ],
            'why_question': [
                "Why did we choose this architecture?",
                "What was the rationale for this approach?",
                "Why did we implement it this way?",
                "What alternatives were considered?",
                "Why is this design better than others?",
                "What were the trade-offs we made?",
                "Why did we use these technologies?",
                "What problems does this solve?",
                "Why was this approach selected?"
            ],
            'next_action_query': [
                "What should I do next?",
                "What are the next steps?",
                "Where should I focus my efforts?",
                "What's the priority right now?",
                "How should I proceed?",
                "What should I work on today?",
                "What's the most important task?",
                "Where do we go from here?"
            ],
            'project_query': [
                "What is the current project status?",
                "What phase are we in?",
                "How is the project progressing?",
                "What are the project goals?",
                "What's the project timeline?",
                "How are we tracking against milestones?",
                "What's the project health?",
                "What are the project deliverables?"
            ],
            'constella_query': [
                "Tell me about the Constella framework",
                "What are the Constella principles?",
                "How does Constella work?",
                "What are astris and auctor tokens?",
                "How does Constella integrate with FAITHH?",
                "What is the Constella philosophy?",
                "How do I use Constella effectively?"
            ],
            'business_query': [
                "How is the business doing?",
                "What's the revenue situation?",
                "How are the client projects going?",
                "What's the status of the LLC?",
                "How is Tomcat Audio performing?",
                "What are the business metrics?",
                "How are we tracking financially?"
            ],
            'recent_changes_query': [
                "What changed recently?",
                "What's new in the system?",
                "What were the latest updates?",
                "What did we just implement?",
                "What's the recent activity?",
                "What changed in the last few days?",
                "What's the latest development?"
            ]
        }
        
        # Multi-intent queries for testing conflict resolution
        self.multi_intent_queries = [
            "What should I do next with the ALIFE experiments and how will it affect the business?",
            "Why did we choose this architecture and what does Constella say about it?",
            "What's the project status and what should I do next to improve Phase 2?",
            "How does FAITHH maintain coherence and what are the recent changes that affect this?",
            "What's the business impact of the ALIFE experiments and what should we do next?"
        ]
    
    def collect_normal_usage_data(self, days: int = 7) -> Dict[str, Any]:
        """Collect data from normal usage patterns"""
        print(f"📊 Collecting normal usage data for {days} days...")
        
        try:
            from backend.ml.performance_tracker import performance_tracker
            
            # Get recent performance data
            recent_data = performance_tracker.get_recent_performance(limit=100)
            
            analysis = {
                'total_samples': len(recent_data),
                'intent_distribution': {},
                'avg_response_time': 0,
                'avg_accuracy': 0,
                'date_range': f"Last {days} days",
                'samples_by_date': {}
            }
            
            if recent_data:
                # Analyze intent distribution
                for record in recent_data:
                    intent_type = 'unknown'
                    for key, value in record.intent.items():
                        if key.startswith('is_') and value:
                            intent_type = key[3:]  # Remove 'is_' prefix
                            break
                    
                    analysis['intent_distribution'][intent_type] = analysis['intent_distribution'].get(intent_type, 0) + 1
                    
                    # Calculate averages
                    analysis['avg_response_time'] += record.response_time
                    if record.accuracy_score:
                        analysis['avg_accuracy'] += record.accuracy_score
                    
                    # Group by date
                    date_key = record.timestamp.date().isoformat()
                    analysis['samples_by_date'][date_key] = analysis['samples_by_date'].get(date_key, 0) + 1
                
                # Finalize averages
                if recent_data:
                    analysis['avg_response_time'] /= len(recent_data)
                    analysis['avg_accuracy'] /= len(recent_data)
            
            print(f"📈 Analysis: {json.dumps(analysis, indent=2)}")
            return analysis
            
        except Exception as e:
            print(f"❌ Error collecting normal usage data: {e}")
            return {'error': str(e)}
    
    def generate_test_queries(self, count_per_intent: int = 3) -> List[str]:
        """Generate diverse test queries for data collection"""
        print(f"🎯 Generating {count_per_intent} test queries per intent type...")
        
        test_queries = []
        
        # Generate queries for each intent type
        for intent_type, queries in self.test_queries.items():
            selected = random.sample(queries, min(count_per_intent, len(queries)))
            test_queries.extend(selected)
        
        # Add multi-intent queries
        test_queries.extend(self.multi_intent_queries)
        
        print(f"📝 Generated {len(test_queries)} test queries")
        return test_queries
    
    def execute_query_collection(self, queries: List[str], delay: float = 2.0) -> Dict[str, Any]:
        """Execute queries to collect performance data"""
        print(f"🚀 Executing {len(queries)} queries for data collection...")
        
        results = {
            'total_queries': len(queries),
            'successful': 0,
            'failed': 0,
            'execution_times': [],
            'errors': []
        }
        
        for i, query in enumerate(queries):
            try:
                print(f"   Query {i+1}/{len(queries)}: {query[:50]}...")
                
                start_time = time.time()
                
                # Execute query via API
                import requests
                response = requests.post(
                    'http://localhost:5557/api/chat',
                    headers={'Content-Type': 'application/json'},
                    json={'message': query},
                    timeout=30
                )
                
                execution_time = time.time() - start_time
                results['execution_times'].append(execution_time)
                
                if response.status_code == 200:
                    results['successful'] += 1
                    print(f"      ✅ Success ({execution_time:.2f}s)")
                else:
                    results['failed'] += 1
                    error_msg = f"HTTP {response.status_code}"
                    results['errors'].append(f"Query {i+1}: {error_msg}")
                    print(f"      ❌ Failed: {error_msg}")
                
                # Delay between queries
                if delay > 0 and i < len(queries) - 1:
                    time.sleep(delay)
                
            except Exception as e:
                results['failed'] += 1
                error_msg = str(e)
                results['errors'].append(f"Query {i+1}: {error_msg}")
                print(f"      ❌ Error: {error_msg}")
        
        # Calculate statistics
        if results['execution_times']:
            results['avg_execution_time'] = sum(results['execution_times']) / len(results['execution_times'])
            results['min_execution_time'] = min(results['execution_times'])
            results['max_execution_time'] = max(results['execution_times'])
        
        print(f"📊 Collection Results:")
        print(f"   Successful: {results['successful']}")
        print(f"   Failed: {results['failed']}")
        print(f"   Avg time: {results.get('avg_execution_time', 0):.2f}s")
        
        return results
    
    def analyze_data_quality(self) -> Dict[str, Any]:
        """Analyze the quality of collected data"""
        print(f"🔍 Analyzing data quality...")
        
        try:
            from backend.ml.performance_tracker import performance_tracker
            
            # Get recent data for analysis
            recent_data = performance_tracker.get_recent_performance(limit=50)
            
            quality_analysis = {
                'total_samples': len(recent_data),
                'complete_samples': 0,
                'missing_accuracy': 0,
                'missing_coherence': 0,
                'intent_coverage': {},
                'date_range': None,
                'quality_score': 0
            }
            
            if recent_data:
                # Check sample completeness
                for record in recent_data:
                    is_complete = True
                    
                    if record.accuracy_score is None:
                        quality_analysis['missing_accuracy'] += 1
                        is_complete = False
                    
                    if record.coherence_score is None:
                        quality_analysis['missing_coherence'] += 1
                        is_complete = False
                    
                    if is_complete:
                        quality_analysis['complete_samples'] += 1
                    
                    # Track intent coverage
                    for key, value in record.intent.items():
                        if key.startswith('is_') and value:
                            intent_type = key[3:]
                            quality_analysis['intent_coverage'][intent_type] = quality_analysis['intent_coverage'].get(intent_type, 0) + 1
                
                # Calculate date range
                dates = [record.timestamp.date() for record in recent_data]
                if dates:
                    quality_analysis['date_range'] = f"{min(dates)} to {max(dates)}"
                
                # Calculate quality score
                if recent_data:
                    completeness_rate = quality_analysis['complete_samples'] / len(recent_data)
                    intent_diversity = len(quality_analysis['intent_coverage']) / 8  # 8 intent types total
                    quality_analysis['quality_score'] = (completeness_rate * 0.6) + (intent_diversity * 0.4)
            
            print(f"📊 Quality Analysis:")
            print(f"   Total samples: {quality_analysis['total_samples']}")
            print(f"   Complete samples: {quality_analysis['complete_samples']}")
            print(f"   Quality score: {quality_analysis['quality_score']:.2f}")
            print(f"   Intent coverage: {len(quality_analysis['intent_coverage'])}/8 types")
            print(f"   Date range: {quality_analysis['date_range']}")
            
            return quality_analysis
            
        except Exception as e:
            print(f"❌ Error analyzing data quality: {e}")
            return {'error': str(e)}
    
    def generate_collection_report(self) -> str:
        """Generate a comprehensive data collection report"""
        print(f"📋 Generating data collection report...")
        
        try:
            # Collect all analyses
            normal_usage = self.collect_normal_usage_data()
            quality_analysis = self.analyze_data_quality()
            
            report = f"""
# Phase 2 Data Collection Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
Phase 2 data collection status and recommendations for weight optimization model training.

## Current Data Status

### Normal Usage Analysis
{json.dumps(normal_usage, indent=2)}

### Data Quality Analysis
{json.dumps(quality_analysis, indent=2)}

## Recommendations

### Immediate Actions
1. **Target Sample Count**: Need 50+ samples for model training
2. **Current Status**: {normal_usage.get('total_samples', 0)} samples collected
3. **Quality Score**: {quality_analysis.get('quality_score', 0):.2f}/1.0
4. **Intent Coverage**: {len(quality_analysis.get('intent_coverage', {}))}/8 intent types

### Data Collection Strategy
1. **Normal Usage**: Continue regular system usage
2. **Deliberate Testing**: Execute targeted test queries
3. **Multi-Intent Testing**: Test complex query scenarios
4. **Quality Assurance**: Validate data completeness

### Timeline Estimate
- **Current Rate**: ~{normal_usage.get('total_samples', 0)} samples/day
- **Target Achievement**: {max(1, (50 - normal_usage.get('total_samples', 0)) // max(1, normal_usage.get('total_samples', 0)))} days at current rate
- **Accelerated Collection**: 2-3 days with deliberate testing

## Next Steps
1. Execute test query collection
2. Monitor data quality metrics
3. Prepare training dataset when target reached
4. Train weight optimization models

## Success Criteria
- [ ] 50+ total performance samples
- [ ] All 8 intent types represented
- [ ] 95%+ data completeness
- [ ] Quality score > 0.8

---
*Report generated by Phase 2 Data Collector*
"""
            
            # Save report
            report_file = f"phase2_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"📄 Report saved to: {report_file}")
            return report
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return f"Error generating report: {e}"

def main():
    """Main data collection function"""
    print("🚀 Phase 2 Data Collection System")
    print("=" * 50)
    
    collector = Phase2DataCollector()
    
    # Step 1: Analyze current data
    print("\n📊 Step 1: Analyzing current data...")
    current_status = collector.collect_normal_usage_data()
    
    # Step 2: Generate test queries
    print("\n🎯 Step 2: Generating test queries...")
    test_queries = collector.generate_test_queries(count_per_intent=2)
    
    # Step 3: Execute data collection
    print("\n🚀 Step 3: Executing data collection...")
    collection_results = collector.execute_query_collection(test_queries, delay=1.0)
    
    # Step 4: Analyze data quality
    print("\n🔍 Step 4: Analyzing data quality...")
    quality_analysis = collector.analyze_data_quality()
    
    # Step 5: Generate report
    print("\n📋 Step 5: Generating collection report...")
    report = collector.generate_collection_report()
    
    # Summary
    print(f"\n🎉 Data Collection Summary:")
    print(f"   Current samples: {current_status.get('total_samples', 0)}")
    print(f"   Test queries executed: {collection_results['successful']}")
    print(f"   Quality score: {quality_analysis.get('quality_score', 0):.2f}")
    print(f"   Intent coverage: {len(quality_analysis.get('intent_coverage', {}))}/8")
    
    # Recommendations
    total_samples = current_status.get('total_samples', 0) + collection_results['successful']
    if total_samples >= 50:
        print(f"\n✅ Sufficient data collected ({total_samples} samples)")
        print(f"🚀 Ready for weight optimization model training!")
    else:
        needed = 50 - total_samples
        print(f"\n⏳ Need {needed} more samples for model training")
        print(f"📈 Estimated time: {max(1, needed // max(1, current_status.get('total_samples', 1)))} days")

if __name__ == "__main__":
    main()
