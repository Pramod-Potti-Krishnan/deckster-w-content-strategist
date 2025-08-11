"""
Content Generation Playbooks V4 - Decoupled Component Strategies
==============================================================

This module contains separate, specialized playbooks for each content component type.
Each playbook provides strategic guidance, templates, and specifications that are
used during the Strategic Briefing stage (Stage 2) of the V4 pipeline.

The key innovation in V4 is the decoupling of strategies - each component type
(text, analytics, image, diagram, table) has its own dedicated playbook with
deep, specialized knowledge about that content type.

Author: AI Assistant
Date: 2024
Version: 4.0
"""

from typing import Dict, Any, List

# ============================================================================
# TEXT PLAYBOOK - Narrative Arcs and HTML Container Structures
# ============================================================================

TEXT_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "title_slide": {
        "narrative_arc": "Introduction / Context / Promise",
        "purpose": "To create a strong first impression, clearly state the topic, and introduce the speaker",
        "tone_guidance": "Professional, confident, welcoming",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Hook the audience"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Provide context"},
            {"role": "presenter_info", "tag": "p", "word_limit": 20, "purpose": "Establish credibility"}
        ],
        "layout_adaptations": {
            "standard": "Use default containers",
            "two_column": "Title spans both columns, presenter info in right column",
            "centered": "All elements center-aligned with vertical spacing"
        }
    },
    
    "case_study_slide": {
        "narrative_arc": "Problem / Solution / Benefit",
        "purpose": "To tell a compelling story of a customer's success using a clear, persuasive narrative structure",
        "tone_guidance": "Concrete, evidence-based, with specific metrics",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Hook the audience"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Customer/context identifier"},
            {"role": "problem_heading", "tag": "h3", "word_limit": 3, "purpose": "Label the challenge"},
            {"role": "problem_text", "tag": "p", "word_limit": 50, "purpose": "Describe the pain point"},
            {"role": "solution_heading", "tag": "h3", "word_limit": 3, "purpose": "Introduce the fix"},
            {"role": "solution_text", "tag": "p", "word_limit": 50, "purpose": "Explain the approach"},
            {"role": "benefit_heading", "tag": "h3", "word_limit": 3, "purpose": "Highlight results"},
            {"role": "benefit_text", "tag": "p", "word_limit": 50, "purpose": "Quantify the impact"}
        ],
        "layout_adaptations": {
            "standard": "Linear flow: Problem → Solution → Benefit",
            "three_column": "Each section (Problem/Solution/Benefit) in its own column",
            "two_column": "Problem in left column, Solution/Benefit in right column",
            "grid": "2x2 grid: Problem (top-left), Solution (top-right), Benefit (bottom-spanning)"
        }
    },
    
    "agenda_slide": {
        "narrative_arc": "Preview / Structure / Journey",
        "purpose": "To provide a clear, concise overview of the presentation's structure and set expectations",
        "tone_guidance": "Clear, organized, action-oriented",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 5, "purpose": "Clear heading"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Optional context or timing"},
            {"role": "agenda_items", "tag": "ul", "items": "3-5", "word_limit_per_item": 8, "purpose": "Guide the journey"}
        ],
        "special_handling": "This is a SUMMARY slide - process AFTER all content slides are complete",
        "layout_adaptations": {
            "standard": "Vertical list of agenda items",
            "two_column": "Split agenda items between columns",
            "three_column": "Distribute items across three columns",
            "grid": "2x2 or 2x3 grid for agenda items"
        }
    },
    
    "content_heavy": {
        "narrative_arc": "Topic Introduction / Deep Dive / Synthesis",
        "purpose": "To provide detailed information with comprehensive coverage of a topic",
        "tone_guidance": "Thorough, informative, educational",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Frame the topic"},
            {"role": "subtitle", "tag": "h2", "word_limit": 20, "purpose": "Context or key theme"},
            {"role": "section_1_heading", "tag": "h3", "word_limit": 5, "purpose": "First aspect"},
            {"role": "section_1_text", "tag": "p", "word_limit": 100, "purpose": "Detailed explanation"},
            {"role": "section_2_heading", "tag": "h3", "word_limit": 5, "purpose": "Second aspect"},
            {"role": "section_2_text", "tag": "p", "word_limit": 100, "purpose": "Detailed explanation"},
            {"role": "section_3_heading", "tag": "h3", "word_limit": 5, "purpose": "Third aspect"},
            {"role": "section_3_text", "tag": "p", "word_limit": 100, "purpose": "Detailed explanation"}
        ],
        "layout_adaptations": {
            "standard": "Linear sections with clear hierarchy",
            "two_column": "Alternate sections between columns for visual balance",
            "three_column": "One section per column with equal weight",
            "grid": "2x2 grid: Title spanning top, three sections in remaining cells"
        }
    },
    
    "data_driven": {
        "narrative_arc": "Key Metric / What It Means / Why It Matters",
        "purpose": "To present data insights clearly and compellingly, letting visualizations tell the story",
        "tone_guidance": "Analytical yet accessible, focused on insights",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Frame the data story"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Time period or context"},
            {"role": "key_insight_1", "tag": "p", "word_limit": 20, "purpose": "Primary insight"},
            {"role": "key_insight_2", "tag": "p", "word_limit": 20, "purpose": "Supporting insight"},
            {"role": "key_insight_3", "tag": "p", "word_limit": 20, "purpose": "Implication"}
        ],
        "layout_adaptations": {
            "standard": "Insights below or beside visualization",
            "two_column": "Visualization left, insights right",
            "grid": "Visualization prominent, insights in smaller cells"
        }
    },
    
    "visual_heavy": {
        "narrative_arc": "Impact Statement",
        "purpose": "To use imagery to convey emotion, concept, or impact with minimal text",
        "tone_guidance": "Bold, evocative, memorable",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 12, "purpose": "Powerful statement"},
            {"role": "subtitle", "tag": "h2", "word_limit": 20, "purpose": "Supporting context"},
            {"role": "supporting_statement", "tag": "p", "word_limit": 25, "purpose": "Additional detail or CTA"}
        ],
        "layout_adaptations": {
            "standard": "Text overlay on image",
            "full_bleed": "Minimal text in safe zones",
            "hero": "Text in lower third or side panel"
        }
    },
    
    "mixed_content": {
        "narrative_arc": "Main Point / Supporting Details / Integration",
        "purpose": "To balance text and visuals equally, creating a harmonious information flow",
        "tone_guidance": "Balanced, informative, engaging",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Set the topic"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Frame the discussion"},
            {"role": "main_point_1", "tag": "h3", "word_limit": 8, "purpose": "First key point"},
            {"role": "detail_1", "tag": "p", "word_limit": 30, "purpose": "Supporting detail"},
            {"role": "main_point_2", "tag": "h3", "word_limit": 8, "purpose": "Second key point"},
            {"role": "detail_2", "tag": "p", "word_limit": 30, "purpose": "Supporting detail"},
            {"role": "main_point_3", "tag": "h3", "word_limit": 8, "purpose": "Third key point"},
            {"role": "detail_3", "tag": "p", "word_limit": 30, "purpose": "Supporting detail"}
        ],
        "layout_adaptations": {
            "standard": "Alternating text and visual elements",
            "two_column": "Text left, supporting visuals right",
            "three_column": "One point per column with associated visual",
            "grid": "2x3 grid: alternating text and visual cells"
        }
    },
    
    "diagram_focused": {
        "narrative_arc": "Concept Introduction / Component Explanation",
        "purpose": "To explain a process, system, or relationship through visual representation",
        "tone_guidance": "Clear, explanatory, technical yet accessible",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Name the system/process"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Type or category"},
            {"role": "introduction", "tag": "p", "word_limit": 30, "purpose": "Set context"},
            {"role": "diagram_labels", "tag": "ul", "items": "4-6", "word_limit_per_item": 5, "purpose": "Label components"}
        ],
        "layout_adaptations": {
            "standard": "Diagram center with labels around",
            "two_column": "Diagram left, explanation right",
            "annotated": "Diagram with callout boxes"
        }
    },
    
    "conclusion_slide": {
        "narrative_arc": "Recap / Reinforcement / Call to Action",
        "purpose": "To summarize key points, reinforce the main message, and provide a clear call-to-action",
        "tone_guidance": "Confident, inspiring, action-oriented",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 15, "purpose": "Strong closing statement"},
            {"role": "subtitle", "tag": "h2", "word_limit": 20, "purpose": "Reinforce main theme"},
            {"role": "key_takeaway_1", "tag": "li", "word_limit": 20, "purpose": "Core message 1"},
            {"role": "key_takeaway_2", "tag": "li", "word_limit": 20, "purpose": "Core message 2"},
            {"role": "key_takeaway_3", "tag": "li", "word_limit": 20, "purpose": "Core message 3"},
            {"role": "call_to_action", "tag": "p", "word_limit": 25, "purpose": "Drive next steps"}
        ],
        "layout_adaptations": {
            "standard": "Centered with emphasis on CTA",
            "two_column": "Takeaways left, CTA right",
            "three_column": "One takeaway per column, CTA below",
            "grid": "2x2: Title spanning top, takeaways and CTA in cells"
        }
    },
    
    "summary_slide": {
        "narrative_arc": "Synthesis / Connections / Big Picture",
        "purpose": "To provide a comprehensive overview of all content presented, highlighting connections and key insights",
        "tone_guidance": "Comprehensive, synthesizing, strategic",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Frame the summary"},
            {"role": "subtitle", "tag": "h2", "word_limit": 20, "purpose": "Overarching insight"},
            {"role": "theme_1", "tag": "h3", "word_limit": 8, "purpose": "First major theme"},
            {"role": "theme_1_summary", "tag": "p", "word_limit": 40, "purpose": "Theme details"},
            {"role": "theme_2", "tag": "h3", "word_limit": 8, "purpose": "Second major theme"},
            {"role": "theme_2_summary", "tag": "p", "word_limit": 40, "purpose": "Theme details"},
            {"role": "theme_3", "tag": "h3", "word_limit": 8, "purpose": "Third major theme"},
            {"role": "theme_3_summary", "tag": "p", "word_limit": 40, "purpose": "Theme details"}
        ],
        "special_handling": "This is a SUMMARY slide - process AFTER all content slides are complete",
        "layout_adaptations": {
            "standard": "Linear theme progression",
            "three_column": "One theme per column for parallel viewing",
            "grid": "2x2 or 3x2 grid for theme organization",
            "hierarchical": "Central concept with themes radiating out"
        }
    },
    
    "section_divider": {
        "narrative_arc": "Transition / Preview",
        "purpose": "To clearly signal a transition to a new section or topic within the presentation",
        "tone_guidance": "Clear, transitional, anticipatory",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 8, "purpose": "New section name"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Section number or theme"},
            {"role": "section_preview", "tag": "p", "word_limit": 20, "purpose": "What's coming"}
        ],
        "layout_adaptations": {
            "standard": "Centered with visual emphasis",
            "full_width": "Bold typography across full width",
            "minimal": "Clean with lots of white space"
        }
    },
    
    "executive_summary": {
        "narrative_arc": "Context / Key Findings / Recommendations / Next Steps",
        "purpose": "To provide decision-makers with actionable insights quickly",
        "tone_guidance": "Authoritative, concise, action-oriented",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 8, "purpose": "Clear positioning"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Time frame or scope"},
            {"role": "context", "tag": "p", "word_limit": 40, "purpose": "Set the stage"},
            {"role": "findings_heading", "tag": "h3", "word_limit": 3, "purpose": "Signal insights"},
            {"role": "findings_list", "tag": "ul", "items": 3, "word_limit_per_item": 20, "purpose": "Key takeaways"},
            {"role": "recommendations_heading", "tag": "h3", "word_limit": 2, "purpose": "Action label"},
            {"role": "recommendations_list", "tag": "ul", "items": 3, "word_limit_per_item": 25, "purpose": "What to do"},
            {"role": "cta", "tag": "p", "word_limit": 20, "purpose": "Drive action"}
        ],
        "layout_adaptations": {
            "standard": "Linear flow from findings to recommendations",
            "two_column": "Findings left, recommendations right",
            "dashboard": "Key metrics at top, details below"
        }
    },
    
    "comparison": {
        "narrative_arc": "Option A / Option B / Winner & Why",
        "purpose": "To help audience make informed decisions between alternatives",
        "tone_guidance": "Balanced initially, then decisive in recommendation",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Frame the choice"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Decision context"},
            {"role": "option_a_heading", "tag": "h3", "word_limit": 5, "purpose": "First option"},
            {"role": "option_a_pros", "tag": "ul", "items": 3, "word_limit_per_item": 15, "purpose": "Benefits"},
            {"role": "option_a_cons", "tag": "ul", "items": 2, "word_limit_per_item": 15, "purpose": "Drawbacks"},
            {"role": "option_b_heading", "tag": "h3", "word_limit": 5, "purpose": "Second option"},
            {"role": "option_b_pros", "tag": "ul", "items": 3, "word_limit_per_item": 15, "purpose": "Benefits"},
            {"role": "option_b_cons", "tag": "ul", "items": 2, "word_limit_per_item": 15, "purpose": "Drawbacks"},
            {"role": "recommendation", "tag": "p", "word_limit": 40, "purpose": "Clear decision"}
        ],
        "layout_adaptations": {
            "standard": "Sequential comparison then recommendation",
            "two_column": "Option A left, Option B right, recommendation below",
            "three_column": "Option A | VS | Option B layout",
            "grid": "2x2: Options in top cells, recommendation spanning bottom"
        }
    },
    
    "process_explanation": {
        "narrative_arc": "Overview / Step 1 / Step 2 / Step 3 / Outcome",
        "purpose": "To explain how something works in clear, sequential steps",
        "tone_guidance": "Clear, instructional, logical flow",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 8, "purpose": "Name the process"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Process category or duration"},
            {"role": "overview", "tag": "p", "word_limit": 35, "purpose": "Big picture view"},
            {"role": "step_1_heading", "tag": "h3", "word_limit": 5, "purpose": "First step label"},
            {"role": "step_1_text", "tag": "p", "word_limit": 30, "purpose": "Explain step 1"},
            {"role": "step_2_heading", "tag": "h3", "word_limit": 5, "purpose": "Second step label"},
            {"role": "step_2_text", "tag": "p", "word_limit": 30, "purpose": "Explain step 2"},
            {"role": "step_3_heading", "tag": "h3", "word_limit": 5, "purpose": "Third step label"},
            {"role": "step_3_text", "tag": "p", "word_limit": 30, "purpose": "Explain step 3"},
            {"role": "outcome", "tag": "p", "word_limit": 25, "purpose": "End result"}
        ],
        "layout_adaptations": {
            "standard": "Linear vertical flow",
            "horizontal": "Steps flow left to right",
            "three_column": "One step per column",
            "circular": "Steps arranged in cycle if process repeats"
        }
    },
    
    # Fallback for any unrecognized slide types
    "default": {
        "narrative_arc": "Introduction / Main Points / Conclusion",
        "purpose": "To communicate information clearly and effectively",
        "tone_guidance": "Clear, professional, adaptable to content",
        "html_containers": [
            {"role": "title", "tag": "h1", "word_limit": 10, "purpose": "Set the topic"},
            {"role": "subtitle", "tag": "h2", "word_limit": 15, "purpose": "Additional context"},
            {"role": "main_content", "tag": "div", "word_limit": 150, "purpose": "Flexible content"}
        ],
        "layout_adaptations": {
            "standard": "Adapt to content needs",
            "two_column": "Split content logically",
            "grid": "Organize content in cells",
            "flexible": "Adjust based on content type"
        }
    }
}

