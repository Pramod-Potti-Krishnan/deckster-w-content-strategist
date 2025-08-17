"""
Quick Test of 5 Key Chart Types
================================

Tests a sample of important chart types to verify the system works.
"""

import os
import asyncio
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

from src.agents.analytics_agent import AnalyticsAgent
from src.agents.analytics_utils.models import AnalyticsRequest, ChartType

# Test 5 key chart types
SAMPLE_CHARTS = [
    {
        "id": "01_line",
        "title": "Monthly Revenue Trend",
        "description": "Show monthly revenue trend over the last 12 months",
        "data_context": "Business revenue data with seasonal patterns",
        "time_period": "12 months",
        "expected": "line"
    },
    {
        "id": "02_bar",
        "title": "Product Sales Comparison",
        "description": "Compare sales across 6 product categories",
        "data_context": "Product categories: Electronics, Clothing, Food, Home, Sports, Books",
        "expected": "bar"
    },
    {
        "id": "03_pie",
        "title": "Market Share Distribution",
        "description": "Show market share percentages for top 5 companies",
        "data_context": "Market share data showing percentage distribution",
        "expected": "pie"
    },
    {
        "id": "04_scatter",
        "title": "Price vs Quality Analysis",
        "description": "Analyze correlation between price and quality scores",
        "data_context": "Product pricing and quality rating data",
        "expected": "scatter"
    },
    {
        "id": "05_heatmap",
        "title": "Feature Correlation Matrix",
        "description": "Show correlation between 5 business metrics",
        "data_context": "Business KPIs: Revenue, Cost, Margin, Volume, Satisfaction",
        "expected": "heatmap"
    }
]

async def test_chart(agent, chart_spec, output_dir):
    """Test a single chart."""
    try:
        print(f"\n{'='*50}")
        print(f"Testing: {chart_spec['id']} - {chart_spec['title']}")
        
        # Create request
        request = AnalyticsRequest(
            title=chart_spec["title"],
            description=chart_spec["description"],
            data_context=chart_spec["data_context"],
            time_period=chart_spec.get("time_period")
        )
        
        # Generate chart
        result = await agent.generate_analytics(request)
        
        # Check success
        success = result.format != "error"
        
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"Chart Type: {result.chart_type}")
        print(f"Format: {result.format}")
        
        # Save output
        if success:
            if result.format == "mermaid":
                # Save Mermaid code
                file_path = output_dir / f"{chart_spec['id']}.mmd"
                content = result.output if hasattr(result, 'output') else result.chart_content
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"Saved: {file_path.name}")
                
            elif result.format in ["png", "base64"]:
                # Save PNG image
                file_path = output_dir / f"{chart_spec['id']}.png"
                content = result.output if hasattr(result, 'output') else result.chart_content
                
                # Handle base64 prefix
                if content.startswith("data:image/png;base64,"):
                    content = content.split(",")[1]
                
                with open(file_path, 'wb') as f:
                    f.write(base64.b64decode(content))
                print(f"Saved: {file_path.name}")
        else:
            error_msg = result.error_message if hasattr(result, 'error_message') else "Unknown error"
            print(f"Error: {error_msg[:100]}")
        
        return {
            "id": chart_spec["id"],
            "title": chart_spec["title"],
            "success": success,
            "chart_type": str(result.chart_type),
            "format": result.format
        }
        
    except Exception as e:
        print(f"Status: ❌ EXCEPTION")
        print(f"Error: {str(e)[:100]}")
        return {
            "id": chart_spec["id"],
            "title": chart_spec["title"],
            "success": False,
            "chart_type": "error",
            "format": "error"
        }

async def main():
    """Run sample test."""
    print("🚀 Testing 5 Sample Charts")
    print("="*50)
    
    # Create output directory
    output_dir = Path("sample_charts_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize agent with MCP tool if available
    try:
        # Try to get MCP tool from the environment
        from mcp__ide__executeCode import mcp__ide__executeCode
        agent = AnalyticsAgent(mcp_tool=mcp__ide__executeCode)
        print("✅ Agent initialized with MCP support\n")
    except ImportError:
        # Fallback without MCP
        agent = AnalyticsAgent()
        print("✅ Agent initialized (no MCP)\n")
    
    # Test charts with delay
    results = []
    for i, chart in enumerate(SAMPLE_CHARTS):
        print(f"\n[{i+1}/5] Processing {chart['expected']} chart...")
        result = await test_chart(agent, chart, output_dir)
        results.append(result)
        
        # Wait to avoid rate limit
        if i < len(SAMPLE_CHARTS) - 1:
            print("⏳ Waiting 7 seconds...")
            await asyncio.sleep(7)
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    successful = [r for r in results if r["success"]]
    print(f"✅ Successful: {len(successful)}/5")
    print(f"📈 Success Rate: {len(successful)/5*100:.0f}%")
    
    # Show results
    print("\nResults:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['id']}: {r['chart_type']} ({r['format']})")
    
    # Create simple HTML gallery
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Sample Charts Test</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }}
        .chart {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        img {{ max-width: 100%; height: auto; }}
        .success {{ color: green; }}
        .failed {{ color: red; }}
    </style>
</head>
<body>
    <h1>Sample Charts Test Results</h1>
    <p>Success Rate: {len(successful)/5*100:.0f}% ({len(successful)}/5)</p>
    <div class="gallery">
"""
    
    for r in results:
        status_class = "success" if r["success"] else "failed"
        html += f"""
        <div class="chart">
            <h3 class="{status_class}">{r['id']}: {r['title']}</h3>
            <p>Type: {r['chart_type']} | Format: {r['format']}</p>
"""
        if r["success"]:
            if r["format"] in ["png", "base64"]:
                html += f'<img src="{r["id"]}.png" alt="{r["title"]}">'
            elif r["format"] == "mermaid":
                html += f'<p>Mermaid chart saved as {r["id"]}.mmd</p>'
        else:
            html += '<p>Chart generation failed</p>'
        html += '</div>'
    
    html += """
    </div>
</body>
</html>"""
    
    gallery_path = output_dir / "gallery.html"
    with open(gallery_path, 'w') as f:
        f.write(html)
    
    print(f"\n📸 Gallery saved to: {gallery_path}")
    print(f"📁 All files saved to: {output_dir}/")

if __name__ == "__main__":
    asyncio.run(main())