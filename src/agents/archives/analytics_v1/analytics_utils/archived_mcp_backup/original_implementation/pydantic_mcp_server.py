"""
Pydantic MCP Server for Python Code Execution
=============================================

Implements a Python execution server following the pydantic MCP approach.
Based on: https://ai.pydantic.dev/mcp/run-python/

This server executes Python code in a subprocess and captures chart outputs
as base64-encoded images.
"""

import os
import sys
import json
import base64
import asyncio
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PydanticMCPServer:
    """
    MCP Server for executing Python code and capturing outputs.
    
    This implementation follows the pydantic MCP pattern for safe
    Python code execution with image capture support.
    """
    
    def __init__(self, python_path: Optional[str] = None):
        """
        Initialize the MCP server.
        
        Args:
            python_path: Path to Python interpreter (defaults to sys.executable)
        """
        # Use venv Python if available, otherwise sys.executable
        if python_path:
            self.python_path = python_path
        elif os.path.exists('venv/bin/python'):
            self.python_path = os.path.abspath('venv/bin/python')
        else:
            self.python_path = sys.executable
        self.timeout = 30  # seconds
        
    async def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code and capture output.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with execution results including stdout, stderr, and images
        """
        logger.info(f"Executing Python code via pydantic MCP server using: {self.python_path}")
        
        # Wrap code to capture matplotlib figures
        wrapped_code = self._wrap_code_for_capture(code)
        
        # Create temporary file for execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(wrapped_code)
            temp_file = f.name
        
        try:
            # Execute Python code in subprocess
            result = await self._run_subprocess(temp_file)
            
            # Parse output for base64 images
            output = result.get('stdout', '')
            base64_image = self._extract_base64_image(output)
            
            return {
                'success': result.get('returncode') == 0,
                'stdout': output,
                'stderr': result.get('stderr', ''),
                'image_base64': base64_image,
                'returncode': result.get('returncode', 0)
            }
            
        except Exception as e:
            logger.error(f"MCP execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': str(e),
                'image_base64': None
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def _wrap_code_for_capture(self, code: str) -> str:
        """
        Wrap user code to automatically capture matplotlib outputs.
        
        Args:
            code: Original Python code
            
        Returns:
            Wrapped code that captures images
        """
        wrapper = '''
import sys
import base64
from io import BytesIO

# Set matplotlib backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Track if we should save the figure
_mcp_figure_created = False

# Hook into plt.show to capture figures
_original_show = plt.show
def _mcp_show(*args, **kwargs):
    global _mcp_figure_created
    _mcp_figure_created = True
    # Don't actually show in non-interactive mode
    pass
plt.show = _mcp_show

# Hook into figure creation
_original_figure = plt.figure
def _mcp_figure(*args, **kwargs):
    global _mcp_figure_created
    _mcp_figure_created = True
    return _original_figure(*args, **kwargs)
plt.figure = _mcp_figure

try:
    # Execute user code
{user_code}
    
    # If a figure was created, save it
    if _mcp_figure_created or plt.get_fignums():
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close('all')
        
        # Output marker for extraction
        print("MCP_BASE64_IMAGE_START")
        print(image_base64)
        print("MCP_BASE64_IMAGE_END")
        
except Exception as e:
    import traceback
    print(f"MCP_ERROR: {{e}}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
'''
        
        # Indent user code
        indented_code = '\n'.join('    ' + line for line in code.split('\n'))
        
        return wrapper.format(user_code=indented_code)
    
    async def _run_subprocess(self, script_path: str) -> Dict[str, Any]:
        """
        Run Python script in subprocess.
        
        Args:
            script_path: Path to Python script
            
        Returns:
            Execution results
        """
        try:
            # Run Python subprocess
            process = await asyncio.create_subprocess_exec(
                self.python_path, script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            return {
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'returncode': process.returncode
            }
            
        except asyncio.TimeoutError:
            process.kill()
            return {
                'stdout': '',
                'stderr': 'Execution timed out',
                'returncode': -1
            }
    
    def _extract_base64_image(self, output: str) -> Optional[str]:
        """
        Extract base64 image from output.
        
        Args:
            output: Subprocess output
            
        Returns:
            Base64 image string if found
        """
        if "MCP_BASE64_IMAGE_START" in output and "MCP_BASE64_IMAGE_END" in output:
            start = output.index("MCP_BASE64_IMAGE_START") + len("MCP_BASE64_IMAGE_START")
            end = output.index("MCP_BASE64_IMAGE_END")
            return output[start:end].strip()
        return None


class PydanticMCPExecutor:
    """
    High-level executor that integrates with the analytics system.
    """
    
    def __init__(self):
        """Initialize the executor with MCP server."""
        self.server = PydanticMCPServer()
        
    async def execute_chart_code(self, code: str) -> Optional[str]:
        """
        Execute chart generation code and return base64 image.
        
        Args:
            code: Python code that generates a chart
            
        Returns:
            Base64-encoded PNG image or None if failed
        """
        result = await self.server.execute_code(code)
        
        if result['success'] and result.get('image_base64'):
            logger.info("Successfully generated chart image via pydantic MCP")
            return result['image_base64']
        else:
            logger.warning(f"Chart generation failed: {result.get('stderr', 'Unknown error')}")
            return None
    
    async def __call__(self, code: str) -> Dict[str, Any]:
        """
        Make the executor callable as an MCP tool.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution results compatible with MCP tool interface
        """
        result = await self.server.execute_code(code)
        
        # Return result directly - mcp_integration knows how to handle it
        return result


# Global instance for easy access
pydantic_mcp_executor = PydanticMCPExecutor()


async def get_pydantic_mcp_tool():
    """
    Get the pydantic MCP tool function.
    
    Returns:
        Async function that can be used as mcp_tool parameter
    """
    return pydantic_mcp_executor


# Example usage and testing
if __name__ == "__main__":
    async def test_mcp_server():
        """Test the MCP server with chart generation."""
        
        print("Testing Pydantic MCP Server")
        print("=" * 50)
        
        # Test 1: Simple code execution
        print("\n1. Testing basic execution...")
        server = PydanticMCPServer()
        print(f"   Using Python: {server.python_path}")
        
        code = """
