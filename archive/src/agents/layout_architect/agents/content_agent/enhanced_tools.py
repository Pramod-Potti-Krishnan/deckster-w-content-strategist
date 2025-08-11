"""
Enhanced tools for Content Agent "Chief Specifier" role.

These tools support the four expert modes:
1. Content Writer - Text expansion (existing)
2. Data Storyteller - Synthetic data and chart selection
3. Visual Briefer - Image prompt generation
4. Diagram Architect - Diagram structure design
"""

import random
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from pydantic_ai import Tool
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# Specific Data Models to avoid additionalProperties issues

class ChartDataPoint(BaseModel):
    """A single data point for charts"""
    label: str = Field(description="Label for this data point (e.g., 'Q1 2024')")
    value: float = Field(description="Numeric value for this point")
    # Optional fields for multi-series data
    series_a: Optional[float] = Field(default=None, description="Value for series A in multi-series charts")
    series_b: Optional[float] = Field(default=None, description="Value for series B in multi-series charts")

class ChartAxes(BaseModel):
    """Axis labels for charts"""
    x_axis: str = Field(description="X-axis label")
    y_axis: str = Field(description="Y-axis label")

class DiagramNode(BaseModel):
    """A node in a diagram"""
    id: str = Field(description="Unique identifier for the node")
    label: str = Field(description="Display text for the node")
    type: str = Field(description="Node type: process, terminal, decision, etc.")
    level: Optional[int] = Field(default=0, description="Hierarchical level")
    # Style properties
    shape: Optional[str] = Field(default="rectangle", description="Node shape")
    color: Optional[str] = Field(default="#3498DB", description="Node color")
    size: Optional[str] = Field(default="medium", description="Node size")

class DiagramConnection(BaseModel):
    """A connection between nodes in a diagram"""
    from_node: str = Field(description="ID of the source node")
    to_node: str = Field(description="ID of the target node")
    label: Optional[str] = Field(default="", description="Label for the connection")
    type: str = Field(default="arrow", description="Connection type: arrow, line, curved")
    # Style properties
    line_style: Optional[str] = Field(default="solid", description="Line style")
    arrow_type: Optional[str] = Field(default="filled", description="Arrow type")
    width: Optional[int] = Field(default=2, description="Line width")

# Data Storyteller Tools

class SyntheticDataInput(BaseModel):
    """Input for synthetic data generation"""
    narrative_context: str = Field(description="The story the data should tell")
    data_category: str = Field(description="Type: revenue, usage, comparison, trend, distribution")
    time_period: str = Field(description="Time span: day, week, month, quarter, year")
    value_range: Optional[Tuple[int, int]] = Field(default=None, description="Min and max values for data")
    data_points_count: Optional[int] = Field(default=None, description="Number of data points")


class SyntheticDataOutput(BaseModel):
    """Output for synthetic data generation"""
    data_points: List[ChartDataPoint] = Field(description="Generated data points")
    labels: List[str] = Field(description="Labels for the data points")
    unit: str = Field(description="Unit of measurement (e.g., $, %, users)")
    trend_direction: str = Field(description="Overall trend: increasing, decreasing, or stable")
    total_sum: float = Field(description="Sum of all values")
    average: float = Field(description="Average of all values")

class ChartSelectionInput(BaseModel):
    """Input for chart type selection"""
    data_points: List[ChartDataPoint] = Field(description="The data points to visualize")
    comparison_goal: str = Field(description="What comparison to highlight")
    data_point_count: int = Field(description="Number of data points")
    has_time_series: bool = Field(default=False, description="Whether data has time component")

class ChartSelectionOutput(BaseModel):
    """Output for chart type selection"""
    chart_type: str = Field(description="Recommended chart type")
    reasoning: str = Field(description="Why this chart type was selected")
    alternative_options: List[str] = Field(description="Other viable chart types")
    styling_hints: Dict[str, str] = Field(description="Styling recommendations")


