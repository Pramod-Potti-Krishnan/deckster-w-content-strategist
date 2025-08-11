"""
Test Mermaid Diagram Generation with Content Agent Output
========================================================

Tests Mermaid-based diagram generation using DiagramContentV4
format from content_agent_v7.
"""

import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.agents.diagram_utils.mermaid_agent import MermaidDiagramAgent
from src.agents.diagram_utils.models import DiagramSpec
from src.agents.content_agent_v7 import DiagramContentV4

OUTPUT_DIR = Path("test_output/mermaid_diagrams")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_process_flow_content() -> DiagramContentV4:
    """Create process flow content as from content agent."""
    return DiagramContentV4(
        pattern="process_flow",
        core_elements=[
            {"id": "receive", "label": "Receive Request", "type": "start"},
            {"id": "validate", "label": "Validate Data", "type": "process"},
            {"id": "check", "label": "Check Compliance", "type": "decision"},
            {"id": "approve", "label": "Approve Request", "type": "process"},
            {"id": "reject", "label": "Reject Request", "type": "process"},
            {"id": "notify", "label": "Notify User", "type": "process"},
            {"id": "complete", "label": "Complete", "type": "end"}
        ],
        relationships=[
            {"from": "receive", "to": "validate", "label": ""},
            {"from": "validate", "to": "check", "label": ""},
            {"from": "check", "to": "approve", "label": "Compliant"},
            {"from": "check", "to": "reject", "label": "Non-compliant"},
            {"from": "approve", "to": "notify", "label": ""},
            {"from": "reject", "to": "notify", "label": ""},
            {"from": "notify", "to": "complete", "label": ""}
        ],
        flow_direction="vertical",
        visual_hierarchy=["check", "approve", "reject"]
    )


def create_sequence_diagram_content() -> DiagramContentV4:
    """Create sequence diagram content as from content agent."""
    return DiagramContentV4(
        pattern="system_architecture",  # Maps to sequence for interactions
        core_elements=[
            {"id": "user", "label": "User", "type": "actor"},
            {"id": "frontend", "label": "Frontend", "type": "system"},
            {"id": "api", "label": "API Server", "type": "system"},
            {"id": "database", "label": "Database", "type": "system"},
            {"id": "cache", "label": "Cache", "type": "system"}
        ],
        relationships=[
            {"from": "user", "to": "frontend", "label": "Login Request", "sequence": "1"},
            {"from": "frontend", "to": "api", "label": "POST /auth/login", "sequence": "2"},
            {"from": "api", "to": "cache", "label": "Check Session", "sequence": "3"},
            {"from": "cache", "to": "api", "label": "Session Not Found", "sequence": "4"},
            {"from": "api", "to": "database", "label": "Verify Credentials", "sequence": "5"},
            {"from": "database", "to": "api", "label": "User Data", "sequence": "6"},
            {"from": "api", "to": "cache", "label": "Store Session", "sequence": "7"},
            {"from": "api", "to": "frontend", "label": "Auth Token", "sequence": "8"},
            {"from": "frontend", "to": "user", "label": "Login Success", "sequence": "9"}
        ],
        flow_direction="sequential",
        visual_hierarchy=["user", "api", "database"]
    )


def create_gantt_chart_content() -> DiagramContentV4:
    """Create Gantt chart content as from content agent."""
    return DiagramContentV4(
        pattern="timeline",  # Maps to Gantt for project timelines
        core_elements=[
            {"id": "research", "label": "Research Phase", "start": "2024-01-01", "duration": "30d"},
            {"id": "design", "label": "Design Phase", "start": "2024-01-31", "duration": "21d"},
            {"id": "development", "label": "Development", "start": "2024-02-21", "duration": "60d"},
            {"id": "testing", "label": "Testing", "start": "2024-04-22", "duration": "14d"},
            {"id": "deployment", "label": "Deployment", "start": "2024-05-06", "duration": "7d"}
        ],
        relationships=[
            {"from": "research", "to": "design", "type": "precedes"},
            {"from": "design", "to": "development", "type": "precedes"},
            {"from": "development", "to": "testing", "type": "precedes"},
            {"from": "testing", "to": "deployment", "type": "precedes"}
        ],
        flow_direction="temporal",
        visual_hierarchy=["development", "testing"]
    )


