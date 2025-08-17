#!/usr/bin/env python3
"""
Test script for hub & spoke templates
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from src.agents.diagram_utils.svg_playbook import (
    get_template_spec,
    validate_svg_structure
)

def test_hub_spoke_templates():
    """Test the hub & spoke templates."""
    print("Testing Hub & Spoke Templates")
    print("=" * 50)
    
    templates = ["hub_spoke_4", "hub_spoke_6"]
    templates_dir = Path(__file__).parent / "src" / "agents" / "diagram_utils" / "templates"
    
    for template_name in templates:
        print(f"\nTesting {template_name}:")
        
        # Get template spec
        spec = get_template_spec(template_name)
        if spec:
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
                    
                # Check for enhanced features
                if "gradient" in svg_content:
                    print(f"  ✓ Enhanced with gradients")
                if "marker-end" in svg_content:
                    print(f"  ✓ Arrow markers added")
                if "stroke-linecap" in svg_content:
                    print(f"  ✓ Smooth line caps")
            else:
                print(f"  ⚠️ SVG file not found")
        else:
            print(f"  ⚠️ Template spec not found")
    
    print("\n" + "=" * 50)
    print("✅ Hub & Spoke templates tested!")

if __name__ == "__main__":
    test_hub_spoke_templates()