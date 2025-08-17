#!/usr/bin/env python3
"""
Test 8 specific chart types with Analytics V2 implementation.
Charts: Horizontal Bar, Violin Plot, Stacked Area, Box Plot, Radar Plot, Bubble Plot, Funnel, Scatter Plot
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.agents.analytics_agent_v2 import create_analytics_v2
from src.agents.analytics_utils_v2.models import ChartType


async def test_eight_charts():
    """Test 8 specific chart types."""
    
    print("=" * 80)
    print("TESTING 8 SPECIFIC CHART TYPES WITH ANALYTICS V2")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}")
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"test_8_charts_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}\n")
    
    # Define test cases for the 8 charts
    test_cases = [
        {
            "chart_type": ChartType.BAR_HORIZONTAL,
            "content": "Rank top 10 products by customer satisfaction score from highest to lowest",
            "title": "Top Product Rankings - Horizontal"
        },
        {
            "chart_type": ChartType.VIOLIN_PLOT,
            "content": "Show response time distributions for different server regions with bimodal patterns",
            "title": "Server Response Time Distribution"
        },
        {
            "chart_type": ChartType.STACKED_AREA_CHART,
            "content": "Display revenue composition across 4 product categories over 12 months showing cumulative growth",
            "title": "Revenue by Category - Stacked Area"
        },
        {
            "chart_type": ChartType.BOX_PLOT,
            "content": "Compare salary distributions across 5 departments showing quartiles and outliers",
            "title": "Salary Distribution by Department"
        },
        {
            "chart_type": ChartType.RADAR_CHART,
            "content": "Compare skill levels across 6 competencies for team assessment",
            "title": "Team Skills Assessment Radar"
        },
        {
            "chart_type": ChartType.BUBBLE_CHART,
            "content": "Analyze products by price (x), sales volume (y), and profit margin (size)",
            "title": "Product Performance Bubble Chart"
        },
        {
            "chart_type": ChartType.FUNNEL,
            "content": "Visualize conversion rates through 5-stage sales pipeline from lead to close",
            "title": "Sales Pipeline Funnel"
        },
        {
            "chart_type": ChartType.SCATTER_PLOT,
            "content": "Analyze correlation between marketing spend and sales revenue across campaigns",
            "title": "Marketing Spend vs Revenue"
        }
    ]
    
    results = []
    successful = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/8] Testing {test_case['chart_type'].value}...")
        print(f"  Content: {test_case['content'][:60]}...")
        
        try:
            # Generate chart
            response = await create_analytics_v2(
                content=test_case["content"],
                title=test_case["title"],
                chart_type=test_case["chart_type"].value,
                use_synthetic_data=True,
                theme={
                    "primary": "#2563EB",
                    "secondary": "#EC4899",
                    "tertiary": "#06B6D4",
                    "style": "modern",
                    "gradient": True
                },
                enhance_labels=True,
                save_files=True,
                output_dir=str(output_dir)
            )
            
            if response.get("success"):
                print(f"  ✓ Success!")
                successful += 1
                
                # Check for PNG file
                png_files = list(output_dir.glob(f"*{test_case['chart_type'].value}*.png"))
                if png_files:
                    png_file = png_files[0]
                    print(f"  PNG: {png_file.name} ({png_file.stat().st_size:,} bytes)")
                else:
                    print(f"  ⚠ PNG file not found")
                
                # Check for JSON file
                json_files = list(output_dir.glob(f"*{test_case['chart_type'].value}*_data.json"))
                if json_files:
                    print(f"  JSON: {json_files[0].name}")
            else:
                print(f"  ✗ Failed: {response.get('error')}")
                failed += 1
            
            results.append({
                "chart_type": test_case["chart_type"].value,
                "title": test_case["title"],
                "success": response.get("success", False),
                "error": response.get("error"),
                "metadata": response.get("metadata")
            })
            
            # Wait 7 seconds between API calls
            if i < len(test_cases):
                print("  Waiting 7 seconds for rate limiting...")
                await asyncio.sleep(7)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
            results.append({
                "chart_type": test_case["chart_type"].value,
                "title": test_case["title"],
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total charts tested: 8")
    print(f"Successful: {successful} ({successful/8*100:.1f}%)")
    print(f"Failed: {failed} ({failed/8*100:.1f}%)")
    
    if successful > 0:
        print("\n✓ Successfully generated:")
        for result in results:
            if result["success"]:
                print(f"  - {result['chart_type']}")
    
    if failed > 0:
        print("\n✗ Failed charts:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['chart_type']}: {result.get('error', 'Unknown error')}")
    
    # Save results
    results_file = output_dir / "test_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": 8,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / 8 if successful else 0
            },
            "results": results
        }, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    # Generate HTML gallery
    html = generate_gallery_html(results, output_dir)
    gallery_file = output_dir / "gallery.html"
    with open(gallery_file, "w") as f:
        f.write(html)
    print(f"Gallery saved to: {gallery_file}")
    
    print("\n" + "=" * 80)
    print(f"Test completed at: {datetime.now().isoformat()}")
    print("=" * 80)
    
    return results


def generate_gallery_html(results, output_dir):
    """Generate HTML gallery for the 8 charts."""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>8 Chart Types Test - Analytics V2</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-top: 30px; }
        .card { background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #2563EB; }
        .card img { width: 100%; height: 400px; object-fit: contain; border: 1px solid #e0e0e0; border-radius: 4px; background: white; }
        .success { color: #10B981; font-weight: bold; }
        .failed { color: #EF4444; font-weight: bold; }
        .stats { background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
    </style>
</head>
<body>
    <h1>8 Chart Types Test - Analytics V2</h1>
    """
    
    # Add statistics
    successful = sum(1 for r in results if r["success"])
    html += f"""
    <div class="stats">
        <h2>Test Results</h2>
        <p>Total Charts: 8</p>
        <p class="success">Successful: {successful}</p>
        <p class="failed">Failed: {8 - successful}</p>
        <p>Success Rate: {successful/8*100:.1f}%</p>
    </div>
    """
    
    # Add chart grid
    html += '<div class="grid">'
    
    for result in results:
        chart_type = result["chart_type"]
        status_class = "success" if result["success"] else "failed"
        
        html += f"""
        <div class="card">
            <h3>{chart_type.replace('_', ' ').title()}</h3>
            <p>Title: {result['title']}</p>
            <p class="{status_class}">Status: {'Success' if result['success'] else 'Failed'}</p>
        """
        
        if result["success"]:
            # Find PNG file
            png_files = list(output_dir.glob(f"*{chart_type}*.png"))
            if png_files:
                png_file = png_files[0].name
                html += f'<img src="{png_file}" alt="{chart_type}">'
        else:
            html += f'<p style="color: #666;">Error: {result.get("error", "Unknown error")}</p>'
        
        html += "</div>"
    
    html += """
    </div>
</body>
</html>
    """
    
    return html


if __name__ == "__main__":
    asyncio.run(test_eight_charts())