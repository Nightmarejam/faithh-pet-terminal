"""
UI Layout Learning Node for FAITHH
Learns optimal UI layouts based on user interaction patterns
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, Counter

class UILayoutOptimizer:
    """Optimizes UI layout based on user behavior and preferences"""
    
    def __init__(self):
        self.interaction_data = defaultdict(list)
        self.layout_configs = {}
        self.performance_metrics = defaultdict(dict)
        self.load_data()
    
    def record_interaction(self, element_id: str, interaction_type: str, context: Dict[str, Any] = None):
        """Record a user interaction with a UI element"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'context': context or {},
            'session_id': context.get('session_id') if context else None
        }
        
        self.interaction_data[element_id].append(interaction)
        self.save_data()
    
    def analyze_usage_patterns(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze usage patterns over a time window"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        patterns = {
            'most_used_elements': [],
            'least_used_elements': [],
            'interaction_sequences': [],
            'peak_usage_times': [],
            'element_clusters': {}
        }
        
        # Count interactions per element
        element_counts = Counter()
        element_types = defaultdict(Counter)
        
        for element_id, interactions in self.interaction_data.items():
            recent_interactions = [
                i for i in interactions 
                if datetime.fromisoformat(i['timestamp']) > cutoff_time
            ]
            
            if recent_interactions:
                element_counts[element_id] = len(recent_interactions)
                
                # Track interaction types
                for interaction in recent_interactions:
                    element_types[element_id][interaction['type']] += 1
        
        # Most and least used elements
        if element_counts:
            patterns['most_used_elements'] = element_counts.most_common(10)
            patterns['least_used_elements'] = element_counts.most_common()[-10:]
        
        # Element type analysis
        patterns['element_types'] = {
            element: dict(types) 
            for element, types in element_types.items()
        }
        
        return patterns
    
    def generate_optimal_layout(self, current_layout: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an optimized layout based on usage patterns"""
        patterns = self.analyze_usage_patterns()
        optimal_layout = current_layout.copy()
        
        # Get most used elements
        most_used = [elem[0] for elem in patterns['most_used_elements'][:5]]
        
        # Promote frequently used elements
        for element_id in most_used:
            if element_id in optimal_layout:
                element_config = optimal_layout[element_id]
                
                # Move to more prominent position
                if element_config.get('position') == 'sidebar':
                    element_config['position'] = 'main'
                    element_config['priority'] = 'high'
                
                # Increase visibility
                if element_config.get('visibility') == 'collapsed':
                    element_config['visibility'] = 'expanded'
                
                # Optimize size
                if 'size' in element_config:
                    element_config['size'] = 'large'
        
        # Demote least used elements
        least_used = [elem[0] for elem in patterns['least_used_elements'][-5:]]
        
        for element_id in least_used:
            if element_id in optimal_layout:
                element_config = optimal_layout[element_id]
                
                # Move to less prominent position
                if element_config.get('position') == 'main':
                    element_config['position'] = 'sidebar'
                    element_config['priority'] = 'low'
                
                # Consider hiding very unused elements
                if patterns['least_used_elements'][-1][1] < 2:  # Used less than 2 times
                    element_config['visibility'] = 'collapsed'
        
        return optimal_layout
    
    def create_adaptive_layout_system(self) -> Dict[str, Any]:
        """Create an adaptive layout system that can learn and evolve"""
        layout_system = {
            'current_layout': {
                'coherence_indicator': {
                    'position': 'main',
                    'priority': 'high',
                    'visibility': 'expanded',
                    'size': 'medium'
                },
                'chat_interface': {
                    'position': 'main',
                    'priority': 'high',
                    'visibility': 'expanded',
                    'size': 'large'
                },
                'rag_panel': {
                    'position': 'sidebar',
                    'priority': 'medium',
                    'visibility': 'collapsed',
                    'size': 'medium'
                },
                'pulse_dashboard': {
                    'position': 'sidebar',
                    'priority': 'medium',
                    'visibility': 'collapsed',
                    'size': 'medium'
                },
                'ml_chips_display': {
                    'position': 'sidebar',
                    'priority': 'low',
                    'visibility': 'collapsed',
                    'size': 'small'
                },
                'project_status': {
                    'position': 'sidebar',
                    'priority': 'medium',
                    'visibility': 'expanded',
                    'size': 'small'
                }
            },
            'learning_parameters': {
                'adaptation_threshold': 0.1,
                'min_interactions_for_adaptation': 10,
                'layout_refresh_interval_hours': 6
            },
            'performance_metrics': {
                'user_satisfaction': 0.0,
                'task_completion_time': 0.0,
                'error_rate': 0.0
            }
        }
        
        return layout_system
    
    def update_layout_performance(self, layout_config: Dict[str, Any], metrics: Dict[str, float]):
        """Update performance metrics for a layout configuration"""
        layout_hash = self._hash_layout(layout_config)
        
        self.performance_metrics[layout_hash] = {
            'config': layout_config,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        self.save_data()
    
    def get_best_layout(self) -> Dict[str, Any]:
        """Get the best performing layout configuration"""
        if not self.performance_metrics:
            return self.create_adaptive_layout_system()['current_layout']
        
        # Find layout with best user satisfaction
        best_layout = None
        best_score = 0.0
        
        for layout_data in self.performance_metrics.values():
            metrics = layout_data['metrics']
            # Weighted score: satisfaction (50%) + efficiency (30%) + low errors (20%)
            score = (
                metrics.get('user_satisfaction', 0) * 0.5 +
                (1.0 - metrics.get('task_completion_time', 1.0)) * 0.3 +
                (1.0 - metrics.get('error_rate', 0)) * 0.2
            )
            
            if score > best_score:
                best_score = score
                best_layout = layout_data['config']
        
        return best_layout or self.create_adaptive_layout_system()['current_layout']
    
    def _hash_layout(self, layout: Dict[str, Any]) -> str:
        """Generate a hash for a layout configuration"""
        import hashlib
        layout_str = json.dumps(layout, sort_keys=True)
        return hashlib.md5(layout_str.encode()).hexdigest()
    
    def save_data(self):
        """Save UI layout data to disk"""
        try:
            data = {
                'interaction_data': dict(self.interaction_data),
                'layout_configs': self.layout_configs,
                'performance_metrics': dict(self.performance_metrics)
            }
            
            with open('ui_layout_learning.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error saving UI layout data: {e}")
    
    def load_data(self):
        """Load UI layout data from disk"""
        try:
            with open('ui_layout_learning.json', 'r') as f:
                data = json.load(f)
            
            self.interaction_data = defaultdict(list, data.get('interaction_data', {}))
            self.layout_configs = data.get('layout_configs', {})
            self.performance_metrics = defaultdict(dict, data.get('performance_metrics', {}))
            
            print("📚 Loaded UI layout learning data")
        except FileNotFoundError:
            print("📚 No existing UI layout data found")
        except Exception as e:
            print(f"❌ Error loading UI layout data: {e}")

# Global UI layout optimizer
ui_optimizer = UILayoutOptimizer()

def record_ui_interaction(element_id: str, interaction_type: str, context: Dict[str, Any] = None):
    """Record a UI interaction"""
    ui_optimizer.record_interaction(element_id, interaction_type, context)

def get_optimal_ui_layout() -> Dict[str, Any]:
    """Get the current optimal UI layout"""
    return ui_optimizer.get_best_layout()

def update_ui_layout_performance(layout: Dict[str, Any], metrics: Dict[str, float]):
    """Update performance metrics for a UI layout"""
    ui_optimizer.update_layout_performance(layout, metrics)

def analyze_ui_usage_patterns() -> Dict[str, Any]:
    """Analyze UI usage patterns"""
    return ui_optimizer.analyze_usage_patterns()
