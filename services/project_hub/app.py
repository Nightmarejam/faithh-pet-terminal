"""
Program Advance System - Project Management & Decision Tracking

Integrated with FAITHH for AI-powered project assistance and decision support.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from flask import Flask, request, jsonify, g

app = Flask(__name__)

# Configuration (service-local data under services/project_hub/data/)
_SERVICE_ROOT = Path(__file__).resolve().parent
FAITHH_BACKEND_URL = os.environ.get("FAITHH_BACKEND_URL", "http://localhost:5557")
PA_DATA_PATH = _SERVICE_ROOT / "data"

# Ensure data directory exists
PA_DATA_PATH.mkdir(parents=True, exist_ok=True)

# Data file paths
PROJECTS_FILE = PA_DATA_PATH / "projects.json"
DECISIONS_FILE = PA_DATA_PATH / "decisions.json"
METRICS_FILE = PA_DATA_PATH / "metrics.json"

class ProjectManager:
    """Manages project data and operations"""
    
    def __init__(self):
        self.projects_file = PROJECTS_FILE
        self.load_projects()
    
    def load_projects(self):
        """Load projects from JSON file"""
        if self.projects_file.exists():
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
        else:
            self.projects = {}
            self.save_projects()
    
    def save_projects(self):
        """Save projects to JSON file"""
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    def create_project(self, project_data: Dict) -> str:
        """Create a new project"""
        project_id = f"project_{len(self.projects) + 1}"
        
        project = {
            'id': project_id,
            'name': project_data.get('name', ''),
            'description': project_data.get('description', ''),
            'status': 'active',
            'priority': project_data.get('priority', 'medium'),
            'created_date': datetime.now().isoformat(),
            'updated_date': datetime.now().isoformat(),
            'milestones': project_data.get('milestones', []),
            'tasks': project_data.get('tasks', []),
            'resources': project_data.get('resources', {}),
            'metrics': {}
        }
        
        self.projects[project_id] = project
        self.save_projects()
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    def update_project(self, project_id: str, updates: Dict) -> bool:
        """Update project"""
        if project_id in self.projects:
            self.projects[project_id].update(updates)
            self.projects[project_id]['updated_date'] = datetime.now().isoformat()
            self.save_projects()
            return True
        return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        if project_id in self.projects:
            del self.projects[project_id]
            self.save_projects()
            return True
        return False
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        return list(self.projects.values())

class DecisionManager:
    """Manages decision data and operations"""
    
    def __init__(self):
        self.decisions_file = DECISIONS_FILE
        self.load_decisions()
    
    def load_decisions(self):
        """Load decisions from JSON file"""
        if self.decisions_file.exists():
            with open(self.decisions_file, 'r') as f:
                self.decisions = json.load(f)
        else:
            self.decisions = {}
            self.save_decisions()
    
    def save_decisions(self):
        """Save decisions to JSON file"""
        with open(self.decisions_file, 'w') as f:
            json.dump(self.decisions, f, indent=2)
    
    def log_decision(self, decision_data: Dict) -> str:
        """Log a new decision"""
        decision_id = f"decision_{len(self.decisions) + 1}"
        
        decision = {
            'id': decision_id,
            'project_id': decision_data.get('project_id', ''),
            'title': decision_data.get('title', ''),
            'description': decision_data.get('description', ''),
            'alternatives': decision_data.get('alternatives', []),
            'chosen_approach': decision_data.get('chosen_approach', ''),
            'rationale': decision_data.get('rationale', ''),
            'impact': decision_data.get('impact', ''),
            'date': datetime.now().isoformat(),
            'outcome': decision_data.get('outcome', '')
        }
        
        self.decisions[decision_id] = decision
        self.save_decisions()
        return decision_id
    
    def get_decision(self, decision_id: str) -> Optional[Dict]:
        """Get decision by ID"""
        return self.decisions.get(decision_id)
    
    def list_decisions(self, project_id: Optional[str] = None) -> List[Dict]:
        """List decisions, optionally filtered by project"""
        decisions = list(self.decisions.values())
        if project_id:
            decisions = [d for d in decisions if d.get('project_id') == project_id]
        return decisions

class FAITHHIntegration:
    """Handles integration with FAITHH backend"""
    
    def __init__(self):
        self.backend_url = FAITHH_BACKEND_URL
    
    def query_faithh(self, message: str) -> Optional[Dict]:
        """Query FAITHH backend"""
        try:
            payload = {
                "message": message,
                "model": "qwen25-grounded:latest"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'response': data.get('response', ''),
                        'model_used': data.get('model_used', ''),
                        'provider': data.get('provider', '')
                    }
            
            return {'success': False, 'error': 'FAITHH query failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'Exception: {str(e)}'}
    
    def get_project_insights(self, project: Dict) -> Optional[str]:
        """Get AI insights for a project"""
        context = f"""
        Project Analysis Request:
        Name: {project.get('name', 'Unknown')}
        Status: {project.get('status', 'Unknown')}
        Priority: {project.get('priority', 'Unknown')}
        Description: {project.get('description', 'No description')}
        Milestones: {len(project.get('milestones', []))} milestones
        Tasks: {len(project.get('tasks', []))} tasks
        
        Please provide insights on this project's progress, potential risks, and recommendations.
        """
        
        result = self.query_faithh(context)
        return result.get('response') if result.get('success') else None
    
    def analyze_decision(self, decision: Dict) -> Optional[str]:
        """Analyze a decision with FAITHH"""
        context = f"""
        Decision Analysis Request:
        Title: {decision.get('title', 'Unknown')}
        Description: {decision.get('description', 'No description')}
        Chosen Approach: {decision.get('chosen_approach', 'Unknown')}
        Rationale: {decision.get('rationale', 'No rationale')}
        Impact: {decision.get('impact', 'Unknown impact')}
        
        Please analyze this decision for potential outcomes, risks, and implementation considerations.
        """
        
        result = self.query_faithh(context)
        return result.get('response') if result.get('success') else None

# Initialize managers
project_manager = ProjectManager()
decision_manager = DecisionManager()
faithh_integration = FAITHHIntegration()

# API Endpoints

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    projects = project_manager.list_projects()
    return jsonify({
        'success': True,
        'projects': projects,
        'count': len(projects)
    })

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No project data provided'
        }), 400
    
    project_id = project_manager.create_project(data)
    project = project_manager.get_project(project_id)
    
    return jsonify({
        'success': True,
        'project': project,
        'project_id': project_id
    }), 201

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get project details"""
    project = project_manager.get_project(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    return jsonify({
        'success': True,
        'project': project
    })

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update project"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No update data provided'
        }), 400
    
    success = project_manager.update_project(project_id, data)
    
    if not success:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    project = project_manager.get_project(project_id)
    
    return jsonify({
        'success': True,
        'project': project
    })

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete project"""
    success = project_manager.delete_project(project_id)
    
    if not success:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    return jsonify({
        'success': True,
        'message': 'Project deleted successfully'
    })

@app.route('/api/decisions', methods=['GET'])
def list_decisions():
    """List all decisions"""
    project_id = request.args.get('project_id')
    decisions = decision_manager.list_decisions(project_id)
    
    return jsonify({
        'success': True,
        'decisions': decisions,
        'count': len(decisions)
    })

@app.route('/api/decisions', methods=['POST'])
def log_decision():
    """Log a new decision"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No decision data provided'
        }), 400
    
    decision_id = decision_manager.log_decision(data)
    decision = decision_manager.get_decision(decision_id)
    
    return jsonify({
        'success': True,
        'decision': decision,
        'decision_id': decision_id
    }), 201

