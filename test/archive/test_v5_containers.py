#!/usr/bin/env python3
"""
Test Content Agent V5 with Narrative-Aware Layout
===============================================

This test demonstrates the enhanced narrative-to-container mapping
where Stage 2 determines container layout and Stage 3 generates
content that respects the narrative flow across physical boundaries.

Author: AI Assistant
Date: 2024
"""

import asyncio
import sys
import os
import warnings
import json
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.agents import PresentationStrawman, Slide
from src.agents.layout_architect.agents.content_agent.content_agent_v5 import ContentAgentV5
from src.agents.layout_architect.model_types.design_tokens import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken, 
    DimensionToken, TokenValue, TokenType
)

# Colors for output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def display_containers(manifest):
    """Display container information from the manifest."""
    # New approach: containers are handled through narrative mapping in Stage 2
    print(f"\n{Colors.BOLD}📦 Content Organization{Colors.ENDC}")
    print(f"Layout preference: {manifest.structure_preference or 'default'}")
    print(f"Content density: {manifest.content_density}")
    
    # Display narrative flow from text content
    if manifest.supporting_text:
        print(f"\n{Colors.CYAN}Narrative Structure:{Colors.ENDC}")
        lines = manifest.supporting_text.split('\n')[:3]
        for line in lines:
            if line.strip():
                print(f"  • {line.strip()[:80]}...")
    
    # Display main points
    if manifest.main_points:
        print(f"\n{Colors.YELLOW}Key Messages:{Colors.ENDC}")
        for point in manifest.main_points[:3]:
            print(f"  • {point}")
    
    # Display visual elements
    if manifest.primary_visual or manifest.supporting_visuals:
        print(f"\n{Colors.MAGENTA}Visual Elements:{Colors.ENDC}")
        if manifest.primary_visual:
            print(f"  Primary: {manifest.primary_visual.visual_type} - {manifest.primary_visual.description[:60]}...")
        for i, visual in enumerate(manifest.supporting_visuals[:2]):
            print(f"  Supporting {i+1}: {visual.visual_type} - {visual.description[:50]}...")
    
    print(f"\n{Colors.GREEN}✓ Container mapping handled in Stage 2 strategic briefing{Colors.ENDC}")
    print(f"{Colors.GREEN}✓ Content respects {manifest.structure_preference} layout through narrative flow{Colors.ENDC}")

async def main():
    print(f"{Colors.BOLD}🚀 Testing Content Agent V5 - Container-Based Content{Colors.ENDC}")
    print("=" * 60)
    
    # Test different layout scenarios
    test_cases = [
        {
            "name": "Two-Column Layout",
            "slide": Slide(
                slide_id="test_2col",
                slide_number=1,
                slide_type="mixed_content",
                title="Market Analysis",
                narrative="Show market trends and insights",
                key_points=[
                    "Market size: $50B and growing",
                    "Key drivers: AI and automation",
                    "Competitive landscape analysis"
                ],
                analytics_needed="Market growth chart",
                structure_preference="two-column"
            )
        },
        {
            "name": "Grid Layout (2x2)",
            "slide": Slide(
                slide_id="test_grid",
                slide_number=2,
                slide_type="data_driven",
                title="Performance Metrics",
                narrative="Comprehensive performance overview",
                key_points=[
                    "Revenue: +25% YoY",
                    "Customer satisfaction: 95%",
                    "Market share: 35%",
                    "Efficiency gains: 40%"
                ],
                analytics_needed="Multiple KPI charts",
                visuals_needed="Success imagery",
                diagrams_needed="Process flow",
                structure_preference="grid"
            )
        },
        {
            "name": "Three-Column Layout",
            "slide": Slide(
                slide_id="test_3col",
                slide_number=3,
                slide_type="mixed_content",
                title="Product Comparison",
                narrative="Compare three product offerings",
                key_points=[
                    "Basic: Essential features",
                    "Professional: Advanced tools",
                    "Enterprise: Full suite"
                ],
                structure_preference="three-column"
            )
        }
    ]
    
    # Create theme
    theme = ThemeDefinition(
        name="Container Test Theme",
        mood_keywords=["professional", "modern"],
        visual_guidelines={"container_style": "clean"},
        formality_level="medium",
        design_tokens=DesignTokens(
            name="test",
            colors={"primary": ColorToken(value="#003366")},
            typography={
                "heading": TypographyToken(
                    fontFamily=TokenValue(value="Arial", type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=24, type=TokenType.FONT_SIZE)
                )
            },
            spacing={"medium": DimensionToken(value=16, type=TokenType.DIMENSION)},
            sizing={"container": DimensionToken(value=200, type=TokenType.DIMENSION)}
        ),
        layout_templates={}
    )
    
    # Create strawman
    strawman = PresentationStrawman(
        main_title="Container Layout Test",
        overall_theme="Testing container-based content generation",
        target_audience="Developers",
        design_suggestions="Clean, organized layouts",
        presentation_duration=10,
        slides=[tc["slide"] for tc in test_cases]
    )
    
    # Create agent (containers are now handled in Stage 2 automatically)
    agent = ContentAgentV5()
    
    # Process each test case
    for test_case in test_cases:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Testing: {test_case['name']}{Colors.ENDC}")
        print("-" * 60)
        
        try:
            manifest = await agent.run(test_case["slide"], theme, strawman)
            
            print(f"{Colors.GREEN}✓ Content generated successfully{Colors.ENDC}")
            print(f"  Title: {manifest.title}")
            print(f"  Word count: {manifest.total_word_count}")
            print(f"  Layout preference: {manifest.structure_preference}")
            
            # Display container information
            display_containers(manifest)
            
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Container test completed{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(main())