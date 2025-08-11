"""
Orchestrator for Phase 2B Content-Driven Layout Architecture with Streaming Support.

This orchestrator coordinates Theme Agent and Content Agent with streaming capabilities,
sending results as soon as they're ready rather than waiting for all processing to complete.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable, AsyncIterator
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


class StreamingCallbacks:
    """Callbacks for streaming updates"""
    def __init__(
        self,
        on_theme_ready: Optional[Callable[[ThemeDefinition], None]] = None,
        on_slide_ready: Optional[Callable[[MVPLayout, ContentManifest], None]] = None,
        on_status_update: Optional[Callable[[str, int], None]] = None
    ):
        self.on_theme_ready = on_theme_ready
        self.on_slide_ready = on_slide_ready
        self.on_status_update = on_status_update


class LayoutArchitectOrchestratorPhase2BStreaming:
    """
    Streaming Orchestrator for Phase 2B Content-Driven Architecture.
    
    Workflow:
    1. Theme Agent starts generating theme
    2. Content Agent processes slides individually
    3. As soon as theme is ready, it's sent via callback
    4. As each slide's content is ready, it's sent to Layout Architect
    5. As each layout is generated, it's sent via callback
    
    This provides real-time updates and better perceived performance.
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
        
        logger.info("Phase 2B Streaming Orchestrator initialized")
        logger.info(f"  - Theme Agent: {theme_model}")
        logger.info(f"  - Content Agent: {content_model}")
        logger.info(f"  - Layout Architect: {layout_model}")
    
    async def process_strawman_streaming(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        callbacks: StreamingCallbacks,
        user_context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process a presentation strawman with streaming updates.
        
        Yields updates as they become available:
        - Theme update when theme is ready
        - Slide updates as each slide is processed
        """
        try:
            logger.info(f"Starting streaming processing for session {session_id}")
            
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
            
            # Start theme generation (async)
            logger.info("Starting theme generation...")
            theme_task = asyncio.create_task(
                self._generate_theme_with_callback(
                    strawman, user_context, session_id, callbacks
                )
            )
            
            # Start processing slides while theme generates
            logger.info(f"Starting slide processing for {len(strawman.slides)} slides...")
            slide_tasks = []
            
            # Create a shared theme future that all slides can wait on
            theme_future = asyncio.Future()
            
            # Process each slide
            for i, slide in enumerate(strawman.slides):
                slide_task = asyncio.create_task(
                    self._process_single_slide(
                        slide=slide,
                        slide_index=i,
                        total_slides=len(strawman.slides),
                        strawman_metadata=strawman_metadata,
                        presentation_context=presentation_context,
                        theme_future=theme_future,
                        callbacks=callbacks,
                        session_id=session_id
                    )
                )
                slide_tasks.append(slide_task)
            
            # Wait for theme and set it in the future for slides to use
            theme = await theme_task
            theme_future.set_result(theme)
            
            # Yield theme update
            yield {
                "type": "theme_ready",
                "theme": theme,
                "session_id": session_id
            }
            
            # Wait for all slides to complete and yield their results
            slide_results = await asyncio.gather(*slide_tasks, return_exceptions=True)
            
            # Process results
            successful_count = 0
            for i, result in enumerate(slide_results):
                if isinstance(result, Exception):
                    logger.error(f"Slide {i+1} processing failed: {result}")
                    yield {
                        "type": "slide_error",
                        "slide_index": i,
                        "error": str(result),
                        "session_id": session_id
                    }
                else:
                    successful_count += 1
                    yield result
            
            # Final status
            yield {
                "type": "complete",
                "session_id": session_id,
                "total_slides": len(strawman.slides),
                "successful_slides": successful_count
            }
            
        except Exception as e:
            logger.error(f"Streaming processing failed: {e}")
            yield {
                "type": "error",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _generate_theme_with_callback(
        self,
        strawman: PresentationStrawman,
        user_context: Optional[Dict[str, Any]],
        session_id: str,
        callbacks: StreamingCallbacks
    ) -> ThemeDefinition:
        """Generate theme and trigger callback when ready"""
        theme = await self.theme_agent.generate_theme(
            strawman=strawman,
            session_id=session_id,
            brand_guidelines=user_context
        )
        
        logger.info(f"Theme generated: {theme.name}")
        
        # Trigger callback if provided
        if callbacks.on_theme_ready:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, callbacks.on_theme_ready, theme
                )
            except Exception as e:
                logger.error(f"Theme callback failed: {e}")
        
        return theme
    
    async def _process_single_slide(
        self,
        slide: Slide,
        slide_index: int,
        total_slides: int,
        strawman_metadata: Dict[str, Any],
        presentation_context: Dict[str, Any],
        theme_future: asyncio.Future,
        callbacks: StreamingCallbacks,
        session_id: str
    ) -> Dict[str, Any]:
        """Process a single slide: content preparation -> layout generation"""
        try:
            logger.info(f"Processing slide {slide_index+1}/{total_slides}: {slide.slide_id}")
            
            # Update status
            if callbacks.on_status_update:
                progress = int((slide_index / total_slides) * 50)  # 0-50% for content
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, callbacks.on_status_update, 
                        f"Preparing content for slide {slide_index+1}", 
                        progress
                    )
                except Exception as e:
                    logger.error(f"Status callback failed: {e}")
            
            # Prepare content for this slide
            content_manifest = await self.content_agent.prepare_content(
                slide=slide,
                strawman_metadata=strawman_metadata,
                theme=None,  # Theme not needed for content preparation
                session_id=session_id
            )
            
            logger.info(f"Content prepared for slide {slide.slide_id}: {content_manifest.total_word_count} words")
            
            # Wait for theme to be ready
            theme = await theme_future
            
            # Update status
            if callbacks.on_status_update:
                progress = int(50 + (slide_index / total_slides) * 50)  # 50-100% for layout
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, callbacks.on_status_update,
                        f"Generating layout for slide {slide_index+1}",
                        progress
                    )
                except Exception as e:
                    logger.error(f"Status callback failed: {e}")
            
            # Generate layout with prepared content
            layout = await self.layout_architect.generate_layout(
                slide=slide,
                theme=theme,
                content_manifest=content_manifest,
                presentation_context=presentation_context
            )
            
            logger.info(f"Layout generated for slide {slide.slide_id} with {len(layout.containers)} containers")
            
            # Trigger callback if provided
            if callbacks.on_slide_ready:
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, callbacks.on_slide_ready, layout, content_manifest
                    )
                except Exception as e:
                    logger.error(f"Slide callback failed: {e}")
            
            return {
                "type": "slide_ready",
                "slide_id": slide.slide_id,
                "slide_index": slide_index,
                "layout": layout,
                "content_manifest": content_manifest,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to process slide {slide.slide_id}: {e}")
            raise
    
    async def process_strawman(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a presentation strawman (backward compatibility).
        
        This method provides the same interface as the non-streaming version
        but collects all results before returning.
        """
        layouts = []
        theme = None
        errors = []
        
        # Create simple callbacks to collect results
        def on_theme_ready(t: ThemeDefinition):
            nonlocal theme
            theme = t
        
        def on_slide_ready(layout: MVPLayout, content: ContentManifest):
            layouts.append(layout)
        
        callbacks = StreamingCallbacks(
            on_theme_ready=on_theme_ready,
            on_slide_ready=on_slide_ready
        )
        
        # Process with streaming but collect all results
        async for update in self.process_strawman_streaming(
            strawman, session_id, callbacks, user_context
        ):
            if update["type"] == "error" or update["type"] == "slide_error":
                errors.append(update.get("error", "Unknown error"))
        
        # Return in expected format
        return {
            "theme": theme or self._create_minimal_theme(),
            "layouts": layouts,
            "metadata": {
                "total_slides": len(strawman.slides),
                "successful_layouts": len(layouts),
                "theme_name": theme.name if theme else "fallback",
                "session_id": session_id,
                "architecture": "phase2b_streaming",
                "errors": errors if errors else None
            }
        }
    
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