# User Guides

How-to guides and tutorials

---

## 🚀 Quick Start Guide

### System Setup
1. **Prerequisites**
   - Python 3.8+ installed
   - Docker and Docker Compose
   - Git for version control

2. **Environment Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd ai-stack
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Infrastructure Setup**
   ```bash
   # Start services
   docker-compose up -d
   
   # Verify services
   docker-compose ps
   ```

4. **Backend Setup**
   ```bash
   # Start backend
   ./restart_backend.sh
   
   # Verify health
   curl http://localhost:5557/health
   ```
### Basic Usage
### Chat Interface
Access the FAITHH interface at http://localhost:5557

### API Usage
```bash
# Chat with FAITHH
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What projects am I working on?"}'

# Search knowledge base
curl -X POST http://localhost:5557/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "genomic experiments", "n_results": 5}'

# Get system status
curl http://localhost:5557/api/status
```

### Context Features
- **Self-Awareness**: FAITHH knows about itself and your projects
- **Decision Tracking**: References past decisions with rationale
- **Project Awareness**: Understands current project states
- **Intent Detection**: Routes queries to appropriate tools
---

## 📚 Advanced Guides

### Genomic Experiments
### Overview
Phase 6 introduces genomic impedance reading, bridging environmental patterns with biological systems.

### Running Experiments
```bash
# Large-scale test
cd experiments/genomic
python3 genomic_large_scale_test.py

# Environmental adaptation
python3 environmental_adaptation_test.py

# Multi-generational evolution
python3 multi_generational_adaptation_fixed.py
```

### API Usage
```bash
# Create genomic sensor
curl -X POST http://localhost:5557/api/genomic/impedance-sensor \
  -H "Content-Type: application/json" \
  -d '{"organism_id": "test_organism", "position": [1.0, 0.0, 0.0], "sensitivity": 0.7}'

# Analyze biasing
curl -X POST http://localhost:5557/api/genomic/biasing-analysis \
  -H "Content-Type: application/json" \
  -d '{"organism_id": "test_organism", "original_genome": "ATGCGTACATGCGTAC", "biasing_strength": 0.7}'
```

### Understanding Results
- **Biasing Potential**: Environmental influence on genetic changes
- **Cognitive Enhancement**: Gene expression bias for cognitive functions
- **Evolutionary Success**: Multi-generational fitness improvements
### ALIFE Research
### Overview
ALIFE experiments investigate cultural evolution in artificial agents.

### Running Experiments
```bash
cd projects/alife
python3 experiments/exp9_complex_cultural_evolution.py
```

### Experiment Configuration
Edit `config.py` to modify parameters:
- Population size
- Environmental conditions
- Evolutionary pressures

### Understanding Results
- **Protocol Evolution**: How cultural protocols change over time
- **Social Specialization**: Emergence of specialized roles
- **Knowledge Accumulation**: Multi-generational learning
### Development
### Development Environment
- **IDE**: VS Code with FAITHH extension recommended
- **Testing**: Use `python -m pytest tests/`
- **Debugging**: Backend logs at `/tmp/backend_debug.log`

### Code Structure
```
backend/           # Backend modules
app/services/      # Service layer
experiments/       # Experiments
docs/             # Documentation
scripts/          # Utility scripts
```

### Contributing
1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests

---

## 🔧 Troubleshooting

### Common Issues
### Common Issues

#### Backend Not Starting
```bash
# Check if port is in use
lsof -i :5557

# Check logs
tail -f backend.log

# Restart backend
./restart_backend.sh
```

#### ChromaDB Connection Issues
```bash
# Check ChromaDB health
curl http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat

# Restart services
docker-compose restart chromadb
```

#### Memory Issues
```bash
# Check memory usage
free -h

# Restart backend if needed
./restart_backend.sh
```

#### Genomic Experiments Not Working
```bash
# Verify genomic endpoints
curl http://localhost:5557/api/genomic/impedance-sensor

# Check error logs
grep -i genomic backend.log
```

---

## 📞 Advanced Features

### Program Advance System
### Overview
Program Advance system provides strategic chip combinations for complex queries.

### Triggering Program Advance
Use specific phrases in your queries:
- "everything about..." → Full Recall
- "business status" → Business Review
- "where was I" → Context Recovery
- "why did we" → Decision Audit
- "project status" → Project Deep Dive

### Available Advances
- **Full Recall**: Maximum context assembly
- **Business Review**: Business-focused analysis
- **Context Recovery**: Timeline context recovery
- **Decision Audit**: Decision forensics with evidence
- **Project Deep Dive**: Multi-domain project analysis
### Coherence Arbiter
### Overview
Coherence Arbiter measures alignment between RAG retrieval and ML chip signals.

### Understanding Coherence Scores
- **High (0.6+)**: Strong alignment between sources
- **Medium (0.3-0.6)**: Moderate alignment
- **Low (<0.3)**: Weak alignment, may need clarification

### Coherence Indicators
- **Tier**: High/Medium/Low coherence level
- **Reasons**: Why coherence score is what it is
- **Suggestions**: Recommended actions for improvement

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
