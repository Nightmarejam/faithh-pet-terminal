"""
FAITHH AI-Driven User Experience System

Provides AI-powered user experience enhancements including:
- User behavior analysis and pattern recognition
- Adaptive interface components based on usage patterns
- Intelligent response optimization
- Personalized user experience features
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque
import threading
import statistics
import hashlib

@dataclass
class UserInteraction:
    """User interaction data point"""
    timestamp: datetime
    user_id: str
    session_id: str
    interaction_type: str  # 'query', 'navigation', 'feature_use', 'error'
    interaction_data: Dict[str, Any]
    response_time: float
    success: bool

@dataclass
class UserPattern:
    """Detected user behavior pattern"""
    pattern_type: str
    confidence: float
    frequency: int
    last_seen: datetime
    description: str
    recommendations: List[str]

class BehaviorAnalyzer:
    """Analyzes user behavior to identify patterns and preferences"""
    
    def __init__(self, pattern_threshold: float = 0.7):
        self.pattern_threshold = pattern_threshold
        self.user_interactions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.user_patterns: Dict[str, List[UserPattern]] = defaultdict(list)
        self.global_patterns: List[UserPattern] = []
        self.lock = threading.Lock()
    
    def add_interaction(self, user_id: str, session_id: str, interaction_type: str, 
                        interaction_data: Dict[str, Any], response_time: float, success: bool):
        """Add a new user interaction"""
        with self.lock:
            interaction = UserInteraction(
                timestamp=datetime.now(),
                user_id=user_id,
                session_id=session_id,
                interaction_type=interaction_type,
                interaction_data=interaction_data,
                response_time=response_time,
                success=success
            )
            
            self.user_interactions[user_id].append(interaction)
            
            # Analyze for patterns every 10 interactions
            if len(self.user_interactions[user_id]) % 10 == 0:
                self._analyze_user_patterns(user_id)
    
    def _analyze_user_patterns(self, user_id: str):
        """Analyze user interactions to identify patterns"""
        interactions = list(self.user_interactions[user_id])
        if len(interactions) < 10:
            return
        
        # Query patterns
        query_patterns = self._analyze_query_patterns(interactions)
        
        # Time patterns
        time_patterns = self._analyze_time_patterns(interactions)
        
        # Feature usage patterns
        feature_patterns = self._analyze_feature_patterns(interactions)
        
        # Error patterns
        error_patterns = self._analyze_error_patterns(interactions)
        
        # Combine all patterns
        all_patterns = query_patterns + time_patterns + feature_patterns + error_patterns
        
        # Filter by confidence threshold
        significant_patterns = [p for p in all_patterns if p.confidence >= self.pattern_threshold]
        
        self.user_patterns[user_id] = significant_patterns
        
        # Update global patterns
        for pattern in significant_patterns:
            self._update_global_patterns(pattern)
    
    def _analyze_query_patterns(self, interactions: List[UserInteraction]) -> List[UserPattern]:
        """Analyze query patterns"""
        patterns = []
        query_interactions = [i for i in interactions if i.interaction_type == 'query']
        
        if len(query_interactions) < 5:
            return patterns
        
        # Analyze query types
        query_types = defaultdict(int)
        for interaction in query_interactions:
            query_data = interaction.interaction_data
            intent_type = query_data.get('intent_type', 'unknown')
            query_types[intent_type] += 1
        
        # Identify dominant query type
        total_queries = len(query_interactions)
        for intent_type, count in query_types.items():
            if count / total_queries >= 0.6:  # 60% or more of queries
                pattern = UserPattern(
                    pattern_type='dominant_query_type',
                    confidence=count / total_queries,
                    frequency=count,
                    last_seen=max(i.timestamp for i in query_interactions),
                    description=f"User primarily asks {intent_type} questions",
                    recommendations=[
                        f"Optimize for {intent_type} queries",
                        f"Provide {intent_type}-focused suggestions",
                        f"Enhance {intent_type} response quality"
                    ]
                )
                patterns.append(pattern)
        
        # Analyze query complexity
        query_lengths = [len(i.interaction_data.get('query_text', '')) for i in query_interactions]
        if query_lengths:
            avg_length = statistics.mean(query_lengths)
            if avg_length > 100:  # Long queries
                pattern = UserPattern(
                    pattern_type='complex_queries',
                    confidence=min(0.9, avg_length / 200),
                    frequency=len([i for i in query_interactions if len(i.interaction_data.get('query_text', '')) > 100]),
                    last_seen=max(i.timestamp for i in query_interactions),
                    description="User prefers detailed, complex queries",
                    recommendations=[
                        "Provide comprehensive responses",
                        "Include detailed explanations",
                        "Offer follow-up suggestions"
                    ]
                )
                patterns.append(pattern)
            elif avg_length < 30:  # Short queries
                pattern = UserPattern(
                    pattern_type='concise_queries',
                    confidence=min(0.9, (100 - avg_length) / 100),
                    frequency=len([i for i in query_interactions if len(i.interaction_data.get('query_text', '')) < 30]),
                    last_seen=max(i.timestamp for i in query_interactions),
                    description="User prefers concise, direct queries",
                    recommendations=[
                        "Provide brief, direct responses",
                        "Use bullet points for clarity",
                        "Focus on key information"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_time_patterns(self, interactions: List[UserInteraction]) -> List[UserPattern]:
        """Analyze time-based patterns"""
        patterns = []
        
        # Analyze time of day
        hour_counts = defaultdict(int)
        for interaction in interactions:
            hour = interaction.timestamp.hour
            hour_counts[hour] += 1
        
        if len(hour_counts) >= 3:
            # Find peak hours
            max_count = max(hour_counts.values())
            peak_hours = [hour for hour, count in hour_counts.items() if count >= max_count * 0.8]
            
            if len(peak_hours) <= 3:  # Concentrated usage
                pattern = UserPattern(
                    pattern_type='time_preference',
                    confidence=max_count / len(interactions),
                    frequency=max_count,
                    last_seen=max(i.timestamp for i in interactions),
                    description=f"User typically active during {', '.join(map(str, peak_hours))} hours",
                    recommendations=[
                        "Optimize system performance during peak hours",
                        "Schedule maintenance during off-peak hours",
                        "Provide faster responses during preferred times"
                    ]
                )
                patterns.append(pattern)
        
        # Analyze session duration
        sessions = defaultdict(list)
        for interaction in interactions:
            sessions[interaction.session_id].append(interaction)
        
        session_durations = []
        for session_interactions in sessions.values():
            if len(session_interactions) >= 2:
                start_time = min(i.timestamp for i in session_interactions)
                end_time = max(i.timestamp for i in session_interactions)
                duration = (end_time - start_time).total_seconds()
                session_durations.append(duration)
        
        if session_durations:
            avg_duration = statistics.mean(session_durations)
            if avg_duration > 1800:  # Long sessions (>30 minutes)
                pattern = UserPattern(
                    pattern_type='long_sessions',
                    confidence=min(0.9, avg_duration / 3600),
                    frequency=len([d for d in session_durations if d > 1800]),
                    last_seen=max(i.timestamp for i in interactions),
                    description="User prefers long, detailed sessions",
                    recommendations=[
                        "Enable session persistence",
                        "Provide progressive disclosure",
                        "Offer in-depth exploration features"
                    ]
                )
                patterns.append(pattern)
            elif avg_duration < 300:  # Short sessions (<5 minutes)
                pattern = UserPattern(
                    pattern_type='short_sessions',
                    confidence=min(0.9, (600 - avg_duration) / 600),
                    frequency=len([d for d in session_durations if d < 300]),
                    last_seen=max(i.timestamp for i in interactions),
                    description="User prefers quick, focused sessions",
                    recommendations=[
                        "Optimize for quick responses",
                        "Provide immediate value",
                        "Minimize loading times"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_feature_patterns(self, interactions: List[UserInteraction]) -> List[UserPattern]:
        """Analyze feature usage patterns"""
        patterns = []
        feature_interactions = [i for i in interactions if i.interaction_type == 'feature_use']
        
        if len(feature_interactions) < 3:
            return patterns
        
        # Analyze feature preferences
        feature_counts = defaultdict(int)
        for interaction in feature_interactions:
            feature = interaction.interaction_data.get('feature_name', 'unknown')
            feature_counts[feature] += 1
        
        total_feature_uses = len(feature_interactions)
        for feature, count in feature_counts.items():
            if count / total_feature_uses >= 0.4:  # 40% or more of feature uses
                pattern = UserPattern(
                    pattern_type='feature_preference',
                    confidence=count / total_feature_uses,
                    frequency=count,
                    last_seen=max(i.timestamp for i in feature_interactions),
                    description=f"User frequently uses {feature} feature",
                    recommendations=[
                        f"Enhance {feature} functionality",
                        f"Provide {feature} shortcuts",
                        f"Offer {feature}-related suggestions"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_error_patterns(self, interactions: List[UserInteraction]) -> List[UserPattern]:
        """Analyze error patterns"""
        patterns = []
        error_interactions = [i for i in interactions if not i.success]
        
        if len(error_interactions) < 3:
            return patterns
        
        # Analyze error types
        error_types = defaultdict(int)
        for interaction in error_interactions:
            error_type = interaction.interaction_data.get('error_type', 'unknown')
            error_types[error_type] += 1
        
        total_errors = len(error_interactions)
        for error_type, count in error_types.items():
            if count / total_errors >= 0.3:  # 30% or more of errors
                pattern = UserPattern(
                    pattern_type='error_pattern',
                    confidence=count / total_errors,
                    frequency=count,
                    last_seen=max(i.timestamp for i in error_interactions),
                    description=f"User frequently encounters {error_type} errors",
                    recommendations=[
                        f"Fix {error_type} issues",
                        f"Provide {error_type} guidance",
                        f"Offer {error_type} prevention tips"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _update_global_patterns(self, pattern: UserPattern):
        """Update global patterns with new user pattern"""
        # Check if similar pattern exists globally
        for global_pattern in self.global_patterns:
            if (global_pattern.pattern_type == pattern.pattern_type and
                abs(global_pattern.confidence - pattern.confidence) < 0.2):
                # Update existing pattern
                global_pattern.frequency += pattern.frequency
                global_pattern.last_seen = max(global_pattern.last_seen, pattern.last_seen)
                global_pattern.confidence = (global_pattern.confidence + pattern.confidence) / 2
                return
        
        # Add new global pattern
        self.global_patterns.append(pattern)
        
        # Keep only significant global patterns
        if len(self.global_patterns) > 100:
            self.global_patterns = sorted(self.global_patterns, key=lambda p: p.frequency, reverse=True)[:50]
    
    def get_user_patterns(self, user_id: str) -> List[UserPattern]:
        """Get patterns for a specific user"""
        with self.lock:
            return self.user_patterns.get(user_id, [])
    
    def get_global_patterns(self) -> List[UserPattern]:
        """Get global user behavior patterns"""
        with self.lock:
            return self.global_patterns.copy()

class AdaptiveInterface:
    """Adaptive interface components based on user behavior"""
    
    def __init__(self):
        self.interface_preferences: Dict[str, Dict] = defaultdict(dict)
        self.adaptation_history: List[Dict] = []
        self.lock = threading.Lock()
    
    def adapt_interface(self, user_id: str, patterns: List[UserPattern]) -> Dict:
        """Generate interface adaptations based on user patterns"""
        adaptations = {
            'layout_changes': [],
            'feature_priorities': [],
            'response_style': 'default',
            'recommendations': []
        }
        
        for pattern in patterns:
            if pattern.pattern_type == 'dominant_query_type':
                intent_type = pattern.description.split('asks ')[1].split(' ')[0]
                adaptations['feature_priorities'].append(f"enhance_{intent_type}")
                adaptations['recommendations'].extend(pattern.recommendations)
            
            elif pattern.pattern_type == 'complex_queries':
                adaptations['layout_changes'].append('expand_response_area')
                adaptations['response_style'] = 'comprehensive'
                adaptations['recommendations'].extend(pattern.recommendations)
            
            elif pattern.pattern_type == 'concise_queries':
                adaptations['layout_changes'].append('compact_response_area')
                adaptations['response_style'] = 'concise'
                adaptations['recommendations'].extend(pattern.recommendations)
            
            elif pattern.pattern_type == 'feature_preference':
                feature = pattern.description.split('uses ')[1].split(' ')[0]
                adaptations['feature_priorities'].append(f"promote_{feature}")
                adaptations['recommendations'].extend(pattern.recommendations)
            
            elif pattern.pattern_type == 'long_sessions':
                adaptations['layout_changes'].append('enable_session_persistence')
                adaptations['recommendations'].extend(pattern.recommendations)
            
            elif pattern.pattern_type == 'short_sessions':
                adaptations['layout_changes'].append('optimize_for_speed')
                adaptations['recommendations'].extend(pattern.recommendations)
        
        # Store adaptation
        with self.lock:
            self.interface_preferences[user_id] = adaptations
            self.adaptation_history.append({
                'user_id': user_id,
                'timestamp': datetime.now(),
                'patterns_count': len(patterns),
                'adaptations': adaptations
            })
            
            # Keep history manageable
            if len(self.adaptation_history) > 1000:
                self.adaptation_history = self.adaptation_history[-500:]
        
        return adaptations
    
    def get_interface_preferences(self, user_id: str) -> Dict:
        """Get interface preferences for a user"""
        with self.lock:
            return self.interface_preferences.get(user_id, {})

class IntelligentResponseOptimizer:
    """Optimizes responses based on user behavior and context"""
    
    def __init__(self):
        self.response_patterns: Dict[str, Dict] = defaultdict(dict)
        self.optimization_history: List[Dict] = []
        self.lock = threading.Lock()
    
    def optimize_response(self, user_id: str, query_text: str, base_response: str, 
                        patterns: List[UserPattern]) -> Dict:
        """Optimize response based on user patterns"""
        optimizations = {
            'length_adjustment': 0,
            'style_adjustment': 'default',
            'content_priorities': [],
            'formatting_suggestions': []
        }
        
        # Apply pattern-based optimizations
        for pattern in patterns:
            if pattern.pattern_type == 'complex_queries':
                optimizations['length_adjustment'] += 0.3  # 30% longer
                optimizations['style_adjustment'] = 'detailed'
                optimizations['content_priorities'].extend(['comprehensive', 'examples', 'follow_up'])
                optimizations['formatting_suggestions'].extend(['structured', 'sections', 'bullet_points'])
            
            elif pattern.pattern_type == 'concise_queries':
                optimizations['length_adjustment'] -= 0.2  # 20% shorter
                optimizations['style_adjustment'] = 'direct'
                optimizations['content_priorities'].extend(['key_points', 'quick_answer'])
                optimizations['formatting_suggestions'].extend(['compact', 'highlighted'])
            
            elif pattern.pattern_type == 'dominant_query_type':
                intent_type = pattern.description.split('asks ')[1].split(' ')[0]
                optimizations['content_priorities'].append(f"focus_{intent_type}")
        
        # Apply length adjustment
        if optimizations['length_adjustment'] != 0:
            target_length = int(len(base_response) * (1 + optimizations['length_adjustment']))
            optimizations['target_length'] = max(100, target_length)  # Minimum 100 chars
        
        # Store optimization
        with self.lock:
            self.response_patterns[user_id] = optimizations
            self.optimization_history.append({
                'user_id': user_id,
                'timestamp': datetime.now(),
                'query_length': len(query_text),
                'base_response_length': len(base_response),
                'optimizations': optimizations
            })
            
            # Keep history manageable
            if len(self.optimization_history) > 1000:
                self.optimization_history = self.optimization_history[-500:]
        
        return optimizations
    
    def get_response_optimizations(self, user_id: str) -> Dict:
        """Get response optimizations for a user"""
        with self.lock:
            return self.response_patterns.get(user_id, {})

class AIDrivenUXSystem:
    """Main AI-driven UX system"""
    
    def __init__(self):
        self.behavior_analyzer = BehaviorAnalyzer()
        self.adaptive_interface = AdaptiveInterface()
        self.response_optimizer = IntelligentResponseOptimizer()
        self.user_sessions: Dict[str, Dict] = defaultdict(dict)
        self.lock = threading.Lock()
    
    def track_interaction(self, user_id: str, session_id: str, interaction_type: str,
                          interaction_data: Dict[str, Any], response_time: float, success: bool):
        """Track user interaction for analysis"""
        self.behavior_analyzer.add_interaction(
            user_id, session_id, interaction_type, interaction_data, response_time, success
        )
        
        # Update session
        with self.lock:
            if session_id not in self.user_sessions[user_id]:
                self.user_sessions[user_id][session_id] = {
                    'start_time': datetime.now(),
                    'interaction_count': 0,
                    'total_response_time': 0,
                    'success_count': 0
                }
            
            session = self.user_sessions[user_id][session_id]
            session['interaction_count'] += 1
            session['total_response_time'] += response_time
            if success:
                session['success_count'] += 1
    
    def get_personalized_experience(self, user_id: str) -> Dict:
        """Get personalized user experience recommendations"""
        patterns = self.behavior_analyzer.get_user_patterns(user_id)
        
        if not patterns:
            return {
                'personalization_level': 'none',
                'reason': 'Insufficient interaction history',
                'recommendations': ['Continue using the system to enable personalization']
            }
        
        # Get interface adaptations
        interface_adaptations = self.adaptive_interface.adapt_interface(user_id, patterns)
        
        # Get response optimizations
        response_optimizations = self.response_optimizer.get_response_optimizations(user_id)
        
        return {
            'personalization_level': 'high' if len(patterns) >= 5 else 'medium',
            'patterns_detected': len(patterns),
            'patterns': [
                {
                    'type': p.pattern_type,
                    'confidence': p.confidence,
                    'description': p.description,
                    'recommendations': p.recommendations
                }
                for p in patterns
            ],
            'interface_adaptations': interface_adaptations,
            'response_optimizations': response_optimizations,
            'global_insights': [
                {
                    'type': p.pattern_type,
                    'description': p.description,
                    'frequency': p.frequency
                }
                for p in self.behavior_analyzer.get_global_patterns()[:5]
            ]
        }
    
    def optimize_response_for_user(self, user_id: str, query_text: str, base_response: str) -> Dict:
        """Optimize response for specific user"""
        patterns = self.behavior_analyzer.get_user_patterns(user_id)
        optimizations = self.response_optimizer.optimize_response(
            user_id, query_text, base_response, patterns
        )
        
        return {
            'optimizations': optimizations,
            'personalized_response': self._apply_optimizations(base_response, optimizations),
            'confidence': sum(p.confidence for p in patterns) / len(patterns) if patterns else 0.0
        }
    
    def _apply_optimizations(self, base_response: str, optimizations: Dict) -> str:
        """Apply optimizations to base response"""
        response = base_response
        
        # Apply length adjustment
        if 'target_length' in optimizations:
            target_length = optimizations['target_length']
            if len(response) > target_length:
                # Truncate response
                response = response[:target_length-3] + "..."
            elif len(response) < target_length:
                # Note: In practice, this would expand the response with relevant content
                pass
        
        # Apply style adjustments
        style = optimizations.get('style_adjustment', 'default')
        if style == 'concise':
            # Add concise formatting
            if '\n' not in response and len(response) > 100:
                response = response.replace('. ', '.\n• ')
        elif style == 'detailed':
            # Add detailed formatting
            if '\n' not in response:
                response = response.replace('. ', '.\n\n')
        
        return response
    
    def get_ux_analytics(self) -> Dict:
        """Get comprehensive UX analytics"""
        with self.lock:
            return {
                'behavior_analyzer': {
                    'total_users': len(self.behavior_analyzer.user_interactions),
                    'total_interactions': sum(len(interactions) for interactions in self.behavior_analyzer.user_interactions.values()),
                    'global_patterns': len(self.behavior_analyzer.global_patterns),
                    'avg_patterns_per_user': sum(len(patterns) for patterns in self.behavior_analyzer.user_patterns.values()) / len(self.behavior_analyzer.user_patterns) if self.behavior_analyzer.user_patterns else 0
                },
                'adaptive_interface': {
                    'personalized_users': len(self.adaptive_interface.interface_preferences),
                    'total_adaptations': len(self.adaptive_interface.adaptation_history),
                    'most_common_adaptations': self._get_most_common_adaptations()
                },
                'response_optimizer': {
                    'optimized_users': len(self.response_optimizer.response_patterns),
                    'total_optimizations': len(self.response_optimizer.optimization_history),
                    'avg_optimization_confidence': self._get_avg_optimization_confidence()
                },
                'session_analytics': {
                    'active_sessions': sum(len(sessions) for sessions in self.user_sessions.values()),
                    'avg_session_duration': self._get_avg_session_duration(),
                    'avg_success_rate': self._get_avg_success_rate()
                }
            }
    
    def _get_most_common_adaptations(self) -> List[str]:
        """Get most common interface adaptations"""
        adaptation_counts = defaultdict(int)
        for adaptation in self.adaptive_interface.adaptation_history:
            for change in adaptation['adaptations'].get('layout_changes', []):
                adaptation_counts[change] += 1
        
        return [adaptation for adaptation, count in sorted(adaptation_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    def _get_avg_optimization_confidence(self) -> float:
        """Get average optimization confidence"""
        if not self.response_optimizer.optimization_history:
            return 0.0
        
        # This would calculate actual confidence from patterns
        return 0.75  # Placeholder
    
    def _get_avg_session_duration(self) -> float:
        """Get average session duration"""
        total_duration = 0
        session_count = 0
        
        for user_sessions in self.user_sessions.values():
            for session in user_sessions.values():
                if 'start_time' in session:
                    duration = (datetime.now() - session['start_time']).total_seconds()
                    total_duration += duration
                    session_count += 1
        
        return total_duration / session_count if session_count > 0 else 0.0
    
    def _get_avg_success_rate(self) -> float:
        """Get average success rate"""
        total_success = 0
        total_interactions = 0
        
        for user_sessions in self.user_sessions.values():
            for session in user_sessions.values():
                total_success += session.get('success_count', 0)
                total_interactions += session.get('interaction_count', 0)
        
        return total_success / total_interactions if total_interactions > 0 else 0.0

# Global AI-driven UX system instance
ai_driven_ux = AIDrivenUXSystem()
