#!/usr/bin/env python3
"""
Quick test to verify table generation is working
"""
import asyncio
import json
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.layout_architect.agents.content_agent import content_agent_v5
from src.models.agents import Slide
from src.agents.layout_architect.model_types.design_tokens import ThemeDefinition
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_table_generation():
    """Test that tables are properly generated for slide 3"""
    
    # Load mock strawman
    with open('test/mock_strawman.json', 'r') as f:
        strawman_data = json.load(f)
    
    # Get slide 3 which has tables_needed
    slide_data = strawman_data['slides'][2]  # Index 2 = slide 3
    slide = Slide(**slide_data)
    
    print(f"\n=== Testing Table Generation for Slide 3 ===")
    print(f"Title: {slide.title}")
    print(f"Tables Needed: {slide.tables_needed}")
    
    # Create simple theme
    theme = ThemeDefinition(
        color_palette=["#1a5f7a", "#3b82a0"],
        font_primary="Inter",
        font_secondary="Open Sans",
        mood_keywords=["professional", "modern"]
    )
    
    # Run content generation
    print("\nRunning content generation...")
    result = await content_agent_v5.run_content_agent_v5(
        slide=slide,
        theme=theme,
        deck_summary="Healthcare digital transformation"
    )
    
    # Check for table component
    table_found = False
    for component in result.components:
        if component.component_type == "table":
            table_found = True
            print(f"\n✓ Table component found!")
            
            if hasattr(component.output, 'html_table'):
                if component.output.html_table:
                    print(f"✓ HTML table generated!")
                    print(f"  First 200 chars: {component.output.html_table[:200]}...")
                else:
                    print(f"✗ HTML table is empty!")
            
            if hasattr(component.output, 'headers'):
                print(f"✓ Headers: {component.output.headers}")
            
            if hasattr(component.output, 'rows'):
                print(f"✓ Rows: {len(component.output.rows)} rows")
                if component.output.rows:
                    print(f"  First row: {component.output.rows[0]}")
    
    if not table_found:
        print("\n✗ ERROR: No table component found in output!")
        print(f"Components found: {[c.component_type for c in result.components]}")
    
    return table_found

if __name__ == "__main__":
    success = asyncio.run(test_table_generation())
    sys.exit(0 if success else 1)