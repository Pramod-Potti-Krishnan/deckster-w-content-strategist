"""
Simplified Theme Agent - Focused on Color Palette and Font Pairing.

This agent creates only:
1. Harmonious color palettes using proper color theory
2. Optimal font pairings for presentations
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel

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
from .tools import (
    generate_color_palette_tool, find_font_pairing_tool,
    ColorPaletteInput, FontPairingInput,
    EnhancedColorPaletteGenerator, PresentationFontPairing
)
from pydantic_ai import Tool

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


class GenerationMetadata(BaseModel):
    """Metadata about how the theme was generated"""
    generation_method: Literal["ai_generated", "fallback"] = Field(
        description="Whether theme was AI-generated or fallback"
    )
    generation_time_ms: int = Field(
        description="Time taken to generate theme in milliseconds"
    )
    ai_confidence_score: float = Field(
        default=0.0,
        description="Confidence score of AI generation (0-1)"
    )
    fallback_reason: Optional[str] = Field(
        default=None,
        description="Reason for using fallback if applicable"
    )


class SimplifiedThemeOutput(BaseModel):
    """Simplified output focusing on colors and fonts only"""
    theme_name: str = Field(description="Descriptive name for the theme")
    
    # Core design elements
    colors: Dict[str, str] = Field(
        description="Color palette with hex values from ColorPaletteOutput.colors",
        default_factory=dict
    )
    typography: Dict[str, Dict[str, Any]] = Field(
        description="Font specifications built from FontPairingOutput",
        default_factory=dict
    )
    
    # Context from director
    formality_level: str = Field(
        description="Formality level from director: high, medium, casual",
        default="medium"
    )
    complexity_allowance: str = Field(
        description="Complexity level from director: executive, detailed, simplified",
        default="detailed"
    )
    
    # Generation metadata - with default factory
    generation_metadata: GenerationMetadata = Field(
        default_factory=lambda: GenerationMetadata(
            generation_method="ai_generated",
            generation_time_ms=0,
            ai_confidence_score=0.0
        ),
        description="Information about how theme was generated"
    )
    
    # Optional rationale
    color_rationale: Optional[str] = Field(
        default=None,
        description="Explanation of color choices"
    )
    font_rationale: Optional[str] = Field(
        default=None,
        description="Explanation of font pairing choices"
    )


class SimplifiedThemeAgent(ContextAwareAgent):
    """
    Simplified Theme Agent - Creates only color palettes and font pairings.
    
    Focuses on:
    - Generating harmonious color palettes with proper color theory
    - Selecting optimal font pairings for presentations
    - Using context from director and strawman effectively
    - Integrating with context management system
    """
    
    def __init__(
        self, 
        model_name: str = "gemini-2.5-flash",
        context_manager: Optional[AgentContextManager] = None
    ):
        """Initialize Theme Agent with AI model, focused tools, and context management"""
        # Initialize context-aware base if context manager provided
        if context_manager:
            super().__init__(AgentType.THEME, context_manager)
        else:
            self.context_manager = None
            
        self.model = create_model_with_fallback(model_name)
        logger.info(f"Initialized SimplifiedThemeAgent with model: {model_name}")
        
        # Create agent with only essential tools
        self.agent = Agent(
            self.model,
            output_type=SimplifiedThemeOutput,
            deps_type=ThemeContext,
            tools=[
                generate_color_palette_tool,
                find_font_pairing_tool
            ],
            system_prompt=self._get_system_prompt(),
            retries=2
        )
        logger.info(f"Agent created with {len(self.agent.tools)} tools")
    
    def _get_system_prompt(self) -> str:
        """Get focused system prompt for color and font generation"""
        return """You are a specialized Theme Agent focused on creating color palettes and font pairings.

Your role is to:
1. Generate harmonious color palettes using proper color theory
2. Select optimal font pairings for presentations

