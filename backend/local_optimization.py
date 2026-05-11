"""
FAITHH Local AI Optimization System

Provides intelligent model selection and optimization
for local AI providers based on query characteristics.

Priority: Phase 4.2 - Advanced AI Integration
"""

import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import json

class ModelPerformanceProfile:
    """Performance profile for a specific model"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.total_requests = 0
        self.successful_requests = 0
        self.total_response_time = 0.0
        self.total_tokens_processed = 0
        self.error_count = 0
        self.last_used = None
        self.performance_history = deque(maxlen=100)
        
        # Model characteristics
        self.context_length = 8192  # Default, can be updated
        self.is_local = True
        self.specialization = []
        self.strengths = []
        self.weaknesses = []
        
        # Performance metrics
        self.avg_response_time = 0.0
        self.success_rate = 100.0
        self.tokens_per_second = 0.0
    
    def update_performance(self, response_time: float, success: bool, 
                          tokens_processed: int = 0, error: str = None):
        """Update performance metrics"""
        self.total_requests += 1
        self.total_response_time += response_time
        self.total_tokens_processed += tokens_processed
        self.last_used = datetime.now()
        
        if success:
            self.successful_requests += 1
        else:
            self.error_count += 1
        
        # Update calculated metrics
        self.avg_response_time = self.total_response_time / self.total_requests
        self.success_rate = (self.successful_requests / self.total_requests) * 100
        
        if self.total_response_time > 0:
            self.tokens_per_second = self.total_tokens_processed / self.total_response_time
        
        # Add to history
        self.performance_history.append({
            'timestamp': datetime.now(),
            'response_time': response_time,
            'success': success,
            'tokens_processed': tokens_processed,
            'error': error
        })
    
    def get_recent_performance(self, minutes: int = 30) -> Dict:
        """Get recent performance metrics"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = [
            perf for perf in self.performance_history
            if perf['timestamp'] >= cutoff_time
        ]
        
        if not recent:
            return {
                'requests': 0,
                'success_rate': 100.0,
                'avg_response_time': 0.0,
                'tokens_per_second': 0.0
            }
        
        successful = [r for r in recent if r['success']]
        total_time = sum(r['response_time'] for r in recent)
        total_tokens = sum(r['tokens_processed'] for r in recent)
        
        return {
            'requests': len(recent),
            'success_rate': (len(successful) / len(recent)) * 100,
            'avg_response_time': total_time / len(recent),
            'tokens_per_second': total_tokens / total_time if total_time > 0 else 0.0
        }
    
    def is_suitable_for_query(self, query_analysis: Dict) -> Tuple[bool, float]:
        """Determine if model is suitable for query with confidence score"""
        confidence = 0.5  # Base confidence
        
        # Check recent performance
        recent_perf = self.get_recent_performance()
        if recent_perf['success_rate'] < 80:
            confidence -= 0.3
        elif recent_perf['success_rate'] > 95:
            confidence += 0.2
        
        if recent_perf['avg_response_time'] > 10:  # 10 seconds
            confidence -= 0.2
        elif recent_perf['avg_response_time'] < 3:  # 3 seconds
            confidence += 0.1
        
        # Check query complexity vs model capabilities
        query_complexity = query_analysis.get('complexity_score', 0.5)
        
        if query_complexity > 0.7 and 'reasoning' in self.strengths:
            confidence += 0.2
        elif query_complexity > 0.7 and 'reasoning' in self.weaknesses:
            confidence -= 0.2
        
        # Check context length requirements
        required_context = query_analysis.get('estimated_context_tokens', 1000)
        if required_context > self.context_length * 0.8:  # 80% of context
            confidence -= 0.4
        
        # Check specialization match
        query_domains = query_analysis.get('domains', [])
        if any(domain in self.specialization for domain in query_domains):
            confidence += 0.3
        
        return confidence > 0.3, min(confidence, 1.0)