# ============================================================================
# ANALYTICS PLAYBOOK - Data Stories and Visualization Strategies
# ============================================================================

ANALYTICS_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "comparison": {
        "purpose": "To compare metrics between two or more items",
        "story_type": "side_by_side_comparison",
        "recommended_charts": ["grouped_bar_chart", "radar_chart", "parallel_coordinates"],
        "required_data_spec": {
            "structure": "comparative",
            "min_items": 2,
            "max_items": 5,
            "fields": ["item_name", "metric_1_value", "metric_2_value", "optional_metric_3"]
        },
        "visual_guidelines": {
            "color_strategy": "categorical_distinct",
            "labeling": "direct_labels_preferred",
            "gridlines": "subtle",
            "aspect_ratio": "16:10"
        },
        "annotation_opportunities": ["winner", "biggest_gap", "surprising_finding"]
    },
    
    "trend_analysis": {
        "purpose": "To show change over time and project future state",
        "story_type": "temporal_progression",
        "recommended_charts": ["line_chart", "area_chart", "connected_scatterplot"],
        "required_data_spec": {
            "structure": "time_series",
            "min_periods": 5,
            "max_periods": 24,
            "fields": ["time_period", "primary_value", "optional_forecast", "optional_benchmark"]
        },
        "visual_guidelines": {
            "color_strategy": "sequential_single_hue",
            "labeling": "start_end_points",
            "gridlines": "vertical_only",
            "aspect_ratio": "16:9",
            "annotations": ["trend_line", "inflection_points", "forecast_boundary"]
        },
        "annotation_opportunities": ["turning_point", "milestone", "projection"]
    },
    
    "distribution": {
        "purpose": "To show how values are spread across a range",
        "story_type": "statistical_insight",
        "recommended_charts": ["histogram", "box_plot", "violin_plot", "density_plot"],
        "required_data_spec": {
            "structure": "statistical",
            "min_samples": 30,
            "fields": ["value", "optional_category", "optional_time_period"]
        },
        "visual_guidelines": {
            "color_strategy": "monochromatic_gradient",
            "labeling": "statistical_markers",
            "gridlines": "horizontal_only",
            "aspect_ratio": "4:3",
            "annotations": ["mean", "median", "outliers", "standard_deviation"]
        },
        "annotation_opportunities": ["outlier", "cluster", "norm"]
    },
    
    "composition": {
        "purpose": "To show parts of a whole and their relative importance",
        "story_type": "proportional_breakdown",
        "recommended_charts": ["pie_chart", "donut_chart", "treemap", "stacked_bar"],
        "required_data_spec": {
            "structure": "hierarchical",
            "min_categories": 3,
            "max_categories": 8,
            "fields": ["category_name", "value", "optional_parent_category"]
        },
        "visual_guidelines": {
            "color_strategy": "categorical_harmonious",
            "labeling": "percentage_labels",
            "gridlines": "none",
            "aspect_ratio": "1:1",
            "annotations": ["largest_segment", "combined_small_segments"]
        },
        "annotation_opportunities": ["dominant", "minority", "equal_split"]
    },
    
    "correlation": {
        "purpose": "To show relationships between variables",
        "story_type": "relationship_discovery",
        "recommended_charts": ["scatter_plot", "bubble_chart", "heatmap", "pair_plot"],
        "required_data_spec": {
            "structure": "multivariate",
            "min_variables": 2,
            "max_variables": 5,
            "fields": ["x_value", "y_value", "optional_size", "optional_color_category"]
        },
        "visual_guidelines": {
            "color_strategy": "diverging_centered",
            "labeling": "axis_titles_crucial",
            "gridlines": "both_axes",
            "aspect_ratio": "1:1",
            "annotations": ["correlation_coefficient", "outliers", "clusters"]
        },
        "annotation_opportunities": ["strong_correlation", "outlier", "cluster"]
    }
}

