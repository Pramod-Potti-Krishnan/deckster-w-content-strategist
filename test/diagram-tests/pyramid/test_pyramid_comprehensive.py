#!/usr/bin/env python3
"""Test pyramid template with comprehensive fixes."""

import sys
from pathlib import Path
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import asyncio
from pathlib import Path
import xml.etree.ElementTree as ET
from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import DiagramSpec, SVGTemplateSpec

async def test_pyramid_comprehensive():
    """Test pyramid with all fixes applied."""
    
    agent = SVGDiagramAgent()
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
    
    # Test themes
    themes = [
        {
            "name": "Default",
            "colors": {
                "primary": "#3b82f6",
                "secondary": "#10b981",
                "accent": "#f59e0b",
                "background": "#ffffff",
                "text": "#1e293b"
            }
        },
        {
            "name": "Dark",
            "colors": {
                "primary": "#8b5cf6",
                "secondary": "#ec4899",
                "accent": "#06b6d4",
                "background": "#1e1e1e",
                "text": "#ffffff"
            }
        }
    ]
    
    for i, theme in enumerate(themes):
        print(f"\n=== Testing pyramid with {theme['name']} theme ===")
        
        # Create spec
        spec = DiagramSpec(
            diagram_type="pyramid",
            content=content,
            theme=theme
        )
        
        # Since we can't use the full agent without API keys, simulate the generation
        template_path = agent.template_base / "pyramid_3_level.svg"
        
        # Extract theme colors
        theme_colors = agent._extract_theme_colors(theme)
        print(f"Theme colors: {theme_colors}")
        
        # Get color replacements
        color_replacements = agent._get_color_replacements("pyramid", theme_colors)
        print(f"Color replacements: {color_replacements}")
        
        # Extract text replacements
        text_replacements = agent._extract_text_from_content("pyramid", content)
        print(f"Text replacements: {text_replacements}")
        
        # Create template spec
        template_spec = SVGTemplateSpec(
            template_name="pyramid_3_level.svg",
            text_replacements=text_replacements,
            color_replacements=color_replacements
        )
        
        # Apply template manually (simulating what the agent would do)
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        # Apply color replacements first
        for element_id, color in color_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                elem.set('fill', color)
                if elem.get('stroke'):
                    elem.set('stroke', color)
                print(f"  Applied color {color} to {element_id}")
        
        # Apply text replacements with wrapping and color contrast
        for element_id, text in text_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                # For pyramid level text, apply color contrast
                if 'level_' in element_id and '_text' in element_id:
                    level_num = element_id.replace('level_', '').replace('_text', '')
                    fill_elem = root.find(f".//*[@id='level_{level_num}_fill']")
                    if fill_elem is not None:
                        bg_color = fill_elem.get('fill', '#ffffff')
                        text_color = agent._get_text_color_for_background(bg_color)
                        elem.set('fill', text_color)
                        print(f"  Set {element_id} text color to {text_color} (bg: {bg_color})")
                    
                    # Apply text wrapping
                    max_width = agent._get_element_width(element_id)
                    lines = agent._wrap_text_for_svg(text, max_width, max_lines=2)
                    
                    if len(lines) > 1:
                        # Clear existing content
                        elem.text = None
                        for child in list(elem):
                            elem.remove(child)
                        
                        # Adjust y position for multi-line
                        x = elem.get('x', '400')
                        y = elem.get('y', '200')
                        y_offset = -((len(lines) - 1) * 10)
                        y_value = float(y) + y_offset
                        elem.set('y', str(y_value))
                        
                        # Add tspan elements
                        for j, line in enumerate(lines):
                            tspan = ET.SubElement(elem, '{http://www.w3.org/2000/svg}tspan')
                            tspan.set('x', x)
                            tspan.set('dy', '0' if j == 0 else '1.2em')
                            tspan.text = line
                            print(f"    Added tspan: {line}")
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
    asyncio.run(test_pyramid_comprehensive())