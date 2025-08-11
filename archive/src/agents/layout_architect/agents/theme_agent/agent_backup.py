"""
Theme Agent - Brand & Style Director (Enhanced).

This enhanced agent analyzes the entire presentation strawman to create
a comprehensive design system that serves as the "brand book" for the 
entire presentation, which the Content Agent uses as creative guidelines.
"""

import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel

from src.models.agents import PresentationStrawman, Slide
from src.utils.logger import setup_logger
from ...utils.model_utils import create_model_with_fallback
from ...model_types.design_tokens import (
    DesignTokens, ThemeDefinition, ColorToken, TypographyToken,
    DimensionToken, LayoutTemplate, GridZone, TokenValue, TokenType
)
from .tools import (
    analyze_mood_and_keywords_tool, generate_color_palette_tool, 
    find_font_pairing_tool, design_layout_templates_tool,
    MoodAnalysisInput, ColorPaletteInput, FontPairingInput, LayoutTemplatesInput
)

logger = setup_logger(__name__)


class ThemeContext(BaseModel):
    """Context for theme generation"""
    strawman: PresentationStrawman
    session_id: str
    brand_guidelines: Optional[Dict[str, Any]] = None


class VisualGuidelines(BaseModel):
    """Visual guidelines for all generated content"""
    iconography_style: str = Field(
        description="Style for icons: line-art, solid, duo-tone, 3d"
    )
    photography_style: str = Field(
        description="Style for photos: corporate-clean, abstract-tech, human-centric, editorial"
    )
    data_viz_style: str = Field(
        description="Style for data visualizations: minimalist, bold-headers, gradient-fills, playful"
    )
    illustration_approach: str = Field(
        description="Approach for illustrations: geometric, organic, hand-drawn, isometric"
    )
    texture_usage: str = Field(
        description="Use of textures: none, subtle, moderate, prominent"
    )
    visual_metaphors: List[str] = Field(
        default_factory=list,
        description="Preferred visual metaphors aligned with theme"
    )


class EnhancedThemeOutput(BaseModel):
    """Enhanced structured output from Theme Agent"""
    theme_name: str = Field(description="Descriptive name for the theme")
    mood_keywords: List[str] = Field(
        description="Keywords extracted from overall_theme and design_suggestions"
    )
    
    # Design tokens
    colors: Dict[str, str] = Field(description="Complete color palette with hex values")
    typography: Dict[str, Dict[str, Any]] = Field(description="Font specifications")
    spacing: Dict[str, int] = Field(description="Spacing scale")
    sizing: Dict[str, int] = Field(description="Sizing scale")
    shadows: Optional[Dict[str, str]] = Field(default=None, description="Shadow definitions")
    borders: Optional[Dict[str, str]] = Field(default=None, description="Border styles")
    
    # Visual guidelines
    visual_guidelines: VisualGuidelines = Field(
        description="Guidelines for all visual content generation"
    )
    
    # Layout templates
    layout_templates: Dict[str, Dict[str, Any]] = Field(
        description="Layout templates for each slide type found in strawman"
    )
    
    # Metadata
    formality_level: str = Field(
        description="Formality level: high, medium, casual",
        default="medium"
    )
    complexity_allowance: str = Field(
        description="Complexity level: executive, detailed, simplified",
        default="executive"
    )
    theme_rationale: str = Field(
        description="Explanation of design decisions",
        default="Professional theme for effective communication"
    )


