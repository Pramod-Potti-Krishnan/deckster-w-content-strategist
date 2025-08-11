"""
Data models for Layout Architect MVP.

These models are designed to be compatible with WebSocket Phase 2 protocol
while maintaining simplicity and clarity.
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class LayoutArrangement(str, Enum):
    """Available layout arrangements."""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"
    AUTO = "auto"


class GridPosition(BaseModel):
    """Integer-based grid position following 160x90 grid system."""
    leftInset: int = Field(description="X position in grid units")
    topInset: int = Field(description="Y position in grid units")
    width: int = Field(description="Width in grid units")
    height: int = Field(description="Height in grid units")
    
    def validate_integers(self) -> bool:
        """Ensure all positions are integers."""
        return all(isinstance(v, int) for v in [
            self.leftInset, self.topInset, self.width, self.height
        ])


class ContainerContent(BaseModel):
    """Content specification for a container (Phase 2 compatible)."""
    type: Literal["text", "placeholder", "image", "chart", "table"]
    text: Optional[str] = None
    style: Optional[str] = None  # h1, h2, h3, body, caption
    placeholder_type: Optional[str] = None
    loading_state: Optional[Dict[str, Any]] = None


class MVPContainer(BaseModel):
    """Container with WebSocket Phase 2 protocol support."""
    name: str = Field(description="Container identifier (e.g., 'title', 'body')")
    content: ContainerContent
    position: Optional[GridPosition] = Field(default=None, description="Custom position or from_theme")
    contributor: Optional[str] = Field(default="layout_architect")
    
    def model_dump(self, **kwargs):
        """Custom serialization to handle GridPosition."""
        data = super().model_dump(**kwargs)
        if 'position' in data and data['position'] is None:
            data['position'] = "from_theme"
        return data


class LayoutHints(BaseModel):
    """Layout hints for Phase 3 agents."""
    content_density: Literal["low", "medium", "high"] = "medium"
    visual_emphasis: float = Field(ge=0, le=1, default=0.5)
    preferred_flow: Literal["vertical", "horizontal", "grid"] = "vertical"


class LayoutSpec(BaseModel):
    """Layout specification for WebSocket protocol."""
    source: Literal["theme", "custom"] = "theme"
    layout_hints: LayoutHints


class ContentState(BaseModel):
    """Track content generation state for progressive updates."""
    base_content: Literal["pending", "complete"] = "complete"
    layout: Literal["pending", "processing", "complete", "error"] = "pending"
    research: Literal["pending", "not_applicable"] = "not_applicable"
    visuals: Literal["pending", "not_applicable"] = "not_applicable"
    charts: Literal["pending", "not_applicable"] = "not_applicable"


class MVPLayout(BaseModel):
    """Layout for a single slide with Phase 2 support."""
    slide_id: str
    slide_number: int
    slide_type: str
    layout: str = Field(description="Theme layout reference (e.g., 'titleSlide')")
    layout_spec: LayoutSpec
    containers: List[MVPContainer]
    content_state: ContentState
    white_space_ratio: float = Field(ge=0, le=1)
    alignment_score: float = Field(ge=0, le=1)
    # Strawman fields for validation and debugging
    slide_title: Optional[str] = None
    strawman_structure_preference: Optional[str] = None
    
    def to_websocket_format(self) -> Dict[str, Any]:
        """Convert to WebSocket slide_update format."""
        result = {
            "slide_id": self.slide_id,
            "slide_number": self.slide_number,
            "slide_type": self.slide_type,
            "layout": self.layout,
            "layout_spec": self.layout_spec.dict(),
            "containers": [c.model_dump() for c in self.containers],
            "content_state": self.content_state.dict()
        }
        # Include strawman fields if available
        if self.slide_title:
            result["slide_title"] = self.slide_title
        if self.strawman_structure_preference:
            result["strawman_structure_preference"] = self.strawman_structure_preference
        return result


class ThemeTypography(BaseModel):
    """Typography specification for theme."""
    fontSize: int
    fontFamily: str = "Inter"
    fontWeight: Literal["normal", "medium", "bold"] = "normal"
    lineHeight: Optional[float] = None
    letterSpacing: Optional[float] = None


class ThemeColors(BaseModel):
    """Color palette for theme."""
    primary: str = Field(pattern="^#[0-9A-Fa-f]{6}$")
    secondary: str = Field(pattern="^#[0-9A-Fa-f]{6}$")
    background: str = Field(pattern="^#[0-9A-Fa-f]{6}$")
    text: str = Field(pattern="^#[0-9A-Fa-f]{6}$", default="#000000")
    accent: Optional[str] = Field(pattern="^#[0-9A-Fa-f]{6}$", default=None)


class ThemeLayout(BaseModel):
    """Layout definition for a specific slide type."""
    containers: Dict[str, GridPosition]


class ThemeConfig(BaseModel):
    """Complete theme configuration (Phase 2 compatible)."""
    layouts: Dict[str, ThemeLayout]
    typography: Dict[str, ThemeTypography]
    colors: ThemeColors


class MVPTheme(BaseModel):
    """Theme following Phase 2 WebSocket structure."""
    theme_name: str
    theme_config: ThemeConfig
    created_for_session: str
    # Strawman fields that guided theme generation
    strawman_overall_theme: Optional[str] = None
    strawman_design_suggestions: Optional[str] = None
    strawman_target_audience: Optional[str] = None
    
    def to_websocket_format(self) -> Dict[str, Any]:
        """Convert to WebSocket theme_update format."""
        result = {
            "theme_name": self.theme_name,
            "theme_config": self.theme_config.dict(),
            "delivery_timing": "before_slides"
        }
        # Include strawman fields if available
        if self.strawman_overall_theme:
            result["strawman_overall_theme"] = self.strawman_overall_theme
        if self.strawman_design_suggestions:
            result["strawman_design_suggestions"] = self.strawman_design_suggestions
        if self.strawman_target_audience:
            result["strawman_target_audience"] = self.strawman_target_audience
        return result


class LayoutConfig(BaseModel):
    """Configuration for Layout Architect MVP."""
    # Grid system
    grid_width: int = 160
    grid_height: int = 90
    margin: int = 8
    gutter: int = 4
    
    # White space
    white_space_min: float = 0.3
    white_space_max: float = 0.5
    
    # AI Structure Analysis
    enable_ai_structure_analysis: bool = True
    
    # Alignment
    enable_grid_snap: bool = True
    alignment_tolerance: int = 0  # Must be exact for MVP
    
    # Layout selection
    auto_arrange: bool = True
    max_columns: int = 3
    max_rows: int = 3
    
    # Model settings
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.7


class AlignmentInfo(BaseModel):
    """Track alignment information for validation."""
    row_groups: Dict[int, List[str]] = Field(default_factory=dict)
    column_groups: Dict[int, List[str]] = Field(default_factory=dict)
    dimension_groups: Dict[str, List[str]] = Field(default_factory=dict)
    
    def add_to_row(self, y: int, container_id: str):
        """Add container to row group."""
        if y not in self.row_groups:
            self.row_groups[y] = []
        self.row_groups[y].append(container_id)
    
    def add_to_column(self, x: int, container_id: str):
        """Add container to column group."""
        if x not in self.column_groups:
            self.column_groups[x] = []
        self.column_groups[x].append(container_id)
    
    def add_to_dimension_group(self, key: str, container_id: str):
        """Add container to dimension group."""
        if key not in self.dimension_groups:
            self.dimension_groups[key] = []
        self.dimension_groups[key].append(container_id)