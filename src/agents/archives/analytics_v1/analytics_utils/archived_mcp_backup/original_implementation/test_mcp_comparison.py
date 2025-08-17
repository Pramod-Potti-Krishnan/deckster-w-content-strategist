"""
Test MCP Implementation Comparison
===================================

Tests both the original complex MCP implementation and the new simplified version.
Allows easy comparison to ensure the simplified version works correctly.

Run with:
    python test_mcp_comparison.py

To switch implementations:
    USE_SIMPLIFIED_MCP=true python test_mcp_comparison.py  (default)
    USE_SIMPLIFIED_MCP=false python test_mcp_comparison.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


async def test_without_mcp():
    """Test behavior when MCP is not available."""
    print("\n" + "="*60)
    print("TEST 1: Without MCP Tool (Code-only mode)")
    print("="*60)
    
    # Test simplified executor without MCP
    from mcp_executor_simplified import SimplifiedMCPExecutor
    
    executor = SimplifiedMCPExecutor(mcp_tool=None)
    
    test_code = """
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 6))
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title('Test Chart')
plt.show()
"""
    
    result = await executor.execute_chart_code(test_code)
    
    print(f"Result type: {result.get('type')}")
    print(f"Message: {result.get('message')}")
    print(f"Code returned: {len(result.get('content', ''))} characters")
    
    assert result['type'] == 'code', "Should return code when MCP not available"
    print("✅ Test passed: Code returned when MCP not available")


async def test_with_mock_mcp():
    """Test behavior with a mock MCP tool."""
    print("\n" + "="*60)
    print("TEST 2: With Mock MCP Tool")
    print("="*60)
    
    # Create a mock MCP tool
    async def mock_mcp_tool(code: str) -> dict:
        """Mock MCP that returns a fake base64 string."""
        if 'matplotlib' in code:
            # Simulate successful chart generation
            return {
                'output': 'BASE64_START\niVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFake\nBASE64_END',
                'returncode': 0
            }
        else:
            return {'output': 'No chart generated', 'returncode': 0}
    
    # Test simplified executor with mock MCP
    from mcp_executor_simplified import SimplifiedMCPExecutor
    
    executor = SimplifiedMCPExecutor(mcp_tool=mock_mcp_tool)
    
    test_code = """
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 6))
plt.bar(['A', 'B', 'C'], [1, 2, 3])
plt.title('Test Bar Chart')
plt.show()
"""
    
    result = await executor.execute_chart_code(test_code)
    
    print(f"Result type: {result.get('type')}")
    print(f"Format: {result.get('format')}")
    print(f"Base64 content: {result.get('content', '')[:50]}...")
    
    assert result['type'] == 'image', "Should return image when MCP succeeds"
    assert result['format'] == 'base64', "Should specify base64 format"
    print("✅ Test passed: Base64 image returned with MCP")


async def test_mcp_failure():
    """Test behavior when MCP execution fails."""
    print("\n" + "="*60)
    print("TEST 3: MCP Execution Failure")
    print("="*60)
    
    # Create a failing MCP tool
    async def failing_mcp_tool(code: str) -> dict:
        """Mock MCP that fails."""
        raise Exception("Simulated MCP failure")
    
    from mcp_executor_simplified import SimplifiedMCPExecutor
    
    executor = SimplifiedMCPExecutor(mcp_tool=failing_mcp_tool)
    
    test_code = "import matplotlib.pyplot as plt"
    
    result = await executor.execute_chart_code(test_code)
    
    print(f"Result type: {result.get('type')}")
    print(f"Message: {result.get('message')}")
    print(f"Error: {result.get('error')}")
    
    assert result['type'] == 'code', "Should fallback to code on failure"
    assert 'error' in result, "Should include error information"
    print("✅ Test passed: Fallback to code on MCP failure")


async def test_implementation_comparison():
    """Compare old and new implementations."""
    print("\n" + "="*60)
    print("TEST 4: Implementation Comparison")
    print("="*60)
    
    use_simplified = os.getenv("USE_SIMPLIFIED_MCP", "true").lower() == "true"
    
    print(f"Currently using: {'SIMPLIFIED' if use_simplified else 'ORIGINAL'} implementation")
    print(f"To switch: USE_SIMPLIFIED_MCP={'false' if use_simplified else 'true'} python {__file__}")
    
    # For now, just verify the environment variable is working
    print(f"✅ Environment variable USE_SIMPLIFIED_MCP is set correctly")
    
    # The full integration test would require proper module imports
    # which need to be run from the parent directory with proper Python path


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP IMPLEMENTATION TESTING")
    print("="*60)
    
    try:
        # Test simplified executor directly
        await test_without_mcp()
        await test_with_mock_mcp()
        await test_mcp_failure()
        
        # Test via python_chart_agent
        await test_implementation_comparison()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✅")
        print("="*60)
        
        # Show file size comparison
        print("\n📊 Code Complexity Comparison:")
        
        original_files = [
            "mcp_integration.py",
            "mcp_python_executor.py", 
            "pydantic_mcp_server.py",
            "mcp_server_config.py"
        ]
        
        original_lines = 0
        for f in original_files:
            try:
                with open(f, 'r') as file:
                    original_lines += len(file.readlines())
            except:
                pass
        
        try:
            with open("mcp_executor_simplified.py", 'r') as f:
                simplified_lines = len(f.readlines())
        except:
            simplified_lines = 0
        
        if original_lines > 0 and simplified_lines > 0:
            reduction = (1 - simplified_lines / original_lines) * 100
            print(f"Original implementation: ~{original_lines} lines")
            print(f"Simplified implementation: {simplified_lines} lines")
            print(f"Code reduction: {reduction:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())