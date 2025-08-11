"""
Structure Layout Agent - Combined Content & Layout Director.

This agent merges the functionality of Structure Agent and Layout Engine
to create an atomic structure-to-layout generation process, eliminating
the Chinese whisper effect and preserving strawman context directly.
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from src.models.agents import Slide
from src.utils.logger import setup_logger
from ...utils.model_utils import create_model_with_fallback
from ...model_types.design_tokens import ThemeDefinition
from ...model_types.semantic_containers import (
    ContainerManifest, SemanticContainer, ContainerRelationship,
    ContentFlow, ContentImportance, ContainerRole, RelationshipType
)
from ...model_types.layout_state import LayoutEngineConfig
from ... import models as mvp_models
MVPLayout = mvp_models.MVPLayout
MVPContainer = mvp_models.MVPContainer
GridPosition = mvp_models.GridPosition
ContainerContent = mvp_models.ContainerContent
LayoutSpec = mvp_models.LayoutSpec
LayoutHints = mvp_models.LayoutHints
ContentState = mvp_models.ContentState

# Import all tools from both agents
from ..structure_agent.tools import (
    content_parser_tool, relationship_analyzer_tool, hierarchy_detector_tool,
    ContentParserInput, RelationshipAnalyzerInput, HierarchyDetectorInput
)
from ..layout_engine.tools import (
    layout_pattern_tool, grid_position_tool, layout_validator_tool, visual_balance_tool,
    LayoutPatternInput, GridPositionInput, LayoutValidationInput, VisualBalanceInput
)

logger = setup_logger(__name__)


class StructureLayoutContext(BaseModel):
    """Context for structure+layout generation"""
    slide: Slide
    theme: ThemeDefinition
    session_id: Optional[str] = None
    presentation_context: Optional[Dict[str, Any]] = None


class ContainerSpec(BaseModel):
    """Specification for a semantic container with layout hints"""
    id: str = Field(description="Unique identifier")
    role: str = Field(description="Semantic role")
    content: str = Field(description="Content text")
    importance: str = Field(description="high, medium, or low")
    visual_weight: float = Field(description="Visual prominence 0-1", ge=0, le=1)
    hierarchy_level: int = Field(description="Content hierarchy level", ge=1, le=5)
    layout_priority: int = Field(description="Layout priority order", ge=1)
    requires_visual: bool = Field(description="Needs visual element", default=False)


class LayoutZoneSpec(BaseModel):
    """Specification for a layout zone"""
    name: str = Field(description="Zone identifier")
    leftInset: int = Field(description="Left position in grid units")
    topInset: int = Field(description="Top position in grid units") 
    width: int = Field(description="Width in grid units")
    height: int = Field(description="Height in grid units")


class StructureLayoutOutput(BaseModel):
    """Combined output from StructureLayout Agent"""
    # Structure analysis results
    containers: List[ContainerSpec] = Field(
        description="Semantic containers with layout hints"
    )
    primary_message: str = Field(
        description="Main message of the slide"
    )
    content_flow: str = Field(
        description="Content flow pattern (linear, hierarchical, etc.)",
        default="linear"
    )
    
    # Layout generation results
    layout_pattern: str = Field(
        description="Selected layout pattern name"
    )
    zones: List[LayoutZoneSpec] = Field(
        description="Calculated layout zones"
    )
    container_positions: Dict[str, LayoutZoneSpec] = Field(
        description="Final container positions"
    )
    
    # Quality metrics
    white_space_ratio: float = Field(
        description="Calculated white space ratio",
        ge=0, le=1
    )
    balance_score: float = Field(
        description="Visual balance score",
        ge=0, le=1
    )
    structure_preference_honored: bool = Field(
        description="Whether strawman structure preference was honored",
        default=False
    )
    
    # Generation metadata
    generation_notes: List[str] = Field(
        description="Notes about the generation process",
        default_factory=list
    )


class StructureLayoutAgent:
    """
    Combined Structure + Layout Agent.
    
    This agent performs atomic structure analysis and layout generation,
    ensuring strawman metadata (especially slide_type and structure_preference)
    drives the entire process without information loss.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite-preview-06-17"):
        """Initialize with AI model and combined tools"""
        # Create model with fallback support and extended timeout for complex operations
        self.model = create_model_with_fallback(model_name, timeout_seconds=35)
        
        # Create agent with all tools from both previous agents
        self.agent = Agent(
            self.model,
            output_type=StructureLayoutOutput,
            deps_type=StructureLayoutContext,
            tools=[
                # Structure analysis tools
                content_parser_tool,
                relationship_analyzer_tool,
                hierarchy_detector_tool,
                # Layout generation tools
                layout_pattern_tool,
                grid_position_tool,
                layout_validator_tool,
                visual_balance_tool
            ],
            system_prompt=self._get_system_prompt(),
            retries=3  # More retries for complex operations
        )
    
    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt combining both agents' expertise"""
        return """You are the Structure Layout Director - a master of both content strategy 
and visual composition. Your role is to analyze slide content and generate optimal layouts 
in a single atomic operation, preserving user intent throughout.

CRITICAL REQUIREMENTS:
1. slide_type and structure_preference from the slide are SACROSANCT - they must drive your decisions
2. Honor the user-approved structure preferences exactly as specified
3. Use semantic analysis to create appropriate containers for the slide_type
4. Generate layout patterns that match the requested structure_preference

Your Process:
PHASE 1 - STRUCTURE ANALYSIS (using slide_type as primary guide):
- Use parse_content tool to analyze all slide fields
- Create containers appropriate for the slide_type:
  * title_slide: title + subtitle + presenter info containers
  * data_driven: title + chart/metrics + insights containers  
  * diagram_focused: title + diagram + explanation containers
  * content_heavy: title + multiple text containers
  * visual_heavy: title + large visual + caption containers
- Use analyze_relationships and detect_hierarchy tools for organization

PHASE 2 - LAYOUT GENERATION (using structure_preference as primary guide):
- Use generate_layout_pattern tool with structure_preference context
- Map structure preferences directly to layout patterns:
  * "Two-column layout" → two-column grid zones
  * "Grid layout (2x2)" → four-quadrant zones
  * "Full-bleed hero image" → hero layout with overlay
  * "Single focal point" → centered focal layout
- Use calculate_grid_positions for precise positioning
- Use validate_layout and score_visual_balance for quality

LAYOUT PATTERN MAPPING (CRITICAL):
- "Two-column layout" → golden_ratio or f_pattern with left/right zones
- "Grid layout (2x2)" → z_pattern with four quadrants
- "Full-bleed hero image" → single zone covering full area with overlay
- "Single focal point" → centered pattern with prominent main zone
- "Three-column" → rule_of_thirds pattern
- "Horizontal layout" → single row with multiple columns

SLIDE TYPE CONTAINER MAPPING (CRITICAL):
- title_slide: title (headline) + subtitle + metadata containers
- data_driven: title + chart (visual) + key metrics (data_point) + insights
- diagram_focused: title + diagram (visual) + explanation (supporting_evidence)
- content_heavy: title + multiple text containers (main_point, supporting_evidence)
- visual_heavy: title + large visual + caption/description
- mixed_content: title + text containers + visual containers

QUALITY REQUIREMENTS:
- White space ratio: 0.3-0.5 (30-50%)
- All positions must be integer grid coordinates
- Minimum 8-unit margins from edges
- 4-unit gutters between containers
- Visual balance score > 0.7

Your output must include:
- containers: Semantic containers with proper roles for the slide_type
- layout_pattern: Pattern name that honors structure_preference
- zones: Calculated layout zones matching the structure_preference
- container_positions: Final positions for all containers
- structure_preference_honored: Set to true only if you matched the preference

REMEMBER: You are eliminating the Chinese whisper effect. The slide_type and 
structure_preference must flow directly into your final layout decisions."""
    
    async def generate_structure_and_layout(
        self,
        slide: Slide,
        theme: ThemeDefinition,
        session_id: Optional[str] = None,
        presentation_context: Optional[Dict[str, Any]] = None,
        config: Optional[LayoutEngineConfig] = None
    ) -> MVPLayout:
        """
        Generate complete structure analysis and layout in one atomic operation.
        
        This method preserves slide_type and structure_preference throughout
        the entire generation process.
        """
        try:
            logger.info(f"Starting atomic structure+layout generation for slide {slide.slide_id}")
            logger.info(f"Slide type: {slide.slide_type}")
            logger.info(f"Structure preference: {getattr(slide, 'structure_preference', 'None')}")
            
            # Create context with full slide data
            context = StructureLayoutContext(
                slide=slide,
                theme=theme,
                session_id=session_id,
                presentation_context=presentation_context
            )
            
            # Build comprehensive prompt
            prompt = self._build_generation_prompt(slide, theme, config)
            logger.info(f"Built generation prompt with {len(prompt)} characters")
            
            # Run agent with extended timeout for Gemini 2.5 Flash Lite
            logger.info("Calling combined agent with all tools...")
            result = await self.agent.run(prompt, deps=context)
            logger.info(f"Agent run completed successfully")
            
            # Convert to MVPLayout
            layout = self._build_mvp_layout(result.output, slide, theme)
            
            # Log success metrics
            logger.info(f"Layout generated successfully:")
            logger.info(f"  - Containers: {len(layout.containers)}")
            logger.info(f"  - White space: {layout.white_space_ratio:.2f}")
            logger.info(f"  - Structure preference honored: {result.output.structure_preference_honored}")
            logger.info(f"  - Pattern used: {result.output.layout_pattern}")
            
            return layout
            
        except Exception as e:
            logger.error(f"Structure+Layout generation failed for slide {slide.slide_id}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            # Return fallback layout that still tries to honor structure preference
            return self._create_fallback_layout(slide, theme)
    
    def _build_generation_prompt(
        self,
        slide: Slide,
        theme: ThemeDefinition,
        config: Optional[LayoutEngineConfig]
    ) -> str:
        """Build comprehensive prompt with all slide context"""
        prompt = f"""Analyze and layout this slide content in one atomic operation:

SLIDE METADATA (CRITICAL CONTEXT):
- Slide ID: {slide.slide_id}
- Slide Number: {slide.slide_number}  
- Slide Type: {slide.slide_type} (USE AS PRIMARY GUIDE FOR CONTAINERS)
- Structure Preference: {getattr(slide, 'structure_preference', 'None')} (MUST HONOR THIS EXACTLY)

SLIDE CONTENT:
- Title: {slide.title}
- Narrative: {slide.narrative or 'None'}
- Key Points: {slide.key_points or []}
- Analytics Needed: {getattr(slide, 'analytics_needed', None) or 'None'}
- Visuals Needed: {getattr(slide, 'visuals_needed', None) or 'None'}
- Diagrams Needed: {getattr(slide, 'diagrams_needed', None) or 'None'}

THEME CONTEXT:
- Theme Name: {theme.name}
- Available Layout Templates: {list(theme.layout_templates.keys()) if hasattr(theme, 'layout_templates') else 'None'}

GENERATION REQUIREMENTS:
1. STRUCTURE ANALYSIS:
   - Use parse_content tool to create semantic containers appropriate for slide_type "{slide.slide_type}"
   - Use analyze_relationships tool to find content connections
   - Use detect_hierarchy tool to organize container priorities

2. LAYOUT GENERATION:
   - Use generate_layout_pattern tool to select pattern matching structure_preference "{getattr(slide, 'structure_preference', 'None')}"
   - Use calculate_grid_positions tool for precise container placement
   - Use validate_layout tool to ensure quality
   - Use score_visual_balance tool for balance optimization

3. CRITICAL SUCCESS CRITERIA:
   - containers must match slide_type requirements
   - layout_pattern must honor structure_preference exactly
   - structure_preference_honored must be true if you matched the preference
   - All container positions must be valid grid coordinates

Please generate both structure and layout atomically, ensuring no loss of context."""
        
        if config:
            prompt += f"""
LAYOUT CONFIG:
- Max iterations: {config.max_iterations}
- White space range: {config.white_space_min}-{config.white_space_max}
"""
        
        return prompt
    
    def _build_mvp_layout(
        self,
        output: StructureLayoutOutput,
        slide: Slide,
        theme: ThemeDefinition
    ) -> MVPLayout:
        """Convert agent output to MVPLayout"""
        containers = []
        
        # Convert containers with positions
        for container_spec in output.containers:
            # Get position from container_positions
            position_spec = output.container_positions.get(container_spec.id)
            if not position_spec:
                logger.warning(f"No position found for container {container_spec.id}")
                continue
            
            # Create MVPContainer
            mvp_container = MVPContainer(
                name=container_spec.id,  # MVPContainer uses 'name' not 'id'
                position=GridPosition(
                    leftInset=position_spec.leftInset,
                    topInset=position_spec.topInset,
                    width=position_spec.width,
                    height=position_spec.height
                ),
                content=ContainerContent(
                    type="visual" if container_spec.requires_visual else "text",
                    text=container_spec.content,
                    style=self._map_role_to_style(container_spec.role)
                )
            )
            containers.append(mvp_container)
        
        # Determine slide number
        slide_number = getattr(slide, 'slide_number', 1)
        
        # Map layout pattern to layout name
        layout_name = self._map_pattern_to_layout_name(output.layout_pattern)
        
        return MVPLayout(
            slide_id=slide.slide_id,
            slide_number=slide_number,
            slide_type=slide.slide_type,
            layout=layout_name,
            layout_spec=LayoutSpec(
                source="custom",
                layout_hints=LayoutHints(
                    content_density="medium",
                    visual_emphasis=0.5,
                    preferred_flow=output.content_flow
                )
            ),
            containers=containers,
            content_state=ContentState(
                base_content="complete",
                layout="generated",
                research="not_applicable",
                visuals="planned" if any(c.requires_visual for c in output.containers) else "not_applicable",
                charts="planned" if any("chart" in c.role.lower() for c in output.containers) else "not_applicable"
            ),
            white_space_ratio=output.white_space_ratio,
            alignment_score=output.balance_score,
            slide_title=slide.title,
            strawman_structure_preference=getattr(slide, 'structure_preference', None)
        )
    
    def _map_role_to_style(self, role: str) -> str:
        """Map semantic role to content style"""
        role_style_map = {
            "headline": "h1",
            "title": "h1", 
            "subtitle": "h2",
            "main_point": "body",
            "key_takeaway": "emphasis",
            "supporting_evidence_text": "body",
            "data_point": "metric",
            "kpi_metric": "metric",
            "call_to_action": "cta",
            "question": "emphasis",
            "definition": "body",
            "example": "body"
        }
        return role_style_map.get(role.lower(), "body")
    
    def _map_pattern_to_layout_name(self, pattern: str) -> str:
        """Map layout pattern to layout name"""
        pattern_layout_map = {
            "golden_ratio": "goldenRatio",
            "rule_of_thirds": "ruleOfThirds", 
            "z_pattern": "zPattern",
            "f_pattern": "fPattern",
            "symmetrical": "symmetrical",
            "asymmetrical": "asymmetrical",
            "two_column": "twoColumn",
            "grid_2x2": "grid2x2",
            "hero": "heroLayout",
            "focal": "focalPoint"
        }
        return pattern_layout_map.get(pattern, "generatedLayout")
    
    def _create_fallback_layout(self, slide: Slide, theme: ThemeDefinition) -> MVPLayout:
        """Create fallback layout that still tries to honor structure preference"""
        logger.info(f"Creating fallback layout for slide {slide.slide_id}")
        
        containers = []
        
        # Always include title
        if slide.title:
            containers.append(MVPContainer(
                name=f"{slide.slide_id}_title",
                position=GridPosition(
                    leftInset=8,
                    topInset=8,
                    width=144,
                    height=20
                ),
                content=ContainerContent(
                    type="text",
                    text=slide.title,
                    style="h1"
                )
            ))
        
        # Add content based on slide type and structure preference
        structure_pref = getattr(slide, 'structure_preference', '')
        y_offset = 32
        
        # Try to honor structure preference in fallback
        if "two-column" in structure_pref.lower():
            # Create two-column layout
            left_width = 70
            right_width = 70
            
            # Add key points to left column
            for i, point in enumerate(slide.key_points or []):
                if i >= 2:  # Limit for space
                    break
                containers.append(MVPContainer(
                    name=f"{slide.slide_id}_left_{i+1}",
                    position=GridPosition(
                        leftInset=8,
                        topInset=y_offset + (i * 20),
                        width=left_width,
                        height=16
                    ),
                    content=ContainerContent(
                        type="text",
                        text=point,
                        style="body"
                    )
                ))
            
            # Add remaining content to right column if any
            remaining_points = slide.key_points[2:] if slide.key_points and len(slide.key_points) > 2 else []
            for i, point in enumerate(remaining_points[:2]):
                containers.append(MVPContainer(
                    name=f"{slide.slide_id}_right_{i+1}",
                    position=GridPosition(
                        leftInset=82,  # 8 + 70 + 4 gutter
                        topInset=y_offset + (i * 20),
                        width=right_width,
                        height=16
                    ),
                    content=ContainerContent(
                        type="text",
                        text=point,
                        style="body"
                    )
                ))
        else:
            # Default vertical layout
            for i, point in enumerate(slide.key_points or []):
                containers.append(MVPContainer(
                    name=f"{slide.slide_id}_point_{i+1}",
                    position=GridPosition(
                        leftInset=8,
                        topInset=y_offset + (i * 20),
                        width=144,
                        height=16
                    ),
                    content=ContainerContent(
                        type="text",
                        text=point,
                        style="body"
                    )
                ))
        
        return MVPLayout(
            slide_id=slide.slide_id,
            slide_number=getattr(slide, 'slide_number', 1),
            slide_type=slide.slide_type,
            layout="fallbackLayout",
            layout_spec=LayoutSpec(
                source="custom",
                layout_hints=LayoutHints(
                    content_density="medium",
                    visual_emphasis=0.5,
                    preferred_flow="linear"
                )
            ),
            containers=containers,
            content_state=ContentState(
                base_content="complete",
                layout="fallback",
                research="not_applicable",
                visuals="not_applicable",
                charts="not_applicable"
            ),
            white_space_ratio=0.4,
            alignment_score=0.8,
            slide_title=slide.title,
            strawman_structure_preference=getattr(slide, 'structure_preference', None)
        )