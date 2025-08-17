"""
SVG Template Playbook
=====================

Comprehensive specifications for all SVG diagram templates with text capacity,
placeholder IDs, and usage guidelines.

Based on validated templates and user specifications.

Author: Diagram Generation System
Date: 2024
Version: 1.0
"""

from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


SVG_PLAYBOOK = {
    "version": "1.0",
    "default_viewbox": "0 0 800 600",
    "templates": {
        # ============== CYCLE / LOOP TEMPLATES ==============
        "cycle_3_step": {
            "name": "3-Step Cycle",
            "category": "cycle",
            "file_name": "cycle_3_step.svg",
            "status": "existing",
            "visual_description": "Three curved arrows forming a circular flow",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "step_1_title": {
                    "id": "step_1_text",
                    "purpose": "First step in cycle",
                    "position": "top",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "step_2_title": {
                    "id": "step_2_text",
                    "purpose": "Second step in cycle",
                    "position": "bottom-right",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "step_3_title": {
                    "id": "step_3_text",
                    "purpose": "Third step in cycle",
                    "position": "bottom-left",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                }
            },
            "color_elements": {
                "step_fills": ["step_1_fill", "step_2_fill", "step_3_fill"],
                "arrows": ["arrow_1", "arrow_2", "arrow_3"]
            },
            "when_to_use": [
                "Continuous improvement cycles",
                "Iterative processes",
                "Feedback loops",
                "Plan-Do-Check cycles"
            ]
        },
        
        "cycle_4_step": {
            "name": "4-Step Cycle",
            "category": "cycle",
            "file_name": "cycle_4_step.svg",
            "status": "existing",
            "visual_description": "Four curved arrows forming a circular flow",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "step_1_title": {
                    "id": "step_1_text",
                    "purpose": "First step in cycle",
                    "position": "top",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "step_2_title": {
                    "id": "step_2_text",
                    "purpose": "Second step in cycle",
                    "position": "right",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "step_3_title": {
                    "id": "step_3_text",
                    "purpose": "Third step in cycle",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "step_4_title": {
                    "id": "step_4_text",
                    "purpose": "Fourth step in cycle",
                    "position": "left",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                }
            },
            "color_elements": {
                "step_fills": ["step_1_fill", "step_2_fill", "step_3_fill", "step_4_fill"],
                "arrows": ["arrow_1", "arrow_2", "arrow_3", "arrow_4"]
            },
            "when_to_use": [
                "PDCA cycles",
                "Seasonal processes",
                "Quarterly reviews",
                "Four-phase workflows"
            ]
        },
        
        "cycle_5_step": {
            "name": "5-Step Cycle",
            "category": "cycle",
            "file_name": "cycle_5_step.svg",
            "status": "existing",
            "visual_description": "Five curved arrows forming a circular flow",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "step_1_title": {
                    "id": "step_1_text",
                    "purpose": "First step in cycle",
                    "position": "top",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_2_title": {
                    "id": "step_2_text",
                    "purpose": "Second step in cycle",
                    "position": "top-right",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_3_title": {
                    "id": "step_3_text",
                    "purpose": "Third step in cycle",
                    "position": "bottom-right",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_4_title": {
                    "id": "step_4_text",
                    "purpose": "Fourth step in cycle",
                    "position": "bottom-left",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_5_title": {
                    "id": "step_5_text",
                    "purpose": "Fifth step in cycle",
                    "position": "top-left",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "step_fills": ["step_1_fill", "step_2_fill", "step_3_fill", "step_4_fill", "step_5_fill"],
                "arrows": ["arrow_1", "arrow_2", "arrow_3", "arrow_4", "arrow_5"]
            },
            "when_to_use": [
                "Complex iterative processes",
                "Five-phase methodologies",
                "Design thinking cycles",
                "Extended feedback loops"
            ]
        },

        # ============== FUNNEL TEMPLATES ==============
        "funnel_3_stage": {
            "name": "3-Stage Funnel",
            "category": "funnel",
            "file_name": "funnel_3_stage.svg",
            "status": "planned",
            "visual_description": "A funnel divided into 3 horizontal sections",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "funnel_title",
                    "purpose": "Main funnel title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "stage_1_title": {
                    "id": "stage_1_text",
                    "purpose": "Top stage (widest)",
                    "position": "top-section",
                    "capacity": {"chars_per_line": 25, "max_lines": 1, "font_size": 16}
                },
                "stage_2_title": {
                    "id": "stage_2_text",
                    "purpose": "Middle stage",
                    "position": "middle-section",
                    "capacity": {"chars_per_line": 20, "max_lines": 1, "font_size": 16}
                },
                "stage_3_title": {
                    "id": "stage_3_text",
                    "purpose": "Bottom stage (narrowest)",
                    "position": "bottom-section",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 16}
                }
            },
            "color_elements": {
                "stage_fills": ["stage_1_fill", "stage_2_fill", "stage_3_fill"]
            },
            "when_to_use": [
                "Simple conversion funnels",
                "Basic sales processes",
                "Three-tier filtering",
                "Qualification stages"
            ]
        },
        
        "funnel_4_stage": {
            "name": "4-Stage Funnel",
            "category": "funnel",
            "file_name": "funnel_4_stage.svg",
            "status": "planned",
            "visual_description": "A funnel divided into 4 horizontal sections",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "funnel_title",
                    "purpose": "Main funnel title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "stage_1_title": {
                    "id": "stage_1_text",
                    "purpose": "Top stage (widest)",
                    "position": "top-section",
                    "capacity": {"chars_per_line": 25, "max_lines": 1, "font_size": 16}
                },
                "stage_2_title": {
                    "id": "stage_2_text",
                    "purpose": "Second stage",
                    "position": "upper-middle",
                    "capacity": {"chars_per_line": 22, "max_lines": 1, "font_size": 16}
                },
                "stage_3_title": {
                    "id": "stage_3_text",
                    "purpose": "Third stage",
                    "position": "lower-middle",
                    "capacity": {"chars_per_line": 18, "max_lines": 1, "font_size": 16}
                },
                "stage_4_title": {
                    "id": "stage_4_text",
                    "purpose": "Bottom stage (narrowest)",
                    "position": "bottom-section",
                    "capacity": {"chars_per_line": 12, "max_lines": 1, "font_size": 16}
                }
            },
            "color_elements": {
                "stage_fills": ["stage_1_fill", "stage_2_fill", "stage_3_fill", "stage_4_fill"]
            },
            "when_to_use": [
                "AIDA model",
                "Four-stage sales process",
                "Customer journey funnel",
                "Detailed conversion tracking"
            ]
        },
        
        "funnel_5_stage": {
            "name": "5-Stage Funnel",
            "category": "funnel",
            "file_name": "funnel_5_stage.svg",
            "status": "existing",
            "visual_description": "A funnel divided into 5 horizontal sections",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "funnel_title",
                    "purpose": "Main funnel title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "stage_1_title": {
                    "id": "stage_1_text",
                    "purpose": "Top stage (widest)",
                    "position": "top-section",
                    "capacity": {"chars_per_line": 25, "max_lines": 1, "font_size": 16}
                },
                "stage_2_title": {
                    "id": "stage_2_text",
                    "purpose": "Second stage",
                    "position": "upper-section",
                    "capacity": {"chars_per_line": 22, "max_lines": 1, "font_size": 16}
                },
                "stage_3_title": {
                    "id": "stage_3_text",
                    "purpose": "Middle stage",
                    "position": "middle-section",
                    "capacity": {"chars_per_line": 18, "max_lines": 1, "font_size": 16}
                },
                "stage_4_title": {
                    "id": "stage_4_text",
                    "purpose": "Fourth stage",
                    "position": "lower-section",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 16}
                },
                "stage_5_title": {
                    "id": "stage_5_text",
                    "purpose": "Bottom stage (narrowest)",
                    "position": "bottom-section",
                    "capacity": {"chars_per_line": 10, "max_lines": 1, "font_size": 16}
                }
            },
            "color_elements": {
                "stage_fills": ["stage_1_fill", "stage_2_fill", "stage_3_fill", "stage_4_fill", "stage_5_fill"]
            },
            "when_to_use": [
                "Detailed sales funnels",
                "Complex conversion processes",
                "Multi-stage filtering",
                "Comprehensive customer journey"
            ]
        },

        # ============== HONEYCOMB TEMPLATES ==============
        "honeycomb_3": {
            "name": "3-Cell Honeycomb",
            "category": "honeycomb",
            "file_name": "honeycomb_3.svg",
            "status": "existing",
            "visual_description": "A central hexagon surrounded by two others",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "honeycomb_title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "hex_1_title": {
                    "id": "hex_1_text",
                    "purpose": "Central hexagon",
                    "position": "center",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "hex_2_title": {
                    "id": "hex_2_text",
                    "purpose": "Right hexagon",
                    "position": "right",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "hex_3_title": {
                    "id": "hex_3_text",
                    "purpose": "Left hexagon",
                    "position": "left",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "hex_fills": ["hex_1_fill", "hex_2_fill", "hex_3_fill"]
            },
            "when_to_use": [
                "Core concept with two supporting elements",
                "Simple interconnected systems",
                "Three-part relationships",
                "Minimal network diagrams"
            ]
        },
        
        "honeycomb_5": {
            "name": "5-Cell Honeycomb",
            "category": "honeycomb",
            "file_name": "honeycomb_5.svg",
            "status": "existing",
            "visual_description": "A central hexagon surrounded by four others",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "honeycomb_title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "hex_1_title": {
                    "id": "hex_1_text",
                    "purpose": "Central hexagon",
                    "position": "center",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "hex_2_title": {
                    "id": "hex_2_text",
                    "purpose": "Top hexagon",
                    "position": "top",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "hex_3_title": {
                    "id": "hex_3_text",
                    "purpose": "Right hexagon",
                    "position": "right",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "hex_4_title": {
                    "id": "hex_4_text",
                    "purpose": "Bottom hexagon",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "hex_5_title": {
                    "id": "hex_5_text",
                    "purpose": "Left hexagon",
                    "position": "left",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "hex_fills": ["hex_1_fill", "hex_2_fill", "hex_3_fill", "hex_4_fill", "hex_5_fill"]
            },
            "when_to_use": [
                "Central concept with four pillars",
                "Balanced system components",
                "Five-element frameworks",
                "Cross-functional relationships"
            ]
        },
        
        "honeycomb_7": {
            "name": "7-Cell Honeycomb",
            "category": "honeycomb",
            "file_name": "honeycomb_7.svg",
            "status": "existing",
            "visual_description": "A central hexagon surrounded by six others",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "honeycomb_title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "hex_1_title": {
                    "id": "hex_1_text",
                    "purpose": "Central hexagon (core)",
                    "position": "center",
                    "capacity": {"chars_per_line": 8, "max_lines": 2, "font_size": 14}
                },
                "hex_2_title": {
                    "id": "hex_2_text",
                    "purpose": "East hexagon",
                    "position": "east",
                    "capacity": {"chars_per_line": 8, "max_lines": 2, "font_size": 14}
                },
                "hex_3_title": {
                    "id": "hex_3_text",
                    "purpose": "Northeast hexagon",
                    "position": "northeast",
                    "capacity": {"chars_per_line": 8, "max_lines": 2, "font_size": 14}
                },
                "hex_4_title": {
                    "id": "hex_4_text",
                    "purpose": "Northwest hexagon",
                    "position": "northwest",
                    "capacity": {"chars_per_line": 8, "max_lines": 2, "font_size": 14}
                },
                "hex_5_title": {
                    "id": "hex_5_text",
                    "purpose": "West hexagon",
                    "position": "west",
                    "capacity": {"chars_per_line": 8, "max_lines": 2, "font_size": 14}
                },
                "hex_6_title": {
                    "id": "hex_6_text",
                    "purpose": "Southwest hexagon",
                    "position": "southwest",
                    "capacity": {"chars_per_line": 8, "max_lines": 2, "font_size": 14}
                },
                "hex_7_title": {
                    "id": "hex_7_text",
                    "purpose": "Southeast hexagon",
                    "position": "southeast",
                    "capacity": {"chars_per_line": 8, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "hex_fills": ["hex_1_fill", "hex_2_fill", "hex_3_fill", "hex_4_fill", "hex_5_fill", "hex_6_fill", "hex_7_fill"]
            },
            "when_to_use": [
                "Complete surrounding relationships",
                "Six supporting elements",
                "Comprehensive frameworks",
                "Full ecosystem visualization"
            ]
        },

        # ============== HUB & SPOKE TEMPLATES ==============
        "hub_spoke_4": {
            "name": "4-Spoke Hub",
            "category": "hub_spoke",
            "file_name": "hub_spoke_4.svg",
            "status": "existing",
            "visual_description": "A central circle with 4 lines radiating to 4 outer circles",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "hub_title": {
                    "id": "hub_text",
                    "purpose": "Central hub",
                    "position": "center",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 16}
                },
                "spoke_1_title": {
                    "id": "spoke_1_text",
                    "purpose": "Top spoke",
                    "position": "top",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_2_title": {
                    "id": "spoke_2_text",
                    "purpose": "Right spoke",
                    "position": "right",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_3_title": {
                    "id": "spoke_3_text",
                    "purpose": "Bottom spoke",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_4_title": {
                    "id": "spoke_4_text",
                    "purpose": "Left spoke",
                    "position": "left",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "hub_fill": "hub_fill",
                "spoke_fills": ["spoke_1_fill", "spoke_2_fill", "spoke_3_fill", "spoke_4_fill"],
                "connectors": ["connector_1", "connector_2", "connector_3", "connector_4"]
            },
            "when_to_use": [
                "Central system with four branches",
                "Organizational structure",
                "Four-directional relationships",
                "Distribution networks"
            ]
        },
        
        "hub_spoke_6": {
            "name": "6-Spoke Hub",
            "category": "hub_spoke",
            "file_name": "hub_spoke_6.svg",
            "status": "existing",
            "visual_description": "A central circle with 6 lines radiating to 6 outer circles",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "hub_title": {
                    "id": "hub_text",
                    "purpose": "Central hub",
                    "position": "center",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 16}
                },
                "spoke_1_title": {
                    "id": "spoke_1_text",
                    "purpose": "Top spoke",
                    "position": "top",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_2_title": {
                    "id": "spoke_2_text",
                    "purpose": "Top-right spoke",
                    "position": "top-right",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_3_title": {
                    "id": "spoke_3_text",
                    "purpose": "Bottom-right spoke",
                    "position": "bottom-right",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_4_title": {
                    "id": "spoke_4_text",
                    "purpose": "Bottom spoke",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_5_title": {
                    "id": "spoke_5_text",
                    "purpose": "Bottom-left spoke",
                    "position": "bottom-left",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "spoke_6_title": {
                    "id": "spoke_6_text",
                    "purpose": "Top-left spoke",
                    "position": "top-left",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "hub_fill": "hub_fill",
                "spoke_fills": ["spoke_1_fill", "spoke_2_fill", "spoke_3_fill", "spoke_4_fill", "spoke_5_fill", "spoke_6_fill"],
                "connectors": ["connector_1", "connector_2", "connector_3", "connector_4", "connector_5", "connector_6"]
            },
            "when_to_use": [
                "Central system with six branches",
                "Comprehensive distribution",
                "Six-dimensional analysis",
                "Extended network topology"
            ]
        },

        # ============== MATRIX TEMPLATES ==============
        "matrix_2x2": {
            "name": "2x2 Matrix",
            "category": "matrix",
            "file_name": "matrix_2x2.svg",
            "status": "existing",
            "visual_description": "A square divided into a 2x2 grid",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "matrix_title",
                    "purpose": "Main matrix title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "x_axis_title": {
                    "id": "x_label",
                    "purpose": "X-axis label",
                    "position": "bottom-center",
                    "capacity": {"chars_per_line": 30, "max_lines": 1, "font_size": 14}
                },
                "y_axis_title": {
                    "id": "y_label",
                    "purpose": "Y-axis label",
                    "position": "left-center",
                    "capacity": {"chars_per_line": 30, "max_lines": 1, "font_size": 14}
                },
                "quad_1_title": {
                    "id": "quadrant_1",
                    "purpose": "Top-right quadrant (High/High)",
                    "position": "top-right",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 16}
                },
                "quad_2_title": {
                    "id": "quadrant_2",
                    "purpose": "Top-left quadrant (Low/High)",
                    "position": "top-left",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 16}
                },
                "quad_3_title": {
                    "id": "quadrant_3",
                    "purpose": "Bottom-left quadrant (Low/Low)",
                    "position": "bottom-left",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 16}
                },
                "quad_4_title": {
                    "id": "quadrant_4",
                    "purpose": "Bottom-right quadrant (High/Low)",
                    "position": "bottom-right",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 16}
                }
            },
            "color_elements": {
                "quadrant_fills": ["q1_fill", "q2_fill", "q3_fill", "q4_fill"]
            },
            "when_to_use": [
                "Priority matrices",
                "Risk assessment",
                "Effort vs impact analysis",
                "BCG growth-share matrix"
            ]
        },
        
        "matrix_3x3": {
            "name": "3x3 Matrix",
            "category": "matrix",
            "file_name": "matrix_3x3.svg",
            "status": "planned",
            "visual_description": "A square divided into a 3x3 grid",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "matrix_title",
                    "purpose": "Main matrix title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "x_axis_title": {
                    "id": "x_label",
                    "purpose": "X-axis label",
                    "position": "bottom-center",
                    "capacity": {"chars_per_line": 30, "max_lines": 1, "font_size": 14}
                },
                "y_axis_title": {
                    "id": "y_label",
                    "purpose": "Y-axis label",
                    "position": "left-center",
                    "capacity": {"chars_per_line": 30, "max_lines": 1, "font_size": 14}
                },
                "cell_1_1_text": {
                    "id": "cell_1_1",
                    "purpose": "Top-left cell",
                    "position": "row-1-col-1",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_1_2_text": {
                    "id": "cell_1_2",
                    "purpose": "Top-center cell",
                    "position": "row-1-col-2",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_1_3_text": {
                    "id": "cell_1_3",
                    "purpose": "Top-right cell",
                    "position": "row-1-col-3",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_2_1_text": {
                    "id": "cell_2_1",
                    "purpose": "Middle-left cell",
                    "position": "row-2-col-1",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_2_2_text": {
                    "id": "cell_2_2",
                    "purpose": "Center cell",
                    "position": "row-2-col-2",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_2_3_text": {
                    "id": "cell_2_3",
                    "purpose": "Middle-right cell",
                    "position": "row-2-col-3",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_3_1_text": {
                    "id": "cell_3_1",
                    "purpose": "Bottom-left cell",
                    "position": "row-3-col-1",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_3_2_text": {
                    "id": "cell_3_2",
                    "purpose": "Bottom-center cell",
                    "position": "row-3-col-2",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "cell_3_3_text": {
                    "id": "cell_3_3",
                    "purpose": "Bottom-right cell",
                    "position": "row-3-col-3",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "cell_fills": ["cell_1_1_fill", "cell_1_2_fill", "cell_1_3_fill",
                              "cell_2_1_fill", "cell_2_2_fill", "cell_2_3_fill",
                              "cell_3_1_fill", "cell_3_2_fill", "cell_3_3_fill"]
            },
            "when_to_use": [
                "Nine-box talent grid",
                "GE-McKinsey matrix",
                "Detailed categorization",
                "Three-level comparisons"
            ]
        },
        
        "swot_matrix": {
            "name": "SWOT Matrix",
            "category": "matrix",
            "file_name": "swot_matrix.svg",
            "status": "existing",
            "visual_description": "2x2 matrix specifically for SWOT analysis",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "swot_title",
                    "purpose": "SWOT Analysis title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "strengths_title": {
                    "id": "strengths_header",
                    "purpose": "Strengths header",
                    "position": "top-left-header",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 18}
                },
                "strengths_items": {
                    "id": "strengths_list",
                    "purpose": "Strengths list items",
                    "position": "top-left-body",
                    "capacity": {"chars_per_line": 25, "max_lines": 5, "font_size": 14}
                },
                "weaknesses_title": {
                    "id": "weaknesses_header",
                    "purpose": "Weaknesses header",
                    "position": "top-right-header",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 18}
                },
                "weaknesses_items": {
                    "id": "weaknesses_list",
                    "purpose": "Weaknesses list items",
                    "position": "top-right-body",
                    "capacity": {"chars_per_line": 25, "max_lines": 5, "font_size": 14}
                },
                "opportunities_title": {
                    "id": "opportunities_header",
                    "purpose": "Opportunities header",
                    "position": "bottom-left-header",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 18}
                },
                "opportunities_items": {
                    "id": "opportunities_list",
                    "purpose": "Opportunities list items",
                    "position": "bottom-left-body",
                    "capacity": {"chars_per_line": 25, "max_lines": 5, "font_size": 14}
                },
                "threats_title": {
                    "id": "threats_header",
                    "purpose": "Threats header",
                    "position": "bottom-right-header",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 18}
                },
                "threats_items": {
                    "id": "threats_list",
                    "purpose": "Threats list items",
                    "position": "bottom-right-body",
                    "capacity": {"chars_per_line": 25, "max_lines": 5, "font_size": 14}
                }
            },
            "color_elements": {
                "quadrant_fills": ["strengths_fill", "weaknesses_fill", "opportunities_fill", "threats_fill"]
            },
            "when_to_use": [
                "Strategic planning",
                "Business analysis",
                "Competitive assessment",
                "Decision making"
            ]
        },

        # ============== PROCESS FLOW TEMPLATES ==============
        "process_flow_3": {
            "name": "3-Step Process Flow",
            "category": "process",
            "file_name": "process_flow_3.svg",
            "status": "planned",
            "visual_description": "Three chevrons pointing right in a sequence",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "process_title",
                    "purpose": "Main process title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "step_1_title": {
                    "id": "step_1_text",
                    "purpose": "First step",
                    "position": "left",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "step_2_title": {
                    "id": "step_2_text",
                    "purpose": "Second step",
                    "position": "center",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "step_3_title": {
                    "id": "step_3_text",
                    "purpose": "Third step",
                    "position": "right",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                }
            },
            "color_elements": {
                "step_fills": ["step_1_fill", "step_2_fill", "step_3_fill"]
            },
            "when_to_use": [
                "Simple linear processes",
                "Three-phase projects",
                "Sequential workflows",
                "Basic procedures"
            ]
        },
        
        "process_flow_5": {
            "name": "5-Step Process Flow",
            "category": "process",
            "file_name": "process_flow_5.svg",
            "status": "existing",
            "visual_description": "Five chevrons pointing right in a sequence",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "process_title",
                    "purpose": "Main process title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "step_1_title": {
                    "id": "step_1_text",
                    "purpose": "First step",
                    "position": "far-left",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_2_title": {
                    "id": "step_2_text",
                    "purpose": "Second step",
                    "position": "left",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_3_title": {
                    "id": "step_3_text",
                    "purpose": "Third step",
                    "position": "center",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_4_title": {
                    "id": "step_4_text",
                    "purpose": "Fourth step",
                    "position": "right",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "step_5_title": {
                    "id": "step_5_text",
                    "purpose": "Fifth step",
                    "position": "far-right",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "step_fills": ["step_1_fill", "step_2_fill", "step_3_fill", "step_4_fill", "step_5_fill"]
            },
            "when_to_use": [
                "Detailed linear processes",
                "Five-phase methodologies",
                "Extended workflows",
                "Comprehensive procedures"
            ]
        },

        # ============== PYRAMID TEMPLATES ==============
        "pyramid_3_level": {
            "name": "3-Level Pyramid",
            "category": "pyramid",
            "file_name": "pyramid_3_level.svg",
            "status": "existing",
            "visual_description": "A triangle divided into 3 horizontal levels",
            "dimensions": {
                "viewbox": "0 0 1000 750",
                "width": 1000,
                "height": 750
            },
            "text_placeholders": {
                "title": {
                    "id": "pyramid_title",
                    "purpose": "Main pyramid title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 26}
                },
                "level_1_title": {
                    "id": "level_1_text",
                    "purpose": "Top level (peak)",
                    "position": "top",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 18}
                },
                "level_2_title": {
                    "id": "level_2_text",
                    "purpose": "Middle level",
                    "position": "middle",
                    "capacity": {"chars_per_line": 18, "max_lines": 2, "font_size": 18}
                },
                "level_3_title": {
                    "id": "level_3_text",
                    "purpose": "Bottom level (foundation)",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 25, "max_lines": 2, "font_size": 18}
                }
            },
            "color_elements": {
                "level_fills": ["level_1_fill", "level_2_fill", "level_3_fill"]
            },
            "when_to_use": [
                "Hierarchical structures",
                "Maslow's hierarchy",
                "Priority levels",
                "Foundation to peak concepts"
            ]
        },
        
        "pyramid_4_level": {
            "name": "4-Level Pyramid",
            "category": "pyramid",
            "file_name": "pyramid_4_level.svg",
            "status": "planned",
            "visual_description": "A triangle divided into 4 horizontal levels",
            "dimensions": {
                "viewbox": "0 0 1000 750",
                "width": 1000,
                "height": 750
            },
            "text_placeholders": {
                "title": {
                    "id": "pyramid_title",
                    "purpose": "Main pyramid title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 26}
                },
                "level_1_title": {
                    "id": "level_1_text",
                    "purpose": "Top level (peak)",
                    "position": "top",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 16}
                },
                "level_2_title": {
                    "id": "level_2_text",
                    "purpose": "Upper-middle level",
                    "position": "upper-middle",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "level_3_title": {
                    "id": "level_3_text",
                    "purpose": "Lower-middle level",
                    "position": "lower-middle",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 16}
                },
                "level_4_title": {
                    "id": "level_4_text",
                    "purpose": "Bottom level (foundation)",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 25, "max_lines": 2, "font_size": 16}
                }
            },
            "color_elements": {
                "level_fills": ["level_1_fill", "level_2_fill", "level_3_fill", "level_4_fill"]
            },
            "when_to_use": [
                "Four-tier hierarchies",
                "Detailed organizational levels",
                "Competency models",
                "Layered architectures"
            ]
        },
        
        "pyramid_5_level": {
            "name": "5-Level Pyramid",
            "category": "pyramid",
            "file_name": "pyramid_5_level.svg",
            "status": "planned",
            "visual_description": "A triangle divided into 5 horizontal levels",
            "dimensions": {
                "viewbox": "0 0 1000 750",
                "width": 1000,
                "height": 750
            },
            "text_placeholders": {
                "title": {
                    "id": "pyramid_title",
                    "purpose": "Main pyramid title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 26}
                },
                "level_1_title": {
                    "id": "level_1_text",
                    "purpose": "Top level (peak)",
                    "position": "top",
                    "capacity": {"chars_per_line": 8, "max_lines": 1, "font_size": 14}
                },
                "level_2_title": {
                    "id": "level_2_text",
                    "purpose": "Second level",
                    "position": "second",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "level_3_title": {
                    "id": "level_3_text",
                    "purpose": "Middle level",
                    "position": "middle",
                    "capacity": {"chars_per_line": 16, "max_lines": 2, "font_size": 14}
                },
                "level_4_title": {
                    "id": "level_4_text",
                    "purpose": "Fourth level",
                    "position": "fourth",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "level_5_title": {
                    "id": "level_5_text",
                    "purpose": "Bottom level (foundation)",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 25, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "level_fills": ["level_1_fill", "level_2_fill", "level_3_fill", "level_4_fill", "level_5_fill"]
            },
            "when_to_use": [
                "Complex hierarchies",
                "Detailed maturity models",
                "Five-level frameworks",
                "Comprehensive pyramids"
            ]
        },

        # ============== VENN DIAGRAM TEMPLATES ==============
        "venn_2_circle": {
            "name": "2-Circle Venn",
            "category": "venn",
            "file_name": "venn_2_circle.svg",
            "status": "existing",
            "visual_description": "Two overlapping circles",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "venn_title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "circle_1_title": {
                    "id": "circle_1_text",
                    "purpose": "Left circle label",
                    "position": "left-circle",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "circle_2_title": {
                    "id": "circle_2_text",
                    "purpose": "Right circle label",
                    "position": "right-circle",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 16}
                },
                "intersection_1_2_text": {
                    "id": "intersection_text",
                    "purpose": "Overlap area",
                    "position": "center",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "circle_fills": ["circle_1_fill", "circle_2_fill"],
                "intersection_fill": "intersection_fill"
            },
            "when_to_use": [
                "Comparing two concepts",
                "Showing commonalities",
                "Set relationships",
                "Dual comparisons"
            ]
        },
        
        "venn_3_circle": {
            "name": "3-Circle Venn",
            "category": "venn",
            "file_name": "venn_3_circle.svg",
            "status": "planned",
            "visual_description": "Three overlapping circles",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "venn_title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "circle_1_title": {
                    "id": "circle_1_text",
                    "purpose": "Top circle label",
                    "position": "top-circle",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "circle_2_title": {
                    "id": "circle_2_text",
                    "purpose": "Bottom-left circle label",
                    "position": "bottom-left-circle",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "circle_3_title": {
                    "id": "circle_3_text",
                    "purpose": "Bottom-right circle label",
                    "position": "bottom-right-circle",
                    "capacity": {"chars_per_line": 12, "max_lines": 2, "font_size": 14}
                },
                "intersection_1_2_text": {
                    "id": "intersection_1_2",
                    "purpose": "Overlap between 1 and 2",
                    "position": "top-left",
                    "capacity": {"chars_per_line": 8, "max_lines": 1, "font_size": 12}
                },
                "intersection_2_3_text": {
                    "id": "intersection_2_3",
                    "purpose": "Overlap between 2 and 3",
                    "position": "bottom",
                    "capacity": {"chars_per_line": 8, "max_lines": 1, "font_size": 12}
                },
                "intersection_1_3_text": {
                    "id": "intersection_1_3",
                    "purpose": "Overlap between 1 and 3",
                    "position": "top-right",
                    "capacity": {"chars_per_line": 8, "max_lines": 1, "font_size": 12}
                },
                "intersection_1_2_3_text": {
                    "id": "intersection_all",
                    "purpose": "Center overlap of all three",
                    "position": "center",
                    "capacity": {"chars_per_line": 6, "max_lines": 1, "font_size": 12}
                }
            },
            "color_elements": {
                "circle_fills": ["circle_1_fill", "circle_2_fill", "circle_3_fill"],
                "intersection_fills": ["intersection_1_2_fill", "intersection_2_3_fill", "intersection_1_3_fill", "intersection_all_fill"]
            },
            "when_to_use": [
                "Three-way comparisons",
                "Complex relationships",
                "Triple intersections",
                "Comprehensive overlaps"
            ]
        },

        # ============== TIMELINE TEMPLATES ==============
        "timeline_horizontal": {
            "name": "Horizontal Timeline",
            "category": "timeline",
            "file_name": "timeline_horizontal.svg",
            "status": "existing",
            "visual_description": "Horizontal line with milestone markers",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "timeline_title",
                    "purpose": "Main timeline title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "milestone_1_date": {
                    "id": "milestone_1_date",
                    "purpose": "First milestone date",
                    "position": "below-marker-1",
                    "capacity": {"chars_per_line": 10, "max_lines": 1, "font_size": 12}
                },
                "milestone_1_text": {
                    "id": "milestone_1_text",
                    "purpose": "First milestone description",
                    "position": "above-marker-1",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 14}
                },
                "milestone_2_date": {
                    "id": "milestone_2_date",
                    "purpose": "Second milestone date",
                    "position": "below-marker-2",
                    "capacity": {"chars_per_line": 10, "max_lines": 1, "font_size": 12}
                },
                "milestone_2_text": {
                    "id": "milestone_2_text",
                    "purpose": "Second milestone description",
                    "position": "above-marker-2",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 14}
                },
                "milestone_3_date": {
                    "id": "milestone_3_date",
                    "purpose": "Third milestone date",
                    "position": "below-marker-3",
                    "capacity": {"chars_per_line": 10, "max_lines": 1, "font_size": 12}
                },
                "milestone_3_text": {
                    "id": "milestone_3_text",
                    "purpose": "Third milestone description",
                    "position": "above-marker-3",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 14}
                },
                "milestone_4_date": {
                    "id": "milestone_4_date",
                    "purpose": "Fourth milestone date",
                    "position": "below-marker-4",
                    "capacity": {"chars_per_line": 10, "max_lines": 1, "font_size": 12}
                },
                "milestone_4_text": {
                    "id": "milestone_4_text",
                    "purpose": "Fourth milestone description",
                    "position": "above-marker-4",
                    "capacity": {"chars_per_line": 15, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "timeline_line": "timeline_line",
                "milestone_markers": ["milestone_1_marker", "milestone_2_marker", "milestone_3_marker", "milestone_4_marker"]
            },
            "when_to_use": [
                "Project timelines",
                "Historical events",
                "Roadmaps",
                "Milestone tracking"
            ]
        },

        # ============== ROADMAP TEMPLATES ==============
        "roadmap_quarterly_4": {
            "name": "Quarterly Roadmap",
            "category": "roadmap",
            "file_name": "roadmap_quarterly_4.svg",
            "status": "existing",
            "visual_description": "A horizontal timeline with 4 sections for quarters",
            "dimensions": {
                "viewbox": "0 0 1000 600",
                "width": 1000,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "roadmap_title",
                    "purpose": "Main roadmap title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 50, "max_lines": 1, "font_size": 24}
                },
                "q1_title": {
                    "id": "q1_header",
                    "purpose": "Q1 header",
                    "position": "q1-top",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 16}
                },
                "q1_item_1": {
                    "id": "q1_item_1",
                    "purpose": "Q1 first item",
                    "position": "q1-row-1",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "q1_item_2": {
                    "id": "q1_item_2",
                    "purpose": "Q1 second item",
                    "position": "q1-row-2",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "q2_title": {
                    "id": "q2_header",
                    "purpose": "Q2 header",
                    "position": "q2-top",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 16}
                },
                "q2_item_1": {
                    "id": "q2_item_1",
                    "purpose": "Q2 first item",
                    "position": "q2-row-1",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "q2_item_2": {
                    "id": "q2_item_2",
                    "purpose": "Q2 second item",
                    "position": "q2-row-2",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "q3_title": {
                    "id": "q3_header",
                    "purpose": "Q3 header",
                    "position": "q3-top",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 16}
                },
                "q3_item_1": {
                    "id": "q3_item_1",
                    "purpose": "Q3 first item",
                    "position": "q3-row-1",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "q3_item_2": {
                    "id": "q3_item_2",
                    "purpose": "Q3 second item",
                    "position": "q3-row-2",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "q4_title": {
                    "id": "q4_header",
                    "purpose": "Q4 header",
                    "position": "q4-top",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 16}
                },
                "q4_item_1": {
                    "id": "q4_item_1",
                    "purpose": "Q4 first item",
                    "position": "q4-row-1",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                },
                "q4_item_2": {
                    "id": "q4_item_2",
                    "purpose": "Q4 second item",
                    "position": "q4-row-2",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "quarter_fills": ["q1_fill", "q2_fill", "q3_fill", "q4_fill"],
                "item_fills": ["q1_items_fill", "q2_items_fill", "q3_items_fill", "q4_items_fill"]
            },
            "when_to_use": [
                "Product roadmaps",
                "Annual planning",
                "Quarterly objectives",
                "Release planning"
            ]
        },

        # ============== GEARS / COGS TEMPLATES ==============
        "gears_3": {
            "name": "3 Interlocking Gears",
            "category": "gears",
            "file_name": "gears_3.svg",
            "status": "planned",
            "visual_description": "Three interlocking gears",
            "dimensions": {
                "viewbox": "0 0 800 600",
                "width": 800,
                "height": 600
            },
            "text_placeholders": {
                "title": {
                    "id": "gears_title",
                    "purpose": "Main diagram title",
                    "position": "top-center",
                    "capacity": {"chars_per_line": 40, "max_lines": 1, "font_size": 24}
                },
                "gear_1_text": {
                    "id": "gear_1_text",
                    "purpose": "First gear label",
                    "position": "gear-1-center",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "gear_2_text": {
                    "id": "gear_2_text",
                    "purpose": "Second gear label",
                    "position": "gear-2-center",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                },
                "gear_3_text": {
                    "id": "gear_3_text",
                    "purpose": "Third gear label",
                    "position": "gear-3-center",
                    "capacity": {"chars_per_line": 10, "max_lines": 2, "font_size": 14}
                }
            },
            "color_elements": {
                "gear_fills": ["gear_1_fill", "gear_2_fill", "gear_3_fill"],
                "gear_teeth": ["gear_1_teeth", "gear_2_teeth", "gear_3_teeth"]
            },
            "when_to_use": [
                "Interconnected processes",
                "Mechanical relationships",
                "Synchronized operations",
                "Interdependent systems"
            ]
        },

        # ============== FISHBONE TEMPLATES ==============
        "fishbone_4_bone": {
            "name": "4-Bone Fishbone",
            "category": "fishbone",
            "file_name": "fishbone_4_bone.svg",
            "status": "planned",
            "visual_description": "A central horizontal line (spine) with a head and 4 diagonal bones branching off",
            "dimensions": {
                "viewbox": "0 0 1000 600",
                "width": 1000,
                "height": 600
            },
            "text_placeholders": {
                "head_title": {
                    "id": "head_text",
                    "purpose": "The effect (problem/outcome)",
                    "position": "right-head",
                    "capacity": {"chars_per_line": 20, "max_lines": 2, "font_size": 18}
                },
                "bone_1_title": {
                    "id": "bone_1_text",
                    "purpose": "First cause category",
                    "position": "top-left",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 14}
                },
                "bone_1_items": {
                    "id": "bone_1_items",
                    "purpose": "Specific causes under category 1",
                    "position": "top-left-items",
                    "capacity": {"chars_per_line": 20, "max_lines": 3, "font_size": 12}
                },
                "bone_2_title": {
                    "id": "bone_2_text",
                    "purpose": "Second cause category",
                    "position": "bottom-left",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 14}
                },
                "bone_2_items": {
                    "id": "bone_2_items",
                    "purpose": "Specific causes under category 2",
                    "position": "bottom-left-items",
                    "capacity": {"chars_per_line": 20, "max_lines": 3, "font_size": 12}
                },
                "bone_3_title": {
                    "id": "bone_3_text",
                    "purpose": "Third cause category",
                    "position": "top-right",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 14}
                },
                "bone_3_items": {
                    "id": "bone_3_items",
                    "purpose": "Specific causes under category 3",
                    "position": "top-right-items",
                    "capacity": {"chars_per_line": 20, "max_lines": 3, "font_size": 12}
                },
                "bone_4_title": {
                    "id": "bone_4_text",
                    "purpose": "Fourth cause category",
                    "position": "bottom-right",
                    "capacity": {"chars_per_line": 15, "max_lines": 1, "font_size": 14}
                },
                "bone_4_items": {
                    "id": "bone_4_items",
                    "purpose": "Specific causes under category 4",
                    "position": "bottom-right-items",
                    "capacity": {"chars_per_line": 20, "max_lines": 3, "font_size": 12}
                }
            },
            "color_elements": {
                "spine_fill": "spine_fill",
                "head_fill": "head_fill",
                "bone_fills": ["bone_1_fill", "bone_2_fill", "bone_3_fill", "bone_4_fill"]
            },
            "when_to_use": [
                "Root cause analysis",
                "Problem solving",
                "Cause and effect analysis",
                "Quality improvement"
            ]
        }
    }
}


