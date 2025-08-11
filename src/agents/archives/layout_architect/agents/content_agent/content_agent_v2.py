"""
Content Agent V2 - A Complete Rebuild
=====================================

Philosophy:
-----------
1. AI-First for Creative Tasks - LLMs handle all creative work
2. Code-First for Logic - Assembly is pure Python, no AI
3. Structure-Aware Text Generation - Content adapts to slide layout
4. Deferred Summary Generation - Summaries generated last with full context

Architecture Overview:
---------------------
    Stage 1: AI Planner
        → Analyzes slide requirements
        → Creates structured task list
        
    Stage 2: AI Specialists (Parallel)
        → Text Specialist: Generates structure-aware content
        → Image Specialist: Creates image prompts
        → Analytics Specialist: Designs data visualizations
        → Diagram Specialist: Builds process/flow diagrams
        
    Stage 3: Deterministic Assembler
        → Pure Python function
        → Maps specialist outputs to ContentManifest
        → No AI involvement

Author: AI Assistant
Date: 2024
Version: 2.0
"""

# ============================================================================
# IMPORTS AND CONSTANTS
# ============================================================================

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# Import existing models that we'll reuse
from src.models.agents import Slide
from src.utils.logger import setup_logger
from src.models.design_tokens import ThemeDefinition
from src.utils.model_utils import create_model_with_fallback

# Set up logging
logger = setup_logger(__name__)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Structure-specific content generation rules
# These define how content should be formatted for each layout type
STRUCTURE_CONTENT_RULES = {
    "Three-Column Layout": {
        "format": "3 columns with ### subtitles",
        "word_count_per_section": (60, 70),
        "total_sections": 3,
        "example": "### Innovation\nAI transforms healthcare through predictive analytics...",
        "instruction": "Generate content for three distinct columns. Each column needs a short ### Subtitle followed by a paragraph of 60-70 words."
    },
    "Bullet Points": {
        "format": "5-7 concise bullet points", 
        "words_per_bullet": (12, 18),
        "total_bullets": (5, 7),
        "example": "• AI reduces diagnosis time by 85% in emergency departments",
        "instruction": "Generate 5-7 distinct bullet points. Each bullet point must be concise, between 12-18 words long."
    },
    "Text Heavy": {
        "format": "Multiple detailed paragraphs with subheadings",
        "word_count_per_paragraph": (150, 180),
        "total_paragraphs": (3, 4),
        "instruction": "Generate 3-4 paragraphs with subheadings. Each paragraph should be 80-100 words of detailed content."
    },
    "Hero Image": {
        "format": "Single powerful statement",
        "total_word_count": (15, 30),
        "instruction": "Generate one single, powerful headline statement and possibly a brief one-sentence sub-heading. Total word count should be under 30."
    },
    "Single Focal Point": {
        "format": "One key message with minimal text",
        "total_word_count": (20, 40),
        "instruction": "Generate one central message with minimal supporting text. Focus on impact over detail."
    },
    "Data Visualization": {
        "format": "Title and key insights only",
        "total_word_count": (150, 180),
        "instruction": "Generate a clear title and 2-3 key data insights. Let the visualization tell the story."
    },
    "Timeline": {
        "format": "Chronological milestones",
        "words_per_milestone": (5, 15),
        "total_milestones": (4, 6),
        "instruction": "Generate 4-6 chronological milestones with dates. Each milestone should be 10-15 words."
    },
    "Comparison": {
        "format": "Side-by-side comparable items",
        "words_per_item": (120, 150),
        "total_items": 2,
        "instruction": "Generate content for exactly 2 items to compare side-by-side. Each item needs 40-60 words."
    },
    "Grid Layout": {
        "format": "Multiple equal-weight items",
        "words_per_item": (180, 210),
        "total_items": (4, 6),
        "instruction": "Generate content for 4-6 grid items. Each item should have a title and 20-30 words of description."
    }
}

# Default model for all AI agents
DEFAULT_MODEL = "gemini-2.5-flash"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PlannerTask(BaseModel):
    """
    Represents a single task identified by the Planner agent.
    Each task will be executed by a specialist agent in parallel.
    """
    task_type: str = Field(
        description="Type of specialist needed: 'text', 'image', 'analytics', or 'diagram'"
    )
    instruction: str = Field(
        description="Specific instruction for the specialist to execute"
    )


class PlannerOutput(BaseModel):
    """
    Output from the Planner agent containing all tasks for a slide.
    """
    tasks: List[PlannerTask] = Field(
        description="List of tasks to be executed by specialists"
    )


class TextContentOutput(BaseModel):
    """
    Structured output from the Text Specialist.
    """
    title: str = Field(description="Main slide title")
    main_points: List[str] = Field(
        description="List of main content points (format varies by structure)"
    )
    supporting_text: Optional[str] = Field(
        default=None,
        description="Additional supporting text if needed"
    )
    word_count: int = Field(description="Total word count of all content")


