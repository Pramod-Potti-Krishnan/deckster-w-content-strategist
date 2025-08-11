"""
Design Tokens models following W3C Design Tokens Community Group format.

These models define the structure for design system tokens that provide
a single source of truth for design decisions across the presentation.
"""

from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TokenType(str, Enum):
    """W3C Design Token types"""
    COLOR = "color"
    DIMENSION = "dimension"
    FONT_FAMILY = "fontFamily"
    FONT_WEIGHT = "fontWeight"
    DURATION = "duration"
    CUBIC_BEZIER = "cubicBezier"
    NUMBER = "number"
    FONT_SIZE = "fontSize"
    LINE_HEIGHT = "lineHeight"
    LETTER_SPACING = "letterSpacing"
    BORDER_RADIUS = "borderRadius"
    BORDER_WIDTH = "borderWidth"
    SHADOW = "shadow"


class TokenValue(BaseModel):
    """Individual token value with metadata"""
    value: Union[str, int, float, Dict[str, Any]]
    type: TokenType
    description: Optional[str] = None
    extensions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom extensions for specific use cases"
    )


class ColorToken(TokenValue):
    """Color token with specific validation"""
    type: TokenType = TokenType.COLOR
    
    @field_validator('value')
    @classmethod
    def validate_color(cls, v):
        """Ensure color is in valid format"""
        if isinstance(v, str):
            # Basic validation for hex colors
            if v.startswith('#') and len(v) in [4, 7, 9]:
                return v
            # Could add RGB/HSL validation here
        raise ValueError(f"Invalid color format: {v}")


class DimensionToken(TokenValue):
    """Dimension token for spacing, sizing"""
    type: TokenType = TokenType.DIMENSION
    unit: str = Field(default="px", description="Unit of measurement")
    
    @field_validator('value')
    @classmethod
    def validate_dimension(cls, v):
        """Ensure dimension is numeric"""
        if isinstance(v, (int, float)) and v >= 0:
            return v
        raise ValueError(f"Invalid dimension: {v}")


class TypographyToken(BaseModel):
    """Composite typography token"""
    fontFamily: TokenValue
    fontSize: TokenValue
    fontWeight: Optional[TokenValue] = None
    lineHeight: Optional[TokenValue] = None
    letterSpacing: Optional[TokenValue] = None


class ShadowToken(TokenValue):
    """Shadow token for elevation effects"""
    type: TokenType = TokenType.SHADOW
    
    @field_validator('value')
    @classmethod
    def validate_shadow(cls, v):
        """Ensure shadow has required properties"""
        if isinstance(v, dict):
            required = ['x', 'y', 'blur', 'color']
            if all(key in v for key in required):
                return v
        raise ValueError(f"Invalid shadow format: {v}")


class TokenGroup(BaseModel):
    """Group of related tokens"""
    description: Optional[str] = None
    tokens: Dict[str, TokenValue]


class DesignTokens(BaseModel):
    """
    W3C Design Tokens format for theme definition.
    
    This provides a standardized way to define design system values
    that can be consumed by any rendering system.
    """
    version: str = Field(default="1.0", description="Design tokens format version")
    name: str = Field(description="Theme name")
    description: Optional[str] = Field(default=None, description="Theme description")
    
    # Core token groups
    colors: Dict[str, Union[ColorToken, Dict[str, ColorToken]]] = Field(
        description="Color palette tokens"
    )
    typography: Dict[str, Union[TypographyToken, TokenValue]] = Field(
        description="Typography system tokens"
    )
    spacing: Dict[str, DimensionToken] = Field(
        description="Spacing scale tokens"
    )
    sizing: Dict[str, DimensionToken] = Field(
        description="Size scale tokens"
    )
    
    # Optional token groups
    shadows: Optional[Dict[str, ShadowToken]] = None
    borders: Optional[Dict[str, TokenValue]] = None
    radii: Optional[Dict[str, DimensionToken]] = None
    motion: Optional[Dict[str, TokenValue]] = None
    
    # Custom extensions
    extensions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom extensions for Deckster-specific needs"
    )
    
    def to_css_variables(self) -> Dict[str, str]:
        """Convert tokens to CSS variables"""
        css_vars = {}
        
        # Colors
        for key, token in self.colors.items():
            if isinstance(token, dict):
                for subkey, subtoken in token.items():
                    css_vars[f"--color-{key}-{subkey}"] = subtoken.value
            else:
                css_vars[f"--color-{key}"] = token.value
        
        # Typography
        for key, token in self.typography.items():
            if isinstance(token, TypographyToken):
                css_vars[f"--font-family-{key}"] = token.fontFamily.value
                css_vars[f"--font-size-{key}"] = f"{token.fontSize.value}px"
                if token.fontWeight:
                    css_vars[f"--font-weight-{key}"] = str(token.fontWeight.value)
                if token.lineHeight:
                    css_vars[f"--line-height-{key}"] = str(token.lineHeight.value)
            else:
                # Handle individual typography tokens
                css_vars[f"--typography-{key}"] = str(token.value)
        
        # Spacing
        for key, token in self.spacing.items():
            css_vars[f"--spacing-{key}"] = f"{token.value}{token.unit}"
        
        # Sizing
        for key, token in self.sizing.items():
            css_vars[f"--size-{key}"] = f"{token.value}{token.unit}"
        
        return css_vars
    
    def to_export_format(self) -> Dict[str, Any]:
        """Export to W3C standard format"""
        export = {
            "$schema": "https://design-tokens.schema.org/draft-01/schema.json",
            "name": self.name,
            "version": self.version
        }
        
        if self.description:
            export["description"] = self.description
        
        # Add token groups
        export["tokens"] = {}
        
        # Colors
        export["tokens"]["color"] = {}
        for key, token in self.colors.items():
            if isinstance(token, dict):
                export["tokens"]["color"][key] = {}
                for subkey, subtoken in token.items():
                    export["tokens"]["color"][key][subkey] = {
                        "$value": subtoken.value,
                        "$type": subtoken.type
                    }
            else:
                export["tokens"]["color"][key] = {
                    "$value": token.value,
                    "$type": token.type
                }
        
        # Add other token groups similarly...
        
        return export


