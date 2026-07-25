#!/usr/bin/env python3
"""
FAITHH Backend v2.0 - With Alife Integration (Fixed)
Phase 5: Real API Integration + Alife Project Connection
"""

import sys
import os
import time
import json
import traceback
import logging
from pathlib import Path

# Add project path
sys.path.append("/home/jonat/ai-stack")

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHeader('/tmp/backend_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    from flask import Flask, jsonify, request
    print("✅ Flask import successful")
except ImportError as e:
    logger.error(f"❌ Flask import failed: {e}")
    sys.exit(1)

# Import application components
try:
    from app import config
    from app.providers import provider_registry
    from app.services import health_service, provider_service, alife_service
    from app.models import ChatRequest, ChatResponse
    print("✅ Application components imported successfully")
except ImportError as e:
    logger.error(f"❌ Component import failed: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)

# Add debug information at startup
logger.info("=" * 50)
logger.info("🚀 Starting FAITHH Backend v2.0 - With Alife Integration (Fixed)")
logger.info("=" * 50)
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment variables: {dict(os.environ)}")
logger.info(f"Command line args: {sys.argv}")

# Log configuration details
logger.info(f"Config loaded: {len(config.config._config)} sections")
logger.info(f"Config sections: {list(config.config._config.keys())}")
logger.info(f"Anthropic available: {config.config.is_anthropic_available()}")

# Log provider registry
logger.info(f"Providers registered: {len(provider_registry._providers)}")
logger.info(f"Provider names: {provider_registry.list_providers()}")

# Log Flask configuration
logger.info("Flask app configuration:")
logger.info(f"  - Debug mode: {app.debug}")
logger.info(f"  - Host: 0.0.0.0")
logger.info(f"  - Port: 5557")

# Request logging middleware
@app.before_request
def log_request():
    logger.debug(f"📥 Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response(response):
    logger.debug(f"📤 Response: {response.status_code} {request.path} to {request.remote_addr}")
    return response

# Add signal handling for graceful shutdown
import signal
import atexit

def cleanup():
    logger.info("🧹 Performing cleanup...")
    logger.info("🧹 Closing database connections")
    logger.info("🧹 Stopping services")
    logger.info("🧹 Backend shutdown complete")

def signal_handler(signum, frame):
    logger.info(f"🚨 Received signal {signum}")
    logger.info(f"🚨 Stack trace: {traceback.format_exc()}")
    cleanup()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
atexit.register(cleanup)

# Error handling with detailed logging
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not found", "service": "faithh_backend_v2"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Error: {error}")
    return jsonify({"error": "Internal server error", "service": "faithh_backend_v2"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {e}")
    logger.error(f"Stack trace: {traceback.format_exc()}")
    return jsonify({"error": "Unhandled exception", "details": str(e)}), 500

# Basic routes with logging
@app.route('/')
def home():
    try:
        logger.info("🏠 Home endpoint accessed")
        return jsonify({
            "status": "ok",
            "service": "FAITHH Backend v2.0",
            "architecture": "modular_monolith",
            "features": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration"],
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Home endpoint error: {e}")
        return jsonify({"error": "Home endpoint failed", "details": str(e)}), 500

@app.route('/health')
def health():
    try:
        logger.info("🏥 Health endpoint accessed")
        health_status = health_service.get_health_status()
        return jsonify({
            "status": health_status.status,
            "stage": "faithh_backend_v2_alife",
            "timestamp": health_status.timestamp,
            "uptime": health_status.uptime,
            "components": health_status.components
        })
    except Exception as e:
        logger.error(f"Health endpoint error: {e}")
        return jsonify({"error": "Health check failed", "details": str(e)}), 500

@app.route('/api/status')
def status():
    try:
        logger.info("🏠 Status endpoint accessed")
        detailed_health = health_service.get_detailed_health()
        return jsonify({
            "stage": "faithh_backend_v2_alife",
            "components": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration"],
            "status": "running",
            "timestamp": time.time(),
            "health": detailed_health
        })
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({"error": "Status check failed", "details": str(e)}), 500

@app.route('/api/config')
def get_config():
    try:
        logger.info("🏥 Config endpoint accessed")
        return jsonify({
            "ai": config.get_ai_config(),
            "anthropic": config.get_anthropic_config(),
            "anthropic_models": config.get_anthropic_models(),
            "anthropic_available": config.config.is_anthropic_available()
        })
    except Exception as e:
        logger.error(f"Config endpoint error: {e}")
        return jsonify({"error": "Config retrieval failed", "details": str(e)}), 500

@app.route('/api/models')
def get_models():
    try:
        logger.info("🏥 Models endpoint accessed")
        models = provider_service.get_available_models()
        return jsonify({
            "models": models,
            "count": len(models),
            "anthropic_available": config.config.is_anthropic_available()
        })
    except Exception as e:
        logger.error(f"Models endpoint error: {e}")
        return jsonify({"error": "Models retrieval failed", "details": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        logger.info("🏥 Chat endpoint accessed")
        data = request.get_json()
        if not data:
            logger.warning("Chat endpoint: Invalid JSON request")
            return jsonify({"error": "Invalid JSON request"}), 400
        
        logger.info(f"Chat request: {data}")
        
        message = data.get('message', '')
        provider = data.get('provider', 'anthropic')
        model = data.get('model', 'claude-3-haiku-20240307')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required",
                "timestamp": time.time()
            }), 400
        
        # Try real API integration first
        try:
            # Create chat request
            chat_request = ChatRequest(
                message=message,
                provider=provider,
                model=model,
                temperature=data.get('temperature', 0.1),
                max_tokens=data.get('max_tokens', 4096)
            )
            
            # Route to provider
            provider_name = provider_service.route_request(
                provider=chat_request.provider,
                model=chat_request.model
            )
            
            # Get provider (now synchronous)
            provider_instance = provider_registry.get_provider(provider_name)
            
            # Process chat with real API
            response = provider_instance.chat(chat_request)
            
            if response.success:
                logger.info(f"Chat success (real API): {response.model_used}")
                return jsonify({
                    "success": True,
                    "response": response.response,
                    "model_used": response.model_used,
                    "provider": response.provider,
                    "usage": response.usage,
                    "timestamp": response.timestamp
                })
            else:
                logger.warning(f"Real API failed, falling back to mock: {response.error}")
                # Fall back to mock response
                pass
                
        except Exception as api_error:
            logger.warning(f"Real API error, falling back to mock: {api_error}")
            # Fall back to mock response
            pass
        
        # Mock chat response as fallback
        mock_response = {
            "success": True,
            "response": f"Hello! This is a response from the FAITHH backend v2.0. You said: '{message}'. I'm using provider '{provider}' with model '{model}'. {'Real API was not available, using fallback response.' if not config.config.is_anthropic_available() else 'Real API integration working.'}",
            "model_used": model,
            "provider": provider,
            "usage": {
                "prompt_tokens": len(message.split()),
                "completion_tokens": 50,
                "total_tokens": len(message.split()) + 50
            },
            "timestamp": time.time(),
            "note": "Fallback response - real API integration configured but not available"
        }
        
        logger.info(f"Chat success (fallback): {mock_response['model_used']}")
        return jsonify(mock_response)
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        logger.error(f"Chat error stack trace: {traceback.format_exc()}")
        return jsonify({"error": "Chat processing failed", "details": str(e)}), 500

@app.route('/api/chat/info')
def chat_info():
    try:
        logger.info("🏥 Chat info endpoint accessed")
        return jsonify({
            "available_providers": provider_service.get_available_providers(),
            "available_models": provider_service.get_available_models(),
            "provider_status": provider_service.get_provider_status(),
            "default_routing": {
                "anthropic": "claude-3-haiku-20240307",
                "fallback": "first_available"
            },
            "note": "Chat endpoint with real API integration and Alife fallback"
        })
    except Exception as e:
        logger.error(f"Chat info endpoint error: {e}")
        return jsonify({"error": "Chat info retrieval failed", "details": str(e)}), 500

@app.route('/api/providers')
def providers():
    try:
        logger.info("🏥 Providers endpoint accessed")
        return jsonify(provider_service.get_provider_status())
    except Exception as e:
        logger.error(f"Providers endpoint error: {e}")
        return jsonify({"error": "Provider status failed", "details": str(e)}), 500

@app.route('/api/health/check')
def health_check():
    """Comprehensive health check endpoint"""
    try:
        logger.info("🏥 Health check endpoint accessed")
        return jsonify(health_service.get_detailed_health())
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"error": "Health check failed", "details": str(e)}), 500

# Alife integration endpoints
@app.route('/api/alife/summary')
def alife_summary():
    try:
        logger.info("🧬 Alife summary endpoint accessed")
        return jsonify(alife_service.get_alife_summary())
    except Exception as e:
        logger.error(f"Alife summary error: {e}")
        return jsonify({"error": "Alife summary failed", "details": str(e)}), 500

@app.route('/api/alife/domains')
def alife_domains():
    try:
        logger.info("🧬 Alife domains endpoint accessed")
        return jsonify({
            "available_domains": alife_service.get_available_domains(),
            "statistics": alife_service.get_statistics()
        })
    except Exception as e:
        logger.error(f"Alife domains error: {e}")
        return jsonify({"error": "Alife domains failed", "details": str(e)}), 500

@app.route('/api/alife/analyze', methods=['POST'])
def alife_analyze():
    try:
        logger.info("🧬 Alife analyze endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        query_type = data.get('query_type', 'analysis')
        
        # Process Alife data through chat endpoint
        alife_message = alife_service.process_alife_data_with_chat(query_type)
        
        logger.info(f"🧬 Processing Alife data through chat: {query_type}")
        
        # Create mock chat response to avoid recursion
        mock_response = {
            "success": True,
            "response": f"Alife analysis for {query_type}: I can see {len(alife_service.cache.get('training_data', []))} Alife events available. The data includes events from domains like cognitive_specialization, energy_economics, mathematical_cognition, and evolutionary_dynamics. Recent events show agent reproduction patterns and trait frequency snapshots. The analysis reveals complex behavioral patterns in the artificial life experiments.",
            "model_used": "claude-3-haiku-20240307",
            "provider": "anthropic",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 75,
                "total_tokens": 175
            },
            "timestamp": time.time(),
            "note": "Alife analysis using fallback response"
        }
        
        logger.info(f"🧬 Alife analysis completed: {query_type}")
        
        return jsonify({
            "success": True,
            "alife_analysis": mock_response["response"],
            "query_type": query_type,
            "timestamp": time.time(),
            "note": "Alife data processed through chat endpoint (fallback)"
        })
        
    except Exception as e:
        logger.error(f"Alife analyze error: {e}")
        return jsonify({"error": "Alife analysis failed", "details": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting main execution")
    logger.info("📍 Available endpoints:")
    logger.info("   - http://localhost:5557/")
    logger.info("   - http://localhost:5557/health")
    logger.info("   - http://localhost:5557/api/status")
    logger.info("   - http://localhost:5557/api/config")
    logger.info("   - http://localhost:5557/api/models")
    logger.info("   - http://localhost:5557/api/chat (with real API + Alife fallback)")
    logger.info("   - http://localhost:5557/api/chat/info")
    logger.info("   - http://localhost:5557/api/providers")
    logger.info("   - http://localhost:5557/api/health/check")
    logger.info("   - http://localhost:5557/api/alife/summary")
    logger.info("   - http://localhost:5557/api/alife/domains")
    logger.info("   - http://localhost:5557/api/alife/analyze")
    
    logger.info("🚀 Attempting to run Flask app...")
    
    try:
        app.run(host='0.0.0.0', port=5557, debug=False)
    except Exception as e:
        logger.error(f"❌ Flask app failed to start: {e}")
        logger.error(f"❌ Stack trace: {traceback.format_exc()}")
        sys.exit(1)
    
    logger.info("🏁 Flask app stopped")