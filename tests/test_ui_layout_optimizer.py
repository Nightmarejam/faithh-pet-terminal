#!/usr/bin/env python3
"""
Unit Tests for UI Layout Optimizer
Tests interaction recording, usage pattern analysis, and layout optimization
"""

import os
import sys
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ui_layout_optimizer import UILayoutOptimizer

class TestUILayoutOptimizer:
    """Test UI layout optimization functionality"""

    def test_optimizer_initialization(self):
        """Test optimizer initializes with empty data structures"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        assert len(optimizer.interaction_data) == 0
        assert len(optimizer.layout_configs) == 0
        assert len(optimizer.performance_metrics) == 0

    def test_record_interaction_basic(self):
        """Test basic interaction recording"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        with patch.object(optimizer, 'save_data'):
            optimizer.record_interaction(
                element_id="coherence_indicator",
                interaction_type="click",
                context={"session_id": "test_session"}
            )
        
        # Verify interaction was recorded
        assert "coherence_indicator" in optimizer.interaction_data
        interactions = optimizer.interaction_data["coherence_indicator"]
        assert len(interactions) == 1
        
        interaction = interactions[0]
        assert interaction["type"] == "click"
        assert interaction["context"]["session_id"] == "test_session"
        assert "timestamp" in interaction

    def test_record_interaction_without_context(self):
        """Test interaction recording without context"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        with patch.object(optimizer, 'save_data'):
            optimizer.record_interaction(
                element_id="chat_interface",
                interaction_type="type"
            )
        
        interactions = optimizer.interaction_data["chat_interface"]
        assert len(interactions) == 1
        
        interaction = interactions[0]
        assert interaction["type"] == "type"
        assert interaction["context"] == {}
        assert interaction["session_id"] is None

    def test_record_interaction_multiple_interactions(self):
        """Test recording multiple interactions for same element"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        with patch.object(optimizer, 'save_data'):
            # Record multiple interactions
            optimizer.record_interaction("rag_panel", "click", {"session_id": "s1"})
            optimizer.record_interaction("rag_panel", "expand", {"session_id": "s1"})
            optimizer.record_interaction("rag_panel", "collapse", {"session_id": "s2"})
        
        interactions = optimizer.interaction_data["rag_panel"]
        assert len(interactions) == 3
        
        # Verify interaction types
        types = [i["type"] for i in interactions]
        assert "click" in types
        assert "expand" in types
        assert "collapse" in types

    def test_analyze_usage_patterns_empty_data(self):
        """Test usage pattern analysis with no interaction data"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        patterns = optimizer.analyze_usage_patterns()
        
        # Should return empty patterns
        assert patterns["most_used_elements"] == []
        assert patterns["least_used_elements"] == []
        assert patterns["element_types"] == {}

    def test_analyze_usage_patterns_with_data(self):
        """Test usage pattern analysis with mock interaction data"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        # Create mock interaction data
        base_time = datetime.now() - timedelta(hours=1)  # Within 24-hour window
        
        mock_interactions = {
            "coherence_indicator": [
                {
                    "timestamp": base_time.isoformat(),
                    "type": "click",
                    "context": {"session_id": "s1"},
                    "session_id": "s1"
                },
                {
                    "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
                    "type": "hover",
                    "context": {"session_id": "s1"},
                    "session_id": "s1"
                },
                {
                    "timestamp": (base_time + timedelta(minutes=20)).isoformat(),
                    "type": "click",
                    "context": {"session_id": "s2"},
                    "session_id": "s2"
                }
            ],
            "rag_panel": [
                {
                    "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
                    "type": "expand",
                    "context": {"session_id": "s1"},
                    "session_id": "s1"
                }
            ],
            "chat_interface": [
                {
                    "timestamp": (base_time - timedelta(hours=25)).isoformat(),  # Outside window
                    "type": "type",
                    "context": {"session_id": "s1"},
                    "session_id": "s1"
                }
            ]
        }
        
        optimizer.interaction_data = mock_interactions
        
        patterns = optimizer.analyze_usage_patterns()
        
        # Verify most used elements
        most_used = patterns["most_used_elements"]
        assert len(most_used) == 2  # coherence_indicator (3) and rag_panel (1)
        assert most_used[0] == ("coherence_indicator", 3)
        assert most_used[1] == ("rag_panel", 1)
        
        # Verify element types
        element_types = patterns["element_types"]
        assert "coherence_indicator" in element_types
        assert element_types["coherence_indicator"]["click"] == 2
        assert element_types["coherence_indicator"]["hover"] == 1
        assert element_types["rag_panel"]["expand"] == 1

    def test_analyze_usage_patterns_time_window_filtering(self):
        """Test that old interactions are filtered out"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        # Create interactions outside time window
        old_time = datetime.now() - timedelta(hours=25)  # Outside 24-hour window
        
        mock_interactions = {
            "old_element": [
                {
                    "timestamp": old_time.isoformat(),
                    "type": "click",
                    "context": {"session_id": "s1"},
                    "session_id": "s1"
                }
            ]
        }
        
        optimizer.interaction_data = mock_interactions
        
        patterns = optimizer.analyze_usage_patterns()
        
        # Should filter out old interactions
        assert patterns["most_used_elements"] == []
        assert patterns["element_types"] == {}

    def test_generate_optimal_layout_promotes_frequently_used(self):
        """Test that frequently used elements are promoted"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        # Mock usage patterns
        with patch.object(optimizer, 'analyze_usage_patterns') as mock_analyze:
            mock_analyze.return_value = {
                "most_used_elements": [
                    ("coherence_indicator", 10),
                    ("rag_panel", 8),
                    ("chat_interface", 6)
                ],
                "least_used_elements": [],
                "element_types": {}
            }
            
            current_layout = {
                "coherence_indicator": {
                    "position": "sidebar",
                    "priority": "medium",
                    "visibility": "collapsed",
                    "size": "medium"
                },
                "rag_panel": {
                    "position": "sidebar",
                    "priority": "low",
                    "visibility": "collapsed",
                    "size": "small"
                },
                "chat_interface": {
                    "position": "main",
                    "priority": "high",
                    "visibility": "expanded",
                    "size": "large"
                }
            }
            
            optimal_layout = optimizer.generate_optimal_layout(current_layout)
            
            # Verify frequently used elements were promoted
            coherence_config = optimal_layout["coherence_indicator"]
            assert coherence_config["position"] == "main"
            assert coherence_config["priority"] == "high"
            assert coherence_config["visibility"] == "expanded"
            assert coherence_config["size"] == "large"
            
            rag_config = optimal_layout["rag_panel"]
            assert rag_config["position"] == "main"
            assert rag_config["priority"] == "high"

    def test_generate_optimal_layout_demotes_unused_elements(self):
        """Test that unused elements are demoted"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        # Mock usage patterns with least used elements
        with patch.object(optimizer, 'analyze_usage_patterns') as mock_analyze:
            mock_analyze.return_value = {
                "most_used_elements": [("chat_interface", 10)],
                "least_used_elements": [
                    ("old_feature", 1),  # Very low usage
                    ("unused_panel", 0)   # Never used
                ],
                "element_types": {}
            }
            
            current_layout = {
                "chat_interface": {
                    "position": "main",
                    "priority": "high",
                    "visibility": "expanded",
                    "size": "large"
                },
                "old_feature": {
                    "position": "main",
                    "priority": "high",
                    "visibility": "expanded",
                    "size": "medium"
                },
                "unused_panel": {
                    "position": "sidebar",
                    "priority": "medium",
                    "visibility": "expanded",
                    "size": "small"
                }
            }
            
            optimal_layout = optimizer.generate_optimal_layout(current_layout)
            
            # Verify unused elements were demoted
            old_feature_config = optimal_layout["old_feature"]
            assert old_feature_config["position"] == "sidebar"
            assert old_feature_config["priority"] == "low"
            
            # Verify never-used element is collapsed
            unused_config = optimal_layout["unused_panel"]
            assert unused_config["visibility"] == "collapsed"

    def test_generate_optimal_layout_preserves_unmentioned_elements(self):
        """Test that elements not in usage patterns are preserved"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        with patch.object(optimizer, 'analyze_usage_patterns') as mock_analyze:
            mock_analyze.return_value = {
                "most_used_elements": [("chat_interface", 10)],
                "least_used_elements": [],
                "element_types": {}
            }
            
            current_layout = {
                "chat_interface": {"position": "main"},
                "neutral_element": {"position": "sidebar", "priority": "medium"}
            }
            
            optimal_layout = optimizer.generate_optimal_layout(current_layout)
            
            # Verify neutral element is preserved
            assert "neutral_element" in optimal_layout
            assert optimal_layout["neutral_element"]["position"] == "sidebar"
            assert optimal_layout["neutral_element"]["priority"] == "medium"

    def test_update_layout_performance(self):
        """Test layout performance metric tracking"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        with patch.object(optimizer, 'save_data'):
            layout_config = {
                "coherence_indicator": {"position": "main"},
                "chat_interface": {"position": "main"}
            }
            
            metrics = {
                "user_satisfaction": 0.8,
                "task_completion_time": 0.3,
                "error_rate": 0.1
            }
            
            optimizer.update_layout_performance(layout_config, metrics)
        
        # Verify performance was recorded
        assert len(optimizer.performance_metrics) == 1
        
        # Find the recorded performance data
        perf_data = None
        for data in optimizer.performance_metrics.values():
            perf_data = data
            break
        
        assert perf_data is not None
        assert perf_data["config"] == layout_config
        assert perf_data["metrics"] == metrics
        assert "timestamp" in perf_data

    def test_get_best_layout_no_data(self):
        """Test getting best layout with no performance data"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        best_layout = optimizer.get_best_layout()
        
        # Should return default adaptive layout
        assert "coherence_indicator" in best_layout
        assert "chat_interface" in best_layout
        assert "rag_panel" in best_layout

    def test_get_best_layout_with_performance_data(self):
        """Test getting best layout with performance data"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        # Add performance data
        layout1 = {"coherence_indicator": {"position": "sidebar"}}
        layout2 = {"coherence_indicator": {"position": "main"}}
        
        metrics1 = {"user_satisfaction": 0.6, "task_completion_time": 0.8, "error_rate": 0.2}
        metrics2 = {"user_satisfaction": 0.9, "task_completion_time": 0.2, "error_rate": 0.05}
        
        with patch.object(optimizer, 'save_data'):
            optimizer.update_layout_performance(layout1, metrics1)
            optimizer.update_layout_performance(layout2, metrics2)
        
        best_layout = optimizer.get_best_layout()
        
        # Should return layout2 (better performance)
        assert best_layout["coherence_indicator"]["position"] == "main"

    def test_layout_hash_generation(self):
        """Test layout hash generation for performance tracking"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        layout1 = {"coherence_indicator": {"position": "main"}}
        layout2 = {"coherence_indicator": {"position": "sidebar"}}
        layout3 = {"coherence_indicator": {"position": "main"}}  # Same as layout1
        
        hash1 = optimizer._hash_layout(layout1)
        hash2 = optimizer._hash_layout(layout2)
        hash3 = optimizer._hash_layout(layout3)
        
        # Same layouts should have same hash
        assert hash1 == hash3
        
        # Different layouts should have different hashes
        assert hash1 != hash2
        
        # Hashes should be strings
        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 hash length

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_data(self, mock_json_dump, mock_file):
        """Test data saving to file"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        # Add some data
        optimizer.interaction_data["test"] = [{"type": "click"}]
        optimizer.layout_configs["test"] = {"position": "main"}
        optimizer.performance_metrics["test"] = {"metrics": {"satisfaction": 0.8}}
        
        optimizer.save_data()
        
        # Verify file operations
        mock_file.assert_called_once_with('ui_layout_learning.json', 'w')
        mock_json_dump.assert_called_once()
        
        # Verify data structure
        call_args = mock_json_dump.call_args[0]
        saved_data = call_args[0]
        
        assert "interaction_data" in saved_data
        assert "layout_configs" in saved_data
        assert "performance_metrics" in saved_data

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_data_file_not_found(self, mock_open):
        """Test graceful handling of missing data file"""
        optimizer = UILayoutOptimizer()
        
        # Should not raise exception
        assert len(optimizer.interaction_data) == 0
        assert len(optimizer.layout_configs) == 0
        assert len(optimizer.performance_metrics) == 0

    @patch("builtins.open", new_callable=mock_open, read_data='{"interaction_data": {"test": [{"type": "click"}]}}')
    @patch("json.load")
    def test_load_data_success(self, mock_json_load, mock_file):
        """Test successful data loading"""
        mock_json_load.return_value = {
            "interaction_data": {"test": [{"type": "click"}]},
            "layout_configs": {},
            "performance_metrics": {}
        }
        
        optimizer = UILayoutOptimizer()
        
        # Should load data
        assert "test" in optimizer.interaction_data
        assert optimizer.interaction_data["test"][0]["type"] == "click"

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_data_error_handling(self, mock_json_dump, mock_file):
        """Test error handling during save"""
        mock_json_dump.side_effect = Exception("Save failed")
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            optimizer = UILayoutOptimizer()
        
        # Should not raise exception
        optimizer.save_data()
        
        # Should handle error gracefully
        mock_json_dump.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
