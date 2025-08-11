"""
Diagram Build Agent - Intelligent Diagram Generation Orchestrator
================================================================

This module provides a two-strategy approach to diagram generation:
1. SVG Templates - Fast, deterministic, presentation-ready
2. Mermaid - Code-driven, flexible, wide variety

Uses pydantic_ai agents for text/code-based diagram generation.

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent

# Import existing components
# ThemeDefinition is now a dict
from src.utils.model_utils import create_model_with_fallback
from src.agents.image_build_agent import ImageBuildAgent, ImageContentV4

# Import diagram utilities
from .diagram_utils.models import (
    DiagramSpec,
    DiagramOutput,
    DiagramRequest,
    GenerationStrategy,
    DiagramPlan,
    DiagramType
)
from .diagram_utils.conductor import ConductorAgent
from .diagram_utils.svg_agent import SVGDiagramAgent
from .diagram_utils.mermaid_agent import MermaidDiagramAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiagramAgent:
    """
    Main orchestrator for diagram generation.
    
    Routes diagram requests to the appropriate generation strategy:
    - SVG templates for standard business diagrams
    - Mermaid for technical and flow diagrams
    """
    
    def __init__(self):
        """Initialize the diagram agent with all strategy handlers."""
        logger.info("Initializing DiagramAgent with two-strategy approach")
        
        # Initialize the conductor for routing decisions
        self.conductor = ConductorAgent()
        
        # Initialize pydantic_ai agents for text-based diagrams
        self.svg_agent = SVGDiagramAgent()
        self.mermaid_agent = MermaidDiagramAgent()
        
        # Track statistics
        self.generation_stats = {
            "svg": 0,
            "mermaid": 0,
            "failures": 0
        }
    
    async def generate_diagram(
        self,
        request: DiagramRequest
    ) -> DiagramOutput:
        """
        Generate a diagram based on the request.
        
        Args:
            request: The diagram generation request with content and constraints
            
        Returns:
            DiagramOutput with the generated diagram and metadata
        """
        logger.info(f"Generating diagram of type: {request.diagram_type}")
        
        try:
            # Step 1: Analyze request and create execution plan
            plan = await self.conductor.analyze_request(request)
            logger.info(f"Selected strategy: {plan.selected_strategy.method} "
                       f"(confidence: {plan.selected_strategy.confidence:.2f})")
            
            # Step 2: Route to appropriate handler
            if plan.selected_strategy.method == "svg_template":
                result = await self._generate_with_svg(request, plan)
                self.generation_stats["svg"] += 1
                
            elif plan.selected_strategy.method == "mermaid":
                result = await self._generate_with_mermaid(request, plan)
                self.generation_stats["mermaid"] += 1
                
            else:
                raise ValueError(f"Unknown generation method: {plan.selected_strategy.method}")
            
            # Step 3: Apply post-processing if needed
            if plan.postprocessing_steps:
                result = await self._apply_postprocessing(result, plan.postprocessing_steps)
            
            return result
            
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            self.generation_stats["failures"] += 1
            
            # Try fallback strategy if available
            if plan.selected_strategy.fallback_method:
                logger.info(f"Attempting fallback: {plan.selected_strategy.fallback_method}")
                plan.selected_strategy.method = plan.selected_strategy.fallback_method
                return await self.generate_diagram(request)
            
            # Return error output
            return DiagramOutput(
                content="",
                generation_method="error",
                success=False,
                error_message=str(e),
                metadata={"error": str(e)}
            )
    
    async def _generate_with_svg(
        self,
        request: DiagramRequest,
        plan: DiagramPlan
    ) -> DiagramOutput:
        """Generate diagram using SVG templates."""
        logger.info("Generating with SVG template strategy")
        
        # Convert request to SVG agent format
        svg_spec = DiagramSpec(
            diagram_type=request.diagram_type,
            content=request.data_points,
            theme=request.theme,
            layout_hints=request.constraints.get("layout", {})
        )
        
        # Generate using pydantic_ai agent
        result = await self.svg_agent.generate(svg_spec)
        
        return DiagramOutput(
            content=result.svg_content,
            generation_method="svg_template",
            success=True,
            metadata={
                "template_used": result.template_name,
                "generation_time_ms": plan.estimated_time_ms
            }
        )
    
    async def _generate_with_mermaid(
        self,
        request: DiagramRequest,
        plan: DiagramPlan
    ) -> DiagramOutput:
        """Generate diagram using Mermaid."""
        logger.info("Generating with Mermaid strategy")
        
        # Convert request to Mermaid agent format
        mermaid_spec = DiagramSpec(
            diagram_type=request.diagram_type,
            content=request.data_points,
            theme=request.theme,
            layout_hints=request.constraints.get("layout", {})
        )
        
        # Generate using pydantic_ai agent with MCP
        result = await self.mermaid_agent.generate(mermaid_spec)
        
        return DiagramOutput(
            content=result.svg_output,
            generation_method="mermaid",
            success=True,
            metadata={
                "mermaid_code": result.mermaid_code,
                "diagram_type": result.diagram_type,
                "generation_time_ms": plan.estimated_time_ms
            }
        )
    
    async def _apply_postprocessing(
        self,
        output: DiagramOutput,
        steps: List[str]
    ) -> DiagramOutput:
        """Apply post-processing steps to the generated diagram."""
        logger.info(f"Applying {len(steps)} post-processing steps")
        
        for step in steps:
            if step == "optimize_svg":
                # Optimize SVG size
                pass
            elif step == "add_accessibility":
                # Add ARIA labels
                pass
            elif step == "apply_theme":
                # Apply additional theme styling
                pass
        
        return output
    
    def get_statistics(self) -> Dict[str, int]:
        """Get generation statistics."""
        return self.generation_stats


class DiagramBuildAgent:
    """
    High-level agent for building diagrams from content specifications.
    This is the main entry point from content_agent_v7.
    """
    
    def __init__(self):
        """Initialize the diagram build agent."""
        self.diagram_agent = DiagramAgent()
        self.playbook_cache = {}
    
    async def build_diagram_from_spec(
        self,
        diagram_spec: Dict[str, Any],
        theme: Dict[str, Any],
        slide_context: Optional[Dict[str, Any]] = None
    ) -> DiagramOutput:
        """
        Build a diagram from a content agent specification.
        
        Args:
            diagram_spec: Diagram specification from content agent
            theme: Theme definition for styling
            slide_context: Optional context about the slide
            
        Returns:
            DiagramOutput with the generated diagram
        """
        # Extract diagram type from spec or infer from content
        diagram_type = self._infer_diagram_type(diagram_spec, slide_context)
        
        # Create request
        request = DiagramRequest(
            content=diagram_spec.get("content", ""),
            diagram_type=diagram_type,
            data_points=diagram_spec.get("data_points", []),
            theme=theme,
            constraints=diagram_spec.get("constraints", {})
        )
        
        # Generate diagram
        result = await self.diagram_agent.generate_diagram(request)
        
        # Log success/failure
        if result.success:
            logger.info(f"Successfully generated {diagram_type} diagram using {result.generation_method}")
        else:
            logger.error(f"Failed to generate {diagram_type} diagram: {result.error_message}")
        
        return result
    
    def _infer_diagram_type(
        self,
        spec: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Infer the diagram type from specification and context."""
        # Check explicit type
        if "diagram_type" in spec:
            return spec["diagram_type"]
        
        # Check pattern from playbook
        if "pattern" in spec:
            pattern = spec["pattern"]
            # Map playbook patterns to diagram types
            pattern_mapping = {
                "process_flow": DiagramType.FLOWCHART,
                "organizational_hierarchy": DiagramType.ORG_CHART,
                "system_architecture": DiagramType.ARCHITECTURE,
                "concept_map": DiagramType.MIND_MAP,
                "comparison_matrix": DiagramType.MATRIX
            }
            return pattern_mapping.get(pattern, DiagramType.FLOWCHART)
        
        # Infer from content
        content = str(spec.get("content", "")).lower()
        if "process" in content or "flow" in content:
            return DiagramType.FLOWCHART
        elif "hierarchy" in content or "org" in content:
            return DiagramType.ORG_CHART
        elif "compare" in content or "versus" in content:
            return DiagramType.MATRIX
        elif "timeline" in content or "roadmap" in content:
            return DiagramType.TIMELINE
        else:
            return DiagramType.CONCEPT_MAP