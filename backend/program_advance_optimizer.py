"""
FAITHH Program Advance Performance Optimizer

Enhances the performance of the Program Advance chip system through:
- Intelligent caching of Program Advance results
- Optimized semantic detection
- Enhanced weighted RRF fusion
- Performance monitoring and auto-tuning
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, OrderedDict
import threading

@dataclass
class PerformanceMetrics:
    """Performance metrics for Program Advance operations"""
    operation_type: str
    execution_time: float
    chip_count: int
    result_quality: float
    cache_hit: bool
    timestamp: datetime

class ProgramAdvanceCache:
    """Intelligent caching system for Program Advance results"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.Lock()
    
    def _generate_key(self, query_text: str, chips: List[str], intent: Dict) -> str:
        """Generate cache key from query components"""
        key_data = f"{query_text.lower()}|{'|'.join(sorted(chips))}|{hash(tuple(sorted(intent.items())))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query_text: str, chips: List[str], intent: Dict) -> Optional[Dict]:
        """Get cached result if available and not expired"""
        key = self._generate_key(query_text, chips, intent)
        
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.now() - entry['timestamp'] < timedelta(seconds=self.ttl_seconds):
                    # Move to end (LRU)
                    self.cache.move_to_end(key)
                    self.hit_count += 1
                    return entry['result']
                else:
                    # Expired, remove
                    del self.cache[key]
        
        self.miss_count += 1
        return None
    
    def put(self, query_text: str, chips: List[str], intent: Dict, result: Dict):
        """Cache a result"""
        key = self._generate_key(query_text, chips, intent)
        
        with self.lock:
            # Remove oldest if at capacity
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            self.cache[key] = {
                'result': result,
                'timestamp': datetime.now()
            }
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }

class SemanticDetectionOptimizer:
    """Optimizes semantic detection for Program Advances"""
    
    def __init__(self):
        self.detection_cache: Dict[str, Tuple[str, float]] = {}
        self.performance_history: List[PerformanceMetrics] = []
        self.optimization_threshold = 0.1  # Optimize if performance drops by 10%
    
    def optimize_detection(self, query_text: str, available_advances: Dict) -> Tuple[str, float]:
        """Optimized semantic detection with caching"""
        start_time = time.time()
        
        # Check cache first
        if query_text in self.detection_cache:
            cached_advance, confidence = self.detection_cache[query_text]
            execution_time = time.time() - start_time
            
            # Record performance
            self.performance_history.append(PerformanceMetrics(
                operation_type="semantic_detection_cached",
                execution_time=execution_time,
                chip_count=0,
                result_quality=confidence,
                cache_hit=True,
                timestamp=datetime.now()
            ))
            
            return cached_advance, confidence
        
        # Perform detection (simplified for demonstration)
        best_advance = None
        best_score = 0.0
        
        for advance_name, advance_config in available_advances.items():
            # Simple keyword matching (would use actual semantic similarity in production)
            triggers = advance_config.get('triggers', [])
            semantic_queries = advance_config.get('semantic_queries', [])
            
            score = 0.0
            query_lower = query_text.lower()
            
            # Check triggers
            for trigger in triggers:
                if trigger in query_lower:
                    score += 0.5
            
            # Check semantic queries (simplified)
            for query in semantic_queries:
                words = query.lower().split()
                matching_words = sum(1 for word in words if word in query_lower)
                score += (matching_words / len(words)) * 0.3
            
            if score > best_score:
                best_score = score
                best_advance = advance_name
        
        # Cache result
        if best_advance and best_score > 0.3:  # Only cache confident detections
            self.detection_cache[query_text] = (best_advance, best_score)
        
        execution_time = time.time() - start_time
        
        # Record performance
        self.performance_history.append(PerformanceMetrics(
            operation_type="semantic_detection_computed",
            execution_time=execution_time,
            chip_count=0,
            result_quality=best_score,
            cache_hit=False,
            timestamp=datetime.now()
        ))
        
        return best_advance, best_score
    
    def get_performance_stats(self) -> Dict:
        """Get semantic detection performance statistics"""
        if not self.performance_history:
            return {}
        
        recent_metrics = [m for m in self.performance_history 
                         if datetime.now() - m.timestamp < timedelta(hours=1)]
        
        if not recent_metrics:
            return {}
        
        avg_execution_time = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
        cache_hit_rate = sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics)
        avg_quality = sum(m.result_quality for m in recent_metrics) / len(recent_metrics)
        
        return {
            'avg_execution_time': avg_execution_time,
            'cache_hit_rate': cache_hit_rate,
            'avg_quality': avg_quality,
            'cache_size': len(self.detection_cache),
            'recent_operations': len(recent_metrics)
        }

