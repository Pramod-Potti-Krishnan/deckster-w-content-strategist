"""
Content Assembly Utility
========================

This module provides utilities for assembling component outputs from content specialists
into the standardized ContentManifest format expected by orchestrators.

This is purely data transformation logic - no AI/LLM calls involved.
Separated from ContentAgentV7 to keep content generation and data formatting concerns separate.

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import logging
from typing import Dict, Any, List, Optional

from pydantic import BaseModel

# Import output types from content specialists
from src.agents.content_agent_v7 import (
    TextContentV4,
    AnalyticsContentV4,
    ImageContentV4,
    DiagramContentV4,
    TableContentV4,
    ContentManifest,
    VisualSpec
)
from src.models.agents import Slide
from src.utils.playbooks_v4 import PlaybookSession

# Configure logging
logger = logging.getLogger(__name__)


def assemble_content_manifest(
    slide: Slide,
    component_outputs: Dict[str, Any],
    playbook_session: Optional[PlaybookSession] = None
) -> ContentManifest:
    """
    Deterministically assemble all component outputs into final manifest.
    
    This function transforms the raw outputs from content specialists
    (TextContentV4, ImageContentV4, etc.) into the standardized
    ContentManifest format expected by orchestrators.
    
    Args:
        slide: The slide being processed
        component_outputs: Dict mapping component names to their outputs
        playbook_session: Optional playbook session (not currently used)
        
    Returns:
        ContentManifest with all content properly organized
    """
    logger.info("Assembling content manifest from component outputs")
    
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
    word_count = 0
    
    # Count words in title
    if manifest.title:
        word_count += len(manifest.title.split())
    
    # Count words in main points
    for point in manifest.main_points:
        word_count += len(point.split())
    
    # Count words in supporting text
    if manifest.supporting_text:
        word_count += len(manifest.supporting_text.split())
    
    manifest.total_word_count = word_count
    
    # Determine content density
    if word_count < 50:
        manifest.content_density = "light"
    elif word_count < 150:
        manifest.content_density = "medium"
    else:
        manifest.content_density = "heavy"
    
    # Log summary
    logger.info(f"Manifest assembled: {word_count} words, {manifest.visual_count} visuals, density: {manifest.content_density}")
    
    return manifest


# Alias for backward compatibility
assemble_content_manifest_v4 = assemble_content_manifest