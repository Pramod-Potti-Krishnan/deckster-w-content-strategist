#!/usr/bin/env python3
"""
Test script to verify background removal functionality for different image archetypes
"""
import asyncio
import os
import sys
from pathlib import Path
import base64
from PIL import Image
from io import BytesIO

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.content_agent.content_agent_v5 import (
    ImageContentV4, generate_image_with_imagen3
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_background_removal():
    """Test background removal for different archetype types"""
    
    print("\n=== Testing Background Removal for Different Archetypes ===\n")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: API key not found in environment")
        return False
    
    print("✓ API key found\n")
    
    # Test cases for different archetypes that should have background removal
    test_cases = [
        {
            "name": "Minimalist Vector Art",
            "spec": ImageContentV4(
                archetype="minimalist_vector_art",
                primary_subject="heart health icon",
                art_direction={"style": "minimalist", "color": "red and blue"},
                mood_keywords=["clean", "modern", "medical"],
                composition_notes="Simple heart icon with pulse line",
                imagen_prompt="A minimalist heart icon with ECG pulse line, flat vector design style. Simple geometric shapes with red heart and blue pulse line. Centered on pure white background. Clean, modern medical iconography.",
                imagen_config={
                    "aspectRatio": "1:1",
                    "model": "imagen-3.0-generate-002",
                    "safety_settings": "block_only_high",
                    "person_generation": "allow_adult"
                }
            )
        },
        {
            "name": "Symbolic Representation",
            "spec": ImageContentV4(
                archetype="symbolic_representation",
                primary_subject="teamwork concept",
                art_direction={"style": "abstract", "color": "blue gradient"},
                mood_keywords=["collaborative", "dynamic", "professional"],
                composition_notes="Interconnected circles representing team unity",
                imagen_prompt="Abstract geometric design of interconnected circles symbolizing teamwork. Blue gradient colors from light to dark. Clean, modern corporate art style on white background. Professional symbolic representation.",
                imagen_config={
                    "aspectRatio": "16:9",
                    "model": "imagen-3.0-generate-002",
                    "safety_settings": "block_only_high",
                    "person_generation": "allow_adult"
                }
            )
        },
        {
            "name": "Regular Illustration (No Removal)",
            "spec": ImageContentV4(
                archetype="spot_illustration",
                primary_subject="office environment",
                art_direction={"style": "illustrative", "color": "warm colors"},
                mood_keywords=["welcoming", "professional", "modern"],
                composition_notes="Modern office space with people working",
                imagen_prompt="Colorful illustration of a modern office environment with people collaborating. Warm color palette with orange and yellow tones. Contemporary illustration style with full background scene.",
                imagen_config={
                    "aspectRatio": "16:9",
                    "model": "imagen-3.0-generate-002",
                    "safety_settings": "block_only_high",
                    "person_generation": "allow_adult"
                }
            )
        }
    ]
    
    # Create output directory
    output_dir = Path("test/generated_images/background_removal_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        print(f"Archetype: {test_case['spec'].archetype}")
        print(f"Should remove background: {'Yes' if test_case['spec'].archetype in ['minimalist_vector_art', 'symbolic_representation'] else 'No'}")
        
        try:
            # Generate image
            result = await generate_image_with_imagen3(test_case['spec'])
            
            if result["success"]:
                print("✅ Image generated successfully")
                
                # Save original image
                original_filename = f"test_{i+1}_{test_case['spec'].archetype}_original.png"
                original_path = output_dir / original_filename
                
                with open(original_path, "wb") as f:
                    f.write(base64.b64decode(result["base64"]))
                print(f"Original saved to: {original_path}")
                
                # Check for transparent version
                if result.get("has_transparent", False) and "transparent_base64" in result:
                    print("✅ Transparent version available")
                    
                    # Save transparent version
                    transparent_filename = f"test_{i+1}_{test_case['spec'].archetype}_transparent.png"
                    transparent_path = output_dir / transparent_filename
                    
                    with open(transparent_path, "wb") as f:
                        f.write(base64.b64decode(result["transparent_base64"]))
                    print(f"Transparent saved to: {transparent_path}")
                    
                    # Verify transparency
                    img = Image.open(transparent_path)
                    if img.mode == 'RGBA':
                        # Check if there are any transparent pixels
                        data = img.getdata()
                        transparent_pixels = sum(1 for pixel in data if pixel[3] < 255)
                        total_pixels = img.width * img.height
                        transparency_percentage = (transparent_pixels / total_pixels) * 100
                        
                        print(f"Transparency check: {transparency_percentage:.1f}% of pixels are transparent")
                        
                        if transparency_percentage > 10:
                            print("✅ Background removal successful")
                        else:
                            print("⚠️ Low transparency detected - background removal may not have worked properly")
                else:
                    if test_case['spec'].archetype in ['minimalist_vector_art', 'symbolic_representation']:
                        print("❌ Expected transparent version but none found")
                    else:
                        print("✓ No transparent version (as expected)")
                
                print(f"Metadata: {result['metadata']}")
                
            else:
                print(f"❌ Generation failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== Background Removal Test Complete ===\n")
    print("Check the generated images in: test/generated_images/background_removal_tests/")
    print("Compare original vs transparent versions to verify background removal quality")
    
    return True

async def test_edge_cases():
    """Test edge cases for background removal"""
    
    print("\n\n=== Testing Edge Cases ===\n")
    
    edge_cases = [
        {
            "name": "Complex Background",
            "spec": ImageContentV4(
                archetype="minimalist_vector_art",
                primary_subject="DNA helix",
                art_direction={"style": "scientific", "color": "blue and green"},
                mood_keywords=["technical", "precise", "modern"],
                composition_notes="DNA double helix structure",
                imagen_prompt="Scientific vector illustration of DNA double helix. Blue and green gradient colors. Technical line art style on white background. Clean, precise molecular visualization.",
                imagen_config={"aspectRatio": "3:4"}
            )
        },
        {
            "name": "Multiple Colors",
            "spec": ImageContentV4(
                archetype="symbolic_representation",
                primary_subject="growth chart",
                art_direction={"style": "business", "color": "multicolor"},
                mood_keywords=["growth", "success", "vibrant"],
                composition_notes="Ascending bar chart with arrow",
                imagen_prompt="Colorful bar chart showing growth trend with upward arrow. Multiple bright colors (red, blue, green, yellow). Business infographic style on white background. Clean vector graphics.",
                imagen_config={"aspectRatio": "16:9"}
            )
        }
    ]
    
    output_dir = Path("test/generated_images/background_removal_tests/edge_cases")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, test_case in enumerate(edge_cases):
        print(f"\nEdge Case {i+1}: {test_case['name']}")
        
        try:
            result = await generate_image_with_imagen3(test_case['spec'])
            
            if result["success"]:
                # Save both versions
                base_name = f"edge_{i+1}_{test_case['name'].lower().replace(' ', '_')}"
                
                # Original
                with open(output_dir / f"{base_name}_original.png", "wb") as f:
                    f.write(base64.b64decode(result["base64"]))
                
                # Transparent (if available)
                if result.get("has_transparent", False):
                    with open(output_dir / f"{base_name}_transparent.png", "wb") as f:
                        f.write(base64.b64decode(result["transparent_base64"]))
                    print("✅ Generated with transparent version")
                else:
                    print("❌ No transparent version generated")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n=== Edge Case Testing Complete ===")

async def main():
    """Run all tests"""
    
    # Test basic background removal
    success = await test_background_removal()
    
    if success:
        # Test edge cases
        await test_edge_cases()
    
    print("\n=== All Tests Complete ===\n")

if __name__ == "__main__":
    asyncio.run(main())