"""
Tool-free Simplified Theme Agent - Uses LLM knowledge directly for colors and fonts.

This agent creates color palettes and font pairings using the LLM's built-in knowledge
rather than external tools, making it simpler and more reliable.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from src.models.agents import PresentationStrawman
from src.utils.logger import setup_logger
from src.utils.agent_context_manager import (
    AgentContextManager, ContextAwareAgent, AgentType
)
from src.utils.model_utils import create_model_with_fallback
from src.models.design_tokens import (
    DesignTokens, ThemeDefinition, ColorToken, TypographyToken,
    DimensionToken, TokenValue, TokenType
)

logger = setup_logger(__name__)


class ThemeContext(BaseModel):
    """Context for theme generation"""
    strawman: PresentationStrawman
    session_id: str
    director_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from director including formality and complexity"
    )
    brand_guidelines: Optional[Dict[str, Any]] = None


class NoToolThemeOutput(BaseModel):
    """Direct theme output without tool dependencies"""
    theme_name: str = Field(description="Descriptive name for the theme")
    
    # Direct color palette
    colors: Dict[str, str] = Field(
        description="Color palette with hex values",
        default_factory=lambda: {
            "primary": "#0066cc",
            "secondary": "#4d94ff",
            "accent": "#ff6b6b",
            "background": "#ffffff",
            "text": "#212121"
        }
    )
    
    # Direct typography specification
    typography: Dict[str, Dict[str, Any]] = Field(
        description="Font specifications",
        default_factory=lambda: {
            "heading": {"family": "Roboto", "size": 36, "weight": 700},
            "body": {"family": "Open Sans", "size": 18, "weight": 400},
            "caption": {"family": "Open Sans", "size": 14, "weight": 400}
        }
    )
    
    # Context from director
    formality_level: str = Field(default="medium")
    complexity_allowance: str = Field(default="detailed")
    
    # Rationales
    theme_rationale: str = Field(
        default="Professional theme optimized for clarity and engagement"
    )


class ToolFreeThemeAgent(ContextAwareAgent):
    """
    Tool-free Theme Agent - Creates themes using LLM knowledge directly.
    
    This simplified version doesn't require external tools, making it more
    reliable with standard Gemini Flash models.
    """
    
    def __init__(
        self, 
        model_name: str = "gemini-2.5-flash",
        context_manager: Optional[AgentContextManager] = None
    ):
        """Initialize Theme Agent with AI model"""
        if context_manager:
            super().__init__(AgentType.THEME, context_manager)
        else:
            self.context_manager = None
            
        self.model = create_model_with_fallback(model_name)
        logger.info(f"Initialized ToolFreeThemeAgent with model: {model_name}")
        
        # Create agent without tools
        self.agent = Agent(
            self.model,
            output_type=NoToolThemeOutput,
            deps_type=ThemeContext,
            tools=[],  # No tools needed
            system_prompt=self._get_comprehensive_prompt(),
            retries=2
        )
    
    def _get_comprehensive_prompt(self) -> str:
        """Get comprehensive prompt with built-in design knowledge"""
        return """You are an expert presentation theme designer. Create a cohesive color palette and font pairing based on the presentation context.

Your output must include:

