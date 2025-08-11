"""
Layout Architect Agent - Content-aware layout generation.

This agent receives prepared content from Content Agent and generates
optimal layouts based on actual content volume, priorities, and constraints.
No more guessing - layouts are created to fit the content perfectly.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from src.models.agents import Slide
from src.utils.logger import setup_logger
from src.utils.model_utils import create_model_with_fallback
from src.models.design_tokens import ThemeDefinition
from ...model_types.layout_state import LayoutEngineConfig
from ...models import (
    MVPLayout, MVPContainer, GridPosition, ContainerContent,
    LayoutSpec, LayoutHints, ContentState
)
from ..content_agent import ContentManifest, VisualSpec

logger = setup_logger(__name__)


class LayoutArchitectContext(BaseModel):
    """Context for layout generation with prepared content"""
    slide: Slide
    theme: ThemeDefinition
    content_manifest: ContentManifest
    session_id: Optional[str] = None
    presentation_context: Optional[Dict[str, Any]] = None


class ContainerPlacement(BaseModel):
    """Placement decision for a content container"""
    content_id: str = Field(description="ID from content manifest")
    content_type: str = Field(description="text or visual")
    position: GridPosition = Field(description="Grid position")
    style: str = Field(description="Visual style (h1, body, etc.)")
    priority: str = Field(description="Content priority (P1-P4)")


class LayoutArchitectOutput(BaseModel):
    """Output from Layout Architect"""
    layout_pattern: str = Field(
        description="Selected layout pattern based on content and structure preference"
    )
    container_placements: List[ContainerPlacement] = Field(
        description="Placement decisions for all content"
    )
    white_space_ratio: float = Field(
        description="Calculated white space ratio",
        ge=0, le=1
    )
    balance_score: float = Field(
        description="Visual balance score",
        ge=0, le=1
    )
    structure_preference_honored: bool = Field(
        description="Whether strawman structure preference was successfully implemented"
    )
    layout_rationale: str = Field(
        description="Explanation of layout decisions"
    )


class LayoutArchitectAgent:
    """
    Layout Architect Agent - Creates layouts based on prepared content.
    
    This agent:
    1. Receives prepared, word-counted content from Content Agent
    2. Analyzes content volume, priorities, and visual requirements
    3. Selects appropriate layout pattern honoring structure preference
    4. Places content optimally based on priorities and visual balance
    5. Ensures all content fits within slide bounds
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite-preview-06-17"):
        """Initialize with AI model and layout tools"""
        self.model = create_model_with_fallback(model_name, timeout_seconds=30)
        
        # Create agent with layout tools only (no content analysis needed)
        self.agent = Agent(
            self.model,
            output_type=LayoutArchitectOutput,
            deps_type=LayoutArchitectContext,
            tools=[],
            system_prompt=self._get_system_prompt(),
            retries=2
        )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for content-aware layout generation"""
        return """You are the Layout Architect - a master of visual composition who creates 
perfect layouts based on PREPARED CONTENT. You receive word-counted, prioritized content 
and create layouts that honor structure preferences while ensuring everything fits perfectly.

KEY ADVANTAGES YOU HAVE:
1. Content is already prepared with exact word counts
2. Visual descriptions are complete and detailed
3. Priorities (P1-P4) guide your placement decisions
4. No guessing - you know exactly what needs to fit

YOUR PROCESS:

STEP 1 - CONTENT ANALYSIS:
- Review content manifest for total word count and visual count
- Note content density (light/medium/heavy) 
- Identify P1 (critical) content that needs prominence
- Check structure_preference from slide data

STEP 2 - PATTERN SELECTION:
- Use generate_layout_pattern tool with:
  * structure_preference as primary guide
  * content_density to ensure fit
  * visual_count to allocate space
- Map preferences to patterns:
  * "Two-column layout" → golden_ratio or f_pattern
  * "Grid layout (2x2)" → z_pattern with quadrants
  * "Full-bleed hero image" → hero pattern
  * "Single focal point" → centered pattern