COLOR PALETTE GUIDELINES:
- Use proper color harmony rules (complementary, analogous, triadic, etc.)
- Consider the presentation context and industry
- Ensure WCAG accessibility compliance
- Create semantic color roles (primary, secondary, accent, etc.)
- Consider color psychology and cultural associations

FONT PAIRING GUIDELINES:
- Select fonts optimized for presentations (not web or print)
- Consider viewing distance and screen projection
- Ensure excellent readability and visual hierarchy
- Match formality level from director metadata
- Avoid overused defaults like Inter for presentations

Use the director's metadata for formality_level and complexity_allowance to guide your choices.
Generate a cohesive theme that works well for the specific presentation context.

IMPORTANT TOOL USAGE AND OUTPUT MAPPING:
1. First call generate_color_palette to create the color scheme
2. Then call find_font_pairing to select appropriate fonts

STEP-BY-STEP PROCESS (YOU MUST FOLLOW THIS EXACTLY):

1. FIRST, call the generate_color_palette tool with appropriate inputs based on the presentation context
2. WAIT for the ColorPaletteOutput response 
3. THEN, call the find_font_pairing tool with appropriate inputs
4. WAIT for the FontPairingOutput response
5. FINALLY, create your SimplifiedThemeOutput using the data from both tool responses

CRITICAL - How to map tool outputs to your SimplifiedThemeOutput:

colors field: Copy the entire 'colors' dictionary from ColorPaletteOutput.colors directly
Example: If ColorPaletteOutput.colors = {"primary": "#123456", "secondary": "#789ABC", ...}
Then your colors field = {"primary": "#123456", "secondary": "#789ABC", ...}

typography field: Build from FontPairingOutput like this:
{
  "heading": {
    "family": FontPairingOutput.heading_font,
    "size": FontPairingOutput.font_sizes["h1"],
    "weight": FontPairingOutput.font_weights["heading"]
  },
  "body": {
    "family": FontPairingOutput.body_font,
    "size": FontPairingOutput.font_sizes["body"],
    "weight": FontPairingOutput.font_weights["body"]
  },
  "caption": {
    "family": FontPairingOutput.body_font,
    "size": FontPairingOutput.font_sizes["caption"],
    "weight": FontPairingOutput.font_weights["body"]
  }
}

color_rationale: Use ColorPaletteOutput.rationale
font_rationale: Use FontPairingOutput.pairing_rationale
theme_name: Create based on context (e.g., "Modern Healthcare Theme", "Executive Finance Theme")

