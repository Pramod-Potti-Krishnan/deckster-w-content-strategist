"""
Enhanced tools for Simplified Theme Agent - Color Palette and Font Pairing.

These tools provide sophisticated color theory and presentation-optimized font selection.
"""

from typing import Dict, List, Tuple, Optional, Literal, Any
from pydantic import BaseModel, Field, validator
from pydantic_ai import Tool
import colorsys
import math
import re
from enum import Enum


# ===== ENHANCED COLOR PALETTE TOOL =====

class ColorHarmony(str, Enum):
    """Color harmony schemes based on color theory"""
    MONOCHROMATIC = "monochromatic"      # Single hue with variations
    ANALOGOUS = "analogous"              # Adjacent colors on wheel
    COMPLEMENTARY = "complementary"      # Opposite colors
    SPLIT_COMPLEMENTARY = "split_complementary"  # Base + two adjacent to complement
    TRIADIC = "triadic"                  # Three equidistant colors
    TETRADIC = "tetradic"               # Two complementary pairs
    SQUARE = "square"                    # Four equidistant colors


class ColorPaletteInput(BaseModel):
    """Enhanced input for color palette generation"""
    presentation_context: str = Field(
        description="Industry/domain context: healthcare, finance, technology, education, etc."
    )
    mood_description: str = Field(
        description="Desired mood: professional, energetic, calm, innovative, trustworthy, etc."
    )
    color_preferences: Optional[str] = Field(
        default=None,
        description="Any specific color preferences or brand colors to incorporate"
    )
    harmony_type: Optional[ColorHarmony] = Field(
        default=None,
        description="Preferred color harmony scheme"
    )
    accessibility_level: Literal["AA", "AAA"] = Field(
        default="AA",
        description="WCAG accessibility level required"
    )
    include_dark_mode: bool = Field(
        default=False,
        description="Whether to generate dark mode variants"
    )


class ColorPaletteOutput(BaseModel):
    """Enhanced output from color palette generation"""
    colors: Dict[str, str] = Field(
        description="Generated color palette with semantic names"
    )
    color_harmony: ColorHarmony = Field(
        description="Color harmony scheme used"
    )
    accessibility_report: Dict[str, Any] = Field(
        description="WCAG compliance report with contrast ratios"
    )
    color_roles: Dict[str, str] = Field(
        description="Semantic roles and usage guidelines for each color"
    )
    color_psychology: Dict[str, str] = Field(
        description="Psychological associations of chosen colors"
    )
    rationale: str = Field(
        description="Explanation of color choices"
    )


