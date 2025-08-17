"""
Analytics Agent Models
======================

Data structures for the analytics generation pipeline.
Defines chart types, requests, outputs, and supporting models.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ChartType(str, Enum):
    """Supported chart types for analytics visualization."""
    # Mermaid-supported charts
    LINE = "line"
    BAR = "bar"
    RADAR = "radar"
    PIE = "pie"
    
    # Python/matplotlib charts
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    AREA = "area"
    BUBBLE = "bubble"
    WATERFALL = "waterfall"
    TREEMAP = "treemap"


class DataDimension(str, Enum):
    """Types of data dimensions for chart selection."""
    TEMPORAL = "temporal"          # Time-based data
    CATEGORICAL = "categorical"    # Categories/groups
    CONTINUOUS = "continuous"      # Numeric ranges
    HIERARCHICAL = "hierarchical"  # Nested structures
    CORRELATION = "correlation"    # Relationships
    DISTRIBUTION = "distribution"  # Statistical distribution


class GenerationMethod(str, Enum):
    """Available methods for chart generation."""
    MERMAID = "mermaid"
    PYTHON_MCP = "python_mcp"
    FALLBACK = "fallback"


class DataPoint(BaseModel):
    """Individual data point for charts."""
    label: str = Field(description="Label or category")
    value: Union[float, int] = Field(description="Numeric value")
    category: Optional[str] = Field(default=None, description="Optional grouping category")
    timestamp: Optional[datetime] = Field(default=None, description="Optional timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AnalyticsRequest(BaseModel):
    """Request structure for analytics generation."""
    title: str = Field(
        description="Chart title"
    )
    description: str = Field(
        description="Description of what to visualize"
    )
    data_context: str = Field(
        description="Context about what the data represents"
    )
    chart_preference: Optional[ChartType] = Field(
        default=None,
        description="Preferred chart type if specified"
    )
    dimensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Data dimensions (x-axis, y-axis, categories, etc.)"
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period for the data (e.g., 'Q1 2024', 'Last 12 months')"
    )
    data_range: Optional[Dict[str, float]] = Field(
        default=None,
        description="Expected data ranges for synthetic generation"
    )
    theme: Dict[str, Any] = Field(
        default_factory=dict,
        description="Visual theme and styling preferences"
    )
    comparison_type: Optional[str] = Field(
        default=None,
        description="Type of comparison (e.g., 'year-over-year', 'vs-target')"
    )
    
    @validator('dimensions')
    def validate_dimensions(cls, v):
        """Ensure dimensions have required fields."""
        if not v:
            v = {}
        # Provide defaults if not specified
        if 'x_axis' not in v:
            v['x_axis'] = {'label': 'X Axis', 'type': 'categorical'}
        if 'y_axis' not in v:
            v['y_axis'] = {'label': 'Y Axis', 'type': 'continuous'}
        return v


class SyntheticDataConfig(BaseModel):
    """Configuration for synthetic data generation."""
    num_points: int = Field(
        default=12,
        description="Number of data points to generate"
    )
    trend: Optional[Literal["increasing", "decreasing", "stable", "cyclic"]] = Field(
        default="stable",
        description="Overall trend pattern"
    )
    seasonality: bool = Field(
        default=False,
        description="Include seasonal patterns"
    )
    noise_level: float = Field(
        default=0.1,
        description="Amount of random variation (0-1)"
    )
    outliers: bool = Field(
        default=False,
        description="Include occasional outliers"
    )
    min_value: Optional[float] = Field(
        default=None,
        description="Minimum value constraint"
    )
    max_value: Optional[float] = Field(
        default=None,
        description="Maximum value constraint"
    )


class ChartOutput(BaseModel):
    """Output structure for generated charts."""
    chart_type: ChartType = Field(
        description="Type of chart generated"
    )
    chart_content: str = Field(
        description="Chart content (Mermaid code or base64 image)"
    )
    format: Literal["mermaid", "png", "svg", "base64", "python_code", "error"] = Field(
        description="Output format of the chart"
    )
    synthetic_data: List[DataPoint] = Field(
        description="Generated synthetic data points"
    )
    raw_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Raw data in simple format for display"
    )
    csv_data: Optional[str] = Field(
        default=None,
        description="Data in CSV format for export/display"
    )
    data_description: str = Field(
        description="Natural language description of the data"
    )
    insights: List[str] = Field(
        default_factory=list,
        description="Key insights from the data"
    )
    generation_method: GenerationMethod = Field(
        description="Method used to generate the chart"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about generation"
    )
    
    @validator('insights')
    def ensure_insights(cls, v, values):
        """Generate basic insights if none provided."""
        if not v and 'synthetic_data' in values:
            data = values['synthetic_data']
            if data:
                # Generate basic insights
                v = []
                values_list = [d.value for d in data]
                if values_list:
                    v.append(f"Average value: {sum(values_list)/len(values_list):.2f}")
                    v.append(f"Range: {min(values_list):.2f} to {max(values_list):.2f}")
        return v


class ChartStrategy(BaseModel):
    """Strategy selection for chart generation."""
    method: GenerationMethod = Field(
        description="Selected generation method"
    )
    chart_type: ChartType = Field(
        description="Selected chart type"
    )
    confidence: float = Field(
        description="Confidence in this strategy (0-1)",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        description="Explanation for the selection"
    )
    fallback_method: Optional[GenerationMethod] = Field(
        default=None,
        description="Fallback if primary fails"
    )
    fallback_chart: Optional[ChartType] = Field(
        default=None,
        description="Alternative chart type"
    )


class MermaidChartConfig(BaseModel):
    """Configuration specific to Mermaid chart generation."""
    chart_type: Literal["pie"] = Field(
        description="Mermaid chart syntax type"
    )
    theme: Optional[str] = Field(
        default="base",
        description="Mermaid theme"
    )
    orientation: Optional[Literal["horizontal", "vertical"]] = Field(
        default="vertical",
        description="Chart orientation"
    )
    show_legend: bool = Field(
        default=True,
        description="Display legend"
    )
    show_values: bool = Field(
        default=True,
        description="Show data values on chart"
    )
    color_scheme: List[str] = Field(
        default_factory=lambda: ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"],
        description="Color palette for the chart"
    )


class PythonChartConfig(BaseModel):
    """Configuration for Python/matplotlib chart generation."""
    library: Literal["matplotlib", "seaborn", "plotly"] = Field(
        default="matplotlib",
        description="Python library to use"
    )
    figure_size: tuple[int, int] = Field(
        default=(10, 6),
        description="Figure dimensions in inches"
    )
    dpi: int = Field(
        default=100,
        description="Resolution in dots per inch"
    )
    style: Optional[str] = Field(
        default="seaborn-v0_8",
        description="Matplotlib style"
    )
    color_palette: Optional[str] = Field(
        default="husl",
        description="Color palette name"
    )
    export_format: Literal["png", "svg", "pdf"] = Field(
        default="png",
        description="Export format"
    )


class AnalyticsPlan(BaseModel):
    """Execution plan for analytics generation."""
    request: AnalyticsRequest = Field(
        description="Original request"
    )
    strategy: ChartStrategy = Field(
        description="Selected generation strategy"
    )
    data_config: SyntheticDataConfig = Field(
        description="Configuration for data synthesis"
    )
    chart_config: Union[MermaidChartConfig, PythonChartConfig] = Field(
        description="Chart-specific configuration"
    )
    estimated_complexity: Literal["simple", "moderate", "complex"] = Field(
        description="Estimated complexity of the visualization"
    )


class DataInsight(BaseModel):
    """Individual insight from data analysis."""
    type: Literal["trend", "outlier", "comparison", "correlation", "distribution"] = Field(
        description="Type of insight"
    )
    description: str = Field(
        description="Human-readable insight"
    )
    confidence: float = Field(
        description="Confidence level (0-1)",
        ge=0.0,
        le=1.0
    )
    supporting_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Data supporting this insight"
    )


# Chart type compatibility mapping
MERMAID_COMPATIBLE_CHARTS = {
    ChartType.PIE
}

PYTHON_REQUIRED_CHARTS = {
    ChartType.LINE,
    ChartType.BAR,
    ChartType.PIE,
    ChartType.SCATTER,
    ChartType.HEATMAP,
    ChartType.HISTOGRAM,
    ChartType.BOX_PLOT,
    ChartType.AREA,
    ChartType.BUBBLE,
    ChartType.WATERFALL,
    ChartType.TREEMAP
}

# Chart selection rules based on data dimensions
CHART_SELECTION_RULES = {
    DataDimension.TEMPORAL: [ChartType.LINE, ChartType.AREA, ChartType.BAR],
    DataDimension.CATEGORICAL: [ChartType.BAR, ChartType.PIE, ChartType.RADAR],
    DataDimension.CONTINUOUS: [ChartType.HISTOGRAM, ChartType.SCATTER, ChartType.LINE],
    DataDimension.HIERARCHICAL: [ChartType.TREEMAP, ChartType.PIE],
    DataDimension.CORRELATION: [ChartType.SCATTER, ChartType.HEATMAP],
    DataDimension.DISTRIBUTION: [ChartType.HISTOGRAM, ChartType.BOX_PLOT]
}