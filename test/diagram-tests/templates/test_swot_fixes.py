#!/usr/bin/env python3
"""Test SWOT template fixes."""

import sys
from pathlib import Path
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import xml.etree.ElementTree as ET
from pathlib import Path
from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import SVGTemplateSpec

def test_swot_fixes():
    """Test SWOT with lighter colors and multi-line items."""
    
    agent = SVGDiagramAgent()
    template_path = Path(__file__).parent / "src/agents/diagram_utils/templates/swot_matrix.svg"
    output_dir = Path("test/diagram-tests/test_output/svg_templates_comprehensive")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test content with comma-separated items
    content = {
        "elements": [
            {"label": "Strong brand recognition, Skilled workforce, Market leader"},
            {"label": "Limited resources, Tech debt, Geographic constraints"},
            {"label": "Growing market, New technologies, Partnership potential"},
            {"label": "Competition, Economic uncertainty, Regulatory changes"}
        ],
        "title": "Strategic SWOT Analysis"
    }
    
    theme = {
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#10b981",
            "accent": "#f59e0b"
        }
    }
    
    print("=== Testing SWOT fixes ===")
    
    # Extract theme colors
    theme_colors = agent._extract_theme_colors(theme)
    print(f"Theme colors: {theme_colors}")
    
    # Get color replacements
    color_replacements = agent._get_color_replacements("swot", theme_colors)
    print(f"Color replacements: {color_replacements}")
    
    # Extract text replacements with newline formatting
    text_replacements = agent._extract_text_from_content("swot", content)
    print(f"\nText replacements:")
    for key, value in text_replacements.items():
        if 'text' in key and key != 'swot_title':
            print(f"  {key}:")
            for line in value.split('\n'):
                print(f"    - {line}")
    
    # Create template spec
    template_spec = SVGTemplateSpec(
        template_name="swot_matrix.svg",
        text_replacements=text_replacements,
        color_replacements=color_replacements
    )
    
    # Apply template
    tree = ET.parse(template_path)
    root = tree.getroot()
    
    # Apply color replacements
    for element_id, color in color_replacements.items():
        elem = root.find(f".//*[@id='{element_id}']")
        if elem is not None:
            old_color = elem.get('fill')
            elem.set('fill', color)
            elem.set('stroke', color)
            print(f"\nColor change {element_id}: {old_color} -> {color}")
    
    # Apply text replacements with multi-line support
    for element_id, text in text_replacements.items():
        elem = root.find(f".//*[@id='{element_id}']")
        if elem is not None:
            if element_id in ['strengths_text', 'weaknesses_text', 'opportunities_text', 'threats_text']:
                # Apply text wrapping for SWOT items (4 lines max)
                max_width = agent._get_element_width(element_id)
                lines = agent._wrap_text_for_svg(text, max_width, max_lines=4)
                
                if len(lines) > 1:
                    elem.text = None
                    for child in list(elem):
                        elem.remove(child)
                    
                    x = elem.get('x', '275')
                    y = elem.get('y', '210')
                    y_offset = -((len(lines) - 1) * 8)  # Smaller offset for SWOT
                    y_value = float(y) + y_offset
                    elem.set('y', str(y_value))
                    
                    for j, line in enumerate(lines):
                        tspan = ET.SubElement(elem, '{http://www.w3.org/2000/svg}tspan')
                        tspan.set('x', x)
                        tspan.set('dy', '0' if j == 0 else '1.2em')
                        tspan.text = line
                    
                    print(f"\n{element_id} wrapped to {len(lines)} lines")
                else:
                    elem.text = text
            else:
                elem.text = text
    
    # Save the result
    output_path = output_dir / "swot_theme_0.svg"
    
    # Convert to string and clean namespaces
    svg_str = ET.tostring(root, encoding='unicode')
    svg_str = svg_str.replace('ns0:', '').replace('xmlns:ns0=', 'xmlns=')
    
    with open(output_path, 'w') as f:
        f.write(svg_str)
    
    print(f"\nSaved to: {output_path}")
    
    # Verify the colors in output
    verify_tree = ET.parse(output_path)
    verify_root = verify_tree.getroot()
    print("\nVerifying colors in output:")
    for section in ['strengths', 'weaknesses', 'opportunities', 'threats']:
        elem = verify_root.find(f".//*[@id='{section}_fill']")
        if elem is not None:
            print(f"  {section}: {elem.get('fill')}")

if __name__ == "__main__":
    test_swot_fixes()