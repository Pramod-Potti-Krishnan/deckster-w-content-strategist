"""
Layout Architect MVP Agent.

Main agent that orchestrates theme generation and layout creation
for the presentation strawman.
"""

import asyncio
from typing import List, Dict, Any, Optional
from uuid import uuid4

from src.models.agents import PresentationStrawman
from src.utils.logger import setup_logger
from src.utils.session_manager import SessionManager
from src.agents.base import BaseAgent

from .models import (
    MVPLayout, MVPTheme, LayoutConfig, LayoutArrangement
)
from .theme_generator import ThemeGenerator
from .layout_engine import LayoutEngine
from .tools import WhiteSpaceTool, AlignmentValidator

logger = setup_logger(__name__)


class LayoutArchitectMVP(BaseAgent):
    """
    MVP Layout Architect agent.
    
    Responsible for:
    - Generating presentation themes
    - Creating professional layouts with grid alignment
    - Ensuring white space and visual balance
    - Progressive delivery of layout updates
    """
    
    def __init__(
        self,
        config: Optional[LayoutConfig] = None,
        session_manager: Optional[SessionManager] = None
    ):
        """Initialize Layout Architect with configuration."""
        super().__init__(name="layout_architect")
        
        self.config = config or LayoutConfig()
        self.session_manager = session_manager
        
        # Initialize components
        self.theme_generator = ThemeGenerator(self.config.model_name)
        self.layout_engine = LayoutEngine(self.config)
        self.white_space_tool = WhiteSpaceTool(
            self.config.grid_width,
            self.config.grid_height,
            self.config.white_space_min,
            self.config.white_space_max
        )
        self.alignment_validator = AlignmentValidator(
            self.config.alignment_tolerance
        )
        
        # Cache for themes
        self._theme_cache: Dict[str, MVPTheme] = {}
    
    async def process_approved_strawman(
        self,
        session_id: str,
        user_id: str,
        strawman: Optional[PresentationStrawman] = None
    ) -> Dict[str, Any]:
        """
        Process approved strawman and generate layouts.
        
        Args:
            session_id: Current session ID
            user_id: User ID for authentication
            strawman: Optional strawman (will fetch from session if not provided)
            
        Returns:
            Dictionary with theme and layouts
        """
        try:
            logger.warning(f"[DEBUG LayoutArchitect] Processing strawman for session {session_id}")
            logger.warning(f"[DEBUG LayoutArchitect] Has session_manager: {self.session_manager is not None}")
            logger.warning(f"[DEBUG LayoutArchitect] Strawman provided: {strawman is not None}")
            
            # Get strawman from session if not provided
            if not strawman:
                if self.session_manager:
                    session = await self.session_manager.get_session(session_id)
                    strawman = session.strawman_data
                else:
                    raise ValueError("No strawman provided and no session manager available")
            
            if not strawman:
                raise ValueError("No strawman data available")
            
            # Generate or retrieve theme
            logger.warning(f"[DEBUG LayoutArchitect] Generating theme for strawman")
            theme = await self._get_or_generate_theme(strawman, session_id)
            logger.warning(f"[DEBUG LayoutArchitect] Generated theme: {theme.theme_name if theme else 'None'}")
            
            # Process slides progressively
            layouts = []
            logger.warning(f"[DEBUG LayoutArchitect] Processing {len(strawman.slides)} slides")
            for i, slide in enumerate(strawman.slides):
                logger.warning(f"[DEBUG LayoutArchitect] Processing slide {i+1}/{len(strawman.slides)}: {slide.slide_id}")
                
                # Add slide number if not present
                slide.slide_number = i + 1
                
                # Create layout for slide
                logger.info(f"[DEBUG LayoutArchitect] Creating layout for slide {slide.slide_id}")
                layout = await self._create_slide_layout(slide, theme)
                logger.info(f"[DEBUG LayoutArchitect] Created layout: {layout.layout if layout else 'None'}")
                
                # Validate layout
                is_valid = await self._validate_layout(layout)
                if not is_valid:
                    logger.warning(f"[DEBUG LayoutArchitect] Layout validation failed for slide {slide.slide_id}")
                else:
                    logger.info(f"[DEBUG LayoutArchitect] Layout validation passed for slide {slide.slide_id}")
                
                layouts.append(layout)
                logger.info(f"[DEBUG LayoutArchitect] Total layouts so far: {len(layouts)}")
                
                # Yield for progressive updates
                await asyncio.sleep(0)  # Allow other tasks to run
            
            logger.warning(f"[DEBUG LayoutArchitect] Successfully processed {len(layouts)} slides")
            logger.warning(f"[DEBUG LayoutArchitect] Returning result with theme: {theme.theme_name}, layouts: {len(layouts)}")
            
            # Validate layouts before returning
            for i, layout in enumerate(layouts):
                if not layout:
                    logger.error(f"[DEBUG LayoutArchitect] Layout {i} is None")
                    raise ValueError(f"Layout {i} is None")
                if not hasattr(layout, 'layout'):
                    logger.error(f"[DEBUG LayoutArchitect] Layout {i} missing 'layout' attribute")
                    logger.error(f"[DEBUG LayoutArchitect] Layout type: {type(layout)}")
                    logger.error(f"[DEBUG LayoutArchitect] Layout attributes: {dir(layout)}")
                    raise AttributeError(f"Layout {i} missing 'layout' attribute")
            
            result = {
                "theme": theme,
                "layouts": layouts,
                "session_id": session_id,
                "status": "complete"
            }
            logger.info(f"[DEBUG LayoutArchitect] Final result keys: {list(result.keys())}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process strawman: {e}")
            raise
    
    async def _get_or_generate_theme(
        self,
        strawman: PresentationStrawman,
        session_id: str
    ) -> MVPTheme:
        """Get theme from cache or generate new one."""
        
        # Check cache first
        if session_id in self._theme_cache:
            logger.info(f"Using cached theme for session {session_id}")
            return self._theme_cache[session_id]
        
        # Generate new theme
        logger.info("[DEBUG LayoutArchitect] Generating new theme via theme_generator")
        theme = await self.theme_generator.generate_theme(strawman, session_id)
        logger.info(f"[DEBUG LayoutArchitect] Theme generated: {theme.theme_name if theme else 'None'}")
        
        # Cache theme
        self._theme_cache[session_id] = theme
        
        # TODO: Save theme to database
        
        return theme
    
    async def _create_slide_layout(
        self,
        slide: Any,
        theme: MVPTheme
    ) -> MVPLayout:
        """Create layout for a single slide."""
        # Determine arrangement
        arrangement = LayoutArrangement.AUTO
        if self.config.auto_arrange:
            # Let engine determine best arrangement
            pass
        
        # Create layout
        layout = await self.layout_engine.process_slide(
            slide, theme, arrangement
        )
        
        logger.info(f"[DEBUG LayoutArchitect] Layout engine returned: {type(layout)}")
        if layout:
            logger.info(f"[DEBUG LayoutArchitect] Layout has 'layout' attr: {hasattr(layout, 'layout')}")
            if hasattr(layout, 'layout'):
                logger.info(f"[DEBUG LayoutArchitect] Layout value: {layout.layout}")
        
        # Validate and adjust if needed
        if layout and hasattr(layout, 'white_space_ratio') and layout.white_space_ratio < self.config.white_space_min:
            logger.warning(
                f"White space ratio {layout.white_space_ratio:.2f} "
                f"below minimum {self.config.white_space_min}"
            )
        
        return layout
    
    async def _validate_layout(self, layout: MVPLayout) -> bool:
        """Validate layout meets all requirements."""
        # Validate white space
        ws_valid, ws_msg = self.white_space_tool.validate_white_space_ratio(
            layout.white_space_ratio
        )
        if not ws_valid:
            logger.warning(f"White space validation: {ws_msg}")
        
        # Validate margins
        margin_valid, margin_issues = self.white_space_tool.validate_margins(
            layout.containers, self.config.margin
        )
        if not margin_valid:
            logger.warning(f"Margin violations: {margin_issues}")
        
        # Validate gutters
        gutter_valid, gutter_issues = self.white_space_tool.validate_gutters(
            layout.containers, self.config.gutter
        )
        if not gutter_valid:
            logger.warning(f"Gutter violations: {gutter_issues}")
        
        # Validate alignment
        align_valid, align_score, align_issues = self.alignment_validator.validate_alignment(
            layout.containers
        )
        if not align_valid:
            logger.warning(f"Alignment issues: {align_issues}")
        
        return ws_valid and margin_valid and gutter_valid and align_valid
    
    def get_layout_by_slide_id(
        self,
        slide_id: str,
        layouts: List[MVPLayout]
    ) -> Optional[MVPLayout]:
        """Get specific layout by slide ID."""
        for layout in layouts:
            if layout.slide_id == slide_id:
                return layout
        return None
    
    async def refine_layout(
        self,
        layout: MVPLayout,
        feedback: str
    ) -> MVPLayout:
        """Refine a layout based on feedback (future enhancement)."""
        logger.info(f"Refining layout for slide {layout.slide_id}")
        # For MVP, just return the same layout
        # Future: Implement actual refinement logic
        return layout