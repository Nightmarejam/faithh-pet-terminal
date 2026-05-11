#!/usr/bin/env python3
"""
Phase 2 Experiment Runner
Runs focused experiments to collect diverse performance data for weight optimization.
"""

import json
import time
import random
import requests
from datetime import datetime
from typing import List, Dict, Any

class Phase2ExperimentRunner:
    """Runs focused experiments to collect performance data"""
    
    def __init__(self):
        self.experiment_queries = {
            # Focus on underrepresented intent types
            'self_query': [
                "What capabilities does FAITHH have?",
                "How does FAITHH help with project management?",
                "What makes FAITHH different from other AI assistants?",
                "How does FAITHH maintain coherence across projects?",
                "What is FAITHH's purpose and philosophy?",
                "How does FAITHH integrate with my existing workflow?",
                "What can FAITHH do to help me stay focused?",
                "How does FAITHH remember project context?"
            ],
            'why_question': [
                "Why did we implement the semantic intent detector?",
                "What was the reasoning behind using all-MiniLM-L6-v2?",
                "Why is weight optimization important for FAITHH?",
                "What led to the decision to implement Phase 2 features?",
                "Why did we choose SQLite for performance tracking?",
                "What was the rationale for the 77.5% confidence threshold?",
                "Why is semantic understanding better than regex patterns?",
                "What problems does Phase 2 solve that Phase 1 didn't?"
            ],
            'next_action_query': [
                "What should I prioritize today?",
                "How can I improve the Phase 2 implementation?",
                "What are the next steps for data collection?",
                "Where should I focus my efforts this week?",
                "What tasks need immediate attention?",
                "How should I structure my work today?",
                "What's the most important thing to do next?",
                "How can I make progress on the weight optimization?"
            ],
            'project_query': [
                "What is the current status of Phase 2?",
                "How are we tracking against our goals?",
                "What are the deliverables for this phase?",
                "What milestones have we achieved?",
                "How is the project progressing overall?",
                "What are the project's success criteria?",
                "How does Phase 2 fit into the overall roadmap?",
                "What are the current project priorities?"
            ],
            'constella_query': [
                "How does Constella integrate with FAITHH?",
                "What are the core principles of Constella?",
                "How do astris and auctor tokens work?",
                "What is the Constella philosophy?",
                "How can I apply Constella to my projects?",
                "What makes Constella different from other frameworks?",
                "How does Constella help with project alignment?",
                "What are the practical benefits of Constella?"
            ],
            'business_query': [
                "How is the audio business performing?",
                "What are the current revenue streams?",
                "How are client projects progressing?",
                "What's the status of Tom Cat Sound?",
                "How is the LLC structured and performing?",
                "What are the business metrics we should track?",
                "How does FAITHH contribute to business success?",
                "What are the growth opportunities for the business?"
            ],
            'recent_changes_query': [
                "What changed in the last 24 hours?",
                "What were the latest updates to Phase 2?",
                "What new features were recently implemented?",
                "How has the system evolved recently?",
                "What modifications were made to the backend?",
                "What's new in the data collection system?",
                "How has the performance tracking improved?",
                "What recent developments should I be aware of?"
            ]
        }
        
        # Complex multi-intent scenarios
        self.multi_intent_experiments = [
            "How does the semantic intent detector work and what should I do next to improve it?",
            "What is the current project status and why did we choose this approach for Phase 2?",
            "How does Constella integrate with FAITHH and what are the business implications?",
            "What changed recently and how does it affect the project timeline?",
            "Why did we implement performance tracking and what should I prioritize based on the data?",
            "How does the weight optimization work and what are the next steps for training?",
            "What capabilities does FAITHH have now and how does that help with business goals?",
            "How is the project progressing and what recent changes should I be aware of?"
        ]
    
    def run_intent_focus_experiment(self, intent_type: str, queries: List[str]) -> Dict[str, Any]:
        """Run focused experiment for specific intent type"""
        print(f"🎯 Running {intent_type} focus experiment...")
        
        results = {
            'intent_type': intent_type,
            'total_queries': len(queries),
            'successful': 0,
            'failed': 0,
            'response_times': [],
            'errors': []
        }
        
        for i, query in enumerate(queries):
            try:
                print(f"   Query {i+1}/{len(queries)}: {query[:50]}...")
                
                start_time = time.time()
                
                response = requests.post(
                    'http://localhost:5557/api/chat',
                    headers={'Content-Type': 'application/json'},
                    json={'message': query},
                    timeout=30
                )
                
                execution_time = time.time() - start_time
                results['response_times'].append(execution_time)
                
                if response.status_code == 200:
                    results['successful'] += 1
                    print(f"      ✅ Success ({execution_time:.2f}s)")
                else:
                    results['failed'] += 1
                    error_msg = f"HTTP {response.status_code}"
                    results['errors'].append(f"Query {i+1}: {error_msg}")
                    print(f"      ❌ Failed: {error_msg}")
                
                # Brief delay between queries
                time.sleep(1.5)
                
            except Exception as e:
                results['failed'] += 1
                error_msg = str(e)
                results['errors'].append(f"Query {i+1}: {error_msg}")
                print(f"      ❌ Error: {error_msg}")
        
        # Calculate statistics
        if results['response_times']:
            results['avg_response_time'] = sum(results['response_times']) / len(results['response_times'])
            results['min_response_time'] = min(results['response_times'])
            results['max_response_time'] = max(results['response_times'])
        
        print(f"📊 {intent_type} Results: {results['successful']}/{results['total_queries']} successful")
        return results
    
    def run_multi_intent_experiment(self) -> Dict[str, Any]:
        """Run multi-intent conflict resolution experiments"""
        print(f"🔀 Running multi-intent experiments...")
        
        return self.run_intent_focus_experiment('multi_intent', self.multi_intent_experiments)
    
    def run_alife_performance_experiment(self) -> Dict[str, Any]:
        """Run ALIFE-specific performance experiments"""
        print(f"🧬 Running ALIFE performance experiments...")
        
        alife_queries = [
            "What were the results of Experiment 4?",
            "How did the beat-genome agents adapt?",
            "What did we learn from the harmonic interference?",
            "How did the wave simulation perform?",
            "What were the key findings from the ALIFE experiments?",
            "How did agents respond to interference patterns?",
            "What was the outcome of the red queen dynamics?",
            "How did the genome evolution progress?"
        ]
        
        return self.run_intent_focus_experiment('alife_performance', alife_queries)
    
    def analyze_experiment_results(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze all experiment results"""
        print(f"📈 Analyzing experiment results...")
        
        analysis = {
            'total_experiments': len(all_results),
            'total_queries': sum(r['total_queries'] for r in all_results),
            'total_successful': sum(r['successful'] for r in all_results),
            'total_failed': sum(r['failed'] for r in all_results),
            'overall_success_rate': 0,
            'intent_types_tested': [],
            'performance_summary': {},
            'recommendations': []
        }
        
        if analysis['total_queries'] > 0:
            analysis['overall_success_rate'] = (analysis['total_successful'] / analysis['total_queries']) * 100
        
        # Collect intent types
        for result in all_results:
            analysis['intent_types_tested'].append(result['intent_type'])
        
        # Performance summary
        all_times = []
        for result in all_results:
            if 'response_times' in result:
                all_times.extend(result['response_times'])
        
        if all_times:
            analysis['performance_summary'] = {
                'avg_response_time': sum(all_times) / len(all_times),
                'min_response_time': min(all_times),
                'max_response_time': max(all_times),
                'total_response_time': sum(all_times)
            }
        
        # Generate recommendations
        if analysis['overall_success_rate'] < 80:
            analysis['recommendations'].append("Consider investigating failed queries for system improvements")
        
        if analysis['performance_summary'].get('avg_response_time', 0) > 10:
            analysis['recommendations'].append("Response times are high, consider optimization")
        
        if len(analysis['intent_types_tested']) < 6:
            analysis['recommendations'].append("Expand intent type coverage for better training data")
        
        return analysis
    
    def generate_experiment_report(self, all_results: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Generate comprehensive experiment report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# Phase 2 Experiment Report
Generated: {timestamp}

## Executive Summary
Successfully executed Phase 2 data collection experiments to gather diverse performance samples for weight optimization model training.

## Experiment Results

### Overall Performance
- **Total Experiments**: {analysis['total_experiments']}
- **Total Queries**: {analysis['total_queries']}
- **Successful Queries**: {analysis['total_successful']}
- **Failed Queries**: {analysis['total_failed']}
- **Success Rate**: {analysis['overall_success_rate']:.1f}%

### Intent Types Tested
{', '.join(analysis['intent_types_tested'])}

### Performance Summary
- **Average Response Time**: {analysis['performance_summary'].get('avg_response_time', 0):.2f}s
- **Min Response Time**: {analysis['performance_summary'].get('min_response_time', 0):.2f}s
- **Max Response Time**: {analysis['performance_summary'].get('max_response_time', 0):.2f}s
- **Total Execution Time**: {analysis['performance_summary'].get('total_response_time', 0):.2f}s

## Detailed Results by Experiment

"""
        
        for result in all_results:
            report += f"""
### {result['intent_type'].replace('_', ' ').title()} Experiment
- **Queries**: {result['successful']}/{result['total_queries']} successful
- **Average Time**: {result.get('avg_response_time', 0):.2f}s
- **Error Rate**: {result['failed']} errors

"""
        
        report += f"""
## Recommendations
{chr(10).join(f"- {rec}" for rec in analysis['recommendations']) if analysis['recommendations'] else "- All experiments performed well"}

## Data Collection Impact
- **Samples Added**: {analysis['total_successful']} new performance samples
- **Intent Coverage**: Expanded to {len(analysis['intent_types_tested'])} intent types
- **Quality Improvement**: Enhanced dataset diversity for ML training

## Next Steps
1. Monitor data quality metrics in performance tracker
2. Continue normal usage to accumulate additional samples
3. Execute weight optimization training when 50+ samples reached
4. Validate model performance with A/B testing

---
*Report generated by Phase 2 Experiment Runner*
"""
        
        return report
    
    def save_experiment_report(self, report: str) -> str:
        """Save experiment report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"phase2_experiment_report_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"📄 Experiment report saved to: {filename}")
        return filename

def main():
    """Main experiment execution function"""
    print("🚀 Phase 2 Experiment Runner")
    print("=" * 50)
    
    runner = Phase2ExperimentRunner()
    all_results = []
    
    # Run focused experiments for underrepresented intent types
    priority_intents = ['self_query', 'why_question', 'next_action_query', 'project_query', 'constella_query', 'business_query', 'recent_changes_query']
    
    for intent_type in priority_intents:
        if intent_type in runner.experiment_queries:
            queries = random.sample(runner.experiment_queries[intent_type], 4)  # Test 4 queries per intent
            result = runner.run_intent_focus_experiment(intent_type, queries)
            all_results.append(result)
            
            # Brief pause between experiments
            time.sleep(2)
    
    # Run multi-intent experiments
    multi_result = runner.run_multi_intent_experiment()
    all_results.append(multi_result)
    
    # Run ALIFE performance experiments
    alife_result = runner.run_alife_performance_experiment()
    all_results.append(alife_result)
    
    # Analyze all results
    analysis = runner.analyze_experiment_results(all_results)
    
    # Generate and save report
    report = runner.generate_experiment_report(all_results, analysis)
    report_file = runner.save_experiment_report(report)
    
    # Summary
    print(f"\n🎉 Experiment Summary:")
    print(f"   Total experiments: {analysis['total_experiments']}")
    print(f"   Total queries: {analysis['total_queries']}")
    print(f"   Success rate: {analysis['overall_success_rate']:.1f}%")
    print(f"   Intent types tested: {len(analysis['intent_types_tested'])}")
    print(f"   Samples added: {analysis['total_successful']}")
    
    print(f"\n📊 Data Collection Progress:")
    print(f"   New samples: {analysis['total_successful']}")
    print(f"   Report saved: {report_file}")
    
    return analysis

if __name__ == "__main__":
    main()
