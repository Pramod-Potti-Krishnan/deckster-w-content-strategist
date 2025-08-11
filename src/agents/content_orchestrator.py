"""
Content Orchestrator - Coordinates Theme, Content, and Image generation.

This orchestrator replaces the layout orchestrator and provides a simpler
pipeline focused on content generation without layout calculations.

Flow:
1. Generate theme using Theme Agent
2. For each slide:
   - Generate content with ContentAgentV7
   - Generate images with ImageBuildAgent
3. Assemble final content package
"""

import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime

from src.models.agents import PresentationStrawman, Slide
from src.models.design_tokens import ThemeDefinition
from src.agents.theme_agent import SimplifiedThemeAgent
from src.agents.content_agent_v7 import ContentAgentV7, ContentManifest
from src.agents.image_build_agent import generate_image
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentGenerationResult:
    """Result of content generation for a single slide."""
    def __init__(
        self,
        slide_id: str,
        content_manifest: ContentManifest,
        generated_images: Optional[Dict[str, str]] = None
    ):
        self.slide_id = slide_id
        self.content_manifest = content_manifest
        self.generated_images = generated_images or {}


class ContentOrchestrator:
    """
    Orchestrates content generation without layout concerns.
    
    Coordinates:
    - Theme generation
    - Content generation per slide
    - Image generation for visual specs
    - Final assembly
    """
    
    def __init__(
        self,
        theme_model: str = "gemini-2.5-flash",
        content_model: str = "gemini-2.5-pro",
        use_tool_free_theme: bool = True
    ):
        """
        Initialize the content orchestrator.
        
        Args:
            theme_model: Model to use for theme generation
            content_model: Model to use for content generation
            use_tool_free_theme: Whether to use the tool-free theme agent
        """
        # Initialize agents
        if use_tool_free_theme:
            from src.agents.theme_agent import ToolFreeThemeAgent
            self.theme_agent = ToolFreeThemeAgent(model_name=theme_model)
        else:
            self.theme_agent = SimplifiedThemeAgent(model_name=theme_model)
            
        self.content_agent = ContentAgentV7()
        
        logger.info("ContentOrchestrator initialized")
        logger.info(f"  - Theme Agent: {theme_model} (tool_free={use_tool_free_theme})")
        logger.info(f"  - Content Agent: {content_model}")
        logger.info("  - Image Build Agent: Ready (using generate_image function)")
    
    async def generate_content(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        director_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        generate_images: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate complete content package for a presentation.
        
        Args:
            strawman: The approved presentation strawman
            session_id: Session identifier
            director_metadata: Metadata from director (formality, complexity)
            user_context: User preferences and brand guidelines
            generate_images: Whether to generate actual images
            
        Returns:
            Dictionary containing theme, content manifests, and generated images
        """
        try:
            logger.info(f"Starting content generation for session {session_id}")
            logger.info(f"  - Slides: {len(strawman.slides)}")
            logger.info(f"  - Generate images: {generate_images}")
            
            # Step 1: Generate theme
            logger.info("Step 1: Generating theme...")
            theme = await self._generate_theme(
                strawman, session_id, director_metadata, user_context
            )
            logger.info(f"Theme generated: {theme.name}")
            
            # Step 2: Generate content for each slide
            logger.info("Step 2: Generating content for slides...")
            content_results = []
            completed_slides = []
            
            for i, slide in enumerate(strawman.slides):
                logger.info(f"Processing slide {i+1}/{len(strawman.slides)}: {slide.slide_id}")
                
                # Generate content
                content_manifest = await self._generate_slide_content(
                    slide, theme, strawman, completed_slides
                )
                
                # Call progress callback if provided
                if progress_callback:
                    await progress_callback({
                        'type': 'slide_content_ready',
                        'slide_index': i,
                        'slide_id': slide.slide_id,
                        'slide_title': slide.title,
                        'content_manifest': content_manifest,
                        'total_slides': len(strawman.slides)
                    })
                
                # Generate images if requested
                generated_images = {}
                if generate_images and content_manifest.primary_visual:
                    logger.info(f"  - Generating image for slide {slide.slide_id}")
                    try:
                        image_result = await generate_image(
                            content_manifest.primary_visual
                        )
                        if image_result.get('success'):
                            # For now, store base64 - later this should upload to storage
                            generated_images['primary'] = image_result.get('image_base64', '')
                    except Exception as e:
                        logger.error(f"Image generation failed for slide {slide.slide_id}: {e}")
                
                # Store result
                result = ContentGenerationResult(
                    slide_id=slide.slide_id,
                    content_manifest=content_manifest,
                    generated_images=generated_images
                )
                content_results.append(result)
                completed_slides.append(content_manifest)
            
            # Step 3: Assemble final package
            logger.info("Step 3: Assembling final content package...")
            final_package = self._assemble_final_package(
                theme, content_results, strawman
            )
            
            logger.info(f"Content generation complete for session {session_id}")
            return final_package
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise
    
    async def generate_content_streaming(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        director_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        generate_images: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate content with streaming updates.
        
        Yields updates as they become available:
        - Theme generation complete
        - Each slide content complete
        - Each image generation complete
        - Final assembly complete
        """
        try:
            # Generate theme
            logger.info("Generating theme...")
            theme = await self._generate_theme(
                strawman, session_id, director_metadata, user_context
            )
            
            yield {
                "type": "theme_ready",
                "theme": theme,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate content for each slide
            completed_slides = []
            
            for i, slide in enumerate(strawman.slides):
                # Generate content
                content_manifest = await self._generate_slide_content(
                    slide, theme, strawman, completed_slides
                )
                
                yield {
                    "type": "content_ready",
                    "slide_id": slide.slide_id,
                    "slide_index": i,
                    "content_manifest": content_manifest,
                    "session_id": session_id,
                    "progress": int((i + 1) / len(strawman.slides) * 50)  # 0-50% for content
                }
                
                # Generate image if needed
                if generate_images and content_manifest.primary_visual:
                    try:
                        image_result = await generate_image(
                            content_manifest.primary_visual
                        )
                        if image_result.get('success'):
                            yield {
                                "type": "image_ready",
                                "slide_id": slide.slide_id,
                                "image_url": image_result.get('url', ''),  # Future: actual URL
                                "session_id": session_id
                            }
                    except Exception as e:
                        logger.error(f"Image generation failed: {e}")
                        yield {
                            "type": "image_error",
                            "slide_id": slide.slide_id,
                            "error": str(e),
                            "session_id": session_id
                        }
                
                completed_slides.append(content_manifest)
            
            # Final completion
            yield {
                "type": "complete",
                "session_id": session_id,
                "total_slides": len(strawman.slides),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Streaming content generation failed: {e}")
            yield {
                "type": "error",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_theme(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        director_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ThemeDefinition:
        """Generate theme for the presentation."""
        brand_guidelines = user_context.get('brand', {}) if user_context else None
        
        theme = await self.theme_agent.generate_theme(
            strawman=strawman,
            session_id=session_id,
            director_metadata=director_metadata,
            brand_guidelines=brand_guidelines
        )
        
        return theme
    
    async def _generate_slide_content(
        self,
        slide: Slide,
        theme: ThemeDefinition,
        strawman: PresentationStrawman,
        completed_slides: List[ContentManifest]
    ) -> ContentManifest:
        """Generate content for a single slide."""
        content_manifest = await self.content_agent.run(
            slide=slide,
            theme=theme,
            strawman=strawman,
            completed_slides=completed_slides,
            return_raw=False
        )
        
        return content_manifest
    
    def _assemble_final_package(
        self,
        theme: ThemeDefinition,
        content_results: List[ContentGenerationResult],
        strawman: PresentationStrawman
    ) -> Dict[str, Any]:
        """Assemble the final content package."""
        return {
            "theme": theme.dict() if hasattr(theme, 'dict') else theme,
            "content": [
                {
                    "slide_id": result.slide_id,
                    "content_manifest": result.content_manifest.dict(),
                    "generated_images": result.generated_images
                }
                for result in content_results
            ],
            "metadata": {
                "total_slides": len(strawman.slides),
                "main_title": strawman.main_title,
                "target_audience": strawman.target_audience,
                "presentation_duration": strawman.presentation_duration,
                "generated_at": datetime.utcnow().isoformat()
            }
        }