async def generate_synthetic_data_tool(input: SyntheticDataInput) -> SyntheticDataOutput:
    """
    Generate plausible synthetic data that supports the narrative.
    
    Creates realistic-looking data points that align with the slide's story,
    ensuring the data supports the key points being made.
    """
    logger.debug(f"Generating synthetic data for {input.data_category}")
    
    # Determine number of data points
    points_count = input.data_points_count or _default_points_for_period(input.time_period)
    
    # Generate labels based on time period
    labels = _generate_time_labels(input.time_period, points_count)
    
    # Ensure value_range is properly set with defaults if needed
    if not input.value_range or len(input.value_range) != 2:
        # Set reasonable defaults based on category
        if input.data_category == "revenue":
            input.value_range = (100000, 500000)  # $100k to $500k
        elif input.data_category == "usage":
            input.value_range = (1000, 10000)  # 1k to 10k users
        elif input.data_category == "percentage" or input.data_category == "distribution":
            input.value_range = (0, 100)  # 0% to 100%
        else:
            input.value_range = (100, 1000)  # Generic range
        logger.debug(f"Using default value_range: {input.value_range}")
    
    # Generate data based on category
    if input.data_category == "revenue":
        data_points = _generate_revenue_data(
            points_count, 
            input.value_range,
            trend="growth" if "growth" in input.narrative_context.lower() else "stable"
        )
        unit = "$"
        
    elif input.data_category == "usage":
        data_points = _generate_usage_data(
            points_count,
            input.value_range,
            pattern="increasing" if "adoption" in input.narrative_context.lower() else "cyclical"
        )
        unit = "users"
        
    elif input.data_category == "comparison":
        # Generate comparative data (e.g., A vs B)
        data_points = _generate_comparison_data(points_count, input.value_range)
        unit = "units"
        
    elif input.data_category == "trend":
        # Generate trend data with clear direction
        trend_direction = _extract_trend_direction(input.narrative_context)
        data_points = _generate_trend_data(points_count, input.value_range, trend_direction)
        unit = "%"
        
    elif input.data_category == "distribution":
        # Generate distribution data (e.g., market share)
        data_points = _generate_distribution_data(points_count, input.value_range)
        unit = "%"
        
    else:
        # Default: generic increasing data
        data_points = _generate_generic_data(points_count, input.value_range)
        unit = "units"
    
    # Structure the data for charts
    structured_data = []
    for i, (label, value) in enumerate(zip(labels, data_points)):
        if isinstance(value, dict):
            # Multi-series data
            point = ChartDataPoint(
                label=label,
                value=value.get("Series A", 0) if "Series A" in value else sum(value.values()) / len(value),
                series_a=value.get("Series A"),
                series_b=value.get("Series B")
            )
        else:
            # Single series
            point = ChartDataPoint(label=label, value=float(value))
        structured_data.append(point)
    
    # Calculate totals
    total_sum = sum(dp.value for dp in structured_data)
    average = total_sum / len(structured_data) if structured_data else 0
    
    # Return properly structured output
    result = SyntheticDataOutput(
        data_points=structured_data,
        labels=labels,
        unit=unit,
        trend_direction=_analyze_trend(data_points),
        total_sum=total_sum,
        average=average
    )
    
    logger.debug(f"Generated data with {len(structured_data)} points")
    logger.debug(f"Sample data point: {structured_data[0].model_dump() if structured_data else 'None'}")
    
    return result


async def select_chart_type_tool(input: ChartSelectionInput) -> ChartSelectionOutput:
    """
    Select the optimal chart type based on data structure and comparison goals.
    
    Analyzes the data characteristics and narrative goals to recommend
    the most effective visualization type.
    """
    logger.debug(f"Selecting chart type for {input.data_point_count} data points")
    
    # Analyze data structure
    is_multi_series = any(dp.series_a is not None for dp in input.data_points)
    has_negative = any(dp.value < 0 or (dp.series_a and dp.series_a < 0) or (dp.series_b and dp.series_b < 0) 
                      for dp in input.data_points)
    
    # Decision logic for chart type
    if "percentage" in input.comparison_goal.lower() or "share" in input.comparison_goal.lower():
        if input.data_point_count <= 6:
            chart_type = "pie"
            reasoning = "Pie chart effectively shows proportional relationships for small datasets"
        else:
            chart_type = "bar"
            reasoning = "Bar chart better for comparing many percentage values"
            
    elif input.has_time_series or "trend" in input.comparison_goal.lower():
        if is_multi_series:
            chart_type = "multi_line"
            reasoning = "Multiple line chart shows trends across different series over time"
        else:
            chart_type = "line"
            reasoning = "Line chart best visualizes trends and changes over time"
            
    elif "correlation" in input.comparison_goal.lower():
        chart_type = "scatter"
        reasoning = "Scatter plot reveals relationships between variables"
        
    elif is_multi_series:
        if "total" in input.comparison_goal.lower():
            chart_type = "stacked_bar"
            reasoning = "Stacked bar shows both individual and total values"
        else:
            chart_type = "grouped_bar"
            reasoning = "Grouped bar enables side-by-side comparison"
            
    elif has_negative:
        chart_type = "waterfall"
        reasoning = "Waterfall chart clearly shows positive and negative contributions"
        
    else:
        # Default based on data point count
        if input.data_point_count <= 10:
            chart_type = "bar"
            reasoning = "Bar chart provides clear comparison for discrete categories"
        else:
            chart_type = "line"
            reasoning = "Line chart better for visualizing many data points"
    
    return ChartSelectionOutput(
        chart_type=chart_type,
        reasoning=reasoning,
        alternative_options=_get_alternative_charts(chart_type),
        styling_hints=_get_chart_styling_hints(chart_type)
    )


