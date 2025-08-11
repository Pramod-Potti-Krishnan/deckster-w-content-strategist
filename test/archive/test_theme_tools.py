#!/usr/bin/env python3
"""
Simple test to verify theme agent tools are working
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.theme_agent.tools import (
    EnhancedColorPaletteGenerator,
    PresentationFontPairing,
    ColorPaletteInput,
    FontPairingInput
)

async def test_tools():
    """Test the tools directly"""
    print("Testing Theme Agent Tools\n")
    
    # Test color palette generator
    print("1. Testing Color Palette Generator:")
    color_gen = EnhancedColorPaletteGenerator()
    color_input = ColorPaletteInput(
        presentation_context="technology",
        mood_description="innovative and modern",
        accessibility_level="AA"
    )
    
    color_output = color_gen.generate_enhanced_palette(color_input)
    print(f"   Colors generated: {list(color_output.colors.keys())}")
    print(f"   Primary color: {color_output.colors.get('primary')}")
    print(f"   Color harmony: {color_output.color_harmony}")
    print(f"   Has rationale: {bool(color_output.rationale)}")
    
    # Test font pairing
    print("\n2. Testing Font Pairing:")
    font_pairing = PresentationFontPairing()
    font_input = FontPairingInput(
        formality_level="medium",
        presentation_context="technology presentation",
        viewing_context="projection",
        complexity_level="detailed"
    )
    
    font_output = font_pairing.find_optimal_pairing(font_input)
    print(f"   Heading font: {font_output.heading_font}")
    print(f"   Body font: {font_output.body_font}")
    print(f"   Font sizes: {list(font_output.font_sizes.keys())}")
    print(f"   Has rationale: {bool(font_output.pairing_rationale)}")
    
    print("\n3. Testing SimplifiedThemeAgent:")
    from src.agents.layout_architect.agents.theme_agent.agent import SimplifiedThemeAgent
    from src.models.agents import PresentationStrawman, Slide
    
    # Create a simple strawman
    strawman = PresentationStrawman(
        main_title="AI Innovation Summit",
        overall_theme="Modern technology and innovation",
        design_suggestions="Clean and futuristic",
        target_audience="Tech executives",
        presentation_duration=20,
        slides=[
            Slide(
                slide_id="1",
                slide_number=1,
                slide_type="title",
                title="AI Innovation Summit",
                key_points=["Welcome"]
            )
        ]
    )
    
    # Create theme agent
    theme_agent = SimplifiedThemeAgent()
    
    try:
        # Generate theme
        theme = await theme_agent.generate_theme(
            strawman=strawman,
            session_id="test_session",
            director_metadata={
                "formality_level": "high",
                "complexity_allowance": "executive"
            }
        )
        
        print(f"   Theme name: {theme.name}")
        print(f"   Has design tokens: {hasattr(theme, 'design_tokens')}")
        if hasattr(theme, 'design_tokens') and hasattr(theme.design_tokens, 'colors'):
            print(f"   Color count: {len(theme.design_tokens.colors)}")
        print(f"   Generation method: {theme.metadata.get('generation_method', 'unknown')}")
        
    except Exception as e:
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tools())