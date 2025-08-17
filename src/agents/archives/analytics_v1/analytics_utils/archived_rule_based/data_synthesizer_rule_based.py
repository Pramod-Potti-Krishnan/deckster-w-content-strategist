"""
Data Synthesizer for Analytics
===============================

Generates realistic synthetic data for charts using LLM and statistical methods.
Creates contextually appropriate data with trends, seasonality, and variations.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import logging
import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field

from src.utils.model_utils import create_model_with_fallback
from .models import (
    DataPoint,
    SyntheticDataConfig,
    AnalyticsRequest,
    ChartType,
    DataInsight
)
from .data_parser import DataParser, ParsedDataPoint

logger = logging.getLogger(__name__)


class DataGenerationContext(BaseModel):
    """Context for data generation."""
    description: str
    context: str
    num_points: int
    time_period: Optional[str]
    expected_range: Optional[Dict[str, float]]


class GeneratedDataset(BaseModel):
    """LLM-generated dataset with metadata."""
    data_points: List[Dict[str, Any]] = Field(
        description="List of data points with labels and values"
    )
    description: str = Field(
        description="Natural language description of the data"
    )
    insights: List[str] = Field(
        description="Key insights from the data",
        default_factory=list
    )
    trend_description: str = Field(
        description="Description of the overall trend",
        default=""
    )


class DataSynthesizer:
    """
    Synthesizes realistic data for analytics visualizations.
    Combines LLM intelligence with statistical methods.
    """
    
    def __init__(self):
        """Initialize the data synthesizer."""
        self.agent = self._create_agent()
        self.random_seed = None
        self.data_parser = DataParser()
        
    def _create_agent(self) -> Agent:
        """Create the pydantic_ai agent for data generation."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            result_type=GeneratedDataset,
            system_prompt="""You are a data analyst expert who generates realistic synthetic data.
            Create data that:
            1. Matches the context and description provided
            2. Shows realistic patterns, trends, and variations
            3. Includes appropriate labels for the data points
            4. Follows statistical distributions found in real-world data
            5. Provides meaningful insights based on the generated data
            
            Consider:
            - Business cycles and seasonality
            - Growth patterns and market dynamics
            - Random variations but with logical constraints
            - Industry-specific benchmarks and ranges
            
            Generate data that tells a coherent story."""
        )
    
    def set_seed(self, seed: int):
        """Set random seed for reproducibility."""
        self.random_seed = seed
        random.seed(seed)
        np.random.seed(seed)
    
    def _generate_time_labels(self, num_points: int, time_period: Optional[str]) -> List[str]:
        """
        Generate time-based labels.
        
        Args:
            num_points: Number of time points
            time_period: Description of time period
            
        Returns:
            List of time labels
        """
        if not time_period:
            time_period = "months"
        
        time_period_lower = time_period.lower()
        
        if 'quarter' in time_period_lower:
            quarters = ['Q1', 'Q2', 'Q3', 'Q4']
            years = []
            current_year = 2024
            
            while len(years) < num_points:
                for q in quarters:
                    if len(years) < num_points:
                        years.append(f"{q} {current_year}")
                current_year += 1
            return years[:num_points]
            
        elif 'month' in time_period_lower:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            if num_points <= 12:
                return months[:num_points]
            else:
                # Add year for multi-year data
                labels = []
                year = 2024
                for i in range(num_points):
                    month_idx = i % 12
                    if i > 0 and month_idx == 0:
                        year += 1
                    labels.append(f"{months[month_idx]} {year}")
                return labels
                
        elif 'week' in time_period_lower:
            return [f"Week {i+1}" for i in range(num_points)]
            
        elif 'day' in time_period_lower:
            start_date = datetime.now() - timedelta(days=num_points-1)
            labels = []
            for i in range(num_points):
                date = start_date + timedelta(days=i)
                labels.append(date.strftime("%m/%d"))
            return labels
            
        elif 'year' in time_period_lower:
            current_year = 2024
            return [str(current_year - num_points + i + 1) for i in range(num_points)]
            
        else:
            # Generic labels
            return [f"Period {i+1}" for i in range(num_points)]
    
    def _generate_categorical_labels(self, num_points: int, context: str) -> List[str]:
        """
        Generate categorical labels based on context.
        
        Args:
            num_points: Number of categories
            context: Context description
            
        Returns:
            List of category labels
        """
        context_lower = context.lower()
        
        # Product categories
        if 'product' in context_lower:
            products = ['Electronics', 'Clothing', 'Food & Beverage', 'Home & Garden', 
                       'Sports', 'Books', 'Toys', 'Health', 'Automotive', 'Beauty']
            return products[:num_points]
        
        # Department/team categories
        elif 'department' in context_lower or 'team' in context_lower:
            departments = ['Sales', 'Marketing', 'Engineering', 'Support', 'HR', 
                          'Finance', 'Operations', 'R&D', 'Legal', 'IT']
            return departments[:num_points]
        
        # Regional categories
        elif 'region' in context_lower or 'location' in context_lower:
            regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 
                      'Middle East', 'Africa', 'Australia', 'Eastern Europe', 
                      'Southeast Asia', 'Nordic']
            return regions[:num_points]
        
        # Customer segments
        elif 'customer' in context_lower or 'segment' in context_lower:
            segments = ['Enterprise', 'SMB', 'Startup', 'Individual', 'Government', 
                       'Education', 'Non-profit', 'Healthcare', 'Retail', 'Financial']
            return segments[:num_points]
        
        else:
            # Generic categories
            return [f"Category {chr(65+i)}" for i in range(num_points)]
    
    def _apply_trend(self, base_values: List[float], trend: str, strength: float = 0.3) -> List[float]:
        """
        Apply a trend to base values.
        
        Args:
            base_values: Initial values
            trend: Trend type
            strength: Trend strength (0-1)
            
        Returns:
            Values with trend applied
        """
        n = len(base_values)
        
        if trend == "increasing":
            # Linear growth with some variation
            trend_line = np.linspace(0, strength * np.mean(base_values), n)
            return [v + t for v, t in zip(base_values, trend_line)]
            
        elif trend == "decreasing":
            # Linear decline
            trend_line = np.linspace(strength * np.mean(base_values), 0, n)
            return [v + t for v, t in zip(base_values, trend_line)]
            
        elif trend == "cyclic":
            # Sinusoidal pattern
            cycle = np.sin(np.linspace(0, 2 * np.pi, n))
            amplitude = strength * np.mean(base_values) * 0.5
            return [v + amplitude * c for v, c in zip(base_values, cycle)]
            
        else:  # stable
            return base_values
    
    def _add_seasonality(self, values: List[float], period: int = 4) -> List[float]:
        """
        Add seasonal patterns to values.
        
        Args:
            values: Base values
            period: Seasonal period
            
        Returns:
            Values with seasonality
        """
        n = len(values)
        seasonal_pattern = []
        
        # Create a seasonal multiplier pattern
        season_multipliers = [1.1, 0.95, 1.05, 0.9]  # Example: quarterly seasonality
        
        for i in range(n):
            season_idx = i % period
            multiplier = season_multipliers[season_idx % len(season_multipliers)]
            seasonal_pattern.append(values[i] * multiplier)
        
        return seasonal_pattern
    
    def _add_noise(self, values: List[float], noise_level: float) -> List[float]:
        """
        Add random noise to values.
        
        Args:
            values: Base values
            noise_level: Amount of noise (0-1)
            
        Returns:
            Values with noise
        """
        if noise_level <= 0:
            return values
        
        noisy_values = []
        for v in values:
            noise = np.random.normal(0, v * noise_level * 0.1)
            noisy_values.append(max(0, v + noise))  # Ensure non-negative
        
        return noisy_values
    
    def _add_outliers(self, values: List[float], outlier_probability: float = 0.05) -> List[float]:
        """
        Add occasional outliers to values.
        
        Args:
            values: Base values
            outlier_probability: Probability of outlier
            
        Returns:
            Values with potential outliers
        """
        result = []
        for v in values:
            if random.random() < outlier_probability:
                # Create an outlier (50-150% deviation)
                multiplier = random.uniform(0.5, 1.5) if random.random() < 0.5 else random.uniform(1.5, 2.5)
                result.append(v * multiplier)
            else:
                result.append(v)
        return result
    
    def _generate_base_values(self, num_points: int, min_val: float, max_val: float) -> List[float]:
        """
        Generate base values within a range.
        
        Args:
            num_points: Number of values
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            List of base values
        """
        # Use a mix of distributions for more realistic data
        distribution_type = random.choice(['uniform', 'normal', 'skewed'])
        
        if distribution_type == 'uniform':
            values = np.random.uniform(min_val, max_val, num_points)
        elif distribution_type == 'normal':
            mean = (min_val + max_val) / 2
            std = (max_val - min_val) / 6  # 99.7% within range
            values = np.random.normal(mean, std, num_points)
            values = np.clip(values, min_val, max_val)
        else:  # skewed
            # Beta distribution for skewed data
            values = np.random.beta(2, 5, num_points)
            values = min_val + values * (max_val - min_val)
        
        return values.tolist()
    
    def _extract_insights(self, data_points: List[DataPoint]) -> List[DataInsight]:
        """
        Extract insights from generated data.
        
        Args:
            data_points: Generated data points
            
        Returns:
            List of data insights
        """
        insights = []
        
        if not data_points:
            return insights
        
        values = [dp.value for dp in data_points]
        labels = [dp.label for dp in data_points]
        
        # Basic statistics
        mean_val = np.mean(values)
        std_val = np.std(values)
        min_val = min(values)
        max_val = max(values)
        
        # Trend analysis
        if len(values) > 3:
            first_half = np.mean(values[:len(values)//2])
            second_half = np.mean(values[len(values)//2:])
            
            if second_half > first_half * 1.1:
                insights.append(DataInsight(
                    type="trend",
                    description=f"Upward trend detected: {((second_half/first_half - 1) * 100):.1f}% increase",
                    confidence=0.8,
                    supporting_data={"first_half_avg": first_half, "second_half_avg": second_half}
                ))
            elif second_half < first_half * 0.9:
                insights.append(DataInsight(
                    type="trend",
                    description=f"Downward trend detected: {((1 - second_half/first_half) * 100):.1f}% decrease",
                    confidence=0.8,
                    supporting_data={"first_half_avg": first_half, "second_half_avg": second_half}
                ))
        
        # Find outliers
        if std_val > 0:
            for i, (label, value) in enumerate(zip(labels, values)):
                z_score = abs((value - mean_val) / std_val)
                if z_score > 2:
                    insights.append(DataInsight(
                        type="outlier",
                        description=f"{label} is an outlier with value {value:.2f}",
                        confidence=min(0.9, z_score / 3),
                        supporting_data={"value": value, "z_score": z_score}
                    ))
        
        # Peak and trough
        max_idx = values.index(max_val)
        min_idx = values.index(min_val)
        
        insights.append(DataInsight(
            type="comparison",
            description=f"Peak at {labels[max_idx]} ({max_val:.2f}), lowest at {labels[min_idx]} ({min_val:.2f})",
            confidence=1.0,
            supporting_data={"peak": {"label": labels[max_idx], "value": max_val},
                           "trough": {"label": labels[min_idx], "value": min_val}}
        ))
        
        return insights
    
    async def generate_synthetic_data(
        self,
        request: AnalyticsRequest,
        config: SyntheticDataConfig,
        chart_type: ChartType
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """
        Generate synthetic data for the analytics request.
        
        Args:
            request: Analytics request
            config: Data generation configuration
            chart_type: Type of chart
            
        Returns:
            Tuple of (data points, description, insights)
        """
        logger.info(f"Generating synthetic data for {request.title}")
        
        # First, try to parse specific data from the request
        # Note: description and data_context are the same, so only use one
        parsed_points = self.data_parser.parse_data_points(request.description)
        
        # Special handling for histograms - generate distribution data
        if chart_type == ChartType.HISTOGRAM and ('mean' in request.description.lower() or 'distribution' in request.description.lower()):
            # Extract parameters from description
            import re
            mean_match = re.search(r'mean\s+(?:age\s+)?(\d+)', request.description.lower())
            std_match = re.search(r'std(?:dev|deviation)?\s+(\d+)', request.description.lower())
            samples_match = re.search(r'(\d+)\s+(?:customers|samples|records)', request.description.lower())
            
            mean_val = float(mean_match.group(1)) if mean_match else 50
            std_val = float(std_match.group(1)) if std_match else 10
            num_samples = int(samples_match.group(1)) if samples_match else 500
            
            logger.info(f"Generating histogram distribution: mean={mean_val}, std={std_val}, samples={num_samples}")
            
            # Generate normally distributed data
            np.random.seed(42)  # For reproducibility
            distribution_data = np.random.normal(mean_val, std_val, num_samples)
            
            # Create data points from the distribution
            data_points = []
            for i, value in enumerate(distribution_data):
                data_points.append(DataPoint(
                    label=f"Sample {i+1}",
                    value=max(0, value)  # Ensure non-negative
                ))
            
            description = f"Generated {num_samples} samples with mean {mean_val:.1f} and std deviation {std_val:.1f}"
            
            # Generate insights
            actual_mean = np.mean([dp.value for dp in data_points])
            actual_std = np.std([dp.value for dp in data_points])
            insights = [
                f"Actual mean: {actual_mean:.2f}",
                f"Actual std deviation: {actual_std:.2f}",
                f"Data range: {min(dp.value for dp in data_points):.2f} to {max(dp.value for dp in data_points):.2f}"
            ]
            
            return data_points, description, insights
        
        if parsed_points:
            logger.info(f"Using parsed data: {len(parsed_points)} points from user request")
            
            # Convert parsed points to DataPoint objects
            data_points = []
            for pp in parsed_points:
                data_points.append(DataPoint(
                    label=pp.label,
                    value=pp.value
                ))
            
            # Generate description based on parsed data
            description = f"Data extracted from user request for {request.title} showing "
            
            # Analyze the parsed data for trends
            values = [dp.value for dp in data_points]
            if len(values) > 3:
                first_val = values[0]
                last_val = values[-1]
                if last_val > first_val * 1.1:
                    description += f"an upward trend from {first_val:.2f} to {last_val:.2f}"
                elif last_val < first_val * 0.9:
                    description += f"a downward trend from {first_val:.2f} to {last_val:.2f}"
                else:
                    description += f"relatively stable values around {np.mean(values):.2f}"
            else:
                description += f"{len(data_points)} data points"
            
            # Extract insights from the actual data
            insight_objects = self._extract_insights(data_points)
            insights = [insight.description for insight in insight_objects[:3]]
            
            return data_points, description, insights
        
        # Determine value range
        min_val = config.min_value if config.min_value is not None else 0
        max_val = config.max_value if config.max_value is not None else 1000
        
        # Generate base values
        base_values = self._generate_base_values(config.num_points, min_val, max_val)
        
        # Apply trend
        if config.trend:
            base_values = self._apply_trend(base_values, config.trend)
        
        # Apply seasonality
        if config.seasonality:
            base_values = self._add_seasonality(base_values)
        
        # Add noise
        if config.noise_level > 0:
            base_values = self._add_noise(base_values, config.noise_level)
        
        # Add outliers
        if config.outliers:
            base_values = self._add_outliers(base_values)
        
        # Generate labels based on chart type and context
        if chart_type in [ChartType.LINE, ChartType.AREA] or request.time_period:
            labels = self._generate_time_labels(config.num_points, request.time_period)
        else:
            labels = self._generate_categorical_labels(config.num_points, request.data_context)
        
        # Create data points
        data_points = []
        for label, value in zip(labels, base_values):
            data_points.append(DataPoint(
                label=label,
                value=round(value, 2)
            ))
        
        # Generate description
        description = f"Synthetic data generated for {request.title} showing "
        if config.trend == "increasing":
            description += "an upward trend "
        elif config.trend == "decreasing":
            description += "a downward trend "
        elif config.trend == "cyclic":
            description += "cyclical patterns "
        else:
            description += "stable patterns "
        
        if config.seasonality:
            description += "with seasonal variations "
        
        description += f"across {config.num_points} data points."
        
        # Extract insights
        insight_objects = self._extract_insights(data_points)
        insights = [insight.description for insight in insight_objects[:3]]  # Top 3 insights
        
        logger.info(f"Generated {len(data_points)} data points with {len(insights)} insights")
        
        return data_points, description, insights
    
    async def generate_with_llm(
        self,
        request: AnalyticsRequest,
        config: SyntheticDataConfig
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """
        Generate synthetic data using LLM for more contextual accuracy.
        
        Args:
            request: Analytics request
            config: Data generation configuration
            
        Returns:
            Tuple of (data points, description, insights)
        """
        context = DataGenerationContext(
            description=request.description,
            context=request.data_context,
            num_points=config.num_points,
            time_period=request.time_period,
            expected_range=request.data_range
        )
        
        prompt = f"""
        Generate realistic synthetic data for this analytics request:
        
        Title: {request.title}
        Context: {request.data_context}
        Description: {request.description}
        Number of data points needed: {config.num_points}
        Time period: {request.time_period or 'Not specified'}
        
        Create {config.num_points} data points that:
        1. Are realistic for this business context
        2. Show {config.trend or 'natural'} trends
        3. Include appropriate labels (time periods or categories)
        4. Have values in a reasonable range for the context
        
        Provide insights about patterns, trends, or notable observations in the data.
        """
        
        try:
            result = await self.agent.run(prompt, deps=context)
            generated = result.data
            
            # Convert to DataPoint objects
            data_points = []
            for point in generated.data_points:
                data_points.append(DataPoint(
                    label=point.get('label', f"Point {len(data_points)+1}"),
                    value=float(point.get('value', 0))
                ))
            
            return data_points, generated.description, generated.insights
            
        except Exception as e:
            logger.warning(f"LLM data generation failed, using statistical method: {e}")
            # Fall back to statistical generation
            return await self.generate_synthetic_data(request, config, ChartType.BAR)