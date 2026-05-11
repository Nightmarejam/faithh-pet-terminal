#!/usr/bin/env python3
"""Check available Groq models for reasoning and coding"""

import groq
import os

def check_groq_models():
    try:
        # Get API key from config or environment
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("❌ GROQ_API_KEY not found in environment")
            return
        
        client = groq.Groq(api_key=api_key)
        models = client.models.list()
        
        print("✅ Groq API connected")
        print("\n🧠 Reasoning & Coding Models:")
        
        reasoning_models = []
        coding_models = []
        mixtral_models = []
        
        for model in models.data:
            model_id = model.id
            if 'reasoning' in model_id.lower():
                reasoning_models.append(model_id)
            elif 'coder' in model_id.lower():
                coding_models.append(model_id)
            elif 'mixtral' in model_id.lower():
                mixtral_models.append(model_id)
        
        if reasoning_models:
            print(f"  Reasoning: {reasoning_models}")
        if coding_models:
            print(f"  Coding: {coding_models}")
        if mixtral_models:
            print(f"  Mixtral: {mixtral_models}")
        
        print(f"\n📋 All available models:")
        for model in models.data:
            print(f"  - {model.id}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_groq_models()
