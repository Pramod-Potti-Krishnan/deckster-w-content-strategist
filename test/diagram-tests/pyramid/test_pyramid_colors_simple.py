#!/usr/bin/env python3
"""Test pyramid color logic directly."""

import sys
from pathlib import Path
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.agents.diagram_utils.svg_agent import SVGDiagramAgent

def test_color_logic():
    """Test the color extraction and replacement logic."""
    agent = SVGDiagramAgent()
    
    # Test theme 1 - all colors defined
    theme1 = {
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#10b981",
            "accent": "#f59e0b",
            "background": "#ffffff",
            "text": "#1e293b"
        }
    }
    
    # Test theme 2 - missing accent
    theme2 = {
        "colors": {
            "primary": "#8b5cf6",
            "secondary": "#ec4899"
        }
    }
    
    print("=== Testing Theme 1 (all colors defined) ===")
    colors1 = agent._extract_theme_colors(theme1)
    print(f"Extracted colors: {colors1}")
    
    replacements1 = agent._get_color_replacements("pyramid", colors1)
    print(f"Pyramid color replacements: {replacements1}")
    print(f"  Level 1 (top): {replacements1.get('level_1_fill')}")
    print(f"  Level 2 (middle): {replacements1.get('level_2_fill')}")
    print(f"  Level 3 (bottom): {replacements1.get('level_3_fill')}")
    
    print("\n=== Testing Theme 2 (missing accent) ===")
    colors2 = agent._extract_theme_colors(theme2)
    print(f"Extracted colors: {colors2}")
    
    replacements2 = agent._get_color_replacements("pyramid", colors2)
    print(f"Pyramid color replacements: {replacements2}")
    print(f"  Level 1 (top): {replacements2.get('level_1_fill')}")
    print(f"  Level 2 (middle): {replacements2.get('level_2_fill')}")
    print(f"  Level 3 (bottom): {replacements2.get('level_3_fill')}")
    
    # Test text color logic
    print("\n=== Testing Text Color Logic ===")
    test_colors = [
        ("#3b82f6", "Blue (primary)"),
        ("#10b981", "Green (secondary)"),
        ("#f59e0b", "Orange (accent)"),
        ("#8b5cf6", "Purple"),
        ("#ffffff", "White"),
        ("#1e293b", "Dark"),
    ]
    
    for color, name in test_colors:
        text_color = agent._get_text_color_for_background(color)
        print(f"  Background {color} ({name}): text should be {text_color}")

if __name__ == "__main__":
    test_color_logic()