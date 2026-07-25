#!/usr/bin/env python3
"""
Simple Phase 3B Test
Debug the signature mapping issue
"""

import sys
import time
sys.path.append("/home/jonat/ai-stack")

from app.services import alife_parasitic_integration

def test_simple_mapping():
    """Test simple signature mapping"""
    print("🧪 Testing Phase 3B Simple Mapping...")
    
    # Load data first
    print("📊 Loading Alife data...")
    result = alife_parasitic_integration.load_alife_data()
    
    if not result.get("success"):
        print(f"❌ Data load failed: {result}")
        return
    
    print(f"✅ Data loaded: {result['total_events']} events")
    
    # Test signature calculation for first event only
    print("🔍 Testing single signature calculation...")
    
    if alife_parasitic_integration.alife_data:
        first_event = alife_parasitic_integration.alife_data[0]
        print(f"📝 First event type: {first_event.get('domain', 'unknown')}")
        
        try:
            signature = alife_parasitic_integration.calculate_parasitic_signature(first_event)
            print(f"✅ Signature calculated: {signature}")
            
            # Test mapping with just first event
            print("🗺️ Testing single event mapping...")
            alife_parasitic_integration.alife_data = [first_event]  # Only first event
            
            mapping_result = alife_parasitic_integration.map_parasitic_signatures()
            print(f"✅ Single mapping result: {mapping_result}")
            
        except Exception as e:
            print(f"❌ Signature calculation failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_simple_mapping()