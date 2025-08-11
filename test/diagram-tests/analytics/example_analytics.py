"""
Analytics Agent Example Usage
==============================

Demonstrates various analytics generation capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.agents.analytics_agent import create_analytics


async def demonstrate_analytics():
    """Demonstrate various analytics capabilities."""
    
    print("Analytics Agent Demonstration")
    print("=" * 50)
    
    # Example 1: Simple Bar Chart
    print("\n1. Generating Quarterly Sales Bar Chart...")
    result = await create_analytics(
        "Show quarterly sales data for 2024 with Q1=100k, Q2=120k, Q3=140k, Q4=160k",
        title="2024 Quarterly Sales Performance"
    )
    
    if result["success"]:
        print(f"   ✓ Chart Type: {result['chart_type']}")
        print(f"   ✓ Format: {result['format']}")
        print(f"   ✓ Data Points: {len(result['data'])}")
        if result['insights']:
            print(f"   ✓ Insights: {result['insights'][0]}")
    
    # Example 2: Line Chart with Trend
    print("\n2. Generating Monthly Revenue Trend Line Chart...")
    result = await create_analytics(
        "Display monthly revenue for the last 12 months showing steady growth from 50k to 200k",
        title="Monthly Revenue Growth Trend",
        chart_type="line"
    )
    
    if result["success"]:
        print(f"   ✓ Chart Type: {result['chart_type']}")
        print(f"   ✓ Description: {result['description'][:100]}...")
        print(f"   ✓ Trend Detected: {'growth' in result['description'].lower()}")
    
    # Example 3: Pie Chart for Distribution
    print("\n3. Generating Market Share Pie Chart...")
    result = await create_analytics(
        "Show market share distribution: Company A has 35%, Company B has 28%, Company C has 22%, Others 15%",
        title="Market Share Distribution",
        chart_type="pie"
    )
    
    if result["success"]:
        print(f"   ✓ Chart Type: {result['chart_type']}")
        print(f"   ✓ Mermaid Code Generated: {'pie' in result['content'].lower()}")
    
    # Example 4: Complex Visualization Request
    print("\n4. Generating Product Category Performance Analysis...")
    result = await create_analytics(
        "Analyze product category performance across 5 categories showing Electronics leading with high growth, "
        "Clothing stable, Food declining slightly, Home goods growing, and Sports seasonal variation",
        title="Product Category Performance Analysis"
    )
    
    if result["success"]:
        print(f"   ✓ Chart Type: {result['chart_type']}")
        print(f"   ✓ Data Points: {len(result['data'])}")
        print(f"   ✓ Insights Generated: {len(result['insights'])}")
    
    # Example 5: Time Series with Seasonality
    print("\n5. Generating Seasonal Sales Pattern...")
    result = await create_analytics(
        "Show ice cream sales over 12 months with clear summer peak and winter trough, "
        "displaying seasonal patterns typical of weather-dependent products",
        title="Ice Cream Sales - Seasonal Pattern",
        chart_type="line"
    )
    
    if result["success"]:
        print(f"   ✓ Chart Type: {result['chart_type']}")
        print(f"   ✓ Seasonality Detected: {'seasonal' in result['description'].lower()}")
    
    # Example 6: Custom Theme Application
    print("\n6. Generating Chart with Custom Theme...")
    custom_theme = {
        "colors": {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "accent": "#45B7D1"
        },
        "style": "seaborn"
    }
    
    result = await create_analytics(
        "Display team performance metrics for 5 teams",
        title="Team Performance Dashboard",
        theme=custom_theme
    )
    
    if result["success"]:
        print(f"   ✓ Chart Type: {result['chart_type']}")
        print(f"   ✓ Theme Applied: {bool(result.get('metadata'))}")
    
    # Print sample Mermaid output
    print("\n" + "=" * 50)
    print("Sample Mermaid Output:")
    print("-" * 50)
    
    sample_result = await create_analytics(
        "Show Q1-Q4 sales: 100, 120, 110, 140",
        title="Quarterly Sales",
        chart_type="bar"
    )
    
    if sample_result["success"] and sample_result["format"] == "mermaid":
        print(sample_result["content"][:500])  # Print first 500 chars
    
    print("\n" + "=" * 50)
    print("Analytics Demonstration Complete!")


async def test_error_handling():
    """Test error handling and fallback mechanisms."""
    
    print("\n\nError Handling Tests")
    print("=" * 50)
    
    # Test with invalid chart type (should fallback)
    print("\n1. Testing Invalid Chart Type...")
    result = await create_analytics(
        "Generate data visualization",
        chart_type="invalid_type"
    )
    print(f"   Result: {'Success with fallback' if result['success'] else 'Failed'}")
    
    # Test with empty content
    print("\n2. Testing Empty Content...")
    result = await create_analytics("")
    print(f"   Result: Chart generated = {result['success']}")
    
    print("\nError Handling Tests Complete!")


async def main():
    """Run all demonstrations."""
    await demonstrate_analytics()
    await test_error_handling()


if __name__ == "__main__":
    print("\n🚀 Starting Analytics Agent Examples...\n")
    asyncio.run(main())
    print("\n✅ All examples completed successfully!\n")