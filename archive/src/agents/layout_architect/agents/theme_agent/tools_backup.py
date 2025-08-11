"""
Enhanced tools for Theme Agent - Mood analysis, color theory, typography, and layout generation.

These tools provide sophisticated approaches to design decisions,
ensuring the theme captures the presentation's intent and creates
a comprehensive design system.
"""

from typing import Dict, List, Tuple, Optional, Literal, Any
from pydantic import BaseModel, Field, validator
from pydantic_ai import Tool
import colorsys
import math
import re


# ===== MOOD ANALYSIS TOOL =====

class MoodAnalysisInput(BaseModel):
    """Input for mood and keyword analysis"""
    overall_theme: str = Field(description="The overall theme description from strawman")
    design_suggestions: str = Field(description="Design suggestions from strawman")
    main_title: Optional[str] = Field(default=None, description="Presentation title for context")
    target_audience: Optional[str] = Field(default=None, description="Target audience for tone inference")


class MoodAnalysisOutput(BaseModel):
    """Output from mood and keyword analysis"""
    mood_keywords: List[str] = Field(
        description="Actionable design keywords extracted from the theme"
    )
    primary_mood: str = Field(
        description="The dominant mood: professional, energetic, calm, innovative, etc."
    )
    emotional_tone: str = Field(
        description="Emotional quality: confident, trustworthy, inspiring, approachable, etc."
    )
    style_direction: str = Field(
        description="Visual style direction based on analysis"
    )


class MoodAnalyzer:
    """Analyze presentation theme to extract actionable mood keywords"""
    
    # Keyword mappings for different moods
    MOOD_KEYWORDS = {
        "professional": ["clean", "structured", "reliable", "corporate", "polished"],
        "modern": ["contemporary", "minimal", "sleek", "innovative", "fresh"],
        "data-driven": ["analytical", "precise", "logical", "evidence-based", "factual"],
        "persuasive": ["compelling", "confident", "impactful", "dynamic", "engaging"],
        "innovative": ["creative", "forward-thinking", "cutting-edge", "bold", "progressive"],
        "trustworthy": ["reliable", "stable", "authentic", "transparent", "credible"],
        "energetic": ["vibrant", "active", "exciting", "lively", "enthusiastic"],
        "calm": ["peaceful", "balanced", "serene", "thoughtful", "gentle"],
        "technical": ["detailed", "systematic", "methodical", "precise", "specialized"],
        "educational": ["informative", "clear", "accessible", "explanatory", "instructive"]
    }
    
    # Color associations with moods
    MOOD_COLORS = {
        "professional": ["blue", "gray", "navy"],
        "energetic": ["orange", "red", "yellow"],
        "calm": ["green", "blue", "lavender"],
        "innovative": ["purple", "teal", "electric"],
        "trustworthy": ["blue", "green", "earth tones"]
    }
    
    def analyze_mood(self, input_data: MoodAnalysisInput) -> MoodAnalysisOutput:
        """Extract mood keywords from theme and suggestions"""
        
        # Combine all text for analysis
        full_text = f"{input_data.overall_theme} {input_data.design_suggestions}"
        if input_data.main_title:
            full_text += f" {input_data.main_title}"
        
        text_lower = full_text.lower()
        
        # Extract explicit keywords
        extracted_keywords = []
        mood_scores = {}
        
        # Score each mood based on keyword presence
        for mood, keywords in self.MOOD_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                mood_scores[mood] = score
                extracted_keywords.extend([kw for kw in keywords if kw in text_lower])
        
        # Find primary mood
        primary_mood = max(mood_scores.items(), key=lambda x: x[1])[0] if mood_scores else "professional"
        
        # Extract color preferences
        color_keywords = []
        for color_word in ["blue", "green", "red", "orange", "purple", "gray", "black", "white"]:
            if color_word in text_lower:
                color_keywords.append(color_word)
        
        # Add mood-specific keywords
        mood_keywords = list(set(extracted_keywords + self.MOOD_KEYWORDS.get(primary_mood, [])))
        
        # Add color keywords if found
        if color_keywords:
            mood_keywords.extend(color_keywords)
        
        # Parse specific descriptors
        if "modern" in text_lower:
            mood_keywords.extend(["modern", "contemporary", "clean"])
        if "traditional" in text_lower:
            mood_keywords.extend(["traditional", "classic", "timeless"])
        if "tech" in text_lower or "technology" in text_lower:
            mood_keywords.extend(["tech-forward", "digital", "innovative"])
        if "health" in text_lower or "medical" in text_lower:
            mood_keywords.extend(["medical", "caring", "professional"])
        
        # Determine emotional tone based on audience
        emotional_tone = self._determine_emotional_tone(
            primary_mood, 
            input_data.target_audience
        )
        
        # Determine style direction
        style_direction = self._determine_style_direction(
            primary_mood,
            mood_keywords,
            color_keywords
        )
        
        # Remove duplicates and limit keywords
        final_keywords = list(set(mood_keywords))[:12]
        
        return MoodAnalysisOutput(
            mood_keywords=final_keywords,
            primary_mood=primary_mood,
            emotional_tone=emotional_tone,
            style_direction=style_direction
        )
    
    def _determine_emotional_tone(self, mood: str, audience: Optional[str]) -> str:
        """Determine emotional tone based on mood and audience"""
        if audience:
            audience_lower = audience.lower()
            if "executive" in audience_lower or "investor" in audience_lower:
                return "confident and authoritative"
            elif "student" in audience_lower or "public" in audience_lower:
                return "approachable and engaging"
            elif "technical" in audience_lower or "engineering" in audience_lower:
                return "precise and knowledgeable"
        
        # Default based on mood
        tone_map = {
            "professional": "confident and trustworthy",
            "energetic": "enthusiastic and inspiring",
            "calm": "thoughtful and reassuring",
            "innovative": "forward-thinking and bold",
            "data-driven": "analytical and credible"
        }
        
        return tone_map.get(mood, "clear and effective")
    
    def _determine_style_direction(
        self, 
        mood: str, 
        keywords: List[str], 
        colors: List[str]
    ) -> str:
        """Determine overall style direction"""
        if "minimal" in keywords or "clean" in keywords:
            return "Minimalist design with plenty of white space and clean typography"
        elif "bold" in keywords or "dynamic" in keywords:
            return "Bold, dynamic design with strong visual hierarchy and impactful elements"
        elif "traditional" in keywords or "classic" in keywords:
            return "Classic, timeless design with traditional typography and layouts"
        elif "tech" in keywords or "digital" in keywords:
            return "Modern tech aesthetic with geometric shapes and digital elements"
        else:
            return f"{mood.capitalize()} design approach with cohesive visual language"


