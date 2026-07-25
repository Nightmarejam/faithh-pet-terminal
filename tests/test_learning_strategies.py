#!/usr/bin/env python3
"""
Unit Tests for ML Learning Strategies
Tests adaptation logic for all learning strategy types
"""

import os
import sys
import pytest
from datetime import datetime
from unittest.mock import patch

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml_learning_framework import (
    LearningNode,
    UILayoutLearningStrategy,
    ModelConfigLearningStrategy,
    CoherenceThresholdLearningStrategy,
    RoutingStrategyLearningStrategy
)

class TestUILayoutLearningStrategy:
    """Test UI Layout Learning Strategy adaptation logic"""

    def test_strategy_learn_no_adaptation_needed(self):
        """Test strategy returns None when no adaptation is needed"""
        strategy = UILayoutLearningStrategy()
        
        node = LearningNode(
            id="test_ui_node",
            type="ui_layout",
            current_state={
                'coherence_indicator': {'position': 'main', 'priority': 'high'},
                'chat_interface': {'position': 'main', 'priority': 'high'}
            },
            performance_metrics={'user_satisfaction': 0.8},  # High satisfaction
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'user_satisfaction': 0.8}
        context = {'element_usage': {'coherence_indicator': 0.9}}
        
        result = strategy.learn(node, metrics, context)
        
        # Should return None when no adaptation needed
        assert result is None

    def test_strategy_learn_with_adaptation(self):
        """Test strategy adapts layout when user satisfaction is low"""
        strategy = UILayoutLearningStrategy()
        
        node = LearningNode(
            id="test_ui_node",
            type="ui_layout",
            current_state={
                'coherence_indicator': {
                    'position': 'sidebar',
                    'priority': 'medium',
                    'visibility': 'collapsed',
                    'size': 'medium'
                },
                'chat_interface': {'position': 'main', 'priority': 'high'}
            },
            performance_metrics={'user_satisfaction': 0.5},  # Low satisfaction
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'user_satisfaction': 0.5}
        context = {
            'element_usage': {
                'coherence_indicator': 0.9,  # Frequently used
                'chat_interface': 0.8
            }
        }
        
        result = strategy.learn(node, metrics, context)
        
        # Should adapt frequently used elements
        assert result is not None
        assert 'coherence_indicator' in result
        
        # Check that frequently used element was promoted
        coherence_config = result['coherence_indicator']
        assert coherence_config['position'] == 'prominent'  # Implementation uses 'prominent'
        assert coherence_config['priority'] == 'high'
        # Note: visibility and size are not modified by the current implementation

    def test_strategy_learn_without_usage_context(self):
        """Test strategy handles missing usage context gracefully"""
        strategy = UILayoutLearningStrategy()
        
        node = LearningNode(
            id="test_ui_node",
            type="ui_layout",
            current_state={'test_element': {'position': 'sidebar'}},
            performance_metrics={'user_satisfaction': 0.4},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'user_satisfaction': 0.4}
        context = {}  # No usage context
        
        result = strategy.learn(node, metrics, context)
        
        # Should handle gracefully
        assert result is not None  # Still returns a result but no specific adaptations

    def test_get_recommendations_high_satisfaction(self):
        """Test recommendations when satisfaction is good"""
        strategy = UILayoutLearningStrategy()
        
        node = LearningNode(
            id="test_ui_node",
            type="ui_layout",
            current_state={},
            performance_metrics={'user_satisfaction': 0.9},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        recommendations = strategy.get_recommendations(node)
        
        # Should have no recommendations for high satisfaction
        assert len(recommendations) == 0

    def test_get_recommendations_low_satisfaction(self):
        """Test recommendations when satisfaction is low"""
        strategy = UILayoutLearningStrategy()
        
        node = LearningNode(
            id="test_ui_node",
            type="ui_layout",
            current_state={},
            performance_metrics={'user_satisfaction': 0.4},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        recommendations = strategy.get_recommendations(node)
        
        # Should have layout optimization recommendation
        assert len(recommendations) > 0
        assert recommendations[0]['type'] == 'layout_optimization'
        assert recommendations[0]['priority'] == 'high'

class TestModelConfigLearningStrategy:
    """Test Model Configuration Learning Strategy"""

    def test_strategy_learn_efficiency_optimization(self):
        """Test strategy optimizes for efficiency when low"""
        strategy = ModelConfigLearningStrategy()
        
        node = LearningNode(
            id="test_model_node",
            type="model_config",
            current_state={'model_size': 14, 'quantization': 'Q4_K_M'},
            performance_metrics={'efficiency': 0.3},  # Low efficiency
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'efficiency': 0.3}
        context = {}
        
        result = strategy.learn(node, metrics, context)
        
        # Should reduce model size for better efficiency
        assert result is not None
        assert 'model_size' in result
        assert result['model_size'] < 14  # Should be reduced
        assert result['model_size'] >= 7  # Should not go below minimum

    def test_strategy_learn_accuracy_optimization(self):
        """Test strategy optimizes for accuracy when low"""
        strategy = ModelConfigLearningStrategy()
        
        node = LearningNode(
            id="test_model_node",
            type="model_config",
            current_state={'model_size': 8},
            performance_metrics={'accuracy': 0.5},  # Low accuracy
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'accuracy': 0.5}
        context = {}
        
        result = strategy.learn(node, metrics, context)
        
        # Should increase model size for better accuracy
        assert result is not None
        assert 'model_size' in result
        assert result['model_size'] > 8  # Should be increased
        assert result['model_size'] <= 70  # Should not exceed maximum

    def test_strategy_learn_boundary_conditions(self):
        """Test strategy respects model size boundaries"""
        strategy = ModelConfigLearningStrategy()
        
        # Test minimum boundary
        node_min = LearningNode(
            id="test_min_node",
            type="model_config",
            current_state={'model_size': 7},  # At minimum
            performance_metrics={'efficiency': 0.1},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_min = strategy.learn(node_min, {'efficiency': 0.1}, {})
        # Should return None if no change would be made (already at minimum)
        if result_min is not None:
            assert result_min['model_size'] >= 7  # Should not go below 7
        
        # Test maximum boundary
        node_max = LearningNode(
            id="test_max_node",
            type="model_config",
            current_state={'model_size': 70},  # At maximum
            performance_metrics={'accuracy': 0.1},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_max = strategy.learn(node_max, {'accuracy': 0.1}, {})
        # Should return None if no change would be made (already at maximum)
        if result_max is not None:
            assert result_max['model_size'] <= 70  # Should not exceed 70

    def test_get_recommendations_both_metrics_low(self):
        """Test recommendations when both efficiency and accuracy are low"""
        strategy = ModelConfigLearningStrategy()
        
        node = LearningNode(
            id="test_model_node",
            type="model_config",
            current_state={},
            performance_metrics={'efficiency': 0.3, 'accuracy': 0.4},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        recommendations = strategy.get_recommendations(node)
        
        # Should recommend model optimization
        assert len(recommendations) > 0
        assert recommendations[0]['type'] == 'model_optimization'
        assert recommendations[0]['priority'] == 'high'

    def test_get_recommendations_efficiency_only_low(self):
        """Test recommendations when only efficiency is low"""
        strategy = ModelConfigLearningStrategy()
        
        node = LearningNode(
            id="test_model_node",
            type="model_config",
            current_state={},
            performance_metrics={'efficiency': 0.3, 'accuracy': 0.8},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        recommendations = strategy.get_recommendations(node)
        
        # Should recommend performance optimization
        assert len(recommendations) > 0
        assert recommendations[0]['type'] == 'performance_optimization'
        assert recommendations[0]['priority'] == 'medium'

class TestCoherenceThresholdLearningStrategy:
    """Test Coherence Threshold Learning Strategy with boundary testing"""

    def test_strategy_learn_satisfaction_low(self):
        """Test strategy lowers thresholds when satisfaction is low"""
        strategy = CoherenceThresholdLearningStrategy()
        
        node = LearningNode(
            id="test_coherence_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.6,
                    'medium_threshold': 0.3,
                    'anchor_validation_threshold': 0.7
                }
            },
            performance_metrics={'user_satisfaction': 0.4},  # Low satisfaction
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'user_satisfaction': 0.4}
        context = {}
        
        result = strategy.learn(node, metrics, context)
        
        # Should lower thresholds to be more permissive
        assert result is not None
        thresholds = result['current_thresholds']
        
        # Should be lowered by 10%
        assert thresholds['high_threshold'] == 0.6 * 0.9  # 0.54
        assert thresholds['medium_threshold'] == 0.3 * 0.9  # 0.27

    def test_strategy_learn_satisfaction_high(self):
        """Test strategy raises thresholds when satisfaction is high"""
        strategy = CoherenceThresholdLearningStrategy()
        
        node = LearningNode(
            id="test_coherence_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.6,
                    'medium_threshold': 0.3,
                    'anchor_validation_threshold': 0.7
                }
            },
            performance_metrics={'user_satisfaction': 0.9},  # High satisfaction
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'user_satisfaction': 0.9}
        context = {}
        
        result = strategy.learn(node, metrics, context)
        
        # Should raise thresholds to be more strict
        assert result is not None
        thresholds = result['current_thresholds']
        
        # Should be raised by 5%
        assert thresholds['high_threshold'] == 0.6 * 1.05  # 0.63
        assert thresholds['medium_threshold'] == 0.3 * 1.05  # 0.315

    def test_strategy_learn_boundary_enforcement_exact_bounds(self):
        """Test strategy enforces boundaries at exact 0.5 and 0.8"""
        strategy = CoherenceThresholdLearningStrategy()
        
        # Test exactly at lower bound (0.5)
        node_low = LearningNode(
            id="test_low_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.5,  # Exactly at lower bound
                    'medium_threshold': 0.3
                }
            },
            performance_metrics={'user_satisfaction': 0.1},  # Very low satisfaction
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_low = strategy.learn(node_low, {'user_satisfaction': 0.1}, {})
        thresholds_low = result_low['current_thresholds']
        
        # Should not go below 0.5
        assert thresholds_low['high_threshold'] >= 0.5
        
        # Test exactly at upper bound (0.8)
        node_high = LearningNode(
            id="test_high_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.8,  # Exactly at upper bound
                    'medium_threshold': 0.3
                }
            },
            performance_metrics={'user_satisfaction': 1.0},  # Perfect satisfaction
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_high = strategy.learn(node_high, {'user_satisfaction': 1.0}, {})
        thresholds_high = result_high['current_thresholds']
        
        # Should not exceed 0.8
        assert thresholds_high['high_threshold'] <= 0.8

    def test_strategy_learn_boundary_enforcement_outside_bounds(self):
        """Test strategy handles values just outside bounds (0.49, 0.81)"""
        strategy = CoherenceThresholdLearningStrategy()
        
        # Test just below lower bound (0.49)
        node_below = LearningNode(
            id="test_below_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.49,  # Just below lower bound
                    'medium_threshold': 0.3
                }
            },
            performance_metrics={'user_satisfaction': 0.1},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_below = strategy.learn(node_below, {'user_satisfaction': 0.1}, {})
        thresholds_below = result_below['current_thresholds']
        
        # Should be clamped to 0.5
        assert thresholds_below['high_threshold'] == 0.5
        
        # Test just above upper bound (0.81)
        node_above = LearningNode(
            id="test_above_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.81,  # Just above upper bound
                    'medium_threshold': 0.3
                }
            },
            performance_metrics={'user_satisfaction': 1.0},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_above = strategy.learn(node_above, {'user_satisfaction': 1.0}, {})
        thresholds_above = result_above['current_thresholds']
        
        # Should be clamped to 0.8
        assert thresholds_above['high_threshold'] == 0.8

    def test_strategy_learn_medium_threshold_boundaries(self):
        """Test medium threshold boundaries (0.2 to 0.6)"""
        strategy = CoherenceThresholdLearningStrategy()
        
        # Test at lower bound (0.2)
        node_med_low = LearningNode(
            id="test_med_low_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.6,
                    'medium_threshold': 0.2  # At lower bound
                }
            },
            performance_metrics={'user_satisfaction': 0.1},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_med_low = strategy.learn(node_med_low, {'user_satisfaction': 0.1}, {})
        thresholds_med_low = result_med_low['current_thresholds']
        
        # Should not go below 0.2
        assert thresholds_med_low['medium_threshold'] >= 0.2
        
        # Test at upper bound (0.6)
        node_med_high = LearningNode(
            id="test_med_high_node",
            type="coherence_threshold",
            current_state={
                'current_thresholds': {
                    'high_threshold': 0.6,
                    'medium_threshold': 0.6  # At upper bound
                }
            },
            performance_metrics={'user_satisfaction': 1.0},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result_med_high = strategy.learn(node_med_high, {'user_satisfaction': 1.0}, {})
        thresholds_med_high = result_med_high['current_thresholds']
        
        # Should not exceed 0.6
        assert thresholds_med_high['medium_threshold'] <= 0.6

    def test_strategy_learn_missing_thresholds(self):
        """Test strategy handles missing thresholds gracefully"""
        strategy = CoherenceThresholdLearningStrategy()
        
        node = LearningNode(
            id="test_missing_node",
            type="coherence_threshold",
            current_state={},  # No thresholds
            performance_metrics={'user_satisfaction': 0.4},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        result = strategy.learn(node, {'user_satisfaction': 0.4}, {})
        
        # Should create default thresholds
        assert 'current_thresholds' in result
        thresholds = result['current_thresholds']
        assert 'high_threshold' in thresholds
        assert 'medium_threshold' in thresholds
        assert 'anchor_validation_threshold' in thresholds

    def test_get_recommendations_low_satisfaction(self):
        """Test recommendations when satisfaction is very low"""
        strategy = CoherenceThresholdLearningStrategy()
        
        node = LearningNode(
            id="test_coherence_node",
            type="coherence_threshold",
            current_state={},
            performance_metrics={'user_satisfaction': 0.3},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        recommendations = strategy.get_recommendations(node)
        
        # Should recommend threshold adjustment
        assert len(recommendations) > 0
        assert recommendations[0]['type'] == 'threshold_adjustment'
        assert recommendations[0]['priority'] == 'high'

class TestRoutingStrategyLearningStrategy:
    """Test Routing Strategy Learning Strategy"""

    def test_strategy_learn_provider_performance_update(self):
        """Test strategy updates provider weights based on performance"""
        strategy = RoutingStrategyLearningStrategy()
        
        node = LearningNode(
            id="test_routing_node",
            type="routing_strategy",
            current_state={
                'ollama_weight': 0.4,  # Direct weights, not nested
                'gemini_weight': 0.4,
                'groq_weight': 0.2
            },
            performance_metrics={'efficiency': 0.5},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'efficiency': 0.5}
        context = {
            'provider_performance': {
                'ollama': 0.8,  # Good performance
                'gemini': 0.6,  # Medium performance
                'groq': 0.3     # Poor performance
            }
        }
        
        result = strategy.learn(node, metrics, context)
        
        # Debug: print the actual result
        if result is None:
            print("DEBUG: Routing strategy returned None")
            print(f"Current strategy: {node.current_state}")
            print(f"Context: {context}")
        
        # Should update provider weights based on performance
        assert result is not None
        weights = result  # Direct weights, not nested
        
        # Ollama should have highest weight (best performance)
        assert weights['ollama_weight'] > weights['gemini_weight']
        assert weights['gemini_weight'] > weights['groq_weight']
        
        # Weights should be capped at 1.0
        for weight_key in ['ollama_weight', 'gemini_weight', 'groq_weight']:
            assert weights[weight_key] <= 1.0

    def test_strategy_learn_missing_provider_performance(self):
        """Test strategy handles missing provider performance gracefully"""
        strategy = RoutingStrategyLearningStrategy()
        
        node = LearningNode(
            id="test_routing_node",
            type="routing_strategy",
            current_state={
                'ollama_weight': 0.4,
                'gemini_weight': 0.4,
                'groq_weight': 0.2
            },
            performance_metrics={'efficiency': 0.5},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        metrics = {'efficiency': 0.5}
        context = {}  # No provider performance data
        
        result = strategy.learn(node, metrics, context)
        
        # Should return None since no provider performance data and no changes made
        assert result is None

    def test_get_recommendations_low_efficiency(self):
        """Test recommendations when routing efficiency is low"""
        strategy = RoutingStrategyLearningStrategy()
        
        node = LearningNode(
            id="test_routing_node",
            type="routing_strategy",
            current_state={},
            performance_metrics={'efficiency': 0.4},
            learning_history=[],
            last_updated=datetime.now()
        )
        
        recommendations = strategy.get_recommendations(node)
        
        # Should recommend routing optimization
        assert len(recommendations) > 0
        assert recommendations[0]['type'] == 'routing_optimization'
        assert recommendations[0]['priority'] == 'medium'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