class RRFFusionOptimizer:
    """Optimizes Weighted Reciprocal Rank Fusion"""
    
    def __init__(self):
        self.fusion_cache: Dict[str, Dict] = {}
        self.weight_history: Dict[str, List[float]] = defaultdict(list)
        self.performance_metrics: List[PerformanceMetrics] = []
    
    def optimize_fusion(self, chip_contexts: Dict[str, Tuple[str, str]], intent: Dict) -> Dict:
        """Optimized RRF fusion with adaptive weights"""
        start_time = time.time()
        
        # Generate cache key
        context_keys = sorted([(chip, ctx[0][:100]) for chip, ctx in chip_contexts.items()])
        cache_key = hashlib.md5(str(context_keys).encode()).hexdigest()
        
        # Check cache
        if cache_key in self.fusion_cache:
            cached_result = self.fusion_cache[cache_key]
            execution_time = time.time() - start_time
            
            self.performance_metrics.append(PerformanceMetrics(
                operation_type="rrf_fusion_cached",
                execution_time=execution_time,
                chip_count=len(chip_contexts),
                result_quality=0.8,  # Would calculate actual quality
                cache_hit=True,
                timestamp=datetime.now()
            ))
            
            return cached_result
        
        # Perform optimized fusion
        fused_result = self._perform_adaptive_fusion(chip_contexts, intent)
        
        # Cache result
        self.fusion_cache[cache_key] = fused_result
        
        execution_time = time.time() - start_time
        
        self.performance_metrics.append(PerformanceMetrics(
            operation_type="rrf_fusion_computed",
            execution_time=execution_time,
            chip_count=len(chip_contexts),
            result_quality=0.8,  # Would calculate actual quality
            cache_hit=False,
            timestamp=datetime.now()
        ))
        
        return fused_result
    
    def _perform_adaptive_fusion(self, chip_contexts: Dict[str, Tuple[str, str]], intent: Dict) -> Dict:
        """Perform adaptive RRF fusion with optimized weights"""
        if not chip_contexts:
            return {'fused_context': '', 'sources': [], 'confidence': 0.0}
        
        # Adaptive weights based on chip performance
        weights = {}
        for chip_name in chip_contexts.keys():
            # Get historical performance for this chip
            if chip_name in self.weight_history:
                recent_weights = self.weight_history[chip_name][-10:]  # Last 10 uses
                avg_weight = sum(recent_weights) / len(recent_weights) if recent_weights else 1.0
                weights[chip_name] = avg_weight
            else:
                weights[chip_name] = 1.0
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        # Perform fusion (simplified)
        fused_parts = []
        all_sources = []
        total_confidence = 0.0
        
        for chip_name, (context, sources) in chip_contexts.items():
            weight = weights.get(chip_name, 1.0)
            if context and weight > 0.1:  # Only include significant contributions
                fused_parts.append(f"[{chip_name}] {context}")
                if sources:
                    all_sources.extend(sources)
                total_confidence += weight
        
        fused_context = '\n\n'.join(fused_parts) if fused_parts else ''
        avg_confidence = total_confidence / len(chip_contexts) if chip_contexts else 0.0
        
        return {
            'fused_context': fused_context,
            'sources': all_sources,
            'confidence': min(avg_confidence, 1.0),
            'weights_used': weights
        }
    
    def update_chip_weight(self, chip_name: str, performance_score: float):
        """Update weight history for a chip"""
        self.weight_history[chip_name].append(performance_score)
        
        # Keep only recent history
        if len(self.weight_history[chip_name]) > 100:
            self.weight_history[chip_name] = self.weight_history[chip_name][-50:]

