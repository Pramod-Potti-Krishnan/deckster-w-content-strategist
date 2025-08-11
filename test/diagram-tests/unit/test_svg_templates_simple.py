#!/usr/bin/env python3
"""
Simple test to verify SVG templates are valid
==============================================
"""

from pathlib import Path
import xml.etree.ElementTree as ET

def test_svg_template(template_path: Path):
    """Test if an SVG template is valid and has required elements."""
    try:
        # Parse the SVG
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        # Check if it's a valid SVG
        if not root.tag.endswith('svg'):
            return False, "Not a valid SVG root element"
        
        # Count text elements with IDs
        text_elements = []
        for elem in root.iter():
            if elem.tag.endswith('text') and elem.get('id'):
                text_elements.append(elem.get('id'))
        
        # Count shape elements with IDs  
        shape_elements = []
        for elem in root.iter():
            if elem.get('id') and '_fill' in elem.get('id', ''):
                shape_elements.append(elem.get('id'))
        
        return True, {
            'text_elements': text_elements,
            'shape_elements': shape_elements,
            'total_text': len(text_elements),
            'total_shapes': len(shape_elements)
        }
        
    except Exception as e:
        return False, str(e)


def main():
    """Test all new templates."""
    template_dir = Path("src/agents/diagram_utils/templates")
    
    # New templates to test
    templates = [
        "hub_spoke_6.svg",
        "honeycomb_7.svg", 
        "swot_matrix.svg",
        "process_flow_5.svg",
        "org_chart_3.svg"
    ]
    
    print("\n" + "="*70)
    print("SVG TEMPLATE VALIDATION")
    print("="*70)
    
    all_valid = True
    
    for template_name in templates:
        template_path = template_dir / template_name
        print(f"\n📋 Testing: {template_name}")
        print("-" * 40)
        
        if not template_path.exists():
            print(f"  ❌ Template not found at {template_path}")
            all_valid = False
            continue
        
        valid, result = test_svg_template(template_path)
        
        if valid:
            print(f"  ✅ Valid SVG")
            print(f"  📝 Text elements: {result['total_text']}")
            if result['total_text'] > 0:
                print(f"     IDs: {', '.join(result['text_elements'][:5])}")
                if len(result['text_elements']) > 5:
                    print(f"     ... and {len(result['text_elements']) - 5} more")
            print(f"  🎨 Shape elements: {result['total_shapes']}")
            if result['total_shapes'] > 0:
                print(f"     IDs: {', '.join(result['shape_elements'][:5])}")
                if len(result['shape_elements']) > 5:
                    print(f"     ... and {len(result['shape_elements']) - 5} more")
        else:
            print(f"  ❌ Invalid: {result}")
            all_valid = False
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if all_valid:
        print("✅ All templates are valid SVG files!")
    else:
        print("❌ Some templates have issues")


if __name__ == "__main__":
    main()