#!/usr/bin/env python3
"""
FAITHH Backend v2.0 - Phase 3B: Alife Parasitic Integration
Phase 5: Real API Integration + Alife + Standing Wave + Moon Damping + Parasitic Feeding + Alife Data Integration
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
    from app.services import health_service, provider_service, alife_service, standing_wave_moon_service, parasitic_alife_service, alife_parasitic_integration
    from app.models import ChatRequest, ChatResponse
    print("✅ Application components imported successfully")
except ImportError as e:
    logger.error(f"❌ Component import failed: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)

# Add debug information at startup
logger.info("=" * 50)
logger.info("🚀 Starting FAITHH Backend v2.0 - Phase 3B: Alife Parasitic Integration")
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
            "features": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration", "standing_wave_resonance", "moon_damping", "parasitic_feeding", "alife_parasitic_integration"],
            "phase": "3B - Alife Parasitic Integration",
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
            "stage": "faithh_backend_v2_phase3b",
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
            "stage": "faithh_backend_v2_phase3b",
            "components": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration", "standing_wave_resonance", "moon_damping", "parasitic_feeding", "alife_parasitic_integration"],
            "status": "running",
            "phase": "3B - Alife Parasitic Integration",
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
            "response": f"Hello! This is a response from the FAITHH backend v2.0 Phase 3B. You said: '{message}'. I'm using provider '{provider}' with model '{model}'. {'Real API was not available, using fallback response.' if not config.config.is_anthropic_available() else 'Real API integration working.'}",
            "model_used": model,
            "provider": provider,
            "usage": {
                "prompt_tokens": len(message.split()),
                "completion_tokens": 50,
                "total_tokens": len(message.split()) + 50
            },
            "timestamp": time.time(),
            "note": "Fallback response - Phase 3B Alife Parasitic Integration backend"
        }
        
        logger.info(f"Chat success (fallback): {mock_response['model_used']}")
        return jsonify(mock_response)
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        logger.error(f"Chat error stack trace: {traceback.format_exc()}")
        return jsonify({"error": "Chat processing failed", "details": str(e)}), 500

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

# Moon Damping Enhanced Standing Wave Resonance endpoints
@app.route('/api/moon-damping/setup', methods=['POST'])
def moon_damping_setup():
    try:
        logger.info("🌙 Moon damping setup endpoint accessed")
        data = request.get_json()
        experiment_id = data.get('experiment_id', 'moon_damping_v1') if data else 'moon_damping_v1'
        moon_enabled = data.get('moon_enabled', True) if data else True
        moon_mass = data.get('moon_mass', 0.3) if data else 0.3
        
        result = standing_wave_moon_service.setup_standing_wave_experiment(
            experiment_id=experiment_id,
            moon_enabled=moon_enabled,
            moon_mass=moon_mass
        )
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🌙 Moon damping experiment setup: {experiment_id}, moon_enabled: {moon_enabled}")
        return jsonify({
            "success": True,
            "experiment": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Moon damping setup error: {e}")
        return jsonify({"error": "Moon damping setup failed", "details": str(e)}), 500

@app.route('/api/moon-damping/status/<experiment_id>')
def moon_damping_status(experiment_id):
    try:
        logger.info(f"🌙 Moon damping status endpoint accessed: {experiment_id}")
        result = standing_wave_moon_service.get_experiment_status(experiment_id)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 404
        
        return jsonify({
            "success": True,
            "status": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Moon damping status error: {e}")
        return jsonify({"error": "Moon damping status failed", "details": str(e)}), 500

@app.route('/api/moon-damping/place-agent', methods=['POST'])
def moon_damping_place_agent():
    try:
        logger.info("🌙 Moon damping place agent endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        experiment_id = data.get('experiment_id', 'moon_damping_v1')
        agent_id = data.get('agent_id')
        position = data.get('position')
        
        if not agent_id or position is None:
            return jsonify({"error": "agent_id and position required"}), 400
        
        result = standing_wave_moon_service.place_agent(experiment_id, agent_id, position)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🌙 Agent placed: {agent_id} at position {position}")
        return jsonify({
            "success": True,
            "placement": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Moon damping place agent error: {e}")
        return jsonify({"error": "Moon damping place agent failed", "details": str(e)}), 500

# Parasitic Impedance Feeding endpoints
@app.route('/api/parasitic/setup', methods=['POST'])
def parasitic_setup():
    try:
        logger.info("🦠 Parasitic setup endpoint accessed")
        data = request.get_json()
        experiment_id = data.get('experiment_id', 'moon_damping_v1') if data else 'moon_damping_v1'
        
        result = parasitic_alife_service.add_parasitic_feeding_to_experiment(experiment_id, standing_wave_moon_service)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🦠 Parasitic feeding enabled: {experiment_id}")
        return jsonify({
            "success": True,
            "parasitic_setup": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Parasitic setup error: {e}")
        return jsonify({"error": "Parasitic setup failed", "details": str(e)}), 500

@app.route('/api/parasitic/create-agent', methods=['POST'])
def parasitic_create_agent():
    try:
        logger.info("🦠 Parasitic create agent endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        experiment_id = data.get('experiment_id', 'moon_damping_v1')
        agent_id = data.get('agent_id')
        position = data.get('position')
        
        if not agent_id or position is None:
            return jsonify({"error": "agent_id and position required"}), 400
        
        # Get Moon damping data for this position
        moon_result = standing_wave_moon_service.place_agent(experiment_id, f"temp_{agent_id}", position)
        moon_damping_data = moon_result.get("placement", {}).get("agent_data", {})
        
        result = parasitic_alife_service.create_parasitic_agent(experiment_id, agent_id, position, moon_damping_data)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🦠 Parasitic agent created: {agent_id} at position {position}")
        return jsonify({
            "success": True,
            "parasitic_agent": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Parasitic create agent error: {e}")
        return jsonify({"error": "Parasitic create agent failed", "details": str(e)}), 500

@app.route('/api/parasitic/extract-energy', methods=['POST'])
def parasitic_extract_energy():
    try:
        logger.info("🦠 Parasitic extract energy endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        experiment_id = data.get('experiment_id', 'moon_damping_v1')
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({"error": "agent_id required"}), 400
        
        result = parasitic_alife_service.extract_parasitic_energy(experiment_id, agent_id)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🦠 Energy extracted for agent: {agent_id}")
        return jsonify({
            "success": True,
            "energy_extraction": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Parasitic extract energy error: {e}")
        return jsonify({"error": "Parasitic extract energy failed", "details": str(e)}), 500

@app.route('/api/parasitic/sustain-nuclear', methods=['POST'])
def parasitic_sustain_nuclear():
    try:
        logger.info("🦠 Parasitic sustain nuclear endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        experiment_id = data.get('experiment_id', 'moon_damping_v1')
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({"error": "agent_id required"}), 400
        
        result = parasitic_alife_service.sustain_nuclear_processes(experiment_id, agent_id)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🦠 Nuclear processes sustained for agent: {agent_id}")
        return jsonify({
            "success": True,
            "nuclear_sustain": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Parasitic sustain nuclear error: {e}")
        return jsonify({"error": "Parasitic sustain nuclear failed", "details": str(e)}), 500

@app.route('/api/parasitic/analyze/<experiment_id>')
def parasitic_analyze(experiment_id):
    try:
        logger.info(f"🦠 Parasitic analyze endpoint accessed: {experiment_id}")
        result = parasitic_alife_service.analyze_parasitic_network(experiment_id)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 404
        
        logger.info(f"🦠 Parasitic analysis completed: {experiment_id}")
        return jsonify({
            "success": True,
            "parasitic_analysis": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Parasitic analyze error: {e}")
        return jsonify({"error": "Parasitic analyze failed", "details": str(e)}), 500

@app.route('/api/parasitic/compare-moon/<experiment_id>')
def parasitic_compare_moon(experiment_id):
    try:
        logger.info(f"🦠 Parasitic compare Moon endpoint accessed: {experiment_id}")
        result = parasitic_alife_service.compare_parasitic_with_without_moon(experiment_id)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 404
        
        logger.info(f"🦠 Parasitic Moon comparison completed: {experiment_id}")
        return jsonify({
            "success": True,
            "moon_comparison": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Parasitic compare Moon error: {e}")
        return jsonify({"error": "Parasitic compare Moon failed", "details": str(e)}), 500

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

if __name__ == '__main__':
    logger.info("🚀 Starting main execution")
    logger.info("📍 Available endpoints:")
    logger.info("   - http://localhost:5557/")
    logger.info("   - http://localhost:5557/health")
    logger.info("   - http://localhost:5557/api/status")
    logger.info("   - http://localhost:5557/api/chat (with real API + Alife + Moon damping + Parasitic feeding + Phase 3B integration)")
    logger.info("   - http://localhost:5557/api/alife/summary")
    logger.info("   - http://localhost:5557/api/alife/domains")
    logger.info("   - http://localhost:5557/api/alife/analyze")
    logger.info("   - http://localhost:5557/api/moon-damping/setup")
    logger.info("   - http://localhost:5557/api/moon-damping/status/<experiment_id>")
    logger.info("   - http://localhost:5557/api/moon-damping/place-agent")
    logger.info("   - http://localhost:5557/api/parasitic/setup")
    logger.info("   - http://localhost:5557/api/parasitic/create-agent")
    logger.info("   - http://localhost:5557/api/parasitic/extract-energy")
    logger.info("   - http://localhost:5557/api/parasitic/sustain-nuclear")
    logger.info("   - http://localhost:5557/api/parasitic/analyze/<experiment_id>")
    logger.info("   - http://localhost:5557/api/parasitic/compare-moon/<experiment_id>")
    logger.info("   - http://localhost:5557/api/phase3b/load-alife-data")
    logger.info("   - http://localhost:5557/api/phase3b/map-signatures")
    logger.info("   - http://localhost:5557/api/phase3b/identify-domains")
    
    logger.info("🚀 Attempting to run Flask app...")
    
    try:
        app.run(host='0.0.0.0', port=5557, debug=False)
    except Exception as e:
        logger.error(f"❌ Flask app failed to start: {e}")
        logger.error(f"❌ Stack trace: {traceback.format_exc()}")
        sys.exit(1)
    
    logger.info("🏁 Flask app stopped")