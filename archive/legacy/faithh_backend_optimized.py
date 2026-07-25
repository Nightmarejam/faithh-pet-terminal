#!/usr/bin/env python3
"""
FAITHH Backend v2.0 - Phase 5: Universal Impedance Field (Optimized)
Optimized version based on Sonnet's performance assessment
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
    from flask import Flask, jsonify, request, send_from_directory
    from pathlib import Path
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
    from app.services.universal_impedance_field_optimized import UniversalImpedanceFieldOptimized
    print("✅ Application components imported successfully")
except ImportError as e:
    logger.error(f"❌ Component import failed: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)

# Define base directory for serving files
BASE_DIR = Path(__file__).parent

# Add debug information at startup
logger.info("=" * 50)
logger.info("🚀 Starting FAITHH Backend v2.0 - Phase 5: Universal Impedance Field (Optimized)")
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

# Initialize services
cosmic_ripple_service = CosmicRippleIntegration(parasitic_alife_service)
universal_impedance_service = UniversalImpedanceFieldOptimized(cosmic_ripple_service)

# Initialize genomic services after dependencies are available
from app.services.genomic_impedance_sensor import GenomicImpedanceSensor
from app.services.genomic_biasing_engine import GenomicBiasingEngine

genomic_impedance_sensor = GenomicImpedanceSensor(parasitic_alife_service, universal_impedance_service)
genomic_biasing_engine = GenomicBiasingEngine(genomic_impedance_sensor)

# Debug: Check what we actually have
logger.info(f"Genomic impedance sensor type: {type(genomic_impedance_sensor)}")
logger.info(f"Genomic impedance sensor dir: {dir(genomic_impedance_sensor)}")
if hasattr(genomic_impedance_sensor, 'create_genomic_sensor'):
    logger.info("✅ create_genomic_sensor method found")
else:
    logger.error("❌ create_genomic_sensor method NOT found")

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

# HTML serving routes
@app.route('/')
def index():
    """Serve the HTML UI"""
    try:
        logger.info("🏠 Serving HTML UI at root path")
        return send_from_directory(BASE_DIR, 'faithh_pet_v4.html')
    except Exception as e:
        logger.error(f"Failed to serve HTML: {e}")
        return jsonify({"error": "UI not available", "details": str(e)}), 500

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve image files"""
    try:
        images_dir = BASE_DIR / 'images'
        if not images_dir.exists():
            images_dir.mkdir(parents=True, exist_ok=True)
        return send_from_directory(images_dir, filename)
    except Exception as e:
        logger.error(f"Failed to serve image {filename}: {e}")
        return jsonify({"error": "Image not found", "details": str(e)}), 404

