# Technical Documentation

Architecture, APIs, and implementation details

---

## 🏗️ System Architecture

### Backend Architecture
The FAITHH backend uses a modular Flask architecture with service-oriented design.

#### Core Components

#### Backend Modules
- **__init__**: Backend module
- **advanced_analytics**: Backend module
- **advanced_analytics_simple**: Predictive analytics with AI-powered insights
- **ai_driven_ux**: Intelligent user experience with personalization and behavior analysis
- **anchor_validator**: Backend module
- **cache**: Intelligent caching with LRU eviction, performance optimization
- **coherence_arbiter**: Measures RAG/chip alignment quality
- **coherence_sensor**: Backend module
- **connection_monitor**: Health checks for 5 services, graceful fallbacks
- **context_builders**: Assembles context from memory/decisions/projects
- **data_loaders**: Backend module
- **enhanced_chip_integration**: Parallel chip retrieval with Program Advance system
- **faithh_backend_adapter**: Backend module
- **faithh_backend_v4_template**: Backend module
- **faithh_enhanced_backend**: Backend module
- **faithh_unified_api**: Backend module
- **integrate_program_advances**: Backend module
- **intent_detection**: Classifies query type for routing
- **llm_providers**: Backend module
- **local_optimization**: Query analysis, model selection, performance profiling
- **ml_learning_framework**: Backend module
- **parallel_chip_engine**: Backend module
- **performance**: Real-time metrics, system monitoring, analytics
- **performance_monitor**: Backend module
- **plc_state_manager**: Backend module
- **program_advance_optimizer**: Optimizes Program Advance chip selection and performance
- **rag_api**: Backend module
- **rag_processor**: Backend module
- **response_cache**: Backend module
- **security_manager**: Backend module
- **security_middleware**: Rate limiting, input validation, request protection
- **tiered_rag_processor**: Backend module
- **tool_executor**: Backend module
- **tool_registry**: Backend module
- **tool_system**: Backend module
- **ui_layout_optimizer**: Backend module

#### Service Layer
- **alife_parasitic_integration**: Integration of parasitic feeding with ALife data
- **alife_parasitic_integration_final**: Service module
- **alife_parasitic_integration_fixed**: Service module
- **alife_service**: Service module
- **chat_service**: Service module
- **cosmic_ripple_integration**: Cosmic ripple effects on impedance patterns
- **genomic_biasing_engine**: DNA copying bias based on impedance patterns
- **genomic_impedance_sensor**: Environmental impedance detection for organisms
- **health_service**: Service module
- **parasitic_alife_service**: Service module
- **parasitic_alife_service_fixed**: Parasitic impedance feeding in ALife experiments
- **provider_service**: Service module
- **standing_wave_moon_service**: Service module
- **standing_wave_service**: Service module
- **universal_impedance_field**: Service module
- **universal_impedance_field_optimized**: Universal impedance field calculations and optimization


## 🔌 API Endpoints

### Core Endpoints
- ('/')
- ('/cockpit')
- ('/faithh_live_state.json')
- ('/images/<path:filename>')
- ('/favicon.ico')
- ('/manifest.json')
- ('/sw.js')
- ('/icons/<path:filename>')
- ('/api/models', methods=['GET'])
- ('/api/chat', methods=['POST'])
- ('/api/search', methods=['POST'])
- ('/api/search/status', methods=['GET'])
- ('/api/upload', methods=['POST'])
- ('/api/rag_search', methods=['POST'])
- ('/api/genomic/impedance-sensor', methods=['POST'])
- ('/api/genomic/biasing-analysis', methods=['POST'])
- ('/api/genomic/sensor-readings/<organism_id>')
- ('/api/genomic/analyze-sensors')
- ('/api/genomic/biasing-patterns')
- ('/api/compass/director', methods=['GET'])
- ('/api/pulse/security/scan', methods=['POST'])
- ('/api/pulse/health/check', methods=['GET'])
- ('/api/pulse/health/heal', methods=['POST'])
- ('/api/pulse/audit/summary', methods=['GET'])
- ('/api/pulse/audit/recent', methods=['GET'])
- ('/api/status', methods=['GET'])
- ('/api/context/collectors', methods=['GET'])
- ('/collectors/status', methods=['GET'])
- ('/api/context/collectors/run', methods=['POST'])
- ('/api/context/collectors/status', methods=['GET'])
- ('/api/test_integrations', methods=['GET'])
- ('/api/ml-learning', methods=['GET'])
- ('/api/ui-layout', methods=['GET'])
- ('/api/ui-layout', methods=['POST'])
- ('/api/cache', methods=['GET'])
- ('/api/performance', methods=['GET'])
- ('/api/program-advance/stats', methods=['GET'])
- ('/api/program-advance/optimization', methods=['GET'])
- ('/api/analytics/comprehensive', methods=['GET'])
- ('/api/analytics/stats', methods=['GET'])
- ('/api/analytics/metrics', methods=['POST'])
- ('/api/ux/personalized', methods=['GET'])
- ('/api/ux/optimize-response', methods=['POST'])
- ('/api/ux/track-interaction', methods=['POST'])
- ('/api/ux/analytics', methods=['GET'])
- ('/api/health')
- ('/health')
- ('/api/pulse/status', methods=['GET'])
- ('/api/pulse/proposals', methods=['GET'])
- ('/api/pulse/approve', methods=['POST'])
- ('/api/pulse/reject', methods=['POST'])
- ('/api/pulse/chips', methods=['GET'])
- ('/api/ml/chips', methods=['GET'])
- ('/api/ml/chips/activate', methods=['POST'])
- ('/api/ml/chips/resync', methods=['POST'])
- ('/api/ml/chips/reload', methods=['POST'])
- ('/api/pulse/reflection/status', methods=['GET'])
- ('/api/pulse/reflection/staleness', methods=['GET'])
- ('/api/pulse/reflection/divergence', methods=['GET'])
- ('/api/pulse/reflection/branches', methods=['GET'])
- ('/api/pulse/reflection/run', methods=['POST'])
- ('/api/pulse/state', methods=['GET'])
- ('/api/pulse/state/refresh', methods=['POST'])
- ('/api/journal', methods=['GET'])
- ('/api/journal/generate', methods=['POST'])
- ('/api/avatar', methods=['GET'])
- ('/api/avatar/generate', methods=['POST'])
- ('/api/filesystem', methods=['POST'])
- ('/api/filesystem/capabilities', methods=['GET'])
- ('/api/compass', methods=['GET'])
- ('/api/compass/log', methods=['POST'])
- ('/api/metrics', methods=['GET'])
- ('/api/compass/status', methods=['GET'])
- ('/api/compare', methods=['POST'])
- ('/api/journal/view/<date>', methods=['GET'])
- ('/api/compass/refresh', methods=['POST'])

