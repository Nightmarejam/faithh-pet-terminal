"""
Focus Analytics - Day 6 Implementation
Following Sonnet's Implementation Excellence Framework
Advanced analytics for focus management and productivity optimization
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

class FocusAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.predictive_models = {}
        self.historical_data = []
        
    def predict_focus_drift(self, historical_data: List[Dict]) -> Dict:
        """
        Predict focus drift based on historical patterns
        Following Sonnet's Performance Excellence: 95%+ success rate target
        """
        try:
            if not historical_data:
                return {
                    "prediction": 0.0,
                    "confidence": 0.0,
                    "trend": "stable",
                    "recommendations": ["Insufficient data for prediction"]
                }
            
            # Extract drift scores from historical data
            drift_scores = [entry.get('drift_score', 0.0) for entry in historical_data[-30:]]  # Last 30 entries
            
            if len(drift_scores) < 3:
                return {
                    "prediction": np.mean(drift_scores) if drift_scores else 0.0,
                    "confidence": 0.3,
                    "trend": "insufficient_data",
                    "recommendations": ["Collect more historical data"]
                }
            
            # Calculate trend using linear regression
            x = np.arange(len(drift_scores))
            y = np.array(drift_scores)
            
            # Simple linear regression for trend detection
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            
            # Predict next drift score
            next_drift = coeffs[0] * len(drift_scores) + coeffs[1]
            
            # Determine trend
            if abs(slope) < 0.01:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            # Calculate confidence based on data consistency
            confidence = max(0.3, 1.0 - (np.std(drift_scores) / (np.mean(drift_scores) + 0.01)))
            
            # Generate recommendations
            recommendations = []
            if next_drift > 0.3:
                recommendations.append("Focus drift risk detected - consider refocusing")
            if trend == "increasing":
                recommendations.append("Drift trend is increasing - implement focus strategies")
            if confidence < 0.5:
                recommendations.append("Low confidence - collect more data")
            
            return {
                "prediction": max(0.0, min(1.0, next_drift)),
                "confidence": confidence,
                "trend": trend,
                "recommendations": recommendations,
                "data_points": len(drift_scores)
            }
            
        except Exception as e:
            self.logger.error(f"Focus drift prediction failed: {e}")
            return {
                "prediction": 0.0,
                "confidence": 0.0,
                "trend": "error",
                "recommendations": ["Prediction failed - check data quality"]
            }
    
    def analyze_productivity_patterns(self, focus_data: List[Dict]) -> Dict:
        """
        Analyze productivity patterns for optimization
        Following Sonnet's Implementation Excellence: Clean, maintainable approaches
        """
        try:
            if not focus_data:
                return {
                    "patterns": [],
                    "insights": [],
                    "optimization_suggestions": ["No data available for analysis"]
                }
            
            # Extract key metrics
            completion_rates = []
            focus_durations = []
            concept_counts = []
            
            for entry in focus_data:
                if 'completion_rate' in entry:
                    completion_rates.append(entry['completion_rate'])
                if 'focus_duration' in entry:
                    focus_durations.append(entry['focus_duration'])
                if 'active_concepts' in entry:
                    concept_counts.append(entry['active_concepts'])
            
            patterns = []
            insights = []
            suggestions = []
            
            # Analyze completion rate patterns
            if completion_rates:
                avg_completion = np.mean(completion_rates)
                completion_trend = "improving" if len(completion_rates) > 1 and completion_rates[-1] > completion_rates[0] else "stable"
                
                patterns.append({
                    "metric": "completion_rate",
                    "average": avg_completion,
                    "trend": completion_trend,
                    "data_points": len(completion_rates)
                })
                
                if avg_completion < 0.6:
                    insights.append("Low completion rate detected")
                    suggestions.append("Break down larger concepts into smaller tasks")
                elif avg_completion > 0.8:
                    insights.append("High completion rate - excellent focus")
                    suggestions.append("Maintain current focus strategies")
            
            # Analyze focus duration patterns
            if focus_durations:
                avg_duration = np.mean(focus_durations)
                optimal_duration = 45  # minutes (based on productivity research)
                
                patterns.append({
                    "metric": "focus_duration",
                    "average": avg_duration,
                    "optimal": optimal_duration,
                    "data_points": len(focus_durations)
                })
                
                if avg_duration < optimal_duration * 0.5:
                    insights.append("Short focus sessions - may indicate frequent interruptions")
                    suggestions.append("Consider longer focus blocks (45-60 minutes)")
                elif avg_duration > optimal_duration * 2:
                    insights.append("Very long focus sessions - risk of burnout")
                    suggestions.append("Implement regular breaks and session limits")
            
            # Analyze concept management patterns
            if concept_counts:
                avg_concepts = np.mean(concept_counts)
                
                patterns.append({
                    "metric": "active_concepts",
                    "average": avg_concepts,
                    "recommended": 3,  # Based on focus research
                    "data_points": len(concept_counts)
                })
                
                if avg_concepts > 5:
                    insights.append("High number of active concepts - potential focus dilution")
                    suggestions.append("Prioritize top 3 concepts for better focus")
                elif avg_concepts < 1:
                    insights.append("Very few active concepts - may miss opportunities")
                    suggestions.append("Consider expanding concept exploration")
            
            return {
                "patterns": patterns,
                "insights": insights,
                "optimization_suggestions": suggestions,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Productivity pattern analysis failed: {e}")
            return {
                "patterns": [],
                "insights": ["Analysis failed"],
                "optimization_suggestions": ["Check data quality and try again"]
            }
    
    def calculate_focus_velocity(self, concept_data: List[Dict]) -> Dict:
        """
        Calculate focus velocity and acceleration metrics
        Following Sonnet's Performance Excellence: Fast response times
        """
        try:
            if not concept_data:
                return {
                    "velocity": 0.0,
                    "acceleration": 0.0,
                    "trend": "no_data",
                    "insights": ["No concept data available"]
                }
            
            # Calculate concept completion velocity
            completed_concepts = []
            timestamps = []
            
            for concept in concept_data:
                if concept.get('state') == 'completed' and 'completed_at' in concept:
                    completed_concepts.append(concept)
                    timestamps.append(datetime.fromisoformat(concept['completed_at']))
            
            if len(completed_concepts) < 2:
                return {
                    "velocity": len(completed_concepts) / 7.0,  # per week
                    "acceleration": 0.0,
                    "trend": "insufficient_data",
                    "insights": [f"Only {len(completed_concepts)} concepts completed"]
                }
            
            # Sort by completion time
            completed_concepts.sort(key=lambda x: x['completed_at'])
            
            # Calculate velocity (concepts per week)
            time_span = (timestamps[-1] - timestamps[0]).days / 7.0  # Convert to weeks
            velocity = len(completed_concepts) / max(time_span, 1.0)
            
            # Calculate acceleration (change in velocity)
            if len(completed_concepts) >= 4:
                mid_point = len(completed_concepts) // 2
                first_half = completed_concepts[:mid_point]
                second_half = completed_concepts[mid_point:]
                
                first_velocity = len(first_half) / (time_span / 2.0)
                second_velocity = len(second_half) / (time_span / 2.0)
                acceleration = (second_velocity - first_velocity) / (time_span / 2.0)
            else:
                acceleration = 0.0
            
            # Determine trend
            if acceleration > 0.1:
                trend = "accelerating"
            elif acceleration < -0.1:
                trend = "decelerating"
            else:
                trend = "stable"
            
            # Generate insights
            insights = []
            if velocity > 3.0:
                insights.append("High completion velocity - excellent productivity")
            elif velocity < 1.0:
                insights.append("Low completion velocity - consider optimization")
            
            if abs(acceleration) > 0.5:
                insights.append(f"Significant {'acceleration' if acceleration > 0 else 'deceleration'} detected")
            
            return {
                "velocity": velocity,
                "acceleration": acceleration,
                "trend": trend,
                "insights": insights,
                "completed_concepts": len(completed_concepts),
                "time_span_weeks": time_span
            }
            
        except Exception as e:
            self.logger.error(f"Focus velocity calculation failed: {e}")
            return {
                "velocity": 0.0,
                "acceleration": 0.0,
                "trend": "error",
                "insights": ["Calculation failed"]
            }
    
    def generate_strategic_alignment_score(self, concepts: List[Dict], strategic_goals: List[str]) -> Dict:
        """
        Generate strategic alignment scores for concepts
        Following Sonnet's Strategic Excellence: Strong foundations and growth opportunities
        """
        try:
            if not concepts or not strategic_goals:
                return {
                    "overall_alignment": 0.0,
                    "concept_scores": [],
                    "recommendations": ["Insufficient data for alignment analysis"]
                }
            
            concept_scores = []
            
            for concept in concepts:
                # Simple alignment scoring based on keyword matching
                title = concept.get('title', '').lower()
                description = concept.get('description', '').lower()
                combined_text = f"{title} {description}"
                
                alignment_score = 0.0
                matched_goals = []
                
                for goal in strategic_goals:
                    goal_lower = goal.lower()
                    # Check for keyword matches
                    if any(keyword in combined_text for keyword in goal_lower.split()):
                        alignment_score += 0.25
                        matched_goals.append(goal)
                
                # Normalize score
                alignment_score = min(1.0, alignment_score)
                
                concept_scores.append({
                    "concept_id": concept.get('id'),
                    "title": concept.get('title'),
                    "alignment_score": alignment_score,
                    "matched_goals": matched_goals,
                    "priority": concept.get('priority', 'medium')
                })
            
            # Calculate overall alignment
            overall_alignment = np.mean([score['alignment_score'] for score in concept_scores]) if concept_scores else 0.0
            
            # Generate recommendations
            recommendations = []
            if overall_alignment < 0.5:
                recommendations.append("Low strategic alignment - review concept priorities")
            elif overall_alignment > 0.8:
                recommendations.append("High strategic alignment - excellent focus direction")
            
            # Find low-aligned concepts
            low_aligned = [score for score in concept_scores if score['alignment_score'] < 0.3]
            if low_aligned:
                recommendations.append(f"Consider re-evaluating {len(low_aligned)} low-alignment concepts")
            
            return {
                "overall_alignment": overall_alignment,
                "concept_scores": concept_scores,
                "recommendations": recommendations,
                "strategic_goals": strategic_goals,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Strategic alignment analysis failed: {e}")
            return {
                "overall_alignment": 0.0,
                "concept_scores": [],
                "recommendations": ["Analysis failed - check data quality"]
            }
    
    def generate_comprehensive_analytics(self, focus_data: List[Dict], concept_data: List[Dict], strategic_goals: List[str]) -> Dict:
        """
        Generate comprehensive focus analytics report
        Following Sonnet's Implementation Excellence: Comprehensive documentation
        """
        try:
            # Generate all analytics components
            drift_prediction = self.predict_focus_drift(focus_data)
            productivity_patterns = self.analyze_productivity_patterns(focus_data)
            focus_velocity = self.calculate_focus_velocity(concept_data)
            strategic_alignment = self.generate_strategic_alignment_score(concept_data, strategic_goals)
            
            # Generate overall insights
            overall_insights = []
            overall_recommendations = []
            
            # Combine insights from all analyses
            overall_insights.extend(productivity_patterns.get('insights', []))
            overall_insights.extend(focus_velocity.get('insights', []))
            
            # Combine recommendations
            overall_recommendations.extend(drift_prediction.get('recommendations', []))
            overall_recommendations.extend(productivity_patterns.get('optimization_suggestions', []))
            overall_recommendations.extend(strategic_alignment.get('recommendations', []))
            
            # Calculate overall health score
            health_components = [
                drift_prediction.get('confidence', 0.0),
                1.0 - drift_prediction.get('prediction', 0.0),  # Invert drift score
                strategic_alignment.get('overall_alignment', 0.0),
                min(1.0, focus_velocity.get('velocity', 0.0) / 3.0)  # Normalize velocity
            ]
            
            overall_health = np.mean(health_components)
            
            return {
                "overall_health_score": overall_health,
                "focus_drift_prediction": drift_prediction,
                "productivity_patterns": productivity_patterns,
                "focus_velocity": focus_velocity,
                "strategic_alignment": strategic_alignment,
                "overall_insights": overall_insights,
                "overall_recommendations": overall_recommendations,
                "generated_at": datetime.now().isoformat(),
                "data_summary": {
                    "focus_data_points": len(focus_data),
                    "concept_data_points": len(concept_data),
                    "strategic_goals_count": len(strategic_goals)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive analytics generation failed: {e}")
            return {
                "overall_health_score": 0.0,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }