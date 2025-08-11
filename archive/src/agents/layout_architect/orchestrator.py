"""
Orchestrator for the two-agent Layout Architect system.

This orchestrator coordinates the Theme Agent and StructureLayout Agent
to generate optimal layouts for slides with preserved strawman context.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.models.agents import Slide, PresentationStrawman
from src.utils.logger import setup_logger
from .model_types.design_tokens import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken, 
    DimensionToken, TokenValue, TokenType, LayoutTemplate, GridZone
)
from .model_types.semantic_containers import ContainerManifest
from .model_types.layout_state import LayoutEngineConfig
from .models import MVPLayout, LayoutSpec, LayoutHints, ContentState
from .agents.theme_agent import ThemeAgent
from .agents.structure_layout_agent import StructureLayoutAgent

# Keep old agents available as fallback
try:
    from .agents.structure_agent import StructureAgent
    from .agents.layout_engine import LayoutEngineAgent
    HAS_OLD_AGENTS = True
except ImportError:
    HAS_OLD_AGENTS = False

logger = setup_logger(__name__)


class LayoutGenerationRequest(BaseModel):
    """Request for layout generation"""
    slide: Slide
    user_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="User/brand context for theme generation"
    )
    presentation_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Presentation-wide context"
    )
    layout_config: Optional[LayoutEngineConfig] = Field(
        default=None,
        description="Configuration for layout engine"
    )


class LayoutGenerationResult(BaseModel):
    """Result of layout generation"""
    slide_id: str
    layout: MVPLayout
    theme: ThemeDefinition
    manifest: Optional[ContainerManifest] = Field(
        default=None,
        description="Optional manifest (not used in 2-agent workflow)"
    )
    generation_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metrics about the generation process"
    )
    success: bool
    error_message: Optional[str] = None


class LayoutArchitectOrchestrator:
    """
    Orchestrator for the two-agent Layout Architect system.
    
    Workflow:
    1. Theme Agent generates design tokens and templates from strawman metadata
    2. StructureLayout Agent performs atomic structure+layout generation with preserved context
    """
    
    def __init__(
        self,
        theme_model: str = "gemini-2.5-flash-lite-preview-06-17",
        structure_layout_model: str = "gemini-2.5-flash-lite-preview-06-17",
        use_legacy_workflow: bool = False
    ):
        """Initialize the orchestrator with two agents"""
        self.theme_agent = ThemeAgent(model_name=theme_model)
        self.structure_layout_agent = StructureLayoutAgent(model_name=structure_layout_model)
        self.use_legacy_workflow = use_legacy_workflow
        
        # Initialize legacy agents if requested and available
        if self.use_legacy_workflow and HAS_OLD_AGENTS:
            self.structure_agent = StructureAgent(model_name=structure_layout_model)
            self.layout_engine = LayoutEngineAgent(model_name=structure_layout_model)
            logger.info("Layout Architect Orchestrator initialized with legacy three-agent workflow")
        else:
            logger.info("Layout Architect Orchestrator initialized with new two-agent workflow")
    
    async def generate_layout(
        self,
        request: LayoutGenerationRequest
    ) -> LayoutGenerationResult:
        """
        Generate a complete layout for a slide.
        
        Uses either new 2-agent workflow (default) or legacy 3-agent workflow.
        """
        slide = request.slide
        metrics = {
            "slide_id": slide.slide_id,
            "slide_type": slide.slide_type,
            "structure_preference": getattr(slide, 'structure_preference', None),
            "workflow": "legacy" if self.use_legacy_workflow else "new"
        }
        
        try:
            logger.info(f"Starting layout generation for slide {slide.slide_id} using {'legacy' if self.use_legacy_workflow else 'new'} workflow")
            
            if self.use_legacy_workflow and HAS_OLD_AGENTS:
                return await self._generate_layout_legacy(request, metrics)
            else:
                return await self._generate_layout_new(request, metrics)
                
        except Exception as e:
            logger.error(f"Layout generation failed for slide {slide.slide_id}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            
            # Try to provide a basic fallback
            try:
                fallback_layout = self._create_emergency_fallback(slide)
                return LayoutGenerationResult(
                    slide_id=slide.slide_id,
                    layout=fallback_layout,
                    theme=self.theme_agent._get_default_theme(slide, "fallback"),
                    generation_metrics=metrics,
                    success=False,
                    error_message=str(e)
                )
            except:
                raise e

    async def _generate_layout_new(
        self,
        request: LayoutGenerationRequest,
        metrics: Dict[str, Any]
    ) -> LayoutGenerationResult:
        """New 2-agent workflow with preserved strawman context"""
        slide = request.slide
        
        # Step 1: Generate theme with full strawman context
        logger.info("Step 1: Generating theme with full context...")
        
        # Note: For individual slide generation, we don't have full strawman
        # But we can simulate strawman metadata for theme generation
        mock_strawman_data = {
            "main_title": slide.title or "Presentation",
            "overall_theme": request.presentation_context.get("overall_theme", "Professional presentation"),
            "design_suggestions": request.presentation_context.get("design_suggestions", "Clean and professional"),
            "target_audience": request.presentation_context.get("target_audience", "General audience")
        }
        
        theme = await self.theme_agent.generate_theme_legacy(
            slide_type=slide.slide_type,
            user_context=request.user_context,
            content_hints=mock_strawman_data
        )
        metrics["theme_name"] = theme.name
        logger.info(f"Theme generated: {theme.name}")
        
        # Step 2: Atomic structure+layout generation
        logger.info("Step 2: Generating structure and layout atomically...")
        layout = await self.structure_layout_agent.generate_structure_and_layout(
            slide=slide,
            theme=theme,
            session_id=metrics.get("session_id"),
            presentation_context=request.presentation_context,
            config=request.layout_config
        )
        
        metrics["layout_container_count"] = len(layout.containers)
        metrics["white_space_ratio"] = layout.white_space_ratio
        metrics["structure_preference_honored"] = getattr(slide, 'structure_preference', None) is not None
        logger.info(f"Atomic layout generated with {len(layout.containers)} containers")
        
        # Create successful result
        return LayoutGenerationResult(
            slide_id=slide.slide_id,
            layout=layout,
            theme=theme,
            manifest=None,  # Not used in 2-agent workflow
            generation_metrics=metrics,
            success=True
        )

    async def _generate_layout_legacy(
        self,
        request: LayoutGenerationRequest,
        metrics: Dict[str, Any]
    ) -> LayoutGenerationResult:
        """Legacy 3-agent workflow for fallback"""
        slide = request.slide
        
        # Step 1: Generate theme with Theme Agent
        logger.info("Step 1: Generating theme (legacy)...")
        theme = await self.theme_agent.generate_theme_legacy(
            slide_type=slide.slide_type,
            user_context=request.user_context,
            content_hints={
                "title": slide.title,
                "key_points": slide.key_points,
                "narrative": slide.narrative,
                "tone": request.presentation_context.get("tone") if request.presentation_context else None
            }
        )
        metrics["theme_name"] = theme.name
        logger.info(f"Theme generated: {theme.name}")
        
        # Step 2: Analyze structure with Structure Agent
        logger.info("Step 2: Analyzing content structure (legacy)...")
        manifest = await self.structure_agent.analyze_structure(
            slide=slide,
            theme_context={
                "name": theme.name,
                "style": getattr(theme, 'style_attributes', {})
            },
            presentation_context=request.presentation_context
        )
        metrics["container_count"] = len(manifest.containers)
        metrics["relationship_count"] = len(manifest.relationships)
        logger.info(f"Structure analyzed: {len(manifest.containers)} containers")
        
        # Step 3: Generate layout with Layout Engine
        logger.info("Step 3: Generating layout (legacy)...")
        layout = await self.layout_engine.generate_layout(
            theme=theme,
            manifest=manifest,
            config=request.layout_config
        )
        metrics["layout_container_count"] = len(layout.containers)
        metrics["white_space_ratio"] = layout.white_space_ratio
        logger.info(f"Layout generated with {len(layout.containers)} containers")
        
        # Analyze layout quality
        quality_analysis = await self.layout_engine.analyze_layout_quality(layout)
        metrics["balance_score"] = quality_analysis["balance_score"]
        metrics["is_valid"] = quality_analysis["is_valid"]
        
        # Create successful result
        return LayoutGenerationResult(
            slide_id=slide.slide_id,
            layout=layout,
            theme=theme,
            manifest=manifest,
            generation_metrics=metrics,
            success=True
        )
    
    async def generate_batch(
        self,
        slides: List[Slide],
        user_context: Optional[Dict[str, Any]] = None,
        presentation_context: Optional[Dict[str, Any]] = None,
        layout_config: Optional[LayoutEngineConfig] = None
    ) -> List[LayoutGenerationResult]:
        """Generate layouts for multiple slides"""
        results = []
        
        # Generate theme once for consistency
        if slides:
            logger.info(f"Generating batch layouts for {len(slides)} slides")
            
            # Use first slide to generate theme
            first_slide = slides[0]
            theme = await self.theme_agent.generate_theme_legacy(
                slide_type=first_slide.slide_type,
                user_context=user_context,
                content_hints={
                    "title": first_slide.title,
                    "presentation_context": presentation_context
                }
            )
            
            # Process each slide with the same theme
            for slide in slides:
                try:
                    # Analyze structure
                    manifest = await self.structure_agent.analyze_structure(
                        slide=slide,
                        theme_context={
                            "name": theme.name,
                            "style": theme.style_attributes
                        },
                        presentation_context=presentation_context
                    )
                    
                    # Generate layout
                    layout = await self.layout_engine.generate_layout(
                        theme=theme,
                        manifest=manifest,
                        config=layout_config
                    )
                    
                    # Create result
                    result = LayoutGenerationResult(
                        slide_id=slide.slide_id,
                        layout=layout,
                        theme=theme,
                        manifest=manifest,
                        generation_metrics={
                            "batch_mode": True,
                            "theme_reused": True
                        },
                        success=True
                    )
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Failed to generate layout for slide {slide.slide_id}: {e}")
                    # Add failed result
                    results.append(LayoutGenerationResult(
                        slide_id=slide.slide_id,
                        layout=self._create_emergency_fallback(slide),
                        theme=theme,
                        manifest=ContainerManifest(
                            slide_id=slide.slide_id,
                            slide_type=slide.slide_type,
                            containers=[],
                            relationships=[],
                            primary_message=slide.title or "Content",
                            content_flow="linear"
                        ),
                        generation_metrics={"batch_mode": True},
                        success=False,
                        error_message=str(e)
                    ))
        
        return results
    
    async def refine_layout(
        self,
        slide_id: str,
        current_layout: MVPLayout,
        feedback: Dict[str, Any],
        theme: Optional[ThemeDefinition] = None,
        manifest: Optional[ContainerManifest] = None
    ) -> LayoutGenerationResult:
        """Refine an existing layout based on feedback"""
        try:
            logger.info(f"Refining layout for slide {slide_id}")
            
            # Use Layout Engine's refinement capability
            refined_layout = await self.layout_engine.refine_layout(
                layout=current_layout,
                feedback=feedback
            )
            
            # Analyze quality
            quality_analysis = await self.layout_engine.analyze_layout_quality(refined_layout)
            
            return LayoutGenerationResult(
                slide_id=slide_id,
                layout=refined_layout,
                theme=theme or ThemeDefinition(name="refined", style_attributes={}),
                manifest=manifest or ContainerManifest(
                    slide_id=slide_id,
                    slide_type="generic",
                    containers=[],
                    relationships=[],
                    primary_message="Refined content",
                    content_flow="linear"
                ),
                generation_metrics={
                    "refinement": True,
                    "balance_score": quality_analysis["balance_score"],
                    "is_valid": quality_analysis["is_valid"]
                },
                success=True
            )
            
        except Exception as e:
            logger.error(f"Layout refinement failed: {e}")
            return LayoutGenerationResult(
                slide_id=slide_id,
                layout=current_layout,
                theme=theme or ThemeDefinition(name="unchanged", style_attributes={}),
                manifest=manifest or ContainerManifest(
                    slide_id=slide_id,
                    slide_type="generic",
                    containers=[],
                    relationships=[],
                    primary_message="Content",
                    content_flow="linear"
                ),
                generation_metrics={"refinement": False},
                success=False,
                error_message=str(e)
            )
    
    def _create_emergency_fallback(self, slide: Slide) -> MVPLayout:
        """Create an emergency fallback layout"""
        from .models import MVPContainer, GridPosition, ContainerContent
        
        containers = []
        
        # Add title
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
        
        # Add key points
        y_offset = 32
        for i, point in enumerate(slide.key_points or []):
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
                    text=point,
                    style="body"
                )
            ))
            y_offset += 20
        
        return MVPLayout(
            slide_id=slide.slide_id,
            slide_number=getattr(slide, 'slide_number', 1),
            slide_type=slide.slide_type,
            layout="verticalStack",  # Default fallback layout
            layout_spec=LayoutSpec(
                source="custom",
                layout_hints=LayoutHints(
                    content_density="medium",
                    visual_emphasis=0.5,
                    preferred_flow="vertical"
                )
            ),
            containers=containers,
            content_state=ContentState(
                base_content="complete",
                layout="error",
                research="not_applicable",
                visuals="not_applicable",
                charts="not_applicable"
            ),
            white_space_ratio=0.4,
            alignment_score=0.8,  # Reasonable fallback score
            slide_title=slide.title,
            strawman_structure_preference=getattr(slide, 'structure_preference', None)
        )
    
    async def get_theme_options(
        self,
        slide_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[ThemeDefinition]:
        """Get multiple theme options for a slide type"""
        # This could be extended to generate multiple theme variations
        theme = await self.theme_agent.generate_theme_legacy(
            slide_type=slide_type,
            user_context=user_context
        )
        
        # For now, return just the one theme
        return [theme]
    
    async def analyze_slide_complexity(self, slide: Slide) -> Dict[str, Any]:
        """Analyze the complexity of a slide to help with layout decisions"""
        # Quick analysis without full generation
        manifest = await self.structure_agent.analyze_structure(slide)
        
        return {
            "slide_id": slide.slide_id,
            "container_count": len(manifest.containers),
            "relationship_count": len(manifest.relationships),
            "content_density": manifest.content_density,
            "complexity_score": manifest.complexity_score,
            "content_flow": manifest.content_flow.value,
            "has_visuals": any(c.requires_visual for c in manifest.containers),
            "hierarchy_depth": max(c.hierarchy_level for c in manifest.containers) if manifest.containers else 1
        }
    
    async def process_strawman(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a presentation strawman to generate theme and layouts.
        
        This adapter method allows the new three-agent system to work
        with the existing DirectorPhase2Extension interface.
        
        Args:
            strawman: The approved presentation strawman
            session_id: Current session ID
            user_context: Optional user/brand context
            
        Returns:
            Dictionary with theme and layouts
        """
        try:
            logger.info(f"Processing strawman for session {session_id}")
            
            # Extract presentation context from strawman (full metadata)
            presentation_context = {
                "main_title": strawman.main_title,
                "overall_theme": strawman.overall_theme,
                "design_suggestions": strawman.design_suggestions,
                "target_audience": strawman.target_audience,
                "title": getattr(strawman, 'title', strawman.main_title),
                "summary": getattr(strawman, 'summary', ''),
                "presentation_style": getattr(strawman, 'presentation_style', ''),
                "duration_minutes": strawman.presentation_duration,
                "session_id": session_id
            }
            
            # Merge with user context
            if user_context:
                presentation_context.update(user_context)
            
            # Generate theme first (once for entire presentation)
            logger.info("Generating theme for presentation...")
            try:
                theme = await self.theme_agent.generate_theme(
                    strawman=strawman,
                    session_id=session_id,
                    brand_guidelines=user_context
                )
                logger.info(f"Theme generated successfully: {theme.name}")
            except Exception as theme_error:
                logger.error(f"Theme generation failed: {theme_error}")
                logger.error(f"Error type: {type(theme_error).__name__}")
                raise
            
            # Process each slide
            layouts = []
            for i, slide in enumerate(strawman.slides):
                logger.info(f"Processing slide {i+1}/{len(strawman.slides)}: {slide.slide_id}")
                
                try:
                    # Create layout generation request
                    request = LayoutGenerationRequest(
                        slide=slide,
                        user_context=user_context,
                        presentation_context=presentation_context
                    )
                    
                    # Generate layout using the theme
                    result = await self.generate_layout(request)
                    
                    if result.success:
                        layouts.append(result.layout)
                        logger.info(f"Layout generated successfully for slide {slide.slide_id}")
                    else:
                        logger.error(f"Failed to generate layout for slide {slide.slide_id}: {result.error_message}")
                        # Add fallback layout
                        layouts.append(self._create_emergency_fallback(slide))
                except Exception as slide_error:
                    logger.error(f"Exception while processing slide {slide.slide_id}: {slide_error}")
                    # Add fallback layout
                    layouts.append(self._create_emergency_fallback(slide))
            
            # Return in format expected by DirectorPhase2Extension
            return {
                "theme": theme,
                "layouts": layouts,
                "metadata": {
                    "total_slides": len(strawman.slides),
                    "successful_layouts": sum(1 for r in layouts if hasattr(r, 'white_space_ratio')),
                    "theme_name": theme.name,
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing strawman: {e}")
            # Return minimal valid response with proper fallback theme
            try:
                # Try to get default theme from theme agent
                fallback_theme = self.theme_agent._get_default_theme(strawman, session_id)
            except:
                # If that fails too, create minimal valid theme
                fallback_theme = self._create_minimal_theme()
            
            return {
                "theme": fallback_theme,
                "layouts": [self._create_emergency_fallback(slide) for slide in strawman.slides],
                "metadata": {
                    "error": str(e),
                    "session_id": session_id
                }
            }
    
    def _create_minimal_theme(self) -> ThemeDefinition:
        """Create a minimal valid theme as last resort fallback."""
        # Create minimal design tokens
        colors = {
            "primary": ColorToken(value="#0066cc", type=TokenType.COLOR),
            "secondary": ColorToken(value="#4d94ff", type=TokenType.COLOR),
            "background": ColorToken(value="#ffffff", type=TokenType.COLOR),
            "text": ColorToken(value="#000000", type=TokenType.COLOR)
        }
        
        typography = {
            "heading": TypographyToken(
                fontFamily=TokenValue(value="Arial", type=TokenType.FONT_FAMILY),
                fontSize=TokenValue(value=32, type=TokenType.FONT_SIZE)
            ),
            "body": TypographyToken(
                fontFamily=TokenValue(value="Arial", type=TokenType.FONT_FAMILY),
                fontSize=TokenValue(value=16, type=TokenType.FONT_SIZE)
            )
        }
        
        spacing = {
            "sm": DimensionToken(value=8, type=TokenType.DIMENSION),
            "md": DimensionToken(value=16, type=TokenType.DIMENSION),
            "lg": DimensionToken(value=24, type=TokenType.DIMENSION)
        }
        
        sizing = {
            "container": DimensionToken(value=1024, type=TokenType.DIMENSION)
        }
        
        design_tokens = DesignTokens(
            name="Minimal Fallback",
            description="Emergency fallback theme",
            colors=colors,
            typography=typography,
            spacing=spacing,
            sizing=sizing
        )
        
        # Create minimal layout templates
        layout_templates = {
            "titleSlide": LayoutTemplate(
                name="titleSlide",
                zones={
                    "title": GridZone(
                        name="title",
                        leftInset=20,
                        topInset=35,
                        width=120,
                        height=20
                    )
                }
            ),
            "contentSlide": LayoutTemplate(
                name="contentSlide",
                zones={
                    "title": GridZone(
                        name="title",
                        leftInset=8,
                        topInset=8,
                        width=144,
                        height=12
                    ),
                    "content": GridZone(
                        name="content",
                        leftInset=8,
                        topInset=24,
                        width=144,
                        height=58
                    )
                }
            )
        }
        
        return ThemeDefinition(
            name="Minimal Fallback",
            design_tokens=design_tokens,
            layout_templates=layout_templates,
            metadata={"emergency_fallback": True}
        )