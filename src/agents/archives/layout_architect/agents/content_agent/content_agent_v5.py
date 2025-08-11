"""
Content Agent V5 - Clean Architecture Implementation
===================================================

This module implements a streamlined content generation pipeline that combines:
- V3's elegant 2-step component planning
- V4's proven strategic briefing and specialist execution

Pipeline Stages:
1. Component Planning (2-step approach from V3)
2. Strategic Briefing (from V4)
3. Parallel Specialist Execution (from V4)
4. Deterministic Assembly (from V4)
5. Icon Enrichment (from V4)

Author: AI Assistant
Date: 2024
Version: 5.0 (Clean Architecture)
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import os
import base64
from io import BytesIO

from pydantic import BaseModel, Field
from pydantic_ai import Agent
import google.generativeai as genai

# Import google.genai for Imagen 3
try:
    from google import genai as google_genai
    from google.genai import types as genai_types
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("google-genai not installed. Imagen 3 generation will not be available.")

# Import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Pillow not installed. Image processing features will not be available.")

# Import rembg for background removal
try:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("rembg not installed. Advanced background removal will not be available.")

# Import from other modules
from src.agents.layout_architect.agents.content_agent.content_agent_v2 import (
    ContentManifest, VisualSpec
)
from src.models.design_tokens import ThemeDefinition
from src.models.agents import Slide, PresentationStrawman
from src.utils.model_utils import create_model_with_fallback
from src.utils.playbooks_v4 import (
    TEXT_PLAYBOOK,
    ANALYTICS_PLAYBOOK,
    IMAGE_PLAYBOOK,
    DIAGRAM_PLAYBOOK,
    TABLE_PLAYBOOK,
    ICON_PLAYBOOK,
    PlaybookSession,
    get_text_strategy,
    get_analytics_strategy,
    get_image_archetype,
    get_diagram_pattern,
    get_table_structure
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
DEFAULT_MODEL = "gemini-2.5-pro"
FLASH_MODEL = "gemini-2.5-flash"  # For simple classification tasks

# ============================================================================
# PLAYBOOK SELECTION GUIDE
# ============================================================================

PLAYBOOK_SELECTION_GUIDE = {
    "text": {
        "title_slide": "Use ONLY for presentation title/intro slides with presenter information",
        "section_divider": "Use ONLY for section breaks and transitions between topics",
        "agenda_slide": "Use ONLY for presentation agenda/outline slides",
        "content_heavy": "Use for detailed, text-rich informational slides with multiple sections",
        "data_driven": "Use when presenting data insights, statistics, and metrics",
        "visual_heavy": "Use when visuals dominate with minimal supporting text",
        "mixed_content": "Use when text and visuals have equal importance and need balance",
        "diagram_focused": "Use when the main content is explaining a diagram or framework",
        "conclusion_slide": "Use ONLY for final/closing/thank you slides",
        "summary_slide": "Use for recap/summary of key points",
        "case_study_slide": "Use for customer stories with problem/solution/benefit structure",
        "executive_summary": "Use for high-level overview slides for executives",
        "comparison": "Use for comparing different options or approaches",
        "process_explanation": "Use for explaining step-by-step processes",
        "default": "Fallback when no specific type matches"
    },
    "analytics": {
        "comparison": "Use for comparing 2-4 items side-by-side (bar charts, column charts)",
        "trend_analysis": "Use for showing changes over time (line charts, area charts)",
        "distribution": "Use for showing parts of a whole (pie charts, donut charts)",
        "composition": "Use for showing component breakdown (stacked bars, treemaps)",
        "correlation": "Use for showing relationships between variables (scatter plots)"
    },
    "image": {
        "hero_image": "Use for high-impact, full-width imagery that dominates the slide",
        "spot_illustration": "Use for small, focused illustrations that support specific points",
        "conceptual_metaphor": "Use for abstract concepts that need visual metaphors",
        "data_humanization": "Use for making data relatable through human-centric imagery"
    },
    "diagram": {
        "process_flow": "Use for sequential processes with clear steps and flow",
        "organizational_hierarchy": "Use for org charts and hierarchical structures",
        "system_architecture": "Use for technical system diagrams and architectures",
        "concept_map": "Use for showing relationships between ideas or concepts",
        "comparison_matrix": "Use for detailed feature/option comparisons in matrix form"
    },
    "table": {
        "data_summary": "Use for presenting numerical data in rows and columns",
        "feature_list": "Use for listing features, benefits, or specifications",
        "comparison_matrix": "Use for comparing multiple items across multiple criteria"
    }
}

# Smart defaults based on slide_type
SMART_DEFAULTS = {
    "text": {
        "title_slide": "title_slide",
        "section_divider": "section_divider",
        "conclusion_slide": "conclusion_slide",
        "data_driven": "data_driven",
        "visual_heavy": "visual_heavy",
        "content_heavy": "content_heavy",
        "diagram_focused": "diagram_focused",
        "summary_slide": "summary_slide",
        "agenda_slide": "agenda_slide",
        # Default to mixed_content for unmatched types
        "_default": "mixed_content"
    },
    "analytics": {
        "data_driven": "trend_analysis",
        # Default to comparison for most cases
        "_default": "comparison"
    },
    "image": {
        "title_slide": "hero_image",
        "visual_heavy": "hero_image",
        "section_divider": "conceptual_metaphor",
        # Default to spot illustration
        "_default": "spot_illustration"
    },
    "diagram": {
        "diagram_focused": "process_flow",
        "process_explanation": "process_flow",
        # Default to concept map
        "_default": "concept_map"
    },
    "table": {
        "data_driven": "data_summary",
        "comparison": "comparison_matrix",
        # Default to feature list
        "_default": "feature_list"
    }
}

# ============================================================================
# MODELS
# ============================================================================

class ComponentsList(BaseModel):
    """Simple list of required components"""
    components: List[str] = Field(
        description="List of required component types: text, analytics, image, diagram, table"
    )

class PlaybookSelections(BaseModel):
    """Selected playbook for each component"""
    selections: Dict[str, str] = Field(
        description="Map of component type to selected playbook key"
    )

class PlannedComponent(BaseModel):
    """Component specification with playbook selection"""
    component_type: str = Field(
        description="Type of component: text, analytics, image, diagram, or table"
    )
    selected_playbook_key: str = Field(
        description="The specific playbook strategy key selected for this component"
    )
    rationale: str = Field(
        description="Brief explanation of why this playbook was selected"
    )

class SubContainer(BaseModel):
    """Individual content piece within a narrative container"""
    role: str = Field(description="Content role from playbook (e.g., 'problem_heading')")
    tag: str = Field(description="HTML tag to use")
    word_limit: int = Field(description="Maximum words for this content")
    purpose: str = Field(description="Purpose of this content piece")

class NarrativeContainer(BaseModel):
    """Container with narrative context and positioning"""
    container_id: str = Field(
        description="Unique identifier like 'col-1', 'grid-1-1'"
    )
    position: Dict[str, Any] = Field(
        description="Physical location (column, grid coordinates)"
    )
    narrative_role: str = Field(
        description="Role in narrative (e.g., 'problem_section', 'solution_section')"
    )
    narrative_sequence: int = Field(
        description="Order in the story flow (1, 2, 3...)"
    )
    sub_containers: List[SubContainer] = Field(
        description="Individual content pieces within this container"
    )
    relationship_to_others: Optional[str] = Field(
        default=None,
        description="How this relates to other containers (e.g., 'leads_to_col_2')"
    )

class StrategicBrief(BaseModel):
    """Output from Stage 2: Strategic Briefing"""
    component_type: str = Field(
        description="Type of component this brief is for"
    )
    playbook_key: str = Field(
        description="The playbook strategy being used"
    )
    detailed_instruction: str = Field(
        description="Hyper-detailed instructions for the specialist"
    )
    required_elements: Dict[str, Any] = Field(
        description="Specific elements the specialist must include"
    )
    style_guidelines: Dict[str, str] = Field(
        description="Style and formatting guidelines"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Constraints and limitations"
    )
    reference_examples: Optional[List[str]] = Field(
        default=None,
        description="Example outputs for reference"
    )
    # New narrative container fields
    narrative_arc: Optional[str] = Field(
        default=None,
        description="Overall narrative structure (e.g., 'Problem/Solution/Benefit')"
    )
    layout_type: Optional[str] = Field(
        default=None,
        description="Layout pattern (e.g., 'two-column', 'grid-2x2')"
    )
    narrative_containers: Optional[List[NarrativeContainer]] = Field(
        default=None,
        description="Container specifications with narrative mapping"
    )
    flow_instructions: Optional[str] = Field(
        default=None,
        description="How the narrative flows across containers"
    )

class StrategicBriefingOutput(BaseModel):
    """Complete output from Stage 2"""
    briefs: List[StrategicBrief]

class ContentBlock(BaseModel):
    """Individual content block with HTML and text"""
    role: str  # "title", "main_point", "supporting_point", "presenter_info", etc.
    content_html: str
    content_text: str

class ContentContainer(BaseModel):
    """A positioned content container for layout-aware content"""
    container_id: str = Field(
        description="Unique identifier like 'grid-1-1', 'col-1', 'main'"
    )
    position: Dict[str, Any] = Field(
        description="Position specification with layout type and coordinates"
    )
    content: ContentBlock = Field(
        description="The actual content in this container"
    )
    z_index: int = Field(
        default=0,
        description="Layering order for overlapping containers"
    )
    responsive_behavior: str = Field(
        default="flow",
        description="How container behaves on different screen sizes: flow, hide, stack"
    )
    semantic_role: Optional[str] = Field(
        default=None,
        description="Semantic meaning: hero, supporting, evidence, callout"
    )
    visual_hierarchy: Optional[int] = Field(
        default=None,
        description="Visual importance from 1 (most) to 5 (least)"
    )

class TextContentV4(BaseModel):
    """Enhanced text output with narrative arc awareness"""
    title: str
    content_blocks: List[ContentBlock]
    narrative_flow: str  # "opening", "building", "climax", "resolution"
    tone_markers: List[str]  # ["authoritative", "inspiring", "data-driven"]
    transition_hooks: Dict[str, str] = Field(
        default_factory=dict,
        description="Hooks for connecting to other slides"
    )

class LayoutAwareTextContent(BaseModel):
    """Text content with container specifications"""
    title: str
    layout_type: str = Field(
        description="Layout pattern: two-column, three-column, grid-2x2, grid-2x3, etc."
    )
    containers: List[ContentContainer] = Field(
        description="Positioned content containers"
    )
    narrative_flow: str
    tone_markers: List[str]
    total_containers: int = Field(
        description="Total number of containers used"
    )

class AnalyticsContentV4(BaseModel):
    """Enhanced analytics output"""
    chart_type: str
    title: str
    data_points: List[Dict[str, Any]]
    insights: List[str]
    visual_encoding: Dict[str, str]  # {"x": "time", "y": "revenue", "color": "category"}

class ImageContentV4(BaseModel):
    """Enhanced image output with Imagen 3 support"""
    archetype: str  # From IMAGE_PLAYBOOK
    primary_subject: str
    art_direction: Dict[str, str]
    mood_keywords: List[str]
    composition_notes: str
    
    # New fields for Imagen 3
    imagen_prompt: str = Field(
        default="",
        description="Optimized prompt for Imagen 3 generation"
    )
    imagen_negative_prompt: Optional[str] = Field(
        default=None,
        description="What to avoid in the generated image"
    )
    imagen_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "aspectRatio": "16:9",  # Default aspect ratio
            "model": "imagen-3.0-generate-002",
            "safety_settings": "block_only_high",
            "person_generation": "allow_adult"
        },
        description="Configuration for Imagen 3 API"
    )
    generated_image_url: Optional[str] = Field(
        default=None,
        description="URL of generated image (if available)"
    )
    generated_image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded generated image"
    )
    
    # Transparent version fields
    transparent_image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded transparent PNG (background removed)"
    )
    has_transparent_version: bool = Field(
        default=False,
        description="Whether a transparent version was generated"
    )

class DiagramContentV4(BaseModel):
    """Enhanced diagram output"""
    pattern: str  # From DIAGRAM_PLAYBOOK
    core_elements: List[Dict[str, str]]
    relationships: List[Dict[str, str]]
    flow_direction: str
    visual_hierarchy: List[str]

class TableContentV4(BaseModel):
    """Enhanced table output"""
    structure_type: str  # From TABLE_PLAYBOOK
    headers: List[str]
    rows: List[List[str]]
    emphasis_cells: List[Tuple[int, int]]
    summary_insight: str
    html_table: str = Field(default="", description="Complete HTML table representation")

class IconEnrichmentOutput(BaseModel):
    """Output from Stage 5: Icon Enrichment"""
    slide_manifests: List[ContentManifest]
    icon_strategy: str = Field(
        description="Overall icon strategy for the deck"
    )
    icon_assignments: Dict[str, List[Dict[str, str]]] = Field(
        description="Icon assignments per slide",
        default_factory=dict
    )

# ============================================================================
# STAGE 1: COMPONENT PLANNING (2-STEP APPROACH)
# ============================================================================

async def identify_required_components(slide: Slide) -> List[str]:
    """
    Simple component identification - just classify what's needed.
    Uses lightweight model for fast classification.
    """
    logger.info(f"Step 1: Identifying required components for: {slide.title}")
    
    prompt = f"""You are an AI assistant that analyzes a presentation slide's data and identifies the core content components needed.

Your only job is to classify which of the following five components are required:
- text: Almost always required for titles and explanations
- image: Needed for visual impact, photos, or illustrations  
- diagram: Needed for showing processes, flows, or relationships
- table: Needed for structured, grid-based data
- analytics: Needed for charts, graphs, and data visualizations

CRITICAL RULES:
1. If analytics_needed has content, you MUST include "analytics" in components
2. If visuals_needed has content, you MUST include "image" in components
3. If diagrams_needed has content, you MUST include "diagram" in components
4. If tables_needed has content, you MUST include "table" in components
5. Text is almost always required unless explicitly empty

The strawman fields (analytics_needed, visuals_needed, diagrams_needed, tables_needed) are the SINGLE SOURCE OF TRUTH.

Analyze this slide data:
{{
  "title": "{slide.title}",
  "slide_type": "{slide.slide_type}",
  "narrative": "{slide.narrative or ''}",
  "key_points": {json.dumps(slide.key_points) if slide.key_points else '[]'},
  "analytics_needed": "{slide.analytics_needed or ''}",
  "visuals_needed": "{slide.visuals_needed or ''}",
  "diagrams_needed": "{slide.diagrams_needed or ''}",
  "tables_needed": "{slide.tables_needed or ''}"
}}

Your output MUST be a simple JSON object with a single key "components" containing a list of the required component strings.

Example Output:
{{"components": ["text", "analytics", "image"]}}"""
    
    # Use faster model for simple classification
    agent = Agent(
        create_model_with_fallback(FLASH_MODEL),
        result_type=ComponentsList,
        system_prompt="You are a component classifier for presentation slides."
    )
    
    result = await agent.run(prompt)
    return result.data.components

def format_selection_guide(component_type: str) -> str:
    """Format the selection guide for a component type into a readable prompt section."""
    if component_type not in PLAYBOOK_SELECTION_GUIDE:
        return "No guide available"
    
    guide = PLAYBOOK_SELECTION_GUIDE[component_type]
    formatted_lines = []
    for key, description in guide.items():
        formatted_lines.append(f"  • {key}: {description}")
    
    return "\n".join(formatted_lines)

async def select_playbook_strategies(
    slide: Slide, 
    components: List[str]
) -> Dict[str, str]:
    """
    Select the best playbook strategy for each required component.
    """
    logger.info(f"Step 2: Selecting playbook strategies for components: {components}")
    
    # Build component context including analytics_needed, visuals_needed, diagrams_needed
    context_parts = [
        f'"title": "{slide.title}"',
        f'"slide_type": "{slide.slide_type}"',
        f'"narrative": "{slide.narrative or ""}"',
        f'"key_points": {json.dumps(slide.key_points) if slide.key_points else "[]"}'
    ]
    
    # Add the specific needs fields
    if slide.analytics_needed:
        context_parts.append(f'"analytics_needed": "{slide.analytics_needed}"')
    if slide.visuals_needed:
        context_parts.append(f'"visuals_needed": "{slide.visuals_needed}"')
    if slide.diagrams_needed:
        context_parts.append(f'"diagrams_needed": "{slide.diagrams_needed}"')
    
    # Build structured prompt with selection guides
    prompt = f"""You are a strategic content planner. Select the BEST playbook strategy for each component.

IMPORTANT RULES:
1. For TEXT components: If the slide_type matches a playbook key, USE THAT KEY
2. Only select different strategies if the slide content strongly suggests it
3. Be specific - avoid defaulting to generic options like "mixed_content" unless truly needed

Slide Context:
- slide_type: "{slide.slide_type}"
- title: "{slide.title}"
- narrative: "{slide.narrative or 'Not specified'}"
- key_points: {json.dumps(slide.key_points) if slide.key_points else 'None'}
- analytics_needed: "{slide.analytics_needed or 'None'}"
- visuals_needed: "{slide.visuals_needed or 'None'}"
- diagrams_needed: "{slide.diagrams_needed or 'None'}"

Required Components: {json.dumps(components)}

{chr(10).join([f"{comp.upper()} Selection Guide:\n{format_selection_guide(comp)}" for comp in components])}

Based on the slide data above, select the most appropriate strategy for each component.
CRITICAL: For text components, if slide_type="{slide.slide_type}", strongly consider using text="{slide.slide_type}" if it exists in the guide.

Example Mappings:
- slide_type="title_slide" → text="title_slide"
- slide_type="data_driven" with trend data → analytics="trend_analysis"
- slide_type="section_divider" → text="section_divider", image="conceptual_metaphor"

Your output must be a JSON object with a "selections" key:
{{"selections": {{"component_type": "selected_playbook_key"}}}}"""
    
    # Use faster model for classification
    agent = Agent(
        create_model_with_fallback(FLASH_MODEL),
        result_type=PlaybookSelections,
        system_prompt="You are an expert at selecting content strategies for presentations."
    )
    
    try:
        result = await agent.run(prompt)
        selections = result.data.selections
        
        # Add smart fallback logic for any missing components
        for component in components:
            if component not in selections:
                # Use SMART_DEFAULTS based on slide_type
                smart_default = None
                if component in SMART_DEFAULTS:
                    smart_default = SMART_DEFAULTS[component].get(slide.slide_type)
                    if not smart_default:
                        smart_default = SMART_DEFAULTS[component].get("_default")
                
                if smart_default:
                    logger.info(f"No playbook selected for {component}, using smart default: {smart_default}")
                    selections[component] = smart_default
                else:
                    logger.warning(f"No playbook selected for {component}, using fallback")
                    # Ultimate fallbacks
                    fallbacks = {
                        "text": "mixed_content",
                        "analytics": "comparison",
                        "image": "spot_illustration",
                        "diagram": "concept_map",
                        "table": "feature_list"
                    }
                    selections[component] = fallbacks.get(component, "default")
        
        # Log the final selections for debugging
        logger.info(f"Playbook selection for slide_type='{slide.slide_type}':")
        for comp, selection in selections.items():
            logger.info(f"  {comp} → {selection}")
        
        return selections
        
    except Exception as e:
        logger.error(f"Error in playbook selection: {e}")
        # Return smart defaults based on slide_type
        selections = {}
        for comp in components:
            if comp in SMART_DEFAULTS:
                smart_default = SMART_DEFAULTS[comp].get(slide.slide_type)
                if not smart_default:
                    smart_default = SMART_DEFAULTS[comp].get("_default")
                selections[comp] = smart_default or "default"
            else:
                selections[comp] = "default"
        
        return selections

# ============================================================================
# STAGE 2: STRATEGIC BRIEFING (FROM V4)
# ============================================================================

def map_narrative_to_containers(
    playbook_key: str,
    layout_type: str,
    slide: Slide
) -> Dict[str, Any]:
    """
    Map playbook narrative elements to physical containers based on layout.
    Returns a dictionary with containers and flow instructions.
    """
    # Get the playbook content
    playbook_content = TEXT_PLAYBOOK.get(playbook_key, TEXT_PLAYBOOK["default"])
    html_containers = playbook_content.get("html_containers", [])
    layout_adaptations = playbook_content.get("layout_adaptations", {})
    narrative_arc = playbook_content.get("narrative_arc", "")
    
    # Get layout-specific adaptation
    layout_guide = layout_adaptations.get(layout_type, layout_adaptations.get("standard", ""))
    
    narrative_containers = []
    
    if layout_type == "two-column" or layout_type == "two_column":
        # Example: case_study with two columns
        if "Problem" in layout_guide and "Solution" in layout_guide:
            # Column 1: Problem section
            problem_containers = [c for c in html_containers if "problem" in c["role"]]
            narrative_containers.append(NarrativeContainer(
                container_id="col-1",
                position={"column": 1},
                narrative_role="problem_section",
                narrative_sequence=1,
                sub_containers=[
                    SubContainer(
                        role=c["role"],
                        tag=c["tag"],
                        word_limit=c["word_limit"],
                        purpose=c["purpose"]
                    ) for c in problem_containers
                ],
                relationship_to_others="leads_to_col_2"
            ))
            
            # Column 2: Solution and Benefit sections
            solution_benefit_containers = [c for c in html_containers 
                                         if "solution" in c["role"] or "benefit" in c["role"]]
            narrative_containers.append(NarrativeContainer(
                container_id="col-2",
                position={"column": 2},
                narrative_role="solution_and_benefit_section",
                narrative_sequence=2,
                sub_containers=[
                    SubContainer(
                        role=c["role"],
                        tag=c["tag"],
                        word_limit=c["word_limit"],
                        purpose=c["purpose"]
                    ) for c in solution_benefit_containers
                ],
                relationship_to_others="resolves_col_1"
            ))
    
    elif layout_type == "three-column" or layout_type == "three_column":
        # Each major section gets its own column
        sections = narrative_arc.split(" / ")
        for i, section in enumerate(sections[:3]):  # Max 3 columns
            section_key = section.lower().strip()
            section_containers = [c for c in html_containers if section_key in c["role"]]
            if section_containers:
                narrative_containers.append(NarrativeContainer(
                    container_id=f"col-{i+1}",
                    position={"column": i+1},
                    narrative_role=f"{section_key}_section",
                    narrative_sequence=i+1,
                    sub_containers=[
                        SubContainer(
                            role=c["role"],
                            tag=c["tag"],
                            word_limit=c["word_limit"],
                            purpose=c["purpose"]
                        ) for c in section_containers
                    ],
                    relationship_to_others=f"part_{i+1}_of_narrative"
                ))
    
    elif "grid" in layout_type:
        # Grid layout - distribute containers across grid cells
        grid_size = 4 if "2x2" in layout_type else 6 if "2x3" in layout_type else 4
        containers_per_cell = max(1, len(html_containers) // grid_size)
        
        for i in range(min(grid_size, len(html_containers))):
            row = (i // 2) + 1 if "2x2" in layout_type else (i // 3) + 1
            col = (i % 2) + 1 if "2x2" in layout_type else (i % 3) + 1
            
            start_idx = i * containers_per_cell
            end_idx = start_idx + containers_per_cell
            cell_containers = html_containers[start_idx:end_idx]
            
            if cell_containers:
                narrative_containers.append(NarrativeContainer(
                    container_id=f"grid-{row}-{col}",
                    position={"grid": {"row": row, "col": col}},
                    narrative_role=f"section_{i+1}",
                    narrative_sequence=i+1,
                    sub_containers=[
                        SubContainer(
                            role=c["role"],
                            tag=c["tag"],
                            word_limit=c["word_limit"],
                            purpose=c["purpose"]
                        ) for c in cell_containers
                    ]
                ))
    
    else:
        # Default/centered layout - single container
        narrative_containers.append(NarrativeContainer(
            container_id="main",
            position={"align": "center"},
            narrative_role="main_content",
            narrative_sequence=1,
            sub_containers=[
                SubContainer(
                    role=c["role"],
                    tag=c["tag"],
                    word_limit=c["word_limit"],
                    purpose=c["purpose"]
                ) for c in html_containers
            ]
        ))
    
    # Always add title container that spans the layout
    title_container = next((c for c in html_containers if c["role"] == "title"), None)
    if title_container:
        narrative_containers.insert(0, NarrativeContainer(
            container_id="title",
            position={"span": "full"},
            narrative_role="title",
            narrative_sequence=0,
            sub_containers=[SubContainer(
                role=title_container["role"],
                tag=title_container["tag"],
                word_limit=title_container["word_limit"],
                purpose=title_container["purpose"]
            )]
        ))
    
    # Generate flow instructions based on the layout
    flow_instructions = f"Content flows {layout_type} layout: "
    if layout_type == "two-column":
        flow_instructions += "Left column establishes context, right column provides details/resolution."
    elif layout_type == "three-column":
        flow_instructions += "Progressive narrative from left to right, with central focus in middle."
    elif layout_type == "grid":
        flow_instructions += "Each quadrant presents a distinct but related aspect, reading Z-pattern."
    else:
        flow_instructions += "Natural top-to-bottom narrative flow."
    
    return {
        "containers": narrative_containers,
        "layout_type": layout_type,
        "flow_instructions": flow_instructions
    }

# ============================================================================
# PLAYBOOK ADAPTATION FUNCTIONS
# ============================================================================

class ContainerSpec(BaseModel):
    """Specification for an HTML container"""
    role: str = Field(description="Role of the container (e.g., 'title', 'section_1_heading')")
    tag: str = Field(description="HTML tag (e.g., 'h1', 'h2', 'p')")
    word_limit: int = Field(description="Maximum word count for this container")
    purpose: str = Field(description="Purpose of this container")

class AdaptedPlaybook(BaseModel):
    """Result of playbook adaptation"""
    html_containers: List[ContainerSpec] = Field(
        description="Adapted HTML containers matching slide needs"
    )
    adaptation_notes: str = Field(
        description="Brief explanation of adaptations made"
    )

def should_adapt_playbook(playbook_key: str, component_type: str, slide: Slide) -> bool:
    """Determine if playbook needs adaptation based on slide content."""
    if component_type == "text" and playbook_key == "content_heavy" and slide.key_points:
        # Check if key points don't match expected sections
        playbook = TEXT_PLAYBOOK.get(playbook_key, {})
        sections = [c for c in playbook.get("html_containers", []) if "section" in c.get("role", "")]
        section_count = len(sections) // 2  # Each section has heading + text
        return len(slide.key_points) != section_count
    
    # Add other adaptation rules as needed
    return False

async def adapt_playbook_to_slide(
    playbook_data: Dict[str, Any],
    component_type: str,
    slide: Slide,
    original_playbook_key: str
) -> Dict[str, Any]:
    """Use FLASH_MODEL to adapt playbook structure to slide needs."""
    
    containers = playbook_data.get("html_containers", [])
    sections = [c for c in containers if "section" in c.get("role", "")]
    section_count = len(sections) // 2  # Each section has heading + text
    
    prompt = f"""You are a playbook adapter. Modify the container structure to match the slide's actual content needs.

SLIDE DATA:
- Title: {slide.title}
- Key Points Count: {len(slide.key_points) if slide.key_points else 0}
- Layout: {slide.structure_preference}
- Actual Key Points:
{chr(10).join([f"  {i+1}. {point}" for i, point in enumerate(slide.key_points or [])])}

CURRENT PLAYBOOK CONTAINERS:
- Has {section_count} content sections
- Total containers: {len(containers)}

Original containers:
{json.dumps(containers, indent=2)}

TASK:
The playbook has {section_count} sections but the slide has {len(slide.key_points or [])} key points.
Adapt the containers to properly accommodate all key points while maintaining:
1. The same narrative arc and structure style
2. Appropriate word limits (may need to adjust based on total content)
3. The same HTML tag types
4. Logical grouping if consolidating points

CRITICAL: Each container MUST have ALL four fields: role, tag, word_limit, purpose

EXAMPLE OUTPUT (if adapting from 3 to 5 key points):
{{
  "html_containers": [
    {{"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Frame the topic"}},
    {{"role": "key_point_1_heading", "tag": "h3", "word_limit": 5, "purpose": "Introduce point 1: Rising costs"}},
    {{"role": "key_point_1_text", "tag": "p", "word_limit": 20, "purpose": "Explain the 200% increase"}},
    {{"role": "key_point_2_heading", "tag": "h3", "word_limit": 5, "purpose": "Introduce point 2: Medical errors"}},
    {{"role": "key_point_2_text", "tag": "p", "word_limit": 20, "purpose": "Explain third leading cause"}},
    {{"role": "key_point_3_heading", "tag": "h3", "word_limit": 5, "purpose": "Introduce point 3: Waste"}},
    {{"role": "key_point_3_text", "tag": "p", "word_limit": 20, "purpose": "Explain 30% waste"}},
    {{"role": "key_point_4_heading", "tag": "h3", "word_limit": 5, "purpose": "Introduce point 4: Burnout"}},
    {{"role": "key_point_4_text", "tag": "p", "word_limit": 20, "purpose": "Explain 44% burnout"}},
    {{"role": "key_point_5_heading", "tag": "h3", "word_limit": 5, "purpose": "Introduce point 5: Wait times"}},
    {{"role": "key_point_5_text", "tag": "p", "word_limit": 20, "purpose": "Explain 24% increase"}}
  ],
  "adaptation_notes": "Adapted from 3 sections to 5 key points. Removed subtitle. Reduced text word limits from 100 to 20 for conciseness."
}}"""

    agent = Agent(
        create_model_with_fallback(FLASH_MODEL),
        result_type=AdaptedPlaybook,
        system_prompt="You adapt playbook templates to match content needs. Be concise and practical."
    )
    
    try:
        result = await agent.run(prompt)
        
        # Convert ContainerSpec objects to dicts
        adapted_containers = []
        for container in result.data.html_containers:
            container_dict = {
                "role": container.role,
                "tag": container.tag,
                "word_limit": container.word_limit,
                "purpose": container.purpose
            }
            adapted_containers.append(container_dict)
        
        # Validate adapted containers
        valid = True
        for container in adapted_containers:
            if not all(k in container for k in ['role', 'tag', 'word_limit', 'purpose']):
                logger.warning(f"Invalid container format after adaptation: {container}")
                valid = False
                break
        
        if not valid:
            logger.warning("Adaptation produced invalid containers. Using original.")
            return {"html_containers": containers, "adaptation_notes": "Failed - using original"}
        
        logger.info(f"Successfully adapted {len(containers)} → {len(adapted_containers)} containers")
        return {
            "html_containers": adapted_containers,
            "adaptation_notes": result.data.adaptation_notes
        }
    except Exception as e:
        logger.warning(f"Playbook adaptation failed: {e}. Using original.")
        return {"html_containers": containers, "adaptation_notes": "Error - using original"}

# ============================================================================
# PLAYBOOK DATA EXTRACTION FUNCTIONS
# ============================================================================

async def extract_text_playbook_elements(playbook_key: str, slide: Optional[Slide] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Extract and optionally adapt required_elements and style_guidelines from TEXT_PLAYBOOK."""
    playbook = TEXT_PLAYBOOK.get(playbook_key, TEXT_PLAYBOOK.get("default", {}))
    
    # Check if adaptation is needed
    containers = playbook.get("html_containers", [])
    adaptation_notes = ""
    
    if slide and should_adapt_playbook(playbook_key, "text", slide):
        logger.info(f"Adapting {playbook_key} playbook for {len(slide.key_points)} key points")
        adaptation_result = await adapt_playbook_to_slide(
            playbook, 
            "text", 
            slide, 
            playbook_key
        )
        containers = adaptation_result.get("html_containers", containers)
        adaptation_notes = adaptation_result.get("adaptation_notes", "")
    
    required_elements = {
        "narrative_arc": playbook.get("narrative_arc", ""),
        "containers": containers,
        "purpose": playbook.get("purpose", ""),
        "special_handling": playbook.get("special_handling", ""),
        "adapted": bool(adaptation_notes),
        "adaptation_notes": adaptation_notes
    }
    
    style_guidelines = {
        "tone": playbook.get("tone_guidance", ""),
        "layout_adaptations": json.dumps(playbook.get("layout_adaptations", {}))
    }
    
    return required_elements, style_guidelines

def extract_analytics_playbook_elements(playbook_key: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Extract required_elements and style_guidelines from ANALYTICS_PLAYBOOK."""
    playbook = ANALYTICS_PLAYBOOK.get(playbook_key, ANALYTICS_PLAYBOOK.get("comparison", {}))
    
    required_elements = {
        "chart_types": playbook.get("recommended_charts", []),
        "data_spec": playbook.get("required_data_spec", {}),
        "story_type": playbook.get("story_type", ""),
        "purpose": playbook.get("purpose", "")
    }
    
    style_guidelines = {
        "visual_guidelines": json.dumps(playbook.get("visual_guidelines", {})),
        "annotation_opportunities": ", ".join(playbook.get("annotation_opportunities", []))
    }
    
    return required_elements, style_guidelines

def extract_image_playbook_elements(playbook_key: str, slide: Optional[Slide] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Extract required_elements and style_guidelines from IMAGE_PLAYBOOK with context-aware aspect ratio."""
    playbook = IMAGE_PLAYBOOK.get(playbook_key, IMAGE_PLAYBOOK.get("spot_illustration", {}))
    
    # Determine the best aspect ratio based on context
    aspect_ratio = "16:9"  # Default
    
    if slide:
        # Based on slide type
        if slide.slide_type == "title_slide":
            aspect_ratio = "16:9"  # Full width hero
        elif slide.structure_preference == "two-column":
            aspect_ratio = "1:1"  # Square fits well in columns
        elif slide.structure_preference == "centered":
            aspect_ratio = "16:9"  # Full width
        
        # Based on playbook archetype
        if playbook_key == "hero_image":
            aspect_ratio = "16:9"  # Landscape for hero images
        elif playbook_key == "spot_illustration":
            aspect_ratio = "1:1"  # Square for spot illustrations
        elif playbook_key == "conceptual_metaphor":
            aspect_ratio = "4:3"  # Traditional aspect
        elif playbook_key == "data_humanization":
            aspect_ratio = "3:4"  # Slightly portrait
        
        # Icons are always square
        if "icon" in (slide.visuals_needed or "").lower():
            aspect_ratio = "1:1"
    
    required_elements = {
        "archetype": playbook.get("archetype", ""),
        "composition": playbook.get("composition", {}),
        "purpose": playbook.get("purpose", ""),
        "size_guidance": playbook.get("size_guidance", {}),
        "imagen_aspect_ratio": aspect_ratio  # Add Imagen-specific aspect ratio
    }
    
    style_guidelines = {
        "mood": ", ".join(playbook.get("mood", [])),
        "color_guidance": json.dumps(playbook.get("color_guidance", {})),
        "avoid": ", ".join(playbook.get("avoid", [])) if "avoid" in playbook else "",
        "style_options": ", ".join(playbook.get("style_options", [])) if "style_options" in playbook else "",
        "metaphor_types": ", ".join(playbook.get("metaphor_types", [])) if "metaphor_types" in playbook else ""
    }
    
    logger.info(f"Selected aspect ratio {aspect_ratio} for {playbook_key} on {slide.slide_type if slide else 'unknown'}")
    
    return required_elements, style_guidelines

def extract_diagram_playbook_elements(playbook_key: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Extract required_elements and style_guidelines from DIAGRAM_PLAYBOOK."""
    playbook = DIAGRAM_PLAYBOOK.get(playbook_key, DIAGRAM_PLAYBOOK.get("concept_map", {}))
    
    required_elements = {
        "pattern": playbook.get("pattern", ""),
        "flow_direction": playbook.get("flow_direction", ""),
        "node_types": playbook.get("node_types", []),
        "purpose": playbook.get("purpose", ""),
        "max_elements": playbook.get("max_elements", 0)
    }
    
    style_guidelines = {
        "visual_style": json.dumps(playbook.get("visual_style", {})),
        "layout_guidance": playbook.get("layout_guidance", ""),
        "emphasis_rules": ", ".join(playbook.get("emphasis_rules", []))
    }
    
    return required_elements, style_guidelines

def extract_table_playbook_elements(playbook_key: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Extract required_elements and style_guidelines from TABLE_PLAYBOOK."""
    playbook = TABLE_PLAYBOOK.get(playbook_key, TABLE_PLAYBOOK.get("feature_list", {}))
    
    required_elements = {
        "structure": playbook.get("structure", ""),
        "headers": playbook.get("headers", []),
        "row_guidance": playbook.get("row_guidance", {}),
        "purpose": playbook.get("purpose", "")
    }
    
    style_guidelines = {
        "visual_treatment": json.dumps(playbook.get("visual_treatment", {})),
        "emphasis_strategy": playbook.get("emphasis_strategy", "")
    }
    
    return required_elements, style_guidelines

async def run_strategic_briefing_agent_v2(
    components: List[PlannedComponent],
    slide: Slide,
    theme: ThemeDefinition,
    playbook_session: PlaybookSession
) -> StrategicBriefingOutput:
    """
    Create focused strategic briefs using pre-selected playbooks.
    This synthesizes the playbook instructions with slide-specific data.
    Enhanced to include narrative-to-container mapping for text components.
    """
    logger.info("Stage 2: Creating strategic briefs with pre-selected playbooks")
    
    # Check if we need container mapping for text components
    text_components = [c for c in components if c.component_type == "text"]
    container_mapping = None
    
    if text_components and slide.structure_preference in ["two-column", "grid", "three-column"]:
        # Get the text playbook content
        text_comp = text_components[0]
        text_playbook_content = TEXT_PLAYBOOK.get(text_comp.selected_playbook_key, {})
        
        # Map narrative to containers
        container_mapping = map_narrative_to_containers(
            playbook_key=text_comp.selected_playbook_key,
            layout_type=slide.structure_preference,
            slide=slide
        )
    
    # Build component summaries
    component_summaries = []
    for comp in components:
        # Get playbook content directly from the appropriate playbook
        playbook_content = None
        if comp.component_type == "text":
            playbook_content = TEXT_PLAYBOOK.get(comp.selected_playbook_key, {})
        elif comp.component_type == "analytics":
            playbook_content = ANALYTICS_PLAYBOOK.get(comp.selected_playbook_key, {})
        elif comp.component_type == "image":
            playbook_content = IMAGE_PLAYBOOK.get(comp.selected_playbook_key, {})
        elif comp.component_type == "diagram":
            playbook_content = DIAGRAM_PLAYBOOK.get(comp.selected_playbook_key, {})
        elif comp.component_type == "table":
            playbook_content = TABLE_PLAYBOOK.get(comp.selected_playbook_key, {})
        
        # Record strategy use
        playbook_session.record_strategy_use(comp.component_type, comp.selected_playbook_key)
        
        # Add container mapping info for text components
        if comp.component_type == "text" and container_mapping:
            component_summaries.append(f"""
Component: {comp.component_type}
Selected Strategy: {comp.selected_playbook_key}
Rationale: {comp.rationale}
Playbook Instructions: {json.dumps(playbook_content, indent=2)}
Container Layout: {container_mapping['layout_type']}
Container Mapping: {json.dumps([{
    'id': c.container_id,
    'position': c.position,
    'narrative_role': c.narrative_role,
    'narrative_sequence': c.narrative_sequence,
    'sub_containers': [{'role': sc.role, 'purpose': sc.purpose, 'word_limit': sc.word_limit} for sc in c.sub_containers]
} for c in container_mapping['containers']], indent=2)}
Flow Instructions: {container_mapping['flow_instructions']}
""")
        else:
            component_summaries.append(f"""
Component: {comp.component_type}
Selected Strategy: {comp.selected_playbook_key}
Rationale: {comp.rationale}
Playbook Instructions: {json.dumps(playbook_content, indent=2)}
""")
    
    prompt = f"""You are an expert strategic briefing specialist. Your job is to create detailed execution briefs for EVERY component identified from the strawman.

CRITICAL REQUIREMENTS:
1. You MUST create a brief for EVERY component listed in PRE-SELECTED COMPONENTS - these were identified from the strawman which is the SINGLE SOURCE OF TRUTH
2. You MUST set the playbook_key field to the "Selected Strategy" value from each component
3. You MUST incorporate ALL details from "Playbook Instructions" into your brief
4. The detailed_instruction MUST reference specific elements from the playbook
5. The playbook may have been ADAPTED to match the slide's content - check for "adaptation_notes" in required_elements
6. If you see adapted containers, use those instead of trying to reconcile yourself
7. NEVER skip or omit any component - if a component is listed, it MUST get a brief

## SLIDE DATA
Title: {slide.title}
Type: {slide.slide_type}
Narrative: {slide.narrative or 'Not specified'}
Key Points: {json.dumps(slide.key_points) if slide.key_points else 'None'}
Analytics Needed: {slide.analytics_needed or 'None'}
Visuals Needed: {slide.visuals_needed or 'None'}
Structure Preference: {slide.structure_preference or 'None'}

## THEME
Mood: {', '.join(theme.mood_keywords)}
Formality: {theme.formality_level}
Visual Guidelines: {json.dumps(theme.visual_guidelines)}

## PRE-SELECTED COMPONENTS AND STRATEGIES
{chr(10).join(component_summaries)}

## YOUR TASK
For each component, create a strategic brief that:

1. EXTRACTS from the Playbook Instructions:
   - For TEXT: narrative_arc, html_containers (with roles, tags, word_limits), tone_guidance, layout_adaptations
   - For ANALYTICS: chart type, data structure, visual encoding specs, insights format
   - For IMAGE: archetype details, composition rules, art direction, mood keywords
   - For DIAGRAM: pattern type, flow direction, core elements, visual hierarchy
   - For TABLE: structure type, header requirements, data organization

2. TRANSFORMS this into:
   - playbook_key: MUST be set to the "Selected Strategy" value
   - detailed_instruction: Step-by-step instructions incorporating ALL playbook details
   - required_elements: Structured data (e.g., containers array, chart specs) extracted from playbook
   - style_guidelines: Extracted style rules from the playbook
   - constraints: Word limits, technical constraints from playbook

3. ENSURES the brief is executable without needing the original playbook

EXAMPLE for text component with title_slide playbook:
{{
  "component_type": "text",
  "playbook_key": "title_slide",
  "detailed_instruction": "Create text content following the Introduction/Context/Promise narrative arc from the playbook. Structure the content into three HTML containers as specified: (1) h1 tag for the title/introduction with max 10 words to hook the audience, (2) h2 tag for subtitle/context with max 15 words to provide context, (3) p tag for presenter info/promise with max 20 words to establish credibility. Maintain professional, confident, welcoming tone throughout. For centered layout, all elements should be center-aligned with vertical spacing.",
  "required_elements": {{
    "narrative_arc": "Introduction / Context / Promise",
    "containers": [
      {{"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Hook the audience"}},
      {{"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Provide context"}},
      {{"role": "presenter_info", "tag": "p", "word_limit": 20, "purpose": "Establish credibility"}}
    ]
  }},
  "style_guidelines": {{
    "tone": "professional, confident, welcoming",
    "layout": "centered with vertical spacing"
  }},
  "constraints": ["Total word count must not exceed 45 words", "Must include presenter information"]
}}

Remember: The playbook_key MUST be populated and ALL playbook details MUST be incorporated into the brief."""

    agent = Agent(
        create_model_with_fallback(DEFAULT_MODEL),
        result_type=StrategicBriefingOutput,
        system_prompt="You are a strategic briefing specialist who creates detailed execution plans."
    )
    
    result = await agent.run(prompt)
    
    # VALIDATION: Ensure we got briefs for all components
    if len(result.data.briefs) < len(components):
        logger.error(f"MISSING BRIEFS: Got {len(result.data.briefs)} briefs but expected {len(components)}")
        logger.error(f"Components requested: {[c.component_type for c in components]}")
        logger.error(f"Briefs received: {[b.component_type for b in result.data.briefs]}")
        
        # Find missing components and create default briefs
        brief_types = {b.component_type for b in result.data.briefs}
        for comp in components:
            if comp.component_type not in brief_types:
                logger.warning(f"Creating default brief for missing component: {comp.component_type}")
                # Create a default brief
                default_brief = StrategicBrief(
                    component_type=comp.component_type,
                    playbook_key=comp.selected_playbook_key,
                    detailed_instruction=f"Create {comp.component_type} content for the slide. Use the {comp.selected_playbook_key} playbook approach.",
                    required_elements={},
                    style_guidelines={},
                    constraints=[]
                )
                result.data.briefs.append(default_brief)
    
    # Apply deterministic extraction of playbook data
    for i, brief in enumerate(result.data.briefs):
        if i < len(components):
            comp = components[i]
            
            # Extract playbook elements based on component type
            req_elems = {}
            style_guide = {}
            
            if comp.component_type == "text":
                req_elems, style_guide = await extract_text_playbook_elements(comp.selected_playbook_key, slide)
            elif comp.component_type == "analytics":
                req_elems, style_guide = extract_analytics_playbook_elements(comp.selected_playbook_key)
            elif comp.component_type == "image":
                req_elems, style_guide = extract_image_playbook_elements(comp.selected_playbook_key, slide)
            elif comp.component_type == "diagram":
                req_elems, style_guide = extract_diagram_playbook_elements(comp.selected_playbook_key)
            elif comp.component_type == "table":
                req_elems, style_guide = extract_table_playbook_elements(comp.selected_playbook_key)
            
            # Update the brief with deterministic data
            brief.required_elements = req_elems
            brief.style_guidelines = style_guide
            brief.playbook_key = comp.selected_playbook_key  # Ensure this is set
            
            logger.info(f"Stage 2 Brief for {brief.component_type} (enhanced):")
            logger.info(f"  - playbook_key: {brief.playbook_key}")
            logger.info(f"  - has required_elements: {bool(brief.required_elements)}")
            logger.info(f"  - has containers: {'containers' in brief.required_elements if brief.required_elements else False}")
            logger.info(f"  - was adapted: {brief.required_elements.get('adapted', False) if brief.required_elements else False}")
            logger.info(f"  - has style_guidelines: {bool(brief.style_guidelines)}")
    
    return result.data

# ============================================================================
# STAGE 3: SPECIALIST EXECUTION (FROM V4)
# ============================================================================

def determine_layout_type(slide: Slide, components: List[str]) -> str:
    """Determine the best layout type based on slide structure preference and components."""
    structure_pref = slide.structure_preference or "default"
    component_count = len(components)
    has_visuals = any(c in components for c in ["analytics", "image", "diagram"])
    
    # Map structure preferences to layout types
    if structure_pref == "two-column" or structure_pref == "two_column":
        return "two-column"
    elif structure_pref == "three-column" or structure_pref == "three_column":
        return "three-column"
    elif structure_pref == "grid" or component_count >= 4:
        if component_count <= 4:
            return "grid-2x2"
        else:
            return "grid-2x3"
    elif structure_pref == "centered":
        return "centered"
    elif has_visuals and component_count >= 3:
        return "grid-2x2"
    else:
        return "two-column"

def create_container_layout(layout_type: str, content_elements: List[Dict[str, str]]) -> Dict[str, Any]:
    """Create container position specifications based on layout type."""
    layouts = {
        "two-column": [
            {"row": 1, "col": 1, "span_rows": 1, "span_cols": 1},
            {"row": 1, "col": 2, "span_rows": 1, "span_cols": 1}
        ],
        "three-column": [
            {"row": 1, "col": 1}, {"row": 1, "col": 2}, {"row": 1, "col": 3}
        ],
        "grid-2x2": [
            {"row": 1, "col": 1}, {"row": 1, "col": 2},
            {"row": 2, "col": 1}, {"row": 2, "col": 2}
        ],
        "grid-2x3": [
            {"row": 1, "col": 1}, {"row": 1, "col": 2}, {"row": 1, "col": 3},
            {"row": 2, "col": 1}, {"row": 2, "col": 2}, {"row": 2, "col": 3}
        ],
        "centered": [
            {"row": 1, "col": 1, "span_cols": 1, "align": "center"}
        ]
    }
    
    return layouts.get(layout_type, layouts["two-column"])

async def run_text_specialist_v4(
    brief: StrategicBrief,
    slide: Slide,
    theme: ThemeDefinition,
    deck_summary: str,
    completed_slides: Optional[List[ContentManifest]] = None
) -> TextContentV4:
    """
    Simplified text specialist that executes detailed brief.
    Enhanced to handle narrative container mapping when available.
    """
    logger.info(f"Text Specialist executing brief for: {slide.title}")
    
    # Build the prompt for text generation
    prompt = f"""You are an expert content writer. Execute the following brief precisely.

## PLAYBOOK: {brief.playbook_key}

## YOUR DETAILED BRIEF
{brief.detailed_instruction}

## REQUIRED ELEMENTS
{json.dumps(brief.required_elements, indent=2)}

## STYLE GUIDELINES  
{json.dumps(brief.style_guidelines, indent=2)}

## CONSTRAINTS
{chr(10).join(f"- {c}" for c in brief.constraints)}

## HTML GENERATION REQUIREMENTS
CRITICAL: You MUST generate proper HTML for EVERY content block:
1. Each ContentBlock requires BOTH content_html AND content_text fields
2. Use the HTML tags specified in the containers from required_elements
3. The content_html field must contain properly formatted HTML with the specified tag
4. The content_text field contains the plain text version (no HTML)

## CONTAINER-TO-HTML MAPPING
Based on the containers in required_elements, create ContentBlock objects as follows:
{chr(10).join([f"- role: '{c['role']}' → use <{c['tag']}> tag → max {c['word_limit']} words" for c in brief.required_elements.get('containers', [])])}

EXAMPLE:
For a container with role="key_point_1_heading", tag="h3", word_limit=5:
{{
  "role": "key_point_1_heading",
  "content_html": "<h3>Costs up 200%</h3>",
  "content_text": "Costs up 200%"
}}

## CONTEXT
Slide Title: {slide.title}
Deck Summary: {deck_summary}
Theme Mood: {', '.join(theme.mood_keywords)}

Create content that follows the brief EXACTLY. Generate HTML for ALL content blocks."""

    agent = Agent(
        create_model_with_fallback(DEFAULT_MODEL),
        result_type=TextContentV4,
        system_prompt="You are a precise content writer who follows briefs exactly and generates proper HTML."
    )
    
    result = await agent.run(prompt)
    
    # Post-process to ensure HTML is generated for all blocks
    containers_map = {}
    if 'containers' in brief.required_elements:
        for container in brief.required_elements['containers']:
            containers_map[container['role']] = container['tag']
    
    for block in result.data.content_blocks:
        # Check if HTML exists but doesn't contain actual HTML tags
        has_html_tags = block.content_html and block.content_html.strip().startswith('<')
        
        # Get the content (from either field)
        content = block.content_text or block.content_html or ""
        
        # If HTML is missing or doesn't have tags, generate it
        if not has_html_tags and content:
            # First try to get tag from containers map
            if block.role in containers_map:
                tag = containers_map[block.role]
                block.content_html = f"<{tag}>{content}</{tag}>"
                # Also ensure content_text is set
                if not block.content_text:
                    block.content_text = content
                logger.warning(f"Generated missing HTML for role '{block.role}' with tag '{tag}'")
            else:
                # Fallback: guess tag based on role
                if 'heading' in block.role.lower():
                    tag = 'h3'
                elif 'title' in block.role.lower():
                    tag = 'h1'
                else:
                    tag = 'p'
                block.content_html = f"<{tag}>{content}</{tag}>"
                # Also ensure content_text is set
                if not block.content_text:
                    block.content_text = content
                logger.warning(f"Generated missing HTML for role '{block.role}' with guessed tag '{tag}'")
    
    # Debug: Log final state of all blocks
    logger.info(f"Text specialist final output for {slide.title}:")
    for i, block in enumerate(result.data.content_blocks):
        logger.info(f"  Block {i+1} [{block.role}]: has_html={bool(block.content_html and '<' in block.content_html)}")
    
    return result.data

# DEPRECATED: Old container implementation - replaced by narrative container mapping in Stage 2
# async def run_text_specialist_v5_containers(
#     brief: StrategicBrief,
#     slide: Slide,
#     theme: ThemeDefinition,
#     deck_summary: str,
#     layout_type: str,
#     completed_slides: Optional[List[ContentManifest]] = None
# ) -> LayoutAwareTextContent:
#     """
#     Enhanced text specialist that generates container-based content.
#     """
#     logger.info(f"Text Specialist (V5) executing container-based brief for: {slide.title}")
#     
#     # Get layout specifications from playbook
#     layout_info = brief.layout_guidance or {}
#     
#     prompt = f"""You are an expert content writer who creates layout-aware, container-based content.
# 
# ## YOUR DETAILED BRIEF
# {brief.detailed_instruction}
# 
# ## LAYOUT SPECIFICATION
# Layout Type: {layout_type}
# {json.dumps(layout_info, indent=2) if layout_info else "Use standard layout for " + layout_type}
# 
# ## REQUIRED ELEMENTS
# {json.dumps(brief.required_elements, indent=2)}
# 
# ## STYLE GUIDELINES  
# {json.dumps(brief.style_guidelines, indent=2)}
# 
# ## CONTAINER REQUIREMENTS
# Based on the {layout_type} layout, you must organize content into containers:
# - For "two-column": Create 2 containers (left and right columns)
# - For "three-column": Create 3 containers (left, center, right columns)
# - For "grid-2x2": Create up to 4 containers in a 2x2 grid
# - For "grid-2x3": Create up to 6 containers in a 2x3 grid
# - For "centered": Create 1 main container with centered alignment
# 
# Each container should have:
# 1. A unique container_id (e.g., "col-1", "grid-1-1", "main")
# 2. Clear semantic role (e.g., "hero", "supporting", "evidence")
# 3. Appropriate HTML content wrapped in container divs
# 4. Visual hierarchy (1-5, where 1 is most important)
# 
# ## CONTEXT
# Slide Title: {slide.title}
# Deck Summary: {deck_summary}
# Theme Mood: {', '.join(theme.mood_keywords)}
# 
# Create container-based content that follows the brief EXACTLY."""
# 
#     agent = Agent(
#         create_model_with_fallback(DEFAULT_MODEL),
#         result_type=LayoutAwareTextContent,
#         system_prompt="You are a layout-aware content writer who organizes content into positioned containers."
#     )
#     
#     result = await agent.run(prompt)
#     return result.data

async def run_analytics_specialist_v4(
    brief: StrategicBrief,
    slide: Slide,
    theme: ThemeDefinition
) -> AnalyticsContentV4:
    """
    Analytics specialist that executes strategic brief.
    """
    logger.info(f"Analytics Specialist executing brief for: {slide.title}")
    
    prompt = f"""You are a data visualization expert. Execute the following brief precisely.

## YOUR DETAILED BRIEF
{brief.detailed_instruction}

## REQUIRED ELEMENTS
{json.dumps(brief.required_elements, indent=2)}

## STYLE GUIDELINES
{json.dumps(brief.style_guidelines, indent=2)}

## DATA CONTEXT
Analytics Needed: {slide.analytics_needed}
Key Points: {json.dumps(slide.key_points)}

Create a chart specification that follows the brief EXACTLY."""

    agent = Agent(
        create_model_with_fallback(DEFAULT_MODEL),
        result_type=AnalyticsContentV4,
        system_prompt="You are a data visualization specialist who follows briefs exactly."
    )
    
    result = await agent.run(prompt)
    return result.data

async def run_image_specialist_v4(
    brief: StrategicBrief,
    slide: Slide,
    theme: ThemeDefinition
) -> ImageContentV4:
    """
    Image specialist that executes strategic brief.
    """
    logger.info(f"Image Specialist executing brief for: {slide.title}")
    
    prompt = f"""You are a visual design expert. Execute the following brief precisely.

## YOUR DETAILED BRIEF  
{brief.detailed_instruction}

## REQUIRED ELEMENTS
{json.dumps(brief.required_elements, indent=2)}

## STYLE GUIDELINES
{json.dumps(brief.style_guidelines, indent=2)}

## VISUAL CONTEXT
Visuals Needed: {slide.visuals_needed or 'Not specified'}
Theme Mood: {', '.join(theme.mood_keywords)}

Create an image specification that follows the brief EXACTLY.

ADDITIONALLY, create an 'imagen_prompt' field with a detailed, descriptive prompt for Imagen 3:
- Be specific about style (photograph, illustration, vector art, digital art, etc.)
- Include composition details (rule of thirds, centered, golden ratio, etc.)
- Specify lighting and mood (natural light, studio lighting, dramatic, soft, etc.)
- Add relevant style modifiers (professional, modern, clean, corporate, artistic)
- Include color guidance from the theme
- Keep it under 200 words but be highly descriptive
- Focus on visual elements rather than abstract concepts

Also set the 'imagen_config' aspectRatio to: {brief.required_elements.get('imagen_aspect_ratio', '16:9')}
This has been pre-selected based on the slide layout and image type.

Example imagen_prompt: "A professional photograph of a modern hospital corridor with natural lighting, shot from a low angle perspective using rule of thirds composition. Clean, bright atmosphere with medical staff in the background. Corporate photography style with shallow depth of field. Colors: medical blues and whites with green accents. High-quality, sharp focus, 4K resolution."

If the slide needs icons or spot illustrations, adjust accordingly:
"Minimalist vector icon of a stethoscope, flat design style, centered composition on white background. Simple line art with 2-3 colors: medical blue and teal accents. Clean, modern, professional iconography suitable for healthcare presentations." """

    agent = Agent(
        create_model_with_fallback(DEFAULT_MODEL),
        result_type=ImageContentV4,
        system_prompt="You are a visual design specialist who follows briefs exactly."
    )
    
    result = await agent.run(prompt)
    
    # Phase 2: Call Imagen 3 if enabled
    if os.getenv("ENABLE_IMAGEN3_GENERATION", "true").lower() == "true":
        try:
            logger.info("Phase 2: Generating image with Imagen 3...")
            
            # Ensure we have an imagen prompt
            if not result.data.imagen_prompt:
                logger.warning("No imagen_prompt generated, using composition notes as fallback")
                result.data.imagen_prompt = f"{result.data.archetype} style image of {result.data.primary_subject}. {result.data.composition_notes}"
            
            imagen_result = await generate_image_with_imagen3(result.data)
            
            if imagen_result["success"]:
                result.data.generated_image_base64 = imagen_result["base64"]
                
                # Check for transparent version
                if imagen_result.get("has_transparent", False) and "transparent_base64" in imagen_result:
                    result.data.transparent_image_base64 = imagen_result["transparent_base64"]
                    result.data.has_transparent_version = True
                    logger.info("Successfully generated image with Imagen 3 (including transparent version)")
                else:
                    logger.info("Successfully generated image with Imagen 3")
            else:
                logger.warning(f"Imagen 3 generation failed: {imagen_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Imagen 3 generation error: {e}")
            # Continue with specification only
    else:
        logger.info("Imagen 3 generation disabled, returning specification only")
    
    return result.data

def remove_white_background(image_bytes: bytes, threshold: int = 240) -> bytes:
    """
    Remove white background from image using color threshold.
    Perfect for clean icons and illustrations with white backgrounds.
    
    Args:
        image_bytes: Raw image bytes
        threshold: RGB threshold for white detection (default 240)
    
    Returns:
        Bytes of transparent PNG
    """
    if not PIL_AVAILABLE:
        logger.warning("PIL not available, cannot remove background")
        return image_bytes
    
    try:
        # Open image and convert to RGBA
        img = Image.open(BytesIO(image_bytes))
        img = img.convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            # If pixel is white/near-white, make transparent
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                newData.append((255, 255, 255, 0))  # Transparent
            else:
                newData.append(item)
        
        img.putdata(newData)
        
        # Save to bytes
        output = BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error removing white background: {e}")
        return image_bytes

def remove_background_advanced(image_bytes: bytes) -> bytes:
    """
    Remove background using AI-powered rembg.
    Works with complex backgrounds and preserves edge quality.
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        Bytes of transparent PNG
    """
    if not REMBG_AVAILABLE:
        logger.warning("rembg not available, falling back to simple removal")
        return remove_white_background(image_bytes)
    
    try:
        # Use rembg to remove background
        output = rembg_remove(image_bytes)
        return output
        
    except Exception as e:
        logger.error(f"Error with rembg, falling back to simple removal: {e}")
        return remove_white_background(image_bytes)

def should_remove_background(archetype: str) -> bool:
    """
    Determine if background should be removed based on image archetype.
    
    Args:
        archetype: The image archetype (e.g., 'minimalist_vector_art')
    
    Returns:
        True if background should be removed
    """
    # Archetypes that benefit from background removal
    bg_removal_archetypes = {
        'minimalist_vector_art',  # Icons and spot illustrations
        'symbolic_representation',  # Simple symbolic images
        # Can add more archetypes as needed
    }
    
    return archetype in bg_removal_archetypes

async def generate_image_with_imagen3(
    image_spec: ImageContentV4
) -> Dict[str, Any]:
    """
    Call Google's imagen-3.0-generate-002 API using google.genai SDK.
    
    Returns:
        Dictionary with image data and metadata
    """
    try:
        # Check if google.genai is available
        if not GOOGLE_GENAI_AVAILABLE:
            logger.error("google-genai not installed. Run: pip install google-genai")
            return {"success": False, "error": "google-genai not installed"}
        
        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment")
            return {"success": False, "error": "GOOGLE_API_KEY or GEMINI_API_KEY not configured"}
        
        logger.info("Using google.genai for Imagen 3 generation")
        
        try:
            # Initialize client
            client = google_genai.Client(api_key=api_key)
            
            # Get aspect ratio from config
            aspect_ratio = image_spec.imagen_config.get("aspectRatio", "16:9")
            
            # Generate image
            logger.info(f"Generating image with prompt: {image_spec.imagen_prompt[:100]}...")
            
            # Use the latest Imagen model
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=image_spec.imagen_prompt,
                config=genai_types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                )
            )
            
            # Check for generated images
            if hasattr(response, 'generated_images') and response.generated_images:
                logger.info(f"Successfully generated {len(response.generated_images)} image(s)")
                
                # Extract first image
                generated_image = response.generated_images[0]
                
                if hasattr(generated_image, 'image'):
                    image_obj = generated_image.image
                    
                    # Get image bytes
                    if hasattr(image_obj, 'image_bytes'):
                        image_bytes = image_obj.image_bytes
                        logger.info(f"Image bytes extracted: {len(image_bytes)} bytes")
                        
                        # Convert to base64
                        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        
                        result = {
                            "success": True,
                            "base64": img_base64,
                            "metadata": {
                                "model": "imagen-3.0-generate-002",
                                "aspect_ratio": aspect_ratio,
                                "prompt_used": image_spec.imagen_prompt
                            }
                        }
                        
                        # Check if background removal should be applied
                        if should_remove_background(image_spec.archetype):
                            logger.info(f"Applying background removal for archetype: {image_spec.archetype}")
                            try:
                                # For minimalist vector art, use simple white removal
                                if image_spec.archetype == 'minimalist_vector_art':
                                    transparent_bytes = remove_white_background(image_bytes)
                                else:
                                    # For other archetypes, use advanced removal
                                    transparent_bytes = remove_background_advanced(image_bytes)
                                
                                # Convert transparent version to base64
                                transparent_base64 = base64.b64encode(transparent_bytes).decode('utf-8')
                                result["transparent_base64"] = transparent_base64
                                result["has_transparent"] = True
                                logger.info("Background removal successful")
                            except Exception as e:
                                logger.error(f"Background removal failed: {e}")
                                result["has_transparent"] = False
                        
                        return result
                    else:
                        logger.error("No image_bytes attribute found")
                        return {"success": False, "error": "Unable to extract image bytes"}
                else:
                    logger.error("No image attribute found in generated_image")
                    return {"success": False, "error": "No image data in response"}
            else:
                logger.warning("No generated_images in response")
                return {"success": False, "error": "No images generated"}
                
        except Exception as e:
            logger.error(f"Imagen 3 generation failed: {e}")
            
            # Try Imagen 4 if Imagen 3 fails
            if "imagen-3" in str(e).lower() or "not found" in str(e).lower():
                logger.info("Trying Imagen 4 instead...")
                try:
                    response = client.models.generate_images(
                        model='imagen-4.0-generate-preview-06-06',
                        prompt=image_spec.imagen_prompt,
                        config=genai_types.GenerateImagesConfig(
                            number_of_images=1,
                        )
                    )
                    
                    if hasattr(response, 'generated_images') and response.generated_images:
                        generated_image = response.generated_images[0]
                        if hasattr(generated_image.image, 'image_bytes'):
                            image_bytes = generated_image.image.image_bytes
                            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                            
                            result = {
                                "success": True,
                                "base64": img_base64,
                                "metadata": {
                                    "model": "imagen-4.0-generate-preview",
                                    "aspect_ratio": "default",
                                    "prompt_used": image_spec.imagen_prompt
                                }
                            }
                            
                            # Apply background removal for Imagen 4 as well
                            if should_remove_background(image_spec.archetype):
                                logger.info(f"Applying background removal for archetype: {image_spec.archetype}")
                                try:
                                    if image_spec.archetype == 'minimalist_vector_art':
                                        transparent_bytes = remove_white_background(image_bytes)
                                    else:
                                        transparent_bytes = remove_background_advanced(image_bytes)
                                    
                                    transparent_base64 = base64.b64encode(transparent_bytes).decode('utf-8')
                                    result["transparent_base64"] = transparent_base64
                                    result["has_transparent"] = True
                                    logger.info("Background removal successful")
                                except Exception as e:
                                    logger.error(f"Background removal failed: {e}")
                                    result["has_transparent"] = False
                            
                            return result
                except Exception as e2:
                    logger.error(f"Imagen 4 also failed: {e2}")
            
            # Provide helpful error messages
            if "quota" in str(e).lower():
                return {"success": False, "error": f"Quota error: {e}. Check your API quotas."}
            elif "billing" in str(e).lower():
                return {"success": False, "error": f"Billing error: {e}. Enable billing for your project."}
            else:
                return {"success": False, "error": f"API error: {str(e)}"}
            
    except Exception as e:
        logger.error(f"Imagen 3 generation failed: {e}")
        return {"success": False, "error": str(e)}

async def run_diagram_specialist_v4(
    brief: StrategicBrief,
    slide: Slide,
    theme: ThemeDefinition
) -> DiagramContentV4:
    """
    Diagram specialist that executes strategic brief.
    """
    logger.info(f"Diagram Specialist executing brief for: {slide.title}")
    
    prompt = f"""You are a diagram design expert. Execute the following brief precisely.

## YOUR DETAILED BRIEF
{brief.detailed_instruction}

## REQUIRED ELEMENTS
{json.dumps(brief.required_elements, indent=2)}

## STYLE GUIDELINES
{json.dumps(brief.style_guidelines, indent=2)}

## DIAGRAM CONTEXT
Diagrams Needed: {slide.diagrams_needed or 'Not specified'}
Key Points: {json.dumps(slide.key_points)}

Create a diagram specification that follows the brief EXACTLY."""

    agent = Agent(
        create_model_with_fallback(DEFAULT_MODEL),
        result_type=DiagramContentV4,
        system_prompt="You are a diagram specialist who follows briefs exactly."
    )
    
    result = await agent.run(prompt)
    return result.data

async def run_table_specialist_v4(
    brief: StrategicBrief,
    slide: Slide,
    theme: ThemeDefinition
) -> TableContentV4:
    """
    Table specialist that executes strategic brief.
    """
    logger.info(f"Table Specialist executing brief for: {slide.title}")
    
    prompt = f"""You are a data table expert. Execute the following brief precisely.

## YOUR DETAILED BRIEF
{brief.detailed_instruction}

## REQUIRED ELEMENTS
{json.dumps(brief.required_elements, indent=2)}

## STYLE GUIDELINES
{json.dumps(brief.style_guidelines, indent=2)}

## TABLE CONTEXT
Key Points: {json.dumps(slide.key_points)}
Data Elements: {slide.analytics_needed or 'Not specified'}

## HTML TABLE GENERATION REQUIREMENTS
CRITICAL: You MUST generate a complete HTML table in the html_table field:
1. Use proper HTML table structure: <table>, <thead>, <tbody>, <tr>, <th>, <td>
2. Add class="data-table" to the <table> element
3. Add class="table-header" to <thead>
4. Add class="emphasis" to cells specified in emphasis_cells (using row,col indices)
5. Include all headers in <thead> with <th> tags
6. Include all data rows in <tbody> with <td> tags

EXAMPLE HTML:
<table class="data-table">
  <thead class="table-header">
    <tr>
      <th>Challenge</th>
      <th>Statistic</th>
      <th>Impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Rising Costs</td>
      <td class="emphasis">200% increase</td>
      <td>Reduced access</td>
    </tr>
  </tbody>
</table>

Create a table specification that follows the brief EXACTLY. Generate both the data structure AND the HTML representation."""

    agent = Agent(
        create_model_with_fallback(DEFAULT_MODEL),
        result_type=TableContentV4,
        system_prompt="You are a table design specialist who follows briefs exactly."
    )
    
    result = await agent.run(prompt)
    
    # Post-process to ensure HTML table is generated
    if not result.data.html_table and result.data.headers and result.data.rows:
        logger.warning("Table HTML missing, generating from data")
        result.data.html_table = generate_table_html(
            headers=result.data.headers,
            rows=result.data.rows,
            emphasis_cells=result.data.emphasis_cells
        )
    
    # Debug logging
    logger.info(f"Table specialist final output for {slide.title}:")
    logger.info(f"  Headers: {result.data.headers}")
    logger.info(f"  Rows: {len(result.data.rows)} rows")
    logger.info(f"  Has HTML: {bool(result.data.html_table)}")
    logger.info(f"  HTML length: {len(result.data.html_table) if result.data.html_table else 0} chars")
    
    return result.data

def generate_table_html(headers: List[str], rows: List[List[str]], emphasis_cells: List[Tuple[int, int]]) -> str:
    """Generate HTML table from data if not provided by AI"""
    html = ['<table class="data-table">']
    
    # Add header
    html.append('  <thead class="table-header">')
    html.append('    <tr>')
    for header in headers:
        html.append(f'      <th>{header}</th>')
    html.append('    </tr>')
    html.append('  </thead>')
    
    # Add body
    html.append('  <tbody>')
    for row_idx, row in enumerate(rows):
        html.append('    <tr>')
        for col_idx, cell in enumerate(row):
            # Check if this cell should be emphasized
            if (row_idx, col_idx) in emphasis_cells:
                html.append(f'      <td class="emphasis">{cell}</td>')
            else:
                html.append(f'      <td>{cell}</td>')
        html.append('    </tr>')
    html.append('  </tbody>')
    
    html.append('</table>')
    return '\n'.join(html)

# ============================================================================
# STAGE 4: DETERMINISTIC ASSEMBLY (FROM V4)
# ============================================================================

def assemble_content_manifest_v4(
    slide: Slide,
    component_outputs: Dict[str, Any],
    playbook_session: PlaybookSession
) -> ContentManifest:
    """
    Deterministically assemble all component outputs into final manifest.
    """
    logger.info("Stage 4: Assembling content manifest")
    
    # Initialize manifest with actual V2 fields
    manifest = ContentManifest(
        slide_id=slide.slide_id,
        slide_type=slide.slide_type,
        structure_preference=slide.structure_preference,
        title="",
        main_points=[],
        supporting_text=None,
        primary_visual=None,
        supporting_visuals=[],
        total_word_count=0,
        visual_count=0,
        content_density="medium",
        theme_elements_applied=[],
        deck_context_used=True
    )
    
    # Process text content
    text_components = [k for k in component_outputs.keys() if k.startswith("text")]
    subtitle_text = ""
    supporting_texts = []
    
    for text_key in text_components:
        text_output = component_outputs[text_key]
        if isinstance(text_output, TextContentV4):
            manifest.title = text_output.title
            
            # Process content blocks
            for block in text_output.content_blocks:
                if block.role == "subtitle":
                    subtitle_text = block.content_text
                elif block.role == "main_point":
                    manifest.main_points.append(block.content_text)
                elif block.role == "supporting_point":
                    supporting_texts.append(block.content_text)
                elif block.role == "presenter_info":
                    # Add to main_points as these are important talking points
                    manifest.main_points.append(block.content_text)
                elif block.role in ["supporting_text", "paragraph"]:
                    supporting_texts.append(block.content_text)
            
            # Add theme elements
            manifest.theme_elements_applied.append(f"narrative_{text_output.narrative_flow}")
            for tone in text_output.tone_markers:
                manifest.theme_elements_applied.append(f"tone_{tone}")
    
    # Combine supporting texts
    if subtitle_text:
        manifest.supporting_text = subtitle_text
        if supporting_texts:
            manifest.supporting_text += "\n" + "\n".join(supporting_texts)
    elif supporting_texts:
        manifest.supporting_text = "\n".join(supporting_texts)
    
    # Process analytics content
    analytics_components = [k for k in component_outputs.keys() if k.startswith("analytics")]
    for analytics_key in analytics_components:
        analytics_output = component_outputs[analytics_key]
        if isinstance(analytics_output, AnalyticsContentV4):
            # Create a visual spec for the chart
            visual_spec = VisualSpec(
                visual_type="chart",
                description=analytics_output.title,
                placement_guidance="primary",
                style_notes={
                    "chart_type": analytics_output.chart_type,
                    "data_points": analytics_output.data_points,
                    "encoding": analytics_output.visual_encoding,
                    "insights": analytics_output.insights
                }
            )
            if not manifest.primary_visual:
                manifest.primary_visual = visual_spec
            else:
                manifest.supporting_visuals.append(visual_spec)
            manifest.visual_count += 1
    
    # Process image content
    image_components = [k for k in component_outputs.keys() if k.startswith("image")]
    for image_key in image_components:
        image_output = component_outputs[image_key]
        if isinstance(image_output, ImageContentV4):
            visual_spec = VisualSpec(
                visual_type="image",
                description=image_output.primary_subject,
                placement_guidance="primary",
                style_notes={
                    "archetype": image_output.archetype,
                    "mood_keywords": image_output.mood_keywords,
                    "composition": image_output.composition_notes,
                    **image_output.art_direction
                }
            )
            manifest.supporting_visuals.append(visual_spec)
            manifest.visual_count += 1
    
    # Process diagram content
    diagram_components = [k for k in component_outputs.keys() if k.startswith("diagram")]
    for diagram_key in diagram_components:
        diagram_output = component_outputs[diagram_key]
        if isinstance(diagram_output, DiagramContentV4):
            visual_spec = VisualSpec(
                visual_type="diagram",
                description=f"{diagram_output.pattern} diagram",
                placement_guidance="primary",
                style_notes={
                    "pattern": diagram_output.pattern,
                    "elements": diagram_output.core_elements,
                    "relationships": diagram_output.relationships,
                    "flow_direction": diagram_output.flow_direction,
                    "hierarchy": diagram_output.visual_hierarchy
                }
            )
            manifest.supporting_visuals.append(visual_spec)
            manifest.visual_count += 1
    
    # Process table content  
    table_components = [k for k in component_outputs.keys() if k.startswith("table")]
    for table_key in table_components:
        table_output = component_outputs[table_key]
        if isinstance(table_output, TableContentV4):
            # Create a visual spec for the table
            visual_spec = VisualSpec(
                visual_type="table",
                description=table_output.summary_insight,
                placement_guidance="supporting",
                style_notes={
                    "structure": table_output.structure_type,
                    "headers": table_output.headers,
                    "rows": table_output.rows,
                    "emphasis_cells": table_output.emphasis_cells
                }
            )
            manifest.supporting_visuals.append(visual_spec)
            manifest.visual_count += 1
    
    # Ensure we have a primary visual if we have any visuals
    if not manifest.primary_visual and manifest.supporting_visuals:
        manifest.primary_visual = manifest.supporting_visuals.pop(0)
    
    # Calculate word count
    word_count = len(manifest.title.split())
    for point in manifest.main_points:
        word_count += len(point.split())
    if manifest.supporting_text:
        word_count += len(manifest.supporting_text.split())
    manifest.total_word_count = word_count
    
    # Determine content density based on word count and visual count
    if word_count < 50 and manifest.visual_count <= 1:
        manifest.content_density = "light"
    elif word_count > 150 or manifest.visual_count > 3:
        manifest.content_density = "heavy"
    else:
        manifest.content_density = "medium"
    
    return manifest

# ============================================================================
# STAGE 5: ICON ENRICHMENT (FROM V4)
# ============================================================================

async def run_icon_enrichment_agent(
    content_manifests: List[ContentManifest],
    theme: ThemeDefinition,
    strawman: PresentationStrawman
) -> IconEnrichmentOutput:
    """
    Holistic icon enrichment across all slides.
    Ensures consistency and prevents overuse.
    """
    logger.info("Stage 5: Icon Enrichment")
    
    # Create slide summaries
    slide_summaries = []
    for manifest in content_manifests:
        summary = {
            "slide_id": manifest.slide_id,
            "title": manifest.title,
            "main_points": manifest.main_points,
            "has_primary_visual": bool(manifest.primary_visual),
            "visual_count": manifest.visual_count,
            "word_count": manifest.total_word_count
        }
        slide_summaries.append(summary)
    
    prompt = f"""You are an icon enrichment specialist. Review all slides and strategically add icons for visual enhancement.

## DECK OVERVIEW
Title: {strawman.main_title}
Theme: {strawman.overall_theme}
Audience: {strawman.target_audience}

## THEME GUIDELINES
Visual Style: {json.dumps(theme.visual_guidelines)}
Mood: {', '.join(theme.mood_keywords)}

## ALL SLIDES
{json.dumps(slide_summaries, indent=2)}

## ICON PLAYBOOK
{json.dumps(ICON_PLAYBOOK, indent=2)}

## YOUR TASK
1. Develop a cohesive icon strategy for the entire deck
2. Assign icons judiciously - not every slide needs icons
3. Ensure icon usage enhances rather than clutters
4. Maintain consistency in icon style and meaning
5. For each slide with icons, specify:
   - Which elements get icons
   - What type of icon (see playbook patterns)
   - Specific icon suggestions

Remember: Less is more. Icons should clarify and enhance, not decorate."""

    agent = Agent(
        create_model_with_fallback(DEFAULT_MODEL),
        result_type=IconEnrichmentOutput,
        system_prompt="You are an icon specialist who enhances presentations with meaningful iconography."
    )
    
    # Set slide_manifests to the input manifests
    enrichment_data = {
        "slide_manifests": content_manifests,
        "prompt": prompt
    }
    
    result = await agent.run(json.dumps(enrichment_data))
    
    # Apply icon assignments to manifests
    output = result.data
    output.slide_manifests = content_manifests  # Ensure we return the original manifests
    
    # Apply icon enrichments
    for manifest in output.slide_manifests:
        if manifest.slide_id in output.icon_assignments:
            icons = output.icon_assignments[manifest.slide_id]
            # Add icons as supporting visuals
            for icon in icons:
                icon_spec = VisualSpec(
                    visual_type="icon",
                    description=icon.get("description", "Icon"),
                    placement_guidance="inline",
                    style_notes=icon
                )
                manifest.supporting_visuals.append(icon_spec)
            # Update visual count
            manifest.visual_count += len(icons)
    
    return output

# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

async def process_single_slide(
    slide: Slide,
    theme: ThemeDefinition,
    deck_summary: str,
    strawman: PresentationStrawman,
    completed_slides: Optional[List[ContentManifest]] = None,
    playbook_session: Optional[PlaybookSession] = None
) -> ContentManifest:
    """
    Process a single slide through the clean V5 pipeline.
    """
    if not playbook_session:
        playbook_session = PlaybookSession()
    
    # Stage 1: Two-step Component Planning
    components = await identify_required_components(slide)
    component_playbooks = await select_playbook_strategies(slide, components)
    
    # Convert to PlannedComponent format
    planned_components = []
    for comp_type, playbook_key in component_playbooks.items():
        planned = PlannedComponent(
            component_type=comp_type,
            selected_playbook_key=playbook_key,
            rationale=f"Selected based on slide type '{slide.slide_type}' and content requirements"
        )
        planned_components.append(planned)
    
    # Stage 2: Strategic Briefing
    strategic_briefs = await run_strategic_briefing_agent_v2(
        planned_components,
        slide,
        theme,
        playbook_session
    )
    
    # Stage 3: Parallel Specialist Execution
    specialist_tasks = []
    component_types = []
    
    for brief in strategic_briefs.briefs:
        if brief.component_type == "text":
            task = run_text_specialist_v4(brief, slide, theme, deck_summary, completed_slides)
            specialist_tasks.append(task)
            component_types.append("text")
        elif brief.component_type == "analytics":
            task = run_analytics_specialist_v4(brief, slide, theme)
            specialist_tasks.append(task)
            component_types.append("analytics")
        elif brief.component_type == "image":
            task = run_image_specialist_v4(brief, slide, theme)
            specialist_tasks.append(task)
            component_types.append("image")
        elif brief.component_type == "diagram":
            task = run_diagram_specialist_v4(brief, slide, theme)
            specialist_tasks.append(task)
            component_types.append("diagram")
        elif brief.component_type == "table":
            task = run_table_specialist_v4(brief, slide, theme)
            specialist_tasks.append(task)
            component_types.append("table")
    
    # Run specialists in parallel
    specialist_results = await asyncio.gather(*specialist_tasks)
    
    # Map results to component types
    component_outputs = {}
    type_counters = {}
    
    for comp_type, result in zip(component_types, specialist_results):
        if comp_type in component_outputs:
            type_counters[comp_type] = type_counters.get(comp_type, 1) + 1
            key = f"{comp_type}_{type_counters[comp_type]}"
        else:
            key = comp_type
            type_counters[comp_type] = 1
        
        component_outputs[key] = result
    
    # Stage 4: Deterministic Assembly
    manifest = assemble_content_manifest_v4(
        slide,
        component_outputs,
        playbook_session
    )
    
    return manifest

# DEPRECATED: Old container implementation - replaced by narrative container mapping in Stage 2
# async def process_single_slide_containers(
#     slide: Slide,
#     theme: ThemeDefinition,
#     deck_summary: str,
#     strawman: PresentationStrawman,
#     completed_slides: Optional[List[ContentManifest]] = None,
#     playbook_session: Optional[PlaybookSession] = None,
#     use_containers: bool = True
# ) -> ContentManifest:
#     """
#     Process a single slide with container-based content generation.
#     """
#     if not playbook_session:
#        playbook_session = PlaybookSession()
#    
#    # Stage 1: Two-step Component Planning
#    components = await identify_required_components(slide)
#    component_playbooks = await select_playbook_strategies(slide, components)
#    
#    # Determine layout type for container-based content
#    layout_type = determine_layout_type(slide, components)
#    logger.info(f"Selected layout type: {layout_type}")
#    
#    # Convert to PlannedComponent format
#    planned_components = []
#    for comp_type, playbook_key in component_playbooks.items():
#        planned = PlannedComponent(
#            component_type=comp_type,
#            selected_playbook_key=playbook_key,
#            rationale=f"Selected based on slide type '{slide.slide_type}' and content requirements"
#        )
#        planned_components.append(planned)
#    
#    # Stage 2: Strategic Briefing with layout guidance
#    strategic_briefs = await run_strategic_briefing_agent_v2(
#        planned_components,
#        slide,
#        theme,
#        playbook_session
#    )
#    
#    # Add layout guidance to briefs
#    for brief in strategic_briefs.briefs:
#        brief.layout_guidance = {
#            "layout_type": layout_type,
#            "total_components": len(components),
#            "container_arrangement": create_container_layout(layout_type, [])
#        }
#    
#    # Stage 3: Parallel Specialist Execution with containers
#    specialist_tasks = []
#    component_types = []
#    
#    for brief in strategic_briefs.briefs:
#        if brief.component_type == "text" and use_containers:
#            # Use container-based text specialist
#            task = run_text_specialist_v5_containers(
#                brief, slide, theme, deck_summary, layout_type, completed_slides
#            )
#            specialist_tasks.append(task)
#            component_types.append("text")
#        elif brief.component_type == "text":
#            # Use regular text specialist
#            task = run_text_specialist_v4(brief, slide, theme, deck_summary, completed_slides)
#            specialist_tasks.append(task)
#            component_types.append("text")
#        elif brief.component_type == "analytics":
#            task = run_analytics_specialist_v4(brief, slide, theme)
#            specialist_tasks.append(task)
#            component_types.append("analytics")
#        elif brief.component_type == "image":
#            task = run_image_specialist_v4(brief, slide, theme)
#            specialist_tasks.append(task)
#            component_types.append("image")
#        elif brief.component_type == "diagram":
#            task = run_diagram_specialist_v4(brief, slide, theme)
#            specialist_tasks.append(task)
#            component_types.append("diagram")
#        elif brief.component_type == "table":
#            task = run_table_specialist_v4(brief, slide, theme)
#            specialist_tasks.append(task)
#            component_types.append("table")
#    
#    # Run specialists in parallel
#    specialist_results = await asyncio.gather(*specialist_tasks)
#    
#    # Map results to component types
#    component_outputs = {}
#    type_counters = {}
#    
#    for comp_type, result in zip(component_types, specialist_results):
#        if comp_type in component_outputs:
#            type_counters[comp_type] = type_counters.get(comp_type, 1) + 1
#            key = f"{comp_type}_{type_counters[comp_type]}"
#        else:
#            key = comp_type
#            type_counters[comp_type] = 1
#        
#        component_outputs[key] = result
#    
#    # Stage 4: Container-aware Assembly
#    if use_containers and "text" in component_outputs and isinstance(component_outputs["text"], LayoutAwareTextContent):
#        manifest = assemble_content_manifest_with_containers(
#            slide,
#            component_outputs,
#            playbook_session,
#            layout_type
#        )
#    else:
#        manifest = assemble_content_manifest_v4(
#            slide,
#            component_outputs,
#            playbook_session
#        )
#    
#     return manifest

# DEPRECATED: Old container assembly
# def assemble_content_manifest_with_containers(
#    slide: Slide,
#    component_outputs: Dict[str, Any],
#    playbook_session: PlaybookSession,
#    layout_type: str
#) -> ContentManifest:
#    """
#    Assemble content manifest with container positioning information.
#    """
#    logger.info("Stage 4: Container-aware Assembly")
#    
#    # Start with regular assembly
#    manifest = assemble_content_manifest_v4(slide, component_outputs, playbook_session)
#    
#    # Add container metadata
#    manifest.supporting_content["layout_type"] = layout_type
#    manifest.supporting_content["containers"] = []
#    
#    # Process container-based text content
#    if "text" in component_outputs and isinstance(component_outputs["text"], LayoutAwareTextContent):
#        text_content = component_outputs["text"]
#        
#        # Store container information
#        for container in text_content.containers:
#            container_info = {
#                "id": container.container_id,
#                "position": container.position,
#                "semantic_role": container.semantic_role,
#                "visual_hierarchy": container.visual_hierarchy,
#                "content_type": "text",
#                "content": {
#                    "role": container.content.role,
#                    "html": container.content.content_html,
#                    "text": container.content.content_text
#                }
#            }
#            manifest.supporting_content["containers"].append(container_info)
#    
#    # Add positioning for other components
#    container_positions = create_container_layout(layout_type, [])
#    next_position_idx = len(manifest.supporting_content["containers"])
#    
#    # Position analytics components
#    for key, output in component_outputs.items():
#        if key.startswith("analytics") and isinstance(output, AnalyticsContentV4):
#            if next_position_idx < len(container_positions):
#                pos = container_positions[next_position_idx]
#                container_info = {
#                    "id": f"analytics-{next_position_idx}",
#                    "position": {"layout": "grid", "coordinates": pos},
#                    "semantic_role": "data",
#                    "visual_hierarchy": 2,
#                    "content_type": "analytics",
#                    "content": {
#                        "chart_type": output.chart_type,
#                        "title": output.title
#                    }
#                }
#                manifest.supporting_content["containers"].append(container_info)
#                next_position_idx += 1
#    
#    # Position image components
#    for key, output in component_outputs.items():
#        if key.startswith("image") and isinstance(output, ImageContentV4):
#            if next_position_idx < len(container_positions):
#                pos = container_positions[next_position_idx]
#                container_info = {
#                    "id": f"image-{next_position_idx}",
#                    "position": {"layout": "grid", "coordinates": pos},
#                    "semantic_role": "visual",
#                    "visual_hierarchy": 2,
#                    "content_type": "image",
#                    "content": {
#                        "archetype": output.archetype,
#                        "subject": output.primary_subject
#                    }
#                }
#                manifest.supporting_content["containers"].append(container_info)
#                next_position_idx += 1
#    
#    return manifest

# ============================================================================
# CONTENT AGENT V5 CLASS
# ============================================================================

class ContentAgentV5:
    """
    Clean Content Agent V5 implementation.
    
    Combines V3's elegant 2-step planning with V4's proven execution.
    No version switching or legacy code.
    """
    
    def __init__(self):
        """
        Initialize Content Agent V5.
        """
        self.playbook_session = PlaybookSession()
    
    async def run(
        self,
        slide: Slide,
        theme: ThemeDefinition,
        strawman: PresentationStrawman,
        completed_slides: Optional[List[ContentManifest]] = None
    ) -> ContentManifest:
        """
        Process a single slide.
        
        Note: For full icon enrichment, use process_all_slides instead.
        """
        deck_summary = f"{strawman.main_title}: {strawman.overall_theme}"
        
        manifest = await process_single_slide(
            slide,
            theme,
            deck_summary,
            strawman,
            completed_slides,
            self.playbook_session
        )
        
        return manifest
    
    async def process_all_slides(
        self,
        slides: List[Slide],
        theme: ThemeDefinition,
        strawman: PresentationStrawman
    ) -> List[ContentManifest]:
        """
        Process all slides with dual-phase orchestration.
        
        Phase 1: Generate core content for all slides
        Phase 2: Enrich with consistent iconography
        """
        deck_summary = f"{strawman.main_title}: {strawman.overall_theme}"
        
        # Phase 1: Core Content Generation
        logger.info("PHASE 1: Core Content Generation")
        manifests = []
        
        for slide in slides:
            logger.info(f"Processing slide {slide.slide_number}: {slide.title}")
            manifest = await process_single_slide(
                slide,
                theme,
                deck_summary,
                strawman,
                manifests.copy(),  # Pass completed slides
                self.playbook_session
            )
            manifests.append(manifest)
            logger.info(f"✓ Completed slide {slide.slide_number}")
        
        # Phase 2: Icon Enrichment
        logger.info("\nPHASE 2: Icon Enrichment")
        enrichment_output = await run_icon_enrichment_agent(
            manifests,
            theme,
            strawman
        )
        
        logger.info(f"✓ Icon strategy: {enrichment_output.icon_strategy}")
        logger.info(f"✓ Enriched {len(enrichment_output.icon_assignments)} slides with icons")
        
        return enrichment_output.slide_manifests