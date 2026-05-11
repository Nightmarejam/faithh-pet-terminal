# API Integration Hardening Plan
**Date:** 2026-02-18 (plan) · **Reality snapshot:** 2026-04-12  
**Purpose:** Ensure UI-Backend synchronization and robust integration

**Authoritative layout (April 2026):** See `AGENTS.md` — canonical backend is `faithh_professional_backend_fixed.py` on port **5557**. Default chat model is **`config.yaml`** `ai.default_model` (currently `qwen25-faithh-v3:latest`); `.env` `DEFAULT_MODEL` is fallback only when YAML does not pin the model.

## Current API Endpoints

### Core Endpoints
| Endpoint | Method | Purpose | UI Usage | Status |
|----------|--------|---------|----------|---------|
| `/health` | GET | Liveness (`restart_backend.sh`) | ✅ Ops | Stable |
| `/api/workspace/registry` | GET | Service registry + RAG hints for Canvas | ✅ UI boot | Stable |
| `/api/chat` | POST | Main chat (optional SSE); may include `rag_results`, `rag_relevance`, `best_distance` | ✅ Active | Stable |
| `/api/models` | GET | List available models | ✅ Active | Stable |
| `/api/status` | GET | System health check | ✅ Active | Stable |
| `/api/upload` | POST | File uploads | ✅ Active | Stable |

### ML & AI Endpoints
| Endpoint | Method | Purpose | UI Usage | Status |
|----------|--------|---------|----------|---------|
| `/api/ml/chips` | GET | Get ML chips | ✅ Active | Stable |
| `/api/ml/chips/activate` | POST | Activate chip | ✅ Active | Stable |
| `/api/rag_search` | POST | RAG search | ❌ Not used | Available |

### PULSE Endpoints
| Endpoint | Method | Purpose | UI Usage | Status |
|----------|--------|---------|----------|---------|
| `/api/pulse/security/scan` | POST | Security scan | ✅ Active | Stable |
| `/api/pulse/health/check` | GET | Health check | ✅ Active | Stable |
| `/api/pulse/health/heal` | POST | Heal system | ✅ Active | Stable |
| `/api/pulse/audit/summary` | GET | Audit summary | ✅ Active | Stable |
| `/api/pulse/audit/recent` | GET | Recent audits | ✅ Active | Stable |
| `/api/pulse/chips` | GET | Pulse chips | ✅ Active | Stable |
| `/api/pulse/state` | GET | Pulse state | ✅ Active | Stable |

### Context Endpoints
| Endpoint | Method | Purpose | UI Usage | Status |
|----------|--------|---------|----------|---------|
| `/api/context/collectors` | GET | List collectors | ✅ Active | Stable |
| `/api/context/collectors/status` | GET | Collector status | ✅ Active | Stable |
| `/api/context/collectors/run` | POST | Run collectors | ✅ Active | Stable |

### Compass Endpoints
| Endpoint | Method | Purpose | UI Usage | Status |
|----------|--------|---------|----------|---------|
| `/api/compass` | GET | Compass data | ✅ Active | Stable |
| `/api/compass/director` | GET | Director view | ✅ Active | Stable |
| `/api/compass/log` | POST | Log event | ✅ Active | Stable |

## Integration Hardening Strategy

### 1. API Contract Management

#### Create API Schema Registry
```javascript
// File: api/schema_registry.js
const API_SCHEMAS = {
    '/api/chat': {
        request: {
            query: "string",
            model: "string (optional)",
            provider: "string (optional)",
            use_rag: "boolean (optional)",
            session_id: "string (optional)"
        },
        response: {
            success: "boolean",
            response: "string",
            model_used: "string",
            provider: "string",
            response_time: "number",
            rag_used: "boolean",
            rag_results: "array<string>",
            intent_detected: "object",
            session_id: "string",
            conversation_depth: "number",
            ml_chips_activated: "array",
            integrations_used: "array"
        }
    },
    // ... other endpoints
};
```