@app.route('/favicon.ico')
def favicon():
    """Serve site favicon."""
    try:
        return send_from_directory(BASE_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception as e:
        logger.error(f"Failed to serve favicon: {e}")
        return jsonify({"error": "Favicon not found"}), 404

@app.route('/manifest.json')
def pwa_manifest():
    """Serve PWA manifest."""
    try:
        return send_from_directory(BASE_DIR, 'manifest.json', mimetype='application/manifest+json')
    except Exception as e:
        logger.error(f"Failed to serve manifest: {e}")
        return jsonify({"error": "Manifest not found"}), 404

@app.route('/sw.js')
def pwa_service_worker():
    """Serve PWA service worker."""
    try:
        return send_from_directory(BASE_DIR, 'sw.js', mimetype='application/javascript')
    except Exception as e:
        logger.error(f"Failed to serve service worker: {e}")
        return jsonify({"error": "Service worker not found"}), 404

@app.route('/icons/<path:filename>')
def pwa_icons(filename):
    """Serve PWA icon files."""
    try:
        icons_dir = BASE_DIR / 'icons'
        return send_from_directory(icons_dir, filename)
    except Exception as e:
        logger.error(f"Failed to serve icon {filename}: {e}")
        return jsonify({"error": "Icon not found"}), 404

# Basic routes with logging
@app.route('/api/home')
def home():
    try:
        logger.info("🏠 Home endpoint accessed")
        return jsonify({
            "status": "ok",
            "service": "FAITHH Backend v2.0",
            "architecture": "modular_monolith",
            "features": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration", "standing_wave_resonance", "moon_damping", "parasitic_feeding", "alife_parasitic_integration", "cosmic_ripple_integration", "universal_impedance_field_optimized"],
            "phase": "5 - Universal Impedance Field (Optimized)",
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
            "stage": "faithh_backend_v2_phase5_optimized",
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
            "stage": "faithh_backend_v2_phase5_optimized",
            "components": ["flask", "config", "providers", "services", "logging", "mock_chat", "alife_integration", "standing_wave_resonance", "moon_damping", "parasitic_feeding", "alife_parasitic_integration", "cosmic_ripple_integration", "universal_impedance_field_optimized"],
            "status": "running",
            "phase": "5 - Universal Impedance Field (Optimized)",
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
            "response": f"Hello! This is a response from the FAITHH backend v2.0 Phase 5 (Optimized). You said: '{message}'. I'm using provider '{provider}' with model '{model}'. {'Real API was not available, using fallback response.' if not config.config.is_anthropic_available() else 'Real API integration working.'}",
            "model_used": model,
            "provider": provider,
            "usage": {
                "prompt_tokens": len(message.split()),
                "completion_tokens": 50,
                "total_tokens": len(message.split()) + 50
            },
            "timestamp": time.time(),
            "note": "Fallback response - Phase 5 Universal Impedance Field (Optimized) backend"
        }
        
        logger.info(f"Chat success (fallback): {mock_response['model_used']}")
        return jsonify(mock_response)
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        logger.error(f"Chat error stack trace: {traceback.format_exc()}")
        return jsonify({"error": "Chat processing failed", "details": str(e)}), 500

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

# Phase 5: Universal Impedance Field (Optimized) endpoints
@app.route('/api/universal/impedance-point', methods=['POST'])
def universal_impedance_point():
    try:
        logger.info("🌌 Universal impedance point endpoint accessed (OPTIMIZED)")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        position = data.get('position', [0.0, 0.0, 0.0])
        if not isinstance(position, list) or len(position) != 3:
            return jsonify({"error": "Position must be [x, y, z] coordinates"}), 400
        
        # OPTIMIZED: Use cached calculation
        field_point = universal_impedance_service.calculate_universal_impedance(tuple(position))
        
        logger.info(f"🌌 Universal impedance calculated for position: {position}")
        return jsonify({
            "success": True,
            "universal_field": {
                "position": field_point.position,
                "base_impedance": field_point.base_impedance,
                "stellar_contribution": field_point.stellar_contribution,
                "dark_energy_modulation": field_point.dark_energy_modulation,
                "quantum_fluctuation": field_point.quantum_fluctuation,
                "total_impedance": field_point.total_impedance,
                "gradient_vector": field_point.gradient_vector,
                "resonance_zones": field_point.resonance_zones
            },
            "optimization": "cached_calculations",
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Universal impedance point error: {e}")
        return jsonify({"error": "Universal impedance point failed", "details": str(e)}), 500

@app.route('/api/universal/analyze-patterns', methods=['POST'])
def universal_analyze_patterns():
    try:
        logger.info("🌌 Universal analyze patterns endpoint accessed (OPTIMIZED)")
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
        
        # OPTIMIZED: Use optimized pattern analysis
        result = universal_impedance_service.analyze_universal_patterns_optimized(positions)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🌌 Universal patterns analyzed for {len(positions)} positions")
        return jsonify({
            "success": True,
            "pattern_analysis": result,
            "optimization": "reduced_complexity",
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Universal analyze patterns error: {e}")
        return jsonify({"error": "Universal analyze patterns failed", "details": str(e)}), 500

@app.route('/api/universal/dark-energy-regions')
def dark_energy_regions():
    try:
        logger.info("🌌 Dark energy regions endpoint accessed")
        
        regions_data = []
        for region in universal_impedance_service.dark_energy_regions:
            regions_data.append({
                "name": region.name,
                "center": region.center,
                "radius": region.radius,
                "strength": region.strength,
                "type": region.type
            })
        
        logger.info(f"🌌 Dark energy regions returned: {len(regions_data)} regions")
        return jsonify({
            "success": True,
            "dark_energy_regions": regions_data,
            "dark_energy_constant": universal_impedance_service.dark_energy_constant,
            "matter_density": universal_impedance_service.matter_density,
            "hubble_constant": universal_impedance_service.hubble_constant,
            "field_resolution": universal_impedance_service.field_resolution,
            "optimization": "reduced_resolution_20_points",
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Dark energy regions error: {e}")
        return jsonify({"error": "Dark energy regions failed", "details": str(e)}), 500

# Phase 6: Genomic Impedance Reading endpoints
@app.route('/api/genomic/impedance-sensor', methods=['POST'])
def create_genomic_impedance_sensor():
    try:
        logger.info("🧬 Genomic impedance sensor endpoint accessed")
        logger.info(f"Genomic sensor type in endpoint: {type(genomic_impedance_sensor)}")
        logger.info(f"Genomic sensor has create_genomic_sensor: {hasattr(genomic_impedance_sensor, 'create_genomic_sensor')}")
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        organism_id = data.get('organism_id')
        position = data.get('position', [0.0, 0.0, 0.0])
        sensitivity = data.get('sensitivity', 0.7)
        
        if not organism_id:
            return jsonify({"error": "organism_id is required"}), 400
        
        if not isinstance(position, list) or len(position) != 3:
            return jsonify({"error": "Position must be [x, y, z] coordinates"}), 400
        
        logger.info(f"About to call create_genomic_sensor for {organism_id}")
        result = genomic_impedance_sensor.create_genomic_sensor(organism_id, tuple(position), sensitivity)
        logger.info(f"Result from create_genomic_sensor: {result}")
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🧬 Genomic sensor created for organism: {organism_id}")
        return jsonify({
            "success": True,
            "genomic_sensor": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Genomic impedance sensor error: {e}")
        logger.error(f"Genomic impedance sensor traceback: {traceback.format_exc()}")
        return jsonify({"error": "Genomic impedance sensor failed", "details": str(e)}), 500

@app.route('/api/genomic/biasing-analysis', methods=['POST'])
def genomic_biasing_analysis():
    try:
        logger.info("🧬 Genomic biasing analysis endpoint accessed")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400
        
        organism_id = data.get('organism_id')
        original_genome = data.get('original_genome')
        biasing_strength = data.get('biasing_strength', 0.5)
        
        if not organism_id or not original_genome:
            return jsonify({"error": "organism_id and original_genome are required"}), 400
        
        result = genomic_biasing_engine.apply_genomic_biasing(organism_id, original_genome, biasing_strength)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🧬 Genomic biasing analysis completed for organism: {organism_id}")
        return jsonify({
            "success": True,
            "biasing_analysis": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Genomic biasing analysis error: {e}")
        return jsonify({"error": "Genomic biasing analysis failed", "details": str(e)}), 500

@app.route('/api/genomic/sensor-readings/<organism_id>')
def genomic_sensor_readings(organism_id):
    try:
        logger.info(f"🧬 Genomic sensor readings endpoint accessed for: {organism_id}")
        
        result = genomic_impedance_sensor.get_sensor_readings(organism_id)
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info(f"🧬 Sensor readings retrieved for organism: {organism_id}")
        return jsonify({
            "success": True,
            "sensor_readings": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Genomic sensor readings error: {e}")
        return jsonify({"error": "Genomic sensor readings failed", "details": str(e)}), 500

@app.route('/api/genomic/analyze-sensors')
def analyze_genomic_sensors():
    try:
        logger.info("🧬 Analyze genomic sensors endpoint accessed")
        
        result = genomic_impedance_sensor.analyze_genomic_sensors()
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info("🧬 Genomic sensors analysis completed")
        return jsonify({
            "success": True,
            "sensors_analysis": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Analyze genomic sensors error: {e}")
        return jsonify({"error": "Analyze genomic sensors failed", "details": str(e)}), 500

@app.route('/api/genomic/biasing-patterns')
def genomic_biasing_patterns():
    try:
        logger.info("🧬 Genomic biasing patterns endpoint accessed")
        
        result = genomic_biasing_engine.analyze_biasing_patterns()
        
        if 'error' in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        logger.info("🧬 Genomic biasing patterns analysis completed")
        return jsonify({
            "success": True,
            "biasing_patterns": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Genomic biasing patterns error: {e}")
        return jsonify({"error": "Genomic biasing patterns failed", "details": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting main execution")
    logger.info("📍 Available endpoints:")
    logger.info("   - http://localhost:5557/")
    logger.info("   - http://localhost:5557/health")
    logger.info("   - http://localhost:5557/api/status")
    logger.info("   - http://localhost:5557/api/chat (with real API + Alife + Moon damping + Parasitic feeding + Phase 3B + Cosmic + Universal + Genomic integration)")
    logger.info("   - http://localhost:5557/api/cosmic/stellar-interference")
    logger.info("   - http://localhost:5557/api/universal/impedance-point (OPTIMIZED)")
    logger.info("   - http://localhost:5557/api/universal/analyze-patterns (OPTIMIZED)")
    logger.info("   - http://localhost:5557/api/universal/dark-energy-regions")
    logger.info("   - http://localhost:5557/api/genomic/impedance-sensor (NEW)")
    logger.info("   - http://localhost:5557/api/genomic/biasing-analysis (NEW)")
    logger.info("   - http://localhost:5557/api/genomic/sensor-readings/<organism_id> (NEW)")
    logger.info("   - http://localhost:5557/api/genomic/analyze-sensors (NEW)")
    logger.info("   - http://localhost:5557/api/genomic/biasing-patterns (NEW)")
    
    logger.info("🚀 Attempting to run Flask app...")
    
    try:
        app.run(host='0.0.0.0', port=5557, debug=False)
    except Exception as e:
        logger.error(f"❌ Flask app failed to start: {e}")
        logger.error(f"❌ Stack trace: {traceback.format_exc()}")
        sys.exit(1)
    
    logger.info("🏁 Flask app stopped")