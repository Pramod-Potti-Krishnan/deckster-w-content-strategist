"""
Analytics Conductor Agent
=========================

Intelligent strategy selection for chart generation.
Analyzes requests and determines the best visualization approach.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import logging
from typing import Optional, List, Dict, Any
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

from src.utils.model_utils import create_model_with_fallback
from .models import (
    AnalyticsRequest,
    ChartType,
    ChartStrategy,
    GenerationMethod,
    DataDimension,
    MermaidChartConfig,
    PythonChartConfig,
    AnalyticsPlan,
    SyntheticDataConfig,
    MERMAID_COMPATIBLE_CHARTS,
    PYTHON_REQUIRED_CHARTS,
    CHART_SELECTION_RULES
)

logger = logging.getLogger(__name__)


class ConductorContext(BaseModel):
    """Context for conductor decision-making."""
    request: AnalyticsRequest
    available_methods: List[GenerationMethod]


class AnalyticsConductor:
    """
    Conductor for analytics generation strategy selection.
    Analyzes requests and determines optimal visualization approach.
    """
    
    def __init__(self):
        """Initialize the conductor agent."""
        self.agent = self._create_agent()
        self.chart_rules = CHART_SELECTION_RULES
        
    def _create_agent(self) -> Agent:
        """Create the pydantic_ai agent for strategy selection."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            result_type=ChartStrategy,
            system_prompt="""You are an expert data visualization strategist. 
            Your role is to analyze analytics requests and determine:
            1. The most appropriate chart type based on the data
            2. The best generation method (Mermaid or Python)
            3. Provide clear reasoning for your choices
            
            Consider:
            - Data dimensions and relationships
            - Comparison vs composition vs distribution needs
            - Temporal patterns and trends
            - User preferences and context
            - Technical capabilities of each method
            
            Mermaid is preferred for simple, clean charts.
            Python is required for complex statistical visualizations."""
        )
    
    def _analyze_data_dimension(self, request: AnalyticsRequest) -> DataDimension:
        """
        Analyze the primary data dimension from the request.
        
        Args:
            request: Analytics request
            
        Returns:
            Primary data dimension
        """
        dimensions = request.dimensions
        context = request.data_context.lower()
        description = request.description.lower()
        
        # Check for temporal indicators
        if request.time_period or any(word in context + description 
                                      for word in ['time', 'month', 'year', 'quarter', 'daily', 'weekly', 'trend']):
            return DataDimension.TEMPORAL
        
        # Check for correlation indicators
        if any(word in context + description 
               for word in ['correlation', 'relationship', 'vs', 'versus', 'compare']):
            return DataDimension.CORRELATION
        
        # Check for distribution indicators
        if any(word in context + description 
               for word in ['distribution', 'spread', 'frequency', 'histogram']):
            return DataDimension.DISTRIBUTION
        
        # Check for hierarchical indicators
        if any(word in context + description 
               for word in ['hierarchy', 'breakdown', 'nested', 'tree']):
            return DataDimension.HIERARCHICAL
        
        # Check dimension types
        x_type = dimensions.get('x_axis', {}).get('type', 'categorical')
        y_type = dimensions.get('y_axis', {}).get('type', 'continuous')
        
        if x_type == 'categorical' and y_type == 'continuous':
            return DataDimension.CATEGORICAL
        elif x_type == 'continuous' and y_type == 'continuous':
            return DataDimension.CONTINUOUS
        
        # Default to categorical
        return DataDimension.CATEGORICAL
    
    def _select_chart_type(self, request: AnalyticsRequest, dimension: DataDimension) -> ChartType:
        """
        Select the most appropriate chart type.
        
        Args:
            request: Analytics request
            dimension: Primary data dimension
            
        Returns:
            Selected chart type
        """
        # If user has a preference and it's valid, use it
        if request.chart_preference:
            return request.chart_preference
        
        # Get recommended charts for this dimension
        recommended_charts = self.chart_rules.get(dimension, [ChartType.BAR])
        
        # Apply context-based selection
        context = request.data_context.lower() + request.description.lower()
        
        # Specific chart type indicators
        if 'pie' in context or 'proportion' in context or 'percentage' in context:
            return ChartType.PIE
        elif 'radar' in context or 'multi' in context and 'dimension' in context:
            return ChartType.RADAR
        elif 'scatter' in context or 'correlation' in context:
            return ChartType.SCATTER
        elif 'heat' in context or 'matrix' in context:
            return ChartType.HEATMAP
        elif 'distribution' in context or 'histogram' in context:
            return ChartType.HISTOGRAM
        
        # Return first recommended chart for the dimension
        return recommended_charts[0] if recommended_charts else ChartType.BAR
    
    def _determine_generation_method(self, chart_type: ChartType) -> tuple[GenerationMethod, Optional[GenerationMethod]]:
        """
        Determine the generation method based on chart type.
        
        Args:
            chart_type: Selected chart type
            
        Returns:
            Tuple of (primary method, fallback method)
        """
        if chart_type in MERMAID_COMPATIBLE_CHARTS:
            # Mermaid is primary, Python as fallback
            return GenerationMethod.MERMAID, GenerationMethod.PYTHON_MCP
        elif chart_type in PYTHON_REQUIRED_CHARTS:
            # Python only, no fallback
            return GenerationMethod.PYTHON_MCP, None
        else:
            # Default to Mermaid with Python fallback
            return GenerationMethod.MERMAID, GenerationMethod.PYTHON_MCP
    
    def _create_data_config(self, request: AnalyticsRequest, dimension: DataDimension) -> SyntheticDataConfig:
        """
        Create configuration for synthetic data generation.
        
        Args:
            request: Analytics request
            dimension: Data dimension
            
        Returns:
            Synthetic data configuration
        """
        config = SyntheticDataConfig()
        
        # Determine number of data points
        if dimension == DataDimension.TEMPORAL:
            if 'quarter' in request.data_context.lower():
                config.num_points = 4
            elif 'month' in request.data_context.lower():
                config.num_points = 12
            elif 'week' in request.data_context.lower():
                config.num_points = 52
            else:
                config.num_points = 12  # Default to monthly
        else:
            # For categorical data, use a reasonable default
            config.num_points = 6
        
        # Determine trend based on context
        context = request.data_context.lower()
        if 'growth' in context or 'increase' in context:
            config.trend = "increasing"
        elif 'decline' in context or 'decrease' in context:
            config.trend = "decreasing"
        elif 'seasonal' in context or 'cyclic' in context:
            config.trend = "cyclic"
            config.seasonality = True
        
        # Set value ranges if provided
        if request.data_range:
            config.min_value = request.data_range.get('min')
            config.max_value = request.data_range.get('max')
        
        return config
    
    def _create_chart_config(
        self, 
        method: GenerationMethod, 
        chart_type: ChartType,
        theme: Dict[str, Any]
    ) -> Any:
        """
        Create chart-specific configuration.
        
        Args:
            method: Generation method
            chart_type: Chart type
            theme: Theme configuration
            
        Returns:
            Chart configuration (Mermaid or Python)
        """
        if method == GenerationMethod.MERMAID:
            # Map chart type to Mermaid syntax
            if chart_type in [ChartType.LINE, ChartType.BAR]:
                mermaid_type = "xychart-beta"
            elif chart_type == ChartType.PIE:
                mermaid_type = "pie"
            elif chart_type == ChartType.RADAR:
                mermaid_type = "radar"
            else:
                mermaid_type = "xychart-beta"
            
            config = MermaidChartConfig(
                chart_type=mermaid_type,
                theme=theme.get('mermaid_theme', 'base')
            )
            
            # Extract colors if available
            if 'colors' in theme:
                colors = theme['colors']
                color_list = []
                for key in ['primary', 'secondary', 'accent', 'success', 'warning']:
                    if key in colors:
                        color_list.append(colors[key])
                if color_list:
                    config.color_scheme = color_list
            
            return config
            
        else:  # Python/matplotlib
            return PythonChartConfig(
                library="matplotlib",
                style=theme.get('matplotlib_style', 'seaborn-v0_8'),
                figure_size=theme.get('figure_size', (10, 6))
            )
    
    async def select_strategy(self, request: AnalyticsRequest) -> AnalyticsPlan:
        """
        Select the optimal strategy for analytics generation.
        
        Args:
            request: Analytics request
            
        Returns:
            Complete analytics plan with strategy and configuration
        """
        logger.info(f"Analyzing analytics request: {request.title}")
        
        # Analyze data dimension
        dimension = self._analyze_data_dimension(request)
        logger.debug(f"Identified data dimension: {dimension}")
        
        # Select chart type
        chart_type = self._select_chart_type(request, dimension)
        logger.debug(f"Selected chart type: {chart_type}")
        
        # Determine generation method
        primary_method, fallback_method = self._determine_generation_method(chart_type)
        logger.debug(f"Generation method: {primary_method}, fallback: {fallback_method}")
        
        # Create strategy
        strategy = ChartStrategy(
            method=primary_method,
            chart_type=chart_type,
            confidence=0.85 if primary_method == GenerationMethod.MERMAID else 0.90,
            reasoning=f"Selected {chart_type.value} chart based on {dimension.value} data dimension. "
                     f"Using {primary_method.value} for generation.",
            fallback_method=fallback_method,
            fallback_chart=ChartType.BAR if chart_type != ChartType.BAR else ChartType.LINE
        )
        
        # Create data configuration
        data_config = self._create_data_config(request, dimension)
        
        # Create chart configuration
        chart_config = self._create_chart_config(primary_method, chart_type, request.theme)
        
        # Estimate complexity
        if chart_type in [ChartType.LINE, ChartType.BAR, ChartType.PIE]:
            complexity = "simple"
        elif chart_type in [ChartType.RADAR, ChartType.SCATTER, ChartType.AREA]:
            complexity = "moderate"
        else:
            complexity = "complex"
        
        # Create and return the plan
        plan = AnalyticsPlan(
            request=request,
            strategy=strategy,
            data_config=data_config,
            chart_config=chart_config,
            estimated_complexity=complexity
        )
        
        logger.info(f"Analytics plan created: {chart_type.value} via {primary_method.value}")
        return plan
    
    async def select_strategy_with_llm(self, request: AnalyticsRequest) -> AnalyticsPlan:
        """
        Use LLM for more sophisticated strategy selection.
        
        Args:
            request: Analytics request
            
        Returns:
            Analytics plan with LLM-powered strategy
        """
        context = ConductorContext(
            request=request,
            available_methods=[GenerationMethod.MERMAID, GenerationMethod.PYTHON_MCP]
        )
        
        prompt = f"""
        Analyze this analytics request and select the best visualization strategy:
        
        Title: {request.title}
        Description: {request.description}
        Context: {request.data_context}
        Time Period: {request.time_period or 'Not specified'}
        Dimensions: {request.dimensions}
        
        Consider the data type, relationships, and user needs to select:
        1. The most appropriate chart type
        2. Whether to use Mermaid (simple) or Python (complex) generation
        3. Provide clear reasoning for your choice
        """
        
        try:
            result = await self.agent.run(prompt, deps=context)
            strategy = result.data
            
            # Use the LLM strategy with our configuration
            dimension = self._analyze_data_dimension(request)
            data_config = self._create_data_config(request, dimension)
            chart_config = self._create_chart_config(strategy.method, strategy.chart_type, request.theme)
            
            return AnalyticsPlan(
                request=request,
                strategy=strategy,
                data_config=data_config,
                chart_config=chart_config,
                estimated_complexity="moderate"  # LLM selections are typically more nuanced
            )
            
        except Exception as e:
            logger.warning(f"LLM strategy selection failed, using rule-based: {e}")
            # Fall back to rule-based selection
            return await self.select_strategy(request)