# Visual Briefer Tools

class ImagePromptInput(BaseModel):
    """Input for image prompt generation"""
    content_context: str = Field(description="What the slide is about")
    visual_goal: str = Field(description="What the image should achieve")
    target_mood: str = Field(description="Emotional tone: professional, inspiring, technical, warm")
    composition_hints: List[str] = Field(description="Elements to include")
    audience_type: Optional[str] = Field(default="general")

class ImagePromptOutput(BaseModel):
    """Output for image prompt generation"""
    detailed_prompt: str = Field(description="Full 200+ word prompt for image generation")
    style_keywords: List[str] = Field(description="Style descriptors")
    negative_prompt: str = Field(description="What to avoid in the image")
    composition_type: str = Field(description="Composition layout type")
    color_palette_suggestion: List[str] = Field(description="Suggested colors")
    prompt_length: int = Field(description="Word count of the prompt")


async def generate_image_prompt_tool(input: ImagePromptInput) -> ImagePromptOutput:
    """
    Generate detailed prompts for image generation APIs.
    
    Creates comprehensive 200+ word prompts with style, composition,
    lighting, and mood specifications for services like DALL-E or Midjourney.
    """
    logger.debug(f"Generating image prompt for {input.target_mood} mood")
    
    # Build style keywords based on mood and context
    style_keywords = _get_style_keywords(input.target_mood, input.audience_type)
    
    # Construct detailed prompt
    prompt_parts = []
    
    # Opening - Set the scene
    prompt_parts.append(_generate_scene_description(input.content_context, input.visual_goal))
    
    # Composition details
    composition_desc = _generate_composition_description(input.composition_hints)
    prompt_parts.append(composition_desc)
    
    # Style and aesthetic
    style_desc = _generate_style_description(input.target_mood, style_keywords)
    prompt_parts.append(style_desc)
    
    # Lighting and atmosphere
    lighting_desc = _generate_lighting_description(input.target_mood)
    prompt_parts.append(lighting_desc)
    
    # Technical specifications
    tech_specs = _generate_technical_specs()
    prompt_parts.append(tech_specs)
    
    # Combine into detailed prompt
    detailed_prompt = " ".join(prompt_parts)
    
    # Generate negative prompt (what to avoid)
    negative_prompt = _generate_negative_prompt(input.target_mood, input.audience_type)
    
    return ImagePromptOutput(
        detailed_prompt=detailed_prompt,
        style_keywords=style_keywords,
        negative_prompt=negative_prompt,
        composition_type=_determine_composition_type(input.composition_hints),
        color_palette_suggestion=_suggest_color_palette(input.target_mood),
        prompt_length=len(detailed_prompt.split())
    )


# Diagram Architect Tools

class DiagramStructureInput(BaseModel):
    """Input for diagram structure design"""
    concept_description: str = Field(description="What the diagram should explain")
    relationship_type: str = Field(description="Type: flow, hierarchy, cycle, network, matrix")
    node_count_estimate: int = Field(description="Approximate number of nodes")
    key_elements: Optional[List[str]] = Field(default=None, description="Main elements to include")

class DiagramStructureOutput(BaseModel):
    """Output for diagram structure design"""
    nodes: List[DiagramNode] = Field(description="All nodes in the diagram")
    connections: List[DiagramConnection] = Field(description="All connections between nodes")
    layout_style: str = Field(description="Recommended layout direction")
    diagram_type: str = Field(description="Type of diagram")
    node_count: int = Field(description="Total number of nodes")
    connection_count: int = Field(description="Total number of connections")
    complexity_level: str = Field(description="simple, moderate, or complex")
    rendering_hints: Dict[str, str] = Field(description="Hints for rendering the diagram")