class VisualSpec(BaseModel):
    """
    Specification for any visual element (image, chart, diagram).
    This is a unified model used by all visual specialists.
    """
    visual_type: str = Field(
        description="Type: 'image', 'chart', 'diagram', 'table'"
    )
    description: str = Field(
        description="Detailed description or prompt for the visual"
    )
    
    # Chart-specific fields
    chart_type: Optional[str] = Field(
        default=None, 
        description="bar, line, pie, scatter, etc."
    )
    data_points: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Structured data for charts"
    )
    axes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Axis labels for charts"
    )
    data_insights: Optional[str] = Field(
        default=None,
        description="Key insight from the data"
    )
    
    # Image-specific fields
    image_prompt: Optional[str] = Field(
        default=None,
        description="Full prompt for image generation"
    )
    composition: Optional[str] = Field(
        default=None,
        description="Image composition details"
    )
    style_keywords: Optional[List[str]] = Field(
        default=None,
        description="Style descriptors for the image"
    )
    
    # Diagram-specific fields
    diagram_style: Optional[str] = Field(
        default=None,
        description="'schematic' or 'artistic'"
    )
    nodes: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Nodes for schematic diagrams"
    )
    connections: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Connections between nodes"
    )
    
    # Common metadata
    theme_colors_used: Optional[List[str]] = Field(
        default=None,
        description="Theme colors to apply"
    )
    priority: str = Field(
        default="P2",
        description="Priority level P1-P4"
    )


class ContentManifest(BaseModel):
    """
    Final output containing all content for a slide.
    This is assembled from specialist outputs.
    """
    slide_id: str
    slide_type: str
    structure_preference: Optional[str] = None
    
    # Text content
    title: str
    main_points: List[str]
    supporting_text: Optional[str] = None
    
    # Visual content
    primary_visual: Optional[VisualSpec] = None
    supporting_visuals: List[VisualSpec] = Field(default_factory=list)
    
    # Metadata
    total_word_count: int
    visual_count: int
    content_density: str = Field(
        description="light, medium, or heavy"
    )
    
    # Theme integration tracking
    theme_elements_applied: List[str] = Field(default_factory=list)
    deck_context_used: bool = Field(default=False)


# ============================================================================
# STAGE 1: AI PLANNER
# ============================================================================