@app.route('/api/decisions/<decision_id>', methods=['GET'])
def get_decision(decision_id):
    """Get decision details"""
    decision = decision_manager.get_decision(decision_id)
    
    if not decision:
        return jsonify({
            'success': False,
            'error': 'Decision not found'
        }), 404
    
    return jsonify({
        'success': True,
        'decision': decision
    })

@app.route('/api/projects/<project_id>/insights', methods=['GET'])
def get_project_insights(project_id):
    """Get AI insights for a project"""
    project = project_manager.get_project(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    insights = faithh_integration.get_project_insights(project)
    
    return jsonify({
        'success': True,
        'project_id': project_id,
        'insights': insights,
        'generated_at': datetime.now().isoformat()
    })

@app.route('/api/decisions/<decision_id>/analysis', methods=['GET'])
def analyze_decision(decision_id):
    """Analyze a decision with FAITHH"""
    decision = decision_manager.get_decision(decision_id)
    
    if not decision:
        return jsonify({
            'success': False,
            'error': 'Decision not found'
        }), 404
    
    analysis = faithh_integration.analyze_decision(decision)
    
    return jsonify({
        'success': True,
        'decision_id': decision_id,
        'analysis': analysis,
        'analyzed_at': datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'project_manager': 'operational',
            'decision_manager': 'operational',
            'faithh_integration': 'connected' if faithh_integration.query_faithh('health check') else 'disconnected'
        }
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    projects = project_manager.list_projects()
    decisions = decision_manager.list_decisions()
    
    metrics = {
        'total_projects': len(projects),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'total_decisions': len(decisions),
        'decisions_this_month': len([d for d in decisions if d.get('date', '').startswith('2026-03')]),
        'project_distribution': {
            'high': len([p for p in projects if p.get('priority') == 'high']),
            'medium': len([p for p in projects if p.get('priority') == 'medium']),
            'low': len([p for p in projects if p.get('priority') == 'low'])
        }
    }
    
    return jsonify({
        'success': True,
        'metrics': metrics,
        'generated_at': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Program Advance System Starting...")
    print(f"📊 Data directory: {PA_DATA_PATH}")
    print(f"🤖 FAITHH integration: {FAITHH_BACKEND_URL}")
    print("🌐 API available at: http://localhost:5001")
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True)