# ===== BASE COLOR PALETTE TOOL =====

class ColorPaletteInput(BaseModel):
    """Input for color palette generation"""
    primary_color: str = Field(description="Primary color in hex format")
    mood: str = Field(description="Mood for the palette: formal, energetic, calm, innovative")
    color_count: int = Field(default=5, description="Number of colors to generate")
    ensure_accessibility: bool = Field(default=True, description="Ensure colors meet WCAG standards")


class ColorPaletteOutput(BaseModel):
    """Output from color palette generation"""
    colors: Dict[str, str] = Field(description="Generated color palette")
    accessibility_report: Dict[str, Any] = Field(description="WCAG compliance report")
    color_roles: Dict[str, str] = Field(description="Semantic roles for each color")


class ColorPaletteGenerator:
    """Generate harmonious color palettes with accessibility"""
    
    def generate_palette(self, input_data: ColorPaletteInput) -> ColorPaletteOutput:
        """Generate a color palette based on input parameters"""
        # Convert hex to RGB
        primary_rgb = self._hex_to_rgb(input_data.primary_color)
        
        # Generate complementary colors based on mood
        colors = self._generate_colors(primary_rgb, input_data.mood, input_data.color_count)
        
        # Check accessibility
        accessibility_report = self._check_accessibility(colors) if input_data.ensure_accessibility else {}
        
        # Assign roles
        color_roles = self._assign_color_roles(colors, input_data.mood)
        
        return ColorPaletteOutput(
            colors=colors,
            accessibility_report=accessibility_report,
            color_roles=color_roles
        )
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: Tuple[float, float, float]) -> str:
        """Convert RGB to hex"""
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
    
    def _generate_colors(self, primary_rgb: Tuple[float, float, float], mood: str, count: int) -> Dict[str, str]:
        """Generate color palette based on mood"""
        h, s, v = colorsys.rgb_to_hsv(*primary_rgb)
        colors = {"primary": self._rgb_to_hex(primary_rgb)}
        
        if mood == "formal":
            # Monochromatic with variations in lightness
            colors["secondary"] = self._rgb_to_hex(colorsys.hsv_to_rgb(h, s * 0.5, v))
            colors["accent"] = self._rgb_to_hex(colorsys.hsv_to_rgb(h, s, v * 0.8))
            colors["neutral"] = "#333333"
            colors["background"] = "#f8f9fa"
        elif mood == "energetic":
            # Complementary colors
            colors["secondary"] = self._rgb_to_hex(colorsys.hsv_to_rgb((h + 0.5) % 1, s, v))
            colors["accent"] = self._rgb_to_hex(colorsys.hsv_to_rgb((h + 0.3) % 1, s * 0.8, v))
            colors["highlight"] = self._rgb_to_hex(colorsys.hsv_to_rgb(h, s, min(v * 1.2, 1)))
            colors["background"] = "#ffffff"
        elif mood == "calm":
            # Analogous colors
            colors["secondary"] = self._rgb_to_hex(colorsys.hsv_to_rgb((h + 0.08) % 1, s * 0.7, v))
            colors["accent"] = self._rgb_to_hex(colorsys.hsv_to_rgb((h - 0.08) % 1, s * 0.7, v))
            colors["neutral"] = "#6c757d"
            colors["background"] = "#f5f7fa"
        else:  # innovative
            # Triadic colors
            colors["secondary"] = self._rgb_to_hex(colorsys.hsv_to_rgb((h + 0.33) % 1, s, v))
            colors["accent"] = self._rgb_to_hex(colorsys.hsv_to_rgb((h + 0.67) % 1, s, v))
            colors["highlight"] = self._rgb_to_hex(colorsys.hsv_to_rgb(h, s * 1.2, v * 0.9))
            colors["background"] = "#fafbfc"
        
        return colors
    
    def _check_accessibility(self, colors: Dict[str, str]) -> Dict[str, Any]:
        """Check WCAG compliance"""
        # Simplified accessibility check
        report = {
            "compliant": True,
            "warnings": [],
            "contrast_ratios": {}
        }
        
        # Check contrast between primary colors and background
        bg_color = colors.get("background", "#ffffff")
        for name, color in colors.items():
            if name != "background":
                ratio = self._calculate_contrast_ratio(color, bg_color)
                report["contrast_ratios"][f"{name}_on_background"] = ratio
                if ratio < 4.5:  # WCAG AA standard
                    report["warnings"].append(f"{name} may have insufficient contrast")
                    report["compliant"] = False
        
        return report
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        # Convert to RGB
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)
        
        # Calculate relative luminance
        def luminance(rgb):
            def channel(c):
                c = c
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
    
    def _assign_color_roles(self, colors: Dict[str, str], mood: str) -> Dict[str, str]:
        """Assign semantic roles to colors"""
        roles = {}
        
        # Common roles
        roles["primary"] = "Main brand color, used for primary actions and key elements"
        roles["secondary"] = "Supporting color for secondary elements"
        roles["background"] = "Page and slide backgrounds"
        
        # Mood-specific roles
        if "accent" in colors:
            roles["accent"] = "Emphasis and call-to-action elements"
        if "highlight" in colors:
            roles["highlight"] = "Interactive states and important information"
        if "neutral" in colors:
            roles["neutral"] = "Text and subtle UI elements"
        
        return roles


