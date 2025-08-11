"""
Diagram Generation Utilities
============================

This package provides two strategies for diagram generation:
1. SVG Templates - Fast, deterministic, presentation-ready
2. Mermaid - Code-driven, flexible, wide variety

The conductor agent intelligently routes requests to the optimal strategy.
"""

from .models import (
    DiagramType,
    GenerationMethod,
    DiagramRequest,
    DiagramSpec,
    DiagramOutput,
    DiagramPlan,
    GenerationStrategy,
    SVGOutput,
    MermaidOutput
)

from .conductor import ConductorAgent
from .svg_agent import SVGDiagramAgent, SVGTemplateLibrary
from .mermaid_agent import MermaidDiagramAgent, MermaidTemplates

__all__ = [
    # Models
    "DiagramType",
    "GenerationMethod",
    "DiagramRequest",
    "DiagramSpec",
    "DiagramOutput",
    "DiagramPlan",
    "GenerationStrategy",
    "SVGOutput",
    "MermaidOutput",
    
    # Agents and Engines
    "ConductorAgent",
    "SVGDiagramAgent",
    "SVGTemplateLibrary",
    "MermaidDiagramAgent",
    "MermaidTemplates"
]

# Version info
__version__ = "1.0.0"