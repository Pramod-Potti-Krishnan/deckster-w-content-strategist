"""
Test script for enhanced Theme and Content Agents collaboration.

This script tests the theme-aware content generation workflow:
1. Create a sample strawman
2. Generate a comprehensive theme using Theme Agent
3. Use the theme to generate content with Content Agent
"""

import asyncio
import json
from typing import List

from src.models.agents import PresentationStrawman, Slide
from src.agents.layout_architect.agents.theme_agent.agent import ThemeAgent
from src.agents.layout_architect.agents.content_agent.agent import ContentAgent


def create_sample_strawman() -> PresentationStrawman:
    """Create a sample strawman for testing"""
    
    slides = [
        Slide(
            slide_id="slide_001",
            slide_type="title_slide",
            title="Digital Transformation Strategy 2025",
            key_points=[
                "Leveraging AI for Business Growth",
                "Cloud-First Architecture",
                "Data-Driven Decision Making"
            ],
            narrative="Introduce our comprehensive digital transformation roadmap"
        ),
        Slide(
            slide_id="slide_002",
            slide_type="data_driven",
            title="Market Opportunity Analysis",
            key_points=[
                "Cloud computing market growing at 15.7% CAGR",
                "89% of enterprises adopting multi-cloud",
                "$1.5 trillion market by 2027"
            ],
            narrative="Present compelling market data showing growth opportunity",
            analytics_needed="Market growth trends and adoption statistics"
        ),
        Slide(
            slide_id="slide_003",
            slide_type="visual_heavy",
            title="Our Technology Stack",
            key_points=[
                "Modern microservices architecture",
                "AI-powered analytics platform",
                "Real-time data processing"
            ],
            narrative="Showcase our advanced technology capabilities",
            visuals_needed="Technology architecture diagram"
        ),
        Slide(
            slide_id="slide_004",
            slide_type="diagram_focused",
            title="Implementation Roadmap",
            key_points=[
                "Q1: Foundation - Infrastructure setup",
                "Q2: Core Platform - Service deployment",
                "Q3: AI Integration - ML models",
                "Q4: Scale & Optimize - Performance tuning"
            ],
            narrative="Detail the phased implementation approach",
            diagrams_needed="Quarterly roadmap with milestones"
        ),
        Slide(
            slide_id="slide_005",
            slide_type="content_heavy",
            title="Key Success Factors",
            key_points=[
                "Executive sponsorship and alignment",
                "Cross-functional collaboration",
                "Continuous learning culture",
                "Agile methodology adoption"
            ],
            narrative="Explain critical factors for successful transformation"
        )
    ]
    
    return PresentationStrawman(
        main_title="Digital Transformation Strategy 2025",
        overall_theme="Modern, data-driven, and innovative - showcasing technological leadership with compelling visuals and clear strategic direction",
        design_suggestions="Use a modern tech aesthetic with blues and teals, clean sans-serif fonts, data visualizations, and futuristic imagery",
        target_audience="Executive leadership team and board members",
        presentation_duration=20,
        slides=slides
    )


async def test_theme_generation():
    """Test Theme Agent generation"""
    print("\n=== Testing Theme Agent ===\n")
    
    # Create strawman
    strawman = create_sample_strawman()
    print(f"Created strawman with {len(strawman.slides)} slides")
    print(f"Overall theme: {strawman.overall_theme}")
    print(f"Target audience: {strawman.target_audience}")
    
    # Initialize Theme Agent
    theme_agent = ThemeAgent()
    
    # Generate theme
    print("\nGenerating comprehensive theme...")
    theme = await theme_agent.generate_theme(
        strawman=strawman,
        session_id="test_session_001"
    )
    
    print(f"\n✓ Generated theme: {theme.name}")
    print(f"  - Mood keywords: {', '.join(theme.mood_keywords[:5])}")
    print(f"  - Primary color: {theme.design_tokens.colors.get('primary', {}).value if 'primary' in theme.design_tokens.colors else 'N/A'}")
    print(f"  - Formality level: {theme.formality_level}")
    print(f"  - Visual guidelines: {list(theme.visual_guidelines.keys())}")
    print(f"  - Layout templates: {list(theme.layout_templates.keys())}")
    
    return theme, strawman


async def test_content_generation(theme, strawman):
    """Test Content Agent with theme integration"""
    print("\n=== Testing Content Agent ===\n")
    
    # Create deck summary
    deck_summary = """
    This presentation outlines our comprehensive digital transformation strategy for 2025,
    focusing on leveraging cutting-edge AI technologies, cloud-first architecture, and 
    data-driven decision making. We'll demonstrate the significant market opportunity,
    showcase our advanced technology stack, and provide a clear implementation roadmap
    with key success factors for executive alignment.
    
    The narrative progresses from market opportunity through our capabilities to concrete
    implementation plans, building confidence in our ability to lead digital transformation
    and capture significant market share in the rapidly growing cloud and AI markets.
    """
    
    # Initialize Content Agent
    content_agent = ContentAgent()
    
    # Test content generation for different slide types
    test_slides = [
        strawman.slides[0],  # title_slide
        strawman.slides[1],  # data_driven
        strawman.slides[2],  # visual_heavy
        strawman.slides[3],  # diagram_focused
    ]
    
    for slide in test_slides:
        print(f"\nGenerating content for {slide.slide_type}: {slide.title}")
        
        manifest = await content_agent.prepare_content(
            slide=slide,
            deck_summary=deck_summary,
            theme=theme,
            strawman_metadata={
                "main_title": strawman.main_title,
                "overall_theme": strawman.overall_theme,
                "design_suggestions": strawman.design_suggestions,
                "target_audience": strawman.target_audience
            },
            session_id="test_session_001"
        )
        
        print(f"✓ Generated content manifest:")
        print(f"  - Title: {manifest.title.text} ({manifest.title.word_count} words)")
        print(f"  - Main points: {len(manifest.main_points)}")
        print(f"  - Total words: {manifest.total_word_count}/{manifest.word_count_limit}")
        print(f"  - Content density: {manifest.content_density}")
        print(f"  - Theme elements applied: {manifest.theme_elements_applied}")
        print(f"  - Deck context used: {manifest.deck_context_used}")
        
        if manifest.title.sources:
            print(f"  - Sources used: {len(manifest.title.sources)}")
        
        if manifest.primary_visual:
            print(f"  - Primary visual: {manifest.primary_visual.visual_type}")
            if manifest.primary_visual.theme_colors_used:
                print(f"    - Theme colors: {manifest.primary_visual.theme_colors_used}")
            if manifest.primary_visual.chart_type:
                print(f"    - Chart type: {manifest.primary_visual.chart_type}")
            if manifest.primary_visual.diagram_type:
                print(f"    - Diagram type: {manifest.primary_visual.diagram_type}")


async def main():
    """Run all tests"""
    print("Starting enhanced agents test...\n")
    
    try:
        # Test Theme Agent
        theme, strawman = await test_theme_generation()
        
        # Test Content Agent with theme
        await test_content_generation(theme, strawman)
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())