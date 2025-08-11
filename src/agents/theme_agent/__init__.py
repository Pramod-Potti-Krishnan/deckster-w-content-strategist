"""Theme Agent - Brand & Style Director for presentation design systems."""

from .agent import SimplifiedThemeAgent, ThemeAgent
from .agent_no_tools import ToolFreeThemeAgent
from .tools import (
    EnhancedColorPaletteGenerator,
    PresentationFontPairing,
    generate_color_palette_tool,
    find_font_pairing_tool,
    ColorPaletteInput,
    FontPairingInput,
    # Backward compatibility imports
    ColorPaletteGenerator,
    FontPairingFinder,
    LayoutTemplateDesigner
)

__all__ = [
    'SimplifiedThemeAgent',
    'ThemeAgent',  # Backward compatibility alias
    'ToolFreeThemeAgent',
    'EnhancedColorPaletteGenerator',
    'PresentationFontPairing',
    'generate_color_palette_tool',
    'find_font_pairing_tool',
    'ColorPaletteInput',
    'FontPairingInput',
    # Backward compatibility exports
    'ColorPaletteGenerator',
    'FontPairingFinder',
    'LayoutTemplateDesigner'
]