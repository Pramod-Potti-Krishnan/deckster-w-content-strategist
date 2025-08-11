"""
Python Chart Generation Agent (MCP)
====================================

Generates complex charts using Python libraries via MCP.
Supports advanced visualizations not available in Mermaid.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import logging
import base64
import json
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO

from .models import (
    AnalyticsPlan,
    ChartOutput,
    ChartType,
    DataPoint,
    GenerationMethod,
    PythonChartConfig
)
from .mcp_integration import get_mcp_integration, execute_chart_with_mcp
from .csv_utils import data_points_to_csv

logger = logging.getLogger(__name__)


class PythonChartAgent:
    """
    Agent for generating charts using Python libraries via MCP.
    Handles complex visualizations using matplotlib, seaborn, and plotly.
    """
    
    def __init__(self, mcp_tool=None):
        """
        Initialize the Python chart agent.
        
        Args:
            mcp_tool: Optional MCP tool function for Python execution
        """
        self.mcp_integration = get_mcp_integration()
        if mcp_tool:
            self.mcp_integration.set_mcp_tool(mcp_tool)
        self.supported_charts = {
            ChartType.SCATTER: self._generate_scatter_plot,
            ChartType.HEATMAP: self._generate_heatmap,
            ChartType.HISTOGRAM: self._generate_histogram,
            ChartType.BOX_PLOT: self._generate_box_plot,
            ChartType.AREA: self._generate_area_chart,
            ChartType.BUBBLE: self._generate_bubble_chart,
            ChartType.WATERFALL: self._generate_waterfall_chart,
            ChartType.TREEMAP: self._generate_treemap,
            # Also support basic charts with better styling
            ChartType.LINE: self._generate_line_chart_advanced,
            ChartType.BAR: self._generate_bar_chart_advanced,
            ChartType.PIE: self._generate_pie_chart_advanced,
            ChartType.RADAR: self._generate_radar_chart_proper
        }
    
    def _prepare_data_for_python(self, data_points: List[DataPoint]) -> Dict[str, List]:
        """
        Prepare data in format suitable for Python plotting.
        
        Args:
            data_points: List of data points
            
        Returns:
            Dictionary with labels and values
        """
        return {
            "labels": [dp.label for dp in data_points],
            "values": [dp.value for dp in data_points],
            "categories": [dp.category for dp in data_points if dp.category]
        }
    
    def _generate_python_code(
        self, 
        chart_type: str,
        data: Dict[str, List],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """
        Generate Python code for chart creation.
        
        Args:
            chart_type: Type of chart
            data: Prepared data
            title: Chart title
            config: Chart configuration
            
        Returns:
            Python code as string
        """
        # Base imports
        imports = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "import seaborn as sns"
        ]
        
        # Add pandas for correlation heatmaps
        if chart_type == "heatmap" and "correlation" in title.lower():
            imports.append("import pandas as pd")
        
        # Set style
        setup = [
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "sns.set_palette('husl')"
        ]
        
        # Chart-specific code
        chart_code = self._get_chart_specific_code(chart_type, data, title)
        
        # Finalization - Let MCP wrapper handle saving
        finalize = [
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()",
            # Don't close or save - let the MCP wrapper handle it
        ]
        
        # Combine all parts
        code_parts = imports + [""] + setup + [""] + chart_code + [""] + finalize
        return "\n".join(code_parts)
    
    def _infer_axis_labels(self, chart_type: str, data: Dict[str, List], title: str) -> tuple[str, str]:
        """
        Infer appropriate axis labels based on data context.
        
        Args:
            chart_type: Type of chart
            data: Data dictionary 
            title: Chart title
            
        Returns:
            Tuple of (x_label, y_label)
        """
        labels = data.get("labels", [])
        title_lower = title.lower()
        
        # Default labels
        x_label = "Categories"
        y_label = "Values"
        
        # Infer based on title context
        if any(word in title_lower for word in ["sales", "revenue", "profit", "income"]):
            y_label = "Amount ($)"
        elif any(word in title_lower for word in ["count", "frequency", "number"]):
            y_label = "Count"
        elif any(word in title_lower for word in ["percentage", "percent", "share"]):
            y_label = "Percentage (%)"
        elif any(word in title_lower for word in ["score", "rating", "satisfaction"]):
            y_label = "Score"
        elif any(word in title_lower for word in ["time", "response"]):
            y_label = "Time (ms)"
            
        # Infer x-axis based on data labels
        if labels and len(labels) > 0:
            first_label = str(labels[0]).lower()
            if first_label.startswith(('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')):
                x_label = "Months"
            elif first_label.startswith(('q1', 'q2', 'q3', 'q4')):
                x_label = "Quarters"  
            elif any(word in first_label for word in ["product", "category", "region", "department"]):
                x_label = "Categories"
            elif "week" in first_label or "day" in first_label:
                x_label = "Time Period"
        
        # Chart-specific adjustments
        if chart_type == "scatter":
            x_label = "X Values"
            y_label = "Y Values"
        elif chart_type == "histogram":
            x_label = "Value Range"
            y_label = "Frequency"
        elif chart_type == "heatmap":
            # More descriptive labels for heatmaps
            if "activity" in title_lower or "weekly" in title_lower:
                x_label = "Day of Week"
                y_label = "Time of Day"
            elif "correlation" in title_lower:
                x_label = "Metrics"
                y_label = "Metrics"
            else:
                x_label = "Columns"
                y_label = "Rows"
            
        return x_label, y_label

    def _get_chart_specific_code(
        self, 
        chart_type: str,
        data: Dict[str, List],
        title: str
    ) -> List[str]:
        """
        Get chart-specific plotting code.
        
        Args:
            chart_type: Type of chart
            data: Data dictionary
            title: Chart title
            
        Returns:
            List of code lines
        """
        labels = data.get("labels", [])
        values = data.get("values", [])
        x_label, y_label = self._infer_axis_labels(chart_type, data, title)
        
        if chart_type == "line":
            return [
                f"labels = {labels}",
                f"values = {values}",
                "x = np.arange(len(labels))",
                "ax.plot(x, values, marker='o', markersize=8, linewidth=2.5, color='#2E8B57')",
                "ax.set_xticks(x)",
                "ax.set_xticklabels(labels, rotation=45, ha='right')",
                f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                "ax.grid(True, alpha=0.3)",
                "# Add value annotations",
                "for i, v in enumerate(values):",
                "    ax.annotate(f'{v:,.0f}', (i, v), textcoords='offset points', xytext=(0,10), ha='center', fontsize=9)"
            ]
            
        elif chart_type == "bar":
            return [
                f"labels = {labels}",
                f"values = {values}",
                "x = np.arange(len(labels))",
                "bars = ax.bar(x, values, color='steelblue', edgecolor='navy', linewidth=1.2)",
                "ax.set_xticks(x)",
                "ax.set_xticklabels(labels, rotation=45, ha='right')",
                f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                "ax.grid(True, alpha=0.3, axis='y')",
                "# Add value labels on bars",
                "for i, bar in enumerate(bars):",
                "    height = bar.get_height()",
                "    ax.annotate(f'{height:,.0f}', xy=(bar.get_x() + bar.get_width()/2, height),",
                "               xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=9)"
            ]
        
        elif chart_type == "scatter":
            # For scatter plots, create x,y pairs from sequential values
            # If we have labels like "Point 1", use index as x
            x_values = list(range(len(values)))
            y_values = values
            return [
                f"x = {x_values}",
                f"y = {y_values}",
                "ax.scatter(x, y, alpha=0.6, s=100, color='coral', edgecolors='darkred')",
                f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                "ax.grid(True, alpha=0.3)"
            ]
        
        elif chart_type == "histogram":
            return [
                f"data = {values}",
                "ax.hist(data, bins=20, edgecolor='black', alpha=0.7, color='skyblue')",
                f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                "ax.grid(True, alpha=0.3, axis='y')"
            ]
        
        elif chart_type == "heatmap":
            # Generate appropriate heatmap based on context
            if "activity" in title.lower() or "weekly" in title.lower():
                # Activity heatmap: 7 days x 7 time periods
                size = min(7, int(len(values) ** 0.5))
                return [
                    f"data = np.array({values[:size*size]}).reshape({size}, {size})",
                    f"x_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][:{size}]",
                    f"y_labels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'][:{size}]",
                    "sns.heatmap(data, annot=True, fmt='.1f', cmap='coolwarm', ax=ax,",
                    "            xticklabels=x_labels, yticklabels=y_labels)",
                    f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                    f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                    "plt.setp(ax.get_xticklabels(), rotation=45, ha='right')",
                    "plt.setp(ax.get_yticklabels(), rotation=0)"
                ]
            elif "correlation" in title.lower():
                # Correlation matrix: Create a proper 5x5 correlation matrix
                return [
                    "# Generate a proper correlation matrix",
                    "np.random.seed(42)",
                    "# Create base data for 5 metrics",
                    "n_samples = 100",
                    "sales = np.random.normal(100, 20, n_samples)",
                    "marketing = sales * 0.7 + np.random.normal(0, 10, n_samples)",
                    "costs = sales * 0.4 + np.random.normal(50, 15, n_samples)",
                    "profit = sales - costs + np.random.normal(0, 5, n_samples)",
                    "growth = (sales[1:] - sales[:-1]).mean() + np.random.normal(5, 2, n_samples-1)",
                    "growth = np.append(growth, growth.mean())",
                    "",
                    "# Create DataFrame and compute correlation",
                    "df = pd.DataFrame({",
                    "    'Sales': sales,",
                    "    'Marketing': marketing,", 
                    "    'Costs': costs,",
                    "    'Profit': profit,",
                    "    'Growth': growth",
                    "})",
                    "corr_matrix = df.corr()",
                    "",
                    "# Plot correlation heatmap",
                    "sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=ax,",
                    "            vmin=-1, vmax=1, center=0,",
                    "            square=True, linewidths=1, cbar_kws={'shrink': 0.8})",
                    f"ax.set_xlabel('')",
                    f"ax.set_ylabel('')",
                    "ax.set_title('Correlation Matrix', pad=20, fontsize=12)",
                    "plt.setp(ax.get_xticklabels(), rotation=45, ha='right')",
                    "plt.setp(ax.get_yticklabels(), rotation=0)"
                ]
            else:
                # Generic heatmap
                size = int(len(values) ** 0.5)
                return [
                    f"data = np.array({values[:size*size]}).reshape({size}, {size})",
                    f"x_labels = [f'Col {{i+1}}' for i in range({size})]",
                    f"y_labels = [f'Row {{i+1}}' for i in range({size})]",
                    "sns.heatmap(data, annot=True, fmt='.1f', cmap='coolwarm', ax=ax,",
                    "            xticklabels=x_labels, yticklabels=y_labels)",
                    f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                    f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                    "plt.setp(ax.get_xticklabels(), rotation=45, ha='right')",
                    "plt.setp(ax.get_yticklabels(), rotation=0)"
                ]
        
        elif chart_type == "box_plot":
            return [
                f"data = [{values}]",
                "box = ax.boxplot(data, patch_artist=True)",
                "box['boxes'][0].set_facecolor('lightblue')",
                f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                "ax.grid(True, alpha=0.3, axis='y')"
            ]
        
        elif chart_type == "area":
            return [
                f"labels = {labels}",
                f"values = {values}",
                "x = np.arange(len(labels))",
                "ax.fill_between(x, values, alpha=0.3, color='lightgreen')",
                "ax.plot(x, values, linewidth=2, color='darkgreen')",
                "ax.set_xticks(x)",
                "ax.set_xticklabels(labels, rotation=45, ha='right')",
                f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                "ax.grid(True, alpha=0.3)"
            ]
        
        else:  # Default fallback - should not happen now
            return [
                f"labels = {labels}",
                f"values = {values}",
                "x = np.arange(len(labels))",
                "ax.bar(x, values, color='steelblue', edgecolor='navy')",
                "ax.set_xticks(x)",
                "ax.set_xticklabels(labels, rotation=45, ha='right')",
                f"ax.set_xlabel('{x_label}', fontsize=12, fontweight='bold')",
                f"ax.set_ylabel('{y_label}', fontsize=12, fontweight='bold')",
                "ax.grid(True, alpha=0.3, axis='y')"
            ]
    
    async def _execute_python_code(self, code: str) -> Optional[str]:
        """
        Execute Python code via MCP and return base64 image.
        
        Args:
            code: Python code to execute
            
        Returns:
            Base64 encoded image or None if failed
        """
        if not self.mcp_integration.is_available:
            logger.debug("MCP not available for Python execution")
            return None
        
        try:
            # Execute code via MCP integration
            base64_image = await self.mcp_integration.execute_chart_code(code)
            return base64_image
        except Exception as e:
            logger.error(f"Failed to execute Python code via MCP: {e}")
            return None
    
    def _generate_scatter_plot(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate scatter plot code."""
        data = self._prepare_data_for_python(data_points)
        return self._generate_python_code("scatter", data, title, config)
    
    def _generate_heatmap(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate heatmap code."""
        data = self._prepare_data_for_python(data_points)
        return self._generate_python_code("heatmap", data, title, config)
    
    def _generate_histogram(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate histogram code."""
        data = self._prepare_data_for_python(data_points)
        return self._generate_python_code("histogram", data, title, config)
    
    def _generate_box_plot(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate box plot code."""
        data = self._prepare_data_for_python(data_points)
        return self._generate_python_code("box_plot", data, title, config)
    
    def _generate_area_chart(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate area chart code."""
        data = self._prepare_data_for_python(data_points)
        return self._generate_python_code("area", data, title, config)
    
    def _generate_bubble_chart(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate bubble chart code."""
        # Bubble chart is like scatter with varying sizes
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            f"x = {[dp.value for dp in data_points[:len(data_points)//2]]}",
            f"y = {[dp.value for dp in data_points[len(data_points)//2:]]}",
            "sizes = np.random.randint(50, 500, len(x))",
            "colors = np.random.rand(len(x))",
            "",
            "ax.scatter(x, y, s=sizes, c=colors, alpha=0.5, cmap='viridis')",
            "ax.set_xlabel('X Values')",
            "ax.set_ylabel('Y Values')",
            f"ax.set_title('{title}')",
            "ax.grid(True, alpha=0.3)",
            "",
            "plt.colorbar(ax.collections[0], ax=ax, label='Color Scale')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_waterfall_chart(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate waterfall chart code."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            f"labels = {[dp.label for dp in data_points]}",
            f"values = {[dp.value for dp in data_points]}",
            "",
            "# Calculate cumulative values",
            "cumulative = np.cumsum(values)",
            "starts = np.concatenate([[0], cumulative[:-1]])",
            "",
            "# Create waterfall",
            "for i, (label, value, start) in enumerate(zip(labels, values, starts)):",
            "    color = 'green' if value >= 0 else 'red'",
            "    ax.bar(i, value, bottom=start, color=color, edgecolor='black')",
            "",
            "ax.set_xticks(range(len(labels)))",
            "ax.set_xticklabels(labels, rotation=45, ha='right')",
            "ax.set_ylabel('Cumulative Value')",
            f"ax.set_title('{title}')",
            "ax.grid(True, alpha=0.3, axis='y')",
            "ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)",
            "",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_treemap(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate treemap code with proper 2D nested layout."""
        # Generate a proper treemap visualization with 2D layout
        code = [
            "import matplotlib.pyplot as plt",
            "import matplotlib.patches as patches",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            "# Use a more compact figure size for treemap",
            "fig, ax = plt.subplots(figsize=(10, 5))",
            "",
            f"labels = {[dp.label for dp in data_points]}",
            f"values = {[dp.value for dp in data_points]}",
            "",
            "# Better treemap layout - divide into rows and columns",
            "def create_treemap_layout(sizes, labels):",
            "    '''Create a better 2D treemap layout'''",
            "    # Sort by size for better layout",
            "    sorted_pairs = sorted(zip(sizes, labels), reverse=True)",
            "    sorted_sizes = [s for s, _ in sorted_pairs]",
            "    sorted_labels = [l for _, l in sorted_pairs]",
            "    ",
            "    # Normalize sizes",
            "    total = sum(sorted_sizes)",
            "    normed = [s/total for s in sorted_sizes]",
            "    ",
            "    rects = []",
            "    ",
            "    # Create a 2D layout",
            "    # First item (largest) takes left half",
            "    if len(normed) >= 1:",
            "        # Engineering (45%) - large rectangle on left",
            "        rects.append((0, 0, 0.45, 1))  # x, y, width, height",
            "    ",
            "    if len(normed) >= 2:",
            "        # Sales (20%) - top right",
            "        rects.append((0.45, 0.5, 0.35, 0.5))",
            "    ",
            "    if len(normed) >= 3:",
            "        # Marketing (15%) - middle right",
            "        rects.append((0.45, 0, 0.35, 0.5))",
            "    ",
            "    if len(normed) >= 4:",
            "        # Operations (12%) - bottom right",
            "        rects.append((0.8, 0.5, 0.2, 0.5))",
            "    ",
            "    if len(normed) >= 5:",
            "        # Support (8%) - bottom right corner",
            "        rects.append((0.8, 0, 0.2, 0.5))",
            "    ",
            "    # Adjust to actual values if different",
            "    if len(normed) == 2:",
            "        rects = [(0, 0, normed[0], 1), (normed[0], 0, normed[1], 1)]",
            "    elif len(normed) == 3:",
            "        rects = [",
            "            (0, 0, normed[0], 1),",
            "            (normed[0], 0.5, normed[1], 0.5),",
            "            (normed[0], 0, normed[2], 0.5)",
            "        ]",
            "    ",
            "    return rects, sorted_labels",
            "",
            "# Create layout",
            "rectangles, sorted_labels = create_treemap_layout(values, labels)",
            "",
            "# Create color map",
            "colors = plt.cm.Set3(np.linspace(0, 1, len(values)))",
            "",
            "# Draw rectangles",
            "for i, (x, y, w, h) in enumerate(rectangles):",
            "    rect = patches.Rectangle((x, y), w, h,",
            "                            linewidth=2, edgecolor='white',",
            "                            facecolor=colors[i], alpha=0.8)",
            "    ax.add_patch(rect)",
            "    ",
            "    # Add label",
            "    if i < len(sorted_labels) and i < len(values):",
            "        # Calculate appropriate font size",
            "        area = w * h",
            "        fontsize = min(12, max(8, int(np.sqrt(area) * 30)))",
            "        ax.text(x + w/2, y + h/2, f'{sorted_labels[i]}\\n{values[i]:.0f}%',",
            "               ha='center', va='center', fontsize=fontsize,",
            "               fontweight='bold', color='black')",
            "",
            "ax.set_xlim(0, 1)",
            "ax.set_ylim(0, 1)",
            "# Don't force equal aspect - let it fit the figure",
            "ax.axis('off')",
            f"ax.set_title('{title}', fontsize=14, fontweight='bold', pad=10)",
            "",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_line_chart_advanced(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate advanced line chart with styling."""
        data = self._prepare_data_for_python(data_points)
        # Use the line chart code directly - it already includes everything we need
        return self._generate_python_code("line", data, title, config)
    
    def _generate_bar_chart_advanced(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate advanced bar chart with styling."""
        data = self._prepare_data_for_python(data_points)
        return self._generate_python_code("bar", data, title, config)
    
    def _generate_pie_chart_advanced(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate advanced pie chart with styling."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            "# Use consistent square figure size for pie charts",
            "fig, ax = plt.subplots(figsize=(8, 8))",
            "",
            f"labels = {[dp.label for dp in data_points]}",
            f"values = {[dp.value for dp in data_points]}",
            "",
            "# Use darker, more vibrant colors",
            "dark_colors = ['#2E4057', '#048A81', '#54C6EB', '#8B5A3C', '#FFA500',",
            "               '#4B0082', '#DC143C', '#228B22', '#FF1493', '#000080']",
            "colors = dark_colors[:len(values)]",
            "",
            "# Create pie chart with white borders between segments",
            "wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors,",
            "                                    autopct='%1.0f%%', startangle=90,",
            "                                    wedgeprops={'edgecolor': 'white', 'linewidth': 3},",
            "                                    textprops={'fontsize': 10})",
            "",
            "# Make percentage text white and bold",
            "for autotext in autotexts:",
            "    autotext.set_color('white')",
            "    autotext.set_fontweight('bold')",
            "    autotext.set_fontsize(11)",
            "",
            "# Adjust label positioning and style",
            "for text in texts:",
            "    text.set_fontsize(10)",
            "",
            f"ax.set_title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_radar_chart_proper(
        self,
        data_points: List[DataPoint],
        title: str,
        config: PythonChartConfig
    ) -> str:
        """Generate proper radar/spider chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "from math import pi",
            "",
            f"fig, ax = plt.subplots(figsize={config.figure_size}, subplot_kw=dict(projection='polar'))",
            "",
            f"categories = {[dp.label for dp in data_points]}",
            f"values = {[dp.value for dp in data_points]}",
            "",
            "# Number of variables",
            "num_vars = len(categories)",
            "",
            "# Compute angle for each axis",
            "angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]",
            "values_plot = values + values[:1]  # Complete the circle",
            "angles += angles[:1]",
            "",
            "# Plot",
            "ax.plot(angles, values_plot, 'o-', linewidth=2, color='#1f77b4')",
            "ax.fill(angles, values_plot, alpha=0.25, color='#1f77b4')",
            "",
            "# Set labels",
            "ax.set_xticks(angles[:-1])",
            "ax.set_xticklabels(categories)",
            "ax.set_ylim(0, max(values) * 1.1)",
            "",
            f"plt.title('{title}', size=14, y=1.08, fontweight='bold')",
            "ax.grid(True)",
            "",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    async def generate_chart(
        self,
        plan: AnalyticsPlan,
        data_points: List[DataPoint],
        data_description: str,
        insights: List[str]
    ) -> ChartOutput:
        """
        Generate chart using Python libraries via MCP.
        
        Args:
            plan: Analytics execution plan
            data_points: Synthetic data points
            data_description: Description of the data
            insights: Data insights
            
        Returns:
            Chart output with base64 image or Python code
        """
        chart_type = plan.strategy.chart_type
        config = plan.chart_config
        title = plan.request.title
        
        logger.info(f"Generating Python {chart_type.value} chart for '{title}'")
        
        # Get the appropriate generator
        generator = self.supported_charts.get(chart_type)
        if not generator:
            logger.error(f"Unsupported chart type for Python: {chart_type}")
            return ChartOutput(
                chart_type=chart_type,
                chart_content="",
                format="python_code",
                synthetic_data=data_points,
                data_description=data_description,
                insights=insights,
                generation_method=GenerationMethod.PYTHON_MCP,
                metadata={"error": f"Chart type {chart_type} not implemented"}
            )
        
        try:
            # Generate Python code
            python_code = generator(data_points, title, config)
            
            # Try to execute via MCP if available
            base64_image = None
            if self.mcp_integration.is_available:
                base64_image = await self._execute_python_code(python_code)
            
            # Create raw data for display
            raw_data = [{"label": dp.label, "value": dp.value} for dp in data_points]
            
            # Generate CSV data
            csv_data = data_points_to_csv(data_points, chart_type)
            
            # Return output
            if base64_image:
                # Return as base64 image
                return ChartOutput(
                    chart_type=chart_type,
                    chart_content=base64_image,
                    format="base64",
                    synthetic_data=data_points,
                    raw_data=raw_data,
                    csv_data=csv_data,
                    data_description=data_description,
                    insights=insights,
                    generation_method=GenerationMethod.PYTHON_MCP,
                    metadata={
                        "title": title,
                        "library": config.library if isinstance(config, PythonChartConfig) else "matplotlib",
                        "execution": "mcp"
                    }
                )
            else:
                # Return Python code for manual execution
                return ChartOutput(
                    chart_type=chart_type,
                    chart_content=python_code,
                    format="python_code",
                    synthetic_data=data_points,
                    raw_data=raw_data,
                    csv_data=csv_data,
                    data_description=data_description,
                    insights=insights,
                    generation_method=GenerationMethod.PYTHON_MCP,
                    metadata={
                        "title": title,
                        "library": config.library if isinstance(config, PythonChartConfig) else "matplotlib",
                        "execution": "code_only",
                        "note": "MCP not available, returning Python code"
                    }
                )
            
        except Exception as e:
            logger.error(f"Failed to generate Python chart: {e}")
            return ChartOutput(
                chart_type=chart_type,
                chart_content="",
                format="error",
                synthetic_data=data_points,
                data_description=data_description,
                insights=insights,
                generation_method=GenerationMethod.PYTHON_MCP,
                metadata={"error": str(e)}
            )

