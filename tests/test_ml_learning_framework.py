#!/usr/bin/env python3
"""
Unit Tests for ML Learning Framework
Tests LearningNode creation, state management, and framework operations
"""

import os
import sys
import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml_learning_framework import (
    LearningNode,
    MLLearningFramework,
    UILayoutLearningStrategy,
    ModelConfigLearningStrategy,
    CoherenceThresholdLearningStrategy,
    RoutingStrategyLearningStrategy
)

class TestLearningNode:
    """Test LearningNode creation, serialization, and state management"""

    def test_learning_node_creation(self):
        """Test node creation with valid config and default metrics"""
        config = {"test_param": "test_value"}
        node = LearningNode(
            id="test_node_1",
            type="ui_layout",
            current_state=config,
            performance_metrics={'accuracy': 0.0, 'efficiency': 0.0, 'user_satisfaction': 0.0},
            learning_history=[],
            last_updated=datetime.now(),
            adaptation_rate=0.1
        )
        
        assert node.id == "test_node_1"
        assert node.type == "ui_layout"
        assert node.current_state == config
        assert node.adaptation_rate == 0.1
        assert len(node.learning_history) == 0
        assert isinstance(node.last_updated, datetime)

    def test_learning_node_serialization(self):
        """Test node to_dict serialization"""
        test_time = datetime.now()
        node = LearningNode(
            id="test_node_2",
            type="model_config",
            current_state={"model_size": 14},
            performance_metrics={'accuracy': 0.8},
            learning_history=[],
            last_updated=test_time,
            adaptation_rate=0.2
        )
        
        node_dict = node.to_dict()
        
        assert node_dict['id'] == "test_node_2"
        assert node_dict['type'] == "model_config"
        assert node_dict['current_state'] == {"model_size": 14}
        assert node_dict['adaptation_rate'] == 0.2
        assert node_dict['last_updated'] == test_time  # asdict keeps datetime object

    def test_learning_node_deserialization(self):
        """Test node from_dict deserialization"""
        test_time = datetime.now()
        node_data = {
            'id': "test_node_3",
            'type': "coherence_threshold",
            'current_state': {"threshold": 0.6},
            'performance_metrics': {'accuracy': 0.7},
            'learning_history': [],
            'last_updated': test_time.isoformat(),
            'adaptation_rate': 0.15
        }
        
        node = LearningNode.from_dict(node_data)
        
        assert node.id == "test_node_3"
        assert node.type == "coherence_threshold"
        assert node.current_state == {"threshold": 0.6}
        assert node.adaptation_rate == 0.15
        assert isinstance(node.last_updated, datetime)

    def test_unique_id_generation_in_framework(self):
        """Test that framework generates unique node IDs"""
        framework = MLLearningFramework()
        
        # Mock save_nodes to avoid file operations
        with patch.object(framework, 'save_nodes'):
            node1_id = framework.create_node("ui_layout", {"test": "config1"})
            node2_id = framework.create_node("ui_layout", {"test": "config2"})
            
            assert node1_id != node2_id
            assert node1_id.startswith("ui_layout_")
            assert node2_id.startswith("ui_layout_")

