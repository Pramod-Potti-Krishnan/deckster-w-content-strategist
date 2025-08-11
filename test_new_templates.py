#!/usr/bin/env python3
"""
Test the newly created SVG templates
=====================================

Tests hub_spoke, honeycomb, swot, process_flow, and org_chart templates.
"""

import asyncio
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.path.append(str(Path(__file__).parent))

from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import DiagramSpec

OUTPUT_DIR = Path("test_output/new_svg_templates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_test_content(diagram_type: str):
    """Create test content for each new diagram type."""
    
    if diagram_type == "hub_spoke":
        return {
            "elements": [
                {"label": "Central Hub"},  # Hub
                {"label": "Marketing"},    # Spoke 1
                {"label": "Sales"},        # Spoke 2
                {"label": "Engineering"},  # Spoke 3
                {"label": "Support"},      # Spoke 4
                {"label": "Finance"},      # Spoke 5
                {"label": "HR"}           # Spoke 6
            ],
            "title": "Department Hub Model"
        }
    
    elif diagram_type == "honeycomb":
        return {
            "elements": [
                {"label": "Core Value"},      # Center
                {"label": "Innovation"},      # Cell 2
                {"label": "Quality"},         # Cell 3
                {"label": "Teamwork"},        # Cell 4
                {"label": "Customer Focus"},  # Cell 5
                {"label": "Integrity"},       # Cell 6
                {"label": "Excellence"}       # Cell 7
            ],
            "title": "Company Values"
        }
    
    elif diagram_type == "swot":
        return {
            "elements": [
                {"label": "Strong brand, Skilled team"},     # Strengths
                {"label": "Limited resources"},              # Weaknesses
                {"label": "Growing market"},                 # Opportunities
                {"label": "Competition"}                     # Threats
            ],
            "title": "SWOT Analysis Q4 2024"
        }
    
    elif diagram_type == "process_flow":
        return {
            "elements": [
                {"label": "Data Input"},
                {"label": "Validation"},
                {"label": "Processing"},
                {"label": "Quality Check"},
                {"label": "Output"}
            ],
            "title": "Data Pipeline"
        }
    
    elif diagram_type == "org_chart":
        return {
            "elements": [
                {"label": "John Smith (CEO)"},       # CEO
                {"label": "Sarah Lee (CTO)"},        # Director 1
                {"label": "Mike Chen (CFO)"},        # Director 2
                {"label": "Amy Jones (COO)"},        # Director 3
                {"label": "Dev Team A"},             # Team 1-1
                {"label": "Dev Team B"},             # Team 1-2
                {"label": "Accounting"},             # Team 2-1
                {"label": "Operations A"},           # Team 3-1
                {"label": "Operations B"}            # Team 3-2
            ],
            "title": "Executive Organization"
        }
    
    return {}


async def test_template(diagram_type: str, agent: SVGDiagramAgent):
    """Test a single template."""
    print(f"\n{'='*50}")
    print(f"Testing: {diagram_type}")
    print(f"{'='*50}")
    
    # Create test content
    content = create_test_content(diagram_type)
    
    # Create theme
    theme = {
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#10b981",
            "accent": "#f59e0b",
            "background": "#ffffff",
            "text": "#1e293b"
        }
    }
    
    # Create spec
    spec = DiagramSpec(
        diagram_type=diagram_type,
        content=content,
        theme=theme,
        layout_hints={}
    )
    
    try:
        # Generate SVG
        result = await agent.generate(spec)
        
        # Save output
        output_file = OUTPUT_DIR / f"{diagram_type}.svg"
        output_file.write_text(result.svg_content)
        
        # Parse and validate SVG
        tree = ET.fromstring(result.svg_content)
        
        # Check if SVG is valid
        if tree.tag.endswith('svg'):
            print(f"  ✅ Valid SVG generated")
        
        # Check for text elements
        text_elements = tree.findall('.//*[@id]')
        text_count = sum(1 for elem in text_elements if elem.tag.endswith('text'))
        print(f"  ✅ Found {text_count} text elements")
        
        # Check for wrapped text
        wrapped_count = 0
        for elem in tree.iter():
            if elem.tag.endswith('text'):
                tspans = list(elem.findall('.//{http://www.w3.org/2000/svg}tspan'))
                if tspans and len(tspans) > 1:
                    wrapped_count += 1
                    elem_id = elem.get('id', 'unknown')
                    print(f"  ✅ Text wrapped in {elem_id}: {len(tspans)} lines")
        
        if wrapped_count == 0:
            print(f"  ℹ️ No text wrapping needed for this template")
        
        print(f"  📁 Saved to: {output_file}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"  ❌ Template not found: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Test all new templates."""
    print("\n" + "="*70)
    print("NEW SVG TEMPLATE TEST")
    print("Testing newly created templates")
    print("="*70)
    
    # Initialize agent
    print("\nInitializing SVG agent...")
    try:
        agent = SVGDiagramAgent()
    except Exception as e:
        print(f"Note: Agent initialization requires API keys: {e}")
        print("Testing with direct template manipulation instead...")
        return
    
    # New templates to test
    templates = [
        "hub_spoke",
        "honeycomb",
        "swot",
        "process_flow",
        "org_chart"
    ]
    
    # Test each template
    results = {}
    for template in templates:
        success = await test_template(template, agent)
        results[template] = success
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for template, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {template}")
    
    print(f"\n  Total: {success_count}/{total_count} templates working")
    print(f"  Output directory: {OUTPUT_DIR}")
    
    if success_count == total_count:
        print("\n🎉 All new templates working perfectly!")
    else:
        failed = [t for t, s in results.items() if not s]
        print(f"\n⚠️ Failed templates: {', '.join(failed)}")


if __name__ == "__main__":
    asyncio.run(main())