class QueryAnalyzer:
    """Analyzes query characteristics for model selection"""
    
    def __init__(self):
        self.complexity_patterns = {
            'simple': [
                r'^(what|how|who|when|where|why)\s+',
                r'^(is|are|do|does|did|can|will|would|should)\s+',
                r'^(tell|show|give|list)\s+me\s+',
                r'\?$'
            ],
            'moderate': [
                r'(explain|describe|summarize|compare)',
                r'(difference|advantage|disadvantage)',
                r'(step|process|method|approach)',
                r'(example|instance|case)'
            ],
            'complex': [
                r'(analyze|evaluate|critique|assess)',
                r'(optimize|improve|enhance|refine)',
                r'(integrate|combine|merge|synthesize)',
                r'(design|architect|implement|develop)',
                r'(debug|troubleshoot|fix|resolve)'
            ]
        }
        
        self.domain_patterns = {
            'coding': [
                r'(code|programming|software|app|application)',
                r'(python|javascript|java|cpp|html|css)',
                r'(function|class|method|variable|algorithm)',
                r'(debug|test|deploy|commit|repository)'
            ],
            'business': [
                r'(business|company|market|customer|client)',
                r'(revenue|profit|cost|budget|finance)',
                r'(strategy|plan|goal|objective|target)',
                r'(marketing|sales|product|service)'
            ],
            'research': [
                r'(research|study|analysis|investigation)',
                r'(data|experiment|hypothesis|methodology)',
                r'(paper|article|publication|journal)',
                r'(theory|framework|model|approach)'
            ],
            'creative': [
                r'(create|design|write|compose|generate)',
                r'(story|poem|song|art|creative)',
                r'(imagine|envision|conceptualize)',
                r'(aesthetic|style|tone|mood)'
            ]
        }
    
    def analyze_query(self, query: str, context: Dict = None) -> Dict:
        """Analyze query characteristics"""
        if context is None:
            context = {}
        
        query_lower = query.lower()
        query_length = len(query)
        
        # Determine complexity
        complexity_score = 0.5
        complexity_level = 'moderate'
        
        # Check against patterns
        for level, patterns in self.complexity_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, query_lower))
            if matches > 0:
                if level == 'simple':
                    complexity_score -= 0.2
                elif level == 'complex':
                    complexity_score += 0.3
                
                if matches >= 2:
                    complexity_level = level
                    break
        
        # Adjust based on query length
        if query_length < 50:
            complexity_score -= 0.1
        elif query_length > 500:
            complexity_score += 0.2
        
        complexity_score = max(0.0, min(1.0, complexity_score))
        
        # Identify domains
        domains = []
        for domain, patterns in self.domain_patterns.items():
            if any(re.search(pattern, query_lower) for pattern in patterns):
                domains.append(domain)
        
        # Estimate context requirements
        estimated_context = self._estimate_context_requirements(query, context)
        
        # Check for specific requirements
        requires_rag = self._requires_rag(query, context)
        requires_reasoning = self._requires_reasoning(query)
        requires_creativity = self._requires_creativity(query)
        
        return {
            'query': query,
            'length': query_length,
            'complexity_score': complexity_score,
            'complexity_level': complexity_level,
            'domains': domains,
            'estimated_context_tokens': estimated_context,
            'requires_rag': requires_rag,
            'requires_reasoning': requires_reasoning,
            'requires_creativity': requires_creativity,
            'timestamp': datetime.now().isoformat()
        }
    
    def _estimate_context_requirements(self, query: str, context: Dict) -> int:
        """Estimate context token requirements"""
        base_tokens = 1000
        
        # Increase based on query characteristics
        if len(query) > 200:
            base_tokens += 500
        
        if any(word in query.lower() for word in ['recent', 'latest', 'current', 'status']):
            base_tokens += 800
        
        if any(word in query.lower() for word in ['history', 'past', 'previous', 'before']):
            base_tokens += 1200
        
        if 'compare' in query.lower() or 'versus' in query.lower():
            base_tokens += 600
        
        # Add context from existing conversation
        if context.get('conversation_history'):
            base_tokens += len(context['conversation_history']) * 100
        
        return base_tokens
    
    def _requires_rag(self, query: str, context: Dict) -> bool:
        """Check if query requires RAG"""
        rag_indicators = [
            'what', 'how', 'why', 'when', 'where', 'who',
            'tell me', 'show me', 'find', 'search', 'look up',
            'information', 'data', 'details', 'specifics'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in rag_indicators)
    
    def _requires_reasoning(self, query: str) -> bool:
        """Check if query requires reasoning"""
        reasoning_indicators = [
            'analyze', 'evaluate', 'compare', 'assess',
            'optimize', 'improve', 'solve', 'determine',
            'best', 'worst', 'better', 'recommend'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in reasoning_indicators)
    
    def _requires_creativity(self, query: str) -> bool:
        """Check if query requires creativity"""
        creative_indicators = [
            'create', 'design', 'write', 'compose', 'generate',
            'imagine', 'envision', 'brainstorm', 'suggest',
            'idea', 'concept', 'innovative', 'original'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in creative_indicators)

