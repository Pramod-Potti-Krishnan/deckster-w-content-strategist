#!/usr/bin/env python3
"""Test updated pyramid template with light colors and increased width."""

import sys
from pathlib import Path
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import xml.etree.ElementTree as ET
from pathlib import Path
from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import SVGTemplateSpec

def test_pyramid_updated():
    """Test the updated pyramid template."""
    
    agent = SVGDiagramAgent()
    template_path = Path(__file__).parent / "src/agents/diagram_utils/templates/pyramid_3_level.svg"
    output_dir = Path("test/diagram-tests/test_output/svg_templates_comprehensive")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test content
    content = {
        "elements": [
            {"label": "Strategic Vision and Leadership Excellence"},
            {"label": "Tactical Planning and Resource Management"},
            {"label": "Operational Excellence and Daily Execution"}
        ],
        "title": "Organizational Hierarchy"
    }
    
    themes = [
        {
            "name": "Default",
            "colors": {
                "primary": "#3b82f6",
                "secondary": "#10b981",
                "accent": "#f59e0b"
            }
        },
        {
            "name": "Dark Theme",
            "colors": {
                "primary": "#8b5cf6",
                "secondary": "#ec4899",
                "accent": "#06b6d4"
            }
        }
    ]
    
    for i, theme in enumerate(themes):
        print(f"\n=== Testing pyramid with {theme['name']} ===")
        
        # Extract theme colors
        theme_colors = agent._extract_theme_colors(theme)
        
        # Get color replacements - should return light colors
        color_replacements = agent._get_color_replacements("pyramid", theme_colors)
        print(f"Color replacements: {color_replacements}")
        
        # Extract text replacements
        text_replacements = agent._extract_text_from_content("pyramid", content)
        
        # Apply template
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        # Verify dimensions
        viewbox = root.get('viewBox')
        width = root.get('width')
        print(f"SVG dimensions: viewBox={viewbox}, width={width}")
        
        # Apply color replacements
        for element_id, color in color_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                elem.set('fill', color)
                elem.set('stroke', color)
        
        # Apply text replacements with wrapping
        for element_id, text in text_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                if '_text' in element_id and 'level_' in element_id:
                    # Text should always be black for pyramid
                    elem.set('fill', '#1e293b')
                    
                    # Apply text wrapping with new widths
                    max_width = agent._get_element_width(element_id)
                    lines = agent._wrap_text_for_svg(text, max_width, max_lines=2)
                    
                    print(f"  {element_id}: max_width={max_width}, lines={len(lines)}")
                    
                    if len(lines) > 1:
                        elem.text = None
                        for child in list(elem):
                            elem.remove(child)
                        
                        x = elem.get('x', '500')  # New center position
                        y = elem.get('y', '200')
                        y_offset = -((len(lines) - 1) * 10)
                        y_value = float(y) + y_offset
                        elem.set('y', str(y_value))
                        
                        for j, line in enumerate(lines):
                            tspan = ET.SubElement(elem, '{http://www.w3.org/2000/svg}tspan')
                            tspan.set('x', x)
                            tspan.set('dy', '0' if j == 0 else '1.2em')
                            tspan.text = line
                    else:
                        elem.text = text
                else:
                    elem.text = text
        
        # Save the result
        output_path = output_dir / f"pyramid_theme_{i}.svg"
        
        # Convert to string and clean namespaces
        svg_str = ET.tostring(root, encoding='unicode')
        svg_str = svg_str.replace('ns0:', '').replace('xmlns:ns0=', 'xmlns=')
        
        with open(output_path, 'w') as f:
            f.write(svg_str)
        
        print(f"Saved to: {output_path}")
        
        # Verify the output
        verify_tree = ET.parse(output_path)
        verify_root = verify_tree.getroot()
        print("\nVerifying output:")
        for level in [1, 2, 3]:
            fill_elem = verify_root.find(f".//*[@id='level_{level}_fill']")
            text_elem = verify_root.find(f".//*[@id='level_{level}_text']")
            if fill_elem is not None and text_elem is not None:
                print(f"  Level {level}: fill={fill_elem.get('fill')}, text_color={text_elem.get('fill')}")

if __name__ == "__main__":
    test_pyramid_updated()