class GridZone(BaseModel):
    """Definition of a grid zone for layout templates"""
    name: str = Field(description="Zone identifier (e.g., 'header', 'content', 'footer')")
    leftInset: int = Field(description="X position in grid units")
    topInset: int = Field(description="Y position in grid units")
    width: int = Field(description="Width in grid units")
    height: int = Field(description="Height in grid units")
    
    # Optional properties
    minHeight: Optional[int] = None
    maxHeight: Optional[int] = None
    canExpand: bool = Field(default=False, description="Whether zone can expand")
    priority: int = Field(default=1, description="Priority for space allocation")
    
    @field_validator('leftInset', 'topInset', 'width', 'height')
    @classmethod
    def validate_positive(cls, v):
        """Ensure all dimensions are positive"""
        if v < 0:
            raise ValueError(f"Grid dimensions must be positive: {v}")
        return v
    
    @field_validator('leftInset', mode='after')
    @classmethod
    def validate_x_bounds(cls, v, info):
        """Ensure x position is within grid bounds"""
        if info.data.get('width') and v + info.data.get('width') > 160:
            raise ValueError(f"Zone exceeds grid width: {v} + {info.data.get('width')} > 160")
        return v
    
    @field_validator('topInset', mode='after')
    @classmethod
    def validate_y_bounds(cls, v, info):
        """Ensure y position is within grid bounds"""
        if info.data.get('height') and v + info.data.get('height') > 90:
            raise ValueError(f"Zone exceeds grid height: {v} + {info.data.get('height')} > 90")
        return v


class LayoutTemplate(BaseModel):
    """Template definition for a specific layout type"""
    name: str = Field(description="Template name (e.g., 'titleSlide', 'contentSlide')")
    description: Optional[str] = None
    zones: Dict[str, GridZone] = Field(description="Named zones within the template")
    defaultFlow: str = Field(
        default="vertical",
        description="Default content flow direction"
    )
    supportedContainers: List[str] = Field(
        default_factory=list,
        description="Container types this template supports"
    )
    
    # Enhanced fields for better layout guidance
    emphasis: str = Field(
        default="content",
        description="Primary emphasis area: title, content, visual, or balanced"
    )
    reading_flow: str = Field(
        default="F-pattern",
        description="Reading flow pattern: F-pattern, Z-pattern, linear, center-focused, visual-first"
    )
    
    def validate_zones_non_overlapping(self) -> bool:
        """Ensure zones don't overlap"""
        zones_list = list(self.zones.values())
        for i, zone1 in enumerate(zones_list):
            for zone2 in zones_list[i+1:]:
                # Check for overlap
                if (zone1.leftInset < zone2.leftInset + zone2.width and
                    zone1.leftInset + zone1.width > zone2.leftInset and
                    zone1.topInset < zone2.topInset + zone2.height and
                    zone1.topInset + zone1.height > zone2.topInset):
                    return False
        return True


class ThemeDefinition(BaseModel):
    """Complete theme definition including tokens and layout templates"""
    name: str
    design_tokens: DesignTokens
    layout_templates: Dict[str, LayoutTemplate]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Enhanced fields for comprehensive design system
    mood_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords extracted from theme analysis"
    )
    visual_guidelines: Dict[str, Any] = Field(
        default_factory=dict,
        description="Guidelines for visual content generation"
    )
    formality_level: str = Field(
        default="medium",
        description="Formality level: high, medium, or casual"
    )
    complexity_allowance: str = Field(
        default="executive",
        description="Complexity level: executive, detailed, or simplified"
    )
    
    # Strawman context (for reference)
    strawman_context: Optional[Dict[str, Any]] = None
    
    def get_template_for_slide_type(self, slide_type: str) -> Optional[LayoutTemplate]:
        """Get appropriate template for a slide type"""
        # Direct match
        if slide_type in self.layout_templates:
            return self.layout_templates[slide_type]
        
        # Try to find a suitable fallback
        type_mapping = {
            "title_slide": "titleSlide",
            "section_header": "sectionSlide",
            "content_heavy": "contentSlide",
            "data_driven": "dataSlide",
            "visual_heavy": "visualSlide"
        }
        
        mapped_type = type_mapping.get(slide_type)
        if mapped_type and mapped_type in self.layout_templates:
            return self.layout_templates[mapped_type]
        
        # Default fallback
        return self.layout_templates.get("contentSlide")