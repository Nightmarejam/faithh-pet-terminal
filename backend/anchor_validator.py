"""
Anchor Validator - Phase 2 Coherence Arbiter Enhancement

Validates specific claims from canonical state files against actual system behavior.
This provides ground truth validation for coherence scoring.

Phase 2 Scope: Start with project_states.json FAITHH phase validation
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnchorValidator:
    """Validates claims against system state and behavior"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def load_project_states(self) -> Dict[str, Any]:
        """Load project states canonical file"""
        states_path = os.path.join(self.base_dir, 'project_states.json')
        try:
            with open(states_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load project_states.json: {e}")
            return {}
    
    def validate_faithh_phase(self, ml_chips=None, ml_chip_centroids=None) -> Dict[str, Any]:
        """
        Validate FAITHH project phase claim against actual system state
        
        Claim from project_states.json: "phase": "Phase 3 Active", "phase_status": "operational"
        
        Phase 3 Active means:
        - ML chips loaded and operational
        - ChromaDB with expected document count range (30K+ chunks)
        - PULSE reflection engine operational
        - Multi-provider LLM support
        
        Args:
            ml_chips: ML chips data (injected to avoid circular import)
            ml_chip_centroids: ML chip centroids data (injected to avoid circular import)
        """
        states = self.load_project_states()
        
        # Extract the claim
        faithh_project = states.get('projects', {}).get('FAITHH', {})
        claimed_phase = faithh_project.get('phase')
        claimed_status = faithh_project.get('phase_status')
        
        validation_result = {
            'claim_type': 'project_phase',
            'project': 'FAITHH',
            'claimed_phase': claimed_phase,
            'claimed_status': claimed_status,
            'validation_timestamp': datetime.now().isoformat(),
            'evidence': [],
            'validation_score': 0.0,
            'is_valid': False
        }
        
        # Weights: ML 30%, Chroma 30%, PULSE 25%, default_provider 7.5%, pulse_documented 7.5% = 100%
        WEIGHT_ML = 0.30
        WEIGHT_CHROMA = 0.30
        WEIGHT_PULSE = 0.25
        WEIGHT_DEFAULT_PROVIDER = 0.075
        WEIGHT_PULSE_DOCUMENTED = 0.075

        # Evidence 1: Check ML chips loaded (Phase 3 core feature)
        if ml_chips is not None and ml_chip_centroids is not None:
            if ml_chips and len(ml_chips) > 0 and ml_chip_centroids is not None:
                validation_result['evidence'].append({
                    'type': 'ml_chips_loaded',
                    'status': 'pass',
                    'details': f'ML chips loaded: {len(ml_chips)} chips, {ml_chip_centroids.shape} centroids'
                })
                validation_result['validation_score'] += WEIGHT_ML
            else:
                validation_result['evidence'].append({
                    'type': 'ml_chips_loaded',
                    'status': 'fail',
                    'details': 'ML chips not loaded or centroids missing'
                })
        else:
            validation_result['evidence'].append({
                'type': 'ml_chips_loaded',
                'status': 'fail',
                'details': 'ML chips data not provided (dependency injection)'
            })
        
        # Evidence 2: Check ChromaDB document count (Phase 3 scale requirement)
        try:
            import requests
            # Try multiple API endpoints as ChromaDB API may have changed
            count_endpoints = [
                'http://192.158.1.243:8000/api/v1/collections/faithh_knowledge_base/count',
                'http://192.158.1.243:8000/api/v2/collections/faithh_knowledge_base/count'
            ]
            
            doc_count = None
            api_error = None
            
            for endpoint in count_endpoints:
                try:
                    response = requests.get(endpoint, timeout=3)
                    if response.status_code == 200:
                        doc_count = response.json().get('count', 0)
                        break
                    elif response.status_code == 410 or response.status_code == 501:
                        api_error = f"API unimplemented: {endpoint}"
                        continue
                except Exception:
                    continue
            
            if doc_count is not None:
                if doc_count >= 30000:  # Phase 3 expects substantial document base
                    validation_result['evidence'].append({
                        'type': 'chromadb_scale',
                        'status': 'pass',
                        'details': f'ChromaDB has {doc_count:,} documents (Phase 3 scale)'
                    })
                    validation_result['validation_score'] += WEIGHT_CHROMA
                else:
                    validation_result['evidence'].append({
                        'type': 'chromadb_scale',
                        'status': 'fail',
                        'details': f'ChromaDB has {doc_count:,} documents (below Phase 3 scale of 30K+)'
                    })
            else:
                # API is unimplemented - use heartbeat as proxy for ChromaDB being operational
                heartbeat_response = requests.get('http://192.158.1.243:8000/api/v2/heartbeat', timeout=3)
                if heartbeat_response.status_code == 200:
                    validation_result['evidence'].append({
                        'type': 'chromadb_scale',
                        'status': 'partial',
                        'details': 'ChromaDB operational but count API unimplemented (API limitation)'
                    })
                    validation_result['validation_score'] += WEIGHT_CHROMA / 2  # Half points for operational
                else:
                    validation_result['evidence'].append({
                        'type': 'chromadb_scale',
                        'status': 'fail',
                        'details': f'ChromaDB not accessible: {api_error or "Unknown error"}'
                    })
                    
        except Exception as e:
            validation_result['evidence'].append({
                'type': 'chromadb_scale',
                'status': 'fail',
                'details': f'Failed to check ChromaDB scale: {e}'
            })
        
        # Evidence 3: Check PULSE reflection engine (Phase 3 advanced feature)
        try:
            pulse_tracker_path = os.path.join(self.base_dir, 'pulse_pattern_tracker.py')
            if os.path.exists(pulse_tracker_path):
                validation_result['evidence'].append({
                    'type': 'pulse_engine',
                    'status': 'pass',
                    'details': 'PULSE reflection engine files present'
                })
                validation_result['validation_score'] += WEIGHT_PULSE
            else:
                validation_result['evidence'].append({
                    'type': 'pulse_engine',
                    'status': 'fail',
                    'details': 'PULSE reflection engine files missing'
                })
        except Exception as e:
            validation_result['evidence'].append({
                'type': 'pulse_engine',
                'status': 'fail',
                'details': f'Failed to check PULSE engine: {e}'
            })

        # Evidence 4 (Phase 3 expansion): Default provider decision recorded and implemented
        try:
            decisions_path = os.path.join(self.base_dir, 'decisions_log.json')
            if os.path.exists(decisions_path):
                with open(decisions_path, 'r') as f:
                    decisions_data = json.load(f)
                decisions = decisions_data.get('decisions', [])
                found = False
                for d in decisions:
                    if d.get('project') != 'faithh':
                        continue
                    status = (d.get('status') or '').lower()
                    text = (d.get('decision', '') + ' ' + d.get('id', '')).lower()
                    if ('default' in text or 'groq' in text or 'provider' in text) and status in ('implemented', 'implemented_phase1', 'implemented_phase2'):
                        found = True
                        break
                if found:
                    validation_result['evidence'].append({
                        'type': 'default_provider_decision',
                        'status': 'pass',
                        'details': 'Default LLM provider decision recorded and implemented in decisions_log'
                    })
                    validation_result['validation_score'] += WEIGHT_DEFAULT_PROVIDER
                else:
                    validation_result['evidence'].append({
                        'type': 'default_provider_decision',
                        'status': 'fail',
                        'details': 'No implemented default provider decision found in decisions_log'
                    })
            else:
                validation_result['evidence'].append({
                    'type': 'default_provider_decision',
                    'status': 'fail',
                    'details': 'decisions_log.json not found'
                })
        except Exception as e:
            validation_result['evidence'].append({
                'type': 'default_provider_decision',
                'status': 'fail',
                'details': f'Failed to check decisions_log: {e}'
            })

        # Evidence 5 (Phase 3 expansion): PULSE status documented in project state
        try:
            faithh_str = json.dumps(states.get('projects', {}).get('FAITHH', {}))
            if 'pulse' in faithh_str.lower() or 'reflection' in faithh_str.lower():
                validation_result['evidence'].append({
                    'type': 'pulse_documented',
                    'status': 'pass',
                    'details': 'PULSE/reflection mentioned in project_states.json FAITHH section'
                })
                validation_result['validation_score'] += WEIGHT_PULSE_DOCUMENTED
            else:
                # Optional: check strategic_plan or last_updated as proxy for state freshness
                validation_result['evidence'].append({
                    'type': 'pulse_documented',
                    'status': 'skip',
                    'details': 'PULSE not explicitly in FAITHH state; optional evidence'
                })
        except Exception as e:
            validation_result['evidence'].append({
                'type': 'pulse_documented',
                'status': 'fail',
                'details': f'Failed to check project state: {e}'
            })

        # Cap score at 1.0 and determine validity (score >= 0.7 = valid)
        validation_result['validation_score'] = min(1.0, validation_result['validation_score'])
        validation_result['is_valid'] = validation_result['validation_score'] >= 0.7
        
        return validation_result
    
    def validate_single_claim(self, claim_path: str) -> Dict[str, Any]:
        """
        Validate a single claim identified by path
        
        Args:
            claim_path: Dot notation path like "projects.FAITHH.phase"
        """
        # For now, just support FAITHH phase validation
        if claim_path == "projects.FAITHH.phase":
            return self.validate_faithh_phase()
        else:
            return {
                'claim_type': 'unsupported',
                'claim_path': claim_path,
                'error': f'Claim path {claim_path} not yet supported in Phase 2'
            }
