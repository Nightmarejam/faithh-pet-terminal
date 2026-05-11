# API Documentation

**Generated**: 2026-03-27 17:45:00  
**Status**: ✅ Complete - All endpoints documented  
**Backend Version**: v4.0-pulse  
**Base URL**: http://localhost:5557

---

## 🌐 API Overview

The FAITHH backend provides a comprehensive REST API for AI interaction, genomic research, and system management. All endpoints return JSON responses and include appropriate error handling.

### Base URL
```
http://localhost:5557
```

### Authentication
Currently no authentication is required (single-user deployment).

### Response Format
```json
{
  "success": true,
  "data": {...},
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

---

## 🤖 Core AI Endpoints

### Chat Interface
**POST** `/api/chat`
Main endpoint for AI conversation and interaction.

**Request Body**:
```json
{
  "message": "What projects am I working on?",
  "context": "optional_context",
  "provider": "auto"
}
```

**Response**:
```json
{
  "success": true,
  "response": "Based on your project states, you're working on...",
  "provider": "ollama",
  "model": "qwen25-grounded:latest",
  "context_used": true,
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### RAG Search
**POST** `/api/search`
Search across indexed knowledge base.

**Request Body**:
```json
{
  "query": "genomic experiments",
  "n_results": 5,
  "filter": "recent"
}
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "id": "doc_123",
      "content": "Genomic experiment results...",
      "score": 0.95,
      "metadata": {...}
    }
  ],
  "total_found": 42,
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### System Status
**GET** `/api/status`
Get comprehensive system status and health information.

**Response**:
```json
{
  "success": true,
  "version": "v4.0-pulse",
  "uptime": "unknown",
  "services": {
    "chromadb": {
      "connected": true,
      "documents": 31771,
      "status": "online"
    },
    "ollama": {
      "models": ["qwen25-grounded:latest", "deepseek-r1:32b"],
      "status": "online"
    }
  },
  "workspace": {
    "uploaded_files": 21
  }
}
```

---

## 🧬 Genomic Research Endpoints

### Create Genomic Impedance Sensor
**POST** `/api/genomic/impedance-sensor`
Create a genomic impedance sensor for an organism.

**Request Body**:
```json
{
  "organism_id": "test_organism_001",
  "position": [1.0, 0.0, 0.0],
  "sensitivity": 0.7,
  "environmental_zone": "medium_impedance"
}
```

**Response**:
```json
{
  "success": true,
  "genomic_sensor": {
    "sensor_id": "test_organism_001_genomic_sensor",
    "organism_id": "test_organism_001",
    "position": [1.0, 0.0, 0.0],
    "sensitivity": 0.7,
    "biasing_potential": 0.148,
    "readings": {
      "internal_impedance": 50.99,
      "external_impedance": 102.51,
      "combined_impedance": 71.60
    },
    "detected_patterns": 1,
    "timestamp": 1774657558.99
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### Genomic Biasing Analysis
**POST** `/api/genomic/biasing-analysis`
Apply genomic biasing to DNA copying based on impedance patterns.

**Request Body**:
```json
{
  "organism_id": "test_organism_001",
  "original_genome": "ATGCGTACATGCGTACATGCGTACATGCGTACATGCGTACATGCGTAC",
  "biasing_strength": 0.7,
  "environmental_zone": "medium_impedance"
}
```

**Response**:
```json
{
  "success": true,
  "biasing_analysis": {
    "organism_id": "test_organism_001",
    "genomic_bias": {
      "mutation_rate_bias": 0.00035,
      "copying_fidelity_bias": 0.85679,
      "source_impedance": 71.60
    },
    "biasing_result": {
      "biased_genome_length": 24,
      "biasing_strength": 0.0537,
      "fidelity_score": 0.85679,
      "mutations_applied": 0,
      "expression_changes": {
        "cognitive_processing": 0.0148,
        "energy_processing": 0.0889,
        "environmental_sensing": 0.1037,
        "metabolic_genes": 0.1037,
        "stress_response": 0.1185
      }
    },
    "sensor_readings": {
      "biasing_potential": 0.148,
      "combined_impedance": 71.60
    }
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### Get Sensor Readings
**GET** `/api/genomic/sensor-readings/<organism_id>`
Get sensor readings for a specific organism.

**Response**:
```json
{
  "success": true,
  "sensor_readings": {
    "organism_id": "test_organism_001",
    "sensor_id": "test_organism_001_genomic_sensor",
    "readings": {
      "internal_impedance": 50.99,
      "external_impedance": 102.51,
      "combined_impedance": 71.60
    },
    "biasing_potential": 0.148,
    "detected_patterns": 1,
    "last_updated": "2026-03-27T17:45:00.000Z"
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### Analyze All Sensors
**GET** `/api/genomic/analyze-sensors`
Analyze all genomic sensors in the system.

**Response**:
```json
{
  "success": true,
  "sensors_analysis": {
    "total_sensors": 100,
    "avg_biasing_potential": 0.163,
    "high_biasing_count": 0,
    "low_biasing_count": 73,
    "environmental_zones": {
      "low_impedance": 33,
      "medium_impedance": 34,
      "high_impedance": 33
    },
    "detected_patterns": {
      "stellar": 12,
      "dark_energy": 8,
      "quantum": 15
    }
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### Get Biasing Patterns
**GET** `/api/genomic/biasing-patterns`
Analyze genomic biasing patterns across all organisms.

**Response**:
```json
{
  "success": true,
  "biasing_patterns": {
    "avg_mutation_rate": 0.00042,
    "avg_fidelity_score": 0.866,
    "avg_cognitive_enhancement": 0.016,
    "expression_trends": {
      "cognitive_processing": 0.0148,
      "energy_processing": 0.0889,
      "environmental_sensing": 0.1037,
      "metabolic_genes": 0.1037,
      "stress_response": 0.1185
    },
    "zone_analysis": {
      "low_impedance": {
        "avg_biasing": 0.089,
        "avg_cognitive": 0.012
      },
      "medium_impedance": {
        "avg_biasing": 0.156,
        "avg_cognitive": 0.018
      },
      "high_impedance": {
        "avg_biasing": 0.234,
        "avg_cognitive": 0.025
      }
    }
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

---

## 🔧 System Management Endpoints

### Health Check
**GET** `/health`
Basic health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-27T17:45:00.000Z",
  "version": "v4.0-pulse"
}
```

### Metrics
**GET** `/api/metrics`
Get detailed system metrics.

**Response**:
```json
{
  "success": true,
  "metrics": {
    "uptime": "unknown",
    "total_requests": 1234,
    "avg_response_time": 0.014,
    "cache_hit_rate": 0.82,
    "error_rate": 0.01,
    "memory_usage": 45.2,
    "cpu_usage": 12.3
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### Compass Refresh
**POST** `/api/compass/refresh`
Trigger collectors refresh and return updated status.

**Response**:
```json
{
  "success": true,
  "message": "Compass data refreshed",
  "data": {
    "total_projects": 3,
    "active_projects": 2,
    "last_updated": "2026-03-27T17:45:00.000Z"
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

---

## 📊 Data Management Endpoints

### Get Project States
**GET** `/api/projects/states`
Get current project states and priorities.

**Response**:
```json
{
  "success": true,
  "projects": {
    "FAITHH": {
      "status": "active",
      "phase": "Phase 6.0",
      "last_updated": "2026-03-27",
      "priorities": ["documentation", "genomic_research"]
    },
    "ALIFE": {
      "status": "active",
      "experiments_completed": 9,
      "current_focus": "cultural_evolution"
    }
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### Get Decision Log
**GET** `/api/decisions/recent`
Get recent decision log entries.

**Query Parameters**:
- `limit`: Number of recent entries (default: 10)

**Response**:
```json
{
  "success": true,
  "decisions": [
    {
      "id": "decision_123",
      "timestamp": "2026-03-27T17:45:00.000Z",
      "decision": "Implement genomic experiments enhancement",
      "rationale": "To improve research capabilities",
      "impact": "high",
      "context": "genomic research phase"
    }
  ],
  "total_count": 156,
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

---

## 🚨 Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "organism_id",
    "issue": "Required field missing"
  },
  "timestamp": "2026-03-27T17:45:00.000Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request data
- `GENOMIC_SERVICE_ERROR`: Genomic services unavailable
- `DATABASE_ERROR`: Database connection issue
- `INTERNAL_ERROR`: Server-side error

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable

---

## 🔌 Usage Examples

### Basic Chat Interaction
```bash
curl -X POST http://localhost:5557/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "What is the status of my genomic experiments?"}'
```

### Genomic Sensor Creation
```bash
curl -X POST http://localhost:5557/api/genomic/impedance-sensor \\
  -H "Content-Type: application/json" \\
  -d '{"organism_id": "test_001", "position": [1.0, 0.0, 0.0], "sensitivity": 0.7}'
```

### Genomic Biasing Analysis
```bash
curl -X POST http://localhost:5557/api/genomic/biasing-analysis \\
  -H "Content-Type: application/json" \\
  -d '{"organism_id": "test_001", "original_genome": "ATGCGTAC...", "biasing_strength": 0.7}'
```

### System Status Check
```bash
curl http://localhost:5557/api/status
```

---

## 📚 Integration Examples

### Python Client
```python
import requests
import json

class FAITHHClient:
    def __init__(self, base_url="http://localhost:5557"):
        self.base_url = base_url
    
    def chat(self, message, provider="auto"):
        """Send chat message to FAITHH"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"message": message, "provider": provider}
        )
        return response.json()
    
    def create_genomic_sensor(self, organism_id, position, sensitivity):
        """Create genomic sensor"""
        response = requests.post(
            f"{self.base_url}/api/genomic/impedance-sensor",
            json={
                "organism_id": organism_id,
                "position": position,
                "sensitivity": sensitivity
            }
        )
        return response.json()
    
    def get_status(self):
        """Get system status"""
        response = requests.get(f"{self.base_url}/api/status")
        return response.json()

# Usage
client = FAITHHClient()
response = client.chat("What projects am I working on?")
print(response["response"])
```

### JavaScript Client
```javascript
class FAITHHAPI {
    constructor(baseUrl = 'http://localhost:5557') {
        this.baseUrl = baseUrl;
    }
    
    async chat(message, provider = 'auto') {
        const response = await fetch(`${this.baseUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                provider: provider
            })
        });
        return response.json();
    }
    
    async createGenomicSensor(organismId, position, sensitivity) {
        const response = await fetch(`${this.baseUrl}/api/genomic/impedance-sensor`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                organism_id: organismId,
                position: position,
                sensitivity: sensitivity
            })
        });
        return response.json();
    }
}

// Usage
const api = new FAITHHAPI();
api.chat('What is the status of my genomic experiments?')
    .then(response => console.log(response.response));
```

---

## 🔄 Rate Limiting

### Current Limits
- **Chat Endpoint**: 60 requests per minute
- **Search Endpoint**: 30 requests per minute
- **Genomic Endpoints**: 20 requests per minute
- **System Endpoints**: 100 requests per minute

### Response Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 2026-03-27T18:00:00Z
```

---

## 📈 Monitoring & Debugging

### Request Logging
All requests are logged with:
- Timestamp
- Endpoint
- Method
- Response status
- Processing time
- User agent

### Debug Mode
Set `FAITHH_DEBUG=1` environment variable to enable:
- Detailed error messages
- Request/response logging
- Performance metrics
- Stack traces

### Health Monitoring
Regular health checks should monitor:
- `/health` endpoint availability
- Response times (< 2s for most endpoints)
- Error rates (< 1%)
- Memory usage (< 80%)

---

## 🛡 Security Considerations

### Current Security Measures
- Input validation and sanitization
- Rate limiting per endpoint
- SQL injection prevention
- XSS protection
- CORS configuration

### Recommendations
- Use HTTPS in production
- Implement API key authentication for multi-user deployment
- Regular security audits
- Keep dependencies updated

---

## 📝 Version History

### v4.0-pulse (Current)
- Added genomic research endpoints
- Enhanced performance monitoring
- Improved error handling
- Real-time health checks

### v3.1
- Added Program Advance system
- Enhanced RAG integration
- Improved context building

### v3.0
- Added ML chips integration
- Enhanced search capabilities
- Improved performance

---

## 📞 Support

### Troubleshooting
1. Check backend status: `curl http://localhost:5557/health`
2. Check logs: `tail -f backend.log`
3. Verify services: `docker-compose ps`
4. Restart backend: `./restart_backend.sh`

### Getting Help
- Check documentation: `/docs/consolidated/`
- Review logs: `/logs/`
- Check system status: `/api/status`

---

*Last Updated: 2026-03-27 17:45:00*  
*Backend Version: v4.0-pulse*  
*API Version: 1.0*