class LocalAIOptimizer:
    """Main local AI optimization system"""
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.model_profiles: Dict[str, ModelPerformanceProfile] = {}
        self.selection_history = deque(maxlen=1000)
        self.optimization_rules = []
        
        # Initialize model profiles
        self._initialize_model_profiles()
        
        # Performance thresholds
        self.thresholds = {
            'min_success_rate': 70.0,  # Minimum success rate
            'max_response_time': 15.0,  # Maximum response time
            'min_confidence': 0.3      # Minimum confidence for selection
        }
    
    def _initialize_model_profiles(self):
        """Initialize profiles for available models"""
        models_config = [
            {
                'name': 'qwen25-grounded:latest',
                'context_length': 8192,
                'is_local': True,
                'specialization': ['reasoning', 'grounding', 'general'],
                'strengths': ['reasoning', 'accuracy', 'reliability'],
                'weaknesses': ['creativity', 'speed']
            }
        ]
        
        for config in models_config:
            profile = ModelPerformanceProfile(config['name'])
            profile.context_length = config['context_length']
            profile.is_local = config['is_local']
            profile.specialization = config['specialization']
            profile.strengths = config['strengths']
            profile.weaknesses = config['weaknesses']
            
            self.model_profiles[config['name']] = profile
    
    def select_optimal_model(self, query: str, context: Dict = None, 
                           available_models: List[str] = None) -> Tuple[str, float]:
        """Select optimal model for query"""
        if context is None:
            context = {}
        
        if available_models is None:
            available_models = list(self.model_profiles.keys())
        
        # Analyze query
        query_analysis = self.query_analyzer.analyze_query(query, context)
        
        # Score each available model
        model_scores = []
        for model_name in available_models:
            if model_name not in self.model_profiles:
                continue
            
            profile = self.model_profiles[model_name]
            
            # Check if model meets minimum requirements
            recent_perf = profile.get_recent_performance()
            if recent_perf['success_rate'] < self.thresholds['min_success_rate']:
                continue
            
            if recent_perf['avg_response_time'] > self.thresholds['max_response_time']:
                continue
            
            # Get suitability score
            suitable, confidence = profile.is_suitable_for_query(query_analysis)
            if not suitable:
                continue
            
            # Apply optimization rules
            adjusted_confidence = self._apply_optimization_rules(
                model_name, query_analysis, confidence
            )
            
            model_scores.append((model_name, adjusted_confidence))
        
        # Sort by confidence score
        model_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select best model
        if model_scores:
            selected_model, confidence = model_scores[0]
            
            # Record selection
            self.selection_history.append({
                'timestamp': datetime.now(),
                'query_analysis': query_analysis,
                'selected_model': selected_model,
                'confidence': confidence,
                'alternatives': model_scores[1:3] if len(model_scores) > 1 else []
            })
            
            return selected_model, confidence
        else:
            # Fallback to default model
            default_model = 'qwen25-grounded:latest'
            if default_model in available_models:
                return default_model, 0.5
            else:
                return available_models[0] if available_models else 'qwen25-grounded:latest', 0.5
    
    def _apply_optimization_rules(self, model_name: str, query_analysis: Dict, 
                                base_confidence: float) -> float:
        """Apply optimization rules to adjust confidence"""
        confidence = base_confidence
        
        # Rule 1: Prefer local models for privacy-sensitive queries
        privacy_keywords = ['personal', 'private', 'confidential', 'sensitive']
        if any(keyword in query_analysis['query'].lower() for keyword in privacy_keywords):
            profile = self.model_profiles.get(model_name)
            if profile and profile.is_local:
                confidence += 0.2
            else:
                confidence -= 0.3
        
        # Rule 2: Boost confidence for domain-specialized models
        domains = query_analysis.get('domains', [])
        profile = self.model_profiles.get(model_name)
        if profile:
            domain_match = any(domain in profile.specialization for domain in domains)
            if domain_match:
                confidence += 0.15
        
        # Rule 3: Consider recent performance trends
        profile = self.model_profiles.get(model_name)
        if profile:
            recent_perf = profile.get_recent_performance(10)  # Last 10 requests
            if recent_perf['requests'] >= 5:
                if recent_perf['success_rate'] > 95:
                    confidence += 0.1
                elif recent_perf['success_rate'] < 80:
                    confidence -= 0.2
        
        # Rule 4: Adjust for complexity requirements
        complexity = query_analysis.get('complexity_score', 0.5)
        if complexity > 0.8 and model_name == 'llama-3.3-70b-versatile':
            confidence += 0.1  # Large model for complex queries
        elif complexity < 0.3 and model_name == 'qwen25-grounded:latest':
            confidence += 0.1  # Efficient model for simple queries
        
        return max(0.0, min(1.0, confidence))
    
    def setup_quality_monitoring(self):
        """Set up quality monitoring framework"""
        self.quality_metrics = {
            'response_quality_scores': deque(maxlen=1000),
            'user_satisfaction_ratings': deque(maxlen=500),
            'context_utilization_rates': deque(maxlen=1000),
            'response_relevance_scores': deque(maxlen=1000),
            'latency_satisfaction': deque(maxlen=1000)
        }
        
        self.quality_thresholds = {
            'min_response_quality': 0.7,
            'min_user_satisfaction': 0.8,
            'min_context_utilization': 0.6,
            'min_relevance_score': 0.75,
            'max_acceptable_latency': 5.0  # seconds
        }
        
        print("✅ Quality monitoring framework initialized")
    
    def record_quality_metrics(self, model_name: str, metrics: Dict):
        """Record quality metrics for a model response"""
        timestamp = datetime.now()
        
        # Record metrics for the specific model
        profile = self.model_profiles.get(model_name)
        if profile:
            profile.quality_history.append({
                'timestamp': timestamp,
                'metrics': metrics
            })
            
            # Update global quality tracking
            for metric_name, value in metrics.items():
                if metric_name in self.quality_metrics:
                    self.quality_metrics[metric_name].append({
                        'timestamp': timestamp,
                        'model': model_name,
                        'value': value
                    })
    
    def analyze_quality_trends(self, model_name: str = None, hours: int = 24) -> Dict:
        """Analyze quality trends over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        trends = {}
        
        models_to_analyze = [model_name] if model_name else list(self.model_profiles.keys())
        
        for model in models_to_analyze:
            profile = self.model_profiles.get(model)
            if not profile:
                continue
                
            recent_quality = [
                entry for entry in profile.quality_history
                if entry['timestamp'] > cutoff_time
            ]
            
            if not recent_quality:
                trends[model] = {'status': 'no_data'}
                continue
            
            # Calculate trend metrics
            avg_quality = sum(
                entry['metrics'].get('response_quality', 0) 
                for entry in recent_quality
            ) / len(recent_quality)
            
            avg_satisfaction = sum(
                entry['metrics'].get('user_satisfaction', 0) 
                for entry in recent_quality
            ) / len(recent_quality)
            
            avg_latency = sum(
                entry['metrics'].get('response_time', 0) 
                for entry in recent_quality
            ) / len(recent_quality)
            
            trends[model] = {
                'status': 'analyzed',
                'sample_size': len(recent_quality),
                'avg_response_quality': avg_quality,
                'avg_user_satisfaction': avg_satisfaction,
                'avg_response_time': avg_latency,
                'quality_trend': 'improving' if len(recent_quality) > 1 else 'insufficient_data'
            }
        
        return trends
    
    def auto_tune_parameters(self, model_name: str) -> Dict:
        """Automatically tune model parameters based on performance"""
        profile = self.model_profiles.get(model_name)
        if not profile:
            return {}
        
        recent_performance = profile.get_recent_performance(20)
        tuning_recommendations = {}
        
        # Analyze response quality
        if recent_performance['requests'] >= 10:
            success_rate = recent_performance['success_rate']
            avg_response_time = recent_performance['avg_response_time']
            
            # Temperature tuning based on quality
            if success_rate < 85:
                tuning_recommendations['temperature'] = {
                    'current': 0.7,
                    'recommended': 0.5,
                    'reason': 'Lower temperature to improve consistency'
                }
            elif success_rate > 95 and avg_response_time < 2:
                tuning_recommendations['temperature'] = {
                    'current': 0.7,
                    'recommended': 0.8,
                    'reason': 'Increase temperature for more creative responses'
                }
            
            # Token limit tuning
            if avg_response_time > 8:
                tuning_recommendations['max_tokens'] = {
                    'current': 4096,
                    'recommended': 2048,
                    'reason': 'Reduce token limit to improve response time'
                }
            elif avg_response_time < 2:
                tuning_recommendations['max_tokens'] = {
                    'current': 4096,
                    'recommended': 6144,
                    'reason': 'Increase token limit for more comprehensive responses'
                }
        
        return tuning_recommendations
    
    def generate_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_models': len(self.model_profiles),
            'models_analyzed': 0,
            'optimization_recommendations': {},
            'quality_summary': {},
            'performance_issues': []
        }
        
        # Analyze all models
        for model_name, profile in self.model_profiles.items():
            if profile.total_requests > 0:
                report['models_analyzed'] += 1
                
                # Get recent performance
                recent_perf = profile.get_recent_performance()
                
                # Check for performance issues
                if recent_perf['success_rate'] < 80:
                    report['performance_issues'].append({
                        'model': model_name,
                        'issue': f'Low success rate: {recent_perf["success_rate"]:.1f}%',
                        'severity': 'high' if recent_perf['success_rate'] < 70 else 'medium'
                    })
                
                if recent_perf['avg_response_time'] > 10:
                    report['performance_issues'].append({
                        'model': model_name,
                        'issue': f'High response time: {recent_perf["avg_response_time"]:.1f}s',
                        'severity': 'high' if recent_perf['avg_response_time'] > 15 else 'medium'
                    })
                
                # Get tuning recommendations
                tuning = self.auto_tune_parameters(model_name)
                if tuning:
                    report['optimization_recommendations'][model_name] = tuning
        
        # Quality summary
        for metric_name, metric_data in self.quality_metrics.items():
            if metric_data:
                recent_values = [
                    entry['value'] for entry in metric_data
                    if entry['timestamp'] > datetime.now() - timedelta(hours=24)
                ]
                if recent_values:
                    report['quality_summary'][metric_name] = {
                        'avg': sum(recent_values) / len(recent_values),
                        'min': min(recent_values),
                        'max': max(recent_values),
                        'sample_size': len(recent_values)
                    }
        
        return report
    
    def apply_auto_tuning(self, model_name: str, recommendations: Dict) -> bool:
        """Apply automatic tuning recommendations"""
        try:
            # This would integrate with the configuration system
            # For now, we'll just log the recommendations
            print(f"🔧 Auto-tuning recommendations for {model_name}:")
            for param, rec in recommendations.items():
                print(f"   {param}: {rec['current']} → {rec['recommended']} ({rec['reason']})")
            
            # In a full implementation, this would update config.yaml
            # and notify the backend of parameter changes
            return True
        except Exception as e:
            print(f"❌ Failed to apply auto-tuning for {model_name}: {e}")
            return False
    
    def update_model_performance(self, model_name: str, response_time: float, 
                             success: bool, tokens_processed: int = 0, 
                             error: str = None):
        """Update model performance metrics"""
        if model_name not in self.model_profiles:
            self.model_profiles[model_name] = ModelPerformanceProfile(model_name)
        
        self.model_profiles[model_name].update_performance(
            response_time, success, tokens_processed, error
        )
    
    def get_optimization_stats(self) -> Dict:
        """Get optimization statistics"""
        total_selections = len(self.selection_history)
        if total_selections == 0:
            return {
                'total_selections': 0,
                'model_usage': {},
                'avg_confidence': 0.0,
                'success_rate': 0.0
            }
        
        # Model usage statistics
        model_usage = defaultdict(int)
        total_confidence = 0.0
        
        for selection in self.selection_history:
            model_usage[selection['selected_model']] += 1
            total_confidence += selection['confidence']
        
        # Calculate success rate
        successful_selections = 0
        for selection in self.selection_history:
            model_name = selection['selected_model']
            if model_name in self.model_profiles:
                profile = self.model_profiles[model_name]
                recent_perf = profile.get_recent_performance(30)  # Last 30 minutes
                if recent_perf['success_rate'] > 80:
                    successful_selections += 1
        
        return {
            'total_selections': total_selections,
            'model_usage': dict(model_usage),
            'avg_confidence': total_confidence / total_selections,
            'success_rate': (successful_selections / total_selections) * 100,
            'model_performance': {
                name: profile.get_recent_performance()
                for name, profile in self.model_profiles.items()
            }
        }
    
    def get_recommendations(self) -> List[Dict]:
        """Get optimization recommendations"""
        recommendations = []
        
        for model_name, profile in self.model_profiles.items():
            recent_perf = profile.get_recent_performance()
            
            # Check for poor performance
            if recent_perf['success_rate'] < 70:
                recommendations.append({
                    'type': 'performance_issue',
                    'model': model_name,
                    'issue': f'Low success rate: {recent_perf["success_rate"]:.1f}%',
                    'suggestion': 'Consider using alternative model or investigating errors'
                })
            
            if recent_perf['avg_response_time'] > 10:
                recommendations.append({
                    'type': 'performance_issue',
                    'model': model_name,
                    'issue': f'High response time: {recent_perf["avg_response_time"]:.1f}s',
                    'suggestion': 'Consider using faster model or optimizing query complexity'
                })
        
        return recommendations

# Global optimizer instance
local_ai_optimizer = LocalAIOptimizer()

# Flask integration
def optimize_model_selection(query: str, context: Dict = None, 
                           available_models: List[str] = None) -> Tuple[str, float]:
    """Optimize model selection for query"""
    return local_ai_optimizer.select_optimal_model(query, context, available_models)

def update_model_performance(model_name: str, response_time: float, 
                          success: bool, tokens_processed: int = 0, 
                          error: str = None):
    """Update model performance metrics"""
    local_ai_optimizer.update_model_performance(
        model_name, response_time, success, tokens_processed, error
    )
