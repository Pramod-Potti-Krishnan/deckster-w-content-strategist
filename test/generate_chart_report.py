#!/usr/bin/env python
"""
Generate HTML Report for Chart Tests
====================================

Creates a beautiful HTML report with all chart visualizations.
"""

import os
import sys
import asyncio
import base64
import json
from pathlib import Path
from datetime import datetime

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics
from src.agents.analytics_utils.pydantic_mcp_server import pydantic_mcp_executor


async def generate_all_charts():
    """Generate all chart types and create HTML report."""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE CHART GENERATION")
    print("="*80)
    
    # Create output directory
    output_dir = Path("test/chart_gallery")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define all test cases
    test_cases = [
        # Line Charts
        {
            "category": "Time Series Charts",
            "title": "Monthly Sales Trend",
            "description": "Monthly sales: Jan $45K, Feb $52K, Mar $48K, Apr $61K, May $58K, Jun $72K, Jul $69K, Aug $75K",
            "chart_type": "line"
        },
        {
            "category": "Time Series Charts",
            "title": "Quarterly Revenue Growth",
            "description": "Q1 2024: $2.5M, Q2: $3.1M, Q3: $3.4M, Q4: $4.2M showing strong growth",
            "chart_type": "line"
        },
        
        # Bar Charts
        {
            "category": "Comparison Charts",
            "title": "Product Category Sales",
            "description": "Sales by category: Electronics $450K, Clothing $320K, Home $280K, Sports $195K, Books $155K",
            "chart_type": "bar"
        },
        {
            "category": "Comparison Charts",
            "title": "Regional Performance",
            "description": "Regional sales: North $1.2M, South $980K, East $1.1M, West $1.3M, Central $750K",
            "chart_type": "bar"
        },
        
        # Pie Charts
        {
            "category": "Distribution Charts",
            "title": "Market Share Analysis",
            "description": "Market share: Our Company 35%, Competitor A 28%, Competitor B 20%, Competitor C 12%, Others 5%",
            "chart_type": "pie"
        },
        {
            "category": "Distribution Charts",
            "title": "Budget Allocation",
            "description": "Budget distribution: R&D 30%, Marketing 25%, Operations 20%, Sales 15%, Admin 10%",
            "chart_type": "pie"
        },
        
        # Scatter Plots
        {
            "category": "Correlation Analysis",
            "title": "Marketing Spend vs Revenue",
            "description": "Marketing (K) vs Revenue (K): (10,45), (15,58), (20,72), (25,85), (30,98), (35,112), (40,125)",
            "chart_type": "scatter"
        },
        {
            "category": "Correlation Analysis",
            "title": "Customer Satisfaction vs Retention",
            "description": "Satisfaction vs Retention %: (70,65), (75,72), (80,78), (85,85), (90,92), (95,96)",
            "chart_type": "scatter"
        },
        
        # Histograms
        {
            "category": "Statistical Charts",
            "title": "Age Distribution",
            "description": "Customer age distribution: 500 customers with mean age 38, std deviation 12",
            "chart_type": "histogram"
        },
        {
            "category": "Statistical Charts",
            "title": "Response Time Analysis",
            "description": "Response times in milliseconds: mean 250ms, std 50ms, 1000 samples",
            "chart_type": "histogram"
        },
        
        # Heatmaps
        {
            "category": "Matrix Visualizations",
            "title": "Correlation Heatmap",
            "description": "Create 5x5 correlation matrix for Sales, Marketing, Costs, Profit, Growth metrics",
            "chart_type": "heatmap"
        },
        {
            "category": "Matrix Visualizations",
            "title": "Activity Heatmap",
            "description": "Weekly activity heatmap: 7 days x 24 hours showing user engagement patterns",
            "chart_type": "heatmap"
        },
        
        # Area Charts
        {
            "category": "Cumulative Charts",
            "title": "Website Traffic Growth",
            "description": "Daily traffic (thousands): Mon 12, Tue 15, Wed 18, Thu 22, Fri 28, Sat 35, Sun 30",
            "chart_type": "area"
        },
        {
            "category": "Cumulative Charts",
            "title": "Cumulative Revenue",
            "description": "Monthly cumulative revenue: Jan 100K, Feb 220K, Mar 380K, Apr 550K, May 750K, Jun 980K",
            "chart_type": "area"
        },
        
        # Special Charts
        {
            "category": "Advanced Analytics",
            "title": "Waterfall Analysis",
            "description": "Profit waterfall: Revenue $500K, +Sales $200K, +Services $150K, -Costs $180K, -Marketing $50K, =Net $620K",
            "chart_type": "waterfall"
        },
        {
            "category": "Advanced Analytics",
            "title": "Department Treemap",
            "description": "Department sizes: Engineering 45%, Sales 20%, Marketing 15%, Operations 12%, Support 8%",
            "chart_type": "treemap"
        }
    ]
    
    results = []
    print(f"\n📊 Generating {len(test_cases)} charts...")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test['title']}")
        print(f"  Type: {test['chart_type']}")
        
        try:
            result = await create_analytics(
                test['description'],
                title=test['title'],
                chart_type=test['chart_type'],
                mcp_tool=pydantic_mcp_executor
            )
            
            if result['success']:
                test_result = {
                    'test': test,
                    'success': True,
                    'format': result['format'],
                    'content': result.get('content', ''),
                    'csv_data': result.get('csv_data', ''),
                    'data': result.get('data', []),
                    'insights': result.get('insights', [])[:3]
                }
                
                if result['format'] == 'base64':
                    # Save PNG
                    img_data = base64.b64decode(result['content'])
                    filename = f"{test['chart_type']}_{i:02d}.png"
                    filepath = output_dir / filename
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    test_result['image_file'] = str(filepath)
                    print(f"  ✅ Generated {len(img_data):,} byte image")
                else:
                    print(f"  ✅ Generated {result['format']} chart")
                
                results.append(test_result)
            else:
                results.append({
                    'test': test,
                    'success': False,
                    'error': 'Generation failed'
                })
                print(f"  ❌ Failed")
                
        except Exception as e:
            results.append({
                'test': test,
                'success': False,
                'error': str(e)
            })
            print(f"  ❌ Error: {e}")
    
    # Generate HTML report
    generate_html_report(results, output_dir)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"📄 Report saved to: test/chart_gallery/index.html")
    print(f"🌐 Open in browser: file://{(output_dir / 'index.html').absolute()}")


