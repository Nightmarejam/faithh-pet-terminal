# API Integration Roadmap

## Overview

This document outlines the roadmap for integrating real AI provider APIs into the FAITHH backend, building on the solid foundation established in Phases 1-4.

## Current Status

### ✅ Completed
- Working chat endpoint with mock responses
- Stable background process management
- Comprehensive logging and monitoring
- Modular architecture foundation
- Production-ready process management

### 🔄 In Progress
- Async compatibility issues resolved
- Provider abstraction layer implemented
- Configuration management system
- Error handling framework

### ❌ Not Started
- Real API integration
- Synchronous provider wrappers
- Rate limiting and caching
- Conversation state management

## Integration Strategy

### Phase 5: Real API Integration

#### 5.1 Synchronous Provider Wrappers

**Objective**: Create sync wrappers for async provider methods

**Implementation**:
```python
# app/providers/sync_anthropic_provider.py
class SyncAnthropicProvider(BaseProvider):
    def __init__(self):
        self.async_provider = AnthropicProvider()
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Synchronous wrapper for async Anthropic provider"""
        if not self.is_available():
            return ChatResponse(
                success=False,
                error="ANTHROPIC_API_KEY not configured",
                provider="anthropic",
                timestamp=time.time()
            )
        
        try:
            # Handle async/sync boundary
            import asyncio
            import concurrent.futures
            
            if asyncio.get_event_loop().is_running():
                # Use thread executor if event loop is running
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, 
                        self.async_provider.chat(request)
                    )
                    return future.result(timeout=60)
            else:
                # Use asyncio.run if no event loop
                return asyncio.run(self.async_provider.chat(request))
                
        except Exception as e:
            return ChatResponse(
                success=False,
                error=f"Provider error: {e}",
                provider="anthropic",
                timestamp=time.time()
            )
```

**Tasks**:
- [ ] Create SyncAnthropicProvider class
- [ ] Implement async/sync boundary handling
- [ ] Add timeout and error handling
- [ ] Test with mock async provider
- [ ] Integrate with provider registry

#### 5.2 API Key Management

**Objective**: Secure API key configuration and validation

**Implementation**:
```python
# app/config/api_keys.py
class APIKeyManager:
    def __init__(self):
        self.keys = {}
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from environment and config"""
        self.keys['anthropic'] = os.environ.get('ANTHROPIC_API_KEY')
        # Add other providers as needed
    
    def validate_key(self, provider: str) -> bool:
        """Validate API key format and availability"""
        key = self.keys.get(provider)
        if not key:
            return False
        
        # Provider-specific validation
        if provider == 'anthropic':
            return key.startswith('sk-ant-api03-') and len(key) > 50
        
        return True
    
    def get_key(self, provider: str) -> str:
        """Get API key for provider"""
        return self.keys.get(provider)
```

**Tasks**:
- [ ] Implement APIKeyManager class
- [ ] Add key validation for each provider
- [ ] Create key rotation mechanism
- [ ] Add key usage monitoring
- [ ] Implement secure key storage

#### 5.3 Real API Integration

**Objective**: Replace mock responses with real API calls

**Implementation**:
```python
# faithh_backend.py (updated chat endpoint)
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        # Create chat request
        chat_request = ChatRequest(
            message=data.get('message', ''),
            provider=data.get('provider', 'anthropic'),
            model=data.get('model', 'claude-3-haiku-20240307'),
            temperature=data.get('temperature', 0.1),
            max_tokens=data.get('max_tokens', 4096)
        )
        
        # Route to provider
        provider_name = provider_service.route_request(
            provider=chat_request.provider,
            model=chat_request.model
        )
        
        # Get provider (now synchronous)
        provider = provider_registry.get_provider(provider_name)
        
        # Process chat with real API
        response = provider.chat(chat_request)
        
        if response.success:
            return jsonify({
                "success": True,
                "response": response.response,
                "model_used": response.model_used,
                "provider": response.provider,
                "usage": response.usage,
                "timestamp": response.timestamp
            })
        else:
            return jsonify({
                "success": False,
                "error": response.error,
                "provider": response.provider,
                "model_attempted": response.model_used,
                "timestamp": response.timestamp
            }), 500
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({"error": "Chat processing failed", "details": str(e)}), 500
```

