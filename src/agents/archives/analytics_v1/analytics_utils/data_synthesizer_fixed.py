"""
Fixed Data Synthesizer
======================

Fixes for data generation including:
- Histogram raw values instead of frequency counts
- Array multiplication errors in anomaly generation
- Proper handling of feature parameters
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import numpy as np
import random

from .models import DataPoint

logger = logging.getLogger(__name__)


class FixedDataSynthesizer:
    """Fixed data synthesizer for chart generation."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the data synthesizer."""
        self.seed = seed or 42
        self.random_state = random.Random(self.seed)
        self.np_random = np.random.RandomState(self.seed)
        
    async def generate_data(
        self,
        chart_type: str,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """
        Generate synthetic data based on chart type.
        
        Args:
            chart_type: Type of chart to generate data for
            request: Analytics request
            features: Synthetic data features from playbook
            requirements: Data requirements from playbook
            
        Returns:
            Tuple of (data_points, description, insights)
        """
        # Generate based on chart type
        generator_map = {
            "line_chart": self._generate_time_series_data_fixed,
            "bar_chart_vertical": self._generate_categorical_data,
            "bar_chart_horizontal": self._generate_categorical_data,
            "pie_chart": self._generate_proportional_data,
            "scatter_plot": self._generate_correlation_data,
            "histogram": self._generate_histogram_raw_data,  # Fixed version
            "heatmap": self._generate_matrix_data,
            "area_chart": self._generate_cumulative_data,
            "bubble_chart": self._generate_multidimensional_data,
            "waterfall": self._generate_waterfall_data,
            "radar_chart": self._generate_multivariate_data,
            "box_plot": self._generate_distribution_summary_data,
            "violin_plot": self._generate_multimodal_data,
            "stacked_area_chart": self._generate_stacked_cumulative_data,
            "grouped_bar_chart": self._generate_grouped_categorical_data,
            "stacked_bar_chart": self._generate_stacked_categorical_data,
            "funnel": self._generate_funnel_data,
            "gantt": self._generate_timeline_data,
            "pareto": self._generate_pareto_data,
            "control_chart": self._generate_process_data,
            "step_chart": self._generate_step_data,
            "hexbin": self._generate_dense_scatter_data,
            "error_bar_chart": self._generate_error_data
        }
        
        generator = generator_map.get(chart_type, self._generate_categorical_data)
        return await generator(request, features, requirements)
    
    async def _generate_time_series_data_fixed(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Fixed time series data generation."""
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
        if "trend" in str(pattern):
            base_value = 100
            trend = 0.5  # Daily growth
            values = [base_value + trend * i + self.np_random.normal(0, 5) for i in range(rows)]
            insights.append(f"Shows {trend*rows:.1f}% growth over period")
        elif "seasonal" in str(pattern):
            values = [50 + 30 * np.sin(2 * np.pi * i / 30) + self.np_random.normal(0, 3) for i in range(rows)]
            insights.append("Clear seasonal pattern with 30-day cycle")
        else:
            values = [self.np_random.uniform(50, 150) for _ in range(rows)]
        
        # Fixed anomaly handling
        if "anomalies" in features:
            anomaly_info = features["anomalies"]
            
            # Handle different anomaly specification formats
            if isinstance(anomaly_info, dict):
                anomaly_count = anomaly_info.get("count", 3)
                magnitude_str = str(anomaly_info.get("magnitude", 2))
            else:
                anomaly_count = 3
                magnitude_str = "2"
            
            # Parse magnitude (could be "2-3x std" or just "2")
            try:
                if "x" in str(magnitude_str):
                    magnitude = float(magnitude_str.split("x")[0].split("-")[0])
                else:
                    magnitude = float(magnitude_str)
            except:
                magnitude = 2.0
            
            # Apply anomalies
            for _ in range(min(anomaly_count, 3)):  # Limit anomalies
                if rows > 20:
                    idx = self.random_state.randint(10, rows - 10)
                    values[idx] = values[idx] * magnitude  # Fixed: direct assignment
                    insights.append(f"Anomaly detected at point {idx}")
        
        # Create data points
        for i, (date, value) in enumerate(zip(dates, values)):
            data_points.append(DataPoint(
                label=f"Day {i+1}",
                value=round(value, 2),
                metadata={"date": date.isoformat(), "index": i}
            ))
        
        description = f"Time series data with {rows} points"
        return data_points, description, insights
    
    async def _generate_histogram_raw_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate raw data values for histogram (not frequency counts)."""
        n = features.get("n", 1000)
        distribution = features.get("distribution", "normal")
        
        # Generate raw values based on distribution type
        if "lognormal" in str(distribution):
            values = self.np_random.lognormal(3, 0.5, n)
            dist_name = "log-normal"
        elif "mixture" in str(distribution) or "bimodal" in str(distribution):
            # Bimodal distribution
            values1 = self.np_random.normal(30, 5, n // 2)
            values2 = self.np_random.normal(70, 5, n // 2)
            values = np.concatenate([values1, values2])
            dist_name = "bimodal"
        else:  # normal
            # For customer age, create realistic distribution
            if "age" in str(request.title).lower() or "age" in str(request.description).lower():
                # Realistic age distribution
                young = self.np_random.normal(25, 3, int(n * 0.2))
                middle = self.np_random.normal(35, 5, int(n * 0.3))
                mature = self.np_random.normal(45, 4, int(n * 0.25))
                senior = self.np_random.normal(55, 6, int(n * 0.15))
                elderly = self.np_random.normal(65, 5, int(n * 0.1))
                values = np.concatenate([young, middle, mature, senior, elderly])
                values = np.clip(values, 18, 75)  # Realistic age range
                dist_name = "age"
            else:
                values = self.np_random.normal(50, 15, n)
                dist_name = "normal"
        
        # Return raw values as data points
        # For histogram, we return the raw values, not binned counts
        data_points = []
        insights = []
        
        # Sample the values if too many (for reasonable data transfer)
        sample_size = min(1000, len(values))
        sampled_values = self.np_random.choice(values, sample_size, replace=False)
        
        for i, value in enumerate(sampled_values):
            data_points.append(DataPoint(
                label=f"Sample_{i+1}",
                value=round(float(value), 2),
                metadata={"index": i, "raw_value": float(value)}
            ))
        
        # Generate insights
        insights.append(f"Distribution: {dist_name}")
        insights.append(f"Mean: {np.mean(values):.1f}, Median: {np.median(values):.1f}")
        insights.append(f"Std Dev: {np.std(values):.1f}")
        insights.append(f"Total samples: {len(values)}")
        
        skewness = (np.mean(values) - np.median(values)) / (np.std(values) + 0.001)
        if abs(skewness) > 0.5:
            insights.append(f"{'Right' if skewness > 0 else 'Left'}-skewed distribution")
        
        description = f"{dist_name.capitalize()} distribution with {n} raw data samples"
        
        return data_points, description, insights
    
    async def _generate_categorical_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate categorical data for bar charts."""
        num_categories = features.get("num_categories", 8)
        value_range = features.get("value_range", [50, 200])
        
        categories = [f"Category {chr(65+i)}" for i in range(num_categories)]
        values = [self.np_random.uniform(value_range[0], value_range[1]) for _ in range(num_categories)]
        
        data_points = []
        for cat, val in zip(categories, values):
            data_points.append(DataPoint(
                label=cat,
                value=round(val, 2),
                metadata={"category": cat}
            ))
        
        description = f"Categorical data with {num_categories} categories"
        insights = [f"Max value: {max(values):.1f}", f"Min value: {min(values):.1f}"]
        
        return data_points, description, insights
    
    async def _generate_proportional_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate proportional data for pie charts."""
        num_segments = features.get("num_segments", 5)
        
        # Generate proportions that sum to 100
        values = self.np_random.exponential(1, num_segments)
        values = (values / values.sum()) * 100
        
        segments = [f"Segment {chr(65+i)}" for i in range(num_segments)]
        
        data_points = []
        for seg, val in zip(segments, values):
            data_points.append(DataPoint(
                label=seg,
                value=round(val, 1),
                metadata={"percentage": val}
            ))
        
        description = f"Proportional data with {num_segments} segments"
        insights = [f"Largest segment: {max(values):.1f}%"]
        
        return data_points, description, insights
    
    async def _generate_correlation_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate correlation data for scatter plots."""
        n_points = features.get("n_points", 100)
        correlation = features.get("correlation", 0.7)
        
        # Generate correlated data
        x = self.np_random.uniform(0, 100, n_points)
        noise = self.np_random.normal(0, 10, n_points)
        y = correlation * x + (1 - correlation) * noise + 50
        
        data_points = []
        for i, (xi, yi) in enumerate(zip(x, y)):
            data_points.append(DataPoint(
                label=f"Point_{i+1}",
                value=round(yi, 2),
                metadata={"x": round(xi, 2), "y": round(yi, 2)}
            ))
        
        description = f"Correlation data with r={correlation:.2f}"
        insights = [f"Correlation coefficient: {correlation:.2f}"]
        
        return data_points, description, insights
    
    async def _generate_matrix_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate matrix data for heatmaps."""
        shape = features.get("shape", [7, 7])
        if isinstance(shape, list):
            rows, cols = shape
        else:
            rows = cols = 7
        
        # Generate matrix
        matrix = self.np_random.normal(50, 20, (rows, cols))
        
        data_points = []
        for i in range(rows):
            for j in range(cols):
                data_points.append(DataPoint(
                    label=f"R{i+1}C{j+1}",
                    value=round(matrix[i, j], 2),
                    metadata={"row": i, "col": j}
                ))
        
        description = f"Matrix data {rows}x{cols}"
        insights = [f"Max value: {np.max(matrix):.1f}"]
        
        return data_points, description, insights
    
    async def _generate_cumulative_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate cumulative data for area charts."""
        periods = features.get("periods", 12)
        
        # Generate cumulative growth
        values = []
        current = 100
        for _ in range(periods):
            growth = self.np_random.uniform(5, 15)
            current += growth
            values.append(current)
        
        data_points = []
        for i, val in enumerate(values):
            data_points.append(DataPoint(
                label=f"Period_{i+1}",
                value=round(val, 2),
                metadata={"period": i+1}
            ))
        
        description = f"Cumulative data over {periods} periods"
        insights = [f"Total growth: {values[-1] - values[0]:.1f}"]
        
        return data_points, description, insights
    
    async def _generate_multidimensional_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate multidimensional data for bubble charts."""
        n_points = features.get("n_points", 10)
        
        data_points = []
        for i in range(n_points):
            data_points.append(DataPoint(
                label=f"Item_{i+1}",
                value=round(self.np_random.uniform(10, 100), 2),
                metadata={
                    "x": round(self.np_random.uniform(0, 100), 2),
                    "y": round(self.np_random.uniform(0, 100), 2),
                    "size": round(self.np_random.uniform(100, 1000), 2)
                }
            ))
        
        description = f"3D data with {n_points} points"
        insights = ["Bubble size represents third dimension"]
        
        return data_points, description, insights
    
    # ... (continuing with remaining methods)
    
    async def _generate_multimodal_data(
        self,
        request: Any,
        features: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], str, List[str]]:
        """Generate multimodal data for violin plots."""
        n_groups = features.get("n_groups", 4)
        
        data_points = []
        for i in range(n_groups):
            # Create bimodal distribution
            mode1 = self.np_random.normal(40 + i*5, 5, 50)
            mode2 = self.np_random.normal(60 + i*5, 5, 50)
            values = np.concatenate([mode1, mode2])
            
            data_points.append(DataPoint(
                label=f"Group_{i+1}",
                value=round(np.median(values), 2),
                metadata={
                    "mean": round(np.mean(values), 2),
                    "std": round(np.std(values), 2),
                    "samples": len(values)
                }
            ))
        
        description = f"Multimodal distributions for {n_groups} groups"
        insights = ["Bimodal distributions visible"]
        
        return data_points, description, insights
    
    # Add remaining methods with same pattern...
    async def _generate_waterfall_data(self, request, features, requirements):
        """Waterfall chart data."""
        categories = ["Start", "Add1", "Add2", "Sub1", "Sub2", "End"]
        values = [100, 30, 20, -15, -25, 110]
        
        data_points = []
        for cat, val in zip(categories, values):
            data_points.append(DataPoint(
                label=cat, value=val,
                metadata={"type": "positive" if val >= 0 else "negative"}
            ))
        
        return data_points, "Waterfall data", ["Shows incremental changes"]
    
    async def _generate_multivariate_data(self, request, features, requirements):
        """Radar chart data."""
        dimensions = features.get("dimensions", 6)
        data_points = []
        for i in range(dimensions):
            data_points.append(DataPoint(
                label=f"Dim_{i+1}",
                value=round(self.np_random.uniform(60, 90), 2),
                metadata={"dimension": f"Dim_{i+1}"}
            ))
        return data_points, f"{dimensions} dimensions", ["Multi-dimensional comparison"]
    
    async def _generate_distribution_summary_data(self, request, features, requirements):
        """Box plot data."""
        n_groups = features.get("n_groups", 4)
        data_points = []
        for i in range(n_groups):
            values = self.np_random.normal(50 + i*10, 10, 100)
            data_points.append(DataPoint(
                label=f"Group_{i+1}",
                value=round(np.median(values), 2),
                metadata={
                    "q1": round(np.percentile(values, 25), 2),
                    "q3": round(np.percentile(values, 75), 2),
                    "min": round(np.min(values), 2),
                    "max": round(np.max(values), 2)
                }
            ))
        return data_points, f"{n_groups} groups", ["Shows quartiles"]
    
    async def _generate_stacked_cumulative_data(self, request, features, requirements):
        """Stacked area data."""
        periods = 8
        series = 4
        data_points = []
        for p in range(periods):
            for s in range(series):
                data_points.append(DataPoint(
                    label=f"P{p+1}_S{s+1}",
                    value=round(self.np_random.uniform(20, 50), 2),
                    metadata={"period": p, "series": s}
                ))
        return data_points, f"{series} series, {periods} periods", ["Stacked composition"]
    
    async def _generate_grouped_categorical_data(self, request, features, requirements):
        """Grouped bar data."""
        groups = 4
        categories = 3
        data_points = []
        for g in range(groups):
            for c in range(categories):
                data_points.append(DataPoint(
                    label=f"G{g+1}_C{c+1}",
                    value=round(self.np_random.uniform(50, 150), 2),
                    metadata={"group": g, "category": c}
                ))
        return data_points, f"{categories} categories, {groups} groups", ["Grouped comparison"]
    
    async def _generate_stacked_categorical_data(self, request, features, requirements):
        """Stacked bar data."""
        categories = 6
        stacks = 4
        data_points = []
        for c in range(categories):
            for s in range(stacks):
                data_points.append(DataPoint(
                    label=f"C{c+1}_S{s+1}",
                    value=round(self.np_random.uniform(10, 40), 2),
                    metadata={"category": c, "stack": s}
                ))
        return data_points, f"{stacks} stacks, {categories} categories", ["Stacked composition"]
    
    async def _generate_funnel_data(self, request, features, requirements):
        """Funnel data."""
        stages = ["Stage1", "Stage2", "Stage3", "Stage4"]
        values = [10000, 3000, 800, 200]
        data_points = []
        for stage, val in zip(stages, values):
            data_points.append(DataPoint(
                label=stage, value=val,
                metadata={"conversion": val/values[0]*100}
            ))
        return data_points, "Funnel data", [f"Conversion: {values[-1]/values[0]*100:.1f}%"]
    
    async def _generate_timeline_data(self, request, features, requirements):
        """Gantt data."""
        tasks = 6
        data_points = []
        start = 0
        for i in range(tasks):
            duration = self.random_state.randint(1, 4)
            data_points.append(DataPoint(
                label=f"Task_{i+1}", value=duration,
                metadata={"start": start, "end": start + duration}
            ))
            start += self.random_state.randint(0, 2)
        return data_points, f"{tasks} tasks", ["Timeline visualization"]
    
    async def _generate_pareto_data(self, request, features, requirements):
        """Pareto data."""
        values = [450, 250, 150, 100, 50]
        labels = [f"Cause_{i+1}" for i in range(5)]
        data_points = []
        cumulative = 0
        total = sum(values)
        for label, val in zip(labels, values):
            cumulative += val
            data_points.append(DataPoint(
                label=label, value=val,
                metadata={"percentage": val/total*100, "cumulative": cumulative/total*100}
            ))
        return data_points, "Pareto data", ["80/20 principle"]
    
    async def _generate_process_data(self, request, features, requirements):
        """Control chart data."""
        n_points = 30
        mean = 50
        std = 5
        values = self.np_random.normal(mean, std, n_points)
        values[10] = mean + 3.5 * std
        values[20] = mean - 3.2 * std
        data_points = []
        for i, val in enumerate(values):
            data_points.append(DataPoint(
                label=f"Sample_{i+1}", value=round(val, 2),
                metadata={"ucl": mean + 3*std, "lcl": mean - 3*std, "mean": mean}
            ))
        return data_points, "Process control data", ["Out-of-control points"]
    
    async def _generate_step_data(self, request, features, requirements):
        """Step chart data."""
        n_steps = 8
        data_points = []
        current_value = 100
        for i in range(n_steps):
            if i % 3 == 0 and i > 0:
                current_value += self.random_state.choice([-20, -10, 10, 20, 30])
            data_points.append(DataPoint(
                label=f"Step_{i+1}", value=current_value,
                metadata={"step": i}
            ))
        return data_points, f"{n_steps} steps", ["Discrete changes"]
    
    async def _generate_dense_scatter_data(self, request, features, requirements):
        """Hexbin data."""
        n_points = 1000
        cluster_centers = [(200, 300), (600, 400), (400, 600)]
        points_per_cluster = n_points // len(cluster_centers)
        data_points = []
        for i, (cx, cy) in enumerate(cluster_centers):
            for j in range(points_per_cluster):
                x = self.np_random.normal(cx, 50)
                y = self.np_random.normal(cy, 50)
                data_points.append(DataPoint(
                    label=f"Point_{i*points_per_cluster+j}",
                    value=round(y, 2),
                    metadata={"x": round(x, 2), "y": round(y, 2), "cluster": i}
                ))
        return data_points, f"{n_points} points, {len(cluster_centers)} clusters", ["Density patterns"]
    
    async def _generate_error_data(self, request, features, requirements):
        """Error bar data."""
        n_conditions = 5
        data_points = []
        for i in range(n_conditions):
            mean = 50 + i * 10
            std_error = self.np_random.uniform(2, 5)
            data_points.append(DataPoint(
                label=f"Condition_{i+1}", value=round(mean, 2),
                metadata={"error": round(std_error, 2)}
            ))
        return data_points, f"{n_conditions} conditions", ["With error bars"]