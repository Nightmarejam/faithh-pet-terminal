# FAITHH API Reference

**Version**: Phase 5.2 Complete  
**Base URL**: `http://localhost:5557`  
**Total Endpoints**: 8 new + existing endpoints  

---

## 🎯 **Overview**

FAITHH Phase 5.2 introduces 8 new API endpoints for advanced analytics and AI-driven user experience, building on the existing foundation. This reference documents all endpoints with request/response examples and usage patterns.

---

## 📊 **Advanced Analytics Endpoints**

### `/api/analytics/comprehensive`
**Method**: `GET`  
**Description**: Get comprehensive analytics with predictions and insights

#### Response Example
```json
{
  "success": true,
  "analytics": {
    "analysis_timestamp": "2026-03-26T20:04:28.701474",
    "predictions": {
      "query_processing_time": {
        "metric_type": "query_processing_time",
        "predicted_value": 1.23,
        "horizon_seconds": 3600,
        "confidence": 0.85,
        "trend": "stable"
      }
    },
    "anomalies": [
      {
        "timestamp": "2026-03-26T20:01:15.123456",
        "metric_type": "response_time",
        "severity": "medium",
        "description": "Anomalous response_time: 2.45 (baseline: 0.85 ± 0.15)",
        "confidence": 0.75
      }
    ],
    "insights": [
      {
        "type": "performance_trend",
        "category": "optimization",
        "priority": "medium",
        "title": "response_time trending upward",
        "description": "response_time is predicted to increase by 1.23 in the next hour",
        "recommendation": "Monitor system capacity and consider scaling if trend continues",
        "confidence": 0.85
      }
    ],
    "metrics_summary": {
      "query_processing_time": {
        "count": 1250,
        "latest_value": 0.95,
        "latest_timestamp": "2026-03-26T20:04:25.000000"
      }
    }
  }
}
```

#### Usage
```bash
curl -s http://localhost:5557/api/analytics/comprehensive | python3 -m json.tool
```

---

### `/api/analytics/stats`
**Method**: `GET`  
**Description**: Get advanced analytics system statistics

#### Response Example
```json
{
  "success": true,
  "analytics_stats": {
    "predictive_analytics": {
      "metrics_tracked": 12,
      "prediction_models": 8,
      "total_predictions": 2847
    },
    "anomaly_detection": {
      "baselines_established": 10,
      "recent_anomalies": 2,
      "total_anomalies": 15
    },
    "insights_generation": {
      "total_insights": 45,
      "patterns_identified": 8,
      "last_analysis": "2026-03-26T20:04:28.701474"
    },
    "system_metrics": {
      "metrics_buffered": 12,
      "total_data_points": 5234,
      "analysis_interval_minutes": 5.0
    }
  }
}
```

#### Usage
```bash
curl -s http://localhost:5557/api/analytics/stats | python3 -m json.tool
```

---

### `/api/analytics/metrics`
**Method**: `POST`  
**Description**: Add a new metric for analytics tracking

#### Request Body
```json
{
  "metric_type": "system_cpu",
  "value": 45.2,
  "context": {
    "server": "main",
    "processes": 12,
    "zone": "production"
  }
}
```

#### Response Example
```json
{
  "success": true,
  "message": "Metric system_cpu added successfully"
}
```

#### Usage
```bash
curl -s -X POST http://localhost:5557/api/analytics/metrics \
  -H "Content-Type: application/json" \
  -d '{"metric_type": "system_cpu", "value": 45.2, "context": {"server": "main"}}'
```

---

## 🤖 **AI-Driven UX Endpoints**

### `/api/ux/personalized`
**Method**: `GET`  
**Description**: Get personalized user experience recommendations

#### Query Parameters
- `user_id` (optional): User identifier (default: "default_user")

#### Response Example
```json
{
  "success": true,
  "user_id": "user_123",
  "personalized_experience": {
    "personalization_level": "high",
    "patterns_detected": 5,
    "patterns": [
      {
        "type": "complex_queries",
        "confidence": 0.85,
        "description": "User prefers detailed, complex queries",
        "recommendations": [
          "Provide comprehensive responses",
          "Include detailed explanations",
          "Offer follow-up suggestions"
        ]
      }
    ],
    "interface_adaptations": {
      "layout_changes": ["expand_response_area"],
      "feature_priorities": ["enhance_search"],
      "response_style": "comprehensive",
      "recommendations": ["Provide comprehensive responses"]
    },
    "response_optimizations": {
      "length_adjustment": 0.3,
      "style_adjustment": "detailed",
      "content_priorities": ["comprehensive", "examples"],
      "formatting_suggestions": ["structured", "sections"]
    },
    "global_insights": [
      {
        "type": "time_preference",
        "description": "User typically active during 14, 15, 16 hours",
        "frequency": 45
      }
    ]
  }
}
```