# ===== ENHANCED COLOR PALETTE TOOL =====

class EnhancedColorPaletteInput(BaseModel):
    """Enhanced input for color palette generation"""
    mood_keywords: List[str] = Field(
        description="Keywords from mood analysis"
    )
    primary_color_hint: Optional[str] = Field(
        default=None,
        description="Optional specific color mentioned in design suggestions"
    )
    industry_context: Optional[str] = Field(
        default=None,
        description="Industry context for appropriate color choices"
    )
    accessibility_level: Literal["AA", "AAA"] = Field(
        default="AA",
        description="WCAG accessibility level required"
    )


class EnhancedColorPaletteGenerator(ColorPaletteGenerator):
    """Enhanced color palette generator that uses mood keywords"""
    
    def generate_enhanced_palette(
        self, 
        input_data: EnhancedColorPaletteInput
    ) -> ColorPaletteOutput:
        """Generate palette based on mood keywords"""
        
        # Determine primary color based on keywords and hints
        primary_color = self._determine_primary_color(
            input_data.mood_keywords,
            input_data.primary_color_hint,
            input_data.industry_context
        )
        
        # Create base palette input
        base_input = ColorPaletteInput(
            primary_color=primary_color,
            mood=self._keywords_to_mood(input_data.mood_keywords),
            color_count=8,  # More colors for comprehensive palette
            ensure_accessibility=True
        )
        
        # Generate base palette
        base_output = self.generate_palette(base_input)
        
        # Enhance with additional colors
        enhanced_colors = self._enhance_palette(
            base_output.colors,
            input_data.mood_keywords,
            input_data.accessibility_level
        )
        
        # Update color roles
        enhanced_roles = self._define_comprehensive_roles(enhanced_colors)
        
        return ColorPaletteOutput(
            colors=enhanced_colors,
            accessibility_report=base_output.accessibility_report,
            color_roles=enhanced_roles
        )
    
    def _determine_primary_color(
        self,
        keywords: List[str],
        hint: Optional[str],
        industry: Optional[str]
    ) -> str:
        """Determine primary color from context"""
        
        # If explicit color hint provided
        if hint:
            color_map = {
                "blue": "#0066cc",
                "green": "#00a86b",
                "red": "#dc3545",
                "orange": "#ff6b35",
                "purple": "#6b46c1",
                "teal": "#14b8a6",
                "navy": "#1e3a8a"
            }
            for color_name, hex_value in color_map.items():
                if color_name in hint.lower():
                    return hex_value
        
        # Industry-specific defaults
        if industry:
            industry_lower = industry.lower()
            if "health" in industry_lower or "medical" in industry_lower:
                return "#14b8a6"  # Teal
            elif "finance" in industry_lower or "banking" in industry_lower:
                return "#1e3a8a"  # Navy
            elif "tech" in industry_lower or "software" in industry_lower:
                return "#0066cc"  # Blue
            elif "education" in industry_lower:
                return "#00a86b"  # Green
        
        # Keyword-based selection
        if "energetic" in keywords or "dynamic" in keywords:
            return "#ff6b35"  # Orange
        elif "calm" in keywords or "peaceful" in keywords:
            return "#00a86b"  # Green
        elif "innovative" in keywords or "creative" in keywords:
            return "#6b46c1"  # Purple
        else:
            return "#0066cc"  # Default blue
    
    def _keywords_to_mood(self, keywords: List[str]) -> str:
        """Convert keywords to closest mood category"""
        mood_mapping = {
            "formal": ["professional", "corporate", "executive"],
            "energetic": ["dynamic", "vibrant", "exciting"],
            "calm": ["peaceful", "serene", "thoughtful"],
            "innovative": ["creative", "cutting-edge", "modern"],
            "trustworthy": ["reliable", "stable", "credible"]
        }
        
        for mood, mood_keywords in mood_mapping.items():
            if any(kw in keywords for kw in mood_keywords):
                return mood
        
        return "formal"  # Default
    
    def _enhance_palette(
        self,
        base_colors: Dict[str, str],
        keywords: List[str],
        accessibility: str
    ) -> Dict[str, str]:
        """Enhance palette with additional semantic colors"""
        enhanced = base_colors.copy()
        
        # Add semantic colors
        enhanced["surface"] = self._lighten_color(base_colors["background"], 0.02)
        enhanced["border"] = self._darken_color(base_colors["background"], 0.15)
        enhanced["muted"] = self._desaturate_color(base_colors["secondary"], 0.5)
        
        # Add state colors if not present
        if "success" not in enhanced:
            enhanced["success"] = "#10b981"  # Green
        if "warning" not in enhanced:
            enhanced["warning"] = "#f59e0b"  # Amber
        if "error" not in enhanced:
            enhanced["error"] = "#ef4444"  # Red
        if "info" not in enhanced:
            enhanced["info"] = "#3b82f6"  # Blue
        
        # Ensure all colors meet accessibility
        if accessibility == "AAA":
            enhanced = self._enforce_aaa_compliance(enhanced)
        
        return enhanced
    
    def _define_comprehensive_roles(self, colors: Dict[str, str]) -> Dict[str, str]:
        """Define comprehensive roles for all colors"""
        return {
            "primary": "Main brand color for headers, CTAs, and key elements",
            "secondary": "Supporting color for subheadings and secondary actions",
            "accent": "Highlight color for emphasis and interactive elements",
            "background": "Main background color for slides",
            "surface": "Elevated surface color for cards and sections",
            "text": "Primary text color for body content",
            "text_secondary": "Secondary text color for captions and metadata",
            "border": "Border color for dividers and outlines",
            "muted": "Muted color for disabled or inactive elements",
            "success": "Positive feedback and success states",
            "warning": "Warnings and caution messages",
            "error": "Error states and critical alerts",
            "info": "Informational messages and hints"
        }
    
    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """Lighten a color by amount (0-1)"""
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(*[x/255.0 for x in rgb])
        v = min(1.0, v + amount)
        return self._adjust_color(h, s, v)
    
    def _darken_color(self, hex_color: str, amount: float) -> str:
        """Darken a color by amount (0-1)"""
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(*[x/255.0 for x in rgb])
        v = max(0.0, v - amount)
        return self._adjust_color(h, s, v)
    
    def _desaturate_color(self, hex_color: str, amount: float) -> str:
        """Desaturate a color by amount (0-1)"""
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(*[x/255.0 for x in rgb])
        s = max(0.0, s - amount)
        return self._adjust_color(h, s, v)
    
    def _enforce_aaa_compliance(self, colors: Dict[str, str]) -> Dict[str, str]:
        """Ensure AAA compliance (7:1 contrast ratio)"""
        # This is a simplified version - real implementation would be more sophisticated
        if self.contrast_ratio(colors["text"], colors["background"]) < 7.0:
            colors["text"] = "#000000" if self.calculate_luminance(
                self.hex_to_rgb(colors["background"])
            ) > 0.5 else "#ffffff"
        
        return colors


