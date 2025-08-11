#!/usr/bin/env python3
"""Test pyramid color fixing."""

import sys
from pathlib import Path
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import asyncio
from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import DiagramSpec

async def test_pyramid_colors():
    """Test pyramid with different themes to ensure distinct colors."""
    agent = SVGDiagramAgent()
    
    # Theme with all colors defined
    theme1 = {
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#10b981",
            "accent": "#f59e0b",
            "background": "#ffffff",
            "text": "#1e293b"
        }
    }
    
    # Theme missing accent color (should get default)
    theme2 = {
        "colors": {
            "primary": "#8b5cf6",
            "secondary": "#ec4899"
        }
    }
    
    content = {
        "core_elements": [
            {"label": "Strategic Vision"},
            {"label": "Tactical Planning"},
            {"label": "Operational Excellence"}
        ],
        "title": "Test Pyramid"
    }
    
    for i, theme in enumerate([theme1, theme2]):
        print(f"\n=== Theme {i+1} ===")
        print(f"Theme colors: {theme['colors']}")
        
        spec = DiagramSpec(
            diagram_type="pyramid",
            content=content,
            theme=theme
        )
        
        # Get the color replacements that would be used
        theme_colors = agent._extract_theme_colors(theme)
        print(f"Extracted colors: {theme_colors}")
        
        color_replacements = agent._get_color_replacements("pyramid", theme_colors)
        print(f"Color replacements: {color_replacements}")
        
        # Test the actual generation
        try:
            result = await agent.generate(spec)
            
            # Parse the SVG to check actual colors
            import xml.etree.ElementTree as ET
            root = ET.fromstring(result.svg_content)
            
            for level in [1, 2, 3]:
                elem = root.find(f".//*[@id='level_{level}_fill']")
                if elem is not None:
                    fill_color = elem.get('fill')
                    print(f"Level {level} fill color: {fill_color}")
                    
                # Check text color too
                text_elem = root.find(f".//*[@id='level_{level}_text']")
                if text_elem is not None:
                    text_color = text_elem.get('fill')
                    print(f"Level {level} text color: {text_color}")
            
            # Save the output
            with open(f"test/diagram-tests/test_output/pyramid_colors_theme_{i+1}.svg", "w") as f:
                f.write(result.svg_content)
            print(f"Saved to test_output/pyramid_colors_theme_{i+1}.svg")
            
        except Exception as e:
            print(f"Error generating: {e}")

if __name__ == "__main__":
    asyncio.run(test_pyramid_colors())