class ThemeAgent:
    """
    Enhanced Theme Agent - Creates comprehensive design systems.
    
    Analyzes the entire strawman to create a design system that:
    - Captures the mood and intent from metadata
    - Creates accessible, harmonious visual systems
    - Provides layout templates for all slide types
    - Establishes visual guidelines for content generation
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite-preview-06-17"):
        """Initialize Theme Agent with AI model and enhanced tools"""
        self.model = create_model_with_fallback(model_name)
        
        # Create agent with comprehensive tools
        self.agent = Agent(
            self.model,
            output_type=EnhancedThemeOutput,
            deps_type=ThemeContext,
            tools=[
                analyze_mood_and_keywords_tool,
                generate_color_palette_tool,
                find_font_pairing_tool,
                design_layout_templates_tool
            ],
            system_prompt=self._get_system_prompt(),
            retries=2
        )
    
    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt for enhanced theme generation"""
        return """You are an Enhanced Brand & Style Director, responsible for creating a 
comprehensive design system that serves as the "brand book" for an entire presentation.

Your mission is to analyze the presentation strawman holistically and create a ThemeDefinition 
that will guide all subsequent content generation.

CRITICAL ANALYSIS SEQUENCE:
1. Extract mood and keywords from overall_theme and design_suggestions using analyze_mood_and_keywords
2. Generate a color palette that embodies these moods using generate_color_palette
3. Select typography that reinforces the tone using find_font_pairing
4. Design layout templates for EVERY slide type in the strawman using design_layout_templates

KEY INPUTS TO ANALYZE:
- overall_theme: The MOST IMPORTANT input - this drives the entire mood
- design_suggestions: Specific style hints to incorporate
- target_audience: Influences formality and complexity levels
- main_title: Helps understand the topic and context
- slides array: Extract ALL unique slide_type values for templates

DESIGN PRINCIPLES:
- MOOD FIRST: The overall_theme is your primary creative driver
- ACCESSIBILITY: All colors must meet WCAG AA standards
- CONSISTENCY: Create a unified visual language
- FLEXIBILITY: Design must work for all content densities
- AUDIENCE AWARE: Match formality to the target audience

VISUAL GUIDELINES CREATION:
Based on the mood keywords, establish:
- Iconography style (matches mood: formal→line-art, playful→duo-tone)
- Photography style (matches audience: executives→corporate-clean)
- Data viz style (matches theme: data-driven→minimalist)
- Illustration approach (matches content: technical→geometric)

FORMALITY MAPPING:
- "executives", "investors", "board" → high formality
- "team", "department", "colleagues" → medium formality
- "general public", "students", "community" → casual formality

COMPLEXITY MAPPING:
- "executives", "investors" → executive (high-level, outcome-focused)
- "technical", "engineering", "research" → detailed (methodology-included)
- "general public", "students" → simplified (clear explanations)

Your output must be a complete ThemeDefinition that Content Agent can use as 
creative constraints and inspiration for every slide."""
    
    async def generate_theme(
        self,
        strawman: PresentationStrawman,
        session_id: str,
        brand_guidelines: Optional[Dict[str, Any]] = None
    ) -> ThemeDefinition:
        """Generate a comprehensive theme for the presentation"""
        try:
            logger.info(f"Starting enhanced theme generation for session {session_id}")
            logger.info(f"Analyzing strawman with {len(strawman.slides)} slides")
            
            # Extract all unique slide types
            slide_types = list(set(slide.slide_type for slide in strawman.slides))
            logger.info(f"Found slide types: {slide_types}")
            
            # Create context
            context = ThemeContext(
                strawman=strawman,
                session_id=session_id,
                brand_guidelines=brand_guidelines
            )
            
            # Build comprehensive prompt
            prompt = self._build_enhanced_theme_prompt(strawman, slide_types, brand_guidelines)
            
            # Run agent with tools
            import asyncio
            try:
                result = await asyncio.wait_for(
                    self.agent.run(prompt, deps=context),
                    timeout=45.0  # Increased timeout for comprehensive analysis
                )
            except asyncio.TimeoutError:
                logger.error(f"Theme generation timed out for session {session_id}")
                return self._create_comprehensive_fallback_theme(strawman, slide_types)
            
            # Convert to ThemeDefinition
            theme = self._build_enhanced_theme_definition(result.output, strawman)
            
            logger.info(f"Successfully generated enhanced theme '{theme.name}' with {len(theme.mood_keywords)} mood keywords")
            return theme
            
        except Exception as e:
            logger.error(f"Enhanced theme generation failed: {e}")
            return self._create_comprehensive_fallback_theme(strawman, slide_types)
    
    def _build_enhanced_theme_prompt(
        self,
        strawman: PresentationStrawman,
        slide_types: List[str],
        brand_guidelines: Optional[Dict[str, Any]]
    ) -> str:
        """Build detailed prompt for enhanced theme generation"""
        prompt = f"""Create a comprehensive design system for this presentation:

PRESENTATION METADATA:
- Title: {strawman.main_title}
- Overall Theme: {strawman.overall_theme} [PRIMARY CREATIVE DRIVER]
- Design Suggestions: {strawman.design_suggestions}
- Target Audience: {strawman.target_audience}
- Duration: {strawman.presentation_duration} minutes
- Total Slides: {len(strawman.slides)}

SLIDE TYPES REQUIRING TEMPLATES:
{', '.join(slide_types)}

ANALYSIS REQUIREMENTS:
1. First, use analyze_mood_and_keywords to extract actionable keywords from:
   - Overall theme: "{strawman.overall_theme}"
   - Design suggestions: "{strawman.design_suggestions}"
   
2. Use generate_color_palette with the extracted mood keywords to create a 
   harmonious color system that embodies the presentation's mood.
   
3. Use find_font_pairing considering the target audience ("{strawman.target_audience}")
   and the formality level implied by the mood keywords.
   
4. Use design_layout_templates to create templates for ALL these slide types:
   {', '.join(slide_types)}
   
5. Based on the mood keywords, define visual guidelines that will ensure
   all generated content aligns with the theme.

REMEMBER: The overall_theme "{strawman.overall_theme}" is your primary creative driver.
Every design decision should support and enhance this theme."""

        if brand_guidelines:
            prompt += f"\n\nBrand Guidelines to incorporate: {brand_guidelines}"
        
        return prompt
    
    def _build_enhanced_theme_definition(
        self,
        output: EnhancedThemeOutput,
        strawman: PresentationStrawman
    ) -> ThemeDefinition:
        """Convert enhanced agent output to comprehensive ThemeDefinition"""
        # Build color tokens
        colors = {}
        for color_name, hex_value in output.colors.items():
            colors[color_name] = ColorToken(value=hex_value, type=TokenType.COLOR)
        
        # Build typography tokens
        typography = {}
        for font_role, font_spec in output.typography.items():
            typography[font_role] = TypographyToken(
                fontFamily=TokenValue(
                    value=font_spec.get("family", "Inter"),
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
                ),
                letterSpacing=TokenValue(
                    value=font_spec.get("letterSpacing", 0),
                    type=TokenType.DIMENSION
                ) if "letterSpacing" in font_spec else None
            )
        
        # Build spacing tokens
        spacing = {}
        for size_name, size_value in output.spacing.items():
            spacing[size_name] = DimensionToken(value=size_value, type=TokenType.DIMENSION)
        
        # Build sizing tokens
        sizing = {}
        for size_name, size_value in output.sizing.items():
            sizing[size_name] = DimensionToken(value=size_value, type=TokenType.DIMENSION)
        
        # Build shadows if provided
        shadows = None
        if output.shadows:
            shadows = {}
            for shadow_name, shadow_value in output.shadows.items():
                shadows[shadow_name] = shadow_value  # Keep as string for now
        
        # Build borders if provided
        borders = None
        if output.borders:
            borders = {}
            for border_name, border_value in output.borders.items():
                borders[border_name] = border_value  # Keep as string for now
        
        # Create DesignTokens
        design_tokens = DesignTokens(
            name=output.theme_name,
            description=output.theme_rationale,
            colors=colors,
            typography=typography,
            spacing=spacing,
            sizing=sizing,
            shadows=shadows,
            borders=borders
        )
        
        # Build layout templates
        layout_templates = {}
        for template_name, template_data in output.layout_templates.items():
            zones = {}
            for zone_name, zone_data in template_data.get("zones", {}).items():
                zones[zone_name] = GridZone(
                    name=zone_name,
                    leftInset=zone_data["leftInset"],
                    topInset=zone_data["topInset"],
                    width=zone_data["width"],
                    height=zone_data["height"]
                )
            
            layout_templates[template_name] = LayoutTemplate(
                name=template_name,
                zones=zones,
                description=template_data.get("description", ""),
                emphasis=template_data.get("emphasis", "content"),
                reading_flow=template_data.get("reading_flow", "F-pattern")
            )
        
        # Create comprehensive ThemeDefinition
        return ThemeDefinition(
            name=output.theme_name,
            mood_keywords=output.mood_keywords,
            design_tokens=design_tokens,
            visual_guidelines=output.visual_guidelines.model_dump(),
            layout_templates=layout_templates,
            formality_level=output.formality_level,
            complexity_allowance=output.complexity_allowance,
            metadata={
                "rationale": output.theme_rationale,
                "created_for": strawman.main_title,
                "session_id": session_id
            },
            strawman_context={
                "audience": strawman.target_audience,
                "overall_theme": strawman.overall_theme,
                "design_suggestions": strawman.design_suggestions
            }
        )
    
    def _create_comprehensive_fallback_theme(
        self,
        strawman: PresentationStrawman,
        slide_types: List[str]
    ) -> ThemeDefinition:
        """Create comprehensive fallback theme"""
        # Analyze theme manually
        theme_lower = strawman.overall_theme.lower()
        
        # Extract basic mood keywords
        mood_keywords = []
        if "professional" in theme_lower:
            mood_keywords.extend(["professional", "clean", "trustworthy"])
        if "data" in theme_lower:
            mood_keywords.extend(["data-driven", "analytical", "precise"])
        if "persuasive" in theme_lower:
            mood_keywords.extend(["persuasive", "compelling", "confident"])
        if "modern" in theme_lower:
            mood_keywords.extend(["modern", "contemporary", "forward-thinking"])
        
        # Default mood keywords if none found
        if not mood_keywords:
            mood_keywords = ["professional", "clear", "effective"]
        
        # Create default color tokens
        colors = {
            "primary": ColorToken(value="#0066cc", type=TokenType.COLOR),
            "secondary": ColorToken(value="#4d94ff", type=TokenType.COLOR),
            "accent": ColorToken(value="#ff6b6b", type=TokenType.COLOR),
            "background": ColorToken(value="#ffffff", type=TokenType.COLOR),
            "surface": ColorToken(value="#f8f9fa", type=TokenType.COLOR),
            "text": ColorToken(value="#212121", type=TokenType.COLOR),
            "text_secondary": ColorToken(value="#757575", type=TokenType.COLOR),
            "success": ColorToken(value="#28a745", type=TokenType.COLOR),
            "warning": ColorToken(value="#ffc107", type=TokenType.COLOR),
            "error": ColorToken(value="#dc3545", type=TokenType.COLOR)
        }
        
        # Create default typography
        typography = {
            "heading": TypographyToken(
                fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                fontSize=TokenValue(value=32, type=TokenType.FONT_SIZE),
                fontWeight=TokenValue(value=700, type=TokenType.FONT_WEIGHT),
                lineHeight=TokenValue(value=1.2, type=TokenType.LINE_HEIGHT),
                letterSpacing=TokenValue(value=-0.02, type=TokenType.DIMENSION)
            ),
            "body": TypographyToken(
                fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                fontSize=TokenValue(value=16, type=TokenType.FONT_SIZE),
                fontWeight=TokenValue(value=400, type=TokenType.FONT_WEIGHT),
                lineHeight=TokenValue(value=1.6, type=TokenType.LINE_HEIGHT)
            ),
            "caption": TypographyToken(
                fontFamily=TokenValue(value="Inter", type=TokenType.FONT_FAMILY),
                fontSize=TokenValue(value=14, type=TokenType.FONT_SIZE),
                fontWeight=TokenValue(value=400, type=TokenType.FONT_WEIGHT),
                lineHeight=TokenValue(value=1.4, type=TokenType.LINE_HEIGHT)
            ),
            "data": TypographyToken(
                fontFamily=TokenValue(value="Roboto Mono", type=TokenType.FONT_FAMILY),
                fontSize=TokenValue(value=14, type=TokenType.FONT_SIZE),
                fontWeight=TokenValue(value=500, type=TokenType.FONT_WEIGHT)
            )
        }
        
        # Create spacing and sizing
        spacing = {
            "xs": DimensionToken(value=4, type=TokenType.DIMENSION),
            "sm": DimensionToken(value=8, type=TokenType.DIMENSION),
            "md": DimensionToken(value=16, type=TokenType.DIMENSION),
            "lg": DimensionToken(value=24, type=TokenType.DIMENSION),
            "xl": DimensionToken(value=32, type=TokenType.DIMENSION),
            "xxl": DimensionToken(value=48, type=TokenType.DIMENSION)
        }
        
        sizing = spacing.copy()  # Use same scale for sizing
        
        # Create visual guidelines
        visual_guidelines = {
            "iconography_style": "line-art",
            "photography_style": "corporate-clean",
            "data_viz_style": "minimalist",
            "illustration_approach": "geometric",
            "texture_usage": "subtle",
            "visual_metaphors": ["growth", "connection", "innovation"]
        }
        
        # Create design tokens
        design_tokens = DesignTokens(
            name="Professional Default",
            description="Clean, professional theme for effective communication",
            colors=colors,
            typography=typography,
            spacing=spacing,
            sizing=sizing
        )
        
        # Create layout templates for all slide types
        layout_templates = {}
        for slide_type in slide_types:
            layout_templates[slide_type] = self._create_fallback_layout_template(slide_type)
        
        # Determine formality and complexity
        audience_lower = strawman.target_audience.lower()
        formality_level = "high" if any(
            word in audience_lower for word in ["executive", "investor", "board"]
        ) else "medium"
        
        complexity_allowance = "executive" if any(
            word in audience_lower for word in ["executive", "investor"]
        ) else "detailed"
        
        return ThemeDefinition(
            name="Professional Default",
            mood_keywords=mood_keywords,
            design_tokens=design_tokens,
            visual_guidelines=visual_guidelines,
            layout_templates=layout_templates,
            formality_level=formality_level,
            complexity_allowance=complexity_allowance,
            metadata={"fallback": True},
            strawman_context={
                "audience": strawman.target_audience,
                "overall_theme": strawman.overall_theme,
                "design_suggestions": strawman.design_suggestions
            }
        )
    
    def _create_fallback_layout_template(self, slide_type: str) -> LayoutTemplate:
        """Create a fallback layout template for any slide type"""
        # Base grid dimensions
        margin = 8
        grid_width = 160
        grid_height = 90
        work_width = grid_width - (2 * margin)
        work_height = grid_height - (2 * margin)
        
        zones = {}
        
        # Common patterns based on slide type keywords
        if "title" in slide_type.lower():
            zones["title"] = GridZone(
                name="title",
                leftInset=20,
                topInset=35,
                width=120,
                height=20
            )
            zones["subtitle"] = GridZone(
                name="subtitle",
                leftInset=20,
                topInset=55,
                width=120,
                height=10
            )
            emphasis = "title"
            
        elif "data" in slide_type.lower() or "chart" in slide_type.lower():
            zones["title"] = GridZone(
                name="title",
                leftInset=margin,
                topInset=margin,
                width=work_width,
                height=10
            )
            zones["visualization"] = GridZone(
                name="visualization",
                leftInset=margin,
                topInset=22,
                width=work_width,
                height=50
            )
            zones["insights"] = GridZone(
                name="insights",
                leftInset=margin,
                topInset=76,
                width=work_width,
                height=6
            )
            emphasis = "visualization"
            
        elif "visual" in slide_type.lower() or "image" in slide_type.lower():
            zones["visual"] = GridZone(
                name="visual",
                leftInset=margin,
                topInset=margin,
                width=work_width,
                height=int(work_height * 0.7)
            )
            zones["caption"] = GridZone(
                name="caption",
                leftInset=margin,
                topInset=margin + int(work_height * 0.7) + 4,
                width=work_width,
                height=work_height - int(work_height * 0.7) - 4
            )
            emphasis = "visual"
            
        else:
            # Default content layout
            zones["title"] = GridZone(
                name="title",
                leftInset=margin,
                topInset=margin,
                width=work_width,
                height=12
            )
            zones["content"] = GridZone(
                name="content",
                leftInset=margin,
                topInset=24,
                width=work_width,
                height=58
            )
            zones["footer"] = GridZone(
                name="footer",
                leftInset=margin,
                topInset=84,
                width=work_width,
                height=6
            )
            emphasis = "content"
        
        return LayoutTemplate(
            name=slide_type,
            zones=zones,
            description=f"Layout for {slide_type} slides",
            emphasis=emphasis,
            reading_flow="F-pattern"
        )
    
    async def generate_theme_legacy(
        self,
        slide_type: str = None,
        user_context: Optional[Dict[str, Any]] = None,
        content_hints: Optional[Dict[str, Any]] = None
    ) -> ThemeDefinition:
        """Legacy method for backward compatibility"""
        # Create a mock strawman from the provided data
        if not hasattr(self, '_default_strawman'):
            self._default_strawman = PresentationStrawman(
                main_title=content_hints.get("title", "Presentation") if content_hints else "Presentation",
                overall_theme=content_hints.get("overall_theme", "Professional") if content_hints else "Professional",
                design_suggestions=content_hints.get("design_suggestions", "") if content_hints else "",
                target_audience=user_context.get("audience", "General") if user_context else "General",
                presentation_duration=15,
                slides=[]
            )
        
        # If we have a specific slide type, add it to ensure template generation
        if slide_type and not any(s.slide_type == slide_type for s in self._default_strawman.slides):
            from src.models.agents import Slide
            mock_slide = Slide(
                slide_id=f"mock_{slide_type}",
                slide_type=slide_type,
                title="Mock Slide",
                key_points=[]
            )
            self._default_strawman.slides.append(mock_slide)
        
        # Use the new comprehensive method
        return await self.generate_theme(
            strawman=self._default_strawman,
            session_id="legacy_session",
            brand_guidelines=user_context
        )
    
    def _get_default_theme(self, strawman: PresentationStrawman, session_id: str) -> ThemeDefinition:
        """Backward compatibility wrapper"""
        slide_types = list(set(slide.slide_type for slide in strawman.slides))
        return self._create_comprehensive_fallback_theme(strawman, slide_types)