async def run_planner_agent(
    slide: Slide, 
    theme: ThemeDefinition
) -> Dict[str, Any]:
    """
    Analyze slide requirements and create a structured plan of tasks.
    
    The Planner is responsible for:
    1. Understanding what content the slide needs
    2. Breaking it down into specific tasks
    3. Determining which specialists are needed
    
    Args:
        slide: The slide object containing all requirements
        theme: Theme definition for understanding layout constraints
        
    Returns:
        Dictionary containing the task list
        
    Example Output:
        {
            "tasks": [
                {
                    "task_type": "text",
                    "instruction": "Generate 3 columns about AI impact..."
                },
                {
                    "task_type": "analytics", 
                    "instruction": "Create bar chart showing growth..."
                }
            ]
        }
    """
    logger.info(f"Planning tasks for slide {slide.slide_id}: {slide.title}")
    
    # Build the sophisticated planning prompt
    prompt = f"""You are a Senior Content Strategist at a premier consulting firm (think McKinsey, Bain, or BCG). Your task is to analyze a single presentation slide's requirements and create a precise execution plan for specialist AI agents.

## YOUR ROLE & MINDSET

You excel at:
- Breaking down complex communication challenges into actionable tasks
- Understanding how different content elements work together to tell a story
- Knowing exactly what type of visual support enhances specific messages
- Creating plans that result in concrete, specific, data-rich content (never vague placeholders)

## SLIDE CONTEXT & REQUIREMENTS

**Slide Details:**
- **Slide Type**: {slide.slide_type}
- **Title**: {slide.title}
- **Core Narrative**: {slide.narrative or 'To present key information clearly and effectively'}
- **Key Points to Cover**: {json.dumps(slide.key_points) if slide.key_points else 'No specific points provided'}
- **Analytics/Data Needs**: {slide.analytics_needed or 'No specific analytics requested'}
- **Visual Requirements**: {slide.visuals_needed or 'No specific visuals requested'}
- **Layout Structure**: {slide.structure_preference or 'Standard layout'}

**Theme & Design Context:**
- **Mood/Tone**: {', '.join(theme.mood_keywords)}
- **Formality Level**: {theme.formality_level}
- **Visual Style**: {theme.visual_guidelines.get('photography_style', 'professional')} photography, {theme.visual_guidelines.get('data_viz_style', 'clean')} data visualization

## YOUR TASK

Analyze the slide requirements and create a task list for specialist agents. Each task should be:
1. **Specific** - Include concrete details about what to generate
2. **Actionable** - Clear enough that a specialist can execute without ambiguity
3. **Complete** - Include all necessary context within the instruction itself

### SPECIALIST TYPES AVAILABLE:
- **text**: Generates all textual content (title, bullets, paragraphs) following structure rules
- **image**: Creates detailed prompts for imagery, photos, or illustrations
- **analytics**: Generates data visualizations with synthetic data (charts, graphs, tables)
- **diagram**: Creates flowcharts, process diagrams, organizational charts, etc.

### CRITICAL RULES:
1. **ALWAYS include a 'text' task** - Every slide needs textual content
2. **Only add visual tasks if explicitly needed** - Look for keywords like "chart", "graph", "diagram", "visual", "image", etc.
3. **Be specific in instructions** - Instead of "create a chart", say "create a bar chart comparing X, Y, and Z with specific metrics"
4. **Consider the structure** - Tailor text instructions to match the layout (e.g., "Generate 3 columns of content" for Three-Column Layout)
5. **Link visuals to the narrative** - The instruction for any visual task MUST explicitly state which part of the text narrative it is meant to support, prove, or illustrate. (e.g., "Create a chart to visually prove the 'Key Findings' from the text task.")

## OUTPUT FORMAT

Return a JSON object with a single key "tasks" containing an array of task objects:

```json
{{
  "tasks": [
    {{
      "task_type": "text",
      "instruction": "Generate [specific format] about [specific topic] including [specific elements] in a [tone] style that [specific goal]"
    }},
    {{
      "task_type": "[specialist type]",
      "instruction": "Create [specific output] showing [specific content] with [specific requirements]"
    }}
  ]
}}
```

## EXAMPLES FOR DIFFERENT SCENARIOS

**Example 1 - Data-Driven Slide:**
Input: Title "Q3 Revenue Performance", analytics_needed: "Revenue breakdown by region"
Output:
```json
{{
  "tasks": [
    {{
      "task_type": "text",
      "instruction": "Generate a compelling title and 3 key insights about Q3 revenue performance, highlighting regional variations and growth drivers, using a confident and analytical tone"
    }},
    {{
      "task_type": "analytics",
      "instruction": "Create a stacked bar chart showing Q3 revenue breakdown by region (North America, Europe, Asia-Pacific, Others) with YoY growth percentages, using actual-looking synthetic data in millions USD to visually support the '3 key insights' mentioned in the text task"
    }}
  ]
}}
```

**Example 2 - Conceptual Slide with Diagram:**
Input: Title "Our Implementation Process", diagrams_needed: "Process flow"
Output:
```json
{{
  "tasks": [
    {{
      "task_type": "text",
      "instruction": "Generate a clear title and concise descriptions for each phase of the implementation process, emphasizing timeline and key deliverables in a consultative tone"
    }},
    {{
      "task_type": "diagram",
      "instruction": "Create a horizontal process flow diagram with 5 phases (Discovery, Design, Development, Testing, Deployment) including timeline markers and key deliverables to visually illustrate the 'phase descriptions' and 'timeline' mentioned in the text content"
    }}
  ]
}}
```

**Example 3 - Text-Heavy Slide:**
Input: Title "Executive Summary", structure_preference: "Two-Column Layout"
Output:
```json
{{
  "tasks": [
    {{
      "task_type": "text",
      "instruction": "Generate an executive summary in two-column format: left column with 'Key Findings' (4 bullets), right column with 'Recommendations' (4 bullets), maintaining parallel structure and executive-level clarity"
    }}
  ]
}}
```

Now, analyze the provided slide requirements and create the appropriate task plan."""

    # Create the agent with structured output and minimal system prompt
    planner = Agent(
        create_model_with_fallback("gemini-2.5-pro"),
        result_type=PlannerOutput,
        system_prompt="You are a helpful AI assistant that generates structured JSON based on user instructions."
    )
    
    try:
        result = await planner.run(prompt)
        return result.data.model_dump()
    except Exception as e:
        logger.error(f"Planner failed: {e}")
        # Enhanced fallback with structure awareness
        fallback_instruction = f"Generate comprehensive text content for a '{slide.slide_type}' slide titled '{slide.title}' following the '{slide.structure_preference or 'Standard'}' layout structure."
        
        # Add specific guidance based on slide type
        if slide.slide_type == "data_driven":
            fallback_instruction += " Include specific metrics and data points that illustrate the key message."
        elif slide.slide_type == "visual_heavy":
            fallback_instruction += " Focus on concise, impactful statements that complement visual elements."
        elif slide.slide_type == "content_heavy":
            fallback_instruction += " Provide detailed explanations and comprehensive coverage of all key points."
        
        return {
            "tasks": [
                {
                    "task_type": "text",
                    "instruction": fallback_instruction
                }
            ]
        }