async def design_diagram_structure_tool(input: DiagramStructureInput) -> DiagramStructureOutput:
    """
    Design the complete structural blueprint for a diagram.
    
    Creates the logical structure including all nodes, connections,
    and layout specifications for diagram rendering engines.
    """
    logger.debug(f"Designing {input.relationship_type} diagram structure")
    
    # Extract key concepts from description
    key_concepts = input.key_elements or _extract_key_concepts(
        input.concept_description, 
        input.node_count_estimate
    )
    
    # Generate nodes based on relationship type
    if input.relationship_type == "flow":
        nodes = _generate_flow_nodes(key_concepts)
        connections = _generate_flow_connections(nodes)
        layout_style = "left-right"
        
    elif input.relationship_type == "hierarchy":
        nodes = _generate_hierarchy_nodes(key_concepts)
        connections = _generate_hierarchy_connections(nodes)
        layout_style = "top-down"
        
    elif input.relationship_type == "cycle":
        nodes = _generate_cycle_nodes(key_concepts)
        connections = _generate_cycle_connections(nodes)
        layout_style = "circular"
        
    elif input.relationship_type == "network":
        nodes = _generate_network_nodes(key_concepts)
        connections = _generate_network_connections(nodes)
        layout_style = "force-directed"
        
    elif input.relationship_type == "matrix":
        nodes = _generate_matrix_nodes(key_concepts)
        connections = []  # Matrix typically doesn't have connections
        layout_style = "grid"
        
    else:
        # Default: simple connected nodes
        nodes = _generate_simple_nodes(key_concepts)
        connections = _generate_simple_connections(nodes)
        layout_style = "auto"
    
    return DiagramStructureOutput(
        nodes=nodes,
        connections=connections,
        layout_style=layout_style,
        diagram_type=_map_to_standard_diagram_type(input.relationship_type),
        node_count=len(nodes),
        connection_count=len(connections),
        complexity_level=_assess_diagram_complexity(len(nodes), len(connections)),
        rendering_hints=_get_rendering_hints(input.relationship_type)
    )


# Helper functions for synthetic data generation

def _default_points_for_period(period: str) -> int:
    """Get default number of data points for time period"""
    return {
        "day": 24,      # hourly
        "week": 7,      # daily
        "month": 30,    # daily
        "quarter": 12,  # weekly
        "year": 12      # monthly
    }.get(period, 10)


def _generate_time_labels(period: str, count: int) -> List[str]:
    """Generate time-based labels"""
    if period == "day":
        return [f"{i:02d}:00" for i in range(count)]
    elif period == "week":
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return days[:count]
    elif period == "month":
        return [f"Day {i+1}" for i in range(count)]
    elif period == "quarter":
        return [f"Week {i+1}" for i in range(count)]
    elif period == "year":
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return months[:count]
    else:
        return [f"Item {i+1}" for i in range(count)]


def _generate_revenue_data(count: int, value_range: Tuple[int, int], trend: str) -> List[float]:
    """Generate revenue data with specified trend"""
    min_val, max_val = value_range
    base = random.uniform(min_val, max_val * 0.6)
    
    data = []
    for i in range(count):
        if trend == "growth":
            # Steady growth with some variation
            value = base * (1 + i * 0.05) + random.uniform(-base * 0.1, base * 0.1)
        else:
            # Stable with variation
            value = base + random.uniform(-base * 0.15, base * 0.15)
        
        data.append(round(value, 2))
    
    return data


def _generate_usage_data(count: int, value_range: Tuple[int, int], pattern: str) -> List[int]:
    """Generate usage data with specified pattern"""
    min_val, max_val = value_range
    
    if pattern == "increasing":
        # S-curve adoption pattern
        data = []
        for i in range(count):
            progress = i / (count - 1)
            # S-curve formula
            value = min_val + (max_val - min_val) * (1 / (1 + pow(2.718, -10 * (progress - 0.5))))
            data.append(int(value + random.randint(-50, 50)))
    else:
        # Cyclical pattern (e.g., daily usage)
        data = []
        for i in range(count):
            # Sin wave with noise
            cycle_value = (math.sin(i * 2 * 3.14159 / count) + 1) / 2
            value = min_val + (max_val - min_val) * cycle_value
            data.append(int(value + random.randint(-20, 20)))
    
    return data


def _generate_comparison_data(count: int, value_range: Tuple[int, int]) -> List[Dict[str, int]]:
    """Generate multi-series comparison data"""
    data = []
    series_names = ["Series A", "Series B"]
    
    for i in range(count):
        point = {}
        for series in series_names:
            point[series] = random.randint(*value_range)
        data.append(point)
    
    return data


