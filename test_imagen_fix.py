#!/usr/bin/env python3
"""
Quick test to verify Imagen 3 image generation fix
==================================================

This script tests that the real Imagen images are now being used
instead of placeholders.
"""

import asyncio
import base64
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.agents.diagram_utils.ai_visual_engine import AIVisualDiagramEngine
from src.agents.content_agent_v7 import DiagramContentV4

async def test_imagen_generation():
    """Test that real Imagen images are generated."""
    print("Testing Imagen 3 Fix...")
    print("="*50)
    
    # Create a simple diagram request
    content = DiagramContentV4(
        pattern="concept_map",
        core_elements=[
            {"id": "center", "label": "AI", "type": "central"},
            {"id": "ml", "label": "Machine Learning", "type": "branch"},
            {"id": "dl", "label": "Deep Learning", "type": "branch"}
        ],
        relationships=[
            {"from": "center", "to": "ml", "type": "includes"},
            {"from": "ml", "to": "dl", "type": "subset"}
        ],
        flow_direction="radial",
        visual_hierarchy=["center"]
    )
    
    # Create theme
    theme = {
        "colors": {
            "primary": "#2563eb",
            "secondary": "#64748b"
        }
    }
    
    # Create AI visual engine
    engine = AIVisualDiagramEngine()
    
    # Generate diagram
    print("Generating diagram...")
    result = await engine.generate_ai_diagram(
        diagram_type="honeycomb",
        content={
            "labels": ["AI", "ML", "DL"],
            "cell_count": 3
        },
        theme=theme,
        constraints={"aspect_ratio": "16:9"}
    )
    
    print(f"✅ Generation complete!")
    print(f"   Has image: {bool(result.image_base64)}")
    
    if result.image_base64:
        # Check if it's a real image or placeholder
        try:
            # Decode first part to check content
            partial = base64.b64decode(result.image_base64[:1000])
            
            # Save for inspection
            test_file = Path("test_imagen_output.png")
            image_data = base64.b64decode(result.image_base64)
            test_file.write_bytes(image_data)
            
            print(f"   Image size: {len(image_data)} bytes")
            print(f"   Saved to: {test_file}")
            
            # Check if it's likely a placeholder (small size)
            if len(image_data) < 10000:
                print("   ⚠️  WARNING: Image is suspiciously small (might be placeholder)")
            else:
                print("   ✅ Image size indicates real Imagen generation!")
                
        except Exception as e:
            print(f"   Error decoding: {e}")
    
    print("="*50)
    print("Test complete! Check test_imagen_output.png")
    
if __name__ == "__main__":
    asyncio.run(test_imagen_generation())