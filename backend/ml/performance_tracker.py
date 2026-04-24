"""
FAITHH Phase 2 - Performance Tracking System
Tracks query performance metrics for machine learning optimization.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
import threading

@dataclass
class QueryPerformance:
    """Performance metrics for a single query"""
    query_id: str
    timestamp: datetime
    intent: Dict[str, Any]
    weights_used: Dict[str, float]
    chip_results: Dict[str, Any]
    response_time: float
    model_used: str
    provider_used: str
    accuracy_score: Optional[float]  # User feedback or automated assessment
    user_feedback: Optional[str]
    context_tokens: int
    coherence_score: Optional[float]
    success: bool
    error_info: Optional[str]

class PerformanceTracker:
    """Tracks and analyzes query performance for ML optimization"""
    
    def __init__(self, db_path: str = "/home/jonat/ai-stack/phase2_performance.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for performance tracking"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    weights_used TEXT NOT NULL,
                    chip_results TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    model_used TEXT NOT NULL,
                    provider_used TEXT NOT NULL,
                    accuracy_score REAL,
                    user_feedback TEXT,
                    context_tokens INTEGER,
                    coherence_score REAL,
                    success BOOLEAN NOT NULL,
                    error_info TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create aggregated metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    date TEXT PRIMARY KEY,
                    total_queries INTEGER,
                    avg_response_time REAL,
                    accuracy_score_avg REAL,
                    coherence_score_avg REAL,
                    success_rate REAL,
                    most_used_model TEXT,
                    most_used_provider TEXT,
                    top_intents TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create weight optimization table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weight_optimizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    old_weights TEXT NOT NULL,
                    new_weights TEXT NOT NULL,
                    performance_change REAL,
                    accuracy_improvement REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
    
    def track_query(self, query_performance: QueryPerformance) -> bool:
        """Track performance metrics for a query"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO query_performance 
                    (query_id, timestamp, intent, weights_used, chip_results, 
                     response_time, model_used, provider_used, accuracy_score, 
                     user_feedback, context_tokens, coherence_score, success, error_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    query_performance.query_id,
                    query_performance.timestamp.isoformat(),
                    json.dumps(query_performance.intent),
                    json.dumps(query_performance.weights_used),
                    json.dumps(query_performance.chip_results),
                    query_performance.response_time,
                    query_performance.model_used,
                    query_performance.provider_used,
                    query_performance.accuracy_score,
                    query_performance.user_feedback,
                    query_performance.context_tokens,
                    query_performance.coherence_score,
                    query_performance.success,
                    query_performance.error_info
                ))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            print(f"❌ Error tracking query performance: {e}")
            return False
    
    def get_recent_performance(self, limit: int = 100) -> List[QueryPerformance]:
        """Get recent performance data"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT query_id, timestamp, intent, weights_used, chip_results,
                           response_time, model_used, provider_used, accuracy_score,
                           user_feedback, context_tokens, coherence_score, success, error_info
                    FROM query_performance
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    results.append(QueryPerformance(
                        query_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        intent=json.loads(row[2]),
                        weights_used=json.loads(row[3]),
                        chip_results=json.loads(row[4]),
                        response_time=row[5],
                        model_used=row[6],
                        provider_used=row[7],
                        accuracy_score=row[8],
                        user_feedback=row[9],
                        context_tokens=row[10],
                        coherence_score=row[11],
                        success=row[12],
                        error_info=row[13]
                    ))
                
                conn.close()
                return results
                
        except Exception as e:
            print(f"❌ Error getting recent performance: {e}")
            return []
    
    def get_weight_optimization_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get data for weight optimization training"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                cursor.execute("""
                    SELECT timestamp, weights_used, chip_results, response_time, 
                           accuracy_score, coherence_score, success
                    FROM query_performance
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                """, (cutoff_date.isoformat(),))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'timestamp': datetime.fromisoformat(row[0]),
                        'weights_used': json.loads(row[1]),
                        'chip_results': json.loads(row[2]),
                        'response_time': row[3],
                        'accuracy_score': row[4],
                        'coherence_score': row[5],
                        'success': row[6]
                    })
                
                conn.close()
                return results
                
        except Exception as e:
            print(f"❌ Error getting optimization data: {e}")
            return []
    
    def record_weight_optimization(self, old_weights: Dict[str, float], 
                                 new_weights: Dict[str, float], 
                                 performance_change: float,
                                 accuracy_improvement: float) -> bool:
        """Record weight optimization results"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO weight_optimizations
                    (timestamp, old_weights, new_weights, performance_change, accuracy_improvement)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    json.dumps(old_weights),
                    json.dumps(new_weights),
                    performance_change,
                    accuracy_improvement
                ))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            print(f"❌ Error recording weight optimization: {e}")
            return False
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for analysis"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get basic metrics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_queries,
                        AVG(response_time) as avg_response_time,
                        AVG(accuracy_score) as avg_accuracy,
                        AVG(coherence_score) as avg_coherence,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                        model_used,
                        provider_used
                    FROM query_performance
                    WHERE timestamp >= ?
                    GROUP BY model_used, provider_used
                """, (cutoff_date.isoformat(),))
                
                model_stats = []
                for row in cursor.fetchall():
                    model_stats.append({
                        'model_used': row[4],
                        'provider_used': row[5],
                        'total_queries': row[0],
                        'avg_response_time': row[1],
                        'avg_accuracy': row[2],
                        'avg_coherence': row[3],
                        'success_rate': row[6]
                    })
                
                # Get intent distribution
                cursor.execute("""
                    SELECT intent, COUNT(*) as count
                    FROM query_performance
                    WHERE timestamp >= ?
                    GROUP BY intent
                    ORDER BY count DESC
                    LIMIT 10
                """, (cutoff_date.isoformat(),))
                
                intent_stats = []
                for row in cursor.fetchall():
                    intent_stats.append({
                        'intent': json.loads(row[0]),
                        'count': row[1]
                    })
                
                conn.close()
                
                return {
                    'period_days': days,
                    'model_stats': model_stats,
                    'intent_distribution': intent_stats,
                    'total_queries': sum(s['total_queries'] for s in model_stats)
                }
                
        except Exception as e:
            print(f"❌ Error getting performance summary: {e}")
            return {}
    
    def update_daily_metrics(self):
        """Update aggregated daily metrics"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                today = datetime.now().date().isoformat()
                
                # Calculate metrics for today
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_metrics
                    (date, total_queries, avg_response_time, accuracy_score_avg, 
                     coherence_score_avg, success_rate, most_used_model, most_used_provider, top_intents)
                    SELECT 
                        date(?),
                        COUNT(*),
                        AVG(response_time),
                        AVG(accuracy_score),
                        AVG(coherence_score),
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                        (SELECT model_used FROM query_performance 
                         WHERE DATE(timestamp) = date(?) 
                         GROUP BY model_used ORDER BY COUNT(*) DESC LIMIT 1),
                        (SELECT provider_used FROM query_performance 
                         WHERE DATE(timestamp) = date(?) 
                         GROUP BY provider_used ORDER BY COUNT(*) DESC LIMIT 1),
                        (SELECT intent FROM query_performance 
                         WHERE DATE(timestamp) = date(?) 
                         GROUP BY intent ORDER BY COUNT(*) DESC LIMIT 1)
                    FROM query_performance
                    WHERE DATE(timestamp) = date(?)
                """, (today, today, today, today))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            print(f"❌ Error updating daily metrics: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old performance data"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                cursor.execute("""
                    DELETE FROM query_performance
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_rows = cursor.rowcount
                conn.commit()
                conn.close()
                
                print(f"🗑️ Cleaned up {deleted_rows} old performance records (older than {days_to_keep} days)")
                return deleted_rows
                
        except Exception as e:
            print(f"❌ Error cleaning up old data: {e}")
            return 0

# Global instance for use across the system
performance_tracker = PerformanceTracker()
