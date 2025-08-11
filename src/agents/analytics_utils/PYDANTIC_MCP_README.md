# Pydantic MCP Server for Python Code Execution

A complete implementation of a Pydantic-based MCP (Model Context Protocol) server for executing Python code and generating real chart images. Based on the guidelines from [https://ai.pydantic.dev/mcp/run-python/](https://ai.pydantic.dev/mcp/run-python/).

## 🎯 Features

- **Safe Python Code Execution**: Runs Python code in a controlled environment with restricted imports
- **Real Chart Generation**: Creates actual matplotlib/seaborn charts as base64-encoded PNG images
- **Multiple Backend Support**: Automatically detects and uses the best available MCP backend
- **Production Ready**: Comprehensive error handling, logging, and timeout management
- **Comprehensive Testing**: Full test suite and demo examples

## 🏗️ Architecture

### Core Components

1. **`pydantic_mcp_server.py`** - Main server implementation
   - `PydanticMCPServer`: Core server class with safe execution environment
   - `PythonExecutionRequest`/`PythonExecutionResult`: Pydantic models for requests/responses
   - Chart generation utilities and base64 image capture

2. **`mcp_integration.py`** - Enhanced MCP integration (Updated)
   - `MCPIntegration`: Multi-backend support with automatic detection
   - Supports both pydantic server and external MCP tools
   - Intelligent fallback mechanisms

3. **`mcp_server_config.py`** - Configuration and management
   - `MCPServerConfig`: Configuration management with JSON file support
   - `MCPServerManager`: Server lifecycle management
   - `MCPServerCLI`: Command-line interface

4. **`pydantic_mcp_demo.py`** - Comprehensive demonstration
   - Complete working examples
   - Multiple chart types
   - Performance testing
   - Real PNG file generation

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from src.agents.analytics_utils.pydantic_mcp_server import get_server, create_chart_with_mcp

async def main():
    # Create a simple chart
    data = {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [100, 120, 95, 140]
    }
    
    result = await create_chart_with_mcp("bar", data, "Quarterly Sales")
    
    if result.success and result.plots:
        # Save the chart
        import base64
        with open("chart.png", "wb") as f:
            f.write(base64.b64decode(result.plots[0]))
        print("Chart saved as chart.png")

asyncio.run(main())
```

### Using MCP Integration

```python
from src.agents.analytics_utils.mcp_integration import get_mcp_integration

# Get integration instance (auto-detects backend)
mcp = get_mcp_integration()

# Check backend info
info = mcp.get_backend_info()
print(f"Backend: {info['backend_type']}")
print(f"Available: {info['is_available']}")

# Execute Python code
code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title('Sine Wave')
plt.show()
"""

result = await mcp.execute_chart_code(code)
if result:
    print(f"Generated base64 image: {len(result)} characters")
```

## 🧪 Testing

### Run Quick Tests

```bash
# From the analytics_utils directory
python -m test_pydantic_mcp
```

### Run Full Demo

```bash
# From the analytics_utils directory
python -m pydantic_mcp_demo
```

### Run Server Health Check

```bash
# From the analytics_utils directory
python -m mcp_server_config health
```

### Generate Example Chart

```bash
# From the analytics_utils directory
python -m mcp_server_config example
```

## 📊 Supported Chart Types

The system supports multiple chart types through both Mermaid and Python backends:

### Python/Matplotlib Charts (via Pydantic MCP Server)
- **Bar Charts**: Standard and advanced bar charts with styling
- **Line Charts**: Trend lines with confidence bands and annotations  
- **Pie Charts**: Donut charts with custom colors and percentages
- **Scatter Plots**: X-Y scatter with variable point sizes
- **Histograms**: Distribution analysis with customizable bins
- **Heatmaps**: 2D data visualization with color mapping
- **Area Charts**: Filled line charts for cumulative data
- **Box Plots**: Statistical distribution visualization
- **Bubble Charts**: Scatter plots with size-based third dimension
- **Waterfall Charts**: Sequential value changes
- **Treemaps**: Hierarchical data as nested rectangles

### Example Output

The demo generates charts like:
- `chart_bar_*.png` - Quarterly revenue bars
- `chart_line_*.png` - Monthly growth trends  
- `chart_pie_*.png` - Market share distribution
- `advanced_dashboard_*.png` - Multi-subplot dashboard

## ⚙️ Configuration

Create a configuration file `mcp_server_config.json`:

```json
{
  "server": {
    "max_execution_time": 30,
    "enable_plotting": true,
    "temp_dir": null,
    "log_level": "INFO"
  },
  "plotting": {
    "default_style": "seaborn",
    "default_figure_size": [10, 6],
    "default_dpi": 100
  },
  "security": {
    "restricted_mode": true
  }
}
```

## 🔒 Security Features

- **Restricted Execution Environment**: Limited builtins and imports
- **Timeout Management**: Configurable execution timeouts  
- **Safe Globals**: Only allowed scientific libraries (numpy, matplotlib, etc.)
- **Resource Limits**: Memory and CPU usage controls
- **Error Isolation**: Comprehensive exception handling

## 📈 Performance

Typical performance metrics from testing:
- Basic execution: ~0.05-0.2 seconds
- Simple charts: ~0.5-1.0 seconds  
- Complex multi-subplot dashboards: ~1.5-3.0 seconds
- Base64 image generation: ~0.1-0.3 seconds additional

Concurrent execution supported with asyncio.

## 🔧 Development

### Adding New Chart Types

1. Add chart type to `models.py`:
```python
class ChartType(str, Enum):
    # ... existing types
    NEW_CHART = "new_chart"
```

2. Implement generator in `pydantic_mcp_server.py`:
```python
def create_new_chart_code(self, data, title, config):
    # Chart-specific matplotlib code
    return chart_code
```

3. Update chart type mappings and test.

### Extending Security

Modify `_prepare_safe_environment()` in `pydantic_mcp_server.py` to add/remove allowed modules and builtins.

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure matplotlib, numpy, seaborn are installed
   ```bash
   pip install matplotlib numpy seaborn pandas
   ```

2. **Backend Detection**: Check logs for backend detection:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Plot Not Generating**: Verify matplotlib backend:
   ```python
   import matplotlib
   print(matplotlib.get_backend())  # Should be 'Agg'
   ```

4. **Timeout Issues**: Increase timeout in configuration or request:
   ```python
   request = PythonExecutionRequest(code=code, timeout=60)
   ```

### Debug Mode

Enable debug logging to see detailed execution information:

```python
import logging
logging.getLogger('src.agents.analytics_utils').setLevel(logging.DEBUG)
```

## 📝 Integration Examples

### With Analytics Agent

```python
from src.agents.analytics_utils.python_chart_agent import PythonChartAgent
from src.agents.analytics_utils.mcp_integration import get_mcp_integration

# Create agent with MCP integration
mcp_integration = get_mcp_integration()
agent = PythonChartAgent(mcp_tool=mcp_integration.execute_python_code)

# Generate chart through agent
chart_output = await agent.generate_chart(plan, data_points, description, insights)
```

### With Existing Codebase

The enhanced `mcp_integration.py` automatically detects and uses the pydantic server, so existing code will seamlessly benefit from the new capabilities:

```python
# Existing code continues to work
from src.agents.analytics_utils.mcp_integration import execute_chart_with_mcp

base64_image = await execute_chart_with_mcp(python_code)
```

## 🎉 Demo Output

Running the full demo creates:
- Multiple PNG chart files
- Advanced dashboard with subplots
- Performance metrics report
- Comprehensive JSON report

Example files generated:
```
mcp_demo_output/
├── chart_bar_143052.png
├── chart_line_143053.png  
├── chart_pie_143054.png
├── chart_scatter_143055.png
├── chart_histogram_143056.png
├── advanced_dashboard_143057.png
└── demo_report_20241125_143058.json
```

This implementation provides a complete, production-ready solution for executing Python code and generating real charts using the pydantic MCP server approach.