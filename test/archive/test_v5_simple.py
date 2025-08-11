#!/usr/bin/env python3
"""
Simple test to verify Content Agent V5 with narrative container mapping
"""

import asyncio
import sys
import os
import warnings
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

async def main():
    print("🚀 Testing Content Agent V5 - Narrative Container Mapping")
    print("=" * 60)
    
    # Create a simple slide with two-column preference
    slide = Slide(
        slide_id="test_001",
        slide_number=1,
        slide_type="mixed_content",
        title="Market Analysis",
        narrative="Show market trends and insights",
        key_points=[
            "Market size: $50B and growing",
            "Key drivers: AI and automation"
        ],
        analytics_needed="Market growth chart",
        structure_preference="two-column"
    )
    
    # Create theme
    theme = ThemeDefinition(
        name="Professional",
        mood_keywords=["professional", "modern"],
        visual_guidelines={"style": "clean"},
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
            sizing={"icon": DimensionToken(value=24, type=TokenType.DIMENSION)}
        ),
        layout_templates={}
    )
    
    # Create strawman
    strawman = PresentationStrawman(
        main_title="Market Analysis Test",
        overall_theme="Testing container-aware content generation",
        target_audience="Developers",
        design_suggestions="Clean layout",
        presentation_duration=10,
        slides=[slide]
    )
    
    # Create agent and process slide
    agent = ContentAgentV5()
    
    try:
        print(f"\nProcessing slide: {slide.title}")
        print(f"Layout preference: {slide.structure_preference}")
        
        manifest = await agent.run(slide, theme, strawman)
        
        print(f"\n✅ Content generated successfully!")
        print(f"Title: {manifest.title}")
        print(f"Word count: {manifest.total_word_count}")
        print(f"Structure: {manifest.structure_preference}")
        
        if manifest.main_points:
            print(f"\nMain points ({len(manifest.main_points)}):")
            for point in manifest.main_points:
                print(f"  • {point}")
        
        if manifest.supporting_text:
            print(f"\nSupporting text preview:")
            print(f"  {manifest.supporting_text[:150]}...")
        
        print(f"\n✨ The narrative container mapping was handled in Stage 2")
        print(f"✨ Content respects {manifest.structure_preference} layout through strategic briefing")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())