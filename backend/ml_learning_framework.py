"""
ML Learning Framework for FAITHH
Extends coherence arbiter pattern to create self-learning, adaptive systems
"""

import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import hashlib
import logging
import os

# Set up logging for adaptation failures
logging.basicConfig(level=logging.INFO)
adaptation_logger = logging.getLogger('ml_adaptation')

# Add file handler for adaptation failures
_log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'adaptation_failures.log')
os.makedirs(os.path.dirname(_log_path), exist_ok=True)
_fh = logging.FileHandler(_log_path)
_fh.setLevel(logging.WARNING)
adaptation_logger.addHandler(_fh)

@dataclass
class LearningNode:
    """A learning node that can adapt and optimize based on usage patterns"""
    id: str
    type: str  # 'ui_layout', 'model_config', 'coherence_threshold', 'routing_strategy'
    current_state: Dict[str, Any]
    performance_metrics: Dict[str, float]
    learning_history: List[Dict[str, Any]]
    last_updated: datetime
    adaptation_rate: float = 0.1  # How quickly to adapt
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningNode':
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

class MLLearningFramework:
    """Main framework for managing learning nodes and adaptive behavior"""
    
    def __init__(self):
        self.nodes: Dict[str, LearningNode] = {}
        self.global_metrics = defaultdict(list)
        self.learning_strategies = {
            'ui_layout': UILayoutLearningStrategy(),
            'model_config': ModelConfigLearningStrategy(),
            'coherence_threshold': CoherenceThresholdLearningStrategy(),
            'routing_strategy': RoutingStrategyLearningStrategy()
        }
        self.load_nodes()
    
    def create_node(self, node_type: str, config: Dict[str, Any]) -> str:
        """Create a new learning node"""
        node_id = f"{node_type}_{int(time.time())}_{hashlib.md5(json.dumps(config).encode()).hexdigest()[:8]}"
        
        node = LearningNode(
            id=node_id,
            type=node_type,
            current_state=config,
            performance_metrics={'accuracy': 0.0, 'efficiency': 0.0, 'user_satisfaction': 0.0},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        self.nodes[node_id] = node
        self.save_nodes()
        
        print(f"🧠 Created learning node: {node_id} (type: {node_type})")
        return node_id
    
    def update_node_performance(self, node_id: str, metrics: Dict[str, float], context: Dict[str, Any] = None):
        """Update performance metrics for a learning node"""
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        
        # Update performance metrics
        for key, value in metrics.items():
            if key in node.performance_metrics:
                # Exponential moving average
                node.performance_metrics[key] = (
                    node.performance_metrics[key] * (1 - node.adaptation_rate) + 
                    value * node.adaptation_rate
                )
            else:
                node.performance_metrics[key] = value
        
        # Record learning event
        learning_event = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics.copy(),
            'context': context or {},
            'previous_state': node.current_state.copy()
        }
        
        node.learning_history.append(learning_event)
        node.last_updated = datetime.now()
        
        # Trigger learning strategy
        strategy = self.learning_strategies.get(node.type)
        if strategy:
            try:
                new_state = strategy.learn(node, metrics, context)
                if new_state:
                    node.current_state = new_state
                    print(f"🎯 Node {node_id} adapted: {list(new_state.keys())[:3]}...")
                    adaptation_logger.info(f"adaptation_success", extra={
                        'node_id': node_id,
                        'node_type': node.type,
                        'adapted_keys': list(new_state.keys()),
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"⚠️  Strategy learning failed for node {node_id}: {e}")
                adaptation_logger.error(f"adaptation_failure", extra={
                    'node_id': node_id,
                    'node_type': node.type,
                    'error': str(e),
                    'metrics': metrics,
                    'context': context,
                    'timestamp': datetime.now().isoformat()
                })
                # Continue without adaptation - learning event was still recorded
        
        self.save_nodes()
        return True
    
    def get_node_recommendations(self, node_id: str) -> List[Dict[str, Any]]:
        """Get learning recommendations for a node"""
        if node_id not in self.nodes:
            return []
        
        node = self.nodes[node_id]
        strategy = self.learning_strategies.get(node.type)
        
        if strategy:
            return strategy.get_recommendations(node)
        
        return []
    
    def analyze_global_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across all learning nodes"""
        analysis = {
            'total_nodes': len(self.nodes),
            'node_types': defaultdict(int),
            'performance_trends': {},
            'adaptation_events': 0,
            'insights': []
        }
        
        for node in self.nodes.values():
            analysis['node_types'][node.type] += 1
            analysis['adaptation_events'] += len(node.learning_history)
            
            # Track performance trends
            for metric, value in node.performance_metrics.items():
                if metric not in analysis['performance_trends']:
                    analysis['performance_trends'][metric] = []
                analysis['performance_trends'][metric].append(value)
        
        # Calculate averages and insights
        for metric, values in analysis['performance_trends'].items():
            if values:
                analysis['performance_trends'][metric] = {
                    'average': np.mean(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'std': np.std(values)
                }
        
        return analysis
    
    def save_nodes(self):
        """Save all learning nodes to disk"""
        nodes_data = {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        
        try:
            with open('ml_learning_nodes.json', 'w') as f:
                json.dump(nodes_data, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error saving learning nodes: {e}")
    
    def load_nodes(self):
        """Load learning nodes from disk"""
        try:
            with open('ml_learning_nodes.json', 'r') as f:
                nodes_data = json.load(f)
            
            for node_id, node_data in nodes_data.items():
                self.nodes[node_id] = LearningNode.from_dict(node_data)
            
            print(f"📚 Loaded {len(self.nodes)} learning nodes")
        except FileNotFoundError:
            print("📚 No existing learning nodes found")
        except Exception as e:
            print(f"❌ Error loading learning nodes: {e}")

class LearningStrategy:
    """Base class for learning strategies"""
    
    def learn(self, node: LearningNode, metrics: Dict[str, float], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn from performance metrics and return new state"""
        raise NotImplementedError
    
    def get_recommendations(self, node: LearningNode) -> List[Dict[str, Any]]:
        """Get recommendations for improving the node"""
        raise NotImplementedError

class UILayoutLearningStrategy(LearningStrategy):
    """Learning strategy for UI layout optimization"""
    
    def learn(self, node: LearningNode, metrics: Dict[str, float], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn UI layout patterns from user interactions"""
        current_layout = node.current_state
        
        # Analyze user interaction patterns
        if 'user_satisfaction' in metrics and metrics['user_satisfaction'] < 0.7:
            # User is not satisfied, suggest layout changes
            new_layout = current_layout.copy()
            
            # Move frequently used elements to more prominent positions
            if 'element_usage' in context:
                usage_data = context['element_usage']
                for element, usage in usage_data.items():
                    if usage > 0.8:  # Frequently used
                        if element in new_layout:
                            new_layout[element]['priority'] = 'high'
                            new_layout[element]['position'] = 'prominent'
            
            return new_layout
        
        return None
    
    def get_recommendations(self, node: LearningNode) -> List[Dict[str, Any]]:
        """Get UI layout recommendations"""
        recommendations = []
        
        if node.performance_metrics.get('user_satisfaction', 0) < 0.6:
            recommendations.append({
                'type': 'layout_optimization',
                'priority': 'high',
                'description': 'Consider reorganizing UI based on usage patterns',
                'action': 'analyze_user_interactions'
            })
        
        return recommendations

class ModelConfigLearningStrategy(LearningStrategy):
    """Learning strategy for model configuration optimization"""
    
    def learn(self, node: LearningNode, metrics: Dict[str, float], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn optimal model configurations"""
        current_config = node.current_state
        
        # Adjust parameters based on performance
        new_config = current_config.copy()
        
        # If response time is too high, suggest smaller model
        if 'efficiency' in metrics and metrics['efficiency'] < 0.5:
            if 'model_size' in new_config:
                new_config['model_size'] = max(new_config['model_size'] * 0.8, 7)  # Don't go below 7B
        
        # If accuracy is low, suggest larger model
        if 'accuracy' in metrics and metrics['accuracy'] < 0.7:
            if 'model_size' in new_config:
                new_config['model_size'] = min(new_config['model_size'] * 1.2, 70)  # Don't exceed 70B
        
        return new_config if new_config != current_config else None
    
    def get_recommendations(self, node: LearningNode) -> List[Dict[str, Any]]:
        """Get model configuration recommendations"""
        recommendations = []
        
        efficiency = node.performance_metrics.get('efficiency', 0)
        accuracy = node.performance_metrics.get('accuracy', 0)
        
        if efficiency < 0.5 and accuracy < 0.7:
            recommendations.append({
                'type': 'model_optimization',
                'priority': 'high',
                'description': 'Current model is neither fast nor accurate - consider different architecture',
                'action': 'test_alternative_models'
            })
        elif efficiency < 0.5:
            recommendations.append({
                'type': 'performance_optimization',
                'priority': 'medium',
                'description': 'Consider smaller model or quantization',
                'action': 'optimize_model_size'
            })
        
        return recommendations

class CoherenceThresholdLearningStrategy(LearningStrategy):
    """Learning strategy for coherence threshold adaptation"""
    
    def learn(self, node: LearningNode, metrics: Dict[str, float], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn optimal coherence thresholds"""
        current_thresholds = node.current_state.copy()
        
        # Ensure thresholds exist
        if 'current_thresholds' not in current_thresholds:
            current_thresholds['current_thresholds'] = {
                'high_threshold': 0.6,
                'medium_threshold': 0.3,
                'anchor_validation_threshold': 0.7
            }
        
        thresholds = current_thresholds['current_thresholds']
        new_thresholds = thresholds.copy()
        
        # Adjust thresholds based on user feedback
        if 'user_satisfaction' in metrics:
            satisfaction = metrics['user_satisfaction']
            
            if satisfaction < 0.6:  # User not satisfied
                # Lower thresholds to be more permissive
                new_thresholds['high_threshold'] *= 0.9
                new_thresholds['medium_threshold'] *= 0.9
            elif satisfaction > 0.8:  # User very satisfied
                # Can be more strict
                new_thresholds['high_threshold'] *= 1.05
                new_thresholds['medium_threshold'] *= 1.05
        
        # Ensure thresholds stay in reasonable bounds
        new_thresholds['high_threshold'] = max(0.5, min(0.8, new_thresholds['high_threshold']))
        new_thresholds['medium_threshold'] = max(0.2, min(0.6, new_thresholds['medium_threshold']))
        
        current_thresholds['current_thresholds'] = new_thresholds
        return current_thresholds if new_thresholds != thresholds else None
    
    def get_recommendations(self, node: LearningNode) -> List[Dict[str, Any]]:
        """Get coherence threshold recommendations"""
        recommendations = []
        
        satisfaction = node.performance_metrics.get('user_satisfaction', 0)
        
        if satisfaction < 0.5:
            recommendations.append({
                'type': 'threshold_adjustment',
                'priority': 'high',
                'description': 'Coherence thresholds may be too strict',
                'action': 'lower_thresholds'
            })
        
        return recommendations

class RoutingStrategyLearningStrategy(LearningStrategy):
    """Learning strategy for routing strategy optimization"""
    
    def learn(self, node: LearningNode, metrics: Dict[str, float], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn optimal routing strategies"""
        current_strategy = node.current_state
        
        new_strategy = current_strategy.copy()
        
        # Adjust routing weights based on performance
        if 'provider_performance' in context:
            provider_perf = context['provider_performance']
            
            # Update provider weights based on performance
            for provider, perf in provider_perf.items():
                if f'{provider}_weight' in new_strategy:
                    # Higher performance = higher weight
                    new_strategy[f'{provider}_weight'] = min(1.0, perf * 1.2)
        
        return new_strategy if new_strategy != current_strategy else None
    
    def get_recommendations(self, node: LearningNode) -> List[Dict[str, Any]]:
        """Get routing strategy recommendations"""
        recommendations = []
        
        efficiency = node.performance_metrics.get('efficiency', 0)
        
        if efficiency < 0.6:
            recommendations.append({
                'type': 'routing_optimization',
                'priority': 'medium',
                'description': 'Consider adjusting provider selection strategy',
                'action': 'rebalance_provider_weights'
            })
        
        return recommendations

# Global learning framework instance
ml_framework = MLLearningFramework()

def get_ml_framework() -> MLLearningFramework:
    """Get the global ML learning framework"""
    return ml_framework

def create_learning_node(node_type: str, config: Dict[str, Any]) -> str:
    """Create a new learning node"""
    return ml_framework.create_node(node_type, config)

def update_node_performance(node_id: str, metrics: Dict[str, float], context: Dict[str, Any] = None) -> bool:
    """Update performance metrics for a learning node"""
    return ml_framework.update_node_performance(node_id, metrics, context)

def get_learning_recommendations(node_id: str) -> List[Dict[str, Any]]:
    """Get learning recommendations for a node"""
    return ml_framework.get_node_recommendations(node_id)

def analyze_ml_patterns() -> Dict[str, Any]:
    """Analyze patterns across all learning nodes"""
    return ml_framework.analyze_global_patterns()
