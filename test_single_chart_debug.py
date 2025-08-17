#!/usr/bin/env python3
"""
Test a single chart with debugging.
"""

import asyncio
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()
print("✓ Dotenv loaded")

# Add timeout wrapper
async def with_timeout(coro, timeout_seconds=30):
    """Run coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        print(f"✗ Operation timed out after {timeout_seconds} seconds")
        return None

async def test_single_chart():
    """Test a single chart generation."""
    
    print("\nImporting analytics_agent_v2...")
    from src.agents.analytics_agent_v2 import create_analytics_v2
    print("✓ Imported")
    
    print("\nCreating output directory...")
    output_dir = Path("test_single_output")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Created: {output_dir}")
    
    print("\nCalling create_analytics_v2...")
    print("  Parameters:")
    print("    content: 'Sales comparison across regions'")
    print("    title: 'Regional Sales'")
    print("    chart_type: 'bar_chart_vertical'")
    print("    use_synthetic_data: True")
    print("    save_files: True")
    print("    output_dir: test_single_output")
    
    try:
        # Call with timeout
        response = await with_timeout(
            create_analytics_v2(
                content="Sales comparison across regions",
                title="Regional Sales",
                chart_type="bar_chart_vertical",
                use_synthetic_data=True,
                save_files=True,
                output_dir=str(output_dir)
            ),
            timeout_seconds=30
        )
        
        if response is None:
            print("✗ Response is None (timed out)")
            return
        
        print("\n✓ Got response!")
        print(f"  Success: {response.get('success')}")
        
        if response.get('success'):
            # Check for files
            png_files = list(output_dir.glob("*.png"))
            json_files = list(output_dir.glob("*.json"))
            
            print(f"  PNG files: {len(png_files)}")
            for f in png_files:
                print(f"    - {f.name}: {f.stat().st_size:,} bytes")
            
            print(f"  JSON files: {len(json_files)}")
            for f in json_files:
                print(f"    - {f.name}")
        else:
            print(f"  Error: {response.get('error')}")
        
        return response
        
    except Exception as e:
        print(f"\n✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("SINGLE CHART DEBUG TEST")
    print("=" * 60)
    
    result = asyncio.run(test_single_chart())
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)