#!/usr/bin/env python
"""
Test Mermaid Chart Fix
======================
Quick test to verify Mermaid charts are working correctly.
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


async def test_mermaid_chart():
    """Test Mermaid chart generation with month labels."""
    
    print("\n" + "="*60)
    print("TESTING MERMAID CHART WITH MONTH LABELS")
    print("="*60)
    
    # Test case with month data
    test_case = {
        "title": "Monthly Sales Trend",
        "description": "Monthly sales: Jan $45K, Feb $52K, Mar $48K, Apr $61K, May $58K, Jun $72K",
        "chart_type": "line"
    }
    
    print(f"\n📊 Testing: {test_case['title']}")
    print(f"Description: {test_case['description']}")
    
    try:
        result = await create_analytics(
            test_case['description'],
            title=test_case['title'],
            chart_type=test_case['chart_type'],
            mcp_tool=pydantic_mcp_executor
        )
        
        if result['success']:
            print(f"\n✅ Success! Format: {result['format']}")
            
            if result['format'] == 'mermaid':
                print("\n📝 Generated Mermaid Code:")
                print("-" * 40)
                print(result['content'])
                print("-" * 40)
                
                # Check for duplicates
                mermaid_code = result['content']
                if 'x-axis' in mermaid_code:
                    x_axis_line = [line for line in mermaid_code.split('\n') if 'x-axis' in line][0]
                    print(f"\nX-axis line: {x_axis_line}")
                    
                    # Count occurrences of "Jan"
                    jan_count = x_axis_line.count('"Jan"')
                    if jan_count > 1:
                        print(f"⚠️  WARNING: 'Jan' appears {jan_count} times - DUPLICATE DATA!")
                    else:
                        print(f"✅ No duplicates - 'Jan' appears {jan_count} time")
                        
            print(f"\n💡 Insights:")
            for insight in result.get('insights', [])[:3]:
                print(f"  - {insight}")
                
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mermaid_chart())