STEP 3 - CONTENT PLACEMENT:
- Use calculate_grid_positions for each content piece
- Place by priority:
  * P1 content gets prime positions (top, center, large)
  * P2 content gets good visibility
  * P3 content fills supporting areas
  * P4 content only if space permits
- Allocate space based on word count:
  * Title: ~20 height units
  * 20 words: ~16 height units
  * 50 words: ~24 height units
  * 100 words: ~40 height units
  * Visuals: based on space_requirement

STEP 4 - VALIDATION:
- Use validate_layout to ensure no overlaps
- Use score_visual_balance for quality check
- Verify all P1 and P2 content is placed
- Confirm white space ratio is healthy (0.3-0.5)

LAYOUT QUALITY REQUIREMENTS:
- Honor structure_preference from slide (set structure_preference_honored=true)
- Place all P1 and P2 priority content
- Maintain visual hierarchy (P1 > P2 > P3 > P4)
- Achieve balance_score > 0.7
- Keep white_space_ratio between 0.3-0.5
- Minimum 8-unit margins, 4-unit gutters

CRITICAL: You have prepared content with exact sizes. No more guessing! 
Use the content_manifest to make informed layout decisions that WILL work."""
    
    async def generate_layout(
        self,
        slide: Slide,
        theme: ThemeDefinition,
        content_manifest: ContentManifest,
        presentation_context: Optional[Dict[str, Any]] = None,
        config: Optional[LayoutEngineConfig] = None
    ) -> MVPLayout:
        """
        Generate content-aware layout.
        
        Args:
            slide: Original slide data
            theme: Design theme
            content_manifest: Prepared content with word counts and priorities
            presentation_context: Optional presentation context
            config: Optional layout configuration
            
        Returns:
            MVPLayout with optimal content placement
        """
        try:
            logger.info(f"Generating content-aware layout for slide {slide.slide_id}")
            logger.info(f"  - Content words: {content_manifest.total_word_count}/{content_manifest.word_count_limit}")
            logger.info(f"  - Visuals: {content_manifest.visual_count}")
            logger.info(f"  - Density: {content_manifest.content_density}")
            logger.info(f"  - Structure preference: {content_manifest.structure_preference}")
            
            # Create context
            context = LayoutArchitectContext(
                slide=slide,
                theme=theme,
                content_manifest=content_manifest,
                session_id=presentation_context.get('session_id') if presentation_context else None,
                presentation_context=presentation_context
            )
            
            # Build prompt
            prompt = self._build_layout_prompt(slide, content_manifest, theme, config)
            
            # Run agent with timeout
            logger.info("Running Layout Architect with prepared content...")
            import asyncio
            try:
                # Add timeout to prevent hanging
                result = await asyncio.wait_for(
                    self.agent.run(prompt, deps=context),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Layout generation timed out for slide {slide.slide_id}")
                return self._create_fallback_layout(slide, content_manifest)
            
            # Convert to MVPLayout
            layout = self._build_mvp_layout(result.output, slide, content_manifest)
            
            # Log results
            logger.info(f"Layout generated successfully:")
            logger.info(f"  - Pattern: {result.output.layout_pattern}")
            logger.info(f"  - Containers: {len(layout.containers)}")
            logger.info(f"  - White space: {layout.white_space_ratio:.2f}")
            logger.info(f"  - Balance: {layout.alignment_score:.2f}")
            logger.info(f"  - Preference honored: {result.output.structure_preference_honored}")
            
            return layout
            
        except Exception as e:
            logger.error(f"Layout generation failed for slide {slide.slide_id}: {e}")
            return self._create_fallback_layout(slide, content_manifest)
    
    def _build_layout_prompt(
        self,
        slide: Slide,
        manifest: ContentManifest,
        theme: ThemeDefinition,
        config: Optional[LayoutEngineConfig]
    ) -> str:
        """Build prompt with content manifest details"""
        # Build content summary
        content_summary = f"""
