"""
SVG Diagram Agent - Template-Based Diagram Generation
====================================================

This agent handles SVG template-based diagram generation using
pydantic_ai tools for XML manipulation and theme application.

Fast, deterministic, and presentation-ready.

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
import re

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from src.utils.model_utils import create_model_with_fallback
from .models import DiagramSpec, SVGOutput, SVGTemplateSpec

logger = logging.getLogger(__name__)


class SVGContext(BaseModel):
    """Context for SVG generation."""
    spec: DiagramSpec
    template_path: str
    theme_colors: Dict[str, str]
    font_family: str = "Inter, system-ui, sans-serif"


class SVGDiagramAgent:
    """
    Agent for generating diagrams using SVG templates.
    Uses pydantic_ai tools for template manipulation.
    """
    
    def __init__(self):
        """Initialize the SVG diagram agent."""
        self.template_base = Path(__file__).parent / "templates"
        try:
            self.agent = self._create_agent()
        except Exception as e:
            logger.warning(f"Could not initialize pydantic_ai agent: {e}")
            self.agent = None
        
        # Tools are defined as methods below with @self.agent.tool decorator
    
    def _create_agent(self) -> Agent:
        """Create the pydantic_ai agent."""
        return Agent(
            create_model_with_fallback("gemini-2.5-flash"),
            result_type=SVGTemplateSpec,
            system_prompt="""You are an SVG template specialist. Your job is to:
            1. Analyze the diagram requirements
            2. Map data to template placeholders
            3. Apply theme colors appropriately
            4. Ensure text fits within boundaries
            
            Focus on creating clean, professional diagrams that are accessible and visually appealing."""
        )
    
    async def generate(self, spec: DiagramSpec) -> SVGOutput:
        """
        Generate an SVG diagram from a template.
        
        Args:
            spec: Diagram specification
            
        Returns:
            SVGOutput with the generated diagram
        """
        logger.info(f"Generating SVG diagram of type: {spec.diagram_type}")
        
        # Determine template
        template_name = self._get_template_name(spec.diagram_type)
        template_path = self.template_base / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        # Extract theme colors
        theme_colors = self._extract_theme_colors(spec.theme)
        
        # Create context
        context = SVGContext(
            spec=spec,
            template_path=str(template_path),
            theme_colors=theme_colors
        )
        
        # Try to extract actual labels from content first
        text_replacements = self._extract_text_from_content(spec.diagram_type, spec.content)
        
        if text_replacements:
            # We have explicit text, use it directly
            color_replacements = self._get_color_replacements(spec.diagram_type, theme_colors)
            template_spec = SVGTemplateSpec(
                template_name=template_name,
                text_replacements=text_replacements,
                color_replacements=color_replacements
            )
            print(f"Using extracted text replacements: {text_replacements}")
        else:
            # Fall back to agent generation
            prompt = f"""Create an SVG template specification for this diagram:
            
            Type: {spec.diagram_type}
            Content: {spec.content}
            Template: {template_name}
            
            Map the content to template placeholders and specify color replacements."""
            
            result = await self.agent.run(prompt, deps=context)
            template_spec = result.data
        
        # Apply template specification
        svg_content = await self._apply_template_spec(
            template_path,
            template_spec,
            context
        )
        
        return SVGOutput(
            svg_content=svg_content,
            template_name=template_name,
            elements_modified=len(template_spec.text_replacements) + len(template_spec.color_replacements),
            validation_passed=True
        )
    
    def _get_template_name(self, diagram_type: str) -> str:
        """Get the template file name for a diagram type."""
        template_mapping = {
            "pyramid": "pyramid_3_level.svg",
            "funnel": "funnel_5_stage.svg",
            "matrix_2x2": "matrix_2x2.svg",
            "matrix": "matrix_2x2.svg",
            "timeline": "timeline_horizontal.svg",
            "cycle": "cycle_4_step.svg",
            "venn": "venn_2_circle.svg",
            "hub_spoke": "hub_spoke_6.svg",
            "honeycomb": "honeycomb_7.svg",
            "swot": "swot_matrix.svg",
            "process_flow": "process_flow_5.svg",
            "process": "process_flow_5.svg",
        }
        
        return template_mapping.get(diagram_type, f"{diagram_type}.svg")
    
    def _extract_theme_colors(self, theme: Any) -> Dict[str, str]:
        """Extract color values from theme."""
        colors = {}
        
        # Extract from theme object (adjust based on actual ThemeDefinition structure)
        if hasattr(theme, 'colors'):
            for key, value in theme.colors.items():
                colors[key] = value
        elif isinstance(theme, dict) and 'colors' in theme:
            colors = theme['colors']
        
        # Provide defaults if needed
        if "primary" not in colors:
            colors["primary"] = "#2563eb"
        if "secondary" not in colors:
            colors["secondary"] = "#64748b"
        if "accent" not in colors:
            colors["accent"] = "#f59e0b"
        if "background" not in colors:
            colors["background"] = "#ffffff"
        if "text" not in colors:
            colors["text"] = "#1e293b"
        
        return colors
    
    async def _apply_template_spec(
        self,
        template_path: Path,
        spec: SVGTemplateSpec,
        context: SVGContext
    ) -> str:
        """Apply the template specification to generate SVG."""
        # Load template
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        # Apply color replacements first to determine text colors
        for element_id, color in spec.color_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                elem.set('fill', color)
                # Also set stroke if it exists
                if elem.get('stroke'):
                    elem.set('stroke', color)
        
        # Apply text replacements
        wrapped_elements = set()  # Track which elements we wrapped
        for element_id, text in spec.text_replacements.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                # Handle text elements
                if elem.tag.endswith('text'):
                    # For pyramid text elements, always use black text with light backgrounds
                    if 'level_' in element_id and '_text' in element_id:
                        # All pyramid levels now have light backgrounds, so use black text
                        elem.set('fill', '#1e293b')
                    
                    # Check if any text element needs wrapping
                    if '_text' in element_id:
                        max_width = self._get_element_width(element_id)
                        # Allow more lines for SWOT text elements
                        max_lines = 4 if element_id in ['strengths_text', 'weaknesses_text', 'opportunities_text', 'threats_text'] else 2
                        lines = self._wrap_text_for_svg(text, max_width, max_lines)
                        print(f"DEBUG: {element_id} - text='{text}', max_width={max_width}, lines={lines}")
                        
                        if len(lines) > 1:
                            # Clear existing text
                            elem.text = None
                            # Remove any existing tspan elements
                            for child in list(elem):
                                elem.remove(child)
                            
                            # Get original position
                            x = elem.get('x', '500' if 'pyramid' in template_spec.template_name else '400')
                            y = elem.get('y', '200')
                            
                            # Adjust y position to center multi-line text
                            y_offset = -((len(lines) - 1) * 10)  # Move up by half total height
                            y_value = float(y) + y_offset
                            elem.set('y', str(y_value))
                            
                            # Create tspan elements for each line
                            # Use namespace-aware element creation
                            for i, line in enumerate(lines):
                                tspan = ET.SubElement(elem, '{http://www.w3.org/2000/svg}tspan')
                                tspan.set('x', x)
                                if i == 0:
                                    tspan.set('dy', '0')
                                else:
                                    tspan.set('dy', '1.2em')
                                tspan.text = line
                                print(f"DEBUG: Created tspan {i} with text: '{line}'")
                            
                            # Mark this element as wrapped
                            wrapped_elements.add(element_id)
                        else:
                            elem.text = text
                    else:
                        elem.text = text
                # Handle existing tspan elements (only if we didn't wrap this element)
                if element_id not in wrapped_elements:
                    for tspan in elem.findall('.//{http://www.w3.org/2000/svg}tspan'):
                        tspan.text = text
        
        # Apply style overrides
        for element_id, styles in spec.style_overrides.items():
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                style_str = "; ".join([f"{k}: {v}" for k, v in styles.items()])
                elem.set('style', style_str)
        
        # Convert to string
        svg_str = ET.tostring(root, encoding='unicode')
        
        # Clean up namespaces
        svg_str = self._clean_svg_namespaces(svg_str)
        
        return svg_str
    
    def _clean_svg_namespaces(self, svg_str: str) -> str:
        """Clean up SVG namespaces for better compatibility."""
        # Remove namespace prefixes
        svg_str = re.sub(r'ns\d+:', '', svg_str)
        svg_str = re.sub(r'xmlns:ns\d+="[^"]*"', '', svg_str)
        
        # Ensure SVG namespace is present
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_str:
            svg_str = svg_str.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        
        return svg_str
    
    def _wrap_text_for_svg(self, text: str, max_width_chars: int, max_lines: int = 2) -> List[str]:
        """
        Wrap text into multiple lines based on character width with line limit.
        
        Args:
            text: Text to wrap
            max_width_chars: Maximum characters per line (approximation)
            max_lines: Maximum number of lines (default 2)
            
        Returns:
            List of text lines (truncated with ellipsis if necessary)
        """
        # Handle text with explicit newlines (like SWOT items)
        if '\n' in text:
            # Split by newlines and return as separate lines
            lines = text.split('\n')
            # Trim to max_lines if needed
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                lines[-1] = lines[-1] + '...'
            return lines
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            # If we're on the last allowed line
            if len(lines) == max_lines - 1:
                # Check if adding this word would exceed width
                if current_length + word_length + (1 if current_line else 0) > max_width_chars:
                    # Finish current line and stop
                    if current_line:
                        # Add ellipsis if there are more words
                        lines.append(' '.join(current_line) + '...')
                    break
                else:
                    current_line.append(word)
                    current_length += word_length + (1 if current_line else 0)
            elif current_length + word_length + (1 if current_line else 0) <= max_width_chars:
                current_line.append(word)
                current_length += word_length + (1 if current_line else 0)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    if len(lines) >= max_lines:
                        break
                current_line = [word]
                current_length = word_length
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _get_text_color_for_background(self, bg_color: str) -> str:
        """
        Determine appropriate text color (white or dark) based on background color.
        
        Args:
            bg_color: Background color in hex format
            
        Returns:
            '#ffffff' for dark backgrounds, '#1e293b' for light backgrounds
        """
        # Simple luminance calculation
        # Remove # if present
        color = bg_color.lstrip('#')
        
        # Convert to RGB
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # Calculate relative luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # Return white text for dark backgrounds, dark text for light backgrounds
            return '#ffffff' if luminance < 0.5 else '#1e293b'
        except:
            # Default to white text if we can't parse the color
            return '#ffffff'
    
    def _get_element_width(self, element_id: str) -> int:
        """
        Get the approximate character width for any text element.
        
        Args:
            element_id: The element ID (e.g., 'level_1_text', 'stage_1_text')
            
        Returns:
            Maximum characters that fit in the element
        """
        width_map = {
            # Pyramid - Updated for larger template with smaller font
            'level_1_text': 22,  # Top level - more chars with smaller font
            'level_2_text': 35,  # Middle level - more chars with smaller font
            'level_3_text': 50,  # Bottom level - more chars with smaller font
            
            # Funnel
            'stage_1_text': 35,  # Top - widest
            'stage_2_text': 30,
            'stage_3_text': 25,
            'stage_4_text': 20,
            'stage_5_text': 15,  # Bottom - narrowest
            
            # Timeline
            'milestone_1_text': 12,
            'milestone_2_text': 12,
            'milestone_3_text': 12,
            'milestone_4_text': 12,
            'milestone_5_text': 12,
            'milestone_6_text': 12,
            
            # Cycle
            'step_1_text': 15,
            'step_2_text': 15,
            'step_3_text': 15,
            'step_4_text': 15,
            
            # Venn
            'left_circle_text': 18,
            'right_circle_text': 18,
            'overlap_text': 15,
            
            # Titles (generally wider)
            'pyramid_title': 40,
            'funnel_title': 40,
            'timeline_title': 40,
            'cycle_title': 40,
            'venn_title': 40,
            'matrix_title': 40,
            
            # Hub & Spoke
            'hub_text': 10,
            'spoke_1_text': 12,
            'spoke_2_text': 12,
            'spoke_3_text': 12,
            'spoke_4_text': 12,
            'spoke_5_text': 12,
            'spoke_6_text': 12,
            'hub_title': 40,
            
            # Honeycomb cells
            'hex_1_text': 10,  # Center
            'hex_2_text': 12,
            'hex_3_text': 12,
            'hex_4_text': 12,
            'hex_5_text': 12,
            'hex_6_text': 12,
            'hex_7_text': 12,
            'honeycomb_title': 40,
            
            # SWOT Matrix - allow more room for multi-line items
            'strengths_text': 25,
            'weaknesses_text': 25,
            'opportunities_text': 25,
            'threats_text': 25,
            'swot_title': 40,
            
            # Process Flow
            'process_1_text': 14,
            'process_2_text': 14,
            'process_3_text': 14,
            'process_4_text': 14,
            'process_5_text': 12,
            'flow_title': 40,
        }
        return width_map.get(element_id, 30)  # Default to 30 chars
    
    def _get_pyramid_level_width(self, element_id: str) -> int:
        """Legacy method for backward compatibility."""
        return self._get_element_width(element_id)
    
    def _extract_text_from_content(self, diagram_type: str, content: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract text labels from content for direct use in templates.
        
        Args:
            diagram_type: Type of diagram
            content: Content dictionary from DiagramSpec
            
        Returns:
            Dictionary of element IDs to text values, or empty dict if can't extract
        """
        text_replacements = {}
        
        # Handle pyramid diagrams
        if diagram_type in ["pyramid", "organizational_hierarchy"]:
            # Check for core_elements or elements
            elements = None
            if isinstance(content, dict):
                if 'core_elements' in content:
                    elements = content['core_elements']
                elif 'elements' in content:
                    elements = content['elements']
                
                if elements and len(elements) >= 3:
                    # Map elements to pyramid levels
                    text_replacements['level_1_text'] = elements[0].get('label', 'Top Level')
                    text_replacements['level_2_text'] = elements[1].get('label', 'Middle Level')
                    text_replacements['level_3_text'] = elements[2].get('label', 'Bottom Level')
                    text_replacements['pyramid_title'] = content.get('title', 'Pyramid Diagram')
                    
        # Handle matrix diagrams
        elif diagram_type in ["matrix", "matrix_2x2", "comparison_matrix"]:
            # Check for core_elements or elements
            elements = None
            if isinstance(content, dict):
                if 'core_elements' in content:
                    elements = content['core_elements']
                elif 'elements' in content:
                    elements = content['elements']
                
                if elements and len(elements) >= 4:
                    text_replacements['quadrant_1'] = elements[0].get('label', 'Quadrant 1')
                    text_replacements['quadrant_2'] = elements[1].get('label', 'Quadrant 2')
                    text_replacements['quadrant_3'] = elements[2].get('label', 'Quadrant 3')
                    text_replacements['quadrant_4'] = elements[3].get('label', 'Quadrant 4')
                
                # Extract axis labels from relationships
                if 'relationships' in content:
                    for rel in content['relationships']:
                        if rel.get('axis') == 'x':
                            text_replacements['x_label'] = rel.get('label', 'X Axis')
                        elif rel.get('axis') == 'y':
                            text_replacements['y_label'] = rel.get('label', 'Y Axis')
                
                text_replacements['matrix_title'] = content.get('title', 'Matrix Diagram')
        
        # Handle funnel diagrams
        elif diagram_type == "funnel":
            elements = self._get_elements_from_content(content)
            if elements and len(elements) >= 5:
                for i in range(min(5, len(elements))):
                    text_replacements[f'stage_{i+1}_text'] = elements[i].get('label', f'Stage {i+1}')
                text_replacements['funnel_title'] = content.get('title', 'Funnel Diagram')
        
        # Handle timeline diagrams
        elif diagram_type == "timeline":
            elements = self._get_elements_from_content(content)
            if elements:
                for i in range(min(6, len(elements))):
                    text_replacements[f'milestone_{i+1}_text'] = elements[i].get('label', f'Milestone {i+1}')
                    # Also handle dates if available
                    if 'date' in elements[i]:
                        text_replacements[f'milestone_{i+1}_date'] = elements[i]['date']
                text_replacements['timeline_title'] = content.get('title', 'Timeline')
        
        # Handle cycle diagrams
        elif diagram_type == "cycle":
            elements = self._get_elements_from_content(content)
            if elements and len(elements) >= 4:
                for i in range(min(4, len(elements))):
                    text_replacements[f'step_{i+1}_text'] = elements[i].get('label', f'Step {i+1}')
                text_replacements['cycle_title'] = content.get('title', 'Cycle Diagram')
        
        # Handle venn diagrams
        elif diagram_type == "venn":
            elements = self._get_elements_from_content(content)
            if elements and len(elements) >= 2:
                text_replacements['left_circle_text'] = elements[0].get('label', 'Set A')
                text_replacements['right_circle_text'] = elements[1].get('label', 'Set B')
                if len(elements) >= 3:
                    text_replacements['overlap_text'] = elements[2].get('label', 'Overlap')
                text_replacements['venn_title'] = content.get('title', 'Venn Diagram')
        
        # Handle hub & spoke diagrams
        elif diagram_type == "hub_spoke":
            elements = self._get_elements_from_content(content)
            if elements and len(elements) >= 1:
                text_replacements['hub_text'] = elements[0].get('label', 'Hub')
                for i in range(1, min(7, len(elements))):
                    text_replacements[f'spoke_{i}_text'] = elements[i].get('label', f'Node {i}')
                text_replacements['hub_title'] = content.get('title', 'Hub and Spoke Model')
        
        # Handle honeycomb diagrams
        elif diagram_type == "honeycomb":
            elements = self._get_elements_from_content(content)
            if elements:
                for i in range(min(7, len(elements))):
                    if i == 0:
                        text_replacements['hex_1_text'] = elements[i].get('label', 'Core')
                    else:
                        text_replacements[f'hex_{i+1}_text'] = elements[i].get('label', f'Cell {i+1}')
                text_replacements['honeycomb_title'] = content.get('title', 'Honeycomb Structure')
        
        # Handle SWOT matrix
        elif diagram_type == "swot":
            elements = self._get_elements_from_content(content)
            if elements and len(elements) >= 4:
                # Split comma-separated items into separate lines
                for i, key in enumerate(['strengths_text', 'weaknesses_text', 'opportunities_text', 'threats_text']):
                    label = elements[i].get('label', 'Item')
                    # Split by comma and clean up each item
                    items = [item.strip() for item in label.split(',')]
                    # Join with newlines for SWOT (will be handled by wrapping)
                    text_replacements[key] = '\n'.join(items)
                text_replacements['swot_title'] = content.get('title', 'SWOT Analysis')
        
        # Handle process flow diagrams
        elif diagram_type in ["process_flow", "process"]:
            elements = self._get_elements_from_content(content)
            if elements:
                for i in range(min(5, len(elements))):
                    text_replacements[f'process_{i+1}_text'] = elements[i].get('label', f'Process {i+1}')
                text_replacements['flow_title'] = content.get('title', 'Process Flow')
        
        return text_replacements
    
    def _get_elements_from_content(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Helper to extract elements from content dictionary."""
        if isinstance(content, dict):
            if 'core_elements' in content:
                return content['core_elements']
            elif 'elements' in content:
                return content['elements']
        return []
    
    def _get_color_replacements(self, diagram_type: str, theme_colors: Dict[str, str]) -> Dict[str, str]:
        """
        Get color replacements based on diagram type and theme.
        
        Args:
            diagram_type: Type of diagram
            theme_colors: Extracted theme colors
            
        Returns:
            Dictionary of element IDs to color values
        """
        primary = theme_colors.get('primary', '#3b82f6')
        secondary = theme_colors.get('secondary', '#10b981')
        accent = theme_colors.get('accent', '#f59e0b')
        
        # Helper function to lighten a color (simple approximation)
        def lighten(color: str, factor: float = 0.3) -> str:
            # Simple lightening - in production you'd want proper color manipulation
            return color
        
        if diagram_type in ["pyramid", "organizational_hierarchy"]:
            # Light colors for all pyramid levels for better text visibility
            return {
                'level_1_fill': '#fef3c7',   # Light amber/yellow
                'level_2_fill': '#d1fae5',   # Light green
                'level_3_fill': '#dbeafe'    # Light blue
            }
            
        elif diagram_type in ["matrix", "matrix_2x2"]:
            return {
                'quadrant_1_fill': primary,
                'quadrant_2_fill': secondary,
                'quadrant_3_fill': accent,
                'quadrant_4_fill': '#ef4444'  # Can be a theme danger color
            }
            
        elif diagram_type == "funnel":
            # Gradient from primary to accent - each stage distinct
            return {
                'stage_1_fill': primary,
                'stage_2_fill': '#8b5cf6',  # Purple
                'stage_3_fill': secondary,
                'stage_4_fill': '#06b6d4',  # Cyan
                'stage_5_fill': accent
            }
            
        elif diagram_type == "timeline":
            # Alternating colors for milestones
            return {
                'milestone_1_fill': primary,
                'milestone_2_fill': secondary,
                'milestone_3_fill': accent,
                'milestone_4_fill': primary,
                'milestone_5_fill': secondary,
                'milestone_6_fill': accent
            }
            
        elif diagram_type == "cycle":
            # Rotating through theme colors - all distinct
            return {
                'step_1_fill': primary,
                'step_2_fill': secondary,
                'step_3_fill': accent,
                'step_4_fill': '#8b5cf6'  # Purple
            }
            
        elif diagram_type == "venn":
            return {
                'left_circle_fill': primary,
                'right_circle_fill': secondary,
                # Overlap uses blend or accent
                'overlap_fill': accent
            }
            
        elif diagram_type == "hub_spoke":
            # Hub is primary, spokes rotate through colors
            return {
                'hub_fill': primary,
                'spoke_1_fill': secondary,
                'spoke_2_fill': accent,
                'spoke_3_fill': '#8b5cf6',  # Purple
                'spoke_4_fill': '#f59e0b',  # Orange
                'spoke_5_fill': '#ef4444',  # Red
                'spoke_6_fill': '#ec4899'   # Pink
            }
            
        elif diagram_type == "honeycomb":
            # Center is primary, surrounding cells use varied colors
            return {
                'hex_1_fill': primary,      # Center
                'hex_2_fill': secondary,
                'hex_3_fill': accent,
                'hex_4_fill': '#8b5cf6',
                'hex_5_fill': '#f59e0b',
                'hex_6_fill': '#ef4444',
                'hex_7_fill': '#06b6d4'
            }
            
        elif diagram_type == "swot":
            # Lighter SWOT colors for better text visibility
            return {
                'strengths_fill': '#d1fae5',    # Light green for positive
                'weaknesses_fill': '#fee2e2',   # Light red for negative
                'opportunities_fill': '#dbeafe', # Light blue for external positive
                'threats_fill': '#fed7aa'       # Light orange for caution
            }
            
        elif diagram_type in ["process_flow", "process"]:
            # Sequential coloring
            return {
                'process_1_fill': primary,
                'process_2_fill': secondary,
                'process_3_fill': accent,
                'process_4_fill': '#8b5cf6',
                'process_5_fill': '#ef4444'
            }
            
        else:
            return {}
    
    # Tool definitions
    async def load_template(
        self,
        ctx: RunContext[SVGContext],
        template_name: str
    ) -> str:
        """Load an SVG template file."""
        template_path = Path(ctx.deps.template_path)
        if template_path.exists():
            return template_path.read_text()
        raise FileNotFoundError(f"Template not found: {template_name}")
    
    async def populate_text(
        self,
        ctx: RunContext[SVGContext],
        element_id: str,
        text: str,
        max_length: Optional[int] = None
    ) -> Dict[str, str]:
        """Populate text in an SVG element."""
        if max_length and len(text) > max_length:
            text = text[:max_length-3] + "..."
        return {element_id: text}
    
    async def apply_colors(
        self,
        ctx: RunContext[SVGContext],
        element_id: str,
        color_role: str
    ) -> Dict[str, str]:
        """Apply theme colors to an SVG element."""
        color = ctx.deps.theme_colors.get(color_role, "#000000")
        return {element_id: color}
    
    async def apply_styles(
        self,
        ctx: RunContext[SVGContext],
        element_id: str,
        styles: Dict[str, str]
    ) -> Dict[str, Dict[str, str]]:
        """Apply CSS styles to an SVG element."""
        return {element_id: styles}
    
    async def validate_svg(
        self,
        ctx: RunContext[SVGContext],
        svg_content: str
    ) -> bool:
        """Validate that the SVG is well-formed."""
        try:
            ET.fromstring(svg_content)
            return True
        except ET.ParseError:
            return False


class SVGTemplateLibrary:
    """
    Library of available SVG templates and their metadata.
    """
    
    TEMPLATES = {
        "pyramid_3_level": {
            "name": "3-Level Pyramid",
            "placeholders": ["level_1_text", "level_2_text", "level_3_text"],
            "color_zones": ["level_1_fill", "level_2_fill", "level_3_fill"],
            "max_text_length": 30
        },
        "funnel_5_stage": {
            "name": "5-Stage Funnel",
            "placeholders": ["stage_1", "stage_2", "stage_3", "stage_4", "stage_5"],
            "color_zones": ["stage_1_fill", "stage_2_fill", "stage_3_fill", "stage_4_fill", "stage_5_fill"],
            "max_text_length": 25
        },
        "matrix_2x2": {
            "name": "2x2 Matrix",
            "placeholders": ["quadrant_1", "quadrant_2", "quadrant_3", "quadrant_4", "x_label", "y_label"],
            "color_zones": ["q1_fill", "q2_fill", "q3_fill", "q4_fill"],
            "max_text_length": 20
        },
        "hub_spoke_6": {
            "name": "Hub & Spoke (6 nodes)",
            "placeholders": ["hub_text", "spoke_1", "spoke_2", "spoke_3", "spoke_4", "spoke_5", "spoke_6"],
            "color_zones": ["hub_fill", "spoke_fill"],
            "max_text_length": 15
        },
        "cycle_4_step": {
            "name": "4-Step Cycle",
            "placeholders": ["step_1", "step_2", "step_3", "step_4"],
            "color_zones": ["step_1_fill", "step_2_fill", "step_3_fill", "step_4_fill"],
            "max_text_length": 20
        },
        "venn_2_circle": {
            "name": "2-Circle Venn Diagram",
            "placeholders": ["circle_1_label", "circle_2_label", "overlap_label"],
            "color_zones": ["circle_1_fill", "circle_2_fill"],
            "max_text_length": 25
        },
        "timeline_horizontal": {
            "name": "Horizontal Timeline",
            "placeholders": ["event_1", "event_2", "event_3", "event_4", "event_5"],
            "color_zones": ["timeline_fill", "milestone_fill"],
            "max_text_length": 30
        },
        "honeycomb_7": {
            "name": "7-Cell Honeycomb",
            "placeholders": ["cell_1", "cell_2", "cell_3", "cell_4", "cell_5", "cell_6", "cell_7"],
            "color_zones": ["cell_fill", "cell_stroke"],
            "max_text_length": 15
        }
    }
    
    @classmethod
    def get_template_info(cls, template_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a template."""
        return cls.TEMPLATES.get(template_name)