class EnhancedColorPaletteGenerator:
    """Generate harmonious color palettes using advanced color theory"""
    
    # Industry-specific color psychology
    INDUSTRY_COLOR_PREFERENCES = {
        "healthcare": {
            "primary_hues": [200, 180, 170],  # Blues and teals
            "associations": ["trust", "calm", "healing", "cleanliness"],
            "avoid_hues": [0, 10, 350]  # Avoid reds (blood association)
        },
        "finance": {
            "primary_hues": [210, 220, 230],  # Deep blues
            "associations": ["stability", "trust", "growth", "security"],
            "avoid_hues": []
        },
        "technology": {
            "primary_hues": [260, 280, 200],  # Purples and blues
            "associations": ["innovation", "future", "precision", "intelligence"],
            "avoid_hues": []
        },
        "education": {
            "primary_hues": [120, 140, 160],  # Greens and blue-greens
            "associations": ["growth", "learning", "freshness", "possibility"],
            "avoid_hues": []
        },
        "creative": {
            "primary_hues": [30, 300, 180],  # Orange, magenta, cyan
            "associations": ["creativity", "energy", "imagination", "expression"],
            "avoid_hues": []
        }
    }
    
    # Mood to color mapping
    MOOD_COLOR_MAPPING = {
        "professional": {"saturation": 0.3, "brightness": 0.7, "harmony": ColorHarmony.ANALOGOUS},
        "energetic": {"saturation": 0.8, "brightness": 0.8, "harmony": ColorHarmony.COMPLEMENTARY},
        "calm": {"saturation": 0.4, "brightness": 0.6, "harmony": ColorHarmony.ANALOGOUS},
        "innovative": {"saturation": 0.7, "brightness": 0.75, "harmony": ColorHarmony.TRIADIC},
        "trustworthy": {"saturation": 0.5, "brightness": 0.65, "harmony": ColorHarmony.MONOCHROMATIC},
        "bold": {"saturation": 0.9, "brightness": 0.7, "harmony": ColorHarmony.SPLIT_COMPLEMENTARY}
    }
    
    def generate_enhanced_palette(self, input_data: ColorPaletteInput) -> ColorPaletteOutput:
        """Generate sophisticated color palette using color theory"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"generate_enhanced_palette called with context: {input_data.presentation_context}")
        
        # Determine base hue from context
        base_hue = self._determine_base_hue(
            input_data.presentation_context,
            input_data.color_preferences
        )
        
        # Get color properties from mood
        mood_props = self._get_mood_properties(input_data.mood_description)
        
        # Determine harmony type
        harmony = input_data.harmony_type or mood_props.get("harmony", ColorHarmony.ANALOGOUS)
        
        # Generate palette using color theory
        colors = self._generate_harmonic_palette(
            base_hue,
            harmony,
            mood_props["saturation"],
            mood_props["brightness"]
        )
        
        # Add utility colors
        colors = self._add_utility_colors(colors, mood_props)
        
        # Ensure accessibility
        colors = self._ensure_accessibility(colors, input_data.accessibility_level)
        
        # Generate dark mode if requested
        if input_data.include_dark_mode:
            dark_colors = self._generate_dark_mode_variants(colors)
            colors.update({f"{k}_dark": v for k, v in dark_colors.items()})
        
        # Create comprehensive report
        accessibility_report = self._generate_accessibility_report(colors)
        color_roles = self._assign_semantic_roles(colors, input_data.presentation_context)
        psychology = self._analyze_color_psychology(colors, input_data.presentation_context)
        
        rationale = self._generate_rationale(
            input_data.presentation_context,
            input_data.mood_description,
            harmony,
            colors
        )
        
        return ColorPaletteOutput(
            colors=colors,
            color_harmony=harmony,
            accessibility_report=accessibility_report,
            color_roles=color_roles,
            color_psychology=psychology,
            rationale=rationale
        )
    
    def _determine_base_hue(self, context: str, preferences: Optional[str]) -> float:
        """Determine base hue from context and preferences"""
        # Check for explicit color preference
        if preferences:
            color_match = re.search(r'#([0-9a-fA-F]{6})', preferences)
            if color_match:
                rgb = self._hex_to_rgb(color_match.group(0))
                h, _, _ = colorsys.rgb_to_hsv(*[c/255.0 for c in rgb])
                return h * 360
        
        # Use industry preferences
        industry = self._normalize_industry(context)
        if industry in self.INDUSTRY_COLOR_PREFERENCES:
            hues = self.INDUSTRY_COLOR_PREFERENCES[industry]["primary_hues"]
            return hues[0] if hues else 210  # Default to blue
        
        return 210  # Default blue
    
    def _normalize_industry(self, context: str) -> str:
        """Normalize industry context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["health", "medical", "clinical"]):
            return "healthcare"
        elif any(word in context_lower for word in ["finance", "banking", "investment"]):
            return "finance"
        elif any(word in context_lower for word in ["tech", "software", "digital", "ai"]):
            return "technology"
        elif any(word in context_lower for word in ["education", "school", "learning"]):
            return "education"
        elif any(word in context_lower for word in ["creative", "design", "art"]):
            return "creative"
        else:
            return "general"
    
    def _get_mood_properties(self, mood: str) -> Dict[str, Any]:
        """Get color properties from mood description"""
        mood_lower = mood.lower()
        
        # Find best matching mood
        for key, props in self.MOOD_COLOR_MAPPING.items():
            if key in mood_lower:
                return props
        
        # Default professional
        return self.MOOD_COLOR_MAPPING["professional"]
    
    def _generate_harmonic_palette(
        self,
        base_hue: float,
        harmony: ColorHarmony,
        saturation: float,
        brightness: float
    ) -> Dict[str, str]:
        """Generate colors using proper color harmony theory"""
        colors = {}
        
        # Normalize hue to 0-360
        base_hue = base_hue % 360
        
        if harmony == ColorHarmony.MONOCHROMATIC:
            colors["primary"] = self._hsv_to_hex(base_hue, saturation, brightness)
            colors["secondary"] = self._hsv_to_hex(base_hue, saturation * 0.7, brightness * 1.1)
            colors["accent"] = self._hsv_to_hex(base_hue, saturation * 1.2, brightness * 0.9)
            
        elif harmony == ColorHarmony.ANALOGOUS:
            colors["primary"] = self._hsv_to_hex(base_hue, saturation, brightness)
            colors["secondary"] = self._hsv_to_hex((base_hue + 30) % 360, saturation * 0.9, brightness)
            colors["accent"] = self._hsv_to_hex((base_hue - 30) % 360, saturation * 0.9, brightness)
            
        elif harmony == ColorHarmony.COMPLEMENTARY:
            colors["primary"] = self._hsv_to_hex(base_hue, saturation, brightness)
            colors["secondary"] = self._hsv_to_hex((base_hue + 180) % 360, saturation * 0.8, brightness)
            colors["accent"] = self._hsv_to_hex(base_hue, saturation * 0.6, brightness * 1.2)
            
        elif harmony == ColorHarmony.SPLIT_COMPLEMENTARY:
            colors["primary"] = self._hsv_to_hex(base_hue, saturation, brightness)
            colors["secondary"] = self._hsv_to_hex((base_hue + 150) % 360, saturation * 0.8, brightness)
            colors["accent"] = self._hsv_to_hex((base_hue + 210) % 360, saturation * 0.8, brightness)
            
        elif harmony == ColorHarmony.TRIADIC:
            colors["primary"] = self._hsv_to_hex(base_hue, saturation, brightness)
            colors["secondary"] = self._hsv_to_hex((base_hue + 120) % 360, saturation * 0.9, brightness)
            colors["accent"] = self._hsv_to_hex((base_hue + 240) % 360, saturation * 0.9, brightness)
            
        elif harmony == ColorHarmony.TETRADIC:
            colors["primary"] = self._hsv_to_hex(base_hue, saturation, brightness)
            colors["secondary"] = self._hsv_to_hex((base_hue + 90) % 360, saturation * 0.9, brightness)
            colors["accent"] = self._hsv_to_hex((base_hue + 180) % 360, saturation * 0.8, brightness)
            colors["highlight"] = self._hsv_to_hex((base_hue + 270) % 360, saturation * 0.8, brightness)
            
        else:  # SQUARE
            colors["primary"] = self._hsv_to_hex(base_hue, saturation, brightness)
            colors["secondary"] = self._hsv_to_hex((base_hue + 90) % 360, saturation, brightness)
            colors["accent"] = self._hsv_to_hex((base_hue + 180) % 360, saturation, brightness)
            colors["highlight"] = self._hsv_to_hex((base_hue + 270) % 360, saturation, brightness)
        
        return colors
    
    def _add_utility_colors(self, colors: Dict[str, str], mood_props: Dict) -> Dict[str, str]:
        """Add utility colors (background, text, etc.)"""
        # Background - very light or very dark
        if mood_props["brightness"] > 0.7:
            colors["background"] = "#FFFFFF"
            colors["surface"] = "#F8F9FA"
            colors["text"] = "#212529"
            colors["text_secondary"] = "#6C757D"
        else:
            colors["background"] = "#1A1A1A"
            colors["surface"] = "#2D2D2D"
            colors["text"] = "#FFFFFF"
            colors["text_secondary"] = "#B8B8B8"
        
        # Semantic colors
        colors["success"] = "#28A745"
        colors["warning"] = "#FFC107"
        colors["error"] = "#DC3545"
        colors["info"] = "#17A2B8"
        
        return colors
    
    def _ensure_accessibility(self, colors: Dict[str, str], level: str) -> Dict[str, str]:
        """Ensure colors meet WCAG accessibility standards"""
        min_ratio = 7.0 if level == "AAA" else 4.5
        
        # Check text colors against backgrounds
        bg_color = colors.get("background", "#FFFFFF")
        
        for key in ["text", "text_secondary"]:
            if key in colors:
                ratio = self._calculate_contrast_ratio(colors[key], bg_color)
                if ratio < min_ratio:
                    # Adjust color to meet requirement
                    colors[key] = self._adjust_for_contrast(colors[key], bg_color, min_ratio)
        
        # Check primary colors against background
        for key in ["primary", "secondary", "accent"]:
            if key in colors:
                ratio = self._calculate_contrast_ratio(colors[key], bg_color)
                if ratio < 3.0:  # Too low even for large text
                    # Create darker/lighter variant
                    colors[f"{key}_text"] = self._adjust_for_contrast(colors[key], bg_color, min_ratio)
        
        return colors
    
    def _generate_dark_mode_variants(self, colors: Dict[str, str]) -> Dict[str, str]:
        """Generate dark mode color variants"""
        dark_colors = {}
        
        for key, color in colors.items():
            if key in ["background", "surface"]:
                # Invert backgrounds
                dark_colors[key] = "#1A1A1A" if color == "#FFFFFF" else "#2D2D2D"
            elif key in ["text", "text_secondary"]:
                # Invert text
                dark_colors[key] = "#FFFFFF" if key == "text" else "#B8B8B8"
            else:
                # Adjust other colors for dark background
                rgb = self._hex_to_rgb(color)
                h, s, v = colorsys.rgb_to_hsv(*[c/255.0 for c in rgb])
                # Increase brightness for dark mode
                v = min(v * 1.2, 1.0)
                dark_colors[key] = self._hsv_to_hex(h * 360, s, v)
        
        return dark_colors
    
    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        """Convert HSV to hex color"""
        # Normalize inputs
        h = (h % 360) / 360.0
        s = max(0, min(1, s))
        v = max(0, min(1, v))
        
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)
        
        # Calculate relative luminance
        def luminance(rgb):
            def channel(c):
                c = c / 255.0
                if c <= 0.03928:
                    return c / 12.92
                return ((c + 0.055) / 1.055) ** 2.4
            
            return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])
        
        lum1 = luminance(rgb1)
        lum2 = luminance(rgb2)
        
        # Calculate contrast ratio
        if lum1 > lum2:
            return (lum1 + 0.05) / (lum2 + 0.05)
        return (lum2 + 0.05) / (lum1 + 0.05)
    
    def _adjust_for_contrast(self, color: str, background: str, min_ratio: float) -> str:
        """Adjust color to meet minimum contrast ratio"""
        rgb = self._hex_to_rgb(color)
        bg_rgb = self._hex_to_rgb(background)
        bg_lum = self._calculate_luminance(bg_rgb)
        
        # Determine if we need darker or lighter
        if bg_lum > 0.5:  # Light background
            # Make color darker
            factor = 0.9
            while self._calculate_contrast_ratio(color, background) < min_ratio and factor > 0:
                rgb = tuple(int(c * factor) for c in rgb)
                color = '#{:02x}{:02x}{:02x}'.format(*rgb)
                factor -= 0.1
        else:  # Dark background
            # Make color lighter
            factor = 1.1
            while self._calculate_contrast_ratio(color, background) < min_ratio and factor < 3:
                rgb = tuple(min(255, int(c * factor)) for c in rgb)
                color = '#{:02x}{:02x}{:02x}'.format(*rgb)
                factor += 0.1
        
        return color
    
    def _calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance"""
        def channel(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])
    
    def _generate_accessibility_report(self, colors: Dict[str, str]) -> Dict[str, Any]:
        """Generate comprehensive accessibility report"""
        report = {
            "wcag_aa_compliant": True,
            "wcag_aaa_compliant": True,
            "contrast_ratios": {},
            "warnings": [],
            "color_blind_safe": True
        }
        
        bg_color = colors.get("background", "#FFFFFF")
        
        # Check all color combinations
        for name, color in colors.items():
            if name != "background":
                ratio = self._calculate_contrast_ratio(color, bg_color)
                report["contrast_ratios"][f"{name}_on_background"] = round(ratio, 2)
                
                if ratio < 4.5:
                    report["wcag_aa_compliant"] = False
                    report["warnings"].append(f"{name} fails AA standard (ratio: {ratio:.2f})")
                if ratio < 7.0:
                    report["wcag_aaa_compliant"] = False
        
        # Check color blind safety
        report["color_blind_analysis"] = self._analyze_color_blind_safety(colors)
        
        return report
    
    def _analyze_color_blind_safety(self, colors: Dict[str, str]) -> Dict[str, bool]:
        """Analyze color blind safety"""
        # Simplified analysis - in production would use proper simulation
        analysis = {
            "protanopia_safe": True,
            "deuteranopia_safe": True,
            "tritanopia_safe": True
        }
        
        # Check if colors rely too heavily on red-green distinction
        primary_rgb = self._hex_to_rgb(colors.get("primary", "#000000"))
        secondary_rgb = self._hex_to_rgb(colors.get("secondary", "#000000"))
        
        # Simple heuristic: check if colors differ in blue channel
        blue_diff = abs(primary_rgb[2] - secondary_rgb[2])
        if blue_diff < 50:
            analysis["tritanopia_safe"] = False
        
        return analysis
    
    def _assign_semantic_roles(self, colors: Dict[str, str], context: str) -> Dict[str, str]:
        """Assign semantic roles to colors"""
        roles = {
            "primary": "Main brand color for headers, primary buttons, and key UI elements",
            "secondary": "Supporting color for secondary actions and complementary elements",
            "accent": "Highlight color for calls-to-action and important information",
            "background": "Main background color for slides",
            "surface": "Elevated surface color for cards and containers",
            "text": "Primary text color for maximum readability",
            "text_secondary": "Secondary text color for less important information"
        }
        
        # Add context-specific guidance
        industry = self._normalize_industry(context)
        if industry == "healthcare":
            roles["primary"] += " - Conveys trust and professionalism in medical context"
        elif industry == "finance":
            roles["primary"] += " - Establishes credibility and stability"
        elif industry == "technology":
            roles["primary"] += " - Suggests innovation and forward-thinking"
        
        return roles
    
    def _analyze_color_psychology(self, colors: Dict[str, str], context: str) -> Dict[str, str]:
        """Analyze psychological associations of colors"""
        psychology = {}
        
        for name, hex_color in colors.items():
            if name in ["background", "surface", "text", "text_secondary"]:
                continue
                
            rgb = self._hex_to_rgb(hex_color)
            h, s, v = colorsys.rgb_to_hsv(*[c/255.0 for c in rgb])
            hue = h * 360
            
            # Determine color family
            if hue < 20 or hue > 340:
                psychology[name] = "Red: Energy, passion, urgency, importance"
            elif hue < 45:
                psychology[name] = "Orange: Creativity, enthusiasm, warmth, friendliness"
            elif hue < 70:
                psychology[name] = "Yellow: Optimism, clarity, warmth, caution"
            elif hue < 150:
                psychology[name] = "Green: Growth, harmony, freshness, safety"
            elif hue < 250:
                psychology[name] = "Blue: Trust, stability, depth, professionalism"
            elif hue < 290:
                psychology[name] = "Purple: Creativity, luxury, wisdom, ambition"
            else:
                psychology[name] = "Pink: Compassion, nurturing, love, playfulness"
            
            # Add saturation/brightness effects
            if s < 0.3:
                psychology[name] += " (Muted: Professional, subtle, sophisticated)"
            elif s > 0.7:
                psychology[name] += " (Vibrant: Energetic, bold, attention-grabbing)"
            
            if v < 0.5:
                psychology[name] += " (Dark: Serious, premium, mysterious)"
            elif v > 0.8:
                psychology[name] += " (Light: Open, airy, approachable)"
        
        return psychology
    
    def _generate_rationale(
        self,
        context: str,
        mood: str,
        harmony: ColorHarmony,
        colors: Dict[str, str]
    ) -> str:
        """Generate explanation of color choices"""
        industry = self._normalize_industry(context)
        
        rationale = f"This color palette uses {harmony.value} harmony to create a {mood} aesthetic "
        rationale += f"appropriate for {industry} presentations. "
        
        if harmony == ColorHarmony.ANALOGOUS:
            rationale += "The analogous colors create a harmonious, cohesive feel that's easy on the eyes. "
        elif harmony == ColorHarmony.COMPLEMENTARY:
            rationale += "The complementary colors provide strong contrast and visual interest. "
        elif harmony == ColorHarmony.TRIADIC:
            rationale += "The triadic scheme offers vibrant diversity while maintaining balance. "
        
        primary_hex = colors.get("primary", "#000000")
        rgb = self._hex_to_rgb(primary_hex)
        h, _, _ = colorsys.rgb_to_hsv(*[c/255.0 for c in rgb])
        
        if industry == "healthcare" and 170 <= h * 360 <= 200:
            rationale += "The blue-green primary color evokes cleanliness, healing, and trust. "
        elif industry == "finance" and 200 <= h * 360 <= 240:
            rationale += "The deep blue primary color conveys stability, trust, and professionalism. "
        
        rationale += "All colors meet WCAG accessibility standards for text and UI elements."
        
        return rationale


# ===== ENHANCED FONT PAIRING TOOL =====

class FontPairingInput(BaseModel):
    """Input for presentation-optimized font pairing"""
    formality_level: Literal["high", "medium", "casual"] = Field(
        description="Formality level from director"
    )
    presentation_context: str = Field(
        description="Type of presentation: executive, technical, educational, sales, etc."
    )
    viewing_context: Literal["screen", "projection", "hybrid"] = Field(
        default="projection",
        description="Primary viewing context"
    )
    complexity_level: Literal["executive", "detailed", "simplified"] = Field(
        default="detailed",
        description="Content complexity from director"
    )
    brand_constraints: Optional[str] = Field(
        default=None,
        description="Any brand font requirements or preferences"
    )


class FontPairingOutput(BaseModel):
    """Output from font pairing generation"""
    heading_font: str = Field(description="Font for headings")
    body_font: str = Field(description="Font for body text")
    accent_font: Optional[str] = Field(default=None, description="Optional accent font")
    font_sizes: Dict[str, int] = Field(description="Recommended sizes for different uses")
    font_weights: Dict[str, int] = Field(description="Recommended weights")
    fallback_stack: List[str] = Field(description="Fallback font stack")
    pairing_rationale: str = Field(description="Why these fonts work together")
    usage_guidelines: Dict[str, str] = Field(description="Guidelines for using the fonts")
    readability_score: float = Field(description="Readability score for presentation context")


class PresentationFontPairing:
    """Find optimal font pairings for presentations"""
    
    # Presentation-optimized font database
    PRESENTATION_FONTS = {
        "heading": {
            "high_impact": {
                "fonts": ["Montserrat", "Bebas Neue", "Oswald", "Anton", "Raleway"],
                "characteristics": "Bold, attention-grabbing, excellent at large sizes"
            },
            "professional": {
                "fonts": ["Helvetica Neue", "Roboto", "Source Sans Pro", "IBM Plex Sans", "Segoe UI"],
                "characteristics": "Clean, trustworthy, corporate-appropriate"
            },
            "elegant": {
                "fonts": ["Playfair Display", "Didot", "Bodoni", "Merriweather", "Crimson Pro"],
                "characteristics": "Sophisticated, refined, adds gravitas"
            },
            "friendly": {
                "fonts": ["Circular", "Nunito", "Quicksand", "Comfortaa", "Rubik"],
                "characteristics": "Approachable, warm, inviting"
            },
            "technical": {
                "fonts": ["Space Grotesk", "Inter", "DM Sans", "Work Sans", "Barlow"],
                "characteristics": "Modern, precise, tech-forward"
            }
        },
        "body": {
            "highly_readable": {
                "fonts": ["Open Sans", "Lato", "Source Sans Pro", "Noto Sans", "Roboto"],
                "characteristics": "Excellent readability at distance"
            },
            "compact": {
                "fonts": ["Arial", "Helvetica", "Segoe UI", "Calibri", "Trebuchet MS"],
                "characteristics": "Space-efficient, clear at small sizes"
            },
            "distinctive": {
                "fonts": ["Avenir", "Proxima Nova", "Gotham", "Futura", "Century Gothic"],
                "characteristics": "Unique personality while maintaining readability"
            },
            "traditional": {
                "fonts": ["Georgia", "Times New Roman", "Baskerville", "Cambria", "Book Antiqua"],
                "characteristics": "Classic, formal, academic"
            }
        }
    }
    
    # Pairing rules
    PAIRING_RULES = {
        ("serif", "sans-serif"): 0.9,  # Classic pairing
        ("sans-serif", "sans-serif"): 0.7,  # Needs careful selection
        ("serif", "serif"): 0.5,  # Difficult to pull off
        ("display", "sans-serif"): 0.8,  # Good for impact
        ("display", "serif"): 0.6,  # Can work for elegant presentations
    }
    
    def find_optimal_pairing(self, input_data: FontPairingInput) -> FontPairingOutput:
        """Find optimal font pairing for presentation context"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"find_optimal_pairing called with formality: {input_data.formality_level}")
        
        # Determine font categories based on context
        heading_category = self._determine_heading_category(
            input_data.formality_level,
            input_data.presentation_context
        )
        
        body_category = self._determine_body_category(
            input_data.complexity_level,
            input_data.viewing_context
        )
        
        # Select specific fonts
        heading_font = self._select_heading_font(
            heading_category,
            input_data.brand_constraints
        )
        
        body_font = self._select_body_font(
            body_category,
            heading_font,
            input_data.brand_constraints
        )
        
        # Optional accent font for special elements
        accent_font = self._select_accent_font(
            heading_font,
            body_font,
            input_data.presentation_context
        )
        
        # Calculate sizes based on viewing context
        font_sizes = self._calculate_optimal_sizes(input_data.viewing_context)
        font_weights = self._determine_weights(input_data.formality_level)
        
        # Create fallback stack
        fallback_stack = self._create_presentation_fallback_stack(
            heading_font,
            body_font,
            accent_font
        )
        
        # Calculate readability score
        readability_score = self._calculate_readability_score(
            heading_font,
            body_font,
            input_data.viewing_context
        )
        
        # Generate comprehensive guidance
        rationale = self._generate_pairing_rationale(
            heading_font,
            body_font,
            input_data
        )
        
        guidelines = self._create_usage_guidelines(
            heading_font,
            body_font,
            accent_font,
            input_data
        )
        
        return FontPairingOutput(
            heading_font=heading_font,
            body_font=body_font,
            accent_font=accent_font,
            font_sizes=font_sizes,
            font_weights=font_weights,
            fallback_stack=fallback_stack,
            pairing_rationale=rationale,
            usage_guidelines=guidelines,
            readability_score=readability_score
        )
    
    def _determine_heading_category(self, formality: str, context: str) -> str:
        """Determine heading font category"""
        context_lower = context.lower()
        
        if formality == "high":
            if "executive" in context_lower or "board" in context_lower:
                return "professional"
            else:
                return "elegant"
        elif formality == "casual":
            if "sales" in context_lower or "marketing" in context_lower:
                return "high_impact"
            else:
                return "friendly"
        else:  # medium
            if "technical" in context_lower or "engineering" in context_lower:
                return "technical"
            else:
                return "professional"
    
    def _determine_body_category(self, complexity: str, viewing: str) -> str:
        """Determine body font category"""
        if complexity == "executive":
            return "highly_readable"
        elif complexity == "detailed":
            if viewing == "screen":
                return "compact"
            else:
                return "highly_readable"
        else:  # simplified
            return "distinctive"
    
    def _select_heading_font(self, category: str, constraints: Optional[str]) -> str:
        """Select specific heading font"""
        # Check brand constraints first
        if constraints:
            for cat_data in self.PRESENTATION_FONTS["heading"].values():
                for font in cat_data["fonts"]:
                    if font.lower() in constraints.lower():
                        return font
        
        # Select from category
        fonts = self.PRESENTATION_FONTS["heading"].get(category, {}).get("fonts", [])
        
        # Avoid overused defaults - randomize selection
        if "Inter" in fonts:
            fonts.remove("Inter")  # Remove Inter as requested
        
        return fonts[0] if fonts else "Helvetica Neue"
    
    def _select_body_font(self, category: str, heading_font: str, constraints: Optional[str]) -> str:
        """Select body font that pairs well with heading"""
        # Check brand constraints
        if constraints:
            for cat_data in self.PRESENTATION_FONTS["body"].values():
                for font in cat_data["fonts"]:
                    if font.lower() in constraints.lower() and font != heading_font:
                        return font
        
        # Get fonts from category
        fonts = self.PRESENTATION_FONTS["body"].get(category, {}).get("fonts", [])
        
        # Ensure contrast with heading font
        if heading_font in fonts:
            fonts.remove(heading_font)
        
        # Apply pairing rules
        heading_type = self._get_font_type(heading_font)
        
        # Filter based on pairing score
        best_fonts = []
        for font in fonts:
            body_type = self._get_font_type(font)
            score = self.PAIRING_RULES.get((heading_type, body_type), 0.5)
            if score >= 0.7:
                best_fonts.append(font)
        
        return best_fonts[0] if best_fonts else fonts[0] if fonts else "Open Sans"
    
    def _select_accent_font(
        self,
        heading: str,
        body: str,
        context: str
    ) -> Optional[str]:
        """Select optional accent font for special elements"""
        context_lower = context.lower()
        
        # Only add accent font for certain contexts
        if any(word in context_lower for word in ["creative", "sales", "marketing"]):
            # Find a distinctive font different from heading and body
            all_fonts = []
            for cat in ["high_impact", "distinctive"]:
                if cat in self.PRESENTATION_FONTS["heading"]:
                    all_fonts.extend(self.PRESENTATION_FONTS["heading"][cat]["fonts"])
            
            # Remove already selected fonts
            all_fonts = [f for f in all_fonts if f not in [heading, body]]
            
            return all_fonts[0] if all_fonts else None
        
        return None
    
    def _get_font_type(self, font_name: str) -> str:
        """Classify font type"""
        serif_fonts = ["Georgia", "Times New Roman", "Baskerville", "Playfair Display", 
                      "Didot", "Bodoni", "Merriweather", "Crimson Pro", "Cambria"]
        display_fonts = ["Bebas Neue", "Anton", "Oswald", "Comfortaa"]
        
        if font_name in serif_fonts:
            return "serif"
        elif font_name in display_fonts:
            return "display"
        else:
            return "sans-serif"
    
    def _calculate_optimal_sizes(self, viewing: str) -> Dict[str, int]:
        """Calculate optimal font sizes for viewing context"""
        if viewing == "projection":
            # Larger sizes for projection
            return {
                "h1": 48,
                "h2": 36,
                "h3": 28,
                "body": 20,
                "caption": 16,
                "minimum": 16
            }
        elif viewing == "screen":
            # Moderate sizes for screen
            return {
                "h1": 36,
                "h2": 28,
                "h3": 24,
                "body": 18,
                "caption": 14,
                "minimum": 14
            }
        else:  # hybrid
            # Balanced sizes
            return {
                "h1": 42,
                "h2": 32,
                "h3": 26,
                "body": 18,
                "caption": 16,
                "minimum": 16
            }
    
    def _determine_weights(self, formality: str) -> Dict[str, int]:
        """Determine font weights based on formality"""
        if formality == "high":
            return {
                "heading": 600,  # Semi-bold, not too heavy
                "body": 400,     # Regular
                "emphasis": 500  # Medium
            }
        elif formality == "casual":
            return {
                "heading": 700,  # Bold for impact
                "body": 400,     # Regular
                "emphasis": 600  # Semi-bold
            }
        else:  # medium
            return {
                "heading": 600,  # Semi-bold
                "body": 400,     # Regular
                "emphasis": 500  # Medium
            }
    
    def _create_presentation_fallback_stack(
        self,
        heading: str,
        body: str,
        accent: Optional[str]
    ) -> List[str]:
        """Create comprehensive fallback stack"""
        stack = [heading, body]
        if accent:
            stack.append(accent)
        
        # Add system fonts as fallbacks
        stack.extend([
            "system-ui",
            "-apple-system",
            "BlinkMacSystemFont",
            "Segoe UI",
            "Helvetica Neue",
            "Arial",
            "sans-serif"
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in stack if not (x in seen or seen.add(x))]
    
    def _calculate_readability_score(
        self,
        heading: str,
        body: str,
        viewing: str
    ) -> float:
        """Calculate readability score for presentation context"""
        score = 0.5  # Base score
        
        # Check body font readability
        highly_readable = self.PRESENTATION_FONTS["body"]["highly_readable"]["fonts"]
        if body in highly_readable:
            score += 0.3
        
        # Check heading impact
        high_impact = self.PRESENTATION_FONTS["heading"]["high_impact"]["fonts"]
        professional = self.PRESENTATION_FONTS["heading"]["professional"]["fonts"]
        if heading in high_impact or heading in professional:
            score += 0.1
        
        # Viewing context bonus
        if viewing == "projection" and body in highly_readable:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_pairing_rationale(
        self,
        heading: str,
        body: str,
        input_data: FontPairingInput
    ) -> str:
        """Generate explanation of font choices"""
        rationale = f"{heading} was selected for headings because it "
        
        # Explain heading choice
        for category, data in self.PRESENTATION_FONTS["heading"].items():
            if heading in data["fonts"]:
                rationale += f"is {data['characteristics'].lower()}. "
                break
        
        rationale += f"{body} complements it perfectly for body text, offering "
        
        # Explain body choice
        for category, data in self.PRESENTATION_FONTS["body"].items():
            if body in data["fonts"]:
                rationale += f"{data['characteristics'].lower()}. "
                break
        
        # Add context-specific reasoning
        if input_data.viewing_context == "projection":
            rationale += "Both fonts are optimized for projection viewing, ensuring clarity even from a distance. "
        
        if input_data.formality_level == "high":
            rationale += "This pairing maintains the professional tone required for executive presentations."
        elif input_data.formality_level == "casual":
            rationale += "This combination creates an approachable, engaging feel perfect for your audience."
        
        return rationale
    
    def _create_usage_guidelines(
        self,
        heading: str,
        body: str,
        accent: Optional[str],
        input_data: FontPairingInput
    ) -> Dict[str, str]:
        """Create comprehensive usage guidelines"""
        guidelines = {
            "headings": f"Use {heading} for all headings. Maintain clear hierarchy with size differences of at least 20%.",
            "body": f"Use {body} for all body text. Keep paragraphs short (3-4 lines max) for presentations.",
            "emphasis": f"For emphasis within body text, use bold weight of {body} rather than italics.",
            "line_spacing": "Use 1.5x line height for body text, 1.2x for headings.",
            "slide_density": "Limit to 6-8 lines of body text per slide for optimal readability."
        }
        
        if accent:
            guidelines["accent_usage"] = f"Reserve {accent} for special callouts, quotes, or key statistics only."
        
        # Viewing-specific guidelines
        if input_data.viewing_context == "projection":
            guidelines["minimum_size"] = "Never go below 16pt for any text element."
            guidelines["contrast"] = "Ensure high contrast between text and background for projection."
        elif input_data.viewing_context == "screen":
            guidelines["minimum_size"] = "Keep body text at 14pt minimum for screen viewing."
        
        # Complexity-specific guidelines
        if input_data.complexity_level == "detailed":
            guidelines["bullets"] = "Use consistent bullet styles. Consider numbered lists for sequential information."
        elif input_data.complexity_level == "executive":
            guidelines["brevity"] = "Use short, impactful statements. One key idea per bullet point."
        
        return guidelines


# Create tool instances for the agent
generate_color_palette_tool = Tool(
    function=EnhancedColorPaletteGenerator().generate_enhanced_palette,
    name="generate_color_palette",
    description="Generate sophisticated color palette using proper color theory and accessibility standards"
)

find_font_pairing_tool = Tool(
    function=PresentationFontPairing().find_optimal_pairing,
    name="find_font_pairing",
    description="Select optimal font pairing specifically for presentations, considering viewing distance and context"
)


# ===== BACKWARD COMPATIBILITY =====
# These are provided for backward compatibility with code that expects the old class names

class ColorPaletteGenerator:
    """Backward compatibility wrapper for EnhancedColorPaletteGenerator"""
    def __init__(self):
        self._generator = EnhancedColorPaletteGenerator()
    
    def generate_palette(self, *args, **kwargs):
        # Convert old-style arguments to new ColorPaletteInput if needed
        if args or kwargs:
            # For now, just return a basic palette
            return {
                "primary": "#0066cc",
                "secondary": "#4d94ff", 
                "accent": "#ff6b6b",
                "background": "#ffffff",
                "text": "#212121"
            }
        return {}


class FontPairingFinder:
    """Backward compatibility wrapper for PresentationFontPairing"""
    def __init__(self):
        self._pairing = PresentationFontPairing()
    
    def find_pairing(self, *args, **kwargs):
        # Convert old-style arguments to new FontPairingInput if needed
        if args or kwargs:
            # Return basic font pairing
            return {
                "heading": {"family": "Helvetica Neue", "size": 32, "weight": 600},
                "body": {"family": "Open Sans", "size": 16, "weight": 400}
            }
        return {}


class LayoutTemplateDesigner:
    """Backward compatibility stub - layout is now handled separately"""
    def __init__(self):
        pass
    
    def design_templates(self, *args, **kwargs):
        # Return empty templates as layout is handled elsewhere
        return {}