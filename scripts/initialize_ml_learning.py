"""
Initialize ML Learning Framework
Creates initial learning nodes for FAITHH self-improvement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml_learning_framework import create_learning_node, update_node_performance

def initialize_learning_system():
    """Initialize the ML learning framework with core learning nodes"""
    
    print("🧠 Initializing ML Learning Framework...")
    
    # 1. UI Layout Learning Node
    ui_layout_config = {
        'current_layout': {
            'coherence_indicator': {'position': 'main', 'priority': 'high', 'visibility': 'expanded'},
            'chat_interface': {'position': 'main', 'priority': 'high', 'visibility': 'expanded'},
            'rag_panel': {'position': 'sidebar', 'priority': 'medium', 'visibility': 'collapsed'},
            'pulse_dashboard': {'position': 'sidebar', 'priority': 'medium', 'visibility': 'collapsed'},
            'ml_chips_display': {'position': 'sidebar', 'priority': 'low', 'visibility': 'collapsed'},
            'project_status': {'position': 'sidebar', 'priority': 'medium', 'visibility': 'expanded'}
        },
        'learning_parameters': {
            'adaptation_threshold': 0.1,
            'min_interactions_for_adaptation': 10,
            'layout_refresh_interval_hours': 6
        }
    }
    
    ui_node_id = create_learning_node('ui_layout', ui_layout_config)
    print(f"✅ Created UI Layout Learning Node: {ui_node_id}")
    
    # 2. Model Configuration Learning Node
    model_config = {
        'current_model': 'qwen25-grounded:latest',
        'model_size': 14.8,  # billions of parameters
        'quantization': 'Q4_K_M',
        'provider': 'ollama',
        'performance_targets': {
            'target_response_time': 3.0,  # seconds
            'target_accuracy': 0.8,
            'target_efficiency': 0.7
        },
        'optimization_parameters': {
            'max_model_size': 70,
            'min_model_size': 7,
            'preferred_providers': ['ollama', 'gemini', 'groq']
        }
    }
    
    model_node_id = create_learning_node('model_config', model_config)
    print(f"✅ Created Model Configuration Learning Node: {model_node_id}")
    
    # 3. Coherence Threshold Learning Node
    coherence_config = {
        'current_thresholds': {
            'high_threshold': 0.6,
            'medium_threshold': 0.3,
            'anchor_validation_threshold': 0.7
        },
        'learning_parameters': {
            'adaptation_rate': 0.05,
            'min_samples_for_adaptation': 20,
            'satisfaction_weight': 0.7
        },
        'performance_metrics': {
            'target_user_satisfaction': 0.8,
            'target_coherence_accuracy': 0.75
        }
    }
    
    coherence_node_id = create_learning_node('coherence_threshold', coherence_config)
    print(f"✅ Created Coherence Threshold Learning Node: {coherence_node_id}")
    
    # 4. Routing Strategy Learning Node
    routing_config = {
        'current_strategy': {
            'selection_method': 'performance_based',
            'fallback_enabled': True,
            'health_check_interval': 60,  # seconds
            'provider_weights': {
                'ollama': 0.4,
                'gemini': 0.4,
                'groq': 0.2
            }
        },
        'learning_parameters': {
            'performance_window_minutes': 30,
            'adaptation_threshold': 0.1,
            'min_requests_for_adaptation': 10
        }
    }
    
    routing_node_id = create_learning_node('routing_strategy', routing_config)
    print(f"✅ Created Routing Strategy Learning Node: {routing_node_id}")
    
    # Initialize with baseline performance metrics
    initial_metrics = {
        'ui_layout': {'user_satisfaction': 0.7, 'task_completion_time': 0.6, 'error_rate': 0.1},
        'model_config': {'accuracy': 0.7, 'efficiency': 0.3, 'user_satisfaction': 0.6},
        'coherence_threshold': {'accuracy': 0.75, 'user_satisfaction': 0.7},
        'routing_strategy': {'efficiency': 0.2, 'user_satisfaction': 0.6}
    }
    
    # Update initial performance metrics
    for node_type, metrics in initial_metrics.items():
        node_id = {
            'ui_layout': ui_node_id,
            'model_config': model_node_id,
            'coherence_threshold': coherence_node_id,
            'routing_strategy': routing_node_id
        }[node_type]
        
        update_node_performance(node_id, metrics, {'initialization': True})
    
    print("🎯 Learning Framework Initialization Complete!")
    print(f"📊 Created 4 learning nodes with baseline metrics")
    
    return {
        'ui_layout_node': ui_node_id,
        'model_config_node': model_node_id,
        'coherence_threshold_node': coherence_node_id,
        'routing_strategy_node': routing_node_id
    }

if __name__ == "__main__":
    nodes = initialize_learning_system()
    print("\n🔄 Learning nodes are ready for adaptive learning!")
    print("📈 The system will now learn from user interactions and optimize itself.")