#### Usage
```bash
curl -s "http://localhost:5557/api/ux/personalized?user_id=user_123" | python3 -m json.tool
```

---

### `/api/ux/optimize-response`
**Method**: `POST`  
**Description**: Optimize response for specific user

#### Request Body
```json
{
  "user_id": "user_123",
  "query_text": "What is the cultural transmission mechanism in ALIFE?",
  "base_response": "Cultural transmission in ALIFE involves agents sharing protocols through direct interactions. The mechanism includes protocol creation, transmission fidelity, and multi-generational persistence."
}
```

#### Response Example
```json
{
  "success": true,
  "user_id": "user_123",
  "optimized_response": {
    "optimizations": {
      "length_adjustment": 0.3,
      "style_adjustment": "detailed",
      "content_priorities": ["comprehensive", "examples"],
      "formatting_suggestions": ["structured", "sections"],
      "target_length": 280
    },
    "personalized_response": "Cultural transmission in ALIFE involves agents sharing protocols through direct interactions.\n\nThe mechanism includes:\n• Protocol creation by innovator agents\n• Transmission fidelity based on social roles\n• Multi-generational persistence through cultural centers\n\nThis process enables the emergence of complex cultural systems with specialized roles and knowledge accumulation.",
    "confidence": 0.82
  }
}
```

#### Usage
```bash
curl -s -X POST http://localhost:5557/api/ux/optimize-response \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "query_text": "What is cultural transmission?", "base_response": "Cultural transmission involves sharing protocols."}'
```

---

### `/api/ux/track-interaction`
**Method**: `POST`  
**Description**: Track user interaction for AI-driven UX analysis

#### Request Body
```json
{
  "user_id": "user_123",
  "session_id": "session_456",
  "interaction_type": "query",
  "interaction_data": {
    "query_length": 45,
    "intent_type": "research",
    "chips_used": ["rag_search", "decisions"],
    "response_time": 1.2
  },
  "response_time": 1.2,
  "success": true
}
```

#### Response Example
```json
{
  "success": true,
  "message": "Interaction tracked successfully"
}
```

#### Usage
```bash
curl -s -X POST http://localhost:5557/api/ux/track-interaction \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "session_id": "session_456", "interaction_type": "query", "interaction_data": {"query_length": 45}, "response_time": 1.2, "success": true}'
```

---

### `/api/ux/analytics`
**Method**: `GET`  
**Description**: Get comprehensive UX analytics

#### Response Example
```json
{
  "success": true,
  "ux_analytics": {
    "behavior_analyzer": {
      "total_users": 25,
      "total_interactions": 1847,
      "global_patterns": 12,
      "avg_patterns_per_user": 3.2
    },
    "adaptive_interface": {
      "personalized_users": 18,
      "total_adaptations": 234,
      "most_common_adaptations": ["expand_response_area", "optimize_for_speed"]
    },
    "response_optimizer": {
      "optimized_users": 15,
      "total_optimizations": 156,
      "avg_optimization_confidence": 0.78
    },
    "session_analytics": {
      "active_sessions": 8,
      "avg_session_duration": 1245.6,
      "avg_success_rate": 0.94
    }
  }
}
```

#### Usage
```bash
curl -s http://localhost:5557/api/ux/analytics | python3 -m json.tool
```

---

## ⚡ **Performance Optimization Endpoints**

### `/api/program-advance/optimization`
**Method**: `GET`  
**Description**: Get Program Advance performance optimization statistics

#### Response Example
```json
{
  "success": true,
  "optimization_stats": {
    "cache_stats": {
      "cache_size": 234,
      "cache_hits": 1847,
      "cache_misses": 123,
      "hit_rate": 0.94,
      "memory_usage": 45.6
    },
    "semantic_detection": {
      "total_detections": 892,
      "cached_detections": 784,
      "detection_accuracy": 0.87,
      "avg_confidence": 0.82
    },
    "rrf_fusion": {
      "total_fusions": 567,
      "optimized_fusions": 523,
      "fusion_efficiency": 0.92,
      "avg_weight_score": 0.78
    },
    "auto_tuning": {
      "tuning_cycles": 45,
      "performance_improvements": 38,
      "avg_improvement_percent": 12.5
    },
    "overall_performance": {
      "total_queries": 1847,
      "avg_response_time": 0.95,
      "optimization_impact": 0.23
    }
  }
}
```

#### Usage
```bash
curl -s http://localhost:5557/api/program-advance/optimization | python3 -m json.tool
```

---

## 🔧 **Existing Core Endpoints**

### `/api/chat`
**Method**: `POST`  
**Description**: Main chat endpoint with Program Advance integration

