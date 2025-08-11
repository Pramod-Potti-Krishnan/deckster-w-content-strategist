#!/usr/bin/env python3
"""
Simple SVG Template Test Without Agent
======================================

Tests SVG template manipulation without requiring API keys.
"""

import asyncio
from pathlib import Path
import xml.etree.ElementTree as ET
import sys
sys.path.append(str(Path(__file__).parent))

from src.agents.content_agent_v7 import DiagramContentV4

OUTPUT_DIR = Path("test/diagram-tests/test_output/svg_simple")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_svg_template_loading():
    """Test loading and manipulating SVG templates."""
    print("\n" + "="*60)
    print("SVG TEMPLATE TEST (No API Required)")
    print("="*60)
    
    # Load pyramid template
    template_path = Path("src/agents/diagram_utils/templates/pyramid_3_level.svg")
    if template_path.exists():
        print(f"✅ Found pyramid template")
        
        # Read template
        svg_content = template_path.read_text()
        
        # Parse as XML
        try:
            tree = ET.fromstring(svg_content)
            print(f"✅ Valid SVG structure")
            
            # Find text elements
            text_elements = tree.findall(".//{http://www.w3.org/2000/svg}text")
            print(f"✅ Found {len(text_elements)} text elements")
            
            # Modify text content
            replacements = {
                "level_1_text": "Strategic Vision",
                "level_2_text": "Tactical Planning", 
                "level_3_text": "Operational Excellence",
                "pyramid_title": "Business Strategy"
            }
            
            for elem in tree.iter():
                elem_id = elem.get('id')
                if elem_id in replacements:
                    # Find text or tspan child
                    if elem.tag.endswith('text'):
                        # Special handling for level_1_text to wrap "Strategic Vision"
                        if elem_id == 'level_1_text':
                            # Clear existing text and children
                            elem.text = None
                            for child in list(elem):
                                elem.remove(child)
                            
                            # Split text into two lines
                            words = replacements[elem_id].split()
                            
                            # Adjust Y position to center the two-line text
                            current_y = int(elem.get('y', '210'))
                            elem.set('y', str(current_y - 10))
                            
                            # Create tspan elements for each line
                            tspan1 = ET.SubElement(elem, '{http://www.w3.org/2000/svg}tspan')
                            tspan1.set('x', elem.get('x', '400'))
                            tspan1.set('dy', '0')
                            tspan1.text = words[0]  # "Strategic"
                            
                            tspan2 = ET.SubElement(elem, '{http://www.w3.org/2000/svg}tspan')
                            tspan2.set('x', elem.get('x', '400'))
                            tspan2.set('dy', '1.2em')
                            tspan2.text = ' '.join(words[1:])  # "Vision"
                            
                            print(f"   Replaced: {elem_id} -> {replacements[elem_id]} (wrapped)")
                        else:
                            elem.text = replacements[elem_id]
                            print(f"   Replaced: {elem_id} -> {replacements[elem_id]}")
            
            # Convert back to string
            modified_svg = ET.tostring(tree, encoding='unicode')
            
            # Save modified version
            output_file = OUTPUT_DIR / "modified_pyramid.svg"
            output_file.write_text(modified_svg)
            print(f"✅ Saved modified SVG to: {output_file}")
            
        except ET.ParseError as e:
            print(f"❌ Invalid SVG: {e}")
    else:
        print(f"❌ Template not found: {template_path}")
    
    # Test matrix template
    matrix_path = Path("src/agents/diagram_utils/templates/matrix_2x2.svg")
    if matrix_path.exists():
        print(f"\n✅ Found matrix template")
        
        svg_content = matrix_path.read_text()
        tree = ET.fromstring(svg_content)
        
        # Modify quadrant labels
        replacements = {
            "quadrant_1": "Stars",
            "quadrant_2": "Question Marks",
            "quadrant_3": "Dogs",
            "quadrant_4": "Cash Cows",
            "x_label": "Market Share",
            "y_label": "Market Growth",
            "matrix_title": "BCG Matrix"
        }
        
        for elem in tree.iter():
            elem_id = elem.get('id')
            if elem_id in replacements:
                if elem.tag.endswith('text'):
                    elem.text = replacements[elem_id]
                    print(f"   Replaced: {elem_id} -> {replacements[elem_id]}")
        
        # Save
        modified_svg = ET.tostring(tree, encoding='unicode')
        output_file = OUTPUT_DIR / "modified_matrix.svg"
        output_file.write_text(modified_svg)
        print(f"✅ Saved modified SVG to: {output_file}")


def create_diagram_content_v4():
    """Test creating DiagramContentV4 for SVG."""
    print("\n" + "="*60)
    print("Testing DiagramContentV4 Creation")
    print("="*60)
    
    # Create pyramid content
    pyramid = DiagramContentV4(
        pattern="organizational_hierarchy",
        core_elements=[
            {"id": "top", "label": "Vision", "level": "1"},
            {"id": "middle", "label": "Strategy", "level": "2"},
            {"id": "bottom", "label": "Execution", "level": "3"}
        ],
        relationships=[
            {"from": "top", "to": "middle", "type": "guides"},
            {"from": "middle", "to": "bottom", "type": "drives"}
        ],
        flow_direction="vertical",
        visual_hierarchy=["top", "middle", "bottom"]
    )
    
    print(f"✅ Created pyramid diagram content")
    print(f"   Pattern: {pyramid.pattern}")
    print(f"   Elements: {len(pyramid.core_elements)}")
    print(f"   Flow: {pyramid.flow_direction}")
    
    # Create matrix content
    matrix = DiagramContentV4(
        pattern="comparison_matrix",
        core_elements=[
            {"id": "q1", "label": "High/High", "x": "high", "y": "high"},
            {"id": "q2", "label": "Low/High", "x": "low", "y": "high"},
            {"id": "q3", "label": "Low/Low", "x": "low", "y": "low"},
            {"id": "q4", "label": "High/Low", "x": "high", "y": "low"}
        ],
        relationships=[
            {"axis": "x", "label": "Effort"},
            {"axis": "y", "label": "Impact"}
        ],
        flow_direction="grid",
        visual_hierarchy=["q1", "q2"]
    )
    
    print(f"\n✅ Created matrix diagram content")
    print(f"   Pattern: {matrix.pattern}")
    print(f"   Quadrants: {len(matrix.core_elements)}")
    print(f"   Axes: {len(matrix.relationships)}")


def main():
    """Run all SVG tests."""
    print("\n" + "="*70)
    print("SVG TEMPLATE TESTS (No API Keys Required)")
    print("="*70)
    
    # Test template manipulation
    test_svg_template_loading()
    
    # Test content creation
    create_diagram_content_v4()
    
    print("\n" + "="*70)
    print("SVG TESTS COMPLETE")
    print(f"Check outputs in: {OUTPUT_DIR}")
    print("="*70)


if __name__ == "__main__":
    main()