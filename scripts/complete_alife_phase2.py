#!/usr/bin/env python3
"""
Complete ALIFE Phase 2 Data Collection

Target: Complete remaining 19 samples to reach 50 total
Current: 31/50 samples (62% complete)
Goal: 50/50 samples (100% complete)
"""

import sys
import os
import json
import random
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add ALIFE project to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'projects', 'alife'))

from projects.alife.faithh_observer import PulseWatcher

def generate_phase2_queries():
    """Generate remaining Phase 2 data collection queries"""
    
    # Current intent coverage from previous session
    current_coverage = {
        'alife_query': 17,
        'why_question': 5, 
        'constella_query': 4,
        'project_query': 3,
        'reasoning': 3,
        'complex_query': 1
    }
    
    # Target balanced distribution for remaining 19 samples
    target_distribution = {
        'alife_query': 6,      # Total: 23
        'why_question': 4,     # Total: 9
        'constella_query': 3,  # Total: 7
        'project_query': 3,    # Total: 6
        'reasoning': 2,        # Total: 5
        'complex_query': 1      # Total: 2
    }
    
    # Generate specific queries for each intent type
    queries = []
    
    # ALIFE queries (6 samples)
    alife_queries = [
        "What mathematical patterns emerged in the cognitive specialization experiment?",
        "How did Fibonacci frequency zones affect agent population dynamics?",
        "What energy economics trade-offs did specialized agents exhibit?",
        "Compare cognitive specialization results across different Fibonacci zones",
        "What evolutionary pressures drove mathematical cognition development?",
        "How sustainable are cognitive specializations over long-term simulations?"
    ]
    
    # Why questions (4 samples)
    why_queries = [
        "Why did cognitive specialization emerge at tick 200 specifically?",
        "Why do agents prefer certain Fibonacci zones over others?",
        "Why is mathematical cognition evolutionarily advantageous?",
        "Why did energy economics balance intelligence vs reproduction?"
    ]
    
    # Constella queries (3 samples)
    constella_queries = [
        "How can ALIFE insights inform Constella community framework design?",
        "What patterns from cognitive specialization apply to community development?",
        "How can mathematical cognition research enhance civic engagement?"
    ]
    
    # Project queries (3 samples)
    project_queries = [
        "What are the next experiments after cognitive specialization breakthrough?",
        "How should ALIFE project roadmap be updated based on Experiment 6 results?",
        "What resources are needed for Experiment 7: Social Cognition?"
    ]
    
    # Reasoning queries (2 samples)
    reasoning_queries = [
        "If cognitive specialization is successful, what does this imply about mathematical cognition evolution?",
        "Given the Fibonacci pattern results, what other mathematical concepts could evolve?"
    ]
    
    # Complex queries (1 sample)
    complex_queries = [
        "Analyze the relationship between Fibonacci zone specialization, energy economics, and long-term population sustainability in cognitive agents, and propose implications for both artificial intelligence research and mathematical education frameworks"
    ]
    
    # Combine all queries
    all_queries = (
        alife_queries + 
        why_queries + 
        constella_queries + 
        project_queries + 
        reasoning_queries + 
        complex_queries
    )
    
    # Shuffle for variety
    random.shuffle(all_queries)
    
    return all_queries

def complete_phase2_data_collection():
    """Execute Phase 2 data collection completion"""
    
    print("🔬 ALIFE Phase 2 Data Collection - Completion Session")
    print(f"📊 Target: Complete remaining 19 samples (31/50 → 50/50)")
    print(f"🎯 Goal: 100% Phase 2 completion")
    print()
    
    # Initialize observer
    observer = PulseWatcher()
    
    # Generate queries
    queries = generate_phase2_queries()
    print(f"📝 Generated {len(queries)} queries for completion")
    print()
    
    # Execute data collection
    results = []
    success_count = 0
    
    for i, query in enumerate(queries, 1):
        print(f"🔄 Sample {31+i}/50: {query[:50]}...")
        
        try:
            # Execute query with FAITHH
            response = observer.observe_lineage(query)
            
            if response and response.get('success'):
                results.append({
                    'sample_number': 31 + i,
                    'query': query,
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                })
                success_count += 1
                print(f"   ✅ Success")
            else:
                print(f"   ❌ Failed: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            
        print()
    
    # Save results
    output_file = Path("/home/jonat/ai-stack/ml/training_data/alife_phase2_completion.json")
    
    completion_data = {
        'session_info': {
            'date': datetime.now().isoformat(),
            'purpose': 'Phase 2 data collection completion',
            'target_samples': 19,
            'successful_samples': success_count,
            'previous_total': 31,
            'new_total': 31 + success_count,
            'completion_rate': f"{((31 + success_count) / 50) * 100:.1f}%"
        },
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(completion_data, f, indent=2)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    print(f"📊 Session Summary:")
    print(f"   Target: 19 samples")
    print(f"   Successful: {success_count} samples")
    print(f"   Previous Total: 31 samples")
    print(f"   New Total: {31 + success_count} samples")
    print(f"   Completion Rate: {((31 + success_count) / 50) * 100:.1f}%")
    
    if success_count >= 15:  # At least 79% success rate
        print(f"   🎉 Phase 2 Data Collection: {'COMPLETE' if (31 + success_count) >= 50 else 'NEARLY COMPLETE'}")
    else:
        print(f"   ⚠️ Phase 2 Data Collection: IN PROGRESS - may need additional session")
    
    return success_count

def update_ml_training_data():
    """Update ML training data with new samples"""
    
    print("🔄 Updating ML training data with new Phase 2 samples...")
    
    # This would integrate the new samples into the training dataset
    # For now, we'll just note that this step needs to be done
    
    training_data_path = Path("/home/jonat/ai-stack/ml/training_data/")
    latest_metadata = None
    
    # Find latest metadata file
    metadata_files = list(training_data_path.glob("alife_metadata_*.json"))
    if metadata_files:
        latest_metadata = max(metadata_files, key=lambda x: x.stat().st_mtime)
        print(f"📄 Latest metadata: {latest_metadata.name}")
    
    print("📝 Next step: Integrate new samples into training pipeline")
    print("🔄 Action needed: Re-run training data preparation script")
    
    return latest_metadata

def main():
    """Main execution function"""
    
    print("🚀 ALIFE Phase 2 Data Collection Completion")
    print("=" * 50)
    
    # Complete Phase 2 data collection
    success_count = complete_phase2_data_collection()
    
    # Update ML training data
    update_ml_training_data()
    
    print()
    print("🎯 Next Steps:")
    if success_count >= 15:
        print("   ✅ Phase 2 data collection complete or nearly complete")
        print("   🔄 Update ML training pipeline with new data")
        print("   🔬 Design Experiment 7: Social Cognition")
        print("   🚀 Begin Phase 5.1: Program Advance integration planning")
    else:
        print("   ⚠️ Phase 2 data collection needs additional session")
        print("   🔄 Investigate query execution issues")
        print("   📝 Retry failed queries in next session")
    
    print()
    print("🎉 Session Complete!")

if __name__ == "__main__":
    main()
