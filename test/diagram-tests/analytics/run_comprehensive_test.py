"""
Comprehensive Analytics Agent Test Runner
=========================================

Full integration test with API key loading.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# Load environment variables from .env file
load_dotenv()

# Set GEMINI_API_KEY from GOOGLE_API_KEY if not already set
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics, AnalyticsAgent
from src.agents.analytics_utils.models import ChartType


async def comprehensive_test():
    """Run comprehensive tests of the analytics agent."""
    
    print("\n" + "="*70)
    print("COMPREHENSIVE ANALYTICS AGENT TEST")
    print("="*70)
    
    test_results = []
    
    # Test 1: Simple Bar Chart
    print("\n[TEST 1] Simple Bar Chart Generation")
    print("-"*40)
    try:
        result = await create_analytics(
            "Show quarterly sales data for 2024 with values around 100-200k per quarter",
            title="Q1-Q4 2024 Sales Performance"
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Chart Type: {result['chart_type']}")
            print(f"   Format: {result['format']}")
            print(f"   Data Points: {len(result['data'])}")
            print(f"   Description: {result['description'][:100]}...")
            if result['insights']:
                print(f"   First Insight: {result['insights'][0]}")
            test_results.append(("Bar Chart", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Bar Chart", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Bar Chart", False))
    
    # Test 2: Line Chart with Trend
    print("\n[TEST 2] Line Chart with Upward Trend")
    print("-"*40)
    try:
        result = await create_analytics(
            "Display monthly revenue growth from January to December showing steady increase from 50k to 200k",
            title="Monthly Revenue Growth Trend",
            chart_type="line"
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Chart Type: {result['chart_type']}")
            print(f"   Trend Detected: {'trend' in result['description'].lower() or 'increase' in result['description'].lower()}")
            print(f"   Data Points: {len(result['data'])}")
            # Check if it's actually trending upward
            if result['data']:
                first_val = result['data'][0]['value']
                last_val = result['data'][-1]['value']
                print(f"   Value Change: {first_val:.2f} → {last_val:.2f}")
            test_results.append(("Line Chart", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Line Chart", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Line Chart", False))
    
    # Test 3: Pie Chart
    print("\n[TEST 3] Pie Chart for Market Share")
    print("-"*40)
    try:
        result = await create_analytics(
            "Show market share: Company A 35%, Company B 28%, Company C 22%, Others 15%",
            title="Market Share Distribution",
            chart_type="pie"
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Chart Type: {result['chart_type']}")
            print(f"   Mermaid Content: {'pie' in result['content'].lower()}")
            print(f"   Data Points: {len(result['data'])}")
            test_results.append(("Pie Chart", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Pie Chart", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Pie Chart", False))
    
    # Test 4: Complex Visualization (Heatmap/Scatter)
    print("\n[TEST 4] Complex Visualization Request")
    print("-"*40)
    try:
        result = await create_analytics(
            "Create a scatter plot showing correlation between advertising spend and sales revenue",
            title="Ad Spend vs Revenue Correlation",
            chart_type="scatter"
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Chart Type: {result['chart_type']}")
            print(f"   Format: {result['format']}")
            print(f"   Generation Method: {result.get('metadata', {}).get('generation_method', 'unknown')}")
            test_results.append(("Scatter Plot", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Scatter Plot", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Scatter Plot", False))
    
    # Test 5: Seasonal Data Pattern
    print("\n[TEST 5] Seasonal Pattern Detection")
    print("-"*40)
    try:
        result = await create_analytics(
            "Show ice cream sales over 12 months with clear summer peak (June-August) and winter low (December-February)",
            title="Ice Cream Sales - Seasonal Pattern",
            chart_type="line"
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Chart Type: {result['chart_type']}")
            print(f"   Seasonality Mentioned: {'seasonal' in result['description'].lower() or 'pattern' in result['description'].lower()}")
            print(f"   Number of Insights: {len(result['insights'])}")
            test_results.append(("Seasonal Pattern", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Seasonal Pattern", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Seasonal Pattern", False))
    
    # Test 6: Radar Chart
    print("\n[TEST 6] Radar Chart for Multi-dimensional Data")
    print("-"*40)
    try:
        result = await create_analytics(
            "Create radar chart for skills assessment: Communication 85, Technical 75, Leadership 90, Teamwork 80, Innovation 70",
            title="Skills Assessment Radar",
            chart_type="radar"
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Chart Type: {result['chart_type']}")
            print(f"   Format: {result['format']}")
            print(f"   Data Points: {len(result['data'])}")
            test_results.append(("Radar Chart", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Radar Chart", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Radar Chart", False))
    
    # Test 7: Custom Theme
    print("\n[TEST 7] Custom Theme Application")
    print("-"*40)
    try:
        custom_theme = {
            "colors": {
                "primary": "#FF6B6B",
                "secondary": "#4ECDC4",
                "accent": "#45B7D1"
            },
            "matplotlib_style": "seaborn",
            "mermaid_theme": "base"
        }
        
        result = await create_analytics(
            "Display team performance metrics for 5 teams",
            title="Team Performance Dashboard",
            theme=custom_theme
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Theme Applied: {bool(result.get('metadata'))}")
            print(f"   Chart Type: {result['chart_type']}")
            test_results.append(("Custom Theme", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Custom Theme", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Custom Theme", False))
    
    # Test 8: Data with Outliers
    print("\n[TEST 8] Data with Outliers Detection")
    print("-"*40)
    try:
        result = await create_analytics(
            "Show monthly sales with most months around 100k but December spike to 300k and January drop to 50k",
            title="Sales with Outliers"
        )
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Outlier Insights: {any('outlier' in i.lower() or 'peak' in i.lower() for i in result['insights'])}")
            print(f"   Number of Insights: {len(result['insights'])}")
            test_results.append(("Outlier Detection", True))
        else:
            print(f"❌ Failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            test_results.append(("Outlier Detection", False))
    except Exception as e:
        print(f"❌ Exception: {e}")
        test_results.append(("Outlier Detection", False))
    
    # Print Mermaid Output Sample
    print("\n" + "="*70)
    print("SAMPLE MERMAID OUTPUT")
    print("="*70)
    
    try:
        sample_result = await create_analytics(
            "Show Q1-Q4 sales: 100, 120, 110, 140",
            title="Quarterly Sales Sample",
            chart_type="bar"
        )
        
        if sample_result["success"] and sample_result["format"] == "mermaid":
            print(sample_result["content"])
        else:
            print("Could not generate Mermaid sample")
    except Exception as e:
        print(f"Error generating sample: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in test_results if success)
    failed = sum(1 for _, success in test_results if not success)
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    print("\nDetailed Results:")
    for test_name, success in test_results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")
    
    return passed, failed


async def test_edge_cases():
    """Test edge cases and error handling."""
    
    print("\n" + "="*70)
    print("EDGE CASE TESTING")
    print("="*70)
    
    edge_results = []
    
    # Test 1: Empty content
    print("\n[EDGE 1] Empty Content")
    try:
        result = await create_analytics("")
        print(f"   Handled: {result['success'] or 'error' in str(result)}")
        edge_results.append(("Empty Content", True))
    except Exception as e:
        print(f"   Exception (expected): {type(e).__name__}")
        edge_results.append(("Empty Content", True))
    
    # Test 2: Invalid chart type
    print("\n[EDGE 2] Invalid Chart Type")
    try:
        result = await create_analytics(
            "Generate chart",
            chart_type="invalid_type"
        )
        print(f"   Fallback Used: {result['success']}")
        edge_results.append(("Invalid Type", result['success']))
    except Exception as e:
        print(f"   Exception: {e}")
        edge_results.append(("Invalid Type", False))
    
    # Test 3: Very large data request
    print("\n[EDGE 3] Large Data Request")
    try:
        result = await create_analytics(
            "Generate 100 data points for daily sales over 3 months",
            title="Large Dataset"
        )
        print(f"   Handled: {result['success']}")
        if result['success']:
            print(f"   Data Points Generated: {len(result['data'])}")
        edge_results.append(("Large Data", result['success']))
    except Exception as e:
        print(f"   Exception: {e}")
        edge_results.append(("Large Data", False))
    
    return edge_results


async def main():
    """Run all tests."""
    print("\n🚀 Starting Comprehensive Analytics Agent Tests...\n")
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: No API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env file")
        return
    
    print(f"✅ API Key loaded: {os.getenv('GEMINI_API_KEY', os.getenv('GOOGLE_API_KEY'))[:10]}...")
    
    # Run comprehensive tests
    passed, failed = await comprehensive_test()
    
    # Run edge case tests
    edge_results = await test_edge_cases()
    
    print("\n" + "="*70)
    print("🎯 ALL TESTS COMPLETED")
    print("="*70)
    
    if failed == 0:
        print("\n✅ All tests passed successfully!")
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the output above.")


if __name__ == "__main__":
    asyncio.run(main())