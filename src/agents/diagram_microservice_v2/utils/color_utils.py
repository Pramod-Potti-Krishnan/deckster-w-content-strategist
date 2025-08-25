"""
Color Utilities for Smart SVG Theming

Provides color manipulation, palette generation, and intelligent color mapping
for SVG diagram templates.
"""

import colorsys
from typing import Dict, List, Tuple, Optional, Any
import re


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color"""
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSL (0-360, 0-100, 0-100)"""
    r, g, b = r/255.0, g/255.0, b/255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convert HSL (0-360, 0-100, 0-100) to RGB"""
    h, s, l = h/360.0, s/100.0, l/100.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return int(r * 255), int(g * 255), int(b * 255)


def adjust_lightness(hex_color: str, percent: float) -> str:
    """Adjust lightness of a color by percentage (-100 to 100)"""
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    l = max(0, min(100, l + percent))
    r, g, b = hsl_to_rgb(h, s, l)
    return rgb_to_hex(r, g, b)


def adjust_saturation(hex_color: str, percent: float) -> str:
    """Adjust saturation of a color by percentage (-100 to 100)"""
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    s = max(0, min(100, s + percent))
    r, g, b = hsl_to_rgb(h, s, l)
    return rgb_to_hex(r, g, b)


def generate_shades(base_color: str, count: int = 5) -> List[str]:
    """Generate shades from a base color"""
    shades = []
    step = 60 / (count - 1)  # Distribute from light to dark
    
    for i in range(count):
        lightness_adjust = 30 - (i * step)  # From +30 to -30
        shades.append(adjust_lightness(base_color, lightness_adjust))
    
    return shades


def get_complementary(hex_color: str) -> str:
    """Get complementary color (opposite on color wheel)"""
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    h = (h + 180) % 360
    r, g, b = hsl_to_rgb(h, s, l)
    return rgb_to_hex(r, g, b)


def get_analogous(hex_color: str) -> Tuple[str, str]:
    """Get two analogous colors (adjacent on color wheel)"""
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    
    h1 = (h + 30) % 360
    h2 = (h - 30) % 360
    
    r1, g1, b1 = hsl_to_rgb(h1, s, l)
    r2, g2, b2 = hsl_to_rgb(h2, s, l)
    
    return rgb_to_hex(r1, g1, b1), rgb_to_hex(r2, g2, b2)


def get_triadic(hex_color: str) -> Tuple[str, str]:
    """Get two triadic colors (120 degrees apart on color wheel)"""
    r, g, b = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(r, g, b)
    
    h1 = (h + 120) % 360
    h2 = (h + 240) % 360
    
    r1, g1, b1 = hsl_to_rgb(h1, s, l)
    r2, g2, b2 = hsl_to_rgb(h2, s, l)
    
    return rgb_to_hex(r1, g1, b1), rgb_to_hex(r2, g2, b2)


class MonochromaticTheme:
    """Monochromatic color theme using shades of a single color"""
    
    def __init__(self, primary_color: str):
        """
        Initialize with a single color
        
        Args:
            primary_color: Base color for generating shades
        """
        self.primary = primary_color.lower()
        self.secondary = None  # Not used in monochromatic
        self.accent = None     # Not used in monochromatic
        self.palette = self._generate_palette()
        self.color_map = self._create_color_map()
    
    def _generate_palette(self) -> Dict[str, List[str]]:
        """Generate monochromatic palette with various shades"""
        palette = {}
        
        # Generate 7 shades from very light to very dark
        # BUT ensure minimum saturation and avoid near-white colors
        palette['primary'] = []
        
        # First ensure the base color has sufficient saturation
        r, g, b = hex_to_rgb(self.primary)
        h, s, l = rgb_to_hsl(r, g, b)
        
        # Ensure minimum saturation of 30%
        if s < 30:
            s = 30
            r, g, b = hsl_to_rgb(h, s, l)
            base_color = rgb_to_hex(r, g, b)
        else:
            base_color = self.primary
        
        for i in range(7):
            # Lightness from 80 to 20 (avoid >80 to prevent near-white)
            target_lightness = 80 - (i * 60 / 6)
            # Adjust from current lightness
            r, g, b = hex_to_rgb(base_color)
            h, s, l = rgb_to_hsl(r, g, b)
            # Maintain saturation, just change lightness
            r, g, b = hsl_to_rgb(h, max(30, s), target_lightness)
            shade = rgb_to_hex(r, g, b)
            palette['primary'].append(shade)
        
        # Also generate slightly desaturated versions for variety (labeled as secondary)
        palette['secondary'] = []
        for i in range(5):
            target_lightness = 70 - (i * 40 / 4)
            # Use base color but reduce saturation slightly
            r, g, b = hex_to_rgb(base_color)
            h, s, l = rgb_to_hsl(r, g, b)
            # Reduce saturation but keep minimum of 20%
            r, g, b = hsl_to_rgb(h, max(20, s - 20), target_lightness)
            shade = rgb_to_hex(r, g, b)
            palette['secondary'].append(shade)
        
        # Even more desaturated for accents
        palette['accent'] = []
        for i in range(3):
            target_lightness = 60 - (i * 30 / 2)
            r, g, b = hex_to_rgb(base_color)
            h, s, l = rgb_to_hsl(r, g, b)
            # Further reduce saturation but keep minimum of 15%
            r, g, b = hsl_to_rgb(h, max(15, s - 30), target_lightness)
            shade = rgb_to_hex(r, g, b)
            palette['accent'].append(shade)
        
        # Neutral grays for text and borders
        gray_base = adjust_saturation(self.primary, -95)
        palette['neutral'] = generate_shades(gray_base, 5)
        
        return palette
    
    def _create_color_map(self) -> Dict[str, str]:
        """Map template colors to monochromatic shades"""
        # This creates a subtle, cohesive look using only primary color variations
        color_map = {}
        
        # All template colors (simplified for brevity - same list as before)
        template_colors = [
            '#ffffff', '#fafafa', '#f8f8f8', '#f5f5f5', '#f0f0f0',
            '#e5e5e5', '#e0e0e0', '#dbeafe', '#d1fae5', '#dcfce7',
            '#cbd5e1', '#bfdbfe', '#bbf7d0', '#93c5fd', '#86efac',
            '#64748b', '#60a5fa', '#3b82f6', '#22c55e', '#1e293b',
            '#2563eb', '#10b981', '#059669', '#0891b2', '#06b6d4',
            '#0e7490', '#14b8a6', '#0d9488', '#f59e0b', '#d97706',
            '#dc2626', '#b91c1c', '#991b1b', '#7f1d1d', '#fbbf24',
            '#f97316', '#fb923c', '#ef4444', '#f87171', '#fca5a5',
            '#fed7aa', '#fde68a', '#fef3c7', '#eff6ff', '#f0f9ff',
            '#475569', '#334155', '#1f2937', '#111827', '#0f172a',
            '#94a3b8', '#e2e8f0', '#f1f5f9', '#f3f4f6', '#e5e7eb',
            '#d1d5db', '#9ca3af', '#6b7280', '#4b5563', '#374151',
            '#1f2937'
        ]
        
        for color in template_colors:
            r, g, b = hex_to_rgb(color)
            h, s, l = rgb_to_hsl(r, g, b)
            
            # Map based on lightness levels with more variation
            if l > 95:
                color_map[color] = '#ffffff'
            elif l > 85:
                # Very light colors - use lightest shade or secondary
                if s < 20:  # Grays
                    color_map[color] = self.palette['neutral'][0]
                else:
                    color_map[color] = self.palette['primary'][0]  # Lightest
            elif l > 70:
                # Light colors - alternate between primary and secondary
                if s < 20:
                    color_map[color] = self.palette['neutral'][1]
                elif hex_to_rgb(color)[0] > hex_to_rgb(color)[1]:  # More red
                    color_map[color] = self.palette['secondary'][0]
                else:
                    color_map[color] = self.palette['primary'][1]
            elif l > 55:
                # Medium-light
                if s < 20:
                    color_map[color] = self.palette['neutral'][2]
                else:
                    color_map[color] = self.palette['primary'][2]
            elif l > 40:
                # Medium
                if s < 20:
                    color_map[color] = self.palette['neutral'][3]
                else:
                    color_map[color] = self.palette['primary'][3]
            elif l > 25:
                # Medium-dark
                if s < 20:
                    color_map[color] = self.palette['neutral'][4]
                else:
                    color_map[color] = self.palette['primary'][4]
            elif l > 15:
                # Dark
                color_map[color] = self.palette['primary'][5]
            else:
                # Very dark
                color_map[color] = self.palette['primary'][6]  # Darkest
        
        return color_map
    
    def apply_to_svg(self, svg_content: str) -> str:
        """Apply monochromatic theme to SVG content"""
        result = svg_content
        sorted_colors = sorted(self.color_map.keys(), key=len, reverse=True)
        
        for old_color, new_color in [(c, self.color_map[c]) for c in sorted_colors]:
            result = result.replace(old_color, new_color)
            result = result.replace(old_color.upper(), new_color.upper())
        
        return result
    
    def get_theme_dict(self) -> Dict[str, Any]:
        """Get theme as dictionary for API response"""
        return {
            "primary": self.primary,
            "secondary": None,  # No secondary in monochromatic
            "accent": None,  # No accent in monochromatic
            "colorScheme": "monochromatic",
            "primaryShades": self.palette['primary'],
            "secondaryShades": self.palette['secondary'],
            "neutralShades": self.palette['neutral'],
            "colorMap": self.color_map
        }


class SmartColorTheme:
    """Smart color theme generator for SVG diagrams (complementary scheme)"""
    
    def __init__(self, primary_color: str, secondary_color: str = None, accent_color: str = None, color_scheme: str = "complementary"):
        """
        Initialize with 1-3 colors
        
        Args:
            primary_color: Main brand color
            secondary_color: Optional secondary color
            accent_color: Optional accent color
            color_scheme: "monochromatic" or "complementary"
        """
        self.primary = primary_color.lower()
        self.color_scheme = color_scheme.lower()
        
        if self.color_scheme == "monochromatic":
            # For monochromatic, ignore secondary and accent
            self.secondary = None
            self.accent = None
        else:
            # For complementary, use provided or generate
            self.secondary = secondary_color.lower() if secondary_color else None
            self.accent = accent_color.lower() if accent_color else None
        
        # Generate full palette
        self.palette = self._generate_palette()
        
        # Create mapping for all template colors
        self.color_map = self._create_color_map()
    
    def _generate_palette(self) -> Dict[str, List[str]]:
        """Generate complete color palette from provided colors"""
        palette = {}
        
        if self.color_scheme == "monochromatic":
            # For monochromatic, generate various shades of primary
            palette['primary'] = []
            for i in range(7):
                lightness_adjust = 40 - (i * 80 / 6)
                shade = adjust_lightness(self.primary, lightness_adjust)
                palette['primary'].append(shade)
            
            # Muted versions for variety
            palette['secondary'] = []
            for i in range(5):
                lightness_adjust = 30 - (i * 60 / 4)
                desaturated = adjust_saturation(self.primary, -30)
                shade = adjust_lightness(desaturated, lightness_adjust)
                palette['secondary'].append(shade)
            
            # Even more muted for accents
            palette['accent'] = []
            for i in range(3):
                lightness_adjust = 20 - (i * 40 / 2)
                desaturated = adjust_saturation(self.primary, -50)
                shade = adjust_lightness(desaturated, lightness_adjust)
                palette['accent'].append(shade)
        else:
            # For complementary, use multiple colors
            palette['primary'] = generate_shades(self.primary, 5)
            
            # Secondary (use complementary if not provided)
            if self.secondary:
                palette['secondary'] = generate_shades(self.secondary, 5)
            else:
                self.secondary = get_complementary(self.primary)
                palette['secondary'] = generate_shades(self.secondary, 5)
            
            # Accent (use triadic if not provided)
            if self.accent:
                palette['accent'] = generate_shades(self.accent, 3)
            else:
                triadic1, triadic2 = get_triadic(self.primary)
                self.accent = triadic1
                palette['accent'] = generate_shades(self.accent, 3)
        
        # Neutral grays (derived from primary with low saturation)
        gray_base = adjust_saturation(self.primary, -90)
        palette['neutral'] = generate_shades(gray_base, 7)
        
        # Success, warning, error colors (adjusted from base colors)
        palette['success'] = generate_shades(adjust_lightness("#22c55e", 0), 3)
        palette['warning'] = generate_shades(adjust_lightness("#f59e0b", 0), 3)
        palette['error'] = generate_shades(adjust_lightness("#ef4444", 0), 3)
        
        return palette
    
    def _create_color_map(self) -> Dict[str, str]:
        """Map all 61 template colors to theme colors"""
        
        # All unique colors found in templates
        template_colors = [
            '#ffffff', '#fafafa', '#f8f8f8', '#f5f5f5', '#f0f0f0',
            '#e5e5e5', '#e0e0e0', '#dbeafe', '#d1fae5', '#dcfce7',
            '#cbd5e1', '#bfdbfe', '#bbf7d0', '#93c5fd', '#86efac',
            '#64748b', '#60a5fa', '#3b82f6', '#22c55e', '#1e293b',
            '#2563eb', '#10b981', '#059669', '#0891b2', '#06b6d4',
            '#0e7490', '#14b8a6', '#0d9488', '#f59e0b', '#d97706',
            '#dc2626', '#b91c1c', '#991b1b', '#7f1d1d', '#fbbf24',
            '#f97316', '#fb923c', '#ef4444', '#f87171', '#fca5a5',
            '#fed7aa', '#fde68a', '#fef3c7', '#eff6ff', '#f0f9ff',
            '#475569', '#334155', '#1f2937', '#111827', '#0f172a',
            '#94a3b8', '#e2e8f0', '#f1f5f9', '#f3f4f6', '#e5e7eb',
            '#d1d5db', '#9ca3af', '#6b7280', '#4b5563', '#374151',
            '#1f2937'
        ]
        
        color_map = {}
        
        # Create a cycle of colors to ensure variety
        color_cycle = []
        if self.color_scheme == "complementary":
            # Use all three color palettes in rotation
            color_cycle = [
                self.palette['primary'][1],
                self.palette['secondary'][1],
                self.palette['accent'][0],
                self.palette['primary'][2],
                self.palette['secondary'][2],
                self.palette['accent'][1],
            ]
        
        cycle_index = 0
        
        for color in template_colors:
            # Categorize by lightness and hue
            r, g, b = hex_to_rgb(color)
            h, s, l = rgb_to_hsl(r, g, b)
            
            # White and very light colors
            if l > 95:
                color_map[color] = '#ffffff'
            
            # Light backgrounds
            elif l > 90:
                color_map[color] = self.palette['neutral'][0]
            
            # Light colored backgrounds - use color cycling for variety
            elif l > 80 and s > 20:
                if self.color_scheme == "complementary":
                    # Cycle through light versions of all palettes
                    color_map[color] = color_cycle[cycle_index % len(color_cycle)]
                    cycle_index += 1
                else:
                    # Monochromatic - use primary
                    color_map[color] = self.palette['primary'][0]
            
            # Medium grays
            elif l > 60 and s < 20:
                color_map[color] = self.palette['neutral'][2]
            
            # Colored elements - ensure variety
            elif s > 30:
                if self.color_scheme == "complementary":
                    # For complementary, distribute colors more evenly
                    # to avoid duplicates
                    if cycle_index % 3 == 0:
                        idx = 2 if l > 50 else 3
                        color_map[color] = self.palette['primary'][min(idx, len(self.palette['primary'])-1)]
                    elif cycle_index % 3 == 1:
                        idx = 2 if l > 50 else 3
                        color_map[color] = self.palette['secondary'][min(idx, len(self.palette['secondary'])-1)]
                    else:
                        idx = 1 if l > 50 else 2
                        color_map[color] = self.palette['accent'][min(idx, len(self.palette['accent'])-1)]
                    cycle_index += 1
                else:
                    # Monochromatic - use primary shades
                    idx = 2 if l > 50 else 3
                    color_map[color] = self.palette['primary'][idx]
            
            # Dark grays and blacks
            elif l < 30:
                color_map[color] = self.palette['neutral'][5] if len(self.palette['neutral']) > 5 else self.palette['neutral'][-1]
            elif l < 40:
                color_map[color] = self.palette['neutral'][4] if len(self.palette['neutral']) > 4 else self.palette['neutral'][-1]
            else:
                color_map[color] = self.palette['neutral'][3] if len(self.palette['neutral']) > 3 else self.palette['neutral'][-1]
        
        return color_map
    
    def apply_to_svg(self, svg_content: str) -> str:
        """Apply theme colors to SVG content"""
        result = svg_content
        
        # Sort by length to avoid partial replacements
        sorted_colors = sorted(self.color_map.keys(), key=len, reverse=True)
        
        for old_color, new_color in [(c, self.color_map[c]) for c in sorted_colors]:
            # Replace both lowercase and uppercase versions
            result = result.replace(old_color, new_color)
            result = result.replace(old_color.upper(), new_color.upper())
        
        return result
    
    def get_theme_dict(self) -> Dict[str, str]:
        """Get theme as dictionary for API response"""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "primaryShades": self.palette['primary'],
            "secondaryShades": self.palette['secondary'],
            "accentShades": self.palette['accent'],
            "neutralShades": self.palette['neutral'],
            "colorMap": self.color_map
        }


def calculate_luminance(hex_color: str) -> float:
    """
    Calculate relative luminance of a color (0.0 = black, 1.0 = white)
    Uses the WCAG formula for relative luminance
    """
    r, g, b = hex_to_rgb(hex_color)
    
    # Convert to 0-1 range
    r, g, b = r/255.0, g/255.0, b/255.0
    
    # Apply gamma correction
    r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
    g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
    b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
    
    # Calculate luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_color(background_color: str, light_color: str = "#ffffff", dark_color: str = "#000000") -> str:
    """
    Get contrasting text color (black or white) based on background luminance
    
    Args:
        background_color: Background color in hex format
        light_color: Color to use on dark backgrounds (default white)
        dark_color: Color to use on light backgrounds (default black)
        
    Returns:
        Either light_color or dark_color based on background luminance
    """
    luminance = calculate_luminance(background_color)
    # Use 0.5 as threshold (can be adjusted for preference)
    return light_color if luminance < 0.5 else dark_color


def is_dark_color(hex_color: str) -> bool:
    """Check if a color is considered dark (luminance < 0.5)"""
    return calculate_luminance(hex_color) < 0.5


def extract_colors_from_svg(svg_content: str) -> List[str]:
    """Extract all color values from SVG content"""
    colors = set()
    
    # Find hex colors
    hex_pattern = r'#[0-9a-fA-F]{6}'
    colors.update(re.findall(hex_pattern, svg_content))
    
    # Find rgb colors
    rgb_pattern = r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
    for match in re.finditer(rgb_pattern, svg_content):
        r, g, b = match.groups()
        colors.add(rgb_to_hex(int(r), int(g), int(b)))
    
    return list(colors)


def validate_color_contrast(color1: str, color2: str, min_ratio: float = 1.5) -> bool:
    """
    Validate that two colors have sufficient contrast
    
    Args:
        color1: First color in hex format
        color2: Second color in hex format
        min_ratio: Minimum contrast ratio required (default 1.5)
    
    Returns:
        True if contrast is sufficient, False otherwise
    """
    lum1 = calculate_luminance(color1)
    lum2 = calculate_luminance(color2)
    
    # Calculate contrast ratio
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    # Avoid division by zero
    if darker == 0:
        darker = 0.001
    
    ratio = (lighter + 0.05) / (darker + 0.05)
    return ratio >= min_ratio


def ensure_color_visibility(color: str, background: str = "#ffffff") -> str:
    """
    Ensure a color is visible against a background
    
    Args:
        color: Color to validate/adjust
        background: Background color (default white)
    
    Returns:
        Adjusted color if needed, or original if already visible
    """
    if not validate_color_contrast(color, background, 1.3):
        # Color is too similar to background, adjust it
        r, g, b = hex_to_rgb(color)
        h, s, l = rgb_to_hsl(r, g, b)
        
        # If color is too light, darken it
        if l > 85:
            l = 60
            s = max(30, s)  # Ensure some saturation
        # If color is too dark for dark background
        elif l < 15 and calculate_luminance(background) < 0.5:
            l = 40
            s = max(30, s)
        
        r, g, b = hsl_to_rgb(h, s, l)
        return rgb_to_hex(r, g, b)
    
    return color