# ============================================================================
# STAGE 2: AI SPECIALISTS (PARALLEL EXECUTION)
# ============================================================================
# 
# This stage contains four specialized AI agents that work in parallel:
# 1. Text Specialist - Generates all textual content (titles, bullets, paragraphs)
# 2. Image Specialist - Creates detailed prompts for image generation
# 3. Analytics Specialist - Designs data visualizations with synthetic data
# 4. Diagram Specialist - Builds process flows, org charts, and concept diagrams
#
# Each specialist receives specific instructions from the Planner and produces
# structured output that the Assembler will combine into the final manifest.
# ============================================================================

# -----------------------------------------------------------------------------
# TEXT SPECIALIST - The Primary Content Generator
# -----------------------------------------------------------------------------
async def run_text_specialist(
    instruction: str,
    slide: Slide,
    theme: ThemeDefinition, 
    deck_summary: str,
    completed_slides: Optional[List[ContentManifest]] = None
) -> Dict[str, Any]:
    """
    Generate structure-aware text content for a slide.
    
    This specialist is the most complex because it must:
    1. Understand the slide's structure preference
    2. Generate content in the exact format required
    3. Integrate theme mood and tone
    4. For summary slides, analyze completed content
    
    Args:
        instruction: Specific task from the planner
        slide: The slide object with all details
        theme: Theme for tone and mood
        deck_summary: Overall presentation narrative
        completed_slides: For summary slides, all completed content
        
    Returns:
        Dictionary with structured text content
    """
    logger.info(f"Text specialist working on: {instruction}")
    
    # Get the structure-specific rules
    # This is crucial - content format must match the layout structure
    structure_pref = slide.structure_preference or "Bullet Points"
    structure_rules = STRUCTURE_CONTENT_RULES.get(
        structure_pref,
        STRUCTURE_CONTENT_RULES["Bullet Points"]  # Default fallback
    )
    
    # Build the context-aware prompt
    prompt = f"""You are an expert content strategist and writer for a top-tier consulting firm. Your task is to write the complete textual content for a single presentation slide.

**Deck Summary Context:**
{deck_summary}

**Your Specific Task:**
{instruction}

**Crucial Structure-Aware Content Rules:**
You MUST adapt your output format based on the slide's structure_preference: "{structure_pref}".
{structure_rules['instruction']}

**Slide Details:**
- Title: {slide.title}
- Narrative: {slide.narrative or 'None'}
- Key Points to Address: {json.dumps(slide.key_points) if slide.key_points else 'None'}

**Theme Integration:**
- Mood Keywords to weave in naturally: {', '.join(theme.mood_keywords)}
- Formality Level: {theme.formality_level}"""

    # Add completed slides context for summary/agenda slides
    if completed_slides and slide.slide_type in ['agenda_slide', 'summary_slide']:
        slide_summaries = []
        for completed in completed_slides:
            slide_summaries.append(f"- {completed.title}")
        
        prompt += f"""

**IMPORTANT: This is a summary/agenda slide. Analyze these completed slides:**
{chr(10).join(slide_summaries)}

Generate a concise summary or agenda that captures the key topics covered."""

    prompt += """

**Execution Requirements:**
- Generate concrete, specific content. Use illustrative names, dates, and numbers.
- Follow the structure rules EXACTLY as specified above.
- Return the content as a JSON object with these keys:
  - "title": The main slide title
  - "main_points": List of content points (format varies by structure)
  - "supporting_text": Optional additional text if needed
  - "word_count": Total word count of all content

**Example for Three-Column Layout:**
```json
{
  "title": "AI Transforms Healthcare Delivery",
  "main_points": [
    "### Diagnosis\\nAI algorithms analyze medical images with 94% accuracy, surpassing human radiologists in detecting early-stage cancers. Stanford Medical Center's implementation reduced diagnosis time from 3 days to 2 hours.",
    "### Treatment\\nPersonalized treatment plans powered by machine learning consider 10,000+ variables per patient. Memorial Sloan Kettering reports 23% better outcomes using AI-guided protocols.",
    "### Prevention\\nPredictive models identify at-risk patients 6 months earlier than traditional methods. Cleveland Clinic prevented 1,200 emergency admissions through proactive intervention programs."
  ],
  "supporting_text": null,
  "word_count": 95
}
```"""

    # Create the text specialist agent
    # Uses Gemini Pro for high-quality content generation
    text_agent = Agent(
        create_model_with_fallback("gemini-2.5-pro"),
        result_type=TextContentOutput,
        system_prompt="You are an expert content writer who creates structured, impactful content."
    )
    
    try:
        result = await text_agent.run(prompt)
        output = result.data.model_dump()
        
        # Add metadata about what we generated
        output["result_type"] = "text_content"
        output["structure_used"] = structure_pref
        
        return output
        
    except Exception as e:
        logger.error(f"Text specialist failed: {e}")
        # Fallback content
        return {
            "result_type": "text_content",
            "title": slide.title or "Content Generation Failed",
            "main_points": ["Content generation encountered an error"],
            "supporting_text": None,
            "word_count": 5
        }


