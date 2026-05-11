#!/usr/bin/env python3
"""
Phase 2 Model Training Script
Trains machine learning models for weight optimization and intent detection.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime
import json

def train_weight_optimizer():
    """Train the weight optimization model"""
    print("🤖 Training Phase 2 Weight Optimization Model")
    print("=" * 50)
    
    try:
        from backend.ml.weight_optimizer import weight_optimizer
        
        # Train with 30 days of data
        success = weight_optimizer.train_model(days=30)
        
        if success:
            print("✅ Weight optimization model trained successfully")
            
            # Get training statistics
            stats = weight_optimizer.get_optimization_stats(days=30)
            print(f"📊 Training stats: {json.dumps(stats, indent=2)}")
        else:
            print("❌ Weight optimization model training failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Error training weight optimizer: {e}")
        return False

def test_semantic_intent_detector():
    """Test the semantic intent detector"""
    print("\n🧠 Testing Phase 2 Semantic Intent Detector")
    print("=" * 50)
    
    try:
        from backend.ml.semantic_intent_detector import semantic_intent_detector
        
        # Test queries
        test_queries = [
            "What is the status of Experiment 4?",
            "How does FAITHH maintain project coherence?",
            "Why did we choose this architecture?",
            "What should I do next in this project?",
            "Tell me about the Constella framework"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            result = semantic_intent_detector.detect_intent(query)
            
            detected_intents = [key for key, value in result.items() if key.startswith('is_') and value]
            confidence = result.get('semantic_confidence', 0)
            detected_by = result.get('detected_by', 'regex')
            
            print(f"   Detected intents: {detected_intents}")
            print(f"   Method: {detected_by}")
            print(f"   Confidence: {confidence:.3f}")
        
        # Get statistics
        stats = semantic_intent_detector.get_intent_statistics()
        print(f"\n📊 Intent detector stats: {json.dumps(stats, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing semantic intent detector: {e}")
        return False

def test_performance_tracking():
    """Test the performance tracking system"""
    print("\n📊 Testing Phase 2 Performance Tracking")
    print("=" * 50)
    
    try:
        from backend.ml.performance_tracker import performance_tracker, QueryPerformance
        
        # Create a test performance record
        test_record = QueryPerformance(
            query_id="test_query_001",
            timestamp=datetime.now(),
            intent={'is_alife_query': True, 'semantic_confidence': 0.85},
            weights_used={'rag_search': 0.9, 'scaffolding': 0.1},
            chip_results={'rag_search': 'test context', 'scaffolding': 'test scaffolding'},
            response_time=1.5,
            model_used='qwen25-grounded',
            provider_used='ollama',
            accuracy_score=0.9,
            user_feedback='good',
            context_tokens=500,
            coherence_score=0.8,
            success=True,
            error_info=None
        )
        
        # Track the test record
        success = performance_tracker.track_query(test_record)
        
        if success:
            print("✅ Performance tracking test successful")
            
            # Get recent performance
            recent = performance_tracker.get_recent_performance(limit=5)
            print(f"📈 Recent performance records: {len(recent)}")
            
            # Get performance summary
            summary = performance_tracker.get_performance_summary(days=7)
            print(f"📊 Performance summary: {json.dumps(summary, indent=2)}")
        else:
            print("❌ Performance tracking test failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Error testing performance tracking: {e}")
        return False

def run_integration_test():
    """Run integration test with all Phase 2 components"""
    print("\n🔗 Running Phase 2 Integration Test")
    print("=" * 50)
    
    try:
        from backend.enhanced_chip_integration import build_enhanced_context
        from backend.intent_detection import detect_query_intent
        
        # Test query
        test_query = "What is the status of the ALIFE experiments?"
        test_intent = detect_query_intent(test_query)
        
        # Mock chip results
        mock_chip_results = {
            'rag': ('Test RAG context about ALIFE experiments', ['doc1', 'doc2'], 'rag_search'),
            'scaffolding': ('Test scaffolding context', 'scaffolding'),
            'project_structure': ('Test project structure', 'project_structure')
        }
        
        # Build enhanced context
        result = build_enhanced_context(
            query_text=test_query,
            intent=test_intent,
            chip_results=mock_chip_results,
            session_id='test_session_001',
            model_used='qwen25-grounded',
            provider_used='ollama'
        )
        
        print("✅ Integration test successful")
        print(f"📝 Context length: {len(result['context'])}")
        print(f"🔧 Method used: {result['metrics']['method']}")
        print(f"🧠 Phase 2 optimization: {result.get('phase2_optimization', {}).get('performance_tracked', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main training and testing function"""
    print("🚀 FAITHH Phase 2 Training & Testing")
    print("=" * 60)
    
    results = {
        'weight_optimizer': False,
        'semantic_intent': False,
        'performance_tracking': False,
        'integration_test': False
    }
    
    # Train weight optimizer
    results['weight_optimizer'] = train_weight_optimizer()
    
    # Test semantic intent detector
    results['semantic_intent'] = test_semantic_intent_detector()
    
    # Test performance tracking
    results['performance_tracking'] = test_performance_tracking()
    
    # Run integration test
    results['integration_test'] = run_integration_test()
    
    # Summary
    print(f"\n🎉 Phase 2 Training & Testing Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All Phase 2 components are ready!")
        print("🚀 Ready to enable Phase 2 intelligence features")
    else:
        print("⚠️ Some components need attention before Phase 2 activation")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()
