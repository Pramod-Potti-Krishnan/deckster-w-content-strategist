"""
Analytics Agent Orchestrator
============================

Main entry point for analytics generation.
Coordinates conductor, data synthesis, and chart generation.

Author: Analytics Agent System  
Date: 2024
Version: 1.0
"""

import logging
from typing import Dict, Any, Optional, List
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

from src.utils.model_utils import create_model_with_fallback
from .analytics_utils.models import (
    AnalyticsRequest,
    ChartOutput,
    ChartType,
    GenerationMethod,
    SyntheticDataConfig
)
from .analytics_utils.conductor import AnalyticsConductor
from .analytics_utils.data_synthesizer import DataSynthesizer
from .analytics_utils.mermaid_chart_agent import MermaidChartAgent
from .analytics_utils.python_chart_agent import PythonChartAgent
from .analytics_utils.mcp_integration import get_mcp_integration

logger = logging.getLogger(__name__)


class AnalyticsAgentContext(BaseModel):
    """Context for analytics agent."""
    request: AnalyticsRequest
    use_llm: bool = True
    mcp_available: bool = False


class AnalyticsAgent:
    """
    Main orchestrator for analytics generation.
    Manages the complete pipeline from request to chart output.
    """
    
    def __init__(self, mcp_tool=None):
        """
        Initialize the analytics agent.
        
        Args:
            mcp_tool: Optional MCP tool function for executing Python code
        """
        self.conductor = AnalyticsConductor()
        self.data_synthesizer = DataSynthesizer()
        self.mermaid_agent = MermaidChartAgent()
        
        # Initialize Python agent with MCP if provided
        self.python_agent = PythonChartAgent(mcp_tool)
        
        # Check MCP availability
        mcp = get_mcp_integration()
        if mcp_tool:
            mcp.set_mcp_tool(mcp_tool)
        self.mcp_available = mcp.is_available
        
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the main pydantic_ai agent."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            result_type=ChartOutput,
            system_prompt="""You are the Analytics Agent orchestrator.
            Your role is to coordinate the generation of data visualizations by:
            1. Understanding the user's analytics needs
            2. Selecting the appropriate visualization strategy
            3. Generating synthetic data when needed
            4. Creating the final chart output
            
            Focus on creating clear, insightful visualizations that tell a story."""
        )
    
    async def generate_analytics(
        self,
        content: str,
        title: Optional[str] = None,
        chart_preference: Optional[ChartType] = None,
        theme: Optional[Dict[str, Any]] = None
    ) -> ChartOutput:
        """
        Generate analytics visualization from natural language request.
        
        Args:
            content: Natural language description of analytics needed
            title: Optional chart title
            chart_preference: Optional preferred chart type
            theme: Optional theme configuration
            
        Returns:
            ChartOutput with generated visualization
        """
        logger.info(f"Processing analytics request: {content[:100]}...")
        
        # Parse content into structured request
        request = self._parse_request(content, title, chart_preference, theme)
        
        try:
            # Step 1: Strategy selection via conductor
            logger.debug("Selecting generation strategy...")
            plan = await self.conductor.select_strategy(request)
            
            # Step 2: Generate synthetic data
            logger.debug("Generating synthetic data...")
            data_points, data_description, insights = await self.data_synthesizer.generate_synthetic_data(
                request,
                plan.data_config,
                plan.strategy.chart_type
            )
            
            # Step 3: Generate chart based on strategy
            logger.debug(f"Generating {plan.strategy.chart_type.value} chart via {plan.strategy.method.value}...")
            
            if plan.strategy.method == GenerationMethod.MERMAID:
                output = await self.mermaid_agent.generate_chart(
                    plan,
                    data_points,
                    data_description,
                    insights
                )
            elif plan.strategy.method == GenerationMethod.PYTHON_MCP:
                output = await self.python_agent.generate_chart(
                    plan,
                    data_points,
                    data_description,
                    insights
                )
            else:
                # Fallback to simple bar chart
                logger.warning(f"Unknown generation method: {plan.strategy.method}")
                output = await self._generate_fallback_chart(
                    plan,
                    data_points,
                    data_description,
                    insights
                )
            
            # Step 4: Handle failures with fallback
            if not output.chart_content and plan.strategy.fallback_method:
                logger.warning(f"Primary generation failed, trying fallback: {plan.strategy.fallback_method}")
                plan.strategy.method = plan.strategy.fallback_method
                
                if plan.strategy.fallback_method == GenerationMethod.MERMAID:
                    output = await self.mermaid_agent.generate_chart(
                        plan,
                        data_points,
                        data_description,
                        insights
                    )
                else:
                    output = await self.python_agent.generate_chart(
                        plan,
                        data_points,
                        data_description,
                        insights
                    )
            
            # Add execution metadata
            output.metadata.update({
                "plan_complexity": plan.estimated_complexity,
                "strategy_confidence": plan.strategy.confidence,
                "data_points_count": len(data_points)
            })
            
            logger.info(f"Successfully generated {output.chart_type.value} chart")
            return output
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            # Return error output
            return ChartOutput(
                chart_type=chart_preference or ChartType.BAR,
                chart_content="",
                format="error",
                synthetic_data=[],
                data_description="Failed to generate analytics",
                insights=[],
                generation_method=GenerationMethod.FALLBACK,
                metadata={"error": str(e)}
            )
    
    def _parse_request(
        self,
        content: str,
        title: Optional[str],
        chart_preference: Optional[ChartType],
        theme: Optional[Dict[str, Any]]
    ) -> AnalyticsRequest:
        """
        Parse natural language into structured request.
        
        Args:
            content: Natural language description
            title: Optional title
            chart_preference: Optional chart type
            theme: Optional theme
            
        Returns:
            Structured AnalyticsRequest
        """
        # Extract key information from content
        data_context = content
        description = content
        
        # Try to identify time period
        time_period = None
        time_keywords = ["month", "quarter", "year", "week", "daily", "Q1", "Q2", "Q3", "Q4"]
        for keyword in time_keywords:
            if keyword.lower() in content.lower():
                time_period = keyword
                break
        
        # Create request
        return AnalyticsRequest(
            title=title or "Analytics Visualization",
            description=description,
            data_context=data_context,
            chart_preference=chart_preference,
            time_period=time_period,
            theme=theme or {}
        )
    
    async def _generate_fallback_chart(
        self,
        plan,
        data_points,
        data_description,
        insights
    ) -> ChartOutput:
        """
        Generate a simple fallback chart.
        
        Args:
            plan: Analytics plan
            data_points: Data points
            data_description: Data description
            insights: Insights
            
        Returns:
            Basic chart output
        """
        # Simple bar chart in Mermaid
        labels = [dp.label for dp in data_points[:5]]  # Limit to 5 for simplicity
        values = [dp.value for dp in data_points[:5]]
        
        mermaid_code = f"""%%{{init: {{'theme':'base'}}}}%%
xychart-beta
    title "{plan.request.title}"
    x-axis [{', '.join(f'"{l}"' for l in labels)}]
    y-axis "Value"
    bar [{', '.join(str(v) for v in values)}]
"""
        
        return ChartOutput(
            chart_type=ChartType.BAR,
            chart_content=mermaid_code,
            format="mermaid",
            synthetic_data=data_points,
            data_description=data_description,
            insights=insights,
            generation_method=GenerationMethod.FALLBACK,
            metadata={"fallback": True}
        )
    
    async def generate_with_llm(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ChartOutput:
        """
        Generate analytics using LLM for complex scenarios.
        
        Args:
            prompt: User prompt
            context: Additional context
            
        Returns:
            Chart output
        """
        agent_context = AnalyticsAgentContext(
            request=self._parse_request(prompt, None, None, None),
            use_llm=True,
            mcp_available=self.mcp_available
        )
        
        full_prompt = f"""
        Generate analytics visualization for this request:
        {prompt}
        
        You have access to:
        - Mermaid charts (line, bar, pie, radar)
        - Python charts via MCP (all complex types)
        - Synthetic data generation with trends
        
        Create a meaningful visualization that tells a story.
        Include relevant insights from the data.
        """
        
        try:
            result = await self.agent.run(full_prompt, deps=agent_context)
            return result.data
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fallback to standard generation
            return await self.generate_analytics(prompt)


# Public API
async def create_analytics(
    content: str,
    title: Optional[str] = None,
    chart_type: Optional[str] = None,
    theme: Optional[Dict[str, Any]] = None,
    mcp_tool=None
) -> Dict[str, Any]:
    """
    Public API for analytics generation.
    
    Args:
        content: Description of analytics needed
        title: Optional chart title
        chart_type: Optional preferred chart type
        theme: Optional theme configuration
        mcp_tool: Optional MCP tool function for executing Python code
        
    Returns:
        Dictionary with chart output
    """
    # Convert string chart type to enum
    chart_preference = None
    if chart_type:
        try:
            chart_preference = ChartType(chart_type.lower())
        except ValueError:
            logger.warning(f"Unknown chart type: {chart_type}")
    
    # Create agent and generate
    agent = AnalyticsAgent(mcp_tool)
    output = await agent.generate_analytics(
        content,
        title,
        chart_preference,
        theme
    )
    
    # Convert to dictionary for API response
    return {
        "success": bool(output.chart_content),
        "chart_type": output.chart_type.value,
        "format": output.format,
        "content": output.chart_content,
        "data": output.raw_data if output.raw_data else [
            {"label": dp.label, "value": dp.value}
            for dp in output.synthetic_data
        ],
        "csv_data": output.csv_data,
        "description": output.data_description,
        "insights": output.insights,
        "metadata": output.metadata
    }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_analytics():
        """Test the analytics agent."""
        
        # Test 1: Simple bar chart
        result = await create_analytics(
            "Show me quarterly sales data for 2024",
            title="Q1-Q4 2024 Sales Performance"
        )
        print(f"Test 1 - Chart type: {result['chart_type']}")
        print(f"Test 1 - Format: {result['format']}")
        
        # Test 2: Line chart with trend
        result = await create_analytics(
            "Display monthly revenue growth showing an upward trend",
            title="Revenue Growth Trend",
            chart_type="line"
        )
        print(f"Test 2 - Chart type: {result['chart_type']}")
        print(f"Test 2 - Insights: {result['insights']}")
        
        # Test 3: Complex visualization
        result = await create_analytics(
            "Create a heatmap showing correlation between different product categories and regions",
            title="Product-Region Correlation",
            chart_type="heatmap"
        )
        print(f"Test 3 - Chart type: {result['chart_type']}")
        print(f"Test 3 - Success: {result['success']}")
    
    asyncio.run(test_analytics())