"""
Test Two-Step Chart Generation System
======================================

Step 1: Generate chart code using analytics system
Step 2: Execute code to create PNG images
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

from src.agents.analytics_agent import AnalyticsAgent
from src.agents.analytics_utils.models import AnalyticsRequest, ChartType

# Test cases for various chart types
CHART_TESTS = [
    {
        "id": "01_bar",
        "title": "Product Sales Comparison",
        "description": "Compare sales across 8 product categories",
        "data_context": "E-commerce sales data by product category"
    },
    {
        "id": "02_pie", 
        "title": "Market Share Distribution",
        "description": "Show market share percentages for top 5 companies",
        "data_context": "Market share data showing percentage distribution"
    },
    {
        "id": "03_line",
        "title": "Monthly Revenue Trend",
        "description": "Revenue trend over 12 months",
        "data_context": "Monthly revenue data showing growth pattern",
        "time_period": "12 months"
    },
    {
        "id": "04_scatter",
        "title": "Price vs Quality Correlation",
        "description": "Analyze correlation between price and quality scores",
        "data_context": "Product pricing and quality rating data"
    },
    {
        "id": "05_histogram",
        "title": "Customer Age Distribution",
        "description": "Distribution of customer ages",
        "data_context": "Customer demographic data"
    },
    {
        "id": "06_area",
        "title": "Cumulative Sales Growth",
        "description": "Cumulative sales growth over quarters",
        "data_context": "Quarterly sales data",
        "time_period": "8 quarters"
    },
    {
        "id": "07_radar",
        "title": "Product Feature Comparison",
        "description": "Compare products across 6 feature dimensions",
        "data_context": "Product features: Quality, Price, Design, Support, Innovation, Reliability"
    },
    {
        "id": "08_bubble",
        "title": "Market Opportunity Analysis",
        "description": "Market opportunities by size, growth, and profitability",
        "data_context": "Strategic market analysis data"
    }
]


async def generate_chart_code(agent, test_case, output_dir):
    """Generate chart code for a test case."""
    try:
        print(f"Generating: {test_case['id']} - {test_case['title']}")
        
        # Create request
        request = AnalyticsRequest(
            title=test_case["title"],
            description=test_case["description"],
            data_context=test_case["data_context"],
            time_period=test_case.get("time_period")
        )
        
        # Generate chart
        result = await agent.generate_analytics(request)
        
        # Save based on format
        if result.format == "mermaid":
            file_path = output_dir / f"{test_case['id']}.mmd"
            content = result.output if hasattr(result, 'output') else result.chart_content
            with open(file_path, 'w') as f:
                f.write(f"# {test_case['title']}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(content)
            print(f"  ✅ Saved Mermaid: {file_path.name}")
            return "mermaid", file_path
            
        elif result.format in ["python_code", "base64"]:
            file_path = output_dir / f"{test_case['id']}.py"
            
            # Get the code
            if result.format == "python_code":
                content = result.output if hasattr(result, 'output') else result.chart_content
            else:
                # If we got base64, still save the Python code if available
                content = result.python_code if hasattr(result, 'python_code') else str(result.chart_content)[:100] + "..."
            
            with open(file_path, 'w') as f:
                f.write(f"# {test_case['title']}\n")
                f.write(f"# Chart Type: {result.chart_type}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(content)
            print(f"  ✅ Saved Python: {file_path.name}")
            return "python", file_path
            
        else:
            print(f"  ❌ Error format: {result.format}")
            return "error", None
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:100]}")
        return "error", None


async def step1_generate_code():
    """Step 1: Generate chart code."""
    print("="*60)
    print("STEP 1: GENERATING CHART CODE")
    print("="*60)
    
    # Create output directory
    output_dir = Path("two_step_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize agent
    agent = AnalyticsAgent()
    print("✅ Analytics Agent initialized\n")
    
    results = []
    for test_case in CHART_TESTS:
        format_type, file_path = await generate_chart_code(agent, test_case, output_dir)
        results.append({
            "id": test_case["id"],
            "title": test_case["title"],
            "format": format_type,
            "file": str(file_path) if file_path else None
        })
        
        # Small delay to avoid rate limits
        await asyncio.sleep(3)
    
    # Save results
    results_file = output_dir / "generation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    successful = [r for r in results if r["format"] != "error"]
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"📁 Files saved to: {output_dir}/")
    
    return output_dir, results


if __name__ == "__main__":
    # Run Step 1
    output_dir, results = asyncio.run(step1_generate_code())
    
    print("\n" + "="*60)
    print("STEP 1 COMPLETE")
    print("="*60)
    print(f"Generated {len([r for r in results if r['format'] != 'error'])} chart code files")
    print(f"\nNext step: Run the execution script to convert to PNG")
    print(f"You can use: python generate_chart_pngs.py")
    print(f"Or run: python execute_two_step_charts.py")