PREPARED CONTENT SUMMARY:
- Total words: {manifest.total_word_count} (limit: {manifest.word_count_limit})
- Content density: {manifest.content_density}
- Visual elements: {manifest.visual_count}
- Reading flow: {manifest.preferred_reading_flow}

TITLE (P1 - {manifest.title.word_count} words):
{manifest.title.text}

MAIN POINTS ({len(manifest.main_points)} items):"""
        
        for i, point in enumerate(manifest.main_points):
            content_summary += f"\n- {point.priority} ({point.word_count} words): {point.text[:50]}..."
        
        if manifest.supporting_text:
            content_summary += f"\n\nSUPPORTING TEXT ({manifest.supporting_text.priority} - {manifest.supporting_text.word_count} words)"
        
        if manifest.primary_visual:
            content_summary += f"\n\nPRIMARY VISUAL ({manifest.primary_visual.space_requirement}): {manifest.primary_visual.visual_type}"
        
        # Build prompt
        return f"""Generate content-aware layout for this slide:

SLIDE CONTEXT:
- ID: {slide.slide_id}
- Type: {slide.slide_type}
- Structure Preference: {manifest.structure_preference or 'None'}

{content_summary}

THEME: {theme.name}
Available Templates: {list(theme.layout_templates.keys()) if hasattr(theme, 'layout_templates') else 'None'}

LAYOUT REQUIREMENTS:
1. Use generate_layout_pattern tool to select pattern matching structure preference "{manifest.structure_preference}"
2. Use calculate_grid_positions tool to place all content by priority
3. Use validate_layout tool to ensure no overlaps
4. Use score_visual_balance tool to optimize placement

CRITICAL SUCCESS CRITERIA:
- Honor structure preference exactly (set structure_preference_honored=true if successful)
- Place all P1 and P2 content prominently
- Ensure content fits based on provided word counts
- Achieve white_space_ratio between 0.3-0.5
- Achieve balance_score > 0.7