# ===== BASE FONT PAIRING TOOL =====

class FontPairingInput(BaseModel):
    """Input for font pairing generation"""
    mood: str = Field(description="Design mood: formal, modern, casual, technical")
    use_case: str = Field(description="Primary use case: presentation, document, web")
    audience: str = Field(description="Target audience description")
    prefer_readable: bool = Field(default=True, description="Prioritize readability")


class FontPairingOutput(BaseModel):
    """Output from font pairing generation"""
    heading_font: str = Field(description="Font for headings")
    body_font: str = Field(description="Font for body text")
    fallback_stack: List[str] = Field(description="Fallback font stack")
    pairing_rationale: str = Field(description="Why these fonts work together")
    usage_guidelines: Dict[str, str] = Field(description="Guidelines for using the fonts")


class FontPairingFinder:
    """Find harmonious font pairings"""
    
    # Base font database
    FONT_DATABASE = {
        "sans-serif": {
            "modern": ["Inter", "Helvetica Neue", "Arial"],
            "readable": ["Open Sans", "Source Sans Pro", "Roboto"],
            "distinctive": ["DM Sans", "Space Grotesk", "Work Sans"]
        },
        "serif": {
            "classic": ["Georgia", "Times New Roman", "Cambria"],
            "modern": ["Playfair Display", "Crimson Pro", "Merriweather"],
            "readable": ["Libre Baskerville", "Source Serif Pro", "Lora"]
        },
        "mono": {
            "code": ["JetBrains Mono", "Fira Code", "Consolas"],
            "ui": ["SF Mono", "IBM Plex Mono", "Roboto Mono"]
        }
    }
    
    def find_pairing(self, input_data: FontPairingInput) -> FontPairingOutput:
        """Find appropriate font pairing"""
        # Determine font categories based on mood
        if input_data.mood == "formal":
            heading_category = "serif"
            body_category = "sans-serif"
        elif input_data.mood == "technical":
            heading_category = "sans-serif"
            body_category = "mono"
        else:
            heading_category = "sans-serif"
            body_category = "sans-serif"
        
        # Select specific fonts
        heading_font = self._select_font(heading_category, input_data.mood, "heading")
        body_font = self._select_font(body_category, input_data.mood, "body")
        
        # Ensure fonts are different if same category
        if heading_font == body_font:
            body_font = self._select_alternative(body_category, heading_font)
        
        # Create fallback stack
        fallback_stack = self._create_fallback_stack(heading_font, body_font)
        
        # Generate rationale
        rationale = self._generate_rationale(heading_font, body_font, input_data.mood)
        
        # Create usage guidelines
        guidelines = self._create_guidelines(heading_font, body_font, input_data.use_case)
        
        return FontPairingOutput(
            heading_font=heading_font,
            body_font=body_font,
            fallback_stack=fallback_stack,
            pairing_rationale=rationale,
            usage_guidelines=guidelines
        )
    
    def _select_font(self, category: str, mood: str, role: str) -> str:
        """Select appropriate font from category"""
        fonts = self.FONT_DATABASE.get(category, {})
        
        # Map mood to font style
        if mood in ["modern", "innovative"]:
            style = "modern"
        elif mood in ["formal", "traditional"]:
            style = "classic"
        else:
            style = "readable"
        
        font_list = fonts.get(style, fonts.get("readable", []))
        return font_list[0] if font_list else "Arial"
    
    def _select_alternative(self, category: str, avoid_font: str) -> str:
        """Select alternative font avoiding specific one"""
        all_fonts = []
        for style_fonts in self.FONT_DATABASE.get(category, {}).values():
            all_fonts.extend(style_fonts)
        
        alternatives = [f for f in all_fonts if f != avoid_font]
        return alternatives[0] if alternatives else "Georgia"
    
    def _create_fallback_stack(self, heading: str, body: str) -> List[str]:
        """Create fallback font stack"""
        return list(set([heading, body, "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"]))
    
    def _generate_rationale(self, heading: str, body: str, mood: str) -> str:
        """Generate pairing rationale"""
        return f"{heading} provides strong visual hierarchy for headings while {body} ensures excellent readability for body text. This combination creates a {mood} aesthetic that guides readers through the content effectively."
    
    def _create_guidelines(self, heading: str, body: str, use_case: str) -> Dict[str, str]:
        """Create usage guidelines"""
        return {
            "headings": f"Use {heading} for all headings (h1-h6). Recommended sizes: 24-48pt",
            "body": f"Use {body} for all body text. Recommended size: 14-18pt",
            "line_height": "1.5-1.7 for body text, 1.2-1.3 for headings",
            "spacing": "Add 0.5-1em margin after headings",
            "hierarchy": "Maintain clear size differences between heading levels"
        }


