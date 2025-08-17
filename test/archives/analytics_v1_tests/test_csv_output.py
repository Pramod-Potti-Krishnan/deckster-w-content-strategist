#!/usr/bin/env python
"""
Test CSV Data Output
====================
Test that charts return CSV data along with visualizations.
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


async def test_csv_output():
    """Test that CSV data is returned with charts."""
    
    print("\n" + "="*60)
    print("TESTING CSV DATA OUTPUT")
    print("="*60)
    
    # Test with a simple bar chart
    result = await create_analytics(
        "Product sales by category: Electronics $450K, Clothing $320K, Food $280K, Sports $190K",
        title="Sales by Category",
        chart_type="bar",
        mcp_tool=pydantic_mcp_executor
    )
    
    print(f"\n📊 Chart Type: {result['chart_type']}")
    print(f"✅ Success: {result['success']}")
    print(f"📄 Format: {result['format']}")
    
    # Check if CSV data is present
    if result.get('csv_data'):
        print("\n📋 CSV Data Returned:")
        print("-" * 40)
        print(result['csv_data'])
        print("-" * 40)
        
        # Count rows
        rows = result['csv_data'].strip().split('\n')
        print(f"\n📊 Data Statistics:")
        print(f"  - Headers: {rows[0] if rows else 'None'}")
        print(f"  - Data Rows: {len(rows) - 1 if len(rows) > 1 else 0}")
        
        # Show raw data format
        if result.get('data'):
            print(f"  - Raw Data Points: {len(result['data'])}")
            print(f"  - Sample: {result['data'][0] if result['data'] else 'None'}")
    else:
        print("\n❌ No CSV data returned!")
    
    # Test with a scatter plot
    print("\n" + "="*60)
    print("Testing Scatter Plot CSV Output")
    print("="*60)
    
    result2 = await create_analytics(
        "Marketing spend vs Revenue correlation: spend $10K revenue $45K, spend $15K revenue $62K, spend $20K revenue $78K, spend $25K revenue $85K",
        title="Marketing vs Revenue",
        chart_type="scatter",
        mcp_tool=pydantic_mcp_executor
    )
    
    if result2.get('csv_data'):
        print("\n📋 Scatter Plot CSV Data:")
        print("-" * 40)
        print(result2['csv_data'])
        print("-" * 40)
    
    return result.get('csv_data') is not None


if __name__ == "__main__":
    success = asyncio.run(test_csv_output())
    
    if success:
        print("\n✅ CSV data output test PASSED!")
    else:
        print("\n❌ CSV data output test FAILED!")
        sys.exit(1)