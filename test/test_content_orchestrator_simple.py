#!/usr/bin/env python3
"""
Simple test for Content Orchestrator - Testing just content generation
=====================================================================

This test bypasses theme generation and uses a predefined theme to test
the content generation pipeline directly.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from src.models.agents import PresentationStrawman
from src.agents.content_agent_v7 import ContentAgentV7
from src.models.design_tokens import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken, 
    DimensionToken, TokenValue, TokenType
)

async def test_content_generation():
    """Test content generation with predefined theme"""
    
    # Load mock strawman
    mock_path = Path(__file__).parent / "mock_strawman.json"
    with open(mock_path, 'r') as f:
        strawman_data = json.load(f)
    
    strawman = PresentationStrawman(**strawman_data)
    
    # Limit to first 2 slides for testing
    strawman.slides = strawman.slides[:2]
    
    # Create a simple theme
    theme = ThemeDefinition(
        name="Healthcare Professional",
        formality_level="high",
        complexity_allowance="detailed",
        design_tokens=DesignTokens(
            name="healthcare",
            description="Healthcare theme",
            colors={
                "primary": ColorToken(value="#0066CC", type=TokenType.COLOR),
                "secondary": ColorToken(value="#00A86B", type=TokenType.COLOR),
                "accent": ColorToken(value="#FF6B6B", type=TokenType.COLOR),
                "background": ColorToken(value="#F0F4F8", type=TokenType.COLOR),
                "text": ColorToken(value="#2D3748", type=TokenType.COLOR)
            },
            typography={
                "heading": TypographyToken(
                    fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=36, type=TokenType.FONT_SIZE),
                    fontWeight=TokenValue(value=700, type=TokenType.FONT_WEIGHT),
                    lineHeight=TokenValue(value=1.2, type=TokenType.LINE_HEIGHT)
                ),
                "body": TypographyToken(
                    fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                    fontSize=TokenValue(value=16, type=TokenType.FONT_SIZE),
                    fontWeight=TokenValue(value=400, type=TokenType.FONT_WEIGHT),
                    lineHeight=TokenValue(value=1.5, type=TokenType.LINE_HEIGHT)
                )
            },
            spacing={
                "xs": DimensionToken(value=4, type=TokenType.DIMENSION, unit="px"),
                "sm": DimensionToken(value=8, type=TokenType.DIMENSION, unit="px"),
                "md": DimensionToken(value=16, type=TokenType.DIMENSION, unit="px"),
                "lg": DimensionToken(value=24, type=TokenType.DIMENSION, unit="px"),
                "xl": DimensionToken(value=32, type=TokenType.DIMENSION, unit="px")
            },
            sizing={}
        ),
        layout_templates={},
        metadata={"test": True}
    )
    
    print("=" * 60)
    print("CONTENT GENERATION TEST")
    print("=" * 60)
    print(f"\nPresentation: {strawman.main_title}")
    print(f"Theme: {theme.name}")
    print(f"Slides to process: {len(strawman.slides)}")
    print()
    
    # Initialize content agent
    content_agent = ContentAgentV7()
    
    # Process each slide
    completed_slides = []
    
    for i, slide in enumerate(strawman.slides):
        print(f"\n{'='*60}")
        print(f"SLIDE {i+1}: {slide.title}")
        print(f"{'='*60}")
        
        try:
            # Generate content
            manifest = await content_agent.run(
                slide=slide,
                theme=theme,
                strawman=strawman,
                completed_slides=completed_slides,
                return_raw=False
            )
            
            # Display results
            print(f"\n✓ Content generated successfully!")
            # Handle title as either string or object with text attribute
            title_text = manifest.title if isinstance(manifest.title, str) else manifest.title.text
            print(f"  - Title: {title_text}")
            print(f"  - Word count: {manifest.total_word_count}")
            print(f"  - Content density: {manifest.content_density}")
            print(f"  - Has visual: {manifest.primary_visual is not None}")
            
            if manifest.main_points:
                print(f"\n  Main points ({len(manifest.main_points)}):")
                for j, point in enumerate(manifest.main_points[:3]):
                    point_text = point if isinstance(point, str) else point.text
                    print(f"    {j+1}. {point_text[:60]}...")
            
            if manifest.primary_visual:
                print(f"\n  Visual specification:")
                print(f"    - Type: {manifest.primary_visual.visual_type}")
                print(f"    - Archetype: {getattr(manifest.primary_visual, 'archetype', 'N/A')}")
                if hasattr(manifest.primary_visual, 'imagen_prompt'):
                    print(f"    - Prompt: {manifest.primary_visual.imagen_prompt[:80]}...")
            
            completed_slides.append(manifest)
            
        except Exception as e:
            print(f"\n✗ Error generating content: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}")
    print(f"\nSuccessfully generated content for {len(completed_slides)}/{len(strawman.slides)} slides")

if __name__ == "__main__":
    asyncio.run(test_content_generation())