# ===== ENHANCED FONT PAIRING TOOL =====

class EnhancedFontPairingInput(BaseModel):
    """Enhanced input for font pairing"""
    mood_keywords: List[str] = Field(description="Keywords from mood analysis")
    formality_level: str = Field(description="high, medium, or casual")
    complexity_allowance: str = Field(description="executive, detailed, or simplified")
    reading_context: Literal["screen", "projection", "print"] = Field(default="screen")


class EnhancedFontPairingFinder(FontPairingFinder):
    """Enhanced font pairing that considers mood keywords"""
    
    # Extended font database with mood associations
    MOOD_FONT_ASSOCIATIONS = {
        "modern": ["Inter", "DM Sans", "Space Grotesk", "Work Sans"],
        "professional": ["Source Sans Pro", "IBM Plex Sans", "Roboto", "Open Sans"],
        "elegant": ["Playfair Display", "Crimson Pro", "Libre Baskerville", "Cormorant"],
        "technical": ["JetBrains Mono", "Fira Code", "IBM Plex Mono", "Roboto Mono"],
        "approachable": ["Nunito", "Rubik", "Poppins", "Comfortaa"],
        "authoritative": ["Helvetica Neue", "Franklin Gothic", "Oswald", "Bebas Neue"]
    }
    
    def find_enhanced_pairing(
        self,
        input_data: EnhancedFontPairingInput
    ) -> FontPairingOutput:
        """Find font pairing based on comprehensive mood analysis"""
        
        # Select heading font based on mood
        heading_font = self._select_heading_font(
            input_data.mood_keywords,
            input_data.formality_level
        )
        
        # Select body font for optimal pairing
        body_font = self._select_body_font(
            heading_font,
            input_data.complexity_allowance,
            input_data.reading_context
        )
        
        # Generate comprehensive output
        return FontPairingOutput(
            heading_font={
                "family": heading_font,
                "category": self._get_font_category(heading_font),
                "weights": "600, 700, 800",
                "fallback": self._get_fallback_stack(heading_font),
                "size_scale": self._get_size_scale(input_data.formality_level, "heading"),
                "letter_spacing": "-0.02em" if "modern" in input_data.mood_keywords else "-0.01em"
            },
            body_font={
                "family": body_font,
                "category": self._get_font_category(body_font),
                "weights": "400, 500, 600",
                "fallback": self._get_fallback_stack(body_font),
                "size_scale": self._get_size_scale(input_data.formality_level, "body"),
                "line_height": self._get_line_height(input_data.complexity_allowance)
            },
            pairing_rationale=self._generate_enhanced_rationale(
                heading_font,
                body_font,
                input_data.mood_keywords
            ),
            usage_guidelines=self._generate_enhanced_guidelines(
                input_data.formality_level,
                input_data.complexity_allowance,
                input_data.reading_context
            )
        )
    
    def _select_heading_font(self, keywords: List[str], formality: str) -> str:
        """Select heading font based on mood and formality"""
        # Check for specific mood matches
        for mood, fonts in self.MOOD_FONT_ASSOCIATIONS.items():
            if any(mood in kw for kw in keywords):
                if formality == "high":
                    # Pick more formal option from the list
                    return fonts[0]
                else:
                    # Pick more casual option
                    return fonts[-1]
        
        # Default based on formality
        if formality == "high":
            return "Helvetica Neue"
        elif formality == "casual":
            return "Poppins"
        else:
            return "Inter"
    
    def _select_body_font(
        self,
        heading: str,
        complexity: str,
        context: str
    ) -> str:
        """Select body font that pairs well with heading"""
        # Predefined excellent pairings
        pairing_map = {
            "Inter": "Inter",  # Monolithic pairing
            "Helvetica Neue": "Helvetica Neue",
            "Playfair Display": "Source Sans Pro",
            "Poppins": "Open Sans",
            "DM Sans": "DM Sans",
            "Space Grotesk": "Inter",
            "Bebas Neue": "Open Sans"
        }
        
        if heading in pairing_map:
            return pairing_map[heading]
        
        # Default to safe sans-serif
        return "Open Sans"
    
    def _get_size_scale(self, formality: str, usage: str) -> Dict[str, int]:
        """Get size scale based on formality"""
        if usage == "heading":
            if formality == "high":
                return {"h1": 48, "h2": 36, "h3": 28, "h4": 24}
            else:
                return {"h1": 56, "h2": 42, "h3": 32, "h4": 26}
        else:
            if formality == "high":
                return {"body": 16, "small": 14, "caption": 12}
            else:
                return {"body": 18, "small": 16, "caption": 14}
    
    def _get_line_height(self, complexity: str) -> float:
        """Get line height based on complexity"""
        if complexity == "executive":
            return 1.5  # Tighter for less text
        elif complexity == "detailed":
            return 1.7  # More space for dense text
        else:
            return 1.6  # Balanced
    
    def _generate_enhanced_rationale(
        self,
        heading: str,
        body: str,
        keywords: List[str]
    ) -> str:
        """Generate detailed rationale for the pairing"""
        mood_description = ", ".join(keywords[:3])
        
        if heading == body:
            return (
                f"{heading} provides a monolithic, cohesive design system "
                f"that perfectly embodies the {mood_description} aesthetic. "
                f"Using variable weights creates hierarchy while maintaining visual unity."
            )
        else:
            return (
                f"{heading} and {body} create a sophisticated contrast "
                f"that captures the {mood_description} mood. "
                f"The pairing balances personality in headings with readability in body text."
            )
    
    def _generate_enhanced_guidelines(
        self,
        formality: str,
        complexity: str,
        context: str
    ) -> Dict[str, str]:
        """Generate comprehensive usage guidelines"""
        guidelines = {
            "hierarchy": "Use weight and size to create clear visual hierarchy",
            "spacing": "Maintain consistent spacing ratios between text levels",
            "contrast": "Ensure sufficient contrast between heading and body styles"
        }
        
        if formality == "high":
            guidelines["tone"] = "Maintain professional restraint in typography usage"
        else:
            guidelines["tone"] = "Feel free to use bolder weights for emphasis"
        
        if complexity == "executive":
            guidelines["density"] = "Keep text blocks short and scannable"
        elif complexity == "detailed":
            guidelines["density"] = "Use generous line height for longer passages"
        
        if context == "projection":
            guidelines["minimum_size"] = "Never go below 24pt for projected content"
            guidelines["weight"] = "Use medium to bold weights for better visibility"
        
        return guidelines