# ============================================================================
# IMAGE PLAYBOOK - Visual Archetypes and Composition Strategies
# ============================================================================

IMAGE_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "hero_image": {
        "purpose": "To create a strong emotional impact and set the tone",
        "archetype": "aspirational_photograph",
        "composition": {
            "rule": "rule_of_thirds",
            "focus": "deep_focus_background_blur",
            "perspective": "slightly_low_angle_for_power"
        },
        "mood": ["optimistic", "professional", "forward-looking"],
        "color_guidance": {
            "palette": "brand_colors_prominent",
            "lighting": "golden_hour_or_bright_daylight",
            "contrast": "medium_high"
        },
        "size_guidance": {
            "aspect_ratio": "16:9",
            "placement": "full_bleed",
            "text_safe_area": "lower_third"
        },
        "avoid": ["stock_photo_cliches", "dated_technology", "overly_staged_scenes"]
    },
    
    "spot_illustration": {
        "purpose": "To add visual interest without overwhelming the content",
        "archetype": "minimalist_vector_art",
        "composition": {
            "rule": "centered_simple",
            "focus": "single_concept",
            "perspective": "flat_or_isometric"
        },
        "mood": ["friendly", "approachable", "clear"],
        "color_guidance": {
            "palette": "limited_2_3_colors",
            "lighting": "flat_even",
            "contrast": "low_medium"
        },
        "size_guidance": {
            "aspect_ratio": "1:1",
            "placement": "inline_with_text",
            "text_safe_area": "none_needed"
        },
        "style_options": ["line_art", "flat_color", "gradient_accents"]
    },
    
    "conceptual_metaphor": {
        "purpose": "To visualize abstract concepts through concrete imagery",
        "archetype": "symbolic_representation",
        "composition": {
            "rule": "central_focus_radial_balance",
            "focus": "sharp_throughout",
            "perspective": "straight_on_or_slight_angle"
        },
        "mood": ["thoughtful", "innovative", "memorable"],
        "color_guidance": {
            "palette": "analogous_harmony",
            "lighting": "dramatic_directional",
            "contrast": "high"
        },
        "size_guidance": {
            "aspect_ratio": "4:3",
            "placement": "centered_with_padding",
            "text_safe_area": "avoid_center"
        },
        "metaphor_types": ["growth", "connection", "transformation", "journey"]
    },
    
    "data_humanization": {
        "purpose": "To make data relatable through human context",
        "archetype": "people_in_context",
        "composition": {
            "rule": "environmental_portrait",
            "focus": "subject_sharp_context_soft",
            "perspective": "eye_level_relatable"
        },
        "mood": ["authentic", "diverse", "engaged"],
        "color_guidance": {
            "palette": "natural_with_brand_accent",
            "lighting": "soft_natural",
            "contrast": "medium"
        },
        "size_guidance": {
            "aspect_ratio": "3:2",
            "placement": "alongside_data",
            "text_safe_area": "bottom_or_top_third"
        },
        "subject_guidance": ["real_situations", "diverse_representation", "active_not_posed"]
    }
}

