"""
Layout engine for positioning containers with different arrangements.

Supports vertical, horizontal, and grid layouts with automatic selection
based on content characteristics.
"""

from typing import List, Optional, Tuple
from enum import Enum

from src.models.agents import Slide
from src.utils.logger import setup_logger
from .models import (
    MVPLayout, MVPContainer, MVPTheme, LayoutArrangement,
    GridPosition, ContainerContent, LayoutSpec, LayoutHints,
    ContentState, LayoutConfig, AlignmentInfo
)
from .structure_analyzer import StructureAnalyzer, StructureAnalysis

logger = setup_logger(__name__)


class LayoutEngine:
    """Engine for creating professional layouts with various arrangements."""
    
    def __init__(self, config: LayoutConfig):
        """Initialize layout engine with configuration."""
        self.config = config
        self.margin = config.margin
        self.gutter = config.gutter
        self.grid_width = config.grid_width
        self.grid_height = config.grid_height
        
        # Initialize structure analyzer if enabled
        self.use_ai_structure = config.enable_ai_structure_analysis if hasattr(config, 'enable_ai_structure_analysis') else False
        self.structure_analyzer = StructureAnalyzer() if self.use_ai_structure else None
    
    async def process_slide(
        self,
        slide: Slide,
        theme: MVPTheme,
        arrangement: LayoutArrangement = LayoutArrangement.AUTO
    ) -> MVPLayout:
        """Process slide and create layout with specified arrangement."""
        try:
            # Determine layout name based on slide type
            layout_name = self._get_layout_name(slide.slide_type)
            
            # Get or create containers
            containers = await self._create_containers(slide, theme, layout_name)
            
            # Analyze structure with AI if enabled
            structure_analysis = None
            if self.use_ai_structure and self.structure_analyzer:
                try:
                    structure_analysis = await self.structure_analyzer.analyze_structure(
                        slide,
                        slide.structure_preference if hasattr(slide, 'structure_preference') else None
                    )
                    logger.info(f"AI Structure Analysis for slide {slide.slide_id}: {structure_analysis.arrangement} - {structure_analysis.rationale}")
                except Exception as e:
                    logger.warning(f"AI structure analysis failed: {e}, falling back to regular logic")
            
            # Determine arrangement if auto
            if arrangement == LayoutArrangement.AUTO:
                if structure_analysis:
                    arrangement = structure_analysis.arrangement
                else:
                    arrangement = self._determine_arrangement(containers, slide)
            
            # Position containers based on arrangement
            positioned_containers = self._position_containers(
                containers, arrangement, slide.slide_type
            )
            
            # Calculate metrics
            white_space_ratio = self._calculate_white_space(positioned_containers)
            alignment_score = self._calculate_alignment_score(positioned_containers)
            
            # Create layout spec
            layout_spec = LayoutSpec(
                source="custom" if slide.slide_type == "content_heavy" else "theme",
                layout_hints=LayoutHints(
                    content_density=self._get_content_density(slide),
                    visual_emphasis=0.3 if slide.visuals_needed else 0.7,
                    preferred_flow=arrangement.value
                )
            )
            
            return MVPLayout(
                slide_id=slide.slide_id,
                slide_number=slide.slide_number,
                slide_type=slide.slide_type,
                layout=layout_name,
                layout_spec=layout_spec,
                containers=positioned_containers,
                content_state=ContentState(layout="complete"),
                white_space_ratio=white_space_ratio,
                alignment_score=alignment_score,
                slide_title=slide.title,
                strawman_structure_preference=slide.structure_preference if hasattr(slide, 'structure_preference') else None
            )
            
        except Exception as e:
            logger.error(f"Layout processing failed for slide {slide.slide_id}: {e}")
            # Return fallback layout
            return self._create_fallback_layout(slide, theme)
    
    def _get_layout_name(self, slide_type: str) -> str:
        """Map slide type to theme layout name."""
        mapping = {
            "title_slide": "titleSlide",
            "section_header": "sectionHeader",
            "content_heavy": "contentSlide",
            "visual_heavy": "contentSlide",
            "data_driven": "contentSlide",
            "interactive": "contentSlide",
            "conclusion": "contentSlide"
        }
        return mapping.get(slide_type, "contentSlide")
    
    async def _create_containers(
        self,
        slide: Slide,
        theme: MVPTheme,
        layout_name: str
    ) -> List[MVPContainer]:
        """Create containers from slide content."""
        containers = []
        
        # Title container
        if slide.title:
            containers.append(MVPContainer(
                name="title",
                content=ContainerContent(
                    type="text",
                    text=slide.title,
                    style="h2" if slide.slide_type != "title_slide" else "h1"
                )
            ))
        
        # Content containers based on slide type
        if slide.slide_type == "title_slide":
            # Add subtitle if narrative exists
            if slide.narrative:
                containers.append(MVPContainer(
                    name="subtitle",
                    content=ContainerContent(
                        type="text",
                        text=slide.narrative,
                        style="h3"
                    )
                ))
        else:
            # Add body containers for key points with semantic naming
            for i, point in enumerate(slide.key_points):
                # Determine semantic name based on content
                container_name = self._get_semantic_container_name(point, i, slide)
                
                containers.append(MVPContainer(
                    name=container_name,
                    content=ContainerContent(
                        type="text",
                        text=point,
                        style="body"
                    )
                ))
            
            # Add placeholder for visuals if needed
            if slide.visuals_needed:
                visual_name = self._get_visual_container_name(slide.visuals_needed)
                containers.append(MVPContainer(
                    name=visual_name,
                    content=ContainerContent(
                        type="placeholder",
                        placeholder_type="image",
                        loading_state={
                            "message": "Visual content will be added",
                            "agent": "visual_designer",
                            "estimated_time": 15
                        }
                    )
                ))
            
            # Add placeholder for diagrams if needed
            if hasattr(slide, 'diagrams_needed') and slide.diagrams_needed:
                diagram_name = self._get_diagram_container_name(slide.diagrams_needed)
                containers.append(MVPContainer(
                    name=diagram_name,
                    content=ContainerContent(
                        type="placeholder",
                        placeholder_type="diagram",
                        loading_state={
                            "message": "Diagram will be generated",
                            "agent": "diagram_creator",
                            "estimated_time": 20
                        }
                    )
                ))
            
            # Add placeholder for analytics/charts if needed
            if hasattr(slide, 'analytics_needed') and slide.analytics_needed:
                chart_name = self._get_chart_container_name(slide.analytics_needed)
                containers.append(MVPContainer(
                    name=chart_name,
                    content=ContainerContent(
                        type="placeholder",
                        placeholder_type="chart",
                        loading_state={
                            "message": "Chart will be generated",
                            "agent": "data_visualizer",
                            "estimated_time": 25
                        }
                    )
                ))
        
        return containers
    
    def _determine_arrangement(
        self,
        containers: List[MVPContainer],
        slide: Slide
    ) -> LayoutArrangement:
        """Automatically determine best arrangement based on content."""
        content_count = len(containers)
        has_visual = any(c.name == "visual" for c in containers)
        
        # Check structure_preference first
        if hasattr(slide, 'structure_preference') and slide.structure_preference:
            pref = slide.structure_preference.lower()
            logger.info(f"[DEBUG LayoutEngine] Slide {slide.slide_id} has structure_preference: {slide.structure_preference}")
            
            # Map common preferences to arrangements
            if any(term in pref for term in ["two-column", "two column", "2-column", "split"]):
                return LayoutArrangement.HORIZONTAL
            elif any(term in pref for term in ["three-column", "three column", "3-column", "triple"]):
                # Three-column layout uses horizontal arrangement with 3 containers
                return LayoutArrangement.HORIZONTAL
            elif any(term in pref for term in ["grid", "quadrant", "matrix", "2x2"]):
                return LayoutArrangement.GRID
            elif any(term in pref for term in ["vertical", "list", "stacked", "linear"]):
                return LayoutArrangement.VERTICAL
            elif any(term in pref for term in ["hero", "full-bleed", "centered", "visual-centered", "focal"]):
                # For hero/visual-centered layouts, use vertical with large visual
                return LayoutArrangement.VERTICAL
        
        # Title slides are always vertical
        if slide.slide_type in ["title_slide", "section_header"]:
            return LayoutArrangement.VERTICAL
        
        # Single or two items: vertical
        if content_count <= 2:
            return LayoutArrangement.VERTICAL
        
        # Visual + text: horizontal
        if has_visual and content_count == 2:
            return LayoutArrangement.HORIZONTAL
        
        # 3-4 items: grid or horizontal
        if 3 <= content_count <= 4:
            return LayoutArrangement.GRID if content_count == 4 else LayoutArrangement.HORIZONTAL
        
        # 5+ items: grid
        if content_count >= 5:
            return LayoutArrangement.GRID
        
        # Default to vertical
        return LayoutArrangement.VERTICAL
    
    def _position_containers(
        self,
        containers: List[MVPContainer],
        arrangement: LayoutArrangement,
        slide_type: str
    ) -> List[MVPContainer]:
        """Position containers based on arrangement."""
        # Calculate work area
        work_area = {
            'x': self.margin,
            'y': self.margin,
            'width': self.grid_width - (2 * self.margin),
            'height': self.grid_height - (2 * self.margin)
        }
        
        # Route to appropriate positioning method
        if arrangement == LayoutArrangement.VERTICAL:
            return self._position_vertical(containers, work_area)
        elif arrangement == LayoutArrangement.HORIZONTAL:
            return self._position_horizontal(containers, work_area)
        elif arrangement == LayoutArrangement.GRID:
            return self._position_grid(containers, work_area)
        else:
            return self._position_vertical(containers, work_area)
    
    def _position_vertical(
        self,
        containers: List[MVPContainer],
        work_area: dict
    ) -> List[MVPContainer]:
        """Position containers in vertical arrangement."""
        positioned = []
        current_y = work_area['y']
        
        # Reserve space for title if present
        title_container = next((c for c in containers if c.name == "title"), None)
        if title_container:
            title_container.position = GridPosition(
                leftInset=work_area['x'],
                topInset=current_y,
                width=work_area['width'],
                height=12
            )
            positioned.append(title_container)
            current_y += 12 + self.gutter
        
        # Position remaining containers
        remaining = [c for c in containers if c.name != "title"]
        if remaining:
            available_height = work_area['height'] - (current_y - work_area['y'])
            container_height = (available_height - (len(remaining) - 1) * self.gutter) // len(remaining)
            container_height = min(container_height, 20)  # Cap height
            
            for container in remaining:
                container.position = GridPosition(
                    leftInset=work_area['x'],
                    topInset=current_y,
                    width=work_area['width'],
                    height=container_height
                )
                positioned.append(container)
                current_y += container_height + self.gutter
        
        return positioned
    
    def _position_horizontal(
        self,
        containers: List[MVPContainer],
        work_area: dict
    ) -> List[MVPContainer]:
        """Position containers in horizontal arrangement."""
        positioned = []
        
        # Handle title separately
        title_container = next((c for c in containers if c.name == "title"), None)
        content_y = work_area['y']
        
        if title_container:
            title_container.position = GridPosition(
                leftInset=work_area['x'],
                topInset=content_y,
                width=work_area['width'],
                height=12
            )
            positioned.append(title_container)
            content_y += 12 + self.gutter
        
        # Position remaining containers horizontally
        remaining = [c for c in containers if c.name != "title"]
        if remaining:
            available_width = work_area['width'] - (len(remaining) - 1) * self.gutter
            container_width = available_width // len(remaining)
            available_height = work_area['height'] - (content_y - work_area['y'])
            
            current_x = work_area['x']
            for container in remaining:
                container.position = GridPosition(
                    leftInset=current_x,
                    topInset=content_y,
                    width=container_width,
                    height=available_height
                )
                positioned.append(container)
                current_x += container_width + self.gutter
        
        return positioned
    
    def _position_grid(
        self,
        containers: List[MVPContainer],
        work_area: dict
    ) -> List[MVPContainer]:
        """Position containers in grid arrangement."""
        positioned = []
        
        # Handle title separately
        title_container = next((c for c in containers if c.name == "title"), None)
        content_y = work_area['y']
        
        if title_container:
            title_container.position = GridPosition(
                leftInset=work_area['x'],
                topInset=content_y,
                width=work_area['width'],
                height=12
            )
            positioned.append(title_container)
            content_y += 12 + self.gutter
        
        # Position remaining in grid
        remaining = [c for c in containers if c.name != "title"]
        if remaining:
            # Determine grid dimensions
            count = len(remaining)
            cols = min(3, count)
            rows = (count + cols - 1) // cols
            
            available_width = work_area['width'] - (cols - 1) * self.gutter
            available_height = work_area['height'] - (content_y - work_area['y'])
            
            cell_width = available_width // cols
            cell_height = (available_height - (rows - 1) * self.gutter) // rows
            cell_height = min(cell_height, 25)  # Cap height
            
            for i, container in enumerate(remaining):
                row = i // cols
                col = i % cols
                
                container.position = GridPosition(
                    leftInset=work_area['x'] + col * (cell_width + self.gutter),
                    topInset=content_y + row * (cell_height + self.gutter),
                    width=cell_width,
                    height=cell_height
                )
                positioned.append(container)
        
        return positioned
    
    def _calculate_white_space(self, containers: List[MVPContainer]) -> float:
        """Calculate white space ratio."""
        total_area = self.grid_width * self.grid_height
        used_area = sum(
            c.position.width * c.position.height
            for c in containers
            if c.position
        )
        return (total_area - used_area) / total_area
    
    def _calculate_alignment_score(self, containers: List[MVPContainer]) -> float:
        """Calculate alignment score based on row/column alignment."""
        if len(containers) < 2:
            return 1.0
        
        alignment_info = AlignmentInfo()
        
        # Group containers by position
        for container in containers:
            if container.position:
                alignment_info.add_to_row(container.position.topInset, container.name)
                alignment_info.add_to_column(container.position.leftInset, container.name)
        
        # Calculate score based on alignment groups
        total_containers = len(containers)
        aligned_containers = max(
            len(group) for group in alignment_info.row_groups.values()
        )
        
        return aligned_containers / total_containers
    
    def _get_content_density(self, slide: Slide) -> str:
        """Determine content density from slide."""
        point_count = len(slide.key_points)
        if point_count <= 3:
            return "low"
        elif point_count <= 5:
            return "medium"
        else:
            return "high"
    
    def _get_semantic_container_name(self, content: str, index: int, slide: Slide) -> str:
        """Generate semantic container name based on content analysis."""
        content_lower = content.lower()
        
        # Check for questions
        if "?" in content:
            return f"discussion_{index + 1}"
        
        # Check for action items (common action verbs)
        action_verbs = ["reduce", "reuse", "recycle", "create", "build", "implement", 
                       "develop", "design", "analyze", "research", "collaborate",
                       "turn off", "use", "make", "take", "start", "stop"]
        if any(content_lower.startswith(verb) for verb in action_verbs):
            return f"action_{index + 1}"
        
        # Check for step-by-step content
        if any(content_lower.startswith(f"{num}.") for num in range(1, 10)):
            return f"step_{index + 1}"
        
        # Check for specific content patterns
        if "impact" in content_lower or "effect" in content_lower:
            return f"impact_{index + 1}"
        elif "challenge" in content_lower or "problem" in content_lower:
            return f"challenge_{index + 1}"
        elif "solution" in content_lower or "opportunity" in content_lower:
            return f"solution_{index + 1}"
        elif "benefit" in content_lower or "advantage" in content_lower:
            return f"benefit_{index + 1}"
        elif "example" in content_lower or "case" in content_lower:
            return f"example_{index + 1}"
        
        # Check slide type for context
        if slide.slide_type == "data_driven":
            return f"data_point_{index + 1}"
        elif slide.slide_type == "content_heavy" and ":" in content:
            # For definition-style content
            return f"definition_{index + 1}"
        
        # Default to generic body naming
        return f"point_{index + 1}"
    
    def _get_visual_container_name(self, visual_description: str) -> str:
        """Generate semantic name for visual container."""
        desc_lower = visual_description.lower()
        
        if "grid" in desc_lower or "collage" in desc_lower:
            return "visual_grid"
        elif "hero" in desc_lower or "main" in desc_lower:
            return "hero_visual"
        elif "icon" in desc_lower:
            return "icon_set"
        elif "photo" in desc_lower or "image" in desc_lower:
            return "main_image"
        else:
            return "visual_content"
    
    def _get_diagram_container_name(self, diagram_description: str) -> str:
        """Generate semantic name for diagram container."""
        desc_lower = diagram_description.lower()
        
        if "flow" in desc_lower or "process" in desc_lower:
            return "process_flow"
        elif "comparison" in desc_lower or "versus" in desc_lower:
            return "comparison_diagram"
        elif "timeline" in desc_lower:
            return "timeline"
        elif "hierarchy" in desc_lower or "org" in desc_lower:
            return "hierarchy_diagram"
        else:
            return "main_diagram"
    
    def _get_chart_container_name(self, chart_description: str) -> str:
        """Generate semantic name for chart container."""
        desc_lower = chart_description.lower()
        
        if "bar" in desc_lower:
            return "bar_chart"
        elif "line" in desc_lower or "trend" in desc_lower:
            return "trend_chart"
        elif "pie" in desc_lower or "distribution" in desc_lower:
            return "distribution_chart"
        elif "comparison" in desc_lower:
            return "comparison_chart"
        else:
            return "data_chart"
    
    def _create_fallback_layout(self, slide: Slide, theme: MVPTheme) -> MVPLayout:
        """Create fallback layout using theme defaults."""
        layout_name = self._get_layout_name(slide.slide_type)
        
        containers = [
            MVPContainer(
                name="title",
                content=ContainerContent(
                    type="text",
                    text=slide.title or "Untitled",
                    style="h2"
                )
            ),
            MVPContainer(
                name="body",
                content=ContainerContent(
                    type="text",
                    text=" ".join(slide.key_points),
                    style="body"
                )
            )
        ]
        
        return MVPLayout(
            slide_id=slide.slide_id,
            slide_number=slide.slide_number,
            slide_type=slide.slide_type,
            layout=layout_name,
            layout_spec=LayoutSpec(source="theme"),
            containers=containers,
            content_state=ContentState(layout="complete"),
            white_space_ratio=0.4,
            alignment_score=1.0,
            slide_title=slide.title,
            strawman_structure_preference=slide.structure_preference if hasattr(slide, 'structure_preference') else None
        )