def get_template_spec(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Get specification for a specific SVG template.
    
    Args:
        template_name: Name of the template to retrieve
        
    Returns:
        Dictionary with template specification or None if not found
    """
    return SVG_PLAYBOOK["templates"].get(template_name)


def get_templates_by_category(category: str) -> List[str]:
    """
    Get all templates in a specific category.
    
    Args:
        category: Category to filter by
        
    Returns:
        List of template names in the category
    """
    templates = []
    for template_name, spec in SVG_PLAYBOOK["templates"].items():
        if spec.get("category") == category:
            templates.append(template_name)
    return templates


def get_text_capacity(template_name: str, element_id: str) -> Optional[Dict[str, Any]]:
    """
    Get text capacity for a specific element in a template.
    
    Args:
        template_name: Name of the template
        element_id: ID of the text element
        
    Returns:
        Dictionary with text capacity information or None
    """
    spec = get_template_spec(template_name)
    if not spec:
        return None
    
    placeholders = spec.get("text_placeholders", {})
    for placeholder_data in placeholders.values():
        if placeholder_data.get("id") == element_id:
            return placeholder_data.get("capacity")
    
    return None


def get_placeholder_ids(template_name: str) -> List[str]:
    """
    Get all text placeholder IDs for a template.
    
    Args:
        template_name: Name of the template
        
    Returns:
        List of placeholder IDs
    """
    spec = get_template_spec(template_name)
    if not spec:
        return []
    
    placeholders = spec.get("text_placeholders", {})
    return [data.get("id") for data in placeholders.values() if data.get("id")]


def get_color_elements(template_name: str) -> Dict[str, Any]:
    """
    Get color element IDs that can be themed.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Dictionary of color element categories and their IDs
    """
    spec = get_template_spec(template_name)
    if not spec:
        return {}
    
    return spec.get("color_elements", {})


def get_template_dimensions(template_name: str) -> Dict[str, Any]:
    """
    Get dimensions for a template.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Dictionary with dimension information
    """
    spec = get_template_spec(template_name)
    if not spec:
        return {}
    
    return spec.get("dimensions", {})


def get_all_template_names() -> List[str]:
    """
    Get list of all template names.
    
    Returns:
        List of all template identifiers
    """
    return list(SVG_PLAYBOOK["templates"].keys())


def get_template_categories() -> List[str]:
    """
    Get all unique template categories.
    
    Returns:
        List of category names
    """
    categories = set()
    for spec in SVG_PLAYBOOK["templates"].values():
        if "category" in spec:
            categories.add(spec["category"])
    return sorted(list(categories))


def get_existing_templates() -> List[str]:
    """
    Get list of templates that have existing SVG files.
    
    Returns:
        List of template names with status 'existing'
    """
    existing = []
    for template_name, spec in SVG_PLAYBOOK["templates"].items():
        if spec.get("status") == "existing":
            existing.append(template_name)
    return existing


def get_planned_templates() -> List[str]:
    """
    Get list of templates that are planned but not yet created.
    
    Returns:
        List of template names with status 'planned'
    """
    planned = []
    for template_name, spec in SVG_PLAYBOOK["templates"].items():
        if spec.get("status") == "planned":
            planned.append(template_name)
    return planned


def validate_svg_structure(svg_content: str, template_name: str) -> Dict[str, Any]:
    """
    Validate that an SVG file contains expected placeholder IDs.
    
    Args:
        svg_content: SVG file content as string
        template_name: Name of the template to validate against
        
    Returns:
        Dictionary with validation results
    """
    spec = get_template_spec(template_name)
    if not spec:
        return {
            "valid": False,
            "error": f"Unknown template: {template_name}"
        }
    
    expected_ids = get_placeholder_ids(template_name)
    missing_ids = []
    
    for element_id in expected_ids:
        if f'id="{element_id}"' not in svg_content:
            missing_ids.append(element_id)
    
    return {
        "valid": len(missing_ids) == 0,
        "missing_ids": missing_ids,
        "expected_ids": expected_ids
    }


def calculate_text_fit(text: str, capacity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate if text will fit within specified capacity.
    
    Args:
        text: Text to check
        capacity: Capacity specification with chars_per_line and max_lines
        
    Returns:
        Dictionary with fit analysis
    """
    chars_per_line = capacity.get("chars_per_line", 20)
    max_lines = capacity.get("max_lines", 1)
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= chars_per_line:
            current_line = current_line + " " + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return {
        "fits": len(lines) <= max_lines,
        "lines_needed": len(lines),
        "max_lines": max_lines,
        "chars_per_line": chars_per_line,
        "wrapped_text": lines[:max_lines]
    }