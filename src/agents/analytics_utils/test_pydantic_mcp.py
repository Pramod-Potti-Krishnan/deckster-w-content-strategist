"""
Test Suite for Pydantic MCP Server Integration
==============================================

Quick test to verify that the pydantic MCP server integration works correctly.
Tests basic functionality without running the full demo.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import asyncio
import logging
import sys
import traceback
from pathlib import Path

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_imports():
    """Test that all modules can be imported correctly."""
    print("🔍 Testing imports...")
    
    try:
        # Test pydantic server import
        from .pydantic_mcp_server import PydanticMCPServer, get_server, PythonExecutionRequest
        print("✅ Pydantic MCP Server imported successfully")
        
        # Test MCP integration import
        from .mcp_integration import MCPIntegration, get_mcp_integration
        print("✅ MCP Integration imported successfully")
        
        # Test configuration import
        from .mcp_server_config import MCPServerConfig, MCPServerManager
        print("✅ MCP Server Config imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False


async def test_server_initialization():
    """Test server initialization and basic health check."""
    print("\n🏥 Testing server initialization...")
    
    try:
        from .pydantic_mcp_server import get_server
        
        # Get server instance
        server = get_server()
        print("✅ Server instance created")
        
        # Run health check
        health = await server.health_check()
        print(f"✅ Health check completed: {health['status']}")
        
        # Check capabilities
        if health.get('plotting_enabled'):
            print("✅ Plotting capabilities enabled")
        else:
            print("⚠️  Plotting capabilities disabled")
        
        return health['status'] == 'healthy'
        
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        traceback.print_exc()
        return False


async def test_mcp_integration():
    """Test MCP integration backend detection."""
    print("\n🔗 Testing MCP integration...")
    
    try:
        from .mcp_integration import get_mcp_integration
        
        # Get integration instance
        integration = get_mcp_integration()
        print(f"✅ Integration created with backend: {integration.backend_type}")
        
        # Get backend info
        info = integration.get_backend_info()
        print(f"   Available: {info['is_available']}")
        print(f"   Capabilities: {info['capabilities']}")
        
        # Test availability
        available = await integration.test_availability()
        print(f"✅ Availability test: {'PASSED' if available else 'FAILED'}")
        
        return available
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        traceback.print_exc()
        return False


async def test_basic_execution():
    """Test basic Python code execution."""
    print("\n🐍 Testing basic execution...")
    
    try:
        from .pydantic_mcp_server import execute_python_with_mcp
        
        # Simple test code
        test_code = """
import sys
import numpy as np

print(f"Python version: {sys.version.split()[0]}")
print(f"NumPy version: {np.__version__}")

result = np.array([1, 2, 3, 4, 5])
mean_val = np.mean(result)
print(f"Test array mean: {mean_val}")

# Set a variable for return value testing
final_result = mean_val * 2
"""
        
        result = await execute_python_with_mcp(test_code)
        
        if result.success:
            print("✅ Basic execution successful")
            print(f"   Execution time: {result.execution_time:.2f}s")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Basic execution failed: {result.error_message}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Basic execution test failed: {e}")
        traceback.print_exc()
        return False


async def test_chart_generation():
    """Test simple chart generation."""
    print("\n📊 Testing chart generation...")
    
    try:
        from .pydantic_mcp_server import create_chart_with_mcp
        
        # Simple chart data
        data = {
            "labels": ["A", "B", "C", "D"],
            "values": [10, 15, 8, 12]
        }
        
        result = await create_chart_with_mcp("bar", data, "Test Chart")
        
        if result.success:
            print("✅ Chart generation successful")
            print(f"   Execution time: {result.execution_time:.2f}s")
            print(f"   Plots generated: {len(result.plots)}")
            
            if result.plots:
                # Verify base64 data
                plot_data = result.plots[0]
                if len(plot_data) > 1000:  # Basic sanity check
                    print("✅ Chart data looks valid")
                    return True
                else:
                    print("⚠️  Chart data seems too small")
                    return False
            else:
                print("⚠️  No plots in result")
                return False
        else:
            print(f"❌ Chart generation failed: {result.error_message}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Chart generation test failed: {e}")
        traceback.print_exc()
        return False


async def run_quick_test():
    """Run a quick test suite."""
    print("🚀 Running Pydantic MCP Server Quick Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Server Initialization", test_server_initialization),
        ("MCP Integration", test_mcp_integration),
        ("Basic Execution", test_basic_execution),
        ("Chart Generation", test_chart_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    overall_success = failed == 0
    print(f"Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    # Run the quick test
    success = asyncio.run(run_quick_test())
    sys.exit(0 if success else 1)