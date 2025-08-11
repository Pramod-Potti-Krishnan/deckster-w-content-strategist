#!/usr/bin/env python3
"""
Debug test to check HTML generation in content_agent_v5
"""
import asyncio
import json
from pathlib import Path
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.layout_architect.agents.content_agent import content_agent_v5
from src.models.agents import Slide
from src.agents.layout_architect.model_types.design_tokens import ThemeDefinition
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_slide_3_html():
    """Test HTML generation for slide 3"""
    
    # Load mock strawman
    with open('test/mock_strawman.json', 'r') as f:
        strawman_data = json.load(f)
    
    # Get slide 3
    slide_data = strawman_data['slides'][2]  # Index 2 = slide 3
    slide = Slide(**slide_data)
    
    # Create mock theme
    theme = ThemeDefinition(
        color_palette=["#1a5f7a", "#3b82a0", "#5ba3c7", "#86c1df", "#b3d9ec"],
        font_primary="Inter",
        font_secondary="Open Sans",
        mood_keywords=["professional", "modern", "clean"]
    )
    
    # Run content generation
    result = await content_agent_v5.run_content_agent_v5(
        slide=slide,
        theme=theme,
        deck_summary="Healthcare digital transformation presentation"
    )
    
    # Debug output
    print("\n=== DEBUG: Text Content Blocks ===")
    for component in result.components:
        if component.component_type == "text" and hasattr(component.output, 'content_blocks'):
            print(f"Found {len(component.output.content_blocks)} text blocks")
            for i, block in enumerate(component.output.content_blocks):
                print(f"\nBlock {i + 1}:")
                print(f"  Role: {block.role}")
                print(f"  Content Text: {repr(block.content_text)}")
                print(f"  Content HTML: {repr(block.content_html)}")
                print(f"  HTML starts with <: {block.content_html.strip().startswith('<') if block.content_html else False}")
                
                # Check if it's a heading that should have h3
                if 'heading' in block.role.lower() and block.content_html:
                    if '<h3>' in block.content_html:
                        print("  ✓ Has h3 tag")
                    else:
                        print("  ✗ Missing h3 tag")

if __name__ == "__main__":
    asyncio.run(test_slide_3_html())