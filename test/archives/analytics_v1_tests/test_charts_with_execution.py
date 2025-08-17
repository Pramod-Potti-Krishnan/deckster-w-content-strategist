"""
Test Chart Generation with Direct Execution
============================================

Since MCP requires Jupyter notebook context, this script tests
chart generation using direct Python execution as a proxy for MCP.
This validates that our chart generation code works correctly.
"""

import os
import sys
import asyncio
import base64
import io
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json
import logging
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.agents.analytics_agent import AnalyticsAgent
from src.agents.analytics_utils.models import AnalyticsRequest, ChartType
from src.agents.analytics_utils.python_chart_agent import PythonChartAgent
from src.agents.analytics_utils.mcp_executor_simplified import SimplifiedMCPExecutor


class DirectExecutionMCPSimulator:
    """
    Simulates MCP execution by directly executing Python code.
    This is used for testing when MCP (Jupyter) is not available.
    """
    
    def __init__(self):
        self.execution_count = 0
        logger.info("Direct Execution MCP Simulator initialized")
    
    async def __call__(self, code: str):
        """
        Execute Python code and return result mimicking MCP response.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict with execution result
        """
        self.execution_count += 1
        logger.info(f"Executing chart code (execution #{self.execution_count})")
        
        try:
            # Create execution namespace
            namespace = {
                'plt': plt,
                'np': np,
                'matplotlib': matplotlib,
                'pi': np.pi
            }
            
            # Execute the code
            exec(code, namespace)
            
            # Check if BASE64 markers are in output
            # (Our wrapped code prints BASE64_START/END markers)
            import sys
            from io import StringIO
            
            # Capture output by re-executing with output capture
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                exec(code, namespace)
                output = captured_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            # Extract base64 if present
            if "BASE64_START" in output and "BASE64_END" in output:
                import re
                match = re.search(r'BASE64_START\s*\n?(.*?)\n?BASE64_END', output, re.DOTALL)
                if match:
                    base64_str = match.group(1).strip()
                    logger.info("Successfully extracted base64 image from execution")
                    return {"output": output}  # Return full output for extraction
            
            # If no BASE64 markers but figure exists, generate base64
            if plt.get_fignums():
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                buffer.close()
                plt.close('all')
                
                # Create output with markers
                output = f"BASE64_START\n{img_base64}\nBASE64_END"
                logger.info("Generated base64 image from matplotlib figure")
                return {"output": output}
            
            logger.warning("No figure generated from code execution")
            return {"output": "No figure generated"}
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {"error": str(e)}


# Test cases focusing on charts that should work
WORKING_CHARTS = [
    {
        "id": "01_bar",
        "title": "Monthly Sales Performance",
        "description": "Bar chart showing sales for each month",
        "data_context": "Monthly sales data for 6 months",
    },
    {
        "id": "02_pie",
        "title": "Product Category Distribution",
        "description": "Pie chart showing percentage distribution across 5 product categories",
        "data_context": "E-commerce product category sales percentages",
    },
    {
        "id": "03_line",
        "title": "Revenue Growth Trend",
        "description": "Line chart showing revenue growth over 8 quarters",
        "data_context": "Quarterly revenue data showing upward trend",
        "time_period": "8 quarters"
    },
    {
        "id": "04_scatter",
        "title": "Price vs Demand Analysis",
        "description": "Scatter plot showing relationship between price and demand",
        "data_context": "Product pricing and sales volume data",
    },
    {
        "id": "05_histogram",
        "title": "Age Distribution",
        "description": "Histogram showing customer age distribution with mean 35",
        "data_context": "Customer demographic data for 500 customers",
    }
]