class ProgramAdvanceOptimizer:
    """Main optimizer for Program Advance system"""
    
    def __init__(self):
        self.cache = ProgramAdvanceCache(max_size=500, ttl_seconds=1800)  # 30 minutes
        self.semantic_optimizer = SemanticDetectionOptimizer()
        self.rrf_optimizer = RRFFusionOptimizer()
        self.optimization_stats = defaultdict(list)
        self.last_optimization = datetime.now()
    
    def optimize_program_advance(self, query_text: str, chip_contexts: Dict[str, Tuple[str, str]], 
                               intent: Dict, available_advances: Dict) -> Dict:
        """Complete Program Advance optimization pipeline"""
        start_time = time.time()
        
        # Check cache first
        cached_result = self.cache.get(query_text, list(chip_contexts.keys()), intent)
        if cached_result:
            return cached_result
        
        # Optimize semantic detection
        advance_name, confidence = self.semantic_optimizer.optimize_detection(query_text, available_advances)
        
        # Optimize RRF fusion
        fused_result = self.rrf_optimizer.optimize_fusion(chip_contexts, intent)
        
        # Combine results
        optimized_result = {
            'advance_detected': advance_name,
            'advance_confidence': confidence,
            'fused_context': fused_result.get('fused_context', ''),
            'sources': fused_result.get('sources', []),
            'confidence': fused_result.get('confidence', 0.0),
            'weights_used': fused_result.get('weights_used', {}),
            'optimization_applied': True,
            'execution_time': time.time() - start_time
        }
        
        # Cache result
        self.cache.put(query_text, list(chip_contexts.keys()), intent, optimized_result)
        
        # Record optimization stats
        self.optimization_stats['total_optimizations'].append(time.time())
        self.optimization_stats['execution_times'].append(optimized_result['execution_time'])
        
        return optimized_result
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive optimization statistics"""
        return {
            'cache_stats': self.cache.get_stats(),
            'semantic_stats': self.semantic_optimizer.get_performance_stats(),
            'rrf_stats': {
                'cache_size': len(self.rrf_optimizer.fusion_cache),
                'weight_history_size': {k: len(v) for k, v in self.rrf_optimizer.weight_history.items()},
                'total_operations': len(self.rrf_optimizer.performance_metrics)
            },
            'overall_stats': {
                'total_optimizations': len(self.optimization_stats['total_optimizations']),
                'avg_execution_time': sum(self.optimization_stats['execution_times']) / len(self.optimization_stats['execution_times']) if self.optimization_stats['execution_times'] else 0,
                'last_optimization': self.last_optimization.isoformat()
            }
        }
    
    def auto_tune(self):
        """Automatically tune optimization parameters"""
        current_time = datetime.now()
        
        # Only auto-tune if enough data available
        if len(self.optimization_stats['execution_times']) < 10:
            return
        
        avg_execution_time = sum(self.optimization_stats['execution_times']) / len(self.optimization_stats['execution_times'])
        
        # Tune cache size if hit rate is low
        cache_stats = self.cache.get_stats()
        if cache_stats['hit_rate'] < 0.3 and cache_stats['size'] < 2000:
            self.cache.max_size = min(2000, self.cache.max_size * 2)
            print(f"🔧 Auto-tuned cache size to {self.cache.max_size}")
        
        # Tune TTL if cache is too small
        if cache_stats['size'] < self.cache.max_size * 0.5:
            self.cache.ttl_seconds = min(7200, self.cache.ttl_seconds * 2)  # Max 2 hours
            print(f"🔧 Auto-tuned cache TTL to {self.cache.ttl_seconds} seconds")
        
        self.last_optimization = current_time

# Global optimizer instance
program_advance_optimizer = ProgramAdvanceOptimizer()