# -----------------------------------------------------------------------------
# IMAGE SPECIALIST - Creates Detailed Image Generation Prompts
# -----------------------------------------------------------------------------
async def run_image_specialist(
    instruction: str,
    theme: ThemeDefinition
) -> VisualSpec:
    """
    Generate detailed image specifications and prompts.
    
    This specialist creates prompts for image generation systems like
    DALL-E or Midjourney, incorporating theme visual guidelines.
    
    Args:
        instruction: Task from planner  
        theme: Theme for visual style guidelines
        
    Returns:
        VisualSpec with detailed image prompt
    """
    logger.info(f"Image specialist working on: {instruction}")
    
    prompt = f"""You are an art director specializing in business presentations. Your task is to create a detailed image specification.

**Your Task:**
{instruction}

**Theme Visual Guidelines:**
- Photography Style: {theme.visual_guidelines.get('photography_style', 'professional')}
- Visual Metaphors: {', '.join(theme.visual_guidelines.get('visual_metaphors', ['growth', 'innovation']))}
- Color Palette: Use {theme.design_tokens.colors.get('primary', {}).value if hasattr(theme.design_tokens.colors.get('primary', {}), 'value') else '#0066cc'} as primary
- Mood: {', '.join(theme.mood_keywords[:3])}

**Requirements:**
1. Write a detailed 150-200 word prompt for a diffusion model (like DALL-E or Midjourney)
2. Describe the composition, lighting, mood, and specific visual elements
3. Include style keywords that align with the theme
4. Specify what should NOT be in the image (negative prompt)

**Output Format:**
Return a JSON object with:
- "visual_type": "image"
- "description": Brief description of the image's purpose
- "image_prompt": The full detailed prompt
- "style_keywords": List of 5-7 style descriptors
- "composition": Description of the layout/composition
- "theme_colors_used": List of hex colors from the theme"""

    # Use Gemini Flash for creating image prompts
    # Flash is sufficient for prompt generation tasks
    model = create_model_with_fallback("gemini-2.5-flash")
    
    try:
        # Direct API call for more flexibility
        response = await model.ainvoke(prompt)
        
        # Parse the JSON response
        if isinstance(response, str):
            import json
            result = json.loads(response)
        else:
            result = response
            
        # Create VisualSpec from the result
        return VisualSpec(
            visual_type="image",
            description=result.get("description", "Image specification"),
            image_prompt=result.get("image_prompt", ""),
            style_keywords=result.get("style_keywords", []),
            composition=result.get("composition", ""),
            theme_colors_used=result.get("theme_colors_used", []),
            priority="P2"
        )
        
    except Exception as e:
        logger.error(f"Image specialist failed: {e}")
        # Fallback
        return VisualSpec(
            visual_type="image",
            description="Fallback image specification",
            image_prompt="Professional business presentation image",
            priority="P3"
        )


# -----------------------------------------------------------------------------
# ANALYTICS SPECIALIST - Generates Data Visualizations with Synthetic Data
# -----------------------------------------------------------------------------
async def run_analytics_specialist(
    instruction: str,
    theme: ThemeDefinition
) -> VisualSpec:
    """
    Generate data visualization specifications with synthetic data.
    
    This specialist:
    1. Determines the best chart type
    2. Generates realistic synthetic data
    3. Creates styling specifications
    4. Writes data insights
    
    Args:
        instruction: Task from planner
        theme: Theme for color and style guidelines
        
    Returns:
        VisualSpec with complete chart specification
    """
    logger.info(f"Analytics specialist working on: {instruction}")
    
    # Extract theme colors safely
    # This ensures charts use the brand colors
    primary_color = "#0066cc"  # Default
    if hasattr(theme.design_tokens, 'colors') and 'primary' in theme.design_tokens.colors:
        color_obj = theme.design_tokens.colors['primary']
        if hasattr(color_obj, 'value'):
            primary_color = color_obj.value
    
    prompt = f"""You are a data analyst and visualization expert. Your task is to create a complete chart specification with synthetic data.

**Your Task:**
{instruction}

**Theme Guidelines:**
- Primary Color: {primary_color}
- Data Viz Style: {theme.visual_guidelines.get('data_viz_style', 'minimalist')}
- Mood: {theme.mood_keywords[0] if theme.mood_keywords else 'professional'}

**Requirements:**
1. Determine the best chart type (bar, line, pie, scatter, etc.)
2. Generate realistic synthetic data that illustrates the point
3. Create clear axis labels and units
4. Write a one-sentence key insight from the data
5. All data should be marked as (illustrative)

**Output Format:**
Return a JSON object with:
- "visual_type": "chart"
- "description": What the chart shows
- "chart_type": The type of chart
- "data_points": Array of data objects
- "axes": Object with "x" and "y" labels
- "data_insights": Key takeaway from the data
- "theme_colors_used": ["{primary_color}"]

**Example Output:**
```json
{{
  "visual_type": "chart",
  "description": "AI diagnostic accuracy improvement over time",
  "chart_type": "line",
  "data_points": [
    {{"year": "2021", "accuracy": 76, "label": "Baseline"}},
    {{"year": "2022", "accuracy": 84, "label": "v2.0"}},
    {{"year": "2023", "accuracy": 91, "label": "v3.0"}},
    {{"year": "2024", "accuracy": 94, "label": "Current"}}
  ],
  "axes": {{"x": "Year", "y": "Accuracy (%)"}},
  "data_insights": "AI diagnostic accuracy improved by 24% over 3 years (illustrative)",
  "theme_colors_used": ["{primary_color}"]
}}
```"""

    model = create_model_with_fallback("gemini-2.5-flash")
    
    try:
        response = await model.ainvoke(prompt)
        
        # Parse response
        if isinstance(response, str):
            import json
            result = json.loads(response)
        else:
            result = response
            
        return VisualSpec(
            visual_type="chart",
            description=result.get("description", ""),
            chart_type=result.get("chart_type", "bar"),
            data_points=result.get("data_points", []),
            axes=result.get("axes", {}),
            data_insights=result.get("data_insights", ""),
            theme_colors_used=result.get("theme_colors_used", [primary_color]),
            priority="P1"
        )
        
    except Exception as e:
        logger.error(f"Analytics specialist failed: {e}")
        # Fallback
        return VisualSpec(
            visual_type="chart",
            description="Data visualization",
            chart_type="bar",
            priority="P3"
        )


