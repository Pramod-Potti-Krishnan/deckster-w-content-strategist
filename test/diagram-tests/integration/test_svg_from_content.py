"""
Test SVG Template Generation with Content Agent Output
=====================================================

Tests SVG template-based diagram generation using DiagramContentV4
format from content_agent_v7.
"""

import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.agents.diagram_utils.svg_agent import SVGDiagramAgent
from src.agents.diagram_utils.models import DiagramSpec
from src.agents.content_agent_v7 import DiagramContentV4

OUTPUT_DIR = Path("test/diagram-tests/test_output/svg_diagrams")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_pyramid_content() -> DiagramContentV4:
    """Create pyramid diagram content as from content agent."""
    return DiagramContentV4(
        pattern="organizational_hierarchy",  # Will map to pyramid
        core_elements=[
            {"id": "strategic", "label": "Strategic Planning", "level": "top"},
            {"id": "tactical", "label": "Tactical Execution", "level": "middle"},
            {"id": "operational", "label": "Operational Support", "level": "bottom"}
        ],
        relationships=[
            {"from": "strategic", "to": "tactical", "type": "supports"},
            {"from": "tactical", "to": "operational", "type": "supports"}
        ],
        flow_direction="vertical",
        visual_hierarchy=["strategic", "tactical", "operational"]
    )


def create_matrix_content() -> DiagramContentV4:
    """Create 2x2 matrix content as from content agent."""
    return DiagramContentV4(
        pattern="comparison_matrix",
        core_elements=[
            {"id": "stars", "label": "Stars", "x": "high", "y": "high", 
             "description": "High growth, High share"},
            {"id": "questions", "label": "Question Marks", "x": "low", "y": "high",
             "description": "High growth, Low share"},
            {"id": "dogs", "label": "Dogs", "x": "low", "y": "low",
             "description": "Low growth, Low share"},
            {"id": "cash_cows", "label": "Cash Cows", "x": "high", "y": "low",
             "description": "Low growth, High share"}
        ],
        relationships=[
            {"axis": "x", "label": "Market Share", "direction": "increasing"},
            {"axis": "y", "label": "Market Growth", "direction": "increasing"}
        ],
        flow_direction="grid",
        visual_hierarchy=["stars", "cash_cows"]
    )


async def test_svg_generation(content: DiagramContentV4, name: str, template_type: str):
    """Test SVG generation from content agent output."""
    print(f"\n{'='*50}")
    print(f"Testing SVG: {name}")
    print(f"Expected template: {template_type}")
    print(f"{'='*50}")
    
    # Create theme
    theme = dict(
        colors={
            "primary": "#4f46e5",
            "secondary": "#7c3aed",
            "accent": "#ec4899",
            "background": "#ffffff",
            "text": "#1f2937"
        },
        typography={"font_family": "Inter"},
        mood_keywords=["professional"],
        formality_level="high",
        visual_guidelines={}
    )
    
    # Create SVG agent
    svg_agent = SVGDiagramAgent()
    
    # Convert content to DiagramSpec
    spec = DiagramSpec(
        diagram_type=template_type,
        content={
            "elements": content.core_elements,
            "relationships": content.relationships,
            "labels": [e["label"] for e in content.core_elements]
        },
        theme=theme,
        layout_hints={"flow": content.flow_direction}
    )
    
    try:
        # Generate SVG
        result = await svg_agent.generate(spec)
        
        print(f"✅ Generated successfully!")
        print(f"   Template used: {result.template_name}")
        print(f"   Elements modified: {result.elements_modified}")
        print(f"   Validation: {'✓' if result.validation_passed else '✗'}")
        
        # Save output
        output_file = OUTPUT_DIR / f"{name.replace(' ', '_').lower()}.svg"
        output_file.write_text(result.svg_content)
        print(f"   Saved to: {output_file}")
        
        # Show preview of SVG content
        preview = result.svg_content[:200] + "..." if len(result.svg_content) > 200 else result.svg_content
        print(f"\n   Preview: {preview}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run SVG template tests."""
    print("\n" + "="*70)
    print("SVG TEMPLATE GENERATION TEST")
    print("Using DiagramContentV4 format from Content Agent")
    print("="*70)
    
    # Test pyramid template
    pyramid_content = create_pyramid_content()
    await test_svg_generation(pyramid_content, "Strategy Pyramid", "pyramid")
    
    # Test matrix template
    matrix_content = create_matrix_content()
    await test_svg_generation(matrix_content, "BCG Matrix", "matrix_2x2")
    
    print("\n" + "="*70)
    print("SVG TESTS COMPLETE")
    print(f"Check outputs in: {OUTPUT_DIR}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())