def csv_to_html_table(csv_data):
    """Convert CSV data to HTML table rows."""
    if not csv_data:
        return "<tr><td>No data available</td></tr>"
    
    try:
        import csv
        import io
        
        reader = csv.reader(io.StringIO(csv_data))
        rows = list(reader)
        
        if not rows:
            return "<tr><td>No data available</td></tr>"
        
        # Create header row
        html = "<thead><tr>"
        for header in rows[0]:
            html += f"<th>{header}</th>"
        html += "</tr></thead><tbody>"
        
        # Create data rows
        for row in rows[1:]:
            html += "<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html += "</tr>"
        
        html += "</tbody>"
        return html
    except Exception as e:
        return f"<tr><td>Error parsing data: {str(e)}</td></tr>"


def generate_html_report(results, output_dir):
    """Generate HTML report with all charts."""
    
    # HTML template with escaped braces
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Chart Gallery</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11.9.0/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .header {
            background: white;
            padding: 40px;
            text-align: center;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }
        
        h1 {
            margin: 0;
            color: #333;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-top: 10px;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
        }
        
        .stat {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.2em;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .category {
            margin-bottom: 50px;
        }
        
        .category-title {
            color: white;
            font-size: 1.8em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
        }
        
        .chart-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        
        .chart-card:hover {
            transform: translateY(-5px);
        }
        
        .chart-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
        }
        
        .chart-title {
            font-size: 1.3em;
            margin: 0;
        }
        
        .chart-type {
            opacity: 0.9;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .chart-description {
            padding: 15px 20px;
            background: #f8f9fa;
            color: #555;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .chart-content {
            padding: 30px;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
        }
        
        .chart-content img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .insights {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }
        
        .insight {
            color: #333;
            margin: 10px 0;
            padding-left: 25px;
            position: relative;
        }
        
        .insight:before {
            content: "💡";
            position: absolute;
            left: 0;
        }
        
        .error {
            color: #d32f2f;
            padding: 20px;
            text-align: center;
        }
        
        .mermaid {
            max-width: 100%;
        }
        
        .data-table-section {
            background: #f1f3f5;
            padding: 20px;
            border-top: 1px solid #dee2e6;
        }
        
        .data-table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .data-table-title {
            font-weight: 600;
            color: #495057;
            font-size: 1.1em;
        }
        
        .toggle-table-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: opacity 0.3s ease;
        }
        
        .toggle-table-btn:hover {
            opacity: 0.8;
        }
        
        .data-table-wrapper {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            max-height: 400px;
            overflow-y: auto;
            display: none;
        }
        
        .data-table-wrapper.visible {
            display: block;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .data-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .data-table tr:hover {
            background: #f8f9fa;
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
    </style>
    <script>
        function toggleTable(tableId) {
            const wrapper = document.getElementById(tableId);
            const btn = document.getElementById(tableId + '-btn');
            if (wrapper.classList.contains('visible')) {
                wrapper.classList.remove('visible');
                btn.textContent = 'Show Data';
            } else {
                wrapper.classList.add('visible');
                btn.textContent = 'Hide Data';
            }
        }
    </script>
</head>
<body>
    <div class="header">
        <h1>📊 Analytics Chart Gallery</h1>
        <p class="subtitle">Comprehensive visualization of all supported chart types</p>
        <p class="subtitle">Generated: ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</p>
        <div class="stats">
            <div class="stat">Total Charts: ''' + str(len(results)) + '''</div>
            <div class="stat">Successful: ''' + str(sum(1 for r in results if r['success'])) + '''</div>
            <div class="stat">Chart Types: ''' + str(len(set(r['test']['chart_type'] for r in results))) + '''</div>
        </div>
    </div>
    
    <div class="container">
'''
    
    # Group by category
    categories = {}
    for result in results:
        cat = result['test']['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)
    
    # Generate each category
    for category, cat_results in categories.items():
        html += f'''
        <div class="category">
            <h2 class="category-title">{category}</h2>
            <div class="chart-grid">
'''
        
        for idx, result in enumerate(cat_results):
            test = result['test']
            
            html += f'''
                <div class="chart-card">
                    <div class="chart-header">
                        <h3 class="chart-title">{test['title']}</h3>
                        <div class="chart-type">Chart Type: {test['chart_type']}</div>
                    </div>
                    <div class="chart-description">{test['description']}</div>
                    <div class="chart-content">
'''
            
            if result['success']:
                if result['format'] == 'base64':
                    # Embed image
                    img_data = base64.b64decode(result['content'])
                    img_base64 = base64.b64encode(img_data).decode()
                    html += f'<img src="data:image/png;base64,{img_base64}" alt="{test["title"]}">'
                elif result['format'] == 'mermaid':
                    # Embed Mermaid
                    html += f'<div class="mermaid">{result["content"]}</div>'
                else:
                    html += f'<p>Format: {result["format"]}</p>'
            else:
                html += f'<div class="error">Error: {result.get("error", "Unknown")}</div>'
            
            html += '''
                    </div>
'''
            
            # Add insights if available
            if result.get('insights'):
                html += '                    <div class="insights">\n'
                for insight in result['insights']:
                    html += f'                        <div class="insight">{insight}</div>\n'
                html += '                    </div>\n'
            
            # Add data table if available
            if result.get('csv_data'):
                table_id = f"table-{test['chart_type']}-{idx}"
                html += f'''
                    <div class="data-table-section">
                        <div class="data-table-header">
                            <span class="data-table-title">📊 Chart Data</span>
                            <button id="{table_id}-btn" class="toggle-table-btn" onclick="toggleTable('{table_id}')">Show Data</button>
                        </div>
                        <div id="{table_id}" class="data-table-wrapper">
                            <table class="data-table">
                                {csv_to_html_table(result['csv_data'])}
                            </table>
                        </div>
                    </div>
'''
            
            html += '                </div>\n'
        
        html += '''
            </div>
        </div>
'''
    
    html += '''
    </div>
    
    <script>
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default'
        });
    </script>
</body>
</html>
'''
    
    # Save HTML
    report_path = output_dir / "index.html"
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"\n📄 HTML report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(generate_all_charts())