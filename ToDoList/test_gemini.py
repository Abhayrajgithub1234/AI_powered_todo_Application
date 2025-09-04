#!/usr/bin/env python3
"""
Test script to verify Gemini API functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
except ImportError as e:
    print(f"✗ Failed to import google.generativeai: {e}")
    sys.exit(1)

# Get API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("✗ GOOGLE_API_KEY not found in environment variables")
    sys.exit(1)
else:
    print(f"✓ API key loaded: {api_key[:10]}...{api_key[-4:]}")

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    print("✓ Gemini API configured")
except Exception as e:
    print(f"✗ Failed to configure Gemini API: {e}")
    sys.exit(1)

# Test model creation
try:
    model = genai.GenerativeModel('gemini-pro')
    print("✓ Model created successfully")
except Exception as e:
    print(f"✗ Failed to create model: {e}")
    sys.exit(1)

# Test simple generation
try:
    print("\n🤖 Testing AI response...")
    response = model.generate_content("Hello! Can you respond with a simple greeting?")
    
    if response.text:
        print(f"✓ AI Response: {response.text}")
        print("\n✅ All tests passed! Gemini API is working correctly.")
    else:
        print("✗ AI response was empty")
        
except Exception as e:
    print(f"✗ Failed to generate content: {e}")
    print(f"   Error type: {type(e).__name__}")
    
    # Try to get more detailed error information
    if hasattr(e, 'details'):
        print(f"   Details: {e.details}")
    if hasattr(e, 'code'):
        print(f"   Code: {e.code}")
        
    print("\n❌ API test failed!")
