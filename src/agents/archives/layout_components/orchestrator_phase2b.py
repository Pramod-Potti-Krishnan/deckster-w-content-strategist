"""
Orchestrator for Phase 2B Content-Driven Layout Architecture.

This orchestrator coordinates Theme Agent and Content Agent in parallel,
then feeds prepared content to Layout Architect for content-aware layout generation.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

from src.models.agents import Slide, PresentationStrawman
from src.utils.logger import setup_logger
from src.models.design_tokens import (
    ThemeDefinition, DesignTokens, ColorToken, TypographyToken, 
    DimensionToken, TokenValue, TokenType, LayoutTemplate, GridZone
)
from .model_types.layout_state import LayoutEngineConfig
from .models import MVPLayout, LayoutSpec, LayoutHints, ContentState
from .agents.theme_agent import ThemeAgent
from .agents.content_agent import ContentAgentV5 as ContentAgent, ContentManifest
from .agents.layout_architect_agent import LayoutArchitectAgent

logger = setup_logger(__name__)


class Phase2BGenerationRequest(BaseModel):
    """Request for Phase 2B layout generation"""
    slide: Slide
    strawman_metadata: Dict[str, Any] = Field(
        description="Main title, overall theme, design suggestions, target audience"
    )
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


class Phase2BGenerationResult(BaseModel):
    """Result of Phase 2B layout generation"""
    slide_id: str
    layout: MVPLayout
    theme: ThemeDefinition
    content_manifest: ContentManifest
    generation_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metrics about the generation process"
    )
    success: bool
    error_message: Optional[str] = None


class LayoutArchitectOrchestratorPhase2B:
    """
    Orchestrator for Phase 2B Content-Driven Architecture.
    
    Workflow:
    1. Theme Agent and Content Agent run in PARALLEL
    2. Layout Architect receives both outputs to generate content-aware layouts
    
    This eliminates guesswork by providing actual content to the layout system.
    """
    
    def __init__(
        self,
        theme_model: str = "gemini-2.5-flash-lite-preview-06-17",
        content_model: str = "gemini-2.5-flash-lite-preview-06-17",
        layout_model: str = "gemini-2.5-flash-lite-preview-06-17"
    ):
        """Initialize the orchestrator with three agents"""
        self.theme_agent = ThemeAgent(model_name=theme_model)
        self.content_agent = ContentAgent()
        self.layout_architect = LayoutArchitectAgent(model_name=layout_model)
        
        logger.info("Phase 2B Orchestrator initialized with content-driven architecture")
        logger.info(f"  - Theme Agent: {theme_model}")
        logger.info(f"  - Content Agent: {content_model}")
        logger.info(f"  - Layout Architect: {layout_model}")
    
    async def generate_layout(
        self,
        request: Phase2BGenerationRequest
    ) -> Phase2BGenerationResult:
        """
        Generate a complete layout using Phase 2B architecture.
        
        Theme and Content agents run in parallel, then Layout Architect
        uses both outputs to create content-aware layouts.
        """
        slide = request.slide
        metrics = {
            "slide_id": slide.slide_id,
            "slide_type": slide.slide_type,
            "structure_preference": getattr(slide, 'structure_preference', None),
            "workflow": "phase2b_content_driven"
        }
        
        try:
            logger.info(f"Starting Phase 2B generation for slide {slide.slide_id}")
            logger.info(f"  - Slide type: {slide.slide_type}")
            logger.info(f"  - Structure preference: {getattr(slide, 'structure_preference', 'None')}")
            logger.info(f"  - Target audience: {request.strawman_metadata.get('target_audience', 'general_public')}")
            
            # Step 1: Run Theme and Content agents in PARALLEL
            logger.info("Step 1: Running Theme and Content agents in parallel...")
            
            theme_task = asyncio.create_task(
                self._generate_theme(slide, request)
            )
            content_task = asyncio.create_task(
                self._prepare_content(slide, request)
            )
            
            # Wait for both to complete
            theme, content_manifest = await asyncio.gather(theme_task, content_task)
            
            metrics["theme_name"] = theme.name
            metrics["content_word_count"] = content_manifest.total_word_count
            metrics["content_density"] = content_manifest.content_density
            logger.info(f"Parallel generation complete:")
            logger.info(f"  - Theme: {theme.name}")
            logger.info(f"  - Content: {content_manifest.total_word_count} words")
            
            # Step 2: Generate layout with prepared content
            logger.info("Step 2: Generating content-aware layout...")
            layout = await self.layout_architect.generate_layout(
                slide=slide,
                theme=theme,
                content_manifest=content_manifest,
                presentation_context=request.presentation_context,
                config=request.layout_config
            )
            
            metrics["layout_container_count"] = len(layout.containers)
            metrics["white_space_ratio"] = layout.white_space_ratio
            metrics["structure_preference_honored"] = layout.strawman_structure_preference == getattr(slide, 'structure_preference', None)
            logger.info(f"Layout generated with {len(layout.containers)} containers")
            logger.info(f"Structure preference honored: {metrics['structure_preference_honored']}")
            
            # Create successful result
            return Phase2BGenerationResult(
                slide_id=slide.slide_id,
                layout=layout,
                theme=theme,
                content_manifest=content_manifest,
                generation_metrics=metrics,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Phase 2B generation failed for slide {slide.slide_id}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            
            # Try to provide a basic fallback
            try:
                fallback_layout = self._create_emergency_fallback(slide)
                fallback_theme = self.theme_agent._get_default_theme(slide, "fallback")
                fallback_content = self.content_agent._create_fallback_manifest(
                    slide, 
                    request.strawman_metadata
                )
                
                return Phase2BGenerationResult(
                    slide_id=slide.slide_id,
                    layout=fallback_layout,
                    theme=fallback_theme,
                    content_manifest=fallback_content,
                    generation_metrics=metrics,
                    success=False,
                    error_message=str(e)
                )
            except:
                raise e
    
    async def _generate_theme(
        self, 
        slide: Slide, 
        request: Phase2BGenerationRequest
    ) -> ThemeDefinition:
        """Generate theme with full strawman context"""
        logger.info("Generating theme with strawman metadata...")
        
        # For backward compatibility with existing theme agent
        mock_strawman = type('MockStrawman', (), {
            'main_title': request.strawman_metadata.get('main_title', 'Presentation'),
            'overall_theme': request.strawman_metadata.get('overall_theme', 'Professional'),
            'design_suggestions': request.strawman_metadata.get('design_suggestions', 'Clean and modern'),
            'target_audience': request.strawman_metadata.get('target_audience', 'general_public'),
            'slides': [slide]
        })()
        
        theme = await self.theme_agent.generate_theme(
            strawman=mock_strawman,
            session_id=request.presentation_context.get('session_id') if request.presentation_context else None,
            brand_guidelines=request.user_context
        )
        
        return theme
    
    async def _prepare_content(
        self,
        slide: Slide,
        request: Phase2BGenerationRequest
    ) -> ContentManifest:
        """Prepare content with word count enforcement"""
        logger.info("Preparing content with word count limits...")
        
        content_manifest = await self.content_agent.prepare_content(
            slide=slide,
            strawman_metadata=request.strawman_metadata,
            theme=None,  # Theme generated in parallel
            session_id=request.presentation_context.get('session_id') if request.presentation_context else None
        )
        
        return content_manifest
    
    async def generate_batch(
        self,
        slides: List[Slide],
        strawman_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        presentation_context: Optional[Dict[str, Any]] = None,
        layout_config: Optional[LayoutEngineConfig] = None
    ) -> List[Phase2BGenerationResult]:
        """Generate layouts for multiple slides with shared theme"""
        results = []
        
        if not slides:
            return results
        
        logger.info(f"Generating batch layouts for {len(slides)} slides")
        
        # Generate theme once for entire presentation
        logger.info("Generating shared theme for presentation...")
        mock_strawman = type('MockStrawman', (), {
            'main_title': strawman_metadata.get('main_title', 'Presentation'),
            'overall_theme': strawman_metadata.get('overall_theme', 'Professional'),
            'design_suggestions': strawman_metadata.get('design_suggestions', 'Clean and modern'),
            'target_audience': strawman_metadata.get('target_audience', 'general_public'),
            'slides': slides
        })()
        
        shared_theme = await self.theme_agent.generate_theme(
            strawman=mock_strawman,
            session_id=presentation_context.get('session_id') if presentation_context else None,
            brand_guidelines=user_context
        )
        
        logger.info(f"Shared theme generated: {shared_theme.name}")
        
        # Process each slide with parallel content preparation
        for i, slide in enumerate(slides):
            logger.info(f"Processing slide {i+1}/{len(slides)}: {slide.slide_id}")
            
            try:
                # Prepare content for this slide
                content_manifest = await self.content_agent.prepare_content(
                    slide=slide,
                    strawman_metadata=strawman_metadata,
                    theme=shared_theme,
                    session_id=presentation_context.get('session_id') if presentation_context else None
                )
                
                # Generate layout with prepared content
                layout = await self.layout_architect.generate_layout(
                    slide=slide,
                    theme=shared_theme,
                    content_manifest=content_manifest,
                    presentation_context=presentation_context,
                    config=layout_config
                )
                
                # Create result
                result = Phase2BGenerationResult(
                    slide_id=slide.slide_id,
                    layout=layout,
                    theme=shared_theme,
                    content_manifest=content_manifest,
                    generation_metrics={
                        "batch_mode": True,
                        "theme_reused": True,
                        "slide_index": i,
                        "total_slides": len(slides)
                    },
                    success=True
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to generate layout for slide {slide.slide_id}: {e}")
                # Add failed result with fallback
                results.append(Phase2BGenerationResult(
                    slide_id=slide.slide_id,
                    layout=self._create_emergency_fallback(slide),
                    theme=shared_theme,
                    content_manifest=self.content_agent._create_fallback_manifest(
                        slide,
                        strawman_metadata
                    ),
                    generation_metrics={"batch_mode": True, "error": True},
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    async def process_strawman(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a presentation strawman using Phase 2B architecture.
        
        This adapter method allows Phase 2B to work with existing Director interface.
        """
        try:
            logger.info(f"Processing strawman with Phase 2B for session {session_id}")
            
            # Extract strawman metadata
            strawman_metadata = {
                "main_title": strawman.main_title,
                "overall_theme": strawman.overall_theme,
                "design_suggestions": strawman.design_suggestions,
                "target_audience": strawman.target_audience
            }
            
            # Extract presentation context
            presentation_context = {
                "session_id": session_id,
                "title": getattr(strawman, 'title', strawman.main_title),
                "summary": getattr(strawman, 'summary', ''),
                "presentation_style": getattr(strawman, 'presentation_style', ''),
                "duration_minutes": strawman.presentation_duration
            }
            
            # Generate layouts for all slides
            results = await self.generate_batch(
                slides=strawman.slides,
                strawman_metadata=strawman_metadata,
                user_context=user_context,
                presentation_context=presentation_context
            )
            
            # Extract layouts from results
            layouts = [result.layout for result in results]
            
            # Use theme from first result (all share same theme)
            theme = results[0].theme if results else self._create_minimal_theme()
            
            # Return in format expected by Director
            return {
                "theme": theme,
                "layouts": layouts,
                "metadata": {
                    "total_slides": len(strawman.slides),
                    "successful_layouts": sum(1 for r in results if r.success),
                    "theme_name": theme.name,
                    "session_id": session_id,
                    "architecture": "phase2b_content_driven"
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing strawman with Phase 2B: {e}")
            # Return minimal valid response
            fallback_theme = self._create_minimal_theme()
            return {
                "theme": fallback_theme,
                "layouts": [self._create_emergency_fallback(slide) for slide in strawman.slides],
                "metadata": {
                    "error": str(e),
                    "session_id": session_id,
                    "architecture": "phase2b_fallback"
                }
            }
    
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
            layout="verticalStack",
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
            alignment_score=0.8,
            slide_title=slide.title,
            strawman_structure_preference=getattr(slide, 'structure_preference', None)
        )
    
    def _create_minimal_theme(self) -> ThemeDefinition:
        """Create a minimal valid theme as last resort fallback"""
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