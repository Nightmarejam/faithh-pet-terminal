#!/usr/bin/env python3
"""
Test compass API response structure
"""

import requests
import json

def test_compass_endpoints():
    print("=== Testing Compass API Endpoints ===")
    
    # Test director endpoint
    try:
        response = requests.get('http://localhost:5557/api/compass/director')
        data = response.json()
        
        print(f"Director endpoint: {response.status_code}")
        print(f"Keys: {data.get('keys', list(data.keys()))}")
        print(f"Has attention_items: {'attention_items' in data}")
        print(f"Has suggested_actions: {'suggested_actions' in data}")
        print(f"Has collector_status: {'collector_status' in data}")
        print(f"Attention items count: {len(data.get('attention_items', []))}")
        print(f"Suggested actions count: {len(data.get('suggested_actions', []))}")
        
        # Check project structure
        projects = data.get('project_states', {}).get('projects', {})
        print(f"Projects type: {type(projects)}")
        print(f"Projects count: {len(projects)}")
        
        if projects:
            first_project = list(projects.values())[0]
            print(f"First project keys: {list(first_project.keys())}")
            print(f"Has next_steps: {'next_steps' in first_project}")
            print(f"Next steps count: {len(first_project.get('next_steps', []))}")
        
    except Exception as e:
        print(f"Director endpoint error: {e}")
    
    print()

if __name__ == "__main__":
    test_compass_endpoints()
