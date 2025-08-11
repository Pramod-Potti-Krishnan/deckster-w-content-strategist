"""
Integration tests for the three-agent Layout Architect system.

Tests the Theme Agent, Structure Agent, Layout Engine Agent, and Orchestrator.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.agents import Slide
from src.agents.layout_architect import (
    LayoutArchitectOrchestrator,
    LayoutGenerationRequest,
    ThemeAgent,
    StructureAgent,
    LayoutEngineAgent,
    LayoutEngineConfig
)

# Load environment variables
load_dotenv()


def create_test_slides() -> List[Slide]:
    """Create a variety of test slides."""
    return [
        Slide(
            slide_id="slide_001",
            slide_number=1,
            title="AI in Healthcare: Transforming Patient Care",
            slide_type="title_slide",
            narrative="Setting the stage for healthcare transformation",
            key_points=["Innovation for Better Patient Outcomes"],
            structure_preference="centered"
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
            ],
            structure_preference="hierarchical"
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
            visuals_needed="Medical AI examples, infographic style",
            structure_preference="visual_left"
        ),
        Slide(
            slide_id="slide_004",
            slide_number=4,
            title="Implementation ROI",
            slide_type="data_driven",
            narrative="Quantifying the business impact",
            key_points=[
                "25% reduction in diagnostic errors",
                "$150M annual cost savings",
                "40% improvement in patient satisfaction"
            ],
            analytics_needed="ROI chart, comparison metrics",
            structure_preference="dashboard"
        )
    ]


async def test_theme_agent():
    """Test the Theme Agent independently."""
    print("\n=== Testing Theme Agent ===")
    
    theme_agent = ThemeAgent()
    
    # Test 1: Generate theme for professional presentation
    print("\n1. Testing professional theme generation:")
    theme = await theme_agent.generate_theme(
        slide_type="content_heavy",
        user_context={
            "brand": "TechHealth Corp",
            "industry": "Healthcare Technology",
            "preferences": {
                "formality": "professional",
                "color_preference": "blue"
            }
        },
        content_hints={
            "title": "Healthcare Innovation",
            "tone": "professional"
        }
    )
    
    print(f"   Theme name: {theme.name}")
    print(f"   Primary color: {theme.tokens.colors.get('primary', {}).get('value', 'N/A')}")
    print(f"   Typography: {theme.tokens.typography.get('heading', {}).get('fontFamily', 'N/A')}")
    print(f"   Templates available: {len(theme.templates)}")
    
    # Test 2: Generate theme for casual presentation
    print("\n2. Testing casual theme generation:")
    theme_casual = await theme_agent.generate_theme(
        slide_type="visual_heavy",
        user_context={
            "brand": "StartupXYZ",
            "industry": "EdTech",
            "preferences": {
                "formality": "casual",
                "modern": True
            }
        }
    )
    
    print(f"   Theme name: {theme_casual.name}")
    print(f"   Style attributes: {theme_casual.style_attributes}")
    
    return theme


async def test_structure_agent():
    """Test the Structure Agent independently."""
    print("\n=== Testing Structure Agent ===")
    
    structure_agent = StructureAgent()
    slides = create_test_slides()
    
    # Test different slide types
    for slide in slides[:3]:  # Test first 3 slides
        print(f"\n{slide.slide_number}. Analyzing {slide.slide_type}: {slide.title}")
        
        manifest = await structure_agent.analyze_structure(
            slide=slide,
            theme_context={"style": "professional"}
        )
        
        print(f"   Containers: {len(manifest.containers)}")
        print(f"   Primary message: {manifest.primary_message}")
        print(f"   Content flow: {manifest.content_flow.value}")
        print(f"   Complexity score: {manifest.complexity_score:.2f}")
        
        # Show container roles
        print("   Container roles:")
        for container in manifest.containers[:3]:  # Show first 3
            print(f"     - {container.role.value}: {container.content[:50]}...")
        
        # Show relationships
        if manifest.relationships:
            print(f"   Relationships: {len(manifest.relationships)}")
    
    return manifest


async def test_layout_engine():
    """Test the Layout Engine Agent independently."""
    print("\n=== Testing Layout Engine Agent ===")
    
    # First, we need a theme and manifest
    theme_agent = ThemeAgent()
    structure_agent = StructureAgent()
    layout_engine = LayoutEngineAgent()
    
    slide = create_test_slides()[2]  # Visual heavy slide
    
    # Generate theme
    theme = await theme_agent.generate_theme(
        slide_type=slide.slide_type,
        user_context={"industry": "Healthcare"}
    )
    
    # Analyze structure
    manifest = await structure_agent.analyze_structure(slide=slide)
    
    # Test layout generation
    print("\n1. Testing layout generation:")
    layout = await layout_engine.generate_layout(
        theme=theme,
        manifest=manifest,
        config=LayoutEngineConfig(
            max_iterations=3,
            white_space_min=0.3,
            white_space_max=0.5
        )
    )
    
    print(f"   Slide ID: {layout.slide_id}")
    print(f"   Containers: {len(layout.containers)}")
    print(f"   White space ratio: {layout.white_space_ratio:.2%}")
    
    # Show container positions
    print("   Container positions:")
    for container in layout.containers:
        pos = container.position
        print(f"     - {container.id}: ({pos.leftInset}, {pos.topInset}) {pos.width}×{pos.height}")
    
    # Test layout quality analysis
    print("\n2. Testing layout quality analysis:")
    quality = await layout_engine.analyze_layout_quality(layout)
    
    print(f"   Balance score: {quality['balance_score']:.2f}")
    print(f"   Center of mass: ({quality['center_of_mass'][0]:.1f}, {quality['center_of_mass'][1]:.1f})")
    print(f"   Valid: {quality['is_valid']}")
    
    if quality.get('recommendations'):
        print("   Recommendations:")
        for rec in quality['recommendations']:
            print(f"     - {rec}")
    
    return layout


async def test_orchestrator():
    """Test the complete orchestrator workflow."""
    print("\n=== Testing Orchestrator ===")
    
    orchestrator = LayoutArchitectOrchestrator()
    slides = create_test_slides()
    
    # Test 1: Single slide generation
    print("\n1. Testing single slide generation:")
    request = LayoutGenerationRequest(
        slide=slides[0],
        user_context={
            "brand": "HealthTech Solutions",
            "industry": "Healthcare",
            "preferences": {
                "formality": "professional",
                "modern": True
            }
        },
        presentation_context={
            "tone": "professional",
            "audience": "Healthcare executives"
        },
        layout_config=LayoutEngineConfig(
            max_iterations=5,
            white_space_min=0.35,
            white_space_max=0.45
        )
    )
    
    result = await orchestrator.generate_layout(request)
    
    print(f"   Success: {result.success}")
    print(f"   Theme: {result.theme.name}")
    print(f"   Containers in manifest: {len(result.manifest.containers)}")
    print(f"   Containers in layout: {len(result.layout.containers)}")
    print(f"   White space: {result.layout.white_space_ratio:.2%}")
    print(f"   Balance score: {result.generation_metrics.get('balance_score', 'N/A')}")
    
    if result.error_message:
        print(f"   Error: {result.error_message}")
    
    # Test 2: Batch generation
    print("\n2. Testing batch generation:")
    results = await orchestrator.generate_batch(
        slides=slides,
        user_context={
            "brand": "TechHealth",
            "industry": "Healthcare Technology"
        },
        presentation_context={
            "tone": "professional",
            "duration": 15
        }
    )
    
    print(f"   Processed {len(results)} slides")
    successful = sum(1 for r in results if r.success)
    print(f"   Successful: {successful}/{len(results)}")
    
    # Show summary for each slide
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"   {status} Slide {result.slide_id}: {len(result.layout.containers)} containers")
    
    # Test 3: Analyze slide complexity
    print("\n3. Testing slide complexity analysis:")
    for slide in slides[:2]:
        complexity = await orchestrator.analyze_slide_complexity(slide)
        print(f"   {slide.title}:")
        print(f"     - Containers: {complexity['container_count']}")
        print(f"     - Complexity: {complexity['complexity_score']:.2f}")
        print(f"     - Content flow: {complexity['content_flow']}")
    
    return results


async def test_error_handling():
    """Test error handling in the system."""
    print("\n=== Testing Error Handling ===")
    
    orchestrator = LayoutArchitectOrchestrator()
    
    # Test 1: Empty slide
    print("\n1. Testing empty slide:")
    empty_slide = Slide(
        slide_id="empty_001",
        slide_number=1,
        title="",
        slide_type="content_heavy",
        key_points=[]
    )
    
    request = LayoutGenerationRequest(slide=empty_slide)
    result = await orchestrator.generate_layout(request)
    
    print(f"   Success: {result.success}")
    print(f"   Error: {result.error_message}")
    print(f"   Fallback containers: {len(result.layout.containers)}")
    
    # Test 2: Invalid configuration
    print("\n2. Testing invalid configuration:")
    slide = create_test_slides()[0]
    request = LayoutGenerationRequest(
        slide=slide,
        layout_config=LayoutEngineConfig(
            max_iterations=0,  # Invalid
            white_space_min=0.8,  # Min > Max
            white_space_max=0.2
        )
    )
    
    result = await orchestrator.generate_layout(request)
    print(f"   Success: {result.success}")
    print(f"   Layout generated anyway: {len(result.layout.containers) > 0}")


async def run_all_tests():
    """Run all integration tests."""
    print("=== Three-Agent Layout Architect Integration Tests ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check environment
    print("\nEnvironment check:")
    google_key = os.getenv("GOOGLE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if google_key:
        print(f"✅ GOOGLE_API_KEY is set (length: {len(google_key)})")
    elif gemini_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(gemini_key)})")
    else:
        print("❌ No API keys found - tests will fail")
        return
    
    try:
        # Run individual agent tests
        await test_theme_agent()
        await test_structure_agent()
        await test_layout_engine()
        
        # Run orchestrator tests
        await test_orchestrator()
        
        # Run error handling tests
        await test_error_handling()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


async def test_specific_scenario():
    """Test a specific scenario for debugging."""
    print("\n=== Testing Specific Scenario ===")
    
    orchestrator = LayoutArchitectOrchestrator()
    
    # Create a complex slide
    slide = Slide(
        slide_id="complex_001",
        slide_number=1,
        title="Quarterly Performance Dashboard",
        slide_type="data_driven",
        narrative="Comprehensive view of Q4 performance metrics",
        key_points=[
            "Revenue: $12.5M (+23% YoY)",
            "Customer acquisition: 1,250 new customers",
            "Churn rate: 2.3% (down from 3.1%)",
            "NPS score: 72 (industry avg: 45)"
        ],
        analytics_needed="Revenue chart, customer growth chart, churn trend, NPS comparison",
        structure_preference="dashboard"
    )
    
    request = LayoutGenerationRequest(
        slide=slide,
        user_context={
            "brand": "DataCorp Analytics",
            "industry": "B2B SaaS",
            "preferences": {
                "data_visualization": "modern",
                "color_scheme": "professional"
            }
        }
    )
    
    print("Generating layout for complex dashboard slide...")
    result = await orchestrator.generate_layout(request)
    
    if result.success:
        print("\nLayout generation successful!")
        print(f"Theme: {result.theme.name}")
        print(f"\nContainers ({len(result.layout.containers)}):")
        for container in result.layout.containers:
            print(f"  - {container.id} ({container.type})")
            print(f"    Position: ({container.position.leftInset}, {container.position.topInset})")
            print(f"    Size: {container.position.width}×{container.position.height}")
        
        print(f"\nMetrics:")
        print(f"  White space: {result.layout.white_space_ratio:.2%}")
        print(f"  Balance score: {result.generation_metrics.get('balance_score', 'N/A')}")
        print(f"  Iterations: {result.generation_metrics.get('total_iterations', 'N/A')}")
    else:
        print(f"\nLayout generation failed: {result.error_message}")


if __name__ == "__main__":
    print("Starting Three-Agent Layout Architect tests...\n")
    
    # Run all tests
    asyncio.run(run_all_tests())
    
    # Optionally run specific scenario
    # asyncio.run(test_specific_scenario())