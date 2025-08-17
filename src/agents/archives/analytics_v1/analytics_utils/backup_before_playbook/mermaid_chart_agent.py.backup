"""
Mermaid Chart Generation Agent
===============================

Generates Mermaid chart syntax for various chart types.
Supports line, bar, radar, and pie charts with theming.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field

from src.utils.model_utils import create_model_with_fallback
from .models import (
    AnalyticsPlan,
    ChartOutput,
    ChartType,
    DataPoint,
    GenerationMethod,
    MermaidChartConfig
)
from .csv_utils import data_points_to_csv

logger = logging.getLogger(__name__)


class MermaidContext(BaseModel):
    """Context for Mermaid generation."""
    chart_type: ChartType
    data_points: List[DataPoint]
    title: str
    config: MermaidChartConfig
    

class MermaidSyntax(BaseModel):
    """Generated Mermaid syntax."""
    code: str = Field(description="Complete Mermaid chart code")
    chart_type: str = Field(description="Type of Mermaid chart")
    estimated_complexity: str = Field(description="Complexity: simple, moderate, complex")


class MermaidChartAgent:
    """
    Agent for generating Mermaid chart syntax.
    Supports line, bar, radar, and pie charts.
    """
    
    def __init__(self):
        """Initialize the Mermaid chart agent."""
        self.agent = self._create_agent()
        self.supported_charts = {
            ChartType.LINE: self._generate_line_chart,
            ChartType.BAR: self._generate_bar_chart,
            ChartType.PIE: self._generate_pie_chart,
            ChartType.RADAR: self._generate_radar_chart
        }
        
    def _create_agent(self) -> Agent:
        """Create the pydantic_ai agent for Mermaid generation."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            result_type=MermaidSyntax,
            system_prompt="""You are an expert in Mermaid chart syntax.
            Generate clean, valid Mermaid code for various chart types.
            
            Key requirements:
            1. Use proper Mermaid syntax for each chart type
            2. Include clear labels and values
            3. Apply color themes appropriately
            4. Ensure code is renderable
            5. Keep syntax simple and maintainable
            
            Chart types:
            - xychart-beta: For line and bar charts
            - pie: For pie charts
            - radar: For radar/spider charts
            
            Always validate that the syntax follows Mermaid's current specification."""
        )
    
    def _format_value(self, value: float, precision: int = 2) -> str:
        """
        Format numeric values for display.
        
        Args:
            value: Numeric value
            precision: Decimal places
            
        Returns:
            Formatted string
        """
        if value == int(value):
            return str(int(value))
        return f"{value:.{precision}f}"
    
    def _escape_label(self, label: str) -> str:
        """
        Escape labels for Mermaid syntax.
        
        Args:
            label: Raw label text
            
        Returns:
            Escaped label
        """
        # Escape special characters
        label = label.replace('"', '\\"')
        label = label.replace("'", "\\'")
        label = label.replace("\n", " ")
        return label
    
    def _generate_line_chart(
        self, 
        data_points: List[DataPoint], 
        title: str,
        config: MermaidChartConfig
    ) -> str:
        """
        Generate Mermaid syntax for line chart using xychart-beta.
        
        Args:
            data_points: Data points
            title: Chart title
            config: Chart configuration
            
        Returns:
            Mermaid code for line chart
        """
        # Build xychart-beta syntax
        lines = ["xychart-beta"]
        
        # Add title if provided
        if title:
            lines.append(f'    title "{self._escape_label(title)}"')
        
        # X-axis with labels
        x_labels = [dp.label for dp in data_points]
        x_axis_line = '    x-axis [' + ', '.join(x_labels) + ']'
        lines.append(x_axis_line)
        
        # Y-axis without label to avoid overlap
        lines.append('    y-axis')
        
        # Line data with numeric values
        values = [self._format_value(dp.value) for dp in data_points]
        line_data = '    line [' + ', '.join(values) + ']'
        lines.append(line_data)
        
        return '\n'.join(lines)
    
    def _generate_bar_chart(
        self, 
        data_points: List[DataPoint], 
        title: str,
        config: MermaidChartConfig
    ) -> str:
        """
        Generate Mermaid syntax for bar chart using xychart-beta.
        
        Args:
            data_points: Data points
            title: Chart title
            config: Chart configuration
            
        Returns:
            Mermaid code for bar chart
        """
        # Build xychart-beta syntax
        lines = ["xychart-beta"]
        
        # Add title if provided
        if title:
            lines.append(f'    title "{self._escape_label(title)}"')
        
        # X-axis with labels
        x_labels = [dp.label for dp in data_points]
        x_axis_line = '    x-axis [' + ', '.join(x_labels) + ']'
        lines.append(x_axis_line)
        
        # Y-axis without label to avoid overlap
        lines.append('    y-axis')
        
        # Bar data with numeric values
        values = [self._format_value(dp.value) for dp in data_points]
        bar_data = '    bar [' + ', '.join(values) + ']'
        lines.append(bar_data)
        
        return '\n'.join(lines)
    
    def _generate_pie_chart(
        self, 
        data_points: List[DataPoint], 
        title: str,
        config: MermaidChartConfig
    ) -> str:
        """
        Generate Mermaid syntax for pie chart.
        
        Args:
            data_points: Data points
            title: Chart title
            config: Chart configuration
            
        Returns:
            Mermaid code for pie chart
        """
        lines = ["%%{init: {'theme':'base'}}%%"]
        lines.append(f'pie title {self._escape_label(title)}' if title else 'pie')
        
        # Add data segments
        total = sum(dp.value for dp in data_points)
        for dp in data_points:
            percentage = (dp.value / total) * 100 if total > 0 else 0
            label = self._escape_label(dp.label)
            lines.append(f'    "{label}" : {self._format_value(dp.value)}')
        
        return '\n'.join(lines)
    
    def _generate_radar_chart(
        self, 
        data_points: List[DataPoint], 
        title: str,
        config: MermaidChartConfig
    ) -> str:
        """
        Generate pseudo-radar chart using Mermaid.
        Note: Mermaid doesn't have native radar charts,
        so we create a representation using available syntax.
        
        Args:
            data_points: Data points
            title: Chart title
            config: Chart configuration
            
        Returns:
            Mermaid code for radar-like visualization
        """
        # Since Mermaid doesn't support radar charts directly,
        # we'll use a creative approach with a pie chart or bar chart
        # For now, fallback to a bar chart representation
        logger.warning("Radar charts not natively supported in Mermaid, using bar chart")
        return self._generate_bar_chart(data_points, title + " (Radar View)", config)
    
    def _apply_theme(self, mermaid_code: str, config: MermaidChartConfig) -> str:
        """
        Apply theme settings to Mermaid code.
        
        Args:
            mermaid_code: Base Mermaid code
            config: Chart configuration with theme
            
        Returns:
            Themed Mermaid code
        """
        # If we have custom colors, we could inject them
        # For now, Mermaid theming is limited, so we keep the base theme
        
        if config.theme and config.theme != "base":
            # Replace theme in init block
            mermaid_code = mermaid_code.replace(
                "{'theme':'base'}", 
                f"{{'theme':'{config.theme}'}}"
            )
        
        return mermaid_code
    
    def _validate_mermaid_syntax(self, code: str) -> bool:
        """
        Basic validation of Mermaid syntax.
        
        Args:
            code: Mermaid code
            
        Returns:
            True if syntax appears valid
        """
        # Basic checks
        if not code or not code.strip():
            return False
        
        # Check for required keywords
        required_keywords = {
            "xychart-beta": ["x-axis", "y-axis"],
            "pie": ["pie"],
            "graph": ["graph"],
            "flowchart": ["flowchart"]
        }
        
        for keyword, requirements in required_keywords.items():
            if keyword in code:
                for req in requirements:
                    if req not in code:
                        logger.warning(f"Missing required element '{req}' for {keyword}")
                        return False
        
        return True
    
    async def generate_chart(
        self,
        plan: AnalyticsPlan,
        data_points: List[DataPoint],
        data_description: str,
        insights: List[str]
    ) -> ChartOutput:
        """
        Generate Mermaid chart from analytics plan.
        
        Args:
            plan: Analytics execution plan
            data_points: Synthetic data points
            data_description: Description of the data
            insights: Data insights
            
        Returns:
            Chart output with Mermaid code
        """
        chart_type = plan.strategy.chart_type
        config = plan.chart_config
        title = plan.request.title
        
        logger.info(f"Generating Mermaid {chart_type.value} chart for '{title}'")
        
        # Check if chart type is supported
        if chart_type not in self.supported_charts:
            logger.error(f"Unsupported chart type for Mermaid: {chart_type}")
            return ChartOutput(
                chart_type=chart_type,
                chart_content="",
                format="mermaid",
                synthetic_data=data_points,
                data_description=data_description,
                insights=insights,
                generation_method=GenerationMethod.MERMAID,
                metadata={"error": f"Chart type {chart_type} not supported in Mermaid"}
            )
        
        try:
            # Generate chart using appropriate method
            generator = self.supported_charts[chart_type]
            mermaid_code = generator(data_points, title, config)
            
            # Apply theme
            mermaid_code = self._apply_theme(mermaid_code, config)
            
            # Validate syntax
            if not self._validate_mermaid_syntax(mermaid_code):
                logger.warning("Generated Mermaid syntax may have issues")
            
            # Create raw data for display
            raw_data = [{"label": dp.label, "value": dp.value} for dp in data_points]
            
            # Generate CSV data
            csv_data = data_points_to_csv(data_points, chart_type)
            
            # Return successful output
            return ChartOutput(
                chart_type=chart_type,
                chart_content=mermaid_code,
                format="mermaid",
                synthetic_data=data_points,
                raw_data=raw_data,
                csv_data=csv_data,
                data_description=data_description,
                insights=insights,
                generation_method=GenerationMethod.MERMAID,
                metadata={
                    "title": title,
                    "num_data_points": len(data_points),
                    "chart_syntax": config.chart_type if isinstance(config, MermaidChartConfig) else "xychart-beta"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate Mermaid chart: {e}")
            return ChartOutput(
                chart_type=chart_type,
                chart_content="",
                format="mermaid",
                synthetic_data=data_points,
                data_description=data_description,
                insights=insights,
                generation_method=GenerationMethod.MERMAID,
                metadata={"error": str(e)}
            )
    
    async def generate_with_llm(
        self,
        plan: AnalyticsPlan,
        data_points: List[DataPoint]
    ) -> str:
        """
        Generate Mermaid chart using LLM for complex scenarios.
        
        Args:
            plan: Analytics plan
            data_points: Data points
            
        Returns:
            Mermaid code
        """
        context = MermaidContext(
            chart_type=plan.strategy.chart_type,
            data_points=data_points,
            title=plan.request.title,
            config=plan.chart_config
        )
        
        prompt = f"""
        Generate Mermaid chart code for this data:
        
        Chart Type: {plan.strategy.chart_type.value}
        Title: {plan.request.title}
        Description: {plan.request.description}
        
        Data Points ({len(data_points)} items):
        {chr(10).join(f"- {dp.label}: {dp.value}" for dp in data_points[:10])}
        {"..." if len(data_points) > 10 else ""}
        
        Requirements:
        1. Use appropriate Mermaid syntax (xychart-beta for line/bar, pie for pie charts)
        2. Include all data points
        3. Format numbers appropriately
        4. Make labels readable
        5. Ensure the code is valid and will render
        
        Generate complete, valid Mermaid code.
        """
        
        try:
            result = await self.agent.run(prompt, deps=context)
            return result.data.code
        except Exception as e:
            logger.warning(f"LLM generation failed, using fallback: {e}")
            # Fallback to deterministic generation
            generator = self.supported_charts.get(
                plan.strategy.chart_type,
                self._generate_bar_chart
            )
            return generator(data_points, plan.request.title, plan.chart_config)


# Example Mermaid outputs for reference:
"""
Line Chart:
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Sales Trend"
    x-axis ["Jan", "Feb", "Mar", "Apr", "May"]
    y-axis "Revenue ($)"
    line [100, 120, 140, 130, 160]

Bar Chart:
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Product Sales"
    x-axis ["Product A", "Product B", "Product C"]
    y-axis "Units Sold"
    bar [45, 38, 52]

Pie Chart:
%%{init: {'theme':'base'}}%%
pie title Market Share
    "Company A" : 45
    "Company B" : 30
    "Company C" : 25
"""