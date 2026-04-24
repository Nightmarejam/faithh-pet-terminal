"""
FAITHH Phase 3 - Predictive Routing System
Anticipate optimal chip combinations based on query patterns and performance history
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ml.performance_tracker import performance_tracker

class PredictiveRouter:
    """Predictive routing system for optimal chip combinations"""
    
    def __init__(self, model_path: str = "/home/jonat/ai-stack/models"):
        self.model_path = model_path
        self.model = None
        self.intent_encoder = LabelEncoder()
        self.provider_encoder = LabelEncoder()
        self.is_trained = False
        
        # Available chips for routing
        self.available_chips = [
            'rag_search', 'google_search', 'decisions', 'constella',
            'conversation_history', 'self_awareness', 'project_structure', 'scaffolding'
        ]
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
    
    def prepare_training_data(self, days: int = 30) -> Tuple[List[Dict], List[List[str]]]:
        """Prepare training data from performance history"""
        print(f"📊 Preparing predictive routing data from last {days} days...")
        
        # Get performance data
        performance_data = performance_tracker.get_weight_optimization_data(days)
        
        if not performance_data:
            print("❌ No performance data available for training")
            return [], []
        
        features = []
        optimal_combinations = []
        
        for record in performance_data:
            # Extract features
            feature = {
                'intent_type': record.get('intent_type', 'unknown'),
                'response_time': record.get('response_time', 0),
                'accuracy_score': record.get('accuracy_score', 0),
                'success': record.get('success', False),
                'context_tokens': record.get('context_tokens', 0),
                'model_used': record.get('model_used', 'unknown'),
                'provider_used': record.get('provider_used', 'unknown')
            }
            
            # Determine optimal chip combination based on performance
            weights_used = record.get('weights_used', {})
            if weights_used:
                # Sort chips by weight (top 3-4 chips considered optimal)
                sorted_chips = sorted(weights_used.items(), key=lambda x: x[1], reverse=True)
                optimal_chips = [chip for chip, weight in sorted_chips if weight > 0.1][:4]
            else:
                optimal_chips = ['rag_search']  # Default fallback
            
            features.append(feature)
            optimal_combinations.append(optimal_chips)
        
        print(f"✅ Prepared {len(features)} training examples")
        return features, optimal_combinations
    
    def extract_features(self, features: List[Dict]) -> np.ndarray:
        """Extract numerical features from training data"""
        
        if not features:
            return np.array([])
        
        # Encode categorical features
        intent_types = [f['intent_type'] for f in features]
        models = [f['model_used'] for f in features]
        providers = [f['provider_used'] for f in features]
        
        # Fit encoders
        self.intent_encoder.fit(intent_types + ['unknown'])
        self.provider_encoder.fit(providers + ['unknown'])
        
        # Extract numerical features
        numerical_features = []
        for feature in features:
            feature_vector = [
                float(self.intent_encoder.transform([feature['intent_type']])[0]),
                float(feature['response_time']),
                float(feature['accuracy_score'] or 0.0),
                float(feature['success']),
                float(feature['context_tokens']),
                float(self.provider_encoder.transform([feature['provider_used']])[0])
            ]
            numerical_features.append(feature_vector)
        
        return np.array(numerical_features)
    
    def train_model(self, days: int = 30) -> bool:
        """Train predictive routing model"""
        print(f"🤖 Training predictive routing model...")
        
        # Prepare training data
        features, optimal_combinations = self.prepare_training_data(days)
        
        if not features:
            print("❌ Insufficient training data")
            return False
        
        # Extract features
        X = self.extract_features(features)
        
        # Create target labels (chip combinations)
        # For simplicity, predict the primary chip
        y = [combo[0] if combo else 'rag_search' for combo in optimal_combinations]
        
        # Train Random Forest classifier
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.model.fit(X, y)
        self.is_trained = True
        
        # Save model
        model_file = os.path.join(self.model_path, 'predictive_router.joblib')
        joblib.dump(self.model, model_file)
        
        # Save encoders
        intent_encoder_file = os.path.join(self.model_path, 'intent_encoder.joblib')
        provider_encoder_file = os.path.join(self.model_path, 'provider_encoder.joblib')
        joblib.dump(self.intent_encoder, intent_encoder_file)
        joblib.dump(self.provider_encoder, provider_encoder_file)
        
        print(f"✅ Model saved to {model_file}")
        print(f"📊 Training accuracy: {self.model.score(X, y):.3f}")
        
        return True
    
    def load_model(self) -> bool:
        """Load trained model"""
        try:
            model_file = os.path.join(self.model_path, 'predictive_router.joblib')
            intent_encoder_file = os.path.join(self.model_path, 'intent_encoder.joblib')
            provider_encoder_file = os.path.join(self.model_path, 'provider_encoder.joblib')
            
            self.model = joblib.load(model_file)
            self.intent_encoder = joblib.load(intent_encoder_file)
            self.provider_encoder = joblib.load(provider_encoder_file)
            self.is_trained = True
            
            print("✅ Predictive routing model loaded")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def predict_optimal_chips(self, query_intent: Dict[str, Any], 
                             context_tokens: int = 0,
                             model_used: str = 'qwen25-grounded',
                             provider_used: str = 'ollama') -> List[str]:
        """Predict optimal chip combination for a query"""
        
        if not self.is_trained:
            if not self.load_model():
                return ['rag_search']  # Default fallback
        
        # Extract features
        intent_type = query_intent.get('intent_type', 'unknown')
        
        # Handle unknown intents
        if intent_type not in self.intent_encoder.classes_:
            intent_type = 'unknown'
        
        # Handle unknown providers
        if provider_used not in self.provider_encoder.classes_:
            provider_used = 'unknown'
        
        feature_vector = np.array([[
            float(self.intent_encoder.transform([intent_type])[0]),
            0.0,  # response_time (unknown for prediction)
            0.0,  # accuracy_score (unknown for prediction)
            1.0,  # success (assume success)
            float(context_tokens),
            float(self.provider_encoder.transform([provider_used])[0])
        ]])
        
        # Predict primary chip
        primary_chip = self.model.predict(feature_vector)[0]
        
        # Get prediction probabilities for confidence
        probabilities = self.model.predict_proba(feature_vector)[0]
        confidence = max(probabilities)
        
        # Build chip combination based on intent and confidence
        chip_combination = self._build_chip_combination(
            primary_chip, query_intent, confidence
        )
        
        return chip_combination
    
    def _build_chip_combination(self, primary_chip: str, 
                              query_intent: Dict[str, Any], 
                              confidence: float) -> List[str]:
        """Build optimal chip combination based on prediction and intent"""
        
        chips = [primary_chip]
        
        # Add secondary chips based on intent
        intent_type = query_intent.get('intent_type', 'unknown')
        
        if intent_type == 'alife_query':
            chips.extend(['rag_search', 'decisions'])
        elif intent_type == 'business_query':
            chips.extend(['rag_search', 'project_structure'])
        elif intent_type == 'constella_query':
            chips.extend(['rag_search', 'constella'])
        elif intent_type == 'project_query':
            chips.extend(['project_structure', 'scaffolding'])
        elif intent_type == 'why_question':
            chips.extend(['rag_search', 'decisions'])
        elif intent_type == 'complex_query':
            chips.extend(['rag_search', 'conversation_history'])
        elif intent_type == 'recent_changes_query':
            chips.extend(['rag_search', 'project_structure'])
        else:
            chips.append('rag_search')
        
        # Remove duplicates and limit to 4 chips
        chips = list(dict.fromkeys(chips))  # Remove duplicates while preserving order
        return chips[:4]
    
    def get_routing_confidence(self, query_intent: Dict[str, Any]) -> float:
        """Get confidence score for routing prediction"""
        
        if not self.is_trained:
            return 0.5  # Default confidence
        
        try:
            # Extract features
            intent_type = query_intent.get('intent_type', 'unknown')
            if intent_type not in self.intent_encoder.classes_:
                return 0.5
            
            feature_vector = np.array([[
                float(self.intent_encoder.transform([intent_type])[0]),
                0.0, 0.0, 1.0, 0.0,
                float(self.provider_encoder.transform(['ollama'])[0])
            ]])
            
            probabilities = self.model.predict_proba(feature_vector)[0]
            return max(probabilities)
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.5
    
    def test_predictions(self, test_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test predictive routing on sample queries"""
        
        print("🧪 Testing predictive routing...")
        
        results = []
        for i, query in enumerate(test_queries):
            intent = query.get('intent', {})
            predicted_chips = self.predict_optimal_chips(intent)
            confidence = self.get_routing_confidence(intent)
            
            result = {
                'query': query.get('message', ''),
                'predicted_chips': predicted_chips,
                'confidence': confidence,
                'intent_type': intent.get('intent_type', 'unknown')
            }
            results.append(result)
            
            print(f"  Query {i+1}: {intent.get('intent_type', 'unknown')}")
            print(f"    Predicted chips: {predicted_chips}")
            print(f"    Confidence: {confidence:.3f}")
        
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        return {
            'results': results,
            'avg_confidence': avg_confidence,
            'total_queries': len(results)
        }

def main():
    """Main predictive routing execution"""
    
    print("🚀 Phase 3 Predictive Routing Implementation")
    print("=" * 60)
    
    # Initialize predictive router
    router = PredictiveRouter()
    
    # Train model
    success = router.train_model(days=30)
    
    if not success:
        print("❌ Model training failed")
        return False
    
    # Test with sample queries
    test_queries = [
        {
            'message': 'What were the key findings of Experiment 6?',
            'intent': {'intent_type': 'alife_query'}
        },
        {
            'message': 'How should I structure pricing for my business?',
            'intent': {'intent_type': 'business_query'}
        },
        {
            'message': 'What changed in the ALIFE infrastructure?',
            'intent': {'intent_type': 'recent_changes_query'}
        },
        {
            'message': 'What should I do next in this project?',
            'intent': {'intent_type': 'project_query'}
        }
    ]
    
    test_results = router.test_predictions(test_queries)
    
    print(f"\n🎯 Predictive Routing Results:")
    print(f"  Average Confidence: {test_results['avg_confidence']:.3f}")
    print(f"  Queries Tested: {test_results['total_queries']}")
    print(f"  Model Status: {'✅ Trained' if router.is_trained else '❌ Not trained'}")
    
    return router.is_trained

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
