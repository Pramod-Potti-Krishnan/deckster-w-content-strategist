"""
Comprehensive Test for All Chart Types
=======================================

Tests all supported chart types with proper data parsing and MCP integration.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# Load environment variables
load_dotenv()

# Set GEMINI_API_KEY from GOOGLE_API_KEY if not already set
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics
from src.agents.analytics_utils.models import ChartType


# Mock MCP execute function for testing
async def mock_mcp_execute_code(code: str) -> dict:
    """Mock MCP execution that returns a dummy base64 image."""
    # For testing, return a simple base64 encoded 1x1 pixel PNG
    dummy_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    return {"output": dummy_base64}


async def test_all_chart_types():
    """Test all supported chart types."""
    
    print("\n" + "="*70)
    print("TESTING ALL CHART TYPES")
    print("="*70)
    
    # Create output directory
    output_dir = "test_output/all_chart_types"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define test cases for each chart type
    test_cases = [
        # Mermaid-supported charts
        {
            "type": ChartType.LINE,
            "title": "Monthly Revenue Trend",
            "content": "Monthly revenue: Jan $100k, Feb $120k, Mar $150k, Apr $180k, May $200k, Jun $220k",
            "expected_format": "mermaid"
        },
        {
            "type": ChartType.BAR,
            "title": "Product Sales Comparison",
            "content": "Product sales: Electronics $2.5M, Clothing $1.8M, Home $1.2M, Sports $900k, Books $600k",
            "expected_format": "mermaid"
        },
        {
            "type": ChartType.PIE,
            "title": "Market Share Distribution",
            "content": "Market share: Company A 35%, Company B 28%, Company C 22%, Others 15%",
            "expected_format": "mermaid"
        },
        {
            "type": ChartType.RADAR,
            "title": "Skills Assessment",
            "content": "Skills: Communication 85, Technical 75, Leadership 90, Problem Solving 80, Creativity 70",
            "expected_format": "mermaid"
        },
        
        # Python/MCP-required charts
        {
            "type": ChartType.SCATTER,
            "title": "Ad Spend vs Revenue",
            "content": "Advertising vs Revenue pairs: (10k, 50k), (20k, 80k), (30k, 110k), (40k, 130k), (50k, 150k)",
            "expected_format": "python_code"  # Will be base64 if MCP available
        },
        {
            "type": ChartType.HEATMAP,
            "title": "Correlation Matrix",
            "content": "Create correlation heatmap for 5x5 matrix with values ranging from -1 to 1",
            "expected_format": "python_code"
        },
        {
            "type": ChartType.HISTOGRAM,
            "title": "Age Distribution",
            "content": "Age distribution of customers with mean 35 and standard deviation 10",
            "expected_format": "python_code"
        },
        {
            "type": ChartType.BOX_PLOT,
            "title": "Salary Distribution",
            "content": "Salary ranges by department: Sales (50k-120k), Engineering (70k-150k), Marketing (45k-100k)",
            "expected_format": "python_code"
        },
        {
            "type": ChartType.AREA,
            "title": "Cumulative Revenue",
            "content": "Cumulative revenue by quarter: Q1 $1M, Q2 $2.5M, Q3 $4M, Q4 $6M",
            "expected_format": "python_code"
        },
        {
            "type": ChartType.BUBBLE,
            "title": "Product Analysis",
            "content": "Products with (revenue, profit, market_share): A(100k, 20k, 15%), B(150k, 40k, 25%), C(80k, 30k, 10%)",
            "expected_format": "python_code"
        },
        {
            "type": ChartType.WATERFALL,
            "title": "Profit Breakdown",
            "content": "Profit waterfall: Starting 100k, Sales +50k, Marketing -20k, Operations -10k, R&D -5k, Final 115k",
            "expected_format": "python_code"
        },
        {
            "type": ChartType.TREEMAP,
            "title": "Budget Allocation",
            "content": "Budget breakdown: Salaries 45%, Operations 20%, Marketing 15%, R&D 12%, Admin 5%, Other 3%",
            "expected_format": "python_code"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing {test_case['type'].value.upper()} Chart")
        print("-"*40)
        print(f"Title: {test_case['title']}")
        print(f"Expected Format: {test_case['expected_format']}")
        
        try:
            # Test without MCP (should return code)
            result = await create_analytics(
                test_case['content'],
                title=test_case['title'],
                chart_type=test_case['type'].value
            )
            
            if result['success']:
                print(f"✅ Generated successfully")
                print(f"   Format: {result['format']}")
                print(f"   Data Points: {len(result.get('data', []))}")
                
                # Check if correct format
                if test_case['type'] in [ChartType.LINE, ChartType.BAR, ChartType.PIE, ChartType.RADAR]:
                    assert result['format'] == 'mermaid', f"Expected mermaid, got {result['format']}"
                else:
                    assert result['format'] in ['python_code', 'base64'], f"Expected Python format, got {result['format']}"
                
                # Save output
                output_file = os.path.join(output_dir, f"{test_case['type'].value}.json")
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                results.append((test_case['type'].value, True, result['format']))
            else:
                print(f"❌ Failed to generate")
                results.append((test_case['type'].value, False, None))
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append((test_case['type'].value, False, "error"))
    
    # Test with mock MCP
    print("\n" + "="*70)
    print("TESTING WITH MOCK MCP EXECUTION")
    print("="*70)
    
    mcp_results = []
    
    for test_case in test_cases[4:8]:  # Test a few Python charts
        print(f"\nTesting {test_case['type'].value} with MCP...")
        
        try:
            result = await create_analytics(
                test_case['content'],
                title=test_case['title'],
                chart_type=test_case['type'].value,
                execute_code_func=mock_mcp_execute_code
            )
            
            if result['success']:
                print(f"✅ Format: {result['format']}")
                mcp_results.append((test_case['type'].value, True, result['format']))
            else:
                print(f"❌ Failed")
                mcp_results.append((test_case['type'].value, False, None))
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            mcp_results.append((test_case['type'].value, False, "error"))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    print("\nWithout MCP:")
    success_count = sum(1 for _, success, _ in results if success)
    print(f"  ✅ Passed: {success_count}/{len(results)}")
    
    print("\nBy Chart Type:")
    for chart_type, success, format_type in results:
        status = "✅" if success else "❌"
        print(f"  {status} {chart_type:12} - {format_type or 'failed'}")
    
    print("\nWith Mock MCP:")
    mcp_success = sum(1 for _, success, _ in mcp_results if success)
    print(f"  ✅ Passed: {mcp_success}/{len(mcp_results)}")
    
    print(f"\n📁 Results saved to: {output_dir}/")
    
    return success_count == len(results)


async def test_data_parsing():
    """Test data parsing from natural language."""
    
    print("\n" + "="*70)
    print("TESTING DATA PARSING")
    print("="*70)
    
    test_inputs = [
        {
            "input": "Q1=$1.2M, Q2=$1.5M, Q3=$1.3M, Q4=$1.8M",
            "expected_labels": ["Q1", "Q2", "Q3", "Q4"],
            "expected_values": [1200000, 1500000, 1300000, 1800000]
        },
        {
            "input": "January: 100k, February: 120k, March: 150k",
            "expected_labels": ["Jan", "Feb", "Mar"],
            "expected_values": [100000, 120000, 150000]
        },
        {
            "input": "Company A 35%, Company B 28%, Company C 22%",
            "expected_labels": ["Company A", "Company B", "Company C"],
            "expected_values": [35, 28, 22]
        }
    ]
    
    from src.agents.analytics_utils.data_parser import DataParser
    parser = DataParser()
    
    all_passed = True
    
    for test in test_inputs:
        print(f"\nInput: {test['input']}")
        points = parser.parse_data_points(test['input'])
        
        if len(points) == len(test['expected_labels']):
            print(f"✅ Parsed {len(points)} points correctly")
            for i, point in enumerate(points):
                if point.label == test['expected_labels'][i] and point.value == test['expected_values'][i]:
                    print(f"   ✓ {point.label}: {point.value}")
                else:
                    print(f"   ✗ Expected {test['expected_labels'][i]}: {test['expected_values'][i]}, got {point.label}: {point.value}")
                    all_passed = False
        else:
            print(f"❌ Expected {len(test['expected_labels'])} points, got {len(points)}")
            all_passed = False
    
    return all_passed


async def test_insight_correlation():
    """Test that insights match the actual data."""
    
    print("\n" + "="*70)
    print("TESTING INSIGHT CORRELATION")
    print("="*70)
    
    # Test with specific data that should show upward trend
    result = await create_analytics(
        "Show quarterly growth: Q1: 100, Q2: 150, Q3: 200, Q4: 250",
        title="Quarterly Growth"
    )
    
    if result['success']:
        print("Generated chart with parsed data")
        print(f"Data points: {result['data']}")
        print(f"Insights: {result['insights']}")
        
        # Check if insights mention upward trend
        has_upward = any('upward' in i.lower() or 'increase' in i.lower() for i in result['insights'])
        if has_upward:
            print("✅ Insights correctly identify upward trend")
        else:
            print("❌ Insights don't match the upward trend in data")
        
        # Check if peak is correctly identified
        values = [d['value'] for d in result['data']]
        if values:
            max_val = max(values)
            max_label = result['data'][values.index(max_val)]['label']
            peak_mentioned = any(max_label in i or str(max_val) in i for i in result['insights'])
            if peak_mentioned:
                print("✅ Peak value correctly identified in insights")
            else:
                print("❌ Peak value not mentioned in insights")
    
    return result['success']


async def main():
    """Run all comprehensive tests."""
    
    print("\n🚀 Starting Comprehensive Chart Type Tests...\n")
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: No API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env file")
        return
    
    # Run tests
    all_types_pass = await test_all_chart_types()
    parsing_pass = await test_data_parsing()
    insights_pass = await test_insight_correlation()
    
    # Summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    tests_status = [
        ("All Chart Types", all_types_pass),
        ("Data Parsing", parsing_pass),
        ("Insight Correlation", insights_pass)
    ]
    
    for test_name, passed in tests_status:
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    all_passed = all(passed for _, passed in tests_status)
    
    if all_passed:
        print("\n✅ All comprehensive tests passed!")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")


if __name__ == "__main__":
    asyncio.run(main())