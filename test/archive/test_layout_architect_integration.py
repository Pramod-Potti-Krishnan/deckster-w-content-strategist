"""
Integration test script for Layout Architect.

This script simulates the flow from strawman approval to layout generation.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.session_manager import SessionManager
from src.agents.director_phase2_integration import DirectorPhase2Extension
from src.models.agents import PresentationStrawman, Slide
from src.agents.layout_architect.models import LayoutConfig

# Load environment variables
load_dotenv()


async def create_test_strawman():
    """Create a test strawman for layout generation."""
    return PresentationStrawman(
        type="PresentationStrawman",
        main_title="AI in Healthcare: Transforming Patient Care",
        overall_theme="Professional and data-driven",
        design_suggestions="Modern professional with blue color scheme and healthcare imagery",
        target_audience="Healthcare executives and administrators",
        presentation_duration=15,
        slides=[
            Slide(
                slide_id="slide_001",
                slide_number=1,
                title="AI in Healthcare: Transforming Patient Care",
                slide_type="title_slide",
                narrative="Setting the stage for healthcare transformation",
                key_points=["Innovation for Better Patient Outcomes"]
            ),
            Slide(
                slide_id="slide_002",
                slide_number=2,
                title="Current Healthcare Challenges",
                slide_type="content_heavy",
                narrative="Identifying pain points in healthcare",
                key_points=[
                    "Rising healthcare costs outpacing inflation",
                    "Critical staff shortages in key specialties",
                    "Diagnostic errors affect 12 million Americans annually"
                ]
            ),
            Slide(
                slide_id="slide_003",
                slide_number=3,
                title="AI Solutions in Practice",
                slide_type="visual_heavy",
                narrative="Demonstrating real-world applications",
                key_points=[
                    "AI detects cancer 30% more accurately",
                    "Predictive models reduce readmissions by 25%",
                    "Robotic surgery increases precision"
                ],
                visuals_needed="**Goal:** Show AI impact. **Content:** Medical AI examples. **Style:** Modern infographic."
            ),
            Slide(
                slide_id="slide_004",
                slide_number=4,
                title="Implementation Roadmap",
                slide_type="data_driven",
                narrative="Providing actionable next steps",
                key_points=[
                    "Phase 1: Assess current infrastructure (3 months)",
                    "Phase 2: Pilot with one department (6 months)",
                    "Phase 3: Scale across organization (12 months)",
                    "Phase 4: Continuous optimization"
                ],
                analytics_needed="Timeline chart showing implementation phases and ROI projections"
            )
        ]
    )


async def test_layout_architect():
    """Test the Layout Architect integration."""
    print("=== Layout Architect Integration Test ===\n")
    
    # Initialize components
    print("1. Initializing components...")
    
    # For testing, we'll use a mock session manager or skip it
    from src.storage.supabase import get_supabase_client
    try:
        supabase = get_supabase_client()
        session_manager = SessionManager(supabase)
    except Exception as e:
        print(f"   Note: Using mock session manager due to: {e}")
        session_manager = None
    
    # Mock WebSocket handler for testing
    class MockWebSocketHandler:
        async def send_message(self, message):
            print(f"\n📤 WebSocket Message: {message['type']}")
            if message['type'] == 'theme_update':
                print(f"   Theme: {message['payload']['theme_name']}")
            elif message['type'] == 'slide_update':
                print(f"   Slide: {message['payload']['slides'][0]['slide_id']}")
                print(f"   Layout: {message['payload']['slides'][0]['layout']}")
            elif message['type'] == 'status_update':
                print(f"   Status: {message['payload']['status']} - {message['payload']['text']}")
    
    websocket_handler = MockWebSocketHandler()
    
    # Create Phase 2 extension
    phase2_ext = DirectorPhase2Extension(session_manager, websocket_handler)
    
    # Create test strawman
    print("\n2. Creating test strawman...")
    strawman = await create_test_strawman()
    print(f"   Created strawman with {len(strawman.slides)} slides")
    
    # Test layout generation
    print("\n3. Generating layouts...")
    result = await phase2_ext.handle_layout_generation_state(
        session_id="test_session_123",
        user_id="test_user",
        context={'strawman_data': strawman}
    )
    
    print(f"\n4. Result: {result['status']}")
    print(f"   Theme: {result.get('theme_name', 'N/A')}")
    print(f"   Slides processed: {result.get('slide_count', 0)}")
    
    # Test direct Layout Architect access
    print("\n5. Testing Layout Architect directly...")
    # Create Layout Architect directly without session manager for testing
    from src.agents.layout_architect import LayoutArchitectMVP
    from src.agents.layout_architect.models import LayoutConfig
    
    layout_architect = LayoutArchitectMVP(
        config=LayoutConfig(),
        session_manager=None  # OK for testing
    )
    
    layout_result = await layout_architect.process_approved_strawman(
        session_id="test_session_direct",
        user_id="test_user",
        strawman=strawman
    )
    
    print(f"\n   Theme generated: {layout_result['theme'].theme_name}")
    print(f"   Theme colors: {layout_result['theme'].theme_config.colors.dict()}")
    
    print("\n6. Layout details for each slide:")
    for layout in layout_result['layouts']:
        print(f"\n   Slide {layout.slide_number} ({layout.slide_type}):")
        print(f"   - Layout: {layout.layout}")
        print(f"   - Containers: {len(layout.containers)}")
        print(f"   - White space: {layout.white_space_ratio:.2%}")
        print(f"   - Alignment score: {layout.alignment_score:.2%}")
        
        for container in layout.containers:
            if container.position and container.position != "from_theme":
                print(f"     • {container.name}: {container.position.dict()}")
    
    print("\n✅ Layout Architect test complete!")


async def test_individual_components():
    """Test individual Layout Architect components."""
    print("\n=== Testing Individual Components ===\n")
    
    from src.agents.layout_architect.tools import (
        GridCalculator, WhiteSpaceTool, AlignmentValidator
    )
    from src.agents.layout_architect.models import MVPContainer, ContainerContent, GridPosition
    
    # Test Grid Calculator
    print("1. Testing Grid Calculator:")
    calc = GridCalculator()
    print(f"   Snap 10.7 to grid: {calc.snap_to_grid(10.7)}")
    cols, rows, w, h = calc.calculate_grid_layout(6, 150, 80, 4, 3)
    print(f"   Grid for 6 items: {cols}x{rows}, cell size: {w}x{h}")
    
    # Test White Space Tool
    print("\n2. Testing White Space Tool:")
    ws_tool = WhiteSpaceTool()
    containers = [
        MVPContainer(
            name="title",
            content=ContainerContent(type="text", text="Title"),
            position=GridPosition(leftInset=8, topInset=8, width=144, height=12)
        ),
        MVPContainer(
            name="body",
            content=ContainerContent(type="text", text="Content"),
            position=GridPosition(leftInset=8, topInset=24, width=144, height=50)
        )
    ]
    ratio = ws_tool.calculate_white_space_ratio(containers)
    print(f"   White space ratio: {ratio:.2%}")
    valid, msg = ws_tool.validate_white_space_ratio(ratio)
    print(f"   Validation: {msg}")
    
    # Test Alignment Validator
    print("\n3. Testing Alignment Validator:")
    validator = AlignmentValidator()
    valid, score, issues = validator.validate_alignment(containers)
    print(f"   Alignment valid: {valid}")
    print(f"   Alignment score: {score:.2%}")
    if issues:
        print(f"   Issues: {issues}")


if __name__ == "__main__":
    print("Starting Layout Architect tests...\n")
    
    # Debug: Print environment check
    print(f"Current directory: {os.getcwd()}")
    print(f".env file exists: {os.path.exists('.env')}")
    
    # Check environment
    google_key = os.getenv("GOOGLE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if google_key:
        print(f"✅ GOOGLE_API_KEY is set (length: {len(google_key)})")
    else:
        print("❌ GOOGLE_API_KEY not found")
        
    if gemini_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(gemini_key)})")
    else:
        print("❌ GEMINI_API_KEY not found")
    
    if not google_key and not gemini_key:
        print("\n⚠️  Warning: No API keys found. Theme generation will fail.")
        print("Make sure you're running from the project root and .env is loaded.")
    
    # Run tests
    asyncio.run(test_layout_architect())
    
    # Run component tests
    asyncio.run(test_individual_components())