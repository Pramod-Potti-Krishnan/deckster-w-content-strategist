"""
Conductor Agent - Intelligent Routing for Diagram Generation
===========================================================

This agent analyzes diagram requests and routes them to the most
appropriate generation strategy based on:
- Diagram type and complexity
- Available templates
- Quality requirements
- Time constraints

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from src.utils.model_utils import create_model_with_fallback
from .models import (
    DiagramRequest,
    DiagramPlan,
    GenerationStrategy,
    GenerationMethod,
    DiagramType,
    TemplateAvailability,
    MermaidSupport,
    RouteDecision
)

logger = logging.getLogger(__name__)


class RoutingContext(BaseModel):
    """Context for routing decisions."""
    request: DiagramRequest
    template_availability: TemplateAvailability
    mermaid_support: MermaidSupport
    quality_requirement: str = Field(default="high")
    time_constraint_ms: Optional[int] = Field(default=None)


class ConductorAgent:
    """
    Intelligent conductor that routes diagram requests to the optimal
    generation strategy.
    """
    
    # Template availability mapping
    AVAILABLE_TEMPLATES = {
        DiagramType.PYRAMID: "templates/pyramid_3_level.svg",
        DiagramType.FUNNEL: "templates/funnel_5_stage.svg",
        DiagramType.MATRIX: "templates/matrix_2x2.svg",
        DiagramType.TIMELINE: "templates/timeline_horizontal.svg",
        DiagramType.CYCLE: "templates/cycle_4_step.svg",
        DiagramType.VENN: "templates/venn_2_circle.svg",
        DiagramType.HUB_SPOKE: "templates/hub_spoke_6.svg",
        DiagramType.HONEYCOMB: "templates/honeycomb_7.svg",
    }
    
    # Mermaid support mapping
    MERMAID_SUPPORTED = {
        DiagramType.FLOWCHART: ("flowchart", "simple"),
        DiagramType.SEQUENCE: ("sequence", "simple"),
        DiagramType.GANTT: ("gantt", "moderate"),
        DiagramType.PIE_CHART: ("pie", "simple"),
        DiagramType.MIND_MAP: ("mindmap", "moderate"),
        DiagramType.TIMELINE: ("timeline", "simple"),
        DiagramType.JOURNEY_MAP: ("journey", "moderate"),
        DiagramType.QUADRANT: ("quadrantChart", "simple"),
        DiagramType.ARCHITECTURE: ("flowchart", "complex"),
        DiagramType.NETWORK: ("flowchart", "complex"),
    }
    
    # Quality-speed tradeoffs
    STRATEGY_CHARACTERISTICS = {
        GenerationMethod.SVG_TEMPLATE: {
            "quality": "perfect",
            "speed_ms": 100,
            "flexibility": "low",
            "deterministic": True
        },
        GenerationMethod.MERMAID: {
            "quality": "good",
            "speed_ms": 500,
            "flexibility": "high",
            "deterministic": True
        }
    }
    
    def __init__(self):
        """Initialize the conductor agent."""
        self.routing_agent = self._create_routing_agent()
        self.template_base_path = Path(__file__).parent / "templates"
    
    def _create_routing_agent(self) -> Agent:
        """Create the pydantic_ai agent for routing decisions."""
        return Agent(
            create_model_with_fallback("gemini-2.5-flash"),
            result_type=RouteDecision,
            system_prompt="""You are a diagram routing specialist. Analyze diagram requests and select the optimal generation strategy.
            
            Consider:
            1. Template availability - Use SVG if perfect template exists
            2. Diagram complexity - Simple diagrams work well with Mermaid
            3. Time constraints - SVG is fastest
            4. Quality requirements - SVG is most consistent
            5. Flexibility - Mermaid offers more flexibility for dynamic content
            
            Prioritize in this order:
            1. SVG templates (if available and suitable)
            2. Mermaid (if supported and appropriate)"""
        )
    
    async def analyze_request(self, request: DiagramRequest) -> DiagramPlan:
        """
        Analyze a diagram request and create an execution plan.
        
        Args:
            request: The diagram generation request
            
        Returns:
            DiagramPlan with selected strategy and execution details
        """
        logger.info(f"Analyzing request for {request.diagram_type} diagram")
        
        # Check template availability
        template_check = self._check_template_availability(request.diagram_type)
        
        # Check Mermaid support
        mermaid_check = self._check_mermaid_support(request.diagram_type)
        
        # Create routing context
        context = RoutingContext(
            request=request,
            template_availability=template_check,
            mermaid_support=mermaid_check,
            quality_requirement=request.constraints.get("quality", "high"),
            time_constraint_ms=request.constraints.get("max_time_ms")
        )
        
        # Get routing decision from agent
        routing_decision = await self._get_routing_decision(context)
        
        # Create execution plan
        plan = self._create_execution_plan(request, routing_decision)
        
        logger.info(f"Created plan: {plan.selected_strategy.method} "
                   f"(confidence: {plan.selected_strategy.confidence:.2f})")
        
        return plan
    
    def _check_template_availability(self, diagram_type: str) -> TemplateAvailability:
        """Check if an SVG template is available for the diagram type."""
        # Check enum values
        if diagram_type in self.AVAILABLE_TEMPLATES:
            template_path = self.AVAILABLE_TEMPLATES[diagram_type]
            full_path = self.template_base_path / template_path
            
            return TemplateAvailability(
                diagram_type=diagram_type,
                has_template=full_path.exists(),
                template_path=str(template_path) if full_path.exists() else None,
                supports_customization=True
            )
        
        # Check for custom templates
        custom_path = self.template_base_path / f"{diagram_type}.svg"
        if custom_path.exists():
            return TemplateAvailability(
                diagram_type=diagram_type,
                has_template=True,
                template_path=f"{diagram_type}.svg",
                supports_customization=True
            )
        
        return TemplateAvailability(
            diagram_type=diagram_type,
            has_template=False
        )
    
    def _check_mermaid_support(self, diagram_type: str) -> MermaidSupport:
        """Check if Mermaid supports the diagram type."""
        # Direct support check
        if diagram_type in self.MERMAID_SUPPORTED:
            mermaid_type, complexity = self.MERMAID_SUPPORTED[diagram_type]
            return MermaidSupport(
                diagram_type=diagram_type,
                is_supported=True,
                mermaid_type=mermaid_type,
                complexity_rating=complexity
            )
        
        # Check if it can be approximated with flowchart
        flowchart_compatible = [
            "process", "flow", "decision", "workflow", "algorithm"
        ]
        if any(term in diagram_type.lower() for term in flowchart_compatible):
            return MermaidSupport(
                diagram_type=diagram_type,
                is_supported=True,
                mermaid_type="flowchart",
                complexity_rating="moderate"
            )
        
        return MermaidSupport(
            diagram_type=diagram_type,
            is_supported=False
        )
    
    async def _get_routing_decision(self, context: RoutingContext) -> RouteDecision:
        """Get routing decision from the AI agent."""
        # Use deterministic rules for clear cases
        if context.template_availability.has_template:
            if context.quality_requirement == "perfect":
                return RouteDecision(
                    primary_method=GenerationMethod.SVG_TEMPLATE,
                    confidence=0.95,
                    rationale="Perfect template available with highest quality requirement",
                    fallback_chain=[GenerationMethod.MERMAID],
                    estimated_quality="perfect",
                    estimated_time_ms=100
                )
        
        if context.mermaid_support.is_supported:
            if context.mermaid_support.complexity_rating == "simple":
                return RouteDecision(
                    primary_method=GenerationMethod.MERMAID,
                    confidence=0.85,
                    rationale=f"Well-supported diagram type in Mermaid ({context.mermaid_support.mermaid_type})",
                    fallback_chain=[],
                    estimated_quality="good",
                    estimated_time_ms=500
                )
        
        # For complex cases, use the AI agent
        prompt = f"""Analyze this diagram request and decide the best generation strategy:
        
        Diagram Type: {context.request.diagram_type}
        Has SVG Template: {context.template_availability.has_template}
        Mermaid Support: {context.mermaid_support.is_supported} ({context.mermaid_support.mermaid_type if context.mermaid_support.is_supported else 'N/A'})
        Quality Required: {context.quality_requirement}
        Time Constraint: {context.time_constraint_ms}ms if specified
        
        Content Preview: {context.request.content[:200]}...
        Data Points: {len(context.request.data_points)} items
        
        Select the optimal strategy considering all factors."""
        
        result = await self.routing_agent.run(prompt)
        return result.data
    
    def _create_execution_plan(
        self,
        request: DiagramRequest,
        routing: RouteDecision
    ) -> DiagramPlan:
        """Create a detailed execution plan."""
        # Determine preprocessing steps
        preprocessing = []
        if routing.primary_method == GenerationMethod.SVG_TEMPLATE:
            preprocessing.append("validate_template_exists")
            preprocessing.append("map_data_to_template_elements")
        elif routing.primary_method == GenerationMethod.MERMAID:
            preprocessing.append("structure_data_for_mermaid")
            preprocessing.append("escape_special_characters")
        
        # Determine postprocessing steps
        postprocessing = []
        if request.constraints.get("add_accessibility", False):
            postprocessing.append("add_accessibility")
        if request.constraints.get("optimize_size", False):
            postprocessing.append("optimize_svg")
        
        # Create strategy
        strategy = GenerationStrategy(
            method=routing.primary_method,
            confidence=routing.confidence,
            reasoning=routing.rationale,
            fallback_method=routing.fallback_chain[0] if routing.fallback_chain else None
        )
        
        # Create plan
        return DiagramPlan(
            request=request,
            selected_strategy=strategy,
            preprocessing_steps=preprocessing,
            postprocessing_steps=postprocessing,
            estimated_time_ms=routing.estimated_time_ms
        )
    
    def has_svg_template(self, diagram_type: str) -> bool:
        """Quick check if SVG template exists."""
        return self._check_template_availability(diagram_type).has_template
    
    def is_mermaid_suitable(self, request: DiagramRequest) -> bool:
        """Quick check if Mermaid is suitable for the request."""
        support = self._check_mermaid_support(request.diagram_type)
        if not support.is_supported:
            return False
        
        # Check complexity
        if len(request.data_points) > 50 and support.complexity_rating == "simple":
            return False
        
        # Check for special requirements that Mermaid can't handle
        if request.constraints.get("require_3d", False):
            return False
        if request.constraints.get("artistic_style", False):
            return False
        
        return True