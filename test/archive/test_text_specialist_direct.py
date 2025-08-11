#!/usr/bin/env python3
"""
Direct test of run_text_specialist_v4 to debug HTML generation
"""
import asyncio
import json
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.content_agent.content_agent_v5 import (
    run_text_specialist_v4, StrategicBrief
)
from src.models.agents import Slide
from src.utils.logger import setup_logger

# Simple mock for ThemeDefinition
class MockTheme:
    def __init__(self):
        self.mood_keywords = ["professional", "clean"]

logger = setup_logger(__name__)

async def test_text_specialist_html():
    """Test HTML generation in text specialist"""
    
    # Create synthetic strategic brief with containers
    brief = StrategicBrief(
        component_type="text",
        playbook_key="content_heavy",
        detailed_instruction="""Create text content for a healthcare crisis slide.
You must create content for each container specified in required_elements.
Each content block should have the role, content_html with proper HTML tags, and content_text.""",
        required_elements={
            "narrative_arc": "Topic Introduction / Deep Dive / Synthesis",
            "containers": [
                {"role": "title", "tag": "h1", "word_limit": 10},
                {"role": "key_point_1_heading", "tag": "h3", "word_limit": 5},
                {"role": "key_point_1_text", "tag": "p", "word_limit": 20},
                {"role": "key_point_2_heading", "tag": "h3", "word_limit": 5},
                {"role": "key_point_2_text", "tag": "p", "word_limit": 20}
            ],
            "purpose": "To provide detailed information"
        },
        style_guidelines={
            "tone": "Professional, informative",
            "layout_adaptations": json.dumps({"two_column": "Split content between columns"})
        },
        constraints=[
            "Follow word limits exactly",
            "Generate HTML for each content block",
            "Ensure content flows naturally"
        ]
    )
    
    # Create simple slide
    slide = Slide(
        slide_number=1,
        slide_id="test_001",
        title="Healthcare Crisis Test",
        slide_type="content_heavy",
        narrative="Test slide for HTML generation",
        key_points=["Rising costs", "Medical errors"]
    )
    
    # Create minimal theme
    theme = MockTheme()
    
    print("=== RUNNING TEXT SPECIALIST ===")
    print(f"Brief playbook: {brief.playbook_key}")
    print(f"Containers: {len(brief.required_elements.get('containers', []))}")
    
    # Run the text specialist
    result = await run_text_specialist_v4(
        brief=brief,
        slide=slide,
        theme=theme,
        deck_summary="Test deck for healthcare"
    )
    
    print("\n=== CONTENT BLOCKS OUTPUT ===")
    for i, block in enumerate(result.content_blocks):
        print(f"\nBlock {i + 1}:")
        print(f"  Role: {block.role}")
        print(f"  Content Text: {repr(block.content_text)}")
        print(f"  Content HTML: {repr(block.content_html)}")
        
        # Check for HTML tags
        if block.content_html:
            has_opening_tag = block.content_html.strip().startswith('<')
            has_h3 = '<h3>' in block.content_html
            has_h1 = '<h1>' in block.content_html
            has_p = '<p>' in block.content_html
            
            print(f"  Has opening tag (<): {has_opening_tag}")
            if has_h1:
                print("  ✓ Contains <h1> tag")
            if has_h3:
                print("  ✓ Contains <h3> tag")
            if has_p:
                print("  ✓ Contains <p> tag")
            if not (has_opening_tag or has_h1 or has_h3 or has_p):
                print("  ✗ NO HTML TAGS FOUND!")

if __name__ == "__main__":
    asyncio.run(test_text_specialist_html())