def create_pie_chart_content() -> DiagramContentV4:
    """Create pie chart content as from content agent."""
    return DiagramContentV4(
        pattern="composition",  # Maps to pie chart
        core_elements=[
            {"id": "product", "label": "Product Sales", "value": "45"},
            {"id": "services", "label": "Services", "value": "30"},
            {"id": "licensing", "label": "Licensing", "value": "15"},
            {"id": "support", "label": "Support", "value": "10"}
        ],
        relationships=[],  # Pie charts don't have relationships
        flow_direction="radial",
        visual_hierarchy=["product", "services"]
    )


async def test_mermaid_generation(content: DiagramContentV4, name: str, expected_type: str):
    """Test Mermaid generation from content agent output."""
    print(f"\n{'='*50}")
    print(f"Testing Mermaid: {name}")
    print(f"Expected type: {expected_type}")
    print(f"Pattern: {content.pattern}")
    print(f"{'='*50}")
    
    # Create theme
    theme = dict(
        colors={
            "primary": "#0ea5e9",
            "secondary": "#8b5cf6",
            "accent": "#f59e0b",
            "background": "#ffffff",
            "text": "#0f172a",
            "border": "#cbd5e1"
        },
        typography={"font_family": "Inter"},
        mood_keywords=["modern", "technical"],
        formality_level="medium",
        visual_guidelines={}
    )
    
    # Create Mermaid agent
    mermaid_agent = MermaidDiagramAgent()
    
    # Convert content to DiagramSpec
    spec = DiagramSpec(
        diagram_type=expected_type,
        content={
            "elements": content.core_elements,
            "relationships": content.relationships,
            "flow": content.flow_direction,
            "emphasis": content.visual_hierarchy
        },
        theme=theme,
        layout_hints={}
    )
    
    try:
        # Generate Mermaid diagram
        result = await mermaid_agent.generate(spec)
        
        print(f"✅ Generated successfully!")
        print(f"   Diagram type: {result.diagram_type}")
        print(f"   Render time: {result.render_time_ms}ms")
        
        # Save Mermaid code
        code_file = OUTPUT_DIR / f"{name.replace(' ', '_').lower()}.mmd"
        code_file.write_text(result.mermaid_code)
        print(f"   Mermaid code saved to: {code_file}")
        
        # Save SVG output
        svg_file = OUTPUT_DIR / f"{name.replace(' ', '_').lower()}.svg"
        svg_file.write_text(result.svg_output)
        print(f"   SVG saved to: {svg_file}")
        
        # Show Mermaid code preview
        print(f"\n   Mermaid Code:")
        lines = result.mermaid_code.split('\n')[:10]
        for line in lines:
            print(f"      {line}")
        if len(result.mermaid_code.split('\n')) > 10:
            print(f"      ... ({len(result.mermaid_code.split('\n')) - 10} more lines)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run Mermaid generation tests."""
    print("\n" + "="*70)
    print("MERMAID DIAGRAM GENERATION TEST")
    print("Using DiagramContentV4 format from Content Agent")
    print("="*70)
    
    # Test 1: Process Flow (Flowchart)
    process_flow = create_process_flow_content()
    await test_mermaid_generation(process_flow, "Approval Process", "flowchart")
    
    # Test 2: Sequence Diagram
    sequence = create_sequence_diagram_content()
    await test_mermaid_generation(sequence, "Login Sequence", "sequence")
    
    # Test 3: Gantt Chart
    gantt = create_gantt_chart_content()
    await test_mermaid_generation(gantt, "Project Timeline", "gantt")
    
    # Test 4: Pie Chart
    pie = create_pie_chart_content()
    await test_mermaid_generation(pie, "Revenue Distribution", "pie_chart")
    
    print("\n" + "="*70)
    print("MERMAID TESTS COMPLETE")
    print(f"Check outputs in: {OUTPUT_DIR}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())