# ============================================================================
# DIAGRAM PLAYBOOK - Information Architecture Patterns
# ============================================================================

DIAGRAM_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "process_flow": {
        "purpose": "To show sequential steps in a process",
        "structure_type": "linear_sequential",
        "layout_options": ["horizontal_flow", "vertical_flow", "circular_cycle"],
        "node_specification": {
            "shape": "rounded_rectangle",
            "min_nodes": 3,
            "max_nodes": 7,
            "content": ["step_number", "action_verb", "outcome"]
        },
        "connection_specification": {
            "type": "directional_arrows",
            "style": "solid_with_direction",
            "labeling": "optional_conditions"
        },
        "visual_hierarchy": {
            "start_node": "emphasized_color",
            "end_node": "emphasized_result",
            "decision_points": "diamond_shape"
        },
        "annotation_opportunities": ["bottleneck", "automation_point", "decision"]
    },
    
    "organizational_hierarchy": {
        "purpose": "To show reporting structures and relationships",
        "structure_type": "tree_hierarchical",
        "layout_options": ["top_down_tree", "radial_tree", "horizontal_levels"],
        "node_specification": {
            "shape": "rectangle_with_role",
            "content": ["name_or_title", "key_responsibility", "optional_metric"]
        },
        "connection_specification": {
            "type": "straight_lines",
            "style": "solid_hierarchical",
            "labeling": "none"
        },
        "visual_hierarchy": {
            "levels": "size_decreases_down",
            "departments": "color_coding",
            "dotted_lines": "matrix_relationships"
        }
    },
    
    "system_architecture": {
        "purpose": "To show technical components and data flow",
        "structure_type": "network_interconnected",
        "layout_options": ["layered_architecture", "hub_spoke", "mesh_network"],
        "node_specification": {
            "shape": "component_specific_icons",
            "content": ["component_name", "key_function", "optional_technology"]
        },
        "connection_specification": {
            "type": "data_flow_arrows",
            "style": "varied_by_connection_type",
            "labeling": "data_type_or_protocol"
        },
        "visual_hierarchy": {
            "core_systems": "larger_central",
            "external_systems": "boundary_placement",
            "data_flow": "arrow_thickness"
        }
    },
    
    "concept_map": {
        "purpose": "To show relationships between ideas",
        "structure_type": "web_associative",
        "layout_options": ["force_directed", "radial_categories", "mind_map"],
        "node_specification": {
            "shape": "varied_by_importance",
            "content": ["concept_name", "brief_description"]
        },
        "connection_specification": {
            "type": "curved_lines",
            "style": "varied_by_relationship",
            "labeling": "relationship_type"
        },
        "visual_hierarchy": {
            "central_concept": "largest_prominent",
            "categories": "color_grouping",
            "connections": "line_weight_by_strength"
        }
    }
}

