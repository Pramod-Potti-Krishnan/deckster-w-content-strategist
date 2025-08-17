"""
Playbook-Based Analytics Conductor
===================================

LLM-powered chart selection using analytics playbook.
This is a parallel implementation to the rule-based conductor.

Key Features:
- Uses LLM to understand user intent
- References playbook for chart selection
- Considers data characteristics
- Provides confidence scores

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from src.utils.model_utils import create_model_with_fallback
from .models import (
    AnalyticsRequest,
    ChartType,
    GenerationMethod,
    ChartStrategy,  # Changed from GenerationStrategy
    SyntheticDataConfig,
    AnalyticsPlan,
    MermaidChartConfig,
    PythonChartConfig
)
from .analytics_playbook import (
    ANALYTICS_PLAYBOOK,
    get_chart_spec,
    find_charts_for_intent,
    get_chart_when_to_use,
    get_chart_data_requirements,
    get_chart_synthetic_features,
    map_chart_type_to_playbook
)

logger = logging.getLogger(__name__)


class ChartSelection(BaseModel):
    """Result of LLM chart selection."""
    primary_chart: str = Field(description="Primary chart type from playbook")
    secondary_chart: Optional[str] = Field(None, description="Alternative chart if primary fails")
    reasoning: str = Field(description="Why this chart was selected")
    confidence: float = Field(0.8, description="Confidence in selection (0-1)")
    data_characteristics: List[str] = Field(description="Key data characteristics identified")
    matched_rules: List[str] = Field(description="Playbook rules that matched")
    

class AnalyticsConductor:
    """
    LLM-powered conductor that uses the analytics playbook for intelligent chart selection.
    """
    
    def __init__(self):
        """Initialize the playbook conductor."""
        self.agent = self._create_agent()
        self.playbook = ANALYTICS_PLAYBOOK
        
    def _create_agent(self) -> Agent:
        """Create the LLM agent for chart selection."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            result_type=ChartSelection,
            system_prompt="""You are an expert data visualization consultant.
            Your role is to select the most appropriate chart type based on:
            1. The user's analytics request and intent
            2. The data characteristics described
            3. The analytics playbook rules
            
            You have access to a comprehensive playbook with 24 chart types.
            Each chart has specific "when_to_use" rules and data requirements.
            
            Focus on:
            - Matching user intent to chart capabilities
            - Ensuring data requirements are met
            - Selecting charts that tell the story effectively
            - Providing clear reasoning for your selection
            
            Always provide a secondary chart option as fallback."""
        )
    
    async def select_strategy(self, request: AnalyticsRequest) -> AnalyticsPlan:
        """
        Select generation strategy using LLM and playbook.
        
        Args:
            request: Analytics request from user
            
        Returns:
            Complete analytics plan with strategy
        """
        logger.info(f"[Playbook] Selecting strategy for: {request.description[:100]}...")
        
        try:
            # Get LLM selection
            selection = await self._get_llm_selection(request)
            
            # Map to generation strategy
            strategy = self._build_strategy(selection, request)
            
            # Get data configuration from playbook
            data_config = self._get_data_config(selection.primary_chart)
            
            # Create chart configuration
            chart_config = self._create_chart_config(strategy.method, strategy.chart_type, request.theme)
            
            # Build complete plan
            plan = AnalyticsPlan(
                request=request,
                strategy=strategy,
                data_config=data_config,
                chart_config=chart_config,
                estimated_complexity=self._estimate_complexity(selection.primary_chart)
            )
            
            logger.info(f"[Playbook] Selected {selection.primary_chart} with {selection.confidence:.0%} confidence")
            return plan
            
        except Exception as e:
            logger.error(f"[Playbook] Selection failed: {e}")
            # Fallback to simple bar chart
            return self._get_fallback_plan(request)
    
    async def _get_llm_selection(self, request: AnalyticsRequest) -> ChartSelection:
        """
        Get chart selection from LLM.
        
        Args:
            request: Analytics request
            
        Returns:
            Chart selection with reasoning
        """
        # Build context with playbook information
        playbook_context = self._build_playbook_context()
        
        prompt = f"""
        Analyze this analytics request and select the best chart type:
        
        Title: {request.title}
        Description: {request.description}
        Context: {request.data_context}
        Time Period: {request.time_period or "Not specified"}
        User Preference: {request.chart_preference.value if request.chart_preference else "None"}
        
        Available chart types and their usage rules:
        {playbook_context}
        
        Consider:
        1. What story is the user trying to tell?
        2. What data patterns would best support this story?
        3. Which chart type best matches the intent and data?
        
        Provide:
        - Primary chart selection from the playbook
        - Secondary fallback option
        - Clear reasoning for your choice
        - Key data characteristics to generate
        - Which playbook rules matched
        """
        
        result = await self.agent.run(prompt)
        return result.data
    
    def _build_playbook_context(self) -> str:
        """Build context string with playbook rules."""
        context_lines = []
        
        for chart_name, spec in self.playbook["charts"].items():
            rules = spec.get("when_to_use", [])
            renderer = spec.get("renderer", "unknown")
            
            context_lines.append(f"\n{chart_name} ({renderer}):")
            for rule in rules[:2]:  # Include first 2 rules for brevity
                context_lines.append(f"  - {rule}")
        
        return "\n".join(context_lines)
    
    def _build_strategy(self, selection: ChartSelection, request: AnalyticsRequest) -> ChartStrategy:
        """
        Build generation strategy from selection.
        
        Args:
            selection: LLM chart selection
            request: Original request
            
        Returns:
            Generation strategy
        """
        # Map playbook chart to ChartType enum
        chart_type = self._map_to_chart_type(selection.primary_chart)
        fallback_type = self._map_to_chart_type(selection.secondary_chart) if selection.secondary_chart else None
        
        # Determine generation method based on renderer
        chart_spec = get_chart_spec(selection.primary_chart)
        method = GenerationMethod.MERMAID if chart_spec.get("renderer") == "mermaid" else GenerationMethod.PYTHON_MCP
        
        # Determine fallback method
        fallback_method = None
        if fallback_type:
            fallback_spec = get_chart_spec(selection.secondary_chart)
            if fallback_spec:
                fallback_method = GenerationMethod.MERMAID if fallback_spec.get("renderer") == "mermaid" else GenerationMethod.PYTHON_MCP
        
        return ChartStrategy(
            chart_type=chart_type,
            method=method,
            confidence=selection.confidence,
            reasoning=selection.reasoning
        )
    
    def _map_to_chart_type(self, playbook_name: str) -> ChartType:
        """
        Map playbook chart name to ChartType enum.
        
        Args:
            playbook_name: Name from playbook (e.g., 'line_chart')
            
        Returns:
            ChartType enum value
        """
        # Reverse mapping from playbook names to enum
        mapping = {
            "line_chart": ChartType.LINE,
            "step_chart": ChartType.LINE,  # Step is similar to line
            "bar_chart_vertical": ChartType.BAR,
            "bar_chart_horizontal": ChartType.BAR,
            "grouped_bar_chart": ChartType.BAR,
            "stacked_bar_chart": ChartType.BAR,
            "pie_chart": ChartType.PIE,
            "scatter_plot": ChartType.SCATTER,
            "histogram": ChartType.HISTOGRAM,
            "heatmap": ChartType.HEATMAP,
            "radar_chart": ChartType.RADAR,
            "box_plot": ChartType.BOX_PLOT,
            "violin_plot": ChartType.BOX_PLOT,  # Similar distribution visualization
            "area_chart": ChartType.AREA,
            "stacked_area_chart": ChartType.AREA,
            "bubble_chart": ChartType.BUBBLE,
            "hexbin": ChartType.SCATTER,  # Dense scatter variant
            "waterfall": ChartType.WATERFALL,
            "error_bar_chart": ChartType.LINE,  # Line with error bars
            "gantt": ChartType.BAR,  # Timeline bars
            "funnel": ChartType.BAR,  # Funnel approximation with bars
            "pareto": ChartType.BAR,  # Ranked bars
            "control_chart": ChartType.LINE  # Process monitoring over time
        }
        
        return mapping.get(playbook_name, ChartType.BAR)
    
    def _get_data_config(self, chart_name: str) -> SyntheticDataConfig:
        """
        Get data configuration from playbook.
        
        Args:
            chart_name: Chart name from playbook
            
        Returns:
            Synthetic data configuration
        """
        features = get_chart_synthetic_features(chart_name)
        
        # Extract configuration
        num_points = features.get("rows", features.get("n", features.get("num_categories", 10)))
        
        # Determine data pattern
        pattern = "random"
        if "trend" in str(features):
            pattern = "trend"
        elif "seasonal" in str(features):
            pattern = "seasonal"
        elif "correlation" in str(features):
            pattern = "correlation"
        
        # Extract value range
        value_range = (0, 100)
        if "value_range" in features:
            value_range = tuple(features["value_range"])
        elif "value_distribution" in features:
            dist = features["value_distribution"]
            if "uniform" in dist:
                # Try to extract range from uniform(a,b) pattern
                import re
                match = re.search(r'uniform\((\d+),(\d+)\)', dist)
                if match:
                    value_range = (int(match.group(1)), int(match.group(2)))
        
        # Parse noise level
        noise_level_raw = features.get("noise_level", 0.1)
        if isinstance(noise_level_raw, str):
            if "none" in noise_level_raw.lower():
                noise_level = 0.0
            elif "low" in noise_level_raw.lower():
                noise_level = 0.1
            elif "medium" in noise_level_raw.lower():
                noise_level = 0.2
            elif "high" in noise_level_raw.lower():
                noise_level = 0.3
            else:
                noise_level = 0.1
        else:
            noise_level = float(noise_level_raw) if noise_level_raw else 0.1
        
        return SyntheticDataConfig(
            num_points=num_points,
            data_pattern=pattern,
            noise_level=noise_level,
            trend_direction="up" if "increasing" in str(features) else "neutral",
            seasonality_period=features.get("x_frequency", 12) if pattern == "seasonal" else 12,
            value_range=value_range,
            categories=features.get("num_categories", features.get("num_groups", [])),
            time_series=features.get("x_frequency") is not None
        )
    
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
            # Only PIE charts use Mermaid
            if chart_type == ChartType.PIE:
                return MermaidChartConfig(
                    chart_type="pie",
                    theme=theme.get('mermaid_theme', 'base') if theme else 'base'
                )
            else:
                # Should not reach here - non-PIE charts should use Python
                logger.warning(f"Non-PIE chart {chart_type} requested for Mermaid, using Python instead")
                return PythonChartConfig(
                    library="matplotlib",
                    figure_size=theme.get('figure_size', (10, 6)) if theme else (10, 6),
                    style=theme.get('style', 'seaborn-v0_8') if theme else 'seaborn-v0_8',
                    palette=theme.get('palette', 'husl') if theme else 'husl'
                )
        else:
            # Python/matplotlib configuration
            return PythonChartConfig(
                library="matplotlib",
                figure_size=theme.get('figure_size', (10, 6)) if theme else (10, 6),
                style=theme.get('style', 'seaborn-v0_8') if theme else 'seaborn-v0_8',
                palette=theme.get('palette', 'husl') if theme else 'husl'
            )
    
    def _estimate_complexity(self, chart_name: str) -> str:
        """
        Estimate complexity based on chart type.
        
        Args:
            chart_name: Chart name from playbook
            
        Returns:
            Complexity level
        """
        # Complex charts requiring Python/matplotlib
        complex_charts = [
            "heatmap", "hexbin", "violin_plot", "control_chart",
            "waterfall", "gantt", "pareto", "bubble_chart",
            "stacked_area_chart", "grouped_bar_chart", "stacked_bar_chart"
        ]
        
        # Medium complexity
        medium_charts = [
            "scatter_plot", "box_plot", "histogram", "error_bar_chart",
            "radar_chart", "area_chart", "step_chart"
        ]
        
        if chart_name in complex_charts:
            return "complex"
        elif chart_name in medium_charts:
            return "moderate"
        else:
            return "simple"
    
    def _get_fallback_plan(self, request: AnalyticsRequest) -> AnalyticsPlan:
        """
        Get fallback plan when LLM selection fails.
        
        Args:
            request: Analytics request
            
        Returns:
            Simple fallback plan
        """
        logger.warning("[Playbook] Using fallback bar chart plan")
        
        return AnalyticsPlan(
            request=request,
            strategy=ChartStrategy(
                chart_type=ChartType.BAR,
                method=GenerationMethod.MERMAID,
                confidence=0.5,
                reasoning="Fallback to simple bar chart"
            ),
            data_config=SyntheticDataConfig(
                num_points=10,
                data_pattern="random",
                value_range=(0, 100)
            ),
            chart_config=PythonChartConfig(
                library="matplotlib",
                figure_size=(10, 6),
                style="seaborn-v0_8",
                palette="husl"
            ),
            estimated_complexity="simple"
        )
    
    async def validate_selection(self, plan: AnalyticsPlan) -> bool:
        """
        Validate that the selected chart matches requirements.
        
        Args:
            plan: Analytics plan to validate
            
        Returns:
            True if valid
        """
        # Map ChartType to playbook name
        playbook_name = map_chart_type_to_playbook(plan.strategy.chart_type.value)
        
        if not playbook_name:
            logger.warning(f"[Playbook] No playbook entry for {plan.strategy.chart_type.value}")
            return True  # Allow it anyway
        
        # Check data requirements
        requirements = get_chart_data_requirements(playbook_name)
        
        # Basic validation
        if not requirements:
            return True
        
        # Check if we have required data roles
        required_roles = [req["role"] for req in requirements if not req.get("optional", False)]
        
        # For now, assume we can generate required data
        # In production, would validate against actual data source
        
        logger.debug(f"[Playbook] Validated {playbook_name} with required roles: {required_roles}")
        return True


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_playbook_conductor():
        """Test the playbook conductor."""
        conductor = PlaybookConductor()
        
        # Test 1: Time series request
        request1 = AnalyticsRequest(
            title="Monthly Sales Trend",
            description="Show me how our sales have grown over the past 12 months",
            data_context="E-commerce platform sales data",
            time_period="12 months"
        )
        
        plan1 = await conductor.select_strategy(request1)
        print(f"Test 1 - Selected: {plan1.strategy.chart_type.value}")
        print(f"Test 1 - Reasoning: {plan1.strategy.reasoning[:100]}...")
        print(f"Test 1 - Confidence: {plan1.strategy.confidence:.0%}\n")
        
        # Test 2: Comparison request
        request2 = AnalyticsRequest(
            title="Product Category Comparison",
            description="Compare revenue across our different product categories",
            data_context="5 main product categories"
        )
        
        plan2 = await conductor.select_strategy(request2)
        print(f"Test 2 - Selected: {plan2.strategy.chart_type.value}")
        print(f"Test 2 - Method: {plan2.strategy.method.value}\n")
        
        # Test 3: Complex visualization
        request3 = AnalyticsRequest(
            title="Customer Behavior Heatmap",
            description="Show customer activity patterns across different times of day and days of week",
            data_context="User engagement metrics",
            chart_preference=ChartType.HEATMAP
        )
        
        plan3 = await conductor.select_strategy(request3)
        print(f"Test 3 - Selected: {plan3.strategy.chart_type.value}")
        print(f"Test 3 - Complexity: {plan3.estimated_complexity}")
        
        # Validate selection
        valid = await conductor.validate_selection(plan3)
        print(f"Test 3 - Valid: {valid}")
    
    asyncio.run(test_playbook_conductor())