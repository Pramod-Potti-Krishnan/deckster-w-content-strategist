"""
Direct Chart Executor
=====================

Executes Python chart code directly without MCP when MCP is unavailable.
This provides a fallback mechanism for chart generation.
"""

import logging
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DirectChartExecutor:
    """Execute chart code directly when MCP is not available."""
    
    @staticmethod
    def execute_chart_code(python_code: str) -> Dict[str, Any]:
        """
        Execute Python chart code directly and return base64 image.
        
        Args:
            python_code: Python code that generates a matplotlib chart
            
        Returns:
            Dictionary with execution result
        """
        try:
            # Create a new namespace for execution
            namespace = {
                'plt': plt,
                'np': np,
                'matplotlib': matplotlib
            }
            
            # Execute the code
            exec(python_code, namespace)
            
            # Capture the figure
            if plt.get_fignums():  # Check if any figures exist
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                buffer.close()
                plt.close('all')  # Close all figures
                
                return {
                    "type": "image",
                    "content": img_base64,
                    "format": "base64"
                }
            else:
                return {
                    "type": "error",
                    "content": python_code,
                    "message": "No figure was created by the code"
                }
                
        except Exception as e:
            logger.error(f"Direct execution failed: {e}")
            return {
                "type": "error",
                "content": python_code,
                "message": f"Execution error: {str(e)}"
            }