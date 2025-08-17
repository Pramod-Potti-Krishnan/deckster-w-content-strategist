# SVG Template Playbook

## Overview

The SVG Template Playbook provides comprehensive specifications for 25 SVG diagram templates with detailed text capacity specifications, placeholder IDs, and usage guidelines. This playbook serves as the authoritative reference for SVG template usage within the system.

## Template Categories (12 Categories, 25 Templates)

### 1. **Cycle/Loop** (3 templates)
- `cycle_3_step` - Three curved arrows forming a circular flow [planned]
- `cycle_4_step` - Four curved arrows forming a circular flow [existing]
- `cycle_5_step` - Five curved arrows forming a circular flow [planned]

### 2. **Funnel** (3 templates)
- `funnel_3_stage` - A funnel divided into 3 horizontal sections [planned]
- `funnel_4_stage` - A funnel divided into 4 horizontal sections [planned]
- `funnel_5_stage` - A funnel divided into 5 horizontal sections [existing]

### 3. **Honeycomb** (3 templates)
- `honeycomb_3` - A central hexagon surrounded by two others [planned]
- `honeycomb_5` - A central hexagon surrounded by four others [planned]
- `honeycomb_7` - A central hexagon surrounded by six others [existing]

### 4. **Hub & Spoke** (2 templates)
- `hub_spoke_4` - Central circle with 4 radiating spokes [planned]
- `hub_spoke_6` - Central circle with 6 radiating spokes [existing]

### 5. **Matrix** (3 templates)
- `matrix_2x2` - A square divided into a 2x2 grid [existing]
- `matrix_3x3` - A square divided into a 3x3 grid [planned]
- `swot_matrix` - Specialized SWOT analysis matrix [existing]

### 6. **Process Flow** (2 templates)
- `process_flow_3` - Three chevrons pointing right [planned]
- `process_flow_5` - Five chevrons pointing right [existing]

### 7. **Pyramid** (3 templates)
- `pyramid_3_level` - Triangle divided into 3 levels [existing]
- `pyramid_4_level` - Triangle divided into 4 levels [planned]
- `pyramid_5_level` - Triangle divided into 5 levels [planned]

### 8. **Venn Diagram** (2 templates)
- `venn_2_circle` - Two overlapping circles [existing]
- `venn_3_circle` - Three overlapping circles [planned]

### 9. **Timeline** (1 template)
- `timeline_horizontal` - Horizontal timeline with milestones [existing]

### 10. **Roadmap** (1 template)
- `roadmap_quarterly_4` - Quarterly roadmap with 4 sections [planned]

### 11. **Gears/Cogs** (1 template)
- `gears_3` - Three interlocking gears [planned]

### 12. **Fishbone** (1 template)
- `fishbone_4_bone` - Cause-and-effect diagram with 4 bones [planned]

## Text Capacity Specifications

Each template includes detailed text capacity specifications for every text placeholder:

### Capacity Categories

**Small Elements** (60-100px width)
- Characters per line: 8-12
- Typical font size: 12-14px
- Best for: Labels, short identifiers

**Medium Elements** (100-150px width)
- Characters per line: 12-18
- Typical font size: 14-16px
- Best for: Titles, descriptions

**Large Elements** (150-230px width)
- Characters per line: 18-25
- Typical font size: 16-18px
- Best for: Main content, detailed text

**Title Elements**
- Characters per line: 30-40
- Typical font size: 24-26px
- Best for: Diagram titles

### Text Capacity Structure

Each text placeholder includes:
```python
{
    "id": "element_id",           # SVG element ID
    "purpose": "description",      # What this text represents
    "position": "location",        # Where in the diagram
    "capacity": {
        "chars_per_line": 15,      # Maximum characters per line
        "max_lines": 2,            # Maximum number of lines
        "font_size": 16            # Font size in pixels
    }
}
```

## Playbook Structure

Each template specification includes:

1. **Basic Metadata**
   - Template name and category
   - File name and status (existing/planned)
   - Visual description

2. **Dimensions**
   - ViewBox specifications
   - Width and height in pixels

3. **Text Placeholders**
   - Complete list of text element IDs
   - Purpose and position of each element
   - Detailed capacity specifications

4. **Color Elements**
   - IDs of elements that can be themed
   - Grouped by type (fills, strokes, etc.)

5. **Usage Guidelines**
   - When to use this template
   - Best practices
   - Common use cases

## Helper Functions

The playbook provides utility functions for template management:

- `get_template_spec(template_name)` - Get full specification for a template
- `get_templates_by_category(category)` - List templates in a category
- `get_text_capacity(template_name, element_id)` - Get text limits for an element
- `get_placeholder_ids(template_name)` - Get all text placeholder IDs
- `get_color_elements(template_name)` - Get themeable element IDs
- `get_template_dimensions(template_name)` - Get template dimensions
- `validate_svg_structure(svg_content, template_name)` - Validate SVG structure
- `calculate_text_fit(text, capacity)` - Check if text fits within capacity
- `get_existing_templates()` - List templates with SVG files
- `get_planned_templates()` - List templates to be created

## Usage Example

```python
from src.agents.diagram_utils.svg_playbook import (
    get_template_spec,
    get_text_capacity,
    calculate_text_fit
)

# Get template specification
spec = get_template_spec("cycle_4_step")

# Check text capacity for an element
capacity = get_text_capacity("cycle_4_step", "step_1_text")
# Returns: {"chars_per_line": 15, "max_lines": 2, "font_size": 16}

# Check if text will fit
result = calculate_text_fit("Plan and Execute", capacity)
# Returns: {"fits": True, "lines_needed": 1, ...}
```

## Template Status

### Existing Templates (10)
Templates with validated SVG files:
- cycle_4_step
- funnel_5_stage
- honeycomb_7
- hub_spoke_6
- matrix_2x2
- swot_matrix
- process_flow_5
- pyramid_3_level
- venn_2_circle
- timeline_horizontal

### Planned Templates (15)
Templates specified but not yet created:
- cycle_3_step, cycle_5_step
- funnel_3_stage, funnel_4_stage
- honeycomb_3, honeycomb_5
- hub_spoke_4
- matrix_3x3
- process_flow_3
- pyramid_4_level, pyramid_5_level
- venn_3_circle
- roadmap_quarterly_4
- gears_3
- fishbone_4_bone

## Text Wrapping Guidelines

The playbook includes automatic text wrapping calculations:

1. **Single Line Text**
   - Keep within chars_per_line limit
   - No wrapping needed

2. **Multi-Line Text**
   - Automatically wrap at word boundaries
   - Respect max_lines constraint
   - Truncate if exceeds capacity

3. **Overflow Handling**
   - Detect when text exceeds capacity
   - Provide wrapped text array
   - Indicate lines needed vs available

## Integration with Theme System

Color elements are identified for each template:
- Primary fills (main shapes)
- Secondary fills (supporting elements)
- Stroke colors
- Text colors
- Background fills

These can be dynamically updated to match user themes.

## Testing

A comprehensive test suite validates:
- Playbook structure integrity
- All template specifications
- Text capacity calculations
- Helper function operations
- SVG structure validation
- Template file existence

Run tests with:
```bash
python3 src/agents/diagram_utils/test_svg_playbook.py
```

## Version

- **Version**: 1.0
- **Date**: 2024
- **Templates**: 25 total (10 existing, 15 planned)
- **Categories**: 12