#### Version API Endpoints
```python
# Add to backend
API_VERSION = "v1"

@app.route(f'/api/{API_VERSION}/chat', methods=['POST'])
def chat_v1():
    # Current implementation
    pass

# Future: /api/v2/chat with breaking changes
```

### 2. Response Validation

#### Frontend Validation Layer
```javascript
// File: api/response_validator.js
class ResponseValidator {
    static validate(endpoint, data) {
        const schema = API_SCHEMAS[endpoint];
        if (!schema) return { valid: true };
        
        const errors = [];
        
        // Required fields check
        Object.entries(schema.response).forEach(([field, type]) => {
            if (!(field in data)) {
                errors.push(`Missing required field: ${field}`);
            }
        });
        
        return {
            valid: errors.length === 0,
            errors
        };
    }
}
```

#### Backend Response Standardization
```python
# Add to backend
def standard_response(success=True, data=None, error=None, metadata=None):
    """Standardize all API responses"""
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
        'api_version': API_VERSION
    }
    
    if success and data:
        response.update(data)
    elif not success and error:
        response['error'] = error
        
    if metadata:
        response['metadata'] = metadata
        
    return jsonify(response)
```

### 3. Error Handling & Resilience

#### Frontend Error Handler
```javascript
// File: api/error_handler.js
class APIErrorHandler {
    static async handle(response, endpoint) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            
            switch (response.status) {
                case 500:
                    console.error('Backend error:', error);
                    return {
                        success: false,
                        error: 'Backend temporarily unavailable',
                        retry_after: 5000
                    };
                case 502:
                case 503:
                case 504:
                    return {
                        success: false,
                        error: 'Service unavailable',
                        retry_after: 10000
                    };
                default:
                    return {
                        success: false,
                        error: error.error || 'Unknown error',
                        retry_after: 2000
                    };
            }
        }
        
        const data = await response.json();
        const validation = ResponseValidator.validate(endpoint, data);
        
        if (!validation.valid) {
            console.error('Response validation failed:', validation.errors);
            return {
                success: false,
                error: 'Invalid response format',
                details: validation.errors
            };
        }
        
        return data;
    }
}
```

#### Automatic Retry Logic
```javascript
// File: api/retry_handler.js
class RetryHandler {
    static async fetchWithRetry(url, options, maxRetries = 3) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                const response = await fetch(url, options);
                const result = await APIErrorHandler.handle(response, url);
                
                if (result.success || !result.retry_after) {
                    return result;
                }
                
                if (i < maxRetries - 1) {
                    await new Promise(resolve => setTimeout(resolve, result.retry_after));
                }
            } catch (error) {
                if (i === maxRetries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)));
            }
        }
    }
}
```

### 4. Connection Health Monitoring

#### Backend Health Check Enhancement
```python
@app.route('/api/health/detailed', methods=['GET'])
def detailed_health():
    """Comprehensive health check for UI monitoring"""
    health = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'ollama': check_ollama_health(),
            'chroma': check_chroma_health(),
            'ml_chips': check_ml_chips_health()
        },
        'performance': {
            'avg_response_time': get_avg_response_time(),
            'active_sessions': len(conversation_sessions),
            'memory_usage': psutil.virtual_memory().percent
        },
        'endpoints': {
            'chat': 'operational',
            'models': 'operational',
            'status': 'operational'
        }
    }
    
    return jsonify(health)
```

#### Frontend Health Monitor
```javascript
// File: ui/health_monitor.js
class HealthMonitor {
    constructor() {
        this.status = 'unknown';
        this.lastCheck = null;
        this.checkInterval = 30000; // 30 seconds
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/api/health/detailed');
            const health = await response.json();
            
            this.status = health.status;
            this.lastCheck = new Date();
            
            // Update UI indicators
            this.updateStatusIndicators(health);
            
            // Log issues
            if (health.status !== 'healthy') {
                console.warn('Health check warning:', health);
            }
            
            return health;
        } catch (error) {
            this.status = 'error';
            console.error('Health check failed:', error);
            return null;
        }
    }
    
    startMonitoring() {
        this.checkHealth();
        setInterval(() => this.checkHealth(), this.checkInterval);
    }
}
```

