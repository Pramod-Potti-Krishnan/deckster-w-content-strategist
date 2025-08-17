"""
SVG Template Agent

Handles diagram generation using pre-built SVG templates.
"""

import os
import re
from typing import Dict, Any, List, Optional
from xml.etree import ElementTree as ET

from models import DiagramRequest
from models.response_models import OutputType
from .base_agent import BaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SVGAgent(BaseAgent):
    """
    Agent for SVG template-based diagram generation
    
    Uses pre-built SVG templates with text and color replacements.
    """
    
    def __init__(self, settings):
        super().__init__(settings)
        self.templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            settings.templates_dir
        )
        self.template_cache: Dict[str, str] = {}
    
    async def initialize(self):
        """Initialize SVG agent and load templates"""
        await super().initialize()
        
        # Scan and cache templates
        self._load_templates()
        
        logger.info(f"SVG Agent initialized with {len(self.template_cache)} templates")
    
    def _load_templates(self):
        """Load SVG templates into cache"""
        if not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.svg'):
                template_name = filename[:-4]
                template_path = os.path.join(self.templates_dir, filename)
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        self.template_cache[template_name] = f.read()
                        self.supported_types.append(template_name)
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {e}")
    
    async def supports(self, diagram_type: str) -> bool:
        """Check if diagram type is supported"""
        return diagram_type in self.template_cache
    
    async def generate(self, request: DiagramRequest) -> Dict[str, Any]:
        """Generate diagram using SVG template"""
        
        # Validate request
        self.validate_request(request)
        
        # Get template
        template = self.template_cache.get(request.diagram_type)
        if not template:
            raise ValueError(f"No template found for {request.diagram_type}")
        
        # Extract data points
        data_points = self.extract_data_points(request)
        
        # Apply replacements
        svg_content = self._apply_replacements(
            template,
            data_points,
            request.theme.dict()
        )
        
        # Apply theme
        svg_content = self.apply_theme(svg_content, request.theme.dict())
        
        return {
            # Old format (backward compatibility)
            "content": svg_content,
            "content_type": "svg",
            "diagram_type": request.diagram_type,
            
            # V2 format indicators
            "output_type": OutputType.SVG.value,
            "svg": {
                "content": svg_content,
                "is_placeholder": False
            },
            "rendering": {
                "server_rendered": True,
                "render_method": "template",
                "render_status": "success"
            },
            
            # Metadata (works for both formats)
            "metadata": {
                "generation_method": "svg_template",
                "template_used": request.diagram_type,
                "elements_modified": len(data_points),
                "cache_hit": False,
                "server_rendered": True
            }
        }
    
    def _apply_replacements(
        self,
        template: str,
        data_points: List[Dict[str, Any]],
        theme: Dict[str, Any]
    ) -> str:
        """
        Apply text replacements to template
        
        Args:
            template: SVG template content
            data_points: Data points to insert
            theme: Theme configuration
            
        Returns:
            Modified SVG content
        """
        
        svg_content = template
        
        # Replace placeholder text with actual content
        for i, point in enumerate(data_points):
            label = point.get("label", "")
            
            # Common placeholder patterns
            placeholders = [
                f"Step {i+1}",
                f"Item {i+1}",
                f"Level {i+1}",
                f"Stage {i+1}",
                f"Phase {i+1}",
                f"Cell {i+1}",
                f"Box {i+1}",
                f"Section {i+1}"
            ]
            
            for placeholder in placeholders:
                if placeholder in svg_content:
                    svg_content = svg_content.replace(placeholder, label)
            
            # Also try with colons
            for placeholder in placeholders:
                full_placeholder = f"{placeholder}:"
                if full_placeholder in svg_content:
                    svg_content = svg_content.replace(
                        full_placeholder,
                        f"{label}:"
                    )
        
        # Handle special replacements for specific diagram types
        if "pyramid" in template:
            svg_content = self._apply_pyramid_replacements(svg_content, data_points)
        elif "cycle" in template:
            svg_content = self._apply_cycle_replacements(svg_content, data_points)
        elif "venn" in template:
            svg_content = self._apply_venn_replacements(svg_content, data_points)
        
        return svg_content
    
    def _apply_pyramid_replacements(
        self,
        svg_content: str,
        data_points: List[Dict[str, Any]]
    ) -> str:
        """Apply pyramid-specific replacements"""
        
        # Pyramid levels are typically numbered from top
        for i, point in enumerate(data_points):
            svg_content = svg_content.replace(f"#{i+1}", point.get("label", ""))
        
        return svg_content
    
    def _apply_cycle_replacements(
        self,
        svg_content: str,
        data_points: List[Dict[str, Any]]
    ) -> str:
        """Apply cycle-specific replacements"""
        
        # Cycles may have special labels like DMAIC
        if len(data_points) == 5:
            # Check for DMAIC pattern
            dmaic_labels = ["Define", "Measure", "Analyze", "Improve", "Control"]
            for i, (label, point) in enumerate(zip(dmaic_labels, data_points)):
                svg_content = svg_content.replace(label, point.get("label", label))
        
        return svg_content
    
    def _apply_venn_replacements(
        self,
        svg_content: str,
        data_points: List[Dict[str, Any]]
    ) -> str:
        """Apply venn-specific replacements"""
        
        # Venn diagrams have Set labels
        for i, point in enumerate(data_points):
            svg_content = svg_content.replace(
                f"Set {chr(65+i)}",
                point.get("label", f"Set {chr(65+i)}")
            )
        
        return svg_content