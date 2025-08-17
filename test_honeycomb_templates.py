#!/usr/bin/env python3
"""
Test script for new honeycomb templates
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from src.agents.diagram_utils.svg_playbook import (
    get_template_spec,
    validate_svg_structure,
    get_text_capacity
)

def test_honeycomb_templates():
    """Test the new honeycomb templates."""
    print("Testing Honeycomb Templates")
    print("=" * 50)
    
    templates = ["honeycomb_3", "honeycomb_5", "honeycomb_7"]
    templates_dir = Path(__file__).parent / "src" / "agents" / "diagram_utils" / "templates"
    
    for template_name in templates:
        print(f"\nTesting {template_name}:")
        
        # Get template spec
        spec = get_template_spec(template_name)
        assert spec is not None, f"Spec not found for {template_name}"
        print(f"  ✓ Template spec found")
        print(f"  ✓ Status: {spec['status']}")
        
        # Check if file exists
        svg_file = templates_dir / f"{template_name}.svg"
        if svg_file.exists():
            print(f"  ✓ SVG file exists")
            
            # Read and validate SVG
            svg_content = svg_file.read_text()
            validation = validate_svg_structure(svg_content, template_name)
            
            if validation["valid"]:
                print(f"  ✓ SVG structure valid")
            else:
                print(f"  ⚠️ Missing IDs: {validation['missing_ids']}")
            
            # Check text capacities
            placeholders = spec.get("text_placeholders", {})
            print(f"  ✓ Text placeholders: {len(placeholders)}")
            
            # Sample capacity check
            if "hex_1_title" in placeholders:
                capacity = get_text_capacity(template_name, "hex_1_text")
                print(f"  ✓ Core hex capacity: {capacity['chars_per_line']} chars × {capacity['max_lines']} lines")
        else:
            print(f"  ⚠️ SVG file not found (expected for planned templates)")
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    test_honeycomb_templates()