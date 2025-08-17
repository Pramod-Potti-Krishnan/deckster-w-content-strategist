#!/usr/bin/env python
"""
Test Simplified MCP Implementation with Full Chart Gallery
==========================================================

This script tests the simplified MCP executor by generating all chart types
supported by the analytics agent. It creates a new gallery to compare with
the existing one.

Run with:
    python test_simplified_chart_gallery.py
"""

import asyncio
import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv()

# Set GEMINI_API_KEY from GOOGLE_API_KEY if needed
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Force use of simplified MCP
os.environ["USE_SIMPLIFIED_MCP"] = "true"

from src.agents.analytics_agent import create_analytics


async def save_chart_image(base64_str: str, filename: str, output_dir: Path):
    """Save base64 image to file."""
    if not base64_str:
        print(f"  ⚠️ No image data for {filename}")
        return False
    
    try:
        # Decode base64 and save
        image_data = base64.b64decode(base64_str)
        filepath = output_dir / filename
        with open(filepath, 'wb') as f:
            f.write(image_data)
        print(f"  ✅ Saved: {filename} ({len(image_data)} bytes)")
        return True
    except Exception as e:
        print(f"  ❌ Failed to save {filename}: {e}")
        return False


async def generate_chart_gallery():
    """Generate all chart types using simplified MCP."""
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"chart_gallery_simplified_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("TESTING SIMPLIFIED MCP WITH FULL CHART GALLERY")
    print("="*70)
    print(f"Output directory: {output_dir}")
    print(f"Using simplified MCP: {os.environ.get('USE_SIMPLIFIED_MCP', 'not set')}")
    
    # Define all test cases matching the gallery
    test_cases = [
        # Line charts
        {
            "name": "line_01_monthly_revenue",
            "request": "Show monthly revenue growth from January to June with values: Jan $45K, Feb $52K, Mar $48K, Apr $61K, May $58K, Jun $67K",
            "chart_type": "line",
            "title": "Monthly Revenue Growth"
        },
        {
            "name": "line_02_quarterly_trend",
            "request": "Display quarterly sales trend for 2024: Q1=$1.2M, Q2=$1.5M, Q3=$1.8M, Q4=$2.1M showing steady growth",
            "chart_type": "line",
            "title": "Quarterly Sales Trend 2024"
        },
        
        # Bar charts
        {
            "name": "bar_03_product_sales",
            "request": "Create a bar chart showing product category sales: Electronics $450K, Clothing $320K, Home & Garden $280K, Sports $195K, Books $150K",
            "chart_type": "bar",
            "title": "Sales by Product Category"
        },
        {
            "name": "bar_04_team_performance",
            "request": "Show team performance metrics: Sales 92%, Marketing 87%, Engineering 95%, Support 89%, HR 91%",
            "chart_type": "bar",
            "title": "Team Performance Metrics"
        },
        
        # Pie charts
        {
            "name": "pie_05_market_share",
            "request": "Display market share distribution: Company A 35%, Company B 28%, Company C 22%, Others 15%",
            "chart_type": "pie",
            "title": "Market Share Distribution"
        },
        {
            "name": "pie_06_budget_allocation",
            "request": "Show budget allocation: R&D 30%, Marketing 25%, Operations 20%, Sales 15%, Admin 10%",
            "chart_type": "pie",
            "title": "Budget Allocation"
        },
        
        # Scatter plots
        {
            "name": "scatter_07_correlation",
            "request": "Create a scatter plot showing correlation between advertising spend (thousands) and sales (thousands) with 20 data points showing positive correlation",
            "chart_type": "scatter",
            "title": "Ad Spend vs Sales Correlation"
        },
        {
            "name": "scatter_08_performance",
            "request": "Display scatter plot of employee performance: experience (years) vs productivity score for 25 employees",
            "chart_type": "scatter",
            "title": "Experience vs Productivity"
        },
        
        # Histograms
        {
            "name": "histogram_09_age_distribution",
            "request": "Show age distribution histogram for 500 customers with mean age 35 and std deviation 12",
            "chart_type": "histogram",
            "title": "Customer Age Distribution"
        },
        {
            "name": "histogram_10_response_times",
            "request": "Create histogram of API response times (ms) for 1000 requests, showing most responses between 50-150ms",
            "chart_type": "histogram",
            "title": "API Response Time Distribution"
        },
        
        # Heatmaps
        {
            "name": "heatmap_11_correlation_matrix",
            "request": "Generate correlation heatmap between 5 metrics: Revenue, Costs, Profit, Customers, Satisfaction",
            "chart_type": "heatmap",
            "title": "Business Metrics Correlation"
        },
        {
            "name": "heatmap_12_activity_map",
            "request": "Create weekly activity heatmap showing user engagement levels across 7 days and 24 hours",
            "chart_type": "heatmap",
            "title": "User Activity Heatmap"
        },
        
        # Area charts
        {
            "name": "area_13_cumulative_growth",
            "request": "Display cumulative revenue growth area chart over 12 months showing steady increase from $100K to $1.5M",
            "chart_type": "area",
            "title": "Cumulative Revenue Growth"
        },
        {
            "name": "area_14_stacked_categories",
            "request": "Show stacked area chart of sales by region over 4 quarters: North, South, East, West",
            "chart_type": "area",
            "title": "Regional Sales Over Time"
        },
        
        # Waterfall chart
        {
            "name": "waterfall_15_profit_breakdown",
            "request": "Create waterfall chart showing profit breakdown: Starting $500K, Sales +$300K, Returns -$50K, Costs -$200K, Tax -$75K, Final $475K",
            "chart_type": "waterfall",
            "title": "Profit Breakdown Analysis"
        },
        
        # Treemap
        {
            "name": "treemap_16_portfolio",
            "request": "Generate treemap of investment portfolio: Stocks 40%, Bonds 30%, Real Estate 20%, Commodities 10%",
            "chart_type": "treemap",
            "title": "Investment Portfolio Breakdown"
        }
    ]
    
    # Track results
    results = {
        "success": [],
        "failed": [],
        "code_only": []
    }
    
    print(f"\nGenerating {len(test_cases)} charts...\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Generating: {test['name']}")
        print(f"  Type: {test['chart_type']}")
        print(f"  Title: {test['title']}")
        
        try:
            # Generate the chart
            result = await create_analytics(
                content=test['request'],
                title=test['title'],
                chart_type=test['chart_type']
            )
            
            if result['success']:
                format_type = result.get('format', 'unknown')
                print(f"  Format: {format_type}")
                
                if format_type == 'base64':
                    # We have an actual image
                    filename = f"{test['name']}.png"
                    if await save_chart_image(result['content'], filename, output_dir):
                        results["success"].append(test['name'])
                    else:
                        results["failed"].append(test['name'])
                        
                elif format_type == 'python_code':
                    # MCP not available, got code instead
                    print(f"  ⚠️ Got Python code instead of image (MCP not available)")
                    # Save the code for reference
                    code_file = output_dir / f"{test['name']}.py"
                    with open(code_file, 'w') as f:
                        f.write(result['content'])
                    results["code_only"].append(test['name'])
                    
                elif format_type == 'mermaid':
                    # Got Mermaid syntax
                    print(f"  📊 Got Mermaid syntax")
                    # Save the Mermaid code
                    mermaid_file = output_dir / f"{test['name']}.mmd"
                    with open(mermaid_file, 'w') as f:
                        f.write(result['content'])
                    results["success"].append(test['name'])
                    
                else:
                    print(f"  ❓ Unknown format: {format_type}")
                    results["failed"].append(test['name'])
            else:
                print(f"  ❌ Generation failed")
                results["failed"].append(test['name'])
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results["failed"].append(test['name'])
    
    # Generate HTML gallery
    print("\n" + "="*70)
    print("GENERATING HTML GALLERY")
    print("="*70)
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Simplified MCP Chart Gallery</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .info {
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .chart-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 15px;
        }
        .chart-card h3 {
            margin-top: 0;
            color: #495057;
        }
        .chart-card img {
            width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        .chart-card .type {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-bottom: 10px;
        }
        .code-notice {
            background: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .mermaid-notice {
            background: #d1ecf1;
            color: #0c5460;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .stat {
            background: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .stat .number {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat .label {
            font-size: 12px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <h1>🎨 Simplified MCP Chart Gallery</h1>
    
    <div class="info">
        <h2>Test Results</h2>
        <p><strong>Generated:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p><strong>MCP Implementation:</strong> Simplified (mcp_executor_simplified.py)</p>
        <p><strong>Total Charts:</strong> """ + str(len(test_cases)) + """</p>
        
        <div class="stats">
            <div class="stat">
                <div class="number">""" + str(len(results['success'])) + """</div>
                <div class="label">Successful</div>
            </div>
            <div class="stat">
                <div class="number">""" + str(len(results['code_only'])) + """</div>
                <div class="label">Code Only</div>
            </div>
            <div class="stat">
                <div class="number">""" + str(len(results['failed'])) + """</div>
                <div class="label">Failed</div>
            </div>
        </div>
    </div>
    
    <div class="gallery">
"""
    
    # Add chart cards
    for test in test_cases:
        html_content += f"""
        <div class="chart-card">
            <span class="type">{test['chart_type'].upper()}</span>
            <h3>{test['title']}</h3>
"""
        
        # Check what we generated
        png_file = output_dir / f"{test['name']}.png"
        py_file = output_dir / f"{test['name']}.py"
        mmd_file = output_dir / f"{test['name']}.mmd"
        
        if png_file.exists():
            html_content += f'            <img src="{test["name"]}.png" alt="{test["title"]}">\n'
        elif mmd_file.exists():
            html_content += f'            <div class="mermaid-notice">📊 Mermaid chart generated (view in Mermaid editor)</div>\n'
        elif py_file.exists():
            html_content += f'            <div class="code-notice">⚠️ Python code generated (MCP not available for execution)</div>\n'
        else:
            html_content += f'            <div class="code-notice">❌ Generation failed</div>\n'
        
        html_content += """        </div>
"""
    
    html_content += """    </div>
</body>
</html>
"""
    
    # Save HTML
    html_file = output_dir / "index.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    print(f"✅ HTML gallery saved to: {html_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Successful: {len(results['success'])} charts")
    print(f"⚠️ Code only: {len(results['code_only'])} charts (MCP not available)")
    print(f"❌ Failed: {len(results['failed'])} charts")
    print(f"\nOutput directory: {output_dir}")
    print(f"View gallery: open {output_dir}/index.html")
    
    return results


async def main():
    """Main entry point."""
    try:
        results = await generate_chart_gallery()
        
        # Exit with error if any failed
        if results['failed']:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())