# ============================================================================
# TABLE PLAYBOOK - Data Organization Patterns
# ============================================================================

TABLE_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "comparison_matrix": {
        "purpose": "To compare multiple items across multiple criteria",
        "structure": {
            "orientation": "criteria_as_rows",
            "headers": ["criteria", "option_1", "option_2", "option_3"],
            "row_grouping": "category_sections"
        },
        "content_guidance": {
            "cell_content": "concise_values_or_symbols",
            "empty_cells": "dash_or_na",
            "units": "in_header_or_first_occurrence"
        },
        "visual_enhancement": {
            "highlighting": "best_in_row",
            "icons": "checkmarks_x_marks",
            "color_coding": "good_neutral_bad",
            "borders": "section_dividers"
        },
        "responsive_behavior": {
            "mobile": "transpose_to_vertical",
            "overflow": "horizontal_scroll"
        }
    },
    
    "data_summary": {
        "purpose": "To present key metrics in organized format",
        "structure": {
            "orientation": "metrics_as_rows",
            "headers": ["metric", "current_value", "previous_value", "change", "target"],
            "row_grouping": "performance_categories"
        },
        "content_guidance": {
            "cell_content": "numbers_with_context",
            "formatting": "appropriate_decimals",
            "units": "consistent_per_column"
        },
        "visual_enhancement": {
            "highlighting": "variance_from_target",
            "sparklines": "trend_column",
            "color_coding": "performance_based",
            "indicators": "arrows_for_change"
        }
    },
    
    "feature_list": {
        "purpose": "To detail features or specifications",
        "structure": {
            "orientation": "features_as_rows",
            "headers": ["feature", "description", "availability", "notes"],
            "row_grouping": "feature_categories"
        },
        "content_guidance": {
            "cell_content": "brief_descriptive",
            "consistency": "parallel_structure",
            "details": "expandable_if_needed"
        },
        "visual_enhancement": {
            "icons": "feature_type_icons",
            "badges": "new_popular_premium",
            "color_coding": "availability_based",
            "borders": "clean_minimal"
        }
    }
}

