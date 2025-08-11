"""
Test Script for Diagram Agent Integration with Content Agent V7
==============================================================

This script tests the diagram generation pipeline using the exact
output format from content_agent_v7's DiagramContentV4.

Tests all three strategies with realistic content agent outputs.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.agents.diagram_agent import DiagramAgent, DiagramBuildAgent
from src.agents.diagram_utils.models import DiagramRequest, DiagramType
# ThemeDefinition is a dict in this context
from src.agents.content_agent_v7 import DiagramContentV4

# Create output directory for test results
OUTPUT_DIR = Path("test/diagram-tests/test_output/diagrams")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_theme() -> dict:
    """Create a sample theme for testing."""
    return dict(
        colors={
            "primary": "#2563eb",
            "secondary": "#64748b",
            "accent": "#f59e0b",
            "background": "#ffffff",
            "text": "#1e293b",
            "border": "#e2e8f0",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        typography={
            "font_family": "Inter, system-ui, sans-serif",
            "heading_font": "Inter, system-ui, sans-serif",
            "base_size": "16px"
        },
        mood_keywords=["professional", "modern", "clean"],
        formality_level="high",
        visual_guidelines={
            "style": "minimalist",
            "border_radius": "8px",
            "shadow": "subtle"
        }
    )


def create_process_flow_diagram() -> DiagramContentV4:
    """Create a process flow diagram as content agent would output it."""
    return DiagramContentV4(
        pattern="process_flow",
        core_elements=[
            {"id": "start", "label": "Patient Registration", "type": "start"},
            {"id": "triage", "label": "Triage Assessment", "type": "process"},
            {"id": "decision", "label": "Urgent Care?", "type": "decision"},
            {"id": "urgent", "label": "Emergency Treatment", "type": "process"},
            {"id": "regular", "label": "Regular Consultation", "type": "process"},
            {"id": "treatment", "label": "Treatment Plan", "type": "process"},
            {"id": "end", "label": "Discharge", "type": "end"}
        ],
        relationships=[
            {"from": "start", "to": "triage", "label": ""},
            {"from": "triage", "to": "decision", "label": ""},
            {"from": "decision", "to": "urgent", "label": "Yes"},
            {"from": "decision", "to": "regular", "label": "No"},
            {"from": "urgent", "to": "treatment", "label": ""},
            {"from": "regular", "to": "treatment", "label": ""},
            {"from": "treatment", "to": "end", "label": ""}
        ],
        flow_direction="horizontal",
        visual_hierarchy=["start", "decision", "end"]
    )


def create_organizational_hierarchy() -> DiagramContentV4:
    """Create an org chart diagram as content agent would output it."""
    return DiagramContentV4(
        pattern="organizational_hierarchy",
        core_elements=[
            {"id": "ceo", "label": "CEO", "level": "1"},
            {"id": "cto", "label": "CTO", "level": "2"},
            {"id": "cfo", "label": "CFO", "level": "2"},
            {"id": "cmo", "label": "CMO", "level": "2"},
            {"id": "eng_lead", "label": "Engineering Lead", "level": "3"},
            {"id": "data_lead", "label": "Data Lead", "level": "3"},
            {"id": "finance_lead", "label": "Finance Lead", "level": "3"},
            {"id": "marketing_lead", "label": "Marketing Lead", "level": "3"}
        ],
        relationships=[
            {"from": "ceo", "to": "cto", "type": "reports_to"},
            {"from": "ceo", "to": "cfo", "type": "reports_to"},
            {"from": "ceo", "to": "cmo", "type": "reports_to"},
            {"from": "cto", "to": "eng_lead", "type": "reports_to"},
            {"from": "cto", "to": "data_lead", "type": "reports_to"},
            {"from": "cfo", "to": "finance_lead", "type": "reports_to"},
            {"from": "cmo", "to": "marketing_lead", "type": "reports_to"}
        ],
        flow_direction="vertical",
        visual_hierarchy=["ceo", "cto", "cfo", "cmo"]
    )


def create_comparison_matrix() -> DiagramContentV4:
    """Create a comparison matrix as content agent would output it."""
    return DiagramContentV4(
        pattern="comparison_matrix",
        core_elements=[
            {"id": "q1", "label": "High Impact, High Effort", "x": "high", "y": "high"},
            {"id": "q2", "label": "High Impact, Low Effort", "x": "low", "y": "high"},
            {"id": "q3", "label": "Low Impact, Low Effort", "x": "low", "y": "low"},
            {"id": "q4", "label": "Low Impact, High Effort", "x": "high", "y": "low"}
        ],
        relationships=[
            {"axis": "x", "label": "Effort Required", "direction": "increasing"},
            {"axis": "y", "label": "Business Impact", "direction": "increasing"}
        ],
        flow_direction="grid",
        visual_hierarchy=["q2", "q1"]  # Prioritize high impact quadrants
    )


def create_concept_map() -> DiagramContentV4:
    """Create a concept map (for AI visual generation) as content agent would."""
    return DiagramContentV4(
        pattern="concept_map",
        core_elements=[
            {"id": "ai", "label": "Artificial Intelligence", "type": "central"},
            {"id": "ml", "label": "Machine Learning", "type": "branch"},
            {"id": "dl", "label": "Deep Learning", "type": "branch"},
            {"id": "nlp", "label": "Natural Language", "type": "branch"},
            {"id": "cv", "label": "Computer Vision", "type": "branch"},
            {"id": "robotics", "label": "Robotics", "type": "branch"},
            {"id": "ethics", "label": "AI Ethics", "type": "branch"}
        ],
        relationships=[
            {"from": "ai", "to": "ml", "type": "includes"},
            {"from": "ai", "to": "dl", "type": "includes"},
            {"from": "ai", "to": "nlp", "type": "includes"},
            {"from": "ai", "to": "cv", "type": "includes"},
            {"from": "ai", "to": "robotics", "type": "includes"},
            {"from": "ai", "to": "ethics", "type": "requires"},
            {"from": "ml", "to": "dl", "type": "subset"}
        ],
        flow_direction="radial",
        visual_hierarchy=["ai", "ml", "dl"]
    )


async def test_diagram_from_content(
    diagram_content: DiagramContentV4,
    theme: dict,
    test_name: str
):
    """Test diagram generation from content agent output."""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Pattern: {diagram_content.pattern}")
    print(f"Elements: {len(diagram_content.core_elements)}")
    print(f"Relationships: {len(diagram_content.relationships)}")
    print(f"{'='*60}")
    
    # Create the diagram build agent
    diagram_agent = DiagramBuildAgent()
    
    # Convert DiagramContentV4 to the format expected by diagram agent
    diagram_spec = {
        "pattern": diagram_content.pattern,
        "content": {
            "core_elements": diagram_content.core_elements,
            "relationships": diagram_content.relationships,
            "flow_direction": diagram_content.flow_direction,
            "visual_hierarchy": diagram_content.visual_hierarchy
        },
        "data_points": diagram_content.core_elements,
        "constraints": {
            "quality": "high",
            "add_accessibility": True
        }
    }
    
    # Build diagram
    try:
        result = await diagram_agent.build_diagram_from_spec(
            diagram_spec=diagram_spec,
            theme=theme,
            slide_context={
                "slide_type": "diagram_focused",
                "title": test_name
            }
        )
        
        print(f"✅ Success!")
        print(f"   Generation method: {result.generation_method}")
        print(f"   Content length: {len(result.content)} chars")
        
        # Save output
        if result.generation_method == "svg_template" or result.generation_method == "mermaid":
            # Save SVG
            output_file = OUTPUT_DIR / f"{test_name.replace(' ', '_').lower()}.svg"
            output_file.write_text(result.content)
            print(f"   Saved to: {output_file}")
        elif result.generation_method == "ai_visual":
            # Save base64 image
            output_file = OUTPUT_DIR / f"{test_name.replace(' ', '_').lower()}.txt"
            output_file.write_text(result.content[:100] + "..." if len(result.content) > 100 else result.content)
            print(f"   Saved preview to: {output_file}")
        
        # Print metadata
        if result.metadata:
            print(f"   Metadata: {json.dumps(result.metadata, indent=2)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("DIAGRAM AGENT INTEGRATION TEST")
    print("Testing with Content Agent V7 Output Format")
    print("="*80)
    
    theme = create_theme()
    
    # Test 1: Process Flow (should use Mermaid)
    process_flow = create_process_flow_diagram()
    await test_diagram_from_content(process_flow, theme, "Healthcare Process Flow")
    
    # Test 2: Organizational Hierarchy (might use SVG if template exists, else Mermaid)
    org_chart = create_organizational_hierarchy()
    await test_diagram_from_content(org_chart, theme, "Company Organization Chart")
    
    # Test 3: Comparison Matrix (should use SVG template)
    matrix = create_comparison_matrix()
    await test_diagram_from_content(matrix, theme, "Priority Matrix")
    
    # Test 4: Concept Map (might use AI visual for complex visualization)
    concept_map = create_concept_map()
    await test_diagram_from_content(concept_map, theme, "AI Concept Map")
    
    print("\n" + "="*80)
    print("INTEGRATION TEST COMPLETE")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())