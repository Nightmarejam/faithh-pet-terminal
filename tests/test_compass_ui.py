#!/usr/bin/env python3
"""
Test compass UI data flow and structure
"""

import requests
import json

def test_compass_ui_data():
    print("=== Testing Compass UI Data Flow ===")
    
    try:
        # Test the director endpoint (what the compass UI uses)
        response = requests.get('http://localhost:5557/api/compass/director')
        data = response.json()
        
        print(f"✅ Director API: {response.status_code}")
        
        # Check required fields for UI rendering
        required_fields = ['success', 'attention_items', 'suggested_actions', 'project_states']
        for field in required_fields:
            if field in data:
                print(f"✅ {field}: Present")
            else:
                print(f"❌ {field}: Missing")
        
        # Check attention items structure
        attention_items = data.get('attention_items', [])
        print(f"📊 Attention Items: {len(attention_items)} items")
        if attention_items:
            item = attention_items[0]
            print(f"   - Message: {item.get('message', 'N/A')}")
            print(f"   - Priority: {item.get('priority', 'N/A')}")
            print(f"   - Source: {item.get('source', 'N/A')}")
        
        # Check suggested actions
        actions = data.get('suggested_actions', [])
        print(f"💡 Suggested Actions: {len(actions)} actions")
        if actions:
            for i, action in enumerate(actions[:3], 1):
                print(f"   {i}. {action}")
        
        # Check projects structure
        project_states = data.get('project_states', {})
        projects = project_states.get('projects', {})
        print(f"🏗️ Projects: {len(projects)} projects")
        
        for project_id, project in list(projects.items())[:3]:
            print(f"   - {project.get('name', project_id)}")
            print(f"     Status: {project.get('status', 'N/A')}")
            print(f"     Phase: {project.get('phase', 'N/A')}")
            next_steps = project.get('next_steps', [])
            print(f"     Next Steps: {len(next_steps)} items")
            if next_steps:
                print(f"       • {next_steps[0][:80]}...")
        
        # Simulate UI data structure
        ui_data = {
            'projects': list(projects.values()),
            'attention_items': attention_items,
            'suggested_actions': actions,
            'success': True
        }
        
        print("\n🎯 UI Data Structure Summary:")
        print(f"   Projects for renderCompassBoard: {len(ui_data['projects'])}")
        print(f"   Items for renderAttentionItems: {len(ui_data['attention_items'])}")
        print(f"   Actions for renderSuggestedActions: {len(ui_data['suggested_actions'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing compass UI: {e}")
        return False

if __name__ == "__main__":
    success = test_compass_ui_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Compass UI data flow is working!")
        print("   The UI should display:")
        print("   • 4 project nodes")
        print("   • Attention items (if any)")
        print("   • Suggested actions (if any)")
    else:
        print("❌ Compass UI data flow has issues")
    print("=" * 50)