# ============================================================================
# ICON PLAYBOOK - Iconography System and Visual Vocabulary
# ============================================================================

ICON_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "style_system": {
        "design_principles": ["minimal", "geometric", "consistent_stroke_width"],
        "technical_specs": {
            "grid_size": "24x24",
            "stroke_width": "2px",
            "corner_radius": "2px",
            "padding": "2px"
        },
        "color_application": {
            "primary": "stroke_only",
            "fill": "none_or_subtle",
            "gradient": "avoid"
        }
    },
    
    "concept_mapping": {
        # Business concepts
        "growth": ["arrow_trending_up", "plant_sprout", "rocket_launch"],
        "challenge": ["mountain_peak", "puzzle_piece", "warning_triangle"],
        "solution": ["lightbulb", "key", "check_circle"],
        "collaboration": ["people_group", "handshake", "network_nodes"],
        "innovation": ["sparkles", "atom", "brain_circuit"],
        "efficiency": ["gauge_speedometer", "lightning_bolt", "gear_streamlined"],
        
        # Actions
        "analyze": ["magnifying_glass", "chart_analysis", "microscope"],
        "implement": ["wrench", "play_circle", "upload_cloud"],
        "monitor": ["eye", "dashboard", "pulse_line"],
        "optimize": ["sliders", "target", "filter_funnel"],
        
        # Results
        "success": ["trophy", "star", "thumbs_up"],
        "improvement": ["arrow_up_right", "chart_growth", "plus_circle"],
        "savings": ["piggy_bank", "dollar_decrease", "efficiency_badge"],
        
        # Objects
        "document": ["file_text", "clipboard", "folder"],
        "technology": ["chip", "server", "cloud"],
        "communication": ["message", "broadcast", "satellite"],
        
        # Abstract
        "insight": ["eye_sparkle", "brain_lightbulb", "crystal_ball"],
        "strategy": ["chess_piece", "map", "compass"],
        "transformation": ["butterfly", "refresh_cycle", "magic_wand"]
    },
    
    "usage_guidelines": {
        "placement": {
            "with_heading": "left_aligned_before_text",
            "in_list": "bullet_replacement",
            "standalone": "centered_with_label"
        },
        "sizing": {
            "with_h1": "32px",
            "with_h2": "24px",
            "with_h3": "20px",
            "inline_text": "16px",
            "decorative": "48px+"
        },
        "interaction": {
            "static": "default",
            "hover": "subtle_color_shift",
            "active": "scale_down_slightly"
        }
    },
    
    "consistency_rules": {
        "within_slide": "max_3_different_icons",
        "within_section": "consistent_style_weight",
        "within_deck": "unified_icon_family",
        "avoid_mixing": ["outlined_and_filled", "different_stroke_weights", "realistic_and_abstract"]
    }
}

