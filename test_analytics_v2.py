"""
Test Analytics Agent V2
========================

Demonstrates the complete analytics generation with PNG and JSON output.
"""

import asyncio
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from src.agents.analytics_agent_v2 import create_analytics_v2


async def test_complete_output():
    """Test generating analytics with PNG and JSON files."""
    
    print("=" * 60)
    print("Testing Analytics Agent V2 - Complete Output")
    print("=" * 60)
    
    # Test 1: Line chart with synthetic data
    print("\n1. Generating line chart with synthetic data...")
    result = await create_analytics_v2(
        content="Show monthly revenue growth trend over the last 12 months with seasonal patterns",
        title="Monthly Revenue Trend 2024",
        theme={
            "primary": "#1E40AF",    # Blue
            "secondary": "#10B981",  # Green
            "tertiary": "#F59E0B"    # Orange
        },
        chart_type="line_chart",
        enhance_labels=True,
        save_files=True,
        output_dir="test_output/line_chart"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files saved:")
        for file_type, path in result['saved_files'].items():
            print(f"     - {file_type}: {path}")
    
    # Test 2: Bar chart with user data
    print("\n2. Generating bar chart with user data...")
    user_data = [
        {"label": "North America", "value": 45000},
        {"label": "Europe", "value": 38000},
        {"label": "Asia Pacific", "value": 52000},
        {"label": "Latin America", "value": 28000},
        {"label": "Middle East", "value": 15000}
    ]
    
    result = await create_analytics_v2(
        content="Compare sales performance across regions",
        title="Sales by Region 2024",
        data=user_data,
        theme={
            "primary": "#059669",    # Green
            "secondary": "#DC2626",  # Red
            "tertiary": "#7C3AED"    # Purple
        },
        chart_type="bar_chart_horizontal",
        save_files=True,
        output_dir="test_output/bar_chart"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files saved:")
        for file_type, path in result['saved_files'].items():
            print(f"     - {file_type}: {path}")
    
    # Test 3: Pie chart with enhanced labels
    print("\n3. Generating pie chart with LLM-enhanced labels...")
    result = await create_analytics_v2(
        content="Show market share distribution for top 5 cloud providers in 2024",
        title="Cloud Market Share 2024",
        enhance_labels=True,
        chart_type="pie_chart",
        save_files=True,
        output_dir="test_output/pie_chart"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files saved:")
        for file_type, path in result['saved_files'].items():
            print(f"     - {file_type}: {path}")
    
    # Test 4: Violin plot (fixed implementation)
    print("\n4. Generating violin plot with bimodal distribution...")
    result = await create_analytics_v2(
        content="Show employee performance score distributions across departments",
        title="Performance Scores by Department",
        chart_type="violin_plot",
        theme={
            "primary": "#2563EB",
            "secondary": "#16A34A",
            "tertiary": "#EA580C"
        },
        save_files=True,
        output_dir="test_output/violin_plot"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files saved:")
        for file_type, path in result['saved_files'].items():
            print(f"     - {file_type}: {path}")
    
    # Test 5: Heatmap
    print("\n5. Generating heatmap...")
    result = await create_analytics_v2(
        content="Create a heatmap showing website activity patterns by hour and day of week",
        title="Weekly Activity Heatmap",
        chart_type="heatmap",
        save_files=True,
        output_dir="test_output/heatmap"
    )
    
    print(f"   Success: {result['success']}")
    if result.get('saved_files'):
        print(f"   Files saved:")
        for file_type, path in result['saved_files'].items():
            print(f"     - {file_type}: {path}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("Check the 'test_output' directory for generated files.")
    print("=" * 60)
    
    # Print summary of data structure
    print("\n📊 Data Structure in JSON files:")
    print("  - labels: X-axis labels")
    print("  - values: Y-axis values")
    print("  - statistics: min, max, mean, median, std")
    print("  - series: Multi-series data if applicable")
    print("  - raw_data: Original data points")
    
    print("\n🎨 Files Generated:")
    print("  - .png: Chart image file")
    print("  - _data.json: Underlying chart data")
    print("  - _metadata.json: Chart metadata and insights")
    print("  - .py: Python code for the chart")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_complete_output())