# -----------------------------------------------------------------------------
# DIAGRAM SPECIALIST - Creates Process Flows and Conceptual Diagrams
# -----------------------------------------------------------------------------
async def run_diagram_specialist(
    instruction: str,
    theme: ThemeDefinition
) -> VisualSpec:
    """
    Generate diagram specifications (flowcharts, process diagrams, etc).
    
    This specialist handles two types:
    1. Schematic diagrams (flowcharts, org charts) - generates nodes/connections
    2. Artistic diagrams (pyramids, cycles) - generates image prompts
    
    Args:
        instruction: Task from planner
        theme: Theme for style guidelines
        
    Returns:
        VisualSpec with diagram specification
    """
    logger.info(f"Diagram specialist working on: {instruction}")
    
    prompt = f"""You are a systems architect and information designer. Your task is to create a diagram specification.

**Your Task:**
{instruction}

**Theme Guidelines:**
- Iconography Style: {theme.visual_guidelines.get('iconography_style', 'line-art')}
- Illustration Approach: {theme.visual_guidelines.get('illustration_approach', 'geometric')}
- Formality: {theme.formality_level}

**Requirements:**
First, analyze the instruction to determine if this requires:
- A "schematic" diagram (flowchart, process flow, org chart) - for logical flows
- An "artistic" diagram (pyramid, circular process, matrix) - for conceptual relationships

**For SCHEMATIC diagrams, generate:**
- Nodes: Array of objects with id, label, and type
- Connections: Array of objects with from, to, and label
- Layout direction: "TB" (top-bottom), "LR" (left-right), etc.

**For ARTISTIC diagrams, generate:**
- A detailed image prompt for the background shape
- Text overlays with positions
- Visual styling instructions

**Output Format:**
Return a JSON object with:
- "visual_type": "diagram"  
- "description": What the diagram illustrates
- "diagram_style": "schematic" or "artistic"
- For schematic: "nodes", "connections", "layout_direction"
- For artistic: "image_prompt", "text_overlays"
- "theme_colors_used": List of theme colors"""

    # Use Gemini Flash for diagram specifications
    model = create_model_with_fallback("gemini-2.5-flash")
    
    try:
        response = await model.ainvoke(prompt)
        
        # Parse response
        if isinstance(response, str):
            import json
            result = json.loads(response)
        else:
            result = response
            
        return VisualSpec(
            visual_type="diagram",
            description=result.get("description", ""),
            diagram_style=result.get("diagram_style", "schematic"),
            nodes=result.get("nodes", []),
            connections=result.get("connections", []),
            image_prompt=result.get("image_prompt", None),
            theme_colors_used=result.get("theme_colors_used", []),
            priority="P2"
        )
        
    except Exception as e:
        logger.error(f"Diagram specialist failed: {e}")
        # Fallback
        return VisualSpec(
            visual_type="diagram",
            description="Process diagram",
            diagram_style="schematic",
            priority="P3"
        )


# ============================================================================
# STAGE 3: DETERMINISTIC ASSEMBLER
# ============================================================================