1. COLORS - A palette with EXACTLY these 5 colors (use hex values):
   - primary: The main brand color (vibrant, memorable)
   - secondary: Supporting color (harmonizes with primary)
   - accent: Highlight color (for CTAs and emphasis)
   - background: Background color (usually white #ffffff or very light)
   - text: Primary text color (dark for readability, usually #212121 or similar)

2. TYPOGRAPHY - Font specifications with EXACTLY these 3 roles:
   - heading: {"family": "Font Name", "size": 32-48, "weight": 600-700}
   - body: {"family": "Font Name", "size": 16-20, "weight": 400}
   - caption: {"family": "Font Name", "size": 14-16, "weight": 400}

INDUSTRY COLOR GUIDELINES:

Healthcare/Medical:
- Primary: Blues (#0077B6) or teals (#00B4D8) for trust and calm
- Avoid reds (blood association)
- Clean, professional palette

Finance/Banking:
- Primary: Deep blues (#003566, #001D3D) for stability
- Gold accents (#FFD60A) for prosperity
- Conservative, trustworthy colors

Technology/Software:
- Primary: Modern purples (#7209B7) or blues (#0066cc)
- Bright accents (#B5179E, #4CC9F0)
- Forward-thinking, innovative palette

Education:
- Primary: Greens (#2D6A4F, #40916C) for growth
- Warm, approachable colors
- Engaging but not distracting

General Business:
- Primary: Professional blue (#0066CC)
- Balanced, versatile palette
- Works across contexts

TYPOGRAPHY GUIDELINES:

High Formality (executives, investors):
- Heading: Helvetica Neue, Playfair Display, or Georgia
- Body: Georgia, Baskerville, or Helvetica Neue
- Classic, authoritative fonts

Medium Formality (team, department):
- Heading: Roboto, Source Sans Pro, or Montserrat
- Body: Open Sans, Lato, or Roboto
- Modern, clean, readable

Casual (public, students):
- Heading: Montserrat, Quicksand, or Nunito
- Body: Lato, Open Sans, or Nunito
- Friendly, approachable fonts

IMPORTANT RULES:
1. Ensure text has high contrast against background (WCAG AA compliant)
2. Heading font can be different from body for hierarchy
3. Body and caption should use the same font family
4. All colors must be valid hex codes
5. Font families must be commonly available
6. Consider the viewing context (projection needs larger sizes)

Base your design on:
- The presentation's overall theme and purpose
- The target audience's expectations
- The appropriate formality level
- Industry best practices

Create a cohesive, professional theme that enhances the presentation's message."""
    
    async def generate_theme(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        director_metadata: Optional[Dict[str, Any]] = None,
        brand_guidelines: Optional[Dict[str, Any]] = None
    ) -> ThemeDefinition:
        """Generate theme using LLM knowledge directly"""
        start_time = time.time()
        
        # Track processing start if context manager available
        if self.context_manager:
            upstream_context = self.get_upstream_context()
            input_data = {
                "strawman": strawman.dict(),
                "director_metadata": director_metadata,
                "brand_guidelines": brand_guidelines,
                "upstream_context": upstream_context
            }
            self.start_processing(input_data, {"started_at": datetime.utcnow().isoformat()})
        
        try:
            logger.info(f"Starting tool-free theme generation for session {session_id}")
            
            # Extract metadata
            metadata = director_metadata or {}
            formality_level = metadata.get("formality_level", "medium")
            complexity_allowance = metadata.get("complexity_allowance", "detailed")
            
            # Create context
            context = ThemeContext(
                strawman=strawman,
                session_id=session_id,
                director_metadata=metadata,
                brand_guidelines=brand_guidelines
            )
            
            # Build prompt
            prompt = self._build_specific_prompt(strawman, metadata)
            
            # Run agent
            import asyncio
            try:
                logger.info("Running tool-free theme agent...")
                result = await asyncio.wait_for(
                    self.agent.run(prompt, deps=context),
                    timeout=20.0  # Faster without tools
                )
                
                generation_time = int((time.time() - start_time) * 1000)
                logger.info(f"Theme generated in {generation_time}ms")
                
                # Log output
                logger.info(f"Generated theme: {result.output.theme_name}")
                logger.info(f"Colors: {result.output.colors}")
                logger.info(f"Typography: {result.output.typography}")
                
            except asyncio.TimeoutError:
                logger.error(f"Theme generation timed out for session {session_id}")
                return self._create_fallback_theme(strawman, formality_level, complexity_allowance)
            
            # Convert to ThemeDefinition
            theme = self._build_theme_definition(result.output, generation_time)
            
            logger.info(f"Successfully generated theme '{theme.name}'")
            
            # Track completion if context manager available
            if self.context_manager:
                output_data = {
                    "theme_definition": theme.dict(),
                    "generation_method": "ai_generated",
                    "generation_time_ms": generation_time
                }
                self.complete_processing(output_data)
                await self.context_manager.save_to_storage()
            
            return theme
            
        except Exception as e:
            logger.error(f"Theme generation failed: {e}")
            
            if self.context_manager:
                self.fail_processing(str(e))
            
            return self._create_fallback_theme(
                strawman,
                metadata.get("formality_level", "medium"),
                metadata.get("complexity_allowance", "detailed")
            )
    
    def _build_specific_prompt(self, strawman: PresentationStrawman, metadata: Dict[str, Any]) -> str:
        """Build specific prompt for this presentation"""
        industry = self._extract_industry(strawman)
        formality = metadata.get("formality_level", "medium")
        
        return f"""Create a theme for this presentation:

CONTEXT:
- Title: {strawman.main_title}
- Theme: {strawman.overall_theme}
- Audience: {strawman.target_audience}
- Industry: {industry}
- Formality Level: {formality}
- Duration: {strawman.presentation_duration} minutes

REQUIREMENTS:
1. Choose colors appropriate for {industry} presentations
2. Select fonts matching {formality} formality level
3. Ensure all colors work well together
4. Name the theme based on the presentation context

Remember to provide exactly 5 colors and 3 typography specifications as defined in the guidelines."""
    
    def _extract_industry(self, strawman: PresentationStrawman) -> str:
        """Extract industry from strawman context"""
        text = f"{strawman.main_title} {strawman.overall_theme}".lower()
        
        if any(word in text for word in ["health", "medical", "clinical", "patient"]):
            return "healthcare"
        elif any(word in text for word in ["finance", "investment", "banking", "trading"]):
            return "finance"
        elif any(word in text for word in ["tech", "software", "ai", "digital", "data"]):
            return "technology"
        elif any(word in text for word in ["education", "learning", "student", "academic"]):
            return "education"
        else:
            return "general business"
    
    def _build_theme_definition(self, output: NoToolThemeOutput, generation_time: int) -> ThemeDefinition:
        """Convert output to ThemeDefinition"""
        # Build color tokens
        colors = {}
        for color_name, hex_value in output.colors.items():
            colors[color_name] = ColorToken(value=hex_value, type=TokenType.COLOR)
        
        # Build typography tokens
        typography = {}
        for font_role, font_spec in output.typography.items():
            typography[font_role] = TypographyToken(
                fontFamily=TokenValue(
                    value=font_spec.get("family", "Arial"),
                    type=TokenType.FONT_FAMILY
                ),
                fontSize=TokenValue(
                    value=font_spec.get("size", 16),
                    type=TokenType.FONT_SIZE
                ),
                fontWeight=TokenValue(
                    value=font_spec.get("weight", 400),
                    type=TokenType.FONT_WEIGHT
                ),
                lineHeight=TokenValue(
                    value=font_spec.get("lineHeight", 1.5),
                    type=TokenType.LINE_HEIGHT
                )
            )
        
        # Create spacing tokens
        spacing = {
            "xs": DimensionToken(value=4, type=TokenType.DIMENSION, unit="px"),
            "sm": DimensionToken(value=8, type=TokenType.DIMENSION, unit="px"),
            "md": DimensionToken(value=16, type=TokenType.DIMENSION, unit="px"),
            "lg": DimensionToken(value=24, type=TokenType.DIMENSION, unit="px"),
            "xl": DimensionToken(value=32, type=TokenType.DIMENSION, unit="px")
        }
        
        # Create design tokens
        design_tokens = DesignTokens(
            name=output.theme_name,
            description=output.theme_rationale,
            colors=colors,
            typography=typography,
            spacing=spacing,
            sizing=spacing
        )
        
        return ThemeDefinition(
            name=output.theme_name,
            design_tokens=design_tokens,
            layout_templates={},
            formality_level=output.formality_level,
            complexity_allowance=output.complexity_allowance,
            metadata={
                "generation_method": "ai_generated",
                "generation_time_ms": generation_time,
                "tool_free": True
            }
        )
    
    def _create_fallback_theme(
        self,
        strawman: PresentationStrawman,
        formality_level: str,
        complexity_allowance: str
    ) -> ThemeDefinition:
        """Create fallback theme based on context"""
        industry = self._extract_industry(strawman)
        
        # Industry-specific color schemes
        color_schemes = {
            "healthcare": {
                "primary": "#0077B6",
                "secondary": "#00B4D8",
                "accent": "#90E0EF",
                "background": "#FFFFFF",
                "text": "#212529"
            },
            "finance": {
                "primary": "#003566",
                "secondary": "#001D3D",
                "accent": "#FFD60A",
                "background": "#FFFFFF",
                "text": "#000814"
            },
            "technology": {
                "primary": "#7209B7",
                "secondary": "#560BAD",
                "accent": "#B5179E",
                "background": "#FFFFFF",
                "text": "#240046"
            },
            "education": {
                "primary": "#2D6A4F",
                "secondary": "#40916C",
                "accent": "#52B788",
                "background": "#FFFFFF",
                "text": "#1B5E3F"
            },
            "general business": {
                "primary": "#0066CC",
                "secondary": "#4D94FF",
                "accent": "#FF6B6B",
                "background": "#FFFFFF",
                "text": "#212121"
            }
        }
        
        # Formality-based font schemes
        font_schemes = {
            "high": {
                "heading": {"family": "Helvetica Neue", "size": 36, "weight": 700},
                "body": {"family": "Georgia", "size": 18, "weight": 400},
                "caption": {"family": "Georgia", "size": 14, "weight": 400}
            },
            "medium": {
                "heading": {"family": "Roboto", "size": 36, "weight": 700},
                "body": {"family": "Open Sans", "size": 18, "weight": 400},
                "caption": {"family": "Open Sans", "size": 14, "weight": 400}
            },
            "casual": {
                "heading": {"family": "Montserrat", "size": 36, "weight": 600},
                "body": {"family": "Lato", "size": 18, "weight": 400},
                "caption": {"family": "Lato", "size": 14, "weight": 300}
            }
        }
        
        # Build theme output
        output = NoToolThemeOutput(
            theme_name=f"{industry.title()} Presentation Theme",
            colors=color_schemes.get(industry, color_schemes["general business"]),
            typography=font_schemes.get(formality_level, font_schemes["medium"]),
            formality_level=formality_level,
            complexity_allowance=complexity_allowance,
            theme_rationale=f"Fallback theme optimized for {industry} presentations with {formality_level} formality"
        )
        
        return self._build_theme_definition(output, 0)


# Export as SimplifiedThemeAgent for compatibility
SimplifiedThemeAgent = ToolFreeThemeAgent