# ============================================================================
# PLAYBOOK UTILITIES
# ============================================================================

def get_text_strategy(slide_type: str, narrative: str) -> Dict[str, Any]:
    """
    Select the best text strategy based on slide type and narrative.
    
    Args:
        slide_type: The type of slide
        narrative: The slide's narrative description
        
    Returns:
        The most appropriate text strategy from TEXT_PLAYBOOK
    """
    # First, check for exact slide_type match
    if slide_type in TEXT_PLAYBOOK:
        return TEXT_PLAYBOOK[slide_type]
    
    # If no exact match, analyze narrative for keywords
    narrative_lower = narrative.lower()
    
    if any(word in narrative_lower for word in ["case", "story", "transform", "success"]):
        return TEXT_PLAYBOOK.get("case_study_slide", TEXT_PLAYBOOK["default"])
    elif any(word in narrative_lower for word in ["summary", "overview", "key findings"]):
        return TEXT_PLAYBOOK.get("executive_summary", TEXT_PLAYBOOK["default"])
    elif any(word in narrative_lower for word in ["compare", "versus", "options", "choice"]):
        return TEXT_PLAYBOOK.get("comparison", TEXT_PLAYBOOK["default"])
    elif any(word in narrative_lower for word in ["process", "steps", "workflow", "how"]):
        return TEXT_PLAYBOOK.get("process_explanation", TEXT_PLAYBOOK["default"])
    elif any(word in narrative_lower for word in ["data", "metric", "analytics", "insight"]):
        return TEXT_PLAYBOOK.get("data_driven", TEXT_PLAYBOOK["default"])
    elif any(word in narrative_lower for word in ["agenda", "outline", "topics"]):
        return TEXT_PLAYBOOK.get("agenda_slide", TEXT_PLAYBOOK["default"])
    elif any(word in narrative_lower for word in ["conclusion", "final", "closing"]):
        return TEXT_PLAYBOOK.get("conclusion_slide", TEXT_PLAYBOOK["default"])
    else:
        return TEXT_PLAYBOOK["default"]  # Default strategy


def get_analytics_strategy(data_type: str, story_goal: str) -> Dict[str, Any]:
    """
    Select the best analytics strategy based on data type and story goal.
    
    Args:
        data_type: Type of data to visualize
        story_goal: The story we want to tell with the data
        
    Returns:
        The most appropriate analytics strategy from ANALYTICS_PLAYBOOK
    """
    story_lower = story_goal.lower()
    
    if any(word in story_lower for word in ["compare", "versus", "between"]):
        return ANALYTICS_PLAYBOOK["comparison"]
    elif any(word in story_lower for word in ["trend", "time", "growth", "change"]):
        return ANALYTICS_PLAYBOOK["trend_analysis"]
    elif any(word in story_lower for word in ["distribution", "spread", "range"]):
        return ANALYTICS_PLAYBOOK["distribution"]
    elif any(word in story_lower for word in ["composition", "breakdown", "parts"]):
        return ANALYTICS_PLAYBOOK["composition"]
    elif any(word in story_lower for word in ["correlation", "relationship", "impact"]):
        return ANALYTICS_PLAYBOOK["correlation"]
    else:
        return ANALYTICS_PLAYBOOK["comparison"]  # Default strategy


