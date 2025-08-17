#!/usr/bin/env python
"""
Test Treemap Generation
=======================
Debug why treemap is not generating as an image.
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


async def test_treemap():
    """Test treemap generation."""
    
    print("\n" + "="*60)
    print("TESTING TREEMAP GENERATION")
    print("="*60)
    
    test_case = {
        "title": "Department Treemap",
        "description": "Department sizes: Engineering 45%, Sales 20%, Marketing 15%, Operations 12%, Support 8%",
        "chart_type": "treemap"
    }
    
    print(f"\n📊 Testing: {test_case['title']}")
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
            print(f"\n✅ Success! Format: {result['format']}")
            
            if result['format'] == 'base64':
                import base64
                img_data = base64.b64decode(result['content'])
                print(f"📊 Generated {len(img_data):,} byte image")
            elif result['format'] == 'python_code':
                print(f"⚠️  Generated Python code instead of image")
                print("Code preview (first 500 chars):")
                print("-" * 40)
                print(result['content'][:500])
                print("-" * 40)
                
                # Try to execute the code directly
                print("\n🔧 Attempting to execute the code via MCP...")
                from src.agents.analytics_utils.mcp_integration import execute_chart_with_mcp
                
                mcp_result = await execute_chart_with_mcp(
                    result['content'],
                    pydantic_mcp_executor
                )
                
                if mcp_result and 'base64' in mcp_result:
                    print("✅ MCP execution successful!")
                else:
                    print(f"❌ MCP execution failed: {mcp_result}")
                    
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_treemap())