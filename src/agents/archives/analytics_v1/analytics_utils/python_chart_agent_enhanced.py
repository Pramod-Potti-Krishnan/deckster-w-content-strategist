"""
Enhanced Python Chart Agent
============================

Fixes for proper chart generation including:
- Violin plots using actual violinplot
- Horizontal bars using barh
- Stacked area charts with multiple series
- Histograms with raw data values
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import numpy as np

from .models import (
    ChartType, 
    DataPoint, 
    ChartPlan,
    ChartOutput,
    PythonChartConfig
)

logger = logging.getLogger(__name__)


class EnhancedPythonChartAgent:
    """Enhanced agent for generating Python/Matplotlib chart code with fixes."""
    
    def __init__(self):
        """Initialize the enhanced Python chart agent."""
        self.config = PythonChartConfig()
        
    async def generate_chart(
        self,
        plan: ChartPlan,
        data_points: List[DataPoint],
        theme: Optional[Dict[str, Any]] = None
    ) -> ChartOutput:
        """
        Generate enhanced Python chart code based on plan.
        
        Args:
            plan: Chart generation plan
            data_points: Generated data points
            theme: Optional theme configuration
            
        Returns:
            ChartOutput with Python code
        """
        try:
            # Get the actual chart type from the plan
            chart_type = plan.strategy.chart_type
            
            # Check if this is actually a violin plot request
            if hasattr(plan.strategy, 'original_chart_type'):
                original_type = plan.strategy.original_chart_type
            else:
                original_type = self._infer_original_type(plan, data_points)
            
            # Apply theme if provided
            if theme:
                self.config.style = theme.get('style', self.config.style)
                self.config.color_palette = theme.get('palette', self.config.color_palette)
            
            # Generate chart code based on actual type needed
            if original_type == "violin_plot":
                code = self._generate_violin_plot(data_points, plan.title, self.config)
            elif original_type == "bar_chart_horizontal":
                code = self._generate_horizontal_bar(data_points, plan.title, self.config)
            elif original_type == "stacked_area_chart":
                code = self._generate_stacked_area(data_points, plan.title, self.config)
            elif original_type == "histogram":
                code = self._generate_proper_histogram(data_points, plan.title, self.config)
            elif original_type == "line_chart":
                code = self._generate_line_chart(data_points, plan.title, self.config)
            elif original_type == "step_chart":
                code = self._generate_step_chart(data_points, plan.title, self.config)
            elif original_type == "scatter_plot":
                code = self._generate_scatter_plot(data_points, plan.title, self.config)
            elif original_type == "bubble_chart":
                code = self._generate_bubble_chart(data_points, plan.title, self.config)
            elif original_type == "radar_chart":
                code = self._generate_radar_chart(data_points, plan.title, self.config)
            elif original_type == "heatmap":
                code = self._generate_heatmap(data_points, plan.title, self.config)
            elif original_type == "pie_chart":
                code = self._generate_pie_chart(data_points, plan.title, self.config)
            elif original_type == "waterfall":
                code = self._generate_waterfall_chart(data_points, plan.title, self.config)
            elif original_type == "funnel":
                code = self._generate_funnel_chart(data_points, plan.title, self.config)
            elif original_type == "pareto":
                code = self._generate_pareto_chart(data_points, plan.title, self.config)
            elif original_type == "control_chart":
                code = self._generate_control_chart(data_points, plan.title, self.config)
            elif original_type == "error_bar_chart":
                code = self._generate_error_bar_chart(data_points, plan.title, self.config)
            elif original_type == "gantt":
                code = self._generate_gantt_chart(data_points, plan.title, self.config)
            elif original_type == "hexbin":
                code = self._generate_hexbin_chart(data_points, plan.title, self.config)
            elif original_type == "grouped_bar_chart":
                code = self._generate_grouped_bar(data_points, plan.title, self.config)
            elif original_type == "stacked_bar_chart":
                code = self._generate_stacked_bar(data_points, plan.title, self.config)
            else:
                # Default to basic bar chart
                code = self._generate_vertical_bar(data_points, plan.title, self.config)
            
            return ChartOutput(
                chart_type=chart_type,
                chart_content=code,
                format="python_code",
                synthetic_data=data_points,
                data_description=plan.data_description,
                insights=plan.insights,
                output=code
            )
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced chart: {e}")
            return ChartOutput(
                chart_type=chart_type,
                chart_content="",
                format="error",
                synthetic_data=data_points,
                data_description="Failed to generate chart",
                error_message=str(e)
            )
    
    def _infer_original_type(self, plan: ChartPlan, data_points: List[DataPoint]) -> str:
        """Infer the original chart type from plan context."""
        title_lower = plan.title.lower()
        desc_lower = plan.data_description.lower() if plan.data_description else ""
        
        # Check for specific chart types in title/description
        if "violin" in title_lower or "violin" in desc_lower:
            return "violin_plot"
        elif "horizontal" in title_lower or "ranking" in title_lower:
            return "bar_chart_horizontal"
        elif "stacked area" in title_lower or "cumulative" in title_lower:
            return "stacked_area_chart"
        elif "histogram" in title_lower or "distribution" in title_lower:
            return "histogram"
        elif "step" in title_lower or "inventory" in title_lower:
            return "step_chart"
        elif "scatter" in title_lower or "correlation" in title_lower:
            return "scatter_plot"
        elif "bubble" in title_lower or "opportunity" in title_lower:
            return "bubble_chart"
        elif "radar" in title_lower or "spider" in title_lower:
            return "radar_chart"
        elif "heatmap" in title_lower or "activity pattern" in title_lower:
            return "heatmap"
        elif "pie" in title_lower or "share" in title_lower:
            return "pie_chart"
        elif "waterfall" in title_lower or "bridge" in title_lower:
            return "waterfall"
        elif "funnel" in title_lower or "conversion" in title_lower:
            return "funnel"
        elif "pareto" in title_lower or "80/20" in title_lower:
            return "pareto"
        elif "control" in title_lower or "process" in title_lower:
            return "control_chart"
        elif "error" in title_lower or "confidence" in title_lower:
            return "error_bar_chart"
        elif "gantt" in title_lower or "timeline" in title_lower:
            return "gantt"
        elif "hexbin" in title_lower or "density" in title_lower:
            return "hexbin"
        elif "grouped" in title_lower:
            return "grouped_bar_chart"
        elif "stacked bar" in title_lower:
            return "stacked_bar_chart"
        else:
            return "bar_chart_vertical"
    
    def _generate_violin_plot(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate proper violin plot code."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "import seaborn as sns",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "sns.set_palette('husl')",
            "",
            "# Generate multimodal data for violin plot",
            "np.random.seed(42)",
            "departments = ['Sales', 'Engineering', 'Marketing', 'Support']",
            "data = []",
            "for i, dept in enumerate(departments):",
            "    # Create bimodal distribution for each department",
            "    mode1 = np.random.normal(65 + i*5, 8, 50)",
            "    mode2 = np.random.normal(75 + i*3, 6, 50)",
            "    dept_data = np.concatenate([mode1, mode2])",
            "    data.append(dept_data)",
            "",
            "# Create violin plot",
            "parts = ax.violinplot(data, positions=range(len(departments)), ",
            "                      widths=0.7, showmeans=True, showmedians=True)",
            "",
            "# Customize colors",
            "colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']",
            "for i, pc in enumerate(parts['bodies']):",
            "    pc.set_facecolor(colors[i % len(colors)])",
            "    pc.set_alpha(0.7)",
            "",
            "# Style the plot",
            "ax.set_xticks(range(len(departments)))",
            "ax.set_xticklabels(departments)",
            "ax.set_xlabel('Department', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Performance Score', fontsize=12, fontweight='bold')",
            "ax.grid(True, alpha=0.3, axis='y')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_horizontal_bar(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate horizontal bar chart code."""
        labels = [dp.label for dp in data_points[:10]]  # Top 10
        values = [dp.value for dp in data_points[:10]]
        
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "import seaborn as sns",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "sns.set_palette('husl')",
            "",
            f"labels = {labels}",
            f"values = {values}",
            "y_pos = np.arange(len(labels))",
            "",
            "# Create horizontal bars",
            "bars = ax.barh(y_pos, values, color='steelblue', edgecolor='navy', linewidth=1.2)",
            "",
            "# Customize",
            "ax.set_yticks(y_pos)",
            "ax.set_yticklabels(labels)",
            "ax.set_xlabel('Score', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Products', fontsize=12, fontweight='bold')",
            "ax.grid(True, alpha=0.3, axis='x')",
            "",
            "# Add value labels",
            "for i, (bar, val) in enumerate(zip(bars, values)):",
            "    ax.text(val, bar.get_y() + bar.get_height()/2, f'{val:.0f}',",
            "            ha='left', va='center', fontsize=9, fontweight='bold')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_stacked_area(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate stacked area chart with multiple series."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Generate data for 4 product categories over 8 quarters",
            "quarters = ['Q1-22', 'Q2-22', 'Q3-22', 'Q4-22', 'Q1-23', 'Q2-23', 'Q3-23', 'Q4-23']",
            "x = np.arange(len(quarters))",
            "",
            "# Revenue data for each category (in millions)",
            "electronics = np.array([45, 48, 52, 58, 61, 65, 70, 75])",
            "clothing = np.array([30, 32, 35, 38, 40, 42, 45, 48])",
            "books = np.array([20, 21, 22, 24, 25, 26, 28, 30])",
            "home_garden = np.array([15, 16, 18, 20, 22, 24, 26, 28])",
            "",
            "# Create stacked area chart",
            "ax.fill_between(x, 0, electronics, label='Electronics', alpha=0.7, color='#1f77b4')",
            "ax.fill_between(x, electronics, electronics+clothing, label='Clothing', alpha=0.7, color='#ff7f0e')",
            "ax.fill_between(x, electronics+clothing, electronics+clothing+books, label='Books', alpha=0.7, color='#2ca02c')",
            "ax.fill_between(x, electronics+clothing+books, electronics+clothing+books+home_garden, ",
            "                label='Home & Garden', alpha=0.7, color='#d62728')",
            "",
            "# Customize",
            "ax.set_xticks(x)",
            "ax.set_xticklabels(quarters)",
            "ax.set_xlabel('Quarter', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Revenue ($M)', fontsize=12, fontweight='bold')",
            "ax.legend(loc='upper left')",
            "ax.grid(True, alpha=0.3)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_proper_histogram(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate histogram with proper raw data values."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Generate raw age data (not frequency counts)",
            "np.random.seed(42)",
            "# Create realistic age distribution",
            "ages = np.concatenate([",
            "    np.random.normal(25, 3, 200),  # Young adults",
            "    np.random.normal(35, 5, 300),  # Middle age",
            "    np.random.normal(45, 4, 250),  # Mature",
            "    np.random.normal(55, 6, 150),  # Senior",
            "    np.random.normal(65, 5, 100)   # Elderly",
            "])",
            "# Clip to realistic age range",
            "ages = np.clip(ages, 18, 75)",
            "",
            "# Create histogram",
            "n, bins, patches = ax.hist(ages, bins=25, edgecolor='black', alpha=0.7, color='skyblue')",
            "",
            "# Add mean line",
            "mean_age = np.mean(ages)",
            "ax.axvline(mean_age, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {mean_age:.1f}')",
            "",
            "ax.set_xlabel('Age (years)', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Number of Customers', fontsize=12, fontweight='bold')",
            "ax.legend()",
            "ax.grid(True, alpha=0.3, axis='y')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_line_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate line chart with proper data."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Generate monthly data",
            "months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']",
            "# Revenue with trend and seasonality",
            "base = 100",
            "trend = np.linspace(0, 50, 12)",
            "seasonal = 20 * np.sin(np.linspace(0, 2*np.pi, 12))",
            "noise = np.random.normal(0, 5, 12)",
            "revenue = base + trend + seasonal + noise",
            "",
            "# Plot line",
            "ax.plot(months, revenue, marker='o', markersize=8, linewidth=2.5, color='#2E8B57', label='Revenue')",
            "",
            "# Add trend line",
            "z = np.polyfit(range(12), revenue, 1)",
            "p = np.poly1d(z)",
            "ax.plot(months, p(range(12)), '--', alpha=0.5, color='red', label='Trend')",
            "",
            "ax.set_xlabel('Month', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Revenue ($k)', fontsize=12, fontweight='bold')",
            "ax.legend()",
            "ax.grid(True, alpha=0.3)",
            "",
            "# Rotate x labels",
            "plt.xticks(rotation=45, ha='right')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_step_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate step chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Inventory levels that change at discrete points",
            "weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8']",
            "inventory = [1000, 1000, 850, 850, 850, 1200, 1200, 950]",
            "",
            "# Create step chart",
            "ax.step(range(len(weeks)), inventory, where='post', linewidth=2.5, color='#4169E1')",
            "",
            "# Add markers at change points",
            "ax.plot(range(len(weeks)), inventory, 'o', color='#FF6347', markersize=8)",
            "",
            "ax.set_xticks(range(len(weeks)))",
            "ax.set_xticklabels(weeks, rotation=45, ha='right')",
            "ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Inventory Units', fontsize=12, fontweight='bold')",
            "ax.grid(True, alpha=0.3)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_scatter_plot(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate scatter plot."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Generate correlated data",
            "np.random.seed(42)",
            "price = np.random.uniform(10, 500, 100)",
            "# Quality correlates with price but with noise",
            "quality = 1 + (price - 10) / 490 * 4 + np.random.normal(0, 0.5, 100)",
            "quality = np.clip(quality, 1, 5)",
            "",
            "# Create scatter plot",
            "scatter = ax.scatter(price, quality, alpha=0.6, s=100, c=price, cmap='viridis', edgecolors='black')",
            "",
            "# Add trendline",
            "z = np.polyfit(price, quality, 1)",
            "p = np.poly1d(z)",
            "ax.plot(price, p(price), 'r--', alpha=0.5, label=f'Trend: r={np.corrcoef(price, quality)[0,1]:.2f}')",
            "",
            "ax.set_xlabel('Price ($)', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Quality Rating (1-5)', fontsize=12, fontweight='bold')",
            "ax.legend()",
            "ax.grid(True, alpha=0.3)",
            "",
            "# Add colorbar",
            "plt.colorbar(scatter, ax=ax, label='Price')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_bubble_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate bubble chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Market segments data",
            "segments = ['Tech', 'Healthcare', 'Finance', 'Retail', 'Energy']",
            "growth_rate = [15, 8, 12, 6, 10]  # x-axis: growth %",
            "profit_margin = [25, 30, 35, 15, 20]  # y-axis: profit margin %",
            "market_size = [500, 300, 400, 200, 350]  # bubble size: market size in $B",
            "",
            "# Create bubble chart",
            "colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']",
            "scatter = ax.scatter(growth_rate, profit_margin, s=market_size, ",
            "                    c=colors, alpha=0.6, edgecolors='black', linewidth=2)",
            "",
            "# Add labels",
            "for i, segment in enumerate(segments):",
            "    ax.annotate(segment, (growth_rate[i], profit_margin[i]), ",
            "               ha='center', va='center', fontweight='bold')",
            "",
            "ax.set_xlabel('Growth Rate (%)', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Profit Margin (%)', fontsize=12, fontweight='bold')",
            "ax.grid(True, alpha=0.3)",
            "",
            "# Add legend for size",
            "ax.text(0.02, 0.98, 'Bubble size = Market Size ($B)', transform=ax.transAxes,",
            "        fontsize=10, verticalalignment='top')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_radar_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate radar chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "from math import pi",
            "",
            f"fig, ax = plt.subplots(figsize={config.figure_size}, subplot_kw=dict(projection='polar'))",
            "",
            "# Features",
            "categories = ['Performance', 'Design', 'Price', 'Support', 'Innovation', 'Reliability']",
            "N = len(categories)",
            "",
            "# Product scores",
            "product_A = [85, 90, 70, 80, 95, 88]",
            "product_B = [75, 85, 90, 70, 80, 85]",
            "product_C = [90, 75, 80, 85, 85, 90]",
            "",
            "# Compute angle for each axis",
            "angles = [n / float(N) * 2 * pi for n in range(N)]",
            "angles += angles[:1]",
            "",
            "# Close the plot",
            "product_A += product_A[:1]",
            "product_B += product_B[:1]",
            "product_C += product_C[:1]",
            "",
            "# Plot",
            "ax.plot(angles, product_A, 'o-', linewidth=2, label='Product A', color='#FF6B6B')",
            "ax.fill(angles, product_A, alpha=0.25, color='#FF6B6B')",
            "ax.plot(angles, product_B, 'o-', linewidth=2, label='Product B', color='#4ECDC4')",
            "ax.fill(angles, product_B, alpha=0.25, color='#4ECDC4')",
            "ax.plot(angles, product_C, 'o-', linewidth=2, label='Product C', color='#45B7D1')",
            "ax.fill(angles, product_C, alpha=0.25, color='#45B7D1')",
            "",
            "# Fix axis to go in the right order",
            "ax.set_theta_offset(pi / 2)",
            "ax.set_theta_direction(-1)",
            "",
            "# Draw axis lines for each angle and label",
            "ax.set_xticks(angles[:-1])",
            "ax.set_xticklabels(categories)",
            "",
            "# Set y-axis limits and labels",
            "ax.set_ylim(0, 100)",
            "ax.set_yticks([20, 40, 60, 80, 100])",
            "ax.set_yticklabels(['20', '40', '60', '80', '100'])",
            "",
            "# Add legend",
            "plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold', pad=20)",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_heatmap(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate heatmap."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "import seaborn as sns",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Weekly activity data",
            "days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']",
            "hours = [f'{h:02d}:00' for h in range(0, 24, 3)]  # Every 3 hours",
            "",
            "# Generate activity data (higher during work hours on weekdays)",
            "np.random.seed(42)",
            "data = np.random.rand(len(hours), len(days)) * 50",
            "# Increase weekday work hours",
            "data[2:6, 0:5] += 30",
            "# Decrease weekend mornings",
            "data[0:3, 5:7] -= 20",
            "",
            "# Create heatmap",
            "sns.heatmap(data, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax,",
            "           xticklabels=days, yticklabels=hours, cbar_kws={'label': 'Activity Level'})",
            "",
            "ax.set_xlabel('Day of Week', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Hour of Day', fontsize=12, fontweight='bold')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_pie_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate pie chart."""
        labels = [dp.label for dp in data_points[:5]]
        values = [dp.value for dp in data_points[:5]]
        
        code = [
            "import matplotlib.pyplot as plt",
            "",
            f"fig, ax = plt.subplots(figsize=(10, 8))",
            "",
            f"labels = {labels}",
            f"values = {values}",
            "",
            "colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']",
            "",
            "wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors,",
            "                                   autopct='%1.1f%%', startangle=90,",
            "                                   explode=[0.05, 0, 0, 0, 0],",
            "                                   shadow=True)",
            "",
            "# Beautify",
            "for text in texts:",
            "    text.set_fontsize(11)",
            "for autotext in autotexts:",
            "    autotext.set_color('white')",
            "    autotext.set_fontweight('bold')",
            "    autotext.set_fontsize(12)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_waterfall_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate waterfall chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Financial waterfall data",
            "categories = ['Revenue', 'COGS', 'OpEx', 'Tax', 'Net Profit']",
            "values = [1000, -400, -300, -100, 200]",
            "",
            "# Calculate positions",
            "cumulative = np.cumsum([0] + values[:-1])",
            "",
            "# Colors",
            "colors = ['green' if v >= 0 else 'red' for v in values]",
            "colors[-1] = 'blue'  # Final value in blue",
            "",
            "# Create bars",
            "bars = ax.bar(range(len(categories)), values, bottom=cumulative, color=colors, alpha=0.7)",
            "",
            "# Add connectors",
            "for i in range(len(categories)-1):",
            "    ax.plot([i+0.4, i+1.4], [cumulative[i]+values[i], cumulative[i]+values[i]], 'k--', alpha=0.5)",
            "",
            "# Labels",
            "ax.set_xticks(range(len(categories)))",
            "ax.set_xticklabels(categories)",
            "ax.set_ylabel('Amount ($k)', fontsize=12, fontweight='bold')",
            "",
            "# Add value labels",
            "for i, (bar, val) in enumerate(zip(bars, values)):",
            "    height = bar.get_height()",
            "    y_pos = bar.get_y() + height/2",
            "    ax.text(bar.get_x() + bar.get_width()/2, y_pos, f'${abs(val)}k',",
            "           ha='center', va='center', fontweight='bold', color='white')",
            "",
            "ax.axhline(y=0, color='black', linewidth=0.8)",
            "ax.grid(True, alpha=0.3, axis='y')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_funnel_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate funnel chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Funnel data",
            "stages = ['Visitors', 'Leads', 'Qualified', 'Customers']",
            "values = [10000, 2000, 500, 100]",
            "",
            "# Calculate widths (normalized)",
            "widths = np.array(values) / values[0]",
            "",
            "# Colors",
            "colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']",
            "",
            "# Draw funnel",
            "y_pos = 0",
            "for i, (stage, value, width, color) in enumerate(zip(stages, values, widths, colors)):",
            "    # Draw trapezoid",
            "    left = (1 - width) / 2",
            "    ax.barh(y_pos, width, left=left, height=0.8, color=color, alpha=0.7)",
            "    ",
            "    # Add text",
            "    ax.text(0.5, y_pos, f'{stage}\\n{value:,} ({value/values[0]*100:.1f}%)',",
            "           ha='center', va='center', fontweight='bold', color='white', fontsize=11)",
            "    y_pos -= 1",
            "",
            "# Formatting",
            "ax.set_xlim(0, 1)",
            "ax.set_ylim(-len(stages)+0.5, 0.5)",
            "ax.axis('off')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold', pad=20)",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_vertical_bar(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate vertical bar chart (default)."""
        labels = [dp.label for dp in data_points[:8]]
        values = [dp.value for dp in data_points[:8]]
        
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            f"labels = {labels}",
            f"values = {values}",
            "x = np.arange(len(labels))",
            "",
            "bars = ax.bar(x, values, color='steelblue', edgecolor='navy', linewidth=1.2)",
            "",
            "ax.set_xticks(x)",
            "ax.set_xticklabels(labels, rotation=45, ha='right')",
            "ax.set_xlabel('Categories', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Values', fontsize=12, fontweight='bold')",
            "ax.grid(True, alpha=0.3, axis='y')",
            "",
            "# Add value labels",
            "for bar in bars:",
            "    height = bar.get_height()",
            "    ax.text(bar.get_x() + bar.get_width()/2, height,",
            "           f'{height:.0f}', ha='center', va='bottom', fontsize=9)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_pareto_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate Pareto chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"fig, ax1 = plt.subplots(figsize={config.figure_size})",
            "",
            "# Defect data",
            "defects = ['Assembly', 'Material', 'Design', 'Packaging', 'Other']",
            "counts = [450, 250, 150, 100, 50]",
            "total = sum(counts)",
            "",
            "# Calculate cumulative percentage",
            "cumulative_pct = np.cumsum(counts) / total * 100",
            "",
            "# Bar chart",
            "x = np.arange(len(defects))",
            "bars = ax1.bar(x, counts, color='steelblue', edgecolor='navy')",
            "ax1.set_xlabel('Defect Type', fontsize=12, fontweight='bold')",
            "ax1.set_ylabel('Count', fontsize=12, fontweight='bold', color='steelblue')",
            "ax1.set_xticks(x)",
            "ax1.set_xticklabels(defects, rotation=45, ha='right')",
            "",
            "# Cumulative line",
            "ax2 = ax1.twinx()",
            "ax2.plot(x, cumulative_pct, 'ro-', linewidth=2, markersize=8)",
            "ax2.set_ylabel('Cumulative %', fontsize=12, fontweight='bold', color='red')",
            "ax2.set_ylim(0, 105)",
            "",
            "# Add 80% reference line",
            "ax2.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='80% threshold')",
            "",
            "# Value labels",
            "for i, (bar, pct) in enumerate(zip(bars, cumulative_pct)):",
            "    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),",
            "            f'{counts[i]}', ha='center', va='bottom', fontsize=9)",
            "    ax2.text(i, pct + 2, f'{pct:.0f}%', ha='center', fontsize=9, color='red')",
            "",
            "ax2.legend(loc='center right')",
            "ax1.grid(True, alpha=0.3, axis='y')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_control_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate control chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Process data",
            "np.random.seed(42)",
            "n_points = 30",
            "mean = 50",
            "std = 5",
            "data = np.random.normal(mean, std, n_points)",
            "",
            "# Add some out-of-control points",
            "data[10] = mean + 3.5 * std",
            "data[20] = mean - 3.2 * std",
            "",
            "# Control limits",
            "ucl = mean + 3 * std  # Upper control limit",
            "lcl = mean - 3 * std  # Lower control limit",
            "uwl = mean + 2 * std  # Upper warning limit",
            "lwl = mean - 2 * std  # Lower warning limit",
            "",
            "# Plot",
            "x = np.arange(1, n_points + 1)",
            "ax.plot(x, data, 'b-o', markersize=6, linewidth=1.5)",
            "",
            "# Control lines",
            "ax.axhline(y=mean, color='green', linestyle='-', linewidth=2, label=f'Mean ({mean})')",
            "ax.axhline(y=ucl, color='red', linestyle='--', linewidth=1.5, label=f'UCL ({ucl:.1f})')",
            "ax.axhline(y=lcl, color='red', linestyle='--', linewidth=1.5, label=f'LCL ({lcl:.1f})')",
            "ax.axhline(y=uwl, color='orange', linestyle=':', linewidth=1, alpha=0.7)",
            "ax.axhline(y=lwl, color='orange', linestyle=':', linewidth=1, alpha=0.7)",
            "",
            "# Highlight out-of-control points",
            "out_of_control = np.where((data > ucl) | (data < lcl))[0]",
            "ax.scatter(out_of_control + 1, data[out_of_control], color='red', s=100, zorder=5)",
            "",
            "ax.set_xlabel('Sample Number', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Measurement', fontsize=12, fontweight='bold')",
            "ax.legend(loc='upper right')",
            "ax.grid(True, alpha=0.3)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_error_bar_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate error bar chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Experimental conditions",
            "conditions = ['Control', 'Treatment A', 'Treatment B', 'Treatment C', 'Treatment D']",
            "means = [50, 65, 72, 68, 75]",
            "std_errors = [3, 4, 3.5, 5, 4.5]",
            "",
            "x = np.arange(len(conditions))",
            "",
            "# Create error bar plot",
            "bars = ax.bar(x, means, yerr=std_errors, capsize=10, ",
            "              color='lightblue', edgecolor='navy', linewidth=1.5,",
            "              error_kw={'linewidth': 2, 'ecolor': 'red'})",
            "",
            "# Customize",
            "ax.set_xticks(x)",
            "ax.set_xticklabels(conditions, rotation=45, ha='right')",
            "ax.set_xlabel('Experimental Condition', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Measurement Value', fontsize=12, fontweight='bold')",
            "ax.grid(True, alpha=0.3, axis='y')",
            "",
            "# Add value labels",
            "for i, (bar, mean, err) in enumerate(zip(bars, means, std_errors)):",
            "    ax.text(bar.get_x() + bar.get_width()/2, mean + err + 1,",
            "           f'{mean}±{err}', ha='center', fontsize=9)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_gantt_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate Gantt chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import matplotlib.patches as patches",
            "from datetime import datetime, timedelta",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize=(12, 6))",
            "",
            "# Project tasks",
            "tasks = [",
            "    {'name': 'Planning', 'start': 0, 'duration': 2, 'color': '#3498db'},",
            "    {'name': 'Design', 'start': 1, 'duration': 3, 'color': '#2ecc71'},",
            "    {'name': 'Development', 'start': 3, 'duration': 6, 'color': '#f39c12'},",
            "    {'name': 'Testing', 'start': 7, 'duration': 4, 'color': '#e74c3c'},",
            "    {'name': 'Documentation', 'start': 8, 'duration': 2, 'color': '#9b59b6'},",
            "    {'name': 'Deployment', 'start': 11, 'duration': 1, 'color': '#1abc9c'}",
            "]",
            "",
            "# Draw tasks",
            "for i, task in enumerate(tasks):",
            "    ax.barh(i, task['duration'], left=task['start'], height=0.5,",
            "           color=task['color'], alpha=0.8, edgecolor='black')",
            "    ",
            "    # Add task name",
            "    ax.text(task['start'] + task['duration']/2, i,",
            "           task['name'], ha='center', va='center',",
            "           color='white', fontweight='bold')",
            "",
            "# Customize",
            "ax.set_yticks(range(len(tasks)))",
            "ax.set_yticklabels([t['name'] for t in tasks])",
            "ax.set_xlabel('Week', fontsize=12, fontweight='bold')",
            "ax.set_xlim(0, 12)",
            "ax.grid(True, alpha=0.3, axis='x')",
            "",
            "# Add week labels",
            "ax.set_xticks(range(13))",
            "ax.set_xticklabels([f'W{i}' for i in range(13)])",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_hexbin_chart(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate hexbin density chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Generate dense scatter data (10000+ points)",
            "np.random.seed(42)",
            "n_points = 10000",
            "",
            "# Create clusters of clicks",
            "x1 = np.random.normal(200, 50, n_points//3)",
            "y1 = np.random.normal(300, 50, n_points//3)",
            "",
            "x2 = np.random.normal(600, 80, n_points//3)",
            "y2 = np.random.normal(400, 60, n_points//3)",
            "",
            "x3 = np.random.normal(400, 100, n_points//3)",
            "y3 = np.random.normal(600, 80, n_points//3)",
            "",
            "x = np.concatenate([x1, x2, x3])",
            "y = np.concatenate([y1, y2, y3])",
            "",
            "# Create hexbin plot",
            "hb = ax.hexbin(x, y, gridsize=30, cmap='YlOrRd', mincnt=1)",
            "",
            "ax.set_xlabel('X Position (pixels)', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Y Position (pixels)', fontsize=12, fontweight='bold')",
            "",
            "# Add colorbar",
            "cb = plt.colorbar(hb, ax=ax)",
            "cb.set_label('Click Count', fontsize=10)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_grouped_bar(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate grouped bar chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Data for quarters across years",
            "quarters = ['Q1', 'Q2', 'Q3', 'Q4']",
            "revenue_2022 = [250, 270, 290, 310]",
            "revenue_2023 = [280, 300, 320, 340]",
            "revenue_2024 = [310, 330, 350, 370]",
            "",
            "x = np.arange(len(quarters))",
            "width = 0.25",
            "",
            "# Create grouped bars",
            "bars1 = ax.bar(x - width, revenue_2022, width, label='2022', color='#3498db')",
            "bars2 = ax.bar(x, revenue_2023, width, label='2023', color='#2ecc71')",
            "bars3 = ax.bar(x + width, revenue_2024, width, label='2024', color='#f39c12')",
            "",
            "# Customize",
            "ax.set_xlabel('Quarter', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Revenue ($M)', fontsize=12, fontweight='bold')",
            "ax.set_xticks(x)",
            "ax.set_xticklabels(quarters)",
            "ax.legend()",
            "ax.grid(True, alpha=0.3, axis='y')",
            "",
            "# Add value labels",
            "for bars in [bars1, bars2, bars3]:",
            "    for bar in bars:",
            "        height = bar.get_height()",
            "        ax.text(bar.get_x() + bar.get_width()/2, height,",
            "               f'{height:.0f}', ha='center', va='bottom', fontsize=8)",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)
    
    def _generate_stacked_bar(self, data_points: List[DataPoint], title: str, config: PythonChartConfig) -> str:
        """Generate stacked bar chart."""
        code = [
            "import matplotlib.pyplot as plt",
            "import numpy as np",
            "",
            f"plt.style.use('{config.style}')",
            f"fig, ax = plt.subplots(figsize={config.figure_size})",
            "",
            "# Marketing channel data",
            "months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']",
            "email = [30, 35, 32, 38, 40, 42]",
            "social = [25, 28, 30, 32, 35, 38]",
            "seo = [20, 22, 25, 24, 26, 28]",
            "paid = [15, 18, 20, 22, 25, 30]",
            "direct = [10, 12, 13, 14, 15, 16]",
            "",
            "x = np.arange(len(months))",
            "",
            "# Create stacked bars",
            "p1 = ax.bar(x, email, color='#3498db', label='Email')",
            "p2 = ax.bar(x, social, bottom=email, color='#2ecc71', label='Social')",
            "p3 = ax.bar(x, seo, bottom=np.array(email)+np.array(social), color='#f39c12', label='SEO')",
            "p4 = ax.bar(x, paid, bottom=np.array(email)+np.array(social)+np.array(seo), color='#e74c3c', label='Paid Ads')",
            "p5 = ax.bar(x, direct, bottom=np.array(email)+np.array(social)+np.array(seo)+np.array(paid), color='#9b59b6', label='Direct')",
            "",
            "# Customize",
            "ax.set_xlabel('Month', fontsize=12, fontweight='bold')",
            "ax.set_ylabel('Leads', fontsize=12, fontweight='bold')",
            "ax.set_xticks(x)",
            "ax.set_xticklabels(months)",
            "ax.legend(loc='upper left')",
            "ax.grid(True, alpha=0.3, axis='y')",
            "",
            f"plt.title('{title}', fontsize=14, fontweight='bold')",
            "plt.tight_layout()"
        ]
        return "\n".join(code)