def _generate_trend_data(count: int, value_range: Tuple[int, int], direction: str) -> List[float]:
    """Generate data with clear trend"""
    min_val, max_val = value_range
    
    if direction == "increasing":
        start = min_val
        end = max_val
    elif direction == "decreasing":
        start = max_val
        end = min_val
    else:  # stable
        start = end = (min_val + max_val) / 2
    
    data = []
    for i in range(count):
        progress = i / (count - 1) if count > 1 else 0
        value = start + (end - start) * progress
        # Add some noise
        value += random.uniform(-abs(end - start) * 0.05, abs(end - start) * 0.05)
        data.append(round(value, 2))
    
    return data


def _generate_distribution_data(count: int, value_range: Tuple[int, int]) -> List[float]:
    """Generate distribution data (percentages that sum to ~100)"""
    # Generate random values
    values = [random.uniform(0.5, 1.5) for _ in range(count)]
    
    # Normalize to sum to 100
    total = sum(values)
    percentages = [round(v / total * 100, 1) for v in values]
    
    # Adjust last value to ensure sum is exactly 100
    current_sum = sum(percentages[:-1])
    percentages[-1] = round(100 - current_sum, 1)
    
    return percentages


def _generate_generic_data(count: int, value_range: Tuple[int, int]) -> List[int]:
    """Generate generic data points"""
    return [random.randint(*value_range) for _ in range(count)]


def _extract_trend_direction(context: str) -> str:
    """Extract trend direction from narrative context"""
    context_lower = context.lower()
    
    increasing_keywords = ["growth", "increase", "rise", "improve", "expand", "surge"]
    decreasing_keywords = ["decline", "decrease", "fall", "reduce", "shrink", "drop"]
    
    if any(keyword in context_lower for keyword in increasing_keywords):
        return "increasing"
    elif any(keyword in context_lower for keyword in decreasing_keywords):
        return "decreasing"
    else:
        return "stable"


