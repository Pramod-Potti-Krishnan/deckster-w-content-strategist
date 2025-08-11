#!/usr/bin/env python3
"""
Test the HTML post-processing logic directly
"""
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.content_agent.content_agent_v5 import (
    ContentBlock, TextContentV4
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_html_postprocessing():
    """Test the post-processing logic that should add HTML tags"""
    
    print("=== TESTING HTML POST-PROCESSING LOGIC ===\n")
    
    # Simulate what the AI might return - content without HTML tags
    test_cases = [
        {
            "name": "Title with HTML",
            "block": ContentBlock(
                role="title",
                content_html="<h1>The Healthcare Crisis: By the Numbers</h1>",
                content_text="The Healthcare Crisis: By the Numbers"
            ),
            "expected_tag": "h1"
        },
        {
            "name": "Heading without HTML tags",
            "block": ContentBlock(
                role="key_point_1_heading",
                content_html="Rising Healthcare Costs",  # No HTML tags!
                content_text="Rising Healthcare Costs"
            ),
            "expected_tag": "h3"
        },
        {
            "name": "Text without HTML tags",
            "block": ContentBlock(
                role="key_point_1_text",
                content_html="Healthcare costs have increased dramatically",  # No HTML tags!
                content_text="Healthcare costs have increased dramatically"
            ),
            "expected_tag": "p"
        },
        {
            "name": "Empty content_text but has content_html",
            "block": ContentBlock(
                role="key_point_2_heading",
                content_html="Medical Errors",  # No HTML tags!
                content_text=""  # Empty!
            ),
            "expected_tag": "h3"
        }
    ]
    
    # Container map (from required_elements)
    containers_map = {
        "title": "h1",
        "key_point_1_heading": "h3",
        "key_point_1_text": "p",
        "key_point_2_heading": "h3",
        "key_point_2_text": "p"
    }
    
    # Run the post-processing logic (copied from content_agent_v5.py)
    for test_case in test_cases:
        block = test_case["block"]
        print(f"Test: {test_case['name']}")
        print(f"  Role: {block.role}")
        print(f"  Original content_html: {repr(block.content_html)}")
        print(f"  Original content_text: {repr(block.content_text)}")
        
        # Check if HTML exists but doesn't contain actual HTML tags
        has_html_tags = block.content_html and block.content_html.strip().startswith('<')
        print(f"  Has HTML tags: {has_html_tags}")
        
        # Get the content (from either field)
        content = block.content_text or block.content_html or ""
        print(f"  Content to use: {repr(content)}")
        
        # If HTML is missing or doesn't have tags, generate it
        if not has_html_tags and content:
            # First try to get tag from containers map
            if block.role in containers_map:
                tag = containers_map[block.role]
                block.content_html = f"<{tag}>{content}</{tag}>"
                # Also ensure content_text is set
                if not block.content_text:
                    block.content_text = content
                print(f"  ✓ Generated HTML with tag '{tag}'")
            else:
                # Fallback: guess tag based on role
                if 'heading' in block.role.lower():
                    tag = 'h3'
                elif 'title' in block.role.lower():
                    tag = 'h1'
                else:
                    tag = 'p'
                block.content_html = f"<{tag}>{content}</{tag}>"
                # Also ensure content_text is set
                if not block.content_text:
                    block.content_text = content
                print(f"  ✓ Generated HTML with guessed tag '{tag}'")
        else:
            print(f"  → No changes needed")
        
        print(f"  Final content_html: {repr(block.content_html)}")
        print(f"  Final content_text: {repr(block.content_text)}")
        print()

if __name__ == "__main__":
    test_html_postprocessing()