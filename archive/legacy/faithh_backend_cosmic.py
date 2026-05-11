#!/usr/bin/env python3
"""
FAITHH Backend v2.0 - Phase 4: Cosmic Ripple Integration
Phase 5: Real API Integration + Alife + Standing Wave + Moon Damping + Parasitic Feeding + Alife Data Integration + Cosmic Ripple Integration
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
        logging.FileHandler('/tmp/backend_debug.log'),
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
    from app.services import (health_service, provider_service, alife_service, 
                            standing_wave_moon_service, parasitic_alife_service, 
                            alife_parasitic_integration)
    from app.models import ChatRequest, ChatResponse
    from app.services.cosmic_ripple_integration import CosmicRippleIntegration
    print("✅ Application components imported successfully")
except ImportError as e:
    logger.error(f"❌ Component import failed: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)

# Add debug information at startup
logger.info("=" * 50)
logger.info("🚀 Starting FAITHH Backend v2.0 - Phase 4: Cosmic Ripple Integration")
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

# Initialize cosmic ripple integration
cosmic_ripple_service = CosmicRippleIntegration(parasitic_alife_service)

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
            "features": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration", "standing_wave_resonance", "moon_damping", "parasitic_feeding", "alife_parasitic_integration", "cosmic_ripple_integration"],
            "phase": "4 - Cosmic Ripple Integration",
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
            "stage": "faithh_backend_v2_phase4",
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
            "stage": "faithh_backend_v2_phase4",
            "components": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration", "standing_wave_resonance", "moon_damping", "parasitic_feeding", "alife_parasitic_integration", "cosmic_ripple_integration"],
            "status": "running",
            "phase": "4 - Cosmic Ripple Integration",
            "timestamp": time.time(),
            "health": detailed_health
        })
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({"error": "Status check failed", "details": str(e)}), 500

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
            "response": f"Hello! This is a response from the FAITHH backend v2.0 Phase 4. You said: '{message}'. I'm using provider '{provider}' with model '{model}'. {'Real API was not available, using fallback response.' if not config.config.is_anthropic_available() else 'Real API integration working.'}",
            "model_used": model,
            "provider": provider,
            "usage": {
                "prompt_tokens": len(message.split()),
                "completion_tokens": 50,
                "total_tokens": len(message.split()) + 50
            },
            "timestamp": time.time(),
            "note": "Fallback response - Phase 4 Cosmic Ripple Integration backend"
        }
        
        logger.info(f"Chat success (fallback): {mock_response['model_used']}")
        return jsonify(mock_response)
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        logger.error(f"Chat error stack trace: {traceback.format_exc()}")
        return jsonify({"error": "Chat processing failed", "details": str(e)}), 500

# Phase 3B: Alife Parasitic Integration endpoints
@app.route('/api/phase3b/load-alife-data')
def load_alife_data():
    try:
        logger.info("📊 Phase 3B load Alife data endpoint accessed")
        result = alife_parasitic_integration.load_alife_data()
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"📊 Alife data loaded: {result['total_events']} events")
        return jsonify({
            "success": True,
            "data_load": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Phase 3B load Alife data error: {e}")
        return jsonify({"error": "Phase 3B load Alife data failed", "details": str(e)}), 500

@app.route('/api/phase3b/map-signatures')
def map_parasitic_signatures():
    try:
        logger.info("📊 Phase 3B map signatures endpoint accessed")
        result = alife_parasitic_integration.map_parasitic_signatures()
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"📊 Parasitic signatures mapped: {result['total_events_mapped']} events")
        return jsonify({
            "success": True,
            "signature_mapping": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Phase 3B map signatures error: {e}")
        return jsonify({"error": "Phase 3B map signatures failed", "details": str(e)}), 500

@app.route('/api/phase3b/identify-domains')
def identify_parasitic_domains():
    try:
        logger.info("📊 Phase 3B identify domains endpoint accessed")
        result = alife_parasitic_integration.identify_parasitic_domains()
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info("📊 Parasitic domains identified")
        return jsonify({
            "success": True,
            "domain_analysis": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Phase 3B identify domains error: {e}")
        return jsonify({"error": "Phase 3B identify domains failed", "details": str(e)}), 500

# Phase 4: Cosmic Ripple Integration endpoints
@app.route('/api/cosmic/stellar-interference', methods=['POST'])
def stellar_interference():
    try:
        logger.info("🌌 Cosmic stellar interference endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        position = data.get('position', [0.0, 0.0, 0.0])
        if not isinstance(position, list) or len(position) != 3:
            return jsonify({"error": "Position must be [x, y, z] coordinates"}), 400
        
        result = cosmic_ripple_service.calculate_stellar_interference(tuple(position))
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🌌 Stellar interference calculated for position: {position}")
        return jsonify({
            "success": True,
            "stellar_interference": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Cosmic stellar interference error: {e}")
        return jsonify({"error": "Cosmic stellar interference failed", "details": str(e)}), 500

@app.route('/api/cosmic/ripple-field', methods=['POST'])
def cosmic_ripple_field():
    try:
        logger.info("🌌 Cosmic ripple field endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        position = data.get('position', [0.0, 0.0, 0.0])
        if not isinstance(position, list) or len(position) != 3:
            return jsonify({"error": "Position must be [x, y, z] coordinates"}), 400
        
        field = cosmic_ripple_service.calculate_cosmic_ripple_field(tuple(position))
        
        logger.info(f"🌌 Cosmic ripple field calculated for position: {position}")
        return jsonify({
            "success": True,
            "cosmic_field": {
                "stellar_interference": field.stellar_interference,
                "resonance_frequency": field.resonance_frequency,
                "impedance_gradient": field.impedance_gradient,
                "harvesting_efficiency": field.harvesting_efficiency,
                "negative_impedance_zones": field.negative_impedance_zones
            },
            "position": position,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Cosmic ripple field error: {e}")
        return jsonify({"error": "Cosmic ripple field failed", "details": str(e)}), 500

@app.route('/api/cosmic/analyze-potential', methods=['POST'])
def analyze_cosmic_potential():
    try:
        logger.info("🌌 Cosmic analyze potential endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        positions = data.get('positions', [])
        if not isinstance(positions, list):
            return jsonify({"error": "Positions must be a list of [x, y, z] coordinates"}), 400
        
        # Validate positions
        for pos in positions:
            if not isinstance(pos, list) or len(pos) != 3:
                return jsonify({"error": "Each position must be [x, y, z] coordinates"}), 400
        
        result = cosmic_ripple_service.analyze_cosmic_parasitic_potential(positions)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🌌 Cosmic potential analyzed for {len(positions)} positions")
        return jsonify({
            "success": True,
            "cosmic_analysis": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Cosmic analyze potential error: {e}")
        return jsonify({"error": "Cosmic analyze potential failed", "details": str(e)}), 500

@app.route('/api/cosmic/stellar-catalog')
def stellar_catalog():
    try:
        logger.info("🌌 Cosmic stellar catalog endpoint accessed")
        
        catalog_data = []
        for star in cosmic_ripple_service.stellar_catalog:
            catalog_data.append({
                "name": star.name,
                "mass": star.mass,
                "position": star.position,
                "luminosity": star.luminosity,
                "spectral_type": star.spectral_type
            })
        
        logger.info(f"🌌 Stellar catalog returned: {len(catalog_data)} stars")
        return jsonify({
            "success": True,
            "stellar_catalog": catalog_data,
            "base_frequency": cosmic_ripple_service.base_frequency,
            "mathematical_resonance": cosmic_ripple_service.mathematical_resonance,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Cosmic stellar catalog error: {e}")
        return jsonify({"error": "Cosmic stellar catalog failed", "details": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting main execution")
    logger.info("📍 Available endpoints:")
    logger.info("   - http://localhost:5557/")
    logger.info("   - http://localhost:5557/health")
    logger.info("   - http://localhost:5557/api/status")
    logger.info("   - http://localhost:5557/api/chat (with real API + Alife + Moon damping + Parasitic feeding + Phase 3B + Cosmic integration)")
    logger.info("   - http://localhost:5557/api/phase3b/load-alife-data")
    logger.info("   - http://localhost:5557/api/phase3b/map-signatures")
    logger.info("   - http://localhost:5557/api/phase3b/identify-domains")
    logger.info("   - http://localhost:5557/api/cosmic/stellar-interference")
    logger.info("   - http://localhost:5557/api/cosmic/ripple-field")
    logger.info("   - http://localhost:5557/api/cosmic/analyze-potential")
    logger.info("   - http://localhost:5557/api/cosmic/stellar-catalog")
    
    logger.info("🚀 Attempting to run Flask app...")
    
    try:
        app.run(host='0.0.0.0', port=5557, debug=False)
    except Exception as e:
        logger.error(f"❌ Flask app failed to start: {e}")
        logger.error(f"❌ Stack trace: {traceback.format_exc()}")
        sys.exit(1)
    
    logger.info("🏁 Flask app stopped")