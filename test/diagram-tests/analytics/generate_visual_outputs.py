"""
Generate Visual Outputs for Analytics Charts
=============================================

Creates actual chart files for viewing.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# Load environment variables
load_dotenv()

# Set GEMINI_API_KEY from GOOGLE_API_KEY if not already set
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics


async def save_mermaid_html(mermaid_code: str, filename: str, title: str):
    """Save Mermaid code as viewable HTML file."""
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4a90e2;
            padding-bottom: 10px;
        }}
        .mermaid {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metadata {{
            margin-top: 20px;
            padding: 15px;
            background: #e8f4f8;
            border-radius: 5px;
        }}
        .insights {{
            margin-top: 15px;
            padding: 15px;
            background: #f0f8e8;
            border-radius: 5px;
        }}
        .data-table {{
            margin-top: 20px;
            width: 100%;
            border-collapse: collapse;
        }}
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .data-table th {{
            background: #4a90e2;
            color: white;
        }}
        .data-table tr:nth-child(even) {{
            background: #f9f9f9;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="mermaid">
{mermaid_code}
    </div>
    {additional_content}
</body>
</html>"""
    
    with open(filename, 'w') as f:
        f.write(html_template.format(
            title=title,
            mermaid_code=mermaid_code,
            additional_content=""
        ))


async def save_python_code(python_code: str, filename: str):
    """Save Python code to file."""
    with open(filename, 'w') as f:
        f.write(python_code)


