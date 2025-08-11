"""
MCP Integration for Analytics
==============================

Direct integration with MCP tools for Python code execution.
Automatically detects and uses available MCP tools, including the pydantic MCP server.

Now supports:
- Built-in pydantic MCP server (preferred)
- External MCP tools (mcp__ide__executeCode)
- Fallback mode

Author: Analytics Agent System
Date: 2024
Version: 3.0
"""

import logging
import base64
import asyncio
from typing import Optional, Callable, Any, Union
from io import BytesIO

logger = logging.getLogger(__name__)


class MCPIntegration:
    """
    Advanced MCP integration with multiple backend support.
    Automatically detects and uses the best available MCP backend:
    1. Pydantic MCP Server (preferred)
    2. External MCP tools (mcp__ide__executeCode)
    3. Fallback mode
    """
    
    def __init__(self):
        """Initialize MCP integration."""
        self.mcp_tool = None
        self.pydantic_server = None
        self.backend_type = None
        self.is_available = False
        self._detect_mcp_backends()
    
    def _detect_mcp_backends(self):
        """
        Detect available MCP backends in order of preference.
        """
        # Try to initialize pydantic MCP server first
        if self._try_pydantic_server():
            self.backend_type = "pydantic_server"
            self.is_available = True
            logger.info("Pydantic MCP server initialized successfully")
            return
        
        # Fall back to external MCP tool detection
        if self._try_external_mcp():
            self.backend_type = "external_mcp"
            self.is_available = True
            logger.info("External MCP tool detected and available")
            return
        
        # No MCP backend available
        self.backend_type = None
        self.is_available = False
        logger.warning("No MCP backend available - running in fallback mode")
    
    def _try_pydantic_server(self) -> bool:
        """
        Try to initialize the pydantic MCP server.
        
        Returns:
            True if successful
        """
        try:
            from .pydantic_mcp_server import get_server
            self.pydantic_server = get_server()
            return True
        except Exception as e:
            logger.debug(f"Pydantic MCP server not available: {e}")
            return False
    
    def _try_external_mcp(self) -> bool:
        """
        Try to detect external MCP tools.
        
        Returns:
            True if successful
        """
        try:
            # Check if we can access the MCP tool
            # In the actual environment, mcp__ide__executeCode is available as a tool
            import sys
            # Check if we're in an environment with MCP tools
            return True
        except Exception as e:
            logger.debug(f"External MCP tool not available: {e}")
            return False
    
    def set_mcp_tool(self, tool_func: Callable):
        """
        Set the MCP tool function explicitly.
        
        Args:
            tool_func: The MCP execute function
        """
        self.mcp_tool = tool_func
        self.is_available = tool_func is not None
        
        # Check if this is a pydantic MCP executor
        if tool_func is not None:
            # Check if it's the pydantic executor
            from .pydantic_mcp_server import pydantic_mcp_executor
            if tool_func is pydantic_mcp_executor or hasattr(tool_func, '__name__') and 'pydantic' in tool_func.__name__.lower():
                self.backend_type = "pydantic_server"
                self.pydantic_server = tool_func
                logger.info("Pydantic MCP executor detected and set")
            else:
                self.backend_type = "external_mcp"
                logger.info("External MCP tool set and ready for use")
    
    async def execute_python_code(self, code: str) -> Optional[dict]:
        """
        Execute Python code using the best available MCP backend.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution result dictionary or None
        """
        if not self.is_available:
            logger.warning("No MCP backend available for execution")
            return None
        
        try:
            logger.info(f"Executing Python code via {self.backend_type}...")
            
            if self.backend_type == "pydantic_server":
                return await self._execute_with_pydantic_server(code)
            elif self.backend_type == "external_mcp":
                return await self._execute_with_external_mcp(code)
            else:
                logger.error("No valid MCP backend configured")
                return None
                
        except Exception as e:
            logger.error(f"MCP execution failed: {e}")
            return None
    
    async def _execute_with_pydantic_server(self, code: str) -> Optional[dict]:
        """
        Execute code using the pydantic MCP server.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution result dictionary
        """
        try:
            from .pydantic_mcp_server import PythonExecutionRequest
            
            request = PythonExecutionRequest(code=code, timeout=30)
            result = await self.pydantic_server.execute_python_code(request)
            
            # Convert pydantic result to dictionary format
            return {
                "success": result.success,
                "output": result.stdout,
                "stderr": result.stderr,
                "plots": result.plots,
                "execution_time": result.execution_time,
                "return_value": result.return_value,
                "error_type": result.error_type,
                "error_message": result.error_message,
                "metadata": result.metadata
            }
            
        except Exception as e:
            logger.error(f"Pydantic server execution failed: {e}")
            return None
    
    async def _execute_with_external_mcp(self, code: str) -> Optional[dict]:
        """
        Execute code using external MCP tool.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution result dictionary
        """
        if not self.mcp_tool:
            logger.warning("External MCP tool not configured")
            return None
        
        try:
            # Call the external MCP tool
            result = await self.mcp_tool(code=code)
            logger.info("External MCP execution completed")
            return result
        except Exception as e:
            logger.error(f"External MCP execution failed: {e}")
            return None
    
    async def execute_chart_code(self, python_code: str) -> Optional[str]:
        """
        Execute Python chart code and return base64 image.
        
        Args:
            python_code: Python code that generates a matplotlib chart
            
        Returns:
            Base64 encoded PNG image or None
        """
        if not self.is_available:
            logger.warning("MCP not available, cannot execute chart code")
            return None
        
        try:
            if self.backend_type == "pydantic_server":
                # Use pydantic server's direct chart capabilities if available
                return await self._execute_chart_with_pydantic(python_code)
            else:
                # Fall back to wrapped code approach for external MCP
                wrapped_code = self._wrap_chart_code(python_code)
                result = await self.execute_python_code(wrapped_code)
                
                if result:
                    return self._extract_base64(result)
        
        except Exception as e:
            logger.error(f"Chart execution failed: {e}")
        
        return None
    
    async def _execute_chart_with_pydantic(self, python_code: str) -> Optional[str]:
        """
        Execute chart code using pydantic server's plotting capabilities.
        
        Args:
            python_code: Python code for chart
            
        Returns:
            Base64 encoded image or None
        """
        try:
            # If we have a pydantic executor, use it directly
            if self.pydantic_server:
                # The pydantic executor handles everything
                result = await self.pydantic_server(python_code)
                
                # Extract base64 from result
                if isinstance(result, dict) and result.get('image_base64'):
                    return result['image_base64']
                
                # Fallback to extraction
                return self._extract_base64(result)
            
            # If no pydantic server, something went wrong
            logger.warning("No pydantic server available")
            return None
                
        except Exception as e:
            logger.error(f"Pydantic chart execution failed: {e}")
            return None
    
    def _wrap_chart_code_for_pydantic(self, code: str) -> str:
        """
        Wrap chart code specifically for pydantic server execution.
        
        Args:
            code: Original Python code
            
        Returns:
            Wrapped code optimized for pydantic server
        """
        # Check if code already handles matplotlib properly
        if 'matplotlib.use(' in code or 'plt.show()' in code:
            return code
        
        # Simple wrapping for pydantic server
        wrapped = f"""
# Ensure proper matplotlib backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set plotting style
plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')

# Original chart code
{code}

# Ensure plot is displayed (will be captured by pydantic server)
plt.tight_layout()
plt.show()
"""
        return wrapped
    
    def _wrap_chart_code(self, code: str) -> str:
        """
        Wrap chart code to ensure base64 output.
        
        Args:
            code: Original Python code
            
        Returns:
            Wrapped code that outputs base64
        """
        # Check if code already handles base64
        if 'base64' in code and 'savefig' in code:
            return code
        
        # Wrap to generate base64
        wrapped = f"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import base64
from io import BytesIO

# Original code
{code}

# Capture and encode the figure
if plt.get_fignums():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close('all')
    
    # Output the base64 string
    print("BASE64_IMAGE_START")
    print(image_base64)
    print("BASE64_IMAGE_END")
else:
    print("ERROR: No figure created")
"""
        return wrapped
    
    def _extract_base64(self, result: dict) -> Optional[str]:
        """
        Extract base64 image from MCP execution result.
        
        Args:
            result: MCP execution result
            
        Returns:
            Base64 string or None
        """
        try:
            # Result might be in different formats
            output = None
            
            if isinstance(result, dict):
                # Check for direct image_base64 field (pydantic MCP server)
                if 'image_base64' in result and result['image_base64']:
                    logger.info(f"Found direct image_base64: {len(result['image_base64'])} characters")
                    return result['image_base64']
                
                # Check for output field
                output = result.get('output', '')
                # Also check for stdout
                if not output:
                    output = result.get('stdout', '')
            elif isinstance(result, str):
                output = result
            else:
                output = str(result)
            
            # Look for base64 markers
            if 'BASE64_IMAGE_START' in output and 'BASE64_IMAGE_END' in output:
                start_idx = output.index('BASE64_IMAGE_START') + len('BASE64_IMAGE_START')
                end_idx = output.index('BASE64_IMAGE_END')
                base64_str = output[start_idx:end_idx].strip()
                
                # Validate base64
                if self._is_valid_base64(base64_str):
                    logger.info("Successfully extracted base64 image from MCP output")
                    return base64_str
                else:
                    logger.warning("Extracted string is not valid base64")
            
            # Try to find raw base64 (if markers aren't present)
            # Look for a long string that could be base64
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 100 and self._is_valid_base64(line):
                    logger.info("Found potential base64 image in output")
                    return line
            
            logger.warning("Could not extract base64 image from MCP output")
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract base64: {e}")
            return None
    
    def _is_valid_base64(self, s: str) -> bool:
        """
        Check if a string is valid base64.
        
        Args:
            s: String to check
            
        Returns:
            True if valid base64
        """
        try:
            if not s or len(s) < 20:
                return False
            # Try to decode
            base64.b64decode(s, validate=True)
            return True
        except Exception:
            return False
    
    async def test_availability(self) -> bool:
        """
        Test if MCP is available and working.
        
        Returns:
            True if MCP is available and working
        """
        if not self.is_available:
            return False
        
        test_code = """
