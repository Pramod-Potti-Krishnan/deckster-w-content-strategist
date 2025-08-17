"""
Playbook-Based Data Synthesizer
================================

Enhanced data synthesis using playbook specifications.
Generates data tailored to specific chart requirements.

Key Features:
- Uses playbook synthetic_data_features
- Chart-specific data patterns
- Intelligent distribution selection
- Realistic data generation

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import logging
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

from .models import (
    AnalyticsRequest,
    ChartType,
    DataPoint,
    SyntheticDataConfig
)
from .analytics_playbook import (
    get_chart_synthetic_features,
    map_chart_type_to_playbook,
    get_chart_data_requirements
)

logger = logging.getLogger(__name__)


class DataSynthesizer:
    """
    Enhanced data synthesizer that uses playbook specifications
    to generate chart-specific synthetic data.
    """
    
    def __init__(self):
        """Initialize the playbook synthesizer."""
        self.random_state = random.Random(42)
        self.np_random = np.random.RandomState(42)
        
    async def generate_synthetic_data(
        self,
        request: AnalyticsRequest,
        config: SyntheticDataConfig,
        chart_type: ChartType
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """
        Generate synthetic data using playbook specifications.
        
        Args:
            request: Analytics request
            config: Data configuration from conductor
            chart_type: Selected chart type
            
        Returns:
            Tuple of (data_points, description, insights)
        """
        logger.info(f"[Playbook Synthesizer] Generating data for {chart_type.value}")
        
        # Get playbook specifications
        playbook_name = map_chart_type_to_playbook(chart_type.value)
        if not playbook_name:
            logger.warning(f"No playbook entry for {chart_type.value}, using default generation")
            return await self._generate_default_data(request, config, chart_type)
        
        features = get_chart_synthetic_features(playbook_name)
        requirements = get_chart_data_requirements(playbook_name)
        
        # Generate based on chart type
        generator_map = {
            "line_chart": self._generate_time_series_data,
            "bar_chart_vertical": self._generate_categorical_data,
            "bar_chart_horizontal": self._generate_categorical_data,
            "pie_chart": self._generate_proportional_data,
            "scatter_plot": self._generate_correlation_data,
            "histogram": self._generate_distribution_data,
            "heatmap": self._generate_matrix_data,
            "area_chart": self._generate_cumulative_data,
            "stacked_area_chart": self._generate_stacked_time_data,
            "grouped_bar_chart": self._generate_grouped_data,
            "stacked_bar_chart": self._generate_stacked_categorical_data,
            "box_plot": self._generate_grouped_distribution_data,
            "bubble_chart": self._generate_three_dimensional_data,
            "waterfall": self._generate_waterfall_data,
            "radar_chart": self._generate_multidimensional_data,
            "gantt": self._generate_timeline_data,
            "funnel": self._generate_funnel_data,
            "pareto": self._generate_pareto_data,
            "control_chart": self._generate_process_data,
            "step_chart": self._generate_step_data,
            "violin_plot": self._generate_multimodal_data,
            "hexbin": self._generate_dense_scatter_data,
            "error_bar_chart": self._generate_error_data
        }
        
        generator = generator_map.get(playbook_name, self._generate_default_data)
        return await generator(request, features, requirements)
    
    async def _generate_time_series_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate time series data for line/area charts."""
        rows = features.get("rows", 100)
        num_series = features.get("num_series", 1)
        frequency = features.get("x_frequency", "daily")
        pattern = features.get("y_pattern", "linear_trend")
        
        # Generate time points
        start_date = datetime.now() - timedelta(days=rows)
        dates = [start_date + timedelta(days=i) for i in range(rows)]
        
        data_points = []
        insights = []
        
        # Generate values based on pattern
        if "trend" in pattern:
            base_value = 100
            trend = 0.5  # Daily growth
            values = [base_value + trend * i + self.np_random.normal(0, 5) for i in range(rows)]
            insights.append(f"Shows {trend*rows:.1f}% growth over period")
        elif "seasonal" in pattern:
            values = [50 + 30 * np.sin(2 * np.pi * i / 30) + self.np_random.normal(0, 3) for i in range(rows)]
            insights.append("Clear seasonal pattern with 30-day cycle")
        else:
            values = [self.np_random.uniform(50, 150) for _ in range(rows)]
        
        # Add anomalies if specified
        if "anomalies" in features:
            anomaly_count = features["anomalies"].get("count", 3)
            for _ in range(anomaly_count):
                idx = self.random_state.randint(10, rows - 10)
                values[idx] *= features["anomalies"].get("magnitude", 2)
                insights.append(f"Anomaly detected at day {idx}")
        
        # Create data points
        for i, (date, value) in enumerate(zip(dates, values)):
            data_points.append(DataPoint(
                label=date.strftime("%Y-%m-%d"),
                value=round(value, 2),
                metadata={"series": "main", "index": i}
            ))
        
        description = f"Time series data with {rows} {frequency} points showing {pattern}"
        
        # Add trend insight
        if len(values) > 1:
            trend_direction = "upward" if values[-1] > values[0] else "downward"
            change_pct = ((values[-1] - values[0]) / values[0]) * 100
            insights.append(f"{trend_direction.capitalize()} trend: {abs(change_pct):.1f}% change")
        
        return data_points, description, insights
    
    async def _generate_categorical_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate categorical data for bar charts."""
        num_categories = features.get("num_categories", 8)
        distribution = features.get("value_distribution", "uniform")
        
        # Generate category names
        if "product" in request.data_context.lower():
            categories = [f"Product {chr(65+i)}" for i in range(num_categories)]
        elif "region" in request.data_context.lower():
            regions = ["North", "South", "East", "West", "Central", "Northeast", "Northwest", "Southeast"]
            categories = regions[:num_categories]
        elif "department" in request.data_context.lower():
            departments = ["Sales", "Marketing", "Engineering", "HR", "Finance", "Operations", "Support", "Legal"]
            categories = departments[:num_categories]
        else:
            categories = [f"Category {i+1}" for i in range(num_categories)]
        
        # Generate values based on distribution
        if "lognormal" in distribution:
            values = self.np_random.lognormal(3, 1, num_categories) * 10
        elif "exponential" in distribution:
            values = self.np_random.exponential(50, num_categories)
        elif "normal" in distribution:
            values = self.np_random.normal(100, 20, num_categories)
        else:  # uniform
            values = self.np_random.uniform(50, 150, num_categories)
        
        # Sort if specified
        if features.get("sorted", False):
            sorted_pairs = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)
            categories, values = zip(*sorted_pairs)
        
        # Create data points
        data_points = []
        insights = []
        
        for category, value in zip(categories, values):
            data_points.append(DataPoint(
                label=category,
                value=round(value, 2),
                metadata={"type": "category"}
            ))
        
        # Generate insights
        max_idx = np.argmax(values)
        min_idx = np.argmin(values)
        insights.append(f"Highest: {categories[max_idx]} ({values[max_idx]:.1f})")
        insights.append(f"Lowest: {categories[min_idx]} ({values[min_idx]:.1f})")
        
        if len(values) > 3:
            top_3_sum = sum(sorted(values, reverse=True)[:3])
            total = sum(values)
            insights.append(f"Top 3 account for {(top_3_sum/total)*100:.1f}% of total")
        
        description = f"Categorical data with {num_categories} categories"
        
        return data_points, description, insights
    
    async def _generate_proportional_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate proportional data for pie charts."""
        num_slices = features.get("num_slices", 4)
        
        # Generate proportions using Dirichlet distribution
        proportions = self.np_random.dirichlet(np.ones(num_slices) * 2)
        
        # Scale to percentages
        percentages = proportions * 100
        
        # Ensure minimum slice size
        min_slice = features.get("min_slice_percent", 5)
        percentages = np.maximum(percentages, min_slice)
        percentages = (percentages / percentages.sum()) * 100
        
        # Generate labels
        if "market" in request.data_context.lower():
            labels = [f"Segment {chr(65+i)}" for i in range(num_slices)]
        else:
            labels = [f"Category {i+1}" for i in range(num_slices)]
        
        # Create data points
        data_points = []
        insights = []
        
        for label, percentage in zip(labels, percentages):
            data_points.append(DataPoint(
                label=label,
                value=round(percentage, 1),
                metadata={"type": "percentage"}
            ))
        
        # Generate insights
        dominant_idx = np.argmax(percentages)
        insights.append(f"{labels[dominant_idx]} dominates with {percentages[dominant_idx]:.1f}%")
        
        if num_slices > 2:
            top_2_sum = sum(sorted(percentages, reverse=True)[:2])
            insights.append(f"Top 2 segments: {top_2_sum:.1f}% of total")
        
        description = f"Proportional data with {num_slices} segments summing to 100%"
        
        return data_points, description, insights
    
    async def _generate_correlation_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate correlation data for scatter plots."""
        n = features.get("n", 400)
        correlation = features.get("correlation", 0.6)
        
        # Generate correlated data
        mean = [50, 50]
        cov = [[100, correlation * 100], [correlation * 100, 100]]
        x, y = self.np_random.multivariate_normal(mean, cov, n).T
        
        # Add outliers
        outliers = features.get("outliers", {})
        outlier_count = outliers.get("count", 6)
        for _ in range(outlier_count):
            idx = self.random_state.randint(0, n-1)
            x[idx] += self.np_random.normal(0, 40)
            y[idx] += self.np_random.normal(0, 40)
        
        # Create data points
        data_points = []
        insights = []
        
        for xi, yi in zip(x, y):
            data_points.append(DataPoint(
                label=f"Point",
                value=round(yi, 2),
                metadata={"x": round(xi, 2), "y": round(yi, 2)}
            ))
        
        # Calculate actual correlation
        actual_corr = np.corrcoef(x, y)[0, 1]
        insights.append(f"Correlation coefficient: {actual_corr:.2f}")
        
        # Identify clusters or patterns
        if actual_corr > 0.7:
            insights.append("Strong positive correlation observed")
        elif actual_corr < -0.7:
            insights.append("Strong negative correlation observed")
        else:
            insights.append("Moderate correlation with some scatter")
        
        description = f"Scatter plot data with {n} points, correlation={correlation:.2f}"
        
        return data_points, description, insights
    
    async def _generate_distribution_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate distribution data for histograms."""
        n = features.get("n", 1000)
        distribution = features.get("distribution", "normal")
        
        # Generate based on distribution type
        if "lognormal" in distribution:
            values = self.np_random.lognormal(3, 0.5, n)
            dist_name = "log-normal"
        elif "mixture" in distribution:
            # Bimodal distribution
            values1 = self.np_random.normal(30, 5, n // 2)
            values2 = self.np_random.normal(70, 5, n // 2)
            values = np.concatenate([values1, values2])
            dist_name = "bimodal"
        else:  # normal
            values = self.np_random.normal(50, 15, n)
            dist_name = "normal"
        
        # Create histogram bins
        hist, bin_edges = np.histogram(values, bins=20)
        
        data_points = []
        insights = []
        
        for i, (count, edge) in enumerate(zip(hist, bin_edges[:-1])):
            data_points.append(DataPoint(
                label=f"{edge:.1f}-{bin_edges[i+1]:.1f}",
                value=int(count),
                metadata={"bin_start": edge, "bin_end": bin_edges[i+1]}
            ))
        
        # Generate insights
        insights.append(f"Distribution: {dist_name}")
        insights.append(f"Mean: {np.mean(values):.1f}, Median: {np.median(values):.1f}")
        insights.append(f"Std Dev: {np.std(values):.1f}")
        
        skewness = (np.mean(values) - np.median(values)) / np.std(values)
        if abs(skewness) > 0.5:
            insights.append(f"{'Right' if skewness > 0 else 'Left'}-skewed distribution")
        
        description = f"{dist_name.capitalize()} distribution with {n} samples"
        
        return data_points, description, insights
    
    async def _generate_matrix_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate matrix data for heatmaps."""
        shape = features.get("shape", [12, 10])
        rows, cols = shape
        
        # Generate matrix with structure
        structure = features.get("row_col_structure", "random")
        
        if "block" in structure:
            # Block pattern
            matrix = np.zeros((rows, cols))
            for i in range(0, rows, 3):
                for j in range(0, cols, 3):
                    block_value = self.np_random.uniform(0, 100)
                    matrix[i:i+3, j:j+3] = block_value + self.np_random.normal(0, 10, (3, 3))
        else:
            # Random with some correlation
            matrix = self.np_random.normal(50, 20, (rows, cols))
        
        # Create data points
        data_points = []
        insights = []
        
        row_labels = [f"Row{i+1}" for i in range(rows)]
        col_labels = [f"Col{i+1}" for i in range(cols)]
        
        for i, row_label in enumerate(row_labels):
            for j, col_label in enumerate(col_labels):
                data_points.append(DataPoint(
                    label=f"{row_label}-{col_label}",
                    value=round(matrix[i, j], 2),
                    metadata={"row": i, "col": j, "row_label": row_label, "col_label": col_label}
                ))
        
        # Generate insights
        max_val = np.max(matrix)
        min_val = np.min(matrix)
        max_pos = np.unravel_index(np.argmax(matrix), matrix.shape)
        
        insights.append(f"Highest value: {max_val:.1f} at {row_labels[max_pos[0]]}, {col_labels[max_pos[1]]}")
        insights.append(f"Value range: {min_val:.1f} to {max_val:.1f}")
        
        # Check for patterns
        row_means = np.mean(matrix, axis=1)
        if np.std(row_means) > 10:
            insights.append("Significant variation across rows detected")
        
        description = f"Matrix data ({rows}x{cols}) for heatmap visualization"
        
        return data_points, description, insights
    
    async def _generate_default_data(
        self,
        request: AnalyticsRequest,
        config: SyntheticDataConfig,
        chart_type: ChartType
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Fallback to default data generation."""
        data_points = []
        insights = []
        
        # Simple random data
        for i in range(config.num_points):
            value = self.np_random.uniform(config.value_range[0], config.value_range[1])
            data_points.append(DataPoint(
                label=f"Item {i+1}",
                value=round(value, 2),
                metadata={"index": i}
            ))
        
        description = f"Generated {config.num_points} data points for {chart_type.value}"
        insights.append(f"Data range: {config.value_range[0]} to {config.value_range[1]}")
        
        return data_points, description, insights
    
    # Additional specialized generators...
    
    async def _generate_cumulative_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate cumulative data for area charts."""
        rows = features.get("rows", 80)
        
        # Generate incremental values
        increments = self.np_random.exponential(5, rows)
        cumulative = np.cumsum(increments)
        
        data_points = []
        for i, value in enumerate(cumulative):
            data_points.append(DataPoint(
                label=f"Period {i+1}",
                value=round(value, 2),
                metadata={"cumulative": True, "increment": round(increments[i], 2)}
            ))
        
        insights = [
            f"Total accumulation: {cumulative[-1]:.1f}",
            f"Average increment: {np.mean(increments):.1f}"
        ]
        
        return data_points, f"Cumulative data over {rows} periods", insights
    
    async def _generate_waterfall_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate waterfall chart data."""
        num_stages = features.get("num_stages", 8)
        start_value = features.get("start_value", 1000)
        
        # Generate deltas
        deltas = self.np_random.normal(0, 150, num_stages)
        
        # Ensure slight negative bias if specified
        if features.get("balance_bias") == "slightly_negative":
            deltas -= 20
        
        # Calculate running totals
        running_total = start_value
        data_points = []
        
        # Add starting value
        data_points.append(DataPoint(
            label="Start",
            value=start_value,
            metadata={"type": "start", "running_total": running_total}
        ))
        
        # Add stages
        stage_names = [f"Stage {i+1}" for i in range(num_stages)]
        for stage, delta in zip(stage_names, deltas):
            running_total += delta
            data_points.append(DataPoint(
                label=stage,
                value=round(delta, 2),
                metadata={"type": "delta", "running_total": round(running_total, 2)}
            ))
        
        # Add ending value
        data_points.append(DataPoint(
            label="End",
            value=round(running_total, 2),
            metadata={"type": "end", "running_total": round(running_total, 2)}
        ))
        
        insights = [
            f"Net change: {running_total - start_value:.1f}",
            f"Percentage change: {((running_total - start_value) / start_value) * 100:.1f}%"
        ]
        
        return data_points, f"Waterfall chart with {num_stages} stages", insights
    
    async def _generate_stacked_time_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate stacked time series data."""
        rows = features.get("rows", 52)
        num_series = features.get("num_series", 4)
        
        # Generate proportions that change over time
        data_points = []
        series_names = [f"Series {chr(65+i)}" for i in range(num_series)]
        
        for week in range(rows):
            # Use Dirichlet for proportions
            proportions = self.np_random.dirichlet(np.ones(num_series))
            total = 100 + week * 2  # Growing total
            
            for series, proportion in zip(series_names, proportions):
                data_points.append(DataPoint(
                    label=f"Week {week+1}",
                    value=round(proportion * total, 2),
                    metadata={"series": series, "week": week, "proportion": proportion}
                ))
        
        insights = [
            f"{num_series} series over {rows} weeks",
            "Shows changing composition over time"
        ]
        
        return data_points, f"Stacked area data", insights
    
    async def _generate_grouped_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate grouped bar chart data."""
        num_groups = features.get("num_groups", 6)
        num_subgroups = features.get("num_subgroups", 3)
        
        group_names = [f"Group {i+1}" for i in range(num_groups)]
        subgroup_names = [f"Type {chr(65+i)}" for i in range(num_subgroups)]
        
        data_points = []
        for group in group_names:
            base_value = self.np_random.uniform(50, 100)
            for subgroup in subgroup_names:
                value = base_value + self.np_random.normal(0, 15)
                data_points.append(DataPoint(
                    label=group,
                    value=round(value, 2),
                    metadata={"group": group, "subgroup": subgroup}
                ))
        
        insights = [f"{num_groups} groups with {num_subgroups} subgroups each"]
        
        return data_points, "Grouped comparison data", insights
    
    async def _generate_stacked_categorical_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate stacked bar chart data."""
        num_categories = features.get("num_categories", 7)
        num_segments = features.get("num_segments", 4)
        
        categories = [f"Category {i+1}" for i in range(num_categories)]
        segments = [f"Segment {chr(65+i)}" for i in range(num_segments)]
        
        data_points = []
        for category in categories:
            # Generate segment values
            total = self.np_random.uniform(100, 500)
            proportions = self.np_random.dirichlet(np.ones(num_segments))
            
            for segment, proportion in zip(segments, proportions):
                data_points.append(DataPoint(
                    label=category,
                    value=round(proportion * total, 2),
                    metadata={"category": category, "segment": segment}
                ))
        
        insights = [f"Composition across {num_categories} categories"]
        
        return data_points, "Stacked bar data", insights
    
    async def _generate_grouped_distribution_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate data for box plots."""
        num_groups = features.get("num_groups", 4)
        
        groups = [f"Group {chr(65+i)}" for i in range(num_groups)]
        data_points = []
        
        for i, group in enumerate(groups):
            # Different distribution for each group
            mean = 50 + i * 10
            std = 10 + i * 2
            values = self.np_random.normal(mean, std, 100)
            
            # Add some outliers
            outlier_count = int(100 * 0.03)
            outlier_indices = self.random_state.sample(range(100), outlier_count)
            for idx in outlier_indices:
                values[idx] = mean + self.random_state.choice([-1, 1]) * std * 3.5
            
            # Store distribution stats
            data_points.append(DataPoint(
                label=group,
                value=round(np.median(values), 2),
                metadata={
                    "group": group,
                    "values": values.tolist(),
                    "q1": round(np.percentile(values, 25), 2),
                    "q3": round(np.percentile(values, 75), 2),
                    "min": round(np.min(values), 2),
                    "max": round(np.max(values), 2),
                    "mean": round(np.mean(values), 2)
                }
            ))
        
        insights = [
            f"Comparing distributions across {num_groups} groups",
            "Shows median, quartiles, and outliers"
        ]
        
        return data_points, "Box plot distribution data", insights
    
    async def _generate_three_dimensional_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate bubble chart data (x, y, size)."""
        n = features.get("n", 200)
        
        # Generate three dimensions
        x_values = self.np_random.uniform(0, 100, n)
        y_values = self.np_random.uniform(0, 100, n)
        sizes = self.np_random.gamma(2, 20, n)
        
        data_points = []
        for i, (x, y, size) in enumerate(zip(x_values, y_values, sizes)):
            data_points.append(DataPoint(
                label=f"Entity {i+1}" if i < 10 else "",  # Label only top entities
                value=round(y, 2),
                metadata={"x": round(x, 2), "y": round(y, 2), "size": round(size, 2)}
            ))
        
        insights = [
            f"{n} data points with 3 dimensions",
            f"Size range: {np.min(sizes):.1f} to {np.max(sizes):.1f}"
        ]
        
        return data_points, "Bubble chart data", insights
    
    async def _generate_multidimensional_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate radar chart data."""
        num_metrics = features.get("num_metrics", 6)
        num_entities = features.get("num_entities", 3)
        
        metrics = [f"Metric {i+1}" for i in range(num_metrics)]
        entities = [f"Entity {chr(65+i)}" for i in range(num_entities)]
        
        data_points = []
        for entity in entities:
            # Generate normalized values for each metric
            values = self.np_random.uniform(20, 100, num_metrics)
            
            for metric, value in zip(metrics, values):
                data_points.append(DataPoint(
                    label=metric,
                    value=round(value, 2),
                    metadata={"entity": entity, "metric": metric, "normalized": True}
                ))
        
        insights = [
            f"Comparing {num_entities} entities across {num_metrics} dimensions",
            "All metrics normalized to 0-100 scale"
        ]
        
        return data_points, "Multi-dimensional comparison data", insights
    
    async def _generate_timeline_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate Gantt chart timeline data."""
        num_tasks = features.get("num_tasks", 12)
        
        tasks = [f"Task {i+1}" for i in range(num_tasks)]
        start_date = datetime.now()
        
        data_points = []
        current_date = start_date
        
        for task in tasks:
            # Random duration between 3 and 14 days
            duration = self.random_state.randint(3, 14)
            
            # Some overlap with previous tasks
            if self.random_state.random() < 0.4 and current_date > start_date:
                # Overlap by going back a few days
                task_start = current_date - timedelta(days=self.random_state.randint(1, 3))
            else:
                task_start = current_date
            
            data_points.append(DataPoint(
                label=task,
                value=duration,
                metadata={
                    "task": task,
                    "start": task_start.isoformat(),
                    "duration_days": duration,
                    "end": (task_start + timedelta(days=duration)).isoformat()
                }
            ))
            
            current_date = task_start + timedelta(days=duration - 2)  # Some overlap
        
        insights = [
            f"{num_tasks} tasks scheduled",
            f"Total timeline: {(current_date - start_date).days} days"
        ]
        
        return data_points, "Project timeline data", insights
    
    async def _generate_funnel_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate funnel chart data."""
        num_stages = features.get("num_stages", 6)
        start_count = features.get("start_count", 10000)
        
        stages = ["Awareness", "Interest", "Consideration", "Intent", "Purchase", "Loyalty"][:num_stages]
        
        # Generate conversion rates
        conversion_rates = [0.6, 0.7, 0.8, 0.75, 0.85, 0.9][:num_stages-1]
        
        data_points = []
        current_count = start_count
        
        for i, stage in enumerate(stages):
            data_points.append(DataPoint(
                label=stage,
                value=round(current_count, 0),
                metadata={
                    "stage": stage,
                    "percentage": round((current_count / start_count) * 100, 1),
                    "conversion_rate": conversion_rates[i] if i < len(conversion_rates) else None
                }
            ))
            
            if i < len(conversion_rates):
                current_count *= conversion_rates[i]
        
        overall_conversion = (data_points[-1].value / start_count) * 100
        
        insights = [
            f"Overall conversion rate: {overall_conversion:.1f}%",
            f"Biggest drop: {stages[0]} to {stages[1]}"
        ]
        
        return data_points, f"Funnel with {num_stages} stages", insights
    
    async def _generate_pareto_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate Pareto chart data."""
        num_categories = features.get("num_categories", 12)
        
        # Generate power law distribution
        values = self.np_random.pareto(1.5, num_categories) * 100
        values = np.sort(values)[::-1]  # Sort descending
        
        categories = [f"Cause {i+1}" for i in range(num_categories)]
        
        # Calculate cumulative percentages
        total = np.sum(values)
        cumulative = np.cumsum(values)
        cumulative_pct = (cumulative / total) * 100
        
        data_points = []
        vital_few_idx = None
        
        for i, (category, value) in enumerate(zip(categories, values)):
            data_points.append(DataPoint(
                label=category,
                value=round(value, 2),
                metadata={
                    "percentage": round((value / total) * 100, 1),
                    "cumulative_percentage": round(cumulative_pct[i], 1)
                }
            ))
            
            # Find 80% threshold
            if vital_few_idx is None and cumulative_pct[i] >= 80:
                vital_few_idx = i + 1
        
        insights = [
            f"Top {vital_few_idx} causes account for 80% of effects",
            f"Highest impact: {categories[0]} ({(values[0]/total)*100:.1f}%)"
        ]
        
        return data_points, "Pareto analysis data", insights
    
    async def _generate_process_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate control chart data."""
        rows = features.get("rows", 60)
        process_mean = features.get("process_mean", 50)
        process_sd = features.get("process_sd", 4)
        
        # Generate process data
        values = self.np_random.normal(process_mean, process_sd, rows)
        
        # Add special causes
        special_causes = features.get("special_causes", {})
        cause_count = special_causes.get("count", 4)
        for _ in range(cause_count):
            idx = self.random_state.randint(5, rows - 5)
            values[idx] = process_mean + self.random_state.choice([-1, 1]) * process_sd * 3.5
        
        # Calculate control limits
        ucl = process_mean + 3 * process_sd
        lcl = process_mean - 3 * process_sd
        
        data_points = []
        violations = 0
        
        for i, value in enumerate(values):
            is_violation = value > ucl or value < lcl
            if is_violation:
                violations += 1
            
            data_points.append(DataPoint(
                label=f"Sample {i+1}",
                value=round(value, 2),
                metadata={
                    "index": i,
                    "ucl": round(ucl, 2),
                    "lcl": round(lcl, 2),
                    "mean": round(process_mean, 2),
                    "violation": is_violation
                }
            ))
        
        insights = [
            f"Process mean: {process_mean:.1f} ± {process_sd:.1f}",
            f"Control limits: {lcl:.1f} to {ucl:.1f}",
            f"Violations detected: {violations}"
        ]
        
        return data_points, "Statistical process control data", insights
    
    async def _generate_step_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate step chart data."""
        rows = features.get("rows", 60)
        num_steps = features.get("num_steps", 6)
        
        # Generate step changes
        step_points = sorted(self.random_state.sample(range(1, rows), num_steps - 1))
        step_points = [0] + step_points + [rows]
        
        data_points = []
        current_value = 50
        
        for i in range(rows):
            # Check if we're at a step point
            for j in range(len(step_points) - 1):
                if step_points[j] <= i < step_points[j + 1]:
                    if i == step_points[j] and j > 0:
                        # Make a step change
                        current_value += self.np_random.uniform(-30, 30)
                    break
            
            data_points.append(DataPoint(
                label=f"Hour {i+1}",
                value=round(current_value, 2),
                metadata={"hour": i, "is_step": i in step_points}
            ))
        
        insights = [
            f"{num_steps} discrete level changes",
            f"Final level: {current_value:.1f}"
        ]
        
        return data_points, "Step function data", insights
    
    async def _generate_multimodal_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate multimodal distribution data for violin plots."""
        num_groups = features.get("num_groups", 3)
        n_per_group = features.get("n_per_group", 150)
        
        groups = [f"Group {chr(65+i)}" for i in range(num_groups)]
        data_points = []
        
        for group in groups:
            # Create multimodal distribution
            mode1 = self.np_random.normal(30, 5, n_per_group // 2)
            mode2 = self.np_random.normal(70, 7, n_per_group // 2)
            values = np.concatenate([mode1, mode2])
            
            # Store full distribution
            data_points.append(DataPoint(
                label=group,
                value=round(np.median(values), 2),
                metadata={
                    "group": group,
                    "values": values.tolist(),
                    "mean": round(np.mean(values), 2),
                    "std": round(np.std(values), 2),
                    "modes": [30, 70]  # Approximate mode centers
                }
            ))
        
        insights = [
            f"Bimodal distributions for {num_groups} groups",
            "Shows full distribution shape"
        ]
        
        return data_points, "Multimodal distribution data", insights
    
    async def _generate_dense_scatter_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate dense scatter data for hexbin plots."""
        n = features.get("n", 20000)
        num_clusters = features.get("clusters", 3)
        
        data_points = []
        all_x = []
        all_y = []
        
        # Generate clustered data
        for cluster in range(num_clusters):
            cluster_size = n // num_clusters
            center_x = self.np_random.uniform(20, 80)
            center_y = self.np_random.uniform(20, 80)
            spread = self.np_random.uniform(5, 15)
            
            x = self.np_random.normal(center_x, spread, cluster_size)
            y = self.np_random.normal(center_y, spread, cluster_size)
            
            all_x.extend(x)
            all_y.extend(y)
        
        # Add background noise
        noise_count = n - len(all_x)
        if noise_count > 0:
            all_x.extend(self.np_random.uniform(0, 100, noise_count))
            all_y.extend(self.np_random.uniform(0, 100, noise_count))
        
        # Sample for data points (too many to store all)
        sample_size = min(1000, n)
        sample_indices = self.random_state.sample(range(len(all_x)), sample_size)
        
        for idx in sample_indices:
            data_points.append(DataPoint(
                label="",
                value=round(all_y[idx], 2),
                metadata={"x": round(all_x[idx], 2), "y": round(all_y[idx], 2)}
            ))
        
        insights = [
            f"Dense scatter with {n} points",
            f"{num_clusters} main clusters identified"
        ]
        
        return data_points, "High-density 2D data", insights
    
    async def _generate_error_data(
        self,
        request: AnalyticsRequest,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate error bar data."""
        num_points = features.get("num_points", 10)
        
        # Generate means and errors
        x_values = list(range(1, num_points + 1))
        means = self.np_random.uniform(20, 80, num_points)
        errors = self.np_random.uniform(2, 10, num_points)
        
        data_points = []
        for x, mean, error in zip(x_values, means, errors):
            data_points.append(DataPoint(
                label=f"Point {x}",
                value=round(mean, 2),
                metadata={
                    "x": x,
                    "mean": round(mean, 2),
                    "error": round(error, 2),
                    "lower": round(mean - error, 2),
                    "upper": round(mean + error, 2),
                    "confidence": 0.95
                }
            ))
        
        insights = [
            f"{num_points} measurements with error bars",
            "95% confidence intervals shown"
        ]
        
        return data_points, "Measurements with uncertainty", insights


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_playbook_synthesizer():
        """Test the playbook synthesizer."""
        synthesizer = PlaybookSynthesizer()
        
        # Test 1: Line chart data
        request1 = AnalyticsRequest(
            title="Sales Trend",
            description="Monthly sales over the past year",
            data_context="E-commerce sales data"
        )
        
        config1 = SyntheticDataConfig(num_points=12)
        data1, desc1, insights1 = await synthesizer.generate_synthetic_data(
            request1, config1, ChartType.LINE
        )
        
        print(f"Test 1 - Generated {len(data1)} points")
        print(f"Description: {desc1}")
        print(f"Insights: {insights1}\n")
        
        # Test 2: Heatmap data
        request2 = AnalyticsRequest(
            title="Activity Heatmap",
            description="User activity by hour and day",
            data_context="App usage patterns"
        )
        
        config2 = SyntheticDataConfig()
        data2, desc2, insights2 = await synthesizer.generate_synthetic_data(
            request2, config2, ChartType.HEATMAP
        )
        
        print(f"Test 2 - Generated {len(data2)} points")
        print(f"First few points: {[dp.label for dp in data2[:3]]}")
        
        # Test 3: Scatter plot data
        request3 = AnalyticsRequest(
            title="Price vs Performance",
            description="Correlation between price and performance metrics",
            data_context="Product analysis"
        )
        
        config3 = SyntheticDataConfig()
        data3, desc3, insights3 = await synthesizer.generate_synthetic_data(
            request3, config3, ChartType.SCATTER
        )
        
        print(f"\nTest 3 - Generated {len(data3)} points")
        print(f"Insights: {insights3}")
    
    asyncio.run(test_playbook_synthesizer())