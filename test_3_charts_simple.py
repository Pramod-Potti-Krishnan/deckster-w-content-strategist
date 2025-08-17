#!/usr/bin/env python3
"""
Simple test for 3 chart types to verify the system is working.
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


async def test_three_charts():
    """Test 3 different chart types."""
    
    print("=" * 60)
    print("TESTING 3 CHART TYPES")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path("test_3_charts_output")
    output_dir.mkdir(exist_ok=True)
    
    # Define 3 test cases
    test_cases = [
        {
            "chart_type": ChartType.BAR_VERTICAL,
            "content": "Compare sales across 5 regions",
            "title": "Regional Sales"
        },
        {
            "chart_type": ChartType.LINE_CHART,
            "content": "Show monthly revenue trend",
            "title": "Revenue Trend"
        },
        {
            "chart_type": ChartType.PIE_CHART,
            "content": "Market share distribution",
            "title": "Market Share"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/3] Testing {test_case['chart_type'].value}...")
        
        try:
            response = await create_analytics_v2(
                content=test_case["content"],
                title=test_case["title"],
                chart_type=test_case["chart_type"].value,
                use_synthetic_data=True,
                save_files=True,
                output_dir=str(output_dir)
            )
            
            if response.get("success"):
                print(f"  ✓ Success!")
                # Check for files
                png_file = output_dir / f"{test_case['chart_type'].value}_{i}.png"
                if png_file.exists():
                    print(f"  PNG: {png_file.stat().st_size:,} bytes")
            else:
                print(f"  ✗ Failed: {response.get('error')}")
            
            results.append(response)
            
            # Wait 7 seconds between calls
            if i < 3:
                print("  Waiting 7 seconds...")
                await asyncio.sleep(7)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({"success": False, "error": str(e)})
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    # Save results
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    asyncio.run(test_three_charts())