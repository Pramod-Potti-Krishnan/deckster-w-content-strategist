"""
Test Chart Generation with MCP
===============================

This script tests chart generation using MCP execution.
It creates a custom MCP wrapper to use the mcp__ide__executeCode tool.
"""

import os
import asyncio
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.agents.analytics_agent import AnalyticsAgent
from src.agents.analytics_utils.models import AnalyticsRequest, ChartType
from src.agents.analytics_utils.mcp_executor_simplified import SimplifiedMCPExecutor


# Create MCP wrapper for our environment
class MCPToolWrapper:
    """Wrapper to provide MCP execution capability."""
    
    def __init__(self):
        self.execution_count = 0
        
    async def execute_code(self, code: str):
        """
        Execute Python code via MCP.
        
        This method will be replaced with actual MCP execution
        when run in the Claude Code environment.
        """
        self.execution_count += 1
        logger.info(f"MCP execution #{self.execution_count}")
        
        # This is where mcp__ide__executeCode would be called
        # For now, return a placeholder
        return {
            "output": "MCP execution placeholder",
            "note": "Replace this with actual mcp__ide__executeCode call"
        }


# Test cases
TEST_CHARTS = [
    {
        "id": "01_line",
        "title": "Revenue Trend Analysis",
        "description": "Monthly revenue trend over 12 months showing growth pattern",
        "data_context": "Financial performance data with seasonal variations",
        "time_period": "12 months"
    },
    {
        "id": "02_bar",
        "title": "Product Category Sales",
        "description": "Sales comparison across 6 product categories",
        "data_context": "E-commerce sales data by category",
    },
    {
        "id": "03_pie",
        "title": "Market Share Breakdown",
        "description": "Market share distribution among top 5 competitors",
        "data_context": "Competitive analysis showing percentage shares",
    },
    {
        "id": "04_scatter",
        "title": "Customer Satisfaction vs Revenue",
        "description": "Correlation between customer satisfaction scores and revenue",
        "data_context": "Customer metrics and financial data",
    },
    {
        "id": "05_heatmap",
        "title": "Performance Metrics Correlation",
        "description": "Correlation matrix of 5 key business metrics",
        "data_context": "KPI correlation analysis",
    }
]


async def test_with_mcp_tool(mcp_tool):
    """
    Test chart generation with MCP tool.
    
    Args:
        mcp_tool: The MCP execution tool function
    """
    print("="*60)
    print("🚀 Testing Chart Generation with MCP")
    print("="*60)
    
    # Create output directory
    output_dir = Path("mcp_test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize agent with MCP tool
    agent = AnalyticsAgent(mcp_tool=mcp_tool)
    print(f"✅ Agent initialized with MCP tool: {mcp_tool is not None}")
    
    # Check MCP availability
    if agent.python_agent.mcp_integration.is_available:
        print("✅ MCP integration is available")
    else:
        print("⚠️  MCP integration not available - will return Python code")
    
    results = []
    
    for i, test_case in enumerate(TEST_CHARTS):
        print(f"\n[{i+1}/{len(TEST_CHARTS)}] Testing: {test_case['title']}")
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
            if success:
                if result.format == "mermaid":
                    file_path = output_dir / f"{test_case['id']}.mmd"
                    content = result.output if hasattr(result, 'output') else result.chart_content
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(f"Saved: {file_path.name}")
                    
                elif result.format in ["png", "base64"]:
                    file_path = output_dir / f"{test_case['id']}.png"
                    content = result.output if hasattr(result, 'output') else result.chart_content
                    
                    if content.startswith("data:image/png;base64,"):
                        content = content.split(",")[1]
                    
                    with open(file_path, 'wb') as f:
                        f.write(base64.b64decode(content))
                    print(f"Saved: {file_path.name}")
                    
                elif result.format == "python_code":
                    print("⚠️  Got Python code (MCP not executing)")
                    file_path = output_dir / f"{test_case['id']}.py"
                    content = result.output if hasattr(result, 'output') else result.chart_content
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(f"Saved Python code: {file_path.name}")
            
            results.append({
                "id": test_case["id"],
                "title": test_case["title"],
                "success": success,
                "format": result.format,
                "chart_type": str(result.chart_type)
            })
            
        except Exception as e:
            print(f"❌ Exception: {str(e)[:100]}")
            results.append({
                "id": test_case["id"],
                "title": test_case["title"],
                "success": False,
                "format": "error",
                "chart_type": "error"
            })
        
        # Delay to avoid rate limits
        if i < len(TEST_CHARTS) - 1:
            print("⏳ Waiting 5 seconds...")
            await asyncio.sleep(5)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r["success"]]
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    
    # Check formats
    formats = {}
    for r in results:
        fmt = r["format"]
        if fmt not in formats:
            formats[fmt] = 0
        formats[fmt] += 1
    
    print("\nFormats generated:")
    for fmt, count in formats.items():
        print(f"  {fmt}: {count}")
    
    # Check if MCP was actually used
    mcp_used = any(r["format"] in ["png", "base64"] for r in results if r["success"])
    if mcp_used:
        print("\n✅ MCP execution successful - PNG images generated!")
    else:
        print("\n⚠️  MCP not executing - only code/mermaid generated")
    
    # Save results
    results_file = output_dir / "results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "mcp_available": agent.python_agent.mcp_integration.is_available,
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len(successful),
                "formats": formats,
                "mcp_used": mcp_used
            }
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")


async def main():
    """Main test function."""
    
    # Try to create MCP tool wrapper
    # In the actual Claude Code environment, we would use mcp__ide__executeCode
    mcp_wrapper = MCPToolWrapper()
    
    # Create async wrapper for MCP execution
    async def mcp_tool(code: str):
        """MCP tool function for analytics."""
        return await mcp_wrapper.execute_code(code)
    
    # Run test with MCP tool
    await test_with_mcp_tool(mcp_tool)
    
    print("\n" + "="*60)
    print("ℹ️  NOTE: To use actual MCP execution:")
    print("  Replace MCPToolWrapper.execute_code with mcp__ide__executeCode")
    print("  This must be run in Claude Code environment with MCP tools")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())