# ===== LAYOUT TEMPLATES TOOL =====

class LayoutTemplatesInput(BaseModel):
    """Input for layout template generation"""
    slide_types: List[str] = Field(description="All unique slide types from strawman")
    mood_keywords: List[str] = Field(description="Keywords from mood analysis")
    visual_emphasis: Dict[str, float] = Field(
        default_factory=dict,
        description="Visual emphasis per slide type (0=text, 1=visual)"
    )
    formality_level: str = Field(description="high, medium, or casual")


class LayoutTemplatesOutput(BaseModel):
    """Output from layout template generation"""
    templates: Dict[str, Dict[str, Any]] = Field(
        description="Layout templates for each slide type"
    )
    grid_system: Dict[str, Any] = Field(
        description="Grid system specifications"
    )
    spacing_rules: Dict[str, Any] = Field(
        description="Spacing rules for consistency"
    )


class LayoutTemplateDesigner:
    """Design layout templates for all slide types"""
    
    # Grid constants
    GRID_WIDTH = 160
    GRID_HEIGHT = 90
    BASE_MARGIN = 8
    
    def design_templates(
        self,
        input_data: LayoutTemplatesInput
    ) -> LayoutTemplatesOutput:
        """Design templates for all slide types"""
        
        templates = {}
        
        for slide_type in input_data.slide_types:
            # Determine visual emphasis
            emphasis = input_data.visual_emphasis.get(slide_type, 0.5)
            
            # Create template based on type and mood
            template = self._create_template(
                slide_type,
                emphasis,
                input_data.mood_keywords,
                input_data.formality_level
            )
            
            templates[slide_type] = template
        
        # Define grid system
        grid_system = self._define_grid_system(input_data.mood_keywords)
        
        # Define spacing rules
        spacing_rules = self._define_spacing_rules(input_data.formality_level)
        
        return LayoutTemplatesOutput(
            templates=templates,
            grid_system=grid_system,
            spacing_rules=spacing_rules
        )
    
    def _create_template(
        self,
        slide_type: str,
        visual_emphasis: float,
        mood_keywords: List[str],
        formality: str
    ) -> Dict[str, Any]:
        """Create a specific template"""
        
        # Adjust margins based on formality
        margin = self.BASE_MARGIN if formality == "high" else self.BASE_MARGIN - 2
        work_width = self.GRID_WIDTH - (2 * margin)
        work_height = self.GRID_HEIGHT - (2 * margin)
        
        zones = {}
        
        # Title slide special case
        if "title" in slide_type.lower():
            zones = self._create_title_zones(
                margin, work_width, work_height, mood_keywords
            )
            emphasis = "title"
            reading_flow = "center-focused"
            
        # Data-driven slides
        elif "data" in slide_type.lower() or "chart" in slide_type.lower():
            zones = self._create_data_zones(
                margin, work_width, work_height, visual_emphasis
            )
            emphasis = "visualization"
            reading_flow = "F-pattern"
            
        # Visual-heavy slides
        elif visual_emphasis > 0.7:
            zones = self._create_visual_zones(
                margin, work_width, work_height, mood_keywords
            )
            emphasis = "visual"
            reading_flow = "visual-first"
            
        # Content-heavy slides
        elif visual_emphasis < 0.3:
            zones = self._create_content_zones(
                margin, work_width, work_height, formality
            )
            emphasis = "content"
            reading_flow = "linear"
            
        # Balanced slides
        else:
            zones = self._create_balanced_zones(
                margin, work_width, work_height, mood_keywords
            )
            emphasis = "balanced"
            reading_flow = "Z-pattern"
        
        return {
            "zones": zones,
            "emphasis": emphasis,
            "reading_flow": reading_flow,
            "description": f"Layout optimized for {slide_type} with {emphasis} emphasis",
            "white_space_target": self._calculate_white_space_target(
                formality, visual_emphasis
            )
        }
    
    def _create_title_zones(
        self,
        margin: int,
        width: int,
        height: int,
        keywords: List[str]
    ) -> Dict[str, Dict[str, int]]:
        """Create zones for title slide"""
        
        if "modern" in keywords or "minimal" in keywords:
            # Asymmetric modern layout
            return {
                "title": {
                    "leftInset": margin * 2,
                    "topInset": int(height * 0.3),
                    "width": int(width * 0.7),
                    "height": int(height * 0.25)
                },
                "subtitle": {
                    "leftInset": margin * 2,
                    "topInset": int(height * 0.3) + int(height * 0.25) + 4,
                    "width": int(width * 0.6),
                    "height": int(height * 0.1)
                },
                "accent": {
                    "leftInset": int(width * 0.75),
                    "topInset": margin,
                    "width": int(width * 0.25),
                    "height": height
                }
            }
        else:
            # Traditional centered layout
            return {
                "title": {
                    "leftInset": int(width * 0.1),
                    "topInset": int(height * 0.35),
                    "width": int(width * 0.8),
                    "height": int(height * 0.2)
                },
                "subtitle": {
                    "leftInset": int(width * 0.15),
                    "topInset": int(height * 0.55),
                    "width": int(width * 0.7),
                    "height": int(height * 0.1)
                },
                "footer": {
                    "leftInset": margin,
                    "topInset": height - 10,
                    "width": width,
                    "height": 10
                }
            }
    
    def _create_data_zones(
        self,
        margin: int,
        width: int,
        height: int,
        visual_emphasis: float
    ) -> Dict[str, Dict[str, int]]:
        """Create zones for data slides"""
        
        # Adjust visualization size based on emphasis
        viz_height = int(height * (0.5 + visual_emphasis * 0.3))
        
        return {
            "title": {
                "leftInset": margin,
                "topInset": margin,
                "width": width,
                "height": 10
            },
            "visualization": {
                "leftInset": margin,
                "topInset": margin + 14,
                "width": int(width * 0.65),
                "height": viz_height
            },
            "insights": {
                "leftInset": int(width * 0.65) + margin + 4,
                "topInset": margin + 14,
                "width": int(width * 0.35) - 4,
                "height": viz_height
            },
            "footer": {
                "leftInset": margin,
                "topInset": margin + 14 + viz_height + 4,
                "width": width,
                "height": height - (margin + 14 + viz_height + 4)
            }
        }
    
    def _create_visual_zones(
        self,
        margin: int,
        width: int,
        height: int,
        keywords: List[str]
    ) -> Dict[str, Dict[str, int]]:
        """Create zones for visual-heavy slides"""
        
        if "full-bleed" in keywords or "hero" in keywords:
            # Full-bleed visual
            return {
                "visual": {
                    "leftInset": 0,
                    "topInset": 0,
                    "width": self.GRID_WIDTH,
                    "height": self.GRID_HEIGHT
                },
                "overlay": {
                    "leftInset": margin * 2,
                    "topInset": height - 30,
                    "width": int(width * 0.6),
                    "height": 25
                }
            }
        else:
            # Standard visual layout
            return {
                "visual": {
                    "leftInset": margin,
                    "topInset": margin,
                    "width": width,
                    "height": int(height * 0.75)
                },
                "caption": {
                    "leftInset": margin,
                    "topInset": margin + int(height * 0.75) + 4,
                    "width": width,
                    "height": height - (margin + int(height * 0.75) + 4)
                }
            }
    
    def _create_content_zones(
        self,
        margin: int,
        width: int,
        height: int,
        formality: str
    ) -> Dict[str, Dict[str, int]]:
        """Create zones for content-heavy slides"""
        
        if formality == "high":
            # Single column for formal presentations
            return {
                "title": {
                    "leftInset": margin,
                    "topInset": margin,
                    "width": width,
                    "height": 12
                },
                "content": {
                    "leftInset": margin,
                    "topInset": margin + 16,
                    "width": width,
                    "height": height - 22
                },
                "footer": {
                    "leftInset": margin,
                    "topInset": height - 6,
                    "width": width,
                    "height": 6
                }
            }
        else:
            # Two-column for casual presentations
            column_width = (width - 4) // 2
            return {
                "title": {
                    "leftInset": margin,
                    "topInset": margin,
                    "width": width,
                    "height": 12
                },
                "left_content": {
                    "leftInset": margin,
                    "topInset": margin + 16,
                    "width": column_width,
                    "height": height - 16
                },
                "right_content": {
                    "leftInset": margin + column_width + 4,
                    "topInset": margin + 16,
                    "width": column_width,
                    "height": height - 16
                }
            }
    
    def _create_balanced_zones(
        self,
        margin: int,
        width: int,
        height: int,
        keywords: List[str]
    ) -> Dict[str, Dict[str, int]]:
        """Create zones for balanced slides"""
        
        return {
            "title": {
                "leftInset": margin,
                "topInset": margin,
                "width": width,
                "height": 10
            },
            "content": {
                "leftInset": margin,
                "topInset": margin + 14,
                "width": int(width * 0.55),
                "height": height - 20
            },
            "visual": {
                "leftInset": int(width * 0.55) + margin + 4,
                "topInset": margin + 14,
                "width": int(width * 0.45) - 4,
                "height": height - 20
            },
            "footer": {
                "leftInset": margin,
                "topInset": height - 6,
                "width": width,
                "height": 6
            }
        }
    
    def _calculate_white_space_target(
        self,
        formality: str,
        visual_emphasis: float
    ) -> float:
        """Calculate target white space ratio"""
        base = 0.3  # 30% base white space
        
        if formality == "high":
            base += 0.1  # More white space for formal
        
        if visual_emphasis > 0.7:
            base -= 0.1  # Less white space for visual-heavy
        
        return max(0.2, min(0.5, base))
    
    def _define_grid_system(self, keywords: List[str]) -> Dict[str, Any]:
        """Define the grid system"""
        return {
            "columns": 16,
            "rows": 9,
            "gutter": 4,
            "margin": self.BASE_MARGIN,
            "baseline": 4,
            "module_size": 10,
            "breakpoints": {
                "small": 40,
                "medium": 80,
                "large": 120
            }
        }
    
    def _define_spacing_rules(self, formality: str) -> Dict[str, Any]:
        """Define spacing rules"""
        base_unit = 8 if formality == "high" else 6
        
        return {
            "unit": base_unit,
            "scale": {
                "xs": base_unit // 2,
                "sm": base_unit,
                "md": base_unit * 2,
                "lg": base_unit * 3,
                "xl": base_unit * 4,
                "xxl": base_unit * 6
            },
            "component_spacing": {
                "title_to_content": base_unit * 2,
                "between_bullets": base_unit,
                "between_sections": base_unit * 3,
                "visual_padding": base_unit
            }
        }


# Create tool instances
analyze_mood_and_keywords_tool = Tool(
    function=MoodAnalyzer().analyze_mood,
    name="analyze_mood_and_keywords",
    description="Extract actionable mood keywords from theme and design suggestions"
)

generate_color_palette_tool = Tool(
    function=EnhancedColorPaletteGenerator().generate_enhanced_palette,
    name="generate_color_palette",
    description="Generate comprehensive color palette based on mood keywords"
)

find_font_pairing_tool = Tool(
    function=EnhancedFontPairingFinder().find_enhanced_pairing,
    name="find_font_pairing",
    description="Select optimal font pairing based on mood and context"
)

design_layout_templates_tool = Tool(
    function=LayoutTemplateDesigner().design_templates,
    name="design_layout_templates",
    description="Design layout templates for all slide types"
)


# Original classes are already defined in this file for backward compatibility