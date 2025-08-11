"""
Pydantic Models for Diagram Generation
======================================

Defines all data structures used across the diagram generation pipeline.
These models ensure type safety and validation throughout the system.

Author: AI Assistant
Date: 2024
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Literal, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator

# ThemeDefinition will be a dict for now
from typing import Any


class DiagramType(str, Enum):
    """Supported diagram types."""
    # Business diagrams
    PYRAMID = "pyramid"
    FUNNEL = "funnel"
    MATRIX = "matrix_2x2"
    MATRIX_3X3 = "matrix_3x3"
    HUB_SPOKE = "hub_spoke"
    CYCLE = "cycle"
    VENN = "venn"
    SWOT = "swot"
    PROCESS_FLOW = "process_flow"
    
    # Technical diagrams
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    ARCHITECTURE = "architecture"
    GANTT = "gantt"
    
    # Creative diagrams
    MIND_MAP = "mind_map"
    TIMELINE = "timeline"
    JOURNEY_MAP = "journey_map"
    HONEYCOMB = "honeycomb"
    CONCEPT_MAP = "concept_map"
    
    # Data visualizations
    PIE_CHART = "pie_chart"
    QUADRANT = "quadrant"
    NETWORK = "network"


class GenerationMethod(str, Enum):
    """Available generation methods."""
    SVG_TEMPLATE = "svg_template"
    MERMAID = "mermaid"


class DiagramRequest(BaseModel):
    """Input request for diagram generation."""
    content: str = Field(
        description="Text content for the diagram"
    )
    diagram_type: str = Field(
        description="Type of diagram from DiagramType enum or custom"
    )
    data_points: List[Dict[str, Any]] = Field(
        description="Structured data points for the diagram",
        default_factory=list
    )
    theme: Dict[str, Any] = Field(
        description="Visual theme for styling"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional constraints and preferences"
    )
    
    @validator('diagram_type')
    def validate_diagram_type(cls, v):
        """Allow both enum values and custom strings."""
        return v


class GenerationStrategy(BaseModel):
    """Selected generation strategy from conductor."""
    method: GenerationMethod = Field(
        description="Selected generation method"
    )
    confidence: float = Field(
        description="Confidence score (0-1)",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        description="Explanation for why this method was chosen"
    )
    fallback_method: Optional[GenerationMethod] = Field(
        default=None,
        description="Fallback method if primary fails"
    )


class DiagramPlan(BaseModel):
    """Execution plan from conductor agent."""
    request: DiagramRequest = Field(
        description="Original request"
    )
    selected_strategy: GenerationStrategy = Field(
        description="Chosen generation strategy"
    )
    preprocessing_steps: List[str] = Field(
        default_factory=list,
        description="Steps to prepare data"
    )
    postprocessing_steps: List[str] = Field(
        default_factory=list,
        description="Steps after generation"
    )
    estimated_time_ms: int = Field(
        description="Estimated generation time in milliseconds"
    )


class DiagramSpec(BaseModel):
    """Internal specification for diagram generation."""
    diagram_type: str = Field(
        description="Type of diagram to generate"
    )
    content: Dict[str, Any] = Field(
        description="Content and data for the diagram"
    )
    theme: Dict[str, Any] = Field(
        description="Theme for styling"
    )
    layout_hints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Layout preferences and hints"
    )


class DiagramOutput(BaseModel):
    """Output from diagram generation."""
    content: str = Field(
        description="Generated diagram (SVG string or base64 image)"
    )
    generation_method: str = Field(
        description="Method used for generation"
    )
    success: bool = Field(
        default=True,
        description="Whether generation succeeded"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about generation"
    )


# SVG-specific models
class SVGTemplateSpec(BaseModel):
    """Specification for SVG template usage."""
    template_name: str = Field(
        description="Name of the template to use"
    )
    text_replacements: Dict[str, str] = Field(
        description="Map of element IDs to replacement text"
    )
    color_replacements: Dict[str, str] = Field(
        description="Map of element IDs to color values"
    )
    style_overrides: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="CSS style overrides for elements"
    )


class SVGOutput(BaseModel):
    """Output from SVG generation."""
    svg_content: str = Field(
        description="Generated SVG as string"
    )
    template_name: str = Field(
        description="Template that was used"
    )
    elements_modified: int = Field(
        description="Number of elements modified"
    )
    validation_passed: bool = Field(
        default=True,
        description="Whether SVG validation passed"
    )


# Mermaid-specific models
class MermaidSpec(BaseModel):
    """Specification for Mermaid generation."""
    diagram_type: str = Field(
        description="Mermaid diagram type"
    )
    mermaid_code: str = Field(
        description="Generated Mermaid code"
    )
    theme_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Theme variables for Mermaid"
    )
    render_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Rendering options"
    )


class MermaidOutput(BaseModel):
    """Output from Mermaid generation."""
    mermaid_code: str = Field(
        description="Mermaid source code"
    )
    svg_output: str = Field(
        description="Rendered SVG"
    )
    diagram_type: str = Field(
        description="Type of Mermaid diagram"
    )
    render_time_ms: int = Field(
        description="Time taken to render"
    )


# Routing models
class TemplateAvailability(BaseModel):
    """Check for template availability."""
    diagram_type: str
    has_template: bool
    template_path: Optional[str] = None
    supports_customization: bool = False


class MermaidSupport(BaseModel):
    """Check for Mermaid support."""
    diagram_type: str
    is_supported: bool
    mermaid_type: Optional[str] = None
    complexity_rating: Optional[str] = None  # simple, moderate, complex


class RouteDecision(BaseModel):
    """Routing decision with rationale."""
    primary_method: GenerationMethod
    confidence: float
    rationale: str
    fallback_chain: List[GenerationMethod] = Field(
        default_factory=list,
        description="Ordered list of fallback methods"
    )
    estimated_quality: str = Field(
        description="Expected quality: high, medium, acceptable"
    )
    estimated_time_ms: int = Field(
        description="Expected generation time"
    )