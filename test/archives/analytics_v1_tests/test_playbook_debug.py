#!/usr/bin/env python3
"""
Debug test of playbook system
"""

import asyncio
import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Map GOOGLE_API_KEY to GEMINI_API_KEY if needed
if os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from src.agents.analytics_agent import create_analytics


async def test_playbook_debug():
    """Test with playbook implementation with debugging."""
    os.environ["USE_PLAYBOOK_SYSTEM"] = "true"
    
    # Reload module to pick up new setting
    import importlib
    import src.agents.analytics_agent
    importlib.reload(src.agents.analytics_agent)
    from src.agents.analytics_agent import create_analytics
    
    print("Testing PLAYBOOK implementation with debug...")
    
    try:
        result = await create_analytics(
            "Show me quarterly sales data for 2024",
            title="Q1-Q4 2024 Sales"
        )
        
        print(f"  Success: {result.get('success')}")
        print(f"  Chart type: {result.get('chart_type')}")
        print(f"  Format: {result.get('format')}")
        print(f"  Data points: {len(result.get('data', []))}")
        
        if not result.get('success'):
            print(f"  Error in metadata: {result.get('metadata', {}).get('error')}")
            
    except Exception as e:
        print(f"Exception caught: {e}")
        traceback.print_exc()


async def main():
    """Run debug test."""
    print("="*60)
    print("PLAYBOOK SYSTEM DEBUG TEST")
    print("="*60)
    
    await test_playbook_debug()
    
    print("\n" + "="*60)
    print("DEBUG TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())