"""
Simplified MCP Executor for Chart Generation
============================================

A clean, simple implementation for executing Python chart code via MCP.
Two modes only: Execute with MCP or return code for manual execution.

This replaces the complex 1,500+ line multi-backend system with a 
straightforward ~100 line implementation.

Author: Analytics Agent System
Date: 2024
Version: 2.0 (Simplified)
"""

import logging
import re
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class SimplifiedMCPExecutor:
    """
    Simplified MCP executor with clear single-path logic.
    
    Design principles:
    1. One execution path (no complex detection)
    2. Clear fallback (execute or return code)
    3. Minimal wrapping (only what's necessary)
    4. No subprocess complications
    """
    
    def __init__(self, mcp_tool=None):
        """
        Initialize the executor.
        
        Args:
            mcp_tool: The MCP execution function (e.g., mcp__ide__executeCode)
                     or None if MCP is not available
        """
        self.mcp_tool = mcp_tool
        self.is_available = mcp_tool is not None
        
        if self.is_available:
            logger.info("MCP executor initialized with tool")
        else:
            logger.info("MCP executor initialized without tool (code-only mode)")
    
    def set_mcp_tool(self, mcp_tool):
        """
        Set or update the MCP tool.
        
        Args:
            mcp_tool: The MCP execution function
        """
        self.mcp_tool = mcp_tool
        self.is_available = mcp_tool is not None
        if self.is_available:
            logger.info("MCP tool updated")
    
    async def execute_chart_code(self, python_code: str) -> Dict[str, Any]:
        """
        Execute chart code via MCP or return for manual execution.
        
        Args:
            python_code: Python code that generates a matplotlib chart
            
        Returns:
            Dictionary with execution result:
            - If MCP available and successful: {"type": "image", "content": base64_str, "format": "base64"}
            - If MCP unavailable or failed: {"type": "code", "content": python_code, "message": reason}
        """
        if not self.is_available:
            return {
                "type": "code",
                "content": python_code,
                "message": "MCP not available, returning Python code for manual execution"
            }
        
        try:
            # Wrap code for matplotlib capture if needed
            wrapped_code = self._wrap_for_matplotlib(python_code)
            
            # Execute via MCP
            logger.debug("Executing code via MCP...")
            result = await self.mcp_tool(code=wrapped_code)
            
            # Extract base64 image from result
            base64_img = self._extract_base64(result)
            
            if base64_img:
                logger.info("Successfully generated chart via MCP")
                return {
                    "type": "image",
                    "content": base64_img,
                    "format": "base64"
                }
            else:
                logger.warning("MCP execution completed but no image generated")
                return {
                    "type": "code",
                    "content": python_code,
                    "message": "No image generated, returning code"
                }
                
        except Exception as e:
            logger.error(f"MCP execution failed: {e}")
            return {
                "type": "code",
                "content": python_code,
                "message": f"MCP execution failed: {str(e)}",
                "error": str(e)
            }
    
    def _wrap_for_matplotlib(self, code: str) -> str:
        """
        Minimal wrapping to ensure matplotlib charts are captured.
        Only wraps if necessary.
        
        Args:
            code: Original Python code
            
        Returns:
            Wrapped code if needed, original otherwise
        """
        # If code already handles base64 output, don't wrap
        if 'base64' in code and 'savefig' in code:
            return code
        
        # Simple wrapping for chart capture
        return f"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Original code
{code}

# Capture the figure if one exists
if plt.get_fignums():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close('all')
    print("BASE64_START")
    print(image_base64)
    print("BASE64_END")
"""
    
    def _extract_base64(self, result: Union[Dict, str]) -> Optional[str]:
        """
        Extract base64 image from MCP execution result.
        Handles various result formats.
        
        Args:
            result: MCP execution result
            
        Returns:
            Base64 string if found, None otherwise
        """
        if not result:
            return None
        
        # Handle different result formats
        if isinstance(result, dict):
            # Check common keys for base64 data
            for key in ['output', 'stdout', 'image_base64', 'image', 'base64']:
                if key in result and result[key]:
                    output = str(result[key])
                    # Try to extract base64 from output
                    base64_str = self._find_base64_in_text(output)
                    if base64_str:
                        return base64_str
        elif isinstance(result, str):
            # Direct string result
            return self._find_base64_in_text(result)
        
        return None
    
    def _find_base64_in_text(self, text: str) -> Optional[str]:
        """
        Find base64 image data in text output.
        
        Args:
            text: Text that may contain base64 data
            
        Returns:
            Base64 string if found, None otherwise
        """
        if not text:
            return None
        
        # Look for marked base64 content
        if "BASE64_START" in text and "BASE64_END" in text:
            match = re.search(r'BASE64_START\s*\n?(.*?)\n?BASE64_END', text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Look for raw base64 (heuristic: long string of base64 chars)
        # Base64 for PNG images typically starts with iVBORw0KGgo
        if 'iVBORw0KGgo' in text:
            # Extract the base64 portion
            lines = text.strip().split('\n')
            for line in lines:
                if len(line) > 100 and re.match(r'^[A-Za-z0-9+/=]+$', line):
                    return line.strip()
        
        return None


# Singleton instance
_executor = None


def get_simplified_executor(mcp_tool=None) -> SimplifiedMCPExecutor:
    """
    Get or create the simplified MCP executor singleton.
    
    Args:
        mcp_tool: MCP execution function if available
        
    Returns:
        SimplifiedMCPExecutor instance
    """
    global _executor
    if _executor is None:
        _executor = SimplifiedMCPExecutor(mcp_tool)
    elif mcp_tool and not _executor.mcp_tool:
        # Update with MCP tool if provided
        _executor.mcp_tool = mcp_tool
        _executor.is_available = True
    return _executor


# Convenience function for backward compatibility
async def execute_chart_with_simplified_mcp(python_code: str, mcp_tool=None) -> Dict[str, Any]:
    """
    Execute chart code using the simplified MCP executor.
    
    Args:
        python_code: Python code generating a chart
        mcp_tool: Optional MCP tool function
        
    Returns:
        Execution result dictionary
    """
    executor = get_simplified_executor(mcp_tool)
    return await executor.execute_chart_code(python_code)