def get_image_archetype(purpose: str, mood: List[str]) -> Dict[str, Any]:
    """
    Select the best image archetype based on purpose and mood.
    
    Args:
        purpose: The purpose of the image
        mood: List of mood keywords
        
    Returns:
        The most appropriate image archetype from IMAGE_PLAYBOOK
    """
    purpose_lower = purpose.lower()
    
    if any(word in purpose_lower for word in ["hero", "impact", "opening", "title"]):
        return IMAGE_PLAYBOOK["hero_image"]
    elif any(word in purpose_lower for word in ["concept", "abstract", "metaphor"]):
        return IMAGE_PLAYBOOK["conceptual_metaphor"]
    elif any(word in purpose_lower for word in ["people", "human", "story", "case"]):
        return IMAGE_PLAYBOOK["data_humanization"]
    else:
        return IMAGE_PLAYBOOK["spot_illustration"]  # Default for general use


def get_diagram_pattern(information_type: str, relationship_type: str) -> Dict[str, Any]:
    """
    Select the best diagram pattern based on information and relationship types.
    
    Args:
        information_type: Type of information to visualize
        relationship_type: Type of relationships to show
        
    Returns:
        The most appropriate diagram pattern from DIAGRAM_PLAYBOOK
    """
    info_lower = information_type.lower()
    rel_lower = relationship_type.lower()
    
    if any(word in info_lower for word in ["process", "workflow", "steps", "sequence"]):
        return DIAGRAM_PLAYBOOK["process_flow"]
    elif any(word in info_lower for word in ["organization", "hierarchy", "structure"]):
        return DIAGRAM_PLAYBOOK["organizational_hierarchy"]
    elif any(word in info_lower for word in ["system", "architecture", "technical"]):
        return DIAGRAM_PLAYBOOK["system_architecture"]
    elif any(word in rel_lower for word in ["concept", "ideas", "relationship"]):
        return DIAGRAM_PLAYBOOK["concept_map"]
    else:
        return DIAGRAM_PLAYBOOK["process_flow"]  # Default pattern


def get_table_structure(data_purpose: str, data_complexity: str) -> Dict[str, Any]:
    """
    Select the best table structure based on purpose and complexity.
    
    Args:
        data_purpose: The purpose of the table
        data_complexity: The complexity level of the data
        
    Returns:
        The most appropriate table structure from TABLE_PLAYBOOK
    """
    purpose_lower = data_purpose.lower()
    
    if any(word in purpose_lower for word in ["compare", "comparison", "versus"]):
        return TABLE_PLAYBOOK["comparison_matrix"]
    elif any(word in purpose_lower for word in ["summary", "metrics", "kpi", "dashboard"]):
        return TABLE_PLAYBOOK["data_summary"]
    elif any(word in purpose_lower for word in ["features", "specifications", "list"]):
        return TABLE_PLAYBOOK["feature_list"]
    else:
        return TABLE_PLAYBOOK["data_summary"]  # Default structure


def get_icon_for_concept(concept: str) -> str:
    """
    Get the most appropriate icon for a concept.
    
    Args:
        concept: The concept to represent
        
    Returns:
        The icon name from the icon mapping
    """
    concept_lower = concept.lower()
    
    # Check direct mapping
    for key, icons in ICON_PLAYBOOK["concept_mapping"].items():
        if key in concept_lower:
            return icons[0]  # Return the first icon option
    
    # Default to a generic icon
    return "circle_dot"


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class PlaybookSession:
    """
    Manages playbook usage across a presentation session.
    Tracks which strategies have been used and ensures consistency.
    """
    
    def __init__(self):
        self.used_strategies = {
            "text": [],
            "analytics": [],
            "image": [],
            "diagram": [],
            "table": []
        }
        self.icon_library = {}
        self.style_locked = False
    
    def record_strategy_use(self, component_type: str, strategy_name: str):
        """Record that a strategy has been used."""
        if component_type in self.used_strategies:
            self.used_strategies[component_type].append(strategy_name)
    
    def get_icon_consistency(self, concept: str) -> str:
        """Get consistent icon for a concept across the presentation."""
        if concept not in self.icon_library:
            self.icon_library[concept] = get_icon_for_concept(concept)
        return self.icon_library[concept]
    
    def lock_style(self):
        """Lock the style choices for consistency."""
        self.style_locked = True
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of playbook usage in this session."""
        return {
            "strategies_used": self.used_strategies,
            "unique_icons": len(self.icon_library),
            "icon_mapping": self.icon_library,
            "style_locked": self.style_locked
        }