"""
FAITHH Phase 2 - Weight Optimization Engine
Uses machine learning to optimize chip fusion weights based on performance data.
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ml.performance_tracker import performance_tracker, QueryPerformance

class WeightOptimizer:
    """Machine learning-based weight optimization for chip fusion"""
    
    def __init__(self, model_path: str = "/home/jonat/ai-stack/models"):
        self.model_path = model_path
        self.model = None
        self.feature_columns = [
            'response_time', 'accuracy_score', 'coherence_score', 'success',
            'context_tokens', 'intent_type', 'model_used', 'provider_used'
        ]
        self.weight_columns = [
            'rag_search', 'google_search', 'decisions', 'constella', 
            'conversation_history', 'self_awareness', 'project_structure', 'scaffolding'
        ]
        self.is_trained = False
        self._ensure_model_directory()
    
    def _ensure_model_directory(self):
        """Ensure model directory exists"""
        os.makedirs(self.model_path, exist_ok=True)
    
    def prepare_training_data(self, days: int = 30) -> Tuple[List[Dict], List[float]]:
        """Prepare training data from performance history"""
        print(f"📊 Preparing training data from last {days} days...")
        
        # Get performance data
        performance_data = performance_tracker.get_weight_optimization_data(days)
        
        if not performance_data:
            print("⚠️ No performance data available for training")
            return [], []
        
        features = []
        targets = []
        
        for record in performance_data:
            # Extract features from performance record
            features.append(self._extract_features(record))
            
            # Target is a combination of performance metrics
            # Lower response time, higher accuracy, higher coherence, higher success
            target_score = (
                0.4 * (1.0 / max(record['response_time'], 0.1)) +  # Response time (inverse)
                0.3 * (record['accuracy_score'] or 0.5) +              # Accuracy
                0.2 * (record['coherence_score'] or 0.5) +              # Coherence
                0.1 * (1.0 if record['success'] else 0.0)               # Success
            )
            
            targets.append(target_score)
        
        print(f"📈 Prepared {len(features)} training samples")
        return features, targets
    
    def _extract_features(self, record: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from performance record"""
        features = {}
        
        # Performance metrics
        features['response_time'] = record['response_time']
        features['accuracy_score'] = record['accuracy_score'] or 0.5
        features['coherence_score'] = record['coherence_score'] or 0.5
        features['success'] = 1.0 if record['success'] else 0.0
        features['context_tokens'] = record.get('context_tokens', 0)
        
        # Intent features (one-hot encoded)
        intent = record.get('intent', {})
        intent_types = ['is_alife_query', 'is_self_query', 'is_why_question', 'is_next_action_query', 
                         'is_project_query', 'is_constella_query', 'is_business_query', 'is_recent_changes_query']
        
        for intent_type in intent_types:
            features[f'intent_{intent_type}'] = 1.0 if intent.get(intent_type, False) else 0.0
        
        # Model features (one-hot encoded)
        model_used = record.get('model_used', 'unknown')
        common_models = ['qwen25-grounded', 'llama3.3', 'deepseek-r1:32b']
        
        for model in common_models:
            features[f"model_{model.replace(':', '_')}"] = 1.0 if model_used == model else 0.0
        
        # Provider features (one-hot encoded)
        provider_used = record.get('provider_used', 'unknown')
        common_providers = ['ollama', 'groq', 'anthropic']
        
        for provider in common_providers:
            features[f'provider_{provider}'] = 1.0 if provider_used == provider else 0.0
        
        # Current weights (for learning from current state)
        weights_used = record.get('weights_used', {})
        for weight_name in self.weight_columns:
            features[f'weight_{weight_name}'] = weights_used.get(weight_name, 0.0)
        
        return features
    
    def train_model(self, days: int = 30) -> bool:
        """Train weight optimization model"""
        print(f"🤖️ Training weight optimization model...")
        
        # Prepare training data
        features, targets = self.prepare_training_data(days)
        
        if len(features) < 50:
            print("⚠️ Insufficient training data (need at least 50 samples)")
            return False
        
        # Convert to numpy arrays
        X = np.array([list(f.values()) for f in features])
        y = np.array(targets)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        try:
            # Try Random Forest first (usually performs better for this type of data)
            print("   Training Random Forest model...")
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            print(f"   Training R²: {train_score:.4f}")
            print(f"   Test R²: {test_score:.4f}")
            
            if test_score < 0.1:  # Very low score, try linear regression
                print("   Random Forest score too low, trying Linear Regression...")
                self.model = LinearRegression()
                self.model.fit(X_train, y_train)
                train_score = self.model.score(X_train, y_train)
                test_score = self.model.score(X_test, y_test)
                print(f"   Linear Regression R²: {train_score:.4f}")
                print(f"   Linear Regression Test R²: {test_score:.4f}")
            
            # Save model
            model_file = os.path.join(self.model_path, 'weight_optimizer.joblib')
            joblib.dump(self.model, model_file)
            
            self.is_trained = True
            print(f"✅ Model saved to {model_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load trained model"""
        model_file = os.path.join(self.model_path, 'weight_optimizer.joblib')
        
        if not os.path.exists(model_file):
            print(f"⚠️ No trained model found at {model_file}")
            return False
        
        try:
            self.model = joblib.load(model_file)
            self.is_trained = True
            print(f"✅ Loaded model from {model_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def predict_optimal_weights(self, query_features: Dict[str, Any]) -> Dict[str, float]:
        """Predict optimal weights for given query features"""
        if not self.is_trained:
            print("⚠️ Model not trained, using default weights")
            return self._get_default_weights()
        
        try:
            # Extract features in correct order
            feature_vector = []
            for col in self.feature_columns:
                feature_vector.append(query_features.get(col, 0.0))
            
            # Add missing features with defaults
            while len(feature_vector) < len(self.feature_columns):
                feature_vector.append(0.0)
            
            # Predict
            if len(feature_vector) != len(self.feature_columns):
                print(f"⚠️ Feature vector length mismatch: {len(feature_vector)} vs {len(self.feature_columns)}")
                return self._get_default_weights()
            
            # Predict optimization delta
            predicted_delta = self.model.predict([feature_vector])[0]
            
            # Get default weights and apply optimization
            default_weights = self._get_default_weights()
            optimized_weights = {}
            
            for i, weight_name in enumerate(self.weight_columns):
                if i < len(predicted_delta):
                    # Apply delta to default weight (with bounds)
                    current_weight = default_weights.get(weight_name, 0.0)
                    optimized_weight = max(0.0, min(1.0, current_weight + predicted_delta[i]))
                    optimized_weights[weight_name] = optimized_weight
                else:
                    optimized_weights[weight_name] = default_weights.get(weight_name, 0.0)
            
            # Normalize weights to sum to 1.0
            total_weight = sum(optimized_weights.values())
            if total_weight > 0:
                for weight_name in optimized_weights:
                    optimized_weights[weight_name] /= total_weight
            
            return optimized_weights
            
        except Exception as e:
            print(f"❌ Error predicting weights: {e}")
            return self._get_default_weights()
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Get default weight configuration"""
        return {
            'rag_search': 0.7,
            'google_search': 0.75,
            'decisions': 0.8,
            'constella': 0.75,
            'conversation_history': 0.6,
            'self_awareness': 0.5,
            'project_structure': 0.4,
            'scaffolding': 0.3
        }
    
    def optimize_weights_for_query(self, query_text: str, intent: Dict[str, Any], 
                                 current_weights: Dict[str, float]) -> Dict[str, float]:
        """Optimize weights for a specific query"""
        # Extract features for this query
        query_features = {
            'response_time': 0.0,  # Will be estimated
            'accuracy_score': 0.0,  # Will be estimated
            'coherence_score': 0.0,  # Will be estimated
            'success': 1.0,  # Assume success
            'context_tokens': len(query_text) // 4,  # Rough estimate
        }
        
        # Add intent features
        for key, value in intent.items():
            if key.startswith('is_'):
                query_features[f'intent_{key}'] = 1.0 if value else 0.0
        
        # Add model and provider features (defaults)
        query_features['model_qwen25_grounded'] = 1.0
        query_features['provider_ollama'] = 1.0
        
        # Add current weights
        for weight_name, weight_value in current_weights.items():
            query_features[f'weight_{weight_name}'] = weight_value
        
        # Predict optimal weights
        optimized_weights = self.predict_optimal_weights(query_features)
        
        return optimized_weights
    
    def evaluate_optimization(self, old_weights: Dict[str, float], 
                            new_weights: Dict[str, float],
                            performance_before: float,
                            performance_after: float) -> Dict[str, Any]:
        """Evaluate the results of weight optimization"""
        performance_change = performance_after - performance_before
        accuracy_improvement = 0.0
        
        # Calculate improvement metrics
        metrics = {
            'performance_change': performance_change,
            'performance_improvement': performance_change > 0,
            'weight_changes': {},
            'significant_change': abs(performance_change) > 0.05
        }
        
        # Calculate weight changes
        for weight_name in self.weight_columns:
            old_val = old_weights.get(weight_name, 0.0)
            new_val = new_weights.get(weight_name, 0.0)
            change = new_val - old_val
            metrics['weight_changes'][weight_name] = {
                'old': old_val,
                'new': new_val,
                'change': change,
                'percent_change': (change / old_val * 100) if old_val != 0 else 0
            }
        
        # Record optimization
        performance_tracker.record_weight_optimization(
            old_weights, new_weights, performance_change, accuracy_improvement
        )
        
        return metrics
    
    def get_optimization_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get history of weight optimizations"""
        try:
            with sqlite3.connect(performance_tracker.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                cursor.execute("""
                    SELECT timestamp, old_weights, new_weights, performance_change, accuracy_improvement
                    FROM weight_optimizations
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (cutoff_date.isoformat(),))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'timestamp': datetime.fromisoformat(row[0]),
                        'old_weights': json.loads(row[1]),
                        'new_weights': json.loads(row[2]),
                        'performance_change': row[3],
                        'accuracy_improvement': row[4]
                    })
                
                return results
                
        except Exception as e:
            print(f"❌ Error getting optimization history: {e}")
            return []
    
    def get_optimization_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get optimization statistics"""
        history = self.get_optimization_history(days)
        
        if not history:
            return {'total_optimizations': 0}
        
        total_optimizations = len(history)
        successful_optimizations = sum(1 for h in history if h['performance_change'] > 0)
        avg_improvement = np.mean([h['performance_change'] for h in history]) if history else 0
        
        return {
            'total_optimizations': total_optimizations,
            'successful_optimizations': successful_optimizations,
            'success_rate': (successful_optimizations / total_optimizations * 100) if total_optimizations > 0 else 0,
            'avg_improvement': avg_improvement,
            'period_days': days
        }

# Global instance
weight_optimizer = WeightOptimizer()
