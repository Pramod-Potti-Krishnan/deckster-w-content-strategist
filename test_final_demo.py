"""
Final Demo - 3 Working Charts
==============================

Demonstrates the complete system with PNG and JSON generation.
"""

import asyncio
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

from src.agents.analytics_agent_v2 import create_analytics_v2


async def demo_three_charts():
    """Generate 3 demonstration charts."""
    
    print("=" * 80)
    print("📊 Analytics Agent V2 - Final Demonstration")
    print("=" * 80)
    print("\nGenerating charts with both PNG images and JSON data files...\n")
    
    # Chart 1: Sales Performance Bar Chart
    print("1️⃣  Sales Performance Bar Chart")
    print("-" * 40)
    
    sales_data = [
        {"label": "North America", "value": 125000},
        {"label": "Europe", "value": 98000},
        {"label": "Asia Pacific", "value": 145000},
        {"label": "Latin America", "value": 67000},
        {"label": "Middle East", "value": 45000},
        {"label": "Africa", "value": 38000}
    ]
    
    result1 = await create_analytics_v2(
        content="Regional sales performance for Q4 2024",
        title="Q4 2024 Sales by Region",
        data=sales_data,
        theme={
            "primary": "#1E40AF",    # Blue
            "secondary": "#10B981",  # Green
            "tertiary": "#F59E0B"    # Orange
        },
        chart_type="bar_chart_vertical",
        save_files=True,
        output_dir="demo_output/sales_chart"
    )
    
    if result1['success']:
        print("✅ Success!")
        if result1.get('saved_files'):
            print("📁 Generated files:")
            for file_type, path in result1['saved_files'].items():
                print(f"   - {file_type:10s}: {os.path.basename(path)}")
        if result1.get('data', {}).get('statistics'):
            stats = result1['data']['statistics']
            print(f"📊 Statistics: Total=${stats['total']:,.0f}, Average=${stats['mean']:,.0f}")
    
    # Chart 2: Monthly Trend Line Chart
    print("\n2️⃣  Monthly Revenue Trend")
    print("-" * 40)
    
    monthly_data = [
        {"label": "Jan", "value": 85000},
        {"label": "Feb", "value": 92000},
        {"label": "Mar", "value": 88000},
        {"label": "Apr", "value": 95000},
        {"label": "May", "value": 103000},
        {"label": "Jun", "value": 112000},
        {"label": "Jul", "value": 118000},
        {"label": "Aug", "value": 125000},
        {"label": "Sep", "value": 122000},
        {"label": "Oct", "value": 130000},
        {"label": "Nov", "value": 138000},
        {"label": "Dec", "value": 145000}
    ]
    
    result2 = await create_analytics_v2(
        content="Monthly revenue trend showing growth pattern",
        title="2024 Monthly Revenue Trend",
        data=monthly_data,
        theme={
            "primary": "#059669",    # Green
            "secondary": "#DC2626",  # Red
            "tertiary": "#7C3AED"    # Purple
        },
        chart_type="line_chart",
        save_files=True,
        output_dir="demo_output/trend_chart"
    )
    
    if result2['success']:
        print("✅ Success!")
        if result2.get('saved_files'):
            print("📁 Generated files:")
            for file_type, path in result2['saved_files'].items():
                print(f"   - {file_type:10s}: {os.path.basename(path)}")
        # Show growth calculation
        if result2.get('data', {}).get('values'):
            values = result2['data']['values']
            growth = ((values[-1] - values[0]) / values[0]) * 100
            print(f"📈 Year-over-year growth: {growth:.1f}%")
    
    # Chart 3: Market Share Pie Chart
    print("\n3️⃣  Market Share Distribution")
    print("-" * 40)
    
    market_data = [
        {"label": "Company A", "value": 35},
        {"label": "Company B", "value": 28},
        {"label": "Company C", "value": 18},
        {"label": "Company D", "value": 12},
        {"label": "Others", "value": 7}
    ]
    
    result3 = await create_analytics_v2(
        content="Market share distribution among top companies",
        title="Market Share 2024",
        data=market_data,
        theme={
            "primary": "#2563EB",
            "secondary": "#EC4899",
            "tertiary": "#06B6D4"
        },
        chart_type="pie_chart",
        save_files=True,
        output_dir="demo_output/market_chart"
    )
    
    if result3['success']:
        print("✅ Success!")
        if result3.get('saved_files'):
            print("📁 Generated files:")
            for file_type, path in result3['saved_files'].items():
                print(f"   - {file_type:10s}: {os.path.basename(path)}")
        # Show market leader
        if result3.get('data', {}).get('labels'):
            print(f"🏆 Market leader: {result3['data']['labels'][0]} ({result3['data']['values'][0]}%)")
    
    # Summary
    print("\n" + "=" * 80)
    print("✨ Demonstration Complete!")
    print("=" * 80)
    print("\n📂 Output Structure:")
    print("""
demo_output/
├── sales_chart/
│   ├── *.png              # Bar chart image
│   ├── *_data.json        # Sales data with statistics
│   └── *_metadata.json    # Chart configuration
├── trend_chart/
│   ├── *.png              # Line chart image
│   ├── *_data.json        # Monthly revenue data
│   └── *_metadata.json    # Chart configuration
└── market_chart/
    ├── *.png              # Pie chart image
    ├── *_data.json        # Market share percentages
    └── *_metadata.json    # Chart configuration
    """)
    
    print("🎯 Key Features Demonstrated:")
    print("   ✅ PNG image generation for visual display")
    print("   ✅ JSON data files with complete underlying data")
    print("   ✅ Statistical analysis (min, max, mean, total)")
    print("   ✅ Theme customization with primary/secondary/tertiary colors")
    print("   ✅ Multiple chart types (bar, line, pie)")
    print("   ✅ Ready for API transmission")


if __name__ == "__main__":
    asyncio.run(demo_three_charts())