class TestMLLearningFramework:
    """Test MLLearningFramework node management and operations"""

    def test_framework_initialization(self):
        """Test framework initializes with learning strategies"""
        framework = MLLearningFramework()
        
        assert len(framework.learning_strategies) == 4
        assert 'ui_layout' in framework.learning_strategies
        assert 'model_config' in framework.learning_strategies
        assert 'coherence_threshold' in framework.learning_strategies
        assert 'routing_strategy' in framework.learning_strategies
        
        # Verify strategy types
        assert isinstance(framework.learning_strategies['ui_layout'], UILayoutLearningStrategy)
        assert isinstance(framework.learning_strategies['model_config'], ModelConfigLearningStrategy)

    @patch('backend.ml_learning_framework.MLLearningFramework.save_nodes')
    def test_create_node(self, mock_save):
        """Test node creation with proper initialization"""
        framework = MLLearningFramework()
        config = {"layout_param": "test"}
        
        node_id = framework.create_node("ui_layout", config)
        
        assert node_id in framework.nodes
        node = framework.nodes[node_id]
        assert node.type == "ui_layout"
        assert node.current_state == config
        assert node.performance_metrics == {'accuracy': 0.0, 'efficiency': 0.0, 'user_satisfaction': 0.0}
        assert len(node.learning_history) == 0
        mock_save.assert_called_once()

    def test_update_node_performance_existing_node(self):
        """Test performance update for existing node"""
        framework = MLLearningFramework()
        
        # Create a test node
        with patch.object(framework, 'save_nodes'):
            node_id = framework.create_node("ui_layout", {"test": "config"})
        
        # Update performance
        metrics = {"accuracy": 0.8, "efficiency": 0.7}
        context = {"test_context": "value"}
        
        result = framework.update_node_performance(node_id, metrics, context)
        
        assert result is True
        node = framework.nodes[node_id]
        
        # Check EMA calculation (adaptation_rate = 0.1)
        expected_accuracy = 0.0 * 0.9 + 0.8 * 0.1  # 0.08
        expected_efficiency = 0.0 * 0.9 + 0.7 * 0.1  # 0.07
        
        assert abs(node.performance_metrics["accuracy"] - expected_accuracy) < 0.001
        assert abs(node.performance_metrics["efficiency"] - expected_efficiency) < 0.001
        
        # Check learning event recorded
        assert len(node.learning_history) == 1
        event = node.learning_history[0]
        assert event["metrics"] == metrics
        assert event["context"] == context
        assert "timestamp" in event
        assert "previous_state" in event

    def test_update_node_performance_nonexistent_node(self):
        """Test performance update for non-existent node"""
        framework = MLLearningFramework()
        
        result = framework.update_node_performance("nonexistent", {"accuracy": 0.8})
        
        assert result is False

    def test_performance_metric_ema_calculation(self):
        """Test exponential moving average calculation accuracy"""
        framework = MLLearningFramework()
        
        with patch.object(framework, 'save_nodes'):
            node_id = framework.create_node("ui_layout", {"test": "config"})
        
        node = framework.nodes[node_id]
        
        # First update
        framework.update_node_performance(node_id, {"accuracy": 0.8})
        expected_after_first = 0.0 * 0.9 + 0.8 * 0.1  # 0.08
        assert abs(node.performance_metrics["accuracy"] - expected_after_first) < 0.001
        
        # Second update
        framework.update_node_performance(node_id, {"accuracy": 0.9})
        expected_after_second = 0.08 * 0.9 + 0.9 * 0.1  # 0.162
        assert abs(node.performance_metrics["accuracy"] - expected_after_second) < 0.001
        
        # Third update
        framework.update_node_performance(node_id, {"accuracy": 0.7})
        expected_after_third = 0.162 * 0.9 + 0.7 * 0.1  # 0.2158
        assert abs(node.performance_metrics["accuracy"] - expected_after_third) < 0.001

    def test_learning_event_recording_structure(self):
        """Test learning event has proper structure"""
        framework = MLLearningFramework()
        
        with patch.object(framework, 'save_nodes'):
            node_id = framework.create_node("ui_layout", {"test": "config"})
        
        # Update performance to trigger event recording
        metrics = {"accuracy": 0.8}
        context = {"session_id": "test_session"}
        
        framework.update_node_performance(node_id, metrics, context)
        
        node = framework.nodes[node_id]
        event = node.learning_history[0]
        
        # Verify event structure
        required_fields = ["timestamp", "metrics", "context", "previous_state"]
        for field in required_fields:
            assert field in event
        
        assert event["metrics"] == metrics
        assert event["context"] == context
        assert event["previous_state"] == {"test": "config"}
        
        # Verify timestamp format
        timestamp = datetime.fromisoformat(event["timestamp"])
        assert isinstance(timestamp, datetime)

    def test_strategy_triggering_on_performance_update(self):
        """Test that learning strategy is triggered on performance update"""
        framework = MLLearningFramework()
        
        with patch.object(framework, 'save_nodes'):
            node_id = framework.create_node("coherence_threshold", {
                "current_thresholds": {"high_threshold": 0.6, "medium_threshold": 0.3}
            })
        
        # Mock the learning strategy
        strategy = framework.learning_strategies['coherence_threshold']
        with patch.object(strategy, 'learn') as mock_learn:
            mock_learn.return_value = {"adapted": True}
            
            metrics = {"user_satisfaction": 0.5}  # Low satisfaction should trigger adaptation
            framework.update_node_performance(node_id, metrics)
            
            # Verify strategy was called
            mock_learn.assert_called_once()
            args = mock_learn.call_args[0]
            assert len(args) == 3  # node, metrics, context
            assert args[1] == metrics

    def test_strategy_failure_handling(self):
        """Test graceful handling of learning strategy failures"""
        framework = MLLearningFramework()
        
        with patch.object(framework, 'save_nodes'):
            node_id = framework.create_node("ui_layout", {"test": "config"})
        
        # Mock strategy to raise exception
        strategy = framework.learning_strategies['ui_layout']
        with patch.object(strategy, 'learn', side_effect=Exception("Strategy failed")):
            # Should not raise exception
            result = framework.update_node_performance(node_id, {"accuracy": 0.8})
            
            # Should still record the learning event despite strategy failure
            assert result is True
            node = framework.nodes[node_id]
            assert len(node.learning_history) == 1

    def test_analyze_global_patterns(self):
        """Test global pattern analysis across all nodes"""
        # Use a fresh framework to avoid loading existing nodes
        with patch('backend.ml_learning_framework.MLLearningFramework.load_nodes'):
            framework = MLLearningFramework()
        
        # Create multiple nodes with different performance
        with patch.object(framework, 'save_nodes'):
            node1_id = framework.create_node("ui_layout", {"test": "config1"})
            node2_id = framework.create_node("model_config", {"test": "config2"})
            
            # Update performance metrics
            framework.update_node_performance(node1_id, {"accuracy": 0.8, "efficiency": 0.7})
            framework.update_node_performance(node2_id, {"accuracy": 0.6, "efficiency": 0.9})
        
        analysis = framework.analyze_global_patterns()
        
        assert analysis['total_nodes'] == 2
        assert analysis['node_types']['ui_layout'] == 1
        assert analysis['node_types']['model_config'] == 1
        assert analysis['adaptation_events'] == 2  # One for each node
        
        # Check performance trends
        assert 'accuracy' in analysis['performance_trends']
        assert 'efficiency' in analysis['performance_trends']

    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_save_nodes(self, mock_json_dump, mock_open):
        """Test node saving to file"""
        # Use a fresh framework to avoid loading existing nodes
        with patch('backend.ml_learning_framework.MLLearningFramework.load_nodes'):
            framework = MLLearningFramework()
        
        with patch.object(framework, 'save_nodes'):
            node_id = framework.create_node("ui_layout", {"test": "config"})
        
        framework.save_nodes()
        
        # Check that open was called for writing (may also be called for reading)
        write_calls = [call for call in mock_open.call_args_list if 'w' in str(call)]
        assert len(write_calls) >= 1
        assert any('ml_learning_nodes.json' in str(call) and 'w' in str(call) for call in write_calls)
        mock_json_dump.assert_called_once()

    def test_silent_failure_prevention(self):
        """Test that learning node state actually changes after update_node_performance"""
        framework = MLLearningFramework()
        
        with patch.object(framework, 'save_nodes'):
            node_id = framework.create_node("coherence_threshold", {
                "current_thresholds": {"high_threshold": 0.6, "medium_threshold": 0.3}
            })
        
        # Get initial state
        initial_node = framework.nodes[node_id]
        initial_thresholds = initial_node.current_state["current_thresholds"].copy()
        initial_metrics = initial_node.performance_metrics.copy()
        
        # Update performance with low satisfaction to trigger adaptation
        metrics = {"user_satisfaction": 0.4}  # Low satisfaction should trigger adaptation
        context = {}
        
        result = framework.update_node_performance(node_id, metrics, context)
        
        # Verify the method succeeded
        assert result is True
        
        # Verify learning event was recorded
        updated_node = framework.nodes[node_id]
        assert len(updated_node.learning_history) == 1
        assert updated_node.learning_history[0]["metrics"] == metrics
        assert updated_node.learning_history[0]["context"] == context
        
        # Verify performance metrics were updated (EMA calculation)
        expected_satisfaction = initial_metrics["user_satisfaction"] * 0.9 + 0.4 * 0.1  # EMA with adaptation_rate=0.1
        assert abs(updated_node.performance_metrics["user_satisfaction"] - expected_satisfaction) < 0.001
        
        # Verify state actually changed (adaptation occurred)
        updated_thresholds = updated_node.current_state["current_thresholds"]
        assert updated_thresholds != initial_thresholds
        
        # Verify adaptation was in the expected direction (lowered thresholds for low satisfaction)
        assert updated_thresholds["high_threshold"] < initial_thresholds["high_threshold"]
        assert updated_thresholds["medium_threshold"] < initial_thresholds["medium_threshold"]
        
        # Verify thresholds stay within bounds
        assert 0.5 <= updated_thresholds["high_threshold"] <= 0.8
        assert 0.2 <= updated_thresholds["medium_threshold"] <= 0.6

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
