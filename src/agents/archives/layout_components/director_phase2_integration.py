"""
Director Phase 2 Integration for Layout Architect.

This module extends the Director agent to handle the LAYOUT_GENERATION state.
"""

import asyncio
from typing import Dict, Any, Optional
from src.utils.logger import setup_logger
from src.agents.layout_architect import LayoutArchitectOrchestrator
from src.agents.layout_architect.orchestrator_phase2b import LayoutArchitectOrchestratorPhase2B
from src.agents.layout_architect.orchestrator_phase2b_streaming import (
    LayoutArchitectOrchestratorPhase2BStreaming, StreamingCallbacks
)
from src.models.agents import PresentationStrawman
from src.agents.layout_architect.models import LayoutConfig
from src.agents.director_out import DirectorOUT
from src.utils.session_manager import SessionManager

logger = setup_logger(__name__)


class DirectorPhase2Extension:
    """Extension to handle Layout Architect integration."""
    
    def __init__(self, session_manager: SessionManager, websocket_handler=None):
        """Initialize Phase 2 extension."""
        self.session_manager = session_manager
        self.websocket_handler = websocket_handler
        logger.info(f"[DEBUG DirectorPhase2Extension] Initialized with websocket_handler: {websocket_handler is not None}")
        
        # Initialize Layout Architect Orchestrator with three agents
        # Use settings for model configuration
        from config.settings import get_settings
        settings = get_settings()
        
        # Check if Phase 2B is enabled (default to Phase 2B for better results)
        use_phase2b = getattr(settings, 'USE_PHASE_2B_ARCHITECTURE', True)
        logger.warning(f"[DEBUG] USE_PHASE_2B_ARCHITECTURE setting: {use_phase2b}")
        
        if use_phase2b:
            # Use streaming version if we have websocket handler (DirectorOUT support)
            if websocket_handler is not None:
                logger.info("Using Phase 2B Content-Driven Architecture with STREAMING")
                self.layout_architect = LayoutArchitectOrchestratorPhase2BStreaming(
                    theme_model=settings.THEME_AGENT_MODEL,
                    content_model=getattr(settings, 'CONTENT_AGENT_MODEL', settings.THEME_AGENT_MODEL),
                    layout_model=getattr(settings, 'LAYOUT_ARCHITECT_MODEL', settings.LAYOUT_ENGINE_MODEL)
                )
                self.use_streaming = True
            else:
                logger.info("Using Phase 2B Content-Driven Architecture (non-streaming)")
                self.layout_architect = LayoutArchitectOrchestratorPhase2B(
                    theme_model=settings.THEME_AGENT_MODEL,
                    content_model=getattr(settings, 'CONTENT_AGENT_MODEL', settings.THEME_AGENT_MODEL),
                    layout_model=getattr(settings, 'LAYOUT_ARCHITECT_MODEL', settings.LAYOUT_ENGINE_MODEL)
                )
                self.use_streaming = False
        else:
            logger.info("Using Phase 2A Two-Agent Architecture")
            # Check if we should use new 2-agent workflow or legacy 3-agent
            use_legacy = getattr(settings, 'USE_LEGACY_WORKFLOW', False)
            self.layout_architect = LayoutArchitectOrchestrator(
                theme_model=settings.THEME_AGENT_MODEL,
                structure_layout_model=getattr(settings, 'STRUCTURE_AGENT_MODEL', settings.THEME_AGENT_MODEL),
                use_legacy_workflow=use_legacy
            )
            self.use_streaming = False
        
        # Store layout config for later use
        self.layout_config = LayoutConfig(
            model_name=settings.LAYOUT_ARCHITECT_MODEL,
            temperature=settings.LAYOUT_ARCHITECT_TEMPERATURE,
            grid_width=settings.LAYOUT_GRID_WIDTH,
            grid_height=settings.LAYOUT_GRID_HEIGHT,
            margin=settings.LAYOUT_MARGIN,
            gutter=settings.LAYOUT_GUTTER,
            white_space_min=settings.LAYOUT_WHITE_SPACE_MIN,
            white_space_max=settings.LAYOUT_WHITE_SPACE_MAX
        )
        
        self.director_out = DirectorOUT(websocket_handler)
    
    async def handle_layout_generation_state(
        self,
        session_id: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle the LAYOUT_GENERATION state.
        
        This is called when the state machine transitions to LAYOUT_GENERATION
        after strawman approval.
        """
        try:
            logger.warning(f"[DEBUG DirectorPhase2Extension] Starting layout generation for session {session_id}")
            logger.warning(f"[DEBUG DirectorPhase2Extension] Has websocket_handler: {self.websocket_handler is not None}")
            
            # Get strawman from context or session
            strawman = context.get('strawman_data')
            logger.warning(f"[DEBUG DirectorPhase2Extension] Strawman from context: {strawman is not None}")
            logger.warning(f"[DEBUG DirectorPhase2Extension] Context keys: {list(context.keys())}")
            
            if not strawman:
                logger.warning(f"[DEBUG DirectorPhase2Extension] No strawman in context, fetching from session")
                session = await self.session_manager.get_session(session_id)
                # Session has presentation_strawman, not strawman_data
                strawman = session.presentation_strawman
                logger.warning(f"[DEBUG DirectorPhase2Extension] Strawman from session: {strawman is not None}")
                logger.warning(f"[DEBUG DirectorPhase2Extension] Strawman type: {type(strawman)}")
            
            if not strawman:
                logger.error(f"[DEBUG DirectorPhase2Extension] No strawman data found in context or session")
                raise ValueError("No strawman data available for layout generation")
            
            # Convert dict to PresentationStrawman if needed
            if isinstance(strawman, dict):
                logger.warning(f"[DEBUG DirectorPhase2Extension] Converting strawman dict to PresentationStrawman object")
                try:
                    strawman = PresentationStrawman(**strawman)
                    logger.warning(f"[DEBUG DirectorPhase2Extension] Successfully converted strawman")
                except Exception as e:
                    logger.error(f"[DEBUG DirectorPhase2Extension] Failed to convert strawman: {e}")
                    logger.error(f"[DEBUG DirectorPhase2Extension] Strawman keys: {list(strawman.keys()) if isinstance(strawman, dict) else 'N/A'}")
                    raise
            
            logger.warning(f"[DEBUG DirectorPhase2Extension] Strawman has {len(getattr(strawman, 'slides', [])) if hasattr(strawman, 'slides') else 'unknown'} slides")
            
            # Process strawman with Layout Architect Orchestrator
            logger.warning(f"[DEBUG DirectorPhase2Extension] Calling Layout Architect Orchestrator process_strawman")
            
            # Extract user context from session if available
            user_context = {}
            if self.session_manager:
                session = await self.session_manager.get_session(session_id)
                user_context = {
                    'brand': getattr(session, 'brand_info', {}),
                    'user_preferences': getattr(session, 'user_preferences', {})
                }
            
            # Check if we're using streaming
            if self.use_streaming and self.director_out:
                logger.info("Using STREAMING layout generation")
                
                # Create callbacks for streaming updates
                def on_theme_ready(theme):
                    logger.info(f"Theme ready callback: {theme.name}")
                    # Send theme immediately via DirectorOUT
                    asyncio.create_task(self.director_out.send_theme_update(session_id, theme))
                
                def on_slide_ready(layout, content_manifest):
                    logger.info(f"Slide ready callback: {layout.slide_id}")
                    # Send slide update immediately via DirectorOUT
                    asyncio.create_task(self.director_out.send_slide_update(
                        session_id=session_id,
                        layout=layout,
                        strawman_data=strawman,
                        is_first=False
                    ))
                
                def on_status_update(status_text, progress):
                    logger.info(f"Status update: {status_text} ({progress}%)")
                    # Send status update via DirectorOUT
                    asyncio.create_task(self.director_out.send_status_update(
                        session_id=session_id,
                        status="generating",
                        text=status_text,
                        progress=progress
                    ))
                
                callbacks = StreamingCallbacks(
                    on_theme_ready=on_theme_ready,
                    on_slide_ready=on_slide_ready,
                    on_status_update=on_status_update
                )
                
                # Process with streaming
                layouts = []
                theme = None
                async for update in self.layout_architect.process_strawman_streaming(
                    strawman=strawman,
                    session_id=session_id,
                    callbacks=callbacks,
                    user_context=user_context
                ):
                    if update["type"] == "theme_ready":
                        theme = update["theme"]
                    elif update["type"] == "slide_ready":
                        layouts.append(update["layout"])
                    elif update["type"] == "complete":
                        logger.info(f"Streaming complete: {update['successful_slides']}/{update['total_slides']} slides")
                        # Send completion status
                        await self.director_out.send_status_update(
                            session_id=session_id,
                            status="complete",
                            text="All slides generated successfully!",
                            progress=100
                        )
                
                # Build result for session update
                result = {
                    'theme': theme,
                    'layouts': layouts,
                    'metadata': {
                        'streaming': True,
                        'total_slides': len(strawman.slides),
                        'successful_layouts': len(layouts)
                    }
                }
            else:
                # Non-streaming path
                logger.info("Using NON-STREAMING layout generation")
                result = await self.layout_architect.process_strawman(
                    strawman=strawman,
                    session_id=session_id,
                    user_context=user_context
                )
                logger.warning(f"[DEBUG DirectorPhase2Extension] Layout Architect returned: theme={result.get('theme') is not None}, layouts={len(result.get('layouts', []))}")
                
                # Send updates via Director OUT (batch mode)
                if self.director_out:
                    logger.warning(f"[DEBUG DirectorPhase2Extension] Calling DirectorOUT handle_layout_generation")
                    try:
                        await self.director_out.handle_layout_generation(
                            session_id=session_id,
                            theme=result['theme'],
                            layouts=result['layouts'],
                            strawman_data=strawman
                        )
                        logger.warning(f"[DEBUG DirectorPhase2Extension] DirectorOUT handle_layout_generation completed")
                    except Exception as e:
                        logger.error(f"[DEBUG DirectorPhase2Extension] DirectorOUT failed: {e}", exc_info=True)
                        raise
            
            # Update session state
            await self.session_manager.update_session_data(
                session_id=session_id,
                layout_data={
                    'theme': result['theme'].model_dump() if hasattr(result['theme'], 'model_dump') else result['theme'].dict(),
                    'layouts': [layout.model_dump() if hasattr(layout, 'model_dump') else layout.dict() for layout in result['layouts']],
                    'status': 'complete'
                }
            )
            
            logger.info(f"Layout generation complete for session {session_id}")
            
            # Get theme name from ThemeDefinition object
            theme_name = getattr(result['theme'], 'name', 'default')
            
            return {
                'status': 'complete',
                'message': 'Layouts generated successfully',
                'theme_name': theme_name,
                'slide_count': len(result['layouts'])
            }
            
        except Exception as e:
            logger.error(f"[DEBUG DirectorPhase2Extension] Layout generation failed: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }