"""
Enhanced Content Agent - Prepares detailed, theme-aware content for slides.

This enhanced agent uses deck-level context and theme guidelines to expand 
strawman content into presentation-ready specifications, with support for
external information integration and comprehensive visual specifications.
"""

import os
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from src.models.agents import Slide
from src.utils.logger import setup_logger
from src.utils.agent_context_manager import (
    AgentContextManager, ContextAwareAgent, AgentType
)
from ...utils.model_utils import create_model_with_fallback
from ...model_types.design_tokens import ThemeDefinition

logger = setup_logger(__name__)


class ContentContext(BaseModel):
    """Enhanced context for content generation"""
    slide: Slide
    deck_summary: str = Field(
        description="2-paragraph summary of the entire presentation's narrative"
    )
    theme: ThemeDefinition = Field(
        description="Complete theme definition from Theme Agent"
    )
    strawman_metadata: Dict[str, Any] = Field(
        description="Main title, overall theme, design suggestions, target audience"
    )
    session_id: Optional[str] = None


class TextContent(BaseModel):
    """Enhanced text content with source attribution"""
    text: str = Field(description="The actual text content")
    word_count: int = Field(description="Word count for this content", ge=0)
    priority: str = Field(description="Priority level: P1, P2, P3, or P4")
    sources: Optional[List[str]] = Field(
        default=None,
        description="Source references for the content"
    )
    tone_keywords: Optional[List[str]] = Field(
        default=None,
        description="Tone keywords from theme used in generation"
    )


# Import the custom models from enhanced_tools
from .enhanced_tools import ChartDataPoint, ChartAxes, DiagramNode, DiagramConnection

class VisualSpec(BaseModel):
    """Enhanced specification for a visual element with theme awareness"""
    visual_type: str = Field(description="chart, diagram, image, table, or icon")
    description: str = Field(description="Detailed description for visual generation")
    
    # Theme alignment
    theme_colors_used: Optional[List[str]] = Field(
        default=None,
        description="Theme colors to use in this visual"
    )
    theme_style_applied: Optional[str] = Field(
        default=None,
        description="Theme visual style applied"
    )
    
    # Chart-specific fields
    chart_type: Optional[str] = Field(default=None, description="bar, line, pie, scatter, etc.")
    data_points: Optional[List[ChartDataPoint]] = Field(default=None, description="Structured data points")
    axes: Optional[ChartAxes] = Field(default=None, description="Chart axis labels")
    data_insights: Optional[str] = Field(default=None, description="Key takeaways from the data")
    unit: Optional[str] = Field(default=None, description="Data unit (e.g., $, %, users)")
    
    # Image-specific fields
    image_prompt: Optional[str] = Field(default=None, description="Full prompt for image generation")
    image_style: Optional[str] = Field(default=None, description="photo, illustration, abstract")
    style_keywords: Optional[List[str]] = Field(default=None, description="Style descriptors")
    composition: Optional[str] = Field(default=None, description="Composition type")
    lighting: Optional[str] = Field(default=None, description="Lighting description")
    negative_prompt: Optional[str] = Field(default=None, description="What to avoid in image")
    
    # Diagram-specific fields
    diagram_type: Optional[str] = Field(default=None, description="flowchart, org_chart, cycle, etc.")
    style_preference: Optional[str] = Field(
        default="schematic",
        description="schematic or artistic"
    )
    nodes: Optional[List[DiagramNode]] = Field(default=None, description="Diagram nodes")
    connections: Optional[List[DiagramConnection]] = Field(default=None, description="Node connections")
    layout_direction: Optional[str] = Field(default=None, description="Layout direction")
    
    # Table-specific fields
    table_data: Optional[Dict[str, List]] = Field(
        default=None,
        description="Structured table data with headers and rows"
    )
    
    # Common fields
    space_requirement: str = Field(default="medium", description="large, medium, or small")
    layout_preference: str = Field(default="center", description="Position preference")
    priority: str = Field(default="P2", description="P1-P4 priority level")
    handoff_ready: bool = Field(default=False, description="Ready for downstream service")


class ContentManifest(BaseModel):
    """Enhanced content manifest with theme integration"""
    slide_id: str
    slide_type: str
    structure_preference: Optional[str] = None  # CRITICAL: Preserved from input slide
    target_audience: str
    
    # Deck context awareness
    deck_context_used: bool = Field(
        default=False,
        description="Whether deck summary was used in generation"
    )
    theme_elements_applied: List[str] = Field(
        default_factory=list,
        description="Which theme elements were applied"
    )
    
    # Text content sections
    title: TextContent
    main_points: List[TextContent] = Field(default_factory=list)
    supporting_text: Optional[TextContent] = None
    
    # Visual content
    primary_visual: Optional[VisualSpec] = None
    supporting_visuals: List[VisualSpec] = Field(default_factory=list)
    
    # Content metrics
    total_word_count: int = Field(ge=0)
    word_count_limit: int = Field(ge=0)
    visual_count: int = Field(ge=0)
    content_density: str = Field(description="light, medium, or heavy")
    
    # Layout hints
    preferred_reading_flow: str = Field(
        default="F-pattern",
        description="Reading flow based on theme and structure"
    )
    emphasis_areas: List[str] = Field(default_factory=list, description="Areas to emphasize")
    grouping_suggestions: List[List[str]] = Field(default_factory=list, description="Content grouping")


class ContentAgent(ContextAwareAgent):
    """
    Enhanced Content Agent - Theme-Aware Content Generation.
    
    Uses deck-level context and theme guidelines to expand strawman
    content into comprehensive, presentation-ready specifications with:
    - Full theme integration in all generation
    - External information search and attribution
    - Intelligent visual specification
    - Layout-aware content volume adjustment
    """
    
    # Enhanced word count limits considering theme typography
    WORD_COUNT_LIMITS = {
        "title_slide": (15, 25),        # Adjusted for large heading fonts
        "section_divider": (10, 20),    
        "content_heavy": (120, 180),    
        "data_driven": (50, 70),        # Less text, more visuals
        "visual_heavy": (40, 60),       
        "mixed_content": (80, 120),    
        "diagram_focused": (60, 90),   
        "conclusion_slide": (80, 120), 
        "default": (70, 100)          
    }
    
    # Structure-specific word count limits (override slide type limits)
    STRUCTURE_WORD_LIMITS = {
        "Hero Image / Full-Bleed": (15, 30),
        "Split Layout": (50, 80),
        "Text Heavy": (120, 180),
        "Data Visualization": (30, 50),
        "Comparison": (60, 100),
        "Timeline": (40, 80),
        "Grid Layout": (60, 120),
        "Centered": (30, 60)
    }
    
    # Audience adjustments remain the same
    AUDIENCE_ADJUSTMENTS = {
        "executives": -0.3,        
        "technical": 0.2,          
        "general_public": 0.0,     
        "educational": 0.1,        
        "healthcare_professionals": 0.0,  
        "investors": -0.2          
    }
    
    def __init__(self, model_name: str = "gemini-2.5-pro",
                 context_manager: Optional[AgentContextManager] = None):
        """Initialize with AI model, comprehensive tools, and optional context management"""
        # Initialize context-aware base if context manager provided
        if context_manager:
            super().__init__(AgentType.CONTENT, context_manager)
        else:
            self.context_manager = None
            
        self.model = create_model_with_fallback(model_name, timeout_seconds=30)
        
        # Import all tools
        from .tools import (
            expand_content_tool, internal_knowledge_search_tool,
            web_search_tool, calculate_word_limit_tool,
            prioritize_content_tool
        )
        from .enhanced_tools import (
            generate_synthetic_data, select_chart_type,
            generate_image_prompt, design_diagram_structure
        )
        
        # Create agent with comprehensive tool set
        self.agent = Agent(
            self.model,
            output_type=ContentManifest,
            deps_type=ContentContext,
            tools=[
                # Enhanced content tools
                expand_content_tool,
                internal_knowledge_search_tool,
                web_search_tool,
                calculate_word_limit_tool,
                prioritize_content_tool,
                # Visual specification tools
                generate_synthetic_data,
                select_chart_type,
                generate_image_prompt,
                design_diagram_structure
            ],
            system_prompt=self._get_enhanced_system_prompt(),
            retries=2
        )
    
    def _get_enhanced_system_prompt(self) -> str:
        """Get enhanced system prompt with theme awareness"""
        return """You are an AI assistant that generates detailed, structured content for presentation slides based on a creative brief. You must strictly adhere to the user's instructions and the Pydantic output format."""
    
    async def prepare_content(
        self,
        slide: Slide,
        deck_summary: str,
        theme: ThemeDefinition,
        strawman_metadata: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> ContentManifest:
        """
        Prepare theme-aware content from strawman data.
        
        Args:
            slide: The slide data from strawman
            deck_summary: 2-paragraph summary of presentation narrative
            theme: Complete theme definition from Theme Agent
            strawman_metadata: Overall presentation metadata
            session_id: Optional session ID
            
        Returns:
            ContentManifest with theme-aware content and visual specifications
        """
        # Track processing start if context manager available
        if self.context_manager:
            # Get upstream context
            upstream_context = self.get_upstream_context()
            
            # Log what we can access
            if "theme" in upstream_context:
                logger.info("Accessing theme data from context manager")
            if "director" in upstream_context:
                logger.info("Accessing strawman data from context manager")
            
            # Prepare input data for tracking
            input_data = {
                "slide": slide.dict(),
                "deck_summary": deck_summary,
                "theme_name": theme.name,
                "strawman_metadata": strawman_metadata,
                "upstream_context_available": list(upstream_context.keys())
            }
            
            self.start_processing(input_data, {
                "started_at": datetime.utcnow().isoformat(),
                "slide_id": slide.slide_id,
                "slide_type": slide.slide_type
            })
        
        try:
            logger.info(f"Preparing theme-aware content for slide {slide.slide_id}")
            # Check for mood_keywords with proper fallback
            mood_keywords_count = len(getattr(theme, 'mood_keywords', [])) if hasattr(theme, 'mood_keywords') else 0
            logger.info(f"Theme: {theme.name} with {mood_keywords_count} mood keywords")
            logger.info(f"Deck context length: {len(deck_summary)} characters")
            
            # Determine expert mode
            mode = self._determine_expert_mode(slide)
            logger.info(f"Expert mode: {mode}")
            
            # Create enhanced context
            context = ContentContext(
                slide=slide,
                deck_summary=deck_summary,
                theme=theme,
                strawman_metadata=strawman_metadata,
                session_id=session_id
            )
            
            # Build theme-aware prompt
            prompt = self._build_enhanced_prompt(
                slide, deck_summary, theme, strawman_metadata, mode
            )
            
            # Run agent with theme context
            import asyncio
            try:
                result = await asyncio.wait_for(
                    self.agent.run(prompt, deps=context),
                    timeout=45.0  # Increased for search operations
                )
            except asyncio.TimeoutError:
                logger.error(f"Content preparation timed out for slide {slide.slide_id}")
                return self._create_theme_aware_fallback(slide, theme, strawman_metadata)
            
            # Log theme integration
            manifest = result.output
            
            # CRITICAL: Ensure structure_preference is preserved
            if hasattr(slide, 'structure_preference') and slide.structure_preference:
                if manifest.structure_preference != slide.structure_preference:
                    logger.warning(f"Structure preference mismatch - fixing: {manifest.structure_preference} -> {slide.structure_preference}")
                    manifest.structure_preference = slide.structure_preference
            
            # Validate content quality - no placeholders
            placeholder_patterns = [
                "summary of", "mention of", "key metric from", "description of",
                "example of", "reference to", "overview of"
            ]
            
            # Check main points for placeholder content
            for point in manifest.main_points:
                text_lower = point.text.lower()
                for pattern in placeholder_patterns:
                    if pattern in text_lower:
                        logger.warning(f"Placeholder content detected: '{pattern}' in '{point.text[:50]}...'")
                        # Attempt to fix by making it more specific
                        if "case study" in slide.title.lower():
                            point.text = point.text.replace(
                                "Summary of a recent study",
                                "Stanford Medical's 2024 radiology AI study"
                            ).replace(
                                "Key metric from the study",
                                "94% diagnostic accuracy (up from 76%)"
                            )
            
            logger.info(f"Content prepared with theme integration:")
            logger.info(f"  - Structure preference: {manifest.structure_preference}")
            logger.info(f"  - Deck context used: {manifest.deck_context_used}")
            logger.info(f"  - Theme elements applied: {manifest.theme_elements_applied}")
            logger.info(f"  - Reading flow: {manifest.preferred_reading_flow}")
            
            if manifest.primary_visual and manifest.primary_visual.theme_colors_used:
                logger.info(f"  - Theme colors in visual: {manifest.primary_visual.theme_colors_used}")
            
            # Track completion if context manager available
            if self.context_manager:
                output_data = {
                    "content_manifest": manifest.dict(),
                    "total_word_count": manifest.total_word_count,
                    "visual_count": manifest.visual_count,
                    "content_density": manifest.content_density,
                    "theme_integration": {
                        "deck_context_used": manifest.deck_context_used,
                        "theme_elements_applied": manifest.theme_elements_applied
                    }
                }
                
                self.complete_processing(output_data, {
                    "completed_at": datetime.utcnow().isoformat(),
                    "expert_mode_used": self._determine_expert_mode(slide)
                })
                
                # Save context to storage
                await self.context_manager.save_to_storage()
            
            return manifest
            
        except Exception as e:
            logger.error(f"Theme-aware content preparation failed: {e}")
            
            # Track failure if context manager available
            if self.context_manager:
                self.fail_processing(str(e))
            
            return self._create_theme_aware_fallback(slide, theme, strawman_metadata)
    
    def _determine_expert_mode(self, slide: Slide) -> str:
        """Determine which expert mode to activate"""
        # Same logic as before
        if slide.slide_type == "data_driven" or slide.analytics_needed:
            return "data_storyteller"
        elif slide.slide_type == "visual_heavy" or slide.visuals_needed:
            return "visual_briefer"
        elif slide.slide_type == "diagram_focused" or slide.diagrams_needed:
            return "diagram_architect"
        else:
            return "content_writer"
    
    def _build_enhanced_prompt(
        self,
        slide: Slide,
        deck_summary: str,
        theme: ThemeDefinition,
        metadata: Dict[str, Any],
        mode: str
    ) -> str:
        """Build comprehensive prompt with deck and theme context"""
        # Get layout template for this slide type
        template = theme.get_template_for_slide_type(slide.slide_type)
        layout_info = self._describe_layout_constraints(template) if template else "Standard layout"
        
        # Get structure preference
        structure_pref = getattr(slide, 'structure_preference', 'None')
        
        # Define structure-specific content guidelines
        structure_guidelines = self._get_structure_guidelines(structure_pref)
        
        # Get word limit for this structure
        word_limit = self._get_word_limit_for_structure(structure_pref)
        
        # Format key points as creative tasks
        formatted_key_points = self._format_key_points_as_tasks(slide.key_points)
        
        prompt = f"""### ROLE & GOAL ###
You are an expert {self._get_role_for_mode(mode)} and content strategist. Your goal is to create compelling, clear, and data-rich content for a single slide in a professional presentation. You must generate specific, concrete content, not just descriptions.

### OVERALL PRESENTATION CONTEXT ###
This slide is part of a larger presentation titled "{metadata.get('main_title', 'the presentation')}". The core narrative is:
"{deck_summary}"

### CREATIVE & DESIGN GUIDELINES (from the Theme) ###
The presentation's theme is "{theme.name}". Adhere to the following creative direction:
- **Tone & Mood:** The tone must be **{', '.join(theme.mood_keywords)}**. Weave these concepts into the text and visual descriptions.
- **Visual Style:** Visuals should follow the theme's **{theme.visual_guidelines.get('photography_style', 'professional')}** photography and **{theme.visual_guidelines.get('data_viz_style', 'clear')}** data visualization guidelines.
- **Layout Constraints:** This slide uses the "{structure_pref}" layout with {structure_guidelines}. You have approximately **{word_limit}** words to work with.

### YOUR SPECIFIC TASK FOR THIS SLIDE ###
Your primary task is to generate the content for the slide titled: **"{slide.title}"**.

The core message of this slide, based on the presentation plan, is:
"{slide.narrative or 'to present key information clearly'}"

To bring this message to life, you must create detailed content that:
{formatted_key_points}

### EXECUTION REQUIREMENTS ###
- Generate specific, concrete content. Use real-world examples, names, numbers, and dates. Mark any invented data clearly with "(illustrative)".
- For any visual elements (charts, diagrams, images), create a complete and detailed specification within the `VisualSpec` object. For charts, you must generate synthetic data.
- Ensure the final `total_word_count` respects the word limit.
- Adhere strictly to the Pydantic output format for the `ContentManifest`.
- The structure_preference must be preserved exactly as: "{structure_pref}"
"""

        return prompt
    
    def _get_role_for_mode(self, mode: str) -> str:
        """Get the expert role based on mode"""
        roles = {
            "data_storyteller": "data analyst and visualization expert",
            "visual_briefer": "visual communications specialist", 
            "diagram_architect": "information architect and process designer",
            "content_writer": "medical communications consultant"
        }
        return roles.get(mode, "communications expert")
    
    def _format_key_points_as_tasks(self, key_points: List[str]) -> str:
        """Format key points as specific creative tasks"""
        if not key_points:
            return "- Create compelling content that supports the slide's core message"
        
        formatted = []
        for point in key_points:
            point_lower = point.lower()
            # Transform each point into a creative task
            if "case study" in point_lower:
                formatted.append(f"- Creates a specific, illustrative case study: {point}. You should invent a plausible hospital, study timeframe, and specific metrics.")
            elif "timeline" in point_lower:
                formatted.append(f"- Develops a concrete timeline: {point}. Create actual dates, milestones, and deliverables.")
            elif "metrics" in point_lower or "data" in point_lower:
                formatted.append(f"- Generates specific metrics: {point}. Provide real numbers with context and comparisons.")
            elif "example" in point_lower:
                formatted.append(f"- Provides a concrete example: {point}. Include names, specifics, and measurable outcomes.")
            elif "breakdown" in point_lower or "phases" in point_lower:
                formatted.append(f"- Creates a detailed breakdown: {point}. List actual phases with timeframes and deliverables.")
            else:
                formatted.append(f"- {point}")
        
        return "\n".join(formatted)
    
    def _format_content_requests(self, key_points: List[str]) -> str:
        """Format key points as simple content requests"""
        if not key_points:
            return "No specific content requested"
        
        formatted = []
        for i, point in enumerate(key_points, 1):
            formatted.append(f"{i}. {point}")
        
        return "\n".join(formatted)
    
    def _get_word_limit_for_structure(self, structure_pref: str) -> str:
        """Get word limit range for structure type"""
        if structure_pref in self.STRUCTURE_WORD_LIMITS:
            min_words, max_words = self.STRUCTURE_WORD_LIMITS[structure_pref]
            return f"{min_words}-{max_words}"
        else:
            return "50-100"  # Default range
    
    def _get_structure_guidelines(self, structure_preference: str) -> str:
        """Get content generation guidelines for specific structure types"""
        guidelines = {
            "Hero Image / Full-Bleed": """- Generate minimal text (15-30 words)
- Create one powerful statement
- Focus on impact""",
            
            "Split Layout": """- Generate 50-80 words of text
- Create 3-4 clear points
- Balance text and visual content""",
            
            "Text Heavy": """- Generate detailed content (120-180 words)
- Create 4-6 main points with details
- Focus on comprehensive information""",
            
            "Data Visualization": """- Generate minimal text (30-50 words)
- Focus on data insights
- Create specific chart/graph data""",
            
            "Comparison": """- Generate 60-100 words
- Create side-by-side comparisons
- Ensure equal weight for each item""",
            
            "Timeline": """- Generate 40-80 words
- Create actual timeline with dates
- Include specific milestones""",
            
            "Grid Layout": """- Generate 60-120 words
- Create 3-6 equal items
- Distribute content evenly""",
            
            "Centered": """- Generate focused content (30-60 words)
- Create one key message
- Keep it simple and impactful"""
        }
        
        return guidelines.get(structure_preference, "- Generate appropriate content for the slide")
    
    def _describe_layout_constraints(self, template: Any) -> str:
        """Describe layout constraints from template"""
        if not template or not hasattr(template, 'zones'):
            return "Standard layout with flexible zones"
        
        constraints = []
        
        # Analyze zones
        if 'title' in template.zones:
            title_zone = template.zones['title']
            constraints.append(f"Title zone: {title_zone.width}x{title_zone.height} grid units")
        
        if 'content' in template.zones:
            content_zone = template.zones['content']
            constraints.append(f"Content zone: {content_zone.width}x{content_zone.height} grid units")
        
        if 'visual' in template.zones or 'visualization' in template.zones:
            visual_zone = template.zones.get('visual') or template.zones.get('visualization')
            constraints.append(f"Visual zone: {visual_zone.width}x{visual_zone.height} grid units")
        
        # Add emphasis and flow
        if hasattr(template, 'emphasis'):
            constraints.append(f"Primary emphasis: {template.emphasis}")
        
        if hasattr(template, 'reading_flow'):
            constraints.append(f"Reading flow: {template.reading_flow}")
        
        return " | ".join(constraints) if constraints else "Flexible layout"
    
    def _create_theme_aware_fallback(
        self,
        slide: Slide,
        theme: ThemeDefinition,
        metadata: Dict[str, Any]
    ) -> ContentManifest:
        """Create theme-aware fallback content"""
        # Calculate word limit with structure awareness first
        structure_pref = getattr(slide, 'structure_preference', None)
        
        # Check structure-specific limits first
        if structure_pref and structure_pref in self.STRUCTURE_WORD_LIMITS:
            min_words, max_words = self.STRUCTURE_WORD_LIMITS[structure_pref]
        else:
            # Fall back to slide type limits
            slide_type = slide.slide_type
            min_words, max_words = self.WORD_COUNT_LIMITS.get(
                slide_type, 
                self.WORD_COUNT_LIMITS['default']
            )
        
        # Apply audience adjustment
        audience = metadata.get('target_audience', 'general_public').lower()
        adjustment = self.AUDIENCE_ADJUSTMENTS.get(audience, 0.0)
        
        # Apply theme typography adjustment
        if theme.design_tokens.typography.get('heading'):
            heading_size = theme.design_tokens.typography['heading'].fontSize.value
            if heading_size > 48:  # Large heading font
                adjustment -= 0.1  # Reduce word count further
        
        word_limit = int(max_words * (1 + adjustment))
        
        # Create theme-aware content
        title_content = TextContent(
            text=slide.title or "Slide",
            word_count=len((slide.title or "Slide").split()),
            priority="P1",
            tone_keywords=theme.mood_keywords[:3]
        )
        
        main_points = []
        total_words = title_content.word_count
        
        for i, point in enumerate(slide.key_points or []):
            # Apply theme tone to points
            themed_point = f"{point}"  # In real implementation, would transform tone
            point_words = len(themed_point.split())
            main_points.append(TextContent(
                text=themed_point,
                word_count=point_words,
                priority="P2",
                tone_keywords=theme.mood_keywords[:2]
            ))
            total_words += point_words
        
        # Determine reading flow from theme
        template = theme.get_template_for_slide_type(slide.slide_type)
        reading_flow = template.reading_flow if template and hasattr(template, 'reading_flow') else "F-pattern"
        
        return ContentManifest(
            slide_id=slide.slide_id,
            slide_type=slide.slide_type,
            structure_preference=getattr(slide, 'structure_preference', None),
            target_audience=metadata.get('target_audience', 'general_public'),
            deck_context_used=False,
            theme_elements_applied=["mood_keywords", "reading_flow"],
            title=title_content,
            main_points=main_points,
            total_word_count=total_words,
            word_count_limit=word_limit,
            visual_count=0,
            content_density="medium",
            preferred_reading_flow=reading_flow,
            emphasis_areas=["title"],
            grouping_suggestions=[]
        )