def assemble_slide_manifest(
    slide: Slide,
    specialist_outputs: List[Dict[str, Any]]
) -> ContentManifest:
    """
    Deterministically assemble specialist outputs into final ContentManifest.
    
    This is a pure Python function with NO AI involvement. It simply:
    1. Takes the outputs from various specialists
    2. Maps them to the appropriate fields in ContentManifest
    3. Calculates metadata like word counts
    4. Returns the complete manifest
    
    Args:
        slide: Original slide object
        specialist_outputs: List of outputs from specialists
        
    Returns:
        Complete ContentManifest ready for use
    """
    logger.info(f"Assembling manifest for slide {slide.slide_id}")
    
    # Initialize with defaults
    manifest = ContentManifest(
        slide_id=slide.slide_id,
        slide_type=slide.slide_type,
        structure_preference=slide.structure_preference,
        title="",
        main_points=[],
        total_word_count=0,
        visual_count=0,
        content_density="medium"
    )
    
    # Process each specialist output
    visuals = []
    
    for output in specialist_outputs:
        # Check if output is a VisualSpec object (from visual specialists)
        if isinstance(output, VisualSpec):
            # Add visual specification directly
            visuals.append(output)
        elif isinstance(output, dict):
            # Process dictionary outputs (from text specialist)
            result_type = output.get("result_type", "")
            
            if result_type == "text_content":
                # Map text content
                manifest.title = output.get("title", "")
                manifest.main_points = output.get("main_points", [])
                manifest.supporting_text = output.get("supporting_text", None)
                manifest.total_word_count = output.get("word_count", 0)
                
                # Track that we used the structure preference
                structure_used = output.get("structure_used", "")
                if structure_used:
                    manifest.theme_elements_applied.append(f"structure_{structure_used}")
            
    # Assign visuals
    if visuals:
        # First visual is primary, rest are supporting
        manifest.primary_visual = visuals[0]
        if len(visuals) > 1:
            manifest.supporting_visuals = visuals[1:]
        manifest.visual_count = len(visuals)
    
    # Calculate content density based on word count and visuals
    if manifest.total_word_count < 50:
        manifest.content_density = "light"
    elif manifest.total_word_count > 120:
        manifest.content_density = "heavy"
    else:
        manifest.content_density = "medium"
        
    # Add theme tracking
    manifest.theme_elements_applied.append("mood_keywords")
    manifest.deck_context_used = True
    
    logger.info(
        f"Assembled manifest: {manifest.total_word_count} words, "
        f"{manifest.visual_count} visuals, {manifest.content_density} density"
    )
    
    return manifest


# ============================================================================
# ORCHESTRATION LAYER
# ============================================================================

async def process_single_slide(
    slide: Slide,
    theme: ThemeDefinition,
    deck_summary: str,
    completed_slides: Optional[List[ContentManifest]] = None
) -> ContentManifest:
    """
    Process a single slide through the three-stage pipeline.
    
    This implements the core workflow:
    1. Plan tasks with AI Planner
    2. Execute tasks in parallel with AI Specialists
    3. Assemble results with deterministic function
    
    Args:
        slide: Slide to process
        theme: Theme definition
        deck_summary: Overall presentation context
        completed_slides: For summary slides, all completed content
        
    Returns:
        Complete ContentManifest for the slide
    """
    logger.info(f"Processing slide {slide.slide_id}: {slide.title}")
    
    # Stage 1: Run the planner
    plan = await run_planner_agent(slide, theme)
    tasks = plan.get("tasks", [])
    logger.info(f"Planner created {len(tasks)} tasks")
    
    # Stage 2: Create specialist coroutines
    specialist_coroutines = []
    
    for task in tasks:
        task_type = task.get("task_type")
        instruction = task.get("instruction")
        
        if task_type == "text":
            # Text specialist needs all parameters
            coro = run_text_specialist(
                instruction, 
                slide, 
                theme, 
                deck_summary,
                completed_slides
            )
            specialist_coroutines.append(coro)
            
        elif task_type == "image":
            coro = run_image_specialist(instruction, theme)
            specialist_coroutines.append(coro)
            
        elif task_type == "analytics":
            coro = run_analytics_specialist(instruction, theme)
            specialist_coroutines.append(coro)
            
        elif task_type == "diagram":
            coro = run_diagram_specialist(instruction, theme)
            specialist_coroutines.append(coro)
            
        else:
            logger.warning(f"Unknown task type: {task_type}")
    
    # Execute all specialists in parallel
    if specialist_coroutines:
        logger.info(f"Running {len(specialist_coroutines)} specialists in parallel")
        specialist_outputs = await asyncio.gather(*specialist_coroutines)
    else:
        # Fallback: at least generate text
        logger.warning("No specialists created, using fallback")
        specialist_outputs = [await run_text_specialist(
            f"Generate content for {slide.title}",
            slide,
            theme,
            deck_summary,
            completed_slides
        )]
    
    # Stage 3: Assemble the final manifest
    manifest = assemble_slide_manifest(slide, specialist_outputs)
    
    return manifest