DO NOT return empty colors or typography fields! You MUST call the tools and use their outputs!"""
    
    async def generate_theme(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        director_metadata: Optional[Dict[str, Any]] = None,
        brand_guidelines: Optional[Dict[str, Any]] = None
    ) -> ThemeDefinition:
        """Generate a simplified theme focusing on colors and fonts"""
        start_time = time.time()
        
        # Track processing start if context manager available
        if self.context_manager:
            # Get upstream context from director
            upstream_context = self.get_upstream_context()
            
            # Prepare input data for tracking
            input_data = {
                "strawman": strawman.dict(),
                "director_metadata": director_metadata,
                "brand_guidelines": brand_guidelines,
                "upstream_context": upstream_context
            }
            
            self.start_processing(input_data, {"started_at": datetime.utcnow().isoformat()})
        
        try:
            logger.info(f"Starting simplified theme generation for session {session_id}")
            
            # Extract metadata from director
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
            
            # Build focused prompt
            prompt = self._build_focused_prompt(strawman, metadata)
            
            # Pre-populate the context values in the prompt
            prompt += f"\n\nIMPORTANT: Set formality_level to '{formality_level}' and complexity_allowance to '{complexity_allowance}' in your output."
            prompt += f"\n\nREMEMBER: You MUST call both tools (generate_color_palette and find_font_pairing) before creating your output!"
            
            # Run agent with tools
            import asyncio
            try:
                logger.info("Running AI agent with tools...")
                result = await asyncio.wait_for(
                    self.agent.run(prompt, deps=context),
                    timeout=30.0  # Reduced timeout for focused generation
                )
                
                generation_time = int((time.time() - start_time) * 1000)
                
                # Debug: Log what we got from the AI
                logger.info(f"AI agent completed in {generation_time}ms")
                logger.info(f"AI returned SimplifiedThemeOutput:")
                logger.info(f"  Theme name: {result.output.theme_name}")
                logger.info(f"  Colors type: {type(result.output.colors)}, content: {result.output.colors}")
                logger.info(f"  Typography type: {type(result.output.typography)}, content: {result.output.typography}")
                logger.info(f"  Formality: {result.output.formality_level}")
                logger.info(f"  Complexity: {result.output.complexity_allowance}")
                
                # Check if tools were called
                if hasattr(result, 'tool_calls'):
                    logger.info(f"  Tool calls made: {len(result.tool_calls) if result.tool_calls else 0}")
                    if result.tool_calls:
                        for tc in result.tool_calls:
                            logger.info(f"    - {tc}")
                else:
                    logger.info("  No tool_calls attribute found in result")
                
                # Check if we got empty data
                if not result.output.colors:
                    logger.warning("AI returned empty colors dictionary!")
                    # Use fallback if AI didn't return proper data
                    return self._create_simplified_fallback_theme(
                        strawman, formality_level, complexity_allowance, 
                        "AI returned empty colors"
                    )
                
                if not result.output.typography:
                    logger.warning("AI returned empty typography dictionary!")
                    # Use fallback if AI didn't return proper data
                    return self._create_simplified_fallback_theme(
                        strawman, formality_level, complexity_allowance,
                        "AI returned empty typography"
                    )
                
                # Update generation metadata
                result.output.generation_metadata.generation_method = "ai_generated"
                result.output.generation_metadata.generation_time_ms = generation_time
                result.output.generation_metadata.ai_confidence_score = 0.95
                
            except asyncio.TimeoutError:
                logger.error(f"Theme generation timed out for session {session_id}")
                fallback_theme = self._create_simplified_fallback_theme(
                    strawman, formality_level, complexity_allowance, "timeout"
                )
                
                # Track failure if context manager available
                if self.context_manager:
                    self.fail_processing("Theme generation timed out")
                
                return fallback_theme
            
            # Convert to ThemeDefinition
            theme = self._build_simplified_theme_definition(result.output, strawman)
            
            logger.info(f"Successfully generated simplified theme '{theme.name}' in {generation_time}ms")
            
            # Track completion if context manager available
            if self.context_manager:
                output_data = {
                    "theme_definition": theme.dict(),
                    "generation_method": result.output.generation_metadata.generation_method,
                    "generation_time_ms": generation_time,
                    "ai_confidence_score": result.output.generation_metadata.ai_confidence_score
                }
                
                self.complete_processing(output_data, {
                    "completed_at": datetime.utcnow().isoformat(),
                    "theme_name": theme.name
                })
                
                # Save context to storage
                await self.context_manager.save_to_storage()
            
            return theme
            
        except Exception as e:
            logger.error(f"Simplified theme generation failed: {e}")
            
            # Track failure if context manager available
            if self.context_manager:
                self.fail_processing(str(e))
            
            return self._create_simplified_fallback_theme(
                strawman, 
                metadata.get("formality_level", "medium"),
                metadata.get("complexity_allowance", "detailed"),
                str(e)
            )
    
    def _build_focused_prompt(
        self,
        strawman: PresentationStrawman,
        metadata: Dict[str, Any]
    ) -> str:
        """Build focused prompt for color and font generation"""
        prompt = f"""Create a color palette and font pairing for this presentation:

PRESENTATION CONTEXT:
- Title: {strawman.main_title}
- Theme: {strawman.overall_theme}
- Audience: {strawman.target_audience}
- Industry/Domain: {self._extract_industry(strawman)}
- Formality Level: {metadata.get('formality_level', 'medium')}
- Complexity: {metadata.get('complexity_allowance', 'detailed')}

