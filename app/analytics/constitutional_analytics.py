"""
Constitutional Analytics - Day 6 Implementation
Following Sonnet's Implementation Excellence Framework
Advanced analytics for constitutional compliance and ethical decision monitoring
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

class ConstitutionalAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.principles_history = []
        self.compliance_records = []
        
    def calculate_compliance_score(self, decisions: List[Dict], principles: List[Dict]) -> Dict:
        """
        Calculate real-time constitutional compliance score
        Following Sonnet's Performance Excellence: 95%+ success rate target
        """
        try:
            if not decisions or not principles:
                return {
                    "overall_compliance": 0.0,
                    "principle_scores": {},
                    "trends": {},
                    "recommendations": ["Insufficient data for compliance analysis"]
                }
            
            principle_scores = {}
            principle_applications = {p['id']: [] for p in principles}
            
            # Analyze each decision against principles
            for decision in decisions:
                decision_text = f"{decision.get('title', '')} {decision.get('description', '')}".lower()
                
                for principle in principles:
                    principle_id = principle['id']
                    principle_keywords = principle.get('keywords', [])
                    
                    # Check if principle applies to decision
                    applies = any(keyword.lower() in decision_text for keyword in principle_keywords)
                    
                    if applies:
                        # Score based on decision outcome and principle alignment
                        alignment_score = self._calculate_decision_alignment(decision, principle)
                        principle_applications[principle_id].append(alignment_score)
            
            # Calculate principle scores
            for principle_id, scores in principle_applications.items():
                if scores:
                    principle_scores[principle_id] = {
                        "average_score": np.mean(scores),
                        "application_count": len(scores),
                        "trend": self._calculate_trend(scores),
                        "recent_score": np.mean(scores[-5:]) if len(scores) >= 5 else np.mean(scores)
                    }
                else:
                    principle_scores[principle_id] = {
                        "average_score": 0.0,
                        "application_count": 0,
                        "trend": "no_data",
                        "recent_score": 0.0
                    }
            
            # Calculate overall compliance
            if principle_scores:
                overall_compliance = np.mean([score['average_score'] for score in principle_scores.values()])
            else:
                overall_compliance = 0.0
            
            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(principle_scores, overall_compliance)
            
            return {
                "overall_compliance": overall_compliance,
                "principle_scores": principle_scores,
                "overall_trend": self._calculate_overall_trend(principle_scores),
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "decisions_analyzed": len(decisions),
                "principles_evaluated": len(principles)
            }
            
        except Exception as e:
            self.logger.error(f"Compliance score calculation failed: {e}")
            return {
                "overall_compliance": 0.0,
                "error": str(e),
                "recommendations": ["Analysis failed - check data quality"]
            }
    
    def _calculate_decision_alignment(self, decision: Dict, principle: Dict) -> float:
        """Calculate alignment score between decision and principle"""
        try:
            # Base score from decision outcome
            outcome_score = 0.5  # Neutral default
            
            if decision.get('outcome') == 'positive':
                outcome_score = 0.8
            elif decision.get('outcome') == 'negative':
                outcome_score = 0.2
            elif decision.get('outcome') == 'neutral':
                outcome_score = 0.5
            
            # Adjust based on explicit constitutional consideration
            if decision.get('constitutional_consideration'):
                outcome_score += 0.2
            
            # Adjust based on stakeholder impact
            stakeholder_impact = decision.get('stakeholder_impact', {})
            if stakeholder_impact.get('positive', 0) > stakeholder_impact.get('negative', 0):
                outcome_score += 0.1
            
            return min(1.0, max(0.0, outcome_score))
            
        except Exception:
            return 0.5  # Default neutral score
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend from a series of scores"""
        if len(scores) < 3:
            return "insufficient_data"
        
        # Simple trend calculation
        recent_avg = np.mean(scores[-3:])
        earlier_avg = np.mean(scores[-6:-3]) if len(scores) >= 6 else np.mean(scores[:-3])
        
        if recent_avg > earlier_avg + 0.05:
            return "improving"
        elif recent_avg < earlier_avg - 0.05:
            return "declining"
        else:
            return "stable"
    
    def _calculate_overall_trend(self, principle_scores: Dict) -> str:
        """Calculate overall trend across all principles"""
        trends = [score['trend'] for score in principle_scores.values() if score['trend'] != 'no_data']
        
        if not trends:
            return "no_data"
        
        improving_count = trends.count('improving')
        declining_count = trends.count('declining')
        stable_count = trends.count('stable')
        
        if improving_count > declining_count and improving_count > stable_count:
            return "improving"
        elif declining_count > improving_count and declining_count > stable_count:
            return "declining"
        else:
            return "stable"
    
    def _generate_compliance_recommendations(self, principle_scores: Dict, overall_compliance: float) -> List[str]:
        """Generate recommendations based on compliance analysis"""
        recommendations = []
        
        if overall_compliance < 0.6:
            recommendations.append("Overall compliance is below threshold - review decision-making process")
        elif overall_compliance > 0.8:
            recommendations.append("Excellent compliance - maintain current practices")
        
        # Identify low-scoring principles
        low_principles = [pid for pid, score in principle_scores.items() if score['average_score'] < 0.5]
        if low_principles:
            recommendations.append(f"Focus on improving compliance for {len(low_principles)} principles")
        
        # Identify declining trends
        declining_principles = [pid for pid, score in principle_scores.items() if score['trend'] == 'declining']
        if declining_principles:
            recommendations.append(f"Address declining compliance for {len(declining_principles)} principles")
        
        return recommendations
    
    def analyze_principle_effectiveness(self, principles: List[Dict], outcomes: List[Dict]) -> Dict:
        """
        Analyze the effectiveness of constitutional principles
        Following Sonnet's Implementation Excellence: Clean, maintainable approaches
        """
        try:
            if not principles or not outcomes:
                return {
                    "effectiveness_scores": {},
                    "insights": [],
                    "recommendations": ["Insufficient data for effectiveness analysis"]
                }
            
            effectiveness_scores = {}
            
            for principle in principles:
                principle_id = principle['id']
                principle_outcomes = []
                
                # Find outcomes related to this principle
                for outcome in outcomes:
                    if principle_id in outcome.get('applicable_principles', []):
                        principle_outcomes.append(outcome.get('success_rate', 0.5))
                
                if principle_outcomes:
                    effectiveness_scores[principle_id] = {
                        "average_effectiveness": np.mean(principle_outcomes),
                        "application_count": len(principle_outcomes),
                        "variance": np.var(principle_outcomes),
                        "trend": self._calculate_trend(principle_outcomes)
                    }
                else:
                    effectiveness_scores[principle_id] = {
                        "average_effectiveness": 0.0,
                        "application_count": 0,
                        "variance": 0.0,
                        "trend": "no_data"
                    }
            
            # Generate insights
            insights = []
            high_effectiveness = [pid for pid, score in effectiveness_scores.items() if score['average_effectiveness'] > 0.8]
            low_effectiveness = [pid for pid, score in effectiveness_scores.items() if score['average_effectiveness'] < 0.4]
            
            if high_effectiveness:
                insights.append(f"{len(high_effectiveness)} principles show high effectiveness")
            if low_effectiveness:
                insights.append(f"{len(low_effectiveness)} principles show low effectiveness")
            
            # Generate recommendations
            recommendations = []
            if low_effectiveness:
                recommendations.append("Review and refine low-effectiveness principles")
            
            # Check for high variance (inconsistent application)
            high_variance = [pid for pid, score in effectiveness_scores.items() if score['variance'] > 0.1]
            if high_variance:
                recommendations.append("Address inconsistent application of some principles")
            
            return {
                "effectiveness_scores": effectiveness_scores,
                "insights": insights,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Principle effectiveness analysis failed: {e}")
            return {
                "effectiveness_scores": {},
                "insights": ["Analysis failed"],
                "recommendations": ["Check data quality"]
            }
    
    def track_ethical_decision_patterns(self, decisions: List[Dict]) -> Dict:
        """
        Track patterns in ethical decision-making
        Following Sonnet's Strategic Excellence: Strong foundations and growth opportunities
        """
        try:
            if not decisions:
                return {
                    "patterns": [],
                    "quality_metrics": {},
                    "recommendations": ["No decision data available"]
                }
            
            # Extract ethical decision patterns
            ethical_decisions = [d for d in decisions if d.get('ethical_consideration', False)]
            
            # Calculate quality metrics
            total_decisions = len(decisions)
            ethical_ratio = len(ethical_decisions) / total_decisions if total_decisions > 0 else 0
            
            # Analyze decision quality
            positive_outcomes = sum(1 for d in decisions if d.get('outcome') == 'positive')
            decision_quality = positive_outcomes / total_decisions if total_decisions > 0 else 0
            
            # Analyze stakeholder consideration
            stakeholder_considered = sum(1 for d in decisions if d.get('stakeholder_impact'))
            stakeholder_ratio = stakeholder_considered / total_decisions if total_decisions > 0 else 0
            
            # Analyze time patterns
            time_patterns = self._analyze_decision_timing(decisions)
            
            # Generate patterns
            patterns = [
                {
                    "pattern": "ethical_consideration_ratio",
                    "value": ethical_ratio,
                    "description": "Ratio of decisions with ethical consideration"
                },
                {
                    "pattern": "decision_quality",
                    "value": decision_quality,
                    "description": "Ratio of positive decision outcomes"
                },
                {
                    "pattern": "stakeholder_consideration",
                    "value": stakeholder_ratio,
                    "description": "Ratio of decisions considering stakeholders"
                }
            ]
            
            # Add time patterns
            patterns.extend(time_patterns)
            
            # Generate recommendations
            recommendations = []
            if ethical_ratio < 0.5:
                recommendations.append("Increase ethical consideration in decision-making")
            if decision_quality < 0.7:
                recommendations.append("Improve decision quality through better analysis")
            if stakeholder_ratio < 0.6:
                recommendations.append("Enhance stakeholder consideration in decisions")
            
            return {
                "patterns": patterns,
                "quality_metrics": {
                    "ethical_ratio": ethical_ratio,
                    "decision_quality": decision_quality,
                    "stakeholder_ratio": stakeholder_ratio,
                    "total_decisions": total_decisions
                },
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Ethical decision pattern analysis failed: {e}")
            return {
                "patterns": [],
                "quality_metrics": {},
                "recommendations": ["Analysis failed"]
            }
    
    def _analyze_decision_timing(self, decisions: List[Dict]) -> List[Dict]:
        """Analyze timing patterns in decision-making"""
        try:
            timing_patterns = []
            
            # Extract timestamps
            timestamps = []
            for decision in decisions:
                if 'timestamp' in decision:
                    timestamps.append(datetime.fromisoformat(decision['timestamp']))
            
            if len(timestamps) < 2:
                return []
            
            # Calculate decision frequency
            time_span = (timestamps[-1] - timestamps[0]).days
            decision_frequency = len(timestamps) / max(time_span, 1)
            
            timing_patterns.append({
                "pattern": "decision_frequency",
                "value": decision_frequency,
                "description": "Decisions per day",
                "unit": "decisions/day"
            })
            
            # Analyze decision speed (if creation and completion times available)
            decision_times = []
            for decision in decisions:
                if 'created_at' in decision and 'completed_at' in decision:
                    created = datetime.fromisoformat(decision['created_at'])
                    completed = datetime.fromisoformat(decision['completed_at'])
                    decision_time = (completed - created).total_seconds() / 3600  # hours
                    decision_times.append(decision_time)
            
            if decision_times:
                avg_decision_time = np.mean(decision_times)
                timing_patterns.append({
                    "pattern": "decision_speed",
                    "value": avg_decision_time,
                    "description": "Average time to complete decisions",
                    "unit": "hours"
                })
            
            return timing_patterns
            
        except Exception as e:
            self.logger.error(f"Decision timing analysis failed: {e}")
            return []
    
    def generate_constitutional_health_report(self, principles: List[Dict], decisions: List[Dict], outcomes: List[Dict]) -> Dict:
        """
        Generate comprehensive constitutional health report
        Following Sonnet's Implementation Excellence: Comprehensive documentation
        """
        try:
            # Generate all analytics components
            compliance_analysis = self.calculate_compliance_score(decisions, principles)
            effectiveness_analysis = self.analyze_principle_effectiveness(principles, outcomes)
            ethical_patterns = self.track_ethical_decision_patterns(decisions)
            
            # Calculate overall constitutional health
            health_components = [
                compliance_analysis.get('overall_compliance', 0.0),
                np.mean([score['average_effectiveness'] for score in effectiveness_analysis.get('effectiveness_scores', {}).values()]) if effectiveness_analysis.get('effectiveness_scores') else 0.0,
                ethical_patterns.get('quality_metrics', {}).get('decision_quality', 0.0)
            ]
            
            overall_health = np.mean(health_components)
            
            # Generate health status
            if overall_health > 0.8:
                health_status = "excellent"
            elif overall_health > 0.6:
                health_status = "good"
            elif overall_health > 0.4:
                health_status = "fair"
            else:
                health_status = "poor"
            
            # Combine all recommendations
            all_recommendations = []
            all_recommendations.extend(compliance_analysis.get('recommendations', []))
            all_recommendations.extend(effectiveness_analysis.get('recommendations', []))
            all_recommendations.extend(ethical_patterns.get('recommendations', []))
            
            # Remove duplicates
            unique_recommendations = list(set(all_recommendations))
            
            # Generate key insights
            key_insights = [
                f"Overall constitutional health: {health_status} ({overall_health:.1%})",
                f"Compliance score: {compliance_analysis.get('overall_compliance', 0.0):.1%}",
                f"Decision quality: {ethical_patterns.get('quality_metrics', {}).get('decision_quality', 0.0):.1%}",
                f"Principles evaluated: {len(principles)}",
                f"Decisions analyzed: {len(decisions)}"
            ]
            
            return {
                "overall_health_score": overall_health,
                "health_status": health_status,
                "compliance_analysis": compliance_analysis,
                "effectiveness_analysis": effectiveness_analysis,
                "ethical_patterns": ethical_patterns,
                "key_insights": key_insights,
                "recommendations": unique_recommendations,
                "generated_at": datetime.now().isoformat(),
                "data_summary": {
                    "principles_count": len(principles),
                    "decisions_count": len(decisions),
                    "outcomes_count": len(outcomes)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Constitutional health report generation failed: {e}")
            return {
                "overall_health_score": 0.0,
                "health_status": "error",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }