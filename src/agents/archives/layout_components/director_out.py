"""
Director OUT agent for Phase 2.

Handles assembly and progressive delivery of layout updates
following the WebSocket Phase 2 protocol.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from src.utils.logger import setup_logger
from src.models.websocket_messages import (
    MessageType, SlideUpdatePayload, StatusPayload,
    SlideData, SlideMetadata
)
from src.agents.layout_architect.models import MVPTheme, MVPLayout

logger = setup_logger(__name__)


class DirectorOUT:
    """
    Director OUT agent for assembling and delivering progressive updates.
    
    Responsibilities:
    - Receive layouts from Layout Architect
    - Convert to WebSocket Phase 2 format
    - Send theme updates
    - Send progressive slide updates
    - Track content state
    """
    
    def __init__(self, websocket_handler=None):
        """Initialize Director OUT with optional WebSocket handler."""
        self.websocket_handler = websocket_handler
        self.update_sequence = 0
        logger.info(f"[DEBUG DirectorOUT] Initialized with websocket_handler: {websocket_handler is not None}")
    
    async def handle_layout_generation(
        self,
        session_id: str,
        theme: MVPTheme,
        layouts: List[MVPLayout],
        strawman_data: Any
    ) -> None:
        """
        Handle the complete layout generation process.
        
        Args:
            session_id: Current session ID
            theme: Generated theme
            layouts: List of layouts for all slides
            strawman_data: Original strawman for metadata
        """
        try:
            logger.info(f"[DEBUG DirectorOUT] Starting layout generation for session {session_id}")
            logger.info(f"[DEBUG DirectorOUT] Theme: {theme.theme_name if theme else 'None'}")
            logger.info(f"[DEBUG DirectorOUT] Number of layouts: {len(layouts) if layouts else 0}")
            
            # Validate inputs
            if not theme:
                raise ValueError("No theme provided to handle_layout_generation")
            if not layouts:
                raise ValueError("No layouts provided to handle_layout_generation")
            if not isinstance(layouts, list):
                raise TypeError(f"Layouts must be a list, got {type(layouts)}")
            
            # Send theme update first
            await self.send_theme_update(session_id, theme)
            
            # Send status update
            await self.send_status_update(
                session_id,
                status="generating",
                text="Enhancing slide layouts...",
                progress=10
            )
            
            # Send progressive slide updates
            total_slides = len(layouts)
            for i, layout in enumerate(layouts):
                progress = int(10 + (80 * (i + 1) / total_slides))
                logger.warning(f"[DEBUG DirectorOUT] Processing slide {i+1}/{total_slides}")
                
                # Send individual slide update
                try:
                    await self.send_slide_update(
                        session_id=session_id,
                        layout=layout,
                        strawman_data=strawman_data,
                        is_first=(i == 0)
                    )
                except Exception as e:
                    logger.error(f"[DEBUG DirectorOUT] Failed to send slide {i+1}: {e}")
                    raise
                
                # Update progress
                await self.send_status_update(
                    session_id=session_id,
                    status="generating",
                    text=f"Processing slide {i + 1} of {total_slides}",
                    progress=progress
                )
            
            # Send completion status
            await self.send_status_update(
                session_id=session_id,
                status="complete",
                text="Layout generation complete",
                progress=100
            )
            
        except Exception as e:
            logger.error(f"Failed to handle layout generation: {e}")
            await self.send_status_update(
                session_id=session_id,
                status="error",
                text="Failed to generate layouts"
            )
            raise
    
    async def send_theme_update(
        self,
        session_id: str,
        theme: Any
    ) -> None:
        """Send theme update message following Phase 2 protocol."""
        logger.info(f"[DEBUG DirectorOUT] send_theme_update called for session {session_id}")
        
        if not self.websocket_handler:
            logger.error("[DEBUG DirectorOUT] No WebSocket handler configured - cannot send theme update")
            return
        
        logger.info(f"[DEBUG DirectorOUT] WebSocket handler exists, checking if it has send_message method")
        
        # Convert theme to WebSocket format
        theme_payload = None
        if hasattr(theme, 'to_websocket_format'):
            # MVPTheme has this method
            theme_payload = theme.to_websocket_format()
        elif hasattr(theme, 'design_tokens'):
            # ThemeDefinition from three-agent system
            theme_payload = self._convert_theme_definition_to_websocket(theme)
        else:
            logger.error(f"[DEBUG DirectorOUT] Unknown theme type: {type(theme)}")
            return
        
        message = {
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "theme_update",
            "payload": theme_payload
        }
        
        logger.info(f"[DEBUG DirectorOUT] Theme update message prepared: {message['type']}")
        logger.info(f"[DEBUG DirectorOUT] Theme payload: {message['payload']}")
        
        try:
            await self.websocket_handler.send_message(message)
            logger.info(f"[DEBUG DirectorOUT] Successfully sent theme update for session {session_id}")
        except Exception as e:
            logger.error(f"[DEBUG DirectorOUT] Failed to send theme update: {e}", exc_info=True)
    
    async def send_slide_update(
        self,
        session_id: str,
        layout: MVPLayout,
        strawman_data: Any,
        is_first: bool = False
    ) -> None:
        """Send progressive slide update following Phase 2 protocol."""
        logger.info(f"[DEBUG DirectorOUT] send_slide_update called for slide {layout.slide_id}")
        
        if not self.websocket_handler:
            logger.error("[DEBUG DirectorOUT] No WebSocket handler configured - cannot send slide update")
            return
        
        self.update_sequence += 1
        
        # Build slide data
        try:
            slide_data = {
                "slide_id": layout.slide_id,
                "slide_number": layout.slide_number,
                "slide_type": layout.slide_type,
                "layout": layout.layout,
                "layout_spec": layout.layout_spec.dict() if layout.layout_spec else {},
                "content_state": layout.content_state.dict() if layout.content_state else {},
                "containers": [c.dict() for c in layout.containers] if layout.containers else []
            }
        except AttributeError as e:
            logger.error(f"[DEBUG DirectorOUT] Layout missing required attribute: {e}")
            logger.error(f"[DEBUG DirectorOUT] Layout type: {type(layout)}")
            logger.error(f"[DEBUG DirectorOUT] Layout attributes: {dir(layout)}")
            raise
        
        # Add original strawman data
        original_slide = self._find_original_slide(
            layout.slide_id, strawman_data
        )
        if original_slide:
            try:
                slide_data.update({
                    "title": original_slide.title,
                    "narrative": original_slide.narrative,
                    "key_points": original_slide.key_points,
                    "analytics_needed": original_slide.analytics_needed,
                    "visuals_needed": original_slide.visuals_needed,
                    "diagrams_needed": original_slide.diagrams_needed,
                    "structure_preference": original_slide.structure_preference
                })
            except AttributeError as e:
                logger.error(f"[DEBUG DirectorOUT] Original slide missing attribute: {e}")
                logger.error(f"[DEBUG DirectorOUT] Original slide type: {type(original_slide)}")
                logger.error(f"[DEBUG DirectorOUT] Original slide attributes: {dir(original_slide)}")
                # Add only available attributes
                for attr in ["title", "narrative", "key_points", "analytics_needed", 
                           "visuals_needed", "diagrams_needed", "structure_preference"]:
                    if hasattr(original_slide, attr):
                        slide_data[attr] = getattr(original_slide, attr)
        else:
            logger.warning(f"[DEBUG DirectorOUT] No original slide found for {layout.slide_id}")
        
        # Build metadata for first slide
        metadata = None
        if is_first:
            metadata = {
                "main_title": strawman_data.main_title,
                "overall_theme": strawman_data.theme,
                "design_suggestions": f"Theme: {layout.layout}",
                "target_audience": strawman_data.target_audience,
                "presentation_duration": int(strawman_data.presentation_duration)
            }
        
        # Create payload
        payload = {
            "operation": "progressive_update",
            "update_sequence": self.update_sequence,
            "slides": [slide_data],
            "affected_slides": [layout.slide_id]
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        # Send message
        message = {
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "slide_update",
            "payload": payload
        }
        
        logger.info(f"[DEBUG DirectorOUT] Slide update message prepared for slide {layout.slide_id}")
        
        try:
            await self.websocket_handler.send_message(message)
            logger.info(f"[DEBUG DirectorOUT] Successfully sent slide update for {layout.slide_id}")
        except Exception as e:
            logger.error(f"[DEBUG DirectorOUT] Failed to send slide update: {e}", exc_info=True)
    
    async def send_status_update(
        self,
        session_id: str,
        status: str,
        text: str,
        progress: Optional[int] = None,
        estimated_time: Optional[int] = None
    ) -> None:
        """Send status update message."""
        logger.info(f"[DEBUG DirectorOUT] send_status_update called: {status} - {text}")
        
        if not self.websocket_handler:
            logger.error("[DEBUG DirectorOUT] No WebSocket handler configured - cannot send status update")
            return
        
        payload = StatusPayload(
            status=status,
            text=text,
            progress=progress,
            estimated_time=estimated_time
        )
        
        message = {
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "status_update",
            "payload": payload.dict(exclude_none=True)
        }
        
        try:
            await self.websocket_handler.send_message(message)
            logger.info(f"[DEBUG DirectorOUT] Successfully sent status update: {status}")
        except Exception as e:
            logger.error(f"[DEBUG DirectorOUT] Failed to send status update: {e}", exc_info=True)
    
    async def send_content_state_update(
        self,
        session_id: str,
        slide_states: Dict[str, Dict]
    ) -> None:
        """Send content state update for tracking agent progress."""
        if not self.websocket_handler:
            logger.warning("No WebSocket handler configured")
            return
        
        message = {
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "content_state_update",
            "payload": {
                "slide_states": slide_states,
                "presentation_progress": self._calculate_progress(slide_states)
            }
        }
        
        await self.websocket_handler.send_message(message)
    
    def _find_original_slide(
        self,
        slide_id: str,
        strawman_data: Any
    ) -> Optional[Any]:
        """Find original slide data from strawman."""
        if not strawman_data:
            logger.warning(f"[DEBUG DirectorOUT] _find_original_slide: No strawman_data provided")
            return None
            
        if not hasattr(strawman_data, 'slides'):
            logger.warning(f"[DEBUG DirectorOUT] _find_original_slide: strawman_data has no 'slides' attribute")
            logger.warning(f"[DEBUG DirectorOUT] strawman_data type: {type(strawman_data)}")
            logger.warning(f"[DEBUG DirectorOUT] strawman_data attributes: {dir(strawman_data)}")
            return None
        
        logger.warning(f"[DEBUG DirectorOUT] Looking for slide_id: {slide_id} in {len(strawman_data.slides)} slides")
        for slide in strawman_data.slides:
            if slide.slide_id == slide_id:
                logger.warning(f"[DEBUG DirectorOUT] Found matching slide: {slide_id}")
                return slide
        
        logger.warning(f"[DEBUG DirectorOUT] No slide found with id: {slide_id}")
        return None
    
    def _calculate_progress(
        self,
        slide_states: Dict[str, Dict]
    ) -> int:
        """Calculate overall presentation progress."""
        if not slide_states:
            return 0
        
        total_progress = 0
        for state in slide_states.values():
            if 'overall_progress' in state:
                total_progress += state['overall_progress']
        
        return int(total_progress / len(slide_states))
    
    def _convert_theme_definition_to_websocket(
        self,
        theme: Any
    ) -> Dict[str, Any]:
        """Convert ThemeDefinition to WebSocket format."""
        # Extract theme name
        theme_name = theme.name if hasattr(theme, 'name') else 'default'
        
        # Convert design tokens to WebSocket format
        design_tokens = theme.design_tokens
        
        # Build colors
        colors = {}
        if hasattr(design_tokens.colors, 'items'):
            # If colors is a dict
            for key, token in design_tokens.colors.items():
                if hasattr(token, 'value'):
                    colors[key] = token.value
        else:
            # If colors is an object with attributes
            colors = {
                "primary": getattr(design_tokens.colors.get('primary', {}), 'value', '#0066cc'),
                "secondary": getattr(design_tokens.colors.get('secondary', {}), 'value', '#4d94ff'),
                "background": getattr(design_tokens.colors.get('background', {}), 'value', '#ffffff'),
                "text": getattr(design_tokens.colors.get('text', {}), 'value', '#333333'),
                "accent": getattr(design_tokens.colors.get('accent', {}), 'value', '#ff6b6b')
            }
        
        # Build typography
        typography = {}
        if hasattr(design_tokens.typography, 'items'):
            for key, token in design_tokens.typography.items():
                if hasattr(token, 'fontFamily'):
                    typography[key] = {
                        "fontSize": getattr(token.fontSize, 'value', 18),
                        "fontFamily": getattr(token.fontFamily, 'value', 'Inter'),
                        "fontWeight": getattr(token.fontWeight, 'value', 'normal') if hasattr(token, 'fontWeight') else 'normal',
                        "lineHeight": getattr(token.lineHeight, 'value', 1.5) if hasattr(token, 'lineHeight') else 1.5
                    }
        
        # Build layouts from layout_templates
        layouts = {}
        if hasattr(theme, 'layout_templates'):
            for template_name, template in theme.layout_templates.items():
                containers = {}
                if hasattr(template, 'zones'):
                    for zone_name, zone in template.zones.items():
                        containers[zone_name] = {
                            "leftInset": zone.leftInset,
                            "topInset": zone.topInset,
                            "width": zone.width,
                            "height": zone.height
                        }
                layouts[template_name] = {"containers": containers}
        
        # Build theme config
        theme_config = {
            "layouts": layouts,
            "typography": typography,
            "colors": colors
        }
        
        # Build WebSocket payload
        payload = {
            "theme_name": theme_name,
            "theme_config": theme_config,
            "delivery_timing": "before_slides"
        }
        
        # Add strawman context if available
        if hasattr(theme, 'strawman_context') and theme.strawman_context:
            if 'overall_theme' in theme.strawman_context:
                payload["strawman_overall_theme"] = theme.strawman_context['overall_theme']
            if 'design_suggestions' in theme.strawman_context:
                payload["strawman_design_suggestions"] = theme.strawman_context['design_suggestions']
            if 'audience' in theme.strawman_context:
                payload["strawman_target_audience"] = theme.strawman_context['audience']
        
        return payload