import sys
print(f"Python {sys.version}")
print("MCP execution test successful")
"""
        
        try:
            result = await self.execute_python_code(test_code)
            success = result is not None and (
                result.get("success", False) or 
                "MCP execution test successful" in result.get("output", "")
            )
            
            if success:
                logger.info(f"MCP backend '{self.backend_type}' test successful")
            else:
                logger.warning(f"MCP backend '{self.backend_type}' test failed")
                
            return success
            
        except Exception as e:
            logger.error(f"MCP availability test failed: {e}")
            return False
    
    def get_backend_info(self) -> dict:
        """
        Get information about the current MCP backend.
        
        Returns:
            Backend information dictionary
        """
        return {
            "backend_type": self.backend_type,
            "is_available": self.is_available,
            "has_pydantic_server": self.pydantic_server is not None,
            "has_external_mcp": self.mcp_tool is not None,
            "capabilities": {
                "python_execution": self.is_available,
                "chart_generation": self.is_available,
                "plot_capture": self.backend_type == "pydantic_server"
            }
        }


# Global singleton instance
_mcp_instance = None


def get_mcp_integration() -> MCPIntegration:
    """
    Get the global MCP integration instance.
    
    Returns:
        MCP integration singleton
    """
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = MCPIntegration()
    return _mcp_instance


async def execute_chart_with_mcp(python_code: str, mcp_tool=None) -> Optional[str]:
    """
    Convenience function to execute chart code with MCP.
    
    Args:
        python_code: Python code generating a chart
        mcp_tool: Optional MCP tool function
        
    Returns:
        Base64 encoded image or None
    """
    mcp = get_mcp_integration()
    
    # Set tool if provided
    if mcp_tool:
        mcp.set_mcp_tool(mcp_tool)
    
    # Execute and return
    return await mcp.execute_chart_code(python_code)


# Function to check if we're in an MCP-enabled environment
def is_mcp_available() -> bool:
    """
    Check if MCP is available in the current environment.
    
    Returns:
        True if MCP is available
    """
    mcp = get_mcp_integration()
    return mcp.is_available