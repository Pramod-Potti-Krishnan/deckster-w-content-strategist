"""
Mermaid Chart Generation Agent
===============================

Generates Mermaid chart syntax for PIE charts only.
All other chart types should use Python/matplotlib.

Author: Analytics Agent System
Date: 2024
Version: 2.0
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
    Only supports PIE charts - all other types use Python/matplotlib.
    """
    
    def __init__(self):
        """Initialize the Mermaid chart agent."""
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the pydantic_ai agent for Mermaid generation."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            result_type=MermaidSyntax,
            system_prompt="""You are an expert in Mermaid pie chart syntax.
            Generate clean, valid Mermaid code for pie charts only.
            
            Key requirements:
            1. Use proper Mermaid pie chart syntax
            2. Include clear labels and values
            3. Ensure percentages are meaningful
            4. Keep syntax simple and maintainable
            5. Values should sum to 100% for clarity
            
            Pie chart syntax:
            pie title "Chart Title"
                "Label A" : value1
                "Label B" : value2
            
            Always validate that the syntax follows Mermaid's pie chart specification."""
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
    
    def _generate_pie_chart(
        self, 
        plan: AnalyticsPlan,
        data_points: List[DataPoint]
    ) -> str:
        """
        Generate Mermaid syntax for pie chart.
        
        Args:
            plan: Analytics plan
            data_points: Data points
            
        Returns:
            Mermaid code for pie chart
        """
        title = plan.request.title
        lines = ["%%{init: {'theme':'base'}}%%"]
        lines.append(f'pie title "{self._escape_label(title)}"' if title else 'pie')
        
        # Ensure we have meaningful data
        if not data_points:
            logger.warning("No data points provided for pie chart")
            lines.append('    "No Data" : 100')
            return '\n'.join(lines)
        
        # Calculate total and percentages
        total = sum(dp.value for dp in data_points)
        if total <= 0:
            logger.warning("Total value is zero or negative, adjusting to show equal segments")
            # Show equal segments if total is invalid
            equal_value = 100 / len(data_points)
            for dp in data_points:
                label = self._escape_label(dp.label)
                lines.append(f'    "{label}" : {self._format_value(equal_value)}')
        else:
            # Use actual percentages
            for dp in data_points:
                percentage = (dp.value / total) * 100
                label = self._escape_label(dp.label)
                lines.append(f'    "{label}" : {self._format_value(percentage)}')
        
        return '\n'.join(lines)
    
    def _apply_theme(self, mermaid_code: str, config: MermaidChartConfig) -> str:
        """
        Apply theme to Mermaid chart.
        
        Args:
            mermaid_code: Base Mermaid code
            config: Chart configuration
            
        Returns:
            Themed Mermaid code
        """
        if config and config.theme and config.theme != "base":
            # Replace the theme in the init block
            return mermaid_code.replace(
                "{'theme':'base'}",
                f"{{'theme':'{config.theme}'}}"
            )
        return mermaid_code
    
    def _validate_mermaid_syntax(self, mermaid_code: str) -> bool:
        """
        Basic validation of Mermaid syntax.
        
        Args:
            mermaid_code: Mermaid code to validate
            
        Returns:
            True if syntax appears valid
        """
        if not mermaid_code:
            return False
        
        # Check for required pie chart elements
        if "pie" not in mermaid_code:
            return False
        
        # Check for at least one data entry
        if '":' not in mermaid_code:
            return False
        
        return True
    
    def _create_error_output(self, plan: AnalyticsPlan, error_msg: str) -> ChartOutput:
        """
        Create error output when chart generation fails.
        
        Args:
            plan: Analytics plan
            error_msg: Error message
            
        Returns:
            Error ChartOutput
        """
        return ChartOutput(
            chart_type=plan.strategy.chart_type,
            chart_content="",
            format="error",
            synthetic_data=[],
            data_description="Failed to generate chart",
            insights=[],
            generation_method=GenerationMethod.MERMAID,
            metadata={"error": error_msg}
        )
    
    async def generate_chart(
        self,
        plan: AnalyticsPlan,
        data_points: List[DataPoint],
        data_description: str,
        insights: List[str]
    ) -> ChartOutput:
        """
        Generate Mermaid chart from analytics plan.
        Only PIE charts are supported.
        
        Args:
            plan: Analytics execution plan
            data_points: Synthetic data points
            data_description: Description of the data
            insights: Data insights
            
        Returns:
            Chart output with Mermaid code
        """
        chart_type = plan.strategy.chart_type
        
        logger.info(f"Generating Mermaid chart for type: {chart_type.value}")
        
        # Only PIE charts are supported in Mermaid
        if chart_type != ChartType.PIE:
            error_msg = f"Chart type {chart_type.value} is not supported in Mermaid. Only PIE charts use Mermaid renderer."
            logger.error(error_msg)
            return self._create_error_output(plan, error_msg)
        
        try:
            # Generate pie chart
            mermaid_code = self._generate_pie_chart(plan, data_points)
            
            # Apply theme
            if isinstance(plan.chart_config, MermaidChartConfig):
                mermaid_code = self._apply_theme(mermaid_code, plan.chart_config)
            
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
                    "title": plan.request.title,
                    "num_data_points": len(data_points),
                    "chart_syntax": "pie"
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to generate Mermaid pie chart: {e}"
            logger.error(error_msg)
            return self._create_error_output(plan, error_msg)
    
    async def generate_with_llm(
        self,
        plan: AnalyticsPlan,
        data_points: List[DataPoint]
    ) -> str:
        """
        Generate Mermaid pie chart using LLM for complex scenarios.
        
        Args:
            plan: Analytics plan
            data_points: Data points
            
        Returns:
            Mermaid code
        """
        if plan.strategy.chart_type != ChartType.PIE:
            raise ValueError(f"Only PIE charts supported, got {plan.strategy.chart_type}")
        
        context = MermaidContext(
            chart_type=plan.strategy.chart_type,
            data_points=data_points,
            title=plan.request.title,
            config=plan.chart_config
        )
        
        prompt = f"""
        Generate Mermaid pie chart code for this data:
        
        Title: {plan.request.title}
        Description: {plan.request.description}
        
        Data Points ({len(data_points)} items):
        {chr(10).join(f"- {dp.label}: {dp.value}" for dp in data_points[:10])}
        {"..." if len(data_points) > 10 else ""}
        
        Requirements:
        1. Use proper Mermaid pie chart syntax
        2. Convert values to percentages that sum to 100%
        3. Include all data points with clear labels
        4. Format numbers to 1 decimal place
        5. Ensure the code is valid and will render
        
        Example format:
        pie title "Chart Title"
            "Label A" : 45.5
            "Label B" : 30.2
            "Label C" : 24.3
        
        Generate complete, valid Mermaid pie chart code.
        """
        
        try:
            result = await self.agent.run(prompt, deps=context)
            return result.data.code
        except Exception as e:
            logger.warning(f"LLM generation failed, using fallback: {e}")
            # Fallback to deterministic generation
            return self._generate_pie_chart(plan, data_points)


# Example Mermaid pie chart output:
"""
%%{init: {'theme':'base'}}%%
pie title "Market Share Distribution 2024"
    "Company A" : 35.5
    "Company B" : 28.3
    "Company C" : 20.7
    "Company D" : 15.5
"""