#!/usr/bin/env python3
"""Direct test of pyramid SVG generation without requiring agent."""

import sys
from pathlib import Path
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import xml.etree.ElementTree as ET
from pathlib import Path
from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import SVGTemplateSpec

def test_pyramid_direct():
    """Test pyramid generation directly."""
    
    agent = SVGDiagramAgent()
    template_path = Path(__file__).parent / "src/agents/diagram_utils/templates/pyramid_3_level.svg"
    
    # Test with different themes
    themes = [
        {
            "name": "Theme 1",
            "colors": {
                "primary": "#3b82f6",
                "secondary": "#10b981",
                "accent": "#f59e0b"
            }
        },
        {
            "name": "Theme 2",
            "colors": {
                "primary": "#8b5cf6",
                "secondary": "#ec4899",
                "accent": "#06b6d4"
            }
        }
    ]
    
    for i, theme in enumerate(themes):
        print(f"\n=== {theme['name']} ===")
        
        # Extract colors
        theme_colors = agent._extract_theme_colors(theme)
        print(f"Extracted colors: primary={theme_colors['primary']}, secondary={theme_colors['secondary']}, accent={theme_colors['accent']}")
        
        # Get color replacements
        color_replacements = agent._get_color_replacements("pyramid", theme_colors)
        print(f"Color replacements: {color_replacements}")
        
        # Create template spec
        text_replacements = {
            'level_1_text': 'Strategic Vision and Leadership Excellence',
            'level_2_text': 'Tactical Planning and Resource Management',
            'level_3_text': 'Operational Excellence and Daily Execution',
            'pyramid_title': 'Organizational Hierarchy'
        }
        
        spec = SVGTemplateSpec(
            template_name="pyramid_3_level.svg",
            text_replacements=text_replacements,
            color_replacements=color_replacements
        )
        
        # Apply the template manually
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        # Apply color replacements
        for element_id, color in color_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                old_color = elem.get('fill')
                elem.set('fill', color)
                elem.set('stroke', color)
                print(f"  {element_id}: {old_color} -> {color}")
        
        # Apply text replacements (with wrapping for level texts)
        for element_id, text in text_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                if '_text' in element_id and 'level_' in element_id:
                    # Apply text color based on background
                    level_num = element_id.replace('level_', '').replace('_text', '')
                    fill_elem = root.find(f".//*[@id='level_{level_num}_fill']")
                    if fill_elem is not None:
                        bg_color = fill_elem.get('fill', '#ffffff')
                        text_color = agent._get_text_color_for_background(bg_color)
                        elem.set('fill', text_color)
                        print(f"  {element_id} text color: {text_color} (bg: {bg_color})")
                    
                    # Apply text wrapping
                    max_width = agent._get_element_width(element_id)
                    lines = agent._wrap_text_for_svg(text, max_width, max_lines=2)
                    
                    if len(lines) > 1:
                        elem.text = None
                        for child in list(elem):
                            elem.remove(child)
                        
                        x = elem.get('x', '400')
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
        output_path = Path(f"test/diagram-tests/test_output/pyramid_direct_theme_{i+1}.svg")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(output_path, encoding='unicode', xml_declaration=False)
        print(f"Saved to: {output_path}")
        
        # Verify the colors in the output
        verify_tree = ET.parse(output_path)
        verify_root = verify_tree.getroot()
        print("\nVerifying colors in output:")
        for level in [1, 2, 3]:
            elem = verify_root.find(f".//*[@id='level_{level}_fill']")
            if elem is not None:
                print(f"  Level {level}: fill={elem.get('fill')}")

if __name__ == "__main__":
    test_pyramid_direct()