## 🔧 Configuration

### Environment Variables
Configuration managed in `config.yaml` with the following sections:
- security:
- # Allowed directories for file operations
- allowed_directories:
- - /home/jonat/ai-stack
- - /tmp/faithh
- # Blocked shell commands for safety
- blocked_commands:
- - rm
- - dd
- - mkfs
- - format
- - fdisk
- - shutdown
- - reboot
- - halt
- # Default permissions for tools
- default_permissions:
- - file.read
- - process.read
- - rag.query
- tools:
- execution_timeout_ms: 30000
- max_concurrent_executions: 5
- enable_combos: true
- combo_bonus_multiplier: 1.5
- api:
- host: localhost
- port: 5557
- websocket_path: /ws/tools
- enable_cors: true
- allowed_origins:
- - http://localhost:8080
- - http://127.0.0.1:8080
- logging:
- level: INFO
- file: logs/tool_execution.log
- max_file_size_mb: 10
- backup_count: 5
- format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
- ai:
- primary_provider: ollama
- fallback_provider: anthropic
- # Local FAITHH models (primary)
- ollama:
- model: qwen25-grounded:latest
- base_url: http://localhost:11434
- # Offloading options to improve context handling
- # Number of GPU layers to keep on GPU (0 = all CPU, -1 = all GPU)
- gpu_layers: -1
- # Context size in tokens (0 = model default)
- context_size: 0
- # Batch size for processing (higher = faster but more VRAM)
- batch_size: 512
- # Keep model in memory after request
- keep_alive: 2h  # Reduced for memory efficiency
- # Groq models (primary inference)
- groq_models:
- default: llama-3.3-70b-versatile
- fast: llama-3.1-8b-instant
- reasoning: openai/gpt-oss-120b
- # Anthropic API (fallback for complex tasks)
- anthropic:
- api_key: ${ANTHROPIC_API_KEY}
- default_model: claude-3-haiku-20240307
- backup_model: claude-3-haiku-20240307
- max_tokens: 4096
- temperature: 0.1
- # Cost optimization settings
- enable_prompt_caching: true
- enable_batch_processing: true
- monthly_budget: 20.0
- cache_ttl_minutes: 60
- # Heavy reasoning model (disabled until environment tuned)
- # heavy_reasoning:
- #   provider: ollama
- #   model: deepseek-r1:32b
- #   gpu_layers: -1
- #   context_size: 8192
- #   batch_size: 512
- #   keep_alive: 30min  # Load on demand

### Dependencies
Dependencies managed in `requirements.txt`:
- flask>=2.3.0
- flask-cors>=4.0.0
- flask-sock>=0.6.0
- google-generativeai>=0.3.0
- pyyaml>=6.0
- requests>=2.31.0
- chromadb>=0.4.0
- sentence-transformers>=2.2.0
- streamlit>=1.28.0
- python-dotenv>=1.0.0
- pytest>=7.0.0
- pytest-asyncio>=0.21.0
- pytest-mock>=3.10.0
- requests-mock>=1.10.0
- pytest-cov>=4.0.0


## 🔒 Security

### Security Measures
- **Rate Limiting**: Configurable request rate limiting
- **Input Validation**: Comprehensive input sanitization
- **Request Protection**: Security middleware for all endpoints
- **Access Control**: Role-based access management (planned)

### Monitoring
- **Health Checks**: Real-time service health monitoring
- **Performance Metrics**: Request tracking and analysis
- **Error Logging**: Comprehensive error tracking and reporting
- **Security Alerts**: Automated security monitoring

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