def _analyze_trend(data_points: List[Any]) -> str:
    """Analyze trend in data"""
    if not data_points:
        return "stable"
    
    # Handle different data structures
    if isinstance(data_points[0], dict):
        # Multi-series - analyze first series
        first_series = list(data_points[0].keys())[0]
        values = [dp[first_series] for dp in data_points]
    else:
        values = data_points
    
    # Simple trend analysis
    first_third = sum(values[:len(values)//3])
    last_third = sum(values[-len(values)//3:])
    
    if last_third > first_third * 1.1:
        return "increasing"
    elif last_third < first_third * 0.9:
        return "decreasing"
    else:
        return "stable"


def _get_alternative_charts(primary: str) -> List[str]:
    """Get alternative chart types"""
    alternatives = {
        "bar": ["column", "horizontal_bar"],
        "line": ["area", "spline"],
        "pie": ["donut", "treemap"],
        "scatter": ["bubble", "heatmap"],
        "stacked_bar": ["stacked_area", "100_stacked_bar"],
        "grouped_bar": ["grouped_column", "multiple_bars"]
    }
    return alternatives.get(primary, [])


def _get_chart_styling_hints(chart_type: str) -> Dict[str, str]:
    """Get styling hints for chart type"""
    return {
        "bar": {"orientation": "vertical", "spacing": "moderate", "labels": "outside"},
        "line": {"smoothing": "slight", "markers": "on_hover", "area_fill": "none"},
        "pie": {"labels": "percentage", "legend": "right", "start_angle": "90"},
        "scatter": {"point_size": "medium", "opacity": "0.7", "trend_line": "optional"},
        "stacked_bar": {"spacing": "tight", "labels": "center", "legend": "top"},
        "multi_line": {"line_width": "2px", "legend": "bottom", "markers": "key_points"}
    }.get(chart_type, {})


# Helper functions for image prompt generation

def _get_style_keywords(mood: str, audience: str) -> List[str]:
    """Get style keywords based on mood and audience"""
    base_keywords = {
        "professional": ["clean", "modern", "minimalist", "corporate", "sleek"],
        "inspiring": ["vibrant", "dynamic", "uplifting", "energetic", "bold"],
        "technical": ["detailed", "precise", "schematic", "technical illustration", "blueprint"],
        "warm": ["friendly", "approachable", "soft lighting", "natural", "inviting"]
    }
    
    audience_modifiers = {
        "executives": ["sophisticated", "premium", "high-end"],
        "technical": ["detailed", "accurate", "informative"],
        "general": ["accessible", "clear", "relatable"],
        "youth": ["trendy", "contemporary", "fresh"]
    }
    
    keywords = base_keywords.get(mood, ["professional", "clean"])
    keywords.extend(audience_modifiers.get(audience, []))
    
    return list(set(keywords))  # Remove duplicates


def _generate_scene_description(context: str, goal: str) -> str:
    """Generate opening scene description"""
    templates = [
        f"A {goal} visualization depicting {context}",
        f"An image that {goal} through visual representation of {context}",
        f"A scene showcasing {context} designed to {goal}"
    ]
    return random.choice(templates)


def _generate_composition_description(hints: List[str]) -> str:
    """Generate composition description"""
    if not hints:
        return "The composition should be balanced and visually appealing."
    
    elements = ", ".join(hints[:3])  # Limit to 3 main elements
    return f"The composition features {elements} arranged in a harmonious layout that guides the viewer's eye naturally through the image."


def _generate_style_description(mood: str, keywords: List[str]) -> str:
    """Generate style description"""
    keyword_str = ", ".join(keywords[:5])
    return f"The visual style should be {keyword_str}, creating a {mood} atmosphere that resonates with the target audience."


def _generate_lighting_description(mood: str) -> str:
    """Generate lighting description"""
    lighting_styles = {
        "professional": "even, soft lighting with subtle shadows for depth",
        "inspiring": "bright, optimistic lighting with warm highlights",
        "technical": "clear, neutral lighting that reveals all details",
        "warm": "golden hour lighting with soft, warm tones"
    }
    return f"Lighting: {lighting_styles.get(mood, 'balanced natural lighting')}."


def _generate_technical_specs() -> str:
    """Generate technical specifications"""
    return "High resolution, professional photography quality, sharp focus, depth of field for visual hierarchy."


def _generate_negative_prompt(mood: str, audience: str) -> str:
    """Generate negative prompt (what to avoid)"""
    common_negatives = ["low quality", "blurry", "pixelated", "amateur", "cluttered"]
    
    mood_specific = {
        "professional": ["casual", "playful", "informal"],
        "inspiring": ["dull", "monotone", "depressing"],
        "technical": ["artistic", "abstract", "vague"],
        "warm": ["cold", "harsh", "sterile"]
    }
    
    negatives = common_negatives + mood_specific.get(mood, [])
    return ", ".join(negatives)


def _determine_composition_type(hints: List[str]) -> str:
    """Determine composition type from hints"""
    hint_text = " ".join(hints).lower()
    
    if "center" in hint_text or "focal" in hint_text:
        return "centered"
    elif "split" in hint_text or "divided" in hint_text:
        return "split_screen"
    elif "grid" in hint_text or "multiple" in hint_text:
        return "grid"
    elif "hero" in hint_text or "full" in hint_text:
        return "full_bleed"
    else:
        return "rule_of_thirds"


def _suggest_color_palette(mood: str) -> List[str]:
    """Suggest color palette based on mood"""
    palettes = {
        "professional": ["#2C3E50", "#3498DB", "#ECF0F1", "#34495E"],
        "inspiring": ["#F39C12", "#E74C3C", "#3498DB", "#2ECC71"],
        "technical": ["#34495E", "#7F8C8D", "#ECF0F1", "#3498DB"],
        "warm": ["#E67E22", "#D35400", "#F39C12", "#E74C3C"]
    }
    return palettes.get(mood, ["#3498DB", "#2C3E50", "#ECF0F1"])


# Helper functions for diagram structure

def _extract_key_concepts(description: str, target_count: int) -> List[str]:
    """Extract key concepts from description"""
    # Simple extraction - in production would use NLP
    words = description.split()
    
    # Filter for capitalized words and important terms
    concepts = []
    for word in words:
        if word[0].isupper() and len(word) > 3:
            concepts.append(word.strip('.,!?'))
    
    # If not enough, add some generic nodes
    while len(concepts) < target_count:
        concepts.append(f"Step {len(concepts) + 1}")
    
    return concepts[:target_count]


def _generate_flow_nodes(concepts: List[str]) -> List[DiagramNode]:
    """Generate nodes for flow diagram"""
    nodes = []
    for i, concept in enumerate(concepts):
        node_type = "process" if i > 0 and i < len(concepts)-1 else "terminal"
        style = _determine_node_style(node_type)
        node = DiagramNode(
            id=f"node_{i}",
            label=concept,
            type=node_type,
            level=i,
            shape=style.get("shape", "rectangle"),
            color=style.get("color", "#3498DB"),
            size=style.get("size", "medium")
        )
        nodes.append(node)
    
    logger.debug(f"Generated {len(nodes)} flow nodes")
    return nodes


def _generate_flow_connections(nodes: List[DiagramNode]) -> List[DiagramConnection]:
    """Generate connections for flow diagram"""
    connections = []
    for i in range(len(nodes) - 1):
        conn_style = _determine_connection_style("arrow")
        connection = DiagramConnection(
            from_node=nodes[i].id,
            to_node=nodes[i + 1].id,
            label="",
            type="arrow",
            line_style=conn_style.get("line", "solid"),
            arrow_type=conn_style.get("arrow", "filled"),
            width=conn_style.get("width", 2)
        )
        connections.append(connection)
    
    logger.debug(f"Generated {len(connections)} flow connections")
    return connections


def _generate_hierarchy_nodes(concepts: List[str]) -> List[DiagramNode]:
    """Generate nodes for hierarchy diagram"""
    nodes = []
    
    # Root node
    style = _determine_node_style("root")
    nodes.append(DiagramNode(
        id="root",
        label=concepts[0],
        type="root",
        level=0,
        shape=style.get("shape", "rectangle"),
        color=style.get("color", "#2C3E50"),
        size=style.get("size", "large")
    ))
    
    # Distribute remaining concepts across levels
    remaining = concepts[1:]
    level = 1
    while remaining:
        level_size = min(3, len(remaining))
        for i in range(level_size):
            style = _determine_node_style("branch")
            nodes.append(DiagramNode(
                id=f"node_{len(nodes)}",
                label=remaining.pop(0),
                type="branch",
                level=level,
                shape=style.get("shape", "rectangle"),
                color=style.get("color", "#3498DB"),
                size=style.get("size", "medium")
            ))
        level += 1
    
    return nodes


def _generate_hierarchy_connections(nodes: List[DiagramNode]) -> List[DiagramConnection]:
    """Generate connections for hierarchy diagram"""
    connections = []
    
    # Connect each level to the previous
    for node in nodes[1:]:
        # Find parent (node from previous level)
        parent_candidates = [n for n in nodes if n.level == node.level - 1]
        if parent_candidates:
            parent = random.choice(parent_candidates)
            conn_style = _determine_connection_style("hierarchy")
            connection = DiagramConnection(
                from_node=parent.id,
                to_node=node.id,
                label="",
                type="hierarchy",
                line_style=conn_style.get("line", "solid"),
                arrow_type=conn_style.get("arrow", "none"),
                width=conn_style.get("width", 2)
            )
            connections.append(connection)
    
    return connections


def _generate_cycle_nodes(concepts: List[str]) -> List[DiagramNode]:
    """Generate nodes for cycle diagram"""
    nodes = []
    angle_step = 360 / len(concepts)
    
    for i, concept in enumerate(concepts):
        style = _determine_node_style("cycle_step")
        node = DiagramNode(
            id=f"node_{i}",
            label=concept,
            type="cycle_step",
            level=0,
            shape=style.get("shape", "circle"),
            color=style.get("color", "#E74C3C"),
            size=style.get("size", "medium")
        )
        nodes.append(node)
    
    return nodes


def _generate_cycle_connections(nodes: List[DiagramNode]) -> List[DiagramConnection]:
    """Generate connections for cycle diagram"""
    connections = []
    
    for i in range(len(nodes)):
        next_index = (i + 1) % len(nodes)
        conn_style = _determine_connection_style("curved_arrow")
        connection = DiagramConnection(
            from_node=nodes[i].id,
            to_node=nodes[next_index].id,
            label="",
            type="curved_arrow",
            line_style=conn_style.get("line", "curved"),
            arrow_type=conn_style.get("arrow", "filled"),
            width=conn_style.get("width", 2)
        )
        connections.append(connection)
    
    return connections


def _generate_network_nodes(concepts: List[str]) -> List[DiagramNode]:
    """Generate nodes for network diagram"""
    nodes = []
    
    # Create central node
    nodes.append({
        "id": "central",
        "label": concepts[0],
        "type": "hub",
        "importance": 1.0
    })
    
    # Create peripheral nodes
    for i, concept in enumerate(concepts[1:], 1):
        nodes.append({
            "id": f"node_{i}",
            "label": concept,
            "type": "node",
            "importance": random.uniform(0.3, 0.8)
        })
    
    return nodes


def _generate_network_connections(nodes: List[DiagramNode]) -> List[DiagramConnection]:
    """Generate connections for network diagram"""
    connections = []
    central = nodes[0]
    
    # Connect all to central
    for node in nodes[1:]:
        connections.append({
            "from": central["id"],
            "to": node["id"],
            "label": "",
            "type": "network",
            "weight": node["importance"]
        })
    
    # Add some cross-connections
    for i in range(len(nodes) // 3):
        node1, node2 = random.sample(nodes[1:], 2)
        connections.append({
            "from": node1["id"],
            "to": node2["id"],
            "label": "",
            "type": "network",
            "weight": 0.3
        })
    
    return connections


def _generate_matrix_nodes(concepts: List[str]) -> List[DiagramNode]:
    """Generate nodes for matrix diagram"""
    nodes = []
    
    # Create 2x2 matrix
    positions = [(0, 0), (1, 0), (0, 1), (1, 1)]
    
    for i, (concept, pos) in enumerate(zip(concepts[:4], positions)):
        nodes.append({
            "id": f"quadrant_{i}",
            "label": concept,
            "type": "matrix_cell",
            "row": pos[0],
            "col": pos[1]
        })
    
    return nodes


def _generate_simple_nodes(concepts: List[str]) -> List[DiagramNode]:
    """Generate simple nodes"""
    return [{
        "id": f"node_{i}",
        "label": concept,
        "type": "default",
        "level": 0
    } for i, concept in enumerate(concepts)]


def _generate_simple_connections(nodes: List[DiagramNode]) -> List[DiagramConnection]:
    """Generate simple connections"""
    connections = []
    
    # Connect in sequence with some branching
    for i in range(len(nodes) - 1):
        conn_style = _determine_connection_style("default")
        connection = DiagramConnection(
            from_node=nodes[i].id,
            to_node=nodes[i + 1].id,
            label="",
            type="default",
            line_style=conn_style.get("line", "solid"),
            arrow_type=conn_style.get("arrow", "open"),
            width=conn_style.get("width", 1)
        )
        connections.append(connection)
    
    return connections


def _determine_node_style(node_type: str) -> Dict[str, Any]:
    """Determine styling for node type"""
    styles = {
        "root": {"shape": "rectangle", "color": "#2C3E50", "size": "large"},
        "hub": {"shape": "circle", "color": "#3498DB", "size": "large"},
        "process": {"shape": "rectangle", "color": "#3498DB", "size": "medium"},
        "terminal": {"shape": "rounded", "color": "#27AE60", "size": "medium"},
        "cycle_step": {"shape": "circle", "color": "#E74C3C", "size": "medium"},
        "matrix_cell": {"shape": "square", "color": "#F39C12", "size": "large"},
        "default": {"shape": "rectangle", "color": "#7F8C8D", "size": "medium"}
    }
    return styles.get(node_type, styles["default"])


def _determine_connection_style(connection_type: str) -> Dict[str, Any]:
    """Determine styling for connection type"""
    styles = {
        "arrow": {"line": "solid", "arrow": "filled", "width": 2},
        "hierarchy": {"line": "solid", "arrow": "none", "width": 2},
        "curved_arrow": {"line": "curved", "arrow": "filled", "width": 2},
        "network": {"line": "dotted", "arrow": "none", "width": 1},
        "default": {"line": "solid", "arrow": "open", "width": 1}
    }
    return styles.get(connection_type, styles["default"])


def _map_to_standard_diagram_type(relationship: str) -> str:
    """Map relationship type to standard diagram type"""
    mapping = {
        "flow": "flowchart",
        "hierarchy": "org_chart",
        "cycle": "cycle_diagram",
        "network": "network_diagram",
        "matrix": "matrix_diagram"
    }
    return mapping.get(relationship, "general_diagram")


def _assess_diagram_complexity(node_count: int, connection_count: int) -> str:
    """Assess diagram complexity"""
    complexity_score = node_count + connection_count * 0.5
    
    if complexity_score < 10:
        return "simple"
    elif complexity_score < 20:
        return "moderate"
    else:
        return "complex"


def _get_rendering_hints(relationship_type: str) -> Dict[str, Any]:
    """Get rendering hints for diagram type"""
    hints = {
        "flow": {
            "node_spacing": "generous",
            "connection_routing": "orthogonal",
            "label_placement": "center"
        },
        "hierarchy": {
            "level_spacing": "uniform",
            "sibling_spacing": "balanced",
            "connection_style": "straight"
        },
        "cycle": {
            "arrangement": "circular",
            "arrow_curvature": "smooth",
            "center_space": "open"
        },
        "network": {
            "layout_algorithm": "force-directed",
            "node_repulsion": "medium",
            "edge_attraction": "low"
        },
        "matrix": {
            "cell_spacing": "tight",
            "border_style": "solid",
            "label_alignment": "center"
        }
    }
    return hints.get(relationship_type, {})


# Register tools
generate_synthetic_data = Tool(generate_synthetic_data_tool)
select_chart_type = Tool(select_chart_type_tool)
generate_image_prompt = Tool(generate_image_prompt_tool)
design_diagram_structure = Tool(design_diagram_structure_tool)


# Import math for calculations
import math