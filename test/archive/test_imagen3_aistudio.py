#!/usr/bin/env python3
"""
Test Imagen 3 using Google AI Studio API (with API key)
"""
import os
import base64
import asyncio

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import google.generativeai as genai

def test_imagen3_ai_studio():
    """Test Imagen 3 via Google AI Studio API"""
    
    print("\n=== Testing Imagen 3 via Google AI Studio ===\n")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    print("✓ API key found")
    
    # Configure genai
    genai.configure(api_key=api_key)
    
    try:
        # List available models to see what's accessible
        print("\nChecking available models...")
        models = genai.list_models()
        
        imagen_models = []
        for model in models:
            if 'imagen' in model.name.lower() or 'image' in model.supported_generation_methods:
                imagen_models.append(model.name)
                print(f"  - {model.name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"    Methods: {model.supported_generation_methods}")
        
        if not imagen_models:
            print("\nNo Imagen models found via AI Studio API")
            print("This might mean:")
            print("1. Imagen 3 requires Vertex AI authentication")
            print("2. The API key doesn't have access to Imagen models")
            print("3. Imagen models use a different access pattern")
        
        # Try the imagen model anyway
        print("\n\nAttempting to use imagen-3.0-generate-002...")
        try:
            model = genai.GenerativeModel('imagen-3.0-generate-002')
            
            # Try with generation config for images
            generation_config = {
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            response = model.generate_content(
                "A simple blue circle on white background",
                generation_config=generation_config
            )
            
            print(f"Response type: {type(response)}")
            
            # Check response
            if hasattr(response, 'parts'):
                for part in response.parts:
                    print(f"Part type: {type(part)}")
                    if hasattr(part, 'inline_data'):
                        print("✅ Found inline data!")
                    if hasattr(part, 'text'):
                        print(f"Text response: {part.text[:200]}")
            
        except Exception as e:
            print(f"\n❌ Error accessing Imagen: {e}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_imagen3_ai_studio()