**Tasks**:
- [ ] Update chat endpoint to use real providers
- [ ] Replace mock responses with API calls
- [ ] Add proper error handling
- [ ] Implement fallback to mock on API failure
- [ ] Test with real API key

### Phase 6: Production Features

#### 6.1 StateService Implementation

**Objective**: Add conversation state management

**Implementation**:
```python
# app/services/state_service.py
class StateService:
    def __init__(self):
        self.conversation_history = {}
        self.user_sessions = {}
        self.max_history = 100
    
    def add_message(self, user_id: str, message: str, response: ChatResponse):
        """Add message to conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'timestamp': time.time(),
            'message': message,
            'response': response.response,
            'provider': response.provider,
            'model': response.model_used,
            'usage': response.usage
        })
        
        # Limit history size
        if len(self.conversation_history[user_id]) > self.max_history:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history:]
    
    def get_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for user"""
        return self.conversation_history.get(user_id, [])[-limit:]
    
    def get_context(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get context for API calls"""
        history = self.get_history(user_id, limit)
        context = []
        for item in history:
            context.append({"role": "user", "content": item['message']})
            context.append({"role": "assistant", "content": item['response']})
        return context
```

**Tasks**:
- [ ] Implement StateService class
- [ ] Add conversation history storage
- [ ] Create context management for API calls
- [ ] Add user session management
- [ ] Implement history cleanup

#### 6.2 CacheService Implementation

**Objective**: Add response caching for performance

**Implementation**:
```python
# app/services/cache_service.py
class CacheService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 1000
    
    def get_cache_key(self, message: str, provider: str, model: str) -> str:
        """Generate cache key for request"""
        import hashlib
        content = f"{message}:{provider}:{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Dict]:
        """Get cached response"""
        if cache_key in self.cache:
            item = self.cache[cache_key]
            if time.time() - item['timestamp'] < self.cache_ttl:
                return item['response']
            else:
                del self.cache[cache_key]
        return None
    
    def set(self, cache_key: str, response: Dict):
        """Cache response"""
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        # Limit cache size
        if len(self.cache) > self.max_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.cache.keys(), 
                key=lambda k: self.cache[k]['timestamp']
            )[:100]
            for key in oldest_keys:
                del self.cache[key]
```

**Tasks**:
- [ ] Implement CacheService class
- [ ] Add response caching logic
- [ ] Implement cache TTL and size limits
- [ ] Add cache hit/miss metrics
- [ ] Create cache management endpoints

#### 6.3 Rate Limiting

**Objective**: Implement API rate limiting

**Implementation**:
```python
# app/services/rate_limit_service.py
class RateLimitService:
    def __init__(self):
        self.requests = {}
        self.limits = {
            'anthropic': {'requests_per_minute': 60, 'tokens_per_minute': 10000}
        }
    
    def check_rate_limit(self, user_id: str, provider: str) -> bool:
        """Check if user is rate limited"""
        now = time.time()
        minute_ago = now - 60
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id] 
            if req_time > minute_ago
        ]
        
        # Check rate limit
        limit = self.limits.get(provider, {'requests_per_minute': 60})
        return len(self.requests[user_id]) < limit['requests_per_minute']
    
    def record_request(self, user_id: str, provider: str):
        """Record API request"""
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        self.requests[user_id].append(time.time())
```

**Tasks**:
- [ ] Implement RateLimitService class
- [ ] Add per-provider rate limits
- [ ] Implement user-based rate limiting
- [ ] Add rate limit headers to responses
- [ ] Create rate limit status endpoints

