"""
Simple Test for Diagram Components Without API Keys
===================================================

Tests the basic functionality of diagram components without
requiring API keys or actual model calls.
"""

import asyncio
from pathlib import Path
import sys
# Add project root to path (3 levels up from this file)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.agents.content_agent_v7 import DiagramContentV4
from src.agents.diagram_utils.models import (
    DiagramSpec, 
    SVGOutput,
    MermaidOutput,
    DiagramType,
    GenerationMethod
)

OUTPUT_DIR = Path("test/diagram-tests/test_output/simple")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_diagram_content_v4():
    """Test DiagramContentV4 creation."""
    print("\n" + "="*50)
    print("Testing DiagramContentV4 Model")
    print("="*50)
    
    # Create a sample diagram content
    diagram = DiagramContentV4(
        pattern="process_flow",
        core_elements=[
            {"id": "start", "label": "Start", "type": "node"},
            {"id": "process", "label": "Process", "type": "node"},
            {"id": "end", "label": "End", "type": "node"}
        ],
        relationships=[
            {"from": "start", "to": "process", "label": "begins"},
            {"from": "process", "to": "end", "label": "completes"}
        ],
        flow_direction="horizontal",
        visual_hierarchy=["start", "process", "end"]
    )
    
    print(f"✅ Created DiagramContentV4")
    print(f"   Pattern: {diagram.pattern}")
    print(f"   Elements: {len(diagram.core_elements)}")
    print(f"   Relationships: {len(diagram.relationships)}")
    print(f"   Flow: {diagram.flow_direction}")
    
    return diagram


def test_diagram_spec():
    """Test DiagramSpec creation."""
    print("\n" + "="*50)
    print("Testing DiagramSpec Model")
    print("="*50)
    
    theme = {
        "colors": {
            "primary": "#2563eb",
            "secondary": "#64748b"
        }
    }
    
    spec = DiagramSpec(
        diagram_type="flowchart",
        content={"elements": [], "relationships": []},
        theme=theme,
        layout_hints={"direction": "TB"}
    )
    
    print(f"✅ Created DiagramSpec")
    print(f"   Type: {spec.diagram_type}")
    print(f"   Theme colors: {list(spec.theme['colors'].keys())}")
    print(f"   Layout hints: {spec.layout_hints}")
    
    return spec


def test_output_models():
    """Test output model creation."""
    print("\n" + "="*50)
    print("Testing Output Models")
    print("="*50)
    
    # Test SVG Output
    svg_output = SVGOutput(
        svg_content='<svg xmlns="http://www.w3.org/2000/svg">...</svg>',
        template_name="pyramid_3_level.svg",
        elements_modified=5,
        validation_passed=True
    )
    print(f"✅ Created SVGOutput")
    print(f"   Template: {svg_output.template_name}")
    print(f"   Modified: {svg_output.elements_modified} elements")
    
    # Test Mermaid Output
    mermaid_output = MermaidOutput(
        mermaid_code="flowchart TD\n  A --> B",
        svg_output="<svg>...</svg>",
        diagram_type="flowchart",
        render_time_ms=150
    )
    print(f"✅ Created MermaidOutput")
    print(f"   Type: {mermaid_output.diagram_type}")
    print(f"   Render time: {mermaid_output.render_time_ms}ms")
    
    # Test AI Visual Output
    ai_output = AIVisualOutput(
        image_base64="data:image/png;base64,iVBORw0KGgo...",
        text_coordinates=None,
        generation_seed=12345,
        has_transparent_version=False,
        transparent_base64=None
    )
    print(f"✅ Created AIVisualOutput")
    print(f"   Has transparent: {ai_output.has_transparent_version}")
    print(f"   Seed: {ai_output.generation_seed}")


def test_svg_template_loading():
    """Test SVG template file access."""
    print("\n" + "="*50)
    print("Testing SVG Template Loading")
    print("="*50)
    
    template_dir = Path("src/agents/diagram_utils/templates")
    
    if template_dir.exists():
        templates = list(template_dir.glob("*.svg"))
        print(f"✅ Found {len(templates)} SVG templates:")
        for template in templates:
            print(f"   - {template.name}")
            # Read and verify it's valid XML
            try:
                content = template.read_text()
                if "<svg" in content:
                    print(f"     ✓ Valid SVG structure")
                else:
                    print(f"     ✗ Invalid SVG")
            except Exception as e:
                print(f"     ✗ Error reading: {e}")
    else:
        print(f"❌ Template directory not found: {template_dir}")


def test_diagram_type_enum():
    """Test DiagramType enum."""
    print("\n" + "="*50)
    print("Testing DiagramType Enum")
    print("="*50)
    
    print(f"✅ Available diagram types:")
    for dt in DiagramType:
        print(f"   - {dt.value}")
    
    print(f"\n✅ Total types: {len(DiagramType)}")


def test_generation_method_enum():
    """Test GenerationMethod enum."""
    print("\n" + "="*50)
    print("Testing GenerationMethod Enum")
    print("="*50)
    
    print(f"✅ Available generation methods:")
    for gm in GenerationMethod:
        print(f"   - {gm.value}")


async def test_mermaid_syntax_building():
    """Test Mermaid syntax generation (without agent)."""
    print("\n" + "="*50)
    print("Testing Mermaid Syntax Building")
    print("="*50)
    
    # Build a simple flowchart
    nodes = [
        {"id": "A", "label": "Start", "shape": "circle"},
        {"id": "B", "label": "Process", "shape": "rectangle"},
        {"id": "C", "label": "Decision", "shape": "diamond"},
        {"id": "D", "label": "End", "shape": "circle"}
    ]
    
    edges = [
        {"from": "A", "to": "B", "label": ""},
        {"from": "B", "to": "C", "label": ""},
        {"from": "C", "to": "D", "label": "Yes"}
    ]
    
    # Build Mermaid syntax manually
    lines = ["flowchart TD"]
    
    for node in nodes:
        if node["shape"] == "circle":
            lines.append(f'    {node["id"]}(("{node["label"]}"))')
        elif node["shape"] == "diamond":
            lines.append(f'    {node["id"]}{{{node["label"]}}}')
        else:
            lines.append(f'    {node["id"]}[{node["label"]}]')
    
    for edge in edges:
        if edge["label"]:
            lines.append(f'    {edge["from"]} -->|{edge["label"]}| {edge["to"]}')
        else:
            lines.append(f'    {edge["from"]} --> {edge["to"]}')
    
    mermaid_code = "\n".join(lines)
    
    print(f"✅ Generated Mermaid code:")
    print("   " + "\n   ".join(mermaid_code.split("\n")))
    
    # Save to file
    output_file = OUTPUT_DIR / "test_flowchart.mmd"
    output_file.write_text(mermaid_code)
    print(f"\n✅ Saved to: {output_file}")


def main():
    """Run all simple tests."""
    print("\n" + "="*70)
    print("SIMPLE DIAGRAM COMPONENT TESTS")
    print("No API keys required")
    print("="*70)
    
    # Test models
    test_diagram_content_v4()
    test_diagram_spec()
    test_output_models()
    
    # Test enums
    test_diagram_type_enum()
    test_generation_method_enum()
    
    # Test templates
    test_svg_template_loading()
    
    # Test Mermaid syntax
    asyncio.run(test_mermaid_syntax_building())
    
    print("\n" + "="*70)
    print("SIMPLE TESTS COMPLETE")
    print(f"Check outputs in: {OUTPUT_DIR}")
    print("="*70)


if __name__ == "__main__":
    main()