"""
Theme generator for Layout Architect MVP.

Analyzes presentation context and generates professional themes
with colors, typography, and layout definitions.
"""

from typing import Dict, Tuple
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from src.models.agents import PresentationStrawman
from src.utils.logger import setup_logger
from .models import (
    MVPTheme, ThemeConfig, ThemeColors, ThemeTypography,
    ThemeLayout, GridPosition
)

logger = setup_logger(__name__)


class ThemeGenerator:
    """Generates themes based on presentation context."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """Initialize theme generator with AI model."""
        import os
        
        # Set GEMINI_API_KEY from GOOGLE_API_KEY if needed
        if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
            os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
        
        self.model = GeminiModel(model_name)
        self.agent = Agent(
            self.model,
            result_type=Dict,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for theme generation."""
        return """You are a professional presentation designer specializing in theme creation.
        
        Generate a cohesive theme based on the presentation context including:
        1. Color palette (3-5 colors with hex codes)
        2. Typography hierarchy (font sizes for different levels)
        3. Professional tone matching the audience and purpose
        
        Consider:
        - Target audience formality level
        - Industry/domain conventions
        - Presentation purpose (inform, persuade, educate)
        - Duration and complexity
        
        Return a JSON object with:
        - theme_name: descriptive name
        - color_palette: primary, secondary, background, text colors
        - typography_sizes: h1, h2, h3, body, caption sizes
        - tone: professional, modern, traditional, creative, etc.
        
        Pay special attention to any design suggestions provided in the context.
        """
    
    async def generate_theme(self, strawman: PresentationStrawman, session_id: str = "default") -> MVPTheme:
        """Generate theme from strawman context."""
        try:
            # Extract context for theme generation
            context = {
                "title": strawman.main_title,
                "audience": strawman.target_audience,
                "duration": strawman.presentation_duration,
                "overall_theme": strawman.overall_theme,
                "design_suggestions": strawman.design_suggestions,
                "slide_count": len(strawman.slides),
                "purpose": self._infer_purpose(strawman)
            }
            
            # Generate theme using AI
            result = await self.agent.run(
                f"Generate a presentation theme for: {context}"
            )
            theme_data = result.data
            
            # Build theme config
            theme_config = self._build_theme_config(theme_data)
            
            return MVPTheme(
                theme_name=theme_data.get("theme_name", "professional"),
                theme_config=theme_config,
                created_for_session=session_id,
                strawman_overall_theme=strawman.overall_theme,
                strawman_design_suggestions=strawman.design_suggestions,
                strawman_target_audience=strawman.target_audience
            )
            
        except Exception as e:
            logger.error(f"Theme generation failed: {e}")
            # Return default theme on error
            return self._get_default_theme(session_id)
    
    def _infer_purpose(self, strawman: PresentationStrawman) -> str:
        """Infer presentation purpose from content."""
        # Use overall_theme or main_title to infer purpose
        content = f"{strawman.overall_theme} {strawman.main_title}".lower()
        
        if any(word in content for word in ["convince", "persuade", "sell"]):
            return "persuade"
        elif any(word in content for word in ["teach", "educate", "learn"]):
            return "educate"
        elif any(word in content for word in ["update", "report", "status", "data"]):
            return "inform"
        else:
            return "general"
    
    def _build_theme_config(self, theme_data: Dict) -> ThemeConfig:
        """Build complete theme configuration."""
        # Extract colors
        colors = theme_data.get("color_palette", {})
        theme_colors = ThemeColors(
            primary=colors.get("primary", "#0066cc"),
            secondary=colors.get("secondary", "#4d94ff"),
            background=colors.get("background", "#ffffff"),
            text=colors.get("text", "#333333"),
            accent=colors.get("accent", "#ff6b6b")
        )
        
        # Build typography
        sizes = theme_data.get("typography_sizes", {})
        typography = {
            "h1": ThemeTypography(
                fontSize=sizes.get("h1", 48),
                fontWeight="bold"
            ),
            "h2": ThemeTypography(
                fontSize=sizes.get("h2", 36),
                fontWeight="bold"
            ),
            "h3": ThemeTypography(
                fontSize=sizes.get("h3", 28),
                fontWeight="medium"
            ),
            "body": ThemeTypography(
                fontSize=sizes.get("body", 18),
                fontWeight="normal"
            ),
            "caption": ThemeTypography(
                fontSize=sizes.get("caption", 14),
                fontWeight="normal"
            )
        }
        
        # Build layouts
        layouts = self._create_standard_layouts()
        
        return ThemeConfig(
            layouts=layouts,
            typography=typography,
            colors=theme_colors
        )
    
    def _create_standard_layouts(self) -> Dict[str, ThemeLayout]:
        """Create standard layouts for different slide types."""
        return {
            "titleSlide": ThemeLayout(
                containers={
                    "title": GridPosition(
                        leftInset=20, topInset=35, width=120, height=20
                    ),
                    "subtitle": GridPosition(
                        leftInset=20, topInset=55, width=120, height=10
                    )
                }
            ),
            "contentSlide": ThemeLayout(
                containers={
                    "title": GridPosition(
                        leftInset=8, topInset=8, width=144, height=12
                    ),
                    "body": GridPosition(
                        leftInset=8, topInset=24, width=144, height=58
                    )
                }
            ),
            "sectionHeader": ThemeLayout(
                containers={
                    "section_title": GridPosition(
                        leftInset=20, topInset=40, width=120, height=10
                    )
                }
            )
        }
    
    def _get_default_theme(self, session_id: str) -> MVPTheme:
        """Get default professional theme as fallback."""
        return MVPTheme(
            theme_name="professional_default",
            theme_config=ThemeConfig(
                layouts=self._create_standard_layouts(),
                typography={
                    "h1": ThemeTypography(fontSize=48, fontWeight="bold"),
                    "h2": ThemeTypography(fontSize=36, fontWeight="bold"),
                    "h3": ThemeTypography(fontSize=28, fontWeight="medium"),
                    "body": ThemeTypography(fontSize=18, fontWeight="normal"),
                    "caption": ThemeTypography(fontSize=14, fontWeight="normal")
                },
                colors=ThemeColors(
                    primary="#0066cc",
                    secondary="#4d94ff",
                    background="#ffffff",
                    text="#333333"
                )
            ),
            created_for_session=session_id
        )