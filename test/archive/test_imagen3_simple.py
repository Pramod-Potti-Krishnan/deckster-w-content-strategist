#!/usr/bin/env python3
"""
Simple test to verify Imagen 3 integration is working
"""
import asyncio
import os
import sys
from pathlib import Path

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.content_agent.content_agent_v5 import (
    ImageContentV4, generate_image_with_imagen3
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_imagen3_simple():
    """Test Imagen 3 with a simple prompt"""
    
    print("\n=== Testing Imagen 3 Integration ===\n")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: API key not found in environment")
        print("Please set: export GOOGLE_API_KEY=your-api-key")
        print("Or: export GEMINI_API_KEY=your-api-key")
        return False
    else:
        print("✓ API key found")
    
    # Create a simple image specification
    image_spec = ImageContentV4(
        archetype="spot_illustration",
        primary_subject="stethoscope",
        art_direction={"style": "minimalist", "color": "blue"},
        mood_keywords=["professional", "clean", "modern"],
        composition_notes="Centered composition, simple design",
        imagen_prompt="A simple blue stethoscope icon, minimalist flat design style, centered on white background. Professional medical illustration, clean vector art style.",
        imagen_config={
            "aspectRatio": "1:1",
            "model": "imagen-3.0-generate-002",
            "safety_settings": "block_only_high",
            "person_generation": "allow_adult"
        }
    )
    
    print(f"\nPrompt: {image_spec.imagen_prompt}")
    print(f"Aspect Ratio: {image_spec.imagen_config['aspectRatio']}")
    
    print("\nCalling Imagen 3...")
    
    try:
        # Call Imagen 3
        result = await generate_image_with_imagen3(image_spec)
        
        if result["success"]:
            print("\n✅ SUCCESS! Image generated")
            print(f"Base64 length: {len(result['base64'])} characters")
            
            # Save the image
            output_dir = Path("test/generated_images")
            output_dir.mkdir(exist_ok=True)
            
            filename = "test_imagen3_stethoscope.png"
            filepath = output_dir / filename
            
            import base64
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(result["base64"]))
            
            print(f"Image saved to: {filepath}")
            print(f"\nMetadata: {result['metadata']}")
            
            return True
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_imagen3_variations():
    """Test different aspect ratios and styles"""
    
    print("\n\n=== Testing Different Aspect Ratios ===\n")
    
    test_cases = [
        {
            "name": "Square Icon",
            "prompt": "A modern healthcare app icon with a heart symbol, flat design, gradient from blue to teal",
            "aspect_ratio": "1:1"
        },
        {
            "name": "Wide Banner",
            "prompt": "A professional medical team in a modern hospital, bright and optimistic atmosphere",
            "aspect_ratio": "16:9"
        },
        {
            "name": "Portrait Photo",
            "prompt": "A friendly doctor with stethoscope, professional headshot style, warm lighting",
            "aspect_ratio": "3:4"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: {test['name']}")
        print(f"Aspect Ratio: {test['aspect_ratio']}")
        
        image_spec = ImageContentV4(
            archetype="test",
            primary_subject="test",
            art_direction={},
            mood_keywords=["professional"],
            composition_notes="Test image",
            imagen_prompt=test["prompt"],
            imagen_config={
                "aspectRatio": test["aspect_ratio"],
                "model": "imagen-3.0-generate-002",
                "safety_settings": "block_only_high",
                "person_generation": "allow_adult"
            }
        )
        
        try:
            result = await generate_image_with_imagen3(image_spec)
            
            if result["success"]:
                print("✅ Generated successfully")
                
                # Save image
                output_dir = Path("test/generated_images")
                output_dir.mkdir(exist_ok=True)
                
                filename = f"test_imagen3_{test['aspect_ratio'].replace(':', 'x')}_{i+1}.png"
                filepath = output_dir / filename
                
                import base64
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(result["base64"]))
                
                print(f"Saved to: {filepath}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all tests"""
    
    # Test basic functionality
    success = await test_imagen3_simple()
    
    if success:
        # Test variations only if basic test passes
        await test_imagen3_variations()
    
    print("\n=== Test Complete ===\n")

if __name__ == "__main__":
    asyncio.run(main())