### `/api/search`
**Method**: `POST`  
**Description**: RAG search across knowledge base

### `/api/models`
**Method**: `GET`  
**Description**: Get available LLM models

### `/api/status`
**Method**: `GET`  
**Description**: System health and status

### `/health`
**Method**: `GET`  
**Description**: Basic health check

---

## 📊 **Usage Patterns**

### **Analytics Integration**
```python
# Track custom metrics
import requests

def track_custom_metric(metric_type, value, context=None):
    response = requests.post('http://localhost:5557/api/analytics/metrics', 
                           json={
                               'metric_type': metric_type,
                               'value': value,
                               'context': context or {}
                           })
    return response.json()

# Get comprehensive analytics
def get_analytics():
    response = requests.get('http://localhost:5557/api/analytics/comprehensive')
    return response.json()
```

### **UX Personalization**
```python
# Get personalized experience
def get_personalization(user_id):
    response = requests.get(f'http://localhost:5557/api/ux/personalized?user_id={user_id}')
    return response.json()

# Optimize response for user
def optimize_response(user_id, query, response):
    result = requests.post('http://localhost:5557/api/ux/optimize-response',
                          json={
                              'user_id': user_id,
                              'query_text': query,
                              'base_response': response
                          })
    return result.json()
```

### **Performance Monitoring**
```python
# Get optimization stats
def get_performance_stats():
    response = requests.get('http://localhost:5557/api/program-advance/optimization')
    return response.json()

# Track user interaction
def track_interaction(user_id, session_id, interaction_type, data, response_time, success):
    response = requests.post('http://localhost:5557/api/ux/track-interaction',
                           json={
                               'user_id': user_id,
                               'session_id': session_id,
                               'interaction_type': interaction_type,
                               'interaction_data': data,
                               'response_time': response_time,
                               'success': success
                           })
    return response.json()
```

---

## 🚨 **Error Handling**

### **Common Error Responses**
```json
{
  "success": false,
  "error": "Invalid request parameters"
}
```

### **HTTP Status Codes**
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `500`: Internal Server Error

### **Error Types**
- **Validation Error**: Missing or invalid parameters
- **System Error**: Internal processing issues
- **Analytics Error**: Analytics system unavailable
- **UX Error**: UX system unavailable

---

## 🔄 **Integration Examples**

### **Full Analytics + UX Flow**
```python
import requests
import time

def analyze_user_session(user_id, session_id, interactions):
    """Complete user session analysis"""
    
    # Track each interaction
    for interaction in interactions:
        track_interaction(user_id, session_id, **interaction)
        time.sleep(0.1)  # Avoid overwhelming the system
    
    # Get personalized insights
    personalization = get_personalization(user_id)
    
    # Get analytics overview
    analytics = get_analytics()
    
    # Get performance stats
    performance = get_performance_stats()
    
    return {
        'personalization': personalization,
        'analytics': analytics,
        'performance': performance
    }
```

### **Real-time Monitoring**
```python
def monitor_system_health():
    """Real-time system health monitoring"""
    
    # Check basic health
    health = requests.get('http://localhost:5557/health').json()
    
    # Get detailed analytics
    analytics = get_analytics()
    
    # Check performance
    performance = get_performance_stats()
    
    # Get UX analytics
    ux_analytics = requests.get('http://localhost:5557/api/ux/analytics').json()
    
    return {
        'health': health,
        'analytics': analytics,
        'performance': performance,
        'ux': ux_analytics
    }
```

---

## 📈 **Performance Considerations**

### **Rate Limiting**
- Analytics endpoints: No rate limiting (internal use)
- UX endpoints: Standard rate limiting applies
- Optimization endpoints: Cached responses (5-minute TTL)

### **Caching**
- Analytics results: Cached for 5 minutes
- UX personalization: Cached per user for 1 hour
- Performance stats: Real-time (no caching)

### **Best Practices**
1. **Batch Analytics**: Track multiple metrics in single requests
2. **User Sessions**: Use consistent session IDs for tracking
3. **Error Handling**: Always check `success` field in responses
4. **Performance**: Use cached endpoints where available

---

## 🎯 **Future Enhancements**

### **Planned Additions**
- **WebSocket Support**: Real-time analytics streaming
- **Advanced ML Models**: Enhanced predictive analytics
- **Multi-User Analytics**: Cross-user pattern analysis
- **Custom Dashboards**: User-configurable analytics views

### **API Versioning**
- Current version: v1 (Phase 5.2)
- Backward compatibility maintained
- Version-specific documentation available

---

*API Reference - Phase 5.2 Complete | 8 New Endpoints | March 2026*  
*Base URL: http://localhost:5557 | Status: Production Ready*  
*Features: Advanced Analytics + AI-Driven UX + Performance Optimization*
