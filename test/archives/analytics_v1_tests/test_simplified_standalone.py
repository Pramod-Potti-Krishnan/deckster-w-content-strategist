#!/usr/bin/env python
"""
Test Simplified MCP Standalone (No Fallback)
============================================

This test verifies that the simplified MCP implementation works
completely on its own without any dependency on the archived files.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup paths and environment
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics


async def test_standalone():
    """Test the simplified MCP implementation standalone."""
    
    print("\n" + "="*70)
    print("TESTING SIMPLIFIED MCP EXECUTOR (NO FALLBACK)")
    print("="*70)
    
    # Test 1: Simple bar chart
    print("\nTest 1: Generating Bar Chart...")
    try:
        result = await create_analytics(
            content="Show sales data: Product A $100K, Product B $150K, Product C $120K",
            title="Product Sales",
            chart_type="bar"
        )
        
        print(f"  Success: {result['success']}")
        print(f"  Format: {result['format']}")
        print(f"  Chart Type: {result['chart_type']}")
        
        if result['success']:
            if result['format'] == 'python_code':
                print("  ✅ Python code generated (expected - no MCP available)")
            elif result['format'] == 'base64':
                print("  ✅ Base64 image generated (MCP was available)")
            else:
                print(f"  ✅ {result['format']} generated")
        else:
            print(f"  ❌ Generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test 2: Complex heatmap
    print("\nTest 2: Generating Heatmap...")
    try:
        result = await create_analytics(
            content="Create a correlation heatmap between metrics: Revenue, Cost, Profit",
            title="Metrics Correlation",
            chart_type="heatmap"
        )
        
        print(f"  Success: {result['success']}")
        print(f"  Format: {result['format']}")
        print(f"  Chart Type: {result['chart_type']}")
        
        if result['success']:
            print(f"  ✅ {result['format']} generated successfully")
        else:
            print(f"  ❌ Generation failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test 3: Direct executor test
    print("\nTest 3: Testing SimplifiedMCPExecutor directly...")
    try:
        from src.agents.analytics_utils.mcp_executor_simplified import SimplifiedMCPExecutor
        
        executor = SimplifiedMCPExecutor()
        test_code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 2])
plt.title('Test')
"""
        
        result = await executor.execute_chart_code(test_code)
        
        print(f"  Result type: {result.get('type')}")
        print(f"  Message: {result.get('message')}")
        
        if result['type'] == 'code':
            print("  ✅ Code returned as expected (no MCP)")
        elif result['type'] == 'image':
            print("  ✅ Image generated (MCP available)")
        else:
            print(f"  ❌ Unexpected result type: {result['type']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    return True


async def main():
    """Main test runner."""
    print("\nVerifying that NO archived files are being imported...")
    
    # Check imports
    import sys
    archived_modules = [m for m in sys.modules.keys() if 'archived_mcp_backup' in m]
    
    if archived_modules:
        print(f"❌ Found archived modules in use: {archived_modules}")
        print("The simplified implementation is NOT standalone!")
        return False
    else:
        print("✅ No archived modules imported - truly standalone!")
    
    # Run tests
    success = await test_standalone()
    
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED - Simplified MCP is fully standalone!")
        print("The implementation works without any archived files.")
    else:
        print("❌ Some tests failed")
    print("="*70)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)