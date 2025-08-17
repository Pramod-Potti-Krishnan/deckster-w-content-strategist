#!/usr/bin/env python
"""
Test Pie Chart Generation
=========================
Test the improved pie chart with darker colors and white borders.
"""

import os
import sys
import asyncio
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics
from src.agents.analytics_utils.pydantic_mcp_server import pydantic_mcp_executor


async def test_pie_chart():
    """Test pie chart generation."""
    
    print("\n" + "="*60)
    print("TESTING IMPROVED PIE CHART")
    print("="*60)
    
    test_cases = [
        {
            "title": "Market Share Analysis",
            "description": "Market share: Our Company 35%, Competitor A 28%, Competitor B 20%, Competitor C 12%, Others 5%",
            "chart_type": "pie"
        },
        {
            "title": "Budget Allocation",
            "description": "Budget distribution: R&D 30%, Marketing 25%, Operations 20%, Sales 15%, Admin 10%",
            "chart_type": "pie"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}] Testing: {test_case['title']}")
        print(f"Type: {test_case['chart_type']}")
        
        try:
            result = await create_analytics(
                test_case['description'],
                title=test_case['title'],
                chart_type=test_case['chart_type'],
                mcp_tool=pydantic_mcp_executor
            )
            
            if result['success']:
                print(f"✅ Success! Format: {result['format']}")
                
                if result['format'] == 'base64':
                    import base64
                    img_data = base64.b64decode(result['content'])
                    print(f"📊 Generated {len(img_data):,} byte image")
                else:
                    print(f"Format: {result['format']}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_pie_chart())