REQUIREMENTS:
1. Use generate_color_palette to create a harmonious color scheme that:
   - Reflects the presentation theme and industry
   - Uses proper color theory (not just basic HSV shifts)
   - Ensures excellent contrast and accessibility
   - Includes semantic roles for each color

2. Use find_font_pairing to select fonts that:
   - Are optimized for presentations (consider projection/screen viewing)
   - Match the formality level
   - Create clear visual hierarchy
   - Avoid generic web fonts like Inter

Remember: This is for a PRESENTATION, not a website or document.
Focus on impact, readability, and professional appearance."""
        
        return prompt
    
    def _extract_industry(self, strawman: PresentationStrawman) -> str:
        """Extract industry/domain from strawman context"""
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
    
    def _build_simplified_theme_definition(
        self,
        output: SimplifiedThemeOutput,
        strawman: PresentationStrawman
    ) -> ThemeDefinition:
        """Convert simplified output to ThemeDefinition"""
        logger.info(f"Building ThemeDefinition from SimplifiedThemeOutput")
        logger.info(f"  Output colors: {output.colors}")
        logger.info(f"  Output typography: {output.typography}")
        
        # Build color tokens
        colors = {}
        for color_name, hex_value in output.colors.items():
            colors[color_name] = ColorToken(value=hex_value, type=TokenType.COLOR)
            logger.info(f"  Created ColorToken for {color_name}: {hex_value}")
        
        # Build typography tokens
        typography = {}
        for font_role, font_spec in output.typography.items():
            logger.info(f"  Processing font role {font_role}: {font_spec}")
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
            logger.info(f"  Created TypographyToken for {font_role}")
        
        # Create minimal spacing/sizing for compatibility
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
            description=f"Simplified theme focused on colors and typography",
            colors=colors,
            typography=typography,
            spacing=spacing,
            sizing=spacing  # Reuse spacing for sizing
        )
        
        logger.info(f"Created DesignTokens with {len(colors)} colors and {len(typography)} typography entries")
        
        theme_def = ThemeDefinition(
            name=output.theme_name,
            design_tokens=design_tokens,
            layout_templates={},  # Empty - layout handled elsewhere
            formality_level=output.formality_level,
            complexity_allowance=output.complexity_allowance,
            metadata={
                "generation_method": output.generation_metadata.generation_method,
                "generation_time_ms": output.generation_metadata.generation_time_ms,
                "ai_confidence_score": output.generation_metadata.ai_confidence_score,
                "color_rationale": output.color_rationale,
                "font_rationale": output.font_rationale
            }
        )
        
        logger.info(f"Created ThemeDefinition: {theme_def.name}")
        logger.info(f"  Has design_tokens: {hasattr(theme_def, 'design_tokens')}")
        logger.info(f"  Design tokens colors: {len(theme_def.design_tokens.colors) if hasattr(theme_def.design_tokens, 'colors') else 'N/A'}")
        
        return theme_def
    
    def _create_simplified_fallback_theme(
        self,
        strawman: PresentationStrawman,
        formality_level: str,
        complexity_allowance: str,
        fallback_reason: str
    ) -> ThemeDefinition:
        """Create a simplified fallback theme"""
        logger.warning(f"Using simplified fallback theme due to: {fallback_reason}")
        
        # Industry-aware fallback colors
        industry = self._extract_industry(strawman)
        colors = self._get_fallback_colors(industry)
        
        # Formality-aware fallback fonts
        typography = self._get_fallback_fonts(formality_level)
        
        # Create design tokens
        design_tokens = DesignTokens(
            name="Fallback Theme",
            description="Simplified fallback theme",
            colors=colors,
            typography=typography,
            spacing={
                "xs": DimensionToken(value=4, type=TokenType.DIMENSION, unit="px"),
                "sm": DimensionToken(value=8, type=TokenType.DIMENSION, unit="px"),
                "md": DimensionToken(value=16, type=TokenType.DIMENSION, unit="px"),
                "lg": DimensionToken(value=24, type=TokenType.DIMENSION, unit="px"),
                "xl": DimensionToken(value=32, type=TokenType.DIMENSION, unit="px")
            },
            sizing={
                "xs": DimensionToken(value=4, type=TokenType.DIMENSION, unit="px"),
                "sm": DimensionToken(value=8, type=TokenType.DIMENSION, unit="px"),
                "md": DimensionToken(value=16, type=TokenType.DIMENSION, unit="px"),
                "lg": DimensionToken(value=24, type=TokenType.DIMENSION, unit="px"),
                "xl": DimensionToken(value=32, type=TokenType.DIMENSION, unit="px")
            }
        )
        
        return ThemeDefinition(
            name="Simplified Fallback",
            design_tokens=design_tokens,
            layout_templates={},
            formality_level=formality_level,
            complexity_allowance=complexity_allowance,
            metadata={
                "generation_method": "fallback",
                "fallback_reason": fallback_reason,
                "generation_time_ms": 0,
                "ai_confidence_score": 0.0
            }
        )
    
    def _get_fallback_colors(self, industry: str) -> Dict[str, ColorToken]:
        """Get industry-appropriate fallback colors"""
        color_schemes = {
            "healthcare": {
                "primary": "#0077B6",  # Medical blue
                "secondary": "#00B4D8",
                "accent": "#90E0EF",
                "background": "#FFFFFF",
                "text": "#212529"
            },
            "finance": {
                "primary": "#003566",  # Financial navy
                "secondary": "#001D3D",
                "accent": "#FFD60A",
                "background": "#FFFFFF",
                "text": "#000814"
            },
            "technology": {
                "primary": "#7209B7",  # Tech purple
                "secondary": "#560BAD",
                "accent": "#B5179E",
                "background": "#FFFFFF",
                "text": "#240046"
            },
            "education": {
                "primary": "#2D6A4F",  # Educational green
                "secondary": "#40916C",
                "accent": "#52B788",
                "background": "#FFFFFF",
                "text": "#1B5E3F"
            },
            "general business": {
                "primary": "#0066CC",  # Professional blue
                "secondary": "#4D94FF",
                "accent": "#FF6B6B",
                "background": "#FFFFFF",
                "text": "#212121"
            }
        }
        
        scheme = color_schemes.get(industry, color_schemes["general business"])
        return {
            name: ColorToken(value=hex_value, type=TokenType.COLOR)
            for name, hex_value in scheme.items()
        }
    
    def _get_fallback_fonts(self, formality_level: str) -> Dict[str, TypographyToken]:
        """Get formality-appropriate fallback fonts"""
        font_schemes = {
            "high": {
                "heading": ("Helvetica Neue", 36, 700),
                "body": ("Georgia", 18, 400),
                "caption": ("Helvetica Neue", 14, 400)
            },
            "medium": {
                "heading": ("Roboto", 32, 700),
                "body": ("Open Sans", 16, 400),
                "caption": ("Roboto", 14, 400)
            },
            "casual": {
                "heading": ("Montserrat", 32, 600),
                "body": ("Lato", 16, 400),
                "caption": ("Lato", 14, 300)
            }
        }
        
        scheme = font_schemes.get(formality_level, font_schemes["medium"])
        typography = {}
        
        for role, (family, size, weight) in scheme.items():
            typography[role] = TypographyToken(
                fontFamily=TokenValue(value=family, type=TokenType.FONT_FAMILY),
                fontSize=TokenValue(value=size, type=TokenType.FONT_SIZE),
                fontWeight=TokenValue(value=weight, type=TokenType.FONT_WEIGHT),
                lineHeight=TokenValue(value=1.5 if role == "body" else 1.2, type=TokenType.LINE_HEIGHT)
            )
        
        return typography


# Maintain backward compatibility
ThemeAgent = SimplifiedThemeAgent