async def orchestrate_content_generation(
    strawman: Any,  # The strawman object with all slides
    theme: ThemeDefinition,
    deck_summary: str
) -> List[ContentManifest]:
    """
    Main orchestrator implementing deferred summary generation.
    
    This function:
    1. Separates content slides from summary slides
    2. Processes all content slides first
    3. Processes summary slides last with full context
    4. Returns ordered results
    
    Args:
        strawman: Complete strawman with all slides
        theme: Theme definition
        deck_summary: Overall presentation narrative
        
    Returns:
        Ordered list of ContentManifests for all slides
    """
    logger.info(f"Starting content generation for {len(strawman.slides)} slides")
    
    # Separate slides into content and summary categories
    content_slides = []
    summary_slides = []
    
    for slide in strawman.slides:
        # Identify summary-type slides
        # Usually slide #2 (agenda) or slides with summary/agenda type
        is_summary = (
            slide.slide_type in ['agenda_slide', 'summary_slide'] or
            slide.slide_number == 2 or
            'agenda' in slide.title.lower() or
            'summary' in slide.title.lower() or
            'overview' in slide.title.lower()
        )
        
        if is_summary:
            summary_slides.append(slide)
            logger.info(f"Deferring summary slide: {slide.slide_id} - {slide.title}")
        else:
            content_slides.append(slide)
    
    # Process all content slides first
    logger.info(f"Processing {len(content_slides)} content slides")
    content_manifests = []
    
    for slide in content_slides:
        manifest = await process_single_slide(
            slide,
            theme,
            deck_summary,
            None  # No completed slides context yet
        )
        content_manifests.append(manifest)
    
    # Now process summary slides with full context
    logger.info(f"Processing {len(summary_slides)} summary slides with context")
    summary_manifests = []
    
    for slide in summary_slides:
        manifest = await process_single_slide(
            slide,
            theme, 
            deck_summary,
            content_manifests  # Pass all completed content
        )
        summary_manifests.append(manifest)
    
    # Combine and sort by slide number to maintain order
    all_manifests = content_manifests + summary_manifests
    
    # Create a mapping of slide_id to slide_number for sorting
    slide_number_map = {
        slide.slide_id: slide.slide_number 
        for slide in strawman.slides
    }
    
    # Sort by original slide number
    all_manifests.sort(
        key=lambda m: slide_number_map.get(m.slide_id, 999)
    )
    
    logger.info(f"Content generation complete. Generated {len(all_manifests)} manifests")
    
    return all_manifests


# ============================================================================
# PUBLIC INTERFACE
# ============================================================================

class ContentAgentV2:
    """
    Public interface for the new Content Agent.
    
    This class provides a clean API that matches the expected interface
    while implementing the new three-stage architecture internally.
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """Initialize the Content Agent V2."""
        self.model_name = model_name
        logger.info(f"ContentAgentV2 initialized with model: {model_name}")
    
    async def prepare_content(
        self,
        slide: Slide,
        deck_summary: str,
        theme: ThemeDefinition,
        strawman_metadata: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> ContentManifest:
        """
        Prepare content for a single slide (backward compatibility).
        
        This method maintains the same interface as the original agent
        but uses the new three-stage pipeline internally.
        """
        return await process_single_slide(
            slide,
            theme,
            deck_summary,
            None  # No completed slides context for single processing
        )
    
    async def generate_all_content(
        self,
        strawman: Any,
        theme: ThemeDefinition,
        deck_summary: str
    ) -> List[ContentManifest]:
        """
        Generate content for all slides with deferred summary generation.
        
        This is the preferred method that implements the full orchestration
        with proper summary slide handling.
        """
        return await orchestrate_content_generation(
            strawman,
            theme,
            deck_summary
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # This section demonstrates how to use the new Content Agent
    
    async def example_usage():
        """Example of using the new Content Agent."""
        
        # Initialize the agent
        agent = ContentAgentV2()
        
        # Example slide
        example_slide = Slide(
            slide_id="slide_001",
            slide_number=1,
            slide_type="content",
            title="AI in Healthcare",
            narrative="Showcase AI impact",
            key_points=["Diagnosis improvements", "Cost reduction", "Patient outcomes"],
            structure_preference="Three-Column Layout"
        )
        
        # Example theme (simplified)
        from src.models.design_tokens import DesignToken, ColorToken
        
        example_theme = ThemeDefinition(
            name="Professional Healthcare",
            mood_keywords=["innovative", "trustworthy", "data-driven"],
            formality_level="high",
            design_tokens={
                "colors": {
                    "primary": ColorToken(value="#0066cc")
                }
            },
            visual_guidelines={
                "photography_style": "professional medical",
                "data_viz_style": "clean minimalist"
            }
        )
        
        # Process single slide
        manifest = await agent.prepare_content(
            slide=example_slide,
            deck_summary="This presentation explores how AI is transforming healthcare...",
            theme=example_theme,
            strawman_metadata={},
            session_id="example_001"
        )
        
        print(f"Generated content for: {manifest.title}")
        print(f"Word count: {manifest.total_word_count}")
        print(f"Structure: {manifest.structure_preference}")
        
    # Run the example
    # asyncio.run(example_usage())