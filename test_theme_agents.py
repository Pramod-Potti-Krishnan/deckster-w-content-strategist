#!/usr/bin/env python3
"""
Test script for Theme Agents.
Verifies that both SimplifiedThemeAgent and ToolFreeThemeAgent work correctly.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.agents import PresentationStrawman, Slide

async def test_theme_agents():
    """Test both theme agents with a simple strawman."""
    
    # Create a simple strawman for testing
    strawman = PresentationStrawman(
        main_title="AI Technology Trends 2024",
        executive_summary="An overview of emerging AI technologies and their impact on business",
        target_audience="Technology executives and decision makers",
        presentation_duration="15",
        theme="Technology Innovation",
        narrative_flow="problem-solution",
        structure_preference="visual-heavy",
        overall_theme="Cutting-edge AI advancements",
        design_suggestions="Modern, clean, tech-forward design",
        slides=[
            Slide(
                slide_number=1,
                slide_id="slide_1",
                title="The AI Revolution",
                slide_type="title_slide",
                narrative="AI is transforming every industry",
                key_points=["AI adoption statistics", "Key transformation areas"]
            ),
            Slide(
                slide_number=2,
                slide_id="slide_2", 
                title="Key AI Technologies",
                slide_type="content_heavy",
                narrative="Three technologies leading the change",
                key_points=["Generative AI", "Computer Vision", "Natural Language Processing"]
            )
        ]
    )
    
    print("=" * 60)
    print("THEME AGENT TESTING")
    print("=" * 60)
    
    # Test 1: ToolFreeThemeAgent
    print("\n1. Testing ToolFreeThemeAgent (no external tools)...")
    print("-" * 40)
    
    try:
        from src.agents.theme_agent import ToolFreeThemeAgent
        tool_free_agent = ToolFreeThemeAgent()
        print("✓ ToolFreeThemeAgent instantiated successfully")
        
        theme1 = await tool_free_agent.generate_theme(
            strawman=strawman,
            session_id="test_session_tool_free",
            director_metadata={
                "formality_level": "medium",
                "complexity_allowance": "detailed"
            }
        )
        
        print(f"✓ Theme generated successfully: '{theme1.name}'")
        print(f"  - Design tokens: {hasattr(theme1, 'design_tokens')}")
        
        if hasattr(theme1, 'design_tokens') and theme1.design_tokens:
            if hasattr(theme1.design_tokens, 'colors'):
                print(f"  - Colors: {list(theme1.design_tokens.colors.keys())}")
                # Print first color value
                first_color = list(theme1.design_tokens.colors.keys())[0]
                print(f"    Example: {first_color} = {theme1.design_tokens.colors[first_color].value}")
            
            if hasattr(theme1.design_tokens, 'typography'):
                print(f"  - Typography: {list(theme1.design_tokens.typography.keys())}")
                # Print first typography
                first_typo = list(theme1.design_tokens.typography.keys())[0]
                typo_token = theme1.design_tokens.typography[first_typo]
                print(f"    Example: {first_typo} = {typo_token.fontFamily.value if hasattr(typo_token, 'fontFamily') else 'N/A'}")
        
        print(f"  - Formality: {theme1.formality_level}")
        print(f"  - Complexity: {theme1.complexity_allowance}")
        
    except Exception as e:
        print(f"✗ ToolFreeThemeAgent failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: SimplifiedThemeAgent  
    print("\n\n2. Testing SimplifiedThemeAgent (with tools)...")
    print("-" * 40)
    
    try:
        from src.agents.theme_agent import SimplifiedThemeAgent
        simplified_agent = SimplifiedThemeAgent()
        print("✓ SimplifiedThemeAgent instantiated successfully")
        
        theme2 = await simplified_agent.generate_theme(
            strawman=strawman,
            session_id="test_session_simplified",
            director_metadata={
                "formality_level": "high",
                "complexity_allowance": "executive"
            }
        )
        
        print(f"✓ Theme generated successfully: '{theme2.name}'")
        print(f"  - Design tokens: {hasattr(theme2, 'design_tokens')}")
        
        if hasattr(theme2, 'design_tokens') and theme2.design_tokens:
            if hasattr(theme2.design_tokens, 'colors'):
                print(f"  - Colors: {list(theme2.design_tokens.colors.keys())}")
                # Print first color value
                first_color = list(theme2.design_tokens.colors.keys())[0]
                print(f"    Example: {first_color} = {theme2.design_tokens.colors[first_color].value}")
            
            if hasattr(theme2.design_tokens, 'typography'):
                print(f"  - Typography: {list(theme2.design_tokens.typography.keys())}")
                # Print first typography
                first_typo = list(theme2.design_tokens.typography.keys())[0]
                typo_token = theme2.design_tokens.typography[first_typo]
                print(f"    Example: {first_typo} = {typo_token.fontFamily.value if hasattr(typo_token, 'fontFamily') else 'N/A'}")
        
        print(f"  - Formality: {theme2.formality_level}")
        print(f"  - Complexity: {theme2.complexity_allowance}")
        
    except Exception as e:
        print(f"✗ SimplifiedThemeAgent failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Import test in ContentOrchestrator style
    print("\n\n3. Testing ContentOrchestrator-style imports...")
    print("-" * 40)
    
    try:
        # Test the exact import pattern used in ContentOrchestrator
        from src.agents.theme_agent import SimplifiedThemeAgent
        print("✓ SimplifiedThemeAgent import successful")
        
        from src.agents.theme_agent import ToolFreeThemeAgent
        print("✓ ToolFreeThemeAgent import successful")
        
        # Test dynamic import as in ContentOrchestrator
        use_tool_free = True
        if use_tool_free:
            from src.agents.theme_agent import ToolFreeThemeAgent
            agent = ToolFreeThemeAgent(model_name="gemini-2.0-flash-exp")
        else:
            agent = SimplifiedThemeAgent(model_name="gemini-2.0-flash-exp")
        
        print("✓ Dynamic agent selection successful")
        print(f"  - Selected agent type: {type(agent).__name__}")
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_theme_agents())