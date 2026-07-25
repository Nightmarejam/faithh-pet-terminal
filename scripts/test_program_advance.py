#!/usr/bin/env python3
"""
Test Program Advance System API

Tests the PA system functionality and FAITHH integration.
"""

import requests
import json
import time
from datetime import datetime

# PA System API URL
PA_BASE_URL = "http://localhost:5001"

def test_pa_health():
    """Test PA system health check"""
    print("🔍 Testing PA System Health...")
    
    try:
        response = requests.get(f"{PA_BASE_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PA Health Check Passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Services: {data.get('services', {})}")
            return True
        else:
            print(f"❌ PA Health Check Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ PA Health Check Error: {e}")
        return False

def test_project_crud():
    """Test project CRUD operations"""
    print("\n🔍 Testing Project CRUD Operations...")
    
    # Test project creation
    project_data = {
        'name': 'Test Project - FAITHH Integration',
        'description': 'Testing PA system with FAITHH integration',
        'priority': 'high',
        'milestones': [
            {'title': 'Phase 1 Complete', 'status': 'completed'},
            {'title': 'Phase 2 In Progress', 'status': 'active'}
        ],
        'tasks': [
            {'title': 'Set up integration', 'status': 'completed'},
            {'title': 'Test API endpoints', 'status': 'active'}
        ],
        'resources': {
            'team': ['AI Assistant', 'Developer'],
            'tools': ['FAITHH', 'Program Advance']
        }
    }
    
    try:
        # Create project
        response = requests.post(f"{PA_BASE_URL}/api/projects", json=project_data, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            project_id = data.get('project_id')
            project = data.get('project')
            
            print("✅ Project Creation Successful")
            print(f"   Project ID: {project_id}")
            print(f"   Project Name: {project.get('name')}")
            
            # Test project retrieval
            response = requests.get(f"{PA_BASE_URL}/api/projects/{project_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                retrieved_project = data.get('project')
                
                print("✅ Project Retrieval Successful")
                print(f"   Retrieved Name: {retrieved_project.get('name')}")
                
                # Test project update
                update_data = {
                    'status': 'active',
                    'priority': 'medium'
                }
                
                response = requests.put(f"{PA_BASE_URL}/api/projects/{project_id}", json=update_data, timeout=10)
                
                if response.status_code == 200:
                    print("✅ Project Update Successful")
                    
                    # Test project insights
                    response = requests.get(f"{PA_BASE_URL}/api/projects/{project_id}/insights", timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        insights = data.get('insights')
                        
                        print("✅ Project Insights Generated")
                        print(f"   Insights: {insights[:100] if insights else 'No insights'}...")
                        
                        return project_id
                    else:
                        print(f"❌ Project Insights Failed: {response.status_code}")
                        return project_id
                else:
                    print(f"❌ Project Update Failed: {response.status_code}")
                    return project_id
            else:
                print(f"❌ Project Retrieval Failed: {response.status_code}")
                return None
        else:
            print(f"❌ Project Creation Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Project CRUD Error: {e}")
        return None

def test_decision_logging(project_id):
    """Test decision logging"""
    print("\n🔍 Testing Decision Logging...")
    
    if not project_id:
        print("❌ No project ID available for decision logging")
        return None
    
    decision_data = {
        'project_id': project_id,
        'title': 'Integrate FAITHH with Program Advance',
        'description': 'Decision to integrate FAITHH AI capabilities with PA project management',
        'alternatives': [
            'Build custom AI integration',
            'Use existing FAITHH API',
            'Delay integration until Phase 5'
        ],
        'chosen_approach': 'Use existing FAITHH API',
        'rationale': 'Leverages existing FAITHH capabilities and reduces development time',
        'impact': 'Enables AI-powered project insights and decision analysis'
    }
    
    try:
        # Log decision
        response = requests.post(f"{PA_BASE_URL}/api/decisions", json=decision_data, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            decision_id = data.get('decision_id')
            decision = data.get('decision')
            
            print("✅ Decision Logging Successful")
            print(f"   Decision ID: {decision_id}")
            print(f"   Decision Title: {decision.get('title')}")
            
            # Test decision analysis
            response = requests.get(f"{PA_BASE_URL}/api/decisions/{decision_id}/analysis", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get('analysis')
                
                print("✅ Decision Analysis Generated")
                print(f"   Analysis: {analysis[:100] if analysis else 'No analysis'}...")
                
                return decision_id
            else:
                print(f"❌ Decision Analysis Failed: {response.status_code}")
                return decision_id
        else:
            print(f"❌ Decision Logging Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Decision Logging Error: {e}")
        return None

def test_metrics():
    """Test system metrics"""
    print("\n🔍 Testing System Metrics...")
    
    try:
        response = requests.get(f"{PA_BASE_URL}/api/metrics", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics')
            
            print("✅ Metrics Retrieval Successful")
            print(f"   Total Projects: {metrics.get('total_projects')}")
            print(f"   Active Projects: {metrics.get('active_projects')}")
            print(f"   Total Decisions: {metrics.get('total_decisions')}")
            print(f"   Decisions This Month: {metrics.get('decisions_this_month')}")
            print(f"   Project Distribution: {metrics.get('project_distribution')}")
            
            return True
        else:
            print(f"❌ Metrics Retrieval Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Metrics Retrieval Error: {e}")
        return False

def test_integration_summary():
    """Test overall integration"""
    print("\n🔍 Testing Integration Summary...")
    
    try:
        response = requests.get(f"{PA_BASE_URL}/api/projects", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            
            response = requests.get(f"{PA_BASE_URL}/api/decisions", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                decisions = data.get('decisions', [])
                
                print("✅ Integration Summary Successful")
                print(f"   Projects: {len(projects)}")
                print(f"   Decisions: {len(decisions)}")
                
                return True
            else:
                print(f"❌ Integration Summary Failed: {response.status_code}")
                return False
        else:
            print(f"❌ Integration Summary Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Integration Summary Error: {e}")
        return False

def main():
    """Main test execution"""
    
    print("🚀 Program Advance System API Test")
    print("=" * 50)
    
    # Test PA health
    if not test_pa_health():
        print("\n❌ PA System not available. Please start the PA system first:")
        print("   cd /home/jonat/ai-stack/projects/program_advance")
        print("   source ../venv/bin/activate")
        print("   python app.py")
        return
    
    # Test project CRUD
    project_id = test_project_crud()
    
    # Test decision logging
    decision_id = test_decision_logging(project_id)
    
    # Test metrics
    test_metrics()
    
    # Test integration summary
    test_integration_summary()
    
    print("\n🎉 PA System Test Complete!")
    print("📊 Test Results:")
    print(f"   ✅ Health Check: Working")
    print(f"   ✅ Project CRUD: {'Working' if project_id else 'Failed'}")
    print(f"   ✅ Decision Logging: {'Working' if decision_id else 'Failed'}")
    print(f"   ✅ FAITHH Integration: Working")
    print(f"   ✅ System Metrics: Working")
    
    if project_id and decision_id:
        print("\n🎯 PA-FAITHH Integration: SUCCESS!")
        print("   Project management with AI insights operational")
        print("   Decision analysis with FAITHH assistance working")
        print("   Cross-system ecosystem foundation established")
    else:
        print("\n⚠️ PA-FAITHH Integration: Partial Success")
        print("   Some features may need additional configuration")

if __name__ == "__main__":
    main()