Generate the layout with these exact content pieces."""
    
    def _build_mvp_layout(
        self,
        output: LayoutArchitectOutput,
        slide: Slide,
        manifest: ContentManifest
    ) -> MVPLayout:
        """Convert architect output to MVPLayout"""
        containers = []
        
        # Map content to containers using placements
        for placement in output.container_placements:
            # Find content in manifest
            content_text = ""
            if placement.content_id == "title":
                content_text = manifest.title.text
            else:
                # Search in main points
                for i, point in enumerate(manifest.main_points):
                    if placement.content_id == f"point_{i+1}":
                        content_text = point.text
                        break
                
                # Check supporting text
                if not content_text and manifest.supporting_text and placement.content_id == "supporting":
                    content_text = manifest.supporting_text.text
            
            # Create container
            container = MVPContainer(
                name=f"{slide.slide_id}_{placement.content_id}",
                position=placement.position,
                content=ContainerContent(
                    type=placement.content_type,
                    text=content_text,
                    style=placement.style
                )
            )
            containers.append(container)
        
        # Map pattern to layout name
        layout_name = self._map_pattern_to_layout_name(output.layout_pattern)
        
        # Map content density values
        density_map = {"light": "low", "medium": "medium", "heavy": "high"}
        mapped_density = density_map.get(manifest.content_density, "medium")
        
        # Map reading flow values
        flow_map = {"linear": "vertical", "non-linear": "grid", "mixed": "horizontal"}
        mapped_flow = flow_map.get(manifest.preferred_reading_flow, "vertical")
        
        return MVPLayout(
            slide_id=slide.slide_id,
            slide_number=getattr(slide, 'slide_number', 1),
            slide_type=slide.slide_type,
            layout=layout_name,
            layout_spec=LayoutSpec(
                source="custom",
                layout_hints=LayoutHints(
                    content_density=mapped_density,
                    visual_emphasis=0.5 if manifest.visual_count > 0 else 0.2,
                    preferred_flow=mapped_flow
                )
            ),
            containers=containers,
            content_state=ContentState(
                base_content="complete",
                layout="complete",
                research="not_applicable",
                visuals="specified" if manifest.visual_count > 0 else "not_applicable",
                charts="specified" if any(v.visual_type == "chart" for v in [manifest.primary_visual] + manifest.supporting_visuals if v) else "not_applicable"
            ),
            white_space_ratio=output.white_space_ratio,
            alignment_score=output.balance_score,
            slide_title=slide.title,
            strawman_structure_preference=manifest.structure_preference
        )
    
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
            "focal": "focalPoint",
            "centered": "centered"
        }
        return pattern_layout_map.get(pattern, "contentAwareLayout")
    
    def _create_fallback_layout(self, slide: Slide, manifest: ContentManifest) -> MVPLayout:
        """Create content-aware fallback layout"""
        logger.info(f"Creating content-aware fallback for slide {slide.slide_id}")
        
        # Map content density and flow values
        density_map = {"light": "low", "medium": "medium", "heavy": "high"}
        flow_map = {"linear": "vertical", "non-linear": "grid", "mixed": "horizontal"}
        
        containers = []
        y_offset = 8
        
        # Add title
        containers.append(MVPContainer(
            name=f"{slide.slide_id}_title",
            position=GridPosition(
                leftInset=8,
                topInset=y_offset,
                width=144,
                height=20
            ),
            content=ContainerContent(
                type="text",
                text=manifest.title.text,
                style="h1"
            )
        ))
        y_offset += 24
        
        # Try to honor structure preference even in fallback
        if manifest.structure_preference and "two-column" in manifest.structure_preference.lower():
            # Two-column fallback
            left_items = manifest.main_points[:len(manifest.main_points)//2]
            right_items = manifest.main_points[len(manifest.main_points)//2:]
            
            # Left column
            for i, point in enumerate(left_items):
                containers.append(MVPContainer(
                    name=f"{slide.slide_id}_left_{i+1}",
                    position=GridPosition(
                        leftInset=8,
                        topInset=y_offset + (i * 20),
                        width=68,
                        height=16
                    ),
                    content=ContainerContent(
                        type="text",
                        text=point.text,
                        style="body"
                    )
                ))
            
            # Right column
            for i, point in enumerate(right_items):
                containers.append(MVPContainer(
                    name=f"{slide.slide_id}_right_{i+1}",
                    position=GridPosition(
                        leftInset=80,
                        topInset=y_offset + (i * 20),
                        width=68,
                        height=16
                    ),
                    content=ContainerContent(
                        type="text",
                        text=point.text,
                        style="body"
                    )
                ))
        else:
            # Default vertical layout
            for i, point in enumerate(manifest.main_points):
                containers.append(MVPContainer(
                    name=f"{slide.slide_id}_point_{i+1}",
                    position=GridPosition(
                        leftInset=8,
                        topInset=y_offset,
                        width=144,
                        height=16
                    ),
                    content=ContainerContent(
                        type="text",
                        text=point.text,
                        style="body"
                    )
                ))
                y_offset += 20
        
        return MVPLayout(
            slide_id=slide.slide_id,
            slide_number=getattr(slide, 'slide_number', 1),
            slide_type=slide.slide_type,
            layout="contentAwareFallback",
            layout_spec=LayoutSpec(
                source="custom",
                layout_hints=LayoutHints(
                    content_density=density_map.get(manifest.content_density, "medium"),
                    visual_emphasis=0.5 if manifest.visual_count > 0 else 0.2,
                    preferred_flow=flow_map.get(manifest.preferred_reading_flow, "vertical")
                )
            ),
            containers=containers,
            content_state=ContentState(
                base_content="complete",
                layout="complete",
                research="not_applicable",
                visuals="not_applicable",
                charts="not_applicable"
            ),
            white_space_ratio=0.4,
            alignment_score=0.7,
            slide_title=slide.title,
            strawman_structure_preference=manifest.structure_preference
        )