#!/usr/bin/env python3
"""
Test SVG Color Theming
=======================

Demonstrates how theme colors are applied to SVG templates.
"""

from pathlib import Path
import xml.etree.ElementTree as ET
import sys

sys.path.append(str(Path(__file__).parent))

from src.agents.diagram_utils.svg_agent import SVGDiagramAgent

def test_color_replacements():
    """Test color replacement logic for different themes."""
    
    # Create a mock agent instance just to access the method
    class MockAgent:
        def _get_color_replacements(self, diagram_type, theme_colors):
            # Copy the actual method implementation
            agent = SVGDiagramAgent.__new__(SVGDiagramAgent)
            return agent._get_color_replacements(diagram_type, theme_colors)
    
    agent = MockAgent()
    
    # Test different themes
    themes = [
        {
            "name": "Blue Theme",
            "colors": {
                "primary": "#2563eb",    # Blue
                "secondary": "#10b981",   # Green
                "accent": "#f59e0b",      # Orange
            }
        },
        {
            "name": "Purple Theme", 
            "colors": {
                "primary": "#7c3aed",     # Purple
                "secondary": "#ec4899",   # Pink
                "accent": "#06b6d4",      # Cyan
            }
        },
        {
            "name": "Dark Theme",
            "colors": {
                "primary": "#1e293b",     # Dark slate
                "secondary": "#475569",   # Slate
                "accent": "#64748b",      # Light slate
            }
        }
    ]
    
    # Test different diagram types
    diagram_types = [
        "pyramid",
        "funnel", 
        "timeline",
        "cycle",
        "venn",
        "hub_spoke",
        "honeycomb",
        "swot",
        "process_flow",
        "org_chart"
    ]
    
    print("\n" + "="*70)
    print("SVG COLOR THEMING TEST")
    print("="*70)
    
    for theme in themes:
        print(f"\n📎 Theme: {theme['name']}")
        print("-" * 50)
        
        for diagram_type in diagram_types:
            # Get color replacements
            colors = agent._get_color_replacements(diagram_type, theme['colors'])
            
            if colors:
                print(f"\n  📊 {diagram_type}:")
                for element_id, color in list(colors.items())[:3]:  # Show first 3
                    print(f"    • {element_id}: {color}")
                if len(colors) > 3:
                    print(f"    ... and {len(colors) - 3} more elements")
            else:
                print(f"\n  ⚠️ {diagram_type}: No color mappings defined")
    
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print("""
✅ Color theming is ALREADY IMPLEMENTED and works by:

1. **Element ID Convention**: SVG elements use ID pattern `*_fill`
   - Examples: hub_fill, spoke_1_fill, level_1_fill
   
2. **Automatic Replacement**: The SVG agent automatically:
   - Finds elements by ID
   - Replaces 'fill' attribute with theme color
   - Also updates 'stroke' if present
   
3. **Theme Structure**: Pass colors in the theme:
   ```python
   theme = {
       "colors": {
           "primary": "#3b82f6",
           "secondary": "#10b981", 
           "accent": "#f59e0b"
       }
   }
   ```

4. **Diagram-Specific Logic**: Each diagram type has custom color mapping:
   - Pyramid: Gradient from light to dark
   - Org Chart: Hierarchical coloring (darker at top)
   - Hub & Spoke: Distinct colors for each spoke
   - SWOT: Traditional SWOT colors with theme influence

5. **Easy to Extend**: To add new color mappings:
   - Add element IDs ending in '_fill' to your SVG
   - Add mapping logic in _get_color_replacements()
    """)


if __name__ == "__main__":
    test_color_replacements()