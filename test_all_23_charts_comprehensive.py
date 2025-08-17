#!/usr/bin/env python3
"""
Comprehensive Test for All 23 Chart Types
==========================================

Tests all 23 chart types with synthetic data and proper rate limiting.
Implements 7-second delays between calls to respect Gemini API limits.

Author: Analytics Agent System V2
Date: 2024
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from src.agents.analytics_agent_v2 import create_analytics_v2
from src.agents.analytics_utils_v2.models import ChartType

# Load environment variables
load_dotenv()


# Define all 23 chart types with appropriate test data
CHART_TEST_CASES = [
    # Line and Trend Charts
    {
        "chart_type": ChartType.LINE_CHART,
        "content": "Show monthly revenue trend for the past year with seasonal patterns",
        "title": "Monthly Revenue Trend 2024"
    },
    {
        "chart_type": ChartType.STEP_CHART,
        "content": "Display inventory levels over time with step changes at restocking points",
        "title": "Inventory Step Changes"
    },
    {
        "chart_type": ChartType.AREA_CHART,
        "content": "Visualize website traffic growth over the last 6 months",
        "title": "Website Traffic Growth"
    },
    {
        "chart_type": ChartType.STACKED_AREA_CHART,
        "content": "Show revenue composition across product categories over quarters",
        "title": "Revenue by Category Over Time"
    },
    
    # Bar Charts
    {
        "chart_type": ChartType.BAR_VERTICAL,
        "content": "Compare sales performance across 8 different regions",
        "title": "Regional Sales Comparison"
    },
    {
        "chart_type": ChartType.BAR_HORIZONTAL,
        "content": "Rank top 10 products by customer satisfaction score",
        "title": "Product Satisfaction Rankings"
    },
    {
        "chart_type": ChartType.GROUPED_BAR,
        "content": "Compare Q1 vs Q2 sales across 5 product lines",
        "title": "Quarterly Sales by Product Line"
    },
    {
        "chart_type": ChartType.STACKED_BAR,
        "content": "Show budget allocation across departments with subcategories",
        "title": "Department Budget Breakdown"
    },
    
    # Distribution Charts
    {
        "chart_type": ChartType.HISTOGRAM,
        "content": "Analyze distribution of customer ages in our database",
        "title": "Customer Age Distribution"
    },
    {
        "chart_type": ChartType.BOX_PLOT,
        "content": "Compare salary distributions across 5 departments with outliers",
        "title": "Salary Distribution by Department"
    },
    {
        "chart_type": ChartType.VIOLIN_PLOT,
        "content": "Show response time distributions for different server regions with bimodal patterns",
        "title": "Server Response Time Analysis"
    },
    
    # Correlation Charts
    {
        "chart_type": ChartType.SCATTER_PLOT,
        "content": "Analyze correlation between marketing spend and sales revenue",
        "title": "Marketing Spend vs Revenue"
    },
    {
        "chart_type": ChartType.BUBBLE_CHART,
        "content": "Compare products by price, sales volume, and profit margin",
        "title": "Product Performance Matrix"
    },
    {
        "chart_type": ChartType.HEXBIN,
        "content": "Visualize density of customer locations on price vs satisfaction grid",
        "title": "Customer Satisfaction Density Map"
    },
    
    # Composition Charts
    {
        "chart_type": ChartType.PIE_CHART,
        "content": "Show market share distribution among top 5 competitors",
        "title": "Market Share 2024"
    },
    {
        "chart_type": ChartType.WATERFALL,
        "content": "Break down profit changes from Q1 to Q2 with contributing factors",
        "title": "Profit Bridge Analysis"
    },
    {
        "chart_type": ChartType.FUNNEL,
        "content": "Visualize conversion rates through 5-stage sales pipeline",
        "title": "Sales Pipeline Conversion"
    },
    
    # Comparison Charts
    {
        "chart_type": ChartType.RADAR_CHART,
        "content": "Compare skill levels across 6 competencies for team assessment",
        "title": "Team Skills Assessment"
    },
    {
        "chart_type": ChartType.HEATMAP,
        "content": "Show correlation matrix between 8 business metrics",
        "title": "Business Metrics Correlation"
    },
    
    # Statistical Charts
    {
        "chart_type": ChartType.ERROR_BAR,
        "content": "Display experimental results with confidence intervals across 6 trials",
        "title": "Experimental Results with Error Bars"
    },
    {
        "chart_type": ChartType.CONTROL_CHART,
        "content": "Monitor production quality metrics with control limits over 20 samples",
        "title": "Quality Control Chart"
    },
    {
        "chart_type": ChartType.PARETO,
        "content": "Analyze defect types showing 80/20 rule with cumulative percentage",
        "title": "Defect Analysis - Pareto Chart"
    },
    
    # Project Charts
    {
        "chart_type": ChartType.GANTT,
        "content": "Display project timeline with 6 tasks, dependencies, and milestones",
        "title": "Project Implementation Timeline"
    }
]


async def test_single_chart(
    test_case: Dict[str, Any],
    output_dir: Path,
    index: int,
    total: int
) -> Dict[str, Any]:
    """Test a single chart type."""
    
    chart_type = test_case["chart_type"]
    print(f"\n[{index}/{total}] Testing {chart_type.value}...")
    print(f"  Content: {test_case['content'][:80]}...")
    
    start_time = time.time()
    result = {
        "chart_type": chart_type.value,
        "index": index,
        "status": "pending",
        "error": None,
        "files": [],
        "execution_time": 0
    }
    
    try:
        # Create analytics with specific chart type
        response = await create_analytics_v2(
            content=test_case["content"],
            title=test_case["title"],
            data=None,  # Use synthetic data
            use_synthetic_data=True,
            theme={
                "primary": "#2563EB",
                "secondary": "#EC4899", 
                "tertiary": "#06B6D4",
                "style": "modern"
            },
            chart_type=chart_type.value,
            enhance_labels=True,
            save_files=True,
            output_dir=str(output_dir)
        )
        
        # Check response
        if response.get("success"):
            result["status"] = "success"
            
            # Check for PNG file
            png_file = output_dir / f"{chart_type.value}_{index:02d}.png"
            if png_file.exists():
                result["files"].append(str(png_file))
                file_size = png_file.stat().st_size
                print(f"  ✓ PNG generated: {file_size:,} bytes")
            else:
                print(f"  ⚠ PNG file not found")
            
            # Check for JSON file
            json_file = output_dir / f"{chart_type.value}_{index:02d}_data.json"
            if json_file.exists():
                result["files"].append(str(json_file))
                print(f"  ✓ JSON data saved")
            
            # Record insights
            metadata = response.get("metadata", {})
            if metadata.get("insights"):
                print(f"  Insights: {metadata['insights'][0]}")
            
        else:
            result["status"] = "failed"
            result["error"] = response.get("error", "Unknown error")
            print(f"  ✗ Failed: {result['error']}")
    
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"  ✗ Error: {e}")
    
    result["execution_time"] = time.time() - start_time
    print(f"  Time: {result['execution_time']:.2f}s")
    
    return result


async def run_comprehensive_test():
    """Run comprehensive test of all 23 chart types."""
    
    print("=" * 80)
    print("COMPREHENSIVE ANALYTICS V2 TEST - ALL 23 CHART TYPES")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Total charts to test: {len(CHART_TEST_CASES)}")
    print(f"Rate limiting: 7 seconds between API calls")
    print("=" * 80)
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"comprehensive_test_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Test results
    results = []
    successful = 0
    failed = 0
    
    # Test each chart type with rate limiting
    for i, test_case in enumerate(CHART_TEST_CASES, 1):
        # Test the chart
        result = await test_single_chart(test_case, output_dir, i, len(CHART_TEST_CASES))
        results.append(result)
        
        # Update counters
        if result["status"] == "success":
            successful += 1
        else:
            failed += 1
        
        # Rate limiting - wait 7 seconds between calls (except for last one)
        if i < len(CHART_TEST_CASES):
            print(f"  Waiting 7 seconds for rate limiting...")
            await asyncio.sleep(7)
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total charts tested: {len(results)}")
    print(f"Successful: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(results)*100:.1f}%)")
    
    # List successful charts
    print("\n✓ Successful charts:")
    for result in results:
        if result["status"] == "success":
            print(f"  - {result['chart_type']}")
    
    # List failed charts
    if failed > 0:
        print("\n✗ Failed charts:")
        for result in results:
            if result["status"] != "success":
                print(f"  - {result['chart_type']}: {result['error']}")
    
    # Save detailed results
    results_file = output_dir / "test_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": failed,
                "success_rate": successful / len(results) if results else 0
            },
            "results": results
        }, f, indent=2)
    print(f"\nDetailed results saved to: {results_file}")
    
    # Generate HTML gallery
    gallery_html = generate_gallery_html(results, output_dir)
    gallery_file = output_dir / "gallery.html"
    with open(gallery_file, "w") as f:
        f.write(gallery_html)
    print(f"HTML gallery saved to: {gallery_file}")
    
    print("\n" + "=" * 80)
    print(f"Test completed at: {datetime.now().isoformat()}")
    print("=" * 80)
    
    return results


def generate_gallery_html(results: List[Dict], output_dir: Path) -> str:
    """Generate HTML gallery of all charts."""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Analytics V2 - Comprehensive Test Gallery</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .chart-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-card h3 {
            margin-top: 0;
            color: #2563EB;
        }
        .chart-card img {
            width: 100%;
            height: 300px;
            object-fit: contain;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background: white;
        }
        .success { color: #10B981; }
        .failed { color: #EF4444; }
        .metadata {
            font-size: 12px;
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Analytics V2 - Comprehensive Test Gallery</h1>
    """
    
    # Add statistics
    successful = sum(1 for r in results if r["status"] == "success")
    html += f"""
    <div class="stats">
        <h2>Test Statistics</h2>
        <p>Total Charts: {len(results)}</p>
        <p class="success">Successful: {successful}</p>
        <p class="failed">Failed: {len(results) - successful}</p>
        <p>Success Rate: {successful/len(results)*100:.1f}%</p>
        <p>Generated: {datetime.now().isoformat()}</p>
    </div>
    """
    
    # Add chart grid
    html += '<div class="chart-grid">'
    
    for result in results:
        status_class = "success" if result["status"] == "success" else "failed"
        html += f"""
        <div class="chart-card">
            <h3>{result['chart_type'].replace('_', ' ').title()}</h3>
            <p class="{status_class}">Status: {result['status']}</p>
        """
        
        if result["status"] == "success" and result["files"]:
            # Find PNG file
            png_files = [f for f in result["files"] if f.endswith('.png')]
            if png_files:
                png_file = Path(png_files[0]).name
                html += f'<img src="{png_file}" alt="{result["chart_type"]}">'
        elif result["error"]:
            html += f'<p style="color: #666;">Error: {result["error"]}</p>'
        
        html += f"""
            <div class="metadata">
                Execution time: {result.get('execution_time', 0):.2f}s
            </div>
        </div>
        """
    
    html += """
    </div>
</body>
</html>
    """
    
    return html


if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(run_comprehensive_test())