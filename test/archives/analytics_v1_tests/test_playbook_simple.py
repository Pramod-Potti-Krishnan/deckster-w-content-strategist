#!/usr/bin/env python3
"""
Simple test of playbook system
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Map GOOGLE_API_KEY to GEMINI_API_KEY if needed
if os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.analytics_agent import create_analytics


async def test_original():
    """Test with original implementation."""
    os.environ["USE_PLAYBOOK_SYSTEM"] = "false"
    
    print("Testing ORIGINAL implementation...")
    result = await create_analytics(
        "Show me monthly sales trend for 2024",
        title="Monthly Sales 2024"
    )
    
    print(f"  Success: {result.get('success')}")
    print(f"  Chart type: {result.get('chart_type')}")
    print(f"  Format: {result.get('format')}")
    print(f"  Data points: {len(result.get('data', []))}")
    print(f"  Has content: {bool(result.get('content'))}")
    

async def test_playbook():
    """Test with playbook implementation."""
    os.environ["USE_PLAYBOOK_SYSTEM"] = "true"
    
    # Reload module to pick up new setting
    import importlib
    import src.agents.analytics_agent
    importlib.reload(src.agents.analytics_agent)
    from src.agents.analytics_agent import create_analytics
    
    print("\nTesting PLAYBOOK implementation...")
    result = await create_analytics(
        "Show me monthly sales trend for 2024",
        title="Monthly Sales 2024"
    )
    
    print(f"  Success: {result.get('success')}")
    print(f"  Chart type: {result.get('chart_type')}")
    print(f"  Format: {result.get('format')}")
    print(f"  Data points: {len(result.get('data', []))}")
    print(f"  Has content: {bool(result.get('content'))}")


async def main():
    """Run both tests."""
    print("="*60)
    print("PLAYBOOK SYSTEM SIMPLE TEST")
    print("="*60)
    
    # Test original
    await test_original()
    
    # Test playbook
    await test_playbook()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())