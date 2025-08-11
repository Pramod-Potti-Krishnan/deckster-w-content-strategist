"""
Test with Real MCP Tool
========================

Uses the actual mcp__ide__executeCode available in the environment.
"""

import os
import sys
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv

# Setup
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
load_dotenv()

if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from src.agents.analytics_agent import create_analytics
from src.agents.analytics_utils.mcp_integration import get_mcp_integration


# Test simple chart generation
test_code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

# Create a simple line chart
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.plot(x, np.cos(x), 'r-', linewidth=2, label='cos(x)')
plt.title('Trigonometric Functions')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True, alpha=0.3)

# Save to base64
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
plt.close()

print("BASE64_IMAGE_START")
print(image_base64)
print("BASE64_IMAGE_END")
"""

print("Testing Python code execution...")
print("This will generate a chart using matplotlib")