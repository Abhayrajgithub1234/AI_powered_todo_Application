#!/usr/bin/env python3
"""
List available Gemini models
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

print("🔍 Listing available models...")
try:
    models = genai.list_models()
    for model in models:
        print(f"Model: {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Supported methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"Error listing models: {e}")
    
    # Try the new model names
    print("\n🧪 Testing different model names...")
    model_names = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-pro'
    ]
    
    for model_name in model_names:
        try:
            print(f"\nTrying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            if response.text:
                print(f"✅ SUCCESS with {model_name}: {response.text[:50]}...")
                break
        except Exception as e:
            print(f"❌ Failed with {model_name}: {e}")