## Testing Strategy

### Unit Tests

#### Provider Tests
```python
# tests/test_sync_anthropic_provider.py
def test_sync_provider_chat():
    provider = SyncAnthropicProvider()
    request = ChatRequest(message="Hello", provider="anthropic")
    
    # Test with mock
    response = provider.chat(request)
    assert response.success == True
    assert "Hello" in response.response
```

#### Service Tests
```python
# tests/test_state_service.py
def test_state_service():
    state = StateService()
    user_id = "test_user"
    
    state.add_message(user_id, "Hello", mock_response)
    history = state.get_history(user_id)
    assert len(history) == 1
    assert history[0]['message'] == "Hello"
```

### Integration Tests

#### API Tests
```python
# tests/test_chat_api.py
def test_chat_api():
    response = client.post('/api/chat', json={
        "message": "Hello",
        "provider": "anthropic"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'response' in data
```

### Load Tests

#### Performance Tests
```python
# tests/test_performance.py
def test_concurrent_requests():
    # Test 10 concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(send_chat_request, f"Message {i}")
            for i in range(10)
        ]
        
        results = [future.result() for future in futures]
        assert all(r['success'] for r in results)
```

## Deployment Considerations

### Environment Configuration

#### Development
```bash
# .env.development
ANTHROPIC_API_KEY=your-dev-key
FLASK_ENV=development
LOG_LEVEL=DEBUG
```

#### Production
```bash
# .env.production
ANTHROPIC_API_KEY=your-prod-key
FLASK_ENV=production
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
CACHE_ENABLED=true
```

### Monitoring

#### Health Checks
```bash
# Basic health
curl http://localhost:5557/health

# Detailed health
curl http://localhost:5557/api/health/check

# Provider status
curl http://localhost:5557/api/providers
```

#### Metrics
```bash
# Request metrics
curl http://localhost:5557/api/metrics

# Cache metrics
curl http://localhost:5557/api/cache/status

# Rate limit status
curl http://localhost:5557/api/rate_limit/status
```

### Security

#### API Key Security
- Use environment variables for API keys
- Implement key rotation
- Monitor key usage
- Add key validation

#### Request Security
- Implement request validation
- Add rate limiting
- Monitor for abuse
- Implement CORS policies

## Timeline

### Week 1: API Integration Foundation
- [ ] Implement SyncAnthropicProvider
- [ ] Add API key management
- [ ] Create comprehensive tests
- [ ] Update chat endpoint

### Week 2: Production Features
- [ ] Implement StateService
- [ ] Add CacheService
- [ ] Implement rate limiting
- [ ] Add monitoring endpoints

### Week 3: Testing and Optimization
- [ ] Comprehensive testing suite
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation updates

### Week 4: Production Deployment
- [ ] Environment configuration
- [ ] Deployment scripts
- [ ] Monitoring setup
- [ ] Production testing

## Success Criteria

### Phase 5 Success
- [ ] Real Anthropic API calls working
- [ ] Proper error handling and fallbacks
- [ ] API key security implemented
- [ ] Comprehensive test coverage

### Phase 6 Success
- [ ] Conversation state management working
- [ ] Response caching implemented
- [ ] Rate limiting active
- [ ] Production monitoring in place

### Overall Success
- [ ] Production-ready backend
- [ ] Comprehensive documentation
- [ ] Automated testing
- [ ] Monitoring and alerting

## Conclusion

This roadmap provides a clear path from the current mock-based system to a production-ready backend with real AI integration. The phased approach ensures:

- **Incremental Progress**: Each phase builds on the previous
- **Risk Mitigation**: Testing at each step
- **Production Readiness**: Comprehensive features and monitoring
- **Maintainability**: Clear documentation and testing

The solid foundation established in Phases 1-4 provides an excellent base for implementing these advanced features with confidence in stability and reliability.