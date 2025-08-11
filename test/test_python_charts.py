#!/usr/bin/env python
"""
Test Python Chart Generation
=============================
Quick test to verify Python charts with axis labels are working correctly.
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


async def test_python_charts():
    """Test Python chart generation with proper axis labels."""
    
    print("\n" + "="*60)
    print("TESTING PYTHON CHARTS WITH AXIS LABELS")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "title": "Monthly Sales Trend",
            "description": "Monthly sales: Jan $45K, Feb $52K, Mar $48K, Apr $61K, May $58K, Jun $72K",
            "chart_type": "line"
        },
        {
            "title": "Product Category Sales",
            "description": "Sales by category: Electronics $450K, Clothing $320K, Home $280K, Sports $195K",
            "chart_type": "bar"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}] Testing: {test_case['title']}")
        print(f"Type: {test_case['chart_type']}")
        print(f"Description: {test_case['description']}")
        
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
                    # Check image size
                    import base64
                    img_data = base64.b64decode(result['content'])
                    print(f"📊 Generated {len(img_data):,} byte image")
                else:
                    print(f"📝 Generated {result['format']} content")
                    if len(result['content']) < 500:
                        print("Content preview:")
                        print("-" * 40)
                        print(result['content'][:400])
                        print("-" * 40)
                        
                print(f"💡 Insights:")
                for insight in result.get('insights', [])[:2]:
                    print(f"  - {insight}")
                    
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        print()


if __name__ == "__main__":
    asyncio.run(test_python_charts())