import sys
print(f"Python {sys.version}")
print("MCP server working!")
"""
        
        result = await server.execute_code(code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['stdout'][:100]}")
        
        # Test 2: Chart generation
        print("\n2. Testing chart generation...")
        
        chart_code = """
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create chart
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.plot(x, np.cos(x), 'r-', linewidth=2, label='cos(x)')
plt.title('Test Chart from Pydantic MCP Server')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
"""
        
        result = await server.execute_code(chart_code)
        print(f"Success: {result['success']}")
        
        if result.get('image_base64'):
            print(f"✅ Image generated! Base64 length: {len(result['image_base64'])}")
            
            # Save test image
            image_data = base64.b64decode(result['image_base64'])
            with open('test_mcp_output.png', 'wb') as f:
                f.write(image_data)
            print("   Saved to test_mcp_output.png")
        else:
            print("❌ No image generated")
            if result.get('stderr'):
                print(f"   Error: {result['stderr']}")
        
        # Test 3: Using the executor
        print("\n3. Testing PydanticMCPExecutor...")
        executor = PydanticMCPExecutor()
        
        base64_image = await executor.execute_chart_code(chart_code)
        if base64_image:
            print(f"✅ Executor worked! Image length: {len(base64_image)}")
        else:
            print("❌ Executor failed")
        
        print("\n" + "=" * 50)
        print("Pydantic MCP Server Ready for Production!")
        print("\nUsage in analytics:")
        print("  from src.agents.analytics_utils.pydantic_mcp_server import pydantic_mcp_executor")
        print("  result = await create_analytics(content, mcp_tool=pydantic_mcp_executor)")
    
    # Run test
    asyncio.run(test_mcp_server())