### 5. API Version Compatibility

#### Backend Version Header
```python
@app.before_request
def add_api_version():
    """Add API version to all responses"""
    if request.path.startswith('/api/'):
        g.api_version = request.headers.get('API-Version', 'v1')
```

#### Frontend Version Negotiation
```javascript
// File: api/version_manager.js
class VersionManager {
    static async getVersion() {
        try {
            const response = await fetch('/api/version');
            return await response.json();
        } catch {
            return { version: 'v1', compatible: true };
        }
    }
    
    static isCompatible(backendVersion, frontendVersion) {
        // Simple semver compatibility check
        const backend = backendVersion.split('.');
        const frontend = frontendVersion.split('.');
        
        return backend[0] === frontend[0]; // Major version must match
    }
}
```

### 6. PULSE Integration for API Sync

#### API Change Detector
```python
# Add to PULSE
def detect_api_changes():
    """Detect when API endpoints change"""
    current_endpoints = get_all_endpoints()
    cached_endpoints = load_cached_endpoints()
    
    changes = {
        'added': set(current_endpoints) - set(cached_endpoints),
        'removed': set(cached_endpoints) - set(current_endpoints),
        'modified': detect_modified_endpoints(current_endpoints, cached_endpoints)
    }
    
    if any(changes.values()):
        notify_ui_developers(changes)
        save_cached_endpoints(current_endpoints)
    
    return changes
```

#### UI Auto-Update Notification
```javascript
// File: ui/api_change_notifier.js
class APIChangeNotifier {
    static async checkForChanges() {
        const lastCheck = localStorage.getItem('api_last_check');
        const response = await fetch('/api/changes/since', {
            headers: { 'If-Modified-Since': lastCheck }
        });
        
        if (response.status === 200) {
            const changes = await response.json();
            this.notifyUser(changes);
            localStorage.setItem('api_last_check', new Date().toUTCString());
        }
    }
    
    static notifyUser(changes) {
        if (changes.added.length > 0 || changes.removed.length > 0) {
            const notification = `
                API has changed:
                Added: ${changes.added.join(', ')}
                Removed: ${changes.removed.join(', ')}
                Please refresh the page.
            `;
            alert(notification);
        }
    }
}
```

## Implementation Priority

### Phase 4 Week 1: Critical
1. ✅ RAG Sources Display (DONE)
2. **Response Validation** - Prevent UI crashes from malformed responses
3. **Error Handling** - Graceful degradation for backend issues
4. **Health Monitoring** - Real-time connection status

### Phase 4 Week 2: Reliability
1. **Retry Logic** - Automatic recovery from temporary failures
2. **API Versioning** - Prepare for future changes
3. **Connection Pooling** - Optimize multiple requests

### Phase 4 Week 3: Automation
1. **PULSE Integration** - Automatic change detection
2. **Schema Registry** - Contract enforcement
3. **Compatibility Matrix** - Version tracking

## Testing Strategy

### API Contract Tests
```javascript
// File: tests/api_contract_tests.js
describe('API Contract Tests', () => {
    test('/api/chat returns expected schema', async () => {
        const response = await API.chat({ query: 'test' });
        expect(response).toHaveProperty('success');
        expect(response).toHaveProperty('response');
        expect(response).toHaveProperty('model_used');
        // ... other required fields
    });
});
```

### Integration Tests
```javascript
// File: tests/integration_tests.js
describe('UI-Backend Integration', () => {
    test('Handles backend gracefully when offline', async () => {
        // Mock backend failure
        // Verify UI shows appropriate message
    });
    
    test('Recovers from temporary backend restart', async () => {
        // Simulate backend restart
        // Verify automatic reconnection
    });
});
```

## Next Steps

1. **Immediate**: Implement response validation and error handling
2. **This Week**: Add health monitoring and retry logic
3. **Next Week**: Begin PULSE integration for API sync
4. **Ongoing**: Maintain API contract tests and documentation

This plan ensures the UI-backend connection remains robust and self-healing, with PULSE providing automated monitoring and change detection.
