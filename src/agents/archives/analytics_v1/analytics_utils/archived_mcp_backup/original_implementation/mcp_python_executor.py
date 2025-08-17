"""
MCP Python Executor for Analytics
==================================

Executes Python code using MCP IDE integration for chart generation.
Handles matplotlib/seaborn chart creation and returns base64 images.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import logging
import base64
import json
from typing import Optional, Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)


class MCPPythonExecutor:
    """
    Executes Python code via MCP IDE integration.
    Used for generating complex charts with matplotlib/seaborn.
    """
    
    def __init__(self, execute_code_func=None):
        """
        Initialize the MCP Python executor.
        
        Args:
            execute_code_func: Function to execute Python code (mcp__ide__executeCode)
        """
        self.execute_code = execute_code_func
        self.is_available = execute_code_func is not None
        
    async def execute_chart_code(self, python_code: str) -> Optional[str]:
        """
        Execute Python code for chart generation.
        
        Args:
            python_code: Python code that generates a chart
            
        Returns:
            Base64 encoded image or None if failed
        """
        if not self.is_available:
            logger.warning("MCP Python executor not available")
            return None
        
        try:
            # Wrap the code to ensure base64 output
            wrapped_code = self._wrap_chart_code(python_code)
            
            # Execute via MCP
            logger.info("Executing Python code via MCP...")
            result = await self.execute_code(code=wrapped_code)
            
            # Extract base64 image from result
            if result:
                # The result should contain the base64 string
                if isinstance(result, dict) and 'output' in result:
                    base64_str = result['output']
                elif isinstance(result, str):
                    base64_str = result
                else:
                    base64_str = str(result)
                
                # Clean up the base64 string
                base64_str = base64_str.strip()
                
                # Validate it's actually base64
                if self._is_valid_base64(base64_str):
                    logger.info("Successfully generated chart via MCP")
                    return base64_str
                else:
                    logger.warning("MCP output doesn't appear to be valid base64")
                    return None
            else:
                logger.warning("No output from MCP execution")
                return None
                
        except Exception as e:
            logger.error(f"Failed to execute Python code via MCP: {e}")
            return None
    
    def _wrap_chart_code(self, code: str) -> str:
        """
        Wrap chart generation code to ensure proper base64 output.
        
        Args:
            code: Original Python code
            
        Returns:
            Wrapped code that outputs base64
        """
        # Check if code already handles base64 output
        if 'base64' in code and 'BytesIO' in code:
            # Code already handles base64, just ensure it prints
            if 'print(' not in code:
                # Add print for the base64 variable
                if 'image_base64' in code:
                    code += "\nprint(image_base64)"
                elif 'base64_str' in code:
                    code += "\nprint(base64_str)"
                elif 'encoded' in code:
                    code += "\nprint(encoded)"
            return code
        
        # Wrap code to generate base64
        wrapped = f"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

# User code
{code}

# Save current figure to base64
if plt.get_fignums():  # Check if there are any figures
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close('all')
    print(image_base64)
else:
    print("ERROR: No matplotlib figure created")
"""
        return wrapped
    
    def _is_valid_base64(self, s: str) -> bool:
        """
        Check if string is valid base64.
        
        Args:
            s: String to check
            
        Returns:
            True if valid base64
        """
        try:
            # Try to decode
            if len(s) % 4 != 0:
                return False
            base64.b64decode(s, validate=True)
            return True
        except Exception:
            return False
    
    async def test_availability(self) -> bool:
        """
        Test if MCP Python execution is available.
        
        Returns:
            True if available and working
        """
        if not self.is_available:
            return False
        
        try:
            # Simple test code
            test_code = """
import sys
print(f"Python {sys.version}")
print("MCP execution working")
"""
            result = await self.execute_code(code=test_code)
            return result is not None
        except Exception as e:
            logger.error(f"MCP availability test failed: {e}")
            return False


# Singleton instance
_mcp_executor = None


def get_mcp_executor(execute_code_func=None) -> MCPPythonExecutor:
    """
    Get or create the MCP executor singleton.
    
    Args:
        execute_code_func: Function to execute code
        
    Returns:
        MCP executor instance
    """
    global _mcp_executor
    if _mcp_executor is None:
        _mcp_executor = MCPPythonExecutor(execute_code_func)
    return _mcp_executor


# Helper function to check if MCP is available
async def is_mcp_available() -> bool:
    """
    Check if MCP Python execution is available.
    
    Returns:
        True if available
    """
    executor = get_mcp_executor()
    return await executor.test_availability()