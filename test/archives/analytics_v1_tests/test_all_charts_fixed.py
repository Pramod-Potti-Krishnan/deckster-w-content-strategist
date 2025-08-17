"""
Test All Charts with Fixes
===========================

Comprehensive test with:
- Fixed chart implementations
- Proper rate limiting (10 second delays)
- Better error handling
- Uses enhanced agents
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

# Add the fixed modules to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.analytics_agent import AnalyticsAgent
from src.agents.analytics_utils.models import AnalyticsRequest

# All 23 chart types with appropriate test cases
ALL_CHART_TESTS = [
    # ========== TREND CHARTS ==========
    {
        "id": "01_line_chart",
        "title": "Monthly Revenue Trend",
        "description": "Show revenue growth trend over 12 months with seasonal patterns",
        "data_context": "Monthly revenue data with clear upward trend and seasonal spikes",
        "time_period": "12 months"
    },
    {
        "id": "02_step_chart",
        "title": "Inventory Level Changes",
        "description": "Display inventory levels that change at discrete points in time",
        "data_context": "Warehouse inventory levels updated weekly showing step changes",
        "time_period": "8 weeks"
    },
    {
        "id": "03_area_chart",
        "title": "Website Traffic Volume",
        "description": "Emphasize the magnitude of daily website traffic over time",
        "data_context": "Daily website visitor counts showing growth and weekend patterns",
        "time_period": "30 days"
    },
    {
        "id": "04_stacked_area_chart",
        "title": "Revenue by Product Category",
        "description": "Show cumulative revenue across 4 product categories over quarters",
        "data_context": "Quarterly revenue breakdown: Electronics, Clothing, Books, Home & Garden",
        "time_period": "8 quarters"
    },
    
    # ========== BAR CHARTS ==========
    {
        "id": "05_bar_vertical",
        "title": "Sales by Region",
        "description": "Compare sales performance across 8 geographic regions",
        "data_context": "Annual sales data for North, South, East, West, Central, Northeast, Northwest, Southeast"
    },
    {
        "id": "06_bar_horizontal",
        "title": "Top Product Rankings",
        "description": "Rank top 10 products by customer satisfaction score horizontally",
        "data_context": "Customer satisfaction scores (1-100) for best-selling products shown as horizontal bars"
    },
    {
        "id": "07_grouped_bar",
        "title": "Quarterly Performance Comparison",
        "description": "Compare Q1-Q4 performance across 3 years with grouped bars",
        "data_context": "Revenue and profit data for 2022, 2023, 2024 by quarter"
    },
    {
        "id": "08_stacked_bar",
        "title": "Marketing Channel Mix",
        "description": "Show composition of leads from different marketing channels as stacked bars",
        "data_context": "Lead sources: Email, Social Media, SEO, Paid Ads, Direct, Referral"
    },
    
    # ========== DISTRIBUTION CHARTS ==========
    {
        "id": "09_histogram",
        "title": "Customer Age Distribution",
        "description": "Analyze the age distribution of customer base using histogram",
        "data_context": "Customer ages ranging from 18 to 75 years"
    },
    {
        "id": "10_box_plot",
        "title": "Product Price Ranges by Category",
        "description": "Compare price distributions across 6 product categories using box plots",
        "data_context": "Price data showing median, quartiles, and outliers for each category"
    },
    {
        "id": "11_violin_plot",
        "title": "Employee Performance Scores",
        "description": "Show distribution shape of performance scores by department using violin plots",
        "data_context": "Performance scores (0-100) for Sales, Engineering, Marketing, Support departments"
    },
    
    # ========== CORRELATION CHARTS ==========
    {
        "id": "12_scatter_plot",
        "title": "Price vs Quality Correlation",
        "description": "Analyze relationship between product price and quality rating",
        "data_context": "Product prices ($10-$500) and quality ratings (1-5 stars)"
    },
    {
        "id": "13_bubble_chart",
        "title": "Market Opportunity Analysis",
        "description": "Compare markets by size, growth rate, and profitability",
        "data_context": "Market segments with revenue (size), growth % (x), profit margin (y)"
    },
    {
        "id": "14_hexbin",
        "title": "User Activity Density",
        "description": "Visualize density of user clicks on website heatmap",
        "data_context": "X,Y coordinates of 10,000+ user clicks on homepage"
    },
    
    # ========== COMPOSITION CHARTS ==========
    {
        "id": "15_pie_chart",
        "title": "Market Share Distribution",
        "description": "Show market share percentages for top 5 companies",
        "data_context": "Market share: Company A (35%), B (25%), C (20%), D (15%), E (5%)"
    },
    {
        "id": "16_waterfall",
        "title": "Profit Bridge Analysis",
        "description": "Show how initial revenue becomes final profit through costs",
        "data_context": "Revenue $1M, minus COGS $400k, OpEx $300k, Tax $100k = Profit $200k"
    },
    {
        "id": "17_funnel",
        "title": "Sales Conversion Funnel",
        "description": "Visualize conversion rates through sales stages",
        "data_context": "Visitors (10000), Leads (2000), Qualified (500), Customers (100)"
    },
    
    # ========== COMPARISON CHARTS ==========
    {
        "id": "18_radar_chart",
        "title": "Product Feature Comparison",
        "description": "Compare products across 6 feature dimensions",
        "data_context": "Features: Performance, Design, Price, Support, Innovation, Reliability"
    },
    {
        "id": "19_heatmap",
        "title": "Weekly Activity Patterns",
        "description": "Show activity intensity by hour and day of week",
        "data_context": "User activity levels for each hour (0-23) across all 7 days"
    },
    
    # ========== STATISTICAL CHARTS ==========
    {
        "id": "20_error_bar",
        "title": "Experimental Results with Confidence",
        "description": "Show measurement results with error margins",
        "data_context": "Test results for 5 conditions with mean values and standard errors"
    },
    {
        "id": "21_control_chart",
        "title": "Manufacturing Process Control",
        "description": "Monitor process quality with control limits",
        "data_context": "Daily quality measurements with upper/lower control limits"
    },
    {
        "id": "22_pareto",
        "title": "Defect Analysis",
        "description": "80/20 analysis of product defect causes",
        "data_context": "Defect types: Assembly (45%), Material (25%), Design (15%), Packaging (10%), Other (5%)"
    },
    
    # ========== PROJECT CHARTS ==========
    {
        "id": "23_gantt",
        "title": "Project Timeline",
        "description": "Show project tasks and their timeline dependencies",
        "data_context": "Project phases: Planning (Week 1-2), Development (Week 3-8), Testing (Week 7-10), Deployment (Week 11)"
    }
]


async def generate_chart_code_with_retry(agent, test_case, output_dir, max_retries=3):
    """Generate chart code with retry logic for rate limiting."""
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}: Generating {test_case['id']} - {test_case['title']}")
            
            # Create request
            request = AnalyticsRequest(
                title=test_case["title"],
                description=test_case["description"],
                data_context=test_case["data_context"],
                time_period=test_case.get("time_period")
            )
            
            # Generate chart
            result = await agent.generate_analytics(request)
            
            # Check if we got an error format
            if result.format == "error":
                # Check if it's a rate limit error
                if hasattr(result, 'error_message') and '429' in str(result.error_message):
                    wait_time = 60 * (attempt + 1)  # Exponential backoff: 60s, 120s, 180s
                    print(f"    ⚠️ Rate limit hit. Waiting {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print(f"    ❌ Error: {getattr(result, 'error_message', 'Unknown error')[:100]}")
                    return {"status": "error", "message": str(getattr(result, 'error_message', 'Unknown error'))[:200]}
            
            # Save based on format
            if result.format == "mermaid":
                file_path = output_dir / f"{test_case['id']}.mmd"
                content = result.output if hasattr(result, 'output') else result.chart_content
                with open(file_path, 'w') as f:
                    f.write(f"# {test_case['title']}\n")
                    f.write(f"# Chart Type: {result.chart_type}\n")
                    f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                    f.write(content)
                print(f"    ✅ Success: Saved as {file_path.name}")
                return {"status": "success", "format": "mermaid", "file": file_path.name, "chart_type": str(result.chart_type)}
                
            elif result.format in ["python_code", "base64", "png"]:
                file_path = output_dir / f"{test_case['id']}.py"
                
                # Get the code
                if result.format == "python_code":
                    content = result.output if hasattr(result, 'output') else result.chart_content
                elif hasattr(result, 'python_code'):
                    content = result.python_code
                else:
                    content = str(result.chart_content)[:100] + "..."
                
                with open(file_path, 'w') as f:
                    f.write(f"# {test_case['title']}\n")
                    f.write(f"# Chart Type: {result.chart_type}\n")
                    f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                    f.write(content)
                print(f"    ✅ Success: Saved as {file_path.name}")
                return {"status": "success", "format": "python", "file": file_path.name, "chart_type": str(result.chart_type)}
            
            else:
                print(f"    ⚠️ Unexpected format: {result.format}")
                return {"status": "error", "format": result.format, "message": f"Unexpected format: {result.format}"}
                
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ Exception on attempt {attempt + 1}: {error_msg[:100]}")
            
            # Check for rate limit in exception
            if '429' in error_msg or 'rate' in error_msg.lower():
                wait_time = 60 * (attempt + 1)
                print(f"    ⚠️ Rate limit detected. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                continue
            
            if attempt == max_retries - 1:
                return {"status": "error", "message": error_msg[:200]}
    
    return {"status": "error", "message": "Max retries exceeded"}


async def generate_all_charts_fixed():
    """Generate code for all 23 chart types with fixes."""
    print("="*80)
    print("COMPREHENSIVE CHART GENERATION TEST (WITH FIXES)")
    print("Generating all 23 chart types from Analytics Playbook")
    print("Using enhanced agents and proper rate limiting")
    print("="*80)
    
    # Create output directory
    output_dir = Path("all_charts_fixed_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize agent (it will use the fixed modules if we've patched them)
    agent = AnalyticsAgent()
    print("✅ Analytics Agent initialized")
    print("⏱️ Using 10-second delay between requests to avoid rate limiting\n")
    
    # Track results by category
    results = {
        "trend": [],
        "bar": [],
        "distribution": [],
        "correlation": [],
        "composition": [],
        "comparison": [],
        "statistical": [],
        "project": []
    }
    
    all_results = []
    
    # Generate each chart with proper rate limiting
    for i, test_case in enumerate(ALL_CHART_TESTS, 1):
        print(f"\n[{i}/23] Processing {test_case['id'].replace('_', ' ').title()}")
        start_time = time.time()
        
        result = await generate_chart_code_with_retry(agent, test_case, output_dir)
        result["id"] = test_case["id"]
        result["title"] = test_case["title"]
        
        # Categorize result
        if "line" in test_case["id"] or "step" in test_case["id"] or "area" in test_case["id"]:
            results["trend"].append(result)
        elif "bar" in test_case["id"]:
            results["bar"].append(result)
        elif "histogram" in test_case["id"] or "box" in test_case["id"] or "violin" in test_case["id"]:
            results["distribution"].append(result)
        elif "scatter" in test_case["id"] or "bubble" in test_case["id"] or "hexbin" in test_case["id"]:
            results["correlation"].append(result)
        elif "pie" in test_case["id"] or "waterfall" in test_case["id"] or "funnel" in test_case["id"]:
            results["composition"].append(result)
        elif "radar" in test_case["id"] or "heatmap" in test_case["id"]:
            results["comparison"].append(result)
        elif "error" in test_case["id"] or "control" in test_case["id"] or "pareto" in test_case["id"]:
            results["statistical"].append(result)
        elif "gantt" in test_case["id"]:
            results["project"].append(result)
        
        all_results.append(result)
        
        # Ensure we wait at least 10 seconds between requests
        elapsed = time.time() - start_time
        if elapsed < 10 and i < len(ALL_CHART_TESTS):
            wait_time = 10 - elapsed
            print(f"  ⏳ Waiting {wait_time:.1f}s before next request...")
            await asyncio.sleep(wait_time)
    
    # Save results
    results_file = output_dir / "generation_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "summary": {
                "total": len(all_results),
                "successful": len([r for r in all_results if r["status"] == "success"]),
                "failed": len([r for r in all_results if r["status"] != "success"])
            },
            "by_category": results,
            "all_results": all_results
        }, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("GENERATION SUMMARY")
    print("="*80)
    
    successful = [r for r in all_results if r["status"] == "success"]
    failed = [r for r in all_results if r["status"] != "success"]
    
    print(f"\n📊 Total Charts: {len(all_results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📈 Success Rate: {len(successful)/len(all_results)*100:.1f}%")
    
    # Summary by category
    print("\n📈 By Category:")
    for category, items in results.items():
        success_count = len([r for r in items if r["status"] == "success"])
        total_count = len(items)
        if total_count > 0:
            print(f"  • {category.title()}: {success_count}/{total_count}")
    
    # List successful charts
    if successful:
        print(f"\n✅ Successfully Generated ({len(successful)}):")
        for r in successful[:10]:  # Show first 10
            print(f"  • {r['id']}: {r.get('chart_type', 'unknown')}")
        if len(successful) > 10:
            print(f"  ... and {len(successful) - 10} more")
    
    # List failed charts if any
    if failed:
        print(f"\n❌ Failed Charts ({len(failed)}):")
        for r in failed:
            print(f"  • {r['id']}: {r.get('message', 'Unknown error')[:50]}")
    
    print(f"\n📁 Files saved to: {output_dir.absolute()}/")
    print(f"📊 Results saved to: {results_file}")
    
    return output_dir, all_results


if __name__ == "__main__":
    # Run the comprehensive test with fixes
    print("\n🚀 Starting Fixed Chart Generation Test")
    print("This will take approximately 4-5 minutes with proper rate limiting\n")
    
    output_dir, results = asyncio.run(generate_all_charts_fixed())
    
    print("\n" + "="*80)
    print("STEP 1 COMPLETE - Code Generation with Fixes")
    print("="*80)
    success_count = len([r for r in results if r['status'] == 'success'])
    print(f"Generated {success_count} chart code files successfully")
    
    if success_count > 0:
        print(f"\n✅ SUCCESS! Generated {success_count}/23 charts")
        print(f"\nNext steps:")
        print(f"1. Run: python execute_all_charts_fixed.py")
        print(f"2. View gallery at: {output_dir}/gallery.html")
    else:
        print(f"\n⚠️ No charts were generated successfully. Check the errors above.")