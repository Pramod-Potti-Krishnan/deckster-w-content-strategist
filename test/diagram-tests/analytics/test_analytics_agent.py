"""
Analytics Agent Test Suite
==========================

Comprehensive tests for the analytics generation system.
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.agents.analytics_agent import AnalyticsAgent, create_analytics
from src.agents.analytics_utils.models import (
    ChartType,
    AnalyticsRequest,
    GenerationMethod,
    DataDimension,
    SyntheticDataConfig
)
from src.agents.analytics_utils.conductor import AnalyticsConductor
from src.agents.analytics_utils.data_synthesizer import DataSynthesizer
from src.agents.analytics_utils.mermaid_chart_agent import MermaidChartAgent


class TestAnalyticsAgent:
    """Test the main analytics agent orchestrator."""
    
    @pytest.mark.asyncio
    async def test_simple_bar_chart_generation(self):
        """Test generating a simple bar chart."""
        result = await create_analytics(
            "Show quarterly sales data for 2024",
            title="Q1-Q4 2024 Sales"
        )
        
        assert result["success"]
        assert result["chart_type"] in ["bar", "line"]
        assert result["format"] in ["mermaid", "python_code"]
        assert len(result["data"]) > 0
    
    @pytest.mark.asyncio
    async def test_line_chart_with_trend(self):
        """Test generating a line chart with trend."""
        result = await create_analytics(
            "Display monthly revenue growth with upward trend",
            title="Revenue Growth",
            chart_type="line"
        )
        
        assert result["success"]
        assert result["chart_type"] == "line"
        assert "trend" in result["description"].lower() or len(result["insights"]) > 0
    
    @pytest.mark.asyncio
    async def test_pie_chart_generation(self):
        """Test generating a pie chart."""
        result = await create_analytics(
            "Show market share distribution among competitors",
            title="Market Share",
            chart_type="pie"
        )
        
        assert result["success"]
        assert result["chart_type"] == "pie"
        assert result["format"] == "mermaid"
        assert "pie" in result["content"].lower()
    
    @pytest.mark.asyncio
    async def test_complex_chart_fallback(self):
        """Test that complex charts fall back appropriately."""
        result = await create_analytics(
            "Create a heatmap of correlations",
            chart_type="heatmap"
        )
        
        assert result["success"] or "error" not in result["format"]
        if result["success"]:
            assert result["chart_type"] in ["heatmap", "bar"]  # May fallback
    
    @pytest.mark.asyncio
    async def test_theme_application(self):
        """Test applying custom theme."""
        theme = {
            "colors": {
                "primary": "#FF6B6B",
                "secondary": "#4ECDC4"
            },
            "style": "seaborn"
        }
        
        result = await create_analytics(
            "Show data with custom colors",
            theme=theme
        )
        
        assert result["success"]
        assert "metadata" in result


class TestConductor:
    """Test the analytics conductor strategy selection."""
    
    @pytest.mark.asyncio
    async def test_dimension_analysis(self):
        """Test data dimension identification."""
        conductor = AnalyticsConductor()
        
        # Test temporal dimension
        request = AnalyticsRequest(
            title="Test",
            description="Monthly sales data",
            data_context="sales over time"
        )
        dimension = conductor._analyze_data_dimension(request)
        assert dimension == DataDimension.TEMPORAL
        
        # Test categorical dimension
        request = AnalyticsRequest(
            title="Test",
            description="Sales by product category",
            data_context="product categories"
        )
        dimension = conductor._analyze_data_dimension(request)
        assert dimension == DataDimension.CATEGORICAL
    
    @pytest.mark.asyncio
    async def test_chart_type_selection(self):
        """Test appropriate chart type selection."""
        conductor = AnalyticsConductor()
        
        # Time series should suggest line chart
        request = AnalyticsRequest(
            title="Test",
            description="Revenue over time",
            data_context="monthly revenue",
            time_period="months"
        )
        plan = await conductor.select_strategy(request)
        assert plan.strategy.chart_type in [ChartType.LINE, ChartType.AREA, ChartType.BAR]
        
        # Proportions should suggest pie chart
        request = AnalyticsRequest(
            title="Test",
            description="Market share percentages",
            data_context="proportion of total market"
        )
        plan = await conductor.select_strategy(request)
        # May select pie or bar depending on analysis
        assert plan.strategy.chart_type in [ChartType.PIE, ChartType.BAR]
    
    @pytest.mark.asyncio
    async def test_method_selection(self):
        """Test generation method selection."""
        conductor = AnalyticsConductor()
        
        # Simple chart should use Mermaid
        request = AnalyticsRequest(
            title="Simple Bar Chart",
            description="Basic comparison",
            data_context="categories",
            chart_preference=ChartType.BAR
        )
        plan = await conductor.select_strategy(request)
        assert plan.strategy.method == GenerationMethod.MERMAID
        
        # Complex chart should use Python
        request = AnalyticsRequest(
            title="Heatmap",
            description="Correlation matrix",
            data_context="correlations",
            chart_preference=ChartType.HEATMAP
        )
        plan = await conductor.select_strategy(request)
        assert plan.strategy.method == GenerationMethod.PYTHON_MCP


class TestDataSynthesizer:
    """Test synthetic data generation."""
    
    @pytest.mark.asyncio
    async def test_basic_data_generation(self):
        """Test generating basic synthetic data."""
        synthesizer = DataSynthesizer()
        
        request = AnalyticsRequest(
            title="Test",
            description="Sales data",
            data_context="quarterly sales"
        )
        
        config = SyntheticDataConfig(
            num_points=4,
            trend="stable",
            noise_level=0.1
        )
        
        data_points, description, insights = await synthesizer.generate_synthetic_data(
            request,
            config,
            ChartType.BAR
        )
        
        assert len(data_points) == 4
        assert all(dp.label for dp in data_points)
        assert all(dp.value >= 0 for dp in data_points)
        assert description
    
    @pytest.mark.asyncio
    async def test_trend_generation(self):
        """Test generating data with trends."""
        synthesizer = DataSynthesizer()
        
        request = AnalyticsRequest(
            title="Growth",
            description="Revenue growth",
            data_context="monthly revenue"
        )
        
        # Test increasing trend
        config = SyntheticDataConfig(
            num_points=12,
            trend="increasing",
            noise_level=0.05
        )
        
        data_points, _, _ = await synthesizer.generate_synthetic_data(
            request,
            config,
            ChartType.LINE
        )
        
        values = [dp.value for dp in data_points]
        # Check general upward trend (last quarter avg > first quarter avg)
        first_quarter_avg = sum(values[:3]) / 3
        last_quarter_avg = sum(values[-3:]) / 3
        assert last_quarter_avg > first_quarter_avg
    
    @pytest.mark.asyncio
    async def test_seasonality_generation(self):
        """Test generating data with seasonality."""
        synthesizer = DataSynthesizer()
        
        request = AnalyticsRequest(
            title="Seasonal",
            description="Seasonal sales",
            data_context="quarterly sales with seasonality"
        )
        
        config = SyntheticDataConfig(
            num_points=12,
            trend="stable",
            seasonality=True,
            noise_level=0.05
        )
        
        data_points, description, _ = await synthesizer.generate_synthetic_data(
            request,
            config,
            ChartType.LINE
        )
        
        assert len(data_points) == 12
        assert "seasonal" in description.lower() or "stable" in description.lower()
    
    @pytest.mark.asyncio
    async def test_insight_extraction(self):
        """Test extracting insights from data."""
        synthesizer = DataSynthesizer()
        
        request = AnalyticsRequest(
            title="Test",
            description="Data for insights",
            data_context="sales data"
        )
        
        config = SyntheticDataConfig(
            num_points=10,
            trend="increasing",
            outliers=True
        )
        
        data_points, _, insights = await synthesizer.generate_synthetic_data(
            request,
            config,
            ChartType.BAR
        )
        
        assert len(insights) > 0
        # Should have insights about peaks/troughs at minimum
        assert any("peak" in i.lower() or "highest" in i.lower() for i in insights)


class TestMermaidChartAgent:
    """Test Mermaid chart generation."""
    
    @pytest.mark.asyncio
    async def test_line_chart_mermaid(self):
        """Test generating Mermaid line chart."""
        agent = MermaidChartAgent()
        
        from src.agents.analytics_utils.models import (
            DataPoint,
            AnalyticsPlan,
            ChartStrategy,
            MermaidChartConfig
        )
        
        # Create test data
        data_points = [
            DataPoint(label="Jan", value=100),
            DataPoint(label="Feb", value=120),
            DataPoint(label="Mar", value=140)
        ]
        
        # Create plan
        request = AnalyticsRequest(
            title="Test Line Chart",
            description="Test",
            data_context="Test"
        )
        
        strategy = ChartStrategy(
            method=GenerationMethod.MERMAID,
            chart_type=ChartType.LINE,
            confidence=0.9,
            reasoning="Test"
        )
        
        config = MermaidChartConfig(
            chart_type="xychart-beta"
        )
        
        plan = AnalyticsPlan(
            request=request,
            strategy=strategy,
            data_config=SyntheticDataConfig(),
            chart_config=config,
            estimated_complexity="simple"
        )
        
        output = await agent.generate_chart(
            plan,
            data_points,
            "Test data",
            ["Insight 1"]
        )
        
        assert output.chart_content
        assert "xychart-beta" in output.chart_content
        assert "line" in output.chart_content.lower()
        assert output.format == "mermaid"
    
    @pytest.mark.asyncio
    async def test_pie_chart_mermaid(self):
        """Test generating Mermaid pie chart."""
        agent = MermaidChartAgent()
        
        from src.agents.analytics_utils.models import DataPoint
        
        data_points = [
            DataPoint(label="Product A", value=45),
            DataPoint(label="Product B", value=30),
            DataPoint(label="Product C", value=25)
        ]
        
        mermaid_code = agent._generate_pie_chart(
            data_points,
            "Market Share",
            MermaidChartConfig(chart_type="pie")
        )
        
        assert "pie" in mermaid_code
        assert "Product A" in mermaid_code
        assert "45" in mermaid_code
    
    @pytest.mark.asyncio
    async def test_bar_chart_mermaid(self):
        """Test generating Mermaid bar chart."""
        agent = MermaidChartAgent()
        
        from src.agents.analytics_utils.models import DataPoint
        
        data_points = [
            DataPoint(label="Q1", value=100),
            DataPoint(label="Q2", value=150),
            DataPoint(label="Q3", value=120),
            DataPoint(label="Q4", value=180)
        ]
        
        mermaid_code = agent._generate_bar_chart(
            data_points,
            "Quarterly Sales",
            MermaidChartConfig(
                chart_type="xychart-beta",
                orientation="vertical"
            )
        )
        
        assert "xychart-beta" in mermaid_code
        assert "bar" in mermaid_code
        assert "Q1" in mermaid_code
        assert "180" in mermaid_code


def run_all_tests():
    """Run all analytics tests."""
    print("Running Analytics Agent Tests...")
    print("=" * 50)
    
    # Run pytest
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_all_tests()