async def save_chart_with_metadata(result: dict, base_filename: str, output_dir: str):
    """Save chart with all metadata and insights."""
    
    # Create full HTML with metadata
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        .chart-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .info-item {{
            display: flex;
            align-items: center;
        }}
        .info-label {{
            font-weight: bold;
            color: #666;
            margin-right: 10px;
        }}
        .info-value {{
            color: #333;
        }}
        .mermaid {{
            background: white;
            padding: 30px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            min-height: 400px;
        }}
        .description {{
            margin: 20px 0;
            padding: 20px;
            background: #e8f4fd;
            border-left: 4px solid #4a90e2;
            border-radius: 5px;
        }}
        .insights {{
            margin: 20px 0;
            padding: 20px;
            background: #f0f8e8;
            border-left: 4px solid #52c41a;
            border-radius: 5px;
        }}
        .insights h3 {{
            margin-top: 0;
            color: #52c41a;
        }}
        .insights ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .insights li {{
            margin: 5px 0;
        }}
        .data-section {{
            margin-top: 30px;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        .data-table th, .data-table td {{
            border: 1px solid #e0e0e0;
            padding: 12px;
            text-align: left;
        }}
        .data-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
        }}
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .data-table tr:hover {{
            background: #e8f4fd;
        }}
        .code-section {{
            margin-top: 30px;
            padding: 20px;
            background: #2d2d2d;
            border-radius: 8px;
            color: #f8f8f2;
        }}
        .code-section h3 {{
            color: #f8f8f2;
            margin-top: 0;
        }}
        pre {{
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        code {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .badge-success {{
            background: #52c41a;
            color: white;
        }}
        .badge-info {{
            background: #1890ff;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title} <span class="badge badge-success">{chart_type}</span></h1>
        
        <div class="chart-info">
            <div class="info-item">
                <span class="info-label">Chart Type:</span>
                <span class="info-value">{chart_type}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Format:</span>
                <span class="info-value">{format}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Data Points:</span>
                <span class="info-value">{data_points}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Generated:</span>
                <span class="info-value">{timestamp}</span>
            </div>
        </div>
        
        {description_section}
        
        {chart_section}
        
        {insights_section}
        
        {data_section}
        
        {code_section}
    </div>
</body>
</html>"""
    
    # Prepare sections
    title = base_filename.replace('_', ' ').title()
    
    # Description section
    description_section = ""
    if result.get('description'):
        description_section = f"""
        <div class="description">
            <strong>Description:</strong> {result['description']}
        </div>"""
    
    # Chart section (for Mermaid)
    chart_section = ""
    if result['format'] == 'mermaid':
        chart_section = f"""
        <div class="mermaid">
{result['content']}
        </div>"""
    elif result['format'] == 'python_code':
        chart_section = """
        <div class="description" style="background: #fff3cd; border-left-color: #ffc107;">
            <strong>Note:</strong> This is a Python-generated chart. The code is provided below.
            To view the chart, run the Python code in a Jupyter notebook or Python environment.
        </div>"""
    
    # Insights section
    insights_section = ""
    if result.get('insights'):
        insights_list = '\n'.join([f"<li>{insight}</li>" for insight in result['insights']])
        insights_section = f"""
        <div class="insights">
            <h3>📊 Key Insights</h3>
            <ul>
                {insights_list}
            </ul>
        </div>"""
    
    # Data table section
    data_section = ""
    if result.get('data'):
        rows = '\n'.join([
            f"<tr><td>{item['label']}</td><td>{item['value']:.2f}</td></tr>"
            for item in result['data']
        ])
        data_section = f"""
        <div class="data-section">
            <h3>📈 Generated Data</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Label</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>"""
    
    # Code section (for Python code)
    code_section = ""
    if result['format'] == 'python_code':
        code_section = f"""
        <div class="code-section">
            <h3>🐍 Python Code</h3>
            <pre><code>{result['content']}</code></pre>
        </div>"""
    
    # Fill in the template
    html_output = html_content.format(
        title=title,
        chart_type=result['chart_type'],
        format=result['format'],
        data_points=len(result.get('data', [])),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description_section=description_section,
        chart_section=chart_section,
        insights_section=insights_section,
        data_section=data_section,
        code_section=code_section
    )
    
    # Save HTML file
    html_file = os.path.join(output_dir, f"{base_filename}.html")
    with open(html_file, 'w') as f:
        f.write(html_output)
    
    # Save raw JSON data
    json_file = os.path.join(output_dir, f"{base_filename}.json")
    with open(json_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # If Python code, also save as .py file
    if result['format'] == 'python_code':
        py_file = os.path.join(output_dir, f"{base_filename}.py")
        with open(py_file, 'w') as f:
            f.write(result['content'])
    
    return html_file


async def generate_all_charts():
    """Generate a comprehensive set of charts for viewing."""
    
    # Create output directory
    output_dir = "test_output/analytics_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📁 Saving charts to: {output_dir}/")
    print("="*60)
    
    charts_to_generate = [
        {
            "name": "quarterly_sales_bar",
            "content": "Show quarterly sales for 2024: Q1=$1.2M, Q2=$1.5M, Q3=$1.3M, Q4=$1.8M",
            "title": "2024 Quarterly Sales Performance",
            "chart_type": "bar"
        },
        {
            "name": "monthly_revenue_trend",
            "content": "Display monthly revenue trend for 12 months showing steady growth from $100k in January to $250k in December with some fluctuation",
            "title": "Monthly Revenue Growth Trend",
            "chart_type": "line"
        },
        {
            "name": "market_share_pie",
            "content": "Market share distribution: TechCorp 35%, DataSoft 28%, CloudNet 22%, StartupXYZ 10%, Others 5%",
            "title": "Market Share Distribution 2024",
            "chart_type": "pie"
        },
        {
            "name": "product_category_performance",
            "content": "Compare performance across product categories: Electronics $2.5M, Clothing $1.8M, Home & Garden $1.2M, Sports $900k, Books $600k",
            "title": "Product Category Performance",
            "chart_type": "bar"
        },
        {
            "name": "seasonal_ice_cream_sales",
            "content": "Ice cream sales by month showing clear seasonality: Jan $20k, Feb $25k, Mar $35k, Apr $50k, May $75k, Jun $120k, Jul $150k, Aug $140k, Sep $90k, Oct $60k, Nov $30k, Dec $25k",
            "title": "Ice Cream Sales - Seasonal Pattern",
            "chart_type": "line"
        },
        {
            "name": "skills_assessment_radar",
            "content": "Team skills assessment: Communication 85%, Technical Skills 75%, Leadership 90%, Problem Solving 80%, Creativity 70%, Time Management 65%",
            "title": "Team Skills Assessment",
            "chart_type": "radar"
        },
        {
            "name": "customer_satisfaction_scores",
            "content": "Customer satisfaction scores by region: North America 4.5/5, Europe 4.3/5, Asia 4.6/5, South America 4.1/5, Africa 4.2/5, Australia 4.4/5",
            "title": "Global Customer Satisfaction",
            "chart_type": "bar"
        },
        {
            "name": "website_traffic_growth",
            "content": "Website traffic growth over 6 months with upward trend: Month 1: 10k visits, Month 2: 12k, Month 3: 18k, Month 4: 25k, Month 5: 32k, Month 6: 45k visits",
            "title": "Website Traffic Growth",
            "chart_type": "line"
        },
        {
            "name": "expense_breakdown_pie",
            "content": "Company expense breakdown: Salaries 45%, Marketing 20%, Operations 15%, R&D 12%, Admin 5%, Other 3%",
            "title": "Expense Distribution",
            "chart_type": "pie"
        },
        {
            "name": "sales_with_outliers",
            "content": "Monthly sales with outliers: Jan $100k, Feb $95k, Mar $105k, Apr $98k, May $102k, Jun $350k (summer sale), Jul $110k, Aug $108k, Sep $95k, Oct $103k, Nov $98k, Dec $420k (holiday spike)",
            "title": "Sales with Seasonal Spikes",
            "chart_type": "line"
        }
    ]
    
    generated_files = []
    
    for i, chart_config in enumerate(charts_to_generate, 1):
        print(f"\n[{i}/{len(charts_to_generate)}] Generating: {chart_config['name']}")
        print("-"*40)
        
        try:
            # Generate the chart
            result = await create_analytics(
                chart_config['content'],
                title=chart_config['title'],
                chart_type=chart_config.get('chart_type')
            )
            
            if result['success']:
                # Save the chart with all metadata
                html_file = await save_chart_with_metadata(
                    result,
                    chart_config['name'],
                    output_dir
                )
                generated_files.append(html_file)
                print(f"✅ Saved: {chart_config['name']}.html")
                print(f"   Type: {result['chart_type']}")
                print(f"   Format: {result['format']}")
                print(f"   Data Points: {len(result.get('data', []))}")
                if result.get('insights'):
                    print(f"   Insights: {len(result['insights'])}")
            else:
                print(f"❌ Failed to generate {chart_config['name']}")
                
        except Exception as e:
            print(f"❌ Error generating {chart_config['name']}: {e}")
    
    # Create index file
    print("\n" + "="*60)
    print("Creating index file...")
    
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Charts Gallery</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .chart-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
            text-decoration: none;
            color: #333;
        }
        .chart-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            border-color: #667eea;
        }
        .chart-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #667eea;
        }
        .chart-type {
            display: inline-block;
            padding: 4px 8px;
            background: #e8f4fd;
            border-radius: 4px;
            font-size: 12px;
            color: #1890ff;
            margin-bottom: 10px;
        }
        .chart-description {
            font-size: 14px;
            color: #666;
            line-height: 1.5;
        }
        .timestamp {
            text-align: center;
            color: #999;
            margin-top: 30px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Analytics Charts Gallery</h1>
        <p>Generated analytics visualizations using the Analytics Agent system.</p>
        <p>Click on any chart to view the full interactive version with data and insights.</p>
        
        <div class="chart-grid">
"""
    
    for chart_config in charts_to_generate:
        chart_file = f"{chart_config['name']}.html"
        index_html += f"""
            <a href="{chart_file}" class="chart-card">
                <div class="chart-title">{chart_config['title']}</div>
                <div class="chart-type">{chart_config.get('chart_type', 'auto').upper()}</div>
                <div class="chart-description">{chart_config['content'][:100]}...</div>
            </a>
"""
    
    index_html += f"""
        </div>
        <div class="timestamp">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    </div>
</body>
</html>"""
    
    index_file = os.path.join(output_dir, "index.html")
    with open(index_file, 'w') as f:
        f.write(index_html)
    
    print(f"✅ Index created: {index_file}")
    
    print("\n" + "="*60)
    print("✨ CHART GENERATION COMPLETE!")
    print(f"📁 All charts saved to: {output_dir}/")
    print(f"🌐 Open {output_dir}/index.html in your browser to view all charts")
    print("="*60)
    
    return output_dir


async def main():
    """Run the chart generation."""
    print("\n🚀 Starting Analytics Chart Generation...")
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: No API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env file")
        return
    
    output_dir = await generate_all_charts()
    
    # Try to open in browser (macOS)
    try:
        import subprocess
        index_path = os.path.join(output_dir, "index.html")
        subprocess.run(["open", index_path])
        print("\n🌐 Opening charts in your default browser...")
    except:
        print("\n📂 Please manually open the index.html file in your browser")


if __name__ == "__main__":
    asyncio.run(main())