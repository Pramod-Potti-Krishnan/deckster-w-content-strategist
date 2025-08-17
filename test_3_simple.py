"""
Test 3 Simple Charts
=====================

Generate 3 basic charts that we know work.
"""

import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from src.agents.analytics_agent_v2 import create_analytics_v2


async def test_three_charts():
    """Test 3 basic charts."""
    
    print("=" * 70)
    print("🎨 Testing 3 Basic Charts with Synthetic Data")
    print("=" * 70)
    
    # Test 1: Bar chart (we know this works)
    print("\n1. Bar Chart with User Data...")
    user_data = [
        {"label": "Product A", "value": 450},
        {"label": "Product B", "value": 380},
        {"label": "Product C", "value": 520},
        {"label": "Product D", "value": 280}
    ]
    
    result = await create_analytics_v2(
        content="Compare product sales",
        title="Product Sales Comparison",
        data=user_data,
        theme={
            "primary": "#2563EB",
            "secondary": "#10B981",
            "tertiary": "#F59E0B"
        },
        chart_type="bar_chart_vertical",
        save_files=True,
        output_dir="test_output/test1_bar"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files: {list(result['saved_files'].keys())}")
    
    # Test 2: Another bar chart with different data
    print("\n2. Horizontal Bar Chart...")
    data2 = [
        {"label": "Team Alpha", "value": 85},
        {"label": "Team Beta", "value": 92},
        {"label": "Team Gamma", "value": 78},
        {"label": "Team Delta", "value": 88}
    ]
    
    result = await create_analytics_v2(
        content="Team performance scores",
        title="Team Performance",
        data=data2,
        chart_type="bar_chart_horizontal",
        save_files=True,
        output_dir="test_output/test2_bar_h"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files: {list(result['saved_files'].keys())}")
    
    # Test 3: Line chart with user data
    print("\n3. Line Chart...")
    data3 = [
        {"label": "Jan", "value": 100},
        {"label": "Feb", "value": 120},
        {"label": "Mar", "value": 115},
        {"label": "Apr", "value": 130},
        {"label": "May", "value": 145},
        {"label": "Jun", "value": 160}
    ]
    
    result = await create_analytics_v2(
        content="Monthly growth trend",
        title="Monthly Growth",
        data=data3,
        chart_type="line_chart",
        save_files=True,
        output_dir="test_output/test3_line"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files: {list(result['saved_files'].keys())}")
    
    print("\n" + "=" * 70)
    print("✅ Test Complete - Check test_output directory")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_three_charts())