async def test_charts_with_simulator():
    """Test chart generation with direct execution simulator."""
    
    print("="*60)
    print("🚀 Testing Chart Generation with Execution Simulator")
    print("="*60)
    print("ℹ️  Using direct Python execution to simulate MCP")
    print("   (MCP requires Jupyter notebook context)")
    print("="*60)
    
    # Create output directory
    output_dir = Path("execution_test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create MCP simulator
    mcp_simulator = DirectExecutionMCPSimulator()
    
    # Initialize agent with simulator
    agent = AnalyticsAgent(mcp_tool=mcp_simulator)
    print(f"✅ Agent initialized with execution simulator\n")
    
    results = []
    successful_pngs = []
    
    for i, test_case in enumerate(WORKING_CHARTS):
        print(f"\n[{i+1}/{len(WORKING_CHARTS)}] Testing: {test_case['title']}")
        print("-" * 40)
        
        try:
            # Create request
            request = AnalyticsRequest(
                title=test_case["title"],
                description=test_case["description"],
                data_context=test_case["data_context"],
                time_period=test_case.get("time_period")
            )
            
            # Generate chart
            result = await agent.generate_analytics(request)
            
            # Check result
            success = result.format != "error"
            print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
            print(f"Chart Type: {result.chart_type}")
            print(f"Format: {result.format}")
            
            # Save output
            saved_file = None
            if success:
                content = result.output if hasattr(result, 'output') else result.chart_content
                
                if result.format == "mermaid":
                    # Save Mermaid code
                    file_path = output_dir / f"{test_case['id']}.mmd"
                    with open(file_path, 'w') as f:
                        f.write(content)
                    saved_file = file_path.name
                    print(f"Saved Mermaid: {file_path.name}")
                    
                elif result.format in ["png", "base64"]:
                    # Save PNG image
                    file_path = output_dir / f"{test_case['id']}.png"
                    
                    if content.startswith("data:image/png;base64,"):
                        content = content.split(",")[1]
                    
                    with open(file_path, 'wb') as f:
                        f.write(base64.b64decode(content))
                    saved_file = file_path.name
                    successful_pngs.append(file_path.name)
                    print(f"✅ Saved PNG: {file_path.name}")
                    
                elif result.format == "python_code":
                    # Try to execute the code directly
                    print("⚠️  Got Python code, attempting direct execution...")
                    
                    # Execute the code to generate image
                    exec_result = await mcp_simulator(content)
                    
                    if "BASE64_START" in str(exec_result.get("output", "")):
                        # Extract and save base64
                        import re
                        output = exec_result["output"]
                        match = re.search(r'BASE64_START\s*\n?(.*?)\n?BASE64_END', output, re.DOTALL)
                        if match:
                            base64_str = match.group(1).strip()
                            file_path = output_dir / f"{test_case['id']}.png"
                            with open(file_path, 'wb') as f:
                                f.write(base64.b64decode(base64_str))
                            saved_file = file_path.name
                            successful_pngs.append(file_path.name)
                            print(f"✅ Executed and saved PNG: {file_path.name}")
                    else:
                        # Save the Python code
                        file_path = output_dir / f"{test_case['id']}.py"
                        with open(file_path, 'w') as f:
                            f.write(content)
                        saved_file = file_path.name
                        print(f"Saved Python code: {file_path.name}")
            
            results.append({
                "id": test_case["id"],
                "title": test_case["title"],
                "success": success,
                "format": result.format,
                "chart_type": str(result.chart_type),
                "saved_file": saved_file
            })
            
        except Exception as e:
            print(f"❌ Exception: {str(e)[:200]}")
            results.append({
                "id": test_case["id"],
                "title": test_case["title"],
                "success": False,
                "format": "error",
                "chart_type": "error",
                "saved_file": None,
                "error": str(e)[:500]
            })
        
        # Small delay
        if i < len(WORKING_CHARTS) - 1:
            await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r["success"]]
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"📈 Success Rate: {len(successful)/len(results)*100:.0f}%")
    
    if successful_pngs:
        print(f"\n✅ Successfully generated {len(successful_pngs)} PNG images:")
        for png in successful_pngs:
            print(f"   - {png}")
    
    # Create HTML gallery
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Chart Execution Test Results</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .stats { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }
        .chart { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        img { max-width: 100%; height: auto; border: 1px solid #ddd; }
        .success { color: green; }
        .failed { color: red; }
    </style>
</head>
<body>
    <h1>Chart Generation Test with Execution</h1>
    <div class="stats">
        <h2>Statistics</h2>
        <p>Success Rate: """ + f"{len(successful)/len(results)*100:.0f}%" + """ (""" + f"{len(successful)}/{len(results)}" + """)</p>
        <p>PNG Images Generated: """ + str(len(successful_pngs)) + """</p>
        <p>Execution Count: """ + str(mcp_simulator.execution_count) + """</p>
    </div>
    <div class="gallery">
"""
    
    for r in results:
        status_class = "success" if r["success"] else "failed"
        html += f"""
        <div class="chart">
            <h3 class="{status_class}">{r['id']}: {r['title']}</h3>
            <p>Type: {r['chart_type']} | Format: {r['format']}</p>
"""
        if r["saved_file"]:
            if r["saved_file"].endswith('.png'):
                html += f'<img src="{r["saved_file"]}" alt="{r["title"]}">'
            elif r["saved_file"].endswith('.mmd'):
                html += f'<p>Mermaid chart: {r["saved_file"]}</p>'
            else:
                html += f'<p>Saved as: {r["saved_file"]}</p>'
        else:
            html += '<p>No output generated</p>'
        html += '</div>'
    
    html += """
    </div>
</body>
</html>"""
    
    gallery_path = output_dir / "gallery.html"
    with open(gallery_path, 'w') as f:
        f.write(html)
    
    print(f"\n📸 Gallery saved to: {gallery_path}")
    
    # Save results JSON
    results_file = output_dir / "results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "execution_count": mcp_simulator.execution_count,
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len(successful),
                "success_rate": len(successful)/len(results),
                "png_count": len(successful_pngs)
            }
        }, f, indent=2)
    
    print(f"📄 Results saved to: {results_file}")
    print(f"\n✅ Test complete! Check {output_dir}/ for all outputs.")


if __name__ == "__main__":
    asyncio.run(test_charts_with_simulator())